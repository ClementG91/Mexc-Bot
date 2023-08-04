from datetime import datetime
from config import load_secret
from mexc import configure_mexc
from data import calculate_indicators, load_historical_data
from trading import (
    calculate_balances,
    calculate_positions,
    execute_sells,
    execute_buys,
)
import discord
from discord_utils import send_messages_to_discord
from messages import MESSAGE_TEMPLATE, subAccountName


# Timeframe to use for technical analysis
timeframe = "1h"

# -- Variables for indicators --
trixLength = 9
trixSignal = 21
stochOverBought = 0.80
stochOverSold = 0.20


def get_time_now():
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    return current_time


def main():
    print(get_time_now())
    # Initialize mexc API client
    secret = load_secret("/var/www/evilcorp5/secret.json")
    mexc = configure_mexc("mexc_exemple", secret, production=True)

    # Initialize Discord client
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    client = discord.Client(intents=intents)

    # Define your list of coins
    pairlist = [
        "BTC/USDC",
        "ETH/USDC",
        "BNB/USDC",
        "XRP/USDC",
        "SOL/USDC",
        "SHIB/USDC",
        "DOGE/USDC",
        "LTC/USDC",
        "MATIC/USDC",
        "AVAX/USDC"
    ]

    # Load historical data
    message_list = []
    dflist = load_historical_data(
        mexc, pairlist, timeframe, 1000, message_list
    )

    # Calculate indicators
    dflist = calculate_indicators(dflist, trixLength, trixSignal)

    # Calculate balances
    usd_balance, balance_in_usd_per_coin, total_balance_in_usd = calculate_balances(
        mexc, dflist
    )
    # Calculate positions
    coin_position_list = calculate_positions(
        balance_in_usd_per_coin, usd_balance
    )

    # Execute sales if sell condition is met
    open_positions = len(coin_position_list)
    message_list, open_positions = execute_sells(
        mexc,
        coin_position_list,
        dflist,
        message_list,
        open_positions,
        balance_in_usd_per_coin,
    )

    # Execute buys if buy condition is met
    message_list, open_positions = execute_buys(
        mexc,
        dflist,
        message_list,
        open_positions,
        coin_position_list,
        usd_balance,
    )
    message_list.append(
        MESSAGE_TEMPLATE["message_wallet"].format(
            subAccountName, str(total_balance_in_usd)
        )
    )
    
    # Send messages to Discord
    send_messages_to_discord(client, secret, message_list)
    print(get_time_now())


if __name__ == "__main__":
    main()
