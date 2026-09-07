#!/usr/bin/env python3
"""A4 를 넘긴 학습지에서 **어디가** 넘쳤는지 짚어 준다.

    python3 tools/where_overflow.py print/unit20.html

`build.py` 는 "2쪽입니다" 까지만 말해 준다. 그런데 A4 한 장에 안 들어간
학습지를 눈으로 보면 멀쩡해 보인다 — 넘친 부분이 둘째 장에 가 있어서다.

여기서는 브라우저에게 실제 배치를 물어본다. 쪽 안의 덩어리마다 바닥이
몇 mm 인지 재서, 페이지 높이(297mm)를 넘긴 첫 덩어리를 짚는다.
그게 덜어 내야 할 자리다.

덜어 내는 순서는 이렇게 잡는 것이 좋았다:
  1. 부모용 안내 문장을 줄인다 (내용이 아니라 설명이다)
  2. 색칠 도안을 줄인다 (`.artbox` 는 남는 공간을 먹는다)
  3. 쓰는 칸 크기를 줄인다 — 이건 마지막이다. 6살 손에는 칸이 커야 한다
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from render import chromium_path  # noqa: E402

PROBE = r"""() => {
  const MM = 96 / 25.4;                    // CSS px per mm
  const out = [];
  document.querySelectorAll('.page').forEach((page, pi) => {
    const top = page.getBoundingClientRect().top;
    const limit = page.getBoundingClientRect().height;
    const walk = (el, depth) => {
      for (const c of el.children) {
        const r = c.getBoundingClientRect();
        out.push({
          page: pi + 1,
          depth,
          tag: c.tagName.toLowerCase(),
          cls: c.className && String(c.className).slice(0, 40),
          text: (c.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 30),
          bottom: (r.bottom - top) / MM,
          over: r.bottom - top > limit + 1,
        });
        if (depth < 2) walk(c, depth + 1);
      }
    };
    walk(page, 0);
    out.push({page: pi + 1, limit: limit / MM, isLimit: true});
  });
  return out;
}"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        sys.exit(f"그런 파일이 없습니다: {path}")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=chromium_path(), args=["--no-sandbox"])
        page = b.new_page()
        page.goto("file://" + path)
        page.wait_for_load_state("networkidle")
        rows = page.evaluate(PROBE)
        b.close()

    limit = next((r["limit"] for r in rows if r.get("isLimit")), 297.0)
    print(f"{os.path.basename(path)} · 쪽 높이 {limit:.0f}mm\n")

    over = [r for r in rows if not r.get("isLimit") and r["over"]]
    for r in rows:
        if r.get("isLimit"):
            continue
        mark = "  ✗" if r["over"] else "   "
        pad = "  " * r["depth"]
        label = f'{r["tag"]}.{r["cls"]}' if r["cls"] else r["tag"]
        print(f'{mark} {r["bottom"]:7.1f}mm  {pad}{label:<28} {r["text"]}')

    print()
    if not over:
        print("넘친 덩어리는 없습니다. 쪽 수가 2쪽이었다면 여백(@page margin)이나 "
              ".page 높이 설정을 보세요.")
    else:
        first = over[0]
        print(f"처음 넘친 자리: {first['tag']}.{first['cls']} "
              f"(바닥 {first['bottom']:.1f}mm, {first['bottom'] - limit:.1f}mm 초과)")
        print("→ 그 위쪽 덩어리부터 덜어 내세요. 부모용 안내 → 색칠 도안 → 쓰는 칸 순서로.")


if __name__ == "__main__":
    main()
