import pytest

from unittest.mock import MagicMock
from influxdb_client import InfluxDBClient
from paho.mqtt import client as mqtt_client

from crypto_ingress import config, mqtt

config.influxdb_client = MagicMock(InfluxDBClient)
mqtt.paho_client = MagicMock(mqtt_client)


@pytest.fixture(scope="function", autouse=True)
def dummy_mqtt_client():
    client = mqtt.connect_mqtt()
    yield client
    client.reset_mock()


@pytest.fixture(scope="function", autouse=True)
def dummy_influx_client():
    client = config.influxdb_client
    yield client
    client.reset_mock()


@pytest.fixture(scope="function", autouse=True)
def reset_candle_tracker():
    from crypto_ingress import server
    server.candle_tracker = {}
