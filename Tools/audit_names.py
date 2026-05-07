from pathlib import Path
import re


ROOT = Path(r"D:\1927\Ascension Launcher\resources\epoch-live\Interface\AddOns\EpochCN")
DATA = ROOT / "Data"
OUT = ROOT / "Tools" / "NAME_COVERAGE.md"

ROW_RE = re.compile(r'^\[(\d+)\]\s*=\s*\{\s*"((?:\\.|[^"\\])*)"', re.UNICODE)


def count_rows(path: Path) -> tuple[int, int, list[tuple[int, str]]]:
    total = 0
    english_like = 0
    samples: list[tuple[int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line.strip())
        if not match:
            continue
        total += 1
        name = match.group(2)
        if name and all(ord(ch) < 128 for ch in name):
            english_like += 1
            if len(samples) < 40:
                samples.append((int(match.group(1)), name))
    return total, english_like, samples


def main() -> None:
    item_total, item_english, item_samples = count_rows(DATA / "ItemData.lua")
    unit_total, unit_english, unit_samples = count_rows(DATA / "UnitData.lua")

    lines = [
        "# EpochCN Name Coverage",
        "",
        "| Type | Total names | English-like names |",
        "| --- | ---: | ---: |",
        f"| Items | {item_total} | {item_english} |",
        f"| NPCs / creatures | {unit_total} | {unit_english} |",
        "",
        "## Item English-Like Samples",
        "",
    ]
    lines.extend(f"- `{item_id}` {name}" for item_id, name in item_samples)
    lines.extend(["", "## Unit English-Like Samples", ""])
    lines.extend(f"- `{unit_id}` {name}" for unit_id, name in unit_samples)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
