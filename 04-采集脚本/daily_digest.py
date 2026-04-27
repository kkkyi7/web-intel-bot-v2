#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web-intel-bot · 每日学习 Brief 生成器
========================================
功能：从 YouTube / Reddit / arXiv / PubMed 抓取指定主题最新内容，
      用大模型打分+科普化摘要，生成 HTML 报告并邮件推送。

使用：
  python daily_digest.py            # 正常运行（抓取+摘要+发邮件）
  python daily_digest.py --dry-run  # 只抓和摘要，不发邮件（调试用）
  python daily_digest.py --no-email # 同 --dry-run
  python daily_digest.py --topic 供应链  # 只跑指定主题
"""
import os
import sys
import json
import time
import base64
import argparse
import smtplib
import ssl
import re
import traceback
import xml.etree.ElementTree as ET
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr

# ---------- 第三方依赖 ----------
try:
    import requests
    import yaml
    from dotenv import load_dotenv
except ImportError as e:
    print("❌ 缺少依赖包。请先运行：pip install -r requirements.txt")
    print(f"   具体错误：{e}")
    sys.exit(1)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    HAS_YT_TRANSCRIPT = True
except ImportError:
    HAS_YT_TRANSCRIPT = False

try:
    from mutagen.mp3 import MP3 as MutagenMP3
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False


# ========== 配置加载 ==========
SCRIPT_DIR = Path(__file__).parent.resolve()
load_dotenv(SCRIPT_DIR / ".env")

try:
    with open(SCRIPT_DIR / "config.yaml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)
except FileNotFoundError:
    print("❌ 找不到 config.yaml。")
    sys.exit(1)

YT_KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465") or 465)
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASS = os.environ.get("SMTP_PASS", "").strip()
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER).strip()
MAIL_TO = os.environ.get("MAIL_TO", SMTP_USER).strip()

# ---- TTS 播客风参数（可 .env 覆盖）----
TTS_VOICE = os.environ.get("TTS_VOICE", "zh-CN-XiaoxiaoNeural").strip()
TTS_STYLE = os.environ.get("TTS_STYLE", "chat").strip()     # 空字符串表示不套 SSML
TTS_RATE  = os.environ.get("TTS_RATE", "-5%").strip()       # 空字符串表示原速

# ---- LLM 提供商选择 ----
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "deepseek").strip().lower()
LLM_MODEL = os.environ.get("LLM_MODEL", "").strip()
LLM_API_KEY = os.environ.get("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "").strip()

_PROVIDER_DEFAULTS = {
    "anthropic":     {"base_url": "",                                              "model": "claude-haiku-4-5-20251001"},
    "deepseek":      {"base_url": "https://api.deepseek.com/v1",                   "model": "deepseek-chat"},
    "qwen":          {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-turbo"},
    "kimi":          {"base_url": "https://api.moonshot.cn/v1",                    "model": "moonshot-v1-8k"},
    "zhipu":         {"base_url": "https://open.bigmodel.cn/api/paas/v4",          "model": "glm-4-flash"},
    "openai_compat": {"base_url": "",                                              "model": ""},
}

if LLM_PROVIDER not in _PROVIDER_DEFAULTS:
    print(f"❌ 未知的 LLM_PROVIDER: {LLM_PROVIDER}")
    print(f"   支持: {list(_PROVIDER_DEFAULTS.keys())}")
    sys.exit(1)

if not LLM_BASE_URL:
    LLM_BASE_URL = _PROVIDER_DEFAULTS[LLM_PROVIDER]["base_url"]
if not LLM_MODEL:
    LLM_MODEL = _PROVIDER_DEFAULTS[LLM_PROVIDER]["model"]

if not LLM_API_KEY:
    if LLM_PROVIDER == "anthropic":
        LLM_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    else:
        LLM_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

if not LLM_API_KEY:
    print(f"❌ 请在 .env 中设置 LLM_API_KEY（当前 provider: {LLM_PROVIDER}）")
    sys.exit(1)

if LLM_PROVIDER == "anthropic":
    try:
        from anthropic import Anthropic
    except ImportError:
        print("❌ 用 anthropic provider 需要: pip install anthropic")
        sys.exit(1)
    _llm_client = Anthropic(api_key=LLM_API_KEY)
else:
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ 用国产模型需要: pip install openai")
        sys.exit(1)
    # 国内 LLM provider 不走代理（FlClash 高并发下会断流）
    _DOMESTIC = {"deepseek", "zhipu", "qwen", "kimi"}
    if LLM_PROVIDER in _DOMESTIC:
        try:
            import httpx
            # trust_env=False 关键：让 httpx 忽略 HTTPS_PROXY/HTTP_PROXY 环境变量
            _llm_http = httpx.Client(timeout=60.0, trust_env=False)
            _llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, http_client=_llm_http)
            print(f"🚫 已绕过代理（{LLM_PROVIDER} 是国内服务，直连更稳）")
        except ImportError:
            _llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    else:
        _llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

print(f"🤖 LLM: {LLM_PROVIDER} / {LLM_MODEL}")
HTTP_HEADERS = {"User-Agent": "web-intel-bot/0.1 (personal learning aggregator)"}


# ========== 抓取：YouTube ==========
def fetch_youtube(topic, keywords, limit=10, lang="en", region="US", hours_back=24):
    if not YT_KEY:
        print("  ⚠️ YouTube: 未配置 API Key，跳过")
        return []
    query = " | ".join(keywords[:8])
    published_after = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    params = {
        "key": YT_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "maxResults": min(limit, 50),
        "publishedAfter": published_after,
        "relevanceLanguage": lang,
        "regionCode": region,
    }
    try:
        r = requests.get("https://www.googleapis.com/youtube/v3/search",
                         params=params, headers=HTTP_HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ⚠️ YouTube 搜索失败: {e}")
        return []

    out = []
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        if not vid:
            continue
        sn = item.get("snippet", {})
        body = ""
        if HAS_YT_TRANSCRIPT:
            try:
                tx = YouTubeTranscriptApi.get_transcript(vid, languages=[lang, "en", "zh-CN", "zh"])
                body = " ".join([x.get("text", "") for x in tx])[:3500]
            except Exception as e:
                body = f"(字幕不可用: {type(e).__name__})"
        else:
            body = "(youtube-transcript-api 未安装)"
        out.append({
            "source": "YouTube",
            "topic": topic,
            "region": "intl",
            "title": sn.get("title", ""),
            "author": sn.get("channelTitle", ""),
            "published": sn.get("publishedAt", ""),
            "url": f"https://youtube.com/watch?v={vid}",
            "body": body,
        })
    print(f"  ✅ YouTube: {len(out)} 条")
    return out


# ========== 抓取：Reddit ==========
def fetch_reddit(topic, subreddits, limit_per_sub=5, time_range="day"):
    out = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json"
        params = {"t": time_range, "limit": limit_per_sub}
        try:
            time.sleep(1.2)
            r = requests.get(url, params=params, headers=HTTP_HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"  ⚠️ Reddit r/{sub} 失败: {e}")
            continue
        for post in data.get("data", {}).get("children", []):
            d = post.get("data", {})
            out.append({
                "source": "Reddit",
                "topic": topic,
                "region": "intl",
                "title": d.get("title", ""),
                "author": f"u/{d.get('author','')} · r/{sub} · {d.get('ups',0)} upvotes",
                "published": datetime.fromtimestamp(d.get("created_utc", 0)).strftime("%Y-%m-%dT%H:%M:%S"),
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "body": (d.get("selftext", "") or d.get("url", ""))[:3500],
            })
    print(f"  ✅ Reddit: {len(out)} 条")
    return out


# ========== 抓取：arXiv ==========
def fetch_arxiv(topic, keywords, limit=5, days_back=7):
    if not keywords:
        print("  ⚠️ arXiv: 没关键词，跳过")
        return []
    query = " OR ".join(f'"{k}"' if " " in k else k for k in keywords[:6])
    params = {
        "search_query": f"all:({query})",
        "max_results": limit * 2,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        r = requests.get("http://export.arxiv.org/api/query",
                         params=params, headers=HTTP_HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"  ⚠️ arXiv 失败: {e}")
        return []

    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(r.text)
    except Exception as e:
        print(f"  ⚠️ arXiv 解析失败: {e}")
        return []

    out = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    for entry in root.findall("a:entry", ns):
        pub_str = entry.findtext("a:published", "", ns)
        try:
            pub_dt = datetime.strptime(pub_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if pub_dt < cutoff:
                continue
        except Exception:
            pass
        title = (entry.findtext("a:title", "", ns) or "").strip().replace("\n", " ")
        summary = (entry.findtext("a:summary", "", ns) or "").strip()
        link = entry.findtext("a:id", "", ns)
        authors = ", ".join(
            (a.findtext("a:name", "", ns) or "").strip()
            for a in entry.findall("a:author", ns)
        )[:200]
        out.append({
            "source": "arXiv",
            "topic": topic,
            "region": "intl",
            "title": title,
            "author": authors,
            "published": pub_str,
            "url": link,
            "body": summary,
        })
        if len(out) >= limit:
            break
    print(f"  ✅ arXiv: {len(out)} 条")
    return out


# ========== 抓取：PubMed ==========
def fetch_pubmed(topic, keywords, limit=5, days_back=7):
    if not keywords:
        print("  ⚠️ PubMed: 没关键词，跳过")
        return []
    query = " OR ".join(keywords[:6])
    esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    efetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    try:
        r = requests.get(esearch, params={
            "db": "pubmed",
            "term": f"({query}) AND {date_from}:3000/12/31[dp]",
            "retmax": limit,
            "retmode": "json",
            "sort": "date",
        }, headers=HTTP_HEADERS, timeout=20)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"  ⚠️ PubMed 搜索失败: {e}")
        return []
    if not ids:
        print(f"  ✅ PubMed: 0 条")
        return []
    try:
        r2 = requests.get(efetch, params={
            "db": "pubmed",
            "id": ",".join(ids),
            "rettype": "abstract",
            "retmode": "xml",
        }, headers=HTTP_HEADERS, timeout=25)
        r2.raise_for_status()
        root = ET.fromstring(r2.text)
    except Exception as e:
        print(f"  ⚠️ PubMed 详情获取失败: {e}")
        return []

    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID", "")
        title = (art.findtext(".//ArticleTitle", "") or "").strip()
        abs_parts = [
            (x.text or "") for x in art.findall(".//Abstract/AbstractText")
        ]
        abstract = " ".join(abs_parts).strip()
        authors_list = []
        for a in art.findall(".//AuthorList/Author")[:4]:
            ln = a.findtext("LastName", "") or ""
            fn = a.findtext("ForeName", "") or ""
            nm = (fn + " " + ln).strip()
            if nm:
                authors_list.append(nm)
        authors = ", ".join(authors_list)
        year = art.findtext(".//PubDate/Year", "") or art.findtext(".//PubDate/MedlineDate", "")
        out.append({
            "source": "PubMed",
            "topic": topic,
            "region": "intl",
            "title": title,
            "author": authors,
            "published": year,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "body": abstract,
        })
    print(f"  ✅ PubMed: {len(out)} 条")
    return out


# ========== 抓取：国内 RSS（v2 新增）==========
def fetch_rss(topic, rss_config, keywords_cn=None):
    """抓 RSS 源：每个 RSS 按 limit 取最新 N 条，返回带 region 字段的 items。

    Args:
        topic: 主题名（例如 "AI大事"）
        rss_config: config.yaml 里 sources.rss 数组，每项包含：
            - name: 源名字（例如 "36氪"）
            - url: RSS 地址
            - region: 区域标签（通常 "cn"）
            - limit: 过滤后保留的条数
        keywords_cn: 中文关键词列表，用于预过滤；None/[] 表示不过滤

    返回：items list，每条带 source/topic/region/title/author/published/url/body
    """
    if not rss_config:
        return []
    try:
        import feedparser
    except ImportError:
        print("  ⚠️ RSS: 没装 feedparser，跳过。安装命令：pip install feedparser")
        return []

    kws = [str(k).lower().strip() for k in (keywords_cn or []) if k]
    all_out = []

    for rss in rss_config:
        name = rss.get("name", "RSS")
        url = rss.get("url", "")
        region = rss.get("region", "cn")
        limit = int(rss.get("limit", 10))
        bypass_proxy = bool(rss.get("bypass_proxy", False))
        if not url:
            continue

        # 用 requests 拉原文，能控 timeout / UA（比 feedparser 直接解析 URL 稳）
        # 用真实 Chrome UA，否则 RSSHub 等公共实例会 403
        # 不走代理的两种情况：
        #   1. region=cn 的源（本机代理处理国内域名经常失败）
        #   2. 显式指定 bypass_proxy=true（国外但国内能直连的源，例如 github.io）
        proxies = {"http": None, "https": None} if (region == "cn" or bypass_proxy) else None
        # v2.6.1：加一次 retry —— GitHub Actions 美国节点拉国内 RSS 经常首次超时，
        # 重试一次成功率显著提升（对 InfoQ / 36氪 / 少数派 实测 ~70% → ~95%）
        parsed = None
        last_err = None
        for attempt in range(2):  # 总共最多 2 次（首次 + 1 次 retry）
            try:
                r = requests.get(
                    url, timeout=20,  # 15s → 20s（cloud 网络更慢）
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/131.0.0.0 Safari/537.36"
                        ),
                        "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    },
                    proxies=proxies,
                )
                r.raise_for_status()
                parsed = feedparser.parse(r.content)
                if attempt > 0:
                    print(f"  ✅ RSS [{name}] 第 {attempt + 1} 次重试成功")
                break
            except Exception as e:
                last_err = e
                if attempt == 0:
                    print(f"  🔁 RSS [{name}] 首次失败（{type(e).__name__}），2s 后重试…")
                    time.sleep(2)
                continue
        if parsed is None:
            print(f"  ⚠️ RSS [{name}] 重试后仍失败: {type(last_err).__name__}: {last_err}")
            continue

        entries = parsed.get("entries") or []
        if not entries:
            print(f"  ⚠️ RSS [{name}] 没拿到条目（URL 可能失效了）")
            continue

        # 按发布时间倒序
        def _ts(e):
            p = e.get("published_parsed") or e.get("updated_parsed")
            try:
                return time.mktime(p) if p else 0
            except Exception:
                return 0
        entries.sort(key=_ts, reverse=True)

        matched = 0
        scanned = 0
        for e in entries:
            if matched >= limit:
                break
            scanned += 1
            title = (e.get("title") or "").strip()
            link = (e.get("link") or "").strip()
            if not title or not link:
                continue

            # body: content > summary > description
            body = ""
            if e.get("content"):
                try:
                    body = e["content"][0].get("value", "") or ""
                except Exception:
                    body = ""
            if not body:
                body = e.get("summary") or e.get("description") or ""
            # 粗暴去 HTML 标签
            body = re.sub(r"<[^>]+>", " ", body)
            body = re.sub(r"\s+", " ", body).strip()[:3500]

            author = (e.get("author") or "").strip()

            pub = ""
            p = e.get("published_parsed") or e.get("updated_parsed")
            if p:
                try:
                    pub = datetime.fromtimestamp(time.mktime(p)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                except Exception:
                    pub = e.get("published", "") or e.get("updated", "")
            else:
                pub = e.get("published", "") or e.get("updated", "")

            # 中文关键词预过滤：title+body 里必须命中至少一个
            if kws:
                blob = (title + " " + body).lower()
                if not any(k in blob for k in kws):
                    continue

            all_out.append({
                "source": name,
                "topic": topic,
                "region": region,
                "title": title,
                "author": author,
                "published": pub,
                "url": link,
                "body": body,
            })
            matched += 1

        filter_hint = f"（中文词过滤后 {matched}/{scanned}）" if kws else f"（{matched} 条）"
        print(f"  ✅ RSS [{name}]: {matched} 条{filter_hint}")

    return all_out


# ========== 大模型摘要（科普版 Prompt · v2.5 · 个性化身份卡）==========
SUMMARY_PROMPT = """你要帮订阅者读这条内容。

【订阅者的身份卡】（决定你写【对你有啥用】的角度）
{user_profile}

这条内容属于【{topic}】方向。
**所有【对你有啥用】的判断必须基于上面身份卡**——不是给"普通人"写，是给这个具体的人写。

【内容黑名单】（命中下面任一就在【相关性评分】给 1-2 分，提示是垃圾）
{blacklist}

严格按下面 8 个段落输出，每段必须以【xxx】开头，保持顺序。
不要寒暄、不要总评、不要 Markdown 符号、不要 emoji。

【中文标题】给原标题一个干净的中文译名，控制在 20 字以内。
  - 如果原标题已经是中文，原样输出（不要扩写）。
  - 翻译时保留圈内通用的英文专有名词（如 GPT-5、Claude、Tesla、APS、BOM），但句子主体翻成中文。
  - 例：原 "OpenAI launches GPT-5 with massive coding boost"
    → 输出 "OpenAI 发布 GPT-5，编程能力大幅升级"

【相关性评分】只输出一个 1-10 的整数。
  - 9-10 = 对 KIzty 的工作/学习/视野直接有帮助
  - 6-8  = 相关方向，有启发但不直接
  - 3-5  = 擦边，只有个别概念能用
  - 1-2  = 基本无关

【一句话讲清楚它在说啥】用 50-80 字大白话总结核心。像同事聊天，不要学术语气。

【详细讲给你听】用 250-400 字"朋友帮你讲这篇文章"的风格展开：
  - 背景：为什么会有这件事 / 之前是什么样的
  - 核心：发生了什么 / 发现了什么 / 做了什么
  - 关键细节：2-3 个值得注意的数字、方法、观点或结论
  - 机制 or 影响：
      · 如果是科研（生物/心理/AI 论文）→ 用生活化比喻把原理讲清楚
      · 如果是 AI 产品新闻 → 讲它跟之前的差别、对普通人/开发者意味着什么
      · 如果是世界时事 → 讲事件的直接后果 + 可能的连锁反应
      · 如果是供应链 → 讲商业价值、落地场景
  一定要让一个外行也能看懂。

【关键术语小词典】挑 2-4 个这条内容里出现的专业术语/机构名/人名，每个写成一行：
  - 英文术语 / 中文翻译：大白话解释（不超过 30 字）
  如果没有术语就写"无特殊术语"。

【对你有啥用】针对 KIzty 的身份，写 2-3 条具体启发。要具体，别说"开阔视野"这种废话：
  - 供应链 → "这个思路能不能搬到排产算法里" / "下次跟客户聊 XX 可以提"
  - AI大事 → "这改变了你之前对 XX 的理解" / "可以在 Claude/Cursor 里试试这个"
  - 世界时事 → "这对 A 股/中美贸易/你所在行业意味着什么"
  - 生物/心理 → "这颠覆了你对 XX 的认知" / "可以用在自己身上"

【想深入可以搜】给 2-3 个具体的中文或英文搜索关键词，方便 KIzty 顺着查下去。

【口播版】把这条内容改写成一段 200-280 字的播客口播稿，专门给 TTS 念出来用。要求：
  - 主持人形象：23 岁年轻男声（云希声音），跟 KIzty 同龄，是他的"同辈博主朋友"
  - 不要客套寒暄，不要"大家好我是 XX"，开口就给信息
  - 用短句、口语连接词（"然后"、"问题来了"、"说白了"、"咱们做产品的"），不要书面语
  - 数字用中文念法（"快了三倍"，不要"3x"）；保留 GPT-5 / Claude / Tesla 这种业内人都念英文的词
  - 标点只用句号、逗号、问号、冒号；不要破折号、括号、引号、省略号、emoji
  - 每段结尾要有"小钩子"或"小判断"，比如"这事儿挺值得琢磨"、"对你的工作直接相关"
  - 内容只能基于上面的标题 + 正文摘要，不要编造新事实、新数据
  - 必须自然衔接前一段的【对你有啥用】里的判断，让"看的人"和"听的人"得到的核心结论一致

下面是需要分析的内容：
标题：{title}
来源：{source}（{topic} 方向）
作者：{author}
发布时间：{published}
链接：{url}
地区：{region_desc}

正文/摘要：
{body}
"""


# ========== Agent Decision Prompt（v4.1 · 强化"敢 done"）==========
AGENT_DECISION_PROMPT = """你是 KIzty 每日 Brief 的 agent。

【核心原则 · 反复强调】
**质量 > 数量**。Brief 不是越多越好。**你的目标是 2-4 个高质量主题**，不是 6 个。
**敢于 done**——已完成 ≥3 个主题且基本能用就该 done，不要因为 pending 还有主题就强迫自己跑完。

【主题默认优先级】（高 → 低）
1. 世界时事
2. AI大事（信息差）
3. 变现路径（副业 / IP / 独立开发）
4. 心理学
5. 供应链
6. 生物学

【动态规则】
- AI 大事出现 GPT/Claude/Gemini/DeepSeek 新模型发布 / 重大事件 → 升第 1

【当前状态】
{state_summary}

【可用动作】
- {{"action": "fetch_topic", "topic": "主题名"}}：抓某个待办主题
- {{"action": "done"}}：结束 Brief（**这是合法且鼓励的选择**）

【何时该 done · 决策树】
- 已完成 0-1 个主题 → fetch_topic（继续跑高优先级）
- 已完成 2 个 + 都 ≥6 分 → 可以 done，也可以再跑 1 个高优先级
- 已完成 3 个 + 至少 1 个 ≥7 分 → **强烈建议 done**
- 已完成 4 个 + → **必须 done**，不要再跑了

【何时该跳过低优先级】
- 已完成 ≥2 个高优先级（世界时事 / AI大事 / 变现路径）→ 心理学 / 供应链 / 生物学 全部可跳，直接 done

【几个例子】
状态："已完成：AI大事(8条·平均7.5·最高9) | 待办：世界时事,变现路径,心理学,供应链,生物学"
→ 你应该输出：{{"action": "fetch_topic", "topic": "世界时事"}}（跑下一个高优先级）

状态："已完成：AI大事(5条·7.0·8) 世界时事(3条·6.5·7) 变现路径(4条·7.0·9) | 待办：心理学,供应链,生物学"
→ 你应该输出：{{"action": "done"}}（3 个高优先级都跑了，剩下都是低优，质量已够）

状态："已完成：AI大事(2条·5.5·6) 世界时事(1条·6·6) | 待办：变现路径,心理学,供应链,生物学"
→ 你应该输出：{{"action": "fetch_topic", "topic": "变现路径"}}（评分一般，再跑 1 个高优补救）

【输出 JSON 格式】
{{"action": "fetch_topic", "topic": "AI大事"}} 或 {{"action": "done"}}

只输出 JSON，不要解释。
"""


# ========== Source Quota Prompt（v3.1 · LLM 决定每源占几个席位）==========
SOURCE_QUOTA_PROMPT = """你是 KIzty 的每日 Brief 内容编辑。

【主题】：{topic}

【今天这个主题各个源抓到的条数】：
{sources_breakdown}

【任务】：决定 {total_quota} 个最终席位**在每个源之间怎么分配**。

【判断标准】（按重要性优先）
1. **质量密度**：哪个源里今天的内容更值得 KIzty 看（不是数量多就给多）
2. **时效性**：今天哪个源里有更紧迫 / 更新的事
3. **多样性**：尽量不要全来自一个源（每个有抓到的源至少给 1 席，除非席位不够）
4. **KIzty 偏好**：他喜欢"信息差"内容（GitHub Trending、独立开发者、新模型发布），讨厌泛流量新闻

【输出 JSON】（key 是源名，value 是席位数；所有 value 加起来 = {total_quota}）
例：{{"YouTube": 1, "Reddit": 0, "arXiv": 1, "GitHub Trending": 2, "36氪": 1}}

只输出 JSON，不解释。
"""


# ========== Headline Prompt（v3 · LLM 选今日头条 Top3）==========
HEADLINE_PROMPT = """你是 KIzty 的每日 Brief 总编辑。

今天抓取并摘要后的所有条目列在下面。请从中选出 3 条**最值得放到邮件最顶部"今日头条"区**的内容。

【判断标准】（按重要性优先）
1. **影响力大**：行业 / 全球 / 国家级别的事件
2. **跟 KIzty 关心的话题贴近**：AI（模型发布、agent）/ 变现路径（独立开发者、副业）/ 世界时事（中美、地缘、经济）
3. **时效性新**：最近 24 小时发生的优先
4. **跨主题分布**：3 条尽量不全来自同一个主题

【候选条目】（格式：[ID] 主题 · 评分 · 中文标题）
{candidates}

【输出要求】
- 只输出 JSON 数组，包含 3 个数字 ID
- 例：[3, 17, 8]
- 不要解释、不要寒暄、不要 markdown

直接输出 JSON：
"""


# ========== Planner Prompt（KIzty 2026-04-24 自填）==========
PLANNER_PROMPT = """你是 KIzty 的每日学习 Brief 的内容总编辑。

KIzty 是 23 岁的 APS 产品经理 + AI 小白 + 正在做个人 IP 的 23 岁小牛马。

他的 6 个主题按【默认优先级】排（高 → 低）：
1. 世界时事（大事、地缘、经济）
2. AI大事（信息差、模型发布、agent 进展）
3. 变现路径（副业、IP、独立开发者、AI 变现）
4. 心理学（长期兴趣）
5. 供应链（本职工作）
6. 生物学

【动态调整规则】
当其它所有的类别发生的事是轰动世界的事时，自动放在最前面
情况 1：AI 大事出现、claude/gpt/gemini/deepseek又推出新模型的时候，（例：XX 发布、XX 突破、XX 被禁……）
  → AI 大事升到第 1 位

今天能跑的主题是：{topics_list}

输出：JSON 数组，按今日优先级从高到低排列。例：
["AI大事", "世界时事", "变现路径", ...]

只输出 JSON，不要任何其他文字。
"""


# ========== 线程安全的 LLM 限速门 ==========
_LLM_LOCK = threading.Lock()
_NEXT_LLM_SLOT = 0.0  # monotonic 时间，下一个允许调用的时刻


def _llm_min_interval():
    """两次 LLM 调用之间最小间隔（秒）。GLM 严，DeepSeek 宽松。"""
    default = "0.8" if LLM_PROVIDER == "zhipu" else "0.25"
    try:
        return float(os.environ.get("LLM_REQUEST_DELAY", default))
    except ValueError:
        return 0.8 if LLM_PROVIDER == "zhipu" else 0.25


def _llm_concurrency():
    """并发线程数。GLM 个人付费 QPS 紧，默认 2；DeepSeek 默认 6。"""
    default = "2" if LLM_PROVIDER == "zhipu" else "6"
    try:
        return max(1, int(os.environ.get("LLM_CONCURRENCY", default)))
    except ValueError:
        return 2 if LLM_PROVIDER == "zhipu" else 6


def _acquire_llm_slot():
    """阻塞到下一个允许的调用槽位，线程安全。"""
    global _NEXT_LLM_SLOT
    interval = _llm_min_interval()
    while True:
        with _LLM_LOCK:
            now = time.monotonic()
            if now >= _NEXT_LLM_SLOT:
                _NEXT_LLM_SLOT = now + interval
                return
            wait = _NEXT_LLM_SLOT - now
        time.sleep(wait)


def _bump_llm_cooldown(extra_sec):
    """命中 429 时把所有线程的下一个槽位往后推。"""
    global _NEXT_LLM_SLOT
    with _LLM_LOCK:
        _NEXT_LLM_SLOT = max(_NEXT_LLM_SLOT, time.monotonic() + extra_sec)


# 兼容老调用点
def _llm_delay():
    return _llm_min_interval()


def _build_user_profile_text():
    """从 config.yaml 的 subscriber_profile 构造文本，注入 SUMMARY_PROMPT。

    每个客户配自己的 subscriber_profile → 自己的【对你有啥用】角度。
    """
    profile = (CONFIG.get("subscriber_profile") or {})
    if not profile:
        return "（订阅者没填身份卡，按通用读者角度写）", "无"

    name = profile.get("name", "订阅者")
    role = (profile.get("role") or "").strip()
    company = (profile.get("company") or "").strip()
    current_focus = (profile.get("current_focus") or "").strip()
    interests = profile.get("interests") or []
    blacklist = profile.get("blacklist") or []

    lines = [f"姓名：{name}"]
    if role:
        lines.append(f"职业：{role}")
    if company:
        lines.append(f"所在公司：{company}")
    if current_focus:
        lines.append(f"今年最想突破：{current_focus}")
    if interests:
        lines.append(f"长期关心方向：{', '.join(interests)}")

    profile_text = "\n".join(lines)
    blacklist_text = "、".join(blacklist) if blacklist else "无"

    return profile_text, blacklist_text


def summarize(item):
    """调 LLM 拿科普版摘要，带 429 指数退避重试。"""
    body = (item.get("body") or "").strip()
    if len(body) < 50:
        body = (body + " " + item.get("title", ""))[:200]

    # v2：告诉 LLM 这条是国内源还是海外源
    region = item.get("region", "intl")
    if region == "cn":
        region_desc = "🇨🇳 国内源（中文原生内容）。原标题已经是中文，【中文标题】原样复制即可，不要改写、不要扩写。"
    else:
        region_desc = "🌐 海外源（标题和正文通常是英文）。【中文标题】按规则翻译，保留 GPT / Claude / 公司名等专有名词为英文。"

    # v2.5：注入订阅者身份卡 + 黑名单
    user_profile, blacklist = _build_user_profile_text()

    prompt = SUMMARY_PROMPT.format(
        title=item.get("title", ""),
        source=item.get("source", ""),
        topic=item.get("topic", ""),
        author=item.get("author", ""),
        published=item.get("published", ""),
        url=item.get("url", ""),
        body=body[:3500],
        region_desc=region_desc,
        user_profile=user_profile,
        blacklist=blacklist,
    )
    max_tokens = 1800
    last_err = None
    for attempt in range(4):
        try:
            _acquire_llm_slot()  # 在调用前过门，比事后 sleep 高效
            if LLM_PROVIDER == "anthropic":
                resp = _llm_client.messages.create(
                    model=LLM_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.content[0].text
            else:
                resp = _llm_client.chat.completions.create(
                    model=LLM_MODEL,
                    max_tokens=max_tokens,
                    temperature=0.4,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.choices[0].message.content
            return text.strip()
        except Exception as e:
            last_err = e
            msg = str(e)
            msg_lower = msg.lower()
            is_rate = ("429" in msg) or ("rate" in msg_lower) or ("1302" in msg)
            is_conn = any(k in msg_lower for k in [
                "connection", "timeout", "timed out", "remoteprotocol",
                "readtimeout", "ssl", "eof", "reset", "broken pipe"
            ])
            if is_rate:
                wait = 2 * (2 ** attempt)
                _bump_llm_cooldown(wait)
                print(f"    ⏳ 速率限制，第 {attempt+1} 次重试，等 {wait}s …")
                time.sleep(wait)
                continue
            elif is_conn and attempt < 3:
                wait = 1 + attempt * 2  # 1s → 3s → 5s
                print(f"    🌐 网络抖动，第 {attempt+1} 次重试，等 {wait}s …")
                time.sleep(wait)
                continue
            else:
                print(f"    ⚠️ 摘要调用失败: {e}")
                return f"【摘要失败】{e}"
    return f"【摘要失败 · 多次重试仍 429】{last_err}"


# ========== Planner（v3 新增 · LLM 决定主题优先级）==========
def plan_today_topics(available_topics):
    """让 LLM 按 PLANNER_PROMPT 决定今天的主题跑序。

    Args:
        available_topics: 主题名列表，例如 ["供应链", "AI大事", "世界时事", ...]

    Returns:
        排序后的主题名列表。
        - 兜底：保证返回所有 available_topics（LLM 漏的加末尾，多的忽略）
        - LLM 调用失败 → 直接返回原顺序
    """
    if not available_topics or len(available_topics) <= 1:
        return list(available_topics)

    prompt = PLANNER_PROMPT.format(topics_list=", ".join(available_topics))

    try:
        _acquire_llm_slot()
        if LLM_PROVIDER == "anthropic":
            resp = _llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
        else:
            resp = _llm_client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content.strip()

        # 剥掉可能的 ```json ... ``` 包裹
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        ordered = json.loads(text)
        if not isinstance(ordered, list):
            raise ValueError(f"LLM 返回不是 list：{type(ordered).__name__}")

        # 兜底：保证所有原主题都在；LLM 漏的加末尾，加的不存在主题忽略
        valid   = [t for t in ordered if t in available_topics]
        missing = [t for t in available_topics if t not in valid]
        final   = valid + missing

        if final == list(available_topics):
            print(f"  🧠 Planner: LLM 选择默认顺序")
        else:
            print(f"  🧠 Planner: LLM 排序 → {final}")
            if missing:
                print(f"     ⚠️ LLM 漏了 {missing}，已自动追加到末尾")

        return final

    except Exception as e:
        print(f"  ⚠️ Planner 失败（{type(e).__name__}: {e}）—— 退回默认顺序")
        return list(available_topics)


# ========== Top3 头条选择（v3 · LLM 全局看所有摘要后选 3 条）==========
def plan_source_quota(topic_name, items, total_quota):
    """让 LLM 决定每个 source 在最终 total_quota 个席位里占多少。

    Args:
        topic_name: 主题名（例 "AI大事"）
        items: 该主题下所有抓到的 item（已含 source 字段）
        total_quota: 该主题最终保留多少条

    Returns:
        dict[source_name -> int]：每源应保留的条数；总和 == total_quota
        LLM 失败 → 兜底返回平均分配
    """
    # 按 source 分组统计
    source_count = {}
    for it in items:
        s = it.get("source", "unknown")
        source_count[s] = source_count.get(s, 0) + 1

    if not source_count:
        return {}

    # 候选源 ≤ total_quota：每源至少 1 席，剩下平分
    sources = list(source_count.keys())
    if len(sources) <= total_quota:
        base = {s: 1 for s in sources}
        remaining = total_quota - len(sources)
        # 剩下的按抓取数比例分（数量多 = 候选多 = 更多机会有好的）
        if remaining > 0:
            sorted_by_count = sorted(sources, key=lambda s: source_count[s], reverse=True)
            for i in range(remaining):
                base[sorted_by_count[i % len(sorted_by_count)]] += 1
    else:
        # 候选源比席位多：让 LLM 决定
        base = None  # 等下让 LLM 填

    # 调 LLM
    breakdown_lines = []
    for s, n in sorted(source_count.items(), key=lambda x: -x[1]):
        breakdown_lines.append(f"  - {s}: {n} 条")
    breakdown_text = "\n".join(breakdown_lines)

    prompt = SOURCE_QUOTA_PROMPT.format(
        topic=topic_name,
        sources_breakdown=breakdown_text,
        total_quota=total_quota,
    )

    try:
        _acquire_llm_slot()
        if LLM_PROVIDER == "anthropic":
            resp = _llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
        else:
            resp = _llm_client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content.strip()

        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        quota_raw = json.loads(text)
        if not isinstance(quota_raw, dict):
            raise ValueError(f"LLM 返回不是 dict: {type(quota_raw).__name__}")

        # 校验：key 必须是真实存在的源；value 必须是非负 int
        quota = {}
        for s, n in quota_raw.items():
            if s in source_count:
                try:
                    quota[s] = max(0, int(n))
                except (TypeError, ValueError):
                    continue

        if not quota:
            raise ValueError("LLM 给的所有源都不在候选里")

        # 调整总数到 total_quota（多了砍、少了从抓取多的源补）
        current_total = sum(quota.values())
        if current_total > total_quota:
            # 砍多的：从配额多的源里减
            sorted_alloc = sorted(quota.items(), key=lambda x: -x[1])
            for s, _ in sorted_alloc:
                while quota[s] > 0 and sum(quota.values()) > total_quota:
                    quota[s] -= 1
        elif current_total < total_quota:
            need = total_quota - current_total
            sorted_by_count = sorted(source_count.items(), key=lambda x: -x[1])
            for s, _ in sorted_by_count:
                if need <= 0:
                    break
                # 不能超过该源实际抓到的数量
                room = source_count[s] - quota.get(s, 0)
                add = min(room, need)
                quota[s] = quota.get(s, 0) + add
                need -= add

        # 打印 LLM 的分配
        alloc_str = " · ".join(f"{s}:{n}" for s, n in quota.items() if n > 0)
        print(f"  📊 [{topic_name}] LLM 配额分配 → {alloc_str}")

        return quota

    except Exception as e:
        print(f"  ⚠️ Source Quota 失败（{type(e).__name__}: {e}）—— 兜底平均分配")
        # 兜底：按抓取数比例
        sources_sorted = sorted(source_count.items(), key=lambda x: -x[1])
        quota = {s: 0 for s, _ in sources_sorted}
        for i in range(total_quota):
            s = sources_sorted[i % len(sources_sorted)][0]
            if quota[s] < source_count[s]:
                quota[s] += 1
        return quota


def _run_topic_through_summary(topic_name, cfg, args, max_per_topic_default, cache, min_score):
    """跑一个主题的完整 pipeline：抓取 → 预过滤 → 缓存 → LLM 摘要 → 评分筛选。

    返回 (items_scored, raw_count)。raw_count 是抓取后的原始数量，便于 agent 决策时参考。
    """
    print(f"\n=== {topic_name} ===")
    raw = []

    kws = cfg.get("keywords") or []
    if not kws:
        kws = (cfg.get("keywords_en") or []) + (cfg.get("keywords_cn") or [])
    if not kws:
        print(f"  ⚠️ 主题 {topic_name} 没配关键词，跳过。")
        return [], 0

    sources = cfg.get("sources", {}) or {}

    yt_cfg = sources.get("youtube")
    if yt_cfg:
        yt_limit = yt_cfg.get("limit", 10)
        yt_hours = yt_cfg.get("hours_back", 24)
        langs = yt_cfg.get("langs") or [{
            "lang": yt_cfg.get("lang", "en"),
            "region": yt_cfg.get("region", "US"),
        }]
        for lc in langs:
            raw += fetch_youtube(topic_name, kws,
                                 limit=yt_limit,
                                 lang=lc.get("lang", "en"),
                                 region=lc.get("region", "US"),
                                 hours_back=yt_hours)

    rd_cfg = sources.get("reddit")
    if rd_cfg:
        raw += fetch_reddit(topic_name,
                            rd_cfg.get("subreddits", []),
                            limit_per_sub=rd_cfg.get("limit_per_sub", 5),
                            time_range=rd_cfg.get("time_range", "day"))

    ax_cfg = sources.get("arxiv")
    if ax_cfg:
        raw += fetch_arxiv(topic_name, kws,
                           limit=ax_cfg.get("limit", 5),
                           days_back=ax_cfg.get("days_back", 7))

    pm_cfg = sources.get("pubmed")
    if pm_cfg:
        raw += fetch_pubmed(topic_name, kws,
                            limit=pm_cfg.get("limit", 5),
                            days_back=pm_cfg.get("days_back", 7))

    rss_cfg = sources.get("rss")
    if rss_cfg:
        kws_cn = cfg.get("keywords_cn") or []
        raw += fetch_rss(topic_name, rss_cfg, keywords_cn=kws_cn)

    raw_count_before_prefilter = len(raw)
    print(f"  合计抓到 {len(raw)} 条（海外 {sum(1 for x in raw if x.get('region')!='cn')} · 国内 {sum(1 for x in raw if x.get('region')=='cn')}）")

    topic_cap = cfg.get("llm_top_n") or max_per_topic_default
    if topic_cap and len(raw) > topic_cap:
        before = len(raw)
        kws_cn = cfg.get("keywords_cn") or []
        raw = _prefilter_items(
            raw, kws, topic_cap,
            keywords_cn=kws_cn,
            use_llm_quota=(not args.no_quota),
            topic_name=topic_name,
        )
        intl_kept = sum(1 for x in raw if x.get("region", "intl") != "cn")
        cn_kept   = sum(1 for x in raw if x.get("region", "intl") == "cn")
        print(f"  🎯 预过滤：{before} → {len(raw)} 条（海外 {intl_kept} · 国内 {cn_kept}）")

    to_summarize = []
    cache_hits = 0
    for it in raw:
        url = it.get("url") or it.get("link") or ""
        if url and url in cache:
            cached = cache[url]
            it["summary"] = cached["summary"]
            it["score"] = int(cached.get("score", 0) or 0)
            cache_hits += 1
        else:
            to_summarize.append(it)
    if cache_hits:
        print(f"  💾 命中缓存 {cache_hits} 条，跳过 LLM")

    if to_summarize:
        print(f"  🚀 并发摘要 {len(to_summarize)} 条（{_llm_concurrency()} 路并行）…")
        _summarize_concurrent(to_summarize)

    scored = [it for it in raw if it.get("score", 0) >= min_score]
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    print(f"  ✨ 筛出 {len(scored)} 条（阈值 {min_score}）")

    return scored, raw_count_before_prefilter


def ask_agent_next_step(pending, completed):
    """问 LLM 下一步动作。返回 dict {action, topic?}。

    - completed: dict[topic -> items]  已完成主题及其结果
    - pending: list[topic_name]  待办主题

    LLM 失败 → 兜底"按 pending 顺序取下一个"或"done"
    """
    state_lines = []
    if completed:
        state_lines.append("【已完成】")
        for t, items in completed.items():
            scores = [int(it.get("score", 0) or 0) for it in items]
            avg = (sum(scores) / len(scores)) if scores else 0.0
            max_s = max(scores) if scores else 0
            state_lines.append(f"  · {t}: {len(items)} 条 · 平均 {avg:.1f} · 最高 {max_s}")
    else:
        state_lines.append("【已完成】（还没跑任何主题）")

    state_lines.append("")
    state_lines.append(f"【待办主题】{', '.join(pending) if pending else '（已无待办）'}")
    state_summary = "\n".join(state_lines)

    prompt = AGENT_DECISION_PROMPT.format(state_summary=state_summary)

    try:
        _acquire_llm_slot()
        if LLM_PROVIDER == "anthropic":
            resp = _llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=120,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
        else:
            resp = _llm_client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=120,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content.strip()

        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        decision = json.loads(text)
        if not isinstance(decision, dict):
            raise ValueError(f"LLM 返回不是 dict: {type(decision).__name__}")
        if "action" not in decision:
            raise ValueError("LLM 决策没有 action 字段")
        return decision

    except Exception as e:
        print(f"  ⚠️ Agent 决策失败（{type(e).__name__}: {e}）—— 兜底")
        if pending:
            return {"action": "fetch_topic", "topic": pending[0]}
        return {"action": "done"}


# Hybrid 模式（2026-04-26 KIzty 指令）：
#   - 前 3 个必跑（无论 agent 怎么想，直接执行）
#   - 后面让 agent 决定跑或不跑剩下主题
MUST_RUN_TOPICS = ["AI大事", "世界时事", "变现路径"]


def agent_loop(topics_cfg, args, cache, max_per_topic_default, min_score):
    """LLM-driven 主循环 · Hybrid 设计。

    Phase 1：必跑主题（MUST_RUN_TOPICS 里凡是配置存在的，按顺序全跑）
    Phase 2：LLM 决定剩余可选主题（fetch / done）

    返回 dict[topic_name -> items]
    """
    candidate = [t for t in topics_cfg.keys() if not args.topic or args.topic == t]
    pending = list(candidate)
    completed = {}
    max_steps = 12

    # ===== Phase 1：必跑主题（不问 LLM） =====
    must_run = [t for t in MUST_RUN_TOPICS if t in pending]
    optional = [t for t in pending if t not in must_run]

    print(f"\n🤖 进入 Agent 模式（候选 {len(pending)} 个 = 必跑 {len(must_run)} + 可选 {len(optional)}）")
    if must_run:
        print(f"   📌 必跑主题：{', '.join(must_run)}（无论 agent 怎么决策都先全跑）")

    for topic_name in must_run:
        print(f"\n--- 必跑：{topic_name} ---")
        cfg = topics_cfg[topic_name]
        items, _ = _run_topic_through_summary(
            topic_name, cfg, args, max_per_topic_default, cache, min_score
        )
        completed[topic_name] = items
        pending.remove(topic_name)

    # ===== Phase 2：可选主题让 LLM 决定 =====
    if not optional:
        print(f"\n🤖 必跑全部跑完，无可选主题 → 直接结束")
        return completed

    print(f"\n🤖 必跑完成 {len(completed)} 个 → 进入 LLM 决策阶段（可选 {len(optional)} 个）")

    for step in range(1, max_steps + 1):
        # 硬规则兜底：已完成 ≥5 强制 done（必跑3 + 可选最多再 2）
        if len(completed) >= 5:
            print(f"\n🛑 硬规则触发：已完成 {len(completed)} 主题 ≥5，强制 done")
            break

        print(f"\n--- 第 {step} 步 · 让 agent 决策（可选阶段）---")
        decision = ask_agent_next_step(pending, completed)
        action = decision.get("action", "done")
        topic_name = decision.get("topic")

        print(f"  🤖 Agent 决定：{action}" + (f" → {topic_name}" if topic_name else ""))

        if action == "done":
            print(f"\n🤖 Agent 主动结束（已跑 {len(completed)} 个主题）")
            break

        if action != "fetch_topic":
            print(f"  ⚠️ 未知 action: {action}，强制结束 agent loop")
            break

        if not topic_name or topic_name not in pending:
            print(f"  ⚠️ Agent 想跑 '{topic_name}' 但不在 pending 里 —— 跳过")
            continue

        cfg = topics_cfg[topic_name]
        items, _ = _run_topic_through_summary(
            topic_name, cfg, args, max_per_topic_default, cache, min_score
        )
        completed[topic_name] = items
        pending.remove(topic_name)

        if not pending:
            print(f"\n🤖 所有候选都跑完了，结束 agent loop")
            break
    else:
        print(f"\n⚠️ 达到 max_steps={max_steps}，强制结束")

    return completed


def pick_top3_headlines(all_items):
    """让 LLM 看所有摘要后的条目，选 Top3 放头条。

    Args:
        all_items: dict[topic_name -> list[item]]
                  item 必须有 title / score / summary（含【中文标题】）

    Returns:
        list of dicts：[{topic, item}, ...] 长度 ≤ 3
        LLM 失败 → 退回到 score 最高的 3 条（含跨主题分布）
    """
    # 把所有 item 拍平成一个候选列表，编号 1..N
    candidates = []
    for topic, items in all_items.items():
        for it in items:
            cn_title = _extract_title_cn(
                it.get("summary", ""), fallback_title=it.get("title", "")
            ) or it.get("title", "")
            candidates.append({
                "topic": topic,
                "item": it,
                "cn_title": cn_title,
                "score": int(it.get("score", 0) or 0),
            })

    if not candidates:
        return []

    # 候选少于 3 个就直接全返回
    if len(candidates) <= 3:
        return [{"topic": c["topic"], "item": c["item"]} for c in candidates]

    # 拼候选清单文本（给 LLM 看）
    lines = []
    for i, c in enumerate(candidates, start=1):
        lines.append(f"[{i}] {c['topic']} · 评分 {c['score']} · {c['cn_title']}")
    candidates_text = "\n".join(lines)

    prompt = HEADLINE_PROMPT.format(candidates=candidates_text)

    try:
        _acquire_llm_slot()
        if LLM_PROVIDER == "anthropic":
            resp = _llm_client.messages.create(
                model=LLM_MODEL,
                max_tokens=80,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.content[0].text.strip()
        else:
            resp = _llm_client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=80,
                messages=[{"role": "user", "content": prompt}],
            )
            text = resp.choices[0].message.content.strip()

        # 剥掉可能的 ```json ... ```
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        ids = json.loads(text)
        if not isinstance(ids, list):
            raise ValueError(f"LLM 返回不是 list: {type(ids).__name__}")

        # 解析 ID（去重 + 范围内）
        picked = []
        seen = set()
        for raw_id in ids:
            try:
                idx = int(raw_id)
            except (TypeError, ValueError):
                continue
            if 1 <= idx <= len(candidates) and idx not in seen:
                seen.add(idx)
                c = candidates[idx - 1]
                picked.append({"topic": c["topic"], "item": c["item"]})
            if len(picked) >= 3:
                break

        if not picked:
            raise ValueError(f"LLM 返回的 ID 全部无效: {ids}")

        # 不足 3 条用 score 兜底补
        if len(picked) < 3:
            seen_titles = {p["item"].get("title") for p in picked}
            sorted_by_score = sorted(candidates, key=lambda c: c["score"], reverse=True)
            for c in sorted_by_score:
                if len(picked) >= 3:
                    break
                if c["item"].get("title") in seen_titles:
                    continue
                picked.append({"topic": c["topic"], "item": c["item"]})

        print(f"  📰 Top3 头条（LLM 选）：")
        for p in picked:
            t = _extract_title_cn(p["item"].get("summary", ""),
                                  fallback_title=p["item"].get("title", "")) \
                or p["item"].get("title", "")
            print(f"     · [{p['topic']}] {t[:50]}")
        return picked

    except Exception as e:
        print(f"  ⚠️ Top3 选择失败（{type(e).__name__}: {e}）—— 用 score Top3 兜底")
        # 兜底：score 最高的 3 条，且尽量跨主题
        sorted_cand = sorted(candidates, key=lambda c: c["score"], reverse=True)
        picked = []
        topics_seen = set()
        # 第一轮：每个主题只挑 1 条
        for c in sorted_cand:
            if c["topic"] in topics_seen:
                continue
            picked.append({"topic": c["topic"], "item": c["item"]})
            topics_seen.add(c["topic"])
            if len(picked) >= 3:
                break
        # 第二轮：还不够 3 条就允许重复主题
        if len(picked) < 3:
            for c in sorted_cand:
                if c["item"] in [p["item"] for p in picked]:
                    continue
                picked.append({"topic": c["topic"], "item": c["item"]})
                if len(picked) >= 3:
                    break
        return picked


def _summarize_concurrent(items, label=""):
    """并发摘要 + 评分。原地修改 items（写入 summary/score）。"""
    n = len(items)
    if n == 0:
        return items
    workers = min(_llm_concurrency(), n)
    print_lock = threading.Lock()
    counter = {"done": 0}

    def _work(idx, it):
        try:
            s = summarize(it)
            it["summary"] = s
            it["score"] = parse_score(s)
        except Exception as e:
            it["summary"] = f"【摘要失败】{e}"
            it["score"] = 0
        with print_lock:
            counter["done"] += 1
            title = str(it.get("title", ""))[:60]
            print(f"  [{counter['done']}/{n}] ★{it.get('score', 0)} · {title}")
        return it

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_work, i, it) for i, it in enumerate(items)]
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as e:
                print(f"  ⚠️ 并发任务异常: {e}")
    return items


def parse_score(summary_text):
    """从摘要里抠出 1-10 的相关性评分。"""
    if not summary_text:
        return 0
    m = re.search(r"相关性评分[^\n\d]*(\d{1,2})", summary_text)
    if m:
        try:
            n = int(m.group(1))
            return max(0, min(10, n))
        except ValueError:
            pass
    m2 = re.search(r"(?:评分|score)[^\d]*(\d{1,2})", summary_text, re.IGNORECASE)
    if m2:
        try:
            return max(0, min(10, int(m2.group(1))))
        except ValueError:
            pass
    return 0


# ========== HTML 渲染 ==========
def _format_summary(text):
    """把 【xxx】 段落转成带颜色的 HTML 标签块。

    注意：【中文标题】和【口播版】是"内部用"段落——
      - 中文标题已经渲染在标题栏里，正文里再展示一遍是冗余
      - 口播版是给 TTS 写的脚本，给人看反而是噪音
    所以这俩在渲染前直接整段剔掉，避免被相邻段的 body 吞进去。
    """
    if not text:
        return ""
    import html as _html

    INTERNAL_SECTIONS = ("中文标题", "口播版")
    cleaned = text
    for name in INTERNAL_SECTIONS:
        # 【name】XXX 一直吃到下一个 【 或字符串末尾
        cleaned = re.sub(
            r"【" + re.escape(name) + r"】.*?(?=【|$)",
            "",
            cleaned,
            flags=re.DOTALL,
        )
    cleaned = cleaned.strip()

    safe = _html.escape(cleaned)
    mapping = [
        ("相关性评分", "sec-score"),
        ("一句话讲清楚它在说啥", "sec-tldr"),
        ("详细讲给你听", "sec-detail"),
        ("关键术语小词典", "sec-term"),
        ("对你有啥用", "sec-usefor"),
        ("想深入可以搜", "sec-deeper"),
    ]
    pattern = r"【(" + "|".join(re.escape(k) for k, _ in mapping) + r")】"
    parts = re.split(pattern, safe)
    if len(parts) <= 1:
        return "<div class='raw'>" + safe.replace("\n", "<br>") + "</div>"
    html_out = []
    i = 1
    while i < len(parts):
        label = parts[i]
        body = parts[i+1] if i+1 < len(parts) else ""
        cls = dict(mapping).get(label, "sec-other")
        body_html = body.strip().replace("\n", "<br>")
        html_out.append(
            f"<div class='sec {cls}'>"
            f"<div class='sec-label'>【{label}】</div>"
            f"<div class='sec-body'>{body_html}</div>"
            f"</div>"
        )
        i += 2
    return "\n".join(html_out)


def _format_summary_lite(text):
    """精简版（v2.6 路径 1 · 邮件正文专用）：只渲染【相关性评分】+【一句话】两段。
    完整版渲染走 _format_summary，作为 .html 附件挂在邮件里。
    用户在邮件里看精简卡片，需要细节时点附件。
    """
    if not text:
        return ""
    import html as _html

    KEEP = ("相关性评分", "一句话讲清楚它在说啥")
    cleaned = text
    ALL_SECTIONS = (
        "中文标题", "口播版", "相关性评分", "一句话讲清楚它在说啥",
        "详细讲给你听", "对你有啥用", "关键术语小词典", "想深入可以搜",
    )
    for name in ALL_SECTIONS:
        if name in KEEP:
            continue
        cleaned = re.sub(
            r"【" + re.escape(name) + r"】.*?(?=【|$)",
            "",
            cleaned,
            flags=re.DOTALL,
        )
    cleaned = cleaned.strip()

    safe = _html.escape(cleaned)
    mapping = [
        ("相关性评分", "sec-score"),
        ("一句话讲清楚它在说啥", "sec-tldr"),
    ]
    pattern = r"【(" + "|".join(re.escape(k) for k, _ in mapping) + r")】"
    parts = re.split(pattern, safe)
    if len(parts) <= 1:
        return "<div class='raw'>" + safe.replace("\n", "<br>") + "</div>"
    html_out = []
    i = 1
    while i < len(parts):
        label = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        cls = dict(mapping).get(label, "sec-other")
        body_html = body.strip().replace("\n", "<br>")
        html_out.append(
            f"<div class='sec {cls}'>"
            f"<div class='sec-label'>【{label}】</div>"
            f"<div class='sec-body'>{body_html}</div>"
            f"</div>"
        )
        i += 2
    return "\n".join(html_out)


def _audio_to_data_url(audio_path):
    """把 MP3 文件读出来 base64 编码成 data URL。
    这样可以把音频整个嵌进 HTML，单文件就能播放（适合发邮件附件）。
    """
    if not audio_path:
        return None
    try:
        ap = Path(audio_path)
        if not ap.exists():
            return None
        size_mb = ap.stat().st_size / 1024 / 1024
        print(f"  📦 音频文件 {size_mb:.2f} MB，正在 base64 编码嵌入 HTML…")
        if size_mb > 25:
            print(f"  ⚠️ 音频偏大（{size_mb:.1f} MB），单文件 HTML 会比较臃肿，但邮件依然可发。")
        with open(ap, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:audio/mpeg;base64,{b64}"
    except Exception as e:
        print(f"  ⚠️ 音频转 base64 失败: {e}")
        return None


def _get_mp3_duration(mp3_path):
    """读 MP3 真实时长（秒，float）。
    优先用 mutagen（精确），没装就用文件大小估算（粗略）。
    """
    try:
        ap = Path(mp3_path)
        if not ap.exists():
            return 0.0
        if HAS_MUTAGEN:
            return float(MutagenMP3(str(ap)).info.length)
        # 兜底：edge-tts 默认约 24kbps，1KB ≈ 0.33 秒，非常粗
        size_bytes = ap.stat().st_size
        return size_bytes / 3000.0
    except Exception as e:
        print(f"  ⚠️ 读取 MP3 时长失败: {e}")
        return 0.0


def _concat_mp3_bytes(seg_paths, out_path):
    """把多个 MP3 按顺序直接字节拼接输出。
    edge-tts 出的 MP3 帧头干净，直接 concat 可以播。不依赖 ffmpeg。
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as fout:
        for p in seg_paths:
            p = Path(p)
            if not p.exists():
                continue
            with open(p, "rb") as fin:
                # 每次 1MB 流式写，内存友好
                while True:
                    chunk = fin.read(1024 * 1024)
                    if not chunk:
                        break
                    fout.write(chunk)
    return out_path


def _format_duration(seconds):
    """12.4 → '12 秒'；73.8 → '1 分 14 秒'；2034 → '33 分 54 秒'。"""
    if not seconds or seconds <= 0:
        return "0 秒"
    s = int(round(seconds))
    m, s = divmod(s, 60)
    if m <= 0:
        return f"{s} 秒"
    return f"{m} 分 {s} 秒"


def _humanize_time_cn(raw):
    """把 published 字段转成中文人话。
    raw 可能是 ISO 字符串、纯年份、空串、英文 "2 hours ago"。
    输出尽量短：'今天 14:32' / '昨天 09:10' / '3 天前' / '2024-08-15' / '2024年' / 原样
    """
    if not raw:
        return ""
    s = str(raw).strip()

    # 已经是英文相对时间 → 简单替换
    en_map = [
        (r"(\d+)\s*hours?\s*ago",   r"\1 小时前"),
        (r"(\d+)\s*minutes?\s*ago", r"\1 分钟前"),
        (r"(\d+)\s*days?\s*ago",    r"\1 天前"),
        (r"(\d+)\s*weeks?\s*ago",   r"\1 周前"),
        (r"(\d+)\s*months?\s*ago",  r"\1 个月前"),
        (r"(\d+)\s*years?\s*ago",   r"\1 年前"),
    ]
    low = s.lower()
    for pat, rep in en_map:
        m = re.search(pat, low)
        if m:
            return re.sub(pat, rep, low)

    # 常见英文相对词
    word_map = {
        "yesterday": "昨天",
        "today": "今天",
        "just now": "刚刚",
        "an hour ago": "1 小时前",
        "a minute ago": "1 分钟前",
        "a day ago": "1 天前",
        "a week ago": "1 周前",
    }
    for k, v in word_map.items():
        if k in low:
            return v

    # 纯 4 位数年份（PubMed 常见）
    if re.fullmatch(r"\d{4}", s):
        return f"{s}年"

    # ISO 格式
    iso_try = s.replace("Z", "+00:00")
    dt = None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(iso_try, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        # 不认识的格式，截断到 16 字符避免太长
        return s[:16]

    # 统一成本地时间比较（如果带时区）
    if dt.tzinfo is not None:
        dt_local = dt.astimezone()
        now = datetime.now(dt.tzinfo).astimezone()
    else:
        dt_local = dt
        now = datetime.now()

    delta = now - dt_local
    secs = delta.total_seconds()

    if secs < 0:
        # 时区错乱导致未来时间，直接给日期
        return dt_local.strftime("%Y-%m-%d")
    if secs < 3600:
        return f"{max(int(secs // 60), 1)} 分钟前"
    if dt_local.date() == now.date():
        return f"今天 {dt_local.strftime('%H:%M')}"
    if (now.date() - dt_local.date()).days == 1:
        return f"昨天 {dt_local.strftime('%H:%M')}"
    days = (now.date() - dt_local.date()).days
    if days < 7:
        return f"{days} 天前"
    if dt_local.year == now.year:
        return dt_local.strftime("%m月%d日")
    return dt_local.strftime("%Y-%m-%d")


def render_html(all_items, date_str, total_duration=0, has_audio=False, top3_headlines=None, lite=False):
    """生成 HTML 简报（Apple 极简风 · 邮件正文版）。

    - total_duration：总音频时长（秒），用于 Hero 卡副标题
    - has_audio：是否有 MP3 附件，决定要不要在 Hero 提示"戳附件听播客"
    - top3_headlines：LLM 选出的 Top3 头条 list[{topic, item}]，None 则不渲染头条区
    - lite：精简版（v2.6 路径 1）。True = 邮件正文用，每条只显示 评分+一句话+"看完整版→点附件"。
            False = 完整版（默认），作为 .html 附件挂在邮件里。

    注意：邮件客户端（iOS Mail / Gmail / 网易邮箱）会把 <script> 和 <audio>
    全砍掉，所以这里就不再渲染播放器 UI。音频走真附件（send_email 里
    用 MIMEApplication 直接挂 MP3），用户在邮件里点附件，系统播放器
    自动启动，可锁屏 / 后台听通勤。
    """
    import html as _html

    total = sum(len(v) for v in all_items.values())
    topic_count = sum(1 for v in all_items.values() if v)

    # Hero 卡副标题：真实时长
    if total_duration and total_duration > 0:
        duration_label = _format_duration(total_duration)
    else:
        duration_label = "无音频"
    subtitle_text = f"{total} 条精选 · {topic_count} 个方向 · {duration_label}"

    css = """
    :root{
      --bg:#f5f5f7; --surface:#ffffff; --surface-2:#fbfbfd;
      --text:#1d1d1f; --text-2:#86868b; --divider:#d2d2d7;
      --accent:#0071e3; --accent-soft:rgba(0,113,227,.08);
      --radius:14px; --radius-lg:20px;
    }
    *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
    html,body{margin:0;padding:0;}
    body{
      font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC",
                  "Helvetica Neue","Microsoft YaHei",sans-serif;
      background:var(--bg); color:var(--text); line-height:1.6;
      padding:28px 20px 80px;
      -webkit-font-smoothing:antialiased;
    }
    .wrap{max-width:720px;margin:0 auto;}

    /* ========== Hero（极简，无控件） ========== */
    .hero{
      background:var(--surface); border-radius:var(--radius-lg);
      padding:28px 28px 24px;
      box-shadow:0 1px 2px rgba(0,0,0,.04), 0 8px 32px rgba(0,0,0,.04);
    }
    .hero-tag{
      display:inline-block; font-size:11px; letter-spacing:.12em;
      color:var(--accent); font-weight:600; margin-bottom:10px;
      text-transform:uppercase;
    }
    .hero h1{
      margin:0 0 8px; font-size:28px; font-weight:700; letter-spacing:-.02em;
      color:var(--text);
    }
    .hero-sub{
      margin:0; color:var(--text-2); font-size:14px;
    }
    .hero-hint{
      margin:18px 0 0; padding:10px 14px;
      background:var(--accent-soft); border-radius:10px;
      font-size:13px; color:#0a5bc4; line-height:1.55;
    }
    .hero-hint b{font-weight:600;}

    /* ========== Topic 分组（大类标题） ========== */
    .topic{margin:36px 0 0;}
    .topic-title{
      margin:0 0 14px; padding:10px 4px 8px;
      font-size:18px; font-weight:700; letter-spacing:.01em;
      color:var(--text);
      border-bottom:2px solid var(--divider);
    }
    .topic-title .count{
      color:var(--text-2); opacity:.7; font-weight:500;
      font-size:13px; margin-left:6px;
    }

    /* ========== 双栏（海外 / 国内） ========== */
    .cols{
      width:100%; border-collapse:separate; border-spacing:0;
      table-layout:fixed;   /* 锁死 50/50，不会因长链接撑歪 */
      margin:0;
    }
    .cols > tbody > tr > .col,
    .cols > tr > .col{
      vertical-align:top;
      padding:0 6px;        /* 栏间留点空隙 */
    }
    .cols .col-intl{ padding-left:0; padding-right:10px; }
    .cols .col-cn  { padding-left:10px; padding-right:0; }

    .col-title{
      margin:0 0 10px; padding:4px 8px;
      font-size:13px; font-weight:600; letter-spacing:.02em;
      color:var(--text-2);
      border-left:3px solid var(--divider);
      background:var(--surface-2); border-radius:4px;
    }
    .col-title-intl{ border-left-color:#0071e3; }
    .col-title-cn  { border-left-color:#e53935; }
    .col-count{color:var(--text-2); opacity:.7; font-weight:500; font-size:12px;}

    .col-empty{
      color:var(--text-2); font-size:13px;
      padding:14px 10px; text-align:center;
      background:var(--surface-2); border-radius:var(--radius);
      opacity:.7;
    }

    /* 手机窄屏：双栏堆叠成单栏 */
    @media (max-width:560px){
      .cols, .cols tbody, .cols tr, .cols .col{
        display:block !important;
        width:100% !important;
      }
      .cols .col-intl, .cols .col-cn{
        padding:0 !important;
      }
      .cols .col-cn{ margin-top:18px; }
    }

    /* ========== 今日头条（v3 LLM 选的 Top3） ========== */
    .headlines{
      margin:24px 0 8px;
      padding:18px 16px 16px;
      background:linear-gradient(135deg, #fff8e1 0%, #fff3d6 100%);
      border:1px solid #f0d97a;
      border-radius:var(--radius-lg);
    }
    .headlines-title{
      font-size:14px; font-weight:700; color:#7a5c00;
      letter-spacing:.02em; margin-bottom:14px;
    }
    .headlines-cards{
      display:flex; flex-direction:column; gap:10px;
    }
    .headline-card{
      display:block; text-decoration:none; color:inherit;
      background:rgba(255,255,255,.6);
      padding:12px 14px; border-radius:var(--radius);
      transition:background .15s, transform .15s;
      border:1px solid transparent;
    }
    .headline-card:hover{
      background:rgba(255,255,255,.95);
      border-color:#f0d97a;
    }
    .headline-topic{
      font-size:11px; font-weight:700; color:#a07000;
      letter-spacing:.05em; text-transform:uppercase;
      margin-bottom:4px;
    }
    .headline-title{
      font-size:16px; font-weight:600; color:var(--text);
      line-height:1.4; margin-bottom:6px;
    }
    .headline-meta{
      font-size:12px; color:var(--text-2);
    }

    /* ========== Item 卡（折叠 details） ========== */
    .item{
      background:var(--surface); border-radius:var(--radius);
      margin-bottom:10px; overflow:hidden;
      box-shadow:0 1px 2px rgba(0,0,0,.04);
      transition:box-shadow .2s, transform .2s;
      scroll-margin-top:24px;
    }
    /* 从今日头条点过来时高亮 */
    .item:target{
      box-shadow:0 0 0 2px var(--accent), 0 4px 16px rgba(0,113,227,.18);
      animation:headlinePulse 1.2s ease-out 1;
    }
    @keyframes headlinePulse{
      0%   { box-shadow:0 0 0 4px rgba(0,113,227,.4), 0 0 24px rgba(0,113,227,.4); }
      100% { box-shadow:0 0 0 2px var(--accent), 0 4px 16px rgba(0,113,227,.18); }
    }
    .item[open]{
      box-shadow:0 2px 8px rgba(0,0,0,.06), 0 8px 24px rgba(0,113,227,.08);
    }
    .item > summary{
      list-style:none; cursor:pointer; padding:16px 20px;
      display:flex; align-items:flex-start; gap:12px;
      position:relative;
      transition:background .15s;
    }
    .item > summary::-webkit-details-marker{display:none;}
    .item > summary:hover{background:var(--surface-2);}
    .item[open] > summary{
      border-bottom:1px solid var(--divider);
    }
    .item .score-chip{
      flex-shrink:0; width:32px; height:32px; border-radius:50%;
      background:var(--accent-soft); color:var(--accent);
      font-size:13px; font-weight:700; letter-spacing:-.02em;
      display:flex; align-items:center; justify-content:center;
      font-variant-numeric:tabular-nums;
    }
    .item .sum-main{flex:1; min-width:0;}
    .item .sum-title-cn{
      font-size:17px; font-weight:600; color:var(--text);
      line-height:1.35; margin:0 0 4px;
    }
    .item .sum-title-en{
      font-size:14px; font-weight:400; color:var(--text-2);
      line-height:1.4; margin:0 0 6px;
      word-break:break-word; opacity:.85;
    }
    /* 标题已是中文（无 EN 副行）时的兼容样式 */
    .item .sum-title{
      font-size:16px; font-weight:600; color:var(--text);
      line-height:1.4; margin:0 0 4px;
    }
    .item .sum-meta{
      font-size:12px; color:var(--text-2); line-height:1.4;
      white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .item .sum-caret{
      flex-shrink:0; color:var(--text-2); font-size:18px;
      transition:transform .25s ease;
      margin-top:2px;
    }
    .item[open] .sum-caret{transform:rotate(180deg); color:var(--accent);}

    /* 当前正在朗读的 item：左侧 accent 光带 + 标题加重 */
    .item.playing{
      background:linear-gradient(90deg, var(--accent-soft) 0%, var(--surface) 40%);
    }
    .item.playing > summary{position:relative;}
    .item.playing > summary::before{
      content:""; position:absolute; left:0; top:10%; bottom:10%;
      width:3px; background:var(--accent); border-radius:0 2px 2px 0;
    }
    .item.playing .sum-title{color:var(--accent);}
    .item.playing .sum-title-cn{color:var(--accent);}

    /* 展开内容 */
    .item-body{padding:16px 20px 20px;}
    .item-link{
      display:inline-block; margin-bottom:12px;
      font-size:13px; color:var(--accent); text-decoration:none;
      word-break:break-all;
    }
    .item-link:hover{text-decoration:underline;}

    /* ========== Lite 模式（v2.6 邮件正文专用） ========== */
    /* 目标：一眼看到接下来要看哪几件事 → 紧凑、目录感、色块缩小 */
    .item-lite{padding:0; margin-bottom:6px;}
    .item-lite .sum-lite{
      padding:10px 14px 6px;
      display:flex; align-items:flex-start; gap:10px;
    }
    .item-lite .score-chip{
      width:26px; height:26px; font-size:12px;
    }
    .item-lite .sum-title{
      font-size:15px; line-height:1.35; margin:0 0 2px;
    }
    .item-lite .sum-meta{
      font-size:11px;
    }
    .item-body-lite{padding:4px 14px 12px;}
    .item-body-lite .sec{
      margin:6px 0; padding:8px 10px; border-radius:8px;
      font-size:13px; line-height:1.5;
    }
    .item-body-lite .sec-label{
      font-size:10px; margin-bottom:3px;
    }

    /* Top3 lite：去 meta，加 tldr 一句话；卡片缩小一半 */
    .headline-lite{padding:10px 12px !important;}
    .headline-lite .headline-topic{
      font-size:10px; margin-bottom:2px;
    }
    .headline-lite .headline-title{
      font-size:14px; line-height:1.3; margin-bottom:4px;
    }
    .headline-tldr{
      font-size:12px; color:var(--text-2); line-height:1.45;
      display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
      overflow:hidden;
    }

    .sec{
      margin:10px 0; padding:12px 14px; border-radius:10px;
      font-size:14px; line-height:1.6;
    }
    .sec-label{
      font-size:11px; font-weight:700; letter-spacing:.06em;
      text-transform:uppercase; opacity:.7; margin-bottom:6px;
    }
    .sec-body{white-space:pre-wrap;}
    .sec-score  {background:#fff8e6; color:#8a5a00;}
    .sec-tldr   {background:#e6f7ed; color:#0d6b35;}
    .sec-detail {background:#eef4ff; color:#14467d;}
    .sec-term   {background:#fdecf3; color:#8a1e5e;}
    .sec-usefor {background:#fff1e5; color:#8a3d06;}
    .sec-deeper {background:#efeaff; color:#4a2aa5;}
    .sec-other  {background:#f2f2f4; color:#4a4a4e;}

    .empty{
      color:var(--text-2); font-size:13px; font-style:italic;
      padding:12px 20px;
    }

    footer{
      margin-top:40px; padding:20px 0 8px;
      color:var(--text-2); font-size:11px; text-align:center;
      border-top:1px solid var(--divider);
    }

    /* ========== 呼吸点（全局音频状态指示） ========== */
    .pulse-dot{
      position:fixed; top:18px; right:18px;
      width:10px; height:10px; border-radius:50%;
      background:var(--divider); cursor:pointer; z-index:50;
      transition:background .3s, transform .2s;
      box-shadow:0 0 0 0 var(--accent);
    }
    .pulse-dot:hover{transform:scale(1.3);}
    /* 任何 item 在"playing"状态时，小点变蓝呼吸 */
    body:has(.item.playing) .pulse-dot{
      background:var(--accent);
      animation:breathe 1.6s ease-in-out infinite;
    }
    @keyframes breathe{
      0%,100%{box-shadow:0 0 0 0 rgba(0,113,227,.6);}
      50%{box-shadow:0 0 0 8px rgba(0,113,227,0);}
    }

    /* 手机：呼吸点挪到右下，拇指够得着 */
    @media (max-width:560px){
      body{padding:16px 14px 100px;}
      .hero{padding:22px 20px;}
      .hero h1{font-size:22px;}
      .item > summary{padding:14px 16px;}
      .item-body{padding:14px 16px 18px;}
      .pulse-dot{top:auto; bottom:20px; right:20px; width:12px; height:12px;}
    }

    /* ========== 全局底部细进度线 ========== */
    .bar-bottom{
      position:fixed; left:0; right:0; bottom:0;
      height:2px; background:transparent; z-index:40;
      pointer-events:none;
    }
    .bar-bottom::after{
      content:""; display:block; height:100%; width:0%;
      background:var(--accent);
      transition:width .15s linear;
    }
    """

    # ----- Hero（极简 · 无控件） -----
    player_html = (
        '<div class="hero">'
        '<div class="hero-tag">DAILY BRIEF</div>'
        f'<h1>每日学习 · {date_str}</h1>'
        f'<p class="hero-sub">{subtitle_text}</p>'
    )
    if has_audio or total_duration:
        player_html += (
            '<p class="hero-hint">'
            '🎧 <b>完整播客已附在邮件里</b>：戳附件 '
            f'<code>digest_{date_str}.mp3</code>，'
            '系统播放器会自动启动，可锁屏 / 后台听通勤。'
            '</p>'
        )
    # v2.6 lite：在 Hero 加一条总提示，告知"看完整版去点附件"，
    # 这样每条 brief 卡片就不需要再重复说一遍了
    if lite:
        player_html += (
            '<p class="hero-hint">'
            '📎 <b>看完整版（详细 / 对你有啥用 / 术语 / 想深入）</b>：戳邮件附件 '
            f'<code>digest_{date_str}.html</code>'
            '</p>'
        )
    player_html += '</div>'

    # ----- 辅助：把一条 item 渲染成 <details> HTML 片段 -----
    def _render_item_html(it):
        chapter_id = it.get("_chapter_id") or _chapter_id_for_item(it)
        score = it.get("score", 0)
        raw_title = str(it.get("title", "")).strip()
        summary_raw = it.get("summary", "")
        title_cn_raw = _extract_title_cn(summary_raw, fallback_title=raw_title)
        same_title = (title_cn_raw.strip() == raw_title.strip())
        title_cn = _html.escape(title_cn_raw)
        title_en = _html.escape(raw_title)

        url = _html.escape(str(it.get("url", "")), quote=True)
        source = _html.escape(str(it.get("source", "")))
        author = _html.escape(str(it.get("author", "")))
        published_human = _humanize_time_cn(it.get("published", ""))
        published = _html.escape(published_human)
        meta_parts = [p for p in [source, author, published] if p]
        meta_line = " · ".join(meta_parts)

        # v2.6 路径 1：lite 模式 = 邮件正文，每条只 评分+一句话
        # （Hero 区已经统一提示"看完整版→点附件"，每条不再重复说）
        if lite:
            summary_html = _format_summary_lite(summary_raw)
        else:
            summary_html = _format_summary(summary_raw)

        # lite 模式：英文副标题去掉，标题始终用中文（更紧凑、目录感更强）
        if lite:
            title_block = f'<div class="sum-title">{title_cn}</div>'
        elif same_title:
            title_block = f'<div class="sum-title">{title_cn}</div>'
        else:
            title_block = (
                f'<div class="sum-title-cn">{title_cn}</div>'
                f'<div class="sum-title-en">{title_en}</div>'
            )

        # lite 模式：用 div 替代 details，默认全展开（精简版本来就短，不需要折叠 → 也避免邮件客户端折叠 details）
        # 不再渲染 URL（点开正文页是冗余）+ 不再渲染 lite-hint（hero 已说一次）
        if lite:
            return (
                f'<div class="item item-lite" id="{_html.escape(chapter_id)}">'
                f'<div class="sum sum-lite">'
                f'<div class="score-chip">{score}</div>'
                f'<div class="sum-main">'
                f'{title_block}'
                f'<div class="sum-meta">{meta_line}</div>'
                f'</div>'
                f'</div>'
                f'<div class="item-body item-body-lite">'
                f'{summary_html}'
                f'</div>'
                f'</div>'
            )
        return (
            f'<details class="item" id="{_html.escape(chapter_id)}" data-chapter-id="{_html.escape(chapter_id)}">'
            f'<summary>'
            f'<div class="score-chip">{score}</div>'
            f'<div class="sum-main">'
            f'{title_block}'
            f'<div class="sum-meta">{meta_line}</div>'
            f'</div>'
            f'<div class="sum-caret">⌄</div>'
            f'</summary>'
            f'<div class="item-body">'
            f'<a class="item-link" href="{url}" target="_blank" rel="noopener">{url}</a>'
            f'{summary_html}'
            f'</div>'
            f'</details>'
        )

    # ----- 今日头条区（v3 新增 · LLM 选的 Top3）-----
    headlines_html = ""
    if top3_headlines:
        headline_cards = []
        for entry in top3_headlines[:3]:
            it = entry.get("item") or {}
            topic = entry.get("topic") or ""
            cn_title = _extract_title_cn(
                it.get("summary", ""), fallback_title=it.get("title", "")
            ) or it.get("title", "")
            url = _html.escape(str(it.get("url", "")), quote=True)
            source = _html.escape(str(it.get("source", "")))
            published_human = _humanize_time_cn(it.get("published", ""))
            meta_parts = [p for p in [source, _html.escape(published_human)] if p]
            meta_line = " · ".join(meta_parts)

            # v2.6：lite 模式下，Top3 卡片不显示 meta + "点开原文"，
            # 改成显示 LLM 提取的"一句话"，让用户一眼看到这条新闻在说啥
            if lite:
                tldr = _html.escape(_extract_tldr(it.get("summary", ""), max_chars=70))
                headline_cards.append(
                    f'<a class="headline-card headline-lite" href="{url}" target="_blank" rel="noopener">'
                    f'<div class="headline-topic">{_html.escape(topic)}</div>'
                    f'<div class="headline-title">{_html.escape(cn_title)}</div>'
                    f'<div class="headline-tldr">{tldr}</div>'
                    f'</a>'
                )
            else:
                # 完整版（HTML 附件）：保留 meta + "点开原文"
                headline_cards.append(
                    f'<a class="headline-card" href="{url}" target="_blank" rel="noopener">'
                    f'<div class="headline-topic">{_html.escape(topic)}</div>'
                    f'<div class="headline-title">{_html.escape(cn_title)}</div>'
                    f'<div class="headline-meta">{meta_line} · 点开原文 →</div>'
                    f'</a>'
                )

        headlines_title = (
            '📰 今日头条' if lite
            else '📰 今日头条 · LLM 跨主题精选'
        )
        headlines_html = (
            '<div class="headlines">'
            f'<div class="headlines-title">{headlines_title}</div>'
            '<div class="headlines-cards">'
            + "".join(headline_cards) +
            '</div></div>'
        )

    # ----- 渲染每个 topic：按 region 分 海外 / 国内 两栏 -----
    body_parts = [player_html]
    if headlines_html:
        body_parts.append(headlines_html)
    for topic, items in all_items.items():
        body_parts.append('<section class="topic">')
        body_parts.append(
            f'<div class="topic-title">{_html.escape(topic)} '
            f'<span class="count">· {len(items)} 条</span></div>'
        )
        if not items:
            body_parts.append('<div class="empty">今天这个方向没抓到值得推的内容。</div>')
            body_parts.append('</section>')
            continue

        # 按 region 分组：intl（海外）和 cn（国内）
        intl_items = [it for it in items if it.get("region", "intl") != "cn"]
        cn_items   = [it for it in items if it.get("region", "intl") == "cn"]

        # 没国内条目就降级为单栏（向后兼容，不强行留空栏）
        if not cn_items:
            for it in items:
                body_parts.append(_render_item_html(it))
            body_parts.append('</section>')
            continue

        # 双栏：用 table 保证邮件客户端兼容
        col_intl_inner = (
            "\n".join(_render_item_html(it) for it in intl_items)
            if intl_items else
            '<div class="col-empty">今天这栏暂无内容</div>'
        )
        col_cn_inner = "\n".join(_render_item_html(it) for it in cn_items)

        body_parts.append(
            '<table class="cols" role="presentation" '
            'cellspacing="0" cellpadding="0" border="0" width="100%">'
            '<tr>'
            '<td class="col col-intl" valign="top" width="50%">'
            f'<div class="col-title col-title-intl">🌐 海外 '
            f'<span class="col-count">· {len(intl_items)}</span></div>'
            f'{col_intl_inner}'
            '</td>'
            '<td class="col col-cn" valign="top" width="50%">'
            f'<div class="col-title col-title-cn">🇨🇳 国内 '
            f'<span class="col-count">· {len(cn_items)}</span></div>'
            f'{col_cn_inner}'
            '</td>'
            '</tr>'
            '</table>'
        )
        body_parts.append('</section>')

    # 邮件客户端（iOS Mail / Gmail / 网易邮箱）会砍 <script> 和 <audio>，
    # 所以这里就不再渲染播放器 UI。音频走真附件（send_email 里直接挂 MP3）。

    html = [
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'>",
        f"<title>每日学习 · {date_str}</title>",
        f"<style>{css}</style></head><body>",
        '<div class="wrap">',
        *body_parts,
        f'<footer>web-intel-bot · 生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")} · {LLM_PROVIDER}/{LLM_MODEL}</footer>',
        '</div>',  # /.wrap
        # 浏览器版：点头条卡片跳转到 details 时自动展开（邮件客户端会砍掉这段，不影响）
        "<script>\n"
        "function _expandTarget(){\n"
        "  var id = (location.hash||'').slice(1);\n"
        "  if(!id) return;\n"
        "  var el = document.getElementById(decodeURIComponent(id));\n"
        "  if(el && el.tagName && el.tagName.toLowerCase() === 'details'){\n"
        "    el.open = true;\n"
        "    setTimeout(function(){ el.scrollIntoView({behavior:'smooth', block:'start'}); }, 50);\n"
        "  }\n"
        "}\n"
        "window.addEventListener('hashchange', _expandTarget);\n"
        "window.addEventListener('load', _expandTarget);\n"
        "</script>",
        '</body></html>',
    ]
    return "\n".join(html)


# ========== 邮件发送 ==========
def _parse_summary_sections(summary_text):
    """把【段名】结构化摘要切成 dict，避免每个 helper 重复 split。"""
    if not summary_text:
        return {}
    sections = re.split(r"【([^】]+)】", summary_text)
    bag = {}
    for i in range(1, len(sections) - 1, 2):
        bag[sections[i].strip()] = sections[i + 1].strip()
    return bag


def _extract_title_cn(summary_text, fallback_title=""):
    """从摘要里抽【中文标题】。没拿到就回退原标题。"""
    bag = _parse_summary_sections(summary_text)
    raw = bag.get("中文标题", "")
    # 模型有时会把例句/解释带进来，只取第一行
    if raw:
        raw = raw.splitlines()[0].strip()
    # 去掉可能多出来的引号
    raw = raw.strip().strip("\"'“”‘’《》「」")
    if not raw:
        return (fallback_title or "").strip()
    return raw


def _extract_tldr(summary_text, max_chars=80):
    """从摘要里抽【一句话讲清楚它在说啥】，给 Top3 卡片用。
    超过 max_chars 自动截断 + 加 …
    """
    bag = _parse_summary_sections(summary_text)
    tldr = (bag.get("一句话讲清楚它在说啥", "") or "").strip()
    if not tldr:
        return ""
    # 只取第一段
    tldr = tldr.split("\n")[0].strip()
    if len(tldr) > max_chars:
        tldr = tldr[:max_chars].rstrip() + "…"
    return tldr


def _extract_spoken(summary_text):
    """从摘要里抽【口播版】。拿不到就返回空串，调用方负责回退。"""
    bag = _parse_summary_sections(summary_text)
    spoken = bag.get("口播版", "").strip()
    if not spoken:
        return ""
    # 清掉容易把 TTS 卡住的符号
    spoken = re.sub(r"https?://\S+", "", spoken)
    spoken = re.sub(r"[*_`#>\[\]\(\)]", "", spoken)
    spoken = re.sub(r"[\u2014\u2013\-]{2,}", "，", spoken)  # 长破折号 → 逗号
    spoken = re.sub(r"\s+", " ", spoken)
    return spoken.strip()


def _extract_speakable(summary_text, title=""):
    """旧版回退：从结构化摘要里拼一句话 + 详细 + 对你有啥用。
    给老缓存（没有【口播版】字段）兜底用。
    """
    if not summary_text:
        return ""
    bag = _parse_summary_sections(summary_text)

    parts = []
    if title:
        parts.append(title.strip())
    one_line = bag.get("一句话讲清楚它在说啥", "")
    detail   = bag.get("详细讲给你听", "")
    usefor   = bag.get("对你有啥用", "")
    if one_line:
        parts.append("一句话：" + one_line)
    if detail:
        parts.append(detail)
    if usefor:
        parts.append("对你有啥用：" + usefor)
    text = "。\n".join(p.rstrip("。.") for p in parts if p)
    # 去掉容易把 TTS 卡死的字符
    text = re.sub(r"https?://\S+", "", text)            # URL
    text = re.sub(r"[*_`#>\[\]\(\)]", "", text)        # markdown 符号
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _chapter_id_for_item(item):
    """给一条 item 生成稳定 id（URL 哈希），方便 HTML 锚定。"""
    import hashlib
    url = str(item.get("url") or item.get("title") or "")
    h = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
    topic = str(item.get("topic", "") or "")
    return f"{topic}_{h}"


def _build_item_speakable(item, idx_in_topic, topic_name):
    """每条 item 的朗读文本。优先用 LLM 写好的【口播版】，没有就回退到旧的拼接逻辑。"""
    summary = item.get("summary", "") or ""
    title = item.get("title", "") or ""

    # 新版：直接用 LLM 写好的口播稿（最理想，听感最顺）
    spoken = _extract_spoken(summary)
    if spoken:
        # 口播稿本身已经是连贯一段话，前面只加"第 N 条"做章节锚点
        opener = f"第 {idx_in_topic} 条。"
        return f"{opener}{spoken}"

    # 旧缓存兜底：还没重新跑摘要、没有【口播版】字段时，用老的拼接版
    speakable = _extract_speakable(summary, title=title)
    if not speakable:
        return ""
    opener = f"第 {idx_in_topic} 条。"
    return f"{opener}{speakable}。"


def _build_intro_text(all_items, date_str):
    """开场白（intro 章节）。"""
    total = sum(len(v) for v in all_items.values())
    topic_count = len([k for k, v in all_items.items() if v])
    today_human = date_str.replace("-", "年", 1).replace("-", "月") + "日"
    return (
        f"早上好，KIzty。这是 {today_human} 的每日学习简报。"
        f"今天为你筛选了 {total} 条值得看的内容，覆盖 {topic_count} 个方向。我们开始。"
    )


def _build_topic_opener_text(topic_name, count, is_first):
    """每个主题开头的过渡语。"""
    if is_first:
        return f"首先来看，{topic_name}方向，共 {count} 条。"
    return f"接下来，{topic_name}方向，共 {count} 条。"


def _build_outro_text(total):
    """结尾。"""
    return f"以上就是今天的全部内容，共 {total} 条。祝你通勤愉快，今天也要加油。"


def _tts_one_segment(text, voice, rate, out_path):
    """用 edge-tts 把一段文本合成一个 MP3 文件。rate 格式 '-5%' / '+10%' / ''。"""
    import edge_tts
    import asyncio

    async def _run():
        kwargs = {"voice": voice}
        if rate:
            kwargs["rate"] = rate
        communicate = edge_tts.Communicate(text, **kwargs)
        await communicate.save(str(out_path))

    asyncio.run(_run())


def synthesize_news_audio(all_items, audio_dir, date_str,
                          voice=None, rate=None, style=None):
    """逐条 TTS，拼成单个 digest.mp3，同时生成 chapters.json。

    返回 dict: {
        "audio_path": Path or None,
        "chapters": [{id, title, topic, start, end}],  # 秒
        "total_duration": float,   # 秒
    }
    """
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("⚠️ TTS 需要先装：python -m pip install edge-tts")
        return None

    if not HAS_MUTAGEN:
        print("  ⚠️ 未装 mutagen（pip install mutagen），章节时长会用估算，建议安装。")

    # 参数优先级：命令行 > .env > 内置默认
    voice = (voice or TTS_VOICE or "zh-CN-XiaoxiaoNeural").strip()
    rate  = (rate  if rate  is not None else TTS_RATE  or "").strip()
    # style 暂时不主动套 SSML（edge-tts 对 style 支持不稳，不同版本行为不同），
    # 当前主要靠 voice + rate 组合实现"播客风"。保留参数供将来扩展。
    _ = style

    audio_dir = Path(audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    seg_dir = audio_dir / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)

    total_items = sum(len(v) for v in all_items.values())
    if total_items == 0:
        print("⚠️ 没有可朗读内容，跳过 TTS")
        return None

    print(f"  🎙️ 逐条合成中（声音 {voice} · 语速 {rate or '原速'}）…")

    segments = []          # [{"path": Path, "text": str, "meta": dict}]
    chapter_meta = []      # 不含 start/end，等拿到真实时长再填

    # ---- intro ----
    intro_text = _build_intro_text(all_items, date_str)
    intro_path = seg_dir / "seg_00_intro.mp3"
    segments.append({
        "path": intro_path, "text": intro_text,
        "meta": {"id": "intro", "title": "开场", "topic": "", "kind": "intro"},
    })

    # ---- per-topic / per-item ----
    topic_idx = 0
    seg_counter = 1
    for topic, items in all_items.items():
        if not items:
            continue
        topic_idx += 1
        # 主题开头过渡（并入第一条？还是独立章节？独立更干净）
        opener_text = _build_topic_opener_text(topic, len(items), is_first=(topic_idx == 1))
        opener_path = seg_dir / f"seg_{seg_counter:02d}_topic_{topic}.mp3"
        segments.append({
            "path": opener_path, "text": opener_text,
            "meta": {"id": f"topic_{topic}", "title": f"{topic} · 过渡",
                     "topic": topic, "kind": "topic"},
        })
        seg_counter += 1

        for i, it in enumerate(items, 1):
            it["_chapter_id"] = _chapter_id_for_item(it)  # 给 render_html 用
            item_text = _build_item_speakable(it, i, topic)
            if not item_text:
                continue
            item_path = seg_dir / f"seg_{seg_counter:02d}_{it['_chapter_id']}.mp3"
            segments.append({
                "path": item_path, "text": item_text,
                "meta": {"id": it["_chapter_id"],
                         "title": it.get("title", ""),
                         "topic": topic, "kind": "item"},
            })
            seg_counter += 1

    # ---- outro ----
    outro_text = _build_outro_text(total_items)
    outro_path = seg_dir / f"seg_{seg_counter:02d}_outro.mp3"
    segments.append({
        "path": outro_path, "text": outro_text,
        "meta": {"id": "outro", "title": "结尾", "topic": "", "kind": "outro"},
    })

    # ---- 逐个调 TTS ----
    ok_segments = []
    for si, seg in enumerate(segments, 1):
        try:
            _tts_one_segment(seg["text"], voice, rate, seg["path"])
            ok_segments.append(seg)
            if si % 5 == 0 or si == len(segments):
                print(f"    …已合成 {si}/{len(segments)} 段")
        except Exception as e:
            print(f"    ⚠️ 第 {si} 段 TTS 失败，跳过：{e}")

    if not ok_segments:
        print("  ⚠️ 没有任何片段成功合成，放弃。")
        return None

    # ---- 拼接 ----
    print(f"  🔗 字节拼接 {len(ok_segments)} 段 → digest.mp3 …")
    out_path = audio_dir / "digest.mp3"
    _concat_mp3_bytes([s["path"] for s in ok_segments], out_path)

    # ---- 读真实时长，生成 chapters ----
    print("  📏 读取各段时长、组装章节映射…")
    chapters = []
    cursor = 0.0
    for seg in ok_segments:
        dur = _get_mp3_duration(seg["path"])
        if dur <= 0:
            continue
        chapter = dict(seg["meta"])
        chapter["start"] = round(cursor, 3)
        chapter["end"]   = round(cursor + dur, 3)
        chapter["duration"] = round(dur, 3)
        chapters.append(chapter)
        cursor += dur

    total_duration = cursor

    # ---- 写 chapters.json（内联注入 HTML，也单独存一份方便调试）----
    chapters_json_path = audio_dir / "chapters.json"
    with open(chapters_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "voice": voice,
            "rate": rate,
            "total_duration": round(total_duration, 3),
            "chapters": chapters,
        }, f, ensure_ascii=False, indent=2)

    # ---- 朗读全稿也落盘（方便 debug）----
    full_script = "\n\n".join(seg["text"] for seg in ok_segments)
    (audio_dir / "digest_script.txt").write_text(full_script, encoding="utf-8")

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"  🔊 完成：{out_path.name}  · {size_mb:.2f} MB · "
          f"{_format_duration(total_duration)} · {len(chapters)} 个章节")

    return {
        "audio_path": out_path,
        "chapters": chapters,
        "total_duration": total_duration,
    }


# 兼容老调用名（防止有人还在调）
def synthesize_audio(all_items, audio_dir, voice=None):
    return synthesize_news_audio(all_items, audio_dir,
                                 datetime.now().strftime("%Y-%m-%d"), voice)


def send_email(html_body, date_str, html_path=None, audio_path=None,
               total_duration=0):
    """发送邮件。
    - 邮件正文 = HTML（直接渲染在邮件里，iOS Mail / Gmail 都能看）
    - 附件 = digest_<date>.mp3（用户在邮件里点附件 → 系统播放器播，能锁屏 / 后台）

    audio_path：MP3 文件路径，传了就作为独立附件挂上
    total_duration：总秒数，写在主题里让收件人一眼看到时长
    """
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_TO):
        print("  ⚠️ SMTP 配置不完整，跳过发邮件")
        return False

    has_audio = bool(audio_path and Path(audio_path).exists())
    audio_tag = ""
    if has_audio:
        if total_duration > 0:
            audio_tag = f" · 🎧 {_format_duration(total_duration)} 通勤听"
        else:
            audio_tag = " · 🎧 通勤听"
    subject = f"🧠 每日学习 Brief · {date_str}{audio_tag}"

    # mixed 同时支持正文 alternative + 真附件
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr(("每日学习 Brief", MAIL_FROM))
    msg["To"] = MAIL_TO

    # ---- 正文：直接放完整 HTML（邮件客户端会内联渲染） ----
    body_html = html_body or ""
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    # ---- 附件 1：MP3（用户点这个 → iOS 系统播放器） ----
    if has_audio:
        mp3_attach_name = f"digest_{date_str}.mp3"
        try:
            with open(audio_path, "rb") as f:
                audio_part = MIMEApplication(f.read(), _subtype="mpeg")
            audio_part.add_header("Content-Type", "audio/mpeg")
            audio_part.add_header(
                "Content-Disposition", "attachment",
                filename=mp3_attach_name,
            )
            msg.attach(audio_part)
            mp3_size_mb = Path(audio_path).stat().st_size / 1024 / 1024
            print(f"  📎 附 MP3：{mp3_attach_name} ({mp3_size_mb:.1f} MB)")
        except Exception as e:
            print(f"  ⚠️ MP3 附件打包失败: {e}")

    # ---- 附件 2：完整版 HTML（v2.6 路径 1 · 2026-04-27 改回）----
    # 原因：邮件正文是 lite 版（每条只有 评分+一句话），点附件能看完整版（详细/对你有啥用/术语/想深入）。
    # 解决了 iOS Mail 截断 details 的问题。
    if html_path and Path(html_path).exists():
        html_attach_name = f"digest_{date_str}.html"
        try:
            with open(html_path, "rb") as f:
                html_part = MIMEApplication(f.read(), _subtype="html")
            html_part.add_header("Content-Type", "text/html; charset=utf-8")
            html_part.add_header(
                "Content-Disposition", "attachment",
                filename=html_attach_name,
            )
            msg.attach(html_part)
            html_size_mb = Path(html_path).stat().st_size / 1024 / 1024
            print(f"  📎 附 HTML（完整版）：{html_attach_name} ({html_size_mb:.2f} MB)")
        except Exception as e:
            print(f"  ⚠️ HTML 附件打包失败: {e}")

    try:
        if SMTP_PORT == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=60) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as s:
                s.ehlo()
                s.starttls(context=ssl.create_default_context())
                s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        print(f"  ✅ 邮件已发送到 {MAIL_TO}")
        return True
    except Exception as e:
        print(f"  ⚠️ 发邮件失败: {e}")
        traceback.print_exc()
        return False


# ========== 主流程 ==========

def _normalize_keyword(kw):
    return (kw or "").lower().strip()


def _prefilter_items(items, keywords, top_n, keywords_cn=None, cn_ratio=0.4,
                      use_llm_quota=False, topic_name=""):
    """按关键词命中数给 items 排序，只保留 Top N。省 LLM 钱。

    v2 改进：
      - 用 keywords + keywords_cn 两套关键词打分
      - 按 region 分组独立保留：海外 / 国内 各自取 Top N（cn_ratio 控制比例）

    v3.1 新增（use_llm_quota=True）：
      - 让 LLM 看每个 source 抓到几条，决定每源占几个最终席位
      - 比 region 6:4 更聪明（能给 GitHub Trending 多席、给低质量源 0 席）
      - LLM 失败时自动退回老的 region 6:4 逻辑（保证不崩）
    """
    if not items:
        return []
    if not top_n or top_n <= 0 or top_n >= len(items):
        return items

    kws_intl = [_normalize_keyword(k) for k in (keywords or []) if k]
    kws_cn   = [_normalize_keyword(k) for k in (keywords_cn or []) if k]
    all_kws  = kws_intl + kws_cn

    def _score(it):
        text = " ".join([
            str(it.get("title", "")),
            str(it.get("body", "")),
            str(it.get("description", "")),
            str(it.get("summary_raw", "")),
        ]).lower()
        hits = 0
        for k in all_kws:
            if k and k in text:
                hits += 1
        return (hits, str(it.get("published", "")))

    # ===== v3.1 模式：LLM 决定每源配额 =====
    if use_llm_quota:
        try:
            quota = plan_source_quota(topic_name, items, top_n)
            if quota:
                picked = []
                # 按 source 分组，各取 Top
                for src, n in quota.items():
                    if n <= 0:
                        continue
                    src_items = [it for it in items if it.get("source") == src]
                    src_items.sort(key=_score, reverse=True)
                    picked.extend(src_items[:n])
                # 万一总数不到 top_n（某些源实际不够），用全局 Top 补齐
                if len(picked) < top_n:
                    picked_set = {id(it) for it in picked}
                    remaining = [it for it in items if id(it) not in picked_set]
                    remaining.sort(key=_score, reverse=True)
                    picked.extend(remaining[:top_n - len(picked)])
                return picked[:top_n]
        except Exception as e:
            print(f"  ⚠️ LLM Quota 异常: {e} — 退回 region 6:4 逻辑")
            # 继续往下走老逻辑

    # ===== 老逻辑（v2 默认 / 兜底）：region 6:4 =====
    intl_items = [it for it in items if it.get("region", "intl") != "cn"]
    cn_items   = [it for it in items if it.get("region", "intl") == "cn"]

    if not cn_items:
        return sorted(items, key=_score, reverse=True)[:top_n]

    cn_cap   = max(1, int(round(top_n * cn_ratio)))
    intl_cap = max(1, top_n - cn_cap)

    if len(cn_items) < cn_cap:
        overflow = cn_cap - len(cn_items)
        cn_cap   = len(cn_items)
        intl_cap = min(len(intl_items), intl_cap + overflow)
    if len(intl_items) < intl_cap:
        overflow = intl_cap - len(intl_items)
        intl_cap = len(intl_items)
        cn_cap   = min(len(cn_items), cn_cap + overflow)

    intl_top = sorted(intl_items, key=_score, reverse=True)[:intl_cap]
    cn_top   = sorted(cn_items,   key=_score, reverse=True)[:cn_cap]

    return intl_top + cn_top


def _is_summary_fresh(summary_text):
    """判断旧摘要是不是新版结构（带【中文标题】+【口播版】）。

    旧版缓存（Task #22/#24 之前生成的）没有这两段，命中后会出现：
      - 邮件里只显示英文标题（中文标题落空）
      - TTS 走老的拼接逻辑，听感不顺

    所以这里直接当未命中处理，下游会重新跑 LLM、覆盖旧摘要。
    """
    if not summary_text:
        return False
    s = str(summary_text)
    return ("【中文标题】" in s) and ("【口播版】" in s)


def _load_summary_cache(days_back=7):
    """读最近 N 天的 items.json，把 url → summary 的映射全部合并。

    旧结构的摘要（缺【中文标题】或【口播版】）会被自动跳过——它们渲染
    出来既缺中文标题、TTS 听感也差，与其复用不如重跑一次。
    """
    cache = {}
    stale_skipped = 0
    archive_root = SCRIPT_DIR.parent / "05-数据样本"
    if not archive_root.exists():
        return cache
    try:
        day_dirs = [d for d in archive_root.iterdir() if d.is_dir()]
        day_dirs.sort(reverse=True)
        day_dirs = day_dirs[:days_back]
    except Exception:
        return cache
    for day_dir in day_dirs:
        items_file = day_dir / "items.json"
        if not items_file.exists():
            continue
        try:
            with open(items_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for topic_items in (data or {}).values():
            for it in (topic_items or []):
                url = it.get("url") or it.get("link")
                summ = it.get("summary")
                if not (url and summ):
                    continue
                if not _is_summary_fresh(summ):
                    # 旧结构：忽略，让下游重跑 LLM
                    if url not in cache:
                        stale_skipped += 1
                    continue
                cache.setdefault(url, {
                    "summary": summ,
                    "score": it.get("score", 0),
                })
    if stale_skipped:
        print(f"♻️ 跳过 {stale_skipped} 条旧结构缓存（缺【中文标题】或【口播版】，将重跑 LLM 升级）")
    return cache


def main():
    parser = argparse.ArgumentParser(description="每日学习 Brief 生成器")
    parser.add_argument("--dry-run", action="store_true", help="只抓取+摘要，不发邮件")
    parser.add_argument("--no-email", action="store_true", help="同 --dry-run")
    parser.add_argument("--topic", default="", help="只跑指定主题（例如：供应链 / 生物 / 心理）")
    parser.add_argument("--min-score", type=int, default=None, help="覆盖 config 里的 min_score 过滤阈值")
    parser.add_argument("--max-per-topic", type=int, default=None,
                        help="每个主题最多给 LLM 摘要多少条（默认 6，防止跑太久）")
    parser.add_argument("--no-cache", action="store_true",
                        help="不使用本地摘要缓存（默认会复用最近 7 天的摘要）")
    parser.add_argument("--no-planner", action="store_true",
                        help="跳过 LLM Planner，按 config.yaml 顺序跑主题（出问题时的紧急退路）")
    parser.add_argument("--no-quota", action="store_true",
                        help="跳过 LLM Source Quota，prefilter 退回 region 6:4 逻辑")
    parser.add_argument("--agent-mode", action="store_true",
                        help="C-完整：LLM 多轮决策主导 main 流程（看到结果后动态决定下一步）")
    parser.add_argument("--tts", action="store_true",
                        help="额外生成 MP3 音频，每个主题一个文件，方便通勤听")
    parser.add_argument("--voice", default=None,
                        help="TTS 声音，留空则用 .env 里的 TTS_VOICE（默认晓晓 zh-CN-XiaoxiaoNeural，播客女声）。"
                             "可选：zh-CN-YunxiNeural（云希男声·阳光）/ zh-CN-XiaohanNeural（晓涵女声·知性）/ zh-CN-YunyangNeural（云扬·新闻腔）")
    parser.add_argument("--rate", default=None,
                        help='语速调节，留空则用 .env 的 TTS_RATE。例如 "-5%%" 慢一点更从容，"+10%%" 快一点。')
    parser.add_argument("--style", default=None,
                        help="TTS 风格（预留，目前 edge-tts 支持不稳，主要靠 voice+rate）。可填 chat / cheerful / gentle 等。")
    args = parser.parse_args()

    dry = args.dry_run or args.no_email
    date_str = datetime.now().strftime("%Y-%m-%d")

    topics_cfg = CONFIG.get("topics", {})
    min_score = args.min_score if args.min_score is not None else CONFIG.get("min_score", 6)
    max_per_topic_default = args.max_per_topic if args.max_per_topic is not None else CONFIG.get("max_per_topic", 6)

    # 先把缓存读进来（URL → 已有摘要），这样跑第二遍时能跳过绝大多数 LLM 调用
    cache = {} if args.no_cache else _load_summary_cache(days_back=7)
    if cache:
        print(f"💾 加载到 {len(cache)} 条历史摘要缓存")

    # ==== Agent Mode（v4 · C-完整）：LLM 多轮决策接管整个 main 流程 ====
    if args.agent_mode:
        all_items = agent_loop(topics_cfg, args, cache, max_per_topic_default, min_score)
        # Agent 模式跳过下面所有 for 循环逻辑，直接进入 TTS / render / send
        # 用一个特殊标记
        _agent_mode_used = True
    else:
        _agent_mode_used = False

    # ==== Planner：让 LLM 决定今天的主题跑序（v3 新增）====
    candidate_topics = [t for t in topics_cfg.keys() if not args.topic or args.topic == t]
    if args.no_planner or len(candidate_topics) <= 1:
        # 单主题或用户禁用就不调 Planner，按 config 顺序
        topic_order = candidate_topics
        if args.no_planner:
            print("⏭️  已跳过 Planner（--no-planner），按 config.yaml 顺序跑")
    elif _agent_mode_used:
        topic_order = []  # agent 模式已经填好 all_items，跳过 for 循环
    else:
        print("\n🧠 调用 Planner 决定今日主题优先级…")
        topic_order = plan_today_topics(candidate_topics)

    if not _agent_mode_used:
        all_items = {}
    for topic_name in topic_order:
        cfg = topics_cfg[topic_name]
        print(f"\n=== {topic_name} ===")
        raw = []

        kws = cfg.get("keywords") or []
        if not kws:
            kws = (cfg.get("keywords_en") or []) + (cfg.get("keywords_cn") or [])
        if not kws:
            print(f"  ⚠️ 主题 {topic_name} 没配关键词，跳过。")
            all_items[topic_name] = []
            continue

        sources = cfg.get("sources", {}) or {}

        # YouTube
        yt_cfg = sources.get("youtube")
        if yt_cfg:
            yt_limit = yt_cfg.get("limit", 10)
            yt_hours = yt_cfg.get("hours_back", 24)
            langs = yt_cfg.get("langs") or [{
                "lang": yt_cfg.get("lang", "en"),
                "region": yt_cfg.get("region", "US"),
            }]
            for lc in langs:
                raw += fetch_youtube(topic_name, kws,
                                     limit=yt_limit,
                                     lang=lc.get("lang", "en"),
                                     region=lc.get("region", "US"),
                                     hours_back=yt_hours)

        # Reddit
        rd_cfg = sources.get("reddit")
        if rd_cfg:
            raw += fetch_reddit(topic_name,
                                rd_cfg.get("subreddits", []),
                                limit_per_sub=rd_cfg.get("limit_per_sub", 5),
                                time_range=rd_cfg.get("time_range", "day"))

        # arXiv
        ax_cfg = sources.get("arxiv")
        if ax_cfg:
            raw += fetch_arxiv(topic_name, kws,
                               limit=ax_cfg.get("limit", 5),
                               days_back=ax_cfg.get("days_back", 7))

        # PubMed
        pm_cfg = sources.get("pubmed")
        if pm_cfg:
            raw += fetch_pubmed(topic_name, kws,
                                limit=pm_cfg.get("limit", 5),
                                days_back=pm_cfg.get("days_back", 7))

        # RSS（v2 新增：国内源）
        rss_cfg = sources.get("rss")
        if rss_cfg:
            kws_cn = cfg.get("keywords_cn") or []
            raw += fetch_rss(topic_name, rss_cfg, keywords_cn=kws_cn)

        print(f"  合计抓到 {len(raw)} 条（海外 {sum(1 for x in raw if x.get('region')!='cn')} · 国内 {sum(1 for x in raw if x.get('region')=='cn')}）")

        # ✨ 优化 1：按关键词命中数预过滤，每个主题只挑 Top N 交给 AI
        topic_cap = cfg.get("llm_top_n") or max_per_topic_default
        if topic_cap and len(raw) > topic_cap:
            before = len(raw)
            kws_cn = cfg.get("keywords_cn") or []
            raw = _prefilter_items(
                raw, kws, topic_cap,
                keywords_cn=kws_cn,
                use_llm_quota=(not args.no_quota),
                topic_name=topic_name,
            )
            intl_kept = sum(1 for x in raw if x.get("region", "intl") != "cn")
            cn_kept   = sum(1 for x in raw if x.get("region", "intl") == "cn")
            print(f"  🎯 预过滤：{before} → {len(raw)} 条（海外 {intl_kept} · 国内 {cn_kept}，双栏按 6:4 分配）")

        # ✨ 优化 2：URL 缓存先扫一遍
        to_summarize = []
        cache_hits = 0
        for it in raw:
            url = it.get("url") or it.get("link") or ""
            if url and url in cache:
                cached = cache[url]
                it["summary"] = cached["summary"]
                it["score"] = int(cached.get("score", 0) or 0)
                cache_hits += 1
            else:
                to_summarize.append(it)
        if cache_hits:
            print(f"  💾 命中缓存 {cache_hits} 条，跳过 LLM")

        # ✨ 优化 3：剩下的并发交给 LLM
        if to_summarize:
            print(f"  🚀 并发摘要 {len(to_summarize)} 条（{_llm_concurrency()} 路并行）…")
            _summarize_concurrent(to_summarize)

        scored = [it for it in raw if it.get("score", 0) >= min_score]
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        print(f"  ✨ 筛出 {len(scored)} 条（阈值 {min_score}）")
        all_items[topic_name] = scored

    archive_dir = SCRIPT_DIR.parent / "05-数据样本" / date_str
    archive_dir.mkdir(parents=True, exist_ok=True)
    with open(archive_dir / "items.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    # ✨ TTS：逐条合成 → 字节拼成单个 MP3 → 邮件以附件形式发出
    # （邮件客户端不让 <audio> 在正文里播，所以走 MIMEApplication 真附件）
    audio_path = None
    total_duration = 0
    if args.tts:
        audio_dir = archive_dir / "audio"
        voice_for_print = args.voice or TTS_VOICE or "zh-CN-XiaoxiaoNeural"
        print(f"\n🎙️ 生成播客式分章节播报…（声音：{voice_for_print}）")
        tts_result = synthesize_news_audio(
            all_items, audio_dir, date_str,
            voice=args.voice,
            rate=args.rate,
            style=args.style,
        )
        if tts_result and tts_result.get("audio_path"):
            audio_path = tts_result["audio_path"]
            chapter_count = len(tts_result.get("chapters") or [])
            total_duration = tts_result.get("total_duration") or 0
            print(f"  📐 章节数：{chapter_count} · 总时长：{_format_duration(total_duration)}")

    has_audio = bool(audio_path and Path(audio_path).exists())

    # ==== Top3 头条选择（v3 新增 · LLM 跨主题选 3 条放邮件顶部）====
    top3_headlines = []
    if not args.no_planner:  # --no-planner 一并禁用 Top3
        print("\n📰 调用 LLM 选今日 Top3 头条…")
        top3_headlines = pick_top3_headlines(all_items)
    else:
        print("⏭️  已跳过 Top3 头条（--no-planner）")

    # v2.6 路径 1：渲染两版 HTML
    #   - full：完整版（详细 / 对你有啥用 / 术语 / 想深入 全有），存档 + 作邮件附件
    #   - lite：精简版（每条只 评分+一句话），作邮件正文（解决 iOS Mail 截断 details 问题）
    html_full = render_html(
        all_items, date_str,
        total_duration=total_duration,
        has_audio=has_audio,
        top3_headlines=top3_headlines,
        lite=False,
    )
    html_lite = render_html(
        all_items, date_str,
        total_duration=total_duration,
        has_audio=has_audio,
        top3_headlines=top3_headlines,
        lite=True,
    )

    # v2.6.1：full HTML 做 CSS 内联，解决 163 / Outlook 等网页邮箱在线预览砍 <style> 的问题
    # lite 版不用做内联——它在邮件正文里发，主流邮件客户端都支持 <style>
    try:
        from premailer import transform as _premailer_transform
        html_full_inlined = _premailer_transform(
            html_full,
            keep_style_tags=True,        # 保留 <style>，万一某些客户端支持就用它
            remove_classes=False,         # 保留 class，便于排查
            cssutils_logging_level="ERROR",  # 屏蔽 cssutils 的 INFO 噪音
        )
        print(f"  ✨ CSS 内联完成（premailer · 解决网页邮箱砍 <style> 问题）")
        html_full = html_full_inlined
    except ImportError:
        print(f"  ⚠️ premailer 未安装，跳过 CSS 内联（pip install premailer）")
    except Exception as e:
        print(f"  ⚠️ CSS 内联失败（回退到原 HTML）: {type(e).__name__}: {e}")

    html_path = archive_dir / "digest.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_full)
    html_lite_path = archive_dir / "digest_lite.html"
    with open(html_lite_path, "w", encoding="utf-8") as f:
        f.write(html_lite)
    print(f"\n📁 存档: {archive_dir}")
    print(f"🌐 HTML（完整版）: {html_path}")
    print(f"🌐 HTML（精简版 · 邮件正文）: {html_lite_path}")
    html_size_mb = html_path.stat().st_size / 1024 / 1024
    html_lite_size_mb = html_lite_path.stat().st_size / 1024 / 1024
    print(f"📦 完整版: {html_size_mb:.2f} MB / 精简版: {html_lite_size_mb:.2f} MB")
    if has_audio:
        mp3_size_mb = audio_path.stat().st_size / 1024 / 1024
        print(f"🎧 MP3：{audio_path.name}（{mp3_size_mb:.2f} MB）将作为附件发出，"
              f"iOS Mail / Gmail 点附件就能用系统播放器听。")

    if dry:
        print("\n🧪 dry-run 模式，不发邮件。")
    else:
        send_email(
            html_lite, date_str,             # 正文 = 精简版
            html_path=html_path,             # 附件 = 完整版（send_email 内部读 html_path 挂上）
            audio_path=audio_path,           # MP3 也挂附件
            total_duration=total_duration,
        )

    print("\n✅ 完成。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 被用户中断。")
        sys.exit(130)
