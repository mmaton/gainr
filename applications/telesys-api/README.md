# Telesys
Telesys is an API server which subscribes to influx metrics and exposes them via a streaming graphql endpoint

# Notes:
Say the client wants to query 4h candlesticks 

We have the ohlc_4h bucket in influx but up until the last completed 4h candlestick which was aggregated up
from smaller timeframes (1h in this case)

We should query ohlc_4h for `n` candlesticks (where start == the left hand side of the chart)

Then we should query the current candlestick and aggregate the two together before sending to the client

Query to aggregate up the last lower timeframe for the current window (in this case the last 15-minute stick):
```flux
import "date"

data = () =>  from(bucket: "ohlc_5m")
    |> range(start: date.truncate(t: now(), unit: 15m))
    // optional filter on crypto |> filter(fn: (r) => r["_measurement"] == "XRP/EUR")
    |> sort(columns: ["_time"])

aggregate = (tables=<-, filterFn, agg, name) =>
            tables
                |> filter(fn: filterFn)
                |> aggregateWindow(every: 15m, fn: agg)
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

|> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
```

Query to get the last 4hr of 15 minute candlesticks, aggregate the last 5m candlesticks, and union join the two
```flux
import "date"
import "join"

prev = from(bucket: "ohlc_15m")
    |> range(start: -4h)
    // |> filter(fn: (r) => r["_measurement"] == "XRP/EUR")
    |> sort(columns: ["_time"])

data = () =>  from(bucket: "ohlc_5m")
    |> range(start: date.truncate(t: now(), unit: 15m))
    // |> filter(fn: (r) => r["_measurement"] == "XRP/EUR")
    |> sort(columns: ["_time"])

aggregate = (tables=<-, filterFn, agg, name) =>
            tables
                |> filter(fn: filterFn)
                |> aggregateWindow(every: 15m, fn: agg)
                |> set(key: "_field", value: name)
                |> duplicate(column: "_start", as: "_time")

curr = union(
    tables: [
        data() |> aggregate(filterFn: (r) => r._field == "open", agg: first, name: "open"),
        data() |> aggregate(filterFn: (r) => r._field == "high", agg: max, name: "high"),
        data() |> aggregate(filterFn: (r) => r._field == "low", agg: min, name: "low"),
        data() |> aggregate(filterFn: (r) => r._field == "close", agg: last, name: "close"),
        data() |> aggregate(filterFn: (r) => r._field == "trades", agg: sum, name: "trades"),
        data() |> aggregate(filterFn: (r) => r._field == "volume", agg: sum, name: "volume"),
    ],
)

union(tables: [prev, curr])
    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```
