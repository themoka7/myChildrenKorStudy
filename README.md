# 공주님의 한글 나라

6살 아이가 **자음·모음부터 문장까지** 차근차근 올라가는 A4 인쇄용 한글 학습지 44장.

- 아이 화면 (진도 지도) → [`index.html`](index.html)
- 부모 화면 (목록·진도 옮기기) → [`list.html`](list.html)
- 학습지 → [`print/`](print/) · 마당 통째로 인쇄는 `print/madangNN.html`

---

## 어떻게 올라가나

| 마당 | 장수 | 무엇 | 학습지 모양 |
|---|---|---|---|
| 1 · 모음 나라 | 5 | ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ | 획순 번호 + 따라쓰기 + 색칠 |
| 2 · 자음 성 | 7 | ㄱ~ㅎ 14자 | 획순 번호 + 따라쓰기 + 그 소리로 시작하는 낱말 그림 |
| 3 · 글자 만들기 | 7 | 가갸거겨…하햐허혀 | 자음×모음 10칸 조합표 |
| 4 · 받침 없는 낱말 | 10 | 나비·모자·치마·마차… | 색칠 도안 + 따라쓰기 (원본 양식) |
| 5 · 받침 있는 낱말 | 10 | 공주·왕관·리본·반지… | 색칠 도안 + 따라쓰기 |
| 6 · 문장 쓰기 | 5 | 「나는 공주예요.」 | 원고지 칸 + 낱말 찾기 |

**한 장은 A4 딱 한 장**입니다. 하루 15분, 색칠부터 하고 따라 쓰면 됩니다.

학습지 맨 아래 점선 상자는 **부모용**입니다. 아이가 틀렸을 때 무엇을 말해 줄지
그대로 읽으면 되게 적어 두었습니다.

## 아직 안 배운 글자가 나올 때

「드레스」의 `ㅔ`, 「꽃」의 `ㄲ`처럼 순서상 아직 안 가르친 글자가 필요할 때가
있습니다. 그런 장에는 머리말에 **「새 글자 ㅔ(에)」** 딱지가 붙습니다.
아이가 못 읽는 게 당연하다는 표시이고, 부모가 먼저 읽어 주면 됩니다.

선언하지 않은 글자가 몰래 들어오면 `tools/check.py` 가 빌드를 막습니다.

---

## 고치는 법

`units.json` **하나가 원본**입니다. `index.html` · `list.html` · `print/*.html`
은 전부 생성물이라 직접 고치면 다음 빌드에 덮어써집니다.

```bash
python3 tools/build.py            # 학습지 44장 + 마당 묶음 + 지도 + 목록
python3 tools/build.py 20 21      # 유닛 몇 개만 (지도·목록은 항상 다시 만듦)
python3 tools/check.py            # 전수 검사 — 커밋 전 필수
python3 tools/fonts.py            # 글꼴 서브셋 다시 만들기 (글자를 새로 쓴 뒤)
python3 tools/fonts.py --check    # 인쇄물에 두부(□)로 나갈 글자가 없는지

python3 tools/preview_art.py      # 색칠 도안 36개를 한 장에
python3 tools/preview_jamo.py     # 자모 24자 획순을 한 장에
python3 tools/where_overflow.py print/unit20.html   # A4를 넘쳤을 때
```

`build.py` 는 만든 학습지를 **Chromium 으로 실제 인쇄해 쪽 수를 셉니다.**
A4 한 장을 넘기면 빌드가 실패합니다 — 넘친 내용은 화면에서 안 보이고
인쇄할 때만 사라지기 때문입니다.

### 새 낱말 하나 추가하기

1. `tools/art.py` 에 색칠 도안을 그린다 → `python3 tools/preview_art.py 이름` 으로 눈으로 확인
2. `units.json` 에 유닛을 넣는다 (`kind`, `word`, `art`)
3. `python3 tools/build.py && python3 tools/fonts.py && python3 tools/check.py`

---

## 만들어진 것들

```
units.json          단 하나의 원본 — 44유닛의 순서·내용·상태
tools/
  art.py            색칠 도안 36개 (SVG 선화)
  jamo.py           자모 24자의 획순 좌표
  sheet.py          A4 학습지 4종 양식
  build.py          전부 다시 만들기 + 레이아웃 검증
  build_map.py      지도 (아이 화면)
  build_index.py    목록 (부모 화면)
  check.py          전수 검사 ★
  fonts.py          글꼴 서브셋 → assets/fonts.css
  render.py         Chromium 인쇄·화면 캡처
  preview_art.py    도안 미리보기
  preview_jamo.py   획순 미리보기
  where_overflow.py A4를 넘긴 자리 짚기
assets/fonts.css    쓰는 글자만 남긴 글꼴 (인터넷 없이도 똑같이 인쇄됨)
print/              생성물 — 낱장 44장 + 마당 묶음 6장
index.html list.html  생성물
```

왜 그렇게 만들었는지와 어디서 깨졌는지는 [`HANDOFF.md`](HANDOFF.md) 에 있습니다.

## 그림에 대하여

색칠 도안 36개는 **전부 이 저장소에서 새로 그린 것**입니다.
양식을 참고한 원본 PDF의 그림은 남의 저작물이라 쓰지 않았습니다.
