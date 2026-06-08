print("TEST SCRIPT STARTED")
from services.anomaly_detector import (
    compute_zscore,
    compute_volatility,
    detect_anomaly
)

# --- Force anomaly case ---
prices = [100]*10 + [20]  # sharp crash

z = compute_zscore(prices)
vol = compute_volatility(prices)

open_price = prices[0]
last_price = prices[-1]

pct_change = ((last_price - open_price) / open_price) * 100

print("Prices:", prices)
print("Z-score:", z)
print("Volatility:", vol)
print("Pct change:", pct_change)

is_anomaly = detect_anomaly(z, pct_change, vol)

print("Anomaly detected:", is_anomaly)