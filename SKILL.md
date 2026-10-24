---
name: character-persona-forge
description: "Generate source-audited soul.md, style.md, and sources.md persona documents for characters from built-in games (Genshin Impact, Honkai: Star Rail, Zenless Zone Zero, Wuthering Waves, Arknights, Arknights: Endfield, Black Myth: Wukong, Hades, Night in the Woods) and other source-backed games via a game-onboarding gate. Use when creating, rebuilding, auditing, or updating a game-character persona for AI roleplay, or mentioning soul.md/style.md, 角色人格文档, 让AI扮演某角色, 原神/星铁/绝区零/鸣潮/明日方舟/终末地/黑神话/Hades/哈迪斯/林中之夜/NITW/博士/管理员/天命人/Zagreus/Mae."
# Qoder Agent Skills 扩展键；严格宿主可忽略，触发信息已包含在 description。
when_to_use: "用户要求为内置游戏或任意有可检索来源的游戏角色制作可注入 AI 的人格文档，或核查已有角色文档的还原度与来源。"
license: CC-BY-NC-SA-4.0
metadata:
  version: "1.7.0"
  description_zh: "为内置游戏与任意有可检索来源的游戏角色生成可注入 AI 的 soul.md、style.md 与 sources.md，含来源发现、官方取证、OOC 红线与自检报告。"
  description_en: "Generate source-audited persona documents for built-in games and arbitrary source-backed games, with onboarding, evidence grading, OOC boundaries, and self-checks."
---

# Character Persona Forge

> 本文件所在目录记为 `<SKILL_ROOT>`；下文所有 `references/`、`assets/`、`scripts/` 路径均相对于该目录。宿主若支持 `{SKILL_ROOT}`，按宿主规则替换。

> **第一条回复硬闸门（最高优先级）**
> 无论用户是否已给全参数、是否用 `Use Skill:` 调用，第一条回复必须先输出四行开工计划 + 成本/时长提示 + 一句“确认按这个计划和成本开工吗？”。计划里必须说明本任务可能耗时较长、消耗较多 token；用户批准成本前不得开始。在用户下一条明确回答前，**禁止联网搜索、抓取页面、调用浏览器、写文件**；可以读本 skill 的 references 以便列计划。
> 只有用户明确说“直接开始/不用问/跳过计划”时才进入 `auto`，视为同时批准成本，允许同一轮继续；否则必须停下等待。计划中的具体标题/版本名/活动名未取证时写“待核实”。没有计划、成本提示与确认记录，交付报告直接判流程失败。

## 概述

把一个游戏角色编译成三份可移植文档：`soul.md` 定义“我是谁”，`style.md` 定义“我怎么说”，`sources.md` 保存来源、证据、冲突和自检报告。

这不是同人设定生成器，而是“官方来源 → 证据分级 → 人格契约 → 自检”的取证流程。核心卖点是**可核查、少 OOC、官方来源优先**。当前内置九款游戏档案（六款 curated + 《黑神话：悟空》《Hades》《Night in the Woods》provisional）；其它游戏通过 `references/game-onboarding.md` 做来源发现与 Game Pack 接入，不需要改核心流程。

## 何时使用

使用：

- 用户要求为《原神》《崩坏：星穹铁道》《绝区零》《鸣潮》《明日方舟》《明日方舟：终末地》《黑神话：悟空》《Hades》《Night in the Woods》中的角色制作人格文档。
- 用户要求为上述之外、但**有可检索来源**的游戏角色制作人格文档；先走 `game-onboarding.md`。
- 用户提到 `soul.md`、`style.md`、角色人格、角色灵魂、让 AI 扮演某角色、角色 OOC 核查，或提到博士/管理员/天命人。
- 用户已有角色文档，要求补来源、修 OOC、更新剧情阶段或重做。

不使用：

- 原创角色、纯数值/配队攻略、实时游戏代打。
- 只有角色名、没有任何可检索来源，且用户拒绝提供材料。此时不要凭记忆硬写。
- v1.7 暂不支持可选/自定义/群像主角，多路线/重制/EA/沙盒正典；遇到先说明边界，不要偷换成一个固定主角硬做。

## 不可妥协的规则

> **开工闸门：** 正式生成前，先列出「拟查官方来源 / 主要缺口 / 输出目录处理方案 / 需要用户回答的问题」，给用户过目；按 `references/confirmation.md` 的 **B 级**处理。用户授权（“随便/你定/按你说的”）或明确进入 `auto`（“直接开始/不用问”）可继续；A 级事项仍须明确回答且本轮不执行。

1. **没有来源就不写。** 核心事实和台词必须有 `[Sxx]` / `[Exx]`；推断必须标 `[Ixx]`。
2. **官方优先。** 官方一手 > 官方平台社区编辑 > 社区 Wiki > 考据/二创。社区 Wiki 只补缺，并标注“社区转录”。
3. **台词逐字。** 引号内必须是可核实的原句；无法确认就转述，不加引号。
4. **不用泄露内容。** 只用已正式上线的剧情、台词和设定。
5. **固定主角称号。** 原神=旅行者，星铁=开拓者，绝区零=绳匠，鸣潮=漂泊者，明日方舟=博士，明日方舟：终末地=管理员，黑神话：悟空=天命人，Hades=Zagreus，Night in the Woods=Mae；新游戏以 pack 的 `default_title` 为准。不绑定玩家的性别、名字或选择。
6. **内容尺度。** 全年龄 + 轻度浪漫；不露骨，不性化未成年角色（禁止级，不接受确认）。
7. **不静默覆盖。** 输出目录已存在时，按 `references/confirmation.md` A 级提问确认更新/新建，本轮不写入。
8. **没联网就停。** 没有检索工具时，要求用户提供官方文本/链接/截图，禁止凭模型记忆生成。
9. **身份诚实。** 不谎称现实人类；被认真询问是否为 AI 时如实说明，可用角色世界观解释“载体”，但不把虚构设定说成现实事实。

## 输入

| 参数 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 游戏 | 是 | 无 | 内置游戏，或任意有可检索来源、已通过 `game-onboarding` 接入的游戏；角色名跨游戏时先确认 |
| 原文语言/译文来源 | 否 | 由 Game Pack 的 `languages` 决定 | 非中文游戏必须确认原文语言与译文来源；`sources.md` §4 / `style.md` §3 最后一列写中文译文，引用时标“译文” |
| 角色 | 是 | 无 | 常用名即可；多形态角色默认最新/主形态 |
| 深度 | 否 | `standard` | `quick` / `standard` / `deep` |
| 输出根目录 | 否 | 当前工作区 `personas/` | 用户可指定 |
| 阶段/身份层 | 否 | 最新状态 | 早期形态写入附录 A |
| 剧透闸门 | 否 | `latest` | 可改为“截至用户进度”或“无剧透” |

当前内置游戏与固定主角称号：

| 游戏 | 写入目录名 | 固定主角称号 |
|---|---|---|
| 原神 | `原神` | 旅行者 |
| 崩坏：星穹铁道 | `崩坏星穹铁道` | 开拓者 |
| 绝区零 | `绝区零` | 绳匠 |
| 鸣潮 | `鸣潮` | 漂泊者 |
| 明日方舟 | `明日方舟` | 博士 |
| 明日方舟：终末地 | `明日方舟终末地` | 管理员 |
| 黑神话：悟空（provisional） | `黑神话悟空` | 天命人 |
| Hades（provisional，P2 验收） | `Hades` | Zagreus |
| Night in the Woods（provisional，P2 社区译文验收） | `NightInTheWoods` | Mae |

角色有多个常用名、同名角色或重大形态时，列出 2-4 个候选让用户选；用户回答后才能继续，不要自作主张。用户没有指定深度时默认 `standard`，不追问深度；但开工计划仍必须先输出并等待确认/授权，不得因为参数齐全直接开工。

### 内置游戏之外的接入

不要跳过接入闸门直接写人格文档。先按 `references/game-onboarding.md` 做来源发现、A/B/C/D/E 定级和用户确认，再运行：

```bash
python scripts/game_profile.py init ...      # 生成 provisional pack + 来源骨架
python scripts/game_profile.py game-check <id>
```

只有 `game-check` 返回 `READY`（或用户显式接受 D 级 CONDITIONAL）后，才进入下面的来源取证流程。新游戏的固定主角称号以 pack 为准；用户未确认前不得替他选。

**游戏级 A 不等于角色级 A。** `game-check` 只校验游戏级 pack；开工计划必须再写目标角色是否有官方角色页、官方可逐字台词或官方设定资料。角色级 S1=0 时按 quick，或在 standard 中把对应章节标 `partial` / `community-only` / `derived`，并先告诉用户官方优先项会扣分。不要把官网首页、关卡名或无关公告写成角色级 S1。

**官方文本不是中文时**：`sources.md` §4 与 `style.md` §3 最后一列写中文译文，原文列保留原语言原句；frontmatter 填 `source_languages` / `translation_policy` / `translation_source`。引用写“译文”，不得把社区译文说成官方中文原句；校验器会强制译文存在且两处一致。

## 流程

1. **预检与开工计划**：确认游戏、角色、歧义、目录、联网；先输出“拟查官方来源 / 角色级 S1 探测 / 主要缺口 / 目录方案 / 待问问题”计划，按 `confirmation.md` B 级处理后再抓取或写文件；A 级事项仍须明确回答。首轮只出计划，不联网、不写文件。
2. **查来源**：先读 `references/sources/common.md` 的通用规则，再只读当前游戏对应的一份：原神→`genshin.md`，星铁→`hsr.md`，绝区零→`zzz.md`，鸣潮→`wuwa.md`，明日方舟→`arknights.md`，明日方舟：终末地→`arknights-endfield.md`，黑神话：悟空→`black-myth-wukong.md`，Hades→`hades.md`，Night in the Woods→`night-in-the-woods.md`；其它游戏读 `game-onboarding.md` 指向的 `sources/<id>.md`。把来源和原文摘录实时写进 `sources.md`。
3. **取证**：按 `references/source-policy.md` 分级、标注、裁决冲突；先冻结来源表与证据表，再写正文；核心结论至少 2 个独立来源交叉核对（standard）。
4. **提取**：身份层、人格张力、核心动机、关系、知识/记忆边界、情绪、语言指纹。
5. **撰写**：复制 `assets/templates/` 三份模板到输出目录（quick 档用 `soul.quick.md` + `style.quick.md`），只引用已冻结的来源/证据 ID；先写核心区，再写附录；至少写 3 个角色专属伪人格和回应前的判断顺序；写清被问“你是不是 AI”时的角色式处理；删除模板注释和占位符。
6. **自检**：先运行 `scripts/persona_tools.py check <输出目录>` 看预算、E 落点和矩阵 stub；再运行 `scripts/validate_persona.py <输出目录> --strict --explain`（standard/deep 自动 strict）；首次使用或修改校验器后先跑 `scripts/selftest.py`；探针测试用 `scripts/probe_harness.py gen-prompts <输出目录> --out-dir research/probe`，把回答写入 `research/probe/answers.md`，把结果写进 `sources.md` 第 8 节（对抗记录用 8.7）。
7. **交付**：先运行 `scripts/persona_tools.py pack <输出目录>` 生成 `injection.md`（身份指令 + soul/style CORE）。报告路径、来源数量、主要缺口/冲突、探针得分与判定；自检 FAIL 不交付。默认按 `references/usage-guide.md` 的**普通用户版**说明三步用法；只有用户明确问 CORE、宿主、系统提示或开发接入时，再展开进阶版。

详细步骤和失败模式见 `references/workflow.md`。

## 深度档

| 档位 | 来源上限 | 证据数 | 核心要求 | 适用 |
|---|---:|---:|---|---|
| `quick` | 10 | 8-15 | 每个核心章节 ≥1 条 S1；可接受较多缺口 | 冷门角色、先出草稿 |
| `standard` | 25 | 20-40 | 官方角色页 + 官方 PV/演示 + 主线/角色任务关键场景 + 语音/漫画/公告；关键结论交叉核对 | 默认 |
| `deep` | 50 | 40-80 | 全剧情出场、全语音、版本变更、跨语言语气对照、完整关系与冲突矩阵 | 重点角色、验收样片 |

来源数只设上限，不设下限：资料不足时在缺口节写清，不用低质来源凑数；但每个核心章节的 S1 覆盖必须达标。

## 输出契约

```
personas/<中文游戏名>/<中文角色名>/
├── soul.md
├── style.md
├── sources.md
└── injection.md   # 可选：pack 生成的一键复制包
```

- 默认游戏目录由 Game Pack 的 `directory` 决定：`原神`、`崩坏星穹铁道`、`绝区零`、`鸣潮`、`明日方舟`、`明日方舟终末地`、`黑神话悟空`、`Hades`、`NightInTheWoods`；新游戏以 `game-init` 生成或用户指定的目录为准。
- `injection.md` 是派生便利文件，不替代三份审计文档；修改 soul/style 后重新运行 `persona_tools.py pack` 即可更新。
- `soul.md` 和 `style.md` 都分 **CORE** 与 **APPENDIX**：核心区可单独注入，附录放阶段细节、扩展语料和证据索引。
- `sources.md` 不参与注入，用于人工核查与后续更新。
- 默认中文目录；需要跨平台/CI 时可在 frontmatter 填 `game_slug` / `character_slug`，或约定 `personas/<game_slug>/<character_slug>/` 的 ASCII 路径，报告仍显示中文名。目录最终按用户指定。
- 推荐注入方式：把 `soul.md` + `style.md` 一起给 agent，并附一句“读取这两份文档，以其中角色身份对话，遵守文档内的运行规则”。上下文紧张时只注入核心区。

## 运行时集成

生成的文档是内容，不是强制机制。要让 agent **始终以角色身份交流、用户不主动取消不退场**，需要按 `references/runtime-integration.md` 做三层注入：

1. **系统层**：把身份指令 + soul/style 核心区贴进 agent 的系统提示词 / 持久指令（`CLAUDE.md`、`AGENTS.md`、`.cursorrules`、GPT Instructions 等）。
2. **锚定层**：每 10–20 轮或工具调用后，贴一次 5–10 行的身份锚。
3. **后置层**：如宿主支持（如 SillyTavern），在对话末尾注入保持指令。

该指南还包含 51 个主流宿主的映射表、OOC 状态机、输出守卫清单和安全层级说明。

## 自检闸门

- 开工计划已按 `confirmation.md` B 级处理（已确认 / 已授权 / `auto` / 无回答按默认执行并说明）；若涉及 A 级事项，均已明确回答。
- **PASS**（≥85 且无关键失败）→ 直接交付。
- **CONDITIONAL**（70–84 且无关键失败）→ 必须列出剩余缺口，由用户明确接受后才交付；校验时加 `--allow-conditional`，否则脚本按失败处理。
- **FAIL**（<70 或任一关键失败）→ 不交付。
- OOC 探针平均 ≥4.0 且无单项 ≤2；对抗性探针平均 ≥4.0、无 ≤2，记录在 `sources.md` §8.7。
- 三份 frontmatter 均有 `forge_version`；§8.7 有 10 项合法 1–5 分，第 1/4/5/6 项不得为 1。
- 来源/证据数量在档位预算内（quick 10/8–15，standard 25/20–40，deep 50/40–80）。
- `style.md` 中 E 原文与 `sources.md` §4 逐字一致；核心区无 S4 二创具体细节。
- 章节确无官方直接覆盖时，用 coverage 标签 `partial` / `community-only` / `derived`，不要硬塞 S1。
- 所有核心事实有来源 ID；所有引用 ID 在 `sources.md` 中存在。
- 章节引用均指向存在的标题；覆盖矩阵的官方/社区计数与来源级别一致。
- 无未替换占位符、无模板注释、无断链、无泄露剧情、无二创冒充正典。
- 冷启动测试：只给核心区，问日常/冲突/知识边界三个问题；被认真问“你是不是 AI”时不否认、不谎称真人；不编造设定或共同记忆。
- 露骨性内容、未成年性化、泄露未上线内容直接拒绝，不走确认；重剧透、身份层切换、写入已存在目录、同名角色选择按 A 级先提问确认，不先执行。
- `style.md` §4 使用“结构注记 + 一句示范”，示范 ≤12 字、只给语气，不得有完整可粘贴回复；回复中不得出现示例的连续 ≥8 个汉字片段。
- 自评抽查 3 条，优先检查“5 分/无问题”；自评分与外部复核分差不超过 1 分。
- standard/deep 默认用全新上下文跑探针，并优先由另一个上下文盲评；quick 无法新开上下文时须注明“自测”。

## 资源

| 文件 | 用途 |
|---|---|
| `assets/templates/soul.md` | 人格文档模板（standard/deep） |
| `assets/templates/style.md` | 语言风格模板（standard/deep） |
| `assets/templates/sources.md` | 来源/证据/自检模板 |
| `assets/templates/soul.quick.md` | quick 档瘦身人格模板 |
| `assets/templates/style.quick.md` | quick 档瘦身风格模板 |
| `assets/examples/standard/qingxiao/` | standard 完整正例，仅作格式参考 |
| `assets/examples/quick/qingxiao/` | quick 完整正例，含 8 来源 / 12 证据的压缩写法 |
| `references/workflow.md` | 端到端流程、深度档、失败模式 |
| `references/audit-workflow.md` | 已有文档的审计与更新流程 |
| `references/confirmation.md` | A/B/C 三级确认标准（唯一口径） |
| `references/usage-guide.md` | 交付后给用户的使用说明模板：默认普通用户三步版；进阶用户再给 CORE/宿主/维护细节 |
| `references/source-policy.md` | 来源分级、引用规则、冲突裁决、安全边界、引用配额 |
| `references/source-registry.md` | 人类可读来源索引（指向 `sources/` 下各游戏文件） |
| `references/game-onboarding.md` | 任意游戏接入：来源发现、A/B/C/D/E 定级、provisional pack、`game-init`/`game-check` 闸门、v1.7 边界 |
| `references/games/index.json` | 机器可读游戏索引（六款 curated + 黑神话：悟空/Hades/Night in the Woods provisional） |
| `references/games/<id>.json` | 游戏档案：名称/别名、目录、主角称号、语言、正典、来源地形、验证参数 |
| `references/sources/common.md` | 通用检索规则、跨游戏质量规则 |
| `references/sources/genshin.md` | 原神官方入口、缺口、检索式、社区补缺 |
| `references/sources/hsr.md` | 星铁官方入口、缺口、检索式、社区补缺 |
| `references/sources/zzz.md` | 绝区零官方入口、缺口、检索式、社区补缺 |
| `references/sources/wuwa.md` | 鸣潮官方入口、缺口、检索式、社区补缺 |
| `references/sources/arknights.md` | 明日方舟官方入口、缺口、检索式、社区补缺 |
| `references/sources/arknights-endfield.md` | 明日方舟：终末地官方入口、缺口、检索式、社区补缺 |
| `references/sources/black-myth-wukong.md` | 黑神话：悟空官方入口、影神图/语音缺口、二郎神取证陷阱 |
| `references/sources/hades.md` | Hades 官方英文/官方简中、字幕转储、Megaera 取证边界 |
| `references/sources/night-in-the-woods.md` | Night in the Woods 官方无中文、英文剧本、Bea 取证边界 |
| `references/quality-rubric.md` | 100 分评分、关键失败项、12 个 OOC 探针 |
| `references/runtime-integration.md` | 运行时集成指南：让 agent 始终以角色身份交流，用户不主动取消不退场 |
| `references/adversarial-probes.md` | 运行时对抗性探针：注入、长对话漂移、工具调用、剧透施压等 10 项 |
| `scripts/game_profile.py` | 游戏档案加载/校验/解析、接入闸门（`check` / `list` / `resolve` / `init` / `game-check`） |
| `scripts/validate_persona.py` | 本地结构校验脚本（Python 3 标准库；standard/deep 自动 strict；游戏名与主角称号从 Game Pack 读取） |
| `scripts/persona_tools.py` | 生成期辅助：分章预算、E 落点对比、§7 矩阵草稿与覆盖预览（E/I→S）、`pack` 一键注入包 |
| `scripts/probe_harness.py` | 抽取 CORE、生成 12+10 探针运行包、把回答整理成 §8.3/§8.7 草稿 |
| `scripts/selftest.py` | 29 项回归（2 正例 + 5 反例 + Game Pack + 游戏别名 + game-init 接入闸门 + 非中文译文校验 + 非中文 quote 配额 + research_depth 一致性 + 解析/JSON/CONDITIONAL/输出守卫/漏洞/8.7/forge/预算/E 一致性/fixture 同步/工具与探针冒烟/探针目录输出） |
| `tests/make_fixtures.py` | 从标准正例派生四个反例，避免多份拷贝漂移 |
| `scripts/check_output.py` | 回复输出守卫：检查客服腔、AI 自指、总结式收尾等 OOC 标记 |
