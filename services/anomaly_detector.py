import numpy as np


def compute_zscore(prices):
    if len(prices) < 5:
        return 0.0
    std = np.std(prices)
    if std == 0:
        return 0.0
    return (prices[-1] - np.mean(prices)) / std


def compute_volatility(prices):
    returns = np.diff(prices) / prices[:-1]
    return np.std(returns) * 100 if len(returns) > 1 else 0.0


def detect_anomaly(z_score, pct_change, volatility):
    return (
        z_score < -2
        and abs(pct_change) > (2 * volatility)
    )