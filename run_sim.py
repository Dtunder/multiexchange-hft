import asyncio
from src.exchange_connector import ExchangeConnector
from src.signal_engine import calculate_obi, get_signal
from src.execution_engine import execute_paper_trade
import json

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
    portfolio_capital = 10000.0

    for ex_id in exchanges:
        connector = ExchangeConnector(ex_id)
        orderbook = await connector.fetch_orderbook(symbol)
        if not orderbook:
            orderbook = get_mock_orderbook(ex_id)

        if orderbook and "bids" in orderbook and "asks" in orderbook:
            obi = calculate_obi(orderbook)
            signal = get_signal(obi)

            price = orderbook["bids"][0][0] if orderbook["bids"] else 50000.0
            execute_paper_trade(signal, symbol, price, portfolio_capital)

        await connector.close()

async def main():
    for i in range(10):
        print(f"Running cycle {i+1}/10")
        await run_trading_cycle()
    print("Successfully ran 10 cycles!")

if __name__ == "__main__":
    asyncio.run(main())
