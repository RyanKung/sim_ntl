import pandas as pd


def read_csv(name, type='5m'):
    res = pd.read_csv(
        './history/binance_%s_%s_kline.csv' % (name, type),
        names=[name, 'open', 'high', 'low', 'last', 'type', 'timestamp']
    )
    res['timestamp'] = res['timestamp'].map(format_ts)
    return res


def get_price(token, eth_usdt=None):  # None for cache able
    if not eth_usdt:
        eth_usdt = read_csv('ETH_USDT')

    if token == 'ETH':
        value = eth_usdt['last']
        timestamp = eth_usdt['timestamp']
    else:
        eth_target = read_csv('%s_ETH' % token)
        merged = pd.merge(eth_target, eth_usdt, on='timestamp')
        value = merged['last_x'] * merged['last_y']
        timestamp = eth_usdt['timestamp']

    return pd.DataFrame({
        token: value,
        'timestamp': timestamp
    }).dropna(how='any')


def get_batch_price(tokens, eth_usdt=None):
    df = pd.concat(
        [get_price(t) for t in tokens], axis=1
    )
    # https://stackoverflow.com/questions/32041245/fast-method-for-removing-duplicate-columns-in-pandas-dataframe
    return df.loc[:, ~df.columns.duplicated()].dropna(how='any')


def format_ts(s):
    return int(str(int(s))[:10])
