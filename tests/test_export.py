from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from ideas_vault.export import export, rows, to_csv, to_json


def test_rows_are_ordered_and_typed(seeded_vault: Path) -> None:
    data = rows(seeded_vault)
    assert [row["folder"] for row in data] == ["001-first", "002-second"]
    assert data[0]["number"] == "001"
    assert data[0]["score"] == 32
    assert data[0]["verdict"] == "GO"
    assert data[0]["market_status"] == "crowded"


def test_to_json_round_trips(seeded_vault: Path) -> None:
    payload = json.loads(to_json(seeded_vault))
    assert [entry["title"] for entry in payload] == ["First Idea", "Second Idea"]
    assert payload[1]["score"] == 20


def test_to_csv_has_header_and_blank_for_missing_score(tmp_path: Path, make_readme) -> None:
    make_readme(tmp_path / "001-scored", title="Scored", score=30, verdict="GO", date="2026-01-01")
    make_readme(tmp_path / "002-blank", title="Blank", score=None, verdict="", date="2026-02-01")

    reader = list(csv.DictReader(io.StringIO(to_csv(tmp_path))))
    assert reader[0]["title"] == "Scored"
    assert reader[0]["score"] == "30"
    assert reader[1]["score"] == ""


def test_export_writes_default_path(seeded_vault: Path) -> None:
    path = export(seeded_vault, "json")
    assert path == seeded_vault / "ideas-vault.json"
    assert json.loads(path.read_text(encoding="utf-8"))[0]["title"] == "First Idea"


def test_export_respects_custom_output_and_format(seeded_vault: Path, tmp_path: Path) -> None:
    target = tmp_path / "out.csv"
    path = export(seeded_vault, "CSV", target)
    assert path == target
    assert path.read_text(encoding="utf-8").startswith("number,folder,title")


def test_export_rejects_unknown_format(seeded_vault: Path) -> None:
    with pytest.raises(ValueError, match="unknown format"):
        export(seeded_vault, "xml")


def test_export_command_writes_file(seeded_vault: Path) -> None:
    from click.testing import CliRunner

    from ideas_vault.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["export", "--format", "json", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    assert (seeded_vault / "ideas-vault.json").exists()


def test_export_command_to_stdout(seeded_vault: Path) -> None:
    from click.testing import CliRunner

    from ideas_vault.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["export", "--format", "csv", "--output", "-", "--vault", str(seeded_vault)])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("number,folder,title")
    assert not (seeded_vault / "ideas-vault.csv").exists()


def test_export_command_missing_vault_errors() -> None:
    from click.testing import CliRunner

    from ideas_vault.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["export", "--vault", "nope-not-here"])
    assert result.exit_code != 0
