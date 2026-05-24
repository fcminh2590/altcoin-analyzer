# 🚀 Altcoin Analyzer v2

Hệ thống phân tích kỹ thuật altcoin tự động với **10+ chỉ báo** và deploy lên cloud miễn phí.

---

## 📊 Chỉ báo có trong phiên bản này

| Chỉ báo | Mô tả |
|---|---|
| **RSI 14** | Relative Strength Index — quá mua/quá bán |
| **Stochastic RSI** | RSI của RSI, nhạy hơn — K và D crossover |
| **Williams %R** | Momentum oscillator — xác nhận đảo chiều |
| **CCI** | Commodity Channel Index — chu kỳ thị trường |
| **MACD** | Trend + momentum — crossover tín hiệu |
| **Bollinger Bands** | Dải biến động giá — squeeze & breakout |
| **EMA 9/21/50/200** | Đường trung bình lũy thừa — crossover |
| **SMA 20/50** | Đường trung bình đơn giản |
| **Ichimoku Cloud** | Hỗ trợ/kháng cự + xu hướng Nhật Bản |
| **Fibonacci** | 7 mức retracement từ swing H/L |
| **ATR 14** | Average True Range — đo độ biến động |
| **OBV** | On-Balance Volume — dòng tiền |
| **Support/Resistance** | Pivot Point — 2 mức S và R |
| **Volume** | So sánh với trung bình 20 nến |

---

## 🖥️ Cài đặt local (máy tính của bạn)

### Yêu cầu
- Python 3.9+ → https://python.org/downloads
  - ⚠️ Windows: tick **"Add Python to PATH"** khi cài

### Các bước

```bash
# 1. Vào thư mục
cd altcoin_v2

# 2. Cài thư viện (chỉ 1 lần)
pip install -r requirements.txt

# 3a. Mở Dashboard (cửa sổ 1)
streamlit run dashboard.py

# 3b. Chạy Bot Telegram (cửa sổ 2)
python main.py
```

Dashboard mở tại: **http://localhost:8501**

---

## ☁️ Deploy lên Cloud (miễn phí, chạy 24/7)

### Cấu trúc deploy

```
📊 Dashboard  →  Streamlit Community Cloud  (miễn phí mãi mãi)
🤖 Bot Telegram →  Render.com worker         (miễn phí)
```

---

### PHẦN 1: Đưa code lên GitHub

**Bước 1** — Tạo tài khoản GitHub tại https://github.com

**Bước 2** — Tạo repository mới:
  - Nhấn **"New repository"**
  - Đặt tên: `altcoin-analyzer`
  - Chọn **Public**
  - Nhấn **"Create repository"**

**Bước 3** — Upload code:
  - Vào trang repo vừa tạo
  - Nhấn **"uploading an existing file"**
  - Kéo thả toàn bộ file trong thư mục `altcoin_v2` vào
  - Nhấn **"Commit changes"**

> ⚠️ **Không** upload file `.env` hoặc `secrets.toml` — chứa thông tin bảo mật!

---

### PHẦN 2: Deploy Dashboard lên Streamlit Cloud

1. Vào https://streamlit.io/cloud → **Sign in with GitHub**
2. Nhấn **"New app"**
3. Chọn repository `altcoin-analyzer`
4. Main file path: `dashboard.py`
5. Nhấn **"Advanced settings"** → **Secrets** → dán vào:
   ```toml
   TELEGRAM_BOT_TOKEN = "token_của_bạn"
   TELEGRAM_CHAT_ID   = "chat_id_của_bạn"
   ```
6. Nhấn **"Deploy!"**

✅ Sau vài phút, bạn có URL dashboard dạng:
`https://your-app.streamlit.app`

---

### PHẦN 3: Deploy Bot Telegram lên Render

1. Vào https://render.com → **Sign up** (dùng GitHub account)
2. Nhấn **"New +"** → **"Background Worker"**
3. Chọn repository `altcoin-analyzer`
4. Điền:
   - **Name**: `altcoin-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: `Free`
5. Nhấn **"Environment"** → thêm các biến:

   | Key | Value |
   |---|---|
   | `TELEGRAM_BOT_TOKEN` | token của bạn |
   | `TELEGRAM_CHAT_ID` | chat ID của bạn |
   | `TIMEFRAME` | `1h` |
   | `SCAN_INTERVAL` | `300` |

6. Nhấn **"Create Background Worker"**

✅ Bot sẽ chạy 24/7 và gửi Telegram khi có tín hiệu!

---

## 🔑 Lấy Token & Chat ID Telegram

### Token (BotFather):
1. Mở Telegram → tìm **@BotFather**
2. Nhắn: `/newbot`
3. Đặt tên bot → lấy token dạng `123456:ABCdef...`

### Chat ID:
1. Nhắn bất kỳ tin nhắn cho bot của bạn
2. Mở trình duyệt, vào:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Tìm `"chat":{"id":` → đó là Chat ID

---

## 📖 Đọc tín hiệu

| Điểm | Ý nghĩa |
|---|---|
| ≥ +6 | 🟢 MUA RẤT MẠNH |
| +4 đến +5 | 🟢 MUA MẠNH |
| +2 đến +3 | 🟡 CÓ THỂ MUA |
| +1 | 🔵 TĂNG NHẸ |
| 0 | ⚪ TRUNG TÍNH — CHỜ |
| -1 | 🟤 GIẢM NHẸ |
| -2 đến -3 | 🟠 CÓ THỂ BÁN |
| -4 đến -5 | 🔴 BÁN MẠNH |
| ≤ -6 | 🔴 BÁN RẤT MẠNH |

---

## ⚠️ Tuyên bố miễn trách

Đây là **công cụ hỗ trợ phân tích kỹ thuật**, không phải lời khuyên đầu tư.
Thị trường crypto biến động cao — hãy tự nghiên cứu và chịu trách nhiệm về quyết định của mình.
