# Changelog

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
