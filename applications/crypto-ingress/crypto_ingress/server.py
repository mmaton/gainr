import asyncio
from datetime import datetime, timedelta

from kraken.spot import KrakenSpotWSClientV2

from crypto_ingress.candle_tracker import candle_tracker, create_or_update_1m_candle_and_aggregate_up, populate_candle_tracker_data
from crypto_ingress.config import logger, SYMBOLS_TO_WATCH
from crypto_ingress.influxdb import InfluxClient
from crypto_ingress.mqtt import connect_mqtt

candle_queue: asyncio.Queue[int] = asyncio.Queue()


async def message_callback(message):
    if message.get("method") == "pong" or message.get("channel") == "heartbeat":
        return

    if message.get("channel") == "ohlc":
        for candle in message.get("data", []):
            logger.debug(candle)
            await candle_queue.put(candle)


async def ohlc_1m_candle_creator():
    """
    At the beginning of every minute, for every symbol, write a new candle to the 1m candle tracker
    """
    while True:
        for symbol, timeframes in candle_tracker.items():
            curr_minute = datetime.now().replace(second=0, microsecond=0)
            last_candle = timeframes["1m"][-1]
            await candle_queue.put({
                "symbol": symbol,
                "interval_begin": curr_minute.isoformat() + '.000000000Z',
                "timestamp": (curr_minute + timedelta(minutes=1)).isoformat() + '.000000Z',
                "open": last_candle["close"],
                "high": last_candle["high"],
                "low": last_candle["low"],
                "close": last_candle["close"],
                "volume": float(0),
                "trades": 0,
            })

        in_one_minute = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        await asyncio.sleep((in_one_minute - datetime.now()).total_seconds())


async def candle_handler(mqtt_client, write_api):
    while True:
        candle = await candle_queue.get()
        await create_or_update_1m_candle_and_aggregate_up(candle, mqtt_client, write_api)


async def kraken_subscription(symbols):
    ws_client = KrakenSpotWSClientV2(callback=message_callback)
    await ws_client.subscribe(
        params={
            "channel": "ohlc",
            "interval": 1,
            "symbol": symbols,
            "snapshot": False,
        },
    )
    while not ws_client.exception_occur:
        await asyncio.sleep(6)


async def main():
    async with InfluxClient() as influx_client:
        write_api = influx_client.write_api()
        await populate_candle_tracker_data(symbols=SYMBOLS_TO_WATCH, write_api=write_api)

        mqtt_client = connect_mqtt()
        mqtt_client.loop_start()

        await asyncio.gather(
            kraken_subscription(SYMBOLS_TO_WATCH),
            ohlc_1m_candle_creator(),
            candle_handler(mqtt_client, write_api)
        )

        mqtt_client.loop_stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        # The websocket client will send {'event': 'asyncio.CancelledError'}
        # via on_message, so you can handle the behavior/next actions individually within your strategy.
