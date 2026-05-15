#!/usr/bin/env python3
"""
FrameXMLStrings 翻译补全脚本。
添加缺失的常用 UI 字符串翻译。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

# New translations to add - focusing on player-visible strings
# Excluding SLASH_ (command aliases), VOICEMACRO_ (voice lines), format-only strings
NEW_TRANSLATIONS = {
    # Key names
    "KEY_DELETE": "删除",
    "KEY_DELETE_MAC": "删除",
    "KEY_END": "End",
    "KEY_ESCAPE": "Esc",
    "KEY_HOME": "Home",
    "KEY_INSERT": "插入",
    "KEY_NUMLOCK": "数字锁定",
    "KEY_PAGEDOWN": "下一页",
    "KEY_PAGEUP": "上一页",
    "KEY_PRINTSCREEN": "截图",
    "KEY_SCROLLLOCK": "滚动锁定",
    "KEY_SPACE": "空格",
    "KEY_TAB": "Tab",
    # Time
    "TIMEMANAGER_AM": "上午",
    "TIMEMANAGER_PM": "下午",
    # Spell
    "SPELL_FAILED_CUSTOM_ERROR_1": "发生了一些错误！",
    "SPELL_FAILED_CUSTOM_ERROR_2": "任务出了问题！",
    "SPELL_HASTE_ABBR": "急速",
    # PVP
    "PVP": "PvP",
    "PVP_ENABLED": "PvP已开启",
    "PVP_FLAG": "PvP",
    "PVP_OPTIONS": "PvP选项",
    # Friends
    "FRIENDS_LIST_WOW_TEMPLATE": "%1$s，%2$d级 %3$s",
    "FRIENDS_TOOLTIP_WOW_TOON_TEMPLATE": "%1$s，%2$s %3$s %4$s",
    # Movie/Cinematic
    "MOVIE_RECORDING_SUBTITLE": "正在录制",
    "MOVIE_SUBTITLE_ENABLED": "字幕已开启",
    # Icon tag (used in chat)
    "ICON_TAG_RAID_TARGET_STAR1": "星形",
    "ICON_TAG_RAID_TARGET_CIRCLE2": "圆形",
    "ICON_TAG_RAID_TARGET_DIAMOND3": "菱形",
    "ICON_TAG_RAID_TARGET_TRIANGLE4": "三角形",
    "ICON_TAG_RAID_TARGET_MOON5": "月亮",
    "ICON_TAG_RAID_TARGET_SQUARE6": "方形",
    "ICON_TAG_RAID_TARGET_CROSS7": "十字",
    "ICON_TAG_RAID_TARGET_SKULL8": "骷髅",
    # Error messages
    "ERR_NAME_DECLENSION_DOESNT_MATCH_BASE_NAME": "你的名字变格必须与原始名字匹配。请输入新名字。",
    "ERR_NAME_RUSSIAN_CONSECUTIVE_SILENT_CHARACTERS": "不允许连续的静音字符。请创建新名字。",
    # Additional common UI strings
    "ITEM_QUALITY0_DESC": "粗糙",
    "ITEM_QUALITY1_DESC": "普通",
    "ITEM_QUALITY2_DESC": "优秀",
    "ITEM_QUALITY3_DESC": "精良",
    "ITEM_QUALITY4_DESC": "史诗",
    "ITEM_QUALITY5_DESC": "传说",
    "ITEM_QUALITY6_DESC": "神器",
    "ITEM_QUALITY7_DESC": "传家宝",
}


def main():
    fxml_path = DATA / "FrameXMLStrings.lua"
    with open(fxml_path, encoding="utf-8") as f:
        text = f.read()

    # Parse existing entries
    existing = {}
    for m in re.finditer(r'\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.)*)"', text):
        existing[m.group(1)] = m.group(2)

    # Add new translations (only if key exists and value is English-only)
    added = 0
    updated_keys = []
    for key, new_val in NEW_TRANSLATIONS.items():
        if key in existing:
            old_val = existing[key]
            # Only update if current value is English-only or placeholder
            if not any(0x4E00 <= ord(c) <= 0x9FFF for c in old_val):
                # Replace in text
                pattern = f'["{key}"] = "{re.escape(old_val)}"'
                replacement = f'["{key}"] = "{esc(new_val)}"'
                if pattern in text:
                    text = text.replace(pattern, replacement)
                    added += 1
                    updated_keys.append(key)
                else:
                    # Try regex replacement
                    old_pattern = re.escape(f'["{key}"]') + r'\s*=\s*"' + re.escape(old_val) + '"'
                    new_replacement = f'["{key}"] = "{esc(new_val)}"'
                    new_text = re.sub(old_pattern, new_replacement, text, count=1)
                    if new_text != text:
                        text = new_text
                        added += 1
                        updated_keys.append(key)
        else:
            # Key doesn't exist yet - add it before the closing brace
            # Find the last entry and add after it
            pass  # Only update existing entries

    with open(fxml_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"=== FrameXMLStrings 补全结果 ===")
    print(f"更新条目: {added}")
    if updated_keys:
        print(f"更新的键:")
        for k in updated_keys[:20]:
            print(f"  {k}")


if __name__ == "__main__":
    main()
