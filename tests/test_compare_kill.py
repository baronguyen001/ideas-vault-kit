from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ideas_vault.cli import cli
from ideas_vault.index import (
    KILL_THRESHOLD,
    collect,
    kill_list,
    render_comparison,
    render_kill_list,
    select,
)


def _vault(tmp_path: Path, make_readme) -> Path:
    make_readme(tmp_path / "001-strong", title="Strong", score=34, verdict="GO", date="2026-01-01")
    make_readme(tmp_path / "002-mid", title="Mid", score=22, verdict="PIVOT", date="2026-02-01")
    make_readme(tmp_path / "003-weak", title="Weak", score=9, verdict="NO-GO", date="2026-03-01")
    make_readme(tmp_path / "004-blank", title="Blank", score=None, verdict="", date="2026-04-01")
    return tmp_path


def test_select_by_number_padded_or_plain(tmp_path: Path, make_readme) -> None:
    metas = collect(_vault(tmp_path, make_readme))
    chosen = select(metas, ["1", "003"])
    assert [m.title for m in chosen] == ["Strong", "Weak"]
    # unknown numbers are skipped, order preserved
    assert select(metas, ["999", "2"])[0].title == "Mid"


def test_kill_list_filters_and_sorts(tmp_path: Path, make_readme) -> None:
    metas = collect(_vault(tmp_path, make_readme))
    killed = kill_list(metas)  # default threshold 15
    assert [m.title for m in killed] == ["Weak"]  # only score 9 < 15; blank excluded
    # raise threshold to include Mid (22)
    killed25 = kill_list(metas, threshold=25)
    assert [m.title for m in killed25] == ["Weak", "Mid"]  # worst first
    assert KILL_THRESHOLD == 15


def test_render_comparison_is_side_by_side(tmp_path: Path, make_readme) -> None:
    metas = collect(_vault(tmp_path, make_readme))
    out = render_comparison(select(metas, ["1", "2"]))
    assert "| Attribute | #001 | #002 |" in out
    assert "| Score /40 | 34 | 22 |" in out
    assert "| GO/KILL | GO | KILL |" in out


def test_render_comparison_empty() -> None:
    assert "No matching ideas" in render_comparison([])


def test_render_kill_list_markdown(tmp_path: Path, make_readme) -> None:
    metas = collect(_vault(tmp_path, make_readme))
    out = render_kill_list(metas)
    assert out.startswith("# Kill list")
    assert "Weak" in out
    assert "Strong" not in out


def test_render_kill_list_none(tmp_path: Path, make_readme) -> None:
    make_readme(tmp_path / "001-ok", title="OK", score=30, verdict="GO", date="2026-01-01")
    out = render_kill_list(collect(tmp_path))
    assert "none below threshold" in out


def test_cli_compare(tmp_path: Path, make_readme) -> None:
    vault = _vault(tmp_path, make_readme)
    result = CliRunner().invoke(cli, ["compare", "1", "3", "--vault", str(vault)])
    assert result.exit_code == 0, result.output
    assert "#001" in result.output and "#003" in result.output


def test_cli_compare_no_match(tmp_path: Path, make_readme) -> None:
    vault = _vault(tmp_path, make_readme)
    result = CliRunner().invoke(cli, ["compare", "999", "--vault", str(vault)])
    assert result.exit_code != 0
    assert "no ideas matched" in result.output


def test_cli_kill_list_to_file(tmp_path: Path, make_readme) -> None:
    vault = _vault(tmp_path, make_readme)
    out_file = tmp_path / "kill.md"
    result = CliRunner().invoke(
        cli, ["kill-list", "--threshold", "25", "--out", str(out_file), "--vault", str(vault)]
    )
    assert result.exit_code == 0, result.output
    text = out_file.read_text(encoding="utf-8")
    assert "Weak" in text and "Mid" in text


def test_cli_kill_list_stdout(tmp_path: Path, make_readme) -> None:
    vault = _vault(tmp_path, make_readme)
    result = CliRunner().invoke(cli, ["kill-list", "--vault", str(vault)])
    assert result.exit_code == 0, result.output
    assert "# Kill list" in result.output
