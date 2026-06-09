import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from schemas.thesis_output import ThesisAnalysis

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "thesis_generation.txt"
PROMPT_VERSION = "thesis_generation_v1"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Keep prompts small so we do not overflow the model context window
ARTICLE_CONTENT_MAX_CHARS = 500


class ThesisEngine:
    """
    The reasoning layer (v1): one LLM call per anomaly.

    It does NOT fetch news itself — the orchestrator passes in price stats + articles.
    """

    def __init__(self, model: str | None = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        self.client = OpenAI(api_key=api_key)
        self.model = model or DEFAULT_MODEL
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Read analyst instructions from the file-driven prompt template."""
        if not PROMPT_PATH.exists():
            raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")
        return PROMPT_PATH.read_text(encoding="utf-8")

    def generate(self, input_bundle: dict) -> ThesisAnalysis:
        """
        Send one anomaly context bundle to the LLM and return validated analysis JSON.

        Uses OpenAI structured parsing so the response must match ThesisAnalysis.
        """
        user_message = json.dumps(input_bundle, indent=2)

        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": user_message},
            ],
            response_format=ThesisAnalysis,
        )

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("LLM returned no parseable thesis analysis")

        return parsed

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    @staticmethod
    def truncate_article_content(content: str, max_chars: int = ARTICLE_CONTENT_MAX_CHARS) -> str:
        """Shorten long article bodies before sending them to the LLM."""
        if len(content) <= max_chars:
            return content
        return content[:max_chars].rstrip() + "…"
