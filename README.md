# TradingAlgo
## Backtesting App

This application allows users to backtest trading strategies using historical market data. It utilizes the Backtrader framework for backtesting and Streamlit for the user interface.

## File Structure

```
    ├── app.py # Main application code 
    ├── strategy.py # Contains the strategy implementation ├── data_fetch.py # Handles data fetching logic 
    ├── plot_utils.py # Contains plotting functions 
    ├── requirements.txt # Python package dependencies 
    └── README.md # Documentation
```


## How to Run

1. Clone the repository.
2. Install the required packages:

`pip install -r requirements.txt`

3. Run the application:
`streamlit run app.py`



## Features

- Handle large historical data.
- User-defined input parameters.
- Strategy implementation and signal generation.
- Backtesting across multiple timeframes.

## Coming Soon

We are continuously working to enhance the application. Upcoming features include:

- **Options and Futures Support**: Ability to backtest options and futures strategies.
- **Additional Indicators**: Incorporation of more technical indicators such as Bollinger Bands, Stochastic Oscillator, and more.

Stay tuned for these exciting updates!

## Contributing

Feel free to contribute to the project by submitting issues or pull requests.


