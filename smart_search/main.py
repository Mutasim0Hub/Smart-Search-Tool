from __future__ import annotations

import sys

from smart_search.ui.menu import (
    expert_query_flow,
    guided_search_flow,
    operator_catalog_menu,
    presets_menu,
    query_builder_menu,
    search_engine_manager,
    search_history_menu,
    settings_menu,
    show_main_menu,
)


BANNER = """\
    

    
███████╗███╗   ███╗ █████╗ ██████╗ ████████╗    ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗    ████████╗ ██████╗  ██████╗ ██╗
██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
███████╗██╔████╔██║███████║██████╔╝   ██║       ███████╗█████╗  ███████║██████╔╝██║     ███████║       ██║   ██║   ██║██║   ██║██║
╚════██║██║╚██╔╝██║██╔══██╗██╔══██╗   ██║       ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║       ██║   ██║   ██║██║   ██║██║
███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║       ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║       ██║   ╚██████╔╝╚██████╔╝███████╗
╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝

[---]                  Smart Search Tool                        [---]
[---]               Created by: Mutasim0Hub                     [---]
            
[---]        GitHub: https://github.com/Mutasim0Hub             [---]
            >>  Type 'help' for usage information.  <<
_______________________________________________________________________                                                                
"""


def _show_banner() -> None:
    try:
        print(BANNER)
    except UnicodeEncodeError:
        sys.stdout.reconfigure(encoding="utf-8")
        print(BANNER)


def main() -> None:
    _show_banner()
    while True:
        try:
            show_main_menu()
            choice = input("Select > ").strip()
            if choice == "0":
                print("Goodbye.")
                break
            if choice == "1":
                guided_search_flow()
            elif choice == "2":
                expert_query_flow()
            elif choice == "3":
                query_builder_menu()
            elif choice == "4":
                operator_catalog_menu()
            elif choice == "5":
                search_engine_manager()
            elif choice == "6":
                search_history_menu()
            elif choice == "7":
                presets_menu()
            elif choice == "8":
                settings_menu()
            else:
                print("[!] Invalid selection.")
        except EOFError:
            print("\nInput closed. Goodbye.")
            break


if __name__ == "__main__":
    main()
