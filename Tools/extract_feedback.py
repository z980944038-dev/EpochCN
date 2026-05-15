#!/usr/bin/env python3
"""
extract_feedback.py
从玩家的 EpochCNDB SavedVariables 文件中提取反馈数据。

用法:
    python3 Tools/extract_feedback.py <SavedVariables文件路径>
    python3 Tools/extract_feedback.py <包含多个SV文件的目录>

输出:
    - 控制台打印反馈摘要
    - 生成 Tools/FEEDBACK_REPORT.md 汇总报告

示例:
    python3 Tools/extract_feedback.py ~/WoW/WTF/Account/PLAYER/SavedVariables/EpochCN.lua
    python3 Tools/extract_feedback.py ~/collected_feedback/
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime


def parse_lua_table(content: str) -> dict:
    """简易解析 Lua SavedVariables 中的 feedback 表。"""
    feedback_data = []

    # 匹配 feedback.history 中的条目
    # 格式: { type = "...", content = "...", context = "...", version = "...", ... }
    pattern = re.compile(
        r'\{\s*'
        r'(?:.*?)'
        r'\["type"\]\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\["content"\]\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\["version"\]\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\["player"\]\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\["zone"\]\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\}',
        re.DOTALL
    )

    # 也尝试另一种格式 (key = value 而非 ["key"] = value)
    pattern2 = re.compile(
        r'\{\s*'
        r'(?:.*?)'
        r'type\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'content\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'version\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'player\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'zone\s*=\s*"([^"]*)"'
        r'(?:.*?)'
        r'\}',
        re.DOTALL
    )

    # 先找到 feedback 区域
    fb_match = re.search(r'\["feedback"\]\s*=\s*\{(.*?)\n\t\}', content, re.DOTALL)
    if not fb_match:
        fb_match = re.search(r'feedback\s*=\s*\{(.*?)\n\t\}', content, re.DOTALL)

    if not fb_match:
        return feedback_data

    fb_section = fb_match.group(1)

    for match in pattern.finditer(fb_section):
        feedback_data.append({
            'type': match.group(1),
            'content': match.group(2),
            'version': match.group(3),
            'player': match.group(4),
            'zone': match.group(5),
        })

    if not feedback_data:
        for match in pattern2.finditer(fb_section):
            feedback_data.append({
                'type': match.group(1),
                'content': match.group(2),
                'version': match.group(3),
                'player': match.group(4),
                'zone': match.group(5),
            })

    return feedback_data


def process_file(filepath: str) -> list:
    """处理单个 SavedVariables 文件。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, UnicodeDecodeError) as e:
        print(f"  警告: 无法读取 {filepath}: {e}")
        return []

    return parse_lua_table(content)


def generate_report(all_feedback: list, output_path: str):
    """生成 Markdown 格式的反馈汇总报告。"""
    type_labels = {
        'translation': '翻译错误',
        'missing': '缺失翻译',
        'bug': 'Bug 报告',
        'suggestion': '功能建议',
        'other': '其他',
    }

    # 按类型分组
    by_type = {}
    for fb in all_feedback:
        t = fb.get('type', 'other')
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(fb)

    lines = []
    lines.append("# EpochCN 用户反馈汇总报告")
    lines.append("")
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**总反馈数:** {len(all_feedback)}")
    lines.append("")

    # 统计
    lines.append("## 统计")
    lines.append("")
    lines.append("| 类型 | 数量 |")
    lines.append("|------|------|")
    for t in ['translation', 'missing', 'bug', 'suggestion', 'other']:
        count = len(by_type.get(t, []))
        if count > 0:
            lines.append(f"| {type_labels.get(t, t)} | {count} |")
    lines.append("")

    # 详细内容
    for t in ['bug', 'translation', 'missing', 'suggestion', 'other']:
        items = by_type.get(t, [])
        if not items:
            continue
        lines.append(f"## {type_labels.get(t, t)} ({len(items)} 条)")
        lines.append("")
        for i, fb in enumerate(items, 1):
            lines.append(f"### #{i}")
            lines.append(f"- **玩家:** {fb.get('player', '?')}")
            lines.append(f"- **版本:** {fb.get('version', '?')}")
            lines.append(f"- **区域:** {fb.get('zone', '')}")
            lines.append("")
            lines.append(f"> {fb.get('content', '')}")
            lines.append("")

    report = "\n".join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return report


def main():
    if len(sys.argv) < 2:
        print("用法: python3 Tools/extract_feedback.py <SavedVariables文件或目录>")
        print("")
        print("示例:")
        print("  python3 Tools/extract_feedback.py path/to/EpochCN.lua")
        print("  python3 Tools/extract_feedback.py path/to/collected_svs/")
        sys.exit(1)

    target = sys.argv[1]
    all_feedback = []

    if os.path.isfile(target):
        print(f"处理文件: {target}")
        feedback = process_file(target)
        all_feedback.extend(feedback)
        print(f"  提取到 {len(feedback)} 条反馈")
    elif os.path.isdir(target):
        print(f"扫描目录: {target}")
        for root, dirs, files in os.walk(target):
            for fname in files:
                if fname.endswith('.lua') and 'EpochCN' in fname:
                    filepath = os.path.join(root, fname)
                    print(f"  处理: {filepath}")
                    feedback = process_file(filepath)
                    all_feedback.extend(feedback)
                    print(f"    提取到 {len(feedback)} 条反馈")
    else:
        print(f"错误: {target} 不存在")
        sys.exit(1)

    if not all_feedback:
        print("\n未找到任何反馈数据。")
        sys.exit(0)

    # 生成报告
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "FEEDBACK_REPORT.md")
    report = generate_report(all_feedback, output_path)

    print(f"\n=== 汇总 ===")
    print(f"总反馈数: {len(all_feedback)}")
    type_labels = {
        'translation': '翻译错误', 'missing': '缺失翻译',
        'bug': 'Bug', 'suggestion': '建议', 'other': '其他'
    }
    for t in ['bug', 'translation', 'missing', 'suggestion', 'other']:
        count = sum(1 for fb in all_feedback if fb.get('type') == t)
        if count > 0:
            print(f"  {type_labels.get(t, t)}: {count}")

    print(f"\n报告已生成: {output_path}")


if __name__ == "__main__":
    main()
