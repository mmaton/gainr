# Crypto Ingress
- TLDR: Subscribes to kraken websockets
- Keeps track of last candlesticks
- Publishes all OHLC updates to MQTT and InfluxDB for 1m timeframes
  - Possible to get multiple or 0 messages per 1m timeframe, server infills periods of time with 0 trades
     - 🙋‍ What happens when we have no trades within 5 minutes and the influxdb task downsamples a period with 0 data.
        Maybe it's a better idea to have another async task (rxpy?) that 1s after every minute creates an empty candle
        if we recieved no data in the last minute, using the same `candle_tracker` hashmap.
- Sets up InfluxDB buckets and tasks to downsample/aggregate data to 1m -> 5m -> 15m -> 1h -> 4h -> 1d -> 1w


TODO: Diagram of ingress process, real documentation
