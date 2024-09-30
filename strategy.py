import backtrader as bt
import numpy as np
import streamlit as st

# Define the Custom Backtrader Strategy
class CustomStrategy(bt.Strategy):
    params = (
        ('short_window', 10),
        ('long_window', 30),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('use_stop_loss', False),
        ('stop_loss_percent', 1.0),
        ('macd_short', 12),
        ('macd_long', 26),
        ('macd_signal', 9)
    )

    def __init__(self):
        self.order = None
        self.log_messages = []
        self.total_buy_trades = 0
        self.total_sell_trades = 0
        self.profitable_trades = 0
        self.trade_returns = []
        self.profit_losses = []

        # Initialize indicators based on user selections
        if st.session_state.get('use_sma'):
            self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_window)
            self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_window)
        
        if st.session_state.get('use_ema'):
            self.short_ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.short_window)
            self.long_ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.long_window)

        if st.session_state.get('use_rsi'):
            self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)

        if st.session_state.get('use_macd'):
            self.macd = bt.indicators.MACD(self.data.close, 
                                            period_me1=self.params.macd_short,
                                            period_me2=self.params.macd_long,
                                            period_signal=self.params.macd_signal)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        self.log_messages.append(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED !! {order.executed.price}")
                self.total_buy_trades += 1
                if self.params.use_stop_loss:
                    self.stop_loss_price = order.executed.price * (1 - self.params.stop_loss_percent / 100)
            elif order.issell():
                self.log(f"SELL EXECUTED !! {order.executed.price}")
                self.total_sell_trades += 1
                profit_loss = order.executed.price - self.buy_price
                self.profit_losses.append(profit_loss)
                self.trade_returns.append(profit_loss / self.buy_price)
                if profit_loss > 0:
                    self.profitable_trades += 1
        self.order = None

    def next(self):
        self.log(f'Close, {self.data.close[0]:.2f}')
        if self.order:
            return

        if not self.position:
            buy_signal = False

            if st.session_state.get('use_sma') and self.short_ma[0] > self.long_ma[0]:
                buy_signal = True
            if st.session_state.get('use_ema') and self.short_ema[0] > self.long_ema[0]:
                buy_signal = True
            if st.session_state.get('use_rsi') and self.rsi[0] < self.params.rsi_oversold:
                buy_signal = True
            if st.session_state.get('use_macd') and self.macd.macd[0] > self.macd.signal[0]:
                buy_signal = True

            if buy_signal:
                self.log(f'BUY CREATE, {self.data.close[0]:.2f}')
                self.buy_price = self.data.close[0]
                self.order = self.buy()
        else:
            if self.params.use_stop_loss and self.data.close[0] < self.stop_loss_price:
                self.log(f'STOP-LOSS TRIGGERED, SELL CREATE, {self.data.close[0]:.2f}')
                self.order = self.sell()
            else:
                sell_signal = False

                if st.session_state.get('use_sma') and self.short_ma[0] < self.long_ma[0]:
                    sell_signal = True
                if st.session_state.get('use_ema') and self.short_ema[0] < self.long_ema[0]:
                    sell_signal = True
                if st.session_state.get('use_rsi') and self.rsi[0] > self.params.rsi_overbought:
                    sell_signal = True
                if st.session_state.get('use_macd') and self.macd.macd[0] < self.macd.signal[0]:
                    sell_signal = True

                if sell_signal:
                    self.log(f'SELL CREATE, {self.data.close[0]:.2f}')
                    self.order = self.sell()

    def stop(self):
        total_trades = self.total_buy_trades + self.total_sell_trades
        win_rate = (self.profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Sharpe Ratio
        if self.trade_returns:
            mean_return = sum(self.trade_returns) / len(self.trade_returns)
            volatility = (sum((x - mean_return) ** 2 for x in self.trade_returns) / len(self.trade_returns)) ** 0.5
            sharpe_ratio = mean_return / volatility if volatility != 0 else 0
        else:
            sharpe_ratio = 0

        # Maximum Drawdown
        cumulative_returns = [sum(self.trade_returns[:i+1]) for i in range(len(self.trade_returns))]
        peak = cumulative_returns[0]
        max_drawdown = 0
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        self.log(f'Win Rate: {win_rate:.2f}%')
        self.log(f'Sharpe Ratio: {sharpe_ratio:.2f}')
        self.log(f'Maximum Drawdown: {max_drawdown:.2f}')

        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
