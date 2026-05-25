import sqlite3
import datetime
import uuid

import os

DB_PATH = os.getenv("DB_PATH", "data/trades.db")

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            symbol TEXT,
            direction TEXT,
            price REAL,
            size REAL,
            notional REAL,
            confidence REAL
        )
    ''')
    conn.commit()
    conn.close()

# Call init_db on module load
init_db()

def log_trade(trade_id, symbol, direction, price, size, notional, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute('''
        INSERT INTO trades (id, timestamp, symbol, direction, price, size, notional, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (trade_id, timestamp, symbol, direction, price, size, notional, confidence))
    conn.commit()
    conn.close()

def execute_paper_trade(signal: dict, symbol: str, price: float, portfolio_value: float) -> dict:
    if signal["direction"] == "NEUTRAL":
        return None

    # 1% fixed fractional position sizing
    risk_pct = 0.01
    notional_size = portfolio_value * risk_pct

    if price == 0:
        size = 0.0
    else:
        size = notional_size / price

    trade_id = str(uuid.uuid4())

    # Log paper order to SQLite
    log_trade(
        trade_id=trade_id,
        symbol=symbol,
        direction=signal["direction"],
        price=price,
        size=size,
        notional=notional_size,
        confidence=signal.get("confidence", 0.0)
    )

    # Virtual P&L logic normally handled later when positions are closed.
    # For paper executing the initial order, we simply return the order details.
    return {
        "id": trade_id,
        "symbol": symbol,
        "direction": signal["direction"],
        "price": price,
        "size": size,
        "notional": notional_size,
        "status": "filled"
    }
