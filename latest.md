# 情报 Brief · 2026-08-14

## 今日 TOP3

1. **DeepSeek V4 Pro 0813 上线，权重已开源** · 分9
   DeepSeek 新模型 V4 Pro 0813 通过 API 上线，权重随后在 Hugging Face 开源，1.7T 参数、893GB，且不同推理等级输出差异明显。
   https://simonwillison.net/2026/Aug/12/deepseek-v4-pro-0813/

2. **图神经网络引导遗传算法优化实物互联网供应链** · 分9
   这篇论文用图神经网络帮遗传算法做初始化，解决实物互联网里工厂、仓库、零售商三级网络的分配和补货问题，在成本不确定时比传统算法更稳更快。
   http://arxiv.org/abs/2608.10245v1

3. **选择无聊的技术** · 分9
   一篇 2015 年的经典文章，核心观点是每家公司创新资源有限，应该把创新花在刀刃上，其余技术栈尽量选成熟稳定的“无聊技术”。HN 网友重新热议，并把它和 AI Agent 时代联系起来。
   https://mcfunley.com/choose-boring-technology

## 今日精选

### GitHub 动态
- [Claude Code 更新：子代理分叉与跨会话消息](https://github.com/anthropics/claude-code/releases/tag/v2.1.232) · GitHubRelease · 分9
  Claude Code 命令行工具更新，默认开启子代理分叉功能，支持跨会话直接发消息，还加强了对 GitLab 令牌的保密处理，并优化了插件市场配置。

### 技术圈
- [理解力成为新瓶颈](https://www.geoffreylitt.com/2026/07/02/understanding-is-the-new-bottleneck) · HackerNews · 分9
  文章说现在写代码不再难，难的是理解代码背后的意图和系统逻辑。AI 能生成一堆能跑的代码，但没人真正理解它为什么这么写，于是理解成了整个研发流程里最卡脖子的环节。
- [选择无聊的技术](https://mcfunley.com/choose-boring-technology) · HackerNews · 分9
  一篇 2015 年的经典文章，核心观点是每家公司创新资源有限，应该把创新花在刀刃上，其余技术栈尽量选成熟稳定的“无聊技术”。HN 网友重新热议，并把它和 AI Agent 时代联系起来。
- [DeepSeek Harness 开发者预览版发布](https://deepseek.com/harness/en/) · HackerNews · 分9
  DeepSeek 开源了一个叫 Harness 的 AI Agent 开发框架，核心卖点是所有运行过程可追踪、可回放，并且整个架构采用插件化设计，支持热插拔。目前是早期预览版，MIT 协议。

### AI大事
- [Cerebras 加速 GPT-5.6 Sol 超快模式](https://www.cerebras.ai/blog/accelerating-gpt-5-6-sol-ultrafast-with-openai) · HackerNews · 分9
  OpenAI 和 Cerebras 合作推出 GPT-5.6 Sol 的 Ultrafast 超快模式，用专用芯片把推理速度拉满，跑完 2500 道 HLE 难题只要 11 小时，比 Claude 快…
- [AutoDesign：长周期智能体设计的元框架优化](http://arxiv.org/abs/2608.13560v1) · arXiv · 分9
  这篇论文提出一个叫 AutoDesign 的框架，让 AI 能根据反馈自动改进自己的设计流程，在论文转海报任务上超过了 Claude 的商业系统，而且成本极低。
- [QuoteBench：匹配分数如何掩盖命令路径故障](http://arxiv.org/abs/2608.13547v1) · arXiv · 分9
  这篇论文发现，评测AI编程代理时只看“匹配分数”会掩盖真实问题。他们造了个测试集，证明同样的命令，换个执行方式成功率能暴跌70多个百分点，模型排名甚至会被颠覆。
- [Grok 4.6 发布，SpaceX 团队打造最强效率模型](https://www.latent.space/p/ainews-spacexai-grok-46-and-grok) · Latent Space · 分9
  xAI 发布 Grok 4.6，性能对标 GPT-5.6 和 Claude，但价格便宜一大截，主打长任务代理和知识工作，被看作编程和排程场景的新默认选择。
- [DeepSeek V4 Pro 0813 上线，权重已开源](https://simonwillison.net/2026/Aug/12/deepseek-v4-pro-0813/) · Simon Willison · 分9
  DeepSeek 新模型 V4 Pro 0813 通过 API 上线，权重随后在 Hugging Face 开源，1.7T 参数、893GB，且不同推理等级输出差异明显。

### 供应链
- [大规模需求转移估计：受限逻辑模型方法](http://arxiv.org/abs/2608.12680v1) · arXiv · 分9
  这篇论文提出一种新方法，能在百万级商品目录下高效估算需求转移系数，即当顾客想买的商品缺货时，需求会转移到哪些替代品上，从而提升需求预测准确性。

_更新于 2026-08-14 03:39 · web-intel-bot_