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
```

Dumps every idea's number, folder, title, score, verdict, market status, and date. Without `--output`, it writes `<vault>/ideas-vault.<format>` and prints the path. Use `--output -` to stream to stdout for piping into a spreadsheet or another tool.

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
