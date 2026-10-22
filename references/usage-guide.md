# 交付后使用说明

> 用途：人格文档通过自检后，把这里的“交付说明模板”原样或压缩后告诉用户。
> 本文件是给用户的操作说明，不是运行时注入内容；不要把本文件贴进聊天 agent。

---

## 交付说明模板

```text
已生成 3 份文件：
- soul.md：定义“我是谁”——身份、动机、关系、知识边界、OOC 红线。
- style.md：定义“我怎么说”——语气、句式、口癖、示例与负向风格规则。
- sources.md：证据、来源、冲突与自检报告；这是审计档，不要注入给聊天 agent。

最短可用：
1. 新开一个会话。
2. 只贴 soul.md 和 style.md 的 CORE 区（不要贴附录，不要贴 sources.md）。
3. 在末尾加一句：“读取这两份文档，以其中角色身份对话，遵守文档内的运行规则。”
4. 测试三问：日常问候、冲突/求助、知识边界；再认真问一次“你是不是 AI”。

想长期保持人设：
- 把身份指令 + CORE 区放进宿主的持久指令/系统提示位。
- 每 10–20 轮，或在工具调用后，贴一次 soul/style 里的身份锚。
- 想退出角色时直接说“出戏”。
- 各宿主的具体注入位置见 references/runtime-integration.md 的宿主映射表。

维护：
- 改动文档后需要新开会话才会生效。
- 校验用 scripts/validate_persona.py <目录> --strict。
- sources.md 留作审计与后续更新，不要当聊天上下文。
```

---

## 按宿主的快捷说明

| 宿主 | 最省事做法 |
|---|---|
| Claude Code / Codex / Trae / Qoder | 把 CORE 区放进项目规则（`CLAUDE.md` / `AGENTS.md` / `.trae/rules` 等），或直接粘贴 |
| Cursor / Windsurf | 放进 Rules；上下文紧张时只贴 CORE 区 |
| SillyTavern / 角色卡类宿主 | `description` ← soul CORE；`personality` ← style 摘要；`post_history_instructions` ← 保持指令 |
| 网页版 ChatGPT / Claude / Gemini | 自定义指令里贴身份指令 + CORE 区；上下文紧张时只贴 CORE |
| WorkBuddy | 放进自定义 Agent 指令，或直接粘贴 |

更完整的 51 个宿主映射见 `references/runtime-integration.md` §6。

---

## 交付时应避免的说法

- 只说“文件已生成”，不给使用方法。
- 让用户把 `sources.md` 也注入给聊天 agent。
- 让用户整份贴 soul/style（含附录）；默认只注入 CORE 区。
- 不提醒“改文档后要新开会话”。
