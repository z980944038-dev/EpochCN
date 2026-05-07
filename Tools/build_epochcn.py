#!/usr/bin/env python3
"""Refresh EpochCN seed data from local addon folders.

This script intentionally only copies seed data. Runtime compatibility lives in
EpochCN's Lua modules so data updates do not require hand-editing addon logic.
"""

from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path("/Users/macos/Desktop")

COPIES = {
    DESKTOP / "QuestCN/Data/QustCN_Data_CN.lua": ROOT / "Data/QuestCN_Data.lua",
    DESKTOP / "Tooltips_Chinese/Data/SpellData_52.lua": ROOT / "Data/SpellData_52.lua",
    DESKTOP / "Tooltips_Chinese/Data/SpellData_Season.lua": ROOT / "Data/SpellData_Season.lua",
    DESKTOP / "Tooltips_Chinese/Data/SpellData_Epoch.lua": ROOT / "Data/SpellData_Epoch.lua",
    DESKTOP / "Tooltips_Chinese/Data/ItemData.lua": ROOT / "Data/ItemData.lua",
    DESKTOP / "Tooltips_Chinese/Data/UnitData.lua": ROOT / "Data/UnitData.lua",
    DESKTOP / "Tooltips_Chinese/Data/CallBoardData.lua": ROOT / "Data/CallBoardData.lua",
    DESKTOP / "Tooltips_Chinese/Data/GlobalData.lua": ROOT / "Data/GlobalData.lua",
}

FRAMEXML_GLOBAL_STRINGS = DESKTOP / "FrameXML/GlobalStrings.lua"
LUA_BIN = Path("/Users/macos/Documents/lua-5.1.5/src/lua")

REMOTES = {
    "pfQuest-epoch": "https://github.com/Bennylavaa/pfQuest-epoch",
    "Maczuga/pfQuest-Epoch": "https://github.com/Maczuga/pfQuest-Epoch",
    "pfQuest-wotlk": "https://github.com/akzkak/pfQuest-wotlk",
    "epochhead": "https://github.com/chrispl57/epochhead",
    "epoch-addons": "https://github.com/Defcons/epoch-addons",
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


def fix_spell_data_52() -> None:
    path = ROOT / "Data/SpellData_52.lua"
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("function LoadTPCNSpellDataSeason()", "function LoadTPCNSpellData52()", 1)
    text = text.replace("TPCN_SpellData_Season = {", "TPCN_SpellData_52 = {", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("fixed Data/SpellData_52.lua loader")


def generate_framexml_strings() -> None:
    if not FRAMEXML_GLOBAL_STRINGS.exists():
        raise FileNotFoundError(FRAMEXML_GLOBAL_STRINGS)

    text = FRAMEXML_GLOBAL_STRINGS.read_text(encoding="utf-8-sig")
    entries = []
    for line in text.splitlines():
        match = re.match(r"^([A-Z0-9_]+)\s*=\s*(.+);\s*$", line)
        if match:
            entries.append(match.groups())

    target = ROOT / "Data/FrameXMLStrings.lua"
    with target.open("w", encoding="utf-8", newline="\n") as out:
        out.write("-- Generated from /Users/macos/Desktop/FrameXML/GlobalStrings.lua\n")
        out.write("EpochCN_FrameXMLStrings = {\n")
        for key, value in entries:
            out.write(f'  ["{key}"] = {value},\n')
        out.write("}\n")
    print(f"generated {len(entries)} FrameXML strings")


def generate_map_data() -> None:
    if not LUA_BIN.exists():
        raise FileNotFoundError(LUA_BIN)
    subprocess.check_call([str(LUA_BIN), str(ROOT / "Tools/generate_map_data.lua")])


def main() -> None:
    for source, target in COPIES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        print(f"copied {source} -> {target}")

    fix_spell_data_52()
    generate_framexml_strings()
    generate_map_data()

    lines = ["# Remote heads", ""]
    for name, url in REMOTES.items():
        lines.append(f"- {name}: `{git_head(url)}`")
    (ROOT / "Tools/REMOTE_HEADS.md").write_text("\n".join(lines) + "\n")
    print("wrote Tools/REMOTE_HEADS.md")


if __name__ == "__main__":
    main()
