from datetime import datetime
from typing import Optional

from telesys.config import influxdb_client, ENVIRONMENT
from telesys.enums import Interval


def validate_symbol(symbol: str):
    """
    Raise exception if influx has no data by that symbol name or the symbol has no "/"
    """
    if "/" not in symbol:
        raise Exception("Symbol is missing a / separator between currency pairs!")

    query_api = influxdb_client.query_api()
    count = query_api.query(f"""
        from(bucket: "{ENVIRONMENT}_ohlc_1m")
            |> range(start: -10y)
            |> filter(fn: (r) => r["_measurement"] == "{symbol}")
            |> limit(n: 1)
            |> count()
    """)
    if not count:
        raise Exception("No data for that symbol!")


def get_mins_for_tf(timeframe: str) -> int:
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


async def get_candles_for_tf(
        symbol: str,
        interval: Optional[Interval] = None,
        since: Optional[datetime] = None,
):
    query_api = influxdb_client.query_api()
    records = query_api.query_stream(f"""
        from(bucket: "{ENVIRONMENT}_ohlc_{interval.value}")
            |> range(start: {since.isoformat()}Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "{symbol}")
            |> sort(columns: ["_time"])
            |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    """)
    return records
