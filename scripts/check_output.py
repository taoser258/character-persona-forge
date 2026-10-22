#!/usr/bin/env python3
"""Flag common OOC/assistant markers in a persona reply.

Usage:
    python3 scripts/check_output.py <file>
    echo "..." | python3 scripts/check_output.py

Exit code 0 if no flags, 1 if any flag.
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FLAGS = [
    "作为一个AI",
    "作为 AI",
    "根据设定",
    "我理解你的感受",
    "希望这能帮到你",
    "作为助手",
    "我是AI助手",
    "我是一个AI",
]


def main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print("Usage: python3 check_output.py [file]")
        print("  Reads a file, or stdin when no file is given.")
        print("  Exit 0 if no OOC markers; 1 if flags are found.")
        return 0
    if len(sys.argv) > 2:
        print("Usage: python3 check_output.py [file]")
        return 2
    if len(sys.argv) == 2:
        text = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")

    hits = [flag for flag in FLAGS if flag in text]
    ellipsis_count = text.count("……")
    if ellipsis_count > 3:
        hits.append(f"省略号 {ellipsis_count} 处（>3）")
    if "首先" in text and "其次" in text and "最后" in text:
        hits.append("首先/其次/最后 三段式")
    if text.rstrip().endswith(("总之。", "综上所述。")):
        hits.append("总结式收尾")

    if not hits:
        print("OK: no OOC markers found")
        return 0
    print("FLAG:")
    for hit in hits:
        print(f"- {hit}")
    print("建议：带身份锚重生成，或检查 style 的负向规则。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
