# Scoring Model

Every idea is scored on four pillars, each from 0 to 10:

| Pillar | Core question |
|---|---|
| Feasibility & Tech | Can one person ship the first useful version without a major blocker? |
| Competition & Market | Is demand validated, and is the niche defensible enough to enter? |
| Scale & Unit Economics | Does each customer make economic sense, and can the model scale? |
| Founder-Fit | Does the idea fit your actual skills, channels, time, budget, and energy? |

## Score Anchors

| Score | Meaning |
|---|---|
| 9-10 | Extremely strong pillar, near-perfect for this idea. |
| 7-8 | Strong, with a clear advantage. |
| 5-6 | Average: not a weakness, not an advantage. |
| 3-4 | Weak, with real barriers. |
| 1-2 | Very weak, near-deal-breaker. |
| 0 | Absolute deal-breaker. |

## Verdict Thresholds

The raw total is the sum of all four pillars, out of 40. Then apply the market-status modifier.

| Adjusted score | Verdict |
|---:|---|
| 30-40 | GO |
| 15-29 | PIVOT |
| 0-14 | NO-GO |

## Market-Status Modifier

| Status | Modifier | Why |
|---|---:|---|
| blue_ocean | -2 | No competitors can mean no validated demand. |
| validated | +2 | 3-7 competitors is often the sweet spot. |
| crowded | 0 | Demand exists, but niche quality decides. |
| saturated | -3 | Many clones and price pressure. |
| dominated | -5 | One or two winners own most demand. |

The adjusted score is clamped to 0-40.

## Auto-Downgrade Rule

Any pillar <=2 caps the verdict. A single near-deal-breaker can never produce a GO.

- If adjusted score is below 15, the verdict is NO-GO.
- Otherwise, the verdict is PIVOT.

Example: `Scorecard(10, 10, 10, 2, "crowded")` has a raw and adjusted score of 32/40, but the verdict is PIVOT because founder-fit is a near-deal-breaker.

## Worked Example

Scores:

- Feasibility: 8
- Competition: 7
- Scale: 8
- Founder-Fit: 9
- Market status: `validated`

Math:

- Raw total: 8 + 7 + 8 + 9 = 32
- Modifier: `validated` = +2
- Adjusted total: 34/40
- Verdict: GO
