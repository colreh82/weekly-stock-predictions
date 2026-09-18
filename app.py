import streamlit as st
import yfinance as yf
import google.generativeai as genai
from datetime import datetime
import json

st.set_page_config(
    page_title="Weekly Stock Predictions",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Weekly Stock Predictions")
st.caption("TSLA • ACHR • COIN • SPCX | Maximum free version")

# --- Configure Gemini ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error("Gemini API key not found or invalid. Please check your Streamlit secrets.")
    st.stop()

stocks = {
    "TSLA": "Tesla",
    "ACHR": "Archer Aviation",
    "COIN": "Coinbase",
    "SPCX": "SpaceX"
}

# --- Current Prices ---
st.subheader("Current Prices")
cols = st.columns(4)

current_data = {}

for i, (ticker, name) in enumerate(stocks.items()):
    with cols[i]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
            change = info.get("regularMarketChangePercent")
            current_data[ticker] = {
                "name": name,
                "price": price,
                "change": change
            }
            st.metric(
                label=f"{name} ({ticker})",
                value=f"${price:.2f}" if price else "N/A",
                delta=f"{change:.2f}%" if change else None
            )
        except Exception:
            st.metric(label=f"{name} ({ticker})", value="Error")
            current_data[ticker] = {"name": name, "price": None, "change": None}

st.divider()

# --- AI Research Section ---
st.subheader("Weekly AI Research & Forecast")

if st.button("🔄 Run Weekly Research (uses Gemini)", type="primary"):
    with st.spinner("Researching all four stocks with Gemini... this may take 20-40 seconds"):
        results = {}

        for ticker, name in stocks.items():
            prompt = f"""
You are a financial research assistant. Today is {datetime.now().strftime('%Y-%m-%d')}.

Analyze the stock {name} ({ticker}) for the coming week.

Provide a structured response in this exact format:

**Direction Bias:** Up / Down / Neutral
**Probability of positive week:** XX%
**Expected move range:** e.g. -3% to +5%
**Key catalysts this week:**
- bullet point 1
- bullet point 2
**Main risks:**
- bullet point 1
- bullet point 2
**Short summary:** 2-3 sentences max.

Be realistic. Do not claim high certainty. Base your view on typical factors that move this stock (news, sector trends, company events, macro). Keep the tone professional and balanced.
"""

            try:
                response = model.generate_content(prompt)
                results[ticker] = response.text
            except Exception as e:
                results[ticker] = f"Error generating research: {str(e)}"

        # Store in session state so it stays after the button click
        st.session_state["research_results"] = results
        st.session_state["research_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# Display results if they exist
if "research_results" in st.session_state:
    st.success(f"Last research run: {st.session_state['research_time']}")

    for ticker, text in st.session_state["research_results"].items():
        with st.expander(f"{stocks[ticker]} ({ticker})", expanded=True):
            st.markdown(text)

st.divider()
st.caption("This is a free personal research tool. Not financial advice. Predictions are probabilistic and can be wrong.")
