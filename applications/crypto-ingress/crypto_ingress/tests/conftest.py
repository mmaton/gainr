from unittest.mock import MagicMock
from influxdb_client import InfluxDBClient

from crypto_ingress import config

config.influxdb_client = MagicMock(InfluxDBClient)
