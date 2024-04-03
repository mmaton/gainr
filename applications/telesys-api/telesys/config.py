import logging
from random import randint

import sentry_sdk
from influxdb_client import InfluxDBClient
from environs import Env

env = Env()

if env.str("SENTRY_DSN", ""):
    sentry_sdk.init(
        dsn=env.str("SENTRY_DSN"),
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.05,
    )

DEBUG = env.bool("DEBUG", False)
ENVIRONMENT = env.str("ENVIRONMENT", "local")

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
INFLUXDB_HOST = "http://" if not INFLUXDB_HOST.startswith("http://") else INFLUXDB_HOST

INFLUXDB_TOKEN = env.str('INFLUXDB_TOKEN')
INFLUXDB_ORG = 'influxdata'

# InfluxDB connection
influxdb_client = InfluxDBClient(url=INFLUXDB_HOST, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# MQTT
MQTT_BROKER = env.str("MQTT_BROKER", "emqx-listeners.emqx-mqtt.svc.cluster.local")
MQTT_PORT = 1883
MQTT_CLIENT_ID = env.str("HOSTNAME", f"unknown-host{randint(100, 200)}")
MQTT_USERNAME = env.str("MQTT_USERNAME", "gainr-backend")
MQTT_PASSWORD = env.str("MQTT_PASSWORD")

