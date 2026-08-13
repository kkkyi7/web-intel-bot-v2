# 情报 Brief · 2026-08-13

## 今日 TOP3

1. **Claude Opus 5 系统提示词全文公开** · 分9
   Simon Willison 拿到了 Claude Opus 5 的系统提示词全文，里面详细说明了 Anthropic 如何让模型处理出口管制这类敏感政治话题，核心是让模型保持事实陈述、不表达个人立场。
   https://simonwillison.net/2026/Aug/9/claude-opus-5-system-prompt/

2. **DeepSeek V4 Pro 0813 发布** · 分9
   DeepSeek 发布 V4 Pro 0813 版本，HN 上开发者实测反馈：在流量模拟和分布式物理引擎任务上表现惊艳，成本极低，有人花 12.5 美元跑了 20 亿 token 还带缓存命中。
   https://openrouter.ai/deepseek/deepseek-v4-pro-0813

3. **深度：为逼光伏制造回流，特朗普再挥大棒** · 分8
   美国对进口多晶硅和光伏组件设最低价加关税，想逼制造业回流。但业内普遍认为伤不到中国，反而推高美国自身光伏成本和电价，盟友也遭殃。
   https://m.thepaper.cn/detail/33773012

## 今日精选

### AI大事
- [与运行时无关的 AI 工作流：一种兼顾生产环境稳定性和快速评估迭代的模式](https://www.infoq.cn/article/Za8vaFWPCM7LtuRfhDmD?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  讲的是把 AI 工作流和具体运行环境解耦，让同一个流程既能快速测试新模型，又能在生产环境稳定跑，不用每次改代码重部署。
- [SpaceXAI 发布 Grok 4.6 与 Grok @Bot](https://www.latent.space/p/ainews-spacexai-grok-46-and-grok) · Latent Space · 分9
  xAI 发布 Grok 4.6，主打长时运行智能体和知识工作，性价比远超同级模型，同时推出 Grok @Bot 协作工具，Cursor 团队并入后首秀获好评。
- [Diagram-MMU：科学图表多模态基准](http://arxiv.org/abs/2608.12262v1) · arXiv · 分9
  一个专门测试多模态大模型读科学图表能力的基准，发现模型看图问答还行，但把图转成代码和改代码很难，Claude-4.6 Opus 在代理模式下三项全提升。
- [窃取专有LLM API的推理轨迹](https://simonwillison.net/2026/Aug/11/stealing-reasoning-traces/) · Simon Willison · 分9
  一篇论文发现Anthropic、OpenAI和Google返回给客户的加密推理链可以用同一家族的弱模型解密，通过越狱弱模型就能还原强模型的隐藏思考内容。目前已修复，但对LLM安全设计有重大启示。
- [Claude Opus 5 系统提示词全文公开](https://simonwillison.net/2026/Aug/9/claude-opus-5-system-prompt/) · Simon Willison · 分9
  Simon Willison 拿到了 Claude Opus 5 的系统提示词全文，里面详细说明了 Anthropic 如何让模型处理出口管制这类敏感政治话题，核心是让模型保持事实陈述、不表达个人立场…

### 技术圈
- [DeepSeek V4 Pro 0813 发布](https://openrouter.ai/deepseek/deepseek-v4-pro-0813) · HackerNews · 分9
  DeepSeek 发布 V4 Pro 0813 版本，HN 上开发者实测反馈：在流量模拟和分布式物理引擎任务上表现惊艳，成本极低，有人花 12.5 美元跑了 20 亿 token 还带缓存命中。
- [Qwen 发布 2.4T 参数开源模型，性能对标 Opus 4.8](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) · HackerNews · 分9
  阿里开源了超大 MoE 模型 Qwen3.8，2.4T 总参数但只激活 95B，性能对标 Claude Opus 4.8，但开源权重和量化版本让个人开发者也能跑起来。
- [AI 正在消灭软件工程的中产阶级吗](https://blog.florianherrengt.com/ai-removing-middle-class-software-engineering.html) · HackerNews · 分9
  HackerNews 热帖讨论 AI 对软件工程岗位结构的影响，核心观点是 AI 正在压缩中间层工程师的生存空间，但资深工程师反而更难被替代，同时低水平工程师借助 AI 可能放大技术债。

### 供应链
- [图神经网络引导遗传算法优化物理互联网供应链](http://arxiv.org/abs/2608.10245v1) · arXiv · 分9
  这篇论文提出用图神经网络帮遗传算法做初始化，解决物理互联网供应链里工厂、仓库、零售商三层网络的分配和运输优化问题，在成本不确定时比传统算法更稳更快。
- [变时域用工需求预测：引入总量约束的施工人力规划](http://arxiv.org/abs/2608.05551v1) · arXiv · 分9
  施工项目里每个任务完工时间不同，预测用工需求时预测长度得跟着变，而且每天预测人数加起来必须等于事先定好的总人数。这篇提出一个叫 CP-RAF 的方法，用相似历史任务做加权平均来分配剩余人力，既满足总量…

_更新于 2026-08-13 03:42 · web-intel-bot_