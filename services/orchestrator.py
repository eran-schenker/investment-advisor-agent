import json
import time
from datetime import datetime, timezone
from pathlib import Path

from schemas.thesis_output import (
    AnomalyEvent,
    ArticleUsed,
    Metadata,
    Sources,
    ThesisOutput,
)
from services.news_service import NewsService
from services.thesis_engine import ThesisEngine

BASE_DIR = Path(__file__).resolve().parent.parent
THESES_DIR = BASE_DIR / "data" / "theses"

# Pause between tickers to reduce Tavily / OpenAI rate-limit risk
INTER_ANOMALY_DELAY_SECONDS = 2


def make_thesis_id(ticker: str, market_timestamp: str) -> str:
    """Human-readable ID stored inside the thesis JSON."""
    return f"{ticker}_{market_timestamp}"


def make_event_filename(ticker: str, market_timestamp: str) -> str:
    """Filesystem-safe filename (colons/spaces replaced for macOS/Windows)."""
    safe_ticker = ticker.replace("^", "")
    safe_ts = market_timestamp.replace(" ", "T").replace(":", "-")
    return f"{safe_ticker}_{safe_ts}"


def thesis_path(ticker: str, market_timestamp: str) -> Path:
    """Full path where this anomaly's thesis JSON should be saved."""
    filename = make_event_filename(ticker, market_timestamp)
    return THESES_DIR / f"{filename}.json"


def enrich_anomaly(anomaly: dict) -> dict:
    """Add derived fields the LLM prompt expects (e.g. up vs down move)."""
    enriched = dict(anomaly)
    enriched["direction"] = "down" if enriched["pct_change"] < 0 else "up"
    return enriched


def build_input_bundle(anomaly: dict, news: dict) -> dict:
    """
    Combine price anomaly + news into one JSON payload for the LLM.

    This is the single context bundle for ONE ticker — never mix tickers here.
    """
    truncated_articles = [
        {
            **article,
            "content": ThesisEngine.truncate_article_content(
                article.get("content") or ""
            ),
        }
        for article in news.get("articles", [])
    ]

    return {
        "event_id": make_thesis_id(anomaly["ticker"], anomaly["market_timestamp"]),
        "anomaly": enrich_anomaly(anomaly),
        "news": {**news, "articles": truncated_articles},
        "analysis_instructions": {
            "primary_question": "fundamental_shift vs scare_situation vs inconclusive_market_noise",
            "require_causal_link": True,
            "note_on_timing": (
                "News may not be strictly time-filtered; use move_time as anchor "
                "and assess plausibility of causal connection."
            ),
        },
    }


def build_sources(news: dict) -> Sources:
    """Record which articles were available when the thesis was generated."""
    return Sources(
        news_retrieved_at=news["retrieved_at"],
        article_count=news["article_count"],
        articles_used=[
            ArticleUsed(
                title=a.get("title"),
                url=a.get("url"),
                published_date=a.get("published_date"),
            )
            for a in news.get("articles", [])
        ],
    )


def save_thesis(thesis: ThesisOutput, path: Path) -> None:
    """Write one validated thesis document to data/theses/."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(thesis.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )


def merge_anomalies(*groups: list[dict]) -> list[dict]:
    """
    Combine live detections and CSV backlog without duplicate (ticker, move time) pairs.

    Live detections win if both sources contain the same event.
    """
    merged: dict[tuple[str, str], dict] = {}

    for group in groups:
        for anomaly in group:
            key = (anomaly["ticker"], anomaly["market_timestamp"])
            merged[key] = anomaly

    return list(merged.values())


def process_anomalies(
    flagged: list[dict],
    news_service: NewsService | None = None,
    thesis_engine: ThesisEngine | None = None,
) -> list[str]:
    """
    Sequential thesis pipeline — one ticker at a time:

    anomaly → news fetch → LLM analysis → save JSON → short pause → next ticker
    """
    if not flagged:
        return []

    news_service = news_service or NewsService()
    thesis_engine = thesis_engine or ThesisEngine()

    # Process earliest market move first for deterministic runs
    ordered = sorted(
        flagged,
        key=lambda a: (a["market_timestamp"], a["ticker"]),
    )

    written_paths: list[str] = []

    for anomaly in ordered:
        ticker = anomaly["ticker"]
        market_timestamp = anomaly["market_timestamp"]
        path = thesis_path(ticker, market_timestamp)

        # V1 dedup: never regenerate the same (ticker, move time)
        if path.exists():
            print(f"Skipping {ticker} @ {market_timestamp} — thesis already exists")
            continue

        try:
            print(f"Processing {ticker} @ {market_timestamp}…")

            # Step 1: fetch news (orchestrator responsibility — not the LLM)
            news = news_service.get_news(anomaly)

            # Step 2: build one isolated input bundle for this ticker
            input_bundle = build_input_bundle(anomaly, news)

            # Step 3: LLM classifies scare vs fundamental vs inconclusive
            analysis = thesis_engine.generate(input_bundle)

            # Step 4: assemble final persisted document (IDs/timestamps set here, not by LLM)
            thesis = ThesisOutput(
                thesis_id=make_thesis_id(ticker, market_timestamp),
                created_at=datetime.now(timezone.utc),
                event=AnomalyEvent(**enrich_anomaly(anomaly)),
                classification=analysis.classification,
                analysis=analysis.analysis,
                recovery_view=analysis.recovery_view,
                investment_view=analysis.investment_view,
                sources=build_sources(news),
                metadata=Metadata(
                    model=thesis_engine.model,
                    prompt_version=thesis_engine.prompt_version,
                ),
            )

            save_thesis(thesis, path)
            written_paths.append(str(path))
            print(f"Saved thesis: {path}")

        except Exception as exc:
            # Fail one ticker, continue the rest of the batch
            print(f"Error processing {ticker} @ {market_timestamp}: {exc}")
            continue

        time.sleep(INTER_ANOMALY_DELAY_SECONDS)

    return written_paths
