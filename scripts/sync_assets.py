from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    (ROOT / "templates", ROOT / "src" / "ideas_vault" / "_assets" / "templates"),
    (ROOT / "pillars", ROOT / "src" / "ideas_vault" / "_assets" / "pillars"),
]


def _sync(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _assert_same(src: Path, dst: Path) -> None:
    comparison = filecmp.dircmp(src, dst)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        msg = (
            f"asset mismatch between {src.relative_to(ROOT)} and {dst.relative_to(ROOT)}: "
            f"left_only={comparison.left_only}, right_only={comparison.right_only}, "
            f"diff={comparison.diff_files}"
        )
        raise SystemExit(msg)
    for name in comparison.common_dirs:
        _assert_same(src / name, dst / name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Copy top-level docs into package assets.")
    parser.add_argument("--check", action="store_true", help="Assert package assets match top-level docs.")
    args = parser.parse_args()
    if not args.sync and not args.check:
        args.check = True

    for src, dst in PAIRS:
        if args.sync:
            _sync(src, dst)
        if args.check:
            _assert_same(src, dst)


if __name__ == "__main__":
    main()
