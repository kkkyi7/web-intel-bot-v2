# 情报 Brief · 2026-08-19

## 今日 TOP3

1. **Qwen 3.8 27B 评分 52，追平 GPT-5.6** · 分10
   阿里开源的小模型 Qwen 3.8 27B 在第三方评测里拿到 52 分，跟 GPT-5.6 最高配置持平，只比两个超大模型低一分，说明小模型性能已经逼近巨头。
   https://simonwillison.net/2026/Aug/17/qwen-38-27b-scores-52/

2. **首席展望｜摩根士丹利邢自强：政策核心在存量发力，全球AI周期仍将支撑中国出口** · 分9
   摩根士丹利首席经济学家判断，全球AI和能源转型投资周期还能撑中国出口至少12个月，政策不会大放水，核心是把已出台的存量政策加快落地，同时AI投资进入下半场，机会从算力扩散到应用和生态。
   https://m.thepaper.cn/detail/33799448

3. **Cursor 发布 Origin，对标 GitHub** · 分8
   Cursor 推出了自己的代码托管平台 Origin，想跟 GitHub 抢开发者。但评论区炸了，因为 Cursor 现在归马斯克管，大家担心代码数据被喂给 Grok，隐私没保障。
   https://cursor.com/changelog/origin-code-hosting

## 今日精选

### AI大事
- [Qwen 3.8 27B 评分 52，追平 GPT-5.6](https://simonwillison.net/2026/Aug/17/qwen-38-27b-scores-52/) · Simon Willison · 分10
  阿里开源的小模型 Qwen 3.8 27B 在第三方评测里拿到 52 分，跟 GPT-5.6 最高配置持平，只比两个超大模型低一分，说明小模型性能已经逼近巨头。
- [前沿模型成本与开源权重流行推动模型路由需求](https://www.latent.space/p/glean-model-routing) · Latent Space · 分9
  这篇讲的是企业AI部署中模型路由越来越火，Glean这家公司靠自动选模型省成本，年收入做到3亿美元，还跟Claude Code比成本便宜4倍，核心逻辑是别啥任务都用最贵的大模型。
- [持续LLM改进的经验链方法](http://arxiv.org/abs/2608.18027v1) · arXiv · 分9
  这篇论文提出一种叫经验链的方法，让大模型在测试时通过反复试错和自我反馈持续变聪明，实验显示平均提升5.6%准确率，还省了19%的API成本，而且模型越强提升越明显。
- [内存价格一年暴涨500%](https://www.tomshardware.com/pc-components/ram/memory-prices-climb-500-percent-in-12-months-up-to-10x-the-lowest-ever-tracked-prices-128gb-of-ddr5-now-usd3-399) · HackerNews · 分9
  内存颗粒价格12个月涨了5倍，128GB DDR5现在要3400美元，创历史新高。这波涨价已经传导到显示器等周边硬件，开发者社区开始讨论要不要重新重视代码的内存效率。
- [让 Agent 真正驱动销售增长——FDE 模式下的业务流重构实战｜AICon深圳](https://www.infoq.cn/article/vrlSsJUrdpfGqsj3CTZK?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分8
  讲的是用 FDE 模式（前端数字员工）重构销售业务流，让 Agent 不是单点提效，而是嵌入整个流程里真正驱动增长，来自 AICon 深圳的实战分享。

### 世界时事
- [首席展望｜摩根士丹利邢自强：政策核心在存量发力，全球AI周期仍将支撑中国出口](https://m.thepaper.cn/detail/33799448) · 澎湃新闻 · 分9
  摩根士丹利首席经济学家判断，全球AI和能源转型投资周期还能撑中国出口至少12个月，政策不会大放水，核心是把已出台的存量政策加快落地，同时AI投资进入下半场，机会从算力扩散到应用和生态。
- [AI风险防范与治理：中美两国路径初探](https://opinion.caixin.com/2026-08-19/102475562.html) · 财新网 · 分8
  这篇文章对比中美两国AI治理思路，讲双方在竞争同时怎么设安全护栏，重点管恶意使用和技术失灵两类风险，还提到2026年智能体爆发让安全问题更紧迫。

### GitHub 动态
- [Claude Code 发布 v2.1.235 更新](https://github.com/anthropics/claude-code/releases/tag/v2.1.235) · GitHubRelease · 分8
  Claude Code 命令行工具发了个小版本更新，主要修了一堆交互细节 bug，加了拼写检查功能，还优化了后台云任务的内存占用。

### 技术圈
- [警惕管理咨询顾问](https://about.iceland.co.uk/our-story/the-dark-ages/beware-management-consultants/) · HackerNews · 分8
  冰岛超市官网用一份故意做得很难用的幻灯片，吐槽管理咨询顾问的套路和空话，HN 网友看完一边笑一边反思自己公司里那帮穿西装的到底在干嘛。
- [Turbovec：Rust 版向量搜索，基于 Google TurboQuant](https://github.com/RyanCodrai/turbovec) · HackerNews · 分8
  Google 的 TurboQuant 量化技术被移植到 Rust，做成了 Turbovec 向量检索库。内存占用大幅下降，1 千万文档只要 4GB，社区在讨论它能否替代 FAISS 成为新基准。

_更新于 2026-08-19 02:41 · web-intel-bot_