#!/usr/bin/env python3
"""Validate a generated persona directory (soul.md, style.md, sources.md).

Usage:
    python3 validate_persona.py <persona-dir> [--strict] [--lenient] [--json] [--allow-conditional]

No third-party dependencies. Exit code 0 if no errors, 1 otherwise.
--strict turns evidence-landing and section-level source-usage findings into errors.
--json prints a machine-readable report (same exit code).
--allow-conditional permits a CONDITIONAL result (70-84, no critical failure) after
the user has explicitly accepted the remaining gaps. Without it, CONDITIONAL fails.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOUL_REQUIRED = [
    "## 1. 人格核心",
    "## 2. 身份与经历",
    "## 3. 动机与决策",
    "## 4. 关系图谱",
    "## 5. 知识与边界",
    "## 6. 情绪与表达内核",
    "## 7. 正向人格提示词",
    "## 8. 负向人格提示词",
]
STYLE_REQUIRED = [
    "## 1. 语言指纹",
    "## 2. 分场景语体",
    "## 3. 官方台词语料",
    "## 4. 示例对话",
    "## 5. 正向风格提示词",
    "## 6. 负向风格提示词",
]
SOURCES_REQUIRED = [
    "## 3. 来源清单",
    "## 4. 原文证据摘录",
    "## 5. 推断与置信度",
    "## 6. 冲突与裁决",
    "## 7. 来源覆盖矩阵",
    "## 8. 自检报告",
]
ALLOWED_GAMES = {"原神", "崩坏星穹铁道", "绝区零", "鸣潮"}
ALLOWED_USERS = {"旅行者", "开拓者", "绳匠", "漂泊者"}
EXPECTED_USER = {"原神": "旅行者", "崩坏星穹铁道": "开拓者", "绝区零": "绳匠", "鸣潮": "漂泊者"}
ALLOWED_DEPTHS = {"quick", "standard", "deep"}
ALLOWED_RESULTS = {"PASS", "CONDITIONAL", "FAIL"}
ID_RE = re.compile(r"\[(S|E|I|C)(\d{2,})\]")
DEF_RE = re.compile(r"^\|\s*\[(S|E|I|C)(\d{2,})\]\s*\|", re.MULTILINE)
CORE_RE = re.compile(r"<!--\s*CORE START\s*-->(.*?)<!--\s*CORE END\s*-->", re.DOTALL)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

LIMITS = {
    "quick": {"soul": 2500, "style": 2000, "total": 4000},
    "standard": {"soul": 4500, "style": 3500, "total": 8000},
    "deep": {"soul": 6000, "style": 5000, "total": 12000},
}
SOURCE_LIMITS = {"quick": 10, "standard": 25, "deep": 50}
EVIDENCE_RANGES = {"quick": (8, 15), "standard": (20, 40), "deep": (40, 80)}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    # Minimal YAML subset: single-line scalars, quoted scalars, inline/block
    # lists, folded/literal blocks, and one level of nested keys (flattened).
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    data: dict[str, str] = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.lstrip().startswith("#"):
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in ("|", ">", "|-", ">-"):
            i += 1
            chunks: list[str] = []
            while i < len(lines) and (lines[i].startswith((" ", "\t"))):
                chunks.append(lines[i].strip())
                i += 1
            sep = "\n" if value.startswith("|") else " "
            data[key] = sep.join(chunks)
            continue
        if value == "":
            items: list[str] = []
            nested: dict[str, str] = {}
            j = i + 1
            while j < len(lines) and (lines[j].startswith((" ", "\t"))):
                stripped = lines[j].strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip().strip('"').strip("'"))
                elif ":" in stripped:
                    nkey, nvalue = stripped.split(":", 1)
                    nested[nkey.strip()] = nvalue.strip().strip('"').strip("'")
                j += 1
            if items:
                data[key] = ", ".join(items)
                i = j
                continue
            if nested:
                data.update(nested)
                i = j
                continue
        data[key] = value.strip('"').strip("'")
        i += 1
    return data, text[end + 4 :]


def cjk_count(text: str) -> int:
    return len(CJK_RE.findall(text))


QUOTE_PAIRS = {"“": "”", "「": "」", "『": "』"}


def extract_quotes(text: str) -> list[str]:
    """Extract Chinese-quoted spans, including nested corner quotes.

    Returns the inner text without the outermost delimiters. This replaces the
    old flat regex, which truncated at the first inner closing quote.
    """
    quotes: list[str] = []
    stack: list[tuple[str, int]] = []
    for index, char in enumerate(text):
        if char in QUOTE_PAIRS:
            stack.append((char, index))
            continue
        if char in {"”", "」", "』"} and stack:
            opener, start = stack[-1]
            if QUOTE_PAIRS.get(opener) == char:
                stack.pop()
                if not stack:
                    quotes.append(text[start + 1 : index])
    return quotes


def get_core(text: str) -> str:
    match = CORE_RE.search(text)
    return match.group(1) if match else ""


def heading_refs(text: str) -> set[str]:
    refs = set(
        re.findall(
            r"^#{2,3}\s+([0-9]+(?:\.[0-9]+)?)\.?(?:\s|$)", text, re.MULTILINE
        )
    )
    refs.update("附录" + x for x in re.findall(r"^#{2,3}\s+附录\s*([A-Z])", text, re.MULTILINE))
    refs.update(
        f"{a}.{b}"
        for a, b in re.findall(r"^###\s+([A-Z])\.([0-9]+)", text, re.MULTILINE)
    )
    return refs


def chapter_refs(body: str) -> list[tuple[str, str, int]]:
    refs: list[tuple[str, str, int]] = []
    num = r"[0-9]{1,2}(?:\.[0-9]+)?(?![0-9.])"
    for lineno, line in enumerate(body.splitlines(), 1):
        for doc in ("soul", "style"):
            pattern = re.compile(
                r"\b" + doc + r"\s+(" + num + r"(?:\s*[、/／，,]\s*" + num + r")*)"
            )
            for match in pattern.finditer(line):
                for part in re.split(r"[、/／，,]\s*", match.group(1)):
                    refs.append((doc, part.strip(), lineno))
            for match in re.finditer(rf"\b{doc}\s+附录\s*([A-Z])", line):
                refs.append((doc, "附录" + match.group(1), lineno))
        for match in re.finditer(r"附录\s*([A-Z])", line):
            refs.append(("either", "附录" + match.group(1), lineno))
    return refs


def source_levels(body: str) -> dict[str, str]:
    levels: dict[str, str] = {}
    for line in body.splitlines():
        match = re.match(r"^\|\s*\[(S\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        levels[match.group(1)] = parts[5].upper() if len(parts) >= 6 else ""
    return levels


def probe_scores(body: str) -> list[int]:
    if "### 8.3" not in body:
        return []
    section = body.split("### 8.3", 1)[1].split("### 8.4", 1)[0]
    scores: list[int] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5 or not re.fullmatch(r"\d{1,2}", parts[0]):
            continue
        if re.fullmatch(r"[1-5]", parts[4]):
            scores.append(int(parts[4]))
    return scores


def adversarial_scores(body: str) -> dict[int, int]:
    if "### 8.7" not in body:
        return {}
    section = body.split("### 8.7", 1)[1].split("\n## ", 1)[0]
    score_idx: int | None = None
    for line in section.splitlines():
        if line.strip().startswith("|") and "得分" in line:
            header = [part.strip() for part in line.strip().strip("|").split("|")]
            for index, cell in enumerate(header):
                if "得分" in cell:
                    score_idx = index
                    break
            break
    scores: dict[int, int] = {}
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if not parts or not re.fullmatch(r"\d{1,2}", parts[0]):
            continue
        number = int(parts[0])
        if score_idx is not None and len(parts) > score_idx:
            if re.fullmatch(r"[1-5]", parts[score_idx]):
                scores[number] = int(parts[score_idx])
    return scores


def parse_sections(text: str) -> tuple[dict[str, str], dict[str, str]]:
    top: dict[str, str] = {}
    subs: dict[str, str] = {}
    parts = re.split(r"(?m)^(## .+)$", text)
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1]
        key = None
        match = re.match(r"##\s+([0-9]+)\.", title)
        if match:
            key = match.group(1)
        else:
            match = re.match(r"##\s+附录\s*([A-Z])", title)
            if match:
                key = "附录" + match.group(1)
        if not key:
            continue
        top[key] = body
        subparts = re.split(r"(?m)^(### .+)$", body)
        for j in range(1, len(subparts), 2):
            stitle = subparts[j].strip()
            sbody = subparts[j + 1]
            smatch = re.match(r"###\s+([0-9]+\.[0-9]+)", stitle)
            if not smatch:
                smatch = re.match(r"###\s+([A-Z]\.[0-9]+)", stitle)
            if smatch:
                subs[smatch.group(1)] = sbody
    return top, subs


def evidence_sources(body: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in body.splitlines():
        match = re.match(r"^\|\s*\[(E\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 4:
            continue
        source = re.search(r"\[(S\d{2,})\]", parts[3])
        if source:
            mapping[match.group(1)] = source.group(1)
    return mapping


def inference_sources(body: str, e2s: dict[str, str]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for line in body.splitlines():
        match = re.match(r"^\|\s*\[(I\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 4:
            continue
        basis = " ".join(parts[2:4])
        sources = {
            e2s[e] for e in re.findall(r"\[(E\d{2,})\]", basis) if e in e2s
        }
        if sources:
            mapping[match.group(1)] = sources
    return mapping


def section_sources(
    body: str, e2s: dict[str, str], i2s: dict[str, set[str]]
) -> set[str]:
    sources = set(re.findall(r"\[(S\d{2,})\]", body))
    for evidence in re.findall(r"\[(E\d{2,})\]", body):
        if evidence in e2s:
            sources.add(e2s[evidence])
    for inference in re.findall(r"\[(I\d{2,})\]", body):
        sources |= i2s.get(inference, set())
    return sources


def quoted_evidence_map(body: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in body.splitlines():
        match = re.match(r"^\|\s*\[(E\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 2:
            continue
        quote = extract_quotes(parts[1])
        if quote:
            mapping[match.group(1)] = re.sub(r"\s+", "", quote[0])
    return mapping


def validate_evidence_text_consistency(
    style_body: str, sources_body: str
) -> list[str]:
    sources = quoted_evidence_map(sources_body)
    style = quoted_evidence_map(style_body)
    errors: list[str] = []
    for evidence, quote in style.items():
        if evidence in sources and quote != sources[evidence]:
            errors.append(
                f"style.md: {evidence} 的原文与 sources.md §4 不一致；E 编号只能有一个原文"
            )
    return errors


def validate_evidence_landing(
    soul_text: str, style_text: str, sources_body: str
) -> list[str]:
    errors: list[str] = []
    soul_top, soul_subs = parse_sections(soul_text)
    style_top, style_subs = parse_sections(style_text)
    tops = {"soul": soul_top, "style": style_top}
    subs = {"soul": soul_subs, "style": style_subs}
    for line in sources_body.splitlines():
        match = re.match(r"^\|\s*\[(E\d{2,})\]\s*\|", line)
        if not match:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 5:
            continue
        cell = parts[4]
        for doc, num, _ in chapter_refs(cell):
            if doc in ("soul", "style"):
                body = tops[doc].get(num) or subs[doc].get(num)
                if body is None:
                    errors.append(
                        f"sources.md: {match.group(1)} 标注用于 {doc} {num}，"
                        f"但 {doc}.md 中不存在该章节"
                    )
                    continue
                if f"[{match.group(1)}]" not in body:
                    errors.append(
                        f"sources.md: {match.group(1)} 标注用于 {doc} {num}，"
                        f"但该章节未引用 {match.group(1)}"
                    )
            else:
                if (
                    f"[{match.group(1)}]" not in soul_top.get(num, "")
                    and f"[{match.group(1)}]" not in style_top.get(num, "")
                ):
                    errors.append(
                        f"sources.md: {match.group(1)} 标注用于 {num}，"
                        f"但 soul/style 附录都未引用 {match.group(1)}"
                    )
    return errors


def validate_matrix_usage(
    soul_text: str, style_text: str, sources_body: str
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    e2s = evidence_sources(sources_body)
    i2s = inference_sources(sources_body, e2s)
    soul_top, _ = parse_sections(soul_text)
    style_top, _ = parse_sections(style_text)
    actual: dict[str, set[str]] = {}
    for doc, top in (("soul", soul_top), ("style", style_top)):
        for num, body in top.items():
            if not num.startswith("附录"):
                actual[f"{doc} {num}"] = section_sources(body, e2s, i2s)
    levels = source_levels(sources_body)
    for row_no, parts in coverage_rows(sources_body):
        chapter, support, status = parts[0], parts[2], parts[5]
        match = re.match(r"^((?:soul|style)\s+[0-9]+(?:\.[0-9]+)?)", chapter)
        if not match:
            continue
        key = match.group(1)
        lookup = key
        if lookup not in actual:
            major = re.match(r"^((?:soul|style)\s+[0-9]+)", key)
            if major:
                lookup = major.group(1)
        if lookup not in actual:
            continue
        listed = set(re.findall(r"\[(S\d{2,})\]", support))
        actual_sources = actual[lookup]
        ghost_s1 = {
            source
            for source in listed
            if levels.get(source) == "S1" and source not in actual_sources
        }
        missing_s1 = {
            source
            for source in actual_sources
            if levels.get(source) == "S1" and source not in listed
        }
        for source in sorted(ghost_s1):
            errors.append(
                f"sources.md §7「{key}」：列出 S1 {source}，但该章节实际未使用"
            )
        for source in sorted(missing_s1):
            warnings.append(
                f"sources.md §7「{key}」：章节实际使用 {source}，但矩阵未列"
            )
        for source in sorted(actual_sources - listed):
            if levels.get(source) != "S1":
                warnings.append(
                    f"sources.md §7「{key}」：章节实际使用 {source}，但矩阵未列"
                )
    return errors, warnings


def section_between(body: str, start: str, end: str) -> str:
    if start not in body:
        return ""
    part = body.split(start, 1)[1]
    if end in part:
        part = part.split(end, 1)[0]
    return part


def validate_soul_structure(
    soul_core: str, strict_mode: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    def issue(msg: str) -> None:
        (errors if strict_mode else warnings).append(msg)

    if "判断顺序" not in soul_core and "四步判断" not in soul_core:
        issue("soul.md: 缺少“回应前的判断顺序”")

    if "### 8.1" in soul_core:
        section = re.split(r"(?m)^### ", soul_core.split("### 8.1", 1)[1], maxsplit=1)[0]
        rows = [line for line in section.splitlines() if line.strip().startswith("|")]
        if max(0, len(rows) - 2) < 3:
            issue("soul.md: 角色专属伪人格少于 3 个")
    else:
        issue("soul.md: 缺少角色专属伪人格清单（8.1）")

    if "### 1.2" in soul_core:
        section = re.split(r"(?m)^### ", soul_core.split("### 1.2", 1)[1], maxsplit=1)[0]
        tensions = len(re.findall(r"^#### ", section, re.MULTILINE))
        if tensions < 3:
            issue("soul.md: 人格张力对少于 3 组")
    else:
        issue("soul.md: 缺少人格张力速写（1.2）")

    return errors, warnings


def validate_style_examples(
    style_core: str, strict_mode: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    def issue(msg: str) -> None:
        (errors if strict_mode else warnings).append(msg)

    if "### 4.1" not in style_core:
        issue("style.md: 缺少 §4 示例对话")
        return errors, warnings

    blocks = re.split(r"(?m)^### 4\.[0-9]+.*$", style_core)[1:]
    for index, block in enumerate(blocks, 1):
        if "结构注记" not in block:
            issue(f"style.md: §4.{index} 缺少“结构注记”")
        if "一句示范" not in block:
            issue(f"style.md: §4.{index} 缺少“一句示范”")
            continue
        match = re.search(r"一句示范\**\s*[：:]\s*[“\"]([^”\"]+)[”\"]", block)
        if not match:
            issue(f"style.md: §4.{index} 的“一句示范”没有引号内的示范句")
            continue
        demo_cjk = len(re.findall(r"[\u4e00-\u9fff]", match.group(1)))
        if demo_cjk > 12:
            issue(f"style.md: §4.{index} 示范句 {demo_cjk} 字，超过 12 字")
    return errors, warnings


def validate_source_heuristics(
    source_rows: list[str],
    soul_fm: dict[str, str],
    style_fm: dict[str, str],
    sources_fm: dict[str, str],
) -> list[str]:
    warnings: list[str] = []
    for line in source_rows:
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue
        sid, url, level = parts[0], parts[2], parts[5].upper()
        if "bilibili.com" in url:
            continue
        expected = None
        if any(
            domain in url
            for domain in ("biligame.com", "fandom.com", "moegirl.org.cn", "huijiwiki.com", "wuther.in")
        ):
            expected = "S3"
        elif (
            any(domain in url for domain in ("wiki.hoyolab.com", "wiki.kurobbs.com", "baike.mihoyo.com"))
            or ("bbs.mihoyo.com" in url and "wiki" in url)
        ):
            expected = "S2"
        elif any(
            domain in url
            for domain in ("mihoyo.com", "hoyoverse.com", "kurogames.com", "kurobbs.com")
        ):
            expected = "S1"
        if expected and level != expected:
            warnings.append(
                f"sources.md: {sid} 域名为 {url.split('/')[2] if '://' in url else url}，"
                f"级别 {level} 与启发式预期 {expected} 不一致"
            )
    for fm_name, fm in (
        ("soul.md", soul_fm),
        ("style.md", style_fm),
        ("sources.md", sources_fm),
    ):
        for key in ("research_date", "updated"):
            value = fm.get(key)
            if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                warnings.append(f"{fm_name}: {key} 应为 YYYY-MM-DD")
    return warnings


def validate_quote_quota(
    style_body: str, sources_body: str, strict_mode: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    def check(label: str, text: str, max_quotes: int, max_cjk: int) -> None:
        quotes = extract_quotes(text)
        cjk = sum(len(re.findall(r"[\u4e00-\u9fff]", q)) for q in quotes)
        if len(quotes) > max_quotes:
            msg = f"{label}: 引用 {len(quotes)} 条，超过上限 {max_quotes}"
            (errors if strict_mode else warnings).append(msg)
        if cjk > max_cjk:
            msg = f"{label}: 引号内中文 {cjk} 字，超过配额 {max_cjk}"
            (errors if strict_mode else warnings).append(msg)

    check(
        "style.md §3 官方台词语料",
        section_between(style_body, "## 3. 官方台词语料", "## 4."),
        30,
        1200,
    )
    check(
        "sources.md §4 原文证据",
        section_between(sources_body, "## 4. 原文证据摘录", "## 5."),
        80,
        3000,
    )
    return errors, warnings


def validate_score_consistency(
    sources_fm: dict[str, str], body: str, strict_mode: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    overall = sources_fm.get("overall_result", "")
    first = re.search(r"总分\s*(\d{1,3})\s*/\s*100", body)
    total = re.search(
        r"\|\s*\*\*合计\*\*\s*\|\s*\*\*100\*\*\s*\|\s*\*\*(\d{1,3})\*\*\s*\|",
        body,
    )
    scores = []
    if first:
        scores.append(int(first.group(1)))
    if total:
        scores.append(int(total.group(1)))
    if len(scores) == 2 and scores[0] != scores[1]:
        errors.append(
            f"sources.md: §1 总分 {scores[0]} 与 §8.6 合计 {scores[1]} 不一致"
        )
    score = scores[0] if scores else None
    if score is not None:
        if overall == "PASS" and score < 85:
            errors.append(f"sources.md: overall_result=PASS，但总分 {score} < 85")
        if overall == "CONDITIONAL" and not (70 <= score <= 84):
            errors.append(
                f"sources.md: overall_result=CONDITIONAL，但总分 {score} 不在 70-84"
            )
    elif overall in {"PASS", "CONDITIONAL"}:
        msg = "sources.md: 未找到可解析的总分（/100）"
        (errors if strict_mode else warnings).append(msg)
    return errors, warnings


COVERAGE_LABELS = {
    "official": "official",
    "官方覆盖": "official",
    "partial": "partial",
    "部分覆盖": "partial",
    "community-only": "community-only",
    "community only": "community-only",
    "社区转录": "community-only",
    "derived": "derived",
    "派生": "derived",
}


def coverage_label(status: str) -> str | None:
    lowered = status.lower()
    for label, value in COVERAGE_LABELS.items():
        if label.lower() in lowered:
            return value
    return None


def coverage_rows(body: str) -> list[tuple[int, list[str]]]:
    if "## 7." not in body:
        return []
    section = body.split("## 7.", 1)[1].split("## 8.", 1)[0]
    rows: list[tuple[int, list[str]]] = []
    for lineno, line in enumerate(section.splitlines(), 1):
        if not line.strip().startswith("|") or "---" in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue
        if parts[0] in {"章节", "soul/style 章节"}:
            continue
        rows.append((lineno, parts))
    return rows


def validate_crossrefs(
    soul_body: str, style_body: str, sources_body: str, depth: str
) -> list[str]:
    errors: list[str] = []
    legal = {"soul": heading_refs(soul_body), "style": heading_refs(style_body)}

    seen: set[tuple[str, str, int]] = set()
    for doc, num, lineno in chapter_refs(sources_body):
        key = (doc, num, lineno)
        if key in seen:
            continue
        seen.add(key)
        if doc == "either":
            if num not in legal["soul"] and num not in legal["style"]:
                errors.append(f"sources.md 第 {lineno} 行：附录引用 {num} 在 soul/style 中都不存在")
        elif num not in legal[doc]:
            errors.append(f"sources.md 第 {lineno} 行：章节引用 {doc} {num} 不存在")

    levels = source_levels(sources_body)
    if not levels:
        return errors
    for sid, level in levels.items():
        if level not in {"S1", "S2", "S3", "S4"}:
            errors.append(f"sources.md：来源 {sid} 的级别 '{level}' 无效（应为 S1-S4）")

    present: set[tuple[str, str]] = set()
    for row_no, parts in coverage_rows(sources_body):
        chapter, support, official_text, community_text, status = (
            parts[0],
            parts[2],
            parts[3],
            parts[4],
            parts[5],
        )
        ids = list(dict.fromkeys(re.findall(r"\[(S\d{2,})\]", support)))
        unknown = [sid for sid in ids if sid not in levels]
        if unknown:
            errors.append(f"sources.md §7 第 {row_no} 行：引用了未定义的来源 {', '.join(unknown)}")
        official_actual = sum(1 for sid in ids if levels.get(sid) == "S1")
        community_actual = len(ids) - official_actual
        try:
            official_decl = int(official_text)
            community_decl = int(community_text)
        except ValueError:
            errors.append(f"sources.md §7 第 {row_no} 行：「官方/社区来源数量」必须是整数")
            continue
        if official_decl != official_actual:
            errors.append(
                f"sources.md §7 第 {row_no} 行「{chapter}」：官方来源数量写 {official_decl}，"
                f"实际 S1 为 {official_actual}"
            )
        if community_decl != community_actual:
            errors.append(
                f"sources.md §7 第 {row_no} 行「{chapter}」：社区来源数量写 {community_decl}，"
                f"实际非 S1 为 {community_actual}"
            )

        match = re.match(r"^(soul|style)\s+([0-9]+(?:\.[0-9]+)?)", chapter)
        if not match:
            continue
        doc, num = match.group(1), match.group(2)
        present.add((doc, num))
        present.add((doc, num.split(".")[0]))
        if num == "0" or "示例" in chapter or "附录" in chapter:
            continue
        label = coverage_label(status)
        if label in {"partial", "community-only", "derived"}:
            continue
        threshold = 2 if depth == "deep" else 1
        if official_actual < threshold:
            errors.append(
                f"sources.md §7 第 {row_no} 行「{chapter}」：S1 来源 {official_actual} 条，"
                f"低于 {depth} 要求的 {threshold} 条；如官方确实未直接覆盖，"
                f"请在覆盖状态标 partial/community-only/derived"
            )

    for doc, max_num in (("soul", 8), ("style", 6)):
        for n in range(1, max_num + 1):
            if (doc, str(n)) not in present:
                errors.append(f"sources.md §7：覆盖矩阵缺少核心章节 {doc} {n}")

    return errors


EXPLAIN_RULES = [
    ("缺少文件", "确认目录下有 soul.md、style.md、sources.md 三份文件。"),
    ("frontmatter 缺少", "对照 assets/templates 对应模板补齐该键。"),
    ("forge_version 应为", "写成三段版本号，例如 1.3.4。"),
    ("存在未替换占位符", "搜索 {{ 与 }}，用实际内容替换后删除模板注释。"),
    ("缺少章节", "从对应模板复制该章节标题和最小结构，不要只加标题。"),
    ("证据", "优先删除纯氛围证据，或把它移入 style 附录；不要硬压关键证据。"),
    ("来源", "删除低价值来源，或合并同一站点的重复条目。"),
    ("E 编号只能有一个原文", "以 sources.md §4 为准，修改 style 中的引用原文。"),
    ("标注用于", "更新 §4 的“用于章节”，或把 E 引用补进该章节。"),
    ("S1 来源", "官方确实未直接覆盖时，把覆盖状态改为 partial/community-only/derived。"),
    ("但该章节实际未使用", "从矩阵删掉该 S1，或把 S1 引用补进该章节。"),
    ("但矩阵未列", "把该来源加入 §7 对应行的支撑来源并更新计数。"),
    ("覆盖矩阵缺少核心章节", "补 soul 1–8 与 style 1–6 共 14 行。"),
    ("编号重复", "重新编号，并同步 soul/style 中所有引用。"),
    ("断链引用", "先在 sources.md §3/§4 定义该 ID，再在正文引用。"),
    ("核心区", "把关系表、场景表、时间线、完整红线移入附录；CORE 只留结论和指针。"),
    ("缺少角色专属伪人格", "在 soul §8.1 补至少 3 行角色专属错误演绎。"),
    ("人格张力对少于", "在 soul §1.2 补到至少 3 组“是 A，而不是 B”。"),
    ("示范句", "缩短为 12 字内的节奏片段，不要写成可整句复用的回复。"),
    ("OOC 探针", "补齐 12 项分数；平均 <4 或单项 ≤2 时先修规则再复测。"),
    ("对抗性探针", "补齐 10 项分数；第 1/4/5/6 项为 1 属关键失败。"),
    ("自检结论", "修完缺口后改 overall_result；CONDITIONAL 需用户明确接受。"),
]


def explain_message(message: str) -> str:
    for pattern, hint in EXPLAIN_RULES:
        if pattern in message:
            return f"{message}\n       → {hint}"
    return message


def main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print("Usage: python3 validate_persona.py <persona-dir> [--strict] [--lenient] [--json] [--allow-conditional] [--explain]")
        print("  --strict              E 引用落地、章节级来源使用、数量/预算类 warning 按错误处理")
        print("  --lenient             即使 standard/deep 也不自动 strict")
        print("  --json                输出 JSON 报告（退出码不变）")
        print("  --allow-conditional   用户已明确接受剩余缺口时，允许 CONDITIONAL(70-84) 通过")
        print("  --explain             给 ERROR/WARN 附上修复建议")
        return 0
    args = [
        arg
        for arg in sys.argv[1:]
        if arg not in ("--strict", "--lenient", "--json", "--allow-conditional", "--explain")
    ]
    strict_flag = "--strict" in sys.argv[1:]
    lenient_flag = "--lenient" in sys.argv[1:]
    json_flag = "--json" in sys.argv[1:]
    allow_conditional = "--allow-conditional" in sys.argv[1:]
    explain_flag = "--explain" in sys.argv[1:]
    if len(args) != 1:
        print("Usage: python3 validate_persona.py <persona-dir> [--strict] [--lenient] [--json] [--allow-conditional] [--explain]")
        return 1

    root = Path(args[0])
    errors: list[str] = []
    warnings: list[str] = []

    files = {name: root / name for name in ("soul.md", "style.md", "sources.md")}
    for name, path in files.items():
        if not path.is_file():
            errors.append(f"缺少文件: {name}")
    if errors:
        print_report(root, errors, warnings, {}, {}, as_json=json_flag)
        return 1

    texts = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
    fms: dict[str, dict[str, str]] = {}
    bodies: dict[str, str] = {}
    for name, text in texts.items():
        fm, body = parse_frontmatter(text)
        fms[name] = fm
        bodies[name] = body
        if not fm:
            errors.append(f"{name}: 缺少或无法解析 YAML frontmatter")
        if "{{" in text or "}}" in text:
            errors.append(f"{name}: 存在未替换的 {{{{...}}}} 占位符")
        if "TEMPLATE NOTE" in text:
            errors.append(f"{name}: 仍保留 TEMPLATE NOTE，请删除")
        if re.search(r"\bTODO\b", text, re.IGNORECASE):
            errors.append(f"{name}: 仍存在 TODO")
        if re.search(r"\[(Sxx|Exx|Ixx|Cxx)\]", text):
            errors.append(f"{name}: 仍存在未编号的示例引用（如 [Sxx]）")

    soul_fm, style_fm, sources_fm = fms["soul.md"], fms["style.md"], fms["sources.md"]
    strict_mode = (
        soul_fm.get("research_depth", "standard") in ("standard", "deep")
    ) and not lenient_flag
    if strict_flag:
        strict_mode = True
    for key in ("document", "character", "game", "version_snapshot", "research_depth", "updated", "forge_version"):
        if not soul_fm.get(key):
            errors.append(f"soul.md: frontmatter 缺少 {key}")
        if not style_fm.get(key):
            errors.append(f"style.md: frontmatter 缺少 {key}")
    for key in ("document", "character", "game", "research_depth", "research_date", "version_snapshot", "overall_result", "forge_version"):
        if not sources_fm.get(key):
            errors.append(f"sources.md: frontmatter 缺少 {key}")
    for name, fm in (("soul.md", soul_fm), ("style.md", style_fm), ("sources.md", sources_fm)):
        value = fm.get("forge_version")
        if value and not re.fullmatch(r"\d+\.\d+\.\d+", value):
            errors.append(f"{name}: forge_version 应为 X.Y.Z")

    for name, fm in (("soul.md", soul_fm), ("style.md", style_fm), ("sources.md", sources_fm)):
        if fm.get("document") and fm["document"] != name.split(".")[0]:
            errors.append(f"{name}: document 应为 {name.split('.')[0]}")
        if fm.get("game") and fm["game"] not in ALLOWED_GAMES:
            errors.append(f"{name}: 不支持的游戏名 '{fm['game']}'")
        if fm.get("research_depth") and fm["research_depth"] not in ALLOWED_DEPTHS:
            errors.append(f"{name}: research_depth 必须是 quick/standard/deep")

    if soul_fm.get("source_policy") != "official-first":
        errors.append("soul.md: source_policy 必须是 official-first")
    if soul_fm.get("primary_language") != "zh-CN":
        errors.append("soul.md: primary_language 必须是 zh-CN")
    if soul_fm.get("content_rating") != "全年龄+轻度浪漫":
        errors.append("soul.md: content_rating 必须是 全年龄+轻度浪漫")
    if soul_fm.get("target_user") not in ALLOWED_USERS:
        errors.append("soul.md: target_user 必须是 旅行者/开拓者/绳匠/漂泊者")
    expected = EXPECTED_USER.get(soul_fm.get("game", ""))
    if expected and soul_fm.get("target_user") != expected:
        errors.append(f"soul.md: 游戏「{soul_fm.get('game')}」的主角称号应为「{expected}」")
    if style_fm.get("primary_language") != "zh-CN":
        errors.append("style.md: primary_language 必须是 zh-CN")
    if sources_fm.get("overall_result") not in ALLOWED_RESULTS:
        errors.append("sources.md: overall_result 必须是 PASS/CONDITIONAL/FAIL")
    elif sources_fm["overall_result"] == "FAIL":
        errors.append("sources.md: 自检结论为 FAIL，修复后再交付")
    elif (
        sources_fm["overall_result"] == "CONDITIONAL"
        and not allow_conditional
    ):
        errors.append(
            "sources.md: 自检结论为 CONDITIONAL；用户明确接受剩余缺口后加 --allow-conditional 才可交付"
        )

    char = soul_fm.get("character")
    game = soul_fm.get("game")
    for name, fm in (("style.md", style_fm), ("sources.md", sources_fm)):
        if fm.get("character") != char:
            errors.append(f"{name}: character 与 soul.md 不一致")
        if fm.get("game") != game:
            errors.append(f"{name}: game 与 soul.md 不一致")

    for name, required in (
        ("soul.md", SOUL_REQUIRED),
        ("style.md", STYLE_REQUIRED),
        ("sources.md", SOURCES_REQUIRED),
    ):
        for heading in required:
            if heading not in bodies[name]:
                errors.append(f"{name}: 缺少章节 {heading}")
    for name in ("soul.md", "style.md"):
        if "<!-- CORE START -->" not in texts[name] or "<!-- APPENDIX START -->" not in texts[name]:
            errors.append(f"{name}: 缺少 CORE/APPENDIX 分区标记")
        if "出戏" not in texts[name] and name == "soul.md":
            errors.append("soul.md: 未写出戏开关")
        if "剧透" not in texts[name] and name == "soul.md":
            errors.append("soul.md: 未写剧透闸门")
        if "人格张力" not in bodies["soul.md"] and name == "soul.md":
            errors.append("soul.md: 未写人格张力速写")
        if "伪人格" not in bodies["soul.md"] and name == "soul.md":
            errors.append("soul.md: 未写角色专属伪人格清单")
        if "记忆边界" not in bodies["soul.md"] and name == "soul.md":
            errors.append("soul.md: 未写记忆边界")
    if "OOC 探针" not in bodies["sources.md"]:
        errors.append("sources.md: 缺少 OOC 探针测试")

    scores = probe_scores(bodies["sources.md"])
    probe_section = ""
    if "### 8.3" in bodies["sources.md"]:
        probe_section = bodies["sources.md"].split("### 8.3", 1)[1].split("### 8.4", 1)[0]
    probe_rows = re.findall(r"^\|\s*(\d{1,2})\s*\|", probe_section, re.MULTILINE)
    if len(scores) >= 12:
        average = sum(scores) / len(scores)
        if average < 4.0:
            errors.append(f"sources.md: OOC 探针平均 {average:.2f}，低于 4.0")
        if min(scores) <= 2:
            errors.append(f"sources.md: OOC 探针存在 ≤2 分（最低 {min(scores)}）")
    else:
        msg = f"sources.md: 只解析到 {len(scores)}/12 个合法探针分数"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)

    all_ids = [f"{a}{b}" for a, b in DEF_RE.findall(bodies["sources.md"])]
    defined = set(all_ids)
    id_dup = sorted({i for i in all_ids if all_ids.count(i) > 1})
    if id_dup:
        errors.append(f"sources.md: 来源/证据编号重复 {', '.join(id_dup)}")
    if not defined:
        errors.append("sources.md: 未发现任何来源/证据定义行（如 | [S01] | ... |）")

    refs: set[str] = set()
    for name in ("soul.md", "style.md"):
        for a, b in ID_RE.findall(bodies[name]):
            refs.add(f"{a}{b}")
    missing = sorted(refs - defined)
    if missing:
        errors.append("断链引用（sources.md 中不存在）: " + ", ".join(missing))

    if not re.search(r"\[(S|I)\d{2,}\]", bodies["soul.md"]):
        errors.append("soul.md: 没有任何来源或推断引用")
    if not re.search(r"\[E\d{2,}\]", bodies["style.md"]):
        errors.append("style.md: 没有任何官方台词证据引用")

    if not probe_section:
        errors.append("sources.md: 缺少 ### 8.3 OOC 探针测试")
    elif len(set(probe_rows)) < 12:
        msg = f"sources.md: OOC 探针只找到 {len(set(probe_rows))}/12 行"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)

    if "### 8.7" not in bodies["sources.md"]:
        msg = "sources.md: 缺少 ### 8.7 对抗性探针记录"
        (errors if strict_mode else warnings).append(msg)
    else:
        adv = adversarial_scores(bodies["sources.md"])
        missing_adv = sorted(set(range(1, 11)) - set(adv))
        if missing_adv:
            msg = (
                "sources.md: §8.7 缺少或无法解析第 "
                + ", ".join(str(n) for n in missing_adv)
                + " 项分数（需 10 项 1-5）"
            )
            (errors if strict_mode else warnings).append(msg)
        else:
            adv_avg = sum(adv.values()) / len(adv)
            if adv_avg < 4.0:
                errors.append(f"sources.md: 对抗性探针平均 {adv_avg:.2f}，低于 4.0")
            if min(adv.values()) <= 2:
                errors.append(
                    f"sources.md: 对抗性探针存在 ≤2 分（最低 {min(adv.values())}）"
                )
            for number in (1, 4, 5, 6):
                if adv.get(number) == 1:
                    errors.append(
                        f"sources.md: 对抗性探针第 {number} 项为 1 分（关键失败）"
                    )

    if "总分" not in bodies["sources.md"] or "/100" not in bodies["sources.md"]:
        warnings.append("sources.md: 未找到总分 /100")

    source_rows = [line for line in bodies["sources.md"].splitlines() if re.match(r"^\|\s*\[S\d{2,}\]\s*\|", line)]
    evidence_rows = [line for line in bodies["sources.md"].splitlines() if re.match(r"^\|\s*\[E\d{2,}\]\s*\|", line)]
    if not source_rows:
        errors.append("sources.md: 来源清单为空")
    if not evidence_rows:
        errors.append("sources.md: 证据摘录为空")
    if source_rows and not any("S1" in row for row in source_rows):
        msg = "sources.md: 未发现 S1 官方一手来源"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)
    if source_rows and not all("http" in row for row in source_rows):
        msg = "sources.md: 部分来源行没有 http(s) URL"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)

    try:
        declared_sources = int(sources_fm.get("source_count", "0"))
        declared_evidence = int(sources_fm.get("evidence_count", "0"))
        if declared_sources and declared_sources != len(source_rows):
            msg = f"sources.md: source_count={declared_sources} 与实际来源行 {len(source_rows)} 不一致"
            if strict_mode:
                errors.append(msg)
            else:
                warnings.append(msg)
        if declared_evidence and declared_evidence != len(evidence_rows):
            msg = f"sources.md: evidence_count={declared_evidence} 与实际证据行 {len(evidence_rows)} 不一致"
            if strict_mode:
                errors.append(msg)
            else:
                warnings.append(msg)
    except ValueError:
        msg = "sources.md: source_count/evidence_count 不是整数"
        (errors if strict_mode else warnings).append(msg)

    depth = soul_fm.get("research_depth", "standard")
    strict = strict_mode
    source_limit = SOURCE_LIMITS.get(depth, SOURCE_LIMITS["standard"])
    if len(source_rows) > source_limit:
        errors.append(
            f"sources.md: 来源 {len(source_rows)} 个，超过 {depth} 上限 {source_limit}"
        )
    evidence_min, evidence_max = EVIDENCE_RANGES.get(
        depth, EVIDENCE_RANGES["standard"]
    )
    if not (evidence_min <= len(evidence_rows) <= evidence_max):
        errors.append(
            f"sources.md: 证据 {len(evidence_rows)} 条，应为 {evidence_min}-{evidence_max} 条（{depth}）"
        )
    errors.extend(
        validate_crossrefs(
            bodies["soul.md"], bodies["style.md"], bodies["sources.md"], depth
        )
    )
    landing_errors = validate_evidence_landing(
        bodies["soul.md"], bodies["style.md"], bodies["sources.md"]
    )
    text_errors = validate_evidence_text_consistency(
        bodies["style.md"], bodies["sources.md"]
    )
    if strict:
        errors.extend(text_errors)
    else:
        warnings.extend(text_errors)
    matrix_errors, matrix_warnings = validate_matrix_usage(
        bodies["soul.md"], bodies["style.md"], bodies["sources.md"]
    )
    if strict:
        errors.extend(landing_errors)
        errors.extend(matrix_errors)
    else:
        warnings.extend(landing_errors)
        warnings.extend(matrix_errors)
    warnings.extend(matrix_warnings)
    score_errors, score_warnings = validate_score_consistency(
        sources_fm, bodies["sources.md"], strict_mode
    )
    errors.extend(score_errors)
    warnings.extend(score_warnings)
    quote_errors, quote_warnings = validate_quote_quota(
        bodies["style.md"], bodies["sources.md"], strict_mode
    )
    errors.extend(quote_errors)
    warnings.extend(quote_warnings)
    soul_struct_errors, soul_struct_warnings = validate_soul_structure(
        get_core(texts["soul.md"]), strict_mode
    )
    style_struct_errors, style_struct_warnings = validate_style_examples(
        get_core(texts["style.md"]), strict_mode
    )
    errors.extend(soul_struct_errors)
    warnings.extend(soul_struct_warnings)
    errors.extend(style_struct_errors)
    warnings.extend(style_struct_warnings)
    warnings.extend(
        validate_source_heuristics(source_rows, soul_fm, style_fm, sources_fm)
    )
    if re.search(r"\[(S|E|I|C)\d\]", bodies["sources.md"]):
        warnings.append("sources.md: 存在一位数编号；请统一为两位（如 S01）")
    limits = LIMITS.get(depth, LIMITS["standard"])
    soul_core_text = get_core(texts["soul.md"])
    if (
        "你不是 AI" in soul_core_text or "不是 AI 助手" in soul_core_text
    ) and "底层是 AI" not in soul_core_text:
        msg = "soul.md: 核心区出现绝对否定 AI 身份的表述；请改为身份双重性声明"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)
    negative_count = len(
        re.findall(r"^\s*(?:-\s*)?(?:\d+\.\s*)?不要", soul_core_text, re.MULTILINE)
    )
    if negative_count > 12:
        warnings.append(
            f"soul.md: 核心区有 {negative_count} 条“不要”规则，建议压缩为 3+3+5，其余移附录"
        )
    if "玩法模式" not in soul_core_text and "AU" not in soul_core_text:
        warnings.append("soul.md: 缺少玩法模式表（正典/AU/OC/旁白/用户演他角色）")
    soul_core = cjk_count(soul_core_text)
    style_core = cjk_count(get_core(texts["style.md"]))
    total_core = soul_core + style_core
    if soul_core > limits["soul"]:
        msg = f"soul.md 核心区 {soul_core} 字，超过 {depth} 预算 {limits['soul']}"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)
    if style_core > limits["style"]:
        msg = f"style.md 核心区 {style_core} 字，超过 {depth} 预算 {limits['style']}"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)
    if total_core > limits["total"]:
        msg = f"核心区合计 {total_core} 字，超过 {depth} 预算 {limits['total']}"
        if strict_mode:
            errors.append(msg)
        else:
            warnings.append(msg)

    if explain_flag:
        errors = [explain_message(item) for item in errors]
        warnings = [explain_message(item) for item in warnings]

    print_report(
        root,
        errors,
        warnings,
        {"S": len(source_rows), "E": len(evidence_rows), "I": len([x for x in defined if x.startswith("I")]), "C": len([x for x in defined if x.startswith("C")])},
        {
            "soul_core": soul_core,
            "style_core": style_core,
            "total_core": total_core,
            "depth": depth,
            "soul_chars": len(re.sub(r"\s", "", soul_core_text)),
            "style_chars": len(re.sub(r"\s", "", get_core(texts["style.md"]))),
        },
        as_json=json_flag,
    )
    return 1 if errors else 0


def print_report(
    root: Path,
    errors: list[str],
    warnings: list[str],
    counts: dict[str, int],
    sizes: dict[str, object],
    as_json: bool = False,
) -> None:
    result = "PASS" if not errors else "FAIL"
    if as_json:
        payload = {
            "persona_dir": str(root),
            "result": result,
            "exit_code": 0 if not errors else 1,
            "errors": errors,
            "warnings": warnings,
            "counts": counts,
            "sizes": {
                **sizes,
                "total_non_space": int(sizes.get("soul_chars", 0))
                + int(sizes.get("style_chars", 0)),
                "estimated_tokens": int(
                    (
                        int(sizes.get("soul_chars", 0))
                        + int(sizes.get("style_chars", 0))
                    )
                    / 1.6
                ),
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"Persona validation: {root}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN:  {item}")
    if counts:
        print(
            "Counts: "
            + f"S={counts.get('S', 0)} E={counts.get('E', 0)} "
            + f"I={counts.get('I', 0)} C={counts.get('C', 0)}"
        )
    if sizes:
        print(
            f"Core CJK chars: soul={sizes.get('soul_core', 0)} "
            f"style={sizes.get('style_core', 0)} total={sizes.get('total_core', 0)} "
            f"(depth={sizes.get('depth', 'standard')})"
        )
        if sizes.get("soul_chars"):
            total_chars = int(sizes.get("soul_chars", 0)) + int(sizes.get("style_chars", 0))
            print(
                f"Core non-space chars: soul={sizes.get('soul_chars', 0)} "
                f"style={sizes.get('style_chars', 0)} total={total_chars}"
            )
            print(f"Est. tokens (rough, informational): ~{int(total_chars / 1.6)}")
    print("Result:", result)
    if errors:
        print("Fix the ERROR items above, then rerun.")


if __name__ == "__main__":
    raise SystemExit(main())
