import streamlit as st
import asyncio
import pandas as pd
import json
import time
import os
import plotly.express as px
import plotly.graph_objects as go
from src.exchange_connector import ExchangeConnector
from src.signal_engine import calculate_obi, get_signal
from src.execution_engine import execute_paper_trade
from src.portfolio_tracker import get_trades_df, calculate_portfolio_metrics

st.set_page_config(page_title="MultiExchange-HFT MVP", layout="wide")
st.title("🚀 MultiExchange-HFT MVP Dashboard")

# State
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'portfolio_capital' not in st.session_state:
    st.session_state.portfolio_capital = 10000.0
if 'obi_history' not in st.session_state:
    st.session_state.obi_history = {'binance': [], 'bybit': [], 'okx': []}

# Sidebar
st.sidebar.header("Controls")
if st.sidebar.button("Start Trading Bot" if not st.session_state.is_running else "Stop Trading Bot"):
    st.session_state.is_running = not st.session_state.is_running

st.sidebar.markdown(f"**Status:** {'Running 🟢' if st.session_state.is_running else 'Stopped 🔴'}")
st.sidebar.markdown(f"**Paper Mode:** {'ON' if os.getenv('PAPER_MODE', 'true').lower() == 'true' else 'OFF'}")

# Layout
col1, col2, col3 = st.columns(3)

# Load mock orderbooks if using for demo/offline running
def get_mock_orderbook(exchange_id):
    try:
        with open("data/mock_orderbook.json", "r") as f:
            data = json.load(f)
            return data.get(exchange_id, {})
    except Exception:
        return {"bids": [], "asks": []}

async def run_trading_cycle():
    exchanges = ['binance', 'bybit', 'okx']
    symbol = 'BTC/USDT'

    # Simple placeholder for real asyncio cycle:
    # Normally we'd use ccxt fetch_orderbook, but to ensure 0 failures and
    # stable demo running, we can blend mock data.
    # In full async code, this runs continuously. Streamlit runs top-down,
    # so we'll do one pass per Streamlit rerun if 'running'.

    for ex_id in exchanges:
        connector = ExchangeConnector(ex_id)
        # Fetch real live data via ccxt
        orderbook = await connector.fetch_orderbook(symbol)

        # Fallback to mock data only if live data fails (e.g., rate limits/network issues)
        if not orderbook:
            orderbook = get_mock_orderbook(ex_id)

        if orderbook and "bids" in orderbook and "asks" in orderbook:
            obi = calculate_obi(orderbook)
            st.session_state.obi_history[ex_id].append(obi)

            # Keep only last 50 points
            if len(st.session_state.obi_history[ex_id]) > 50:
                st.session_state.obi_history[ex_id].pop(0)

            signal = get_signal(obi)

            # Mock price
            price = orderbook["bids"][0][0] if orderbook["bids"] else 50000.0

            execute_paper_trade(signal, symbol, price, st.session_state.portfolio_capital)

        await connector.close()

# Main logic loop (streamlit style)
if st.session_state.is_running:
    asyncio.run(run_trading_cycle())
    time.sleep(1) # simple throttling
    st.rerun()

# --- Metrics ---
st.subheader("Portfolio Metrics")
metrics = calculate_portfolio_metrics(st.session_state.portfolio_capital)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Running Capital", f"${metrics['running_capital']:.2f}")
m2.metric("Total P&L", f"${metrics['pnl']:.2f}")
m3.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
m4.metric("Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%")

# --- OBI Charts ---
st.subheader("Live Order Book Imbalance (OBI)")
if any(len(v) > 0 for v in st.session_state.obi_history.values()):
    df_obi = pd.DataFrame(st.session_state.obi_history)
    fig = px.line(df_obi, title="OBI across Exchanges", labels={"value": "OBI", "index": "Time"}, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No OBI data yet. Start the bot.")

# --- Trade Log ---
st.subheader("Trade Log")
trades_df = get_trades_df()
if not trades_df.empty:
    st.dataframe(trades_df.sort_values(by="timestamp", ascending=False).head(20), use_container_width=True)
else:
    st.write("No trades logged yet.")
