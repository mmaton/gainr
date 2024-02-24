from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from influxdb_client import Point

from crypto_ingress.config import influxdb_client
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.server import message_callback, infill_missing_candles


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

    async def test_message_callback_with_ohlc_data(self, ohlc_data, dummy_mqtt_client):
        message = {"channel": "ohlc", "data": ohlc_data}
        write_api = influxdb_client.write_api()
        await message_callback(dummy_mqtt_client, message)
        assert write_api.write.called
        call_kwargs = write_api.write.call_args.kwargs
        assert call_kwargs['bucket'] == "ohlc_1m"
        assert isinstance(call_kwargs['record'][0], Point)
        assert len(call_kwargs['record']) == 1

    async def test_message_callback_with_ping(self, dummy_mqtt_client):
        call = await message_callback(dummy_mqtt_client, {"method": "pong"})
        assert call is None

    async def test_infill_missing_candles(self, ohlc_data):
        ohlc_data.append(deepcopy(ohlc_data[0]))
        ohlc_data[1]["interval_begin"] = "2024-02-22T09:45:00.000000000Z"

        infill = await infill_missing_candles(ohlc_data)
        assert len(infill) == 4
        assert infill[1]["interval_begin"] == "2024-02-22T09:43:00.000000000Z"
        assert infill[2]["interval_begin"] == "2024-02-22T09:44:00.000000000Z"

    async def test_infill_missing_candles_does_not_create_extra_unnecessary_candles(self, ohlc_data):
        infill = await infill_missing_candles(ohlc_data)
        assert len(infill) == 1

    async def test_infill_missing_candles_saves_last_candle_between_calls(self, ohlc_data):
        infill = await infill_missing_candles(ohlc_data)
        assert len(infill) == 1

        for i in range(3, 6):
            data_after = deepcopy(ohlc_data)
            data_after[0]["interval_begin"] = f"2024-02-22T09:4{i}:00.000000000Z"
            infill = await infill_missing_candles(data_after)
            assert len(infill) == 1

    async def test_infilling_missing_candles_on_receiving_previous_and_next_candles(self, ohlc_data, dummy_mqtt_client):
        data_before = ohlc_data
        data_after = deepcopy(ohlc_data)
        data_after[0]["interval_begin"] = "2024-02-22T09:45:00.000000000Z"
        write_api = influxdb_client.write_api()
        await message_callback(dummy_mqtt_client, {"channel": "ohlc", "data": data_before})
        await message_callback(dummy_mqtt_client, {"channel": "ohlc", "data": data_after})

        second_write_points = write_api.write.call_args_list[1][1]['record']
        start_timestamp = datetime.fromisoformat(data_before[0]["interval_begin"][:-1])

        for i in range(1, 4):
            expected_interval_begin = start_timestamp + timedelta(minutes=i)
            assert second_write_points[i - 1]._time == expected_interval_begin

        assert dummy_mqtt_client.publish.call_count == 4

    async def test_infill_on_first_candle_does_nothing(self, ohlc_data):
        infilled_candles = await infill_missing_candles(ohlc_data)
        assert len(infilled_candles) == 1

    async def test_infill_does_not_add_candles_on_multiple_candles_within_same_begin_interval(self, ohlc_data):
        for i in range(5):
            ohlc_data[0]["trades"] = i
            infilled_candles = await infill_missing_candles(ohlc_data)
            assert len(infilled_candles) == 1
