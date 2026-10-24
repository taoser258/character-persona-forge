#!/usr/bin/env python3
"""Load and validate character-persona-forge game packs.

Game packs live in `references/games/<id>.json` and are indexed by
`references/games/index.json`. The validator uses this module so game names,
directories, protagonist titles, languages, and source profiles are declared in
one place instead of scattered constants.

Usage:
    python3 scripts/game_profile.py check
    python3 scripts/game_profile.py list
    python3 scripts/game_profile.py resolve <game name or alias>
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
GAMES_DIR = ROOT / "references" / "games"
PACK_TEMPLATE = ROOT / "assets" / "templates" / "game-profile.json"
SOURCE_TEMPLATE = ROOT / "assets" / "templates" / "game-source-profile.md"
SCHEMA_VERSION = 1
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TODO_RE = re.compile(r"\bTODO\b")
ZH_OFFICIAL_LANGUAGES = {"zh", "zh-cn", "zh-hans", "zh-hant", "zh-tw"}

STATUSES = {"curated", "provisional", "generic"}
SOURCE_LANDSCAPES = {"A", "B", "C", "D", "E"}
PROTAGONIST_MODES = {"fixed", "selectable", "custom", "ensemble"}
CANON_TYPES = {"live_service", "complete", "branching", "remake", "sandbox", "early_access"}
TRANSLATION_POLICIES = {"none", "official_zh", "community_translation"}
COVERAGE_LABELS = {"partial", "community-only", "derived"}
DEPTHS = {"quick", "standard", "deep"}

LANDSCAPE_NOTES = {
    "A": "官方中文入口 + 可用的社区 Wiki 转录；角色级官方页面缺口需在来源档案中写明。",
    "B": "官方页面很少或官方只有非中文；有社区 Wiki，按翻译政策处理原文。",
    "C": "有官方入口，但社区 Wiki 覆盖不足；人格章节常标 community-only / derived。",
    "D": "只有社区 Wiki/二创，官方不可达；仅 quick，需显式接受 CONDITIONAL。",
    "E": "没有任何可检索来源；v1.7 拒绝生成。",
}
LANDSCAPE_MAX_DEPTH = {"A": "deep", "B": "standard", "C": "standard", "D": "quick", "E": None}
DEPTH_ORDER = {"quick": 0, "standard": 1, "deep": 2}


class GameProfileError(Exception):
    """Raised when the game registry cannot be loaded."""


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GameProfileError(f"缺少文件: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GameProfileError(f"JSON 解析失败: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GameProfileError(f"顶层必须是对象: {path}")
    return data


def _non_empty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_relative_path(value: str) -> bool:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or re.match(r"^[A-Za-z]:", value):
        return False
    return True


def validate_pack(pack: dict, expected_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(pack, dict):
        return ["游戏档案必须是 JSON 对象"]
    pack_id = pack.get("id") if isinstance(pack.get("id"), str) else "?"
    prefix = f"{pack_id}: "

    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append(prefix + f"schema_version 必须为 {SCHEMA_VERSION}")
    if not _non_empty_string(pack.get("id")) or not ID_RE.fullmatch(pack.get("id", "")):
        errors.append(prefix + "id 必须是小写字母/数字/连字符")
    elif expected_id and pack.get("id") != expected_id:
        errors.append(prefix + f"id 与文件名不一致（应为 {expected_id}）")
    if pack.get("status") not in STATUSES:
        errors.append(prefix + f"status 必须是 {sorted(STATUSES)}")
    for key in ("display_name", "game_field", "directory", "source_profile"):
        if not _non_empty_string(pack.get(key)):
            errors.append(prefix + f"缺少或为空的 {key}")
    aliases = pack.get("aliases")
    if not isinstance(aliases, list) or not aliases or not all(_non_empty_string(a) for a in aliases):
        errors.append(prefix + "aliases 必须是非空字符串数组")
    else:
        lowered = [a.strip().casefold() for a in aliases]
        if len(lowered) != len(set(lowered)):
            errors.append(prefix + "aliases 内部有重复")
    directory = pack.get("directory")
    if _non_empty_string(directory):
        if Path(directory).name != directory or directory in {".", ".."} or ":" in directory:
            errors.append(prefix + "directory 必须是单层安全目录名")
    source_profile = pack.get("source_profile")
    if _non_empty_string(source_profile):
        if not _safe_relative_path(source_profile):
            errors.append(prefix + "source_profile 必须是仓库内相对路径")
        elif not (ROOT / source_profile).is_file():
            errors.append(prefix + f"source_profile 不存在: {source_profile}")
    if pack.get("source_landscape") not in SOURCE_LANDSCAPES:
        errors.append(prefix + f"source_landscape 必须是 {sorted(SOURCE_LANDSCAPES)}")

    languages = pack.get("languages")
    if not isinstance(languages, dict):
        errors.append(prefix + "缺少 languages 对象")
    else:
        official = languages.get("official")
        if not isinstance(official, list) or not official or not all(_non_empty_string(x) for x in official):
            errors.append(prefix + "languages.official 必须是非空字符串数组")
        if not _non_empty_string(languages.get("output")):
            errors.append(prefix + "languages.output 不能为空")
        if not isinstance(languages.get("official_zh"), bool):
            errors.append(prefix + "languages.official_zh 必须是布尔值")
        if languages.get("translation_policy") not in TRANSLATION_POLICIES:
            errors.append(prefix + f"languages.translation_policy 必须是 {sorted(TRANSLATION_POLICIES)}")

    protagonist = pack.get("protagonist")
    if not isinstance(protagonist, dict):
        errors.append(prefix + "缺少 protagonist 对象")
    else:
        mode = protagonist.get("mode")
        if mode not in PROTAGONIST_MODES:
            errors.append(prefix + f"protagonist.mode 必须是 {sorted(PROTAGONIST_MODES)}")
        elif mode in {"selectable", "custom", "ensemble"}:
            errors.append(prefix + f"v1.7 暂不支持 protagonist.mode={mode}（字段已预留，计划 v1.8）")
        default_title = protagonist.get("default_title")
        allowed_titles = protagonist.get("allowed_titles")
        if not _non_empty_string(default_title):
            errors.append(prefix + "protagonist.default_title 不能为空")
        if not isinstance(allowed_titles, list) or not allowed_titles or not all(
            _non_empty_string(t) for t in allowed_titles
        ):
            errors.append(prefix + "protagonist.allowed_titles 必须是非空字符串数组")
        elif _non_empty_string(default_title) and default_title not in allowed_titles:
            errors.append(prefix + "protagonist.default_title 必须在 allowed_titles 中")
        if mode == "selectable" and isinstance(allowed_titles, list) and len(allowed_titles) < 2:
            errors.append(prefix + "selectable 模式至少需要 2 个 allowed_titles")
        if not isinstance(protagonist.get("gender_neutral"), bool):
            errors.append(prefix + "protagonist.gender_neutral 必须是布尔值")

    canon = pack.get("canon")
    if not isinstance(canon, dict) or canon.get("type") not in CANON_TYPES:
        errors.append(prefix + f"canon.type 必须是 {sorted(CANON_TYPES)}")
    elif canon.get("type") in {"branching", "remake", "early_access", "sandbox"}:
        errors.append(
            prefix + f"v1.7 暂不支持 canon.type={canon.get('type')}（字段已预留，计划 v1.8）"
        )

    content = pack.get("content")
    if not isinstance(content, dict) or not _non_empty_string(content.get("rating")):
        errors.append(prefix + "content.rating 不能为空")

    verification = pack.get("verification")
    if not isinstance(verification, dict):
        errors.append(prefix + "缺少 verification 对象")
    else:
        if not isinstance(verification.get("s1_required_for_core"), bool):
            errors.append(prefix + "verification.s1_required_for_core 必须是布尔值")
        cross_check = verification.get("cross_check")
        if not isinstance(cross_check, int) or isinstance(cross_check, bool) or cross_check < 1:
            errors.append(prefix + "verification.cross_check 必须是 >=1 的整数")
        labels = verification.get("coverage_labels")
        if not isinstance(labels, list) or not set(labels).issubset(COVERAGE_LABELS):
            errors.append(prefix + f"verification.coverage_labels 必须是 {sorted(COVERAGE_LABELS)} 的子集")
        if verification.get("default_depth") not in DEPTHS:
            errors.append(prefix + f"verification.default_depth 必须是 {sorted(DEPTHS)}")

    pitfalls = pack.get("known_pitfalls")
    if pitfalls is not None and (
        not isinstance(pitfalls, list) or not all(_non_empty_string(x) for x in pitfalls)
    ):
        errors.append(prefix + "known_pitfalls 必须是字符串数组")
    return errors


def load_packs() -> tuple[dict[str, dict], list[str]]:
    """Load every indexed pack. Returns (packs_by_id, errors)."""
    errors: list[str] = []
    try:
        index = _read_json(GAMES_DIR / "index.json")
    except GameProfileError as exc:
        return {}, [str(exc)]
    if index.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"index.json: schema_version 必须为 {SCHEMA_VERSION}")
    game_ids = index.get("games")
    if not isinstance(game_ids, list) or not game_ids:
        return {}, errors + ["index.json: games 必须是非空数组"]

    packs: dict[str, dict] = {}
    seen_fields: dict[str, str] = {}
    seen_dirs: dict[str, str] = {}
    seen_aliases: dict[str, str] = {}
    for game_id in game_ids:
        if not isinstance(game_id, str) or not ID_RE.fullmatch(game_id):
            errors.append(f"index.json: 非法游戏 id {game_id!r}")
            continue
        path = GAMES_DIR / f"{game_id}.json"
        try:
            pack = _read_json(path)
        except GameProfileError as exc:
            errors.append(str(exc))
            continue
        pack_errors = validate_pack(pack, expected_id=game_id)
        errors.extend(pack_errors)
        packs[game_id] = pack
        game_field = pack.get("game_field")
        directory = pack.get("directory")
        if isinstance(game_field, str):
            if game_field in seen_fields:
                errors.append(f"{game_id}: game_field 与 {seen_fields[game_field]} 重复")
            seen_fields[game_field] = game_id
        if isinstance(directory, str):
            if directory in seen_dirs:
                errors.append(f"{game_id}: directory 与 {seen_dirs[directory]} 重复")
            seen_dirs[directory] = game_id
        aliases = pack.get("aliases")
        if isinstance(aliases, list):
            for alias in aliases:
                if not isinstance(alias, str):
                    continue
                key = alias.strip().casefold()
                if key in seen_aliases and seen_aliases[key] != game_id:
                    errors.append(f"{game_id}: alias {alias!r} 与 {seen_aliases[key]} 重复")
                seen_aliases[key] = game_id

    return packs, errors


def resolve_game(name: str, packs: dict[str, dict] | None = None) -> dict | None:
    if packs is None:
        packs, _ = load_packs()
    wanted = (name or "").strip()
    if not wanted:
        return None
    candidates = [(p.get("id"), p) for p in packs.values()]
    for value, pack in candidates:
        if value == wanted:
            return pack
    for pack in packs.values():
        if pack.get("game_field") == wanted or pack.get("display_name") == wanted:
            return pack
        if wanted in pack.get("aliases", []):
            return pack
    wanted_folded = wanted.casefold()
    for pack in packs.values():
        names = [pack.get("id"), pack.get("game_field"), pack.get("display_name"), *pack.get("aliases", [])]
        if any(isinstance(value, str) and value.casefold() == wanted_folded for value in names):
            return pack
    return None


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _safe_directory_name(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|：，,。.、·・\s]+', "", name)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = value.strip()
        key = text.casefold()
        if text and key not in seen:
            seen.add(key)
            result.append(text)
    return result


def _render_source_skeleton(
    display_name: str,
    title: str,
    landscape: str,
    canon: str,
    official: list[str],
    official_zh: bool,
    date: str,
) -> str:
    text = SOURCE_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{DISPLAY_NAME}}": display_name,
        "{{TITLE}}": title,
        "{{LANDSCAPE}}": landscape,
        "{{CANON}}": canon,
        "{{LANGUAGES}}": "、".join(official),
        "{{OFFICIAL_ZH}}": "是" if official_zh else "否",
        "{{DATE}}": date,
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def _collision_errors(
    packs: dict[str, dict], game_id: str, aliases: list[str], game_field: str, directory: str
) -> list[str]:
    errors: list[str] = []
    for alias in aliases:
        other = resolve_game(alias, packs)
        if other and other.get("id") != game_id:
            errors.append(f"别名 {alias!r} 已被 {other.get('id')} 使用")
    for other_id, other in packs.items():
        if other_id == game_id:
            continue
        if other.get("game_field") == game_field:
            errors.append(f"game_field {game_field!r} 已被 {other_id} 使用")
        if other.get("directory") == directory:
            errors.append(f"directory {directory!r} 已被 {other_id} 使用")
    return errors


def command_init(args) -> int:
    packs, registry_errors = load_packs()
    if registry_errors:
        print("FAIL: 现有游戏档案有错误，先运行 check 修复再 init")
        for error in registry_errors:
            print("-", error)
        return 1

    game_id = args.id.strip()
    if not ID_RE.fullmatch(game_id):
        print("FAIL: --id 必须是小写字母/数字/连字符")
        return 1
    display_name = args.display_name.strip()
    title = args.title.strip()
    if not display_name or not title:
        print("FAIL: --display-name 与 --title 不能为空")
        return 1

    aliases = _dedupe([display_name, *args.alias])
    game_field = (args.game_field or display_name).strip()
    directory = (args.directory or _safe_directory_name(display_name)).strip()
    if not directory or Path(directory).name != directory or directory in {".", ".."}:
        print("FAIL: --directory 必须是单层安全目录名")
        return 1

    source_profile = (args.source_profile or f"references/sources/{game_id}.md").replace("\\", "/")
    if not source_profile.startswith("references/sources/") or not source_profile.endswith(".md"):
        print("FAIL: --source-profile 必须是 references/sources/ 下的 .md 路径")
        return 1
    if not _safe_relative_path(source_profile):
        print("FAIL: --source-profile 必须是仓库内相对路径")
        return 1

    pack_path = GAMES_DIR / f"{game_id}.json"
    index_path = GAMES_DIR / "index.json"
    try:
        index = _read_json(index_path)
    except GameProfileError as exc:
        print(f"FAIL: index.json 无法读取：{exc}")
        return 1
    indexed = index.get("games") if isinstance(index.get("games"), list) else []
    if pack_path.exists() and not args.force:
        print(f"FAIL: {pack_path.relative_to(ROOT)} 已存在；确认要覆盖 provisional 档案时加 --force")
        return 1
    if pack_path.exists() and args.force:
        existing = _read_json(pack_path)
        if existing.get("status") != "provisional":
            print("FAIL: 只允许 --force 覆盖 provisional 档案；curated 档案请手工修改")
            return 1
    if game_id in indexed and not args.force:
        print(f"FAIL: index.json 已登记 {game_id}；确认要覆盖时加 --force")
        return 1

    collisions = _collision_errors(packs, game_id, aliases, game_field, directory)
    if collisions:
        print("FAIL: 名称冲突")
        for error in collisions:
            print("-", error)
        return 1

    official = _dedupe(args.official_lang or ["zh-CN"])
    if not official:
        print("FAIL: --official-lang 不能为空")
        return 1
    official_zh = any(lang.strip().lower() in ZH_OFFICIAL_LANGUAGES for lang in official)
    translation_policy = "none" if official_zh else "community_translation"

    if not PACK_TEMPLATE.is_file():
        print(f"FAIL: 缺少 pack 模板 {PACK_TEMPLATE.relative_to(ROOT)}")
        return 1
    if not SOURCE_TEMPLATE.is_file():
        print(f"FAIL: 缺少来源模板 {SOURCE_TEMPLATE.relative_to(ROOT)}")
        return 1

    pack = _read_json(PACK_TEMPLATE)
    pack.update(
        {
            "id": game_id,
            "status": args.status,
            "display_name": display_name,
            "aliases": aliases,
            "game_field": game_field,
            "directory": directory,
            "source_profile": source_profile,
            "source_landscape": args.landscape,
            "source_landscape_notes": args.notes or LANDSCAPE_NOTES[args.landscape],
        }
    )
    pack["languages"] = {
        "official": official,
        "output": "zh-CN",
        "official_zh": official_zh,
        "translation_policy": translation_policy,
    }
    allowed_titles = _dedupe([title, *args.allowed_title])
    pack["protagonist"] = {
        "mode": "fixed",
        "default_title": title,
        "allowed_titles": allowed_titles,
        "gender_neutral": True,
    }
    pack["canon"] = {"type": args.canon}
    pack["content"] = {"rating": args.content_rating}
    max_depth = LANDSCAPE_MAX_DEPTH[args.landscape]
    pack["verification"] = {
        "s1_required_for_core": args.landscape in {"A", "B"},
        "cross_check": 2 if args.landscape in {"A", "B"} else 1,
        "coverage_labels": ["partial", "community-only", "derived"],
        "default_depth": "quick" if max_depth == "quick" else "standard",
    }

    today = datetime.date.today().isoformat()
    source_path = ROOT / source_profile
    created_source = False
    if source_path.exists():
        if not source_path.is_file():
            print(f"FAIL: 来源档案路径不是文件：{source_profile}")
            return 1
    else:
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            _render_source_skeleton(
                display_name, title, args.landscape, args.canon, official, official_zh, today
            ),
            encoding="utf-8",
        )
        created_source = True

    errors = validate_pack(pack, expected_id=game_id)
    if errors:
        if created_source:
            source_path.unlink()
        print("FAIL: 生成的档案未通过校验")
        for error in errors:
            print("-", error)
        return 1

    _write_json(pack_path, pack)
    if game_id not in indexed:
        indexed.append(game_id)
    index["games"] = indexed
    index["updated"] = today
    _write_json(index_path, index)

    todo_count = len(TODO_RE.findall(source_path.read_text(encoding="utf-8")))
    print(f"PASS: 已创建 {game_id}")
    print(f"- pack: {pack_path.relative_to(ROOT)}")
    print(f"- source: {source_profile} (TODO: {todo_count})")
    print(f"- landscape: {args.landscape} / canon: {args.canon} / title: {title}")
    print("next:")
    print("  1. 补全来源档案，清掉 TODO")
    print(f"  2. python scripts/game_profile.py game-check {game_id}")
    print("  3. 通过后把 status 从 provisional 改为 curated，并运行 check 与 selftest")
    return 0


def command_game_check(args) -> int:
    packs, registry_errors = load_packs()
    pack = resolve_game(args.name, packs)
    if not pack:
        print(f"NOT FOUND: {args.name}")
        return 1

    game_id = pack.get("id")
    errors = validate_pack(pack, expected_id=game_id)
    warnings = list(registry_errors)
    landscape = pack.get("source_landscape")
    max_depth = LANDSCAPE_MAX_DEPTH.get(landscape)
    depth = (pack.get("verification") or {}).get("default_depth")

    source_path = ROOT / str(pack.get("source_profile", ""))
    todo_count = 0
    if source_path.is_file():
        todo_count = len(TODO_RE.findall(source_path.read_text(encoding="utf-8")))
    else:
        errors.append(f"来源档案不存在: {pack.get('source_profile')}")

    if landscape == "E":
        errors.append("来源地形 E：v1.7 拒绝生成，请换游戏或由用户提供可检索材料")
    elif max_depth and depth in DEPTH_ORDER and DEPTH_ORDER[depth] > DEPTH_ORDER[max_depth]:
        errors.append(f"来源地形 {landscape} 最高支持 {max_depth}，当前 default_depth={depth}")

    languages = pack.get("languages") or {}
    if not languages.get("official_zh") and languages.get("translation_policy") == "none":
        errors.append("官方无中文但 translation_policy=none；非中文原文需走翻译标注流程")

    if pack.get("status") == "provisional":
        warnings.append("status=provisional：接入信息尚未由用户确认，生成前需明确告知")

    conditional = landscape == "D" and not args.accept_conditional
    if errors:
        status = "FAIL"
    elif todo_count:
        status = "INCOMPLETE"
    elif conditional:
        status = "CONDITIONAL"
    else:
        status = "READY"

    result = {
        "id": game_id,
        "display_name": pack.get("display_name"),
        "status": status,
        "pack_status": pack.get("status"),
        "landscape": landscape,
        "max_depth": max_depth,
        "default_depth": depth,
        "canon": (pack.get("canon") or {}).get("type"),
        "title": (pack.get("protagonist") or {}).get("default_title"),
        "source_profile": pack.get("source_profile"),
        "todo_count": todo_count,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{status}: {game_id} ({pack.get('display_name')})")
        print(f"- landscape: {landscape} / max depth: {max_depth} / default: {depth}")
        print(f"- canon: {result['canon']} / title: {result['title']}")
        print(f"- source_profile: {result['source_profile']} (TODO: {todo_count})")
        for warning in warnings:
            print("WARN:", warning)
        for error in errors:
            print("ERROR:", error)
        if status == "INCOMPLETE":
            print("next: 补全来源档案中的 TODO，再运行一次 game-check")
        elif status == "CONDITIONAL":
            print("next: 来源地形 D 仅支持 quick；确认接受后加 --accept-conditional")
        elif status == "READY":
            print("next: 可进入角色人格文档开工计划；provisional 档案在交付前改 curated 或说明原因")

    if status == "READY":
        return 0
    if status in {"INCOMPLETE", "CONDITIONAL"}:
        return 2
    return 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="校验 index.json 与全部游戏档案")
    sub.add_parser("list", help="列出已登记游戏")
    resolve = sub.add_parser("resolve", help="按 id、游戏名或别名解析游戏档案")
    resolve.add_argument("name")
    init = sub.add_parser("init", help="创建 provisional 游戏档案与来源骨架")
    init.add_argument("--id", required=True, help="小写字母/数字/连字符")
    init.add_argument("--display-name", required=True)
    init.add_argument("--title", required=True, help="固定主角称号")
    init.add_argument("--alias", action="append", default=[], help="可重复；展示名会自动加入")
    init.add_argument("--game-field", help="写入 frontmatter 的 game 值；默认等于展示名")
    init.add_argument("--directory", help="默认输出目录名；默认由展示名去标点得到")
    init.add_argument("--source-profile", help="默认 references/sources/<id>.md")
    init.add_argument("--landscape", required=True, choices=sorted(SOURCE_LANDSCAPES))
    init.add_argument("--canon", default="complete", choices=["live_service", "complete"])
    init.add_argument("--official-lang", action="append", help="可重复；默认 zh-CN")
    init.add_argument("--allowed-title", action="append", default=[], help="可重复")
    init.add_argument("--content-rating", default="全年龄+轻度浪漫")
    init.add_argument("--notes", help="来源地形说明")
    init.add_argument("--status", default="provisional", choices=["provisional"])
    init.add_argument("--force", action="store_true", help="仅覆盖 provisional 档案")
    game_check = sub.add_parser("game-check", help="检查单个游戏是否可进入人格文档流程")
    game_check.add_argument("name")
    game_check.add_argument("--json", action="store_true")
    game_check.add_argument("--accept-conditional", action="store_true")
    args = parser.parse_args()

    if args.command == "init":
        return command_init(args)
    if args.command == "game-check":
        return command_game_check(args)
    if args.command == "check":
        packs, errors = load_packs()
        if errors:
            print("FAIL")
            for error in errors:
                print("-", error)
            return 1
        print(f"PASS: {len(packs)} game packs valid")
        return 0
    if args.command == "list":
        packs, errors = load_packs()
        for error in errors:
            print("WARN:", error)
        for game_id, pack in packs.items():
            protagonist = pack.get("protagonist", {})
            print(
                f"{game_id}\t{pack.get('game_field')}\t{pack.get('directory')}\t"
                f"{protagonist.get('default_title')}\t{pack.get('status')}\t{pack.get('source_landscape')}"
            )
        return 0 if not errors else 1
    if args.command == "resolve":
        packs, errors = load_packs()
        if errors:
            for error in errors:
                print("WARN:", error)
        pack = resolve_game(args.name, packs)
        if not pack:
            print(f"NOT FOUND: {args.name}")
            return 1
        print(json.dumps(pack, ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
