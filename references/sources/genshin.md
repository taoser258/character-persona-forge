# 原神来源

> 通用规则见 `common.md`；本文件只保留原神专属入口、缺口、检索式与社区补缺。

## 1. 原神

### 1.1 官方入口
| 名称 | URL | 内容类型 | 语言 | 访问与抽取备注 | 核实 |
|---|---|---|---|---|---|
| 国服官网 | https://ys.mihoyo.com/ | 主页、角色、新闻、活动入口 | 中 | SPA；直接请求仅空壳，需浏览器 | 已核实 |
| 国服角色页 | https://ys.mihoyo.com/main/character/fontaine | 角色简介、称号、CV | 中 | 客户端渲染；正文需浏览器，搜索索引可辅助 | 部分核实 |
| 全球站 | https://genshin.hoyoverse.com/zh-cn/character/ | 多语角色页 | 中/英/日等 | 结构类似国服；地区内容可能不同步 | 部分核实 |
| 新闻/版本页 | https://ys.mihoyo.com/main/news | 版本公告、活动、PV 图文 | 中 | SPA；单篇正文需浏览器；可能有 JSON API，未验证 | 已核实入口 |
| 网页活动 | https://act.mihoyo.com/ys/event/ | 版本活动、小游戏文案 | 中 | 活动页生命周期短；及时存档 | 部分核实 |
| 米游社观测枢 | https://baike.mihoyo.com/ys/obc/ | 角色/任务/语音条目 | 中 | 官方托管、玩家编辑；S2；JS 渲染 | 已核实 |
| 米游社原神区 | https://www.miyoushe.com/ys/ | 官方帖、公告、同人 | 中 | 部分需登录；区分官方号与玩家帖 | 已核实 |
| B站原神 | https://space.bilibili.com/401742377 | 角色 PV/演示、版本 PV、短片 | 中 | 官方投稿常无字幕：API `subtitle.list` 可能为空；只取简介事实，不硬造台词 | 已核实 |
| 微博 @原神 | https://weibo.com/ysmihoyo | 立绘、短讯、角色档案图 | 中 | 登录墙/访客验证；部分内容不可达 | 部分核实 |
| HoYoLAB / HoYoWiki | https://wiki.hoyolab.com/pc/genshin/home | 多语 Wiki、角色/语音/任务 | 多语 | 实测 403（2026-10-21） 地区限制；需海外网络/登录 | 部分核实 |

### 1.2 官方可直接取得
角色页称号与简介、PV/角色演示中的台词与演出、版本公告、网页活动文案、官方社媒短文案、官方漫画/访谈。

### 1.3 官方缺口（须社区补）
- 游戏内全量语音（战斗/待机/受击/好感）及文字稿。
- 角色故事 1-5、神之眼/命之座文案。
- 魔神任务、传说任务、邀约事件、限时活动的完整对话。
- 旧版本文本（被后续版本改写/下线的剧情）。
- 生日邮件/信件、部分官方漫画章节。
- 角色页历史版本与已下线活动页。

### 1.4 检索式
1. `site:ys.mihoyo.com 角色名 角色PV`
2. `site:ys.mihoyo.com/main/news 角色名 版本`
3. `site:baike.mihoyo.com/ys 角色名 语音`
4. `site:wiki.biligame.com/ys 角色名 语音`
5. `site:wiki.biligame.com/ys 角色名 角色故事`
6. `site:wiki.biligame.com/ys 角色名 传说任务`
7. `site:genshin-impact.fandom.com "角色英文名" Voice-Overs`
8. `site:genshin-impact.fandom.com "角色英文名" Story`
9. B站：`原神 角色名 角色PV|角色演示|生日`
10. 米游社/观测枢：`角色名 语音|角色故事|传说任务`

### 1.5 社区补缺
| 来源 | URL | 强项 | 注意 |
|---|---|---|---|
| BWIKI 原神 | https://wiki.biligame.com/ys/ | 语音、角色故事、任务文本、版本 | 优先 `?action=raw`；`web_fetch` 可能被 TencentEdgeOne 拦截，改用 `curl.exe` + 浏览器 UA + `Accept-Language: zh-CN`；语音页常是 `<角色名>语音` 独立页，不是 `<角色名>/语音` 子页 |
| Fandom | https://genshin-impact.fandom.com/ | 英文语音、故事、任务、版本 | 实测常不可达；英文术语可做对照 |
| 萌娘百科 | https://mzh.moegirl.org.cn/原神 | 角色概览、语音摘录、梗 | JS 挑战；不适合当唯一来源 |
| Honey Hunter | https://genshin.honeyhunterworld.com/ | 多语语音/故事数据 | Cloudflare 403；可能含数据挖掘，须标来源性质 |

### 1.6 抽取顺序
官方公告/PV → 观测枢或 BWIKI 全量文本 → Fandom 英文交叉核对 → 萌娘/Honey 只补细枝末节。角色页正文抓不到时，不要凭搜索摘要写“官方原文”。

### 1.7 实测技巧与陷阱（2026-10-22）
- `ys.mihoyo.com` 新闻详情是 Nuxt SPA；普通 UA 可能只得空壳，`Googlebot` UA 有时触发 SSR，正文可能在 `article.content` 的 `\uXXXX` 转义里。
- 官方长文可能以图片发布：公告页只有两三句文字 + 长图时，文字内容要标“社区转录”，不得写成官方逐字文本。
- B站官方投稿的 API `subtitle.list` 常为空；没有字幕就只记录视频标题、简介与可核实演出事实。
- HoYoWiki / HoYoLAB 可能 403 或地区限制；微博可能 302 到访客墙。记录不可达即可，不要反复硬试。
- BWIKI 语音页命名不可猜：优先尝试独立页 `<角色名>语音`，再尝试 `<角色名>/语音` 等子页。

