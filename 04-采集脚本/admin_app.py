#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local profile admin for web-intel-bot."""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml
from flask import Flask, Response, redirect, render_template_string, request, send_file, url_for


SCRIPT_DIR = Path(__file__).parent.resolve()
PROFILES_DIR = SCRIPT_DIR / "profiles"
ARCHIVE_ROOT = SCRIPT_DIR.parent / "05-数据样本"
DAILY_SCRIPT = SCRIPT_DIR / "daily_digest.py"
CONFIG_PATH = SCRIPT_DIR / "config.yaml"

app = Flask(__name__)


DEFAULT_PROFILE = {
    "name": "AI 产品经理 Demo",
    "role": "AI 产品经理 / 产品负责人。\n关注模型能力、Agent 落地、开源工具、竞品动态和产品增长。",
    "company_context": "面向 B 端或效率工具类 AI 产品团队。\n日常需要把行业新闻转成路线图判断、竞品观察、功能灵感和团队讨论材料。",
    "current_focus": "快速识别 AI 产品机会，判断哪些新模型、新工具、新增长案例值得跟进。",
    "interests": ["AI 模型与 Agent", "开源工具与开发者生态", "产品增长", "竞品动态", "个人效率工作流"],
    "blacklist": ["空泛融资新闻", "标题党", "纯营销软文", "没有产品启发的泛科技新闻"],
    "mail_to": "demo@example.com",
    "topic_priority": ["AI大事", "竞品动态", "产品增长", "个人效率", "变现路径"],
    "tone": "像一个资深 AI 产品同事帮我筛重点。\n少讲概念，多讲产品判断、路线图、竞品分析和增长实验。",
}


def safe_slug(raw):
    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", (raw or "").strip())
    slug = re.sub(r"-+", "-", slug).strip("-_")
    return slug or "ai_pm_demo"


def list_profiles():
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p.stem for p in PROFILES_DIR.glob("*.yaml"))


def load_profile(slug):
    path = PROFILES_DIR / f"{safe_slug(slug)}.yaml"
    if not path.exists():
        return dict(DEFAULT_PROFILE)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    merged = dict(DEFAULT_PROFILE)
    merged.update(data)
    return merged


def split_lines(text):
    return [line.strip(" -\t") for line in (text or "").splitlines() if line.strip(" -\t")]


def form_profile(form):
    return {
        "name": form.get("name", "").strip(),
        "role": form.get("role", "").strip(),
        "company_context": form.get("company_context", "").strip(),
        "current_focus": form.get("current_focus", "").strip(),
        "interests": split_lines(form.get("interests", "")),
        "blacklist": split_lines(form.get("blacklist", "")),
        "mail_to": form.get("mail_to", "").strip(),
        "topic_priority": split_lines(form.get("topic_priority", "")),
        "tone": form.get("tone", "").strip(),
    }


def save_profile(slug, profile):
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = PROFILES_DIR / f"{safe_slug(slug)}.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(profile, f, allow_unicode=True, sort_keys=False)
    return path


def load_topics():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return list((data.get("topics") or {}).keys())
    except Exception:
        return []


def latest_digest_path(slug):
    root = ARCHIVE_ROOT / safe_slug(slug)
    if not root.exists():
        return None
    candidates = sorted(root.glob("*/digest.html"), reverse=True)
    return candidates[0] if candidates else None


def run_preview(slug, max_per_topic):
    cmd = [
        sys.executable,
        str(DAILY_SCRIPT),
        "--profile",
        safe_slug(slug),
        "--dry-run",
        "--max-per-topic",
        str(max_per_topic or 5),
    ]
    started = datetime.now()
    proc = subprocess.run(
        cmd,
        cwd=str(SCRIPT_DIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
    )
    elapsed = (datetime.now() - started).total_seconds()
    return proc.returncode, elapsed, proc.stdout


TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>情报后台</title>
  <style>
    *{box-sizing:border-box}
    body{margin:0;background:#f6f7f9;color:#17181a;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
    header{height:56px;border-bottom:1px solid #dfe3e8;background:#fff;display:flex;align-items:center;padding:0 24px;gap:16px}
    header h1{font-size:17px;margin:0;font-weight:650}
    header .meta{color:#667085;font-size:13px}
    main{display:grid;grid-template-columns:260px 1fr;min-height:calc(100vh - 56px)}
    aside{border-right:1px solid #dfe3e8;background:#fff;padding:18px}
    .profile-link{display:block;padding:9px 10px;border-radius:6px;color:#2d3748;text-decoration:none;font-size:14px;margin-bottom:4px}
    .profile-link.active{background:#e9f2ff;color:#0a58ca;font-weight:600}
    .content{padding:24px;max-width:980px}
    .toolbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;gap:12px}
    .toolbar h2{font-size:22px;margin:0}
    .actions{display:flex;gap:10px;align-items:center}
    form{background:#fff;border:1px solid #dfe3e8;border-radius:8px;padding:20px}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    label{display:block;font-size:13px;font-weight:600;color:#344054;margin-bottom:6px}
    input,textarea{width:100%;border:1px solid #cfd6df;border-radius:6px;padding:9px 10px;font:inherit;font-size:14px;background:#fff}
    textarea{min-height:94px;resize:vertical;line-height:1.45}
    .wide{grid-column:1/-1}
    button,.button{border:1px solid #1b64d8;background:#1b64d8;color:#fff;border-radius:6px;padding:9px 13px;font-size:14px;text-decoration:none;cursor:pointer}
    .button.secondary,button.secondary{background:#fff;color:#1b64d8}
    .hint{font-size:12px;color:#667085;margin-top:6px}
    .status{margin:0 0 14px;padding:10px 12px;border-radius:6px;background:#eef6ff;color:#174ea6;font-size:14px}
    .output{margin-top:18px;background:#101828;color:#e5e7eb;border-radius:8px;padding:14px;white-space:pre-wrap;max-height:420px;overflow:auto;font:12px/1.45 Consolas,monospace}
    @media(max-width:820px){main{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid #dfe3e8}.grid{grid-template-columns:1fr}.content{padding:16px}}
  </style>
</head>
<body>
  <header>
    <h1>AI 产品人情报后台</h1>
    <div class="meta">本地私有配置台</div>
  </header>
  <main>
    <aside>
      <a class="profile-link {{ 'active' if slug == 'new' else '' }}" href="{{ url_for('index', profile='new') }}">新建 profile</a>
      {% for item in profiles %}
        <a class="profile-link {{ 'active' if item == slug else '' }}" href="{{ url_for('index', profile=item) }}">{{ item }}</a>
      {% endfor %}
      {% if topics %}
        <div class="hint" style="margin-top:18px">可用主题：{{ topics|join(' / ') }}</div>
      {% endif %}
    </aside>
    <section class="content">
      <div class="toolbar">
        <h2>{{ title }}</h2>
        <div class="actions">
          {% if latest_url %}
            <a class="button secondary" href="{{ latest_url }}" target="_blank">打开最近预览</a>
          {% endif %}
        </div>
      </div>
      {% if message %}<p class="status">{{ message }}</p>{% endif %}
      <form method="post">
        <div class="grid">
          <div>
            <label>Profile slug</label>
            <input name="slug" value="{{ slug if slug != 'new' else 'ai_pm_demo' }}" pattern="[A-Za-z0-9_-]+" required>
            <div class="hint">英文、数字、下划线、短横线。</div>
          </div>
          <div>
            <label>收件邮箱</label>
            <input name="mail_to" value="{{ p.mail_to }}">
          </div>
          <div>
            <label>客户名称</label>
            <input name="name" value="{{ p.name }}" required>
          </div>
          <div>
            <label>本次预览每主题条数</label>
            <input name="max_per_topic" type="number" min="1" max="12" value="{{ max_per_topic }}">
          </div>
          <div class="wide">
            <label>角色 / 工作场景</label>
            <textarea name="role">{{ p.role }}</textarea>
          </div>
          <div class="wide">
            <label>公司 / 产品上下文</label>
            <textarea name="company_context">{{ p.company_context }}</textarea>
          </div>
          <div class="wide">
            <label>近期关注</label>
            <textarea name="current_focus">{{ p.current_focus }}</textarea>
          </div>
          <div>
            <label>兴趣方向</label>
            <textarea name="interests">{{ list_text(p.interests) }}</textarea>
          </div>
          <div>
            <label>内容黑名单</label>
            <textarea name="blacklist">{{ list_text(p.blacklist) }}</textarea>
          </div>
          <div>
            <label>主题优先级</label>
            <textarea name="topic_priority">{{ list_text(p.topic_priority) }}</textarea>
            <div class="hint">一行一个主题，按高到低排序。</div>
          </div>
          <div>
            <label>输出语气</label>
            <textarea name="tone">{{ p.tone }}</textarea>
          </div>
        </div>
        <div class="actions" style="margin-top:18px">
          <button formaction="{{ url_for('save') }}">保存配置</button>
          <button class="secondary" formaction="{{ url_for('preview') }}">保存并生成预览</button>
        </div>
      </form>
      {% if output %}
        <pre class="output">{{ output }}</pre>
      {% endif %}
    </section>
  </main>
</body>
</html>
"""


def render_page(slug="ai_pm_demo", message="", output="", max_per_topic=5):
    profiles = list_profiles()
    slug = safe_slug(slug)
    profile = load_profile(slug) if slug != "new" else dict(DEFAULT_PROFILE)
    latest = latest_digest_path(slug)
    return render_template_string(
        TEMPLATE,
        profiles=profiles,
        slug=slug,
        p=profile,
        title=("新建 profile" if slug == "new" else f"profile / {slug}"),
        topics=load_topics(),
        message=message,
        output=output,
        max_per_topic=max_per_topic,
        latest_url=(url_for("latest", slug=slug) if latest else ""),
        list_text=lambda value: "\n".join(value or []) if isinstance(value, list) else (value or ""),
    )


@app.route("/")
def index():
    slug = request.args.get("profile") or (list_profiles()[0] if list_profiles() else "ai_pm_demo")
    message = "配置已保存。" if request.args.get("saved") else ""
    return render_page(slug=slug, message=message)


@app.route("/save", methods=["POST"])
def save():
    slug = safe_slug(request.form.get("slug"))
    save_profile(slug, form_profile(request.form))
    return redirect(url_for("index", profile=slug, saved=1))


@app.route("/preview", methods=["POST"])
def preview():
    slug = safe_slug(request.form.get("slug"))
    save_profile(slug, form_profile(request.form))
    max_per_topic = int(request.form.get("max_per_topic") or 5)
    try:
        code, elapsed, output = run_preview(slug, max_per_topic)
        status = f"预览完成，退出码 {code}，耗时 {elapsed:.1f}s。"
    except subprocess.TimeoutExpired as e:
        status = "预览超时。"
        output = e.stdout or ""
    except Exception as e:
        status = f"预览失败：{type(e).__name__}: {e}"
        output = ""
    return render_page(slug=slug, message=status, output=output, max_per_topic=max_per_topic)


@app.route("/latest/<slug>")
def latest(slug):
    path = latest_digest_path(slug)
    if not path:
        return Response("No digest.html found for this profile.", status=404)
    return send_file(path)


if __name__ == "__main__":
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="127.0.0.1", port=7860, debug=False)
