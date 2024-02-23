import pytest

from unittest.mock import MagicMock
from influxdb_client import InfluxDBClient
from paho.mqtt import client as mqtt_client

from crypto_ingress import config, mqtt

config.influxdb_client = MagicMock(InfluxDBClient)
mqtt.paho_client = MagicMock(mqtt_client)


@pytest.fixture(scope="session")
def dummy_mqtt_client():
    yield mqtt.connect_mqtt()