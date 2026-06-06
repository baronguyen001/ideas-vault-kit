# Changelog

## v0.2.0 - 2026-06-06

- Added `ivault score "idea" --suggest`: an opt-in, bring-your-own-key Gemini helper that suggests 0-10 scores plus a one-line rationale per pillar. You still edit the numbers. It degrades gracefully when `GEMINI_API_KEY` is unset and adds no LLM SDK dependency (stdlib only).
- Added `ivault export --format csv|json [--output FILE|-]`: dump every idea (scores + verdict + market status) from a vault to a file or stdout.
- Added `ivault rank`: a leaderboard of all ideas sorted by adjusted `/40` with a quick GO/KILL flag.
- Added an `ideas-vault` console-script alias for `ivault`.
- Added tests for export, rank, and a mocked Gemini suggestion path.

## v0.1.0 - 2026-05-28

- Added the 4-pillar idea scoring framework.
- Added `ivault new`, `ivault score`, `ivault index`, and `ivault list`.
- Added provider-agnostic LLM prompt mode.
- Added templates, calibration pillars, two worked examples, and package assets.
- Added CI for Python 3.11 and 3.12 on Ubuntu and Windows.

## Roadmap

- v0.2: `ivault shortlist` for quick scoring many ideas into `_shortlists/`.
- v0.2: HTML/PDF export of an idea report.
- v0.2: bundled skill manifest for use inside the future `barobao-skills` pack.
- v0.3: weighted pillars.
- v0.3: Notion or Obsidian export adapter.
