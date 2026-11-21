from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from smart_search.core.models import SearchQuery, SearchResult
from smart_search.core.operators import get_operator_catalog  # type: ignore
from smart_search.core.query_builder import build_search_query
from smart_search.core.query_engine import generate_query
from smart_search.core.validator import validate_search_query
from smart_search.history import add_history_entry, list_history
from smart_search.saved_queries import list_saved_queries, save_query
from smart_search.search.manager import (
    deduplicate_results,
    get_default_provider,
    get_provider,
    get_provider_statuses,
    normalize_results,
    search_all_providers,
)
from smart_search.settings import load_settings, update_setting
from smart_search.ui.display import print_results


BASE_DIR = Path(__file__).resolve().parents[1]


def safe_input(prompt_text: str) -> str:
    return input(prompt_text)


def prompt_choice(prompt_text: str, valid: list[str]) -> str:
    while True:
        value = safe_input(prompt_text).strip()
        if value in valid:
            return value
        if not value:
            return ""
        print("Invalid selection. Try again.")


def prompt_text(prompt_text: str, default: str = "") -> str:
    answer = safe_input(prompt_text).strip()
    if answer:
        return answer
    return default


def load_presets() -> list[dict]:
    path = BASE_DIR / "data" / "presets.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def execute_search(query_text: str, provider_name: str, target: str, scopes: list[str]) -> None:
    settings = load_settings()
    result_limit = os.getenv("RESULTS_PER_PAGE", str(settings.get("results_per_page", 10)))
    try:
        max_results = int(result_limit)
    except ValueError:
        print("[!] RESULTS_PER_PAGE must be an integer between 1 and 10.")
        return
    if not isinstance(max_results, int) or not 1 <= max_results <= 10:
        print("[!] Results per page must be between 1 and 10 in Settings.")
        return

    if provider_name == "all":
        errors: dict[str, str] = {}
        results_by_provider = search_all_providers(
            query_text,
            max_results=max_results,
            errors=errors,
        )
        combined: list[SearchResult] = []
        for name, results in results_by_provider.items():
            print(f"{name.title()}: {len(results)} results")
            combined.extend(normalize_results(results, name))
        for name, error in errors.items():
            print(f"[!] {name.title()}: {error}")
        if errors and len(errors) == len(results_by_provider):
            print("[!] No configured provider completed the search.")
            return
        combined_results = deduplicate_results(combined)
        if settings.get("history_enabled", True):
            add_history_entry(query_text, "all", target, scopes)
        print_results(combined_results, title="COMBINED RESULTS")
        print(f"Unique results: {len(combined_results)}")
        return

    try:
        provider = get_provider(provider_name)
        if not provider.configured:
            print(f"[!] {provider.name.title()} is not configured. Check the provider setup in README.md.")
            return
        results = provider.search(query_text, max_results=max_results)
    except (RuntimeError, ValueError, requests.RequestException) as exc:
        print(f"[!] Search failed: {exc}")
        return

    normalized = normalize_results(results, provider.name)
    if settings.get("history_enabled", True):
        add_history_entry(query_text, provider.name, target, scopes)
    print_results(normalized, title=f"{provider.name.upper()} RESULTS")


def _edit_query_field(query: SearchQuery) -> bool:
    field = safe_input(
        "Edit field (keywords/domain/filetype/title/url/text/exclude): "
    ).strip().lower()
    if field == "keywords":
        query.keywords = [item.strip() for item in safe_input("Keywords, comma-separated: ").split(",") if item.strip()]
    elif field == "domain":
        query.domain = safe_input("Domain: ").strip()
    elif field == "filetype":
        query.filetype = safe_input("File type: ").strip()
    elif field == "title":
        query.title = safe_input("Title contains: ").strip()
    elif field == "url":
        query.url = safe_input("URL contains: ").strip()
    elif field == "text":
        query.text = safe_input("Text contains: ").strip()
    elif field == "exclude":
        query.exclude = [item.strip() for item in safe_input("Exclude terms, comma-separated: ").split(",") if item.strip()]
    else:
        print("[!] Unknown field.")
        return False
    return True


def query_preview_menu(query: SearchQuery) -> None:
    while True:
        final_query = generate_query(query)
        print("\nQUERY PREVIEW")
        print(f"Target: {query.target}")
        print(f"Scopes: {' + '.join(query.scopes)}")
        print(f"Generated query: {final_query or '(empty query)'}")
        print("\n[1] Search")
        print("[2] Edit")
        print("[3] Add Operator")
        print("[4] Save")
        print("[5] Back")
        choice = safe_input("Select > ").strip()
        if choice == "1":
            if not final_query:
                print("[!] Enter at least one search term or operator first.")
                continue
            errors = validate_search_query(query)
            if errors:
                print("Please correct these query issues before searching:")
                for error in errors:
                    print(f" - {error}")
                continue
            provider_name = choose_provider_name()
            if provider_name:
                execute_search(final_query, provider_name, query.target, query.scopes)
            return
        if choice == "2":
            if _edit_query_field(query):
                errors = validate_search_query(query)
                if errors:
                    print("Validation warnings:")
                    for error in errors:
                        print(f" - {error}")
            continue
        if choice == "3":
            key = safe_input("Operator name (for example: site or intitle): ").strip().rstrip(":")
            value = safe_input("Operator value: ").strip()
            if key and value:
                query.custom_ops[key] = value
            else:
                print("[!] Operator name and value are required.")
            continue
        if choice == "4":
            name = safe_input("Name for this saved query: ").strip()
            try:
                save_query(name, query.to_dict())
                print("[+] Query saved.")
            except ValueError as exc:
                print(f"[!] {exc}")
            continue
        if choice == "5":
            return
        print("[!] Invalid selection.")


def show_main_menu() -> None:
    print("\nSMART SEARCH TOOL")
    print("v0.1")
    print("\n[1] Guided Search")
    print("[2] Expert Query")
    print("[3] Query Builder")
    print("[4] Search Operators")
    print("[5] Search Engines")
    print("[6] Search History")
    print("[7] Presets")
    print("[8] Settings")
    print("\n[0] Exit")


def guided_search_flow() -> None:
    targets = {
        "1": "general",
        "2": "website",
        "3": "documents",
        "4": "profile",
        "5": "news",
        "6": "academic",
        "7": "custom",
    }
    print("\nTarget:")
    for key, label in targets.items():
        print(f"[{key}] {label.title()}")
    while True:
        target_key = prompt_choice("Select > ", list(targets))
        if target_key:
            break
        print("[!] Please choose a valid target.")
    query = SearchQuery(target=targets[target_key])

    scopes = {
        "1": "web",
        "2": "domain",
        "3": "file",
        "4": "title",
        "5": "url",
        "6": "text",
        "7": "multiple",
    }
    print("\nScopes:")
    for key, label in scopes.items():
        print(f"[{key}] {label.title()}")
    selected = []
    while True:
        choice = safe_input("Select scope (blank to finish) > ").strip()
        if not choice:
            break
        if choice in scopes:
            selected.append(scopes[choice])
        else:
            print("Invalid scope.")
    if not selected:
        selected = ["web"]
    query.scopes = selected

    print("\nKeywords:")
    query.keywords = [item.strip() for item in prompt_text("Keywords: ", "").split(",") if item.strip()]
    query.domain = prompt_text("Domain: ", "")
    query.filetype = prompt_text("File type: ", "")
    query.title = prompt_text("Title: ", "")
    query.url = prompt_text("URL contains: ", "")
    query.text = prompt_text("Text contains: ", "")
    query.exclude = [item.strip() for item in prompt_text("Exclude: ", "").split(",") if item.strip()]

    errors = validate_search_query(query)
    if errors:
        print("Validation errors: ")
        for error in errors:
            print(f" - {error}")
        return

    query_preview_menu(query)


def expert_query_flow() -> None:
    query_text = safe_input("Enter expert query: ").strip()
    if not query_text:
        print("Query cannot be empty.")
        return
    print(f"Query ready: {query_text}")
    provider_name = choose_provider_name()
    if provider_name:
        execute_search(query_text, provider_name, target="general", scopes=["expert"])


def choose_provider_name() -> str:
    statuses = get_provider_statuses()
    print("\nSearch Provider:")
    provider_names = list(statuses)
    for index, name in enumerate(provider_names, start=1):
        label = statuses[name]["status"]
        print(f"[{index}] {name.title()} - Status: {label}")
    print("[5] All Search Engines")

    while True:
        choice = safe_input("Select > ").strip()
        if choice == "5":
            return "all"
        if not choice:
            return ""
        if choice.isdigit() and 1 <= int(choice) <= len(provider_names):
            return provider_names[int(choice) - 1]
        print("[!] Invalid provider selection.")


def query_builder_menu(initial_data: dict | None = None) -> None:
    print("\nQUERY BUILDER")
    print("Enter values below. Leave blank to skip fields.")

    initial_data = initial_data or {}
    data: dict[str, object] = {
        "target": safe_input(f"Target [{initial_data.get('target', 'documents')}]: ").strip()
        or initial_data.get("target", "documents"),
        "scopes": list(initial_data.get("scopes", [])),
        "keywords": list(initial_data.get("keywords", [])),
        "domain": initial_data.get("domain", ""),
        "filetype": initial_data.get("filetype", ""),
        "title": initial_data.get("title", ""),
        "url": initial_data.get("url", ""),
        "text": initial_data.get("text", ""),
        "exclude": list(initial_data.get("exclude", [])),
        "range": initial_data.get("range", ""),
        "custom_ops": dict(initial_data.get("custom_ops", {})),
    }

    print("\nScopes (enter numbers separated by commas, e.g. 2,3,4):")
    print("1=web  2=domain  3=file  4=title  5=url  6=text  7=multiple")
    current_scopes = ", ".join(str(scope) for scope in data["scopes"])
    scope_input = safe_input(f"Scopes [{current_scopes}]: ").strip()
    if scope_input:
        scope_map = {
            "1": "web",
            "2": "domain",
            "3": "file",
            "4": "title",
            "5": "url",
            "6": "text",
            "7": "multiple",
        }
        data["scopes"] = [scope_map[item.strip()] for item in scope_input.split(",") if item.strip() in scope_map]
    if not data["scopes"]:
        data["scopes"] = ["web"]

    keywords_raw = safe_input(f"Keywords (comma-separated) [{', '.join(data['keywords'])}]: ").strip()
    if keywords_raw:
        data["keywords"] = [item.strip() for item in keywords_raw.split(",") if item.strip()]

    for field, label in (
        ("domain", "Domain"),
        ("filetype", "File type"),
        ("title", "Title contains"),
        ("url", "URL contains"),
        ("text", "Text contains"),
    ):
        current_value = str(data[field])
        data[field] = safe_input(f"{label} [{current_value}]: ").strip() or current_value

    exclude_raw = safe_input(f"Exclude terms (comma-separated) [{', '.join(data['exclude'])}]: ").strip()
    if exclude_raw:
        data["exclude"] = [item.strip() for item in exclude_raw.split(",") if item.strip()]

    current_range = str(data["range"])
    data["range"] = safe_input(f"Range (for example 2023..2025) [{current_range}]: ").strip() or current_range

    additional = safe_input("Additional operators (key:value, blank to skip): ").strip()
    if additional:
        custom_ops: dict[str, str] = {}
        for part in additional.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                custom_ops[key.strip()] = value.strip()
        data["custom_ops"] = custom_ops

    query = build_search_query(data)
    errors = validate_search_query(query)
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f" - {error}")
        return

    query_preview_menu(query)


def operator_catalog_menu() -> None:
    catalog = get_operator_catalog()
    categories = sorted({item["category"] for item in catalog.values()})
    print("\nOperator categories:")
    for category in categories:
        print(f"- {category.title()}")
    for name, item in sorted(catalog.items()):
        print(f"\n{name}")
        print(f"Syntax: {item.get('syntax')}")
        print(f"Description: {item.get('description')}")
        print(f"Status: {item.get('status')}")


def search_engine_manager() -> None:
    statuses = get_provider_statuses()
    print("\nSEARCH ENGINE MANAGER")
    for name, info in statuses.items():
        print(f"{name.title()} - Status: {info['status']} - {info['description']}")
    print("\nDefault provider:", get_default_provider())
    print("\n[1] Configure Engine")
    print("[2] Set Default")
    print("[3] Test Connection")
    print("[4] Back")

    while True:
        choice = safe_input("Select > ").strip()
        if choice == "4":
            return
        if choice == "1":
            print("Add provider credentials to the local .env file; never commit that file.")
            print("Brave: BRAVE_API_KEY")
            print("Google (existing API customers only): GOOGLE_API_KEY and GOOGLE_CX_ID")
            return
        if choice == "2":
            provider = safe_input("Provider name: ").strip().lower()
            if provider in statuses:
                update_setting("default_provider", provider)
                print(f"Default provider saved as: {provider}")
                if os.getenv("DEFAULT_PROVIDER"):
                    print("[!] DEFAULT_PROVIDER in .env takes precedence over the saved setting.")
                return
            print("[!] Unknown provider.")
            continue
        if choice == "3":
            provider_name = choose_provider_name()
            if provider_name:
                execute_search("test", provider_name, "general", ["web"])
            return
        print("[!] Invalid selection.")


def search_history_menu() -> None:
    history = list_history()
    print("\nSEARCH HISTORY")
    if not history:
        print("No search history yet.")
        return
    for index, item in enumerate(history, 1):
        print(f"[{index}] {item.get('query', '')} | {item.get('provider', 'unknown')} | {item.get('timestamp', '')}")
    selected = safe_input("Enter an entry number to search again, or press Enter to return: ").strip()
    if selected.isdigit() and 1 <= int(selected) <= len(history):
        entry = history[int(selected) - 1]
        provider_name = choose_provider_name()
        if provider_name:
            execute_search(
                entry.get("query", ""),
                provider_name,
                entry.get("target", "general"),
                entry.get("scopes", []),
            )


def presets_menu() -> None:
    presets = load_presets()
    print("\nPRESETS")
    for index, preset in enumerate(presets, 1):
        print(f"[{index}] {preset['name']}")
    saved_queries = list_saved_queries()
    saved_start = len(presets) + 1
    for offset, entry in enumerate(saved_queries):
        print(f"[{saved_start + offset}] Saved: {entry.get('name', 'Unnamed')}")
    print("[0] Back")

    while True:
        selected = safe_input("Select a preset/query number > ").strip()
        if selected == "0" or not selected:
            return
        if not selected.isdigit():
            print("[!] Invalid selection.")
            continue
        index = int(selected) - 1
        if 0 <= index < len(presets):
            query_data = presets[index]
            print(f"Loaded preset: {query_data['name']}")
            query_builder_menu(query_data)
            return
        saved_index = index - len(presets)
        if 0 <= saved_index < len(saved_queries):
            query_data = saved_queries[saved_index].get("query", {})
            query_builder_menu(query_data)
            return
        print("[!] Invalid preset/query number.")


def settings_menu() -> None:
    settings = load_settings()
    print("\nSETTINGS")
    for key, value in settings.items():
        print(f"{key}: {value}")
    print("\n[1] Update default provider")
    print("[2] Update results per page")
    print("[3] Back")

    while True:
        choice = safe_input("Select > ").strip()
        if choice == "3":
            return
        if choice == "1":
            value = safe_input("Provider name: ").strip().lower()
            if value not in get_provider_statuses():
                print("[!] Choose an available provider: " + ", ".join(get_provider_statuses()))
                continue
            updated = update_setting("default_provider", value)
            print(f"Default provider updated to: {updated['default_provider']}")
            return
        if choice == "2":
            value = safe_input("Results per page: ").strip()
            if value.isdigit() and 1 <= int(value) <= 10:
                updated = update_setting("results_per_page", int(value))
                print(f"Results per page updated to: {updated['results_per_page']}")
                if os.getenv("RESULTS_PER_PAGE"):
                    print("[!] RESULTS_PER_PAGE in .env takes precedence over the saved setting.")
                return
            print("[!] Enter a number between 1 and 10.")

        print("[!] Invalid selection.")
