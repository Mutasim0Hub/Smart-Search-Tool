import smart_search.history as history_store
import smart_search.saved_queries as saved_queries_store
import smart_search.settings as settings_store


def test_history_persistence_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(history_store, "HISTORY_PATH", tmp_path / "history.json")
    history_store.add_history_entry(
        "site:example.com filetype:pdf",
        "brave",
        target="documents",
        scopes=["domain", "file"],
    )
    history = history_store.list_history()
    assert any(item["query"] == "site:example.com filetype:pdf" for item in history)


def test_settings_can_be_updated_without_changing_defaults(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings_store, "SETTINGS_PATH", tmp_path / "settings.json")
    original_defaults = settings_store.DEFAULT_SETTINGS_PATH.read_text(encoding="utf-8")
    updated = settings_store.update_setting("default_provider", "brave")
    assert updated["default_provider"] == "brave"
    assert settings_store.load_settings()["default_provider"] == "brave"
    assert settings_store.DEFAULT_SETTINGS_PATH.read_text(encoding="utf-8") == original_defaults


def test_saved_query_persists_in_user_data(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(saved_queries_store, "SAVED_QUERIES_PATH", tmp_path / "saved.json")
    saved_queries_store.save_query("Research", {"target": "academic", "scopes": ["web"]})
    saved = saved_queries_store.list_saved_queries()
    assert saved[0]["name"] == "Research"
    assert saved[0]["query"]["target"] == "academic"
