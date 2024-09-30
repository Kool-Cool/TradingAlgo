import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data
def fetch_data(symbol, start, end):
    """Fetch stock data from Yahoo Finance and cache it."""
    data = yf.download(symbol, start=start, end=end)
    return data
