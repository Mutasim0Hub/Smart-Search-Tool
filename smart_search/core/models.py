from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchQuery:
    target: str = "general"
    scopes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    domain: str = ""
    filetype: str = ""
    title: str = ""
    url: str = ""
    text: str = ""
    exclude: list[str] = field(default_factory=list)
    range_value: str = ""
    custom_ops: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "scopes": self.scopes,
            "keywords": self.keywords,
            "domain": self.domain,
            "filetype": self.filetype,
            "title": self.title,
            "url": self.url,
            "text": self.text,
            "exclude": self.exclude,
            "range": self.range_value,
            "custom_ops": self.custom_ops,
        }


@dataclass
class SearchResult:
    title: str = ""
    url: str = ""
    snippet: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class ProviderInfo:
    name: str
    configured: bool = False
    status: str = "Not Configured"
    description: str = ""
