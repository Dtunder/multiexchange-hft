import pytest
import sqlite3
import os

# Set environment variable BEFORE importing so they pick up test.db
os.environ["DB_PATH"] = "data/test_trades.db"

from src.execution_engine import execute_paper_trade, init_db
from src.portfolio_tracker import get_trades_df, calculate_portfolio_metrics

# Re-init db or clear table for tests
def setup_module():
    # Make sure we use a separate test db file, test_trades.db
    if os.path.exists('data/test_trades.db'):
        os.remove('data/test_trades.db')
    init_db()

def teardown_module():
    if os.path.exists('data/test_trades.db'):
        os.remove('data/test_trades.db')

def test_execute_paper_trade_long():
    signal = {"direction": "LONG", "confidence": 0.25}
    portfolio = 10000.0
    price = 50000.0

    result = execute_paper_trade(signal, "BTC/USDT", price, portfolio)

    assert result is not None
    assert result["direction"] == "LONG"
    assert result["notional"] == 100.0 # 1% of 10000
    assert result["size"] == 100.0 / 50000.0
    assert result["status"] == "filled"

def test_execute_paper_trade_short():
    signal = {"direction": "SHORT", "confidence": 0.18}
    portfolio = 10000.0
    price = 50000.0

    result = execute_paper_trade(signal, "BTC/USDT", price, portfolio)

    assert result is not None
    assert result["direction"] == "SHORT"
    assert result["notional"] == 100.0

def test_execute_paper_trade_neutral():
    signal = {"direction": "NEUTRAL", "confidence": 0.05}
    portfolio = 10000.0
    price = 50000.0

    result = execute_paper_trade(signal, "BTC/USDT", price, portfolio)

    assert result is None

def test_db_logging():
    df = get_trades_df()
    assert len(df) == 2 # The long and the short from above
    assert "BTC/USDT" in df["symbol"].values

def test_portfolio_metrics():
    metrics = calculate_portfolio_metrics(10000.0)
    assert "pnl" in metrics
    assert "running_capital" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics
    assert isinstance(metrics["pnl"], (float, int)) or type(metrics["pnl"]).__name__ == 'float64'
