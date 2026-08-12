# 情报 Brief · 2026-08-12

## 今日 TOP3

1. **窃取闭源大模型推理链** · 分9 · 2信源
   研究者发现Anthropic、OpenAI和Google的模型用同一个密钥加密思维链，把加密块喂给同系列弱模型再越狱，就能还原强模型的隐藏推理内容，目前已被修复。
   https://simonwillison.net/2026/Aug/11/stealing-reasoning-traces/#atom-everything

2. **AMD 收购 Taalas，定制 ASIC 押注推理** · 分9
   AMD 收购了做定制 AI 芯片的 Taalas，加上 Meta 新模型成本碾压、OpenAI 合并模型版本，整个行业在往“垂直整合 + 极致性价比”方向猛冲。
   https://www.latent.space/p/ainews-amd-buys-taalas

3. **Go 是 AI 辅助软件工程的理想语言** · 分9
   Google 官方博客发文论证 Go 语言最适合 AI 辅助编程，理由是语法简单、工具链完善、编译快，AI 生成的代码更容易被审查和修复。HN 评论区吵翻了，有人支持有人反对。
   https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/

## 今日精选

### AI大事
- [窃取闭源大模型推理链](https://simonwillison.net/2026/Aug/11/stealing-reasoning-traces/#atom-everything) · Simon Willison · 分9
  研究者发现Anthropic、OpenAI和Google的模型用同一个密钥加密思维链，把加密块喂给同系列弱模型再越狱，就能还原强模型的隐藏推理内容，目前已被修复。
- [让 AI 输出更易读：两个提示词技巧](https://www.bensbites.com/p/make-it-readable) · Ben's Bites · 分9
  作者发现 AI 回复越来越难读，于是测试了两个自定义指令：用 ASD-STE100 简化技术英语，以及“像对 ADHD 患者一样说话”，组合使用后输出质量提升十倍。
- [AMD 收购 Taalas，定制 ASIC 押注推理](https://www.latent.space/p/ainews-amd-buys-taalas) · Latent Space · 分9
  AMD 收购了做定制 AI 芯片的 Taalas，加上 Meta 新模型成本碾压、OpenAI 合并模型版本，整个行业在往“垂直整合 + 极致性价比”方向猛冲。
- [早报｜Manus官宣恢复独立运营/米哈游新作上线未满一月宣布停运/胖东来发放7万元「委屈奖](https://www.ifanr.com/1674811?utm_source=rss&utm_medium=rss&utm_campaign=) · 爱范儿 · 分8
  这是一篇 AI 圈早报合集，核心三条：Manus 被 Meta 收购不到一年后因监管原因恢复独立运营，前千问负责人林俊旸创业获腾讯支持，ChatGPT 和 Gemini 月活双双破 10 亿。

### GitHub 动态
- [langchain-core 发布 1.5.4 修复版](https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.5.4) · GitHubRelease · 分9
  langchain-core 从 1.5.3 升到 1.5.4，主要是修 bug，包括兼容 pydantic 2.14、修工具参数传递问题、修流式追踪器的内存泄漏，还有几个安全相关的修复。
- [crewAI 发布 1.15.15，新增流程结果与人工介入信号](https://github.com/crewAIInc/crewAI/releases/tag/1.15.15) · GitHubRelease · 分8
  crewAI 这个多智能体编排框架发了小版本更新，主要加了流程运行结果、耗时和人工介入信号的输出，修了几个安全漏洞，还统一了命令行参数格式。

### 技术圈
- [Go 是 AI 辅助软件工程的理想语言](https://developers.googleblog.com/why-go-is-an-ideal-language-for-ai-assisted-software-engineering/) · HackerNews · 分9
  Google 官方博客发文论证 Go 语言最适合 AI 辅助编程，理由是语法简单、工具链完善、编译快，AI 生成的代码更容易被审查和修复。HN 评论区吵翻了，有人支持有人反对。
- [Nvidia 的高风险生意](https://stratechery.com/2026/nvidias-risky-business/) · HackerNews · 分9
  这篇文章分析 Nvidia 在 AI 算力市场的统治地位并非牢不可破，指出其软件生态的短板、需求增长的二阶假设可能过于乐观，以及来自本地推理、中国芯片和机器人等方向的潜在威胁。

### 世界时事
- [伊朗战争致巴拿马运河拥堵](https://database.caixin.com/2026-08-12/102473291.html) · 财新网 · 分8
  伊朗战争导致全球航运绕行，巴拿马运河突然爆满，有船东愿意花400万美元插队过闸，说明全球供应链正在经历一次剧烈的路径重构和成本冲击。
- [一句“美女”换来2.15亿美元罚单](https://companies.caixin.com/2026-08-12/102473287.html) · 财新网 · 分8
  2016年一家中资银行纽约分行因员工习惯性称呼女性客户“美女”，被美国监管认定存在性别歧视与合规缺陷，开出2.15亿美元罚单，相当于该行8年利润总和。

_更新于 2026-08-12 01:35 · web-intel-bot_