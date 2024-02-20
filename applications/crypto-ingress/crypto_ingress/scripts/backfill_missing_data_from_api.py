"""
We can only get up to 720 candles from the Kraken REST API, this means we will have insufficient data to produce
linear regression on e.g 1m, 5m, 15m, 1h candles between the last candle in CSV imported data and where the worker
indexed recent 1m OHLC data.

But we can still work on higher timeframes.
- Find the beginning of the most recent gap in OHLC candlesticks for 1m, 5m, 15m, 1h, 4h, 1d candles in influx
- Call the Kraken REST API to get candlesticks at that timeframe for the interval
- Index the 720 candlesticks

720 hours = 30 days
"""
