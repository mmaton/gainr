from kraken.spot import Market

from crypto_ingress import config


def get_secret_kwargs() -> dict:
    if config.KRAKEN_KEY and config.KRAKEN_SECRET:
        return {
            "key": config.KRAKEN_KEY,
            "secret": config.KRAKEN_SECRET
        }

    return {}


class KrakenMarket:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = Market(**get_secret_kwargs())
        return cls._instance
