#!/usr/bin/env python3
"""Build a portable release archive from an explicit runtime allowlist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile

from check_portability import scan


ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = (".codex-plugin", "skills", "scripts", "assets")
FILES = (".mcp.json", "README.md")


def version() -> str:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return str(manifest["version"])


def package(output: Path) -> list[str]:
    """Archive runtime files only; local credentials and review evidence never enter releases."""

    issues = scan(ROOT)
    if issues:
        raise ValueError(f"plugin is not portable: {issues}")
    members: list[Path] = []
    for directory in DIRECTORIES:
        members.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
    members.extend(ROOT / name for name in FILES)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(members)):
            archive.write(path, Path("collab-verified-review") / path.relative_to(ROOT))
    return [str(path.relative_to(ROOT)) for path in sorted(set(members))]


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the Collab Verified Review Codex Plugin")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / f"collab-verified-review-{version()}.zip",
    )
    args = parser.parse_args()
    members = package(args.output.resolve())
    print(json.dumps({"package": str(args.output.resolve()), "fileCount": len(members)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
