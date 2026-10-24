# Changelog

## 1.7.0 — 2026-10-24

> 首个支持“任意有来源的游戏接入”和“非中文原文 + 中文译文”的版本。六款 curated 游戏 + 黑神话：悟空、Hades、Night in the Woods 三款 provisional 试点；selftest 29/29。

### P0 — Game Pack 地基（2026-10-24）

- 新增 `references/games/index.json`、六份 curated Game Pack 与 `references/games/schema.md`；游戏名、别名、目录、主角称号、语言、正典与来源地形改为机器可读。
- 新增 `scripts/game_profile.py`：`check` / `list` / `resolve`，校验 pack 字段、别名/目录唯一性和来源档案存在性。
- `validate_persona.py` 改为动态读取 Game Pack，移除写死的游戏/称号常量；六款现有游戏行为保持不变，并新增 `game_slug` 一致性检查。
- selftest 扩到 **25/25**，新增 Game Pack 回归；P0 不改变现有产物格式。
- v1.7 试点确认为《黑神话：悟空》；自定义/可选主角、多路线、重制版等字段已预留但暂不支持。

### P1 — 任意游戏接入与黑神话试点（2026-10-24）

- 新增 `references/game-onboarding.md`：任意游戏的来源发现、A/B/C/D/E 定级、深度承诺、provisional pack 流程、失败模式与 v1.7 边界。
- 新增 `assets/templates/game-profile.json` 与 `assets/templates/game-source-profile.md`；`game_profile.py` 新增 `init` / `game-check`，支持脚手架、索引更新、TODO 检查、D 级 CONDITIONAL 闸门与 E 级拒绝。
- 新增《黑神话：悟空》来源档案与 provisional Game Pack（固定主角“天命人”，`complete` 线性正典）；记录官网无角色页、官方账号系列化、BWIKI“二郎显圣真君”页面标题、影神图/语音转录与剧透陷阱。
- `game-check` 按来源地形限制默认深度：A 最高 deep，B/C 最高 standard，D 仅 quick；`provisional` 不阻止生成但必须在开工计划中说明。
- selftest 扩到 **26/26**，新增 `game-init` 脚手架、重复拒绝、READY/INCOMPLETE/CONDITIONAL 闸门回归。
- **二郎神 quick 试点（PASS 86/100）**：14 条证据、4 个来源；发现“游戏级 A ≠ 角色级 A”——黑神话官网只有营销页，角色级 S1=0，14 个核心章节中 12 个只能标 `community-only` / `derived`，官方优先仅 8/15。已在 `game-onboarding.md` 新增 §3.1 角色级 S1 探测，并同步 `schema.md`、`source-policy.md`、`workflow.md`、`SKILL.md` 与双语 README。
- 模板、示例与派生 fixture 的 `forge_version` 升到 **1.7.0**；`game_slug` 占位提示加入 `black-myth-wukong`。文档与命令同步：SKILL、双语 README、AGENTS、CONTRIBUTING、schema、来源注册表。二郎神试点文档在本地 `personas/黑神话悟空/二郎神/`，未提交。

### P2 — 非中文原文流程（2026-10-24）

- `sources.md` §4 与 `style.md` §3/附录的 E 表新增可选最后一列 `中文译文（非中文必填）`；`原文` 列保留原语言原句，中文游戏填 `—`。列尾追加，兼容旧文档。
- 三份人格文档 frontmatter 新增 `source_languages` / `translation_policy` / `translation_source`；pack 的 `languages` 与文档声明会被交叉校验。
- `validate_persona.py` 新增：非中文流程每条 E 必须有中文译文、style 译文与 sources §4 一致、译文含中文、`official_zh` 与 `community_translation` 不得混标、`official_zh=false` 时禁止 `translation_policy=none`。
- 模板、schema、source-policy、workflow、SKILL 与双语 README 同步非中文规则；中文文档行为不变。
- selftest 扩到 **29/29**，新增译文映射、缺失/不一致、frontmatter 政策、非中文 quote 配额回归；用临时非中文 pack 做过端到端 strict PASS，并验证缺失译文会 FAIL。
- **真实场景验收（official_zh）**：新增《Hades》provisional pack 与来源档案。Megaera（墨纪拉）先做 quick 试点，再升 **standard**——英文原文 + 官方简中逐行对照，20 条证据、5 个来源，strict PASS，自评 **88/100**；删除一条中文译文后校验器正确 FAIL。
- **真实场景验收（community_translation）**：新增《Night in the Woods》provisional pack 与来源档案，以 Bea（碧娅）做 quick 试点——官方无中文，英文剧本 + 本文中文翻译，14 条证据，strict PASS，自评 **86/100**；删除一条中文译文后校验器正确 FAIL。游戏总数扩到 **9**（六款 curated + 黑神话/Hades/NITW provisional）。

### Review fixes（2026-10-24）

- A1：Night in the Woods pack 的官方语言补为 `["en", "ja"]`，与来源档案一致。
- A2：`game-init` 回归不再写死 “10 game packs valid”，改为先读基线数量再断言 +1。
- A3：`init` 读取损坏/缺失 `index.json` 时输出单行 FAIL，不再 traceback。
- A4：`game-check` 的 TODO 匹配改为词边界 `\bTODO\b`，与 persona 校验器口径一致。
- A5：`init --status` 只允许 `provisional`，堵住一步生成 curated 的旁路；schema 注明 `generic` 预留未用。
- A6：`official_zh` 推断接受简体/繁体（`zh` / `zh-CN` / `zh-Hans` / `zh-Hant` / `zh-TW`）。
- A7：`persona_tools.py pack` 的游戏展示名改为从 Game Pack 读取，删除 v1.6 残留硬编码。
- A8：表格解析支持转义竖线 `\|`；sources/style 模板注明原文含 `|` 时必须转义。
- A9：三份文档 `research_depth` 不一致时直接报错；新增 `fail_depth_mismatch` 反例 fixture，selftest **29/29**。
- B1（用户选方案 A）：非中文文档 `translation_required` 时 §3 引号上限 30→60、§4 80→160，CJK 上限不变；新增配额边界回归。
- B2（用户授权）：墨纪拉三份文档 H1 的“（quick）”改为“（standard）”，frontmatter 不变。
- B3（用户选删除）：移除 `game_profile.py init --official-zh` 参数；官方中文由 `languages.official` 的简繁集合推断。
- B4（用户选跳过）：五份来源档案的章节编号不重排。
- 独立盲评：Megaera standard 在 probe2 全量复测中 OOC **4.58** / 对抗 **4.60**（PASS，无 ≤2）；据此补 AU 固定句式、查证口令、示例句禁止复用等 CORE 规则；probe3 定向复测 9 题平均 **4.44**，示例复读已消除，查证顺序列为打磨项。
- 新增 `THIRD_PARTY_NOTICES.md`：记录 Hades/NITW 社区转录来源、无许可证声明、仅短句核对、不打包原始剧本/字幕；双语 README 的许可声明同步更新。

> C 类中“来源许可”已通过 NOTICE 与“不打包原文”收口；“standard 含金量”已完成独立盲评；发布流程与 WorkBuddy 补测仍待执行。

## 1.6.2 — 2026-10-24

- 交付说明改为默认“普通用户三步版”：新增 `persona_tools.py pack` 生成 `injection.md` 一键复制包（身份指令 + soul/style CORE），普通用户无需理解 CORE、宿主或系统提示。
- 校验器接受游戏全称别名（`明日方舟：终末地`、`崩坏：星穹铁道`），修复 SKILL 输入表与校验器口径不一致导致的返工。
- 模板说明文字移除会触发校验的 `[Sxx]` / `TODO` 字面；探针未执行状态统一为明确标记，strict 校验继续拦截残留标记。
- E 落点“用于章节”列改为正文定稿后按 `evidence-map` 回填；§7 必须按 `matrix-preview` 实际输出誊写，不得按设计意图手填；探针结果禁止预填。
- 终末地来源补充 BWIKI 首选入口、官网 SPA 边界、PRTS 角色页覆盖限制、搜索摘要错配与并行抓取上限。
- selftest 扩到 **24/24**，新增游戏全称别名回归。

## 1.6.1 — 2026-10-23

- 根据《明日方舟》维什戴尔执行记录：来源矩阵模板列全 14 个核心章节并说明 S/E/I→来源计数；新增 `persona_tools.py matrix-preview` 逐章显示实际来源、S1/社区数和覆盖状态。
- 探针模板明确 `TODO(未执行/未评分)`、最终分数单值规则；strict validator 阻止未清理的 TODO；CORE 改动后用新轻量上下文复测受影响题目。
- 补充 CORE 超预算压缩顺序，以及明日方舟 PRTS 反爬、语音槽位歧义和疑似时装语音混入等取证注意事项。

## 1.6.0 — 2026-10-23

- 新增《明日方舟》《明日方舟：终末地》来源档案、固定主角称号映射与独立 game slug；终末地与明日方舟的记忆/经历边界明确隔离。
- 更新 SKILL 输入表、工作流、来源注册/政策、模板、双语 README 与贡献说明；模板、清宵样例和派生 fixture 升至 `forge_version: 1.6.0`。
- 扩展 validator 的游戏名与固定玩家称号映射。

## 1.5.3 — 2026-10-22

- README 详解（中英同步）：新增“它是怎么制作人格文档的”，展开八阶段流水线、S1–S4 取证分级、两阶段冻结 ID、七维提取、CORE/APPENDIX 骨架与 12+10 探针。
- 新增“注入后如何维持长期对话”：三层注入、身份锚、OOC 状态机、输出守卫、最小可用流程、维护节奏与诚实的边界。
- 明确生成产物默认全中文；模板、示例与反例 fixture 同步升到 `forge_version: 1.5.3`。

## 1.5.2 — 2026-10-22

- 公开发布准备：中文优先双 README、25 个宿主说明、可扩展游戏来源架构、单 skill 仓库布局。
- 新增 `AGENTS.md`、`CONTRIBUTING.md`、`SECURITY.md`、GitHub Actions CI。
- 修复 Windows CI 的 fixture CRLF/LF 不一致；CI 4/4 jobs 通过。
- 许可证保持 **CC BY-NC-SA 4.0**。

## 1.5.1 — 2026-10-22

- 探针编排防重跑：`answers.md` 是唯一汇总文件；spawn 前必须检查是否存在且非空，`no-active-peer` 不等于失败。
- `probe_harness.py gen-prompts` 新增 `--out-dir`，推荐输出 `probe-package.md` + `answers.md`，避免把目录当成单文件。
- `persona_tools.py` 新增 `matrix-stub` 别名；分章配额明确标为 advisory，validator 只强制总预算。
- 新增规则：探针后改 CORE 必须复跑受影响探针，否则不得标 PASS。
- 首轮计划中的任务名/版本名/活动名未取证时标“待核实”。
- 原神来源笔记补充：B站官方投稿常无字幕、BWIKI 用 `curl.exe` + `action=raw`、语音页常为 `<角色名>语音` 独立页。
- selftest 扩到 23/23，新增 `probe_out_dir`。
- 新增中文优先的双语 README（`README.md` / `README.en.md`）；许可证从 MIT 切换为 **CC BY-NC-SA 4.0**。
- README 明确“当前内置四款游戏、来源架构可扩展”，补充 25 个主流宿主接入方式和正式仓库架构。
- 新增 `AGENTS.md`、`CONTRIBUTING.md`、`SECURITY.md`、`.github/workflows/selftest.yml`；单 skill 仓库采用根目录即 skill 的布局。
- 修复 Windows CI：`make_fixtures.py` 显式以 LF 写入并规范化 fixture，避免 CRLF/LF 哈希不一致。

## 1.5.0 — 2026-10-22

- standard 模板减负：人格核心 10 维表压到 6 维；时间线/相处场景/情绪细表默认移附录；分场景语体保留 6 个高频场景；每章加入 ASCII `BUDGET` 注释。
- 新增 `scripts/probe_harness.py`：抽取 CORE、生成 12+10 探针运行包、把回答整理成 §8.3/§8.7 草稿；不自动评分。
- 补宿主与取证细节：官方 SPA/搜索索引摘要口径、视频无逐字字幕口径、社区反爬策略、Windows PowerShell/UTF-8 说明、连载期角色形态。
- selftest 扩到 22/22，新增探针运行包与报告草稿冒烟测试。

## 1.4.0 — 2026-10-22

- 新增 `scripts/persona_tools.py`：`budget` 分章 CJK 配额、`evidence-map` 对比 §4 声明与正文实际 E 落点、`matrix` 生成 §7 草稿、`check` 汇总输出。
- 校验器新增 `--explain`：给 ERROR/WARN 附修复建议。
- 修复嵌套引号解析：`“...「...」...”` / `「...『...』...」` 不再被提前截断。
- 覆盖矩阵新增 coverage 标签：`partial` / `community-only` / `derived`（或中文等价）可放宽该行 S1 硬要求，避免硬塞 S1。
- workflow/selftest/SKILL 同步：压缩正文后必跑 `persona_tools check`；selftest 扩到 20 项。

## 1.3.4 — 2026-10-22

- 开工计划增加**成本/时长提示**：第一条回复必须说明本任务可能耗时较长、消耗较多 token，并在用户批准成本前停；`auto` 视为同时接受成本。
- 新增 `references/usage-guide.md`：交付时必须按模板告诉用户三份文件的作用、最短可用路径、宿主注入方式、保持人设与维护方法。
- `SKILL.md` / `workflow.md` / `confirmation.md` 同步更新；sources 模板 8.1 记录“计划已含成本/时长提示”。

## 1.3.3 — 2026-10-22

- 首轮硬闸门：无论参数是否齐全，第一条回复只输出四行开工计划并停；回答前禁止联网搜索、抓页面、写文件。只有明确 `auto` 才可同轮继续。
- 校验器增加来源/证据预算：quick ≤10 来源/8–15 证据；standard ≤25/20–40；deep ≤50/40–80。
- 校验器增加 E 原文一致性：`style.md` 引用的 E 原文必须与 `sources.md` §4 逐字一致。
- 新增 S4 规则：二创具体生活细节不得进核心，也不得借用官方 E/S ID；rubric 与 sources 模板增加自检项。
- 新增两阶段写入：先冻结来源/证据 ID，再写正文；rubric 增加 standard 章节字数配额表。
- style §4 增加“示范句不得作为回复首句”的防复读约束。
- `references/sources/zzz.md` 补 `?page=feature` / `?page=world` 技巧与“搜索标题≠正文”陷阱。
- selftest 增加 `over_evidence_budget`、`bad_evidence_text`，当前 18/18。

## 1.3.2 — 2026-10-22

- 确认分级拆出**禁止级**：露骨性内容、未成年性化、泄露未上线内容、冒充真实人物/诈骗直接拒绝，确认不能解锁。
- “写入已存在目录”统一归 A 级；B 级只保留开工计划（不涉及已存在目录）、深度、来源预算、新目录命名/版本号选择。
- 校验器新增硬门禁：三份 frontmatter 必须有 `forge_version`（X.Y.Z）；§8.7 必须有 10 项合法 1–5 分，平均 ≥4、无 ≤2、第 1/4/5/6 项不得为 1。
- selftest 增加 `missing_adversarial`、`bad_adversarial_scores`、`missing_forge_version`，当前 16/16；另加 fixture 派生同步检查。
- 可选润色：规则 6 明确“禁止级，不接受确认”；审计流程重打分时同步重跑 §8.7；rubric 注明 §8.7 表头必须是“得分(1-5)”。
- 修正审计流程笔误：总分变化写 §8.6，OOC 探针变化写 §8.3，对抗性探针变化写 §8.7。
- 修正 workflow 开工计划记录四态、来源文件映射表、confirmation 引号、source-policy 不可信输入措辞、quick 档 D/E 说明、标准 §8.7 标题。
- WorkBuddy 清宵样片补 `forge_version` 与 §8.7（quick CORE 压力测试存档），不改核心区。

## 1.3.1 — 2026-10-22

- 确认规则收敛：删除 `workflow.md §9` 的旧规则，只保留指针；`SKILL.md`、`workflow.md`、`soul`、`rubric` 统一引用 `confirmation.md` 的 A/B/C + `ask/auto`。
- 校验器补漏：CONDITIONAL 分数必须落在 70–84；12 条探针必须有 12 个可解析分数；`source_count/evidence_count` 非整数在 strict 下报错；矩阵子章节行可满足核心章节覆盖。
- 模板自洽：soul 模板补第 3 组人格张力；sources 模板补 `forge_version`、CONDITIONAL 占位、8.7 对抗性探针；quick soul/style 补信任横幅。
- 示例对齐：standard 清宵补 0.7、修正 0.1 残留与 §8.1 张力计数；style §4 删除“至少 3 个场景”旧句；quick 评分改用 8 项表、平均分改 4.83、补 8.7；附录 D/E 语义统一。
- 新增 `tests/make_fixtures.py`，四个反例改为从标准正例派生；`selftest.py` 增加输出守卫与两个漏洞回归，当前 12/12。
- 清理 `hsr.md` 内部备忘、runtime 宿主数 42→51、runtime 身份锚措辞、CHANGELOG 反例计数；补 `.gitignore`，清理 `__pycache__`；补 `source-policy` 抓取内容防注入。

## 1.3.0 — 2026-10-22

- 新增 `assets/examples/standard/qingxiao/` 与 `assets/examples/quick/qingxiao/` 两份正例，以及 `tests/fixtures/` 四个反例。
- 新增 `scripts/selftest.py`，2 正例 + 4 反例 + 解析/JSON/CONDITIONAL 覆盖。
- 新增 `references/audit-workflow.md`。
- 新增 `references/confirmation.md`，确认规则收敛为 A/B/C 三级。
- 新增 `references/adversarial-probes.md` 与 `scripts/check_output.py`。
- 新增 quick 瘦身模板 `soul.quick.md` / `style.quick.md`。
- 核心区负向规则改为 3+3+5，完整清单移附录 E。
- 新增玩法模式表（正典 / AU / OC / 旁白 / 用户演他角色）。
- 校验器：standard/deep 自动 strict；新增重复 ID、游戏↔称号、绝对否定 AI、引用配额、判断顺序、伪人格/张力数量、style §4 格式、来源域名启发式、日期/ID 检查；新增 `--json` 与 `--allow-conditional`，frontmatter 支持块列表/折叠块/一层嵌套键，矩阵支持 `soul 1.1` 子章节，幽灵 S1 检查覆盖零引用章节。
- 冷启动与盲评：standard/deep 默认新上下文跑探针并优先盲评；quick 无此能力时须注明“自测”。
- 来源注册表按游戏拆分到 `references/sources/`，总索引保留。
- 身份口径统一为“以角色身份说话，但底层是 AI，被认真询问时如实承认”。
- `style.md` 新增附录 D“完整示例对话（不注入）”，作为语气校准参照。
- 模板与正例新增 `forge_version` / `game_slug` / `character_slug`，便于审计与跨平台引用。
- 新增 `CHANGELOG.md` 与 MIT `LICENSE`；SKILL.md 版本号升到 1.3.0。
- SKILL.md frontmatter 收敛为标准键 + `metadata`，英文描述加引号，修复 `Honkai: Star Rail` 在严格 YAML 下截断的问题。
- 交接文档补充对抗性探针、输出守卫、来源拆分、版本追溯、完整示例与 ASCII 兼容检查项。

## 1.2.0 — 2026-10-22

- 修复身份双重性口径、确认分级、CONDITIONAL 交付口径。
- `--strict` 对 standard/deep 默认启用。
- 新增 `references/runtime-integration.md` 与 51 个宿主映射。
- `style` 示例改为“结构注记 + 一句示范”。

## 1.1.0 — 2026-10-21

- 修复剧透确认、示例复读、矩阵计数、章节引用与自评偏差。
- 新增章节级来源使用检查与示例复读扣分项。

## 1.0.0 — 2026-10-21

- 首版：四游戏来源注册表、soul/style/sources 模板、质量清单、校验脚本。
