from smart_search.core.models import SearchQuery, SearchResult
from smart_search.core.query_engine import generate_query
from smart_search.core.validator import validate_search_query
from smart_search.search.manager import deduplicate_results, get_provider_statuses


def test_query_generation_basic() -> None:
    query = SearchQuery(
        target="documents",
        scopes=["domain", "file", "title"],
        keywords=["annual financial report"],
        domain="example.com",
        filetype="pdf",
        title="2025",
        exclude=["draft"],
    )
    result = generate_query(query)
    assert "site:example.com" in result
    assert "filetype:pdf" in result
    assert '"annual financial report"' in result
    assert "intitle:2025" in result
    assert "-draft" in result


def test_exact_phrase_and_or_and_exclusions() -> None:
    query = SearchQuery(
        target="website",
        scopes=["web"],
        keywords=["report OR annual", "financial report"],
        exclude=["draft", "old"],
    )
    result = generate_query(query)
    assert '"financial report"' in result
    assert "(report OR annual)" in result
    assert "-draft" in result
    assert "-old" in result


def test_operator_tokens() -> None:
    query = SearchQuery(
        target="general",
        scopes=["domain", "title", "url", "text"],
        domain="example.com",
        title="report",
        url="finance",
        text="annual",
    )
    result = generate_query(query)
    assert "site:example.com" in result
    assert "intitle:report" in result
    assert "inurl:finance" in result
    assert "intext:annual" in result


def test_multiple_scopes_are_handled() -> None:
    query = SearchQuery(target="documents", scopes=["domain", "file", "title"])
    result = generate_query(query)
    assert result == ""
    assert query.scopes == ["domain", "file", "title"]


def test_or_expression_is_preserved_as_an_alternative() -> None:
    query = SearchQuery(target="general", scopes=["web"], keywords=["cat OR dog"])
    assert generate_query(query) == "(cat OR dog)"


def test_invalid_input_reports_errors() -> None:
    query = SearchQuery(
        target="invalid",
        scopes=["unknown"],
        domain="bad domain",
        filetype="bad value",
    )
    errors = validate_search_query(query)
    assert errors
    assert any("Unsupported target" in error for error in errors)
    assert any("Invalid domain" in error for error in errors)
    assert any("File type is invalid" in error for error in errors)


def test_result_deduplication() -> None:
    results = [
        SearchResult(title="Report", url="https://example.com/report.pdf", snippet="Alpha", source="Google"),
        SearchResult(title="Report", url="https://example.com/report.pdf", snippet="Beta", source="Bing"),
    ]
    deduped = deduplicate_results(results)
    assert len(deduped) == 1
    assert "Google" in deduped[0].source
    assert "Bing" in deduped[0].source


def test_provider_selection_inventory() -> None:
    statuses = get_provider_statuses()
    assert set(statuses) == {"google", "brave"}
