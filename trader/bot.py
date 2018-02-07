from decimal import Decimal as D

import random


class Exchange:

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
        num_bought = D('1000')
        return num_bought


class Trader:
    """
    A trader that always wants more flat-money.
    """

    def __init__(self, premium_rate=0.05):
        self.assets = {
            'eos': 0,
            'omg': 0,
            'ntl': 0,
        }
        self.premium_rate = premium_rate

    @staticmethod
    def get_price_with_impact_cost(min_price, premium_rate):
        return min_price * (1 + premium_rate)

    @staticmethod
    def get_premium_rate():
        return D(random.randint(1, 100)) / D('100')

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
        """
        If > 1， source
        :param source_token_name:
        :param target_token_name:
        :return:
        """
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

    def do_transition(self, token_name, num_token, num_ntl):
        Exchange.buy()
