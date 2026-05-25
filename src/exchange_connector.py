import os
import ccxt.async_support as ccxt
import asyncio

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"

class ExchangeConnector:
    def __init__(self, exchange_id: str):
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class()

    async def fetch_orderbook(self, symbol: str, limit: int = 10):
        try:
            return await self.exchange.fetch_order_book(symbol, limit)
        except Exception as e:
            print(f"Error fetching orderbook for {self.exchange_id}: {e}")
            return None

    async def fetch_ticker(self, symbol: str):
        try:
            return await self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"Error fetching ticker for {self.exchange_id}: {e}")
            return None

    async def place_paper_order(self, symbol: str, type: str, side: str, amount: float, price: float = None):
        if PAPER_MODE:
            print(f"[PAPER] Placed {side} order for {amount} {symbol} at {price} on {self.exchange_id}")
            return {
                "id": f"paper_{asyncio.get_event_loop().time()}",
                "symbol": symbol,
                "type": type,
                "side": side,
                "amount": amount,
                "price": price,
                "status": "closed"
            }
        else:
            try:
                return await self.exchange.create_order(symbol, type, side, amount, price)
            except Exception as e:
                print(f"Error placing real order on {self.exchange_id}: {e}")
                return None

    async def close(self):
        await self.exchange.close()
