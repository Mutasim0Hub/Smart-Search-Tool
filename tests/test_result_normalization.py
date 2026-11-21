from smart_search.core.models import SearchResult
from smart_search.search.manager import deduplicate_results, normalize_results


def test_normalize_results_assigns_source() -> None:
    raw = [
        SearchResult(title="Alpha", url="https://example.com/a", snippet="summary", source="google"),
        SearchResult(title="Beta", url="https://example.com/b", snippet="detail", source="bing"),
    ]
    result = normalize_results(raw, "google")
    assert len(result) == 2
    assert result[0].source == "google"
    assert result[0].title == "Alpha"


def test_deduplicate_results_merges_sources() -> None:
    results = [
        SearchResult(title="Alpha", url="https://example.com/a", snippet="one", source="Google"),
        SearchResult(title="Alpha", url="https://example.com/a", snippet="two", source="Bing"),
    ]
    deduped = deduplicate_results(results)
    assert len(deduped) == 1
    assert "Google" in deduped[0].source
    assert "Bing" in deduped[0].source


def test_deduplicate_results_ignores_url_fragment_and_trailing_slash() -> None:
    results = [
        SearchResult(title="Alpha", url="HTTPS://Example.com/report/#section", source="Google"),
        SearchResult(title="Alpha", url="https://example.com/report", source="Brave"),
    ]
    assert len(deduplicate_results(results)) == 1
