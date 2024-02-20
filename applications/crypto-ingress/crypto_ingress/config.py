import logging

from influxdb_client import InfluxDBClient
from environs import Env

env = Env()

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# InfluxDB settings
INFLUXDB_HOST = env.str('INFLUXDB_HOST')
INFLUXDB_TOKEN = env.str('INFLUXDB_TOKEN')
INFLUXDB_ORG = 'influxdata'

# InfluxDB connection
influxdb_client = InfluxDBClient(url=INFLUXDB_HOST, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
