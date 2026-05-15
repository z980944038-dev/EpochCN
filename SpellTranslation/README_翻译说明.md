# 法术翻译表说明

来源：`spell/Spell.dbc`，也就是从 `patch-B.MPQ` 导出的英文法术底表。

## 推荐翻译顺序
1. 先翻译 `spell_english_spellbook_priority.tsv`，这是 `SkillLineAbility.dbc` 中会进入法术书/技能书的优先集合。
2. 如果模型上下文有限，使用 `chunks_1000/spell_english_chunk_001.tsv` 这类分片文件逐批翻译。
3. 翻译结果请保留原列，并填写 `name_zh`、`rank_zh`、`description_zh`、`tooltip_zh`。

## 重要规则
- 不要翻译或删除 `$s1`、`$d`、`$o1`、`${...}`、`$lxxx:yyy;`、`|cFFFFFFFF`、`|r` 等 WoW 变量/颜色/条件标记。
- `\n` 表示游戏内换行，翻译后仍保留 `\n`。
- `rank_en` 如 `Rank 1` 翻成 `等级 1`；`Passive` 翻成 `被动`；`Racial Passive` 翻成 `种族被动`；`Summon` 翻成 `召唤`。
- 空英文可以保持中文空白。
- 如果不确定魔改技能含义，可以先直译，并在 `notes` 标注。

## 文件
- 全量 TSV：`spell_english_full_for_translation.tsv`
- 法术书优先 TSV：`spell_english_spellbook_priority.tsv`
- 全量 JSONL：`spell_english_full_for_translation.jsonl`
- 分片目录：`chunks_1000/`
