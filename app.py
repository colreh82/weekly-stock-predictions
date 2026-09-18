import streamlit as st
import yfinance as yf
from groq import Groq
from datetime import datetime

st.set_page_config(
    page_title="Weekly Stock Predictions",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Weekly Stock Predictions")
st.caption("TSLA • ACHR • COIN • SPCX | Maximum free version (Groq)")

# --- Configure Groq ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Could not load Groq API key: {e}")
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
        except Exception:
            st.metric(label=f"{name} ({ticker})", value="Error")

st.divider()

# --- AI Research Section ---
st.subheader("Weekly AI Research & Forecast")

if st.button("🔄 Run Weekly Research (uses Groq)", type="primary"):
    with st.spinner("Researching all four stocks... this may take 20-40 seconds"):
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

Be realistic. Do not claim high certainty. Keep the tone professional and balanced.
"""

            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=600
                )
                results[ticker] = completion.choices[0].message.content
            except Exception as e:
                results[ticker] = f"**Error:** {type(e).__name__}: {str(e)}"

        st.session_state["research_results"] = results
        st.session_state["research_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# Display results
if "research_results" in st.session_state:
    st.success(f"Last research run: {st.session_state['research_time']}")

    for ticker, text in st.session_state["research_results"].items():
        with st.expander(f"{stocks[ticker]} ({ticker})", expanded=True):
            st.markdown(text)

st.divider()
st.caption("This is a free personal research tool. Not financial advice.")
