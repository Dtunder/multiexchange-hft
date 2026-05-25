import pytest
import json
from src.signal_engine import calculate_obi, get_signal

@pytest.fixture
def mock_orderbook():
    with open("data/mock_orderbook.json", "r") as f:
        data = json.load(f)
    return data

def test_calculate_obi_binance(mock_orderbook):
    ob = mock_orderbook["binance"]
    obi = calculate_obi(ob, levels=10)

    # Manually calc from json:
    # Bids sum: 1.5+2+0.5+3+1+1+2+1.5+0.5+1 = 14.0
    # Asks sum: 1+2.5+1+0.5+3+1.5+2+1+1.5+0.5 = 14.5
    # Total = 28.5
    # OBI = (14.0 - 14.5) / 28.5 = -0.5 / 28.5 = -0.01754
    assert round(obi, 4) == -0.0175

def test_calculate_obi_bybit(mock_orderbook):
    ob = mock_orderbook["bybit"]
    obi = calculate_obi(ob, levels=10)

    # Bids sum: 1+1.5+2+1+0.5+1.5+2+1+0.5+1 = 12.0
    # Asks sum: 2+1.5+1+2.5+1+0.5+1+1.5+2+1 = 14.0
    # Total = 26.0
    # OBI = (12 - 14) / 26 = -2/26 = -0.0769
    assert round(obi, 4) == -0.0769

def test_get_signal_long():
    signal = get_signal(0.20, threshold=0.15)
    assert signal["direction"] == "LONG"
    assert signal["confidence"] == 0.20

def test_get_signal_short():
    signal = get_signal(-0.18, threshold=0.15)
    assert signal["direction"] == "SHORT"
    assert signal["confidence"] == 0.18

def test_get_signal_neutral():
    signal = get_signal(0.10, threshold=0.15)
    assert signal["direction"] == "NEUTRAL"
    assert signal["confidence"] == 0.10

def test_calculate_obi_empty():
    ob = {"bids": [], "asks": []}
    obi = calculate_obi(ob)
    assert obi == 0.0
