import operator
from .netrual import NLT_components, NLT_accounts, NLT_REWARD


def highest(market_prices: dict):
    return max({
        t: float(p) * NLT_components[t].min_bid

        for t, p in market_prices.items()
        if t != 'timestamp'
    }.items(), key=operator.itemgetter(1))


def lowest(market_prices: dict):
    return min({
        t: float(p) * NLT_components[t].min_bid
        for t, p in market_prices.items()
        if t != 'timestamp'
    }.items(), key=operator.itemgetter(1))


def get_profit_pair(market_prices, threshold=0.001):
    highest_component, highest_value = highest(market_prices)
    lowest_component, lowest_value = lowest(market_prices)
    if float(highest_value) / float(lowest_value) < (1 + threshold):
        return False
    return {
        'from': NLT_components[lowest_component],
        'to': NLT_components[highest_component],
        'rate': highest_value / lowest_value
    }


def exchange(market_prices, ts, sender):
    pair = get_profit_pair(market_prices)
    assert pair['from'](ts).auction(
        sender, pair['from'].min_bid * pair['rate'])
    pair['to'](ts).redeem(sender, NLT_REWARD)


def nlt_price_2(market_price: dict):
    minted = {t: c.min_bid for t, c in NLT_components.items()}
    return sum([market_price[t] * v for t, v in minted.items()]) / float(len(NLT_components) * NLT_REWARD)


def nlt_price(market_price: dict):
    h = highest(market_price)[0]
    return (market_price[h] * NLT_components[h].min_bid) / NLT_REWARD


def nlt_fm_price(market_price: dict):
    if 'timestamp' in market_price:
        market_price = market_price.drop('timestamp')
    total_supply = list(NLT_components.values())[0].total_supply
    return sum([NLT_components[t].reserve * p for t, p in market_price.items()]) / total_supply


def profit_rate(p_c, p_nlt, min_bid):
    value_c = min_bid * p_c
    value_nlt = p_nlt * NLT_REWARD
    return float(value_c) / float(value_nlt)


def auction_threshold(p_c, p_nlt, min_bid, threshold=0.01):
    profit = profit_rate(p_c, p_nlt, min_bid)
    return 1 / profit > (1 + threshold)


def redeem_threshold(p_c, p_nlt, min_bid, threshold=0.01):
    profit = profit_rate(p_c, p_nlt, min_bid)
    return profit > (1 + threshold)


def get_worth_to_auction(market_price: dict, price_model=nlt_price,
                         threshold_func=auction_threshold, threshold=0.01):
    price = price_model(market_price)
    return {
        k: {
            'price': v,
            'min_bid': NLT_components[k].min_bid,
            'delta': price * NLT_REWARD - v * NLT_components[k].min_bid
        }
        for k, v in market_price.items()
        if threshold_func(v, price, NLT_components[k].min_bid, threshold)
    }


def get_worth_to_redeem(market_price: dict, price_model=nlt_price, threshold_func=redeem_threshold, threshold=0.01):
    price = price_model(market_price)
    return {
        k: {
            'price': v,
            'min_bid': NLT_components[k].min_bid,
            'delta': v * NLT_components[k].min_bid - price * NLT_REWARD
        }
        for k, v in market_price.items()
        if threshold_func(v, price, NLT_components[k].min_bid, threshold)
    }


def determin_auction_quantity(market_price: dict, price_model=nlt_price, threshold=0.01):
    price = price_model(market_price)

    planned = {
        k: NLT_REWARD * price / v['price']
        for k, v
        in get_worth_to_auction(market_price, threshold=threshold).items()
    }
    return {
        k: v
        for k, v
        in planned.items()
    }


def get_redeem_price(market_price: dict, amount=1000):
    return {
        t: NLT_components[t].get_redeem_price(1000)
        for t, p in market_price.items()
    }


def determin_redeem_quantity(market_price: dict, price_model=nlt_price, threshold=0.01):
    price = price_model(market_price)

    def quantity(token, t_price, n_price):
        q = 0
        while (NLT_components[token].get_redeem_amount(q + NLT_REWARD) * t_price) / (n_price * (q + NLT_REWARD)) > 1 + threshold:
            if NLT_components[token].get_redeem_amount(q + NLT_REWARD) > NLT_components[token].reserve:
                return q
            q += NLT_REWARD
        return q

    planned = {
        k: quantity(k, v['price'], price)
        for k, v
        in get_worth_to_auction(market_price, threshold=threshold).items()
    }

    return {
        k: v
        for k, v in planned.items()
        if v != 0
    }


def check_status():
    return {k: v.minted for k, v in NLT_components.items()}


def check_min_bid():
    return {k: v.min_bid for k, v in NLT_components.items()}


def redeem(token, market_price, sender, rate=0.002):
    balance = NLT_accounts.get(sender, float(0))
    return NLT_components[token].redeem(sender, balance * rate)


def redeem_strategy(plan: dict, sender: str, ts: int):
    return {
        'redeemed %s' % t: NLT_components[t](ts).redeem(sender, q)
        for t, q in plan.items()
    }


def auction_strategy(plan: dict, sender: str, ts: int):
    return {
        'auctioned %s' % t: NLT_components[t](ts).auction(sender, bid)
        for t, bid in plan.items()
    }
