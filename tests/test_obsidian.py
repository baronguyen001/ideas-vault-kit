from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ideas_vault.cli import cli
from ideas_vault.index import collect
from ideas_vault.obsidian import MOC_NAME, export_obsidian, render_moc, render_note


def test_render_note_has_frontmatter_and_wikilinks(seeded_vault: Path) -> None:
    metas = collect(seeded_vault)
    by_market = {"crowded": metas}
    note = render_note(metas[0], by_market)

    # Dataview-compatible frontmatter block.
    assert note.startswith("---\n")
    assert "title: First Idea" in note
    assert "score: 32" in note
    assert "verdict: GO" in note
    assert "market_status: crowded" in note
    assert "flag: GO" in note
    assert "tags: [idea-vault, idea]" in note
    # Wikilink back to the MOC and across to the sibling idea sharing the market status.
    assert f"[[{MOC_NAME}]]" in note
    assert "[[002 Second Idea]]" in note


def test_render_note_without_siblings_is_explicit(tmp_path: Path, make_readme) -> None:
    make_readme(tmp_path / "001-solo", title="Solo", score=30, verdict="GO", date="2026-01-01")
    meta = collect(tmp_path)[0]
    note = render_note(meta, {"crowded": [meta]})
    assert "No sibling ideas share this market status yet." in note


def test_render_moc_ranks_by_score_with_flags(seeded_vault: Path) -> None:
    moc = render_moc(collect(seeded_vault))
    assert f"# {MOC_NAME}" in moc
    # First Idea (32) outranks Second Idea (20).
    assert moc.index("[[001 First Idea]]") < moc.index("[[002 Second Idea]]")
    # GO/KILL flag column collapses the verdict.
    assert "| GO |" in moc
    assert "| KILL |" in moc


def test_export_obsidian_writes_notes_and_moc(seeded_vault: Path) -> None:
    out = export_obsidian(seeded_vault)
    assert out == seeded_vault / "obsidian"
    moc = out / f"{MOC_NAME}.md"
    assert moc.exists()
    assert (out / "001 First Idea.md").exists()
    assert (out / "002 Second Idea.md").exists()
    # Notes cross-link each other (shared market status -> wikilink).
    first = (out / "001 First Idea.md").read_text(encoding="utf-8")
    assert "[[002 Second Idea]]" in first


def test_export_obsidian_custom_out(seeded_vault: Path, tmp_path: Path) -> None:
    target = tmp_path / "vault"
    out = export_obsidian(seeded_vault, target)
    assert out == target
    assert (target / f"{MOC_NAME}.md").exists()


def test_export_command_obsidian(seeded_vault: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    target = tmp_path / "obs"
    result = runner.invoke(
        cli,
        ["export", "--format", "obsidian", "--out", str(target), "--vault", str(seeded_vault)],
    )
    assert result.exit_code == 0, result.output
    assert (target / f"{MOC_NAME}.md").exists()
    assert str(target) in result.output


def test_export_command_obsidian_rejects_stdout(seeded_vault: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["export", "--format", "obsidian", "--output", "-", "--vault", str(seeded_vault)],
    )
    assert result.exit_code != 0
    assert "folder of notes" in result.output
