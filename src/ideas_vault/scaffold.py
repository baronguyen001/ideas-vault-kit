from __future__ import annotations

import re
import shutil
import unicodedata
from datetime import date
from pathlib import Path

from ideas_vault.paths import templates_dir

IDEA_FILES = (
    "README.md",
    "01-feasibility.md",
    "02-competition.md",
    "03-scale-economics.md",
    "04-founder-fit.md",
    "05-verdict.md",
)


def slugify(name: str) -> str:
    """ASCII kebab-case, capped at 6 words and 50 characters."""
    normalized = unicodedata.normalize("NFKD", name.replace("đ", "d").replace("Đ", "D"))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[a-zA-Z0-9]+", ascii_name.lower())
    slug = "-".join(words[:6])[:50].strip("-")
    return re.sub(r"-{2,}", "-", slug) or "idea"


def next_number(vault: Path) -> str:
    numbers = []
    for child in vault.iterdir():
        if child.is_dir() and (match := re.match(r"^(\d{3})-", child.name)):
            numbers.append(int(match.group(1)))
    return f"{(max(numbers) + 1) if numbers else 1:03d}"


def new_idea(vault: Path, name: str, *, on: date | None = None) -> Path:
    vault = vault.resolve()
    if not vault.exists() or not vault.is_dir():
        msg = f"vault not found: {vault}"
        raise FileNotFoundError(msg)

    slug = slugify(name)
    duplicate = next(vault.glob(f"???-{slug}"), None)
    if duplicate is not None and duplicate.is_dir():
        msg = f"idea slug already exists: {slug}"
        raise FileExistsError(msg)

    folder = vault / f"{next_number(vault)}-{slug}"
    folder.mkdir(parents=False)
    created_on = (on or date.today()).isoformat()

    for filename in IDEA_FILES:
        src = templates_dir() / filename
        dst = folder / filename
        shutil.copyfile(src, dst)
        text = dst.read_text(encoding="utf-8")
        text = text.replace("{{title}}", name).replace("{{date}}", created_on)
        dst.write_text(text, encoding="utf-8", newline="\n")

    return folder
