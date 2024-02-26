import logging

from environs import Env
from influxdb_client import InfluxDBClient
import sentry_sdk

env = Env()

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

if env.str("SENTRY_DSN", ""):
    sentry_sdk.init(
        dsn="https://47ca2931367402cbb606d89f0096d517@o4506804531625984.ingest.sentry.io/4506804537065472",
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.05,
    )

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

MQTT_OHLC_TOPIC_BASE = f"gainr/{ENVIRONMENT}"
