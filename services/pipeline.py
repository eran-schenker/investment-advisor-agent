# services/pipeline.py

from services.market_data import get_market_data_and_detect_anomalies


def run_pipeline():
    results, flagged = get_market_data_and_detect_anomalies()
    return results, flagged