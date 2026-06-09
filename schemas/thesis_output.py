from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AnomalyEvent(BaseModel):
    """Price move facts copied from the anomaly detector into the saved thesis."""

    ticker: str
    market_timestamp: str  # when the price bar occurred
    detected_at: str       # when our pipeline noticed it
    price: float
    z_score: float
    pct_change: float
    volatility: float
    direction: Literal["up", "down"]


class Classification(BaseModel):
    """Core analyst judgment: scare, fundamental change, or inconclusive noise."""

    type: Literal[
        "fundamental_shift",
        "scare_situation",
        "inconclusive_market_noise",
    ]
    subtype: Literal["simple_scare", "overcorrection"] | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str


class Analysis(BaseModel):
    """News causality assessment and likely drivers of the move."""

    likely_causes: list[str]
    news_causal_assessment: Literal["strong", "moderate", "weak", "none"]
    news_causal_explanation: str
    when_news_insufficient: str | None = None


class RecoveryView(BaseModel):
    """Directional recovery expectation — no numeric price targets in v1."""

    expected_recovery: Literal[
        "full_reversion",
        "partial_reversion",
        "unlikely_reversion",
        "unclear",
    ]
    recovery_rationale: str


class InvestmentView(BaseModel):
    """Structured bull/bear factors plus a pre-decision stance (not a trade signal)."""

    key_drivers: list[str]
    key_risks: list[str]
    recommended_stance: Literal["monitor", "investigate_further", "no_action"]
    stance_rationale: str


class ArticleUsed(BaseModel):
    """One news source cited in the thesis output."""

    title: str | None = None
    url: str | None = None
    published_date: str | None = None


class Sources(BaseModel):
    """Audit trail of news retrieved for this anomaly."""

    news_retrieved_at: str
    article_count: int
    articles_used: list[ArticleUsed]


class Metadata(BaseModel):
    """Which model/prompt produced this thesis (for reproducibility)."""

    model: str
    prompt_version: str
    processing_mode: str = "sequential_single_pass"


class ThesisAnalysis(BaseModel):
    """Fields the LLM returns — orchestrator wraps these into ThesisOutput."""

    classification: Classification
    analysis: Analysis
    recovery_view: RecoveryView
    investment_view: InvestmentView


class ThesisOutput(BaseModel):
    """Full persisted thesis document written to data/theses/*.json."""

    thesis_id: str
    version: int = 1
    status: Literal["pending_review"] = "pending_review"
    created_at: datetime
    event: AnomalyEvent
    classification: Classification
    analysis: Analysis
    recovery_view: RecoveryView
    investment_view: InvestmentView
    sources: Sources
    metadata: Metadata
