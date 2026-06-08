import os
import requests
from datetime import datetime


class NewsService:

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found")

    def get_news(self, anomaly, max_results=10):

        ticker = anomaly["ticker"]
        move_time = anomaly["market_timestamp"]

        payload = {
            "api_key": self.api_key,
            "query": ticker,
            "topic": "news",
            "max_results": max_results
        }

        response = requests.post(
            "https://api.tavily.com/search",
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        return {
            "ticker": ticker,
            "move_time": move_time,
            "retrieved_at": datetime.utcnow().isoformat(),
            "article_count": len(results),
            "articles": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content", ""),
                    "published_date": r.get("published_date")
                }
                for r in results
            ]
        }