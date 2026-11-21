from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from smart_search.core.models import SearchResult
from smart_search.search.providers.google import GoogleProvider


def test_google_provider_search_uses_api_when_configured() -> None:
    provider = GoogleProvider()
    provider.configured = True

    mock_response = Mock()
    mock_response.json.return_value = {
        "items": [
            {
                "title": "Annual Report",
                "link": "https://example.com/report.pdf",
                "snippet": "Financial report for 2025",
                "displayLink": "example.com",
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch("smart_search.search.providers.google.requests.get", return_value=mock_response):
        results = provider.search("site:example.com filetype:pdf", max_results=1)

    assert len(results) == 1
    assert results[0].title == "Annual Report"
    assert results[0].url == "https://example.com/report.pdf"
    assert results[0].source == "google"


def test_google_provider_rejects_missing_configuration() -> None:
    provider = GoogleProvider()
    provider.configured = False

    try:
        provider.search("site:example.com", max_results=2)
        assert False, "Expected RuntimeError for unconfigured provider"
    except RuntimeError as exc:
        assert "GOOGLE_API_KEY" in str(exc)


def test_google_provider_sanitizes_errors_that_may_contain_api_key() -> None:
    provider = GoogleProvider()
    provider.configured = True
    response = Mock()
    response.status_code = 403
    error = requests.HTTPError(
        "request failed: https://google.example/search?key=do-not-print",
        response=response,
    )
    response.raise_for_status.side_effect = error

    with patch("smart_search.search.providers.google.requests.get", return_value=response):
        with pytest.raises(RuntimeError) as raised:
            provider.search("test")

    assert "do-not-print" not in str(raised.value)
    assert "credentials or API permissions" in str(raised.value)
