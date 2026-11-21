from __future__ import annotations

import json
from pathlib import Path

from smart_search.user_data import get_user_data_directory


DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parent / "config" / "settings.json"
SETTINGS_PATH = get_user_data_directory() / "settings.json"


def load_settings() -> dict:
    with DEFAULT_SETTINGS_PATH.open("r", encoding="utf-8") as handle:
        defaults = json.load(handle)

    if not SETTINGS_PATH.exists():
        return defaults

    with SETTINGS_PATH.open("r", encoding="utf-8") as handle:
        saved = json.load(handle)
    if not isinstance(saved, dict):
        raise ValueError(f"Settings file must contain a JSON object: {SETTINGS_PATH}")
    return {**defaults, **saved}


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(settings, handle, ensure_ascii=False, indent=2)


def update_setting(key: str, value: object) -> dict:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
