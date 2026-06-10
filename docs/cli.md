# CLI Reference

The CLI entry point is `ivault`. The package also installs `ideas-vault` as an identical alias, so `ivault rank` and `ideas-vault rank` are the same command.

## Vault Resolution

Every command uses this order:

1. `--vault PATH`
2. `IVAULT_DIR`
3. Current working directory

The vault must be an existing folder.

## `ivault new`

```bash
ivault new "AI receipt sorter for freelancers" --vault my-ideas --date 2026-05-28
```

Creates `NNN-ai-receipt-sorter-for-freelancers/`, copies the six template files, fills `{{title}}` and `{{date}}`, and refuses duplicate slugs.

## `ivault score`

Interactive:

```bash
ivault score
```

Non-interactive:

```bash
ivault score --feasibility 8 --competition 7 --scale 8 --founder-fit 9 --market validated
```

This prints:

- raw total
- market modifier
- adjusted total
- verdict

With `--write FOLDER`, it also updates:

- `FOLDER/05-verdict.md`
- `FOLDER/README.md` frontmatter

Use `--reindex` to regenerate `INDEX.md` immediately.

### AI suggestion (optional)

```bash
export GEMINI_API_KEY=...
ivault score "AI receipt sorter for freelancers" --suggest
ivault score "..." --suggest --model gemini-2.5-pro
```

`--suggest` is an opt-in, bring-your-own-key helper. It asks Gemini for a 0-10 score and a one-line rationale per pillar plus a market-status guess, prints them as a table with the resulting verdict, and shows the exact `score --write` command to commit. It never writes files itself; you still edit the numbers.

The model is taken from `--model`, then `IVAULT_GEMINI_MODEL`, then the default `gemini-2.5-flash`. With no key set, the command prints `set GEMINI_API_KEY to enable` and exits cleanly. No LLM SDK is added; the call uses the standard library only.

## `ivault index`

```bash
ivault index --vault my-ideas
```

Scans `NNN-*/README.md`, reads YAML frontmatter, and rewrites `INDEX.md`. Running it twice is byte-identical.

## `ivault list`

```bash
ivault list --vault my-ideas
ivault list --verdict GO
ivault list --min-score 30
```

Prints a table with number, title, score, verdict, and date.

## `ivault rank`

```bash
ivault rank --vault my-ideas
```

Prints a leaderboard of every idea, sorted by adjusted `/40` (highest first; unscored ideas sink to the bottom). The `Flag` column collapses the verdict to a quick `GO` / `KILL` decision while the full verdict stays in its own column.

## `ivault export`

```bash
ivault export --format json --vault my-ideas        # writes my-ideas/ideas-vault.json
ivault export --format csv --output report.csv      # writes report.csv
ivault export --format csv --output -                # streams CSV to stdout
ivault export --format obsidian --out my-ideas/obsidian   # writes a folder of notes
```

For `csv` and `json`, dumps every idea's number, folder, title, score, verdict, market status, and date. Without `--output`, it writes `<vault>/ideas-vault.<format>` and prints the path. Use `--output -` to stream to stdout for piping into a spreadsheet or another tool.

For `obsidian`, writes a folder of markdown notes (default `<vault>/obsidian`, or set `--out`): one note per idea with Dataview-compatible frontmatter and `[[wikilinks]]` to ideas that share a market status, plus a generated `Ideas MOC.md` ranked by adjusted `/40`. `--output -` is rejected because the export is a folder, not a single stream.

## `ivault report`

```bash
ivault report --html board.html --vault my-ideas
ivault report --html board.html --title "My Shortlist"
```

Writes a self-contained HTML leaderboard (default `<vault>/ideas-vault.html`): every idea as a score bar with a GO/KILL badge, ranked highest `/40` first, with clickable column headers. Pure string templating — no JS dependency and no network call.

## `ivault notion-sync`

```bash
pip install "ideas-vault-kit[notion]"
export NOTION_API_KEY=...
export NOTION_DB=...
ivault notion-sync --vault my-ideas
```

Opt-in, bring-your-own-key. Upserts each idea into a Notion database as a row (score, verdict, market status, GO/KILL flag), keyed by the idea folder name so re-running updates rows in place. The key is read from `NOTION_API_KEY` and the database id from `NOTION_DB`. With either unset, it prints `set NOTION_API_KEY + NOTION_DB to enable` and exits cleanly; without the `requests` extra it prints an install hint. The target database needs a title property `Name` plus `Idea Key`, `Number`, `Verdict`, `Flag`, `Market Status`, `Date`, and `Score`.

## Frontmatter Schema

```yaml
---
title: AI receipt sorter for freelancers
date: 2026-05-28
verdict: PIVOT
score: 26
market_status: crowded
---
```

Unscored ideas use `verdict: ""`, `score: null`, and `market_status: ""`.
