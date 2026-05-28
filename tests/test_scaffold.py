from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ideas_vault.scaffold import IDEA_FILES, new_idea, next_number, slugify


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("AI Receipt Sorter!!", "ai-receipt-sorter"),
        ("Cà phê Đặc biệt for Busy Founders", "ca-phe-dac-biet-for-busy"),
        ("one two three four five six seven", "one-two-three-four-five-six"),
    ],
)
def test_slugify(name: str, expected: str) -> None:
    assert slugify(name) == expected


def test_slugify_caps_at_50_chars() -> None:
    assert len(slugify("supercalifragilisticexpialidocious " * 4)) <= 50


def test_next_number_empty_and_gaps(tmp_path: Path) -> None:
    assert next_number(tmp_path) == "001"
    (tmp_path / "001-first").mkdir()
    (tmp_path / "009-ninth").mkdir()
    (tmp_path / "notes").mkdir()
    assert next_number(tmp_path) == "010"


def test_new_idea_copies_files_and_fills_placeholders(tmp_path: Path) -> None:
    folder = new_idea(tmp_path, "Test Idea", on=date(2026, 5, 28))
    assert folder.name == "001-test-idea"
    for filename in IDEA_FILES:
        assert (folder / filename).exists()
    assert not (folder / "kill.md").exists()
    readme = (folder / "README.md").read_text(encoding="utf-8")
    assert "{{title}}" not in readme
    assert "{{date}}" not in readme
    assert 'title: "Test Idea"' in readme
    assert 'date: "2026-05-28"' in readme


def test_new_idea_refuses_duplicate_slug(tmp_path: Path) -> None:
    new_idea(tmp_path, "Test Idea")
    with pytest.raises(FileExistsError):
        new_idea(tmp_path, "Test Idea")
