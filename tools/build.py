#!/usr/bin/env python3
"""units.json → 학습지·지도·목록을 전부 다시 만든다.

    python3 tools/build.py            # 전부
    python3 tools/build.py 20 21      # 유닛 몇 개만 (지도·목록도 같이)
    python3 tools/build.py --no-verify  # 레이아웃 검증 건너뛰기 (빠름)

**레이아웃 검증이 이 스크립트의 존재 이유다.**

A4 학습지는 넘쳐도 화면에서는 안 보인다. 브라우저에서 열어 보면 멀쩡한데
인쇄하면 두 장째에 칸 하나가 덜렁 넘어가 있다. 그래서 만들 때마다 Chromium
으로 실제 인쇄 PDF 를 뽑아 **쪽 수를 센다.** 한 장이 아니면 빌드를 실패시킨다.

느리다(장당 1초쯤). 그래도 끈다는 선택지는 두지 않았다 — 검증을 끄면
언젠가 두 장짜리가 인쇄되고, 그때는 이미 아이가 앞에 앉아 있다.
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import sheet  # noqa: E402


def load():
    with open(os.path.join(ROOT, "units.json"), encoding="utf-8") as f:
        return json.load(f)


def all_units(data):
    """(유닛, 그룹) 을 번호 순으로."""
    out = []
    for g in data["groups"]:
        for u in g["units"]:
            out.append((u, g))
    out.sort(key=lambda p: p[0]["n"])
    return out


def build_sheets(data, only=None, verify=True):
    pairs = all_units(data)
    total = len(pairs)
    outdir = os.path.join(ROOT, "print")
    os.makedirs(outdir, exist_ok=True)

    made, failures = [], []
    for u, g in pairs:
        if only and u["n"] not in only:
            continue
        path = os.path.join(outdir, f"unit{u['n']:02d}.html")
        try:
            html = sheet.build(u, g, total)
        except Exception as e:
            failures.append(f"유닛 {u['n']:02d} 만들기 실패: {e}")
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        made.append((u, path))

    if failures:
        sys.exit("\n".join(failures))

    # 마당 통째로 인쇄용. 한 장씩 44번 인쇄 버튼을 누르는 부모는 없다.
    if not only:
        for g in data["groups"]:
            us = sorted(g["units"], key=lambda u: u["n"])
            path = os.path.join(outdir, f"madang{us[0]['n']:02d}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(sheet.build_bundle(us, g, total))
        print(f"마당 묶음 {len(data['groups'])}개 → print/madangNN.html")

    if verify and made:
        failures = verify_pages(made)
        if not only:
            # 묶음도 재 본다. 낱장이 1쪽씩이어도 묶으면 어긋날 수 있다 —
            # 쪽 사이에 여백이 한 번만 끼어도 마지막 장이 밀려난다.
            from render import pdf_pages
            for g in data["groups"]:
                us = sorted(g["units"], key=lambda u: u["n"])
                p = os.path.join(outdir, f"madang{us[0]['n']:02d}.html")
                n = pdf_pages(p)
                print(f"  {'✓' if n == len(us) else '✗'} {os.path.basename(p)}  "
                      f"{n}쪽 / {len(us)}장")
                if n != len(us):
                    failures.append(f"마당 묶음 {os.path.basename(p)} 가 {n}쪽입니다 "
                                    f"({len(us)}장이어야 합니다).")
        if failures:
            sys.exit("\n".join(failures)
                     + "\n\nA4 한 장을 넘겼습니다. 내용을 덜어 내세요."
                       "\n어디가 넘쳤는지 보려면: python3 tools/where_overflow.py print/unitNN.html")

    return [p for _, p in made]


def verify_pages(made):
    """만든 학습지가 정말 A4 한 장인지 Chromium 으로 인쇄해 본다."""
    from render import pdf_pages
    bad = []
    t0 = time.time()
    for i, (u, path) in enumerate(made, 1):
        n = pdf_pages(path)
        mark = "✓" if n == 1 else "✗"
        print(f"  {mark} unit{u['n']:02d}  {n}쪽", flush=True)
        if n != 1:
            bad.append(f"유닛 {u['n']:02d} ({os.path.basename(path)}) 가 {n}쪽입니다 — A4 한 장이어야 합니다.")
    print(f"  레이아웃 검증 {len(made)}장 · {time.time() - t0:.0f}초")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("units", nargs="*", type=int, help="비우면 전부")
    ap.add_argument("--no-verify", action="store_true",
                    help="레이아웃 검증 건너뛰기 (초안 만들 때만)")
    a = ap.parse_args()

    data = load()
    only = set(a.units) or None

    print("학습지를 만듭니다…")
    paths = build_sheets(data, only, verify=not a.no_verify)
    print(f"학습지 {len(paths)}장 → print/")

    # 지도와 목록은 유닛 몇 개만 만들었을 때도 항상 다시 만든다.
    # 진도가 어긋난 지도가 남으면 아이가 헷갈린다.
    import build_map
    import build_index
    build_map.build(data)
    build_index.build(data)

    if a.no_verify:
        print("\n⚠️  레이아웃 검증을 건너뛰었습니다. 커밋 전에 --no-verify 없이 한 번 돌리세요.")


if __name__ == "__main__":
    main()
