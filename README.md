
```markdown
# Investment Advisor Agent

A local Python pipeline that monitors a stock watchlist, detects statistical price anomalies, fetches related news, and generates structured investment-thesis JSON for human review.

**Not financial advice.** This project does not execute trades and is not intended for autonomous investment decisions.

## What it does

```
Yahoo Finance → anomaly detection → Tavily news → OpenAI thesis → JSON on disk
```

On each run the system:

1. Fetches prices for a fixed watchlist (AAPL, TSLA, MSFT, GOOGL, NVDA, AMZN, ^GSPC)
2. Flags unusual moves (z-score + volatility rules)
3. For each new anomaly: pulls financial news and generates a structured thesis
4. Saves outputs locally under `data/`

Theses are written with `status: pending_review` — nothing is acted on automatically.

## Quick start

**Requirements:** Python 3.10+, OpenAI API key, Tavily API key

```bash
git clone https://github.com/YOUR_USER/investment-advisor-agent.git
cd investment-advisor-agent

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

## Usage

### One-off run (manual + backlog)

Processes live anomalies and any flagged CSV rows that never got a thesis:

```bash
python main.py
```

### Scheduled runs (market hours)

Runs hourly, Mon–Fri, 9:00–16:00 US/Eastern. Keep the terminal open:

```bash
python scheduler.py
```

You should see `Starting scheduler...`, then hourly logs like `Running anomaly job at ...` or `Outside market hours — skipping run`.

## Outputs

| Path | Contents |
|------|----------|
| `data/market_data.csv` | Price snapshots and anomaly flags (gitignored) |
| `data/theses/{TICKER}_{timestamp}.json` | Structured thesis per event (gitignored) |

Example thesis fields: event stats, classification (`scare_situation`, etc.), likely causes, recovery view, recommended stance, source articles.

## Project layout

```
services/
  market_data.py      # fetch prices, detect anomalies, CSV persistence
  orchestrator.py     # news + thesis pipeline per anomaly
  thesis_engine.py    # LLM thesis generation
  news_service.py     # Tavily integration
scheduler.py          # hourly market-hours job
main.py               # manual run with CSV backlog
schemas/              # Pydantic models for thesis JSON
prompts/              # LLM prompt templates
docs/                 # architecture & workflow details
```

## Current status

**Working:** anomaly detection, news retrieval, thesis generation, scheduler, CSV backlog recovery.

**Planned:** human review UI, holding tracking, thesis re-evaluation over time.

See [docs/workflow_walkthrough.md](docs/workflow_walkthrough.md) for a step-by-step walkthrough.

## Design principles

- Local execution only
- Sequential processing (one ticker at a time)
- Deterministic orchestration — no multi-agent framework
- Human approval before any investment action

## License

MIT — see [LICENSE](LICENSE).
```

---
