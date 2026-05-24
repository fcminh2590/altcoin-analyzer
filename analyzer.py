"""
analyzer.py — Tính toán đầy đủ 10+ chỉ báo kỹ thuật
  RSI · MACD · Bollinger Bands · EMA/SMA
  Stochastic RSI · Williams %R · Ichimoku Cloud
  Fibonacci · ATR · OBV · CCI
"""
import numpy as np
import pandas as pd
from config import (
    RSI_OVERSOLD, RSI_OVERBOUGHT,
    STOCHRSI_OVERSOLD, STOCHRSI_OVERBOUGHT,
    WILLIAMS_OVERSOLD, WILLIAMS_OVERBOUGHT,
    CCI_OVERSOLD, CCI_OVERBOUGHT,
)


# ══════════════════════════════════════════════════════
#  CÁC HÀM TÍNH CHỈ BÁO
# ══════════════════════════════════════════════════════

def calc_rsi(close: pd.Series, period=14) -> pd.Series:
    d    = close.diff()
    gain = d.clip(lower=0).rolling(period).mean()
    loss = (-d.clip(upper=0)).rolling(period).mean()
    rs   = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def calc_stoch_rsi(close: pd.Series, rsi_period=14, stoch_period=14,
                   k_period=3, d_period=3):
    """Stochastic RSI — K và D lines."""
    rsi      = calc_rsi(close, rsi_period)
    rsi_min  = rsi.rolling(stoch_period).min()
    rsi_max  = rsi.rolling(stoch_period).max()
    stoch    = (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan) * 100
    k        = stoch.rolling(k_period).mean()
    d        = k.rolling(d_period).mean()
    return k, d


def calc_macd(close: pd.Series, fast=12, slow=26, signal=9):
    ema_f  = close.ewm(span=fast,   adjust=False).mean()
    ema_s  = close.ewm(span=slow,   adjust=False).mean()
    macd   = ema_f - ema_s
    sig    = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig, macd - sig


def calc_bollinger(close: pd.Series, period=20, mul=2):
    mid   = close.rolling(period).mean()
    std   = close.rolling(period).std()
    return mid + mul*std, mid, mid - mul*std


def calc_ema(close: pd.Series, p: int) -> pd.Series:
    return close.ewm(span=p, adjust=False).mean()


def calc_sma(close: pd.Series, p: int) -> pd.Series:
    return close.rolling(p).mean()


def calc_williams_r(df: pd.DataFrame, period=14) -> pd.Series:
    """Williams %R: -100 (oversold) → 0 (overbought)."""
    hh = df["high"].rolling(period).max()
    ll = df["low"].rolling(period).min()
    return (hh - df["close"]) / (hh - ll).replace(0, np.nan) * -100


def calc_cci(df: pd.DataFrame, period=20) -> pd.Series:
    """Commodity Channel Index."""
    tp      = (df["high"] + df["low"] + df["close"]) / 3
    sma_tp  = tp.rolling(period).mean()
    mad     = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))


def calc_atr(df: pd.DataFrame, period=14) -> pd.Series:
    """Average True Range."""
    prev_c = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_c).abs(),
        (df["low"]  - prev_c).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def calc_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(df["close"].diff()).fillna(0)
    return (direction * df["volume"]).cumsum()


def calc_ichimoku(df: pd.DataFrame):
    """
    Ichimoku Cloud:
      tenkan  = (9-period high + 9-period low) / 2
      kijun   = (26-period high + 26-period low) / 2
      span_a  = (tenkan + kijun) / 2   [shifted +26]
      span_b  = (52-period high + 52-period low) / 2  [shifted +26]
      chikou  = close [shifted -26]
    """
    def mid(h, l): return (h + l) / 2

    tenkan = mid(df["high"].rolling(9).max(),  df["low"].rolling(9).min())
    kijun  = mid(df["high"].rolling(26).max(), df["low"].rolling(26).min())
    span_a = mid(tenkan, kijun).shift(26)
    span_b = mid(df["high"].rolling(52).max(), df["low"].rolling(52).min()).shift(26)
    chikou = df["close"].shift(-26)
    return tenkan, kijun, span_a, span_b, chikou


def calc_fibonacci(df: pd.DataFrame, lookback=100):
    """Fibonacci Retracement từ swing high/low trong N nến gần nhất."""
    recent = df.tail(lookback)
    hi     = recent["high"].max()
    lo     = recent["low"].min()
    diff   = hi - lo
    levels = {
        "fib_0":    hi,
        "fib_236":  hi - 0.236 * diff,
        "fib_382":  hi - 0.382 * diff,
        "fib_500":  hi - 0.500 * diff,
        "fib_618":  hi - 0.618 * diff,
        "fib_786":  hi - 0.786 * diff,
        "fib_100":  lo,
        "fib_hi":   hi,
        "fib_lo":   lo,
    }
    return levels


def calc_pivot_sr(df: pd.DataFrame):
    h, l, c = df["high"].iloc[-1], df["low"].iloc[-1], df["close"].iloc[-1]
    pivot = (h + l + c) / 3
    return {
        "pivot":        pivot,
        "resistance_1": 2*pivot - l,
        "resistance_2": pivot + (h - l),
        "support_1":    2*pivot - h,
        "support_2":    pivot - (h - l),
    }


# ══════════════════════════════════════════════════════
#  PHÂN TÍCH TỔNG HỢP
# ══════════════════════════════════════════════════════

def analyze(df: pd.DataFrame) -> dict:
    close, high, low, volume = df["close"], df["high"], df["low"], df["volume"]

    rsi                          = calc_rsi(close)
    stoch_k, stoch_d             = calc_stoch_rsi(close)
    macd_l, signal_l, hist       = calc_macd(close)
    bb_upper, bb_mid, bb_lower   = calc_bollinger(close)
    ema9   = calc_ema(close, 9)
    ema21  = calc_ema(close, 21)
    ema50  = calc_ema(close, 50)
    ema200 = calc_ema(close, 200)
    sma20  = calc_sma(close, 20)
    sma50  = calc_sma(close, 50)
    wpr    = calc_williams_r(df)
    cci    = calc_cci(df)
    atr    = calc_atr(df)
    obv    = calc_obv(df)
    tenkan, kijun, span_a, span_b, chikou = calc_ichimoku(df)
    fib    = calc_fibonacci(df)
    sr     = calc_pivot_sr(df)

    vol_ma = volume.rolling(20).mean()
    vol_ratio = volume.iloc[-1] / vol_ma.iloc[-1] if vol_ma.iloc[-1] else 1.0

    def last(s): return s.iloc[-1] if not s.empty else np.nan
    def prev(s): return s.iloc[-2] if len(s) >= 2 else np.nan

    return {
        # ── Giá trị mới nhất ──
        "price":         last(close),
        "rsi":           last(rsi),
        "stoch_k":       last(stoch_k),
        "stoch_d":       last(stoch_d),
        "stoch_k_prev":  prev(stoch_k),
        "stoch_d_prev":  prev(stoch_d),
        "macd":          last(macd_l),
        "macd_signal":   last(signal_l),
        "macd_hist":     last(hist),
        "macd_prev":     prev(macd_l),
        "msig_prev":     prev(signal_l),
        "bb_upper":      last(bb_upper),
        "bb_middle":     last(bb_mid),
        "bb_lower":      last(bb_lower),
        "ema9":          last(ema9),
        "ema21":         last(ema21),
        "ema50":         last(ema50),
        "ema200":        last(ema200),
        "sma20":         last(sma20),
        "sma50":         last(sma50),
        "williams_r":    last(wpr),
        "cci":           last(cci),
        "atr":           last(atr),
        "obv":           last(obv),
        "obv_prev":      prev(obv),
        "tenkan":        last(tenkan),
        "kijun":         last(kijun),
        "span_a":        last(span_a),
        "span_b":        last(span_b),
        "volume_ratio":  vol_ratio,
        **fib,
        **sr,
        # ── Series (vẽ biểu đồ) ──
        "df":         df,
        "rsi_s":      rsi,
        "stoch_k_s":  stoch_k,
        "stoch_d_s":  stoch_d,
        "macd_s":     macd_l,
        "signal_s":   signal_l,
        "hist_s":     hist,
        "bb_upper_s": bb_upper,
        "bb_mid_s":   bb_mid,
        "bb_lower_s": bb_lower,
        "ema9_s":     ema9,
        "ema21_s":    ema21,
        "ema50_s":    ema50,
        "ema200_s":   ema200,
        "wpr_s":      wpr,
        "cci_s":      cci,
        "atr_s":      atr,
        "obv_s":      obv,
        "tenkan_s":   tenkan,
        "kijun_s":    kijun,
        "span_a_s":   span_a,
        "span_b_s":   span_b,
    }


# ══════════════════════════════════════════════════════
#  TẠO TÍN HIỆU MUA / BÁN
# ══════════════════════════════════════════════════════

def generate_signals(data: dict):
    signals  = []
    strength = 0

    p    = data["price"]
    rsi  = data["rsi"]
    sk   = data["stoch_k"];    sd   = data["stoch_d"]
    skp  = data["stoch_k_prev"]; sdp = data["stoch_d_prev"]
    macd = data["macd"];       msig = data["macd_signal"]
    mh   = data["macd_hist"]
    bbu  = data["bb_upper"];   bbl  = data["bb_lower"]
    e9   = data["ema9"];       e21  = data["ema21"]
    e50  = data["ema50"];      e200 = data["ema200"]
    wpr  = data["williams_r"]
    cci  = data["cci"]
    atr  = data["atr"]
    obv  = data["obv"];        obvp = data["obv_prev"]
    tk   = data["tenkan"];     kj   = data["kijun"]
    sa   = data["span_a"];     sb   = data["span_b"]
    vol  = data["volume_ratio"]
    s1   = data["support_1"];  r1   = data["resistance_1"]

    def add(t, reason, val=None):
        nonlocal strength
        signals.append((t, reason, val))
        if t == "BUY":   strength += 2 if "mạnh" in reason.lower() or "crossover" in reason.lower() else 1
        elif t == "SELL": strength -= 2 if "mạnh" in reason.lower() or "crossover" in reason.lower() else 1

    # ── RSI ──
    if rsi < RSI_OVERSOLD:
        add("BUY",  f"RSI quá bán mạnh ({rsi:.1f})", rsi)
    elif rsi < RSI_OVERSOLD + 10:
        add("BUY",  f"RSI tiệm cận vùng quá bán ({rsi:.1f})", rsi)
    elif rsi > RSI_OVERBOUGHT:
        add("SELL", f"RSI quá mua mạnh ({rsi:.1f})", rsi)
    elif rsi > RSI_OVERBOUGHT - 10:
        add("SELL", f"RSI tiệm cận vùng quá mua ({rsi:.1f})", rsi)

    # ── Stochastic RSI ──
    if not any(np.isnan(v) for v in [sk, sd, skp, sdp]):
        if sk < STOCHRSI_OVERSOLD and sd < STOCHRSI_OVERSOLD:
            add("BUY",  f"StochRSI quá bán ({sk:.1f})", sk)
        elif skp < sdp and sk > sd and sk < 50:
            add("BUY",  "StochRSI crossover tăng (K cắt lên D)", sk)
        if sk > STOCHRSI_OVERBOUGHT and sd > STOCHRSI_OVERBOUGHT:
            add("SELL", f"StochRSI quá mua ({sk:.1f})", sk)
        elif skp > sdp and sk < sd and sk > 50:
            add("SELL", "StochRSI crossover giảm (K cắt xuống D)", sk)

    # ── Williams %R ──
    if not np.isnan(wpr):
        if wpr <= WILLIAMS_OVERSOLD:
            add("BUY",  f"Williams %R quá bán ({wpr:.1f})", wpr)
        elif wpr >= WILLIAMS_OVERBOUGHT:
            add("SELL", f"Williams %R quá mua ({wpr:.1f})", wpr)

    # ── CCI ──
    if not np.isnan(cci):
        if cci < CCI_OVERSOLD:
            add("BUY",  f"CCI vùng quá bán ({cci:.0f})", cci)
        elif cci > CCI_OVERBOUGHT:
            add("SELL", f"CCI vùng quá mua ({cci:.0f})", cci)

    # ── MACD ──
    if macd > msig and mh > 0:
        add("BUY",  "MACD cắt lên Signal ↑ crossover mạnh", macd)
    elif macd < msig and mh < 0:
        add("SELL", "MACD cắt xuống Signal ↓ crossover mạnh", macd)

    # ── Bollinger Bands ──
    if p <= bbl:
        add("BUY",  f"Giá chạm/phá dải dưới BB mạnh", p)
    elif p >= bbu:
        add("SELL", f"Giá chạm/phá dải trên BB mạnh", p)

    # ── EMA Crossover ──
    if e9 > e21 and e21 > e50:
        add("BUY",  "EMA9>21>50 — xu hướng tăng", e9)
    elif e9 < e21 and e21 < e50:
        add("SELL", "EMA9<21<50 — xu hướng giảm", e9)

    # ── Golden / Death Cross ──
    if e50 > e200:
        add("BUY",  "Golden Cross: EMA50 > EMA200 (dài hạn)", e50)
    else:
        add("SELL", "Death Cross: EMA50 < EMA200 (dài hạn)", e50)

    # ── Ichimoku ──
    if not any(np.isnan(v) for v in [tk, kj, sa, sb]):
        cloud_top = max(sa, sb);  cloud_bot = min(sa, sb)
        if p > cloud_top:
            add("BUY",  "Ichimoku: giá trên mây (xu hướng tăng)", p)
        elif p < cloud_bot:
            add("SELL", "Ichimoku: giá dưới mây (xu hướng giảm)", p)
        # TK Cross
        if tk > kj:
            add("BUY",  "Ichimoku: Tenkan cắt lên Kijun (TK Cross)", tk)
        else:
            add("SELL", "Ichimoku: Tenkan dưới Kijun (bearish)", tk)

    # ── OBV ──
    if not np.isnan(obv) and not np.isnan(obvp):
        if obv > obvp and p > data.get("price", p):
            signals.append(("INFO", f"OBV tăng — xác nhận xu hướng tăng", obv))
        elif obv < obvp:
            signals.append(("INFO", f"OBV giảm — áp lực bán gia tăng", obv))

    # ── Fibonacci ──
    fib_levels = [
        (data["fib_618"], "61.8%"), (data["fib_500"], "50%"),
        (data["fib_382"], "38.2%"), (data["fib_236"], "23.6%"),
    ]
    for fval, fname in fib_levels:
        if abs(p - fval) / p < 0.008:
            signals.append(("INFO", f"Giá gần vùng Fibonacci {fname} (${fval:.5g})", p))

    # ── Volume ──
    if vol > 2.0:
        signals.append(("INFO", f"Volume đột biến cực mạnh ({vol:.1f}× TB)", vol))
    elif vol > 1.5:
        signals.append(("INFO", f"Volume cao bất thường ({vol:.1f}× TB)", vol))

    # ── ATR (thông tin về độ biến động) ──
    if not np.isnan(atr):
        atr_pct = atr / p * 100
        signals.append(("INFO", f"ATR: ${atr:.5g} — biến động {atr_pct:.1f}%/nến", atr))

    # ── Support / Resistance ──
    if p > 0:
        if abs(p - s1) / p < 0.012:
            add("BUY",  f"Giá gần hỗ trợ S1 (${s1:.5g})", p)
        if abs(p - r1) / p < 0.012:
            add("SELL", f"Giá gần kháng cự R1 (${r1:.5g})", p)

    # ── Tín hiệu tổng ──
    if   strength >= 6:  overall = "🟢 MUA RẤT MẠNH"
    elif strength >= 4:  overall = "🟢 MUA MẠNH"
    elif strength >= 2:  overall = "🟡 CÓ THỂ MUA"
    elif strength >= 1:  overall = "🔵 TĂNG NHẸ"
    elif strength <= -6: overall = "🔴 BÁN RẤT MẠNH"
    elif strength <= -4: overall = "🔴 BÁN MẠNH"
    elif strength <= -2: overall = "🟠 CÓ THỂ BÁN"
    elif strength <= -1: overall = "🟤 GIẢM NHẸ"
    else:                overall = "⚪ TRUNG TÍNH — CHỜ"

    return signals, overall, strength
