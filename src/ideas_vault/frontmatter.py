from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.DOTALL)


@dataclass
class IdeaMeta:
    title: str
    date: str
    verdict: str
    score: int | None
    market_status: str
    folder: str = ""


def _coerce_str(value: Any) -> str:
    return "" if value is None else str(value)


def parse(path: Path) -> IdeaMeta | None:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return None
    data = yaml.safe_load(match.group(1)) or {}
    score = data.get("score")
    return IdeaMeta(
        title=_coerce_str(data.get("title")),
        date=_coerce_str(data.get("date")),
        verdict=_coerce_str(data.get("verdict")),
        score=int(score) if score not in (None, "") else None,
        market_status=_coerce_str(data.get("market_status")),
        folder=path.parent.name,
    )


def dump(meta: IdeaMeta) -> str:
    data = {
        "title": meta.title,
        "date": meta.date,
        "verdict": meta.verdict,
        "score": meta.score,
        "market_status": meta.market_status,
    }
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{body}\n---\n"


def update_readme(path: Path, meta: IdeaMeta) -> None:
    text = path.read_text(encoding="utf-8")
    block = dump(meta)
    if _FRONTMATTER_RE.match(text):
        updated = _FRONTMATTER_RE.sub(block, text, count=1)
    else:
        updated = f"{block}\n{text}"
    path.write_text(updated, encoding="utf-8", newline="\n")
