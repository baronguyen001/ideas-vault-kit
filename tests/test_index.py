from __future__ import annotations

from pathlib import Path

from ideas_vault.index import collect, regenerate, render_index


def test_collect_reads_sorted_metas_and_skips_missing_frontmatter(seeded_vault: Path) -> None:
    metas = collect(seeded_vault)
    assert [meta.folder for meta in metas] == ["001-first", "002-second"]
    assert [meta.title for meta in metas] == ["First Idea", "Second Idea"]


def test_render_index_table_sorted(seeded_vault: Path) -> None:
    rendered = render_index(collect(seeded_vault))
    assert "| # | Title | Score /40 | Verdict | Date | Folder |" in rendered
    assert rendered.index("First Idea") < rendered.index("Second Idea")
    assert "[001-first](001-first/README.md)" in rendered


def test_regenerate_is_idempotent(seeded_vault: Path) -> None:
    path = regenerate(seeded_vault)
    first = path.read_bytes()
    regenerate(seeded_vault)
    assert path.read_bytes() == first
