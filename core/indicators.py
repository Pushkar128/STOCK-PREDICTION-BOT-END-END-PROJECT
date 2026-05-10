import pandas as pd
import numpy as np

def compute_indicators(df):
    if df.empty or len(df) < 50:
        return df
        
    # EMA 20 & 50 calculation is fine
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    
    # RSI Calculation (14 period)
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    
    # FIX: Calculate average volume of the PREVIOUS 20 completed candles
    # This prevents the "live" growing volume from messing up the average
    df["avg_volume"] = df["volume"].shift(1).rolling(window=20).mean()
    
    return df

def generate_signal(df):
    if len(df) < 2:
        return "WAIT", None

    latest = df.iloc[-1]
    
    # Safety Check: Ensure we have avg_volume data
    if pd.isna(latest["avg_volume"]):
        return "WAIT", None

    # Now 'latest["volume"]' is your live growing volume
    # and 'latest["avg_volume"]' is the steady target to beat
    volume_spike = latest["volume"] > latest["avg_volume"] * 1.2
    
    is_bullish = latest["ema20"] > latest["ema50"]
    is_bearish = latest["ema20"] < latest["ema50"]
    rsi = latest.get("rsi", 50)   # default 50 if not calculated

    if is_bullish and volume_spike and rsi < 65:
        return "BUY", round(latest["close"] * 1.008, 2)
    elif is_bearish and volume_spike and rsi > 35:
        return "SELL", round(latest["close"] * 0.992, 2)

    return "WAIT", None