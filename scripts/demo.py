import asyncio
import os
import json

# Force use a local test database for demo runs so we don't mess with dev DB
os.environ["DB_PATH"] = "data/demo_trades.db"

from src.exchange_connector import ExchangeConnector
from src.signal_engine import calculate_obi, get_signal
from src.execution_engine import execute_paper_trade
from src.portfolio_tracker import calculate_portfolio_metrics

def get_mock_orderbook(exchange_id):
    try:
        with open("data/mock_orderbook.json", "r") as f:
            data = json.load(f)
            return data.get(exchange_id, {})
    except Exception:
        return {"bids": [], "asks": []}

async def run_demo_cycle():
    exchanges = ['binance', 'bybit', 'okx']
    symbol = 'BTC/USDT'
    portfolio_capital = 10000.0

    trades_executed = 0
    print("Starting MultiExchange-HFT MVP Demo...")
    print(f"Initial Capital: ${portfolio_capital}")
    print("-" * 50)

    for ex_id in exchanges:
        print(f"Fetching data for {ex_id.upper()}...")
        connector = ExchangeConnector(ex_id)

        # In demo we force mock data to ensure it runs end-to-end without network issues
        orderbook = get_mock_orderbook(ex_id)

        if orderbook and "bids" in orderbook and "asks" in orderbook:
            obi = calculate_obi(orderbook)
            print(f"  -> {ex_id.upper()} OBI: {obi:.4f}")

            signal = get_signal(obi)
            print(f"  -> Signal: {signal['direction']} (Confidence: {signal['confidence']:.2f})")

            price = orderbook["bids"][0][0] if orderbook["bids"] else 50000.0

            result = execute_paper_trade(signal, symbol, price, portfolio_capital)
            if result:
                print(f"  -> Executed: {result['size']:.6f} {symbol} at ${result['price']:.2f}")
                trades_executed += 1
            else:
                print(f"  -> No trade executed (NEUTRAL signal)")

        await connector.close()
        print("-" * 50)

    print("\nCalculating metrics...")
    metrics = calculate_portfolio_metrics(portfolio_capital)
    print(f"Total Trades Logged Today: {trades_executed}")
    print(f"Simulated P&L: ${metrics['pnl']:.2f}")
    print(f"Running Capital: ${metrics['running_capital']:.2f}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
    print("Demo completed successfully!")

if __name__ == "__main__":
    if os.path.exists("data/demo_trades.db"):
        os.remove("data/demo_trades.db")
    from src.execution_engine import init_db
    init_db()

    asyncio.run(run_demo_cycle())
