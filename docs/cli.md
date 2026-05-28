# CLI Reference

The CLI entry point is `ivault`.

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
