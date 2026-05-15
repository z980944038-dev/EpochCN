#!/usr/bin/env python3
"""Refresh EpochCN seed data from local addon folders.

This script intentionally only copies seed data. Runtime compatibility lives in
EpochCN's Lua modules so data updates do not require hand-editing addon logic.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
DEFAULT_DESKTOP = Path(os.environ.get("EPOCHCN_DESKTOP_ROOT", HOME / "Desktop")).expanduser()
DEFAULT_QUESTCN_ROOT = Path(os.environ.get("EPOCHCN_QUESTCN_ROOT", DEFAULT_DESKTOP / "QuestCN")).expanduser()
DEFAULT_TOOLTIPS_ROOT = Path(os.environ.get("EPOCHCN_TOOLTIPS_ROOT", DEFAULT_DESKTOP / "Tooltips_Chinese")).expanduser()
DEFAULT_FRAMEXML_GLOBAL_STRINGS = Path(
    os.environ.get("EPOCHCN_FRAMEXML_GLOBAL_STRINGS", DEFAULT_DESKTOP / "FrameXML/GlobalStrings.lua")
).expanduser()
DEFAULT_LUA_BIN = Path(os.environ.get("EPOCHCN_LUA_BIN", ROOT / "lua-5.1.5/src/lua")).expanduser()

REMOTES = {
    "pfQuest-epoch": "https://github.com/Bennylavaa/pfQuest-epoch",
    "Maczuga/pfQuest-Epoch": "https://github.com/Maczuga/pfQuest-Epoch",
    "pfQuest-wotlk": "https://github.com/akzkak/pfQuest-wotlk",
    "epochhead": "https://github.com/chrispl57/epochhead",
    "epoch-addons": "https://github.com/Defcons/epoch-addons",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh EpochCN seed data from local addon folders and regenerate derived files."
    )
    parser.add_argument(
        "--questcn-root",
        type=Path,
        default=DEFAULT_QUESTCN_ROOT,
        help="QuestCN addon root containing Data/QustCN_Data_CN.lua",
    )
    parser.add_argument(
        "--tooltips-root",
        type=Path,
        default=DEFAULT_TOOLTIPS_ROOT,
        help="Tooltips_Chinese addon root containing the seed Data/*.lua files",
    )
    parser.add_argument(
        "--framexml-global-strings",
        type=Path,
        default=DEFAULT_FRAMEXML_GLOBAL_STRINGS,
        help="Path to FrameXML GlobalStrings.lua",
    )
    parser.add_argument(
        "--lua-bin",
        type=Path,
        default=DEFAULT_LUA_BIN,
        help="Lua 5.1 executable used to run Tools/generate_map_data.lua",
    )
    parser.add_argument(
        "--skip-remote-heads",
        action="store_true",
        help="Skip git ls-remote checks when generating Tools/REMOTE_HEADS.md",
    )
    return parser.parse_args()


def build_copy_map(questcn_root: Path, tooltips_root: Path) -> dict[Path, Path]:
    return {
        questcn_root / "Data/QustCN_Data_CN.lua": ROOT / "Data/QuestCN_Data.lua",
        tooltips_root / "Data/SpellData_Season.lua": ROOT / "Data/SpellData_Season.lua",
        tooltips_root / "Data/SpellData_Epoch.lua": ROOT / "Data/SpellData_Epoch.lua",
        tooltips_root / "Data/ItemData.lua": ROOT / "Data/ItemData.lua",
        tooltips_root / "Data/UnitData.lua": ROOT / "Data/UnitData.lua",
        tooltips_root / "Data/CallBoardData.lua": ROOT / "Data/CallBoardData.lua",
        tooltips_root / "Data/GlobalData.lua": ROOT / "Data/GlobalData.lua",
    }


def git_head(url: str) -> str:
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", url, "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=20,
        ).strip()
    except Exception:
        return "unknown"

    return out.split()[0] if out else "unknown"


def generate_framexml_strings(framexml_global_strings: Path) -> None:
    if not framexml_global_strings.exists():
        raise FileNotFoundError(framexml_global_strings)

    text = framexml_global_strings.read_text(encoding="utf-8-sig")
    entries = []
    for line in text.splitlines():
        match = re.match(r"^([A-Z0-9_]+)\s*=\s*(.+);\s*$", line)
        if match:
            entries.append(match.groups())

    target = ROOT / "Data/FrameXMLStrings.lua"
    with target.open("w", encoding="utf-8", newline="\n") as out:
        out.write(f"-- Generated from {framexml_global_strings}\n")
        out.write("EpochCN_FrameXMLStrings = {\n")
        for key, value in entries:
            out.write(f'  ["{key}"] = {value},\n')
        out.write("}\n")
    print(f"generated {len(entries)} FrameXML strings")


def generate_map_data(lua_bin: Path) -> None:
    if not lua_bin.exists():
        raise FileNotFoundError(lua_bin)
    subprocess.check_call([str(lua_bin), str(ROOT / "Tools/generate_map_data.lua")])


def main() -> None:
    args = parse_args()
    copies = build_copy_map(args.questcn_root.expanduser(), args.tooltips_root.expanduser())

    for source, target in copies.items():
        if not source.exists():
            raise FileNotFoundError(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        print(f"copied {source} -> {target}")

    generate_framexml_strings(args.framexml_global_strings.expanduser())
    generate_map_data(args.lua_bin.expanduser())

    lines = ["# Remote heads", ""]
    for name, url in REMOTES.items():
        head = "skipped" if args.skip_remote_heads else git_head(url)
        lines.append(f"- {name}: `{head}`")
    (ROOT / "Tools/REMOTE_HEADS.md").write_text("\n".join(lines) + "\n")
    print("wrote Tools/REMOTE_HEADS.md")


if __name__ == "__main__":
    main()
