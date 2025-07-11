import backtrader as bt
import pandas as pd
from strategy.custom_strategies import BaseStrategy

def run_backtest(datafile, strategy_params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BaseStrategy, **strategy_params)

    df = pd.read_csv(datafile, index_col='Date', parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    data = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(data)
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.0001)
    
    results = cerebro.run()
    return cerebro, results[0]
