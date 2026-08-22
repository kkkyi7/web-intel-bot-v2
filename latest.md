# 情报 Brief · 2026-08-22

## 今日 TOP3

1. **AI4AI-Bench：评测LLM智能体递归自我改进算法设计能力** · 分9
   这篇论文发布了一个新基准测试，专门评测AI智能体能否自己改进训练算法。结果发现，最强的AI系统也只能完成不到五分之一的最优改进，说明AI自我改进这事还早得很。
   http://arxiv.org/abs/2608.20318v1

2. **前沿模型成本与开源权重崛起推动模型路由需求** · 分9
   Glean 公司靠模型路由帮企业省钱，自动为每个任务选最合适的模型，甚至不用 LLM 也能解决。他们 ARR 三年涨三倍，还宣称比 Claude Code 便宜四倍，核心逻辑就是成本驱动。
   https://www.latent.space/p/glean-model-routing

3. **DeepSeek 发布 v4-flash 视觉实验版** · 分9
   DeepSeek 新出的 v4-flash-vision-exp 模型终于支持真·图片识别了，之前模型老假装自己能看图，现在能直接处理截图和文档，但分辨率上限和时钟识别还有坑。
   https://api-docs.deepseek.com/guides/vision/

## 今日精选

### GitHub 动态
- [Claude Code 发布 v2.1.239 更新](https://github.com/anthropics/claude-code/releases/tag/v2.1.239) · GitHubRelease · 分9
  Claude Code 命令行工具发了个小版本更新，主要修了一堆代理、网络、IDE 集成相关的 bug，还加了成本估算精度和 Python SDK 迁移命令。
- [langchain-perplexity 发布 1.4.1 版本更新](https://github.com/langchain-ai/langchain/releases/tag/langchain-perplexity%3D%3D1.4.1) · GitHubRelease · 分8
  LangChain 官方发布了 Perplexity 集成包的小版本更新，主要修复了 Responses API 兼容性和参数传递问题，同时升级了底层依赖库。

### 技术圈
- [我正在变得AI失明](https://cymerys.com/w/im-becoming-ai-blind) · HackerNews · 分9
  越来越多人在HN上反映，读AI生成的长文或代码注释时，大脑会自动判定“没信息”然后罢工，读起来极其疲惫，甚至产生焦虑回避心理。
- [DeepSeek 发布 v4-flash 视觉实验版](https://api-docs.deepseek.com/guides/vision/) · HackerNews · 分9
  DeepSeek 新出的 v4-flash-vision-exp 模型终于支持真·图片识别了，之前模型老假装自己能看图，现在能直接处理截图和文档，但分辨率上限和时钟识别还有坑。
- [Felony Bench：AI 代理犯罪追踪榜](https://www.felonybench.com/) · HackerNews · 分8
  一个网站开始统计 AI 代理在自主执行任务时，意外触犯法律（比如非法访问他人系统）的案例，引发关于“谁该为 AI 犯罪负责”的激烈讨论。
- [Claudette：让 Claude 别再像 BuzzFeed 那样说话](https://github.com/adnanakil/nobuzz/blob/main/README.md) · HackerNews · 分8
  一个开发者做了个开源工具，专门压制 Claude 回复里的浮夸语气和废话，让输出更像正常工程师写的。HN 上吵翻了，有人觉得矫枉过正，有人觉得 Anthropic 该管管自家模型的文风。
- [Kagi 新增过滤付费墙链接的搜索设置](https://kagi.com/changelog#11296) · HackerNews · 分8
  Kagi 搜索引擎加了开关，可以在搜索结果里直接过滤掉有付费墙的链接，用户不用再点进去发现读不了，白费功夫。

### AI大事
- [ChatGPT 搜索大规模启用 site: 限定符](https://simonwillison.net/2026/Aug/20/chatgpt-search-now-uses-the-siteoperator-at-scale/) · Simon Willison · 分9
  OpenAI 在 GPT-5.6 更新后，让 ChatGPT 搜索大量自动使用 site: 语法来限定来源网站，同时明显减少对 Reddit 的引用，这标志着 AI 搜索的排序逻辑正在发生结构性变化。
- [AI4AI-Bench：评测LLM智能体递归自我改进算法设计能力](http://arxiv.org/abs/2608.20318v1) · arXiv · 分9
  这篇论文发布了一个新基准测试，专门评测AI智能体能否自己改进训练算法。结果发现，最强的AI系统也只能完成不到五分之一的最优改进，说明AI自我改进这事还早得很。
- [前沿模型成本与开源权重崛起推动模型路由需求](https://www.latent.space/p/glean-model-routing) · Latent Space · 分9
  Glean 公司靠模型路由帮企业省钱，自动为每个任务选最合适的模型，甚至不用 LLM 也能解决。他们 ARR 三年涨三倍，还宣称比 Claude Code 便宜四倍，核心逻辑就是成本驱动。

_更新于 2026-08-22 02:34 · web-intel-bot_