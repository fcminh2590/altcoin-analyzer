"""
alerts.py — Gửi cảnh báo Telegram, chống spam
"""
import requests, logging
logger = logging.getLogger(__name__)


def send_telegram(msg: str, token: str, chat_id: str) -> bool:
    if not token or "YOUR_BOT" in token:
        logger.warning("Telegram chưa cấu hình"); return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
        ok = r.status_code == 200
        if ok: logger.info("✅ Telegram sent")
        else:  logger.error(f"❌ Telegram {r.status_code}: {r.text[:200]}")
        return ok
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}"); return False


def build_message(symbol, data, signals, overall, strength, tf) -> str:
    buys  = [r for t,r,_ in signals if t=="BUY"]
    sells = [r for t,r,_ in signals if t=="SELL"]
    infos = [r for t,r,_ in signals if t=="INFO"]

    def fmt_list(items, limit=6):
        return "\n".join(f"  • {i}" for i in items[:limit]) or "  (không có)"

    wpr = data.get("williams_r", float("nan"))
    cci = data.get("cci", float("nan"))
    sk  = data.get("stoch_k", float("nan"))

    return (
        f"🔔 <b>CẢNH BÁO: {symbol} [{tf}]</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 Giá: <b>${data['price']:,.6g}</b>\n"
        f"📊 Tín hiệu: <b>{overall}</b>  (điểm: {strength:+d})\n\n"
        f"🔢 <b>Chỉ báo:</b>\n"
        f"  RSI 14: {data['rsi']:.1f}  |  StochRSI K: {sk:.1f}\n"
        f"  Williams %R: {wpr:.1f}  |  CCI: {cci:.0f}\n"
        f"  MACD hist: {data['macd_hist']:+.5g}\n"
        f"  BB: [{data['bb_lower']:.5g} — {data['bb_upper']:.5g}]\n"
        f"  ATR: ${data['atr']:.5g}  |  Vol: {data['volume_ratio']:.1f}×\n\n"
        f"🟢 <b>Tín hiệu MUA ({len(buys)}):</b>\n{fmt_list(buys)}\n\n"
        f"🔴 <b>Tín hiệu BÁN ({len(sells)}):</b>\n{fmt_list(sells)}\n\n"
        f"ℹ️ {fmt_list(infos, 3)}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ S1: ${data['support_1']:.5g}  |  R1: ${data['resistance_1']:.5g}\n"
        f"📐 Fib 61.8%: ${data['fib_618']:.5g}  |  38.2%: ${data['fib_382']:.5g}\n"
        f"☁️ Ichimoku: Tenkan {data['tenkan']:.5g} / Kijun {data['kijun']:.5g}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Phân tích kỹ thuật, không phải lời khuyên đầu tư."
    )


class AlertTracker:
    def __init__(self): self._last = {}
    def should_send(self, sym, overall):
        if self._last.get(sym) != overall:
            self._last[sym] = overall; return True
        return False
