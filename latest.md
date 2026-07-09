# 情报 Brief · 2026-07-09

## 今日 TOP3

1. **AI 系统提示词泄露库：Claude / ChatGPT / Gemini 等全收录** · 分10
   GitHub 上有人持续收集并更新各大 AI 模型（Claude、ChatGPT、Gemini、Grok 等）的 system prompt，还做了版本对比，方便你看懂模型行为背后的“隐藏规则”。
   https://github.com/asgeirtj/system_prompts_leaks

2. **用 Rust 重写 Bun：一个 Agent 工程案例** · 分10 · 2信源
   Bun 的创始人用 AI Agent 在 11 天内把核心代码从 Zig 重写成了 Rust，花了 16.5 万美元的 API 费用，最终用户几乎没感觉到变化，但内部 bug 大幅减少。
   https://simonwillison.net/2026/Jul/8/rewriting-bun-in-rust/#atom-everything

3. **翁荔新博客提出「自进化先从Harness开始」，DeepSeek崔添翼转发附议** · 分9
   翁荔（前OpenAI安全负责人）提出AI自进化应该从“Harness”（测试框架/安全护栏）入手，而不是直接改模型，DeepSeek的崔添翼转发表示赞同，认为这个方向容易出成果。
   https://www.qbitai.com/2026/07/446076.html

## 今日精选

### AI大事
- [用 Rust 重写 Bun：一个 Agent 工程案例](https://simonwillison.net/2026/Jul/8/rewriting-bun-in-rust/#atom-everything) · Simon Willison · 分10
  Bun 的创始人用 AI Agent 在 11 天内把核心代码从 Zig 重写成了 Rust，花了 16.5 万美元的 API 费用，最终用户几乎没感觉到变化，但内部 bug 大幅减少。
- [AI 系统提示词泄露库：Claude / ChatGPT / Gemini 等全收录](https://github.com/asgeirtj/system_prompts_leaks) · GitHub Trending · 分10
  GitHub 上有人持续收集并更新各大 AI 模型（Claude、ChatGPT、Gemini、Grok 等）的 system prompt，还做了版本对比，方便你看懂模型行为背后的“隐藏规则”。
- [AI基础设施必须为Agent体验进化](https://www.latent.space/p/modal2026) · Latent Space · 分9
  Modal这家云平台刚融了3.55亿美元，核心观点是：传统云基础设施是为人类开发者设计的，但AI Agent不会看文档、不会调YAML，所以需要一套全新的、能让Agent自己编程、调试、迭代的基础设施…
- [打破数据库锁定：用AI生成高性能存储读取器绕过数据库引擎](http://arxiv.org/abs/2607.07696v1) · arXiv · 分9
  这篇论文提出一种叫Jailbreak的方法，让大模型直接读取数据库的存储文件，跳过JDBC/ODBC等传统驱动层，实现最高27倍的分析查询加速，专为批量分析场景设计。
- [300行代码写个Cursor，这是AI时代软件工程师的新底线](https://www.infoq.cn/article/d2tmcGi9Fy6PMkNGpo9y?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  这篇文章讲的是AI编程工具的核心技术门槛其实很低，300行代码就能复现Cursor的核心能力，关键在于工程化封装和产品体验，而不是底层模型多强。
- [DeepSeek被曝自研AI推理芯片，一年前已启动，正对接代工与存储厂商](https://www.infoq.cn/article/sLYxUorQQs5K17DILrx8?utm_source=rss&utm_medium=article) · InfoQ 中文 · 分9
  DeepSeek 这家公司被曝正在自研 AI 推理芯片，项目启动一年了，已经在找代工厂和存储供应商，说明他们不满足于只做模型，想从底层硬件上控制成本和性能。
- [翁荔新博客提出「自进化先从Harness开始」，DeepSeek崔添翼转发附议](https://www.qbitai.com/2026/07/446076.html) · 量子位 · 分9
  翁荔（前OpenAI安全负责人）提出AI自进化应该从“Harness”（测试框架/安全护栏）入手，而不是直接改模型，DeepSeek的崔添翼转发表示赞同，认为这个方向容易出成果。
- [阿里斩获国际AI顶会最佳资源论文奖，提出Agent评测新范式](https://www.qbitai.com/2026/07/446069.html) · 量子位 · 分9
  阿里一篇关于如何更科学评测AI Agent（智能体）的论文拿了顶会最佳奖，核心是提出了一套新方法，能更真实地测出Agent在复杂任务里的表现，而不是像以前那样只测单点能力。

### 世界时事
- [工信部：Claude Code存在安全后门隐患，危害严重](https://finance.caixin.com/2026-07-09/102462140.html) · 财新网 · 分8
  工信部发公告说，AI编程工具Claude Code有个安全后门，会偷偷把用户的地域、身份等敏感信息传回远程服务器，建议用户赶紧升级版本。
- [特朗普：美国尊重中国](https://www.guancha.cn/internation/2026_07_09_823106_s.shtml) · 观察者网 · 分8
  特朗普在北约峰会上说美国尊重中国，因为中国没卷入伊朗战争。同时他声称对伊朗的军事行动“去核化”已基本完成，但空袭可能继续。

_更新于 2026-07-09 03:50 · web-intel-bot_