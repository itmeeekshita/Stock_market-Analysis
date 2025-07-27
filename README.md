# 📈 Stock Market Sentiment Analytics

A powerful, interactive dashboard built with **Streamlit** that visualizes stock market performance and analyzes recent **news sentiment**. This project uses real-time stock data and news to provide insights into market trends for **US-based stocks** like `AAPL`, `MSFT`, `TSLA`, etc.

![dashboard demo](https://img.icons8.com/color/96/000000/stocks.png)

## 🚀 Features

- 📊 Candlestick & Line Chart of historical stock prices from **Stooq**
- 📈 Moving Average (SMA) analysis to track trends
- 📰 Live News Sentiment analysis from **Finnhub API**
- 🥧 Sentiment Distribution Chart with sentiment labels
- 📋 Stock Summary with metrics and outlook
- 🎓 Educational Glossary for finance beginners
- 📅 Interactive date range selection

## 📂 Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
```

## 🛠️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/stock-market-sentiment-analytics.git
cd stock-market-sentiment-analytics
```

### 2. (Optional) Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your Finnhub API Key

- Sign up at https://finnhub.io
- Set your API key as an environment variable:

```bash
export FINNHUB_API_KEY=your_api_key_here
# On Windows use:
# set FINNHUB_API_KEY=your_api_key_here
```

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

## 🧠 How It Works

- Stock prices are fetched from **Stooq** (CSV endpoint).
- News articles are fetched from **Finnhub API**.
- Sentiment is calculated using **TextBlob** polarity scores.
- Visualizations include candlestick, line, volume, and sentiment distribution.

### Sentiment Categories

- Very Positive (polarity > 0.3)
- Positive (0.05 < polarity ≤ 0.3)
- Neutral (-0.05 ≤ polarity ≤ 0.05)
- Negative (-0.3 ≤ polarity < -0.05)
- Very Negative (polarity < -0.3)

## 📝 To-Do / Future Enhancements

- Add support for international tickers
- Add live Twitter sentiment analysis
- Add CSV/PDF export of sentiment
- Add more technical indicators (MACD, RSI)

## 📌 Limitations

- Only supports US-based stocks (e.g., AAPL, TSLA)
- Finnhub’s free API has limited rate (60 calls/min)
- Sentiment depends on headline quality and TextBlob accuracy

## 📷 Screenshots

![Price Chart](https://your-link.com/price.png)
![News Sentiment](https://your-link.com/news.png)
![Sentiment Donut](https://your-link.com/donut.png)

## ⚠️ Disclaimer

> This dashboard is for **educational purposes only** and does **not constitute financial advice**.
> Investing in stocks involves risk. Always do your own research.
