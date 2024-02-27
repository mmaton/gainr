from datetime import datetime, timedelta
from typing import List, Iterable
from influxdb_client import Point
from influxdb_client.client.write_api import WritePrecision


async def format_influxdb_ohlc(data: Iterable[dict]) -> List[Point]:
    influxdb_points = [
        (
            Point(f"{entry['symbol']}")
            .time(datetime.fromisoformat(entry['interval_begin'][:-1]), write_precision=WritePrecision.NS)
            .field('open', entry['open'])
            .field('high', entry['high'])
            .field('low', entry['low'])
            .field('close', entry['close'])
            .field('volume', entry['volume'])
            .field('trades', entry['trades'])
        )
        for entry in data
    ]
    return influxdb_points


async def ohlc_to_dict(candles: List, symbol: str, interval: int) -> List[dict]:
    candles_as_dict = []
    for candle in candles:
        interval_begin = datetime.fromtimestamp(candle[0])
        candles_as_dict.append({
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
    return candles_as_dict
