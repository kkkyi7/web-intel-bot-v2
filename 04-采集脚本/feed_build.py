# -*- coding: utf-8 -*-
"""
feed_build.py —— 把 web-intel-bot 历史 items.json 焊进自包含「情报流.html」。
同时产出 latest.md / latest.json（微信 bot 固定拉取）和 data/index.json（历史懒加载清单）。
"""
import json
import os
import re
import sys
import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DATA_DIR = Path(os.environ.get("FEED_DATA_DIR") or (PROJECT / "05-数据样本"))
TEMPLATE = HERE / "feed_template.html"
OUT = Path(os.environ.get("FEED_OUT") or (PROJECT / "情报流.html"))
LATEST_MD = Path(os.environ.get("FEED_LATEST_MD") or (PROJECT / "latest.md"))
LATEST_JSON = Path(os.environ.get("FEED_LATEST_JSON") or (PROJECT / "latest.json"))
INDEX_JSON = Path(os.environ.get("FEED_INDEX_JSON") or (OUT.parent / "data" / "index.json"))
EMBED_DAYS = int(os.environ.get("FEED_EMBED_DAYS") or "0")  # 0 = 全量内嵌（本地默认）

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
KEEP = (
    "title", "source", "author", "published", "url", "summary", "score",
    "also_sources", "source_count", "region",
)


def date_from_path(p: Path) -> str:
    for part in reversed(p.parts):
        m = DATE_RE.search(part)
        if m:
            return m.group(1)
    return ""


def _parse_summary_sections(summary_text):
    if not summary_text:
        return {}
    sections = re.split(r"【([^】]+)】", summary_text)
    bag = {}
    for i in range(1, len(sections) - 1, 2):
        bag[sections[i].strip()] = sections[i + 1].strip()
    return bag


def _title_cn(summary_text, fallback=""):
    bag = _parse_summary_sections(summary_text)
    raw = (bag.get("中文标题") or "").splitlines()[0].strip().strip("\"'“”‘’《》「」")
    return raw or (fallback or "").strip()


def _tldr(summary_text, max_chars=100):
    bag = _parse_summary_sections(summary_text)
    for key in ("一句话讲清楚它在说啥", "一句话讲清楚", "一句话"):
        t = (bag.get(key) or "").split("\n")[0].strip()
        if t:
            return t[:max_chars].rstrip() + ("…" if len(t) > max_chars else "")
    useful = (bag.get("对你有啥用") or "").split("\n")[0].strip()
    if useful:
        return useful[:max_chars].rstrip() + ("…" if len(useful) > max_chars else "")
    return ""


def _json_escape_payload(obj) -> str:
    payload = (json.dumps(obj, ensure_ascii=False)
               .replace("<", "\\u003c")
               .replace(">", "\\u003e")
               .replace("&", "\\u0026")
               .replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))
    return payload


def load_items():
    rows, seen = [], {}
    files = sorted(DATA_DIR.rglob("items.json"))
    for f in files:
        date = date_from_path(f)
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! 跳过 {f}: {e}")
            continue
        if not isinstance(obj, dict):
            continue
        for category, items in obj.items():
            if not isinstance(items, list):
                continue
            for it in items:
                if not isinstance(it, dict):
                    continue
                row = {k: it.get(k) for k in KEEP}
                row["category"] = category
                row["date"] = date or (it.get("published", "") or "")[:10]
                if row.get("also_sources"):
                    row["source_count"] = int(row.get("source_count") or (1 + len(row["also_sources"])))
                url = row.get("url") or (row.get("title", "") + "|" + row["date"])
                prev = seen.get(url)
                if prev is None:
                    seen[url] = row
                else:
                    a = (row.get("score") or 0, row.get("date") or "")
                    b = (prev.get("score") or 0, prev.get("date") or "")
                    if a > b:
                        seen[url] = row
        try:
            rel = f.relative_to(PROJECT)
        except ValueError:
            rel = f
        print(f"  · {rel}  [{date or '无日期'}]")
    rows = list(seen.values())
    rows.sort(key=lambda r: (r.get("date") or "", r.get("score") or 0, r.get("published") or ""),
              reverse=True)
    return rows, len(files)


def load_meta_by_date():
    metas = {}
    for f in sorted(DATA_DIR.rglob("meta.json")):
        date = date_from_path(f)
        if not date:
            continue
        try:
            metas[date] = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return metas


def load_all_fetched_by_date():
    out = {}
    for f in sorted(DATA_DIR.rglob("all_fetched.json")):
        date = date_from_path(f)
        if not date:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                out[date] = data
        except Exception:
            pass
    return out


def _cutoff_date(embed_days: int) -> str:
    if embed_days <= 0:
        return ""
    d = datetime.date.today() - datetime.timedelta(days=embed_days - 1)
    return d.strftime("%Y-%m-%d")


def build_latest(rows, metas, gen_time: str):
    """产出 latest.md / latest.json，供微信 Hermes bot 拉取。"""
    dates = sorted({r.get("date") for r in rows if r.get("date")}, reverse=True)
    today = dates[0] if dates else datetime.date.today().strftime("%Y-%m-%d")
    today_rows = [r for r in rows if r.get("date") == today]
    today_rows.sort(key=lambda r: (r.get("score") or 0), reverse=True)

    meta = metas.get(today) or {}
    top3 = meta.get("top3") or []

    grouped = {}
    for r in today_rows[:10]:
        cat = r.get("category") or "其他"
        grouped.setdefault(cat, []).append({
            "title": _title_cn(r.get("summary") or "", r.get("title") or ""),
            "tldr": _tldr(r.get("summary") or ""),
            "score": r.get("score") or 0,
            "url": r.get("url") or "",
            "source": r.get("source") or "",
            "source_count": int(r.get("source_count") or 1),
        })

    latest_json = {
        "date": today,
        "generated_at": gen_time,
        "top3": top3,
        "stats": meta.get("stats") or {},
        "items": today_rows[:10],
        "by_topic": grouped,
    }

    lines = [f"# 情报 Brief · {today}", ""]
    if top3:
        lines.append("## 今日 TOP3")
        lines.append("")
        for i, t in enumerate(top3, 1):
            sc = t.get("score") or ""
            sc_txt = f" · 分{sc}" if sc else ""
            n = t.get("source_count") or 1
            n_txt = f" · {n}信源" if n > 1 else ""
            lines.append(f"{i}. **{t.get('title', '')}**{sc_txt}{n_txt}")
            if t.get("tldr"):
                lines.append(f"   {t['tldr']}")
            if t.get("url"):
                lines.append(f"   {t['url']}")
            lines.append("")

    lines.append("## 今日精选")
    lines.append("")
    for cat, items in grouped.items():
        lines.append(f"### {cat}")
        for it in items:
            sc = it.get("score") or ""
            lines.append(f"- [{it['title']}]({it['url']}) · {it.get('source', '')} · 分{sc}")
            if it.get("tldr"):
                lines.append(f"  {it['tldr']}")
        lines.append("")

    lines.append(f"_更新于 {gen_time} · web-intel-bot_")
    return "\n".join(lines), latest_json


def main():
    if not DATA_DIR.exists():
        sys.exit(f"找不到数据目录：{DATA_DIR}")
    if not TEMPLATE.exists():
        sys.exit(f"找不到模板：{TEMPLATE}")

    print(f"扫描 {DATA_DIR} ...")
    rows, n_files = load_items()
    metas = load_meta_by_date()
    all_fetched = load_all_fetched_by_date()
    cats = sorted({r["category"] for r in rows})
    dates = sorted({r["date"] for r in rows if r["date"]})
    gen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cutoff = _cutoff_date(EMBED_DAYS)

    embed_rows = [r for r in rows if not cutoff or (r.get("date") or "") >= cutoff]
    if EMBED_DAYS > 0 and len(embed_rows) < len(rows):
        print(f"  内嵌近 {EMBED_DAYS} 天：{len(embed_rows)} / {len(rows)} 条")

    # meta：优先用最新日期的
    latest_date = dates[-1] if dates else ""
    embed_meta = metas.get(latest_date) or {}
    embed_fetched = {}
    if cutoff:
        embed_fetched = {d: v for d, v in all_fetched.items() if d >= cutoff}
    elif all_fetched:
        embed_fetched = all_fetched

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__FEED_DATA__", _json_escape_payload(embed_rows))
    html = html.replace("__FEED_META__", _json_escape_payload(embed_meta))
    html = html.replace("__FEED_FETCHED__", _json_escape_payload(embed_fetched))
    html = html.replace("__FEED_DATES__", _json_escape_payload(dates))
    html = html.replace("__FEED_EMBED_DAYS__", str(EMBED_DAYS))
    html = html.replace("__GEN_TIME__", gen)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    # data/index.json：历史懒加载日期清单
    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(
        json.dumps({
            "dates": dates,
            "embed_days": EMBED_DAYS,
            "cutoff": cutoff,
            "generated_at": gen,
            "total": len(rows),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    latest_md, latest_json = build_latest(rows, metas, gen)
    LATEST_MD.write_text(latest_md, encoding="utf-8")
    LATEST_JSON.write_text(json.dumps(latest_json, ensure_ascii=False, indent=2), encoding="utf-8")

    print("-" * 50)
    print(f"✓ 共 {len(rows)} 条 / {len(dates)} 天 / {len(cats)} 个方向（扫描 {n_files} 个 items.json）")
    if cats:
        print(f"✓ 方向：{'、'.join(cats)}")
    print(f"✓ 已生成：{OUT}")
    print(f"✓ latest.md → {LATEST_MD}")
    print(f"✓ latest.json → {LATEST_JSON}")
    if EMBED_DAYS > 0:
        print(f"✓ data/index.json → {INDEX_JSON}")


if __name__ == "__main__":
    main()
