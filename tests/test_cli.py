from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ideas_vault.cli import cli
from ideas_vault.frontmatter import parse


def test_new_index_list_happy_path(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "Test Idea", "--vault", str(tmp_path), "--date", "2026-05-28"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "001-test-idea" / "README.md").exists()

    result = runner.invoke(cli, ["index", "--vault", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "INDEX.md").exists()

    result = runner.invoke(cli, ["list", "--vault", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Test Idea" in result.output


def test_score_non_interactive_prints_go() -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "score",
            "--feasibility",
            "8",
            "--competition",
            "7",
            "--scale",
            "8",
            "--founder-fit",
            "9",
            "--market",
            "crowded",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "GO 32/40" in result.output


def test_score_write_mutates_files_and_reindexes(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "Test Idea", "--vault", str(tmp_path), "--date", "2026-05-28"])
    assert result.exit_code == 0, result.output
    folder = tmp_path / "001-test-idea"

    result = runner.invoke(
        cli,
        [
            "score",
            "--write",
            str(folder),
            "--reindex",
            "--feasibility",
            "8",
            "--competition",
            "7",
            "--scale",
            "8",
            "--founder-fit",
            "9",
            "--market",
            "validated",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "GO 34/40" in result.output
    assert "Regenerated" in result.output
    assert "**Adjusted total** | **34/40**" in (folder / "05-verdict.md").read_text(encoding="utf-8")
    meta = parse(folder / "README.md")
    assert meta is not None
    assert meta.verdict == "GO"
    assert meta.score == 34
    assert meta.market_status == "validated"
    assert "Test Idea" in (tmp_path / "INDEX.md").read_text(encoding="utf-8")


def test_bad_score_exits_nonzero() -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "score",
            "--feasibility",
            "11",
            "--competition",
            "7",
            "--scale",
            "8",
            "--founder-fit",
            "9",
            "--market",
            "crowded",
        ],
    )
    assert result.exit_code != 0
