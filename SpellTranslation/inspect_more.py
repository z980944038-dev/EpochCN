# -*- coding: utf-8 -*-
import sys
path = sys.argv[1]
want = int(sys.argv[2])
with open(path, "r", encoding="utf-8") as f:
    next(f)  # header
    shown = 0
    for i, line in enumerate(f, start=1):
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        if len(cols) == want:
            # Want rows where at least one middle column has data
            non_empty = sum(1 for c in cols[4:] if c.strip())
            if non_empty >= 3 and shown < 5:
                print(f"--- line {i} (cols={len(cols)}) ---")
                for j, c in enumerate(cols):
                    preview = c if len(c) < 150 else c[:150] + "..."
                    print(f"  [{j}] {preview!r}")
                shown += 1
