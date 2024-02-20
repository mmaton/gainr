from datetime import datetime
from typing import List

from influxdb_client import Point
from influxdb_client.client.write_api import WritePrecision


async def format_influxdb_ohlc(data: List[dict]) -> List[Point]:
    influxdb_points = [
        (
            Point(f"{entry['symbol']}")
            .time(datetime.fromisoformat(entry['timestamp'][:-1]), write_precision=WritePrecision.MS)
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
