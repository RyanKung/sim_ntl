from decimal import Decimal as D

import random


EOS = 'eos'
OMG = 'omg'
NTL = 'ntl'


class Exchange:
    num_ntl_each_round = D('1000')

    @classmethod
    def update_kline(cls):
        # update all data
        pass

    @classmethod
    def get_flat_price(cls, token_name):
        return 1

    @classmethod
    def get_ntl_min_price(cls, token_name):
        return 1

    @classmethod
    def redeem(cls, num_ntl, token_name):
        """
        return token.
        """
        num_redeemed = D(0)
        return num_redeemed

    @classmethod
    def buy(cls, num_token, token):
        """
        To buy given number of NTL buy token.
        Return num_amount of ntl if succeed, None if failed
        :param num_token: 10
        :param token: for example EOS
        """
        num_bought = cls.num_ntl_each_round
        return num_bought

    @classmethod
    def get_ntl_each_round(cls):
        return cls.num_ntl_each_round


class Trader:
    """
    A trader that always wants more flat-money.
    """

    def __init__(self, num_eos, num_omg, premium_rate=0.05):
        self.assets = {
            EOS: num_eos,
            OMG: num_omg,
            NTL: D('0'),
        }
        self.premium_rate = premium_rate

    @staticmethod
    def get_price_with_impact_cost(min_price, premium_rate):
        return min_price * (1 + premium_rate)

    @staticmethod
    def get_premium_rate():
        return D(random.randint(1, 20)) / D('100')

    def get_ntl_relative_price(
            self, source_token_name, target_token_name, premium_rate=None
    ):
        source_ntl_price = Exchange.get_ntl_min_price(source_token_name)
        target_ntl_price = Exchange.get_ntl_min_price(target_token_name)
        if premium_rate is not None:
            target_ntl_price = self.get_price_with_impact_cost(
                target_ntl_price, premium_rate=premium_rate
            )
        return target_ntl_price / source_ntl_price

    def get_token_relative_price(self, source_token_name, target_token_name):
        source_market_price = Exchange.get_flat_price(source_token_name)
        target_market_price = Exchange.get_flat_price(target_token_name)
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
        price = Exchange.get_ntl_min_price(source)
        source_cost = price * Exchange.get_ntl_each_round()
        if self.assets[source] < source_cost:
            return
        ntl_got = Exchange.buy(source_cost, source)
        if ntl_got is None:
            return
        self.assets[NTL] += ntl_got
        self.assets[source] -= source_cost
        num_target_got = Exchange.redeem(self.assets[NTL], target)
        self.assets[NTL] = D('0')
        self.assets[target] += num_target_got


def main():
    trader = Trader(D('1000') * D('10'), D('1000') * D('10'))
    while True:
        Exchange.update_kline()
        trader.one_cycle()
        print(trader.assets)