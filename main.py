import uvicorn
import pyotp
import pandas as pd
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from SmartApi import SmartConnect
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import logging

# This shuts down the noise but keeps ERROR and CRITICAL alerts
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

# --- INDICATOR LOGIC ---
from core.indicators import compute_indicators, generate_signal

# --- CONFIG ---
API_KEY = "QtoPVyA1"
CLIENT_ID = "AAAL039888"
PASSWORD = "2025"
TOTP_SECRET = "PHL7N7FAWYE3WXRDW2R55SWO5I" #PHL7N7FAWYE3WXRDW2R55SWO5I

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./trades.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class TradeSignal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String)
    stock = Column(String)
    type = Column(String) 
    price = Column(Float)
    target = Column(Float)

Base.metadata.create_all(bind=engine)

# --- GLOBAL STATE ---
market_data = {
    "stock": "SBIN",
    "price": 0,
    "signal": "WAIT",
    "ema20": 0,
    "ema50": 0,
    "is_vol_spike": False,
    "current_vol": 0,
    "avg_vol": 0,
    "target": None,
    "market_status": "LIVE",
    "last_updated": "Initializing..."
}

# --- BACKGROUND BOT LOOP ---
# --- BACKGROUND BOT LOOP ---
def update_market_data_loop():
    global market_data
    print("🚀 AlphaBot SBIN Loop Started...")
    
    obj = SmartConnect(api_key=API_KEY)
    otp = pyotp.TOTP(TOTP_SECRET).now()
    session = obj.generateSession(CLIENT_ID, PASSWORD, otp)

    if not session.get("status"):
        print("❌ Login Failed")
        return

    print("✅ Logged into Angel One")

    while True:
        try:
            now = datetime.now()
            current_time = now.time()
            current_hhmm = now.strftime("%H:%M")
            current_full_time = now.strftime("%Y-%m-%d %H:%M:%S")
            weekday = now.weekday()   # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday

            # === Market Hours + Weekend Check ===
            market_open = datetime.strptime("09:15", "%H:%M").time()
            market_close = datetime.strptime("15:30", "%H:%M").time()

            if weekday >= 5 or current_time < market_open or current_time > market_close:
                market_data["market_status"] = "CLOSED"
                market_data["signal"] = "WAIT"
                
                if weekday >= 5:
                    print(f"😴 WEEKEND - Market Closed. Next trading day: Monday 09:15 AM")
                else:
                    print(f"😴 MARKET CLOSED ({current_hhmm}). Next open: Tomorrow 09:15 AM")
                
                time.sleep(300)   # Sleep 5 minutes
                continue

            market_data["market_status"] = "LIVE"

            # === Rest of your code (fetching candles etc.) ===
            from_date = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
            to_date = now.strftime("%Y-%m-%d %H:%M")

            res = obj.getCandleData({
                "exchange": "NSE",
                "symboltoken": "3045",
                "interval": "FIVE_MINUTE",
                "fromdate": from_date,
                "todate": to_date
            })

            if res and res.get("data"):
                df = pd.DataFrame(res["data"], columns=["time", "open", "high", "low", "close", "volume"])
                df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)

                df = compute_indicators(df)
                latest = df.iloc[-1]

                signal, target = generate_signal(df)

                # Prevent duplicate signals
                if signal != "WAIT" and signal != market_data.get("signal"):
                    db = SessionLocal()
                    new_trade = TradeSignal(
                        time=current_full_time,
                        stock="SBIN",
                        type=signal,
                        price=round(float(latest["close"]), 2),
                        target=target
                    )
                    db.add(new_trade)
                    db.commit()
                    db.close()
                    print(f"💾 RECORDED {signal} at {current_full_time}")

                market_data.update({
                    "price": round(float(latest["close"]), 2),
                    "ema20": round(float(latest.get("ema20", 0)), 2),
                    "ema50": round(float(latest.get("ema50", 0)), 2),
                    "current_vol": int(latest["volume"]),
                    "avg_vol": int(latest.get("avg_volume", 0)),
                    "is_vol_spike": latest["volume"] > latest.get("avg_volume", 0) * 1.2,
                    "signal": signal,
                    "target": target,
                    "last_updated": current_hhmm
                })

                print(f"✅ Dashboard Sync: {current_hhmm} | Signal: {signal}")

            time.sleep(30)

        except Exception as e:
            print(f"🚨 Loop Error: {e}")
            time.sleep(10)
# --- BACKGROUND BOT LOOP ---
# def update_market_data_loop():
#     global market_data
#     print("🚀 AlphaBot SBIN Loop Started...")
    
#     obj = SmartConnect(api_key=API_KEY)
#     otp = pyotp.TOTP(TOTP_SECRET).now()
#     session = obj.generateSession(CLIENT_ID, PASSWORD, otp)

#     if not session.get("status"):
#         print("❌ Login Failed")
#         return

#     print("✅ Logged into Angel One")

#     while True:
#         try:
#             now = datetime.now()
#             current_time = now.time()
#             current_hhmm = now.strftime("%H:%M")
#             current_full_time = now.strftime("%Y-%m-%d %H:%M:%S")

#             # === Market Hours Check ===
#             market_open = datetime.strptime("09:15", "%H:%M").time()
#             market_close = datetime.strptime("15:30", "%H:%M").time()

#             if current_time < market_open or current_time > market_close:
#                 market_data["market_status"] = "CLOSED"
#                 market_data["signal"] = "WAIT"
#                 print(f"😴 MARKET CLOSED ({current_hhmm}). Next market open: Tomorrow 09:15 AM")
#                 time.sleep(300)   # Sleep 5 minutes
#                 continue

#             market_data["market_status"] = "LIVE"

#             # === Fetch Candle Data ===
#             from_date = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
#             to_date = now.strftime("%Y-%m-%d %H:%M")

#             res = obj.getCandleData({
#                 "exchange": "NSE",
#                 "symboltoken": "3045",
#                 "interval": "FIVE_MINUTE",
#                 "fromdate": from_date,
#                 "todate": to_date
#             })

#             if res and res.get("data"):
#                 df = pd.DataFrame(res["data"], columns=["time", "open", "high", "low", "close", "volume"])
#                 df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)

#                 df = compute_indicators(df)
#                 latest = df.iloc[-1]

#                 signal, target = generate_signal(df)

#                 # Save signal only when it changes (prevents duplicates)
#                 if signal != "WAIT" and signal != market_data.get("signal"):
#                     db = SessionLocal()
#                     new_trade = TradeSignal(
#                         time=current_full_time,
#                         stock="SBIN",
#                         type=signal,
#                         price=round(float(latest["close"]), 2),
#                         target=target
#                     )
#                     db.add(new_trade)
#                     db.commit()
#                     db.close()
#                     print(f"💾 RECORDED {signal} at {current_full_time}")

#                 # Update Dashboard
#                 market_data.update({
#                     "price": round(float(latest["close"]), 2),
#                     "ema20": round(float(latest.get("ema20", 0)), 2),
#                     "ema50": round(float(latest.get("ema50", 0)), 2),
#                     "current_vol": int(latest["volume"]),
#                     "avg_vol": int(latest.get("avg_volume", 0)),
#                     "is_vol_spike": latest["volume"] > latest.get("avg_volume", 0) * 1.2,
#                     "signal": signal,
#                     "target": target,
#                     "last_updated": current_hhmm
#                 })

#                 print(f"✅ Dashboard Sync: {current_hhmm} | Signal: {signal}")

#             time.sleep(30)

#         except Exception as e:
#             print(f"🚨 Loop Error: {e}")
#             time.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=update_market_data_loop, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/signal")
def get_signal(): return market_data

@app.get("/history")
def get_history():
    db = SessionLocal()
    trades = db.query(TradeSignal).order_by(TradeSignal.id.desc()).all()
    db.close()
    return trades

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="error", access_log=False)