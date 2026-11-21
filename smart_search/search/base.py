from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests

from smart_search.core.models import SearchResult


def provider_request_error(provider_name: str, error: requests.RequestException) -> RuntimeError:
    response = getattr(error, "response", None)
    status_code = getattr(response, "status_code", None)
    if isinstance(error, requests.Timeout):
        message = f"{provider_name.title()} request timed out."
    elif status_code in (401, 403):
        message = f"{provider_name.title()} rejected the credentials or API permissions."
    elif status_code == 429:
        message = f"{provider_name.title()} API quota or rate limit was reached."
    elif status_code:
        message = f"{provider_name.title()} request failed with HTTP status {status_code}."
    else:
        message = f"{provider_name.title()} network request failed."
    return RuntimeError(message)


class SearchProvider(ABC):
    """Base abstraction for all search providers."""

    name: str = "provider"
    configured: bool = False
    description: str = ""

    @abstractmethod
    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Execute a real or stubbed provider search."""

    def supports_operator(self, operator_name: str) -> bool:
        return True

    def provider_status(self) -> str:
        return "Configured" if self.configured else "Not Configured"

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "configured": self.configured,
            "status": self.provider_status(),
            "description": self.description,
        }
