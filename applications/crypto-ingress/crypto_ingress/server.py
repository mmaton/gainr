import asyncio
from influxdb_client.client.write_api import SYNCHRONOUS
from kraken.spot import KrakenSpotWSClientV2

from crypto_ingress.config import influxdb_client, logger
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


async def message_callback(message):
    if message.get("method") == "pong" or message.get("channel") == "heartbeat":
        return

    if message.get("channel") == "ohlc":
        candles = await format_influxdb_ohlc(message.get("data"))
        write_api.write(bucket="ohlc_1m", record=candles)
        logger.debug(message.get("data"))
        logger.info(f"Wrote {len(candles)} candles")


async def main():
    client = KrakenSpotWSClientV2(callback=message_callback)
    await client.subscribe(
        params={
            "channel": "ohlc",
            "interval": 1,
            "symbol": ["XRP/EUR", "BTC/EUR"],
        }
    )
    while not client.exception_occur:
        await asyncio.sleep(6)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        # The websocket client will send {'event': 'asyncio.CancelledError'}
        # via on_message, so you can handle the behavior/next actions
        # individually within your strategy.
