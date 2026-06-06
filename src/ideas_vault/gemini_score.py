"""Optional, bring-your-own-key Gemini helper that suggests pillar scores.

This module is opt-in and never imported by the rest of the CLI at startup. It
keeps the project offline-first: there is no LLM SDK dependency. The only network
call goes through :func:`_post`, a thin ``urllib`` wrapper that tests monkeypatch.

The suggestions are advisory. The framework still expects you to read the
detail files and edit the numbers yourself before committing a verdict.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from ideas_vault.scoring import MARKET_MODIFIERS, Scorecard

DEFAULT_MODEL = "gemini-2.5-flash"
_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_PILLARS = ("feasibility", "competition", "scale", "founder_fit")
_FALLBACK_SCORE = 5
_FALLBACK_MARKET = "crowded"


class GeminiError(RuntimeError):
    """Raised when a Gemini request fails or returns an unexpected payload."""


class MissingApiKeyError(GeminiError):
    """Raised when no API key is available; the CLI degrades gracefully."""


@dataclass(frozen=True)
class PillarSuggestion:
    score: int
    rationale: str


@dataclass(frozen=True)
class ScoreSuggestion:
    feasibility: PillarSuggestion
    competition: PillarSuggestion
    scale: PillarSuggestion
    founder_fit: PillarSuggestion
    market_status: str
    notes: str = ""

    def scorecard(self) -> Scorecard:
        """Build a :class:`Scorecard` from the suggested numbers."""
        return Scorecard(
            self.feasibility.score,
            self.competition.score,
            self.scale.score,
            self.founder_fit.score,
            self.market_status,
        )


_PILLAR_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "rationale": {"type": "string"},
    },
    "required": ["score", "rationale"],
}

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "feasibility": _PILLAR_SCHEMA,
        "competition": _PILLAR_SCHEMA,
        "scale": _PILLAR_SCHEMA,
        "founder_fit": _PILLAR_SCHEMA,
        "market_status": {"type": "string", "enum": list(MARKET_MODIFIERS)},
        "notes": {"type": "string"},
    },
    "required": ["feasibility", "competition", "scale", "founder_fit", "market_status"],
}


def build_prompt(description: str) -> str:
    """Return the provider-agnostic scoring prompt for one idea."""
    markets = ", ".join(MARKET_MODIFIERS)
    return (
        "You are a cold, evidence-driven evaluator of side-project ideas. "
        "Score this idea on four pillars, each an integer from 0 to 10, using these anchors: "
        "9-10 near-perfect, 7-8 strong, 5-6 average, 3-4 weak, 1-2 near-deal-breaker, 0 deal-breaker.\n\n"
        f"Idea:\n{description}\n\n"
        "Pillars:\n"
        "- feasibility: can one person ship a first useful version without a major blocker?\n"
        "- competition: is demand validated, and is there a defensible niche to enter?\n"
        "- scale: do the unit economics work as the business grows?\n"
        "- founder_fit: does it fit a solo automation-leaning builder's skills, channel, budget, and time?\n\n"
        f"Classify market_status as exactly one of: {markets}.\n"
        "Give a one-line rationale per pillar. Be conservative: when in doubt, score lower. "
        "Add a short notes field with the single biggest risk. "
        "Return only JSON matching the requested schema."
    )


def _build_payload(description: str) -> dict:
    return {
        "contents": [{"parts": [{"text": build_prompt(description)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }


def _post(url: str, payload: dict, *, timeout: float = 30.0) -> dict:
    """POST ``payload`` as JSON and return the decoded response. Patched in tests."""
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _clamp_score(value: object) -> int:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return _FALLBACK_SCORE
    return max(0, min(10, number))


def _pillar(data: dict, key: str) -> PillarSuggestion:
    block = data.get(key)
    if not isinstance(block, dict):
        block = {}
    return PillarSuggestion(
        score=_clamp_score(block.get("score")),
        rationale=str(block.get("rationale", "")).strip(),
    )


def _from_dict(data: dict) -> ScoreSuggestion:
    market = str(data.get("market_status", "")).strip().lower()
    if market not in MARKET_MODIFIERS:
        market = _FALLBACK_MARKET
    return ScoreSuggestion(
        feasibility=_pillar(data, "feasibility"),
        competition=_pillar(data, "competition"),
        scale=_pillar(data, "scale"),
        founder_fit=_pillar(data, "founder_fit"),
        market_status=market,
        notes=str(data.get("notes", "")).strip(),
    )


def _parse_response(raw: dict) -> ScoreSuggestion:
    try:
        text = raw["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError("unexpected Gemini response shape") from exc
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise GeminiError("Gemini did not return valid JSON") from exc
    if not isinstance(data, dict):
        raise GeminiError("Gemini returned JSON that is not an object")
    return _from_dict(data)


def suggest(
    description: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 30.0,
) -> ScoreSuggestion:
    """Ask Gemini for suggested pillar scores. Raises on missing key or transport error.

    The key is read from ``api_key`` or the ``GEMINI_API_KEY`` environment variable.
    The model is read from ``model`` or ``IVAULT_GEMINI_MODEL`` or :data:`DEFAULT_MODEL`.
    """
    description = (description or "").strip()
    if not description:
        msg = "idea description must not be empty"
        raise ValueError(msg)

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        msg = "set GEMINI_API_KEY to enable"
        raise MissingApiKeyError(msg)

    model = model or os.getenv("IVAULT_GEMINI_MODEL") or DEFAULT_MODEL
    url = f"{_ENDPOINT.format(model=model)}?key={key}"
    try:
        raw = _post(url, _build_payload(description), timeout=timeout)
    except urllib.error.URLError as exc:
        msg = f"Gemini request failed: {exc}"
        raise GeminiError(msg) from exc
    return _parse_response(raw)
