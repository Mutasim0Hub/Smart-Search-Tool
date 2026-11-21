from __future__ import annotations

import os

import requests

from smart_search.core.models import SearchResult
from smart_search.search.base import SearchProvider, provider_request_error


class GoogleProvider(SearchProvider):
    name = "google"
    description = "Google Custom Search API"

    def __init__(self) -> None:
        self.configured = bool(
            os.getenv("GOOGLE_API_KEY", "").strip()
            and os.getenv("GOOGLE_CX_ID", "").strip()
        )

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        if not self.configured:
            raise RuntimeError("Google is not configured. Set GOOGLE_API_KEY and GOOGLE_CX_ID.")
        if not 1 <= max_results <= 10:
            raise ValueError("Google Custom Search supports 1 to 10 results per request.")
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        params = {
            "key": os.getenv("GOOGLE_API_KEY"),
            "cx": os.getenv("GOOGLE_CX_ID"),
            "q": query,
            "num": min(max_results, 10),
        }
        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise provider_request_error(self.name, exc) from None
        if not isinstance(payload, dict):
            raise ValueError("Google returned an unexpected response format.")

        results: list[SearchResult] = []
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise ValueError("Google returned an invalid results list.")
        for item in items[:max_results]:
            if not isinstance(item, dict):
                continue
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=self.name,
                    metadata={"displayLink": item.get("displayLink", "")},
                )
            )
        return results
