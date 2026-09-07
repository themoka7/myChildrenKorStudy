#!/usr/bin/env python3
"""전수 검사. 커밋 전에 반드시 돌린다.

    python3 tools/check.py

**이 검사기의 핵심은 8번이다** — 「아직 안 배운 글자가 낱말에 나오는가」.

「차근차근」이라고 써 놓고 20번 학습지에 아직 안 가르친 겹받침이 나오면
그 말이 거짓이 된다. 사람은 44장을 눈으로 훑다가 반드시 놓친다.
그래서 units.json 의 자모 마당에서 '언제 무엇을 가르치는지' 를 읽어 내서
낱말·문장의 모든 글자를 자모로 풀어 대조한다.

일부러 새 글자를 넣어야 할 때가 있다 (드레스의 ㅔ, 꽃의 ㄲ). 그때는
units.json 에 `"new": ["ㅔ"]` 라고 **적어 두어야** 통과한다. 적으면
학습지에도 「새 글자」 딱지가 붙는다 — 부모가 모르고 지나가지 않게.

검사기가 아무것도 못 찾았을 때 통과시키지 않는다. 0개를 세고 "이상 없음"
을 내는 검사기가 제일 위험하다.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import art      # noqa: E402
import jamo     # noqa: E402
import sheet    # noqa: E402


# 글자를 자모로 푸는 것은 sheet 쪽에 하나만 둔다 — 두 벌이 되면 어긋난다.
decompose = sheet.split


def written(u):
    """그 학습지에서 아이가 **직접 쓰는** 글자.

    자음 페이지의 예시 낱말(거울·곰)은 읽고 색칠만 하지 쓰지 않는다.
    그래서 여기 넣지 않는다 — 넣으면 안 배운 글자라고 잘못 잡힌다.
    """
    k = u["kind"]
    if k == "word":
        return u["word"]
    if k == "sentence":
        return u["sentence"]
    if k == "table":
        return "".join(sheet.compose(c, v)
                       for c in u["chars"] for v in sheet.BASE_VOWELS)
    return ""


def main():
    os.chdir(ROOT)
    errors, warnings = [], []
    data = json.load(open("units.json", encoding="utf-8"))

    units = []
    for g in data["groups"]:
        for u in g["units"]:
            units.append((u, g))
    units.sort(key=lambda p: p[0]["n"])

    if not units:
        sys.exit("units.json 에 유닛이 하나도 없습니다.")
    if len(units) < 10:
        sys.exit(f"유닛이 {len(units)}개뿐입니다. units.json 이 깨진 것 같습니다.")

    # ── 1. 번호가 1부터 빠짐없이 ────────────────────────────
    ns = [u["n"] for u, _ in units]
    if len(set(ns)) != len(ns):
        dup = sorted({n for n in ns if ns.count(n) > 1})
        errors.append(f"유닛 번호가 겹칩니다: {dup}")
    if ns != list(range(1, len(ns) + 1)):
        errors.append(f"유닛 번호가 1..{len(ns)} 로 이어지지 않습니다: {ns}")

    # ── 2. 양식이 아는 것인지 ──────────────────────────────
    for u, _ in units:
        if u["kind"] not in sheet.BUILDERS:
            errors.append(f"유닛 {u['n']}: 모르는 양식 {u['kind']!r}")

    # ── 3. 색칠 도안 이름이 실제로 있는지 ──────────────────
    for u, _ in units:
        name = u.get("art")
        if name and name not in art.ART:
            errors.append(f"유닛 {u['n']}: 그런 도안이 없습니다 — {name!r}")
    for c in jamo.CONSONANTS.values():
        for w in c["words"]:
            if w not in art.ART:
                errors.append(f"자음 예시 낱말 도안이 없습니다: {w!r}")

    # ── 4. 자모 유닛의 글자에 획순 자료가 있는지 ───────────
    for u, _ in units:
        for ch in u.get("chars", []):
            if ch not in jamo.ALL:
                errors.append(f"유닛 {u['n']}: 획순 자료가 없는 자모 {ch!r}")

    # ── 5. 받침 마당이 이름값을 하는지 ─────────────────────
    for u, g in units:
        if u["kind"] != "word":
            continue
        has = any(decompose(c)[2] for c in u["word"] if decompose(c))
        if "받침 없는" in g["theme"] and has:
            errors.append(f"유닛 {u['n']} 「{u['word']}」 에 받침이 있는데 "
                          f"「{g['theme']}」 마당에 있습니다.")
        if "받침 있는" in g["theme"] and not has:
            errors.append(f"유닛 {u['n']} 「{u['word']}」 에 받침이 없는데 "
                          f"「{g['theme']}」 마당에 있습니다.")

    # ── 6. 학습지 파일이 다 있는지 ─────────────────────────
    made = set()
    for u, _ in units:
        p = f"print/unit{u['n']:02d}.html"
        if os.path.exists(p):
            made.add(u["n"])
        else:
            errors.append(f"학습지가 없습니다: {p} — python3 tools/build.py")

    # ── 6b. 마당 묶음이 다 있는지 ─────────────────────────
    for g in data["groups"]:
        first = min(u["n"] for u in g["units"])
        p = f"print/madang{first:02d}.html"
        if not os.path.exists(p):
            errors.append(f"마당 묶음이 없습니다: {p} — python3 tools/build.py")

    # ── 7. 지도·목록이 진짜 파일을 가리키는지 ──────────────
    # 링크를 0개 찾고 통과하지 않도록 개수를 기대값과 맞춰 본다.
    for page, pat in (("index.html", r'print/unit\$\{'), ("list.html", r'print/unit(\d+)\.html')):
        if not os.path.exists(page):
            errors.append(f"{page} 이 없습니다 — python3 tools/build.py")
            continue
        html = open(page, encoding="utf-8").read()
        if page == "list.html":
            found = [int(m) for m in re.findall(pat, html)]
            if len(found) != len(units):
                errors.append(f"{page} 의 학습지 링크가 {len(found)}개입니다 "
                              f"(유닛은 {len(units)}개).")
            for n in found:
                if n not in made:
                    errors.append(f"{page} 이 없는 학습지를 가리킵니다: unit{n:02d}")
        else:
            # 지도는 링크를 자바스크립트가 만든다. 정규식으로 훑으면 0개가
            # 나오고 "이상 없음"이 된다 — 그래서 칸 개수를 대신 센다.
            stones = len(re.findall(r'class="stone" data-n="(\d+)"', html))
            if stones != len(units):
                errors.append(f"index.html 의 칸이 {stones}개입니다 "
                              f"(유닛은 {len(units)}개).")

    # ── 8. 아직 안 배운 글자가 나오는가 ★ ──────────────────
    taught = set()          # 지금까지 가르친 자모
    declared = set()        # units.json 이 "새 글자" 로 선언한 것
    for u, g in units:
        if u["kind"] == "jamo":
            taught |= set(u["chars"])
        declared |= set(u.get("new", []))

        unknown = set()
        for ch in written(u):
            for j in decompose(ch):
                if j and j not in taught and j not in declared:
                    unknown.add(j)
        if unknown:
            errors.append(
                f"유닛 {u['n']} ({g['theme']}): 아직 안 배운 글자가 나옵니다 — "
                f"{' '.join(sorted(unknown))}\n"
                f"    → 일부러 넣는 것이라면 units.json 의 유닛 {u['n']} 에 "
                f'"new": {json.dumps(sorted(unknown), ensure_ascii=False)} 를 적으세요.')

        # 선언은 했는데 실제로는 안 쓰는 경우 — 딱지만 붙고 내용이 없다
        used = {j for ch in written(u) for j in decompose(ch) if j}
        stale = set(u.get("new", [])) - used
        if stale:
            warnings.append(f"유닛 {u['n']}: \"new\" 에 적힌 {' '.join(sorted(stale))} 가 "
                            f"이 학습지에 안 나옵니다.")

    # ── 9. 자음 예시 낱말이 그 자음으로 시작하는지 ─────────
    for ch, c in jamo.CONSONANTS.items():
        for w in c["words"]:
            first = decompose(w[0])
            if first and first[0] != ch:
                errors.append(f"{ch} 의 예시 낱말 「{w}」 가 {ch} 로 시작하지 않습니다.")

    # ── 결과 ───────────────────────────────────────────────
    for w in warnings:
        print(f"⚠️  {w}")
    if errors:
        print()
        for e in errors:
            print(f"✗ {e}")
        sys.exit(f"\n검사 실패 — {len(errors)}건")

    print(f"검사 통과 — 유닛 {len(units)}개 · 학습지 {len(made)}장 · "
          f"도안 {len(art.ART)}개 · 가르치는 자모 {len(taught)}자"
          + (f" · 새 글자 {len(declared)}자" if declared else ""))


if __name__ == "__main__":
    main()
