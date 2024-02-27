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

from crypto_ingress.config import ENVIRONMENT
from crypto_ingress.influxdb import InfluxClient
from crypto_ingress.influxdb_point_formats import format_influxdb_ohlc


parser = argparse.ArgumentParser(
    prog='bulk-index',
    description='Takes an OHLCV csv from kraken and imports it into the ohlc bucket in influxdb',
)
parser.add_argument('csv_file_path')
parser.add_argument('interval')
parser.add_argument('pair')


async def main(csv_file_path: str, interval: int, pair: str):
    chunk_size = 500

    path = Path(csv_file_path)

    async with InfluxClient() as influx_client:
        write_api = influx_client.write_api()
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
                await write_api.write(bucket=f"{ENVIRONMENT}_ohlc_{interval}", record=influxdb_points)
                print(f"Wrote {len(chunk)} candles from {data[0]['timestamp']} to {data[-1]['timestamp']}")


if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(main(csv_file_path=args.csv_file_path, interval=args.interval, pair=args.pair))
