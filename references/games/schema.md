# Game Pack Schema (v1)

> 机器可读的游戏元数据放在 `references/games/<id>.json`，由 `references/games/index.json` 索引。
> 人类可读的来源入口、检索式、缺口与已知坑仍放 `references/sources/<id>.md`。
> 校验命令：`python scripts/game_profile.py check`；接入闸门：`init` / `game-check`。

## 1. 文件

```text
references/games/
├── index.json          # 游戏 id 列表与 schema_version
├── schema.md           # 本文件
├── genshin.json
├── hsr.json
├── zzz.json
├── wuwa.json
├── arknights.json
├── arknights-endfield.json
├── black-myth-wukong.json
├── hades.json
└── night-in-the-woods.json
```

`index.json`：

```json
{
  "schema_version": 1,
  "updated": "2026-10-24",
  "games": ["genshin", "hsr"]
}
```

## 2. 必填字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | int | 当前为 `1` |
| `id` | string | 小写字母/数字/连字符，必须与文件名一致 |
| `status` | string | `curated` / `provisional` / `generic`（v1.7 仅使用 curated / provisional；`generic` 预留未用，`game-init` 只生成 provisional） |
| `display_name` | string | 展示名，如“明日方舟：终末地” |
| `aliases` | string[] | 用户可能输入的名称；全局唯一（大小写不敏感） |
| `game_field` | string | 写入三份文档 frontmatter 的 `game` 值；全局唯一 |
| `directory` | string | 默认输出目录名，单层安全目录；全局唯一 |
| `source_profile` | string | 仓库内相对路径，指向 `references/sources/<id>.md` |
| `source_landscape` | string | `A` / `B` / `C` / `D` / `E` |
| `languages` | object | 官方语言、输出语言、翻译政策 |
| `protagonist` | object | 玩家主角模型与固定称号 |
| `canon` | object | 正典类型 |
| `content` | object | 内容分级 |
| `verification` | object | 来源/证据门禁参数 |

可选字段：`source_landscape_notes`（string）、`known_pitfalls`（string[]）。

## 3. 来源地形

| 等级 | 定义 | v1.7 承诺 |
|---|---|---|
| `A` | 官方中文 + 官方角色/公告入口 + 可用的社区 Wiki 转录 | standard/deep |
| `B` | 官方只有非中文，或官方页面很少；有社区 Wiki | standard（需翻译政策） |
| `C` | 有官方入口，但社区 Wiki 覆盖不足 | standard，人格章节常标 community-only/derived |
| `D` | 只有社区 Wiki/二创，官方不可达 | 仅 quick；默认 CONDITIONAL |
| `E` | 没有任何可检索来源 | 拒绝生成 |

`source_landscape` 是**游戏级**声明，不是自动检测，也不代表每个角色都有 S1。新游戏接入时必须先做游戏级来源发现，再对目标角色做角色级 S1 探测（见 `../game-onboarding.md` §3.1），最后由用户确认。角色级 S1=0 时，开工计划应按 quick 或 `community-only` / `partial` 处理。

`game-check` 会按地形限制 `verification.default_depth`：A 最高 deep，B/C 最高 standard，D 仅 quick 且需 `--accept-conditional`，E 直接拒绝。`init` 对 D/E 自动写 quick。

## 4. 主角模型

```json
"protagonist": {
  "mode": "fixed",
  "default_title": "博士",
  "allowed_titles": ["博士"],
  "gender_neutral": true
}
```

| mode | 含义 | v1.7 |
|---|---|---|
| `fixed` | 一个固定称号 | 支持 |
| `selectable` | 多个可选称号 | 预留，暂不支持 |
| `custom` | 玩家自定义名字 | 预留，暂不支持 |
| `ensemble` | 没有单一主角/群像 | 预留，暂不支持 |

`target_user` 必须属于 `allowed_titles`；`custom` 模式将改为允许用户确认的名字。字段先保留，等 v1.8 再实现。

## 5. 正典类型

```json
"canon": { "type": "live_service" }
```

| type | 含义 | v1.7 |
|---|---|---|
| `live_service` | 持续更新，按版本快照 | 支持 |
| `complete` | 已完结的线性正典 | 支持 |
| `branching` | 多路线/多结局 | 预留，暂不支持 |
| `remake` | 重制版/多时间线 | 预留，暂不支持 |
| `early_access` | EA/未完成正典 | 预留，暂不支持 |
| `sandbox` | 沙盒/涌现叙事 | 预留，暂不支持 |

## 6. 语言与翻译

```json
"languages": {
  "official": ["zh-CN"],
  "output": "zh-CN",
  "official_zh": true,
  "translation_policy": "none"
}
```

- `official`：官方语言列表（BCP-47）。
- `output`：生成文档语言，默认 `zh-CN`。
- `official_zh`：是否存在官方中文（简体或繁体均可）。
- `translation_policy`：`none` / `official_zh` / `community_translation`。

v1.7 支持“官方只有非中文”的游戏。落地字段与规则：

- 三份人格文档的 frontmatter 增加 `source_languages`（原文语言，block list）、`translation_policy`（与 pack 一致）、`translation_source`（官方中文版或社区译者/链接）。
- `sources.md` §4 与 `style.md` §3 的表格**最后一列**为 `中文译文（非中文必填）`；`原文` 列保留原语言原句，中文游戏填 `—`。
- `official_zh=true` 时用 `official_zh` 或 `none`；`official_zh=false` 时不能填 `none`，只能用 `community_translation`（或用户提供的官方中文版 `official_zh`）。
- 校验器会强制：非中文流程每条 E 都有中文译文、style 译文与 sources §4 一致、译文含中文、frontmatter 与 pack 的语言政策一致。
- 引用时写“译文”并注明来源；**不得把社区译文说成官方中文原句**。原文与译文冲突时保留两者，按 `source-policy.md` 裁决。

示例：

```yaml
source_languages:
  - en
translation_policy: "community_translation"
translation_source: "译者名/链接"
```

```markdown
| [E01] | “I am the storm.” | 序章 | [S01] | soul 1 / style 3 | 高 | 官方英文本 | “我就是风暴。” |
```

## 7. 验证参数

```json
"verification": {
  "s1_required_for_core": true,
  "cross_check": 2,
  "coverage_labels": ["partial", "community-only", "derived"],
  "default_depth": "standard"
}
```

`source_landscape=D` 时，`game-check` 会把允许深度限制为 `quick`，并要求 CONDITIONAL 的显式接受；`E` 拒绝。`status=provisional` 表示接入信息尚未由用户确认，不阻止生成，但必须在开工计划中说明。

## 8. 添加或修改游戏

推荐用接入工具，不要手写索引：

```bash
python scripts/game_profile.py init \
  --id <id> --display-name "<展示名>" --title "<固定主角称号>" \
  --alias "<别名>" --landscape <A/B/C/D/E> --canon <live_service/complete>
python scripts/game_profile.py game-check <id>
python scripts/game_profile.py check
python scripts/selftest.py
```

`init` 会创建 `references/games/<id>.json`、来源骨架，并把 `id` 加进 `index.json`；来源档案补完后 `game-check` 才会返回 `READY`。完整流程与定级标准见 `../game-onboarding.md`。

手工修改时：

1. 保持 `id` 与文件名、`index.json` 一致。
2. 改 `aliases` / `game_field` / `directory` 后跑 `check`，确认全局唯一。
3. `source_profile` 必须指向仓库内已存在的文件。
4. 用户确认接入信息后，把 `status` 从 `provisional` 改为 `curated`。
