# -*- coding: utf-8 -*-
"""
feed_build.py —— 把 web-intel-bot 历史 items.json 全部焊进一个自包含的「情报流.html」。
双击该 html 即可在浏览器里翻、筛、搜，零服务器、零部署、离线可用。
bot 每天跑完后顺手 `python feed_build.py` 重生成一次即可。
"""
import json, re, sys, os, datetime
from pathlib import Path

HERE      = Path(__file__).resolve().parent
PROJECT   = HERE.parent
# 可被环境变量覆盖（CI 用）；本地直接跑时用默认值。
DATA_DIR  = Path(os.environ.get("FEED_DATA_DIR") or (PROJECT / "05-数据样本"))
TEMPLATE  = HERE / "feed_template.html"
OUT       = Path(os.environ.get("FEED_OUT") or (PROJECT / "情报流.html"))

DATE_RE   = re.compile(r"(\d{4}-\d{2}-\d{2})")
KEEP      = ("title", "source", "author", "published", "url", "summary", "score")

def date_from_path(p: Path) -> str:
    for part in reversed(p.parts):
        m = DATE_RE.search(part)
        if m:
            return m.group(1)
    return ""

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
                url = row.get("url") or (row.get("title", "") + "|" + row["date"])
                # 去重：同 url 保留分数更高 / 日期更新的那条
                prev = seen.get(url)
                if prev is None:
                    seen[url] = row
                else:
                    a = (row.get("score") or 0, row.get("date") or "")
                    b = (prev.get("score") or 0, prev.get("date") or "")
                    if a > b:
                        seen[url] = row
        print(f"  · {f.relative_to(PROJECT)}  [{date or '无日期'}]")
    rows = list(seen.values())
    rows.sort(key=lambda r: (r.get("score") or 0, r.get("published") or r.get("date") or ""),
              reverse=True)
    return rows, len(files)

def main():
    if not DATA_DIR.exists():
        sys.exit(f"找不到数据目录：{DATA_DIR}")
    if not TEMPLATE.exists():
        sys.exit(f"找不到模板：{TEMPLATE}")
    print(f"扫描 {DATA_DIR} ...")
    rows, n_files = load_items()
    cats  = sorted({r["category"] for r in rows})
    dates = sorted({r["date"] for r in rows if r["date"]})
    gen   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__FEED_DATA__", json.dumps(rows, ensure_ascii=False))
    html = html.replace("__GEN_TIME__", gen)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")

    print("-" * 50)
    print(f"✓ 共 {len(rows)} 条 / {len(dates)} 天 / {len(cats)} 个方向（扫描 {n_files} 个 items.json）")
    print(f"✓ 方向：{ '、'.join(cats) }")
    print(f"✓ 已生成：{OUT}")

if __name__ == "__main__":
    main()
