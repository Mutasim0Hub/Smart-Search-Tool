from __future__ import annotations

import re

from smart_search.core.models import SearchQuery


SUPPORTED_TARGETS = {
    "general",
    "website",
    "documents",
    "profile",
    "news",
    "academic",
    "custom",
}

SUPPORTED_SCOPES = {
    "web",
    "domain",
    "file",
    "title",
    "url",
    "text",
    "multiple",
    "custom",
}


def _is_valid_domain(value: str) -> bool:
    if not value:
        return True
    pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$"
    return bool(re.fullmatch(pattern, value))


def validate_search_query(query: SearchQuery) -> list[str]:
    errors: list[str] = []

    if not query.target:
        errors.append("Target is required.")
    elif query.target not in SUPPORTED_TARGETS:
        errors.append("Unsupported target.")

    if not query.scopes:
        errors.append("At least one search scope is required.")
    else:
        invalid_scopes = [scope for scope in query.scopes if scope not in SUPPORTED_SCOPES]
        if invalid_scopes:
            errors.append(f"Unsupported scope(s): {', '.join(invalid_scopes)}")

    if query.domain and not _is_valid_domain(query.domain):
        errors.append("Invalid domain.")

    if query.filetype:
        cleaned = query.filetype.strip().lstrip(".")
        if not re.fullmatch(r"[A-Za-z0-9]{1,16}", cleaned):
            errors.append("File type is invalid.")

    if query.url and not re.match(r"^[A-Za-z0-9._/-]+$", query.url):
        errors.append("URL value contains invalid characters.")

    if query.title and len(query.title.strip()) < 2:
        errors.append("Title value is too short.")

    for keyword in query.keywords:
        if len(keyword.strip()) == 0:
            errors.append("Keywords cannot be empty.")

    if query.exclude and any(not term.strip() for term in query.exclude):
        errors.append("Excluded terms cannot be empty.")

    return errors


def validate_query_string(query_text: str) -> list[str]:
    errors: list[str] = []
    if not query_text or not query_text.strip():
        errors.append("Query cannot be empty.")
    return errors
