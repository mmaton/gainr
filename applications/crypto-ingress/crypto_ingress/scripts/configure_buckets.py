"""
Create OHLC bucket:
-
"""
import argparse
from enum import Enum
from textwrap import dedent

from crypto_ingress import config
from crypto_ingress.config import influxdb_client, ENVIRONMENT
from influxdb_client.rest import ApiException
from influxdb_client.domain.task_create_request import TaskCreateRequest


TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
# E.g 1*2 seconds after the 5th minute we run ohlc_downsample_5m,
# then 2*2 seconds for ohlc_downsample_15m and so on.
DOWNSAMPLE_OFFSET_MULTIPLIER = 2
env = ENVIRONMENT


class Action(Enum):
    INSTALL = 'install'
    UNINSTALL = 'uninstall'

    def __str__(self):
        return self.value


def install():
    for tf in TIMEFRAMES:
        try:
            influxdb_client.buckets_api().create_bucket(bucket_name=f"{env}_ohlc_{tf}")
            config.logger.info(f"Created bucket {env}_ohlc_{tf}")
        except ApiException as e:
            if f"bucket with name {env}_ohlc_{tf} already exists" in e.message:
                pass
                config.logger.info(f"Not creating bucket {env}_ohlc_{tf}, it already exists!")
            else:
                raise e


def uninstall():
    for tf in TIMEFRAMES:
        find_bucket = influxdb_client.buckets_api().find_bucket_by_name(bucket_name=f"{env}_ohlc_{tf}")
        if find_bucket:
            influxdb_client.buckets_api().delete_bucket(bucket=find_bucket)
            config.logger.info(f"Deleted bucket {env}_ohlc_{tf}")
        else:
            config.logger.info(f"Not deleting bucket {env}_ohlc_{tf}, it doesn't exist!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=Action, default=Action.INSTALL)
    args = parser.parse_args()

    if args.action == Action.INSTALL:
        install()
    else:
        uninstall()
