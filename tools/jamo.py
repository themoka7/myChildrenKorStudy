#!/usr/bin/env python3
"""자모 24자의 획순(쓰는 순서).

**이게 이 자료의 핵심이다.** 6살에게 한글을 가르칠 때 제일 먼저 굳는 것이
쓰는 순서다. 순서가 틀어진 채로 굳으면 글씨가 느려지고 나중에 고치기 어렵다.
그래서 큰 글자 옆에 ①②③ 번호와 화살표를 붙인다.

좌표계는 100×100 이다. 쓰는 쪽에서 원하는 크기로 늘린다.

획수는 학교에서 가르치는 것을 따랐다:
    ㄱ1 ㄴ1 ㄷ2 ㄹ3 ㅁ3 ㅂ4 ㅅ2 ㅇ1 ㅈ3 ㅊ4 ㅋ2 ㅌ3 ㅍ4 ㅎ3
    ㅏ2 ㅑ3 ㅓ2 ㅕ3 ㅗ2 ㅛ3 ㅜ2 ㅠ3 ㅡ1 ㅣ1

각 획은 ("d", 번호위치) 다. 번호위치가 None 이면 **획이 나아가는 반대쪽**에
자동으로 놓는다 — 시작점 위에 그대로 얹으면 획을 가려서 오히려 헷갈린다.
ㅅ·ㅈ·ㅊ 처럼 두 획이 같은 점에서 출발하는 자모만 위치를 직접 적어 두었다.
`ㅇ`·`ㅎ` 의 동그라미는 ("circle", (cx, cy, r), 번호위치) 로 따로 둔다.
"""
import re

# 모음 — 이름은 '입 모양'이다. 아이는 소리부터 배운다.
VOWELS = {
    "ㅏ": {"sound": "아", "mouth": "입을 크게 벌려요", "strokes": [
        ("M38 10 V90", None),
        ("M38 50 H76", None),
    ]},
    "ㅑ": {"sound": "야", "mouth": "이 - 아 를 빨리 붙여요", "strokes": [
        ("M38 10 V90", None),
        ("M38 34 H76", None),
        ("M38 66 H76", None),
    ]},
    "ㅓ": {"sound": "어", "mouth": "입을 반쯤 벌려요", "strokes": [
        ("M24 50 H62", None),
        ("M62 10 V90", None),
    ]},
    "ㅕ": {"sound": "여", "mouth": "이 - 어 를 빨리 붙여요", "strokes": [
        ("M24 34 H62", None),
        ("M24 66 H62", None),
        ("M62 10 V90", None),
    ]},
    "ㅗ": {"sound": "오", "mouth": "입을 동그랗게", "strokes": [
        ("M50 20 V56", None),
        ("M12 56 H88", None),
    ]},
    "ㅛ": {"sound": "요", "mouth": "이 - 오 를 빨리 붙여요", "strokes": [
        ("M34 20 V56", None),
        ("M66 20 V56", None),
        ("M12 56 H88", None),
    ]},
    "ㅜ": {"sound": "우", "mouth": "입술을 앞으로 쭉", "strokes": [
        ("M12 44 H88", None),
        ("M50 44 V80", None),
    ]},
    "ㅠ": {"sound": "유", "mouth": "이 - 우 를 빨리 붙여요", "strokes": [
        ("M12 44 H88", None),
        ("M34 44 V80", None),
        ("M66 44 V80", None),
    ]},
    "ㅡ": {"sound": "으", "mouth": "입을 옆으로 길게", "strokes": [
        ("M12 50 H88", None),
    ]},
    "ㅣ": {"sound": "이", "mouth": "입을 옆으로 활짝", "strokes": [
        ("M50 10 V90", None),
    ]},
}

# 자음 — 이름과, 그 소리로 시작하는 낱말(색칠 도안이 있는 것만).
CONSONANTS = {
    "ㄱ": {"name": "기역", "words": ["거울", "곰"], "strokes": [
        ("M20 22 H76 V82", None),
    ]},
    "ㄴ": {"name": "니은", "words": ["나비", "나무"], "strokes": [
        ("M24 18 V78 H80", None),
    ]},
    "ㄷ": {"name": "디귿", "words": ["달", "드레스"], "strokes": [
        ("M22 20 H78", None),
        ("M22 20 V80 H78", None),
    ]},
    "ㄹ": {"name": "리을", "words": ["리본"], "strokes": [
        ("M22 18 H76 V48", None),
        ("M22 48 H76", None),
        ("M22 48 V80 H76", None),
    ]},
    "ㅁ": {"name": "미음", "words": ["모자", "물고기"], "strokes": [
        ("M24 20 V80", None),
        ("M24 20 H78 V80", None),
        ("M24 80 H78", None),
    ]},
    "ㅂ": {"name": "비읍", "words": ["별", "바다"], "strokes": [
        ("M24 16 V82", None),
        ("M78 16 V82", None),
        ("M24 52 H78", None),
        ("M24 82 H78", None),
    ]},
    "ㅅ": {"name": "시옷", "words": ["사과", "사탕"], "strokes": [
        ("M50 18 L20 84", (34, 8)),
        ("M52 24 L80 84", (68, 14)),
    ]},
    "ㅇ": {"name": "이응", "words": ["오리", "왕관"], "strokes": [
        ("circle", (50, 50, 32), (15, 21)),
    ]},
    "ㅈ": {"name": "지읒", "words": ["집"], "strokes": [
        ("M20 24 H80", None),
        ("M50 24 L22 84", (34, 11)),
        ("M50 24 L78 84", (66, 11)),
    ]},
    "ㅊ": {"name": "치읓", "words": ["치마"], "strokes": [
        ("M50 8 V22", None),
        ("M20 34 H80", None),
        ("M50 34 L22 88", (32, 20)),
        ("M50 34 L78 88", (68, 20)),
    ]},
    "ㅋ": {"name": "키읔", "words": ["케이크"], "strokes": [
        ("M20 22 H76 V82", None),
        ("M22 52 H76", None),
    ]},
    "ㅌ": {"name": "티읕", "words": ["토끼"], "strokes": [
        ("M22 18 H78", None),
        ("M22 18 V80 H78", None),
        ("M22 49 H78", None),
    ]},
    "ㅍ": {"name": "피읖", "words": ["포도"], "strokes": [
        ("M18 24 H82", None),
        ("M36 24 V76", None),
        ("M64 24 V76", None),
        ("M18 76 H82", None),
    ]},
    "ㅎ": {"name": "히읗", "words": ["하트"], "strokes": [
        ("M50 6 V20", None),
        ("M22 32 H78", None),
        ("circle", (50, 66, 24), (18, 58)),
    ]},
}

ALL = {**VOWELS, **CONSONANTS}


def _head(d):
    """획의 시작점과 첫 방향을 읽는다.

    쓰는 경로는 "M x y" 뒤에 V / H / L 하나로 시작한다. 그 첫 명령이
    획이 어느 쪽으로 나아가는지를 말해 준다.
    """
    m = re.match(r"M\s*(-?[\d.]+)\s+(-?[\d.]+)\s*([VHL])\s*(-?[\d.]+)"
                 r"(?:\s+(-?[\d.]+))?", d)
    if not m:
        raise ValueError(f"획 경로를 못 읽었습니다: {d!r}")
    x, y = float(m.group(1)), float(m.group(2))
    cmd, a = m.group(3), float(m.group(4))
    if cmd == "V":
        dx, dy = 0.0, a - y
    elif cmd == "H":
        dx, dy = a - x, 0.0
    else:                                   # L x2 y2
        dx, dy = a - x, float(m.group(5)) - y
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    return (x, y), (dx / n, dy / n)


def _auto_badge(d, back=13):
    """번호를 획이 나아가는 **반대쪽**에 놓는다.

    시작점 위에 얹으면 획을 가리고, 글자 중심에서 밀어내면 세로획의 위끝처럼
    획을 따라 밀리는 자리가 생긴다. 진행 방향의 반대쪽은 그 획이 지나가지
    않는 곳이라 어느 자모에서든 안전하다.
    """
    (x, y), (dx, dy) = _head(d)
    return x - dx * back, y - dy * back


def stroke_svg(ch, size=150, show_numbers=True):
    """자모 하나의 획순 그림. 번호가 붙은 큰 글자.

    viewBox 를 글자(0~100)보다 넓게 잡아 둔다. 번호가 글자 밖으로 나가야
    획을 안 가리기 때문이다 — 좁게 잡으면 번호가 잘린다.
    """
    if ch not in ALL:
        raise KeyError(f"획순 자료가 없는 자모입니다: {ch!r}")

    parts = []
    for i, st in enumerate(ALL[ch]["strokes"], 1):
        kind = st[0]
        if kind == "circle":
            cx, cy, r = st[1]
            parts.append(f'<circle class="st" cx="{cx}" cy="{cy}" r="{r}"/>')
            at = st[2] if len(st) > 2 else (cx - r - 11, cy - r - 11)
        else:
            parts.append(f'<path class="st" d="{kind}"/>')
            at = st[1] or _auto_badge(kind)
        if show_numbers:
            x, y = at
            parts.append(
                f'<circle class="num-bg" cx="{x:.1f}" cy="{y:.1f}" r="8"/>'
                f'<text class="num" x="{x:.1f}" y="{y:.1f}">{i}</text>')

    return (f'<svg class="stroke-order" viewBox="-16 -16 132 132" width="{size}" '
            f'height="{size}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{ch} 쓰는 순서">'
            f'<g class="guide"><path d="M50 0 V100 M0 50 H100"/></g>'
            + "".join(parts) + "</svg>")


def stroke_count(ch):
    return len(ALL[ch]["strokes"])


def describe(ch):
    """부모용 한 줄. '몇 획으로, 어디서 시작해서' 를 말로 적어 준다."""
    n = stroke_count(ch)
    if ch in VOWELS:
        return f"{n}획 · 소리는 「{VOWELS[ch]['sound']}」 · {VOWELS[ch]['mouth']}"
    return f"{n}획 · 이름은 「{CONSONANTS[ch]['name']}」"


if __name__ == "__main__":
    for ch in ALL:
        print(ch, describe(ch))
