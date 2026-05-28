from __future__ import annotations

import os
from importlib import resources
from pathlib import Path


def templates_dir() -> Path:
    return Path(str(resources.files("ideas_vault") / "_assets" / "templates"))


def resolve_vault(arg: str | Path | None = None) -> Path:
    candidate = Path(arg or os.getenv("IVAULT_DIR") or Path.cwd()).expanduser()
    vault = candidate.resolve()
    if not vault.exists() or not vault.is_dir():
        msg = f"vault not found: {vault}"
        raise FileNotFoundError(msg)
    return vault
