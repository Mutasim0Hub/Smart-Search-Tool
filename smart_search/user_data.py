from __future__ import annotations

import os
from pathlib import Path


def get_user_data_directory() -> Path:
    if os.name == "nt":
        base_directory = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        data_directory = base_directory / "SmartSearchTool"
    elif os.getenv("XDG_DATA_HOME"):
        data_directory = Path(os.environ["XDG_DATA_HOME"]) / "smart-search-tool"
    else:
        data_directory = Path.home() / ".local" / "share" / "smart-search-tool"

    data_directory.mkdir(parents=True, exist_ok=True)
    return data_directory
