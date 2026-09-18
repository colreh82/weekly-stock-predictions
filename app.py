import streamlit as st
import yfinance as yf
from groq import Groq
from datetime import datetime
import pandas as pd
import re

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

# Initialize history
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Helper: extract probability ---
def extract_probability(text):
    match = re.search(r"Probability of positive week:\s*(\d+)%", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

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
    with st.spinner("Researching all four stocks..."):
        results = {}
        run_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        for ticker, name in stocks.items():
            prompt = f"""
You are a cautious financial research assistant. Today is {datetime.now().strftime('%Y-%m-%d')}.

Produce a realistic weekly outlook for {name} ({ticker}).

Rules:
- Be balanced and conservative.
- Probability of a positive week should stay between 45% and 62%.
- Keep every section short.

Respond in exactly this format:

**Direction Bias:** Up / Down / Neutral
**Probability of positive week:** XX%
**Expected move range:** e.g. -3% to +4%
**Key catalysts this week:**
- (1-3 short points)
**Main risks:**
- (1-3 short points)
**Short summary:**
(2-3 sentences max)
"""

            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=700
                )
                results[ticker] = completion.choices[0].message.content
            except Exception as e:
                results[ticker] = f"**Error:** {str(e)}"

        # Save to history
        history_entry = {
            "run_time": run_time,
            "results": results
        }
        st.session_state["history"].insert(0, history_entry)
        st.session_state["research_results"] = results
        st.session_state["research_time"] = run_time

# Latest full research
if "research_results" in st.session_state:
    st.success(f"Last research run: {st.session_state['research_time']}")
    for ticker, text in st.session_state["research_results"].items():
        with st.expander(f"{stocks[ticker]} ({ticker})", expanded=False):
            st.markdown(text)

st.divider()

# --- Probability Trend History ---
st.subheader("Probability Trend (Positive Week)")

if st.session_state["history"]:
    # Build probability table
    rows = []
    for entry in reversed(st.session_state["history"]):  # oldest first for trend
        row = {"Run Time": entry["run_time"]}
        for ticker in stocks:
            text = entry["results"].get(ticker, "")
            prob = extract_probability(text)
            row[stocks[ticker]] = prob if prob is not None else "—"
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    # Simple line chart
    chart_df = df.set_index("Run Time")
    # Convert to numeric where possible
    for col in chart_df.columns:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")
    
    st.line_chart(chart_df)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Probability History as CSV",
        data=csv,
        file_name=f"probability_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("No history yet. Run the research to start tracking probabilities.")

st.caption("Free personal tool. Not financial advice. History lasts while the app is active — download the CSV to keep it permanently.")
