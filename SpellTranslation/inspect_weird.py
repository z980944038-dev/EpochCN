# -*- coding: utf-8 -*-
import sys
from collections import Counter
path = sys.argv[1]
want = int(sys.argv[2])
max_show = int(sys.argv[3]) if len(sys.argv) > 3 else 3
shown = 0
with open(path, "r", encoding="utf-8") as f:
    next(f)  # header
    for i, line in enumerate(f, start=1):
        line_nl = line.rstrip("\n").rstrip("\r")
        if not line_nl.strip():
            continue
        cols = line_nl.split("\t")
        if len(cols) == want:
            if shown < max_show:
                print(f"--- line {i} (cols={len(cols)}) ---")
                for j, c in enumerate(cols):
                    preview = c if len(c) < 120 else c[:120] + "..."
                    print(f"  [{j}] {preview!r}")
            shown += 1
print(f"Total: {shown}")
