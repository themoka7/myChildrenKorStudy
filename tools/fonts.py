#!/usr/bin/env python3
"""글꼴을 필요한 글자만 남기고 잘라서 CSS 한 장에 넣는다.

**왜 굳이 이렇게 하나**

인쇄용 저장소다. 부모가 인쇄 버튼을 누르는 순간 인터넷이 느리거나 끊겨 있으면
구글 웹폰트가 안 붙고, 그러면 글자 크기가 달라져서 **A4 한 장이 두 장이 된다.**
따라쓰기 칸 안의 회색 글자가 칸 밖으로 삐져나가기도 한다.

그래서 쓰는 글자만 골라내(subset) base64 로 CSS 안에 박아 둔다. 파일 하나만
있으면 비행기 안에서도 똑같이 인쇄된다.

한글 전체(11,172자)를 넣으면 5MB 가 넘지만, 이 자료가 실제로 쓰는 글자는
300자 남짓이라 100KB 아래로 떨어진다.

사용법:
    python3 tools/fonts.py              # assets/fonts.css 다시 만들기
    python3 tools/fonts.py --check      # 빠진 글자가 있는지만 본다
"""
import argparse
import base64
import io
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".build", "fonts")
OUT = os.path.join(ROOT, "assets", "fonts.css")

# 구글 폰트가 주는 실제 파일. URL 이 바뀌면 받아오기가 404 로 죽는다 —
# 조용히 넘어가지 않게 두는 편이 낫다. 캐시가 있으면 받지 않는다.
SOURCES = {
    # 파일이름            (구글 CSS 가 가리키는 ttf, css font-family, weight)
    "notokr-400.ttf": ("https://fonts.gstatic.com/s/notosanskr/v39/"
                       "PbyxFmXiEBPT4ITbgNA5Cgms3VYcOA-vvnIzzuoyeLQ.ttf",
                       "Noto Sans KR", 400),
    "notokr-700.ttf": ("https://fonts.gstatic.com/s/notosanskr/v39/"
                       "PbyxFmXiEBPT4ITbgNA5Cgms3VYcOA-vvnIzzg01eLQ.ttf",
                       "Noto Sans KR", 700),
    "jua-400.ttf": ("https://fonts.gstatic.com/s/jua/v18/co3KmW9ljjAjcw.ttf",
                    "Jua", 400),
    "gaegu-700.ttf": ("https://fonts.gstatic.com/s/gaegu/v23/"
                      "TuGSUVB6Up9NU573jvw7.ttf", "Gaegu", 700),
}

# 어느 페이지에나 나오는 글자. 데이터에서 못 긁어 오는 것들을 여기에 둔다.
ALWAYS = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    " .,!?·:;~/()[]<>-—–…'\"%&+=#@*"
    "①②③④⑤⑥⑦⑧⑨⑩"
    "★☆♥♡●○◇◆■□▶◀→←↓↑✓✔"
    # 자모 낱자 (자음·모음 페이지에서 통째로 쓴다)
    "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
)


def fetch(name):
    """원본 ttf 를 받아 .build/fonts 에 캐시한다."""
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and os.path.getsize(path) > 100_000:
        return path
    os.makedirs(CACHE, exist_ok=True)
    url = SOURCES[name][0]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if len(data) < 100_000:
        sys.exit(f"글꼴이 이상하게 작습니다 ({len(data)}바이트): {url}\n"
                 "구글 폰트 URL 이 바뀌었을 수 있습니다 — tools/fonts.py 의 SOURCES 를 고쳐 주세요.")
    open(path, "wb").write(data)
    return path


def subset(ttf_path, chars):
    """필요한 글자만 남긴 woff2 바이트를 준다."""
    from fontTools import subset as ss
    from fontTools.ttLib import TTFont

    font = TTFont(ttf_path)
    opt = ss.Options()
    opt.layout_features = ["*"]      # 한글 조합에 쓰이는 기능을 살려 둔다
    opt.notdef_outline = True
    opt.desubroutinize = True
    opt.drop_tables += ["DSIG"]

    sub = ss.Subsetter(options=opt)
    sub.populate(text="".join(sorted(set(chars))))
    sub.subset(font)

    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def corpus():
    """이 저장소가 실제로 찍는 모든 글자를 모은다.

    units.json 뿐 아니라 **템플릿에 박힌 안내 문구**도 긁는다. 안내 문구를
    빼먹으면 '따라쓰고 색칠해요' 같은 제목이 통째로 두부(□)가 된다.
    """
    import json
    import re

    text = set(ALWAYS)

    data = open(os.path.join(ROOT, "units.json"), encoding="utf-8").read()
    text |= set(data)
    json.loads(data)  # 깨진 JSON 이면 여기서 죽는다

    # 템플릿·지도·목록에 박아 둔 한글 문구
    for name in ("sheet.py", "build_map.py", "build_index.py", "jamo.py"):
        p = os.path.join(ROOT, "tools", name)
        if os.path.exists(p):
            text |= set(open(p, encoding="utf-8").read())

    # 조합표(3마당)의 음절은 **빌드할 때 만들어진다.** units.json 에도
    # 소스에도 '갸' 라는 글자가 없어서, 소스만 긁으면 통째로 빠진다.
    # (실제로 그렇게 두부 글자가 나갈 뻔했다 — 검사기가 잡았다)
    # 그래서 학습지가 만드는 것과 같은 방법으로 여기서도 만들어 둔다.
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import jamo
    import sheet
    for c in jamo.CONSONANTS:
        for v in sheet.BASE_VOWELS:
            text.add(sheet.compose(c, v))

    # 소스에서 긁으면 한글이 아닌 기호까지 딸려 오지만, 서브셋에 몇 자
    # 더 들어가는 손해가 두부 글자가 나가는 손해보다 훨씬 싸다.
    return {c for c in text if c.strip() and ord(c) > 31}


def build():
    chars = corpus()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    faces, total = [], 0
    for name, (_, family, weight) in SOURCES.items():
        ttf = fetch(name)
        woff2 = subset(ttf, chars)
        total += len(woff2)
        b64 = base64.b64encode(woff2).decode()
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
        print(f"  {family} {weight}: {len(woff2) / 1024:.0f}KB")

    header = ("/* 자동 생성 — tools/fonts.py 가 만듭니다. 직접 고치지 마세요. */\n"
              f"/* 글자 {len(chars)}자를 남긴 서브셋입니다. */\n")
    open(OUT, "w", encoding="utf-8").write(header + "\n".join(faces) + "\n")
    print(f"글자 {len(chars)}자 · 합계 {total / 1024:.0f}KB → assets/fonts.css")


def check():
    """생성된 HTML 이 쓰는 글자가 전부 서브셋에 있는지 본다.

    나중에 안내 문구를 고치고 fonts.py 를 다시 안 돌리면 그 글자가 두부(□)로
    인쇄된다. 눈으로는 잘 안 보인다 — 그래서 검사기가 본다.
    """
    import glob
    import re

    if not os.path.exists(OUT):
        sys.exit("assets/fonts.css 가 없습니다. python3 tools/fonts.py 를 먼저 돌리세요.")

    have = corpus()
    used, where = set(), {}
    files = glob.glob(os.path.join(ROOT, "print", "*.html"))
    files += [os.path.join(ROOT, f) for f in ("index.html", "list.html")]
    for f in files:
        if not os.path.exists(f):
            continue
        html = open(f, encoding="utf-8").read()
        html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
        html = re.sub(r"<[^>]+>", " ", html)
        for c in html:
            if "가" <= c <= "힣" or "ㄱ" <= c <= "ㆎ":
                used.add(c)
                where.setdefault(c, os.path.basename(f))

    # 아무것도 못 찾았는데 통과시키면 안 된다. 검사기가 0개를 찾고
    # "이상 없음" 을 내는 것이 제일 위험하다 — 고장난 줄도 모른다.
    if len(used) < 100:
        sys.exit(f"인쇄물에서 한글을 {len(used)}자밖에 못 찾았습니다 "
                 f"(검사한 파일 {len(files)}개). 학습지를 먼저 만드세요: "
                 "python3 tools/build.py")

    missing = sorted(used - have)
    if missing:
        detail = ", ".join(f"{c}({where[c]})" for c in missing[:20])
        sys.exit(f"서브셋에 없는 글자 {len(missing)}자가 인쇄물에 있습니다: {detail}\n"
                 "python3 tools/fonts.py 로 글꼴을 다시 만드세요.")
    print(f"글꼴 검사 통과 — 인쇄물이 쓰는 한글 {len(used)}자가 모두 들어 있습니다.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="빠진 글자만 검사")
    a = ap.parse_args()
    check() if a.check else build()
