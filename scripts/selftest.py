#!/usr/bin/env python3
"""Regression test for validate_persona.py and check_output.py.

Usage:
    python3 scripts/selftest.py

No third-party dependencies. Exit code 0 if all cases pass.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_persona.py"
sys.path.insert(0, str(VALIDATOR.parent))
from validate_persona import (  # noqa: E402
    extract_quotes,
    parse_frontmatter,
    translation_map,
    validate_quote_quota,
    validate_translation_consistency,
    validate_translation_metadata,
)
from game_profile import load_packs, resolve_game, validate_pack  # noqa: E402

PERSONA_TOOLS = ROOT / "scripts" / "persona_tools.py"
PROBE_HARNESS = ROOT / "scripts" / "probe_harness.py"

CASES = [
    ("pass_standard", ROOT / "assets/examples/standard/qingxiao", 0, None),
    ("pass_quick", ROOT / "assets/examples/quick/qingxiao", 0, None),
    ("fail_missing_probe", ROOT / "tests/fixtures/fail_missing_probe", 1, "探针"),
    ("fail_dup_id", ROOT / "tests/fixtures/fail_dup_id", 1, "重复"),
    ("fail_bad_identity", ROOT / "tests/fixtures/fail_bad_identity", 1, "绝对否定 AI"),
    (
        "fail_conditional_unapproved",
        ROOT / "tests/fixtures/fail_conditional_unapproved",
        1,
        "CONDITIONAL",
    ),
    (
        "fail_depth_mismatch",
        ROOT / "tests/fixtures/fail_depth_mismatch",
        1,
        "research_depth 在三份文档中不一致",
    ),
]


def run_case(name: str, target: Path, expected_code: int, expected_text: str | None) -> bool:
    if not target.is_dir():
        print(f"FAIL {name}: fixture missing: {target}")
        return False
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(target), "--strict"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == expected_code
    if expected_text and expected_text not in output:
        ok = False
    if ok:
        print(f"PASS {name} (exit {proc.returncode})")
        return True
    print(f"FAIL {name}: expected exit {expected_code}, got {proc.returncode}")
    if expected_text and expected_text not in output:
        print(f"  expected text not found: {expected_text}")
    print("  output:")
    for line in output.splitlines()[-12:]:
        print(f"    {line}")
    return False


def run_parser_and_json_checks() -> list[bool]:
    results: list[bool] = []
    sample = (
        "---\n"
        "name: demo\n"
        "aliases:\n"
        "  - A\n"
        "  - B\n"
        "metadata:\n"
        '  version: "9.9"\n'
        "description: >-\n"
        "  line one\n"
        "  line two\n"
        "---\n"
        "body\n"
    )
    fm, body = parse_frontmatter(sample)
    ok = (
        fm.get("aliases") == "A, B"
        and fm.get("version") == "9.9"
        and fm.get("description") == "line one line two"
        and body.strip() == "body"
    )
    print(("PASS" if ok else "FAIL") + " frontmatter_parser")
    results.append(ok)

    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(ROOT / "assets/examples/standard/qingxiao"),
            "--strict",
            "--json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        payload = json.loads(proc.stdout)
        ok = (
            proc.returncode == 0
            and payload.get("result") == "PASS"
            and payload.get("exit_code") == 0
            and payload.get("errors") == []
        )
    except json.JSONDecodeError:
        ok = False
    print(("PASS" if ok else "FAIL") + " json_report")
    results.append(ok)

    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(ROOT / "tests/fixtures/fail_conditional_unapproved"),
            "--strict",
            "--allow-conditional",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0 and "Result: PASS" in (proc.stdout or "")
    print(("PASS" if ok else "FAIL") + " conditional_override")
    results.append(ok)

    bad = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_output.py")],
        input="作为一个AI，我理解你的感受。希望这能帮到你。",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    good = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_output.py")],
        input="今天的风有点吵。你刚才说什么？",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = bad.returncode == 1 and good.returncode == 0
    print(("PASS" if ok else "FAIL") + " output_guard")
    results.append(ok)

    results.extend(run_variant_checks())
    return results


def run_variant_checks() -> list[bool]:
    results: list[bool] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        conditional = tmp_path / "conditional_out_of_range"
        shutil.copytree(ROOT / "tests/fixtures/fail_conditional_unapproved", conditional)
        src = conditional / "sources.md"
        text = src.read_text(encoding="utf-8")
        text = text.replace("总分 80/100", "总分 50/100")
        text = text.replace("| **合计** | **100** | **80** |", "| **合计** | **100** | **50** |")
        src.write_text(text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(conditional), "--strict", "--allow-conditional"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "不在 70-84" in output
        print(("PASS" if ok else "FAIL") + " conditional_out_of_range")
        results.append(ok)

        bad_scores = tmp_path / "bad_probe_scores"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", bad_scores)
        src = bad_scores / "sources.md"
        lines = src.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        in_probes = False
        for line in lines:
            if line.startswith("### 8.3"):
                in_probes = True
            elif line.startswith("### 8.4"):
                in_probes = False
            if (
                in_probes
                and line.startswith("|")
                and not line.startswith("|---")
                and not line.startswith("| #")
            ):
                parts = [part.strip() for part in line.strip().strip("|").split("|")]
                if len(parts) == 6 and parts[0].isdigit():
                    parts[4] = "好"
                    line = "| " + " | ".join(parts) + " |"
            out.append(line)
        src.write_text("\n".join(out) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(bad_scores), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "合法探针分数" in output
        print(("PASS" if ok else "FAIL") + " bad_probe_scores")
        results.append(ok)

        missing_adv = tmp_path / "missing_adversarial"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", missing_adv)
        src = missing_adv / "sources.md"
        text = src.read_text(encoding="utf-8")
        start = text.index("### 8.7")
        end = text.index("## 9.", start)
        src.write_text(text[:start] + text[end:], encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(missing_adv), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "8.7" in output
        print(("PASS" if ok else "FAIL") + " missing_adversarial")
        results.append(ok)

        bad_adv = tmp_path / "bad_adversarial_scores"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", bad_adv)
        src = bad_adv / "sources.md"
        lines = src.read_text(encoding="utf-8").splitlines()
        out = []
        in_adversarial = False
        score_idx: int | None = None
        for line in lines:
            if line.startswith("### 8.7"):
                in_adversarial = True
            elif line.startswith("## 9."):
                in_adversarial = False
            if in_adversarial and line.strip().startswith("|"):
                parts = [part.strip() for part in line.strip().strip("|").split("|")]
                if score_idx is None and "得分" in line:
                    for index, cell in enumerate(parts):
                        if "得分" in cell:
                            score_idx = index
                            break
                elif (
                    score_idx is not None
                    and parts
                    and parts[0].isdigit()
                    and len(parts) > score_idx
                ):
                    parts[score_idx] = "好"
                    line = "| " + " | ".join(parts) + " |"
            out.append(line)
        src.write_text("\n".join(out) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(bad_adv), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "8.7" in output
        print(("PASS" if ok else "FAIL") + " bad_adversarial_scores")
        results.append(ok)

        missing_forge = tmp_path / "missing_forge_version"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", missing_forge)
        src = missing_forge / "sources.md"
        lines = [
            line
            for line in src.read_text(encoding="utf-8").splitlines()
            if not line.startswith("forge_version:")
        ]
        src.write_text("\n".join(lines) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(missing_forge), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "forge_version" in output
        print(("PASS" if ok else "FAIL") + " missing_forge_version")
        results.append(ok)

        over_budget = tmp_path / "over_evidence_budget"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", over_budget)
        src = over_budget / "sources.md"
        text = src.read_text(encoding="utf-8")
        extra = "\n".join(
            f"| [E{n}] | “超预算测试 {n}” | 测试 | [S01] | style 3 | 高 | 测试 |"
            for n in range(33, 42)
        )
        text = text.replace("\n## 5. 推断与置信度", "\n" + extra + "\n\n## 5. 推断与置信度")
        src.write_text(text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(over_budget), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "证据 41 条" in output
        print(("PASS" if ok else "FAIL") + " over_evidence_budget")
        results.append(ok)

        bad_quote = tmp_path / "bad_evidence_text"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", bad_quote)
        src = bad_quote / "style.md"
        text = src.read_text(encoding="utf-8")
        text = text.replace("弦凝千古寂", "弦凝千古寂X", 1)
        src.write_text(text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(bad_quote), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 1 and "E 编号只能有一个原文" in output
        print(("PASS" if ok else "FAIL") + " bad_evidence_text")
        results.append(ok)
    return results


def run_game_profile_checks() -> bool:
    packs, errors = load_packs()
    black_myth = resolve_game("Black Myth: Wukong", packs) or {}
    hades = resolve_game("Hades", packs) or {}
    nitw = resolve_game("NITW", packs) or {}
    checks = {
        "nine packs": len(packs) == 9,
        "registry clean": not errors,
        "genshin alias": (resolve_game("原神", packs) or {}).get("id") == "genshin",
        "full-name alias": (resolve_game("明日方舟：终末地", packs) or {}).get("id")
        == "arknights-endfield",
        "english alias": (resolve_game("Arknights", packs) or {}).get("id") == "arknights",
        "black myth alias": black_myth.get("id") == "black-myth-wukong",
        "black myth pilot": (
            (black_myth.get("protagonist") or {}).get("default_title") == "天命人"
            and (black_myth.get("canon") or {}).get("type") == "complete"
        ),
        "hades alias": hades.get("id") == "hades",
        "hades official zh": (
            (hades.get("languages") or {}).get("official_zh") is True
            and (hades.get("languages") or {}).get("translation_policy") == "official_zh"
        ),
        "nitw alias": nitw.get("id") == "night-in-the-woods",
        "nitw community translation": (
            (nitw.get("languages") or {}).get("official_zh") is False
            and (nitw.get("languages") or {}).get("translation_policy")
            == "community_translation"
        ),
    }
    invalid = {
        "schema_version": 1,
        "id": "Bad ID",
        "status": "curated",
    }
    invalid_errors = validate_pack(invalid)
    checks["invalid pack rejected"] = any("id" in error for error in invalid_errors)
    ok = all(checks.values())
    print(("PASS" if ok else "FAIL") + " game_profiles")
    if not ok:
        for name, passed in checks.items():
            if not passed:
                print(f"  failed: {name}")
        for error in errors[:10]:
            print("  registry:", error)
    return ok


def run_game_alias_check() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "game_alias"
        shutil.copytree(ROOT / "assets/examples/standard/qingxiao", target)
        for filename in ("soul.md", "style.md", "sources.md"):
            path = target / filename
            text = path.read_text(encoding="utf-8")
            text = text.replace('game: "鸣潮"', 'game: "明日方舟：终末地"')
            text = text.replace('game_slug: "wuwa"', 'game_slug: "arknights-endfield"')
            if filename == "soul.md":
                text = text.replace('target_user: "漂泊者"', 'target_user: "管理员"')
            path.write_text(text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(target), "--strict"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        ok = proc.returncode == 0
        print(("PASS" if ok else "FAIL") + " game_alias")
        if not ok:
            print((proc.stdout or "") + (proc.stderr or ""))
        return ok


def run_game_init_check() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name in ("scripts", "assets", "references"):
            shutil.copytree(
                ROOT / name,
                root / name,
                ignore=shutil.ignore_patterns("__pycache__"),
            )
        script = root / "scripts" / "game_profile.py"

        def run(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(script), *args],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

        baseline = run("check")
        baseline_count = next(
            (int(token) for token in baseline.stdout.split() if token.isdigit()),
            None,
        )

        init = run(
            "init",
            "--id",
            "test-game",
            "--display-name",
            "测试游戏",
            "--title",
            "试炼者",
            "--alias",
            "测试",
            "--landscape",
            "A",
            "--canon",
            "complete",
        )
        pack_path = root / "references" / "games" / "test-game.json"
        source_path = root / "references" / "sources" / "test-game.md"
        index = json.loads((root / "references" / "games" / "index.json").read_text(encoding="utf-8"))
        checks = {
            "init passes": init.returncode == 0,
            "pack written": pack_path.is_file(),
            "source skeleton": source_path.is_file() and "TODO" in source_path.read_text(encoding="utf-8"),
            "index updated": "test-game" in index.get("games", []),
        }

        all_check = run("check")
        checks["baseline check"] = baseline.returncode == 0 and baseline_count is not None
        checks["init registry valid"] = (
            all_check.returncode == 0
            and baseline_count is not None
            and f"{baseline_count + 1} game packs valid" in all_check.stdout
        )

        incomplete = run("game-check", "测试游戏", "--json")
        try:
            incomplete_json = json.loads(incomplete.stdout)
        except json.JSONDecodeError:
            incomplete_json = {}
        checks["incomplete gate"] = (
            incomplete.returncode == 2 and incomplete_json.get("status") == "INCOMPLETE"
        )

        source_path.write_text("# 测试游戏来源\n\n> 已人工补全。\n", encoding="utf-8")
        ready = run("game-check", "测试游戏", "--json")
        try:
            ready_json = json.loads(ready.stdout)
        except json.JSONDecodeError:
            ready_json = {}
        checks["ready gate"] = ready.returncode == 0 and ready_json.get("status") == "READY"

        duplicate = run(
            "init",
            "--id",
            "test-game",
            "--display-name",
            "测试游戏",
            "--title",
            "试炼者",
            "--landscape",
            "A",
        )
        checks["duplicate rejected"] = duplicate.returncode == 1

        run(
            "init",
            "--id",
            "test-d",
            "--display-name",
            "测试D",
            "--title",
            "行者",
            "--landscape",
            "D",
            "--canon",
            "complete",
        )
        (root / "references" / "sources" / "test-d.md").write_text(
            "# 测试D来源\n\n> 已人工补全。\n", encoding="utf-8"
        )
        conditional = run("game-check", "test-d", "--json")
        accepted = run("game-check", "test-d", "--accept-conditional", "--json")
        try:
            accepted_json = json.loads(accepted.stdout)
        except json.JSONDecodeError:
            accepted_json = {}
        checks["conditional gate"] = conditional.returncode == 2
        checks["conditional accepted"] = (
            accepted.returncode == 0
            and accepted_json.get("status") == "READY"
            and accepted_json.get("default_depth") == "quick"
        )

        ok = all(checks.values())
        print(("PASS" if ok else "FAIL") + " game_init")
        if not ok:
            for name, passed in checks.items():
                if not passed:
                    print(f"  failed: {name}")
            for proc in (init, all_check, incomplete, ready, duplicate, conditional, accepted):
                if proc.returncode != 0:
                    print((proc.stdout or "") + (proc.stderr or ""))
        return ok


def run_nonzh_translation_checks() -> bool:
    sources = """
## 4. 原文证据摘录
| ID | 原文（原语言） | 场景/对象 | 来源 | 用于章节 | 置信度 | 备注 | 中文译文（非中文必填） |
|---|---|---|---|---|---|---|---|
| [E01] | “I am the storm.” | 序章 | [S01] | soul 1 | 高 | 官方英文本 | “我就是风暴。” |
| [E02] | “No gods.” | 序章 | [S01] | soul 1 | 高 | 官方英文本 | “没有神。” |
| [E03] | “A \\| B” | 序章 | [S01] | soul 1 | 高 | 官方英文本 | “甲\\|乙” |
"""
    style_ok = """
## 3. 官方台词语料
| ID | 原文（原语言） | 场景/对象 | 用途 | 来源 | 置信度 | 中文译文（非中文必填） |
|---|---|---|---|---|---|---|
| [E01] | “I am the storm.” | 序章 | 语感 | [S01] | 高 | “我就是风暴。” |
"""
    style_missing = style_ok.replace("| “我就是风暴。” |", "|  |")
    style_mismatch = style_ok.replace("“我就是风暴。”", "“我是风暴。”")
    translations = translation_map(sources)
    good_pack = {
        "languages": {
            "official": ["en"],
            "official_zh": False,
            "translation_policy": "community_translation",
        }
    }
    zh_pack = {
        "languages": {
            "official": ["zh-CN"],
            "official_zh": True,
            "translation_policy": "none",
        }
    }
    good_fm = {
        "soul.md": {
            "source_languages": "en",
            "translation_policy": "community_translation",
            "translation_source": "社区译者A",
        }
    }
    checks = {
        "translation map": translations == {
            "E01": "我就是风暴。",
            "E02": "没有神。",
            "E03": "甲|乙",
        },
        "escaped pipe": translations.get("E03") == "甲|乙",
        "translation complete": validate_translation_consistency(
            sources, style_ok, True
        )
        == [],
        "translation missing": any(
            "E01" in error
            for error in validate_translation_consistency(sources, style_missing, True)
        ),
        "translation mismatch": any(
            "不一致" in error
            for error in validate_translation_consistency(sources, style_mismatch, True)
        ),
        "translation metadata ok": validate_translation_metadata(good_fm, good_pack)
        == [],
        "translation metadata none rejected": any(
            "不能是 none" in error
            for error in validate_translation_metadata(
                {
                    "soul.md": {
                        "source_languages": "en",
                        "translation_policy": "none",
                        "translation_source": "",
                    }
                },
                good_pack,
            )
        ),
        "translation metadata required": any(
            "必须填写 translation_policy" in error
            for error in validate_translation_metadata({"soul.md": {}}, good_pack)
        ),
        "translation source required": any(
            "translation_source" in error
            for error in validate_translation_metadata(
                {
                    "soul.md": {
                        "source_languages": "en",
                        "translation_policy": "community_translation",
                        "translation_source": "",
                    }
                },
                good_pack,
            )
        ),
        "chinese docs unaffected": validate_translation_metadata({"soul.md": {}}, zh_pack)
        == [],
    }
    ok = all(checks.values())
    print(("PASS" if ok else "FAIL") + " nonzh_translation")
    if not ok:
        for name, passed in checks.items():
            if not passed:
                print(f"  failed: {name}")
        print("  translations:", translations)
    return ok


def run_translation_quota_checks() -> bool:
    def style_with(rows: int) -> str:
        lines = [
            "## 3. 官方台词语料",
            "| ID | 原文 | 译文 |",
            "|---|---|---|",
        ]
        for index in range(rows):
            lines.append(f'| [E{index + 1:02d}] | “en{index}” | “中{index}” |')
        lines.append("## 4.")
        return "\n".join(lines) + "\n"

    def has_quota_error(body: str, limit: int, translation_required: bool) -> bool:
        errors, _ = validate_quote_quota(
            body, "", True, translation_required=translation_required
        )
        return any(f"超过上限 {limit}" in error for error in errors)

    checks = {
        "nonzh 30 rows/60 quotes": not has_quota_error(
            style_with(30), 60, translation_required=True
        ),
        "nonzh 31 rows/62 quotes": has_quota_error(
            style_with(31), 60, translation_required=True
        ),
        "zh 15 rows/30 quotes": not has_quota_error(
            style_with(15), 30, translation_required=False
        ),
        "zh 16 rows/32 quotes": has_quota_error(
            style_with(16), 30, translation_required=False
        ),
    }
    ok = all(checks.values())
    print(("PASS" if ok else "FAIL") + " translation_quota")
    if not ok:
        for name, passed in checks.items():
            if not passed:
                print(f"  failed: {name}")
    return ok


def run_fixture_sync_check() -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "tests").mkdir(parents=True)
        shutil.copy2(ROOT / "tests" / "make_fixtures.py", root / "tests" / "make_fixtures.py")
        shutil.copytree(
            ROOT / "assets" / "examples" / "standard" / "qingxiao",
            root / "assets" / "examples" / "standard" / "qingxiao",
        )
        proc = subprocess.run(
            [sys.executable, str(root / "tests" / "make_fixtures.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            print("FAIL fixture_sync: regeneration failed")
            print((proc.stdout or "") + (proc.stderr or ""))
            return False

        def hashes(directory: Path) -> dict[str, str]:
            return {
                path.relative_to(directory).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in directory.rglob("*")
                if path.is_file()
            }

        generated = hashes(root / "tests" / "fixtures")
        committed = hashes(ROOT / "tests" / "fixtures")
        ok = generated == committed
        print(("PASS" if ok else "FAIL") + " fixture_sync")
        if not ok:
            diff = sorted(set(generated) ^ set(committed))
            changed = sorted(
                key
                for key in set(generated) & set(committed)
                if generated[key] != committed[key]
            )
            print(f"  only-one-side: {diff[:5]}")
            print(f"  changed: {changed[:5]}")
        return ok


def run_tool_and_quote_checks() -> list[bool]:
    results: list[bool] = []

    nested = '“她说：「天空」很高。”'
    quotes = extract_quotes(nested)
    ok = quotes == ["她说：「天空」很高。"]
    print(("PASS" if ok else "FAIL") + " nested_quotes")
    results.append(ok)

    proc = subprocess.run(
        [sys.executable, str(PERSONA_TOOLS), "check", str(ROOT / "assets/examples/standard/qingxiao")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and "=== BUDGET ===" in output and "Evidence map" in output
    print(("PASS" if ok else "FAIL") + " persona_tools_smoke")
    results.append(ok)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "probes.md"
        proc = subprocess.run(
            [sys.executable, str(PROBE_HARNESS), "gen-prompts", str(ROOT / "assets/examples/standard/qingxiao"), "--out", str(out)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        text = out.read_text(encoding="utf-8") if out.exists() else ""
        ok = (
            proc.returncode == 0
            and "## 12 个 OOC 探针" in text
            and "## 10 个对抗性探针" in text
        )
        print(("PASS" if ok else "FAIL") + " probe_harness_smoke")
        results.append(ok)

        out_dir = Path(tmp) / "probe"
        proc = subprocess.run(
            [sys.executable, str(PROBE_HARNESS), "gen-prompts", str(ROOT / "assets/examples/standard/qingxiao"), "--out-dir", str(out_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        package = out_dir / "probe-package.md"
        answers = out_dir / "answers.md"
        ok = (
            proc.returncode == 0
            and package.is_file()
            and answers.is_file()
            and "## OOC" in answers.read_text(encoding="utf-8")
        )
        print(("PASS" if ok else "FAIL") + " probe_out_dir")
        results.append(ok)

        answers = Path(tmp) / "answers.md"
        answers.write_text(
            "## OOC\n1. 测试回答。\n2. 测试回答。\n\n## 对抗\n1. 测试回答。\n2. 测试回答。\n",
            encoding="utf-8",
        )
        report = Path(tmp) / "report.md"
        proc = subprocess.run(
            [sys.executable, str(PROBE_HARNESS), "format-report", str(answers), "--out", str(report)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        text = report.read_text(encoding="utf-8") if report.exists() else ""
        ok = (
            proc.returncode == 0
            and "### 8.3 OOC 探针测试" in text
            and "### 8.7 对抗性探针记录" in text
        )
        print(("PASS" if ok else "FAIL") + " probe_report_smoke")
        results.append(ok)
    return results


def main() -> int:
    results = [run_case(*case) for case in CASES]
    results.extend(run_parser_and_json_checks())
    results.append(run_game_profile_checks())
    results.append(run_game_alias_check())
    results.append(run_game_init_check())
    results.append(run_nonzh_translation_checks())
    results.append(run_translation_quota_checks())
    results.append(run_fixture_sync_check())
    results.extend(run_tool_and_quote_checks())
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
