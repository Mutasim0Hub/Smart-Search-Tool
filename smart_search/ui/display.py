from __future__ import annotations

from typing import Iterable

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover
    Console = None
    Panel = None
    Table = None


console = Console() if Console is not None else None


def print_header(title: str) -> None:
    if console is not None:
        console.print(Panel.fit(title, style="bold cyan"))
    else:
        print(f"\n=== {title} ===\n")


def print_menu(title: str, options: Iterable[tuple[str, str]]) -> None:
    if console is not None:
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Action")
        for key, label in options:
            table.add_row(key, label)
        console.print(Panel.fit(title, style="bold yellow"))
        console.print(table)
    else:
        print(f"\n{title}\n")
        for key, label in options:
            print(f"[{key}] {label}")
        print()


def print_error(message: str) -> None:
    if console is not None:
        console.print(f"[bold red][!] {message}[/bold red]")
    else:
        print(f"[!] {message}")


def print_success(message: str) -> None:
    if console is not None:
        console.print(f"[bold green]{message}[/bold green]")
    else:
        print(message)


def print_query_preview(query: str) -> None:
    print_header("QUERY PREVIEW")
    print(query)
    print()


def print_results(results: list, title: str = "RESULTS") -> None:
    if console is not None:
        console.print(Panel.fit(title, style="bold magenta"))
        if not results:
            console.print("No results returned.")
            return
        for index, result in enumerate(results, 1):
            console.print(f"[{index:02}] {result.title}", markup=False)
            console.print(f"Source: {result.source}", markup=False)
            console.print(f"URL: {result.url}", markup=False)
            console.print(f"Snippet: {result.snippet}", markup=False)
            console.print()
    else:
        print(f"\n{title}\n")
        if not results:
            print("No results returned.")
            return
        for index, result in enumerate(results, 1):
            print(f"[{index:02}] {result.title}")
            print(f"Source: {result.source}")
            print(f"URL: {result.url}")
            print(f"Snippet: {result.snippet}")
            print()
