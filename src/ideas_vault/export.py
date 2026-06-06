"""Dump every scored idea in a vault to CSV or JSON. Built on :mod:`ideas_vault.index`."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Callable
from pathlib import Path

from ideas_vault.index import _idea_number, collect

FIELDS = ("number", "folder", "title", "score", "verdict", "market_status", "date")


def rows(vault: Path) -> list[dict[str, object]]:
    """Return one plain dict per idea, ordered by idea number."""
    out: list[dict[str, object]] = []
    for meta in collect(vault):
        out.append(
            {
                "number": _idea_number(meta.folder),
                "folder": meta.folder,
                "title": meta.title,
                "score": meta.score,
                "verdict": meta.verdict,
                "market_status": meta.market_status,
                "date": meta.date,
            }
        )
    return out


def to_json(vault: Path) -> str:
    return json.dumps(rows(vault), indent=2, ensure_ascii=False) + "\n"


def to_csv(vault: Path) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(FIELDS), lineterminator="\n")
    writer.writeheader()
    for row in rows(vault):
        record = dict(row)
        if record["score"] is None:
            record["score"] = ""
        writer.writerow(record)
    return buffer.getvalue()


RENDERERS: dict[str, Callable[[Path], str]] = {"json": to_json, "csv": to_csv}


def export(vault: Path, fmt: str, output: str | Path | None = None) -> Path:
    """Render the vault to ``fmt`` and write it to ``output`` (or ``<vault>/ideas-vault.<fmt>``)."""
    fmt = fmt.lower()
    renderer = RENDERERS.get(fmt)
    if renderer is None:
        choices = ", ".join(sorted(RENDERERS))
        msg = f"unknown format: {fmt} (choose from {choices})"
        raise ValueError(msg)
    path = Path(output) if output else vault / f"ideas-vault.{fmt}"
    path.write_text(renderer(vault), encoding="utf-8", newline="\n")
    return path
