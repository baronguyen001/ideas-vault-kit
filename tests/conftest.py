from __future__ import annotations

from pathlib import Path

import pytest


def write_readme(folder: Path, *, title: str, score: int | None, verdict: str, date: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    score_value = "null" if score is None else str(score)
    readme = folder / "README.md"
    readme.write_text(
        "\n".join(
            [
                "---",
                f"title: {title}",
                f"date: {date}",
                f"verdict: {verdict}",
                f"score: {score_value}",
                "market_status: crowded",
                "---",
                f"# {title}",
                "",
                "Body.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return readme


@pytest.fixture
def seeded_vault(tmp_path: Path) -> Path:
    write_readme(tmp_path / "002-second", title="Second Idea", score=20, verdict="PIVOT", date="2026-02-01")
    write_readme(tmp_path / "001-first", title="First Idea", score=32, verdict="GO", date="2026-01-01")
    (tmp_path / "003-no-frontmatter").mkdir()
    (tmp_path / "003-no-frontmatter" / "README.md").write_text("# Missing\n", encoding="utf-8")
    return tmp_path
