"""
We can only get up to 720 candles from the Kraken REST API, this means we will have insufficient data to produce
linear regression on e.g 1m, 5m, 15m, 1h candles between the last candle in CSV imported data and where the worker
indexed recent 1m OHLC data.

But we can still work on higher timeframes.
- Find the beginning of the most recent gap in OHLC candlesticks for 1m, 5m, 15m, 1h, 4h, 1d candles in influx
- Call the Kraken REST API to get candlesticks at that timeframe for the interval
- Index the 720 candlesticks

720 hours = 30 days
"""
import asyncio
import tenacity

from crypto_ingress.config import OHLC_INTERVALS, SYMBOLS_TO_WATCH, logger, ENVIRONMENT
from crypto_ingress.influxdb import InfluxClient
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc, ohlc_to_dict
from crypto_ingress.kraken import KrakenMarket


async def main():
    market_client = KrakenMarket()

    @tenacity.retry(
        wait=tenacity.wait_random_exponential(multiplier=1, max=60),
        stop=tenacity.stop_after_delay(60),
        reraise=True,
    )
    def get_candles(symbol: str, interval: int):
        try:
            candles = market_client.get_ohlc(pair=symbol, interval=interval, since=0)
        except Exception as e:
            logger.error(f"Got error when fetching 720 candles for {symbol} {interval}: {e}")
            raise e
        return candles[symbol]

    async with InfluxClient() as influx_client:
        write_api = influx_client.write_api()

        for symbol in SYMBOLS_TO_WATCH:
            for interval, interval_friendly in OHLC_INTERVALS:
                logger.info(f"Getting candles for {symbol} {interval_friendly}....")
                candles = await ohlc_to_dict(get_candles(symbol, interval), symbol, interval)
                points = await format_influxdb_ohlc(candles)
                logger.info(f"Writing candles {symbol} {interval_friendly}....")
                await write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{interval_friendly}", record=points)
                logger.info(f"Indexed {len(candles)} for {symbol} {interval_friendly}")


if __name__ == "__main__":
    asyncio.run(main())
