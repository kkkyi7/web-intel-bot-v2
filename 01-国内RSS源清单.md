# 国内 RSS 源清单 · v2.0

> **更新于** 2026-04-22
>
> 国内 RSS 生态比海外差很多——微信公众号不能直接订阅、微博需要爬虫、知乎专栏官方 RSS 停了。
> 下面这份是筛选过的：**优先官方直连、公开免登录、稳定 2+ 年**。

---

## 一、⭐ 官方直连（最稳，优先用这些）

这 6 个是自有 RSS、不依赖第三方，挂的概率最低。

| 名称 | URL | 主要覆盖 | 稳定性 |
|---|---|---|---|
| **36氪** | `https://36kr.com/feed` | 综合科技、创投、AI、新消费 | ★★★★★ |
| **机器之心** | `https://www.jiqizhixin.com/rss` | AI 研究、大模型、agent | ★★★★★ |
| **InfoQ 中文** | `https://www.infoq.cn/feed` | 企业技术、架构、开发、AI 工程化 | ★★★★☆ |
| **少数派** | `https://sspai.com/feed` | 科技产品、效率工具、AI 应用、心理 | ★★★★★ |
| **极客公园** | `http://main_feed.geekpark.net/feeds/all.atom` | 消费科技、AI 产品、创业 | ★★★★☆ |
| **爱范儿** | `https://www.ifanr.com/feed` | 消费科技、AI 应用、产品评测 | ★★★★☆ |

---

## 二、📡 RSSHub 源（备用，稳定性中等）

RSSHub 是个"把没有 RSS 的网站变成 RSS"的公共服务。公共实例偶尔会挂，想 100% 稳定需要自己部署一个（**本周先不做**）。

### 公共实例（任选其一，出问题换另一个）
- `https://rsshub.app/`（官方）
- `https://rsshub.rssforever.com/`（国内用户友好）

### 可用路径（把 URL 前缀换成上面任一实例）

| 名称 | 路径 | 主要覆盖 |
|---|---|---|
| **量子位** | `/qbitai` | AI 专业媒体 |
| **虎嗅 24 小时** | `/huxiu/article` | 商业科技 |
| **钛媒体** | `/tmtpost` | 产业科技 |
| **澎湃新闻推荐** | `/thepaper/featured` | 时政新闻 |
| **财新网最新** | `/caixin/latest` | 财经 / 政经 |
| **果壳·科学人** | `/guokr/scientific` | 科普 / 生物 |
| **返朴** | `/fanpu/articles` | 硬核科学 |
| **简单心理** | `/jiandanxinli/post` | 心理学科普 |
| **壹心理** | `/xinli001/news` | 心理学、情绪 |

---

## 三、按主题推荐组合

每个主题先配 2-3 个源，跑一周看效果再增减。

### 📦 供应链 / APS
中文供应链专业 RSS 极少，只能从综合科技源里用关键词过滤。
- 36氪（综合，keywords_cn 过滤"供应链 / 智能制造 / 工业软件"）
- InfoQ 中文（技术视角）
- 机器之心（AI 在供应链的应用）

### 🤖 AI 大事
最丰富，能选到专业媒体。
- 机器之心 ⭐⭐⭐
- 量子位（RSSHub）
- 36氪
- 少数派（AI 工具应用视角）

### 🌍 世界时事
国内视角的时政 / 财经。
- 澎湃新闻（RSSHub）
- 财新网（RSSHub，有付费墙，免费部分够用）
- 36氪（经济、政策）

### 🧬 生物学
- 果壳·科学人（RSSHub）
- 返朴（RSSHub）
- 机器之心（AI+生物交叉）

### 🧠 心理学
- 简单心理（RSSHub）
- 壹心理（RSSHub）
- 少数派（效率 / 心理 / 生活栏目）

---

## 四、v2 config.yaml 里怎么配

每个主题的 `sources` 下加 `rss` 数组，每条带 `name` / `url` / `region`：

```yaml
供应链:
  keywords: [...]                      # 英文关键词（给海外源用）
  keywords_cn:                         # ⭐ 新增：中文关键词（给国内源预过滤用）
    - 供应链
    - 排产
    - APS
    - 智能制造
    - 工业软件
    - 生产调度
  sources:
    youtube: {...}                     # 自动打 region: intl
    reddit: {...}                      # 自动打 region: intl
    arxiv: {...}                       # 自动打 region: intl

    rss:                               # ⭐ 新增
      - name: "36氪"
        url: "https://36kr.com/feed"
        region: cn
        limit: 10                      # 抓 10 条后用 keywords_cn 过滤
      - name: "机器之心"
        url: "https://www.jiqizhixin.com/rss"
        region: cn
        limit: 8
      - name: "InfoQ 中文"
        url: "https://www.infoq.cn/feed"
        region: cn
        limit: 8
```

---

## 五、不想用的源（记录下来避免反复踩坑）

| 名称 | 原因 |
|---|---|
| 微信公众号 | 没有官方 RSS，所有 RSSHub 路径都极不稳定 |
| 微博 | 反爬强，需要 cookie，合规风险高 |
| 知乎专栏 | 官方 RSS 已下线，RSSHub 路径频繁失效 |
| 今日头条 | 无 RSS，反爬 |
| 新浪新闻 | 接口不稳定 |
| 央视新闻 | RSS 结构乱 |

---

## 六、后续升级建议

**v2.5 可以做**：自己部署 RSSHub（免费 VPS + Docker 一键装），稳定性瞬间变 ★★★★★

**v3.0 可以做**：接入爬虫类源（公众号 / 微博）+ 内容去重 + 事实性校验

本周：**只用上面第一栏的 6 个官方源，已经够覆盖 AI 大事 + 少量供应链和心理了**。其他主题的 RSSHub 源列出来但先不加到 config，等 v2.0 跑通再扩。
