from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta

from config.credentials import API_KEY, CLIENT_ID, PASSWORD, TOTP_SEED
from core.indicators import compute_indicators, generate_signal_and_target


def login_and_predict():
    # 1️⃣ Connect to Angel One
    obj = SmartConnect(api_key=API_KEY)

    # 2️⃣ Generate TOTP automatically
    otp = pyotp.TOTP(TOTP_SEED).now()

    # 3️⃣ Login (READ-ONLY)
    session = obj.generateSession(CLIENT_ID, PASSWORD, otp)
    if not session.get("status"):
        print("❌ Login failed:", session)
        return

    print("✅ Login successful")

    # 4️⃣ Stock details (SBIN example)
    exchange = "NSE"
    symboltoken = "3045"      # SBIN token
    interval = "FIVE_MINUTE"  # 5-minute timeframe

    # 5️⃣ Time range (last ~2 trading days)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=2)

    # 6️⃣ Fetch historical candle data
    hist = obj.getCandleData({
        "exchange": exchange,
        "symboltoken": symboltoken,
        "interval": interval,
        "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
        "todate": to_date.strftime("%Y-%m-%d %H:%M")
    })

    if "data" not in hist or hist["data"] is None:
        print("❌ No candle data received")
        return

    # 7️⃣ Create DataFrame
    candles = pd.DataFrame(
        hist["data"],
        columns=["time", "open", "high", "low", "close", "volume"]
    )

    # Convert numeric columns
    candles[["open", "high", "low", "close", "volume"]] = candles[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    # 8️⃣ Compute indicators
    candles = compute_indicators(candles)

    latest = candles.iloc[-1]

    # 9️⃣ Generate signal + target + ATR
    signal, target, atr = generate_signal_and_target(latest)

    # 🔟 Print clean output
    print(
        f"\nSBIN | Price: {latest['close']:.2f}\n"
        f"RSI: {latest['rsi']:.2f}\n"
        f"EMA20: {latest['ema20']:.2f}\n"
        f"EMA50: {latest['ema50']:.2f}\n"
        f"Volume: {int(latest['volume'])}\n"
        f"Volume MA20: {int(latest['vol_ma20'])}\n"
        f"ATR: {atr:.2f}\n"
        f"Signal: {signal}"
    )

    if target:
        print(f"Target: {target:.2f}")
        print("Expected Timeframe: 5–15 minutes (5-min candles)")
    else:
        print("Target: N/A (conditions not strong enough)")


if __name__ == "__main__":
    login_and_predict()
# //////////////////////////////////////////////////////////////////////////////////////////////////
from SmartApi import SmartConnect
import pyotp
import pandas as pd
import time
from datetime import datetime, timedelta

from config.credentials import API_KEY, CLIENT_ID, PASSWORD, TOTP_SEED
from core.indicators import compute_indicators, generate_signal_and_target


def seconds_to_next_5min():
    now = datetime.now()
    next_min = ((now.minute // 5) + 1) * 5
    next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=next_min)
    return max(1, int((next_time - now).total_seconds()))


def login_and_run():
    print("🔐 Logging in to Angel One (ONE TIME)...")

    obj = SmartConnect(api_key=API_KEY)
    otp = pyotp.TOTP(TOTP_SEED).now()
    session = obj.generateSession(CLIENT_ID, PASSWORD, otp)

    if not session.get("status"):
        print("❌ Login failed")
        return

    print("✅ Login successful — bot is running\n")

    exchange = "NSE"
    symboltoken = "3045"      # SBIN
    interval = "FIVE_MINUTE"

    try:
        while True:
            sleep_seconds = seconds_to_next_5min()
            print(f"⏳ Waiting {sleep_seconds}s for next candle close...")
            time.sleep(sleep_seconds + 2)  # +2s safety buffer

            to_date = datetime.now()
            from_date = to_date - timedelta(days=2)

            hist = obj.getCandleData({
                "exchange": exchange,
                "symboltoken": symboltoken,
                "interval": interval,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })

            if not hist.get("data"):
                print("⚠ No candle data received")
                continue

            candles = pd.DataFrame(
                hist["data"],
                columns=["time", "open", "high", "low", "close", "volume"]
            )

            candles[["open", "high", "low", "close", "volume"]] = candles[
                ["open", "high", "low", "close", "volume"]
            ].astype(float)

            candles = compute_indicators(candles)
            latest = candles.iloc[-1]

            signal, target, atr = generate_signal_and_target(latest)

            print("\n==============================")
            print(f"Candle Closed At: {latest['time']}")
            print(f"Price: {latest['close']:.2f}")
            print(f"RSI: {latest['rsi']:.2f}")
            print(f"EMA20: {latest['ema20']:.2f}")
            print(f"EMA50: {latest['ema50']:.2f}")
            print(f"Volume: {int(latest['volume'])}")
            print(f"ATR: {atr:.2f}")
            print(f"Signal: {signal}")

            if target:
                print(f"Target: {target:.2f}")
                print("Timeframe: 5–15 minutes")

            print("==============================\n")

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped manually. Logged out safely.")


if __name__ == "__main__":
    login_and_run()
# //////////////////////////////////////////////////
from core.live_data import login_and_run

login_and_run()
