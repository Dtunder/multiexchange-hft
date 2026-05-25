# MultiExchange-HFT MVP

An asynchronous multi-exchange High-Frequency Trading (HFT) paper trading bot connecting to Binance, Bybit, and OKX. The bot calculates Order Book Imbalance (OBI) to generate signals, executes 1% fractional paper trades into a SQLite database, and displays live metrics on a Streamlit dashboard.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Dashboard

To run the Streamlit application:

```bash
streamlit run app.py
```

## Testing

To run the test suite, which heavily uses `unittest.mock` for network separation:

```bash
PYTHONPATH=. pytest tests/
```

## Environment Variables & Mock Flags

- `PAPER_MODE`: Set to `true` (default) to log paper trades instead of attempting real execution on exchanges. Set to `false` for real order execution.
- `DB_PATH`: Defines the path to the SQLite trade log database. Defaults to `data/trades.db` in production and `data/test_trades.db` in tests.
