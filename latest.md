# 情报 Brief · 2026-08-02

## 今日 TOP3

1. **开源权重革命：Simon Willison 播客对谈** · 分9
   Simon Willison 参加 Oxide and Friends 播客，聊了 Kimi K3 证明开源权重模型能跟闭源前沿模型正面竞争、一次意外网络攻击事件，以及 AI 圈大佬联名公开信支持开源权重，还顺带回顾了年初预测。
   https://simonwillison.net/2026/Jul/31/oxide-and-friends/#atom-everything

2. **上下文反卷积实现方差稳定的需求感知：促销零售中的核调制算子** · 分9
   这篇论文提出一种叫上下文反卷积的两阶段预测方法，把促销冲击和基础需求拆开建模，在零售数据集上显著降低预测误差的波动性，但总成本是否降低取决于持有成本和缺货成本的相对比例。
   http://arxiv.org/abs/2607.25664v1

3. **和美德决裂、赞扬中国…法国这个总统候选人有多头铁** · 分7
   法国极左翼候选人梅朗雄主张退出北约、拆法德轴心、亲中反美，民调显示他可能进第二轮，但大概率输给极右翼勒庞，欧盟很慌。
   https://www.guancha.cn/internation/2026_07_30_825624_s.shtml

## 今日精选

### AI大事
- [Quick BI 数据分析智能体的可靠工程实践](https://www.infoq.cn/article/VJ3s26QZUG1C5ANF2O4Q?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  阿里 Quick BI 团队分享怎么把数据分析智能体做到可靠落地，核心是工程化手段解决 LLM 幻觉、SQL 生成不稳、权限控制难这些真实问题，不是炫技。
- [开源权重革命：Simon Willison 播客对谈](https://simonwillison.net/2026/Jul/31/oxide-and-friends/#atom-everything) · Simon Willison · 分9
  Simon Willison 参加 Oxide and Friends 播客，聊了 Kimi K3 证明开源权重模型能跟闭源前沿模型正面竞争、一次意外网络攻击事件，以及 AI 圈大佬联名公开信支持开源…
- [Beacon：智能体视觉推理的时机与方式](http://arxiv.org/abs/2607.28595v1) · arXiv · 分9
  这篇论文研究多模态大模型用工具做视觉推理时，模型不会判断啥时候该用工具，导致简单问题反而被工具拖累。作者提出Beacon模型，通过强化学习让模型学会按需调用工具，整体性能明显提升。
- [AI 正在吃掉金融业，AIE NYC 开放报名](https://www.latent.space/p/ainews-ai-is-eating-finance-aie-nyc) · Latent Space · 分9
  AI 在金融各细分领域全面落地，OpenAI 和 Anthropic 都专门为金融场景推出工具和模板，行业大会 AIE NYC 把金融作为主舞台，一堆大行和 fintech 分享实战经验。
- [Gemini API 托管代理升级：3.6 Flash 与钩子](https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api-3-6-flash-hooks/) · Google AI Blog · 分9
  Google 给 Gemini API 的托管代理加了新功能，包括更快的 3.6 Flash 模型和 hooks 钩子机制，让开发者能构建更可靠、能上生产的 AI 代理，不用自己管基础设施。
- [last30days：AI 代理跨平台搜索工具](https://github.com/mvanhorn/last30days-skill) · GitHub Trending · 分9
  一个开源 AI 技能，能同时搜 Reddit、X、YouTube 等平台，按点赞和真实金钱下注排序，合成一份最近30天的简报，帮你快速了解某个人或话题的最新动态。
- [Cursor 从用量页和 CSV 导出中移除费用信息](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153) · HackerNews · 分8
  Cursor 悄悄把用量页面和 CSV 导出里的美元费用信息去掉了，只保留 token 数。官方说是误删了功能开关，但社区怀疑是在掩盖真实成本，引发了对 AI 编程工具定价透明度的讨论。

### 供应链
- [上下文反卷积实现方差稳定的需求感知：促销零售中的核调制算子](http://arxiv.org/abs/2607.25664v1) · arXiv · 分9
  这篇论文提出一种叫上下文反卷积的两阶段预测方法，把促销冲击和基础需求拆开建模，在零售数据集上显著降低预测误差的波动性，但总成本是否降低取决于持有成本和缺货成本的相对比例。

### 技术圈
- [Google 如何毁掉了 RSS 的普及](https://openrss.org/blog/how-google-helped-destroy-adoption-of-rss-feeds) · HackerNews · 分8
  文章复盘 Google Reader 关闭如何重创 RSS 生态，讨论开放网络被围墙花园取代的遗憾，以及 Substack 等新平台如何填补空白。

### GitHub 动态
- [Mem0 Python SDK 发布 v2.0.15 修复补丁](https://github.com/mem0ai/mem0/releases/tag/v2.0.15) · GitHubRelease · 分8
  Mem0 这个做 AI 记忆的开源库更新了，主要修了删数据删不干净、搜索数量被限制这些 bug，还把默认的重排模型换成了 GPT-5 mini。

_更新于 2026-08-02 01:36 · web-intel-bot_