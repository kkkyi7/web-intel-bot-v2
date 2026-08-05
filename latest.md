# 情报 Brief · 2026-08-05

## 今日 TOP3

1. **GPT-5.6 降价 20%-80%，同智商成本四个月降 13 倍** · 分9
   OpenAI 用 GPT-5.6 自己优化推理和调度，把同等智能水平的 token 价格打下来 13 倍，还宣布全线降价，连开源模型的性价比都被比下去了。
   https://www.latent.space/p/ainews-gpt-56-price-cut-by-20-80

2. **Uber 开源 ADR：企业 AI 代理安全检测与响应系统** · 分9
   Uber 开源了 ADR 系统，专门监控和保护企业里用的 AI 代理（比如 Claude Code、Cursor），能检测攻击、评估风险、阻止危险操作，已在 Uber 生产环境跑起来了。
   https://github.com/uber/ADR

3. **上下文反卷积：促销零售中方差稳定的需求感知** · 分9
   这篇论文提出一种叫上下文反卷积的两阶段预测方法，把促销冲击和稳定基线分开建模，在M5和Favorita数据集上大幅降低预测误差的离散度，但只有在持有成本够高时才能降低总成本。
   http://arxiv.org/abs/2607.25664v1

## 今日精选

### AI大事
- [用Skill Hub一键调用技能，重塑 AI Agent 实战力](https://www.infoq.cn/video/b52zg9lZJ6dguds0SxaO?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  InfoQ 视频讲了一个叫 Skill Hub 的东西，让 AI Agent 能像装 App 一样一键调用各种技能，不用每次重新训练或写复杂代码，直接提升 Agent 在真实业务里的干活能力。
- [LLM 0.32 发布：推理轨迹、服务端工具与更智能日志](https://simonwillison.net/2026/Aug/4/new-release-of-llm/#atom-everything) · Simon Willison · 分9
  Simon Willison 发布了命令行工具 LLM 0.32，支持显示模型推理过程、调用服务端工具（如代码执行和联网搜索）、重写了日志系统，并默认切换到 GPT-5.6 Luna 模型。
- [GPT-5.6 降价 20%-80%，同智商成本四个月降 13 倍](https://www.latent.space/p/ainews-gpt-56-price-cut-by-20-80) · Latent Space · 分9
  OpenAI 用 GPT-5.6 自己优化推理和调度，把同等智能水平的 token 价格打下来 13 倍，还宣布全线降价，连开源模型的性价比都被比下去了。
- [AirLLM：单张4GB显卡跑70B大模型](https://github.com/lyogavin/airllm) · GitHub Trending · 分9
  AirLLM 这个开源工具能大幅降低大模型推理时的显存占用，让 70B 甚至 671B 的超大模型在普通单张显卡上跑起来，不用量化、剪枝或蒸馏，原理是分层加载和按专家流式加载。
- [Uber 开源 ADR：企业 AI 代理安全检测与响应系统](https://github.com/uber/ADR) · GitHub Trending · 分9
  Uber 开源了 ADR 系统，专门监控和保护企业里用的 AI 代理（比如 Claude Code、Cursor），能检测攻击、评估风险、阻止危险操作，已在 Uber 生产环境跑起来了。

### 供应链
- [推理工程大师课：Baseten 实战解析](https://www.latent.space/p/inference-eng) · Latent Space · 分9
  Baseten 两位专家聊推理工程，讲如何把开源模型变成又快又便宜的 API。核心是量化、缓存、投机解码这些优化手段，能让推理速度提升 20% 到 200%，还讨论了训练和推理正在融合的趋势。
- [对话卓驭 CEO 沈劭劼：汽车在被撞前 0.01 秒退出智驾肯定是不行的](https://www.ifanr.com/1673777?utm_source=rss&utm_medium=rss&utm_campaign=) · 爱范儿 · 分9
  卓驭 CEO 聊智驾技术迭代速度，端到端模型让车比人快 0.1 秒反应，供应商和车企从甲乙方变成联合开发，边界正在被重新划定。
- [上下文反卷积：促销零售中方差稳定的需求感知](http://arxiv.org/abs/2607.25664v1) · arXiv · 分9
  这篇论文提出一种叫上下文反卷积的两阶段预测方法，把促销冲击和稳定基线分开建模，在M5和Favorita数据集上大幅降低预测误差的离散度，但只有在持有成本够高时才能降低总成本。

### 世界时事
- [能源内参：国际油价大跌，工信部叫停动力电池梯次利用](https://www.caixin.com/2026-08-05/102471335.html) · 财新网 · 分8
  国际油价因美伊局势缓和大幅下跌，同时工信部收紧废旧动力电池回收标准，叫停梯次利用，强调安全和质量，影响新能源和制造业供应链。

### GitHub 动态
- [Claude Code 发布 v2.1.222 修复更新](https://github.com/anthropics/claude-code/releases/tag/v2.1.222) · GitHubRelease · 分8
  Claude Code 发了个小版本更新，修了一堆 bug，主要是隔离机制、代理连接、用量统计和权限控制的问题，属于开发者工具的日常迭代。

_更新于 2026-08-05 04:43 · web-intel-bot_