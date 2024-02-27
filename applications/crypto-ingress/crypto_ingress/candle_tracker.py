import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, List

import tenacity
from kraken.spot import Market

from crypto_ingress.config import logger, MQTT_OHLC_TOPIC_BASE, write_api, ENVIRONMENT
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc

candle_tracker: dict[str, dict[int: Deque[dict]]] = defaultdict(dict)


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


def aggregate_up(symbol: str, from_tf: str, to_tf: str):
    """
    Returns the aggregated up `to_tf`, this may include a new candle
    """
    from_candles = candle_tracker[symbol][from_tf]
    to_candles = candle_tracker[symbol][to_tf]
    from_interval_begin = from_candles[-1]["interval_begin"][:-1]
    to_timestamp = to_candles[-1]["timestamp"][:-1]

    # Do we need to create a new candle in the to_candles (e.g every 5, 15, ... 10080 minutes)
    if datetime.fromisoformat(from_interval_begin) >= datetime.fromisoformat(to_timestamp):
        last_candle = from_candles[-1]
        mins_for_tf = get_minutes_for_timeframe(to_tf)
        next_begin = datetime.fromisoformat(to_candles[-1]["interval_begin"][:-1]) + timedelta(minutes=mins_for_tf)
        next_timestamp = datetime.fromisoformat(to_candles[-1]["timestamp"][:-1]) + timedelta(minutes=mins_for_tf)

        candle_tracker[symbol][to_tf].append({
            "symbol": last_candle["symbol"],
            "interval_begin": next_begin.isoformat() + '.000000000Z',
            "timestamp": next_timestamp.isoformat() + '.000000Z',
            "open": last_candle["open"],
            "high": last_candle["high"],
            "low":  last_candle["low"],
            "close": last_candle["close"],
            "volume": last_candle["volume"],
            "trades": last_candle["trades"],
        })
    # Update the latest candle in the to_candles
    else:
        agg_candles = [c for c in from_candles if c["interval_begin"] >= to_candles[-1]["interval_begin"]]
        candle_tracker[symbol][to_tf][-1] |= {
            "open": agg_candles[0]["open"],
            "high": max([c["high"] for c in agg_candles]),
            "low": min([c["low"] for c in agg_candles]),
            "close": agg_candles[-1]["close"],
            "volume": sum(c["volume"] for c in agg_candles),
            "trades": sum(c["trades"] for c in agg_candles),
        }


async def aggregate_1m_candles_up(candle: dict, mqtt_client) -> None:
    new_candles: dict[str, List[dict]] = defaultdict(list)  # timeframe: [candles]

    symbol = candle["symbol"]
    candle.pop("interval", "")

    # Update or create a new candle in the 1m timeframe for the current candle's symbol
    symbol_1m_timeframe = candle_tracker[symbol]["1m"]
    curr_interval_begin = datetime.fromisoformat(candle["interval_begin"][:-1])
    last_interval_begin = datetime.fromisoformat(symbol_1m_timeframe[-1]["interval_begin"][:-1])
    last_timestamp = datetime.fromisoformat(symbol_1m_timeframe[-1]["timestamp"][:-1])

    # Don't add 0 volume scheduled placeholder candles if we already have data from the WS
    if curr_interval_begin == last_interval_begin and candle["trades"] == 0:
        return

    # New candle needed in our candle_tracker - deque means oldest will be dropped
    # Update the `interval_begin` to the `timestamp` of the previous candle
    if curr_interval_begin >= last_timestamp:
        candle_tracker[symbol]["1m"].append(candle)

    # Update the current 1m candle with the new OHLC data from WS
    elif curr_interval_begin == last_interval_begin:
        # Update current candle
        candle_tracker[symbol]["1m"][-1] = {
            "symbol": symbol,
            "interval_begin": candle["interval_begin"],
            "timestamp": candle["timestamp"],
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low":float(candle["low"]),
            "close": float(candle["close"]),
            "volume": float(candle["volume"]),
            "trades": int(candle["trades"]),
        }

    # We'll need to write this new candle to influxdb
    new_candles["1m"].append(candle_tracker[symbol]["1m"][-1])

    from_tf = "1m"
    logger.debug(f"New candle for {symbol} {from_tf}: {candle_tracker[symbol][from_tf][-1]}")

    # Aggregate up this new data to higher timeframes
    for to_tf in ["5m", "15m", "1h", "4h", "1d", "1w"]:
        aggregate_up(symbol, from_tf, to_tf)
        from_tf = to_tf
        new_candles[to_tf].append(candle_tracker[symbol][to_tf][-1])
        logger.debug(f"New candle for {symbol} {to_tf}: {candle_tracker[symbol][to_tf][-1]}")

    # Now notify MQTT and store in influx
    for timeframe, candles in new_candles.items():
        for candle in candles:
            mqtt_client.publish(
                MQTT_OHLC_TOPIC_BASE + f"/ohlc_{timeframe}/{candle.get('symbol')}",
                json.dumps(candle)
            )
        points = await format_influxdb_ohlc(candles)
        write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{timeframe}", record=points)
    logger.info(f"Wrote candles for each timeframe")


async def populate_candle_tracker_data(symbols) -> None:
    market_client = Market()
    intervals = [(1, "1m"), (5, "5m"), (15, "15m"), (60, "1h"), (240, "4h"), (1440, "1d"), (10080, "1w")]
    started_at = datetime.now()

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

            @tenacity.retry(
                wait=tenacity.wait_random_exponential(multiplier=1, max=60),
                stop=tenacity.stop_after_delay(60),
                reraise=True,
            )
            def get_candles():
                return market_client.get_ohlc(
                    pair=symbol,
                    interval=interval,
                    since=int((started_at - timedelta(minutes=next_interval)).timestamp())
                )
            candles = get_candles()

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
                    "volume": float(candle[6]),
                    "trades": candle[7],
                    "timestamp": (interval_begin + timedelta(minutes=interval)).isoformat() + '.000000Z',
                })

            points = await format_influxdb_ohlc(candle_tracker[symbol][interval_friendly])
            # Keeps influx up to date in case of any downtime
            write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{interval_friendly}", record=points)
