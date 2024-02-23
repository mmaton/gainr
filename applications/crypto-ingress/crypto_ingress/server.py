import json

import asyncio
from functools import partial

from influxdb_client.client.write_api import SYNCHRONOUS
from kraken.spot import KrakenSpotWSClientV2

from crypto_ingress.config import influxdb_client, logger, MQTT_OHLC_TOPIC_BASE
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.mqtt import connect_mqtt

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


async def message_callback(mqtt_client, message):
    if message.get("method") == "pong" or message.get("channel") == "heartbeat":
        return

    if message.get("channel") == "ohlc":
        for candle in message.get("data"):
            mqtt_client.publish(MQTT_OHLC_TOPIC_BASE + f"/{candle.get('symbol')}", json.dumps(candle))

        candles = await format_influxdb_ohlc(message.get("data"))
        write_api.write(bucket="ohlc_1m", record=candles)
        for candle in candles:
            logger.debug(candle)
        logger.info(f"Wrote {len(candles)} candles")


async def main():
    mqtt_client = connect_mqtt()
    mqtt_client.loop_start()

    client = KrakenSpotWSClientV2(callback=partial(message_callback, mqtt_client))
    await client.subscribe(
        params={
            "channel": "ohlc",
            "interval": 1,
            "symbol": ["XRP/EUR", "BTC/EUR"],
        }
    )
    while not client.exception_occur:
        await asyncio.sleep(6)
    mqtt_client.loop_stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        # The websocket client will send {'event': 'asyncio.CancelledError'}
        # via on_message, so you can handle the behavior/next actions
        # individually within your strategy.