import logging
import os
import warnings

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

from services.anomaly_detector import compute_zscore, detect_anomaly, compute_volatility

# Tickers the scheduler watches each run
WATCHLIST = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "^GSPC"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "market_data.csv")

# Try these Yahoo Finance query shapes if the first one returns no rows
FETCH_STRATEGIES = [
    {"period": "5d", "interval": "1h"},
    {"period": "1mo", "interval": "1h"},
    {"period": "5d", "interval": "1d"},
    {"period": "1mo", "interval": "1d"},
]


def load_history():
    """Load all previously saved market snapshots from CSV."""
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()


def append_data(df: pd.DataFrame):
    """Append this run's rows to the market data CSV (creates file/folder if needed)."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    file_exists = os.path.exists(DATA_PATH)
    df.to_csv(DATA_PATH, mode="a", header=not file_exists, index=False)


def fetch_price_history(ticker: str) -> pd.DataFrame:
    """
    Pull recent price bars for one ticker from Yahoo Finance.

    Yahoo sometimes returns empty data (network blips, rate limits, bad interval).
    We try several period/interval combinations before giving up.
    """
    # Reduce noisy "possibly delisted" messages in the terminal
    logging.getLogger("yfinance").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", category=FutureWarning)

    for kwargs in FETCH_STRATEGIES:
        try:
            hist = yf.Ticker(ticker).history(**kwargs)
            if hist is not None and not hist.empty:
                return hist
        except Exception:
            continue

    # Last resort: batch download API (different Yahoo code path)
    try:
        hist = yf.download(
            ticker,
            period="5d",
            interval="1h",
            progress=False,
            threads=False,
        )
        if hist is not None and not hist.empty:
            # download() can return multi-level columns for a single ticker
            if isinstance(hist.columns, pd.MultiIndex):
                hist = hist.droplevel(1, axis=1)
            return hist
    except Exception:
        pass

    return pd.DataFrame()


def _estimate_volatility_from_csv(df: pd.DataFrame, ticker: str, market_timestamp: str) -> float:
    """
    When rebuilding an anomaly from CSV history, volatility is not stored on each row.
    Estimate it from the last few saved prices for that ticker before the move.
    """
    ticker_rows = df[df["ticker"] == ticker].copy()
    if ticker_rows.empty:
        return 0.0

    ticker_rows = ticker_rows[ticker_rows["timestamp"] <= market_timestamp]
    prices = ticker_rows["price"].astype(float).tolist()
    if len(prices) < 2:
        return 0.0

    return round(float(compute_volatility(prices[-12:])), 2)


def get_unprocessed_anomalies_from_csv() -> list[dict]:
    """
    Find anomaly rows already saved in market_data.csv that do not yet have a thesis file.

    This catches backlog when:
    - a previous run flagged an anomaly but thesis generation never ran, or
    - live Yahoo fetch failed on a later run even though CSV still shows anomaly_flag=True.
    """
    from services.orchestrator import thesis_path

    df = load_history()
    if df.empty or "anomaly_flag" not in df.columns:
        return []

    # CSV may store True as bool or string depending on how it was written
    flagged_rows = df[
        df["anomaly_flag"].astype(str).str.lower().isin(["true", "1"])
    ].copy()

    if flagged_rows.empty:
        return []

    # Keep one row per (ticker, move time); latest CSV row wins
    flagged_rows = flagged_rows.sort_values("timestamp")
    flagged_rows = flagged_rows.drop_duplicates(subset=["ticker", "timestamp"], keep="last")

    backlog = []
    for _, row in flagged_rows.iterrows():
        ticker = row["ticker"]
        market_timestamp = row["timestamp"]

        if thesis_path(ticker, market_timestamp).exists():
            continue

        backlog.append({
            "ticker": ticker,
            "market_timestamp": market_timestamp,
            "detected_at": market_timestamp,
            "price": float(row["price"]),
            "z_score": round(float(row["z_score"]), 2),
            "pct_change": round(float(row["pct_change"]), 2),
            "volatility": _estimate_volatility_from_csv(df, ticker, market_timestamp),
            "source": "csv_backlog",
        })

    return backlog


def get_market_data_and_detect_anomalies():
    """
    Main market-data step for each scheduler/manual run:
    1. Fetch live prices for the watchlist
    2. Compute z-score / volatility / percent change
    3. Flag statistical anomalies
    4. Append this run's metrics to CSV
    """
    load_history()  # reserved for future use against prior rows

    results = []
    flagged = []

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for ticker in WATCHLIST:
        hist = fetch_price_history(ticker)

        if hist.empty:
            print(f"No price data for {ticker} — skipped (check network or Yahoo availability)")
            continue

        market_timestamp = hist.index[-1].strftime("%Y-%m-%d %H:%M:%S")

        prices = hist["Close"].astype(float).tolist()

        last_price = float(prices[-1])
        open_price = float(hist["Open"].iloc[0])

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
                "z_score": round(float(z_score), 2),
                "pct_change": round(float(pct_change), 2),
                "volatility": round(float(volatility), 2),
                "source": "live_detection",
            })

        results.append({
            "timestamp": market_timestamp,
            "ticker": ticker,
            "price": last_price,
            "pct_change": round(float(pct_change), 2),
            "z_score": round(float(z_score), 2),
            "anomaly_flag": is_anomaly,
        })

    new_df = pd.DataFrame(results)
    append_data(new_df)

    return results, flagged
