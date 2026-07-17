# 情报 Brief · 2026-07-17

## 今日 TOP3

1. **Kimi K3 发布与鹈鹕基准测试的启示** · 分9 · 3信源
   中国 AI 实验室月之暗面发布了 2.8 万亿参数的 Kimi K3 模型，性能超越 GPT-5.5 和 Claude Opus 4.8，但定价也大幅上涨。作者还反思了自创的“鹈鹕骑自行车”测试已不再能有效衡量模型能力。
   https://simonwillison.net/2026/Jul/16/kimi-k3/#atom-everything

2. **全球供应链物流中断预测与缓解的智能专家系统** · 分9
   这篇论文搞了个智能系统，先用图模型算出供应链里风险怎么传染，再结合多种预测模型提前预判物流中断，最后给出可执行的缓解方案，实验效果不错。
   https://pubmed.ncbi.nlm.nih.gov/42463892/

3. **Codex 用户半年增长超 10 倍达 700 万，是否超越 Claude Code** · 分9
   OpenAI 的 Codex 编程工具 6 个月用户从 55 万涨到 700 万，最近一天就新增 100 万，跟 Claude Code 的 200 万用户和 25 亿美元年收入形成对比，但两者统计口径不同。
   https://www.latent.space/p/ainews-codex-usage-up-10x-in-6-months

## 今日精选

### 世界时事
- [双标！中国AI被骂偷，美国照抄叫工程](https://www.guancha.cn/internation/2026_07_17_824045_s.shtml) · 观察者网 · 分9
  《福布斯》发文批评美国双标：中国用美国模型叫偷，美国公司用中国架构和蒸馏中国模型训练新模型，却被夸成工程创新。本质是政治干预导致美国企业被迫用次优方案。

### GitHub 动态
- [Claude Code 发布 v2.1.212 更新](https://github.com/anthropics/claude-code/releases/tag/v2.1.212) · GitHubRelease · 分9
  Claude Code 这次更新主要优化了开发者的多任务处理能力，新增了会话分叉、后台任务、搜索限制和子任务预算控制等功能。
- [Anthropic Python SDK 发布 v0.117.0，新增 dreaming 与 MCP Tunnels](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.117.0) · GitHubRelease · 分9
  Anthropic 的 Python SDK 更新到 v0.117.0，主要加了两个新功能：一个是让模型能“做梦”的 dreaming 模式，另一个是 MCP Tunnels 隧道功能，还修了个凭证泄…
- [LangChain 发布 1.3.14，新增工具错误中间件](https://github.com/langchain-ai/langchain/releases/tag/langchain%3D%3D1.3.14) · GitHubRelease · 分9
  LangChain 发了小版本更新，核心是给工具调用加了两个中间件：一个专门处理可重试的错误，另一个统一拦截工具执行中的异常，让 Agent 更稳定。

### AI大事
- [Kimi K3 发布与鹈鹕基准测试的启示](https://simonwillison.net/2026/Jul/16/kimi-k3/#atom-everything) · Simon Willison · 分9
  中国 AI 实验室月之暗面发布了 2.8 万亿参数的 Kimi K3 模型，性能超越 GPT-5.5 和 Claude Opus 4.8，但定价也大幅上涨。作者还反思了自创的“鹈鹕骑自行车”测试已不再…
- [Grok 与 Cursor 合作推出新模型](https://www.bensbites.com/p/grok-x-cursor) · Ben's Bites · 分9
  SpaceXAI 和 Cursor 联合训练了 Grok 4.5，性能接近 Anthropic 的顶级模型 Opus，但成本大幅降低，在 Cursor 中可用，对开发者是个高性价比选择。

### 供应链
- [软件项目的共同语言不是英语或Python](https://simonwillison.net/2026/Jul/14/armin-ronacher/#atom-everything) · Simon Willison · 分9
  Armin Ronacher 指出，软件项目真正的共同语言是大家对概念、边界、不变量的共同理解，这种理解靠“摩擦”来同步，而 AI Agent 正在消除这种摩擦，可能带来隐性风险。
- [Codex 用户半年增长超 10 倍达 700 万，是否超越 Claude Code](https://www.latent.space/p/ainews-codex-usage-up-10x-in-6-months) · Latent Space · 分9
  OpenAI 的 Codex 编程工具 6 个月用户从 55 万涨到 700 万，最近一天就新增 100 万，跟 Claude Code 的 200 万用户和 25 亿美元年收入形成对比，但两者统计口…
- [从供应链网络推断库存动态：一种带自主验证的图学习方法](http://arxiv.org/abs/2607.10642v1) · arXiv · 分9
  这篇论文提出用多智能体半监督框架，在中小企业缺乏库存数据的情况下，通过供应链网络拓扑推断库存变化，并用多个经济模型自动验证预测结果。
- [AI基础设施必须为Agent体验进化](https://www.latent.space/p/modal2026) · Latent Space · 分9
  Modal CTO 聊为什么传统云平台是为人类开发者设计的，现在Agent自己写代码跑任务，基础设施必须从“开发者体验”转向“Agent体验”，比如弹性推理、沙箱、GPU快照等。

_更新于 2026-07-17 04:41 · web-intel-bot_