#!/usr/bin/env python3
"""색칠 도안을 한 장에 모아서 PNG 로 뽑는다.

그림은 **눈으로 봐야만** 검증된다. 코드가 통과해도 그림이 안 읽히면 소용없다.
(실제로 '우유'가 집처럼, '공주' 왕관이 뿔처럼 보였다)

사용법:
    python3 tools/preview_art.py                # 전부
    python3 tools/preview_art.py 유니콘 구두 모자  # 몇 개만
    python3 tools/preview_art.py -o /tmp/a.png
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import art  # noqa: E402
from render import screenshot  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="비우면 전부")
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, ".build", "art.png"))
    ap.add_argument("--cols", type=int, default=6)
    a = ap.parse_args()

    names = a.names or art.names()
    for n in names:
        if n not in art.ART:
            sys.exit(f"그런 도안이 없습니다: {n!r}\n있는 것: {', '.join(art.names())}")

    cells = "".join(f"<figure>{art.svg(n)}<figcaption>{n}</figcaption></figure>"
                    for n in names)
    html = f"""<!doctype html><meta charset="utf-8"><title>도안</title>
<style>
 body{{margin:0;background:#fff;font-family:system-ui,sans-serif}}
 main{{display:grid;grid-template-columns:repeat({a.cols},1fr);gap:4px;padding:8px}}
 figure{{margin:0;border:1px solid #ccc}}
 svg{{width:100%;height:auto;display:block}}
 figcaption{{font-size:12px;padding:3px;background:#eee;text-align:center}}
</style><main>{cells}</main>"""

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    screenshot(html, a.out, width=200 * a.cols)
    print(f"도안 {len(names)}개 → {a.out}")


if __name__ == "__main__":
    main()
