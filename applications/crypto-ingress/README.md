# Crypto Ingress

- TLDR: Subscribes to kraken websockets
- Keeps track of last candlesticks
- Publishes all OHLC updates to MQTT and InfluxDB for 1m timeframes
    - Possible to get multiple or 0 messages per 1m timeframe, server infills periods of time with 0 trades
        - 🙋‍ What happens when we have no trades within 5 minutes and the influxdb task downsamples a period with 0
          data.
          Maybe it's a better idea to have another async task (rxpy?) that 1s after every minute creates an empty candle
          if we recieved no data in the last minute, using the same `candle_tracker` hashmap.
            - Observed: Telesys API development, querying for last 4h 15m candlesticks + current 15m candlestick
              aggregated
              from 5m candles. No data for 5 minutes because no trades for 5 minutes (2024-02-25T02:15:00.000Z ->
              2024-02-25T02:20:00.000Z)
- Sets up InfluxDB buckets and tasks to downsample/aggregate data to 1m -> 5m -> 15m -> 1h -> 4h -> 1d -> 1w

# Ideas:

- Start up app
- Initialize an empty hashmap like so
  ```
    {symbol: {"1m": {}, "5m": {}, "15m": {}, "1h": {}, "4h": {}, "1d": {}, "1w": {}}
  ```
- Subscribe to OHLC 1m, 5m, 15m, 1h, 4h, 1d, 1w updates via kraken websocket API
    - For every timeframe:
        - Store the latest n candlesticks in order to build up the higher timeframe, the Kraken websocket API will
          return the last 10 candlesticks for each timeframe upon startup
        - For every timeframe except `1m`:
            - Unsubscribe from OHLC updates after storing the first batch of candles, we can now go on to using 1m
              candles to aggregate them up
            - Set the key for the timeframe to `initialized: True`
        - Update the latest `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, and `1w` candle if the symbol's `initialized` is True
    - Every minute:
        - Infill missing `1m` timeframe data, for example if there are no trades in the last minute, this is because
          the kraken WSS API will not send any candles if there are no trades
        - Update the latest `5m`, `15m`, `1h`, `4h`, `1d`, or `1w` and `1w` candle
        - Look at every symbol's `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, and `1w` latest candle
          - If the current time (UTC) is > the latest candle's `timestamp` then we need to 


TODO: Diagram of ingress process, real documentation
