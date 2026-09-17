import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Weekly Stock Predictions",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Weekly Stock Predictions")
st.caption("TSLA • ACHR • COIN • SPCX | Maximum free version")

stocks = {
    "TSLA": "Tesla",
    "ACHR": "Archer Aviation",
    "COIN": "Coinbase",
    "SPCX": "SpaceX"
}

st.subheader("Current Prices")

cols = st.columns(4)

for i, (ticker, name) in enumerate(stocks.items()):
    with cols[i]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            change = info.get("regularMarketChangePercent")
            
            st.metric(
                label=f"{name} ({ticker})",
                value=f"${price:.2f}" if price else "N/A",
                delta=f"{change:.2f}%" if change else None
            )
        except Exception as e:
            st.metric(label=f"{name} ({ticker})", value="Error")
            st.caption(str(e)[:50])

st.divider()
st.info("Next steps: We will add the AI research agent and weekly predictions.")
