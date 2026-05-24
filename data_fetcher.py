"""
data_fetcher.py — Lấy dữ liệu từ Binance public API (không cần API key)
"""
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)
BINANCE_BASE = "https://api.binance.com"


def get_ohlcv(symbol: str, interval: str = "1h", limit: int = 300) -> pd.DataFrame:
    url    = f"{BINANCE_BASE}/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    resp   = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    cols = ["timestamp","open","high","low","close","volume",
            "close_time","quote_volume","trades","tbbase","tbquote","ignore"]
    df = pd.DataFrame(resp.json(), columns=cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp")
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    return df[["open","high","low","close","volume"]]


def get_ticker_24h(symbol: str) -> dict:
    resp = requests.get(f"{BINANCE_BASE}/api/v3/ticker/24hr",
                        params={"symbol": symbol.upper()}, timeout=10)
    resp.raise_for_status()
    return resp.json()
