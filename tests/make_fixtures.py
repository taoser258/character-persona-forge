#!/usr/bin/env python3
"""Regenerate negative fixtures from the standard positive example.

Usage:
    python3 tests/make_fixtures.py

The fixtures are intentionally small patches on top of the standard example so
they do not drift when the example is updated.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "assets" / "examples" / "standard" / "qingxiao"
FIXTURES = ROOT / "tests" / "fixtures"


def fresh(name: str) -> Path:
    target = FIXTURES / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(BASE, target)
    return target


def patch_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"patch anchor not found in {path}: {old[:40]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def make_missing_probe() -> None:
    target = fresh("fail_missing_probe")
    path = target / "sources.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    removed = False
    in_probes = False
    for line in lines:
        if line.startswith("### 8.3"):
            in_probes = True
        elif line.startswith("### 8.4"):
            in_probes = False
        if in_probes and not removed and line.startswith("| 12 |"):
            removed = True
            continue
        out.append(line)
    if not removed:
        raise SystemExit("probe row 12 not found")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def make_dup_id() -> None:
    target = fresh("fail_dup_id")
    path = target / "sources.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    duplicated = False
    for line in lines:
        out.append(line)
        if not duplicated and line.startswith("| [E01] |"):
            out.append(line)
            duplicated = True
    if not duplicated:
        raise SystemExit("E01 row not found")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def make_bad_identity() -> None:
    target = fresh("fail_bad_identity")
    path = target / "soul.md"
    text = path.read_text(encoding="utf-8")
    start = text.index("### 0.1 身份")
    end = text.index("### 0.2", start)
    replacement = (
        "### 0.1 身份\n"
        "你不是 AI 助手，也不是在扮演。你就是角色本人。\n\n"
    )
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def make_conditional() -> None:
    target = fresh("fail_conditional_unapproved")
    path = target / "sources.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace('overall_result: "PASS"', 'overall_result: "CONDITIONAL"', 1)
    text = text.replace("总分 92/100", "总分 80/100", 1)
    text = text.replace(
        "| **合计** | **100** | **92** | **PASS** |",
        "| **合计** | **100** | **80** | **CONDITIONAL** |",
        1,
    )
    text = text.replace("结论：PASS；总分：92/100", "结论：CONDITIONAL；总分：80/100", 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    make_missing_probe()
    make_dup_id()
    make_bad_identity()
    make_conditional()
    print("Regenerated 4 fixtures from assets/examples/standard/qingxiao")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
