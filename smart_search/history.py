from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from smart_search.user_data import get_user_data_directory


HISTORY_PATH = get_user_data_directory() / "history.json"


def ensure_history_file() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]", encoding="utf-8")


def load_history() -> list[dict]:
    ensure_history_file()
    try:
        with HISTORY_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as exc:
        raise ValueError(f"Search history file is invalid JSON: {HISTORY_PATH}") from exc


def save_history(history: list[dict]) -> None:
    ensure_history_file()
    with HISTORY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, ensure_ascii=False, indent=2)


def add_history_entry(query: str, provider: str, target: str = "general", scopes: list[str] | None = None) -> None:
    history = load_history()
    history.append(
        {
            "query": query,
            "provider": provider,
            "target": target,
            "scopes": scopes or [],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    save_history(history)


def list_history() -> list[dict]:
    return load_history()
