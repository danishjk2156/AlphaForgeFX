import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def next(self):
        if self.position.size == 0:
            if self.data.close[0] > self.sma[0] and self.rsi[0] < self.params.rsi_oversold:
                self.buy()
        else:
            if self.rsi[0] > self.params.rsi_overbought:
                self.close()
