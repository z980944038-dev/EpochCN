# -*- coding: utf-8 -*-
import sys
path = sys.argv[1]
want = int(sys.argv[2]) if len(sys.argv) > 2 else 2
shown = 0
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        line_nl = line.rstrip("\n").rstrip("\r")
        cols = line_nl.split("\t")
        if len(cols) == want:
            if shown < 5:
                print(f"--- line {i} (cols={len(cols)}) ---")
                print(repr(line_nl[:300]))
            shown += 1
print(f"Total lines with {want} cols: {shown}")
