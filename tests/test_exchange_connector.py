import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.exchange_connector import ExchangeConnector
import ccxt.async_support as ccxt

@pytest.mark.asyncio
async def test_fetch_orderbook():
    with patch("src.exchange_connector.ccxt.binance") as MockBinance:
        # Set up the mock instance
        mock_instance = AsyncMock()
        mock_instance.fetch_order_book = AsyncMock(return_value={"bids": [[50000, 1]], "asks": [[50001, 1]]})
        mock_instance.close = AsyncMock()
        MockBinance.return_value = mock_instance

        connector = ExchangeConnector("binance")
        ob = await connector.fetch_orderbook("BTC/USDT")

        assert ob is not None
        assert ob["bids"][0][0] == 50000
        mock_instance.fetch_order_book.assert_called_once_with("BTC/USDT", 10)

        await connector.close()
        mock_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_place_paper_order():
    with patch("src.exchange_connector.ccxt.bybit") as MockBybit, \
         patch("src.exchange_connector.PAPER_MODE", True):
        mock_instance = AsyncMock()
        mock_instance.close = AsyncMock()
        MockBybit.return_value = mock_instance

        connector = ExchangeConnector("bybit")

        # In PAPER_MODE, it should not call exchange.create_order
        mock_instance.create_order = AsyncMock()

        result = await connector.place_paper_order("BTC/USDT", "limit", "buy", 0.1, 50000)
        assert result["side"] == "buy"
        assert result["status"] == "closed"
        mock_instance.create_order.assert_not_called()

        await connector.close()
        mock_instance.close.assert_called_once()

@pytest.mark.asyncio
async def test_place_real_order():
    with patch("src.exchange_connector.ccxt.okx") as MockOkx, \
         patch("src.exchange_connector.PAPER_MODE", False):
        mock_instance = AsyncMock()
        mock_instance.create_order = AsyncMock(return_value={"id": "real_id", "status": "open"})
        mock_instance.close = AsyncMock()
        MockOkx.return_value = mock_instance

        connector = ExchangeConnector("okx")
        result = await connector.place_paper_order("BTC/USDT", "limit", "sell", 0.1, 50000)

        assert result["id"] == "real_id"
        mock_instance.create_order.assert_called_once_with("BTC/USDT", "limit", "sell", 0.1, 50000)

        await connector.close()
        mock_instance.close.assert_called_once()
