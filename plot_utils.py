import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objs as go


def plot_data(data, name, price_type):
    """Plot stock prices and moving averages using Plotly."""
    data['50_SMA'] = data['Close'].rolling(window=50).mean()
    fig = go.Figure()

    # Price trace
    fig.add_trace(go.Scatter(x=data.index, y=data[price_type],
                             mode='lines', name=f'{price_type} Prices', line=dict(width=2)))
    # 50-day SMA trace
    fig.add_trace(go.Scatter(x=data.index, y=data['50_SMA'],
                             mode='lines', name='50-day SMA', line=dict(color='orange', width=2)))
    # Volume trace
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'],
                         name='Volume', yaxis='y2', opacity=0.5))

    # Update layout
    fig.update_layout(
        title=f'{price_type} Prices for {name}',
        xaxis_title='Date',
        yaxis_title=f'{price_type} Price',
        yaxis2=dict(title='Volume', overlaying='y', side='right'),
        hovermode='x unified',
        xaxis_rangeslider_visible=True
    )

    # Last price annotation
    last_date = data.index[-1]
    last_price = data[price_type].iloc[-1]
    fig.add_annotation(x=last_date, y=last_price,
                       text=f'Last {price_type}: {last_price:.2f}',
                       showarrow=True, arrowhead=2, ax=0, ay=-40)

    st.plotly_chart(fig)
