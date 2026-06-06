from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ideas_vault.cli import cli
from ideas_vault.index import collect, go_or_kill, rank


def test_go_or_kill_mapping() -> None:
    assert go_or_kill("GO") == "GO"
    assert go_or_kill("PIVOT") == "KILL"
    assert go_or_kill("NO-GO") == "KILL"
    assert go_or_kill("") == "-"


def test_rank_sorts_by_score_desc_then_unscored_last(tmp_path: Path) -> None:
    from tests.conftest import write_readme

    write_readme(tmp_path / "001-low", title="Low", score=18, verdict="PIVOT", date="2026-01-01")
    write_readme(tmp_path / "002-high", title="High", score=34, verdict="GO", date="2026-02-01")
    write_readme(tmp_path / "003-blank", title="Blank", score=None, verdict="", date="2026-03-01")

    ordered = rank(collect(tmp_path))
    assert [meta.title for meta in ordered] == ["High", "Low", "Blank"]


def test_rank_command_outputs_leaderboard_with_flags(seeded_vault: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["rank", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    lines = [line for line in result.output.splitlines() if line.startswith("| 1") or line.startswith("| 2")]
    assert "First Idea" in lines[0]
    assert lines[0].strip().endswith("GO |")
    assert "Second Idea" in lines[1]
    assert lines[1].strip().endswith("KILL |")
    # First Idea (32) ranks above Second Idea (20).
    assert result.output.index("First Idea") < result.output.index("Second Idea")


def test_rank_command_missing_vault_errors() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["rank", "--vault", "does-not-exist"])
    assert result.exit_code != 0
