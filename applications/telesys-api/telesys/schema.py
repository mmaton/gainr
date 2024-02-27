import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional, AsyncGenerator, Annotated

import strawberry

from telesys.config import ENVIRONMENT
from telesys.enums import Interval
from telesys.influx_queries import get_candles_for_tf, get_mins_for_tf
from telesys.mqtt import connect_mqtt


@strawberry.type
class OHLCData:
    begin: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int
    symbol: str


@strawberry.type
class Query:
    @strawberry.field
    async def ohlc(
            self,
            interval: Optional[Interval] = Interval.MINUTE,
            symbol: Annotated[
                Optional[str],
                strawberry.argument(description="Filter by pair, e.g 'XRP/EUR'")
            ] = "XRP/EUR",
            since: Annotated[
                Optional[datetime],
                strawberry.argument(description="Defaults to start at 5x `interval`"),
            ] = None,
    ) -> Optional[List[OHLCData]]:
        candles = []
        since = datetime.now() - timedelta(minutes=5 * get_mins_for_tf(interval.value)) if not since else since

        for point in await get_candles_for_tf(symbol=symbol, interval=interval, since=since):
            candles.append(OHLCData(
                begin=point.values["_time"],
                open=point.values["open"],
                high=point.values["high"],
                low=point.values["low"],
                close=point.values["close"],
                volume=point.values["volume"],
                trades=point.values["trades"],
                symbol=point.values["_measurement"],
            ))

        return candles


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def ohlc(
            self,
            interval: Optional[Interval] = Interval.MINUTE,
            symbol: Annotated[
                Optional[str],
                strawberry.argument(description="Filter by pair, e.g 'XRP/EUR'")
            ] = "XRP/EUR",
            since: Annotated[
                Optional[datetime],
                strawberry.argument(description="Defaults to start at 5x `interval`"),
            ] = None,
    ) -> AsyncGenerator[OHLCData, None]:
        candles = asyncio.Queue()
        since = datetime.now() - timedelta(minutes=5 * get_mins_for_tf(interval.value)) if not since else since

        for point in await get_candles_for_tf(symbol=symbol, interval=interval, since=since):
            await candles.put(
                OHLCData(
                    begin=point.values["_time"],
                    open=point.values["open"],
                    high=point.values["high"],
                    low=point.values["low"],
                    close=point.values["close"],
                    volume=point.values["volume"],
                    trades=point.values["trades"],
                    symbol=point.values["_measurement"],
                )
            )

        # Callback when a message is received from MQTT
        def on_message(client, userdata, msg):
            payload = json.loads(msg.payload)
            candles.put_nowait(
                OHLCData(
                    begin=datetime.fromisoformat(payload["interval_begin"][:-1]).replace(tzinfo=timezone.utc),
                    open=payload["open"],
                    high=payload["high"],
                    low=payload["low"],
                    close=payload["close"],
                    volume=payload["volume"],
                    trades=payload["trades"],
                    symbol=payload["symbol"],
                )
            )

        mqtt_client = connect_mqtt()
        mqtt_client.on_message = on_message
        mqtt_client.loop_start()
        mqtt_client.subscribe(f"gainr/{ENVIRONMENT}/ohlc_{interval.value}/{symbol}")
        try:
            while True:
                yield await candles.get()
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            print("Cancelled")
            mqtt_client.unsubscribe(f"gainr/{ENVIRONMENT}/ohlc_{interval.value}/{symbol}")
            mqtt_client.loop_stop()
