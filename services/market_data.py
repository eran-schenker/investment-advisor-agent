import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from services.anomaly_detector import compute_zscore, detect_anomaly, compute_volatility

WATCHLIST = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "^GSPC"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "market_data.csv")


def load_history():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()


def append_data(df: pd.DataFrame):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)  # ← add this

    file_exists = os.path.exists(DATA_PATH)
    df.to_csv(DATA_PATH, mode="a", header=not file_exists, index=False)



def get_market_data_and_detect_anomalies():
    df_history = load_history()

    results = []
    flagged = []

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

    for ticker in WATCHLIST:
        hist = yf.Ticker(ticker).history(period="5d", interval="1h")

        if hist.empty:
            continue

        market_timestamp = hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")

        prices = hist["Close"].astype(float).tolist()

        last_price = prices[-1]
        open_price = hist["Open"].iloc[0]

        pct_change = ((last_price - open_price) / open_price) * 100

        z_score = compute_zscore(prices)
        volatility = compute_volatility(prices)

        is_anomaly = detect_anomaly(z_score, pct_change, volatility)

        if is_anomaly:
            flagged.append({
                "ticker": ticker,
                "market_timestamp": market_timestamp,
                "detected_at": run_timestamp,
                "price": last_price,
                "z_score": round(z_score, 2),
                "pct_change": round(pct_change, 2),
                "volatility": round(volatility, 2),
            })


        results.append({
            "timestamp": market_timestamp,
            "ticker": ticker,
            "price": last_price,
            "pct_change": round(pct_change, 2),
            "z_score": round(z_score, 2),
            "anomaly_flag": is_anomaly
        })
        

    new_df = pd.DataFrame(results)
    append_data(new_df)

    return results, flagged