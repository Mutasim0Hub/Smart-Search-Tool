from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "operators.json"


def load_operator_catalog(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    target = Path(path) if path is not None else DATA_FILE
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return {item["name"]: item for item in data}


OPERATOR_CATALOG = load_operator_catalog()


def get_operator_catalog() -> dict[str, dict[str, Any]]:
    return OPERATOR_CATALOG


def get_operator(name: str) -> dict[str, Any] | None:
    return OPERATOR_CATALOG.get(name)


def get_operators_by_category(category: str) -> list[dict[str, Any]]:
    return [item for item in OPERATOR_CATALOG.values() if item.get("category") == category]
