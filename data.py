from ta import trend, momentum
from messages import MESSAGE_TEMPLATE, subAccountName


def calculate_indicators(dflist):
    for coin in dflist:
        df = dflist[coin]
        df.drop(columns=df.columns.difference(
            ['open', 'high', 'low', 'close', 'volume']), inplace=True)

        # your indicator

        df.dropna(inplace=True)
    return dflist


def load_historical_data(mexc, pairlist, timeframe, nbOfCandles, message_list=None):
    dflist = {}
    for pair in pairlist:
        try:
            df = mexc.get_more_last_historical_async(pair, timeframe, 1000)
            dflist[pair.replace('/USDC', '')] = df
        except Exception as err:
            if message_list is not None:
                print(err)
                message_list.append(MESSAGE_TEMPLATE['message_erreur'].format(
                    subAccountName, nbOfCandles, pair))
    return dflist
