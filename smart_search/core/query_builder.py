from __future__ import annotations

from typing import Any

from smart_search.core.models import SearchQuery


def build_search_query(data: dict[str, Any]) -> SearchQuery:
    query = SearchQuery()
    query.target = str(data.get("target") or "general")
    query.scopes = [str(item).strip() for item in data.get("scopes", []) if str(item).strip()]
    query.keywords = [str(item).strip() for item in data.get("keywords", []) if str(item).strip()]
    query.domain = str(data.get("domain") or "").strip()
    query.filetype = str(data.get("filetype") or "").strip()
    query.title = str(data.get("title") or "").strip()
    query.url = str(data.get("url") or "").strip()
    query.text = str(data.get("text") or "").strip()
    query.exclude = [str(item).strip() for item in data.get("exclude", []) if str(item).strip()]
    query.range_value = str(data.get("range") or "").strip()
    query.custom_ops = {
        str(key): str(value)
        for key, value in (data.get("custom_ops") or {}).items()
        if str(key).strip() and str(value).strip()
    }
    return query
