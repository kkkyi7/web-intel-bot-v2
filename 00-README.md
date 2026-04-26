# web-intel-bot · 全网数据采集与 AI 学习分析系统

> 个人 + 小团队学习管道：每天自动从 YouTube/Reddit/arXiv/PubMed 等多源抓取供应链/生物/心理三个方向的最新内容 → Claude 摘要打分 → 邮件日报 + 本地 HTML 存档

---

## 🚀 最快上手路径（推荐）

**忽略 n8n 方案，直接用 `04-采集脚本/` 里的 Python 脚本**。不需要服务器、不需要订阅、不需要写代码，只要：

1. 装 Python
2. 双击 `setup.bat` 装依赖
3. 填 `.env` 里的 API Key（YouTube 免费 + DeepSeek 支付宝充 ¥10 够用 2-3 个月）
4. 双击 `run.bat` 开跑

完整步骤见 👉 [`04-采集脚本/启动指南.md`](04-采集脚本/启动指南.md)

> **重要提示**：你订阅的 Claude Max 是网页/桌面应用的用量，**不包含 API 调用**。脚本里的摘要+打分需要 API，已经默认改用 DeepSeek（支付宝充值，比 Claude Haiku 便宜 ~10 倍，中文质量更好）。具体见启动指南第 3 步。

---

## 目录索引

| 文件/目录 | 用途 | 何时看 |
|---|---|---|
| `00-README.md` | 你正在看的这个，项目总览 | 随时 |
| `01-架构方案.md` | 完整 5 层架构 + 4 阶段路线图 | 想了解全貌 |
| `02-MVP阶段0清单.md` | n8n 方案的详细操作手册（备选路径） | 想用 n8n 就看这个 |
| `03-n8n工作流配置/` | n8n 的可导入模板（备选路径配套） | 用 n8n 时配套用 |
| **`04-采集脚本/`** | **Python 主力实现（推荐）** | **直接用** |
| `05-数据样本/` | 每天跑完的 JSON 和 HTML 会自动存到这里 | 跑起来后看 |

---

## 两种实施路径对比

| | **Python 脚本（推荐）** | n8n 工作流（备选） |
|---|---|---|
| 学习成本 | 零代码可用（双击 bat） | 要学 n8n UI |
| 部署 | 本机双击运行 + 定时任务 | 要 n8n Cloud (€20/月) 或自部署 |
| 成本 | 只有 API 费（DeepSeek 约 ¥3-10/月，Claude 约 ¥30-100/月） | + n8n 订阅费 |
| 改 Prompt | 改 `daily_digest.py` 里的一段文字 | n8n UI 里点 |
| 加新源 | 改 `config.yaml` 加几行 | 复制节点重新配 |
| 适合 | 个人用、小团队本地共享 | 跨团队协作、多触发器混用 |

**结论：个人学习阶段 0/1 用 Python 就够，阶段 2/3 团队化再切 n8n。**

---

## 推荐阅读顺序

1. **新手**：直接去 [`04-采集脚本/启动指南.md`](04-采集脚本/启动指南.md) 按 5 步做完，一个下午跑通
2. **想懂原理**：读完 `01-架构方案.md` 的"一、整体设计思路"和"九、实施路线图"（10 分钟）
3. **想深入**：读完整个 `01-架构方案.md`，了解阶段 1/2/3 要加什么

---

## 当前阶段：0（MVP）

```
[进行中] 阶段 0 · MVP（Python 脚本 + 4 源 + 邮件日报）
[ 待开始 ] 阶段 1 · PDF 研报管道 + 数据库持久化
[ 待开始 ] 阶段 2 · RAG 向量库 + 主题深度报告
[ 待开始 ] 阶段 3 · 团队化 + 可视化仪表盘
```

### 阶段 0 已覆盖的源

- ✅ YouTube（官方 API + 字幕自动抓取）
- ✅ Reddit（免登录 JSON 接口）
- ✅ arXiv（运筹/计算机论文）
- ✅ PubMed（生物/心理学论文）
- ⏸️ B站（阶段 1 加，需要 MediaCrawler）
- ⏸️ 小红书/抖音/微信公众号（阶段 1 加）
- ⏸️ PDF 研报（阶段 1 加，需要 MinerU）

### 阶段 0 验收

连续跑 7 天，满足 👉 [`02-MVP阶段0清单.md` 第 7 章的 5 项验收](02-MVP阶段0清单.md) 即可毕业进阶段 1。

---

## 三个学习方向的关键词词典

已内置在 `04-采集脚本/config.yaml` 里，直接改那个文件就能调整。

### 供应链 / APS（你的本职方向）
- 中文：APS, 高级排程, 供应链优化, 多级库存, 需求预测, S&OP, 数字孪生, MES, ERP 集成
- 英文：advanced planning and scheduling, APS, supply chain optimization, multi-echelon inventory, demand forecasting, S&OP, supply chain digital twin, control tower

### 生物学
- 中文：分子生物学, 表观遗传, CRISPR, 单细胞测序, 神经科学, 衰老, 肠道菌群
- 英文：molecular biology, epigenetics, CRISPR, single-cell sequencing, neuroscience, longevity, gut microbiome

### 心理学
- 中文：认知科学, 行为经济学, 决策心理, 注意力, 元认知, 习惯养成, 情绪调节
- 英文：cognitive science, behavioral economics, decision making, attention, metacognition, habit formation, emotion regulation

---

## 遇到问题怎么办

1. 先翻 [`04-采集脚本/启动指南.md`](04-采集脚本/启动指南.md) 末尾的常见问题
2. 跑 `run_dry.bat` 看详细日志
3. 把报错贴过来，我帮你定位
4. 有邮件收到了想调摘要质量 → 贴 1-2 条样本过来，我帮你改 Prompt

---

## 后续演进路线

- **阶段 1（1-2 周后）**：加 B站 + PDF 研报解析（MinerU）+ SQLite 数据库持久化（替代现在的 JSON 文件）
- **阶段 2（1 个月后）**：加向量库（pgvector）+ Claude 问答 + 自动周报
- **阶段 3（按需）**：Notion 集成 + 团队 Web UI（AnythingLLM）+ 可视化仪表盘

每个阶段跑顺了才上下一个，不要囤积未完成的半成品。
