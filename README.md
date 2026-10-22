# Character Persona Forge

[English](README.en.md) | **简体中文**

[![Version](https://img.shields.io/badge/version-1.5.1-blue.svg)](#)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![selftest](https://img.shields.io/badge/selftest-23%2F23-brightgreen.svg)](#验证与自检)

> 把游戏角色编译成**可审阅、可注入、可验证**的人格文档。

`character-persona-forge` 是一个 Agent Skill：为《原神》《崩坏：星穹铁道》《绝区零》《鸣潮》角色生成三份可移植文档——`soul.md`、`style.md`、`sources.md`。它不是让模型“凭印象写角色卡”，而是把**官方来源、证据分级、人格边界、运行时注入、自检测试**串成一条可审计的流水线。

---

## 为什么不是普通角色卡

| 普通角色卡 | Character Persona Forge |
|---|---|
| 设定与台词常无出处 | 每条核心事实和台词都有 `[S##]` / `[E##]` 来源编号 |
| 角色聊几轮就变回助手 | 提供 CORE 注入、身份锚、后置指令与 OOC 状态机 |
| 只写“像不像” | 12 个 OOC 探针 + 10 个对抗性探针 + 冷启动测试 |
| 无法判断什么时候可以交付 | 预算、矩阵、E 落点、引用配额、身份安全都有硬门禁 |
| 换宿主就失效 | 同一套文件可被 Claude Code、Codex、Trae、Qoder、WorkBuddy、DSH 等宿主读取 |

---

## 产出

```text
personas/<游戏>/<角色>/
├── soul.md      # 我是谁：身份、经历、动机、关系、知识边界、OOC 红线
├── style.md     # 我怎么说：语域、句式、口癖、示例、风格红线
└── sources.md   # 证据档案：来源、原文、推断、冲突、覆盖矩阵、自检报告
```

`soul.md` 与 `style.md` 都分为 **CORE** 与 **APPENDIX**。CORE 可单独注入，APPENDIX 保存阶段细节、扩展语料和证据索引；`sources.md` 不参与注入，只用于审计和后续更新。

---

## 核心能力

- **官方来源优先**：S1 官方一手 > S2 官方平台 > S3 社区 Wiki > S4 考据/二创；缺口必须标注“社区转录”。
- **两阶段写入**：先冻结来源表与证据 ID，再写正文，避免“先写正文再补来源”的返工。
- **CORE 可移植**：核心区自包含，附录按需加载，控制上下文成本。
- **运行时集成**：三层注入模型、OOC 状态机、51 个宿主映射、输出守卫。
- **工具链**：分章预算、E 落点对比、§7 矩阵 stub、探针运行包、结构校验器。
- **双语触发**：支持中文与英文角色名、游戏名触发。

---

## 安装

把整个 `character-persona-forge/` 目录复制到宿主的 skills 目录。

| 宿主 | 常见全局路径 | 项目级路径 |
|---|---|---|
| Claude Code | `~/.claude/skills/character-persona-forge/` | `.claude/skills/character-persona-forge/` |
| Codex / 通用 Agent Skills | `~/.agents/skills/character-persona-forge/` | `.agents/skills/character-persona-forge/` |
| DeepSeek Harness (DSH) | `~/.dsh/skills/character-persona-forge/` | `.dsh/skills/character-persona-forge/` |
| Trae CN | `~/.trae-cn/skills/character-persona-forge/` | `.trae/skills/character-persona-forge/` |
| Trae 国际版 | `~/.trae/skills/character-persona-forge/` | `.trae/skills/character-persona-forge/` |
| Qoder | `~/.qoder/skills/character-persona-forge/` | `.qoder/skills/character-persona-forge/` |
| WorkBuddy | `~/.workbuddy/skills/character-persona-forge/` | 按宿主项目约定 |

安装后重启或重新加载宿主，然后说：

```text
使用 character-persona-forge，制作《原神》角色纳西妲的人格文档
```

也可以直接点名：

```text
Use Skill: character-persona-forge
```

---

## 使用流程

1. **计划闸门**：第一条回复只输出四行计划 + 成本/时长提示 + 确认问句；用户批准前不联网、不写文件。
2. **取证**：先官方、后社区；边查边写 `sources.md`。
3. **冻结 ID**：来源表与证据表先定稿，正文只引用已定义 ID。
4. **写正文**：先写 `soul.md` / `style.md` 的 CORE，再补附录。
5. **自检**：跑预算、E 落点、矩阵、结构校验、12+10 探针。
6. **交付**：报告路径、来源数、缺口、探针分数，并附使用方法。

---

## 验证与自检

要求 Python 3.9+，全部脚本只用标准库。

```bash
# 1. 校验器自身回归
python scripts/selftest.py

# 2. 生成期辅助：分章预算 / E 落点 / 矩阵 stub
python scripts/persona_tools.py check personas/<游戏>/<角色>

# 3. 正式结构校验
python scripts/validate_persona.py personas/<游戏>/<角色> --strict --explain
```

常用子命令：

```bash
python scripts/persona_tools.py budget personas/<游戏>/<角色>
python scripts/persona_tools.py evidence-map personas/<游戏>/<角色>
python scripts/persona_tools.py matrix-stub personas/<游戏>/<角色>
python scripts/probe_harness.py gen-prompts personas/<游戏>/<角色> --out-dir research/probe
python scripts/check_output.py reply.md
```

---

## 质量门禁

- CORE 预算：quick ≤4,000；standard ≤8,000；deep ≤12,000 CJK。
- 来源/证据：quick ≤10 / 8–15；standard ≤25 / 20–40；deep ≤50 / 40–80。
- 覆盖矩阵：soul 1–8 + style 1–6 共 14 行，官方/社区计数必须与实际引用一致。
- 12 个 OOC 探针平均 ≥4.0，无 ≤2。
- 10 个对抗性探针平均 ≥4.0，无 ≤2；第 1/4/5/6 项不得为 1。
- 被认真询问是否为 AI 时必须如实说明，不谎称现实人类。
- 露骨性内容、未成年性化、泄露未上线内容、冒充真实人物/诈骗为禁止级，不走确认流程。

---

## 仓库结构

```text
.
├── SKILL.md                  # 技能入口
├── README.md                 # 中文说明（默认）
├── README.en.md              # English README
├── CHANGELOG.md
├── LICENSE                   # CC BY-NC-SA 4.0
├── references/               # 流程、确认、来源政策、评分、运行时集成
├── assets/
│   ├── templates/            # soul/style/sources 模板（standard + quick）
│   └── examples/             # 标准档 / quick 档参考样例
├── scripts/                  # 校验器、生成辅助、探针 harness
└── tests/                    # 反向回归 fixture
```

---

## 适合与不适合

**适合：**

- 想给游戏角色做可长期使用的人格文档；
- 需要区分“官方设定 / 社区转录 / 推断”；
- 想在不同 Agent 宿主之间复用同一套人格；
- 需要可回归的 OOC 与边界测试。

**不适合：**

- 纯角色卡美化、头像生成、数值攻略；
- 没有来源且拒绝提供材料的“凭记忆硬写”；
- 想绕过平台安全策略、冒充真人或使用泄露内容。

---

## 许可证与声明

本仓库的原创文档、模板、脚本与示例按 **[CC BY-NC-SA 4.0](LICENSE)** 发布：允许署名、非商业性共享与 Adapt，但衍生作品须以相同许可共享。

> 说明：Creative Commons 官方不建议将 CC 许可用于软件本身。本项目按你的要求统一使用该许可；如需将脚本用于商业或软件分发场景，请联系维护者讨论单独授权。

- **禁止商业使用**；如需商业授权，请联系维护者。
- 游戏角色、名称、官方台词与设定版权归原权利方所有。
- 本仓库是粉丝制作的工作流工具，与 HoYoverse、miHoYo、Kuro Games 无隶属或背书关系。
- 引用官方内容仅用于评论、研究与风格校准，请遵守来源站点条款，避免批量抓取。
- 生成文档用于个人非商业角色扮演；发布到公开平台前请自行确认当地法律与平台规则。

---

## Contributing

欢迎提交 issue / PR。提交前请至少运行：

```bash
python scripts/selftest.py
```

新增规则时请同时补一个反例或回归检查，避免“文档写了、脚本没查”。
