# 鸣潮来源

> 通用规则见 `common.md`；本文件只保留鸣潮专属入口、缺口、检索式与社区补缺。

## 4. 鸣潮

### 4.1 官方入口
| 名称 | URL | 内容类型 | 语言 | 访问与抽取备注 | 核实 |
|---|---|---|---|---|---|
| 库洛游戏官网 | https://www.kurogames.com/ | 企业站/产品入口 | 中/英 | SPA；直接请求仅标题 | 已核实 |
| 鸣潮中文站 | https://mc.kurogames.com/ | 首页、共鸣者情报、版本 PV、活动 | 中 | Vite SPA；静态 HTML 不含角色文本；需浏览器 | 已核实 |
| 鸣潮全球站 | https://wutheringwaves.kurogames.com/en/ | 多语主页 | 英/日/韩等 | SPA；任意路径常返回同一页面；无独立角色页 | 已核实 |
| 库街区 | https://www.kurobbs.com/mc/ | 公告/活动/帖子 | 中 | SPA；浏览公开，互动需登录 | 已核实 |
| 库街区 WIKI | https://wiki.kurobbs.com/mc/home | 图鉴/攻略 | 中 | 官方域名托管+玩家编辑；S2；非官方撰写 | 已核实 |
| B站鸣潮 | https://space.bilibili.com/1955897084 | 角色 PV/演示、版本 PV、动态 | 中 | 账号已比对；搜索 API 需 Cookie | 已核实 |
| 微博 @鸣潮 | 账号名“鸣潮”（URL 未核实） | 图文/公告/立绘 | 中 | 302 访客墙；需登录 | 部分核实 |
| YouTube | https://www.youtube.com/@WutheringWaves | 角色演示/版本 PV（含 CC） | 多语 | 实测不可达（2026-10-21）；据官方商店描述佐证 | 部分核实 |
| X | https://twitter.com/Wuthering_Waves | 短讯/立绘 | 英 | 需登录，未取到内容 | 未核实 |

### 4.2 官方可直接取得
共鸣者情报一句简介+立绘、版本 PV/角色演示、活动公告、官方社媒短文案、库街区公告。官方“共鸣者档案”通常不足以支撑人格文档。

**关键事实：鸣潮没有官方角色故事/语音文本页。** 官方能给的主要是简介、PV 条目、展示文案与公告；五段角色故事、珍贵之物、频谱/超频报告、主线全流程都在社区 Wiki。不要把“官网有角色页”当成官方故事文本。

### 4.3 官方缺口（须社区补）
- 官方没有角色故事/语音文本页；角色故事、珍贵之物、频谱/超频报告、主线全流程只能靠社区转录或录屏。
- 游戏内“角色故事/档案”全文、伴星任务完整对白、主线剧情文本：官网零覆盖。
- 语音的解锁条件、好感度分级、中/英/日多语对照：官方无公开对照表。
- 视频字幕只覆盖 PV/演示，不含游戏内对话；B站官方稿无字幕轨，需 ASR。
- 微博登录墙、YouTube 不可达时，社媒一手料获取成本最高。

### 4.4 检索式
1. `site:wuwa.huijiwiki.com 角色名 档案`
2. `site:wuwa.huijiwiki.com 角色名 经历`
3. `site:wiki.biligame.com/wutheringwaves 角色名 语音`
4. `site:wiki.biligame.com/wutheringwaves 角色名 角色故事`
5. `site:wiki.biligame.com/wutheringwaves 角色名 伴星任务`
6. B站：`鸣潮 角色名 伴星任务|角色演示|语音`
7. `site:kurobbs.com/mc 角色名 共鸣者档案`
8. `site:zh.moegirl.org.cn 角色名 鸣潮`
9. `site:wutheringwaves.fandom.com "英文名" voice-overs`
10. YouTube：`Wuthering Waves Character Demo 英文名`

### 4.5 社区补缺
| 来源 | URL | 强项 | 注意 |
|---|---|---|---|
| BWIKI 鸣潮 | https://wiki.biligame.com/wutheringwaves/ | 角色页、语音、档案、伴星任务 | MediaWiki；curl 有反爬，直接请求/浏览器 UA 可过；单页 50+ 条中文台词 |
| 灰机wiki 鸣潮 | https://wuwa.huijiwiki.com/ | 角色档案、经历、珍贵之物、频谱/超频报告、部分语音 | 角色故事与主线全流程的最佳来源；S3，必须标“社区转录” |
| Fandom | https://wutheringwaves.fandom.com/ | 英文剧情/语音转录 | 实测不可达（2026-10-21）；需换网络 |
| 萌娘百科 | https://zh.moegirl.org.cn/鸣潮 | 角色/设定/声优 | 403 反爬；直接请求可读 |
| Prydwen | https://www.prydwen.gg/wuthering-waves/ | 数值/配队/Tier | 攻略站，S4；不作为剧情事实 |
| WuWa Tracker | https://wuwatracker.com/ | 抽卡记录/资源 | 无剧情；不用于人格 |

### 4.6 抽取顺序
官网/库街区等 `networkidle` 后取 DOM → 灰机wiki 角色档案/经历 → BWIKI 角色页/语音 → B站/YouTube 演示字幕 → Fandom/萌娘交叉核对。不要按 URL 猜官网角色页；鸣潮没有纯官方 Wiki，也没有官方角色故事/语音文本页。

