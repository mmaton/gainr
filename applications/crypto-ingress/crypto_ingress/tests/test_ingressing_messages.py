from datetime import datetime

import pytest
from influxdb_client import Point

from crypto_ingress.config import influxdb_client
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc
from crypto_ingress.server import message_callback


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
