import logging

from environs import Env
from influxdb_client import InfluxDBClient

env = Env()

DEBUG = env.bool("DEBUG", False)

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG if DEBUG else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# InfluxDB settings
INFLUXDB_HOST = env.str('INFLUXDB_HOST')
INFLUXDB_TOKEN = env.str('INFLUXDB_TOKEN')
INFLUXDB_ORG = 'influxdata'

# InfluxDB connection
influxdb_client = InfluxDBClient(url=INFLUXDB_HOST, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# MQTT
MQTT_BROKER = env.str("MQTT_BROKER", "emqx-listeners.emqx-mqtt.svc.cluster.local")
MQTT_PORT = 1883
MQTT_CLIENT_ID = env.str("HOSTNAME", "unknown-host")
MQTT_USERNAME = env.str("MQTT_USERNAME", "gainr-backend")
MQTT_PASSWORD = env.str("MQTT_PASSWORD")

MQTT_OHLC_TOPIC_BASE = "gainr/ohlc_1m"
