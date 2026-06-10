from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from ideas_vault.cli import cli
from ideas_vault.index import collect
from ideas_vault.report import render_report, report


def test_render_report_is_valid_html_with_key_fields(seeded_vault: Path) -> None:
    html = render_report(collect(seeded_vault))
    assert html.startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")
    # Well-formed-ish: tags are balanced for the structural elements.
    for tag in ("html", "head", "body", "table", "tbody"):
        assert html.count(f"<{tag}") == html.count(f"</{tag}>")
    # Key fields present.
    assert "First Idea" in html
    assert "Second Idea" in html
    assert "32/40" in html
    assert 'class="badge go"' in html
    assert "GO" in html and "KILL" in html
    assert "Feasibility" in html  # legend names the four pillars


def test_render_report_orders_by_score(seeded_vault: Path) -> None:
    html = render_report(collect(seeded_vault))
    # First Idea (32) appears before Second Idea (20).
    assert html.index("First Idea") < html.index("Second Idea")


def test_render_report_custom_title_is_escaped() -> None:
    html = render_report([], title="A & B <script>")
    assert "A &amp; B &lt;script&gt;" in html
    assert "No scored ideas yet." in html


def test_report_writes_default_path(seeded_vault: Path) -> None:
    path = report(seeded_vault)
    assert path == seeded_vault / "ideas-vault.html"
    assert path.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_report_custom_output(seeded_vault: Path, tmp_path: Path) -> None:
    target = tmp_path / "board.html"
    path = report(seeded_vault, target, title="My Board")
    assert path == target
    assert "My Board" in path.read_text(encoding="utf-8")


def test_report_command_writes_html(seeded_vault: Path, tmp_path: Path) -> None:
    runner = CliRunner()
    target = tmp_path / "out.html"
    result = runner.invoke(
        cli, ["report", "--html", str(target), "--vault", str(seeded_vault)]
    )
    assert result.exit_code == 0, result.output
    assert target.exists()
    assert "<!DOCTYPE html>" in target.read_text(encoding="utf-8")


def test_report_command_missing_vault_errors() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["report", "--vault", "does-not-exist"])
    assert result.exit_code != 0
