# Start off with 1m candles
# Schedule every minute creates the next candle
# 1m window stores 6x 1m candles, one in the future
# Times      : [-4m, -3m, -2m, -1m, now, +1m]
# Num Trades : [5  , 0  , 10 , 0  , 3  , 0  ]
from collections import deque
from datetime import datetime, timedelta

import asyncio

current_minute = datetime.now().replace(second=0, microsecond=0)

candles_1m = deque(
    [{"interval_begin": (current_minute - timedelta(minutes=m)).isoformat()} for m in range(4, -2, -1)],
    maxlen=6
)

print(candles_1m)


async def ohlc_1m_candle_creator():
    while True:
        next_interval = datetime.fromisoformat(candles_1m[-1]["interval_begin"]) + timedelta(minutes=1)
        candles_1m.append({"interval_begin": next_interval.isoformat()})
        print(candles_1m)
        await asyncio.sleep((next_interval - datetime.now()).total_seconds())


asyncio.run(ohlc_1m_candle_creator())
