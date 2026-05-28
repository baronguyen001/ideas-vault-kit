from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    GO = "GO"
    PIVOT = "PIVOT"
    NO_GO = "NO-GO"


MARKET_MODIFIERS: dict[str, int] = {
    "blue_ocean": -2,
    "validated": 2,
    "crowded": 0,
    "saturated": -3,
    "dominated": -5,
}


@dataclass(frozen=True)
class Scorecard:
    feasibility: int
    competition: int
    scale: int
    founder_fit: int
    market_status: str | None = None

    def __post_init__(self) -> None:
        for name, value in zip(
            ("feasibility", "competition", "scale", "founder_fit"),
            self.pillars,
            strict=True,
        ):
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 10:
                msg = f"{name} must be an integer from 0 to 10"
                raise ValueError(msg)
        if self.market_status is not None and self.market_status not in MARKET_MODIFIERS:
            choices = ", ".join(MARKET_MODIFIERS)
            msg = f"market_status must be one of: {choices}"
            raise ValueError(msg)

    @property
    def pillars(self) -> tuple[int, int, int, int]:
        return (self.feasibility, self.competition, self.scale, self.founder_fit)


def raw_total(s: Scorecard) -> int:
    """Sum of the four pillars, 0..40."""
    return sum(s.pillars)


def modifier(s: Scorecard) -> int:
    """Market-status adjustment applied after the raw /40 score."""
    return MARKET_MODIFIERS.get(s.market_status, 0)


def adjusted_total(s: Scorecard) -> int:
    """Raw total plus market modifier, clamped to 0..40."""
    return max(0, min(40, raw_total(s) + modifier(s)))


def verdict(s: Scorecard) -> Verdict:
    """Return the final verdict after thresholds and the auto-downgrade rule."""
    adj = adjusted_total(s)
    if min(s.pillars) <= 2:
        return Verdict.NO_GO if adj < 15 else Verdict.PIVOT
    if adj >= 30:
        return Verdict.GO
    if adj < 15:
        return Verdict.NO_GO
    return Verdict.PIVOT
