"""
main.py — Bot quét thị trường và gửi cảnh báo Telegram 24/7
Chạy: python main.py
"""
import time, logging, sys
from config import (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
                    WATCHLIST, TIMEFRAME, SCAN_INTERVAL, MIN_SIGNAL_STRENGTH)
from data_fetcher import get_ohlcv
from analyzer    import analyze, generate_signals
from alerts      import send_telegram, build_message, AlertTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log     = logging.getLogger(__name__)
tracker = AlertTracker()


def scan():
    log.info(f"🔍 Quét {len(WATCHLIST)} coins [{TIMEFRAME}]…")
    for sym in WATCHLIST:
        try:
            df              = get_ohlcv(sym, TIMEFRAME)
            data            = analyze(df)
            sigs, ov, score = generate_signals(data)
            log.info(f"  {sym:12s}  {ov}  ({score:+d})")
            if abs(score) >= MIN_SIGNAL_STRENGTH and tracker.should_send(sym, ov):
                msg = build_message(sym, data, sigs, ov, score, TIMEFRAME)
                send_telegram(msg, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        except Exception as e:
            log.error(f"  ❌ {sym}: {e}")
        time.sleep(0.5)
    log.info("✅ Xong.\n")


def main():
    log.info("=" * 50)
    log.info("🚀 Altcoin Analyzer Bot v2 khởi động!")
    log.info(f"   Coins: {', '.join(WATCHLIST)}")
    log.info(f"   TF: {TIMEFRAME}  |  Quét mỗi {SCAN_INTERVAL}s")
    log.info("=" * 50)

    send_telegram(
        f"🚀 <b>Bot khởi động!</b>\n"
        f"Theo dõi {len(WATCHLIST)} coins [{TIMEFRAME}]\n"
        + ", ".join(WATCHLIST),
        TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    )

    while True:
        try:
            scan()
        except KeyboardInterrupt:
            log.info("👋 Dừng."); break
        except Exception as e:
            log.error(f"Lỗi vòng chính: {e}")
        log.info(f"😴 Chờ {SCAN_INTERVAL}s…")
        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    main()
