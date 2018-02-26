import random
from pandas import DataFrame

from .netrual import Component, NLT_reserve, NLT_components, NLT_REWARD # noqa
from .utils import redeem_strategy, auction_strategy, nlt_price, nlt_price_2
from .utils import determin_auction_quantity, determin_redeem_quantity


def warmup(start_timestamp, sender):
    begin = start_timestamp - Component.auction_window - 1
    for c in NLT_components.values():
        res = c(begin).auction(sender, random.randint(0, 100))
        print(res)


def rational_warmup(start_timestamp, market_price, sender):
    begin = start_timestamp - Component.auction_window - 1
    for c in NLT_components.values():
        res = c(begin).auction(sender, (15 / float(market_price[c.token])) * NLT_REWARD)
        print(res)


def sim_loop(market_prices: DataFrame, sender='satoshi'):
    '''
    [{token: price}]
    '''
    ret = []
    tokens = [t for t in market_prices.columns if t != 'timestamp']
    [Component(t) for t in tokens]  # inital
#    warmup(market_prices.timestamp[0], sender)
    rational_warmup(market_prices.timestamp[0], market_prices.T[0], 'satoshi')
    old_cycle = -1

    for i, data in market_prices.iterrows():
        print("==" * 10)
        ts = data['timestamp']

        [c(ts) for c in NLT_components.values()]
        market_price = {k: v for k, v in data.items() if k != 'timestamp'}
        price = nlt_price(market_price)
        print('PRICE OF NLT %s' % price)
        plan_to_redeem = determin_redeem_quantity(market_price)
        print('plan to redeem %s for' % plan_to_redeem)

        redeemed = redeem_strategy(plan_to_redeem, sender, ts)
        print('Redeemed %s' % redeemed)

        curr_cycle = list(NLT_components.values())[0].cycle
        #  Only do auction when get a new cycle
        if old_cycle != -1 and curr_cycle != old_cycle:
            if curr_cycle > 200:
                return ret
            plan_to_auction = determin_auction_quantity(market_price)
            auctioned = auction_strategy(plan_to_auction, sender, ts)
            print('plan to auction %s' % plan_to_auction)
            print('Auctioned %s' % auctioned)
        old_cycle = curr_cycle
        ret.append(dict({
            'ts': ts,
            'price': price,
            'price2': nlt_price_2(market_price)
        }, **NLT_reserve))
    return ret
