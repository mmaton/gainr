"""
USAGE:
    poetry run python crypto_ingress/scripts/bulk_index_into_influxdb.py <path to csv> <interval> <pair>
e.g:
    poetry run python crypto_ingress/scripts/bulk_index_into_influxdb.py ../../data/XRPEUR_1.csv 1m XRP/EUR
"""


import argparse
from datetime import datetime
from pathlib import Path

import asyncio
from influxdb_client.client.write_api import SYNCHRONOUS

from crypto_ingress.config import influxdb_client, ENVIRONMENT
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc


parser = argparse.ArgumentParser(
    prog='bulk-index',
    description='Takes an OHLCV csv from kraken and imports it into the ohlc bucket in influxdb',
)
parser.add_argument('csv_file_path')
parser.add_argument('interval')
parser.add_argument('pair')


def bulk_write_influxdb(client, data, interval: str):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{interval}", record=data)


async def main(csv_file_path: str, interval: int, pair: str):
    chunk_size = 500

    path = Path(csv_file_path)

    with path.open(mode='r') as csv_file:
        while True:
            chunk = [next(csv_file, None) for _ in range(chunk_size)]
            if chunk[-1] is None:
                chunk = list(filter(None, chunk))
            if not chunk:
                break  # Reached the end of the file

            data = []
            for row in chunk:
                row = row.rstrip('\n').split(',')
                data.append({
                    'timestamp': datetime.fromtimestamp(int(row[0])).isoformat() + "Z",
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4]),
                    'volume': float(row[5]),
                    'trades': int(row[6]),
                    'interval': interval,
                    'symbol': pair,

                })

            influxdb_points = await format_influxdb_ohlc(data)
            bulk_write_influxdb(influxdb_client, influxdb_points)
            print(f"Wrote {len(chunk)} candles from {data[0]['timestamp']} to {data[-1]['timestamp']}")


if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(main(csv_file_path=args.csv_file_path, interval=args.interval, pair=args.pair))
