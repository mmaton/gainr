from datetime import datetime, timedelta

import pytest

from crypto_ingress.candle_tracker import aggregate_up, create_or_update_1m_candle_and_aggregate_up
from crypto_ingress.config import OHLC_INTERVALS
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.server import message_callback, candle_queue


class TestCryptoIngress:
    """
    Just happy-path testing for now
    """
    @pytest.fixture
    def ohlc_data(self):
        return [
            {
                'symbol': 'BTC/EUR',
                'open': 47765.0,
                'high': 47792.1,
                'low': 47764.9,
                'close': 47792.1,
                'trades': 26,
                'volume': 0.21876281,
                'vwap': 47782.8,
                'interval_begin': '2024-02-22T09:42:00.000000000Z',
                'interval': 1,
                'timestamp': '2024-02-22T09:43:00.000000Z'
            }
        ]

    async def test_influxdb_point_formatter(self, ohlc_data):
        candles = await format_influxdb_ohlc(ohlc_data)
        point = candles[0]
        assert vars(point) == {
            '_tags': {},
            '_fields': {
                'open': 47765.0,
                'high': 47792.1,
                'low': 47764.9,
                'close': 47792.1,
                'volume': 0.21876281,
                'trades': 26
            },
            '_name': 'BTC/EUR',
            '_time': datetime(2024, 2, 22, 9, 42),
            '_write_precision': 'ns',
            '_field_types': {}
        }
        assert len(candles) == 1

    async def test_message_callback_with_ohlc_data(self, ohlc_data):
        await message_callback({"channel": "ohlc", "data": ohlc_data})
        assert candle_queue.qsize() == 1

    async def test_message_callback_with_ping_does_nothing(self, reset_candle_queue):
        await message_callback({"method": "pong"})
        assert candle_queue.qsize() == 0

    async def test_aggregating_up_latest_1m_candlestick_to_5m(self, mock_candle_tracker):
        mock_candle_tracker["BTC/EUR"]["1m"][-1]["volume"] += 10
        previous_5m_volume = mock_candle_tracker["BTC/EUR"]["5m"][-1]["volume"]
        aggregate_up(symbol="BTC/EUR", from_tf="1m", to_tf="5m")

        assert mock_candle_tracker["BTC/EUR"]["5m"][-1]["volume"] == previous_5m_volume + 10

    async def test_aggregating_up_on_new_1m_candle_creates_new_5m_candle(self, mock_candle_tracker):
        last_1m_candle = mock_candle_tracker["BTC/EUR"]["1m"][-1]
        last_5m_candle = mock_candle_tracker["BTC/EUR"]["5m"][-1]
        curr_interval_begin = datetime.fromisoformat(last_1m_candle["interval_begin"][:-1])

        mock_candle_tracker["BTC/EUR"]["1m"].append({
            "symbol": "BTC/EUR",
            "interval_begin": (curr_interval_begin + timedelta(minutes=1)).isoformat() + '.000000000Z',
            "timestamp": (curr_interval_begin + timedelta(minutes=2)).isoformat() + '.000000Z',
            "open": last_1m_candle["close"],
            "high": last_1m_candle["high"],
            "low": last_1m_candle["low"],
            "close": last_1m_candle["close"],
            "volume": float(0),
            "trades": 0,
        })
        aggregate_up(symbol="BTC/EUR", from_tf="1m", to_tf="5m")

        assert mock_candle_tracker["BTC/EUR"]["5m"][-1] != last_5m_candle
        assert mock_candle_tracker["BTC/EUR"]["5m"][-2] == last_5m_candle

        last_5m_begin_interval = datetime.fromisoformat(last_5m_candle["interval_begin"][:-1])
        new_5m_begin_interval = datetime.fromisoformat(mock_candle_tracker["BTC/EUR"]["5m"][-1]["interval_begin"][:-1])
        assert new_5m_begin_interval == last_5m_begin_interval + timedelta(minutes=5)

    async def test_pushing_empty_candle_for_same_begin_interval_does_not_create_new_candle_and_agg_up(
            self,
            mock_candle_tracker,
            mock_mqtt_client,
            mock_influx_client,
    ):
        new_candle = mock_candle_tracker["BTC/EUR"]["1m"][-1] | {"volume": float(0), "trades": 0}

        await create_or_update_1m_candle_and_aggregate_up(new_candle, mock_mqtt_client, mock_influx_client.write_api())
        assert mock_candle_tracker["BTC/EUR"]["1m"][-1]["volume"] != 0.0

    async def test_pushing_new_0_volume_candle_for_next_tf_aggregates_data_up(
            self,
            mock_candle_tracker,
            mock_mqtt_client,
            mock_influx_client
    ):
        write_api = mock_influx_client.write_api()
        last_1m_candle = mock_candle_tracker["BTC/EUR"]["1m"][-1]
        curr_interval_begin = datetime.fromisoformat(last_1m_candle["interval_begin"][:-1])

        new_candle = {
            "symbol": "BTC/EUR",
            "interval_begin": (curr_interval_begin + timedelta(minutes=1)).isoformat() + '.000000000Z',
            "timestamp": (curr_interval_begin + timedelta(minutes=2)).isoformat() + '.000000Z',
            "open": last_1m_candle["close"],
            "high": last_1m_candle["high"],
            "low": last_1m_candle["low"],
            "close": last_1m_candle["close"],
            "volume": float(0),
            "trades": 0,
        }
        await create_or_update_1m_candle_and_aggregate_up(new_candle, mock_mqtt_client, write_api)
        assert len(write_api.write.call_args_list) == len(OHLC_INTERVALS)

        for call_idx, (_, tf) in enumerate(OHLC_INTERVALS):
            call_as_dict = write_api.write.call_args_list[call_idx][1]
            assert call_as_dict["bucket"] == f"local_ohlc_{tf}"
            assert len(call_as_dict["record"]) == 1
