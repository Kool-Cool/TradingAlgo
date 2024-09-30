import streamlit as st
import backtrader as bt
from datetime import datetime
from strategy import CustomStrategy
from data_fetch import fetch_data
from plot_utils import plot_data


# Streamlit App
st.set_page_config(page_title="Backtesting with Backtrader", layout="wide")

# Dictionary of stocks and indices
stocks_dict = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "State Bank of India": "SBIN.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Larsen & Toubro": "LT.NS",
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Sensex": "^BSESN"
}

st.title('📈 Backtesting with Backtrader')

# User selection
selected_company = st.sidebar.selectbox("Select a company or index:", list(stocks_dict.keys()))
ticker = stocks_dict[selected_company]

# Input for date range
start_date = st.sidebar.date_input("Start Date", value=datetime(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.today())
if start_date > end_date:
    st.error("Start date cannot be after end date.")

# Strategy Parameters
st.sidebar.header("Select Strategy Parameters")
short_window = st.sidebar.slider("Short Moving Average Window", 1, 50, 10)
long_window = st.sidebar.slider("Long Moving Average Window", 1, 50, 30)
rsi_period = st.sidebar.slider("RSI Period", 1, 50, 14)
rsi_overbought = st.sidebar.slider("RSI Overbought Level", 50, 100, 70)
rsi_oversold = st.sidebar.slider("RSI Oversold Level", 0, 50, 30)
stop_loss_percent = st.sidebar.slider("Stop-Loss Percentage", 0.0, 10.0, 1.0)

# MACD parameters
st.sidebar.header("MACD Parameters")
macd_short = st.sidebar.slider("MACD Short Period", 1, 50, 12)
macd_long = st.sidebar.slider("MACD Long Period", 1, 50, 26)
macd_signal = st.sidebar.slider("MACD Signal Period", 1, 50, 9)

# Indicator selection
st.sidebar.header("Select Indicators")
st.sidebar.checkbox("Use Short Moving Average", key='use_sma', value=True)
st.sidebar.checkbox("Use Long Moving Average", key='use_lma', value=True)
st.sidebar.checkbox("Use RSI", key='use_rsi', value=True)
st.sidebar.checkbox("Use Exponential Moving Average", key='use_ema', value=True)
st.sidebar.checkbox("Use MACD", key='use_macd', value=True)
st.sidebar.checkbox("Enable Stop-Loss", key='use_stop_loss', value=True)

if st.button("Run Backtest"):
    # Download data using yfinance
    data = fetch_data(ticker, start=start_date, end=end_date)

    # Check if data was fetched successfully
    if data.empty:
        st.error("No data fetched. Please check the ticker and date range.")
    else:
        # Plot stock data
        plot_data(data, selected_company, 'Close')

        # Prepare data for Backtrader
        data_bt = bt.feeds.PandasData(dataname=data)

        # Initialize Cerebro
        cerebro = bt.Cerebro()
        cerebro.adddata(data_bt)

        # Add strategy with user-defined parameters
        cerebro.addstrategy(CustomStrategy, 
                             short_window=short_window, 
                             long_window=long_window, 
                             rsi_period=rsi_period, 
                             rsi_overbought=rsi_overbought, 
                             rsi_oversold=rsi_oversold,
                             use_stop_loss=st.session_state['use_stop_loss'], 
                             stop_loss_percent=stop_loss_percent, 
                             macd_short=macd_short, 
                             macd_long=macd_long, 
                             macd_signal=macd_signal)
        
        initial_value = 1000000.0  # Initial balance
        cerebro.broker.setcash(initial_value)

        # Run the backtest
        results = cerebro.run()

        # Access the logs from the last strategy instance
        strategy_instance = results[0]
        log_messages = strategy_instance.log_messages

        # Get final balance and calculate net profit/loss
        final_value = cerebro.broker.getvalue()
        net_profit_loss = final_value - initial_value  

        # Display results in a more structured way
        st.markdown(f"### Initial Balance: **${initial_value:.2f}**")
        st.markdown(f"### Final Balance: **${final_value:.2f}**")
        st.markdown(f"### Net Profit/Loss: **${net_profit_loss:.2f}**")
        st.markdown(f"### Total Buy Trades: **{strategy_instance.total_buy_trades}**")
        st.markdown(f"### Total Sell Trades: **{strategy_instance.total_sell_trades}**")
        st.markdown(f"### Win Rate: **{strategy_instance.profitable_trades / (strategy_instance.total_buy_trades + strategy_instance.total_sell_trades) * 100:.2f}%**")
        st.markdown(f'### Sharpe Ratio: {strategy_instance.sharpe_ratio:.2f}')  # Ensure sharpe_ratio is calculated correctly
        st.markdown(f'### Maximum Drawdown: {strategy_instance.max_drawdown:.2f}')  # Ensure max_drawdown is calculated correctly

        # Show logs in a scrollable div
        with st.expander("View Log Messages", expanded=False):
            for msg in log_messages:
                st.text(msg)

        # Plot the results
        fig = cerebro.plot()[0][0]  
        st.pyplot(fig)
