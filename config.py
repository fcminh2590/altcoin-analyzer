# =====================================================
#  CẤU HÌNH ALTCOIN ANALYZER v2
# =====================================================
import os

# ── TELEGRAM ──────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID_HERE")

# ── DANH SÁCH COIN ────────────────────────────────
# Thêm/bớt coin tùy ý, định dạng: XXXUSDT
WATCHLIST = [
    # ── Top coins ──
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    # ── DeFi ──
    "AVAXUSDT", "LINKUSDT", "UNIUSDT", "AAVEUSDT", "MKRUSDT",
    # ── Layer 2 ──
    "ARBUSDT", "OPUSDT", "MATICUSDT", "STRKUSDT",
    # ── AI & Gaming ──
    "FETUSDT", "RENDERUSDT", "INJUSDT", "NEARUSDT",
    # ── Others ──
    "DOTUSDT", "ADAUSDT", "ATOMUSDT", "LTCUSDT",
]

# ── PHÂN TÍCH ─────────────────────────────────────
TIMEFRAME     = os.getenv("TIMEFRAME", "1h")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))
CANDLE_LIMIT  = 300

# ── NGƯỠNG CÁC CHỈ BÁO ───────────────────────────
RSI_OVERSOLD    = 30
RSI_OVERBOUGHT  = 70

STOCHRSI_OVERSOLD   = 20
STOCHRSI_OVERBOUGHT = 80

WILLIAMS_OVERSOLD   = -80
WILLIAMS_OVERBOUGHT = -20

CCI_OVERSOLD    = -100
CCI_OVERBOUGHT  = 100

# ── NGƯỠNG GỬI ALERT ─────────────────────────────
MIN_SIGNAL_STRENGTH = 3
