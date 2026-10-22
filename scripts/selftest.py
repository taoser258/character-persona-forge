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
from validate_persona import extract_quotes, parse_frontmatter  # noqa: E402

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
    results.append(run_fixture_sync_check())
    results.extend(run_tool_and_quote_checks())
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
