import backtrader as bt
from datetime import date, datetime, time, timedelta

class CrossOver(bt.Strategy):
    """A simple moving average crossover strategy,
    at SMA 50/200 a.k.a. the "Golden Cross Strategy"
    """
    params = (('fast', 50),
              ('slow', 200),
              ('order_pct', 0.95),
              ('market', 'BTC/USD')
              )

    def __init__(self):
        sma = bt.indicators.SimpleMovingAverage
        cross = bt.indicators.CrossOver
        self.fastma = sma(self.data.close,
                          period=self.p.fast,
                          plotname='FastMA')
        sma = bt.indicators.SimpleMovingAverage
        self.slowma = sma(self.data.close,
                          period=self.p.slow,
                          plotname='SlowMA')
        self.crossover = cross(self.fastma, self.slowma)

    def start(self):
        self.size = None

    def log(self, txt, dt=None):
        """ Logging function for this strategy
        """
        dt = dt or self.datas[0].datetime.date(0)
        time = self.datas[0].datetime.time()
        print('%s - %s, %s' % (dt.isoformat(), time, txt))

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0:
                amount_to_invest = (self.p.order_pct *
                                    self.broker.cash)
                self.size = amount_to_invest / self.data.close
                msg = "*** MKT: {} BUY: {}"
                self.log(msg.format(self.p.market, self.size))
                self.buy(size=self.size)

        if self.position.size > 0:
            # we have an open position or made it to the end of backtest
            last_candle = (self.data.close.buflen() == len(self.data.close) + 1)
            if (self.crossover < 0) or last_candle:
                msg = "*** MKT: {} SELL: {}"
                self.log(msg.format(self.p.market, self.size))
                self.close()

class OpeningRangeBreakout(bt.Strategy):
    
    params = dict(
        num_opening_bars=15
    )

    def __init__(self):
        self.opening_range_low = 0
        self.opening_range_high = 0
        self.opening_range = 0
        self.bought_today = False
        self.order = None
    
    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime()

        print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            order_details = f"{order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}"

            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order_details}")
            else:  # Sell
                self.log(f"SELL EXECUTED, Price: {order_details}")
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        current_bar_datetime = self.data.num2date(self.data.datetime[0])
        previous_bar_datetime = self.data.num2date(self.data.datetime[-1])

        if current_bar_datetime.date() != previous_bar_datetime.date():
            self.opening_range_low = self.data.low[0]
            self.opening_range_high = self.data.high[0]
            self.bought_today = False
        
        opening_range_start_time = time(9, 30, 0)
        dt = datetime.combine(date.today(), opening_range_start_time) + timedelta(minutes=self.p.num_opening_bars)
        opening_range_end_time = dt.time()

        if current_bar_datetime.time() >= opening_range_start_time \
            and current_bar_datetime.time() < opening_range_end_time:           
            self.opening_range_high = max(self.data.high[0], self.opening_range_high)
            self.opening_range_low = min(self.data.low[0], self.opening_range_low)
            self.opening_range = self.opening_range_high - self.opening_range_low
        else:
            if self.order:
                return
            
            if self.position and (self.data.close[0] > (self.opening_range_high + self.opening_range)):
                self.close()
                
            if self.data.close[0] > self.opening_range_high and not self.position and not self.bought_today:
                self.order = self.buy()
                self.bought_today = True

            if self.position and (self.data.close[0] < (self.opening_range_high - self.opening_range)):
                self.order = self.close()

            # liquidate at 2:45pm EST
            if self.position and current_bar_datetime.time() >= time(14, 45, 0):
                self.log("RUNNING OUT OF TIME - LIQUIDATING POSITION")
                self.close()

    def stop(self):
        self.log('(Num Opening Bars %2d) Ending Value %.2f' %
                 (self.params.num_opening_bars, self.broker.getvalue()))

        if self.broker.getvalue() > 130000:
            self.log("*** BIG WINNER ***")

        if self.broker.getvalue() < 70000:
            self.log("*** MAJOR LOSER ***")