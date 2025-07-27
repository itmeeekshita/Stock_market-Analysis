import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
import time
import finnhub
import os

# Set page configuration and style
st.set_page_config(
    page_title="Stock Market Sentiment Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 16px;
    }
    .news-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sentiment-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation and Inputs
with st.sidebar: 
    st.image("https://img.icons8.com/color/96/000000/stocks.png", width=100)
    st.title("Navigation")
    st.markdown(
        '<span style="color: red; font-size: 14px;">Only US stocks are supported (e.g., AAPL, MSFT, TSLA).</span>',
        unsafe_allow_html=True
    )
    analysis_view = st.radio("Select Analysis", [
        "📊 Price Chart",
        "📈 Moving Average",
        "📰 News Sentiment",
        "🥧 Sentiment Distribution"
    ])
    st.markdown("---")
    ticker = st.text_input("Enter Stock Ticker Symbol:", "AAPL").upper()
    st.subheader("Select Date Range")
    today = datetime.now().date()
    default_start = today - timedelta(days=7)
    start_date = st.date_input("Start date", default_start, key="start_date")
    end_date = st.date_input("End date", today, key="end_date")
    if start_date > end_date:
        st.error("Start date must be before end date.")

# Get Finnhub API key from environment or prompt
api_key = os.getenv("FINNHUB_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your Finnhub API Key:", type="password")
    if not api_key:
        st.warning("Please provide a Finnhub API key to fetch data.")
        st.stop()

finnhub_client = finnhub.Client(api_key=api_key)

# Convert dates to UNIX timestamps
from_time = int(datetime.combine(start_date, datetime.min.time()).timestamp())
to_time = int(datetime.combine(end_date, datetime.min.time()).timestamp())

# Remove Finnhub historical data function and add Stooq function

def fetch_historical_data_stooq(ticker, start_date, end_date):
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    try:
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'])
        # Filter by date range
        mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
        df = df.loc[mask]
        df = df.rename(columns={'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'})
        return df
    except Exception as e:
        st.error(f"Error fetching historical data from Stooq: {e}")
        return pd.DataFrame()

# Fetch company news (Finnhub)
def fetch_company_news(ticker, start_date, end_date):
    try:
        res = finnhub_client.company_news(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        return pd.DataFrame(res)
    except Exception as e:
        st.error(f"Error fetching company news: {e}")
        return pd.DataFrame()

# Sentiment analysis for news headlines (unchanged)
def analyze_sentiment(df):
    if df.empty or 'headline' not in df.columns:
        return pd.DataFrame()
    def get_sentiment(text):
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        if polarity > 0.3:
            sentiment = "Very Positive"
        elif polarity > 0.05:
            sentiment = "Positive"
        elif polarity < -0.3:
            sentiment = "Very Negative"
        elif polarity < -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        return pd.Series([polarity, subjectivity, sentiment])
    sentiment_data = df['headline'].apply(get_sentiment)
    df = df.copy()
    df['sentiment_score'] = sentiment_data[0]
    df['subjectivity'] = sentiment_data[1]
    df['sentiment_label'] = sentiment_data[2]
    return df

# Fetch all data (use Stooq for historical)
historical_data = fetch_historical_data_stooq(ticker, start_date, end_date)
company_news = fetch_company_news(ticker, start_date, end_date)
sentiment_df = analyze_sentiment(company_news)

# Main title
st.title("📈 Stock Market Sentiment Analytics")

# --- SUMMARY SECTION ---
if not historical_data.empty:
    price_change = historical_data['Close'].iloc[-1] - historical_data['Close'].iloc[0]
    price_change_pct = (price_change / historical_data['Close'].iloc[0]) * 100
    max_price = historical_data['Close'].max()
    min_price = historical_data['Close'].min()
    volatility = max_price - min_price
    most_common_sentiment = sentiment_df['sentiment_label'].mode()[0] if not sentiment_df.empty else 'N/A'
    st.markdown(f"""
    ### 📋 Stock Summary
    - **Price change:** {price_change:.2f} USD ({price_change_pct:.2f}%)
    - **Highest close:** {max_price:.2f} USD
    - **Lowest close:** {min_price:.2f} USD
    - **Volatility:** {volatility:.2f} USD
    - **Most common news sentiment:** {most_common_sentiment}
    """)
    # Simple suggestion
    if price_change_pct > 2 and most_common_sentiment in ['Positive', 'Very Positive']:
        st.success("The outlook is positive (bullish). Many news articles are positive and the price is rising.")
    elif price_change_pct < -2 and most_common_sentiment in ['Negative', 'Very Negative']:
        st.error("The outlook is negative (bearish). Many news articles are negative and the price is falling.")
    else:
        st.info("The outlook is neutral. There is no strong trend in price or news sentiment.")
else:
    st.info("No price data available for summary.")

st.info("""
**How to read this dashboard:**
- The price change tells you if the stock went up or down in your selected period.
- Volatility is the difference between the highest and lowest closing prices (higher means more risk).
- News sentiment is based on recent headlines: positive, negative, or neutral.
- The outlook is a simple suggestion, not financial advice!
""")

# --- VISUALIZATIONS ---
if analysis_view == "📊 Price Chart":
    st.header(f"Price Chart for {ticker}")
    st.info("A candlestick chart shows the open, high, low, and close prices for each day. Green means the price went up, red means it went down.")
    if not historical_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=historical_data['Date'],
            open=historical_data['Open'],
            high=historical_data['High'],
            low=historical_data['Low'],
            close=historical_data['Close'],
            name='Price'))
        st.plotly_chart(fig, use_container_width=True)
        # Add a simple line chart for closing prices
        st.subheader("Closing Price Line Chart")
        st.line_chart(historical_data.set_index('Date')['Close'])
        st.info("This line chart shows how the closing price changed over time.")
        # Add a bar chart for volume
        st.subheader("Trading Volume")
        st.bar_chart(historical_data.set_index('Date')['Volume'])
        st.info("Volume is the number of shares traded each day. High volume can mean more interest or news.")
    else:
        st.warning("No price data available. Try a different date range or ticker.")

elif analysis_view == "📈 Moving Average":
    st.header(f"Moving Average for {ticker}")
    st.info("A moving average smooths out price data to help you see the trend. It's not a prediction, but it helps spot uptrends or downtrends.")
    if not historical_data.empty:
        window = st.slider("Select Moving Average Window (days)", 3, 30, 7)
        historical_data['SMA'] = historical_data['Close'].rolling(window=window).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=historical_data['Date'], y=historical_data['Close'], name='Close', line=dict(color='blue')))
        fig2.add_trace(go.Scatter(x=historical_data['Date'], y=historical_data['SMA'], name=f'{window}-day SMA', line=dict(color='orange')))
        fig2.update_layout(title=f"{ticker} Close Price & {window}-day SMA", xaxis_title='Date', yaxis_title='Price (USD)')
        st.plotly_chart(fig2, use_container_width=True)
        st.info(f"The orange line is the {window}-day moving average. If the blue line (price) is above the orange line, the stock is in an uptrend.")
    else:
        st.warning("No price data available. Try a different date range or ticker.")

elif analysis_view == "📰 News Sentiment":
    st.header(f"News Sentiment for {ticker}")
    st.info("This table shows recent news headlines and their sentiment analysis. Positive means the news is good for the stock, negative means bad news.")
    if not sentiment_df.empty:
        st.dataframe(sentiment_df[['datetime', 'headline', 'sentiment_label', 'sentiment_score', 'subjectivity']])
    else:
        st.warning("No news data or sentiment available for this period.")

elif analysis_view == "🥧 Sentiment Distribution":
    st.header(f"Sentiment Distribution for {ticker}")
    st.info("This donut chart shows the proportion of positive, negative, and neutral news sentiment. More green means more positive news.")
    if not sentiment_df.empty:
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        fig3 = go.Figure(data=[go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, hole=0.4)])
        fig3.update_layout(title="News Sentiment Distribution", annotations=[dict(text='Sentiment', x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No news data or sentiment available for this period.")

# --- EDUCATIONAL GLOSSARY ---
with st.expander("📚 Glossary: Stock Market Terms"):
    st.markdown("""
    - **Closing Price:** The last price at which the stock traded during the day.
    - **Volume:** The number of shares traded in a day.
    - **Moving Average (SMA):** The average closing price over a set number of days.
    - **Bullish:** Expecting the price to go up.
    - **Bearish:** Expecting the price to go down.
    - **Volatility:** How much the price moves up and down. High volatility = more risk.
    - **Sentiment:** The mood of news headlines (positive, negative, neutral).
    """)

# --- DISCLAIMER ---
st.warning("This dashboard is for educational purposes only and is not financial advice. Investing in stocks involves risk.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>💡 Data updates based on your input | Powered by Finnhub, Stooq, and TextBlob</p>
    </div>
""", unsafe_allow_html=True) 
