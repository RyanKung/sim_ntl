from decimal import Decimal as D

import pytest
import mock

import bot


@pytest.mark.parametrize(
    'eos_flat, eos_ntl, omg_flat, omg_ntl, premium_rate, result',
    (
        (1, 1, 1, 1, None, False),
        (2, 2, 1, 1, None, False),
        (1, 0.5, 1, 1, None, False),
        (1, 1, 2, 1, None, True),
        (2, 1, 1, 1, None, False),
        (1, 2, 1, 1, None, True),
        (1, 2, 1, 1, 1, False),
        (1, 2, 1, 1, 0.9, True),
        (1, 2, 1, 1, 1.1, False),
    )
)
def test_should_redeem_target_token(
        eos_flat, eos_ntl, omg_flat, omg_ntl, premium_rate, result,
):
    trader = bot.Trader(D('1000') * D('10'), D('1000') * D('10'))
    exchange = bot.Exchange

    def get_flat_price(token_name):
        if token_name == 'eos':
            return eos_flat
        else:
            return omg_flat

    def get_ntl_price(token_name):
        if token_name == 'eos':
            return eos_ntl
        else:
            return omg_ntl

    with mock.patch.object(exchange, 'get_flat_price', get_flat_price), \
         mock.patch.object(exchange, 'get_ntl_min_price', get_ntl_price):
        assert trader.should_convert2target(
            'eos', 'omg', premium_rate=premium_rate
        ) is result
