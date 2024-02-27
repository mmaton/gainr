from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest
from influxdb_client import InfluxDBClient
from paho.mqtt import client as mqtt_client

from crypto_ingress import candle_tracker
from crypto_ingress import config, mqtt
from crypto_ingress.server import candle_queue
from crypto_ingress.tests.candle_tracker_data import mock_candle_tracker_data

config.influxdb_client = MagicMock(InfluxDBClient)
mqtt.paho_client = MagicMock(mqtt_client)


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


@pytest.fixture(scope="function", autouse=True)
def mock_mqtt_client():
    client = mqtt.connect_mqtt()
    yield client
    client.reset_mock()


@pytest.fixture(scope="function", autouse=True)
async def reset_candle_queue():
    while not candle_queue.empty():
        await candle_queue.get()


@pytest.fixture(scope="function", autouse=True)
def mock_influx_client():
    with patch('crypto_ingress.influxdb.InfluxClient') as mock_client:
        mock_client.write_api.return_value = AsyncMock()
        mock_client.__new__.return_value = "test"
        yield mock_client


@pytest.fixture(scope="function")
def mock_candle_tracker():
    candle_tracker.candle_tracker = deepcopy(mock_candle_tracker_data)
    yield candle_tracker.candle_tracker
