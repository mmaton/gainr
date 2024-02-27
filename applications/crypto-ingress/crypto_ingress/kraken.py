from kraken.spot import Market

from crypto_ingress import config


class KrakenMarket:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            market_kwargs = {}
            if config.KRAKEN_KEY and config.KRAKEN_SECRET:
                market_kwargs = {
                    "key": config.KRAKEN_KEY,
                    "secret": config.KRAKEN_SECRET
                }
            cls._instance = Market(**market_kwargs)
        return cls._instance
