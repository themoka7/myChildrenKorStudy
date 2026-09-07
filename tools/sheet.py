#!/usr/bin/env python3
"""A4 학습지 한 장을 만든다. 네 가지 양식이 있다.

    jamo      자모 한 자씩 — 획순 번호 + 따라쓰기 + 예시 그림   (1·2마당)
    table     자음 × 모음 조합표 — 가갸거겨…                     (3마당)
    word      낱말 — 색칠 도안 + 따라쓰기 (원본 PDF 양식)         (4·5마당)
    sentence  문장 — 원고지 칸에 따라쓰기                         (6마당)

**설계에서 양보하지 않은 것**

1. **한 유닛은 A4 딱 한 장이다.** 두 장이 되면 빌드가 실패한다.
   6살에게 두 장은 길다. 그리고 부모가 인쇄할 때 종이가 아깝다.

2. **바탕을 칠하지 않는다.** 전면 배경색은 잉크를 먹고, 크레파스가 안 먹는다.
   색은 머리말 탭·선·강조에만 쓴다.

3. **쓰는 칸에는 십자 보조선을 넣는다.** 한글은 네모 안에 균형을 맞춰 쓰는
   글자라서, 가운데를 알려 주지 않으면 글자가 한쪽으로 쏠린다.

4. **부모용 한 줄을 페이지 맨 아래에 둔다.** 정답지를 따로 뽑게 하면
   아무도 안 뽑는다. 아이가 틀렸을 때 뭐라고 말해 줄지를 적어 둔다.
"""
import html as _html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import art
import jamo

# ──────────────────────────────────────────────────────────────
#  팔레트 — 세 화면(학습지·지도·목록)이 한 덩어리로 보이게
# ──────────────────────────────────────────────────────────────
CSS = """
:root{
  --ink:#3B2B40;      /* 글자·테두리 — 진한 보라회색 */
  --rose:#E0508A;     /* 강조·머리말 탭 */
  --gold:#E8A33D;     /* 굵은 밑줄 */
  --lilac:#A98BD0;    /* 보조 */
  --line:#CFC2D8;     /* 연한 선 */
  --trace:#D6D2DA;    /* 따라쓰기 회색 글자 */
  --guide:#E6E0EC;    /* 칸 안 십자 보조선 */
  --serif:'Noto Sans KR',system-ui,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;
  --round:'Jua','Noto Sans KR',system-ui,sans-serif;
  --hand:'Gaegu','Noto Sans KR',system-ui,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:var(--serif);color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}

@page{size:A4;margin:0}
.page{
  width:210mm;height:297mm;padding:11mm 13mm 8mm;
  display:flex;flex-direction:column;background:#fff;position:relative;
}

/* ── 머리말 ─────────────────────────────────────── */
.head{display:flex;align-items:flex-end;gap:7mm;flex:none}
.tab{
  font-family:var(--round);font-size:9.2mm;line-height:1;color:#fff;
  background:var(--rose);padding:3.4mm 6mm 4.2mm;
  border-radius:0 0 9mm 9mm;margin-top:-11mm;letter-spacing:-.3mm;
}
.head .say{font-family:var(--round);font-size:6.4mm;padding-bottom:1.4mm;letter-spacing:-.2mm}
.newpill{
  margin-left:auto;font-family:var(--round);font-size:4mm;color:#fff;
  background:var(--lilac);border-radius:999px;padding:1.6mm 4mm;margin-bottom:1.6mm;
}
.newpill + .no{margin-left:3mm}
.head .no{margin-left:auto;font-family:var(--round);font-size:4.6mm;color:var(--lilac);padding-bottom:2mm}
.rule{height:2.6mm;background:var(--gold);border-radius:1.3mm;margin:2.5mm 0 0;flex:none}
.rule.thin{height:1.2mm;background:var(--line)}

/* ── 본문 틀 ─────────────────────────────────────── */
main{flex:1 1 auto;display:flex;flex-direction:column;gap:4mm;padding-top:4mm;min-height:0}
.band{display:flex;align-items:center;gap:4mm;flex:none}
.band h2{
  font-family:var(--round);font-size:4.8mm;margin:0;color:var(--rose);
  background:#FCEFF5;border-radius:3mm;padding:1.4mm 3.4mm;white-space:nowrap;
}
.band .hint{font-family:var(--hand);font-size:4.6mm;color:var(--lilac)}

/* ── 쓰는 칸 ─────────────────────────────────────── */
.boxes{display:flex;gap:2.6mm;flex:none}
.box{
  border:0.9mm solid var(--ink);border-radius:2.4mm;background:#fff;
  display:grid;place-items:center;position:relative;overflow:hidden;flex:none;
}
/* 십자 보조선 — 글자를 칸 가운데에 앉히는 기준이다 */
.box::before,.box::after{
  content:"";position:absolute;background:var(--guide);
}
.box::before{left:8%;right:8%;height:0.4mm;top:50%}
.box::after{top:8%;bottom:8%;width:0.4mm;left:50%}
.box>span{position:relative;font-weight:500;line-height:1;z-index:1}
.box.gray>span{color:var(--trace)}
.box.blank>span{visibility:hidden}
.box.space::before,.box.space::after{display:none}
.box.space{border-style:dashed;border-color:var(--line)}

/* ── 색칠 도안 ───────────────────────────────────── */
.art{display:block;width:100%;height:100%}
.artbox{flex:1 1 auto;display:grid;place-items:center;min-height:0}
.artbox svg{max-height:100%;width:auto;max-width:100%}

/* ── 획순 ────────────────────────────────────────── */
.jamo-row{display:flex;gap:5mm;align-items:center;flex:none}
.stroke-order{flex:none}
.stroke-order .guide path{stroke:var(--guide);stroke-width:1.1;stroke-dasharray:3 3;fill:none}
.stroke-order .st{stroke:var(--ink);stroke-width:9;fill:none;stroke-linecap:round;stroke-linejoin:round}
.stroke-order .num-bg{fill:var(--rose)}
.stroke-order .num{fill:#fff;font-family:var(--round);font-size:11px;text-anchor:middle;dominant-baseline:central}
.jamo-meta{font-family:var(--round);font-size:4.4mm;color:var(--lilac);text-align:center;margin-top:1mm}

/* ── 예시 낱말 ───────────────────────────────────── */
/* 카드에 너비를 못 박아 둔다. height:100% 로 두면 부모 높이가 auto 라
   그림이 0 으로 찌그러진다 — 실제로 그렇게 인쇄될 뻔했다. */
.words{display:flex;gap:6mm;justify-content:center;align-items:center;
       flex:1 1 auto;min-height:0;flex-wrap:wrap}
.word-card{display:flex;flex-direction:column;align-items:center;gap:1mm;width:40mm;flex:none}
.word-card svg{width:100%;height:auto}
.word-card b{font-family:var(--round);font-weight:400;font-size:7mm}

/* ── 조합표 ──────────────────────────────────────── */
.grid10{display:grid;grid-template-columns:repeat(10,1fr);gap:1.6mm;flex:none}
.grid10 .box{width:auto;aspect-ratio:1/1;border-width:0.7mm;border-radius:1.8mm}
.grid10 .box>span{font-size:8.4mm}
.lead{font-family:var(--round);font-size:5.6mm;color:var(--rose);width:9mm;flex:none;align-self:center}
.tablerow{display:flex;gap:2.5mm;align-items:center;flex:none}
.tablerow .grid10{flex:1 1 auto}

/* ── 부모용 ──────────────────────────────────────── */
.parent{
  flex:none;margin-top:auto;border:0.7mm dashed var(--lilac);border-radius:3mm;
  padding:2.6mm 4mm;font-size:3.5mm;line-height:1.5;color:#5C4A63;background:#FBF8FD;
}
.parent b{color:var(--rose);font-family:var(--round);font-weight:400;margin-right:2mm}
.foot{flex:none;display:flex;justify-content:space-between;align-items:center;
      margin-top:2mm;font-size:3.1mm;color:var(--lilac)}
.stars{letter-spacing:1mm;font-size:4.6mm;color:var(--gold)}
"""


def esc(s):
    return _html.escape(str(s), quote=False)


def box(ch, mm, cls=""):
    """쓰는 칸 하나. ch 가 None 이면 빈 칸."""
    size = f"width:{mm}mm;height:{mm}mm"
    font = f"font-size:{mm * 0.68:.1f}mm"
    inner = esc(ch) if ch else "　"
    return (f'<div class="box {cls}" style="{size}">'
            f'<span style="{font}">{inner}</span></div>')


def row(chars, mm, cls=""):
    return ('<div class="boxes">'
            + "".join(box(c, mm, cls) for c in chars) + "</div>")


NEW_NAMES = {
    "ㅔ": "에", "ㅖ": "예", "ㅐ": "애", "ㅒ": "얘", "ㅘ": "와", "ㅚ": "외",
    "ㅝ": "워", "ㅟ": "위", "ㅢ": "의",
    "ㄲ": "쌍기역", "ㄸ": "쌍디귿", "ㅃ": "쌍비읍", "ㅆ": "쌍시옷", "ㅉ": "쌍지읒",
    "ㄺ": "겹받침 ㄹㄱ", "ㄼ": "겹받침 ㄹㅂ", "ㄶ": "겹받침 ㄴㅎ", "ㄵ": "겹받침 ㄴㅈ",
}


def new_badge(u):
    """이 학습지에서 처음 나오는 글자를 눈에 띄게 알린다.

    안 배운 글자를 슬쩍 끼워 넣으면 아이는 '나는 못 읽는구나' 로 받아들인다.
    **처음 나오는 것이라고 말해 주면** 못 읽는 게 당연한 일이 된다.
    """
    chars = u.get("new") or []
    if not chars:
        return "", ""
    tags = " ".join(f"{c}({NEW_NAMES[c]})" if c in NEW_NAMES else c for c in chars)
    pill = f'<div class="newpill">새 글자 {esc(tags)}</div>'
    note = (f' <b style="margin-left:0">오늘 처음 나오는 글자</b>{esc(tags)} 가 오늘 처음입니다 — '
            "아이가 못 읽어도 당연합니다. <b>부모가 먼저 읽어 주고</b> 따라 하게 하세요.")
    return pill, note


def page(title, tab, say, no, body, parent, note_label="부모님께", pill=""):
    """A4 한 장. **문서가 아니라 쪽 하나**를 돌려준다.

    쪽과 문서를 나눠 두는 이유는 하나다 — 마당을 통째로 인쇄할 수 있어야
    한다. 한 장씩 44번 인쇄 버튼을 누르는 부모는 없다.
    """
    return f"""<div class="page">
  <header class="head">
    <div class="tab">{esc(tab)}</div>
    <div class="say">{esc(say)}</div>
    {pill}
    <div class="no">{esc(no)}</div>
  </header>
  <div class="rule"></div>
  <main>{body}</main>
  <div class="parent"><b>{esc(note_label)}</b>{parent}</div>
  <div class="foot">
    <span>{esc(title)}</span>
    <span class="stars">☆ ☆ ☆</span>
  </div>
</div>"""


def document(title, pages, css_href="../assets/fonts.css"):
    """쪽 하나 또는 여럿을 인쇄용 문서로 감싼다."""
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{css_href}">
<style>{CSS}</style>
</head><body>
{''.join(pages)}
</body></html>"""


# ──────────────────────────────────────────────────────────────
#  ① 자모 — 획순 + 따라쓰기 + 예시 그림
# ──────────────────────────────────────────────────────────────

def sheet_jamo(u, group, total):
    chars = u["chars"]
    is_vowel = chars[0] in jamo.VOWELS
    blocks = []

    for ch in chars:
        info = jamo.ALL[ch]
        meta = (f"소리 「{info['sound']}」" if is_vowel
                else f"이름 「{info['name']}」")
        # 회색 3칸 → 빈칸 3칸을 한 줄로. 왼쪽에서 오른쪽으로 가면서
        # 도움이 줄어드는 것이 아이 눈에 그대로 보인다.
        cells = ('<div class="boxes">'
                 + "".join(box(ch, 20, "gray") for _ in range(3))
                 + "".join(box(ch, 20, "blank") for _ in range(3))
                 + "</div>")
        blocks.append(f"""
        <div class="jamo-row">
          <div style="flex:none">
            {jamo.stroke_svg(ch, size=132)}
            <div class="jamo-meta">{esc(meta)} · {jamo.stroke_count(ch)}획</div>
          </div>
          {cells}
        </div>""")

    if is_vowel:
        sounds = " ".join(jamo.VOWELS[c]["sound"] for c in chars)
        mouths = " · ".join(f"{c} 는 {jamo.VOWELS[c]['mouth']}" for c in chars)
        tail = f"""
        <div class="band"><h2>색칠해요</h2>
          <span class="hint">{esc(sounds)} 하고 말하면서 칠해 보세요</span></div>
        <div class="artbox">{art.svg(u["art"])}</div>"""
        parent = (f"{esc(mouths)}. "
                  "모음은 <b>소리를 먼저</b> 익히게 하세요 — 모양보다 소리가 먼저입니다. "
                  "칸 안의 십자선은 글자를 가운데에 앉히는 기준선입니다.")
    else:
        cards = "".join(
            f'<div class="word-card">{art.svg(w)}<b>{esc(w)}</b></div>'
            for c in chars for w in jamo.CONSONANTS[c]["words"])
        first = "".join(f"{c}({jamo.CONSONANTS[c]['name']})" for c in chars)
        tail = f"""
        <div class="band"><h2>이 소리로 시작해요</h2>
          <span class="hint">낱말을 소리 내어 읽고 색칠해 보세요</span></div>
        <div class="words">{cards}</div>"""
        parent = (
            f"오늘 배운 자음은 {esc(first)} 입니다. "
            "아이가 획순을 어기면 <b>지우지 말고</b> 번호를 짚으며 한 번 더 보여 주세요 — "
            "지우면 쓰기 자체를 싫어하게 됩니다. "
            "그림의 낱말을 읽어 주고 <b>첫소리만</b> 따라 말하게 하면 소리와 글자가 붙습니다.")

    body = "".join(blocks) + tail
    return page(
        title=f"{u['n']:02d}. {' '.join(chars)}",
        tab="한글쓰기", say="쓰는 순서대로 따라 써요.",
        no=f"{group['theme']} · {u['n']}/{total}",
        body=body, parent=parent)


# ──────────────────────────────────────────────────────────────
#  ② 조합표 — 자음 × 모음
# ──────────────────────────────────────────────────────────────

BASE_VOWELS = ["ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅡ", "ㅣ"]

# 한글 음절 조합: 0xAC00 + (초성*21 + 중성)*28 + 종성
_CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
_JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"


# 0번은 '받침 없음'. 문자열의 맨 앞 공백으로 두면 읽는 사람도 편집기도
# 헷갈린다 — 실제로 이 자리가 널바이트로 저장돼서 빌드가 죽은 적이 있다.
_JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ",
         "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ",
         "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]


def compose(cho, jung, jong=""):
    """자모를 합쳐 한 글자로. ㄱ + ㅏ → 가"""
    return chr(0xAC00 + (_CHO.index(cho) * 21 + _JUNG.index(jung)) * 28
               + _JONG.index(jong))


def split(ch):
    """한 글자를 (초성, 중성, 종성) 으로. 받침이 없으면 ''. 한글이 아니면 ()."""
    if not ("가" <= ch <= "힣"):
        return ()
    i = ord(ch) - 0xAC00
    return _CHO[i // 588], _JUNG[(i % 588) // 28], _JONG[i % 28]


def sheet_table(u, group, total):
    rows = []
    for ch in u["chars"]:
        syl = [compose(ch, v) for v in BASE_VOWELS]
        gray = "".join(f'<div class="box gray"><span>{s}</span></div>' for s in syl)
        blank = "".join('<div class="box blank"><span>가</span></div>'
                        for _ in syl)
        rows.append(f"""
        <div class="tablerow"><div class="lead">{esc(ch)}</div>
          <div class="grid10">{gray}</div></div>
        <div class="tablerow"><div class="lead"></div>
          <div class="grid10">{blank}</div></div>""")

    a, b = u["chars"]
    body = f"""
    <div class="band"><h2>글자를 만들어요</h2>
      <span class="hint">{esc(a)} 와 ㅏ 가 만나면 「{compose(a, 'ㅏ')}」</span></div>
    {''.join(rows)}
    <div class="band"><h2>색칠해요</h2>
      <span class="hint">읽을 수 있는 글자에 동그라미를 치고 색칠하세요</span></div>
    <div class="artbox">{art.svg(u["art"])}</div>"""

    parent = (
        f"오늘은 {esc(a)}·{esc(b)} 에 모음 열 개를 붙였습니다. "
        f"「{compose(a, 'ㅏ')}」 를 짚고 <b>“{esc(a)} 에 ㅏ 를 붙이면?”</b> 하고 물어보세요. "
        "전부 못 읽어도 됩니다 — <b>읽은 글자에 동그라미</b>만 쳐 두고 다음에 또 하면 늘어납니다. "
        "이 마당이 한글의 고비라서, 못 읽는 칸이 많아도 다음 마당으로 넘기지 마세요.")

    return page(
        title=f"{u['n']:02d}. {a}·{b} 글자 만들기",
        tab="한글쓰기", say="소리 내어 읽고 따라 써요.",
        no=f"{group['theme']} · {u['n']}/{total}",
        body=body, parent=parent)


# ──────────────────────────────────────────────────────────────
#  ③ 낱말 — 원본 PDF 양식 (색칠 + 따라쓰기)
# ──────────────────────────────────────────────────────────────

def sheet_word(u, group, total):
    w = u["word"]
    # 글자 수에 따라 칸을 키운다. 한 글자면 큼직하게, 세 글자면 줄인다.
    mm = {1: 46, 2: 42, 3: 34}.get(len(w), 30)
    body = f"""
    <div class="artbox">{art.svg(u["art"])}</div>
    <div style="display:flex;flex-direction:column;align-items:center;gap:3mm;flex:none">
      {row(list(w), mm, "gray")}
      {row(list(w), mm, "blank")}
    </div>"""

    tail = decompose_note(w)
    pill, note = new_badge(u)
    parent = (
        f"「{esc(w)}」 는 {esc(tail)} 입니다. "
        "먼저 <b>그림을 보고 이름을 말하게</b> 한 다음 글자를 보여 주세요 — "
        "그림 → 소리 → 글자 순서라야 통글자로 외우지 않습니다. "
        "색칠은 덤이 아니라 <b>연필을 오래 쥐는 연습</b>입니다. 먼저 칠하게 두세요."
        + note)

    return page(
        title=f"{u['n']:02d}. {w}",
        tab="한글쓰기", say="따라쓰고 색칠해요.",
        no=f"{group['theme']} · {u['n']}/{total}",
        body=body, parent=parent, pill=pill)


def decompose_note(word):
    """낱말을 자모로 풀어서 부모가 읽어 줄 수 있게 적는다.

    「나비」 → 「ㄴ+ㅏ=나, ㅂ+ㅣ=비」
    """
    parts = []
    for ch in word:
        cho_jung_jong = split(ch)
        if not cho_jung_jong:
            continue
        cho, jung, jong = cho_jung_jong
        s = f"{cho}+{jung}"
        if jong:
            s += f"+{jong}"
        parts.append(f"{s}={ch}")
    return ", ".join(parts)


# ──────────────────────────────────────────────────────────────
#  ④ 문장 — 원고지 칸
# ──────────────────────────────────────────────────────────────

def sheet_sentence(u, group, total):
    s = u["sentence"]
    cells = list(s)
    # 문장은 **반드시 한 줄에** 들어가야 한다. 줄이 넘어가면 마지막 한두 칸이
    # 외톨이로 떨어져서, 아이가 그게 같은 문장인지 모른다.
    # 그래서 칸 수에 맞춰 칸 크기를 줄인다 (쓸 만한 최소는 12mm쯤).
    inner, gap = 184, 2.6
    mm = min(17.0, (inner - gap * (len(cells) - 1)) / len(cells))
    if mm < 12:
        raise ValueError(
            f"유닛 {u['n']}: 문장이 {len(cells)}칸이라 한 줄에 안 들어갑니다 "
            f"(칸이 {mm:.1f}mm). 문장을 짧게 고치세요 — units.json")

    def line(cls):
        return ('<div class="boxes">'
                + "".join(box(c if c != " " else None, mm,
                              f"{cls} space" if c == " " else cls)
                          for c in cells) + "</div>")

    # 문장에서 찾아 동그라미 칠 낱말. 데이터에 적어 두지 않으면 첫 어절에서
    # 조사를 떼어 쓴다 — 하지만 그러면 「나」 처럼 시시한 낱말이 나오기도 해서
    # units.json 의 find 로 짚어 주는 편이 낫다.
    target = u.get("find") or s.split()[0].rstrip("을를이가는은.!?")
    pill, note = new_badge(u)
    body = f"""
    <div class="band"><h2>읽어요</h2>
      <span class="hint" style="font-size:7mm;color:var(--ink)">{esc(s)}</span></div>
    <div style="font-family:var(--hand);font-size:4.8mm;color:var(--lilac);flex:none">
      ① 한 글자씩 손가락으로 짚으며 읽어요 &nbsp; ② 회색 글자를 따라 써요 &nbsp;
      ③ 빈 칸에 혼자 써요 &nbsp; (점선 칸은 띄어쓰기예요 — 비워 둡니다)
    </div>
    {line("gray")}
    {line("blank")}
    {line("blank")}
    <div class="band"><h2>찾아요</h2>
      <span class="hint">문장에서 「{esc(target)}」 를 찾아 동그라미 치고, 그림을 색칠하세요</span></div>
    <div class="artbox">{art.svg(u["art"])}</div>"""

    parent = (
        f"오늘 문장은 「{esc(s)}」 입니다. "
        "<b>띄어쓰기 칸(점선)은 비워 둡니다</b> — 여기서 아이가 제일 많이 틀립니다. "
        "마침표도 한 칸을 차지한다는 것을 짚어 주세요. "
        "다 쓴 뒤 <b>손가락으로 짚으며 소리 내어</b> 한 번 더 읽게 하면 문장이 통째로 남습니다."
        + note)

    return page(
        title=f"{u['n']:02d}. {s}",
        tab="한글쓰기", say="읽고 따라 써요.",
        no=f"{group['theme']} · {u['n']}/{total}",
        body=body, parent=parent, pill=pill)


BUILDERS = {
    "jamo": sheet_jamo,
    "table": sheet_table,
    "word": sheet_word,
    "sentence": sheet_sentence,
}


def build_page(u, group, total):
    """유닛 하나의 A4 쪽. 문서로 감싸지 않은 알맹이."""
    kind = u.get("kind")
    if kind not in BUILDERS:
        raise ValueError(f"유닛 {u.get('n')}: 모르는 양식 {kind!r} "
                         f"(쓸 수 있는 것: {', '.join(BUILDERS)})")
    return BUILDERS[kind](u, group, total)


def title_of(u):
    k = u["kind"]
    if k in ("jamo", "table"):
        return f"{u['n']:02d}. {' '.join(u['chars'])}"
    return f"{u['n']:02d}. {u.get('word') or u.get('sentence')}"


def build(u, group, total):
    """유닛 하나짜리 인쇄 문서."""
    return document(title_of(u), [build_page(u, group, total)])


def build_bundle(units, group, total):
    """마당 하나를 통째로. 쪽마다 A4 한 장씩 이어 붙는다."""
    pages = [build_page(u, group, total) for u in units]
    return document(f"{group['theme']} · {len(pages)}장", pages)
