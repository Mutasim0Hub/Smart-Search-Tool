from smart_search.core.query_engine import generate_query
from smart_search.ui import menu


def test_query_builder_generates_query_from_interactive_input(monkeypatch) -> None:
    responses = iter(
        [
            "documents",
            "2,3,4",
            "annual financial report",
            "example.com",
            "pdf",
            "2025",
            "",
            "",
            "draft",
            "",
            "",
        ]
    )
    captured = {}

    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))
    monkeypatch.setattr(menu, "query_preview_menu", lambda query: captured.setdefault("query", query))

    menu.query_builder_menu()

    assert generate_query(captured["query"]) == (
        'site:example.com filetype:pdf intitle:2025 "annual financial report" -draft'
    )


def test_query_builder_accepts_blank_scopes_and_optional_fields(monkeypatch) -> None:
    responses = iter(["", "", "", "", "", "", "", "", "", "", ""])
    captured = {}

    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))
    monkeypatch.setattr(menu, "query_preview_menu", lambda query: captured.setdefault("query", query))

    menu.query_builder_menu()

    assert captured["query"].scopes == ["web"]
    assert generate_query(captured["query"]) == ""
