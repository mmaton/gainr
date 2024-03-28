import logging

import sentry_sdk
from environs import Env


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
        dsn=env.str("SENTRY_DSN"),
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

# MQTT
MQTT_BROKER = env.str("MQTT_BROKER", "emqx-listeners.emqx-mqtt.svc.cluster.local")
MQTT_PORT = 1883
MQTT_CLIENT_ID = env.str("HOSTNAME", "unknown-host")
MQTT_USERNAME = env.str("MQTT_USERNAME", "gainr-backend")
MQTT_PASSWORD = env.str("MQTT_PASSWORD")

MQTT_OHLC_TOPIC_BASE = f"gainr/{ENVIRONMENT}"

# Kraken - Trading
KRAKEN_KEY = env.str("KRAKEN_KEY", "")
KRAKEN_SECRET = env.str("KRAKEN_SECRET", "")
OHLC_INTERVALS = [(1, "1m"), (5, "5m"), (15, "15m"), (60, "1h"), (240, "4h"), (1440, "1d"), (10080, "1w")]
SYMBOLS_TO_WATCH = ["BTC/EUR", "XRP/EUR"]
