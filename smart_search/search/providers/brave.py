from __future__ import annotations

import os

import requests

from smart_search.core.models import SearchResult
from smart_search.search.base import SearchProvider, provider_request_error


class BraveProvider(SearchProvider):
    name = "brave"
    description = "Brave Search API"

    def __init__(self) -> None:
        self.configured = bool(os.getenv("BRAVE_API_KEY", "").strip())

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        if not self.configured:
            raise RuntimeError("Brave is not configured. Set BRAVE_API_KEY.")
        if not 1 <= max_results <= 10:
            raise ValueError("Brave provider requests in this app are limited to 1 to 10 results.")
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        headers = {"Accept": "application/json", "X-Subscription-Token": os.getenv("BRAVE_API_KEY", "")}
        params = {"q": query, "count": min(max_results, 10)}
        try:
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise provider_request_error(self.name, exc) from None
        if not isinstance(payload, dict):
            raise ValueError("Brave returned an unexpected response format.")

        results: list[SearchResult] = []
        web_results = payload.get("web", {}).get("results", [])
        if not isinstance(web_results, list):
            raise ValueError("Brave returned an invalid results list.")
        for item in web_results[:max_results]:
            if not isinstance(item, dict):
                continue
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    source=self.name,
                    metadata={"profile": item.get("profile", "")},
                )
            )
        return results
