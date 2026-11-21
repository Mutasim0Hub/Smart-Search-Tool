from __future__ import annotations

import os
import logging
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
import requests

from smart_search.core.models import SearchResult
from smart_search.search.base import SearchProvider
from smart_search.search.providers.brave import BraveProvider
from smart_search.search.providers.google import GoogleProvider
from smart_search.settings import load_settings


load_dotenv()

PROVIDER_CLASSES: dict[str, type[SearchProvider]] = {
    "google": GoogleProvider,
    "brave": BraveProvider,
}


def list_provider_names() -> list[str]:
    return list(PROVIDER_CLASSES)


def get_default_provider() -> str:
    configured_default = os.getenv("DEFAULT_PROVIDER", "").strip()
    if configured_default:
        configured_default = configured_default.lower()
        if configured_default in PROVIDER_CLASSES:
            return configured_default
        logging.warning("Unknown DEFAULT_PROVIDER %r; checking saved settings.", configured_default)

    settings_default = load_settings().get("default_provider", "brave")
    if settings_default not in PROVIDER_CLASSES:
        logging.warning("Unknown default provider %r; using Brave.", settings_default)
        return "brave"
    return settings_default


def get_provider_statuses() -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for name, provider_cls in PROVIDER_CLASSES.items():
        provider = provider_cls()
        statuses[name] = {
            "configured": provider.configured,
            "status": provider.provider_status(),
            "description": provider.description,
        }
    return statuses


def get_provider(name: str) -> SearchProvider:
    provider_cls = PROVIDER_CLASSES.get(name.lower())
    if not provider_cls:
        raise ValueError(f"Unknown provider: {name}")
    return provider_cls()


def search_all_providers(
    query: str,
    max_results: int = 10,
    provider_names: list[str] | None = None,
    errors: dict[str, str] | None = None,
) -> dict[str, list[SearchResult]]:
    names = provider_names or list_provider_names()
    results_by_provider: dict[str, list[SearchResult]] = {}
    for name in names:
        provider = get_provider(name)
        if not provider.configured:
            results_by_provider[name] = []
            if errors is not None:
                errors[name] = "Provider is not configured."
            continue
        try:
            results_by_provider[name] = provider.search(query, max_results=max_results)
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            logging.warning("%s search failed: %s", name, exc)
            if errors is not None:
                errors[name] = str(exc)
            results_by_provider[name] = []
    return results_by_provider


def normalize_results(results: list[SearchResult], source: str) -> list[SearchResult]:
    normalized: list[SearchResult] = []
    for result in results:
        item = SearchResult(
            title=result.title or "Untitled",
            url=(result.url or "").strip(),
            snippet=result.snippet or "",
            source=source,
            metadata=dict(result.metadata),
        )
        normalized.append(item)
    return normalized


def _result_identity(result: SearchResult) -> str:
    if not result.url.strip():
        return re.sub(r"\s+", " ", result.title.strip()).casefold()

    try:
        parsed = urlsplit(result.url.strip())
        if not parsed.scheme or not parsed.netloc:
            return result.url.strip().casefold()

        hostname = parsed.hostname.lower() if parsed.hostname else ""
        port = parsed.port
        if port and not (
            (parsed.scheme.lower() == "http" and port == 80)
            or (parsed.scheme.lower() == "https" and port == 443)
        ):
            hostname = f"{hostname}:{port}"
        path = parsed.path.rstrip("/") or "/"
        return urlunsplit((parsed.scheme.lower(), hostname, path, parsed.query, ""))
    except ValueError:
        return result.url.strip().casefold()


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    deduped: list[SearchResult] = []
    seen: dict[str, SearchResult] = {}
    for result in results:
        key = _result_identity(result)
        if not key:
            deduped.append(result)
            continue
        if key not in seen:
            sources = set([result.source]) if result.source else set()
            result.metadata["sources"] = sorted(sources)
            result.source = ", ".join(sorted(sources))
            seen[key] = result
            deduped.append(result)
        else:
            existing = seen[key]
            sources = set(existing.metadata.get("sources", [existing.source]))
            if result.source:
                sources.add(result.source)
            existing.metadata["sources"] = sorted(sources)
            existing.source = ", ".join(sorted(sources))
    return deduped
