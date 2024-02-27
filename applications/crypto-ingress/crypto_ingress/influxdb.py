from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from crypto_ingress.config import INFLUXDB_HOST, INFLUXDB_TOKEN, INFLUXDB_ORG


class InfluxClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = InfluxDBClientAsync(url=INFLUXDB_HOST, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        return cls._instance
