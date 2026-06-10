from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import click

from ideas_vault import __version__
from ideas_vault import index as index_mod
from ideas_vault.export import RENDERERS as EXPORT_RENDERERS
from ideas_vault.export import export as export_vault
from ideas_vault.frontmatter import IdeaMeta, parse, update_readme
from ideas_vault.paths import resolve_vault
from ideas_vault.scaffold import new_idea as scaffold_new_idea
from ideas_vault.scoring import (
    MARKET_MODIFIERS,
    Scorecard,
    adjusted_total,
    modifier,
    raw_total,
    verdict,
)

if TYPE_CHECKING:
    from ideas_vault.gemini_score import ScoreSuggestion


def _color_enabled() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _signed(value: int) -> str:
    return f"{value:+d}"


def _print_scoreboard(scorecard: Scorecard) -> None:
    final = verdict(scorecard)
    color = {"GO": "green", "PIVOT": "yellow", "NO-GO": "red"}[final.value]
    click.echo("| Metric | Value |")
    click.echo("|---|---:|")
    click.echo(f"| Raw total | {raw_total(scorecard)}/40 |")
    click.echo(f"| Market modifier | {_signed(modifier(scorecard))} |")
    click.echo(f"| Adjusted total | {adjusted_total(scorecard)}/40 |")
    click.echo("| Verdict | ", nl=False)
    click.secho(final.value, fg=color, color=_color_enabled(), nl=False)
    click.echo(" |")
    click.echo(f"{final.value} {adjusted_total(scorecard)}/40")


def _score_section(scorecard: Scorecard) -> str:
    final = verdict(scorecard)
    return "\n".join(
        [
            "## Final scoreboard",
            "",
            "| Pillar | Score /10 |",
            "|---|---:|",
            f"| 1. Feasibility & Tech | {scorecard.feasibility} |",
            f"| 2. Competition & Market | {scorecard.competition} |",
            f"| 3. Scale & Unit Economics | {scorecard.scale} |",
            f"| 4. Founder-Fit | {scorecard.founder_fit} |",
            f"| **Raw total** | **{raw_total(scorecard)}/40** |",
            f"| **Market modifier** | **{_signed(modifier(scorecard))}** |",
            f"| **Adjusted total** | **{adjusted_total(scorecard)}/40** |",
            "",
            "---",
            "",
            f"## Verdict: **{final.value}**",
            "",
        ]
    )


def _replace_verdict_file(folder: Path, scorecard: Scorecard) -> None:
    path = folder / "05-verdict.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    replacement = _score_section(scorecard)
    pattern = re.compile(r"## Final scoreboard\n.*?(?=\n## Reasoning|\Z)", re.DOTALL)
    if pattern.search(text):
        text = pattern.sub(replacement.rstrip(), text, count=1)
    else:
        text = f"{replacement}\n## Reasoning\n\n{text}"
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def _title_from_readme(readme: Path) -> str:
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return readme.parent.name


def _write_score(folder: Path, scorecard: Scorecard) -> None:
    if not folder.exists() or not folder.is_dir():
        msg = f"idea folder not found: {folder}"
        raise click.ClickException(msg)
    readme = folder / "README.md"
    if not readme.exists():
        msg = f"README.md not found in {folder}"
        raise click.ClickException(msg)

    _replace_verdict_file(folder, scorecard)
    meta = parse(readme) or IdeaMeta(
        title=_title_from_readme(readme),
        date=date.today().isoformat(),
        verdict="",
        score=None,
        market_status="",
        folder=folder.name,
    )
    meta.verdict = verdict(scorecard).value
    meta.score = adjusted_total(scorecard)
    meta.market_status = scorecard.market_status or ""
    update_readme(readme, meta)


def _print_suggestion(suggestion: ScoreSuggestion) -> None:
    scorecard = suggestion.scorecard()
    final = verdict(scorecard)
    click.echo("Suggested scores (advisory — read the detail files and edit before you commit):")
    click.echo("")
    click.echo("| Pillar | Suggested /10 | Rationale |")
    click.echo("|---|---:|---|")
    click.echo(f"| Feasibility | {suggestion.feasibility.score} | {suggestion.feasibility.rationale} |")
    click.echo(f"| Competition | {suggestion.competition.score} | {suggestion.competition.rationale} |")
    click.echo(f"| Scale | {suggestion.scale.score} | {suggestion.scale.rationale} |")
    click.echo(f"| Founder-fit | {suggestion.founder_fit.score} | {suggestion.founder_fit.rationale} |")
    click.echo(
        f"| Market status | {suggestion.market_status} | "
        f"{_signed(MARKET_MODIFIERS[suggestion.market_status])} modifier |"
    )
    if suggestion.notes:
        click.echo(f"\nBiggest risk: {suggestion.notes}")
    click.echo(f"\nSuggested verdict: {final.value} ({adjusted_total(scorecard)}/40)")
    click.echo(
        "\nReview, then commit your own numbers:\n"
        "  ivault score --write <folder> --reindex "
        f"--feasibility {suggestion.feasibility.score} --competition {suggestion.competition.score} "
        f"--scale {suggestion.scale.score} --founder-fit {suggestion.founder_fit.score} "
        f"--market {suggestion.market_status}"
    )


def _run_suggest(idea: str | None, model: str | None) -> None:
    from ideas_vault import gemini_score

    description = idea or click.prompt("Idea to score")
    try:
        suggestion = gemini_score.suggest(description, model=model)
    except gemini_score.MissingApiKeyError:
        click.echo("set GEMINI_API_KEY to enable")
        return
    except gemini_score.GeminiError as exc:
        raise click.ClickException(str(exc)) from exc
    _print_suggestion(suggestion)


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        msg = "date must use YYYY-MM-DD"
        raise click.BadParameter(msg) from exc


@click.group()
@click.version_option(version=__version__, prog_name="ivault")
def cli() -> None:
    """Markdown idea vault CLI."""


@cli.command("new")
@click.argument("name")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option("--date", "on_value", type=str, default=None, help="Creation date as YYYY-MM-DD.")
def new_command(name: str, vault: Path | None, on_value: str | None) -> None:
    """Create a numbered idea folder from the templates."""
    try:
        folder = scaffold_new_idea(resolve_vault(vault), name, on=_parse_date(on_value))
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(str(folder))


@cli.command("index")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
def index_command(vault: Path | None) -> None:
    """Regenerate INDEX.md."""
    try:
        path = index_mod.regenerate(resolve_vault(vault))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(str(path))


@cli.command("list")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option("--verdict", "verdict_filter", type=click.Choice(["GO", "PIVOT", "NO-GO"]))
@click.option("--min-score", type=int, default=None)
def list_command(vault: Path | None, verdict_filter: str | None, min_score: int | None) -> None:
    """List scored ideas in a vault."""
    try:
        metas = index_mod.collect(resolve_vault(vault))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    if verdict_filter:
        metas = [meta for meta in metas if meta.verdict == verdict_filter]
    if min_score is not None:
        metas = [meta for meta in metas if meta.score is not None and meta.score >= min_score]

    click.echo("| # | Title | Score /40 | Verdict | Date |")
    click.echo("|---|---|---:|---|---|")
    for meta in metas:
        number = meta.folder.split("-", 1)[0]
        score = "" if meta.score is None else str(meta.score)
        click.echo(f"| {number} | {meta.title} | {score} | {meta.verdict} | {meta.date} |")


@cli.command("score")
@click.argument("idea", required=False)
@click.option("--suggest", is_flag=True, help="Ask Gemini (BYO GEMINI_API_KEY) to suggest scores for IDEA.")
@click.option("--model", default=None, help="Gemini model id used by --suggest.")
@click.option("--write", "write_folder", type=click.Path(file_okay=False, path_type=Path), default=None)
@click.option("--reindex", is_flag=True, help="Regenerate INDEX.md after --write.")
@click.option("--market", type=click.Choice(list(MARKET_MODIFIERS)), default=None)
@click.option("--feasibility", type=click.IntRange(0, 10), default=None)
@click.option("--competition", type=click.IntRange(0, 10), default=None)
@click.option("--scale", type=click.IntRange(0, 10), default=None)
@click.option("--founder-fit", "founder_fit", type=click.IntRange(0, 10), default=None)
def score_command(
    idea: str | None,
    suggest: bool,
    model: str | None,
    write_folder: Path | None,
    reindex: bool,
    market: str | None,
    feasibility: int | None,
    competition: int | None,
    scale: int | None,
    founder_fit: int | None,
) -> None:
    """Score an idea interactively, from flags, or from an AI suggestion (--suggest)."""
    if suggest:
        _run_suggest(idea, model)
        return

    feasibility = feasibility if feasibility is not None else click.prompt("Feasibility", type=click.IntRange(0, 10))
    competition = competition if competition is not None else click.prompt("Competition", type=click.IntRange(0, 10))
    scale = scale if scale is not None else click.prompt("Scale", type=click.IntRange(0, 10))
    founder_fit = founder_fit if founder_fit is not None else click.prompt("Founder-fit", type=click.IntRange(0, 10))
    market = market or click.prompt("Market status", type=click.Choice(list(MARKET_MODIFIERS)))

    scorecard = Scorecard(feasibility, competition, scale, founder_fit, market)
    _print_scoreboard(scorecard)

    if write_folder is not None:
        folder = write_folder.resolve()
        _write_score(folder, scorecard)
        click.echo(f"Wrote scoreboard to {folder / '05-verdict.md'} + README frontmatter.")
        if reindex:
            path = index_mod.regenerate(folder.parent)
            click.echo(f"Regenerated {path}.")
        else:
            click.echo("Run `ivault index` to refresh INDEX.md.")


@cli.command("export")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["csv", "json", "obsidian"]),
    default="json",
    show_default=True,
)
@click.option("--output", "-o", "output", type=str, default=None, help="Output file, or - for stdout.")
@click.option(
    "--out",
    "out_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory for --format obsidian (default <vault>/obsidian).",
)
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
def export_command(fmt: str, output: str | None, out_dir: Path | None, vault: Path | None) -> None:
    """Dump every idea (scores + verdict) to CSV, JSON, or an Obsidian note folder."""
    try:
        resolved = resolve_vault(vault)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    if fmt == "obsidian":
        if output == "-":
            msg = "obsidian export writes a folder of notes; use --out, not --output -"
            raise click.ClickException(msg)
        from ideas_vault.obsidian import export_obsidian

        target = out_dir if out_dir is not None else (Path(output) if output else None)
        path = export_obsidian(resolved, target)
        click.echo(str(path))
        return
    if output == "-":
        click.echo(EXPORT_RENDERERS[fmt](resolved), nl=False)
        return
    path = export_vault(resolved, fmt, output)
    click.echo(str(path))


@cli.command("rank")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
def rank_command(vault: Path | None) -> None:
    """Print a leaderboard of every idea, sorted by adjusted /40, with a GO/KILL flag."""
    try:
        metas = index_mod.collect(resolve_vault(vault))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo("| Rank | # | Title | Score /40 | Verdict | Flag |")
    click.echo("|---:|---|---|---:|---|---|")
    for position, meta in enumerate(index_mod.rank(metas), start=1):
        number = meta.folder.split("-", 1)[0]
        score = "" if meta.score is None else str(meta.score)
        flag = index_mod.go_or_kill(meta.verdict)
        click.echo(f"| {position} | {number} | {meta.title} | {score} | {meta.verdict} | {flag} |")


@cli.command("report")
@click.option("--html", "html_path", type=str, default=None, help="Output HTML file (default <vault>/ideas-vault.html).")
@click.option("--title", default=None, help="Heading for the leaderboard page.")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
def report_command(html_path: str | None, title: str | None, vault: Path | None) -> None:
    """Write a self-contained HTML leaderboard (4-pillar bars + GO/KILL badges)."""
    from ideas_vault.report import report as render_html_report

    try:
        resolved = resolve_vault(vault)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    path = render_html_report(resolved, html_path, title=title)
    click.echo(str(path))


@cli.command("notion-sync")
@click.option("--vault", type=click.Path(file_okay=False, path_type=Path), default=None)
def notion_sync_command(vault: Path | None) -> None:
    """Upsert every idea into a Notion database (opt-in: BYO NOTION_API_KEY + NOTION_DB)."""
    from ideas_vault import notion_sync

    try:
        resolved = resolve_vault(vault)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    try:
        results = notion_sync.sync(resolved)
    except notion_sync.MissingConfigError:
        click.echo(notion_sync.ENABLE_HINT)
        return
    except notion_sync.MissingRequestsError as exc:
        click.echo(str(exc))
        return
    except notion_sync.NotionError as exc:
        raise click.ClickException(str(exc)) from exc

    if not results:
        click.echo("No ideas found to sync.")
        return
    for result in results:
        click.echo(f"{result.action}: {result.idea_key} ({result.title})")
    created = sum(1 for r in results if r.action == "created")
    updated = len(results) - created
    click.echo(f"Synced {len(results)} ideas to Notion ({created} created, {updated} updated).")
