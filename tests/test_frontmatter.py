from __future__ import annotations

from pathlib import Path

from ideas_vault.frontmatter import IdeaMeta, dump, parse, update_readme


def test_parse_round_trips_valid_block(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    meta = IdeaMeta("AI receipt sorter", "2026-05-28", "PIVOT", 26, "crowded", "")
    path.write_text(f"{dump(meta)}\n# Body\n", encoding="utf-8")

    parsed = parse(path)

    assert parsed == IdeaMeta("AI receipt sorter", "2026-05-28", "PIVOT", 26, "crowded", tmp_path.name)


def test_parse_returns_none_without_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("# No metadata\n", encoding="utf-8")
    assert parse(path) is None


def test_update_readme_replaces_only_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text(
        "---\ntitle: Old\ndate: 2026-01-01\nverdict: \"\"\nscore: null\nmarket_status: \"\"\n---\n"
        "# Heading\n\nBody stays.\n",
        encoding="utf-8",
    )
    update_readme(path, IdeaMeta("New", "2026-05-28", "GO", 32, "validated", "001-new"))

    text = path.read_text(encoding="utf-8")
    assert "title: New" in text
    assert "# Heading\n\nBody stays.\n" in text


def test_update_readme_prepends_when_missing(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("# Heading\n", encoding="utf-8")
    update_readme(path, IdeaMeta("New", "2026-05-28", "", None, "", ""))
    assert path.read_text(encoding="utf-8").startswith("---\ntitle: New\n")
