# Changelog

## v0.3.0 - 2026-06-10

- Added `ivault export --format obsidian [--out DIR]`: writes one markdown note per idea with Dataview-compatible frontmatter, `[[wikilinks]]` between ideas that share a market status, and a generated `Ideas MOC.md` ranked by adjusted `/40`. Drops straight into an Obsidian vault, no plugin required.
- Added `ivault report --html FILE [--title TEXT]`: a self-contained HTML leaderboard (score bars + GO/KILL badges, ranked highest `/40` first, clickable headers). Pure string templating — no JS dependency, no network. A good artifact for a launch post.
- Added `ivault notion-sync`: an opt-in, bring-your-own-key Notion sync that upserts each idea as a database row keyed by the idea folder name (create or update). `requests` is an optional `[notion]` extra; with no `NOTION_API_KEY` + `NOTION_DB` it prints `set NOTION_API_KEY + NOTION_DB to enable` and adds no dependency to the core install.
- Added `.env.example` documenting the optional Gemini and Notion environment variables (placeholders only).
- Added tests for Obsidian export (wikilinks + frontmatter), the HTML report (valid HTML + key fields), and a fully mocked Notion sync (no live calls in CI).

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

- `ivault shortlist` for quick scoring many ideas into `_shortlists/`.
- PDF export of an idea report (HTML report shipped in v0.3).
- Bundled skill manifest for use inside the future `barobao-skills` pack.
- Weighted pillars.
