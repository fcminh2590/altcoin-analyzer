# =====================================================
#  CẤU HÌNH ALTCOIN ANALYZER v2
#  ⚠️  Chỉnh sửa file này trước khi chạy!
#  Khi deploy, dùng biến môi trường thay thế.
# =====================================================
import os

# ── TELEGRAM ──────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("8993343438:AAHdAIlMHZu2XUfS13hYs2JEOx4HkTNg7oM")
TELEGRAM_CHAT_ID   = os.getenv("1003655211")

# ── DANH SÁCH COIN ────────────────────────────────
WATCHLIST = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "ADAUSDT", "DOTUSDT", "AVAXUSDT", "LINKUSDT",
    "MATICUSDT", "ARBUSDT",
]

# ── PHÂN TÍCH ─────────────────────────────────────
TIMEFRAME     = os.getenv("TIMEFRAME", "1h")   # 1m 5m 15m 30m 1h 4h 1d
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))  # giây
CANDLE_LIMIT  = 300   # tăng lên để tính Ichimoku chính xác hơn

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
MIN_SIGNAL_STRENGTH = 3   # điểm tối thiểu để gửi (tối đa ~14)
