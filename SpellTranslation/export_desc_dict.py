# -*- coding: utf-8 -*-
from desc_dict import DESC_ZH
import os

output = 'desc_dict.tsv'
with open(output, 'w', encoding='utf-8') as f:
    f.write("description_en\tdescription_zh\n")
    for en, zh in DESC_ZH.items():
        # Replace actual newlines with literal \n
        en_clean = en.replace('\t', ' ').replace('\n', '\\n')
        zh_clean = zh.replace('\t', ' ').replace('\n', '\\n')
        f.write(f"{en_clean}\t{zh_clean}\n")

print(f"Exported {len(DESC_ZH)} entries to {output}")
