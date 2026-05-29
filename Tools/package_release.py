#!/usr/bin/env python3
"""Build a clean EpochCN release zip from runtime addon files only."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ADDON_NAME = "EpochCN"
RUNTIME_DIRS = ("Data", "Modules", "docs")
RUNTIME_FILES = ("EpochCN.toc", "Core.lua", "README.md", "LICENSE")


def addon_version() -> str:
    toc = ROOT / "EpochCN.toc"
    match = re.search(r"^## Version:\s*(.+)$", toc.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else "unknown"


def iter_runtime_files():
    for name in RUNTIME_FILES:
        path = ROOT / name
        if path.is_file():
            yield path

    for dirname in RUNTIME_DIRS:
        base = ROOT / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and not path.name.startswith("."):
                yield path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean EpochCN release zip.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / f"{ADDON_NAME}-v{addon_version()}.zip",
        help="Output zip path.",
    )
    args = parser.parse_args()

    output = args.output.expanduser()
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)

    files = list(iter_runtime_files())
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = Path(ADDON_NAME) / path.relative_to(ROOT)
            zf.write(path, arcname.as_posix())

    print(f"wrote {output}")
    print(f"files: {len(files)}")


if __name__ == "__main__":
    main()
