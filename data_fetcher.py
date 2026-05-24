"""
data_fetcher.py — Dùng OKX API (hoạt động tốt tại Việt Nam)
"""
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)
OKX_BASE = "https://www.okx.com"

# Chuyển đổi timeframe sang định dạng OKX
TF_MAP = {
    "1m": "1m",  "5m": "5m",  "15m": "15m", "30m": "30m",
    "1h": "1H",  "4h": "4H",  "1d": "1D",
}

# Chuyển đổi symbol: BTCUSDT → BTC-USDT
def to_okx_symbol(symbol: str) -> str:
    symbol = symbol.upper().replace("USDT", "")
    return f"{symbol}-USDT"


def get_ohlcv(symbol: str, interval: str = "1h", limit: int = 300) -> pd.DataFrame:
    """Lấy dữ liệu nến OHLCV từ OKX."""
    okx_symbol   = to_okx_symbol(symbol)
    okx_interval = TF_MAP.get(interval, "1H")

    url    = f"{OKX_BASE}/api/v5/market/candles"
    params = {"instId": okx_symbol, "bar": okx_interval, "limit": limit}
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # OKX trả về: [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    # Newest first → đảo ngược
    rows = data["data"]
    df = pd.DataFrame(rows, columns=[
        "timestamp","open","high","low","close",
        "volume","volCcy","volCcyQuote","confirm"
    ])
    df = df.iloc[::-1].reset_index(drop=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df = df.set_index("timestamp")
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)

    return df[["open","high","low","close","volume"]]


def get_ticker_24h(symbol: str) -> dict:
    """Lấy thống kê 24h từ OKX."""
    okx_symbol = to_okx_symbol(symbol)
    resp = requests.get(
        f"{OKX_BASE}/api/v5/market/ticker",
        params={"instId": okx_symbol},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    resp.raise_for_status()
    items = resp.json().get("data", [])
    if not items:
        return {"priceChangePercent": 0, "quoteVolume": 0}
    t = items[0]
    last  = float(t.get("last",  0))
    open_ = float(t.get("open24h", last)) or last
    pct   = ((last - open_) / open_ * 100) if open_ else 0
    return {
        "priceChangePercent": round(pct, 2),
        "quoteVolume":        float(t.get("volCcy24h", 0)),
        "lastPrice":          last,
    }
