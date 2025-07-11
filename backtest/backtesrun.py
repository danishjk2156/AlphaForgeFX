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
    portfolio_values = []

    class EquityLogger(bt.Observer):
        lines = ('equity',)

        def next(self):
            self.lines.equity[0] = self._owner.broker.getvalue()

            cerebro.addobserver(EquityLogger)
            cerebro.addobserver(bt.observers.Value)


            cerebro.broker.setcash(100000)
            cerebro.broker.setcommission(commission=0.0001)
                
            results = cerebro.run()
            return cerebro, results[0]

    class SMARSI(bt.Strategy):
        params = (
            ('sma_period', 20),
            ('rsi_period', 14),
            ('rsi_overbought', 70),
            ('rsi_oversold', 30),
        )

    def __init__(self):
        self.sma = bt.ind.SMA(period=self.params.sma_period)
        self.rsi = bt.ind.RSI(period=self.params.rsi_period)
        self.order = None
        self.trades = []

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.rsi < self.params.rsi_oversold and self.data.close[0] > self.sma[0]:
                self.order = self.buy()
        else:
            if self.rsi > self.params.rsi_overbought:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            action = "BUY" if order.isbuy() else "SELL"
            self.trades.append({
                "Date": self.data.datetime.date(0).strftime("%Y-%m-%d"),
                "Action": action,
                "Price": order.executed.price,
                "Size": order.executed.size,
                "PnL": order.executed.pnl,
            })
        self.order = None
        results = cerebro.run()
        strat = results[0]

        # Recalculate true equity curve from broker
        equity_curve = [v[0] for v in cerebro.runstop()]
        dates = df.index[:len(equity_curve)]

        equity_df = pd.DataFrame({"Equity": equity_curve}, index=dates)

        trades_df = pd.DataFrame(strat.trades)

        num_trades = len(trades_df)
        win_trades = trades_df[trades_df['PnL'] > 0]
        win_rate = round(len(win_trades) / num_trades * 100, 2) if num_trades > 0 else 0

        metrics = {
            "Final Portfolio Value": round(cerebro.broker.getvalue(), 2),
            "Total Trades": num_trades,
            "Winning Trades": len(win_trades),
            "Win Rate (%)": win_rate,
            "Sharpe Ratio": strat.analyzers.sharpe.get_analysis().get('sharperatio', 'N/A')
        }

        return {
            "equity_curve": equity_df,
            "metrics": metrics,
            "trades": trades_df
        }

