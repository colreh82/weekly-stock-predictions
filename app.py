import streamlit as st
import yfinance as yf
from groq import Groq
from datetime import datetime
import pandas as pd
import json

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

# Initialize history in session state
if "history" not in st.session_state:
    st.session_state["history"] = []

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
        run_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        for ticker, name in stocks.items():
            prompt = f"""
You are a cautious financial research assistant. Today is {datetime.now().strftime('%Y-%m-%d')}.

Your task is to produce a realistic weekly outlook for {name} ({ticker}).

Rules you must follow:
- Be balanced and conservative. Never claim high certainty.
- Probability of a positive week should normally stay between 45% and 62%.
- Base your view on typical catalysts that actually move this stock (earnings, product news, regulation, sector trends, macro, company-specific events).
- If there is no strong catalyst, lean Neutral.
- Keep every section short and clear.

Respond in exactly this format (use the headings):

**Direction Bias:** Up / Down / Neutral

**Probability of positive week:** XX%

**Expected move range:** e.g. -3% to +4%

**Key catalysts this week:**
- (1-3 short bullet points only)

**Main risks:**
- (1-3 short bullet points only)

**Short summary:**
(2-3 sentences maximum. Be direct and realistic.)
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
                results[ticker] = f"**Error:** {type(e).__name__}: {str(e)}"

        # Save this run to history
        history_entry = {
            "run_time": run_time,
            "results": results
        }
        st.session_state["history"].insert(0, history_entry)  # newest first
        st.session_state["research_results"] = results
        st.session_state["research_time"] = run_time

# Display latest results
if "research_results" in st.session_state:
    st.success(f"Last research run: {st.session_state['research_time']}")

    for ticker, text in st.session_state["research_results"].items():
        with st.expander(f"{stocks[ticker]} ({ticker})", expanded=True):
            st.markdown(text)

st.divider()

# --- History Section ---
st.subheader("Weekly History")

if st.session_state["history"]:
    st.write(f"Saved runs: {len(st.session_state['history'])}")

    # Download button
    history_for_download = []
    for entry in st.session_state["history"]:
        for ticker, text in entry["results"].items():
            history_for_download.append({
                "Run Time": entry["run_time"],
                "Ticker": ticker,
                "Name": stocks[ticker],
                "Full Research": text
            })

    df = pd.DataFrame(history_for_download)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download History as CSV",
        data=csv,
        file_name=f"stock_research_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # Show past runs
    for i, entry in enumerate(st.session_state["history"]):
        with st.expander(f"Run from {entry['run_time']}", expanded=(i == 0)):
            for ticker, text in entry["results"].items():
                st.markdown(f"### {stocks[ticker]} ({ticker})")
                st.markdown(text)
                st.divider()
else:
    st.info("No history yet. Run the research to start tracking.")

st.caption("This is a free personal research tool. Not financial advice. History is kept while the app is active — download the CSV to keep a permanent record.")
