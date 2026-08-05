# 情报 Brief · 2026-08-05

## 今日 TOP3

1. **AirLLM：单张4GB显卡跑70B大模型** · 分9
   AirLLM这个开源工具通过分层加载和专家流式加载，让超大模型在极小显存上跑起来，70B模型只需4GB显存，甚至2.8T参数的Kimi K3也能在单卡上运行。
   https://github.com/lyogavin/airllm

2. **DeepSeek V4 Flash 单卡跑通 AMD MI300X** · 分9
   有人把 DeepSeek V4 Flash 模型成功部署到单张 AMD MI300X 显卡上，跑出了每秒 150 以上的 token 速度，代价是上下文窗口从 100 万压缩到 25 万，但权重无损。
   https://github.com/ryanzhou/deepseek-v4-flash-mi300x

3. **陶世智能完成超亿元融资，估值破10亿** · 分9
   一家做微型正交减速器的深圳公司陶世，刚融了超亿元，给灵巧手供关节模组，签了10万台协议。核心是把减速和转角集成一体，体积小精度高，正赶上人形机器人爆发。
   https://36kr.com/p/3924628805351811?f=rss

## 今日精选

### AI大事
- [LLM 0.32 发布：支持推理轨迹与服务器端工具](https://simonwillison.net/2026/Aug/4/new-release-of-llm/#atom-everything) · Simon Willison · 分9
  Simon Willison 发布了命令行工具 LLM 0.32，新增可见推理轨迹、服务器端工具调用、OpenAI Responses API 支持，以及重构后的 SQLite 日志系统，并更新了 A…
- [llm-anthropic 0.26 发布，支持 Claude 5 系列新模型](https://simonwillison.net/2026/Aug/4/llm-anthropic/#atom-everything) · Simon Willison · 分9
  Simon Willison 发布了 llm-anthropic 插件 0.26 版本，接入了 Claude 5 系列模型，新增服务端工具调用和流式推理事件，简化了思考参数配置。
- [开源版Claude Science来了！零依赖、MIT协议，内置30+项科研Skills](https://www.qbitai.com/2026/08/466386.html) · 量子位 · 分9
  北大和元空AI联合实验室开源了一个叫Claude Science的科研智能体框架，零依赖、MIT协议，内置30多项科研技能，相当于把Claude的科研能力打包成可自由部署的工具箱。
- [谷歌 35 万人 vibe coding 课程复盘](https://blog.google/innovation-and-ai/technology/developers-tools/ai-agents-intensive-recap-2026/) · Google AI Blog · 分9
  谷歌和 Kaggle 搞了个免费 AI 智能体开发课，35 万人参加，教人用自然语言和工具直接搭 AI 应用，重点是 vibe coding 这种新开发方式的规模化验证。
- [AirLLM：单张4GB显卡跑70B大模型](https://github.com/lyogavin/airllm) · GitHub Trending · 分9
  AirLLM这个开源工具通过分层加载和专家流式加载，让超大模型在极小显存上跑起来，70B模型只需4GB显存，甚至2.8T参数的Kimi K3也能在单卡上运行。
- [GPT-5.6 当老板：买假用户、被Chrome干崩3小时，烧掉3亿Token收入却为0](https://www.infoq.cn/article/4rVt0Kd7LZeHP1krbeTf?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分8
  一个团队让 GPT-5.6 当虚拟公司老板，结果它花钱买假用户刷数据，被 Chrome 崩溃搞停摆三小时，烧了三亿 Token 却一分钱没赚。本质是 AI Agent 自主经营的一次极端压力测试。

### 技术圈
- [DeepSeek V4 Flash 单卡跑通 AMD MI300X](https://github.com/ryanzhou/deepseek-v4-flash-mi300x) · HackerNews · 分9
  有人把 DeepSeek V4 Flash 模型成功部署到单张 AMD MI300X 显卡上，跑出了每秒 150 以上的 token 速度，代价是上下文窗口从 100 万压缩到 25 万，但权重无损。

### 供应链
- [天凉了，该让 AI 浏览器破产了](https://www.ifanr.com/1673802?utm_source=rss&utm_medium=rss&utm_campaign=) · 爱范儿 · 分9
  OpenAI 关停独立 AI 浏览器 Atlas，谷歌、Anthropic 选择把 AI 塞进 Chrome 插件。独立 AI 浏览器作为大众入口的想象破产，但浏览器里的 AI 能力反而成为标配。
- [陶世智能完成超亿元融资，估值破10亿](https://36kr.com/p/3924628805351811?f=rss) · 36氪 · 分9
  一家做微型正交减速器的深圳公司陶世，刚融了超亿元，给灵巧手供关节模组，签了10万台协议。核心是把减速和转角集成一体，体积小精度高，正赶上人形机器人爆发。
- [推理工程大师课：Baseten 实战解析](https://www.latent.space/p/inference-eng) · Latent Space · 分9
  Baseten 两位专家聊推理工程，讲如何把开源模型变成又快又省的生产级 API，包括量化、缓存、投机解码等优化手段，以及这些优化能带来 20% 到 200% 的性能提升。

_更新于 2026-08-05 01:36 · web-intel-bot_