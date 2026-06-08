
---

# 📄 `docs/PROJECT_STATUS.md`

```markdown
# Project Status — Investment Monitoring System

## 1. Current Phase

We are in:

> Phase 0 — Functional Market Anomaly Detection System

The system is working as a deterministic pipeline with no reasoning layer yet.

---

## 2. Implemented Components

### 2.1 Market Data Pipeline

**Files:**
- services/market_data.py
- services/anomaly_detector.py
- services/pipeline.py

Capabilities:
- Fetches market data via yfinance
- Computes statistical indicators:
  - z-score
  - volatility
  - percent change
- Detects anomalies using deterministic rules
- Stores data in `data/market_data.csv`

---

### 2.2 Scheduler

**File:** scheduler.py

Capabilities:
- Runs pipeline on interval (hourly)
- Restricts execution to US market hours
- Ensures weekday-only execution

---

### 2.3 News Retrieval Service

**File:** services/news_service.py

Capabilities:
- Retrieves financial news via Tavily API
- Accepts anomaly event as input
- Returns structured article dataset
- Preserves `market_timestamp` for future causal alignment

---

## 3. Current Execution Flow

Scheduler
→ Pipeline
→ Market Data Fetch
→ Anomaly Detection
→ Flagged anomalies (in-memory only)

No downstream processing currently exists.

---

## 4. Current Directory Structure

```text
.
├── data
│   └── market_data.csv
├── main.py
├── notebook.ipynb
├── requirements.txt
├── scheduler.py
├── test_anomaly.py
├── services
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── market_data.py
│   ├── news_service.py
│   └── pipeline.py