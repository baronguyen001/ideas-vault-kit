from __future__ import annotations

import json
import urllib.error

import pytest
from click.testing import CliRunner

from ideas_vault import gemini_score
from ideas_vault.cli import cli


def _gemini_envelope(body: dict) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}


_GOOD_BODY = {
    "feasibility": {"score": 8, "rationale": "Known APIs, scoped build."},
    "competition": {"score": 7, "rationale": "Validated market."},
    "scale": {"score": 8, "rationale": "Low COGS subscription."},
    "founder_fit": {"score": 9, "rationale": "Strong solo fit."},
    "market_status": "validated",
    "notes": "Distribution is the main risk.",
}


def test_build_prompt_includes_idea_and_markets() -> None:
    prompt = gemini_score.build_prompt("AI receipt sorter")
    assert "AI receipt sorter" in prompt
    assert "blue_ocean" in prompt
    assert "founder_fit" in prompt


def test_suggest_parses_mocked_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: _gemini_envelope(_GOOD_BODY))
    suggestion = gemini_score.suggest("An idea", api_key="test-key")

    assert suggestion.feasibility.score == 8
    assert suggestion.competition.rationale == "Validated market."
    assert suggestion.market_status == "validated"
    assert suggestion.notes == "Distribution is the main risk."
    # The suggestion converts straight into the existing scoring model.
    assert suggestion.scorecard().feasibility == 8


def test_suggest_clamps_scores_and_falls_back_on_bad_market(monkeypatch: pytest.MonkeyPatch) -> None:
    body = {
        "feasibility": {"score": 99, "rationale": "too high"},
        "competition": {"score": -4, "rationale": "too low"},
        "scale": {"score": "oops", "rationale": "not a number"},
        "founder_fit": {},
        "market_status": "totally-unknown",
    }
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: _gemini_envelope(body))
    suggestion = gemini_score.suggest("idea", api_key="k")

    assert suggestion.feasibility.score == 10
    assert suggestion.competition.score == 0
    assert suggestion.scale.score == 5
    assert suggestion.founder_fit.score == 5
    assert suggestion.market_status == "crowded"


def test_suggest_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(gemini_score.MissingApiKeyError, match="GEMINI_API_KEY"):
        gemini_score.suggest("idea")


def test_suggest_rejects_empty_description() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        gemini_score.suggest("   ", api_key="k")


def test_suggest_wraps_transport_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: object, **_k: object) -> dict:
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(gemini_score, "_post", boom)
    with pytest.raises(gemini_score.GeminiError, match="request failed"):
        gemini_score.suggest("idea", api_key="k")


def test_suggest_rejects_bad_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: {"nope": True})
    with pytest.raises(gemini_score.GeminiError, match="unexpected"):
        gemini_score.suggest("idea", api_key="k")


def test_suggest_rejects_non_json_text(monkeypatch: pytest.MonkeyPatch) -> None:
    envelope = {"candidates": [{"content": {"parts": [{"text": "not json"}]}}]}
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: envelope)
    with pytest.raises(gemini_score.GeminiError, match="valid JSON"):
        gemini_score.suggest("idea", api_key="k")


def test_cli_suggest_without_key_degrades(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "Some idea", "--suggest"])
    assert result.exit_code == 0, result.output
    assert "set GEMINI_API_KEY to enable" in result.output


def test_cli_suggest_with_key_prints_table(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: _gemini_envelope(_GOOD_BODY))
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "An idea worth scoring", "--suggest"])
    assert result.exit_code == 0, result.output
    assert "Suggested scores" in result.output
    assert "Suggested verdict: GO (34/40)" in result.output
    assert "Validated market." in result.output


def test_cli_suggest_reports_gemini_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_score, "_post", lambda *a, **k: {"bad": "shape"})
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "An idea", "--suggest"])
    assert result.exit_code != 0
