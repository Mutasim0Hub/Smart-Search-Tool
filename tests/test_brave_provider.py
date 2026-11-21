from __future__ import annotations

from unittest.mock import Mock, patch

from smart_search.search.providers.brave import BraveProvider


def test_brave_provider_search_uses_api_when_configured() -> None:
    provider = BraveProvider()
    provider.configured = True

    mock_response = Mock()
    mock_response.json.return_value = {
        "web": {
            "results": [
                {
                    "title": "Brave Result",
                    "url": "https://example.com/brave-result",
                    "description": "Brave summary",
                }
            ]
        }
    }
    mock_response.raise_for_status.return_value = None

    with patch("smart_search.search.providers.brave.requests.get", return_value=mock_response):
        results = provider.search("site:example.com", max_results=1)

    assert len(results) == 1
    assert results[0].title == "Brave Result"
    assert results[0].url == "https://example.com/brave-result"
    assert results[0].source == "brave"
