# Day 1 收尾：在 Windows 上验证 + 发真邮件

> 我已经把代码全改完（T1.1–T1.6 全部 ✓）。现在交给你在 Windows 本机跑一遍，
> 这是 T1.7，也是 Day 1 的终点。

---

## 步骤 1：把密钥搬过来（30 秒）

新项目还没 `.env`（里面有你的 API Key 和邮箱密码，我不会动）。复制一下：

```cmd
copy "C:\Claude\web-intel-bot\04-采集脚本\.env"  "C:\Claude\web-intel-bot-v2\04-采集脚本\.env"
```

---

## 步骤 2：装新依赖 feedparser（10 秒）

```cmd
cd C:\Claude\web-intel-bot-v2\04-采集脚本
pip install feedparser
```

（mutagen 之前 v1 就装过了，不用重装。）

---

## 步骤 3：语法自检（5 秒）

```cmd
python -c "import py_compile; py_compile.compile('daily_digest.py', doraise=True); print('OK')"
```

如果输出 `OK` 就过。输出 SyntaxError 就把错误贴给我，我修。

---

## 步骤 4：dry-run 只跑 1 个主题看效果（3-5 分钟）

不发邮件，只生成 HTML 文件，先验证数据结构对不对。

```cmd
python daily_digest.py --dry-run --topic AI大事 --max-per-topic 3 --no-cache
```

**你要在终端输出里看到这些**：

- `✅ RSS [机器之心]: N 条（中文词过滤后 N/M）`
- `✅ RSS [36氪]: N 条...`
- `✅ RSS [InfoQ 中文]: N 条...`
- `合计抓到 XX 条（海外 XX · 国内 XX）`  ← **关键：这行证明 region 分组生效**

最后会在 `C:\Claude\web-intel-bot-v2\05-数据样本\2026-04-22\digest.html` 生成 HTML 文件。

---

## 步骤 5：浏览器打开 HTML 验证（1 分钟）

```cmd
start C:\Claude\web-intel-bot-v2\05-数据样本\2026-04-22\digest.html
```

**你应该看到**：

- ✅ Hero 卡正常
- ✅ **AI 大事** 主题下，分成 "🌐 海外" + "🇨🇳 国内" 两栏
- ✅ 主题大标题有下划线，层级清晰
- ✅ 浏览器窗口拉窄到手机宽度（<560px），两栏会自动堆叠成上下单栏

---

## 步骤 6：全主题跑 + 带 TTS + 发真邮件（15 分钟）

前 5 步都顺了再跑这个。

```cmd
python daily_digest.py --tts --max-per-topic 5 --no-cache
```

（`--no-cache` 是因为 v2 的结构变了，老缓存里的条目没 region 字段，最好重跑一遍；**跑完后下次就不用加这个 flag**。）

收到邮件后，手机上打开，看：
- 每个主题里都是海外/国内双栏
- 点击条目展开，正文干净（不漏口播稿）
- MP3 作为附件在邮件底部

---

## 排错清单

| 现象 | 大概原因 | 怎么修 |
|---|---|---|
| `SyntaxError` | 编辑过程中串行了 | 贴错误给我 |
| `✅ RSS [36氪]: 0 条` 全是 0 | 网络 / URL 失效 | 先浏览器访问 `https://36kr.com/feed` 确认能打开 |
| 国内栏空、海外栏有内容 | RSS 都抓不到（防火墙？） | 检查网络，RSS 源要公开可访问 |
| 邮件里两栏挤成一坨 | 邮件客户端 CSS 限制 | iOS Mail 应该正常；Outlook 可能不支持媒体查询，是已知限制 |
| `ModuleNotFoundError: feedparser` | 没装 | `pip install feedparser` |

---

## 成功标志

☐ dry-run 输出里 `海外 XX · 国内 XX` 两个数都 > 0
☐ 浏览器打开 digest.html 能看到双栏
☐ 手机邮箱收到新邮件，主题 `🧠 每日学习 Brief · 2026-04-22`
☐ 邮件里每个主题都是双栏（至少 AI 大事 / 供应链 / 心理学）
☐ 点 MP3 附件，系统播放器正常启动

全打勾 = Day 1 结束，v2.0 的骨架就稳了。

---

## Day 1 做了啥（回顾）

- 新建 `C:\Claude\web-intel-bot-v2\` 项目（老项目没动）
- 调研 + 写了 `01-国内RSS源清单.md`（6 个官方直连 + 9 个 RSSHub 备用）
- `config.yaml` 每个主题加了 `keywords_cn` + `sources.rss`
- 4 个现有 fetcher（YouTube / Reddit / arXiv / PubMed）统一打 `region: intl`
- 新写 `fetch_rss()` 函数（feedparser + 中文关键词预过滤）
- `render_html` 主循环重构：按 region 分双栏（用 `<table>` 兼容邮件客户端）
- CSS 升级：大类标题加下划线加大字号；双栏卡片；手机窄屏单栏降级

---

## 下一步（Day 2）

跑一周看国内源的质量，然后：
- 淘汰没用的源 / 加新源
- 调 `keywords_cn` 列表（哪个词漏掉了就加上）
- LLM prompt 针对中文源微调
