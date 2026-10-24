# Character Persona Forge

[English](README.en.md) | **简体中文**

[![Version](https://img.shields.io/badge/version-1.7.0-blue.svg)](#)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![selftest](https://img.shields.io/badge/selftest-29%2F29-brightgreen.svg)](#验证与自检)

> 把游戏角色编译成**可审阅、可注入、可验证**的人格文档。

`character-persona-forge` 是一个 Agent Skill：把官方来源、证据分级、人格边界、运行时注入和自检测试串成一条可审计的流水线，生成 `soul.md`、`style.md`、`sources.md`，并可选生成 `injection.md` 一键注入包。

它不是“让模型自由发挥一段角色扮演提示词”，而是“来源 → 证据 → 人格契约 → 自检”的文档生产流程。仓库内置 **9 个经过重点优化与实测的 Game Pack**：六款 curated 游戏 + 黑神话：悟空、Hades、Night in the Woods 三款 provisional 试点。**支持范围不限于此**：任意有可检索来源的游戏都可以通过 `references/game-onboarding.md` 接入。

---

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [产出](#产出)
- [重点优化与验证的游戏](#重点优化与验证的游戏)
- [它是怎么制作人格文档的](#它是怎么制作人格文档的)
- [注入后如何维持长期对话](#注入后如何维持长期对话)
- [验证与自检](#验证与自检)
- [质量门禁](#质量门禁)
- [仓库架构](#仓库架构)
- [新增游戏](#新增游戏)
- [适合与不适合](#适合与不适合)
- [许可证与声明](#许可证与声明)
- [Contributing](#contributing)

---

## 安装

### 方式 A：让 Agent 直接安装（推荐）

把下面这句话发给支持 Agent Skills 的宿主（Claude Code、Codex、Cursor、ZCode、WorkBuddy 等）：

> 帮我安装这个 skill：https://github.com/taoser258/character-persona-forge

Agent 会按当前宿主的规则，把仓库放到对应的 skills 目录，并检查 `SKILL.md` 是否可读。若宿主不支持自动安装，用方式 B。

### 方式 B：手动安装

```bash
git clone https://github.com/taoser258/character-persona-forge.git
# 把 $SKILLS_DIR 换成当前宿主的 skills 目录
cp -r character-persona-forge "$SKILLS_DIR/character-persona-forge"
```

常见宿主目录不同（如 `~/.claude/skills/`、`.agents/skills/`、`~/.zcode/skills/`），完整 51 个宿主映射见 `references/runtime-integration.md` §6。

### 验证安装

```bash
cd "$SKILLS_DIR/character-persona-forge"
python scripts/selftest.py
# 预期：29/29 checks passed
```

---

## 快速开始

直接对 Agent 说：

> 用 character-persona-forge 给《黑神话：悟空》的“二郎神”做一份 quick 人格文档。

Skill 的第一条回复会先给：

1. 拟查官方来源
2. 角色级 S1 探测
3. 主要缺口
4. 目录方案
5. 待确认问题
6. 成本/时长提示

确认后才会联网、写文件。生成完成后，打开 `injection.md`，全选复制，贴进 AI 的自定义指令/角色设定/系统提示即可；找不到入口就当第一条消息发送。用户说“出戏 / OOC / 退出角色”时暂停角色。

更完整的普通用户说明见 `references/usage-guide.md`；进阶用法见 `references/runtime-integration.md`。

---

## 产出

| 文件 | 作用 | 是否注入 |
|---|---|---|
| `soul.md` | 我是谁、人格张力、动机、关系、知识/记忆边界、OOC 红线 | 是（CORE） |
| `style.md` | 语言指纹、分场景语体、官方台词、示例、风格红线 | 是（CORE） |
| `sources.md` | 来源、证据、推断、冲突、覆盖矩阵、自检与探针 | 否，供审计 |
| `injection.md` | 身份指令 + soul/style CORE 的一键复制包 | 是 |

默认目录：`personas/<游戏目录>/<角色名>/`。三份审计文档是源，`injection.md` 是派生便利文件。

---

## 重点优化与验证的游戏

这些游戏做过专门的来源整理、提示词校准和实测，人格文档生成效果更稳定；**不是支持范围的全部**。其它游戏按 `references/game-onboarding.md` 接入即可。

| 游戏 | 状态 | 固定主角称号 | 来源档案 |
|---|---|---|---|
| 原神 / Genshin Impact | curated | 旅行者 | `genshin.md` |
| 崩坏：星穹铁道 / Honkai: Star Rail | curated | 开拓者 | `hsr.md` |
| 绝区零 / Zenless Zone Zero | curated | 绳匠 | `zzz.md` |
| 鸣潮 / Wuthering Waves | curated | 漂泊者 | `wuwa.md` |
| 明日方舟 / Arknights | curated | 博士 | `arknights.md` |
| 明日方舟：终末地 / Arknights: Endfield | curated | 管理员 | `arknights-endfield.md` |
| 黑神话：悟空 / Black Myth: Wukong | provisional | 天命人 | `black-myth-wukong.md` |
| Hades | provisional | Zagreus | `hades.md` |
| Night in the Woods | provisional | Mae | `night-in-the-woods.md` |

来源档案均位于 `references/sources/`。

说明：

- **provisional** 表示该 pack 的接入信息尚未由用户确认，不阻止生成，但开工计划里必须说明。
- 游戏级来源地形为 A，不代表每个角色都有角色级 S1。黑神话就是 A 级游戏，但二郎神角色级 S1=0，最终 12/14 章标 `community-only` / `derived`。
- 任意游戏接入、A/B/C/D/E 定级和深度上限见 `references/game-onboarding.md`。

---

## 它是怎么制作人格文档的

| 阶段 | 产出 | 关键闸门 |
|---|---|---|
| 1. 开工计划 | 四行计划 + 成本/时长 + 确认 | 用户确认前不联网、不写文件 |
| 2. 来源发现 | 来源档案 + A/B/C/D/E 定级 | 无来源就停 |
| 3. 取证 | `sources.md` 来源表 + 证据表 | S1–S4 分级，社区转录标注 |
| 4. 冻结 ID | `[S##]` / `[E##]` / `[I##]` / `[C##]` | 先证据，后正文 |
| 5. 提取 | 身份、人格、动机、关系、边界、情绪、语言 | 只写可观察行为 |
| 6. 写作 | `soul.md` / `style.md` 的 CORE + APPENDIX | 核心区可独立注入 |
| 7. 校验 | validator + selftest | 结构、预算、矩阵、译文硬门禁 |
| 8. 验收与交付 | 12 OOC + 10 对抗探针、`injection.md` | FAIL 不交付 |

来源分级：S1 官方一手，S2 官方平台/授权，S3 社区 Wiki/转录，S4 考据/二创。关键结论优先用 S1；S3 只补缺口并标注“社区转录”。

详细步骤、失败模式和压缩顺序见 `references/workflow.md`；评分与关键失败项见 `references/quality-rubric.md`。

---

## 注入后如何维持长期对话

只把文档贴进系统提示还不够。推荐三层：

1. **系统层**：身份指令 + soul/style CORE 放进系统提示或持久指令。
2. **锚定层**：每 10–20 轮或工具调用后，贴一次 5–10 行身份锚。
3. **后置层**：宿主支持时，在对话末尾追加保持指令。

文档内的抗漂移设计包括：身份锚、OOC 状态机、知识/记忆边界、输出守卫和剧透闸门。完整说明和 51 个宿主映射见 `references/runtime-integration.md`。

---

## 验证与自检

要求 Python 3.9+，脚本只用标准库。

```bash
# 0. 新游戏接入（可选）
python scripts/game_profile.py init --id <id> --display-name "<展示名>" --title "<主角称号>" --landscape <A/B/C/D/E>
python scripts/game_profile.py game-check <id>

# 1. 游戏档案与回归
python scripts/game_profile.py check
python scripts/selftest.py

# 2. 生成期辅助
python scripts/persona_tools.py check personas/<游戏>/<角色>

# 3. 正式结构校验
python scripts/validate_persona.py personas/<游戏>/<角色> --strict --explain
```

`scripts/selftest.py` 覆盖 2 个正例 + 5 个反例 + Game Pack / `game-init` / 非中文译文 / 非中文 quote 配额 / research_depth 一致性等回归，目前 **29/29**。

常用子命令：

```bash
python scripts/persona_tools.py budget personas/<游戏>/<角色>
python scripts/persona_tools.py matrix-preview personas/<游戏>/<角色>
python scripts/persona_tools.py pack personas/<游戏>/<角色>
python scripts/probe_harness.py gen-prompts personas/<游戏>/<角色> --out-dir research/probe
```

---

## 质量门禁

- CORE 预算：quick ≤4,000；standard ≤8,000；deep ≤12,000 CJK。
- 来源/证据：quick ≤10 / 8–15；standard ≤25 / 20–40；deep ≤50 / 40–80。
- 覆盖矩阵：soul 1–8 + style 1–6 共 14 行；官方/社区计数必须与实际引用一致。
- 12 个 OOC 探针平均 ≥4.0，无 ≤2；10 个对抗探针平均 ≥4.0，无 ≤2。
- 被认真询问是否为 AI 时必须如实说明，不谎称现实人类。
- 露骨性内容、未成年性化、泄露未上线内容、冒充真实人物/诈骗为禁止级。

---

## 仓库架构

```text
character-persona-forge/
├── SKILL.md                 # Skill 入口与硬闸门
├── README.md / README.en.md # 中文优先的双语说明
├── AGENTS.md                # 仓库维护规则
├── THIRD_PARTY_NOTICES.md   # 第三方来源与许可
├── assets/
│   ├── templates/           # soul/style/sources/game-profile 模板
│   └── examples/            # standard/quick 正例
├── references/
│   ├── game-onboarding.md   # 任意游戏接入
│   ├── games/               # Game Pack JSON + schema
│   ├── sources/             # 每款游戏的来源档案
│   ├── workflow.md          # 端到端流程
│   ├── quality-rubric.md    # 评分与探针
│   └── runtime-integration.md
├── scripts/
│   ├── game_profile.py      # pack 校验 / init / game-check
│   ├── validate_persona.py  # 结构、预算、矩阵、译文校验
│   ├── persona_tools.py     # 预算、矩阵、注入包
│   ├── probe_harness.py     # 探针包与报告
│   ├── check_output.py      # 回复输出守卫
│   └── selftest.py          # 29 项回归
└── tests/                   # 反例 fixture 与生成器
```

---

## 新增游戏

1. 按 `references/game-onboarding.md` 做来源发现与 A/B/C/D/E 定级。
2. 用 `game-init` 生成 provisional pack、来源骨架和 index 条目。
3. 补全 `references/sources/<id>.md`，清掉 TODO。
4. 运行 `game-check` 到 `READY`；用户确认后把 `status` 改为 `curated`。
5. 更新 `references/source-registry.md`、双语 README，运行 `check` 与 `selftest.py`。

v1.7 只支持固定主角与连载/完结线性正典；可选/自定义/群像主角、多路线、重制、EA、沙盒字段已预留，暂不支持。D 级只做 quick 且需显式接受 CONDITIONAL；E 级拒绝生成。

---

## 适合与不适合

**适合：**

- 想给游戏角色做长期、可审计的人格文档；
- 需要 AI 在多轮对话里稳定保持角色语气；
- 想核查已有角色文档的来源、OOC 和边界。

**不适合：**

- 原创角色、纯数值/配队攻略、实时游戏代打；
- 只有角色名、没有任何可检索来源，且不愿提供材料；
- 只想生成一张角色卡或一段短提示词。

---

## 许可证与声明

本仓库原创文档、模板、脚本与示例按 **[CC BY-NC-SA 4.0](LICENSE)** 发布：允许署名、非商业性共享与 Adapt，衍生作品须以相同许可共享。

- **禁止商业使用**；商业授权请联系维护者。
- 游戏角色、名称、官方台词与设定版权归原权利方所有。
- 本仓库是粉丝制作的工作流工具，与 HoYoverse、miHoYo、Kuro Games、Hypergryph、Supergiant Games、Infinite Fall、Finji 无隶属或背书关系。
- 第三方社区转录来源与许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；仓库不打包剧本、字幕或语音原文。
- 引用官方内容仅用于评论、研究与风格校准，请遵守来源站点条款。

---

## Contributing

欢迎 Issue 和 PR。提交前请运行：

```bash
python scripts/selftest.py
python scripts/persona_tools.py check assets/examples/standard/qingxiao
python scripts/validate_persona.py assets/examples/standard/qingxiao --strict --explain
```

新增规则必须同时补反例 fixture 或回归检查；详见 `CONTRIBUTING.md`。
