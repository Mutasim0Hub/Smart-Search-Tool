from __future__ import annotations

import re

from smart_search.core.models import SearchQuery


def _format_keyword(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if " " in text:
        return f'"{text}"'
    return text


def generate_query(search_query: SearchQuery) -> str:
    parts: list[str] = []

    if search_query.domain:
        parts.append(f"site:{search_query.domain}")

    if search_query.filetype:
        parts.append(f"filetype:{search_query.filetype}")

    if search_query.url:
        parts.append(f"inurl:{search_query.url}")

    if search_query.title:
        parts.append(f"intitle:{search_query.title}")

    if search_query.text:
        parts.append(f"intext:{search_query.text}")

    if search_query.keywords:
        keyword_parts: list[str] = []
        for keyword in search_query.keywords:
            alternatives = [
                alternative.strip()
                for alternative in re.split(r"\s+OR\s+", keyword, flags=re.IGNORECASE)
                if alternative.strip()
            ]
            if len(alternatives) > 1:
                keyword_parts.append(f"({' OR '.join(_format_keyword(value) for value in alternatives)})")
            elif alternatives:
                keyword_parts.append(_format_keyword(alternatives[0]))
        for token in keyword_parts:
            if token and token not in parts:
                parts.append(token)

    for key, value in sorted(search_query.custom_ops.items()):
        if not value:
            continue
        parts.append(f"{key}:{value}")

    for term in search_query.exclude:
        parts.append(f"-{term}")

    if search_query.range_value:
        parts.append(f"{search_query.range_value}")

    return " ".join(part for part in parts if part)


def build_query_from_structured_data(data: dict) -> str:
    from smart_search.core.query_builder import build_search_query

    return generate_query(build_search_query(data))
