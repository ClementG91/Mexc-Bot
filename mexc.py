from spot_mexc import Spotmexc


def configure_mexc(account_to_select, secret, production=False):
    mexc = Spotmexc(
        apiKey=secret[account_to_select]["apiKey"],
        secret=secret[account_to_select]["secret"],
        password=secret[account_to_select]["password"],
    )
    return mexc
