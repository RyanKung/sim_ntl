from collections import defaultdict
from decimal import Decimal as D

import random

import pandas as pd
import time

from sim.netrual import Component


EOS = 'EOS'
OMG = 'OMG'
NTL = 'NTL'


def read_csv(name, type='5m'):
    return pd.read_csv(
    './csv/binance_%s_%s_kline.csv' %(name, type),
    names=[name, 'open', 'high', 'low', 'last', 'type', 'timestamp']
)


def get_usdt_price_pandas(target_symbol):
    target2eth = read_csv('%s_ETH' % target_symbol)
    eth2usdt = read_csv('ETH_USDT')
    target2eth2usdt = pd.merge(target2eth, eth2usdt, on='timestamp')
    target2eth2usdt['price_usdt'] = target2eth2usdt['last_x'] * target2eth2usdt['last_y']
    return target2eth2usdt


class Exchange:
    num_ntl_each_round = D('1000')

    def __init__(self, symbols):
        """
        :type components: dict[str, sim.netrual.Component]
        """
        self.current_index = 0
        self.symbols = symbols
        self.prices = {}
        self.components = {}
        self.current_prices = defaultdict(lambda : D('0'))
        for symbol in symbols:
            self.components[symbol] = Component(symbol)
            self.prices[symbol] = get_usdt_price_pandas(symbol)

    def update_kline(self):
        for symbol in self.symbols:
            component = self.components[symbol]
            prices = self.prices[symbol]
            ts = prices['timestamp'][self.current_index]
            component(ts)
            self.current_prices[symbol] = D(
                prices['price_usdt'][self.current_index]
            )
        self.current_index += 1

    def bootstrap(self):
        self.update_kline()
        for component in self.components.values():
            component.auction('the-god', 1000)

    def get_flat_price(self, symbol):
        return self.current_prices[symbol]

    def get_ntl_min_price(self, token_name):
        component = self.components[token_name]
        return component.min_bid

    def redeem(self, num_ntl, symbol, sender_name):
        """
        return token.
        """
        component = self.components[symbol]
        num_redeemed = component.redeem(sender_name, num_ntl)
        if num_redeemed is False:
            return None
        return num_redeemed

    def buy(self, num_token, symbol, sender_name):
        """
        To buy given number of NTL buy token.
        Return num_amount of ntl if succeed, None if failed
        :param num_token: 10
        :param symbol: for example EOS
        :param sender_name: trader_name
        """
        component = self.components[symbol]
        result = component.auction(sender_name, num_token)
        if result:
            return self.num_ntl_each_round
        return None

    @classmethod
    def get_ntl_each_round(cls):
        return cls.num_ntl_each_round


class Trader:
    """
    A trader that always wants more flat-money.
    """
    name = 'greed-is-good'

    def __init__(self, num_eos, num_omg, exchange):
        """
        :type exchange: Exchange
        """
        self.assets = {
            EOS: num_eos,
            OMG: num_omg,
            NTL: D('0'),
        }
        self.exchange = exchange

    @staticmethod
    def get_price_with_impact_cost(min_price, premium_rate):
        return min_price * (1 + premium_rate)

    @staticmethod
    def get_premium_rate():
        return D(random.randint(1, 20)) / D('100')

    def get_ntl_relative_price(
            self, source_token_name, target_token_name, premium_rate=None
    ):
        source_ntl_price = self.exchange.get_ntl_min_price(source_token_name)
        target_ntl_price = self.exchange.get_ntl_min_price(target_token_name)
        if premium_rate is not None:
            target_ntl_price = self.get_price_with_impact_cost(
                target_ntl_price, premium_rate=premium_rate
            )
        return target_ntl_price / source_ntl_price

    def get_token_relative_price(self, source_token_name, target_token_name):
        source_market_price = self.exchange.get_flat_price(source_token_name)
        target_market_price = self.exchange.get_flat_price(target_token_name)
        return target_market_price / source_market_price

    def should_convert2target(self, source_token, target_token, premium_rate=None):
        ntl_relative_price = self.get_ntl_relative_price(
            source_token, target_token, premium_rate=premium_rate
        )
        flat_relative_price = self.get_token_relative_price(source_token, target_token)
        if ntl_relative_price < flat_relative_price:
            return True
        return False

    def one_cycle(self):
        """
        Should be run each round.
        """
        premium_rate = self.get_premium_rate()
        if self.should_convert2target(
            EOS, OMG, premium_rate=premium_rate
        ):
            self.do_transition(EOS, OMG)
            return
        if self.should_convert2target(
            OMG, EOS, premium_rate=premium_rate
        ):
            self.do_transition(OMG, EOS)
            return

    def do_transition(self, source, target):
        price = self.exchange.get_ntl_min_price(source)
        source_cost = price * self.exchange.get_ntl_each_round()
        if self.assets[source] < source_cost:
            return
        ntl_got = self.exchange.buy(source_cost, source, self.name)
        if ntl_got is None:
            return
        self.assets[NTL] += ntl_got
        self.assets[source] -= source_cost
        num_target_got = self.exchange.redeem(
            self.assets[NTL],
            target,
            self.name
        )
        self.assets[NTL] = D('0')
        self.assets[target] += num_target_got


def main():
    exchange = Exchange(['EOS', 'OMG'])
    trader = Trader(
        D('1000') * D('10'), D('1000') * D('10'),
        exchange,
    )
    exchange.bootstrap()
    while True:
        exchange.update_kline()
        trader.one_cycle()
        print(trader.assets)
        time.sleep(1)

main()
