"""
Create OHLC bucket:
-
"""
import argparse
from enum import Enum
from textwrap import dedent

from crypto_ingress import config
from crypto_ingress.config import influxdb_client
from influxdb_client.rest import ApiException
from influxdb_client.domain.task_create_request import TaskCreateRequest


TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
# E.g 1*2 seconds after the 5th minute we run ohlc_downsample_5m,
# then 2*2 seconds for ohlc_downsample_15m and so on.
DOWNSAMPLE_OFFSET_MULTIPLIER = 2


class Action(Enum):
    INSTALL = 'install'
    UNINSTALL = 'uninstall'

    def __str__(self):
        return self.value


def create_downsample_query(from_timeframe: str, to_timeframe: str, offset: int = 0):
    # https://community.influxdata.com/t/flux-multiple-aggregates/10221/8
    flux = dedent(f'''
        import "date"
        option task = {{name: "ohlc_downsample_{to_timeframe}", every: {to_timeframe}, offset: {offset}s}}
        
        data = () =>  from(bucket: "ohlc_{from_timeframe}")
         |> range(
                start: date.sub(d: {to_timeframe}, from: date.truncate(t: now(), unit: {to_timeframe})),
                stop: date.truncate(t: now(), unit: {to_timeframe})
            )
         |> sort(columns: ["_time"])
        
        aggregate = (tables=<-, filterFn, agg, name) =>
                    tables
                        |> filter(fn: filterFn)
                        |> aggregateWindow(every: {to_timeframe}, fn: agg)
                        |> set(key: "_field", value: name)
                        |> duplicate(column: "_start", as: "_time")
        
        union(
            tables: [
                data() |> aggregate(filterFn: (r) => r._field == "open", agg: first, name: "open"),
                data() |> aggregate(filterFn: (r) => r._field == "high", agg: max, name: "high"),
                data() |> aggregate(filterFn: (r) => r._field == "low", agg: min, name: "low"),
                data() |> aggregate(filterFn: (r) => r._field == "close", agg: last, name: "close"),
                data() |> aggregate(filterFn: (r) => r._field == "trades", agg: sum, name: "trades"),
                data() |> aggregate(filterFn: (r) => r._field == "volume", agg: sum, name: "volume"),
            ],
        )
        |> to(bucket: "ohlc_{to_timeframe}", org: "influxdata")
    ''')
    return TaskCreateRequest(
        org=config.INFLUXDB_ORG,
        flux=flux,
    )


def install():
    last_tf = None
    offset_count = 1
    for tf in TIMEFRAMES:
        try:
            influxdb_client.buckets_api().create_bucket(bucket_name=f"ohlc_{tf}")
            config.logger.info(f"Created bucket ohlc_{tf}")
        except ApiException as e:
            if f"bucket with name ohlc_{tf} already exists" in e.message:
                pass
                config.logger.info(f"Not creating bucket ohlc_{tf}, it already exists!")
            else:
                raise e

        if last_tf:
            find_task = influxdb_client.tasks_api().find_tasks(name=f"ohlc_downsample_{tf}")
            offset = offset_count * DOWNSAMPLE_OFFSET_MULTIPLIER
            query = create_downsample_query(from_timeframe=last_tf, to_timeframe=tf, offset=offset)
            if not find_task:
                # Create task
                influxdb_client.tasks_api().create_task(task_create_request=query)
                config.logger.info(f"Created downsample task ohlc_downsample_{tf}")
            else:
                # Update
                find_task[0].flux = query.flux
                influxdb_client.tasks_api().update_task(task=find_task[0])
                config.logger.info(f"Updated downsample task ohlc_downsample_{tf}")
            offset += 1

        last_tf = tf


def uninstall():
    last_tf = None
    for tf in TIMEFRAMES:
        find_bucket = influxdb_client.buckets_api().find_bucket_by_name(bucket_name=f"ohlc_{tf}")
        if find_bucket:
            influxdb_client.buckets_api().delete_bucket(bucket=find_bucket)
            config.logger.info(f"Deleted bucket ohlc_{tf}")
        else:
            config.logger.info(f"Not deleting bucket ohlc_{tf}, it doesn't exist!")

        if last_tf:
            find_task = influxdb_client.tasks_api().find_tasks(name=f"ohlc_downsample_{tf}")
            if find_task:
                # Delete
                influxdb_client.tasks_api().delete_task(task_id=find_task[0].id)
                config.logger.info(f"Deleted downsample task ohlc_downsample_{tf}")

        last_tf = tf


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=Action, default=Action.INSTALL)
    args = parser.parse_args()

    if args.action == Action.INSTALL:
        install()
    else:
        uninstall()
