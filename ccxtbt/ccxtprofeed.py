# https://github.com/ccxt/ccxt/blob/master/examples/ccxt.pro/py/binance-watch-ohlcv.py
import time

import ccxt.pro
from asyncio import run
import queue
import threading
# print('CCXT Pro version', ccxt.pro.__version__)


class TimeframeSubscribe():
    def __init__(self,symbol,timeframe,_queue):
        self.symbol = symbol
        self.timeframe = timeframe
        self._queue = _queue
        self.timeframe = '1m'
        print(self.timeframe,self.symbol)

    def table(self,values):
        first = values[0]
        keys = list(first.keys()) if isinstance(first, dict) else range(0, len(first))
        widths = [max([len(str(v[k])) for v in values]) for k in keys]
        string = ' | '.join(['{:<' + str(w) + '}' for w in widths])
        return "\n".join([string.format(*[str(v[k]) for k in keys]) for v in values])

    def parse_timeframe(self,timeframe_str):
        # Extract the numeric part and the unit part
        value = int(timeframe_str[:-1])
        unit = timeframe_str[-1]

        # Convert the timeframe to milliseconds
        if unit == 'm':
            return value * 60000  # minutes to milliseconds
        elif unit == 'h':
            return value * 3600000  # hours to milliseconds
        elif unit == 'd':
            return value * 86400000  # days to milliseconds
        else:
            raise ValueError("Invalid timeframe unit. Use 'm' for minutes, 'h' for hours, or 'd' for days.")

    def is_new_timeframe_start(self,now, last, timeframe_str):
        # Convert the timeframe string to milliseconds
        timeframe = self.parse_timeframe(timeframe_str)

        # Convert milliseconds to integers
        now = int(now)
        last = int(last)

        # Calculate the timeframes for now and last
        now_timeframe = now // timeframe
        last_timeframe = last // timeframe

        # Check if now is the start of a new timeframe
        return now_timeframe != last_timeframe

    async def main(self):
        exchange = ccxt.pro.binance({
            'options': {
                'OHLCVLimit': 1000,  # how many candles to store in memory by default
                'defaultType': 'future'
            },
        })
        # symbol = 'ETH/USDT'  # or BNB/USDT, etc...
        # timeframe = '1m'  # 5m, 1h, 1d
        limit = 10  # how many candles to return max
        method = 'watchOHLCV'
        last_ohlcv = []
        last_time = 0
        if (method in exchange.has) and exchange.has[method]:
            max_iterations = 100000  # how many times to repeat the loop before exiting
            for i in range(0, max_iterations):
                try:
                    ohlcvs = await exchange.watch_ohlcv(self.symbol,self.timeframe, None, limit)
                    now = exchange.milliseconds()
                    r = self.is_new_timeframe_start(now, last_time,self.timeframe)
                    if r is True and len(last_ohlcv) != 0:
                        # print(self.table([[exchange.iso8601(o[0])] + o[1:] for o in last_ohlcv]))
                        self._queue.put(last_ohlcv)
                    last_time = now
                    last_ohlcv = ohlcvs
                    print('Loop iteration:', i, 'current time:', exchange.iso8601(now), self.symbol, self.timeframe)

                except Exception as e:
                    print(type(e).__name__, str(e))
                    break
            await exchange.close()
        else:
            print(exchange.id, method, 'is not supported or not implemented yet')

    def start(self):
        run(self.main())

# if __name__ == '__main__':
#     timeframe = '1m'
#     symbol = 'ETH/USDT'
#     q = queue.Queue()
#     _run = TimeframeSubscribe(symbol, timeframe, q)
#     producer_thread = threading.Thread(target=_run.start)
#     producer_thread.start()
#     data = q.get()
#     if data is not None:
#         print(data)
#     time.sleep(1)