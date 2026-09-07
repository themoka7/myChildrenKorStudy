#!/usr/bin/env python3
"""자모 24자의 획순 그림을 한 장에 모아 PNG 로 뽑는다.

번호가 획을 덮으면 아이가 어디서 시작하는지 못 읽는다. 그런데 코드로는
못 잡는다 — 눈으로 봐야 한다.

    python3 tools/preview_jamo.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import jamo          # noqa: E402
from render import screenshot   # noqa: E402
from sheet import CSS           # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, ".build", "jamo.png")
cells = "".join(
    f'<figure>{jamo.stroke_svg(ch, size=150)}'
    f'<figcaption>{ch} · {jamo.stroke_count(ch)}획</figcaption></figure>'
    for ch in jamo.ALL)
html = f"""<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="assets/fonts.css">
<style>{CSS}
 body{{background:#fff}}
 main{{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;padding:10px}}
 figure{{margin:0;border:1px solid #ddd;border-radius:8px;text-align:center;padding:4px}}
 figcaption{{font-family:var(--round);font-size:16px;color:var(--lilac)}}
</style><main>{cells}</main>"""

path = os.path.join(ROOT, ".build", "_jamo.html")
os.makedirs(os.path.dirname(path), exist_ok=True)
open(path, "w", encoding="utf-8").write(html)
# fonts.css 를 상대경로로 찾아야 해서 저장소 뿌리에 두고 연다
root_copy = os.path.join(ROOT, "_preview_jamo.html")
open(root_copy, "w", encoding="utf-8").write(html)
try:
    screenshot(root_copy, out, width=1100)
finally:
    os.remove(root_copy)
print("획순 24자 →", out)
