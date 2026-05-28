# ideas-vault-kit

> A 4-pillar method to kill 9 of every 10 side-project ideas before you write a line of code. Markdown vault + a tiny CLI + a copy-paste LLM prompt.

[![PyPI](https://img.shields.io/pypi/v/ideas-vault-kit.svg)](https://pypi.org/project/ideas-vault-kit/)
[![CI](https://github.com/barobaonguyen/ideas-vault-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/barobaonguyen/ideas-vault-kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](pyproject.toml)

![CLI score screenshot](screenshots/cli_score.png)

```bash
pip install ideas-vault-kit
```

[See a worked GO example](examples/001-postpal-crosspost/README.md)

Ideas pile up in notes apps because every idea feels exciting when it is still vague. Then one of them eats three months before the boring problems appear: distribution, pricing, compliance, churn, or founder mismatch. This kit gives you a cold rubric instead of another list.

## The 4 Pillars

| Pillar | Core question |
|---|---|
| Feasibility & Tech | Can one person ship it without a major blocker? |
| Competition & Market | Is demand validated, and can you enter with a niche? |
| Scale & Unit Economics | Does each customer make sense as the business grows? |
| Founder-Fit | Does it fit your skills, channel, budget, time, and energy? |

Score each pillar from 0 to 10. Sum to `/40`, apply the market-status modifier, then decide:

| Adjusted score | Verdict |
|---:|---|
| 30-40 | GO |
| 15-29 | PIVOT |
| 0-14 | NO-GO |

Market status nudges the score: `validated` gets `+2`, `blue_ocean` gets `-2`, `crowded` gets `0`, `saturated` gets `-3`, and `dominated` gets `-5`. There is also an auto-downgrade: any pillar `<=2` means the idea can never be GO, even if the total is high.

![Workflow diagram](screenshots/workflow_diagram.png)

## Two Ways To Run It

Manual CLI:

```bash
mkdir my-ideas
cd my-ideas
ivault new "AI receipt sorter for freelancers"

# Fill the markdown files yourself, then score it:
ivault score --write 001-ai-receipt-sorter-for-freelancers

# Or score non-interactively:
ivault score --feasibility 8 --competition 7 --scale 8 --founder-fit 9 --market validated

ivault index
ivault list --verdict GO
```

LLM prompt:

Do not want to research by hand? Paste [docs/prompt.md](docs/prompt.md) into Claude, Gemini, or GPT with your idea. It asks the model to research the market, fill the six files, score the pillars, and output an index row. The prompt is provider-agnostic and contains no SDK dependency. It works especially well with search-grounded models; for Gemini-oriented agent patterns, see [gemini-agent-toolkit](https://github.com/barobaonguyen/gemini-agent-toolkit).

## Worked Example

[PostPal](examples/001-postpal-crosspost/README.md) is a synthetic GO example: cross-post build-in-public updates from one markdown file to X, Mastodon, and LinkedIn.

| Pillar | Score /10 |
|---|---:|
| Feasibility & Tech | 8 |
| Competition & Market | 7 |
| Scale & Unit Economics | 8 |
| Founder-Fit | 7 |
| **Raw total** | **30/40** |
| **Market modifier** | **+2** |
| **Adjusted total** | **32/40** |

The contrast example is [iOS apps for local restaurants](examples/002-ios-restaurant-apps/README.md), a public viral claim that the framework kills at 14/40 because App Store policy, saturated alternatives, and sales-channel mismatch matter more than a catchy revenue screenshot.

![Example report screenshot](screenshots/example_report.png)

## Why Not a Notion Template?

This is git-tracked, so you can diff how your thinking changed. It forces a number, so vague enthusiasm has to become evidence. It has an auto-downgrade, so one fatal flaw kills the idea instead of hiding inside a high total. It works offline, has no account, calls no network, and stores nothing outside your own markdown vault.

## Customize It

Edit your founder profile once in [templates/04-founder-fit.md](templates/04-founder-fit.md). Tune thresholds in [docs/scoring.md](docs/scoring.md) if your risk tolerance differs. Translate [templates/](templates/) if you want to evaluate ideas in another language; the framework is language-agnostic.

## Bigger Toolkit

This repo is intentionally small. The LLM prompt pairs with [gemini-agent-toolkit](https://github.com/barobaonguyen/gemini-agent-toolkit), and the `ideas-vault` workflow is planned for the upcoming `barobao-skills` pack.

## Contributing

Issues and PRs are welcome for bug fixes, clearer docs, extra examples, and test coverage. Keep the project offline-first: no hosted service, no scraping dependency, no LLM SDK in the CLI.

## License

MIT.
