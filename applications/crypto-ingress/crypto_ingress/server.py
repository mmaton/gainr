import json
from copy import deepcopy
from datetime import datetime, timedelta

import asyncio
from functools import partial

from influxdb_client.client.write_api import SYNCHRONOUS
from kraken.spot import KrakenSpotWSClientV2

from crypto_ingress.config import influxdb_client, logger, MQTT_OHLC_TOPIC_BASE
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.mqtt import connect_mqtt

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

candle_tracker: dict[str, dict] = {}


async def infill_missing_candles(candles: list[dict]) -> list[dict]:
    """
    This assumes that candles are always delivered by the Kraken websocket in-order
    """
    new_candles = []
    for current_candle in candles:
        symbol = current_candle.get("symbol")
        last_candle = candle_tracker.get(symbol)

        if not last_candle:
            # First time we've seen a candle for current symbol, store and return
            candle_tracker[symbol] = current_candle
            continue

        # Check if we have any missing candles for the current symbol
        last_candle_interval_begin = datetime.fromisoformat(last_candle["interval_begin"][:-1])
        current_candle_interval_begin = datetime.fromisoformat(current_candle["interval_begin"][:-1])
        mins_between_candles = (current_candle_interval_begin - last_candle_interval_begin).seconds // 60

        if mins_between_candles > 1:
            for i in range(1, mins_between_candles):
                new_candle = deepcopy(current_candle)

                new_time = last_candle_interval_begin + timedelta(minutes=i)
                new_candle['interval_begin'] = new_time.isoformat() + '.000000000Z'
                new_candle['timestamp'] = (new_time + timedelta(minutes=1)).isoformat() + '.000000000Z'
                # Close of the previous candlestick becomes the open of the new one
                new_candle['open'] = last_candle['close']
                new_candle['close'] = last_candle['close']
                new_candle['volume'] = float(0)
                new_candle['trades'] = 0
                new_candle['vwap'] = float(0)

                new_candles.append(new_candle)

        candle_tracker[symbol] = current_candle

    all_candles = candles + new_candles
    all_candles.sort(key=lambda x: x.get("interval_begin"))
    return all_candles


async def message_callback(mqtt_client, message):
    if message.get("method") == "pong" or message.get("channel") == "heartbeat":
        return

    if message.get("channel") == "ohlc":
        infilled_candles = await infill_missing_candles(message.get("data"))

        for candle in infilled_candles:
            mqtt_client.publish(MQTT_OHLC_TOPIC_BASE + f"/{candle.get('symbol')}", json.dumps(candle))

        candles = await format_influxdb_ohlc(infilled_candles)
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