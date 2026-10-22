# 绝区零来源

> 通用规则见 `common.md`；本文件只保留绝区零专属入口、缺口、检索式与社区补缺。

## 3. 绝区零

### 3.1 官方入口
| 名称 | URL | 内容类型 | 语言 | 访问与抽取备注 | 核实 |
|---|---|---|---|---|---|
| 国服官网 | https://zzz.mihoyo.com/ | 主页、设定档案、活动 | 中 | Nuxt SPA；HTML 仅空壳；需浏览器 | 部分核实 |
| 全球站 | https://zenless.hoyoverse.com/zh-cn/ | 多语主页/角色 | 中/英等 | SPA；角色详情需客户端渲染 | 部分核实 |
| 角色页 | https://zzz.mihoyo.com/character?id=126035 | 简介、阵营、CV、台词 | 中 | 客户端重渲染；搜索索引有收录 | 已核实 |
| 新闻/代理人档案 | https://zzz.mihoyo.com/news | 档案、机制、版本公告、网页活动 | 中 | SPA；单篇正文需浏览器 | 已核实入口 |
| B站绝区零 | https://space.bilibili.com/1636034895 | 角色 PV/展示/EP/未归档影像/ZTALK | 中 | 移动 UA 视频页可取 JSON；搜索 API 有风控；无公开字幕 | 已核实 |
| 微博/米游社 | https://weibo.com/n/绝区零；https://www.miyoushe.com/zzz/ | 档案转发、生日、短剧 | 中 | 微博登录墙；米游社部分需登录 | 部分核实 |
| HoYoLAB / YouTube | https://www.hoyolab.com/；https://www.youtube.com/@ZZZ_Official | 英文公告、PV | 英 | 实测 403（2026-10-21）/不可达；需海外网络 | 部分核实 |
| HoYoWiki | https://wiki.hoyolab.com/pc/zzz/home | 角色资料库（基础/技能/养成） | 多语 | 地区 403；语音/剧情有限 | 部分核实 |

### 3.2 官方可直接取得
代理人档案（引言+简介+CV）、角色页文案、New Eridan 短剧对白、版本公告、生日/节日图文、开发者访谈。PV/展示有语音，但无台本。

### 3.3 官方缺口（须社区补）
- 全量语音（战斗/待机/受击/信赖）及文本；游戏内无语音回放。
- 代理人秘闻、信赖/密友同行、主线与活动剧情全文。
- 已下线活动与旧版剧情。
- 视频无官方字幕，需转写并会丢失语气/多语言差异。
- 角色页无历史版本；未发现长篇官方漫画，仅短篇栏目。

### 3.4 检索式
1. `site:zzz.mihoyo.com/news "代理人档案" 角色名`
2. `site:zenless.hoyoverse.com "Agent Record" 英文名`
3. B站：`绝区零 角色名 角色展示|角色PV|EP|代理人未归档影像`
4. `site:miyoushe.com/zzz 角色名 语音|角色故事|代理人秘闻`
5. `site:zenless-zone-zero.fandom.com "英文名" voice-overs`
6. `site:wiki.biligame.com/zzz 角色名 语音`
7. `site:weibo.com 绝区零 角色名 New Eridan`
8. `site:youtube.com/@ZZZ_Official 英文名 demo`

### 3.5 社区补缺
| 来源 | URL | 强项 | 注意 |
|---|---|---|---|
| BWIKI 绝区零 | https://wiki.biligame.com/zzz/ | 图鉴、数值、少量语音、版本 | 首页静态 200；角色页有风控；编辑自述无完整语音库 |
| Fandom | https://zenless-zone-zero.fandom.com/ | Profile、Voice-Overs、Story、Trust | 本网络连接失败；通常静态可抓；英文 |
| 萌娘百科 | https://zh.moegirl.org.cn/绝区零 | CV/概览/梗 | Cloudflare 403 |
| Honey Hunter | https://zzz.honeyhunterworld.com/agents/?lang=CN | 数值/材料 | 无剧情文本；Cloudflare 403 |
| Fami通访谈（篝火转载） | https://gouhuo.qq.com/content/detail/0_20241223172912_sSKi1mBxn | 开发者访谈 | 第三方转载、官方受访；S1 辅助 |

### 3.6 抽取顺序
官网/角色页用无头浏览器取 DOM → 新闻索引定位单篇 → B站移动 UA 取 `__INITIAL_STATE__`，字幕需登录或 ASR → BWIKI/Fandom 补语音与剧情 → 萌娘/Honey 只补细枝末节。

### 3.7 实测技巧与陷阱（2026-10-22）

- 新闻单篇 `zzz.mihoyo.com/m/news/{id}` 若正文只显示“数据加载中”，在 URL 后加 `?page=feature` 或 `?page=world` 再抓，常见情况下正文可读。
- 搜索索引的标题可能与页面正文不一致（例如 `id=166039` 标题写叶瞬光、正文却是赛维里安）；**以页面内正文为准**，不要拿索引标题当角色确认。
- 无头浏览器不是可靠兜底；SPA 渲染仍可能失败。失败时改用官方 App Store 简介、官方公告条目、官方短片文案，不要用搜索摘要冒充官方原文。

