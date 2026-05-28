from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "README.md", ROOT / "INDEX.md", ROOT / "docs", ROOT / "pillars", ROOT / "examples"]
LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    files: list[Path] = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
        elif target.exists():
            files.extend(sorted(target.rglob("*.md")))
    return files


def _is_external(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "mailto"}


def main() -> None:
    failures: list[str] = []
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith("#") or _is_external(raw):
                continue
            target = raw.split("#", 1)[0].strip("<>")
            if not target:
                continue
            resolved = (path.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                failures.append(f"{path.relative_to(ROOT)}: link leaves repo: {raw}")
                continue
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)}: missing link target: {raw}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
