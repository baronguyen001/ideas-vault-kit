from __future__ import annotations

import pytest

from ideas_vault.scoring import (
    MARKET_MODIFIERS,
    Scorecard,
    Verdict,
    adjusted_total,
    modifier,
    raw_total,
    verdict,
)


def test_scorecard_totals_and_modifier() -> None:
    scorecard = Scorecard(8, 7, 8, 9, "validated")
    assert raw_total(scorecard) == 32
    assert modifier(scorecard) == MARKET_MODIFIERS["validated"]
    assert adjusted_total(scorecard) == 34


def test_adjusted_total_clamps_to_bounds() -> None:
    assert adjusted_total(Scorecard(10, 10, 10, 10, "validated")) == 40
    assert adjusted_total(Scorecard(0, 0, 0, 0, "dominated")) == 0


@pytest.mark.parametrize(
    ("scorecard", "expected"),
    [
        (Scorecard(8, 7, 8, 9, "crowded"), Verdict.GO),
        (Scorecard(4, 4, 4, 4, None), Verdict.PIVOT),
        (Scorecard(3, 3, 3, 3, "blue_ocean"), Verdict.NO_GO),
    ],
)
def test_verdict_thresholds(scorecard: Scorecard, expected: Verdict) -> None:
    assert verdict(scorecard) is expected


def test_auto_downgrade_never_go() -> None:
    scorecard = Scorecard(10, 10, 10, 2, "crowded")
    assert adjusted_total(scorecard) == 32
    assert verdict(scorecard) is Verdict.PIVOT


def test_auto_downgrade_can_no_go() -> None:
    assert verdict(Scorecard(2, 4, 4, 4, "crowded")) is Verdict.NO_GO


@pytest.mark.parametrize(
    "kwargs",
    [
        {"feasibility": -1, "competition": 1, "scale": 1, "founder_fit": 1},
        {"feasibility": 11, "competition": 1, "scale": 1, "founder_fit": 1},
        {"feasibility": True, "competition": 1, "scale": 1, "founder_fit": 1},
    ],
)
def test_rejects_bad_scores(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        Scorecard(**kwargs)


def test_rejects_unknown_market_status() -> None:
    with pytest.raises(ValueError):
        Scorecard(1, 1, 1, 1, "unknown")
