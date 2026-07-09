#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""高分警报：当天 TOP 条目 ≥ ALERT_MIN_SCORE 时，通过 Server酱推微信。

用法：
  python push_alert.py [--meta path/to/meta.json]

环境变量：
  SERVERCHAN_SENDKEY  必填才真正推送；未配置则静默跳过
  ALERT_MIN_SCORE     默认 9
  ALERT_FEED_URL      推送里附带的页面链接，默认 GitHub Pages
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

DEFAULT_FEED_URL = "https://kkkyi7.github.io/web-intel-bot-v2/index.html"
DEFAULT_MIN_SCORE = 9


def find_latest_meta(root: Path) -> Path | None:
    candidates = sorted(root.rglob("meta.json"), reverse=True)
    return candidates[0] if candidates else None


def load_meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_alerts(meta: dict, min_score: int) -> list[dict]:
    top3 = meta.get("top3") or []
    alerts = [t for t in top3 if int(t.get("score") or 0) >= min_score]
    alerts.sort(key=lambda t: int(t.get("score") or 0), reverse=True)
    return alerts


def build_message(alerts: list[dict], meta: dict, feed_url: str) -> tuple[str, str]:
    date = meta.get("date") or ""
    best = alerts[0]
    title = f"情报警报 · {best.get('title', '')[:40]}"
    lines = [
        f"**{date}** 出现 {len(alerts)} 条高分情报（≥{os.environ.get('ALERT_MIN_SCORE', DEFAULT_MIN_SCORE)}）",
        "",
    ]
    for i, a in enumerate(alerts, 1):
        sc = a.get("score") or ""
        src = a.get("source") or ""
        topic = a.get("topic") or ""
        lines.append(f"{i}. **{a.get('title', '')}** · 分{sc}")
        if a.get("tldr"):
            lines.append(f"   {a['tldr']}")
        meta_bits = " · ".join(x for x in [topic, src] if x)
        if meta_bits:
            lines.append(f"   _{meta_bits}_")
        if a.get("url"):
            lines.append(f"   {a['url']}")
        lines.append("")
    lines.append(f"[打开情报流]({feed_url})")
    return title, "\n".join(lines)


def push_serverchan(sendkey: str, title: str, desp: str) -> None:
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    r = requests.post(url, data={"title": title, "desp": desp}, timeout=20)
    r.raise_for_status()
    data = r.json() if r.content else {}
    if isinstance(data, dict) and data.get("code") not in (0, None, "0"):
        raise RuntimeError(f"Server酱返回异常: {data}")
    print(f"  ✅ Server酱已推送：{title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="高分情报 Server酱 推送")
    parser.add_argument("--meta", default="", help="meta.json 路径；默认在 05-数据样本 下找最新")
    parser.add_argument("--min-score", type=int, default=None)
    args = parser.parse_args()

    min_score = args.min_score if args.min_score is not None else int(
        os.environ.get("ALERT_MIN_SCORE", DEFAULT_MIN_SCORE)
    )
    sendkey = (os.environ.get("SERVERCHAN_SENDKEY") or "").strip()
    feed_url = (os.environ.get("ALERT_FEED_URL") or DEFAULT_FEED_URL).strip()

    script_dir = Path(__file__).resolve().parent
    archive_root = script_dir.parent / "05-数据样本"

    if args.meta:
        meta_path = Path(args.meta)
    else:
        meta_path = find_latest_meta(archive_root)

    if not meta_path or not meta_path.exists():
        print("⏭️  找不到 meta.json，跳过警报")
        return 0

    meta = load_meta(meta_path)
    alerts = pick_alerts(meta, min_score)
    if not alerts:
        print(f"⏭️  今日无 ≥{min_score} 分条目，跳过警报（{meta_path}）")
        return 0

    title, desp = build_message(alerts, meta, feed_url)
    print(f"📢 命中 {len(alerts)} 条高分 · {title}")

    if not sendkey:
        print("⏭️  未配置 SERVERCHAN_SENDKEY，跳过推送（本地预览上方标题即可）")
        print("---")
        print(desp)
        return 0

    try:
        push_serverchan(sendkey, title, desp)
    except Exception as e:
        print(f"❌ 推送失败: {type(e).__name__}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
