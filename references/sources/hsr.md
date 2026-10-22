# 崩坏：星穹铁道来源

> 通用规则见 `common.md`；本文件只保留崩坏：星穹铁道专属入口、缺口、检索式与社区补缺。

## 2. 崩坏：星穹铁道

### 2.1 官方入口
| 名称 | URL | 内容类型 | 语言 | 访问与抽取备注 | 核实 |
|---|---|---|---|---|---|
| 国服官网 | https://sr.mihoyo.com/ | 角色页、新闻、PV 入口 | 中 | 纯 SPA；直接请求仅 CSS/埋点；需无头浏览器 | 已核实 |
| 角色页 | https://sr.mihoyo.com/?nav=character | 角色简介、称号、CV | 中 | 客户端渲染；搜索索引辅助 | 已核实入口 |
| 新闻页 | https://sr.mihoyo.com/news/{id} | 版本/活动公告、PV 图文 | 中 | 正文 SSR，可直接请求；无统一索引 | 已核实 |
| 国际服 | https://hsr.hoyoverse.com/zh-cn/home | 角色/新闻/媒体 | 中/英/日/韩 | Nuxt SSR，可直抓；与国服不完全同步 | 已核实 |
| 米游社区 | https://www.miyoushe.com/sr/ | 官方帖、公告、同人 | 中 | SPA；官方版块需登录 | 已核实 |
| 开拓者笔记 | https://bbs.mihoyo.com/sr/wiki/ | 角色图鉴、阅读物、影音回廊 | 中 | 官方平台+玩家维护；S2；SPA 外壳 | 已核实 |
| HoYoWiki | https://wiki.hoyolab.com/pc/hsr/home | 多语角色/语音/任务 | 多语 | 直连 403；需登录+无头 | 部分核实 |
| B站星铁 | https://space.bilibili.com/1340190821 | 角色 PV、千星纪游、动画短片 | 中 | 账号已核实；视频页有风控，需 cookie | 已核实账号 |
| 微博 @崩坏星穹铁道 | https://weibo.com/n/崩坏星穹铁道 | 立绘、短讯、角色档案图 | 中 | 302 游客验证/登录墙 | 部分核实 |
| YouTube | https://www.youtube.com/@HonkaiStarRail_ZH | PV/CM，多语 CC | 多语 | URL 来自官方商店文案；实测直连失败（2026-10-21） | 未核实 |

### 2.2 官方可直接取得
角色一句话简介+称号+中文 CV、版本/活动公告全文、PV/角色演示/千星纪游/动画短片的标题与简介、官方社媒短文案、开拓者笔记的角色基础数据与阅读物条目。

### 2.3 官方缺口（须社区补）
- 角色故事 Lv20/40/60/80 全文。
- 角色语音（问候/关于自己/星魂/战斗）文本与音频。
- 同行任务、开拓任务、冒险任务的完整对话。
- 模拟宇宙/差分宇宙事件、阅读物、短信、邮件。
- 历史版本公告索引；官方连载漫画（多为米游社同人，须区分）。

### 2.4 检索式
1. `site:sr.mihoyo.com 千星纪游 角色名`
2. `site:sr.mihoyo.com/news 版本 更新说明`
3. `site:bbs.mihoyo.com/sr/wiki 角色名 语音`
4. `site:wiki.biligame.com/sr 角色名 同行任务`
5. `site:honkai-star-rail.fandom.com "角色英文名" "Character Story"`
6. `site:zh.moegirl.org.cn 角色名 星穹铁道`
7. B站：`崩坏星穹铁道 角色名 角色PV`（限 space 1340190821）
8. 米游社：`开拓者笔记 角色名 语音`
9. `site:hoyolab.com 角色名 "voice lines"`
10. 微博：`崩坏星穹铁道 角色名 立绘`

### 2.5 社区补缺
| 来源 | URL | 强项 | 注意 |
|---|---|---|---|
| BWIKI 星铁 | https://wiki.biligame.com/sr/ | 任务全文、角色语音、阅读物、模拟宇宙、官方视频索引 | 静态 MediaWiki，直接请求可用；任务页含完整对话 |
| Fandom | https://honkai-star-rail.fandom.com/ | 角色故事 Part I-IV、语音原文+ogg | 直连常失败；需换 UA/镜像；英文 |
| 萌娘百科 | https://zh.moegirl.org.cn/崩坏：星穹铁道 | 角色条目、设定概述、梗 | 静态可抓；适合人格/口癖补缺 |
| Honey Hunter | https://hsr.honeyhunterworld.com/ | 角色数据、语音条目 | Cloudflare 403；需无头 |
| StarRailRes | https://github.com/Mar-7th/StarRailRes | 角色基础数据、图标、别名 | 无语音/剧情；适合建 ID/别名表 |

### 2.6 抽取顺序
官网/news 公告 → BWIKI 任务与语音 → Fandom `/Lore` 与 `/Voice-Overs` 交叉核对 → 萌娘补人格/口癖 → StarRailRes 建别名表。视频字幕优先 YouTube 官方双语频道；B站需 cookie，缺字幕再 ASR。

