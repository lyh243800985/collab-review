#!/usr/bin/env python3
"""Reject machine-specific paths and accidentally committed credentials."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


TEXT_SUFFIXES = {".json", ".md", ".py", ".js", ".yaml", ".yml", ".html", ".toml", ".txt"}
# Only runtime files enter the release archive; repository history and legacy notes stay local.
IGNORED_DIRS = {".git", ".temp", ".venv", "__pycache__", ".pytest_cache", "dist", "build", "docs", "tests"}
DRIVE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
# Split the literal so this checker does not report its own rule definition.
FILE_URI = re.compile("file:" + "///", re.IGNORECASE)
FIGMA_TOKEN = re.compile(r"figd_[A-Za-z0-9_-]{12,}")


def scan(root: Path) -> list[dict[str, str]]:
    """Scan only distributable text files; generated reports and environments are excluded."""

    issues: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            issues.append({"file": str(path.relative_to(root)), "issue": "not UTF-8"})
            continue
        for label, pattern in (("absolute drive path", DRIVE_PATH), ("file URI", FILE_URI), ("Figma token", FIGMA_TOKEN)):
            if pattern.search(content):
                issues.append({"file": str(path.relative_to(root)), "issue": label})
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that a plugin can be moved safely")
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    issues = scan(args.root.resolve())
    print(json.dumps({"portable": not issues, "issues": issues}, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
