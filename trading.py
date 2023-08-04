from messages import MESSAGE_TEMPLATE, subAccountName
import time

trixLength = 9
trixSignal = 21

# -- Hyper parameters --
maxOpenPosition = 2
stochOverBought = 0.80
stochOverSold = 0.20
TpPct = 5


def calculate_balances(mexc, dflist):
    usd_balance = mexc.get_balance_of_one_coin('USDC')
    balance_in_usd_per_coin = {}
    for coin in dflist:
        symbol = coin + '/USDC'
        last_price = float(mexc.convert_price_to_precision(
            symbol, mexc.get_bid_ask_price(symbol)['ask']))
        coin_balance = mexc.get_balance_of_one_coin(coin)
        balance_in_usd_per_coin[coin] = coin_balance * last_price
        total_balance_in_usd = sum(
            balance_in_usd_per_coin.values()) + usd_balance
    return usd_balance, balance_in_usd_per_coin, total_balance_in_usd


def calculate_positions(balance_in_usd_per_coin, total_balance_in_usd):
    coin_position_list = []
    for coin in balance_in_usd_per_coin:
        if balance_in_usd_per_coin[coin] > 0.05 * total_balance_in_usd:
            coin_position_list.append(coin)
    return coin_position_list


def buy_condition(row, previousRow=None):
    if (
        # your buy condition
    ):
        return True
    else:
        return False


def sell_condition(row, previousRow=None):
    if (
        # your sell condition
    ):
        return True
    else:
        return False


def execute_sells(mexc, coin_position_list, dflist, message_list, open_positions, balance_in_usd_per_coin):
    for coin in coin_position_list:
        symbol = coin + '/USDC'
        sell_price = float(mexc.convert_price_to_precision(
            symbol, mexc.get_bid_ask_price(symbol)['ask']))
        coin_balance = mexc.get_balance_of_one_coin(coin)
        if sell_condition(dflist[coin].iloc[-2], dflist[coin].iloc[-3]) == True:
            open_positions -= 1

            open_orders = mexc.get_open_order(symbol)
            if len(open_orders) > 0:
                order_id = open_orders[0]['id']
                canceled_order = mexc.cancel_order_by_id(order_id, symbol)
                print('order cancel')
            time.sleep(1)
            print('sell', coin_balance, symbol, 'at ', sell_price)
            sell = mexc.place_limit_order(
                symbol, 'sell', coin_balance, sell_price, reduce=False)
            message_list.append(MESSAGE_TEMPLATE['message_sell'].format(
                subAccountName, str(coin), str(sell_price)))
        else:
            message_list.append(MESSAGE_TEMPLATE['message_keep'].format(subAccountName, str(
                coin_balance), str(coin), str(sell_price), str(balance_in_usd_per_coin[coin])))
            print('keep', balance_in_usd_per_coin[coin], coin)
            print(open_positions)
    return message_list, open_positions


def execute_buys(mexc, dflist, message_list, open_positions, coin_position_list, usd_balance):
    if open_positions < maxOpenPosition:
        for coin in dflist:
            if coin not in coin_position_list:
                try:
                    if buy_condition(dflist[coin].iloc[-2], dflist[coin].iloc[-3]) == True and open_positions < maxOpenPosition:
                        symbol = coin + '/USDC'
                        buy_price = float(mexc.convert_price_to_precision(
                            symbol, mexc.get_bid_ask_price(symbol)['ask']))
                        tp_price = float(mexc.convert_price_to_precision(
                            symbol, buy_price + TpPct * buy_price))
                        buy_quantity_in_usd = mexc.get_balance_of_one_coin(
                            'USDC') * 1 / (maxOpenPosition - open_positions)
                        if open_positions == maxOpenPosition - 1:
                            buy_quantity_in_usd = 0.95 * buy_quantity_in_usd
                        buy_amount = float(mexc.convert_amount_to_precision(symbol, float(
                            mexc.convert_amount_to_precision(symbol, buy_quantity_in_usd / buy_price))))
                        message_list.append(MESSAGE_TEMPLATE['message_buy'].format(
                            subAccountName, str(buy_amount), str(coin), str(buy_price)))
                        buy = mexc.place_limit_order(
                            symbol, 'buy', buy_amount, buy_price, reduce=False)
                        print('buy', buy_amount, coin, 'at ', buy_price)
                        open_positions += 1
                except Exception as e:
                    error_message = {str(e)}
                    message_list.append(MESSAGE_TEMPLATE['message_error'].format(
                        subAccountName, error_message))
                    print(error_message)
                    continue

    return message_list, open_positions


def cancel_orders(mexc, symbol):
    open_orders = mexc.get_open_order(symbol)
    if len(open_orders) > 0:
        order_id = open_orders[0]['id']
        print(order_id)
        canceled_order = mexc.cancel_order_by_id(order_id, symbol)
