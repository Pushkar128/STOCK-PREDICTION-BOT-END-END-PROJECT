from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import numpy as np
import threading
import time
import random

# ================= FASTAPI APP =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= GLOBAL STATE =================

market_state = {
    "stock": "SBIN",
    "price": 0.0,
    "signal": "WAIT",
    "rsi": None,
    "ema20": None,
    "ema50": None,
    "target": None,
    "timeframe": "5–15 mins",
    "sentiment": "NEUTRAL",
    "last_updated": None
}

price_history = []

# ================= UTILS =================

def safe(v):
    """Convert NaN / numpy → JSON safe"""
    if v is None:
        return None
    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
        return None
    return round(float(v), 2)

# ================= INDICATORS =================

def compute_indicators(df):
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# ================= SIGNAL LOGIC =================

def generate_signal(latest):
    price = latest["close"]
    rsi = latest["rsi"]
    ema20 = latest["ema20"]
    ema50 = latest["ema50"]

    signal = "WAIT"
    target = None

    if rsi is not None:
        if rsi < 30 and ema20 > ema50:
            signal = "BUY"
            target = price + 1.5
        elif rsi > 70 and ema20 < ema50:
            signal = "SELL"
            target = price - 1.5

    return signal, target

# ================= BACKGROUND BOT =================

def bot_loop():
    global market_state

    while True:
        # 🔹 Simulated live price (works even when market closed)
        price = round(968 + random.uniform(-2, 2), 2)
        price_history.append(price)

        if len(price_history) > 200:
            price_history.pop(0)

        df = pd.DataFrame({"close": price_history})

        df = compute_indicators(df)
        latest = df.iloc[-1]

        signal, target = generate_signal(latest)

        market_state.update({
            "price": safe(price),
            "rsi": safe(latest["rsi"]),
            "ema20": safe(latest["ema20"]),
            "ema50": safe(latest["ema50"]),
            "signal": signal,
            "target": safe(target),
            "last_updated": datetime.now().strftime("%H:%M:%S")
        })

        print("📊 Updated:", market_state)
        time.sleep(5)   # every 5 seconds

# ================= API =================

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/signal")
def get_signal():
    return market_state

# ================= START BOT =================

threading.Thread(target=bot_loop, daemon=True).start()
