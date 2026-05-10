#!/usr/bin/env python3
"""
用 pfQuest-epoch enUS 的 quest 英文标题给 EpochQuestData[id][5]（英文标题字段）
批量补齐。EpochQuestData 的第 5 字段是"英文标题"，Core.lua 会把它注册到
questIDByTitle，这样 NPC 对话框显示英文标题时也能映射到中文数据。
"""
import re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "Tools" / "cache" / "pfquest_epoch"
DATA = ROOT / "Data"


def unesc(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


# Load pfQuest-epoch enUS quest titles: { id: "English T" }
def load_enUS_titles():
    path = CACHE / "quests-enUS.lua"
    text = path.read_text(encoding="utf-8")
    m = {}
    # Match blocks [id] = { ["T"] = "..."
    pattern = re.compile(r'\[(\d+)\]\s*=\s*\{[^}]*?\["T"\]\s*=\s*"((?:[^"\\]|\\.)*)"', re.S)
    for qid, title in pattern.findall(text):
        m[int(qid)] = unesc(title)
    return m


def main():
    en_titles = load_enUS_titles()
    print(f"Loaded {len(en_titles)} pfQuest-epoch enUS quest titles.")

    path = DATA / "EpochQuestData.lua"
    text = path.read_text(encoding="utf-8")

    # EpochQuestData entries: [id]={"中文标题","目标","描述","source","英文标题"}
    # We may add or correct the 5th field when pfQuest-epoch has a definitive English.
    entry_re = re.compile(
        r'(\[(\d+)\]=\{"((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)",(?:"((?:[^"\\]|\\.)*)")?\})'
    )
    # Some entries have 4 fields (no English yet); support that.
    entry_re_4 = re.compile(
        r'(\[(\d+)\]=\{"((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)"\})'
    )

    added = corrected = kept = 0

    def repl5(m):
        nonlocal added, corrected, kept
        whole, qid, title, obj, desc, source, eng = m.groups()
        qid = int(qid)
        want = en_titles.get(qid)
        if not want:
            kept += 1
            return whole
        if eng == want:
            kept += 1
            return whole
        if eng:
            # 存在旧英文，如果不一样且 want 有效就更新
            corrected += 1
        else:
            added += 1
        return f'[{qid}]={{"{title}","{obj}","{desc}","{source}","{esc(want)}"}}'

    new_text = entry_re.sub(repl5, text)

    # 4-field entries: add English as 5th
    def repl4(m):
        nonlocal added
        whole, qid, title, obj, desc, source = m.groups()
        qid = int(qid)
        want = en_titles.get(qid)
        if not want:
            return whole
        added += 1
        return f'[{qid}]={{"{title}","{obj}","{desc}","{source}","{esc(want)}"}}'

    new_text = entry_re_4.sub(repl4, new_text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")

    print(f"Added English titles: {added}")
    print(f"Corrected English titles: {corrected}")
    print(f"Unchanged entries: {kept}")


if __name__ == "__main__":
    main()
