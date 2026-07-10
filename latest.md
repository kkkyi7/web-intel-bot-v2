# 情报 Brief · 2026-07-10

## 今日 TOP3

1. **SpaceXAI 发布 Grok 4.5，Cursor 收购后首个 Opus 级模型** · 分9
   马斯克的 xAI 发布了新模型 Grok 4.5，定位是“Opus 级但更快更便宜”，专门为编程和 AI Agent 场景训练，并且是和 Cursor 合作训练的，直接对标 OpenAI 和 Anthropic 的旗舰模型。
   https://www.latent.space/p/ainews-spacexai-launches-grok-45

2. **AI基础设施必须为Agent体验进化** · 分9
   Modal CTO讲为什么传统云平台是为人类开发者设计的，现在AI Agent自己写代码、跑任务，基础设施需要从开发者体验转向Agent体验，比如弹性推理、沙盒、GPU快照。
   https://www.latent.space/p/modal2026

3. **Lilian Weng 总结 35 篇论文：关于“驾驭工程”与递归自我改进** · 分9
   Lilian Weng 发了一篇重磅总结，核心观点是：AI 的递归自我改进（RSI）关键不在于改模型权重，而在于改进“驾驭系统”（Harness）。这正在成为 Agent 产品落地的核心设计趋势。
   https://www.latent.space/p/ainews-lilian-weng-summarizes-35

## 今日精选

### AI大事
- [AI系统提示词泄露仓库](https://github.com/asgeirtj/system_prompts_leaks) · GitHub Trending · 分10
  这个GitHub仓库持续收集并更新各大AI模型（Claude、ChatGPT、Gemini等）的底层系统提示词，让你看到模型被设定的“隐藏规则”，比如Claude Fable 5和GPT-5.5的完整…
- [last30days-skill：AI 代理搜索工具](https://github.com/mvanhorn/last30days-skill) · GitHub Trending · 分10
  这是一个开源的 AI 代理技能，能同时搜索 Reddit、X、YouTube、Hacker News 等平台，根据点赞、转发和真实金钱投注来排序内容，最后合成一份关于任何话题的“过去30天”摘要。
- [OpenAI 发布 GPT-5.6 家族：Luna、Terra、Sol](https://simonwillison.net/2026/Jul/9/gpt-5-6/#atom-everything) · Simon Willison · 分9
  OpenAI 发布了三个新模型，从便宜到贵分别是 Luna、Terra、Sol。它们在长任务智能体测试上大幅超过 Claude Fable 5，但在代码能力上被 Fable 反超。API 还新增了多智…
- [Meta 发布 Muse Spark 1.1 模型](https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/) · HackerNews · 分9
  Meta 发布了新模型 Muse Spark 1.1，在编程和终端任务上性能接近 OpenAI 和 Anthropic 的顶级模型，但价格只有它们的十分之一甚至更低，而且开放权重。
- [GPT-5.5 生物漏洞赏金计划](https://openai.com/index/bio-bug-bounty) · OpenAI Blog · 分9
  OpenAI 推出 GPT-5.5 的“生物漏洞赏金”计划，悬赏安全专家找出模型在生物、化学、核武器等领域的恶意使用风险，最高奖励 3 万美元。
- [SpaceXAI 发布 Grok 4.5，Cursor 收购后首个 Opus 级模型](https://www.latent.space/p/ainews-spacexai-launches-grok-45) · Latent Space · 分9
  马斯克的 xAI 发布了新模型 Grok 4.5，定位是“Opus 级但更快更便宜”，专门为编程和 AI Agent 场景训练，并且是和 Cursor 合作训练的，直接对标 OpenAI 和 Anth…

### 技术圈
- [在慢电脑上跑通 GLM 5.2](https://github.com/JustVugg/colibri) · HackerNews · 分9
  一个开发者用 32GB 内存的普通笔记本，通过把模型拆成磁盘+内存混合加载，让 744B 参数的 MoE 大模型 GLM 5.2 跑起来了，虽然速度只有 0.1 token/秒。
- [用Rust重写Postgres，通过全部回归测试](https://github.com/malisper/pgrust) · HackerNews · 分9
  作者用LLM辅助把30年历史的Postgres数据库用Rust语言重写了一遍，现在已通过全部回归测试。项目引发了关于AI生成代码可维护性、许可证兼容性和重写策略的激烈讨论。

### 供应链
- [自研焊接具身大脑模型，以“智能焊工”切入工业制造具身智能赛道，「昇视唯盛」完成数亿元B轮融资](https://36kr.com/p/3887871679347208?f=rss) · 36氪 · 分9
  一家叫昇视唯盛的公司融了数亿元，专门做能像老焊工一样自己看、自己焊的AI焊接机器人，不用人编程，能自动适应不同工件，替代1.5到2个焊工，1年回本。
- [AI基础设施必须为Agent体验进化](https://www.latent.space/p/modal2026) · Latent Space · 分9
  Modal CTO讲为什么传统云平台是为人类开发者设计的，现在AI Agent自己写代码、跑任务，基础设施需要从开发者体验转向Agent体验，比如弹性推理、沙盒、GPU快照。

_更新于 2026-07-10 01:37 · web-intel-bot_