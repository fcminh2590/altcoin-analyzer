"""
dashboard.py — Web Dashboard đầy đủ tất cả chỉ báo
Chạy: streamlit run dashboard.py
"""
import time, numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import WATCHLIST, TIMEFRAME
from data_fetcher import get_ohlcv, get_ticker_24h
from analyzer import analyze, generate_signals

st.set_page_config(page_title="🚀 Altcoin Analyzer v2", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

# ── Dark theme CSS ────────────────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="stMetric"] { background:#1a1d2e; border-radius:10px; padding:10px 14px; }
.buy-signal  { background:#0a2e18; border-left:3px solid #00e676;
               padding:6px 12px; border-radius:4px; margin:3px 0; font-size:0.9em; }
.sell-signal { background:#2e0a0a; border-left:3px solid #ff1744;
               padding:6px 12px; border-radius:4px; margin:3px 0; font-size:0.9em; }
.info-signal { background:#1a1a2e; border-left:3px solid #64b5f6;
               padding:6px 12px; border-radius:4px; margin:3px 0; font-size:0.9em; }
</style>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Cài đặt")
    st.markdown("**🪙 Chọn coin**")
    coin_mode = st.radio("", ["Danh sách có sẵn", "Tìm kiếm bất kỳ"], horizontal=True, label_visibility="collapsed")

    if coin_mode == "Danh sách có sẵn":
        coin = st.selectbox("", WATCHLIST, label_visibility="collapsed")
    else:
        custom = st.text_input("Nhập tên coin (VD: PEPEUSDT, SHIBUSDT...)", value="BTCUSDT").strip().upper()
        if not custom.endswith("USDT"):
            custom = custom + "USDT"
        coin = custom
        st.caption(f"Sẽ tìm: **{coin}**")
    tf   = st.selectbox("⏱ Timeframe", ["1m","5m","15m","30m","1h","4h","1d","1w","1M"], index=4)

    st.markdown("**Overlay giá:**")
    show_ema = st.checkbox("EMA 9/21/50/200", True)
    show_bb  = st.checkbox("Bollinger Bands", True)
    show_ich = st.checkbox("Ichimoku Cloud",  True)
    show_fib = st.checkbox("Fibonacci",       True)
    show_sr  = st.checkbox("Support/Resistance", True)

    st.markdown("**Bảng phụ:**")
    show_macd  = st.checkbox("MACD",         True)
    show_rsi   = st.checkbox("RSI",          True)
    show_stoch = st.checkbox("Stochastic RSI", True)
    show_wpr   = st.checkbox("Williams %R",  True)
    show_cci   = st.checkbox("CCI",          True)
    show_atr   = st.checkbox("ATR",          False)
    show_obv   = st.checkbox("OBV",          False)
    show_vol   = st.checkbox("Volume",       True)

    st.divider()
    auto_ref = st.checkbox("🔄 Auto refresh", False)
    ref_sec  = st.slider("Chu kỳ (giây)", 30, 300, 60, 30)
    st.divider()
    st.caption("📡 Dữ liệu: Binance API\n(Miễn phí, không cần API key)")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def load(sym, timeframe):
    df = get_ohlcv(sym, timeframe, limit=300)
    d  = analyze(df)
    s, ov, sc = generate_signals(d)
    tk = get_ticker_24h(sym)
    return d, s, ov, sc, tk

# ── Helpers ───────────────────────────────────────────────────────────────────
DARK = "#0e1117"
PLOT = dict(template="plotly_dark", paper_bgcolor=DARK, plot_bgcolor=DARK,
            font_color="#e0e0e0", margin=dict(l=10,r=80,t=30,b=10),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))

def add_candlestick(fig, df, row=1):
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="Giá",
        increasing_line_color="#00c853", decreasing_line_color="#ff1744",
        increasing_fillcolor="#00c853",  decreasing_fillcolor="#ff1744",
    ), row=row, col=1)

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🚀 Altcoin Technical Analyzer v2")
st.caption("RSI · MACD · StochRSI · Williams %R · CCI · Bollinger · EMA · Ichimoku · Fibonacci · ATR · OBV")
st.divider()

try:
    with st.spinner(f"Đang tải {coin} [{tf}]…"):
        data, signals, overall, score, ticker = load(coin, tf)

    pct = float(ticker.get("priceChangePercent", 0))
    p   = data["price"]
    vol = float(ticker.get("quoteVolume", 0))

    # ── Metrics row ──
    m = st.columns(7)
    m[0].metric("💰 Giá",        f"${p:,.6g}",         f"{pct:+.2f}%")
    m[1].metric("📊 RSI",        f"{data['rsi']:.1f}",
                "QB" if data['rsi']<30 else ("QM" if data['rsi']>70 else "OK"))
    m[2].metric("⚡ StochRSI K", f"{data['stoch_k']:.1f}")
    m[3].metric("📉 Williams %R",f"{data['williams_r']:.1f}")
    m[4].metric("📐 CCI",        f"{data['cci']:.0f}")
    m[5].metric("📦 Volume",     f"{data['volume_ratio']:.1f}×",
                "⚠️ Cao" if data['volume_ratio']>1.5 else "Bình thường")
    m[6].metric("🏆 Tín hiệu",   overall, f"Điểm: {score:+d}")

    st.divider()

    # ── Build subplot list ────────────────────────────────────────────────────
    sub_rows   = [("Biểu đồ giá", 0.40)]
    if show_macd:  sub_rows.append(("MACD",          0.12))
    if show_rsi:   sub_rows.append(("RSI",           0.10))
    if show_stoch: sub_rows.append(("Stochastic RSI",0.10))
    if show_wpr:   sub_rows.append(("Williams %R",   0.09))
    if show_cci:   sub_rows.append(("CCI",           0.09))
    if show_atr:   sub_rows.append(("ATR",           0.09))
    if show_obv:   sub_rows.append(("OBV",           0.09))
    if show_vol:   sub_rows.append(("Volume",        0.09))

    n   = len(sub_rows)
    heights = [r[1] for r in sub_rows]
    total   = sum(heights)
    heights = [h/total for h in heights]

    fig = make_subplots(rows=n, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        subplot_titles=[r[0] for r in sub_rows],
                        row_heights=heights)

    df   = data["df"]
    idx  = df.index
    row  = 1

    # ── Row 1: Price chart ────────────────────────────────────────────────────
    add_candlestick(fig, df, row)

    if show_bb:
        for y, name, color, fill in [
            (data["bb_upper_s"], "BB↑", "rgba(255,193,7,.5)", None),
            (data["bb_mid_s"],   "BBm", "rgba(255,193,7,.25)",None),
            (data["bb_lower_s"],"BB↓", "rgba(255,193,7,.5)","tonexty"),
        ]:
            fig.add_trace(go.Scatter(x=idx, y=y, name=name, showlegend=True,
                line=dict(color=color,width=1,dash="dash"),
                fill=fill, fillcolor="rgba(255,193,7,.03)"), row=row, col=1)

    if show_ema:
        for key, name, color, w in [
            ("ema9_s","EMA9","#ff6b6b",1),("ema21_s","EMA21","#4ecdc4",1),
            ("ema50_s","EMA50","#45b7d1",1.5),("ema200_s","EMA200","#f9ca24",2),
        ]:
            fig.add_trace(go.Scatter(x=idx, y=data[key], name=name,
                line=dict(color=color,width=w)), row=row, col=1)

    if show_ich:
        tk_s, kj_s = data["tenkan_s"], data["kijun_s"]
        sa_s, sb_s = data["span_a_s"], data["span_b_s"]
        fig.add_trace(go.Scatter(x=idx, y=tk_s, name="Tenkan",
            line=dict(color="#e91e63",width=1.2)), row=row, col=1)
        fig.add_trace(go.Scatter(x=idx, y=kj_s, name="Kijun",
            line=dict(color="#2196f3",width=1.2)), row=row, col=1)
        fig.add_trace(go.Scatter(x=idx, y=sa_s, name="SpanA",
            line=dict(color="rgba(0,230,118,.4)",width=1)), row=row, col=1)
        fig.add_trace(go.Scatter(x=idx, y=sb_s, name="SpanB",
            line=dict(color="rgba(255,82,82,.4)",width=1),
            fill="tonexty", fillcolor="rgba(120,120,200,.07)"), row=row, col=1)

    if show_fib:
        fib_cfg = [
            ("fib_0",  "Fib 0%",    "rgba(200,200,200,.4)"),
            ("fib_236","Fib 23.6%", "rgba(100,181,246,.5)"),
            ("fib_382","Fib 38.2%", "rgba(129,212,250,.5)"),
            ("fib_500","Fib 50%",   "rgba(255,255,100,.5)"),
            ("fib_618","Fib 61.8%", "rgba(255,167,38,.6)"),
            ("fib_786","Fib 78.6%", "rgba(239,83,80,.5)"),
            ("fib_100","Fib 100%",  "rgba(200,200,200,.4)"),
        ]
        for key, label, color in fib_cfg:
            fig.add_hline(y=data[key], line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right",
                          row=row, col=1)

    if show_sr:
        for val, label, color in [
            (data["resistance_2"],f"R2 {data['resistance_2']:.5g}","rgba(255,82,82,.5)"),
            (data["resistance_1"],f"R1 {data['resistance_1']:.5g}","rgba(255,82,82,.85)"),
            (data["pivot"],       f"P  {data['pivot']:.5g}",      "rgba(200,200,200,.4)"),
            (data["support_1"],   f"S1 {data['support_1']:.5g}",  "rgba(0,200,83,.85)"),
            (data["support_2"],   f"S2 {data['support_2']:.5g}",  "rgba(0,200,83,.5)"),
        ]:
            fig.add_hline(y=val, line_dash="dot", line_color=color,
                          annotation_text=label, annotation_position="right",
                          row=row, col=1)
    row += 1

    # ── MACD ──────────────────────────────────────────────────────────────────
    if show_macd:
        fig.add_trace(go.Scatter(x=idx,y=data["macd_s"],   name="MACD",   line=dict(color="#4ecdc4",width=1.5)), row=row,col=1)
        fig.add_trace(go.Scatter(x=idx,y=data["signal_s"], name="Signal", line=dict(color="#ff6b6b",width=1.5)), row=row,col=1)
        hc = ["#00c853" if v>=0 else "#ff1744" for v in data["hist_s"]]
        fig.add_trace(go.Bar(x=idx,y=data["hist_s"],name="Hist",marker_color=hc,opacity=.7), row=row,col=1)
        fig.add_hline(y=0, line_color="rgba(255,255,255,.2)", row=row, col=1)
        row += 1

    # ── RSI ───────────────────────────────────────────────────────────────────
    if show_rsi:
        fig.add_trace(go.Scatter(x=idx,y=data["rsi_s"],name="RSI",line=dict(color="#a29bfe",width=1.5)), row=row,col=1)
        for y, color in [(70,"rgba(255,82,82,.7)"),(30,"rgba(0,200,83,.7)")]:
            fig.add_hline(y=y, line_dash="dash", line_color=color, row=row, col=1)
        fig.add_hrect(y0=70,y1=100, fillcolor="rgba(255,82,82,.07)", row=row,col=1)
        fig.add_hrect(y0=0, y1=30,  fillcolor="rgba(0,200,83,.07)",  row=row,col=1)
        row += 1

    # ── Stochastic RSI ────────────────────────────────────────────────────────
    if show_stoch:
        fig.add_trace(go.Scatter(x=idx,y=data["stoch_k_s"],name="StochK",line=dict(color="#fd79a8",width=1.5)), row=row,col=1)
        fig.add_trace(go.Scatter(x=idx,y=data["stoch_d_s"],name="StochD",line=dict(color="#fdcb6e",width=1.5)), row=row,col=1)
        for y, color in [(80,"rgba(255,82,82,.7)"),(20,"rgba(0,200,83,.7)")]:
            fig.add_hline(y=y, line_dash="dash", line_color=color, row=row, col=1)
        fig.add_hrect(y0=80,y1=100, fillcolor="rgba(255,82,82,.07)", row=row,col=1)
        fig.add_hrect(y0=0, y1=20,  fillcolor="rgba(0,200,83,.07)",  row=row,col=1)
        row += 1

    # ── Williams %R ───────────────────────────────────────────────────────────
    if show_wpr:
        fig.add_trace(go.Scatter(x=idx,y=data["wpr_s"],name="W%R",line=dict(color="#00cec9",width=1.5)), row=row,col=1)
        for y, color in [(-20,"rgba(255,82,82,.7)"),(-80,"rgba(0,200,83,.7)")]:
            fig.add_hline(y=y, line_dash="dash", line_color=color, row=row, col=1)
        row += 1

    # ── CCI ───────────────────────────────────────────────────────────────────
    if show_cci:
        fig.add_trace(go.Scatter(x=idx,y=data["cci_s"],name="CCI",line=dict(color="#e17055",width=1.5)), row=row,col=1)
        for y, color in [(100,"rgba(255,82,82,.7)"),(-100,"rgba(0,200,83,.7)")]:
            fig.add_hline(y=y, line_dash="dash", line_color=color, row=row, col=1)
        fig.add_hline(y=0, line_color="rgba(255,255,255,.2)", row=row, col=1)
        row += 1

    # ── ATR ───────────────────────────────────────────────────────────────────
    if show_atr:
        fig.add_trace(go.Scatter(x=idx,y=data["atr_s"],name="ATR",line=dict(color="#6c5ce7",width=1.5)), row=row,col=1)
        row += 1

    # ── OBV ───────────────────────────────────────────────────────────────────
    if show_obv:
        fig.add_trace(go.Scatter(x=idx,y=data["obv_s"],name="OBV",
            line=dict(color="#00b894",width=1.5),fill="tozeroy",
            fillcolor="rgba(0,184,148,.07)"), row=row,col=1)
        row += 1

    # ── Volume bars ───────────────────────────────────────────────────────────
    if show_vol:
        vc = ["#00c853" if c>=o else "#ff1744"
              for c,o in zip(df["close"],df["open"])]
        fig.add_trace(go.Bar(x=idx,y=df["volume"],name="Volume",
            marker_color=vc,opacity=.7), row=row,col=1)
        fig.add_trace(go.Scatter(x=idx,y=data["vol_ma_s"] if hasattr(data.get("vol_ma_s",None),"iloc") else None,
            name="Vol MA20",line=dict(color="#fdcb6e",width=1.2)), row=row,col=1)

    fig.update_layout(height=max(500, 160*n), **PLOT)
    st.plotly_chart(fig, use_container_width=True)

    # ── Tín hiệu chi tiết ────────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 Tín hiệu chi tiết")
    cb, cs = st.columns(2)

    with cb:
        st.markdown("#### 🟢 Tín hiệu MUA")
        buys = [r for t,r,_ in signals if t=="BUY"]
        for r in buys: st.markdown(f'<div class="buy-signal">✓ {r}</div>', unsafe_allow_html=True)
        if not buys: st.info("Không có tín hiệu mua.")

    with cs:
        st.markdown("#### 🔴 Tín hiệu BÁN")
        sells = [r for t,r,_ in signals if t=="SELL"]
        for r in sells: st.markdown(f'<div class="sell-signal">✗ {r}</div>', unsafe_allow_html=True)
        if not sells: st.info("Không có tín hiệu bán.")

    infos = [r for t,r,_ in signals if t=="INFO"]
    if infos:
        st.markdown("#### ℹ️ Thông tin thêm")
        for r in infos: st.markdown(f'<div class="info-signal">• {r}</div>', unsafe_allow_html=True)

    # ── Bảng số liệu ─────────────────────────────────────────────────────────
    with st.expander("📊 Bảng chỉ báo đầy đủ", expanded=False):
        metrics_df = pd.DataFrame({
            "Chỉ báo": ["RSI 14","StochRSI K","StochRSI D","Williams %R","CCI",
                         "MACD","MACD Signal","MACD Hist","ATR",
                         "EMA9","EMA21","EMA50","EMA200",
                         "BB Upper","BB Middle","BB Lower",
                         "Tenkan","Kijun","Span A","Span B"],
            "Giá trị": [
                f"{data['rsi']:.2f}", f"{data['stoch_k']:.2f}", f"{data['stoch_d']:.2f}",
                f"{data['williams_r']:.2f}", f"{data['cci']:.2f}",
                f"{data['macd']:.6g}", f"{data['macd_signal']:.6g}", f"{data['macd_hist']:.6g}",
                f"{data['atr']:.5g}",
                f"{data['ema9']:.5g}", f"{data['ema21']:.5g}",
                f"{data['ema50']:.5g}", f"{data['ema200']:.5g}",
                f"{data['bb_upper']:.5g}", f"{data['bb_middle']:.5g}", f"{data['bb_lower']:.5g}",
                f"{data['tenkan']:.5g}", f"{data['kijun']:.5g}",
                f"{data['span_a']:.5g}", f"{data['span_b']:.5g}",
            ],
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    with st.expander("🛡️ Hỗ trợ, Kháng cự & Fibonacci"):
        c1, c2 = st.columns(2)
        with c1:
            sr_df = pd.DataFrame({
                "Mức": ["R2","R1","Pivot","S1","S2"],
                "Giá ($)": [f"{data[k]:.6g}" for k in
                            ["resistance_2","resistance_1","pivot","support_1","support_2"]],
            })
            st.dataframe(sr_df, use_container_width=True, hide_index=True)
        with c2:
            fib_df = pd.DataFrame({
                "Fibonacci": ["0% (High)","23.6%","38.2%","50%","61.8%","78.6%","100% (Low)"],
                "Giá ($)": [f"{data[k]:.6g}" for k in
                            ["fib_0","fib_236","fib_382","fib_500","fib_618","fib_786","fib_100"]],
            })
            st.dataframe(fib_df, use_container_width=True, hide_index=True)

    # ── Watchlist overview ────────────────────────────────────────────────────
    st.divider()
    st.subheader("👀 Watchlist")
    rows = []
    for sym in WATCHLIST:
        try:
            d, sigs, ov, sc, _ = load(sym, tf)
            rows.append({
                "Coin": sym,
                "Giá ($)": f"{d['price']:,.6g}",
                "RSI": f"{d['rsi']:.1f}",
                "StochK": f"{d['stoch_k']:.1f}",
                "W%R": f"{d['williams_r']:.1f}",
                "CCI": f"{d['cci']:.0f}",
                "MACD": "↑" if d["macd"]>d["macd_signal"] else "↓",
                "Ichimoku": ("☁️ Trên" if d["price"]>max(d["span_a"],d["span_b"])
                              else "☁️ Dưới" if d["price"]<min(d["span_a"],d["span_b"]) else "☁️ Trong"),
                "Vol": f"{d['volume_ratio']:.1f}×",
                "Tín hiệu": ov, "Điểm": sc,
            })
        except:
            rows.append({"Coin": sym, "Tín hiệu": "⛔ Lỗi"})

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if auto_ref:
        for i in range(ref_sec, 0, -1):
            st.caption(f"🔄 Làm mới sau {i}s…"); time.sleep(1)
        st.cache_data.clear(); st.rerun()

except Exception as e:
    st.error(f"❌ Lỗi: {e}")
    st.code(str(e))
