# -*- coding: utf-8 -*-
"""
Normalize TSV to strict 12-col schema:
  spell_id, priority, skill_line_ids,
  name_en, rank_en, description_en, tooltip_en,
  name_zh, rank_zh, description_zh, tooltip_zh,
  notes

Behaviour:
- 12 cols   : pass through.
- 13-14 cols: if trailing columns are all empty, drop them.
- 11 cols   : append "" for notes.
- <=10 cols : pad with "" at the end.
- 16 cols   : handle the "shifted zh" pattern where positions 7..10 are pad
               and positions 11..14 hold the actual zh. Keep pos 15 as notes.
- 26 cols   : manually handled below (known case: spell 689 + 813 concat).
- Any other unexpected shape is logged.
"""
import sys, os

SRC = sys.argv[1]
DST = sys.argv[2]
LOG = sys.argv[3] if len(sys.argv) > 3 else None

log_lines = []
def log(s): log_lines.append(s)

def is_trailing_empty(cols, keep):
    return all(c.strip() == "" for c in cols[keep:])

def normalize(cols, lineno):
    n = len(cols)

    if n == 12:
        return [cols], None

    if n == 11:
        return [cols + [""]], "pad-notes"

    if n == 10:
        return [cols + ["", ""]], "pad-tip+notes"

    if n == 9:
        return [cols + ["", "", ""]], "pad-3"
    if n == 8:
        return [cols + ["", "", "", ""]], "pad-4"
    if n == 5 or n == 2 or n < 8:
        # mostly stub untranslated rows, pad to 12
        return [cols + [""] * (12 - n)], f"pad-to-12(from={n})"

    if n == 13 or n == 14:
        if is_trailing_empty(cols, 12):
            return [cols[:12]], f"trim-{n-12}"
        else:
            log(f"line {lineno}: {n}-col row has non-empty trailing, keep first 12 and log extra: {cols[12:]!r}")
            return [cols[:12]], f"trim-{n-12}-nonempty"

    if n == 16:
        # Pattern: [0..6] en fields + [7..10] empty pad + [11..14] zh fields + [15] notes
        pad = cols[7:11]
        if all(c.strip() == "" for c in pad):
            fixed = cols[:7] + cols[11:15] + [cols[15]]
            if len(fixed) == 12:
                return [fixed], "unshift-16"
        log(f"line {lineno}: 16-col row with unexpected pad content: {pad!r}")
        # Fallback: take first 12
        return [cols[:12]], "16-fallback"

    if n == 26:
        # Known case: spell 689 "Drain Life" row glued with next row.
        # cols[10] was "每$t1秒向施法者吸取$s1点813" where "813" is the start
        # of the next row's spell_id. cols[11..] already align as a new row.
        if cols[0] == "689" and cols[11] == "spellbook" and cols[13] == "Language Thalassian":
            # Restore tip_zh by stripping the '813' suffix
            tip_zh_raw = cols[10]
            if tip_zh_raw.endswith("813"):
                tip_zh_fixed = tip_zh_raw[:-3]
            else:
                tip_zh_fixed = tip_zh_raw
            row1 = cols[:10] + [tip_zh_fixed, ""]  # notes = ''
            assert len(row1) == 12
            # Row2 starts with spell_id "813"
            row2_cols = ["813"] + cols[11:]  # 16 total
            # Now row2 is 16 cols, apply same 16-col logic
            pad = row2_cols[7:11]
            if all(c.strip() == "" for c in pad):
                row2 = row2_cols[:7] + row2_cols[11:15] + [row2_cols[15]]
                assert len(row2) == 12
            else:
                row2 = row2_cols[:12]
            log(f"line {lineno}: split 26-col row into 689(Drain Life)+813(Language Thalassian).")
            return [row1, row2], "split-26"
        log(f"line {lineno}: unknown 26-col row, taking first 12.")
        return [cols[:12]], "26-fallback"

    # Any other unexpected
    log(f"line {lineno}: unexpected {n} cols, taking first 12 if possible.")
    if n > 12:
        return [cols[:12]], f"trim-{n}-cols"
    return [cols + [""] * (12 - n)], f"pad-{n}-cols"

def main():
    out_rows = []
    shape_stats = {}
    with open(SRC, "r", encoding="utf-8") as f:
        header = next(f).rstrip("\n").rstrip("\r").split("\t")
        assert len(header) == 12, f"Unexpected header: {header}"
        for i, line in enumerate(f, start=2):
            line_nl = line.rstrip("\n").rstrip("\r")
            if not line_nl.strip():
                continue
            cols = line_nl.split("\t")
            new_rows, tag = normalize(cols, i)
            key = tag or f"cols={len(cols)}"
            shape_stats[key] = shape_stats.get(key, 0) + 1
            out_rows.extend(new_rows)

    # Write output
    with open(DST, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(header) + "\n")
        for r in out_rows:
            # Ensure exactly 12 cells and no embedded tabs
            cleaned = [(c or "").replace("\t", " ") for c in r]
            if len(cleaned) != 12:
                # Shouldn't happen - pad or trim as a last resort
                while len(cleaned) < 12: cleaned.append("")
                cleaned = cleaned[:12]
            f.write("\t".join(cleaned) + "\n")

    print(f"Input rows: {sum(shape_stats.values())}")
    print(f"Output rows: {len(out_rows)}")
    print("Transformations applied:")
    for k in sorted(shape_stats):
        print(f"  {k}: {shape_stats[k]}")

    if LOG and log_lines:
        with open(LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"\nLog written to {LOG} ({len(log_lines)} entries)")
    elif log_lines:
        print(f"\n(log entries: {len(log_lines)})")
        for l in log_lines[:10]: print(" ", l)

main()
