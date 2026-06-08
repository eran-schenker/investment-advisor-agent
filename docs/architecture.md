# Investment Monitoring & Thesis Evolution System

## 1. System Overview

This is a local Python system that detects market anomalies and evolves toward a stateful investment reasoning engine.

The system is not primarily an anomaly detector.

Its core purpose is:

> Track market events and compare new evidence against an original investment thesis over time.

---

## 2. Core Design Principle

The system is built around a deterministic event → reasoning → decision pipeline:

Market Data
↓
Anomaly Detection
↓
News Retrieval
↓
Thesis Generation (future)
↓
Human Review (future)
↓
Holding Creation (future)
↓
Ongoing Monitoring (future)
↓
Thesis Re-evaluation vs Original Assumptions

---

## 3. Hard Constraints

These constraints define system boundaries:

- Local execution only
- Sequential processing (one ticker at a time)
- No distributed systems
- No microservices
- No multi-agent frameworks (LangGraph explicitly avoided)
- Deterministic orchestration preferred
- Human approval required before any “holding” is created
- No autonomous trading decisions

---

## 4. Current System Components

### 4.1 Market Data + Anomaly Detection

**File:** `services/market_data.py`

Responsibilities:
- Fetch price data via yfinance
- Compute:
  - percent change
  - rolling z-score
  - volatility
- Detect anomalies using deterministic thresholds
- Persist market data to CSV (`data/market_data.csv`)

Outputs:
- `results` → all ticker metrics
- `flagged` → anomaly events (in-memory only)

---

### 4.2 Anomaly Detection Logic

**File:** `services/anomaly_detector.py`

Core logic:
- z-score threshold: `z < -2`
- volatility-adjusted movement condition

Pure deterministic computation layer.

---

### 4.3 Pipeline Layer

**File:** `services/pipeline.py`

Thin orchestration wrapper:

```python
run_pipeline()

4.4 News Retrieval Service

File: services/news_service.py

Purpose:
Retrieve contextual financial news for anomaly events.

Input:

{
    "ticker": "...",
    "market_timestamp": "..."
}

Output:

{
    "ticker": "...",
    "move_time": "...",
    "retrieved_at": "...",
    "article_count": N,
    "articles": [...]
}

Key design decisions:

move_time is preserved for causal alignment
Retrieval is relevance-based (not strictly time-filtered)
Used as input for future thesis generation
4.5 Scheduler

File: scheduler.py

Responsibilities:

Runs pipeline on interval
Enforces market hours (US/Eastern)
Ensures execution only during trading days

Flow:

Scheduler
→ Pipeline
→ Market Data Fetch
→ Anomaly Detection
→ Flagged anomalies (currently not persisted or processed)

5. Data Layer
Market Data Storage

File: data/market_data.csv

Stores:

historical price snapshots
computed indicators
anomaly flags

No structured event store yet for anomalies or theses.

6. Current System Behavior

At runtime:

Scheduler triggers pipeline hourly
Market data is fetched
Metrics are computed
Anomalies are flagged
Results are printed/logged
Flagged anomalies are NOT yet acted upon
7. What Is NOT Implemented Yet
Monitoring orchestrator
Thesis generation engine
Human approval workflow
Holding system
Thesis persistence layer
Thesis versioning / evolution system
Event-driven anomaly pipeline
8. Forward Architecture Direction
8.1 Monitoring Orchestrator (Next Step)

Triggered when anomalies occur.

Responsibilities:

call news_service
call thesis engine (future)
persist outputs
8.2 Thesis Engine (Core Intelligence Layer)

Will:

classify Scare vs Fundamental
generate structured reasoning
assign confidence
extract key drivers and risks
8.3 Human-in-the-Loop System

No automatic trading decisions.

Flow:

Anomaly → Thesis → Review → Approval → Holding

8.4 Holding System (Future)

State model:

Active Holding
Exited

No partial exits.

9. Key Architectural Insight

The system value is NOT in:

anomaly detection
news retrieval
summarization

see original chatGPT converstaion: https://chatgpt.com/c/6a172056-2784-83ea-b21a-2c76dc7b39e3
