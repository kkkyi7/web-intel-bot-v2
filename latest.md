# 情报 Brief · 2026-07-09

## 今日 TOP3

1. **用 Rust 重写 Bun 的完整复盘** · 分10 · 2信源
   Bun 的创始人 Jarred 用 11 天、花了 16.5 万美元的 API 费用，借助 AI Agent 把 Bun 的核心从 Zig 重写成了 Rust，并且上线后用户几乎没察觉变化。
   https://simonwillison.net/2026/Jul/8/rewriting-bun-in-rust/#atom-everything

2. **Grok 4.5 发布** · 分9
   xAI 发布了 Grok 4.5，性能对标顶级模型 Opus 4.7，但价格只有对手的一半甚至更低，核心优势是用了 Cursor 的海量真实编程数据训练，推理效率提升了 4 倍。
   https://x.ai/news/grok-4-5

3. **AI 系统提示词泄露库：Claude/GPT/Gemini 等模型底层指令公开** · 分10
   一个 GitHub 仓库持续收集并对比了 Claude、ChatGPT、Gemini 等主流 AI 模型的系统提示词（System Prompt），让你看到这些模型被设定的“底层行为规则”，比如 Claude Fable 5 和 Opus 4.8 之间具体改了啥。
   https://github.com/asgeirtj/system_prompts_leaks

## 今日精选

### AI大事
- [用 Rust 重写 Bun 的完整复盘](https://simonwillison.net/2026/Jul/8/rewriting-bun-in-rust/#atom-everything) · Simon Willison · 分10
  Bun 的创始人 Jarred 用 11 天、花了 16.5 万美元的 API 费用，借助 AI Agent 把 Bun 的核心从 Zig 重写成了 Rust，并且上线后用户几乎没察觉变化。
- [AI 系统提示词泄露库：Claude/GPT/Gemini 等模型底层指令公开](https://github.com/asgeirtj/system_prompts_leaks) · GitHub Trending · 分10
  一个 GitHub 仓库持续收集并对比了 Claude、ChatGPT、Gemini 等主流 AI 模型的系统提示词（System Prompt），让你看到这些模型被设定的“底层行为规则”，比如 Cl…
- [SpaceXAI 发布 Grok 4.5，Cursor 收购后首个 Opus 级模型](https://www.latent.space/p/ainews-spacexai-launches-grok-45) · Latent Space · 分9
  Elon Musk 的 xAI 发布了 Grok 4.5，号称是 Opus 级但更快更便宜的模型，专门为编程和 Agent 场景训练，并且是和 Cursor 合作训练的，直接对标 GPT 和 Clau…
- [Grok 4.5 发布](https://x.ai/news/grok-4-5) · HackerNews · 分9
  xAI 发布了 Grok 4.5，性能对标顶级模型 Opus 4.7，但价格只有对手的一半甚至更低，核心优势是用了 Cursor 的海量真实编程数据训练，推理效率提升了 4 倍。
- [打破数据库锁定：用 LLM 自动生成高性能存储读取器绕过数据库引擎](http://arxiv.org/abs/2607.07696v1) · arXiv · 分9
  这篇论文提出一种叫 Jailbreak 的方法，让 LLM 直接读取数据库的底层存储文件，绕过 JDBC/ODBC 等传统驱动层，实现最高 27 倍的分析查询加速，且结果与标准查询完全一致。
- [CEO 认为游戏数据比互联网更适合训练 AI](https://techcrunch.com/video/why-this-ceo-thinks-video-games-make-better-training-data-than-the-internet/) · TechCrunch AI · 分9
  这位 CEO 认为大语言模型（如 ChatGPT）缺乏对物理世界空间和时间的理解，而游戏数据（如 3D 环境、动作序列）能补上这个短板，是通往通用人工智能（AGI）的关键。

### 供应链
- [自研焊接具身大脑模型，以“智能焊工”切入工业制造具身智能赛道，「昇视唯盛」完成数亿元B轮融资｜36氪首发](https://36kr.com/p/3887871679347208?f=rss) · 36氪 · 分9
  一家叫昇视唯盛的机器人公司融了数亿元，专门做能像老焊工一样自主判断怎么焊的AI焊接机器人，不用预先编程，能适应复杂非标工件，已经在钢构、船舶等行业落地。
- [AI基础设施必须为Agent体验进化](https://www.latent.space/p/modal2026) · Latent Space · 分9
  Modal CTO 讨论为什么传统云基础设施不适合AI Agent工作负载，以及他们如何从开发者体验转向Agent体验，刚完成3.55亿美元C轮融资。

### 技术圈
- [我好像得了LLM倦怠症](https://www.alecscollon.com/blog/llm-burnout/) · HackerNews · 分9
  一位独立开发者抱怨用LLM写代码后产出翻了20倍，但人也快被累垮了。HN评论区炸了，大家普遍反映多窗口切换、模型降质、输出风格雷同让人身心俱疲。
- [微软发布Flint：面向AI智能体的可视化语言](https://microsoft.github.io/flint-chart/#/) · HackerNews · 分9
  微软开源了Flint，一种专门为AI智能体设计的可视化中间语言。它让AI能通过简单描述自动生成高质量图表，解决了现有方案要么图表丑、要么AI容易出错的两难问题。

_更新于 2026-07-09 07:43 · web-intel-bot_