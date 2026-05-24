"""
data_fetcher.py — Lấy dữ liệu từ Bybit API (hoạt động tốt tại Việt Nam)
"""
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)
BYBIT_BASE = "https://api.bybit.com"

# Chuyển đổi timeframe sang định dạng Bybit
TF_MAP = {
    "1m": "1",   "5m": "5",   "15m": "15",  "30m": "30",
    "1h": "60",  "4h": "240", "1d": "D",
}


def get_ohlcv(symbol: str, interval: str = "1h", limit: int = 300) -> pd.DataFrame:
    """Lấy dữ liệu nến OHLCV từ Bybit."""
    bybit_interval = TF_MAP.get(interval, "60")
    url    = f"{BYBIT_BASE}/v5/market/kline"
    params = {
        "category": "linear",
        "symbol":   symbol.upper(),
        "interval": bybit_interval,
        "limit":    limit,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    rows = data["result"]["list"]  # newest first → cần đảo ngược
    df = pd.DataFrame(rows, columns=["timestamp","open","high","low","close","volume","turnover"])
    df = df.iloc[::-1].reset_index(drop=True)  # đảo thành oldest first

    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df = df.set_index("timestamp")
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)

    return df[["open","high","low","close","volume"]]


def get_ticker_24h(symbol: str) -> dict:
    """Lấy thống kê 24h từ Bybit."""
    resp = requests.get(
        f"{BYBIT_BASE}/v5/market/tickers",
        params={"category": "linear", "symbol": symbol.upper()},
        timeout=10,
    )
    resp.raise_for_status()
    items = resp.json()["result"]["list"]
    if not items:
        return {}
    t = items[0]
    # Chuyển về format giống Binance để dashboard dùng được
    return {
        "priceChangePercent": float(t.get("price24hPcnt", 0)) * 100,
        "quoteVolume":        float(t.get("turnover24h", 0)),
        "lastPrice":          float(t.get("lastPrice", 0)),
    }
