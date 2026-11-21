from __future__ import annotations

import json
from datetime import datetime, timezone

from smart_search.user_data import get_user_data_directory


SAVED_QUERIES_PATH = get_user_data_directory() / "saved_queries.json"


def list_saved_queries() -> list[dict]:
    if not SAVED_QUERIES_PATH.exists():
        return []
    with SAVED_QUERIES_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Saved queries file must contain a JSON array: {SAVED_QUERIES_PATH}")
    return data


def save_query(name: str, query_data: dict) -> dict:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Saved query name cannot be empty.")

    saved = list_saved_queries()
    entry = {
        "name": cleaned_name,
        "query": query_data,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    saved.append(entry)
    SAVED_QUERIES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SAVED_QUERIES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(saved, handle, ensure_ascii=False, indent=2)
    return entry
