# 情报 Brief · 2026-07-22

## 今日 TOP3

1. **图神经网络作为供应链优化元模型的潜力：数据集、架构与方向** · 分9
   这篇论文探讨了用图神经网络（GNN）替代传统仿真模型来预测供应链网络性能，并给出了公开数据集和初步实验结果，为供应链拓扑优化打开了新思路。
   http://arxiv.org/abs/2607.16769v1

2. **AI Agent 设计原理与工程实战开源书** · 分10
   李博杰写了一本开源书，用“Agent = LLM + 上下文 + 工具”这个公式，从原理到代码手把手教你搭 AI Agent，10 章正文加 88 个配套实验项目，全免费。
   https://github.com/bojieli/ai-agent-book

3. **新一轮关税，最快本周** · 分8
   美国10%全球关税本周五到期，特朗普政府最快本周对数十国加征新关税，同时已对加拿大部分产品加征50%关税，贸易战可能进一步升级。
   https://www.guancha.cn/internation/2026_07_22_824604_s.shtml

## 今日精选

### AI大事
- [AI Agent 设计原理与工程实战开源书](https://github.com/bojieli/ai-agent-book) · GitHub Trending · 分10
  李博杰写了一本开源书，用“Agent = LLM + 上下文 + 工具”这个公式，从原理到代码手把手教你搭 AI Agent，10 章正文加 88 个配套实验项目，全免费。
- [Kimi K3 与 Fable 模型对比，达到业界顶尖水平](https://fireworks.ai/blog/kimik3-fable) · HackerNews · 分9
  有人做了一个路由模型，在 Kimi K3 和 Fable 两个模型之间自动选更便宜、更准的那个来回答问题，结果 Kimi K3 在大部分任务上被选中的次数高达 72%-96%。
- [Jack Dorsey 推出 Buzz，团队与 AI Agent 共用的群聊平台](https://techcrunch.com/2026/07/21/jack-dorsey-is-taking-on-slack-with-buzz-a-group-chat-platform-for-teams-and-their-ai-agents/) · TechCrunch AI · 分9
  Jack Dorsey 做了一个叫 Buzz 的办公聊天软件，核心是把人类和 AI Agent 放在同一个群聊里，让 AI 像同事一样参与讨论和执行任务，直接对标 Slack。
- [保持缓存活跃是值得的：Agent 工作负载的 Keepalive 经济学](http://arxiv.org/abs/2607.19214v1) · arXiv · 分9
  这篇论文发现，AI Agent 在调用工具或等待审批的间隙，LLM 的缓存会被清掉，导致每次都要重新算一遍，成本高、速度慢。他们提出客户端定时发“心跳”请求来保持缓存，能把后续请求成本降低最多 12.…
- [与 Claude Code 团队 Cat 和 Thariq 的炉边对话](https://simonwillison.net/2026/Jul/21/cat-and-thariq/#atom-everything) · Simon Willison · 分9
  Anthropic 的 Claude Code 团队分享了他们如何用自家工具（Claude Tag、Fable）做开发，以及随着模型变强，他们从“盯代码”转向“放手让 AI 做，自己搞创意”的工作方式…
- [AI 新闻：今天没啥大事](https://www.latent.space/p/ainews-not-much-happened-today-173) · Latent Space · 分9
  这期 AI 新闻汇总了周末几件大事：Kimi K3 和 Qwen 3.8 Max 两个超大规模模型即将开源，美国可能限制中国开源模型，以及一个用开源模型做安全防御的真实案例。
- [Sam Altman 邮件曝光：OpenAI 曾计划开源 GPT-3 级模型](https://simonwillison.net/2026/Jul/20/sam-altman/#atom-everything) · Simon Willison · 分9
  2022 年 10 月 Sam Altman 给 OpenAI 董事会写信，提议尽快发布一个能在普通电脑上跑的 GPT-3 级开源模型，目的是抢先占位，阻止其他团队（如 Stability）做出类似产…

### 技术圈
- [Poolside 发布 Laguna S 2.1 模型](https://poolside.ai/blog/introducing-laguna-s-2-1) · HackerNews · 分9
  Poolside 发布了一个中等规模的开源模型 Laguna S 2.1，性能对标 DeepSeek V4 Flash，能在消费级硬件上本地运行，社区实测代码能力很强，价格还便宜。

### 供应链
- [图神经网络作为供应链优化元模型的潜力：数据集、架构与方向](http://arxiv.org/abs/2607.16769v1) · arXiv · 分9
  这篇论文探讨了用图神经网络（GNN）替代传统仿真模型来预测供应链网络性能，并给出了公开数据集和初步实验结果，为供应链拓扑优化打开了新思路。
- [预测-校正循环：基于小样本连续上下文Bandit的需求预测](http://arxiv.org/abs/2607.16354v1) · arXiv · 分9
  这篇论文提出一个两阶段需求预测框架：先用传统ML模型做初始预测，再用一个轻量级在线学习算法根据实时反馈做小样本校正，在沃尔玛数据上平均RMSE降低9.52%。

_更新于 2026-07-22 01:36 · web-intel-bot_