#!/usr/bin/env python3
"""Drafting helpers for character-persona-forge persona directories.

Usage:
    python3 persona_tools.py budget <persona-dir>
    python3 persona_tools.py evidence-map <persona-dir>
    python3 persona_tools.py matrix <persona-dir>
    python3 persona_tools.py check <persona-dir>

No third-party dependencies. These commands only read and report; they do not
rewrite soul.md, style.md, or sources.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from validate_persona import (  # noqa: E402
    LIMITS,
    chapter_refs,
    cjk_count,
    coverage_rows,
    evidence_sources,
    get_core,
    inference_sources,
    parse_frontmatter,
    parse_sections,
    section_sources,
    source_levels,
)

SOUL_STANDARD_QUOTAS = {
    "0": 600,
    "1": 850,
    "2": 450,
    "3": 450,
    "4": 500,
    "5": 550,
    "6": 400,
    "7": 250,
    "8": 450,
}
STYLE_STANDARD_QUOTAS = {
    "0": 250,
    "1": 650,
    "2": 300,
    "3": 1000,
    "4": 500,
    "5": 250,
    "6": 350,
}
SECTION_NAMES = {
    ("soul", "0"): "运行规则",
    ("soul", "1"): "人格核心",
    ("soul", "2"): "身份与经历",
    ("soul", "3"): "动机与决策",
    ("soul", "4"): "关系图谱",
    ("soul", "5"): "知识与边界",
    ("soul", "6"): "情绪与表达",
    ("soul", "7"): "正向人格提示词",
    ("soul", "8"): "负向人格提示词",
    ("style", "0"): "使用规则",
    ("style", "1"): "语言指纹",
    ("style", "2"): "分场景语体",
    ("style", "3"): "官方台词语料",
    ("style", "4"): "示例对话",
    ("style", "5"): "正向风格提示词",
    ("style", "6"): "负向风格提示词",
}


def load_persona(directory: Path):
    files = {name: directory / name for name in ("soul.md", "style.md", "sources.md")}
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise SystemExit("缺少文件: " + ", ".join(missing))
    texts = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
    frontmatter = {}
    bodies = {}
    for name, text in texts.items():
        fm, body = parse_frontmatter(text)
        frontmatter[name] = fm
        bodies[name] = body
    depth = frontmatter["soul.md"].get("research_depth", "standard")
    return texts, frontmatter, bodies, depth


def scaled_quota(base: int, depth: str, kind: str) -> int:
    standard_total = LIMITS["standard"][kind]
    total = LIMITS.get(depth, LIMITS["standard"])[kind]
    return max(50, int(round(base * total / standard_total / 10.0) * 10))


def command_budget(directory: Path) -> int:
    texts, _, _, depth = load_persona(directory)
    limits = LIMITS.get(depth, LIMITS["standard"])
    print(f"Persona budget: {directory} (depth={depth})")
    print("Note: per-section quotas are advisory; validate_persona.py enforces only total CORE budgets.")

    for doc in ("soul", "style"):
        core = get_core(texts[f"{doc}.md"])
        used = cjk_count(core)
        limit = limits[doc]
        remaining = limit - used
        mark = "OK" if remaining >= 0 else "OVER"
        print(f"{doc} core: {used}/{limit} CJK ({remaining:+d}) {mark}")
        quotas = SOUL_STANDARD_QUOTAS if doc == "soul" else STYLE_STANDARD_QUOTAS
        top, _ = parse_sections(core)
        for key in sorted(top, key=lambda value: (len(value), value)):
            used_section = cjk_count(top[key])
            base = quotas.get(key)
            if base is None:
                quota_text = "无配额"
            else:
                quota = scaled_quota(base, depth, doc)
                delta = used_section - quota
                quota_text = f"{quota} CJK ({delta:+d})"
            name = SECTION_NAMES.get((doc, key), "")
            label = f"{doc} {key} {name}".strip()
            print(f"  {label}: {used_section} CJK; advisory quota {quota_text}")
    total = cjk_count(get_core(texts["soul.md"])) + cjk_count(get_core(texts["style.md"]))
    print(f"total core: {total}/{limits['total']} CJK ({limits['total'] - total:+d})")
    return 0


def evidence_usage(soul_text: str, style_text: str) -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {}
    for doc, text in (("soul", soul_text), ("style", style_text)):
        top, subs = parse_sections(text)
        for key, body in top.items():
            for evidence in re.findall(r"\[(E\d{2,})\]", body):
                usage.setdefault(evidence, set()).add(f"{doc} {key}")
        for key, body in subs.items():
            for evidence in re.findall(r"\[(E\d{2,})\]", body):
                usage.setdefault(evidence, set()).add(f"{doc} {key}")
    return usage


def declared_usage(sources_body: str) -> dict[str, set[str]]:
    declared: dict[str, set[str]] = {}
    for line in sources_body.splitlines():
        match = re.match(r"^\|\s*\[(E\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5:
            continue
        for doc, num, _ in chapter_refs(parts[4]):
            if doc == "either":
                declared.setdefault(match.group(1), set()).add(num)
            else:
                declared.setdefault(match.group(1), set()).add(f"{doc} {num}")
    for evidence, chapters in declared.items():
        specific = {chapter for chapter in chapters if chapter.startswith(("soul ", "style "))}
        generic = chapters - specific
        for chapter in list(generic):
            if any(chapter in item for item in specific):
                chapters.remove(chapter)
    return declared


def command_evidence_map(directory: Path) -> int:
    texts, _, bodies, _ = load_persona(directory)
    usage = evidence_usage(texts["soul.md"], texts["style.md"])
    declared = declared_usage(bodies["sources.md"])
    print(f"Evidence map: {directory}")
    print("Legend: OK = every declared chapter actually cites the E; extra actual citations are informational.")

    all_ids = sorted(set(declared) | set(usage))
    for evidence in all_ids:
        declared_set = declared.get(evidence, set())
        actual_set = usage.get(evidence, set())
        missing = sorted(declared_set - actual_set)
        extra = sorted(actual_set - declared_set)
        status = "OK" if not missing else "UPDATE"
        print(f"{evidence}: {status}")
        print(f"  declared: {', '.join(sorted(declared_set)) or '-'}")
        print(f"  actual:   {', '.join(sorted(actual_set)) or '-'}")
        if missing:
            print(f"  fix: remove from §4 or add E to: {', '.join(missing)}")
        if extra:
            print(f"  info: extra citations (not required in §4): {', '.join(extra)}")
    return 0


def command_matrix(directory: Path) -> int:
    texts, _, bodies, depth = load_persona(directory)
    e2s = evidence_sources(bodies["sources.md"])
    i2s = inference_sources(bodies["sources.md"], e2s)
    levels = source_levels(bodies["sources.md"])
    threshold = 2 if depth == "deep" else 1
    print(f"Matrix stub: {directory} (depth={depth})")
    print("把“关键结论”改写为本章实际结论；支撑来源和计数可直接粘贴到 §7。")
    print()
    print("| soul/style 章节 | 关键结论 | 支撑来源 | 官方来源数量 | 社区来源数量 | 覆盖状态 |")
    print("|---|---|---|---:|---:|---|")
    for doc, max_num in (("soul", 8), ("style", 6)):
        core = get_core(texts[f"{doc}.md"])
        top, _ = parse_sections(core)
        for number in range(1, max_num + 1):
            body = top.get(str(number), "")
            sources = section_sources(body, e2s, i2s)
            ordered = sorted(
                sources,
                key=lambda value: int(re.search(r"\d+", value).group()),
            )
            support = "".join(f"[{source}]" for source in ordered)
            official = sum(1 for source in ordered if levels.get(source) == "S1")
            community = len(ordered) - official
            if official >= threshold:
                status = "达标"
            elif official > 0:
                status = "partial（部分覆盖）"
            elif ordered:
                status = "community-only（社区转录）"
            else:
                status = "待补"
            name = SECTION_NAMES.get((doc, str(number)), "")
            print(
                f"| {doc} {number} {name} | {{待填结论}} | {support or '{{待补}}'} "
                f"| {official} | {community} | {status} |"
            )
    print()
    print("注意：`derived` / `community-only` / `partial` 状态可放宽该行 S1 硬要求。")
    return 0


def command_check(directory: Path) -> int:
    print("=== BUDGET ===")
    command_budget(directory)
    print()
    print("=== EVIDENCE MAP ===")
    command_evidence_map(directory)
    print()
    print("=== MATRIX DRAFT ===")
    command_matrix(directory)
    print()
    print("下一步：python3 validate_persona.py <dir> --strict --explain")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("budget", "统计核心区与分章 CJK 配额（分章值为建议，不作为 validator 硬门禁）"),
        ("evidence-map", "对比 §4 声明的 E 落点与正文实际引用"),
        ("matrix", "根据正文实际引用生成可直接粘贴的 §7 矩阵 stub"),
        ("matrix-stub", "matrix 的别名"),
        ("check", "依次输出 budget / evidence-map / matrix"),
    ):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("persona_dir", help="包含 soul.md/style.md/sources.md 的目录")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    directory = Path(args.persona_dir)
    if not directory.is_dir():
        print(f"目录不存在: {directory}")
        return 1
    if args.command == "budget":
        return command_budget(directory)
    if args.command == "evidence-map":
        return command_evidence_map(directory)
    if args.command in ("matrix", "matrix-stub"):
        return command_matrix(directory)
    if args.command == "check":
        return command_check(directory)
    parser.error("未知命令")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
