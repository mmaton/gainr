import json
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import List

import asyncio
from functools import partial

from influxdb_client.client.write_api import SYNCHRONOUS
from kraken.spot import KrakenSpotWSClientV2
from kraken.spot import Market

from crypto_ingress.config import influxdb_client, logger, MQTT_OHLC_TOPIC_BASE, ENVIRONMENT
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.mqtt import connect_mqtt

write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

candle_tracker: dict[str, dict[int: List[dict]]] = defaultdict(dict)  # symbol: {interval: [{candle}, {candle}]}


def get_minutes_for_timeframe(timeframe: str) -> int:
    timeframe_to_minutes = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
        "1w": 10080,
    }
    return timeframe_to_minutes[timeframe]


async def message_callback(mqtt_client, message):
    if message.get("method") == "pong" or message.get("channel") == "heartbeat":
        return

    if message.get("channel") == "ohlc":
        candles = message.get("data")

        new_candles: dict[int, List[dict]] = defaultdict(list)  # timeframe: [candles]

        for candle in candles:
            symbol = candle["symbol"]
            candle.pop("interval")

            sum_previous_trades = sum_previous_volume = 0

            # Update the current candle in candle_tracker or create a new candle if need be - for each TF
            for timeframe, timeframe_candles in candle_tracker[symbol].items():
                candle_interval_begin = datetime.fromisoformat(candle["interval_begin"][:-1])
                last_candle_interval_begin = datetime.fromisoformat(timeframe_candles[-1]["interval_begin"][:-1])
                last_candle_timestamp = datetime.fromisoformat(timeframe_candles[-1]["timestamp"][:-1])

                # TODO: Can we offload these writes to MQTT/Influx to another thread?
                if timeframe == "15m" and symbol == "BTC/EUR":
                    breakpoint()
                if candle_interval_begin > last_candle_timestamp:
                    # New candle needed in our candle_tracker - deque means oldest will be dropped
                    # Update the `interval_begin` to the `timestamp` of the previous candle
                    candle["interval_begin"] = last_candle_timestamp.isoformat() + '.000000000Z'
                    interval = get_minutes_for_timeframe(timeframe)
                    new_timestamp = datetime.fromisoformat(candle["interval_begin"][:-1]) + timedelta(minutes=interval)
                    candle["timestamp"] = new_timestamp.isoformat() + '.000000Z'

                    candle_tracker[symbol][timeframe].append(candle)
                    new_candles[timeframe].append(candle)

                elif candle_interval_begin >= last_candle_interval_begin:
                    interval = get_minutes_for_timeframe(timeframe)

                    # Update current candle
                    candle_tracker[symbol][timeframe][-1] = {
                        "interval_begin": candle_tracker[symbol][timeframe][-1]["interval_begin"],
                        "symbol": symbol,
                        "timestamp": candle_tracker[symbol][timeframe][-1]["timestamp"],
                        "open": float(candle_tracker[symbol][timeframe][-1]["open"]),
                        "high": max(candle_tracker[symbol][timeframe][-1]["high"], candle["high"]),
                        "low": min(candle_tracker[symbol][timeframe][-1]["low"], candle["low"]),
                        "close": float(candle["close"]),
                        "trades": int(candle["trades"] if interval == 1 else sum_previous_trades),
                        "volume": float(candle["volume"] if interval == 1 else sum_previous_volume),
                    }
                    new_candles[timeframe].append(candle_tracker[symbol][timeframe][-1])
                else:
                    # Otherwise the candle is older than what we've got already, discard and move on
                    ...

                # Sum up the previous timeframe's candles if we need to update the latest candle in the next TF
                sum_previous_trades += sum(c["trades"] for c in candle_tracker[symbol][timeframe])
                sum_previous_volume += sum(c["volume"] for c in candle_tracker[symbol][timeframe])

        # Now notify MQTT and store in influx
        for timeframe, candles in new_candles.items():
            for candle in candles:
                mqtt_client.publish(
                    MQTT_OHLC_TOPIC_BASE + f"/ohlc_{timeframe}/{candle.get('symbol')}",
                    json.dumps(candle)
                )
            points = await format_influxdb_ohlc(candles)
            write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{timeframe}", record=points)
            logger.info(f"Wrote {len(candles)} candles for timeframe {timeframe}")
            logger.debug(candles)


async def populate_candle_tracker_data(symbols) -> None:
    market_client = Market()
    intervals = [(1, "1m"), (5, "5m"), (15, "15m"), (60, "1h"), (240, "4h"), (1440, "1d"), (10080, "1w")]
    started_at = datetime.now(tz=timezone.utc)

    for symbol in symbols:
        for interval_idx, (interval, interval_friendly) in enumerate(intervals):
            logger.info(f"Populating {symbol} {interval_friendly}")
            if interval_idx < len(intervals) - 1:
                next_interval = intervals[interval_idx + 1][0]
                num_candles = intervals[interval_idx + 1][0] // interval
            else:
                next_interval = interval
                num_candles = 1

            # Use a deque to ensure we only have the required number of candles stored to build up larger timeframes
            candle_tracker[symbol][interval_friendly] = deque(maxlen=num_candles)
            candles = market_client.get_ohlc(
                pair=symbol,
                interval=interval,
                since=int((started_at - timedelta(minutes=next_interval)).timestamp())
            )
            # Reformat the data to resemble websocket candles
            for candle in candles[symbol]:
                interval_begin = datetime.fromtimestamp(candle[0])
                candle_tracker[symbol][interval_friendly].append({
                    "interval_begin": interval_begin.isoformat() + '.000000000Z',
                    "symbol": symbol,
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "vwap": float(candle[5]),
                    "volume": float(candle[6]),
                    "trades": candle[7],
                    "timestamp": (interval_begin + timedelta(minutes=interval)).isoformat() + '.000000Z',
                })

            points = await format_influxdb_ohlc(candle_tracker[symbol][interval_friendly])
            write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{interval_friendly}", record=points)


async def main():
    mqtt_client = connect_mqtt()
    mqtt_client.loop_start()

    symbols_to_watch = ["XRP/EUR", "BTC/EUR"]

    await populate_candle_tracker_data(symbols=symbols_to_watch)

    ws_client = KrakenSpotWSClientV2(callback=partial(message_callback, mqtt_client))
    await ws_client.subscribe(
        params={
            "channel": "ohlc",
            "interval": 1,
            "symbol": symbols_to_watch,
            "snapshot": False,
        },
    )

    while not ws_client.exception_occur:
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