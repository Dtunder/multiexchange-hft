def calculate_obi(orderbook: dict, levels: int = 10) -> float:
    bids = orderbook.get("bids", [])[:levels]
    asks = orderbook.get("asks", [])[:levels]

    bid_vol = sum(bid[1] for bid in bids)
    ask_vol = sum(ask[1] for ask in asks)

    total_vol = bid_vol + ask_vol
    if total_vol == 0:
        return 0.0

    obi = (bid_vol - ask_vol) / total_vol
    return obi

def get_signal(obi: float, threshold: float = 0.15) -> dict:
    if obi > threshold:
        direction = "LONG"
    elif obi < -threshold:
        direction = "SHORT"
    else:
        direction = "NEUTRAL"

    return {
        "direction": direction,
        "confidence": abs(obi)
    }
