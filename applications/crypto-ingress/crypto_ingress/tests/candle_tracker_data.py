# flake8: noqa E501

from collections import deque

mock_candle_tracker_data = {
    'BTC/EUR': {
        '1m': deque(maxlen=5, iterable=[
            {'interval_begin': '2024-02-27T15:45:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52564.6, 'high': 52605.9, 'low': 52561.5, 'close': 52582.1, 'volume': 0.15886208, 'trades': 14, 'timestamp': '2024-02-27T15:46:00.000000Z'},
            {'interval_begin': '2024-02-27T15:46:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52582.1, 'high': 52582.1, 'low': 52560.3, 'close': 52560.3, 'volume': 2.51024945, 'trades': 29, 'timestamp': '2024-02-27T15:47:00.000000Z'},
            {'interval_begin': '2024-02-27T15:47:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52560.4, 'high': 52560.4, 'low': 52484.2, 'close': 52486.3, 'volume': 2.31040103, 'trades': 39, 'timestamp': '2024-02-27T15:48:00.000000Z'},
            {'interval_begin': '2024-02-27T15:48:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52477.6, 'high': 52477.6, 'low': 52427.0, 'close': 52427.0, 'volume': 0.85255308, 'trades': 45, 'timestamp': '2024-02-27T15:49:00.000000Z'},
            {'interval_begin': '2024-02-27T15:49:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52427.1, 'high': 52427.1, 'low': 52381.6, 'close': 52381.6, 'volume': 0.68885234, 'trades': 45, 'timestamp': '2024-02-27T15:50:00.000000Z'}
        ]),
        '5m': deque(maxlen=3, iterable=[
            {'interval_begin': '2024-02-27T15:35:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52722.1, 'high': 52825.0, 'low': 52711.5, 'close': 52746.7, 'volume': 4.43370392, 'trades': 171, 'timestamp': '2024-02-27T15:40:00.000000Z'},
            {'interval_begin': '2024-02-27T15:40:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52746.7, 'high': 52750.0, 'low': 52560.3, 'close': 52560.3, 'volume': 7.32054538, 'trades': 131, 'timestamp': '2024-02-27T15:45:00.000000Z'},
            {'interval_begin': '2024-02-27T15:45:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52564.6, 'high': 52605.9, 'low': 52381.6, 'close': 52381.6, 'volume': 6.52091798, 'trades': 172, 'timestamp': '2024-02-27T15:50:00.000000Z'}
        ]),
        '15m': deque(maxlen=4, iterable=[
            {'interval_begin': '2024-02-27T15:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52593.9, 'high': 52684.9, 'low': 52427.3, 'close': 52591.1, 'volume': 16.82542787, 'trades': 428, 'timestamp': '2024-02-27T15:15:00.000000Z'},
            {'interval_begin': '2024-02-27T15:15:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52591.1, 'high': 52825.0, 'low': 52536.1, 'close': 52808.4, 'volume': 22.86850119, 'trades': 598, 'timestamp': '2024-02-27T15:30:00.000000Z'},
            {'interval_begin': '2024-02-27T15:30:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52808.5, 'high': 52825.0, 'low': 52560.3, 'close': 52560.3, 'volume': 15.35367572, 'trades': 419, 'timestamp': '2024-02-27T15:45:00.000000Z'},
            {'interval_begin': '2024-02-27T15:45:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52560.4, 'high': 52560.4, 'low': 52381.6, 'close': 52381.6, 'volume': 3.85180645, 'trades': 129, 'timestamp': '2024-02-27T16:00:00.000000Z'}
         ]),
        '1h': deque(maxlen=4, iterable=[
            {'interval_begin': '2024-02-27T12:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52050.0, 'high': 52850.0, 'low': 52041.3, 'close': 52299.4, 'volume': 69.21487187, 'trades': 2642, 'timestamp': '2024-02-27T13:00:00.000000Z'},
            {'interval_begin': '2024-02-27T13:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52300.0, 'high': 52688.5, 'low': 52162.4, 'close': 52662.9, 'volume': 86.99566809, 'trades': 2305, 'timestamp': '2024-02-27T14:00:00.000000Z'},
            {'interval_begin': '2024-02-27T14:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52662.9, 'high': 52848.1, 'low': 52252.5, 'close': 52593.9, 'volume': 70.71084175, 'trades': 2405, 'timestamp': '2024-02-27T15:00:00.000000Z'},
            {'interval_begin': '2024-02-27T15:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52593.9, 'high': 52825.0, 'low': 52381.6, 'close': 52381.6, 'volume': 58.89941123, 'trades': 1574, 'timestamp': '2024-02-27T16:00:00.000000Z'}
        ]),
        '4h': deque(maxlen=6, iterable=[
            {'interval_begin': '2024-02-26T16:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 48690.0, 'high': 50148.3, 'low': 48627.9, 'close': 50061.6, 'volume': 510.03734641, 'trades': 12062, 'timestamp': '2024-02-26T20:00:00.000000Z'},
            {'interval_begin': '2024-02-26T20:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 50080.3, 'high': 50450.0, 'low': 49762.9, 'close': 49926.9, 'volume': 259.33390743, 'trades': 8023, 'timestamp': '2024-02-27T00:00:00.000000Z'},
            {'interval_begin': '2024-02-27T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 49927.0, 'high': 51775.0, 'low': 49926.9, 'close': 51000.0, 'volume': 278.62346738, 'trades': 8125, 'timestamp': '2024-02-27T04:00:00.000000Z'},
            {'interval_begin': '2024-02-27T04:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 51000.0, 'high': 51900.0, 'low': 50999.9, 'close': 51636.7, 'volume': 225.48160102, 'trades': 7454, 'timestamp': '2024-02-27T08:00:00.000000Z'},
            {'interval_begin': '2024-02-27T08:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 51636.7, 'high': 52345.0, 'low': 51616.2, 'close': 52050.0, 'volume': 436.73300351, 'trades': 9864, 'timestamp': '2024-02-27T12:00:00.000000Z'},
            {'interval_begin': '2024-02-27T12:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 52050.0, 'high': 52850.0, 'low': 52041.3, 'close': 52381.6, 'volume': 285.82079294, 'trades': 8926, 'timestamp': '2024-02-27T16:00:00.000000Z'}
        ]),
        '1d': deque(maxlen=7, iterable=[
            {'interval_begin': '2024-02-21T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 48349.4, 'high': 48400.0, 'low': 46851.5, 'close': 47930.3, 'volume': 685.19985535, 'trades': 28692, 'timestamp': '2024-02-22T00:00:00.000000Z'},
            {'interval_begin': '2024-02-22T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 47934.0, 'high': 48070.0, 'low': 47051.0, 'close': 47370.0, 'volume': 602.52996557, 'trades': 22868, 'timestamp': '2024-02-23T00:00:00.000000Z'},
            {'interval_begin': '2024-02-23T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 47364.1, 'high': 47575.7, 'low': 46610.5, 'close': 46873.7, 'volume': 553.15647146, 'trades': 24015, 'timestamp': '2024-02-24T00:00:00.000000Z'},
            {'interval_begin': '2024-02-24T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 46873.7, 'high': 47710.0, 'low': 46731.0, 'close': 47622.0, 'volume': 232.73276113, 'trades': 15985, 'timestamp': '2024-02-25T00:00:00.000000Z'},
            {'interval_begin': '2024-02-25T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 47622.0, 'high': 47925.0, 'low': 47404.9, 'close': 47786.2, 'volume': 288.93431985, 'trades': 15672, 'timestamp': '2024-02-26T00:00:00.000000Z'},
            {'interval_begin': '2024-02-26T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 47793.5, 'high': 50450.0, 'low': 46950.1, 'close': 49926.9, 'volume': 1210.00976637, 'trades': 38506, 'timestamp': '2024-02-27T00:00:00.000000Z'},
            {'interval_begin': '2024-02-27T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 49927.0, 'high': 52850.0, 'low': 49926.9, 'close': 52381.6, 'volume': 1226.65886485, 'trades': 34369, 'timestamp': '2024-02-28T00:00:00.000000Z'}
        ]),
        '1w': deque(maxlen=1, iterable=[
            {'interval_begin': '2024-02-22T00:00:00.000000000Z', 'symbol': 'BTC/EUR', 'open': 47934.0, 'high': 52850.0, 'low': 46610.5, 'close': 52381.6, 'volume': 4114.02214923, 'trades': 151415, 'timestamp': '2024-02-29T00:00:00.000000Z'}
        ])
    }
}
