from __future__ import annotations

import re
import shutil
import struct
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(r"D:\1927\Ascension Launcher\resources\ascension-live\1")
WORK = ROOT / "_cn_work_spell_name_fix"
OVERLAY = WORK / "overlay"
PATCH_B_SPELL = ROOT / "spell" / "Spell.dbc"
CURRENT_SPELL = OVERLAY / "DBFilesClient" / "Spell.dbc"
MPQCLI = ROOT / "_cn_tools" / "mpqcli.exe"
OUT_MPQ = WORK / "patch-X-native-batch24-spell-from-patch-b.MPQ"
REPORT = ROOT / "PATCH_X_BATCH24_SPELL_REPORT.md"

ACTIVE_PATCHES = [
    ROOT / "patch-X.MPQ",
    ROOT.parent.parent / "patch-X.MPQ",
    ROOT.parent / "Data" / "patch-X.MPQ",
]

# WotLK Spell.dbc localized enUS string columns.
TEXT_FIELDS = {
    136: "name",
    153: "rank",
    170: "description",
    187: "tooltip",
}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def read_cstring(blob: bytes, offset: int) -> str:
    if offset <= 0 or offset >= len(blob):
        return ""
    end = blob.find(b"\0", offset)
    if end < 0:
        return ""
    raw = blob[offset:end]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="ignore")


class Dbc:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        header = struct.unpack_from("<4s4I", self.data, 0)
        self.magic, self.row_count, self.field_count, self.record_size, self.string_size = header
        if self.magic != b"WDBC":
            raise ValueError(f"{path} is not a WDBC file")
        if self.record_size != self.field_count * 4:
            raise ValueError(f"{path} has unexpected record size")
        expected = 20 + self.row_count * self.record_size + self.string_size
        if expected != len(self.data):
            raise ValueError(f"{path} size mismatch: expected {expected}, got {len(self.data)}")
        self.rows: list[list[int]] = [
            list(struct.unpack_from("<" + "I" * self.field_count, self.data, 20 + i * self.record_size))
            for i in range(self.row_count)
        ]
        self.strings = self.data[20 + self.row_count * self.record_size :]

    def text(self, row: list[int], field: int) -> str:
        return read_cstring(self.strings, row[field])


def collect_translations(base: Dbc, current: Dbc) -> tuple[dict[int, dict[int, str]], Counter, Counter]:
    by_id: dict[int, list[int]] = defaultdict(list)
    duplicate_ids: Counter = Counter()
    for idx, row in enumerate(current.rows):
        spell_id = row[0]
        by_id[spell_id].append(idx)
        if len(by_id[spell_id]) > 1:
            duplicate_ids[spell_id] += 1

    translations: dict[int, dict[int, str]] = defaultdict(dict)
    source_counter: Counter = Counter()
    field_counter: Counter = Counter()

    for idx, base_row in enumerate(base.rows):
        spell_id = base_row[0]
        candidates: list[tuple[str, list[int]]] = []
        for current_idx in by_id.get(spell_id, []):
            candidates.append(("id", current.rows[current_idx]))
        if idx < len(current.rows) and current.rows[idx][0] != spell_id:
            candidates.append(("row-index-fallback", current.rows[idx]))

        for source_name, current_row in candidates:
            for field in TEXT_FIELDS:
                if field in translations[spell_id]:
                    continue
                text = current.text(current_row, field).strip()
                if not text or not has_cjk(text):
                    continue
                base_text = base.text(base_row, field).strip()
                if text == base_text:
                    continue
                translations[spell_id][field] = text
                source_counter[source_name] += 1
                field_counter[TEXT_FIELDS[field]] += 1

    return translations, source_counter, field_counter


def rebuild_spell(base: Dbc, translations: dict[int, dict[int, str]]) -> tuple[bytes, Counter]:
    rows = [row[:] for row in base.rows]
    string_block = bytearray(base.strings)
    offset_by_bytes: dict[bytes, int] = {}
    applied = Counter()

    def intern(text: str) -> int:
        raw = text.encode("utf-8") + b"\0"
        existing = offset_by_bytes.get(raw)
        if existing is not None:
            return existing
        offset = len(string_block)
        string_block.extend(raw)
        offset_by_bytes[raw] = offset
        return offset

    by_base_id = {row[0]: idx for idx, row in enumerate(base.rows)}
    for spell_id, field_map in translations.items():
        row_idx = by_base_id.get(spell_id)
        if row_idx is None:
            continue
        for field, text in field_map.items():
            rows[row_idx][field] = intern(text)
            applied[TEXT_FIELDS[field]] += 1

    header = struct.pack(
        "<4s4I",
        b"WDBC",
        base.row_count,
        base.field_count,
        base.record_size,
        len(string_block),
    )
    record_bytes = bytearray()
    for row in rows:
        record_bytes.extend(struct.pack("<" + "I" * base.field_count, *row))
    return header + record_bytes + string_block, applied


def validate_rebuild(base: Dbc, rebuilt: Dbc) -> tuple[int, Counter]:
    allowed = set(TEXT_FIELDS)
    diff_rows = 0
    diff_fields: Counter = Counter()
    for base_row, new_row in zip(base.rows, rebuilt.rows):
        row_has_diff = False
        for field, (old, new) in enumerate(zip(base_row, new_row)):
            if old == new or field in allowed:
                continue
            row_has_diff = True
            diff_fields[field] += 1
        if row_has_diff:
            diff_rows += 1
    return diff_rows, diff_fields


def backup(path: Path, stamp: str) -> Path | None:
    if not path.exists():
        return None
    dest = WORK / f"backup_{path.stem}_before_batch24_{stamp}{path.suffix}"
    shutil.copy2(path, dest)
    return dest


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    if not PATCH_B_SPELL.exists():
        raise FileNotFoundError(PATCH_B_SPELL)
    if not CURRENT_SPELL.exists():
        raise FileNotFoundError(CURRENT_SPELL)
    if not MPQCLI.exists():
        raise FileNotFoundError(MPQCLI)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    WORK.mkdir(exist_ok=True)
    backups = [backup(CURRENT_SPELL, stamp)]
    backups.extend(backup(path, stamp) for path in ACTIVE_PATCHES)

    base = Dbc(PATCH_B_SPELL)
    current = Dbc(CURRENT_SPELL)
    if (base.row_count, base.field_count, base.record_size) != (
        current.row_count,
        current.field_count,
        current.record_size,
    ):
        raise ValueError("Patch-B Spell.dbc and current Spell.dbc have different structures")

    translations, source_counter, field_counter = collect_translations(base, current)
    rebuilt_bytes, applied = rebuild_spell(base, translations)

    CURRENT_SPELL.write_bytes(rebuilt_bytes)
    rebuilt = Dbc(CURRENT_SPELL)
    bad_rows, bad_fields = validate_rebuild(base, rebuilt)
    if bad_rows:
        raise RuntimeError(f"Non-text fields changed in rebuilt Spell.dbc: {bad_rows} rows, {bad_fields}")

    if OUT_MPQ.exists():
        OUT_MPQ.unlink()
    run([str(MPQCLI), "create", str(OVERLAY), "--game", "wow-wotlk", "--output", str(OUT_MPQ)])
    for target in ACTIVE_PATCHES:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT_MPQ, target)

    report = [
        "# PATCH-X batch24: Spell.dbc from patch-B base",
        "",
        "## 目的",
        "- 以 `spell/Spell.dbc`（从 `patch-B.MPQ` 导出）作为权威底表。",
        "- 仅迁移当前补丁已有中文的法术文本字段，避免覆盖 Ascension/patch-B 的法术数值和结构改动。",
        "- 顺带清理旧流程误写到非文本字段里的少量字符串偏移。",
        "",
        "## 文本字段",
        "- field 136: 法术名称",
        "- field 153: 等级/副标题",
        "- field 170: 法术描述",
        "- field 187: 光环/tooltip 文本",
        "",
        "## 应用统计",
        f"- 可迁移 spell id 数：{len(translations)}",
        f"- 已应用文本数：{sum(applied.values())}",
        f"- 按字段：{dict(applied)}",
        f"- 来源统计：{dict(source_counter)}",
        f"- 收集统计：{dict(field_counter)}",
        "",
        "## DBC 结构",
        f"- 行数：{rebuilt.row_count}",
        f"- 字段数：{rebuilt.field_count}",
        f"- 记录大小：{rebuilt.record_size}",
        f"- patch-B 字符串池：{base.string_size}",
        f"- batch24 字符串池：{rebuilt.string_size}",
        "- 非文本字段校验：通过，除 136/153/170/187 外与 patch-B 完全一致。",
        "",
        "## 输出",
        f"- `{OUT_MPQ}`",
    ]
    report.extend(f"- `{target}`" for target in ACTIVE_PATCHES)
    report.extend(["", "## 备份"])
    report.extend(f"- `{b}`" for b in backups if b)
    report.extend(
        [
            "",
            "## 游戏内测试建议",
            "- 进入游戏确认不会 #132。",
            "- 打开技能书、天赋/法术相关页面。",
            "- 鼠标悬停动作条法术、Buff/Debuff、训练师或技能相关物品。",
            "- 重点观察法术名、等级、描述是否仍中文，若有英文残留再进入下一轮补齐。",
            "",
        ]
    )
    REPORT.write_text("\n".join(report), encoding="utf-8")

    print(f"Built {OUT_MPQ}")
    print(f"Applied {sum(applied.values())} spell text entries: {dict(applied)}")
    print(f"Wrote report {REPORT}")


if __name__ == "__main__":
    main()
