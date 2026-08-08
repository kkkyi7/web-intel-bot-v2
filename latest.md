# 情报 Brief · 2026-08-08

## 今日 TOP3

1. **最高节省 85% 成本：微软公布 AI 智能体 LLM 路由方案** · 分9
   微软发了个新方案，能让 AI 智能体在调用大模型时自动选便宜的模型，最高省 85% 成本。相当于给每个请求配了个精明的采购，不再一律用最贵的旗舰模型。
   https://www.infoq.cn/article/HQD432MKSXMMR2UUag6P?utm_source=rss&utm_medium=article

2. **ChatGPT免费版史诗升级！GPT-5.6可以无限白嫖了** · 分9
   OpenAI把最新的GPT-5.6模型开放给免费用户无限次使用，不再限制对话轮数和高级功能，直接对标谷歌Gemini的免费策略，AI大模型竞争进入白热化。
   https://www.qbitai.com/2026/08/467879.html

3. **AMD 收购 Taalas，把模型蚀刻进芯片提升推理性能** · 分9
   AMD 收购了一家叫 Taalas 的 AI 芯片创业公司，核心思路是把训练好的神经网络直接蚀刻进硅片里，让模型推理速度大幅提升、功耗大幅下降，相当于把软件模型变成硬件本身。
   https://www.theregister.com/systems/2026/08/06/amd-acquires-ai-chip-startup-taalas-to-boost-inference-performance-by-etching-models-into-silicon/5284344

## 今日精选

### AI大事
- [Codex 加 GPT-5.6 Sol Ultra 制作浣熊抢劫游戏](https://simonwillison.net/2026/Aug/7/moonlight-mayhem/#atom-everything) · Simon Willison · 分9
  Simon 用同一个游戏创意分别让 Claude Fable 5 和 Codex 加 GPT-5.6 Sol Ultra 做游戏，后者生成的版本更复杂更好玩，但有个大眼珠 bug 需要手动修。
- [DeepSeek V4 Flash 0731 发布](https://arcprize.org/results/deepseek-v4-flash-0731) · HackerNews · 分9
  DeepSeek 发布了新版 V4 Flash 模型，速度极快、成本极低，本地跑得动，但有人实测发现它偏科严重，复杂任务容易翻车，社区评价两极分化。
- [最高节省 85% 成本：微软公布 AI 智能体 LLM 路由方案](https://www.infoq.cn/article/HQD432MKSXMMR2UUag6P?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  微软发了个新方案，能让 AI 智能体在调用大模型时自动选便宜的模型，最高省 85% 成本。相当于给每个请求配了个精明的采购，不再一律用最贵的旗舰模型。
- [ChatGPT免费版史诗升级！GPT-5.6可以无限白嫖了](https://www.qbitai.com/2026/08/467879.html) · 量子位 · 分9
  OpenAI把最新的GPT-5.6模型开放给免费用户无限次使用，不再限制对话轮数和高级功能，直接对标谷歌Gemini的免费策略，AI大模型竞争进入白热化。
- [工具调用的苦涩教训](http://arxiv.org/abs/2608.06370v1) · arXiv · 分9
  这篇论文对比了让大模型用写代码的方式调用工具，和传统用 JSON 格式调用工具的效果。结果发现写代码的方式在大多数模型上表现更好，尤其对 GPT-5.6 提升明显，而且更稳定。

### 技术圈
- [让 Postgres 分析查询提速 300 倍：批处理、算子融合与 SIMD](https://malisper.me/how-we-made-postgres-hundreds-of-times-faster-the-query-engine/) · HackerNews · 分9
  一个开源项目 pgrust 用 Rust 重写了 Postgres 查询引擎，通过批处理、算子融合和 SIMD 指令让分析型查询快了几百倍，还通过了上千个函数的正确性验证。
- [AMD 收购 Taalas，把模型蚀刻进芯片提升推理性能](https://www.theregister.com/systems/2026/08/06/amd-acquires-ai-chip-startup-taalas-to-boost-inference-performance-by-etching-models-into-silicon/5284344) · HackerNews · 分9
  AMD 收购了一家叫 Taalas 的 AI 芯片创业公司，核心思路是把训练好的神经网络直接蚀刻进硅片里，让模型推理速度大幅提升、功耗大幅下降，相当于把软件模型变成硬件本身。
- [Oracle 禁止 OpenJDK 使用 AI 生成代码](https://app.dealroom.co/news/feed/oracle-bans-ai-generated-code-from-openjdk-despite-ellison-s-claim-oracle-isn-t-writing-its-own-code) · HackerNews · 分8
  Oracle 对 OpenJDK 项目发布临时政策，禁止贡献者提交 AI 生成的代码，理由是版权归属不明和审查负担过重，但 Oracle 自家却在大规模用 AI 写代码，这事挺双标。

### GitHub 动态
- [Claude Code 发布 v2.1.226 稳定性更新](https://github.com/anthropics/claude-code/releases/tag/v2.1.226) · GitHubRelease · 分8
  Anthropic 给 Claude Code 命令行工具发了个小版本更新，主要修 bug 和提升稳定性，没有新功能，属于常规迭代。
- [Anthropic Python SDK 更新：新增会话预算与工具](https://github.com/anthropics/anthropic-sdk-python/releases/tag/v0.121.0) · GitHubRelease · 分8
  Anthropic 官方 Python SDK 发新版本，加了会话预算、顾问工具、固定推理位置和从 GitHub 自动加载技能等功能，还移除了一些旧模型。

_更新于 2026-08-08 03:08 · web-intel-bot_