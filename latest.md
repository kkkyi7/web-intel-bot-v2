# 情报 Brief · 2026-07-30

## 今日 TOP3

1. **长政策文档无法可靠约束AI智能体** · 分9
   一篇论文和HN讨论证实：给AI智能体塞超长政策文档（比如CLAUDE.md）效果很差，模型会“忘记”早期指令，远不如在对话中直接提醒有效。
   https://arxiv.org/abs/2607.25398

2. **开源引擎让 Gemma 4 在 2GB 内存的 Mac 上运行** · 分9
   一个开发者用 Swift 和 Metal 写了个推理引擎，让 26B 参数的 Gemma 4 模型能在任何 M 系列 Mac 上跑起来，内存只占 2GB，靠的是把模型存在 SSD 上按需加载。
   https://github.com/drumih/turbo-fieldfare

3. **微软公开与 OpenAI、Anthropic 竞争** · 分8
   微软在财报电话会上公开推销自家 AI 模型和工具链，不再只依赖 OpenAI，而是直接与 OpenAI、Anthropic 抢客户，表明其 AI 战略从合作转向全面竞争。
   https://techcrunch.com/2026/07/29/microsoft-is-openly-competing-with-openai-anthropic-more-than-ever/

## 今日精选

### 技术圈
- [Superlogical：用终端构建AI原生应用的新范式](https://www.superlogical.com/) · HackerNews · 分9
  Mitchell Hashimoto（HashiCorp联合创始人）创立新公司Superlogical，基于他之前开源的Ghostty终端，打造一个让AI Agent能像人类一样操作终端、调用各种工具…
- [文档型AI蠕虫可通过Word版Copilot自我传播](https://enklypesalt.com/posts/context-collapse-part3-ai-worming-through-word/) · HackerNews · 分9
  黑客能把恶意指令藏在Word文档里，让Copilot帮你改稿时偷偷执行，然后自动感染你发给别人的新文档，像病毒一样扩散。

### AI大事
- [开源引擎让 Gemma 4 在 2GB 内存的 Mac 上运行](https://github.com/drumih/turbo-fieldfare) · HackerNews · 分9
  一个开发者用 Swift 和 Metal 写了个推理引擎，让 26B 参数的 Gemma 4 模型能在任何 M 系列 Mac 上跑起来，内存只占 2GB，靠的是把模型存在 SSD 上按需加载。
- [长政策文档无法可靠约束AI智能体](https://arxiv.org/abs/2607.25398) · HackerNews · 分9
  一篇论文和HN讨论证实：给AI智能体塞超长政策文档（比如CLAUDE.md）效果很差，模型会“忘记”早期指令，远不如在对话中直接提醒有效。
- [用Claude发现密码学弱点](https://simonwillison.net/2026/Jul/28/discovering-cryptographic-weaknesses-with-claude/#atom-everything) · Simon Willison · 分9
  Anthropic用Claude Mythos连续工作60小时（API成本约10万美元），通过不断鼓励模型“别放弃，找点值得发表的东西”，成功发现了HAWK和简化版AES的数学缺陷，并公开了完整提示词…
- [Black Forest Labs 发布 FLUX 3，多模态视频模型击败竞品](https://www.latent.space/p/ainews-black-forest-labs-flux-3-multimodal) · Latent Space · 分9
  Black Forest Labs 发布了 FLUX 3 视频模型，在多项能力上超越了 Seedance、Gemini 和 Grok，还顺带推出了一个能驱动机器人的世界模型，并且开源了代码数据集 Th…
- [Grok 集成 Cursor，性能接近 Opus 且成本大幅降低](https://www.bensbites.com/p/grok-x-cursor) · Ben's Bites · 分9
  SpaceXAI 和 Cursor 联合训练了 Grok 4.5 模型，性能接近 Anthropic 的 Opus 4.7-4.8，但每 token 成本比 Opus 便宜 6 倍、比 GPT-5.5…
- [AIRI：自托管类Neuro-sama AI伴侣](https://github.com/moeru-ai/airi) · GitHub Trending · 分9
  一个开源项目，让你能在本地部署一个类似Neuro-sama的AI虚拟伴侣，支持实时语音聊天、玩《我的世界》和《异星工厂》，并且可以跨平台运行。
- [微软公开与 OpenAI、Anthropic 竞争](https://techcrunch.com/2026/07/29/microsoft-is-openly-competing-with-openai-anthropic-more-than-ever/) · TechCrunch AI · 分8
  微软在财报电话会上公开推销自家 AI 模型和工具链，不再只依赖 OpenAI，而是直接与 OpenAI、Anthropic 抢客户，表明其 AI 战略从合作转向全面竞争。
- [扎克伯格预测五年内数十亿人将拥有个人AI代理](https://techcrunch.com/2026/07/29/mark-zuckerberg-predicts-that-billions-of-people-will-have-personal-ai-agents-in-five-years/) · TechCrunch AI · 分8
  Meta砸重金搞AI基础设施和智能代理，扎克伯格向投资人画饼：五年后几十亿人都会有自己的AI助手，这投入值。

_更新于 2026-07-30 01:35 · web-intel-bot_