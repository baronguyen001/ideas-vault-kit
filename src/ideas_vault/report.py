"""Render a self-contained HTML leaderboard for a vault.

Pure string templating: no JS dependency, no template engine, no network. The output
is a single ``.html`` file you can open locally or attach to a launch post. Each idea
shows its adjusted ``/40`` as a progress bar plus a GO/KILL badge; the table is ordered
by score (highest first) so it reads like a static, pre-sorted leaderboard.

Per-idea pillar breakdowns are not stored in the vault frontmatter (only the adjusted
total and verdict are), so the bars chart the adjusted ``/40``; the four pillars that
feed it are named in the page legend.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from ideas_vault.frontmatter import IdeaMeta
from ideas_vault.index import _idea_number, collect, go_or_kill, rank

_MAX_SCORE = 40

_BADGE_CLASS = {"GO": "go", "PIVOT": "pivot", "NO-GO": "nogo"}

_STYLE = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  margin: 0; padding: 2rem; line-height: 1.5; color: #1b1f24; background: #f6f8fa; }
.wrap { max-width: 860px; margin: 0 auto; }
h1 { margin: 0 0 .25rem; font-size: 1.6rem; }
.sub { color: #57606a; margin: 0 0 1.5rem; }
table { width: 100%; border-collapse: collapse; background: #fff;
  border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; }
th, td { padding: .6rem .75rem; text-align: left; border-bottom: 1px solid #eaeef2;
  font-size: .95rem; vertical-align: middle; }
th { background: #f6f8fa; font-weight: 600; cursor: pointer; user-select: none; }
td.num, th.num { text-align: right; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
.bar { position: relative; height: 16px; width: 160px; background: #eaeef2;
  border-radius: 8px; overflow: hidden; }
.bar > span { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 8px;
  background: linear-gradient(90deg, #2da44e, #57ab5a); }
.bar.kill > span { background: linear-gradient(90deg, #cf222e, #e5534b); }
.badge { display: inline-block; padding: .1rem .55rem; border-radius: 999px;
  font-size: .8rem; font-weight: 600; color: #fff; }
.badge.go { background: #2da44e; }
.badge.pivot { background: #bf8700; }
.badge.nogo { background: #cf222e; }
.badge.none { background: #8c959f; }
.legend { margin: 1.25rem 0 0; color: #57606a; font-size: .85rem; }
footer { margin-top: 1.5rem; color: #8c959f; font-size: .8rem; }
""".strip()

# Static, dependency-free column sorter so headers feel clickable in a launch demo.
_SCRIPT = """
document.querySelectorAll('th[data-sort]').forEach(function (th) {
  th.addEventListener('click', function () {
    var table = th.closest('table');
    var body = table.tBodies[0];
    var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
    var numeric = th.dataset.sort === 'num';
    var asc = th.dataset.dir !== 'asc';
    th.dataset.dir = asc ? 'asc' : 'desc';
    var rows = Array.prototype.slice.call(body.rows);
    rows.sort(function (a, b) {
      var x = a.cells[idx].dataset.value || a.cells[idx].textContent;
      var y = b.cells[idx].dataset.value || b.cells[idx].textContent;
      if (numeric) { x = parseFloat(x) || 0; y = parseFloat(y) || 0; return asc ? x - y : y - x; }
      return asc ? x.localeCompare(y) : y.localeCompare(x);
    });
    rows.forEach(function (row) { body.appendChild(row); });
  });
});
""".strip()


def _badge(meta: IdeaMeta) -> str:
    if not meta.verdict:
        return '<span class="badge none">unscored</span>'
    cls = _BADGE_CLASS.get(meta.verdict, "none")
    return f'<span class="badge {cls}">{escape(meta.verdict)}</span>'


def _bar(meta: IdeaMeta) -> str:
    score = meta.score or 0
    pct = max(0, min(100, round(100 * score / _MAX_SCORE)))
    kill = " kill" if go_or_kill(meta.verdict) == "KILL" else ""
    label = "" if meta.score is None else f"{meta.score}/40"
    return (
        f'<div class="bar{kill}" title="{label}" role="img" aria-label="{label or "unscored"}">'
        f'<span style="width: {pct}%"></span></div>'
    )


def _row(position: int, meta: IdeaMeta) -> str:
    number = _idea_number(meta.folder)
    score_value = "" if meta.score is None else str(meta.score)
    score_cell = "" if meta.score is None else f"{meta.score}/40"
    return (
        "<tr>"
        f'<td class="num">{position}</td>'
        f'<td class="num">{escape(number)}</td>'
        f"<td>{escape(meta.title)}</td>"
        f'<td>{_bar(meta)}</td>'
        f'<td class="num" data-value="{score_value or 0}">{score_cell}</td>'
        f'<td>{_badge(meta)}</td>'
        f'<td>{escape(go_or_kill(meta.verdict))}</td>'
        "</tr>"
    )


def render_report(metas: list[IdeaMeta], *, title: str = "Ideas Vault Leaderboard") -> str:
    """Return a complete, self-contained HTML document for ``metas`` ranked by score."""
    ranked = rank(metas)
    rows = "\n".join(_row(position, meta) for position, meta in enumerate(ranked, start=1))
    if not rows:
        rows = '<tr><td colspan="7">No scored ideas yet.</td></tr>'
    safe_title = escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
{_STYLE}
</style>
</head>
<body>
<div class="wrap">
<h1>{safe_title}</h1>
<p class="sub">{len(ranked)} ideas, ranked by adjusted score out of 40.</p>
<table>
<thead>
<tr>
<th class="num" data-sort="num">Rank</th>
<th class="num" data-sort="num">#</th>
<th data-sort="text">Idea</th>
<th>Score</th>
<th class="num" data-sort="num">/40</th>
<th data-sort="text">Verdict</th>
<th data-sort="text">Flag</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
<p class="legend">Pillars scored 0-10 each: Feasibility &amp; Tech, Competition &amp; Market,
Scale &amp; Unit Economics, Founder-Fit. Summed to /40, adjusted by market status, then
GO &gt;= 30, PIVOT 15-29, NO-GO &lt; 15. Any pillar &lt;= 2 caps the verdict at PIVOT or NO-GO.</p>
<footer>Generated by ideas-vault-kit &middot; <code>ivault report --html</code></footer>
</div>
<script>
{_SCRIPT}
</script>
</body>
</html>
"""


def report(vault: Path, output: str | Path | None = None, *, title: str | None = None) -> Path:
    """Render the vault leaderboard to ``output`` (default ``<vault>/ideas-vault.html``)."""
    metas = collect(vault)
    html = render_report(metas, title=title) if title else render_report(metas)
    path = Path(output) if output else vault / "ideas-vault.html"
    path.write_text(html, encoding="utf-8", newline="\n")
    return path
