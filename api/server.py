# from fastapi import FastAPI

# app = FastAPI()

# latest_signal = {
#     "stock": "SBIN",
#     "price": 972.15,
#     "signal": "WAIT",
#     "rsi": 46.6,
#     "ema20": 973.4,
#     "ema50": 973.9,
#     "target": None,
#     "timeframe": "5–15 mins"
# }

# @app.get("/signal")
# def get_signal():
#     return latest_signal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 1. Import CORS

app = FastAPI()

# 2. Add the CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permits all origins (for local development)
    allow_credentials=True,
    allow_methods=["*"],      # Permits all methods (GET, POST, etc.)
    allow_headers=["*"],      # Permits all headers
)

latest_signal = {
    "stock": "SBIN",
    "price": 972.15,
    "signal": "WAIT",
    "rsi": 46.6,
    "ema20": 973.4,
    "ema50": 973.9,
    "target": None,
    "timeframe": "5–15 mins"
}

@app.get("/signal")
def get_signal():
    return latest_signal

# 3. Add an entry point to run with python server.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)