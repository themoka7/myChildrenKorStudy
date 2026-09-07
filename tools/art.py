#!/usr/bin/env python3
"""색칠 도안 — 굵은 선 하나로 그린 흑백 선화.

아이가 크레파스로 칠할 그림이다. 그래서 규칙이 셋 있다.

  1. **선이 굵다** (stroke-width 7). 6살이 칠하면 선 밖으로 나간다.
     선이 얇으면 칠한 색에 파묻혀서 그림이 뭉개진다.
  2. **면이 닫혀 있다.** 열린 선으로 그리면 칠할 영역이 안 생긴다.
  3. **속은 흰색**(fill:#fff)이다. 인쇄할 때 잉크를 안 먹고, 화면에서도
     겹친 선이 서로를 가려 준다.

모든 그림은 `viewBox 0 0 240 200` 안에 그린다. 쓰는 쪽에서 크기를 정한다.

⚠️ 원본 PDF(달콤부부 블로그)의 그림은 남의 저작물이라 쓰지 않았다.
   여기 있는 것은 전부 이 저장소에서 새로 그린 것이다.
"""

# 선화 공통 속성. 그림마다 다시 쓰지 않게 <g> 하나로 묶어서 상속시킨다.
STROKE = ('fill="#fff" stroke="#111" stroke-width="7" '
          'stroke-linecap="round" stroke-linejoin="round"')

# 칠할 면이 아니라 '표정·무늬' 인 선. 속을 안 채운다.
LINE = 'fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'
THIN = 'fill="none" stroke="#111" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"'
DOT = 'fill="#111" stroke="none"'


ART = {}


def art(name):
    """그림 하나를 등록한다."""
    def deco(fn):
        ART[name] = fn()
        return fn
    return deco


# ──────────────────────────────────────────────────────────────
#  공주 나라
# ──────────────────────────────────────────────────────────────

@art("왕관")
def _crown():
    return f'''
    <path {STROKE} d="M34 128 L52 52 L86 104 L120 40 L154 104 L188 52 L206 128 Z"/>
    <path {STROKE} d="M34 128 h172 a6 6 0 0 1 6 6 v24 a6 6 0 0 1 -6 6 h-172 a6 6 0 0 1 -6 -6 v-24 a6 6 0 0 1 6 -6 Z"/>
    <circle {STROKE} cx="52" cy="44" r="11"/>
    <circle {STROKE} cx="120" cy="32" r="12"/>
    <circle {STROKE} cx="188" cy="44" r="11"/>
    <circle {STROKE} cx="76" cy="146" r="9"/>
    <circle {STROKE} cx="120" cy="146" r="9"/>
    <circle {STROKE} cx="164" cy="146" r="9"/>'''


@art("공주")
def _princess():
    return f'''
    <path {STROKE} d="M84 46 L92 12 L106 34 L120 6 L134 34 L148 12 L156 46 Z"/>
    <path {STROKE} d="M84 46 h72 v12 h-72 Z"/>
    <circle {STROKE} cx="120" cy="88" r="40"/>
    <path {STROKE} d="M82 82 C66 130 68 164 82 188 L102 134 Z"/>
    <path {STROKE} d="M158 82 C174 130 172 164 158 188 L138 134 Z"/>
    <path {STROKE} d="M100 124 L140 124 L190 197 L50 197 Z"/>
    <circle {DOT} cx="107" cy="84" r="5"/>
    <circle {DOT} cx="133" cy="84" r="5"/>
    <path {LINE} d="M110 102 q10 9 20 0"/>'''


@art("드레스")
def _dress():
    return f'''
    <path {STROKE} d="M92 30 L148 30 L156 84 L84 84 Z"/>
    <path {STROKE} d="M82 84 h76 v18 h-76 Z"/>
    <path {STROKE} d="M84 102 L156 102 L200 190 q-80 16 -160 0 Z"/>
    <path {THIN} d="M92 30 L74 52 M148 30 L166 52"/>
    <path {THIN} d="M110 110 L96 176 M130 110 L144 176 M120 110 v68"/>'''


@art("리본")
def _ribbon():
    return f'''
    <path {STROKE} d="M108 100 L46 62 C28 74 28 126 46 138 Z"/>
    <path {STROKE} d="M132 100 L194 62 C212 74 212 126 194 138 Z"/>
    <path {STROKE} d="M108 118 L84 178 L112 168 L120 190 L128 168 L156 178 L132 118 Z"/>
    <circle {STROKE} cx="120" cy="100" r="17"/>'''


@art("반지")
def _ring():
    # 보석이 위, 반지 테가 아래. 뒤집으면 아이 눈에 '반지'로 안 읽힌다.
    return f'''
    <ellipse {STROKE} cx="120" cy="140" rx="54" ry="48"/>
    <ellipse fill="#fff" stroke="#111" stroke-width="6" cx="120" cy="140" rx="34" ry="30"/>
    <path {STROKE} d="M120 24 L86 62 L120 108 L154 62 Z"/>
    <path {THIN} d="M86 62 h68 M120 24 v84 M103 43 L120 62 L137 43"/>'''


@art("마차")
def _carriage():
    return f'''
    <path {STROKE} d="M120 34 C176 34 206 76 206 116 C206 148 172 164 120 164
                       C68 164 34 148 34 116 C34 76 64 34 120 34 Z"/>
    <path {THIN} d="M120 34 C104 74 104 124 120 164 M120 34 C136 74 136 124 120 164
                    M64 50 C58 90 62 130 78 158 M176 50 C182 90 178 130 162 158"/>
    <rect {STROKE} x="96" y="76" width="48" height="52" rx="22"/>
    <circle {STROKE} cx="66" cy="170" r="26"/>
    <circle {STROKE} cx="174" cy="170" r="26"/>
    <circle {DOT} cx="66" cy="170" r="6"/>
    <circle {DOT} cx="174" cy="170" r="6"/>'''


@art("성")
def _castle():
    return f'''
    <path {STROKE} d="M40 190 v-88 h34 v88 Z"/>
    <path {STROKE} d="M166 190 v-88 h34 v88 Z"/>
    <path {STROKE} d="M74 190 v-64 h92 v64 Z"/>
    <path {STROKE} d="M40 102 L57 60 L74 102 Z"/>
    <path {STROKE} d="M166 102 L183 60 L200 102 Z"/>
    <path {STROKE} d="M74 126 L120 76 L166 126 Z"/>
    <path {STROKE} d="M104 190 v-38 a16 16 0 0 1 32 0 v38 Z"/>
    <path {LINE} d="M120 76 v-28 M57 60 v-22 M183 60 v-22"/>
    <path {STROKE} d="M120 48 L152 58 L120 68 Z"/>
    <rect {STROKE} x="49" y="122" width="16" height="20" rx="7"/>
    <rect {STROKE} x="175" y="122" width="16" height="20" rx="7"/>'''


@art("유니콘")
def _unicorn():
    # 오른쪽을 보는 얼굴 옆모습. 뿔 → 귀 → 갈기 순으로 읽히게 배치했다.
    return f'''
    <path {STROKE} d="M118 40 C158 40 186 66 190 100 C194 132 178 158 150 168
                       L150 192 L96 192 L96 152 C74 140 66 106 82 74 C92 54 104 40 118 40 Z"/>
    <path {STROKE} d="M126 44 L138 6 L154 42 Z"/>
    <path {THIN} d="M130 32 l18 5 M134 20 l16 5"/>
    <path {STROKE} d="M96 56 L74 26 L106 40 Z"/>
    <path {STROKE} d="M84 74 C56 66 34 82 30 106 C50 100 62 106 68 116
                       C46 118 30 138 32 160 C54 148 68 152 76 160
                       C66 128 68 96 84 74 Z"/>
    <circle {DOT} cx="152" cy="94" r="6"/>
    <path {LINE} d="M186 120 q-10 8 -20 4"/>
    <circle {DOT} cx="182" cy="106" r="4"/>'''


@art("요정")
def _fairy():
    return f'''
    <path {STROKE} d="M96 96 C60 66 34 74 30 100 C26 126 56 140 96 128 Z"/>
    <path {STROKE} d="M144 96 C180 66 206 74 210 100 C214 126 184 140 144 128 Z"/>
    <circle {STROKE} cx="120" cy="80" r="30"/>
    <path {STROKE} d="M106 108 L134 108 L156 186 L84 186 Z"/>
    <circle {DOT} cx="110" cy="76" r="4.5"/>
    <circle {DOT} cx="130" cy="76" r="4.5"/>
    <path {LINE} d="M112 92 q8 7 16 0"/>
    <path {THIN} d="M186 150 l0 -18 M177 141 l18 0 M40 158 l0 -14 M33 151 l14 0"/>'''


@art("거울")
def _mirror():
    return f'''
    <ellipse {STROKE} cx="120" cy="80" rx="62" ry="70"/>
    <ellipse fill="#fff" stroke="#111" stroke-width="6" cx="120" cy="80" rx="44" ry="52"/>
    <path {STROKE} d="M106 150 h28 v40 a14 14 0 0 1 -28 0 Z"/>
    <path {THIN} d="M100 58 q12 -14 26 -12 M96 78 q4 -8 10 -12"/>'''


@art("구두")
def _shoe():
    # 옆모습으로 세 번 그려 봤지만 전부 새·물개처럼 보였다.
    # 위에서 내려다본 모양이면 '신발 구멍 + 리본' 만으로 분명해진다.
    return f'''
    <path {STROKE} d="M120 10 C168 10 194 56 194 108 C194 158 166 192 120 192
                       C74 192 46 158 46 108 C46 56 72 10 120 10 Z"/>
    <path {STROKE} d="M120 62 C150 62 166 86 166 112 C166 142 146 162 120 162
                       C94 162 74 142 74 112 C74 86 90 62 120 62 Z"/>
    <path {STROKE} d="M108 34 L72 16 C58 24 58 48 72 56 Z"/>
    <path {STROKE} d="M132 34 L168 16 C182 24 182 48 168 56 Z"/>
    <circle {STROKE} cx="120" cy="35" r="12"/>
    <path {THIN} d="M84 176 h72"/>'''


@art("케이크")
def _cake():
    return f'''
    <path {STROKE} d="M46 190 v-52 h148 v52 Z"/>
    <path {STROKE} d="M62 138 v-40 h116 v40 Z"/>
    <path {THIN} d="M62 116 q16 12 29 0 q13 -12 29 0 q16 12 29 0 q13 -12 29 0"/>
    <path {THIN} d="M46 166 q18 12 33 0 q15 -12 33 0 q18 12 33 0 q15 -12 33 0"/>
    <rect {STROKE} x="93" y="60" width="12" height="38" rx="5"/>
    <rect {STROKE} x="135" y="60" width="12" height="38" rx="5"/>
    <path {STROKE} d="M99 58 C90 48 99 36 99 30 C99 38 108 46 99 58 Z"/>
    <path {STROKE} d="M141 58 C132 48 141 36 141 30 C141 38 150 46 141 58 Z"/>'''


@art("사탕")
def _candy():
    return f'''
    <circle {STROKE} cx="120" cy="104" r="48"/>
    <path {THIN} d="M120 104 m-26 0 a26 26 0 0 1 26 -26 a38 38 0 0 1 0 52 a14 14 0 0 1 0 -28"/>
    <path {STROKE} d="M74 86 L34 60 L44 104 L34 148 L74 122 Z"/>
    <path {STROKE} d="M166 86 L206 60 L196 104 L206 148 L166 122 Z"/>'''


@art("하트")
def _heart():
    return f'''
    <path {STROKE} d="M120 182 C34 122 40 50 82 50 C104 50 117 68 120 82
                       C123 68 136 50 158 50 C200 50 206 122 120 182 Z"/>'''


@art("별")
def _star():
    return f'''
    <path {STROKE} d="M120 24 L148 90 L220 96 L166 142 L182 212
                       L120 174 L58 212 L74 142 L20 96 L92 90 Z"/>'''


@art("꽃")
def _flower():
    return f'''
    <path {LINE} d="M120 190 v-58"/>
    <path {STROKE} d="M120 160 C96 156 80 168 82 184 C100 186 116 178 120 160 Z"/>
    <circle {STROKE} cx="120" cy="52" r="28"/>
    <circle {STROKE} cx="72" cy="86" r="28"/>
    <circle {STROKE} cx="168" cy="86" r="28"/>
    <circle {STROKE} cx="90" cy="142" r="28"/>
    <circle {STROKE} cx="150" cy="142" r="28"/>
    <circle {STROKE} cx="120" cy="100" r="26"/>'''


# ──────────────────────────────────────────────────────────────
#  자연 · 동물
# ──────────────────────────────────────────────────────────────

@art("나비")
def _butterfly():
    return f'''
    <path {STROKE} d="M112 100 C72 52 34 52 30 84 C26 116 66 128 112 116 Z"/>
    <path {STROKE} d="M128 100 C168 52 206 52 210 84 C214 116 174 128 128 116 Z"/>
    <path {STROKE} d="M112 120 C76 132 52 154 62 178 C82 192 106 168 112 136 Z"/>
    <path {STROKE} d="M128 120 C164 132 188 154 178 178 C158 192 134 168 128 136 Z"/>
    <path {STROKE} d="M120 66 a10 10 0 0 1 10 10 v88 a10 10 0 0 1 -20 0 v-88 a10 10 0 0 1 10 -10 Z"/>
    <path {THIN} d="M116 66 C106 44 92 34 78 32 M124 66 C134 44 148 34 162 32"/>'''


@art("토끼")
def _rabbit():
    return f'''
    <path {STROKE} d="M96 92 C86 56 84 26 94 20 C106 16 110 48 112 88 Z"/>
    <path {STROKE} d="M144 92 C154 56 156 26 146 20 C134 16 130 48 128 88 Z"/>
    <circle {STROKE} cx="120" cy="130" r="52"/>
    <circle {DOT} cx="102" cy="122" r="5.5"/>
    <circle {DOT} cx="138" cy="122" r="5.5"/>
    <path {STROKE} d="M120 140 l-9 -8 h18 Z"/>
    <path {LINE} d="M120 148 q-12 12 -22 2 M120 148 q12 12 22 2"/>
    <path {THIN} d="M66 132 h-24 M68 146 h-24 M174 132 h24 M172 146 h24"/>'''


@art("오리")
def _duck():
    return f'''
    <path {STROKE} d="M78 190 C44 178 34 148 46 124 C58 100 92 92 122 98
                       C158 104 182 130 178 158 C174 182 138 198 78 190 Z"/>
    <circle {STROKE} cx="148" cy="72" r="34"/>
    <path {STROKE} d="M182 72 L222 82 L182 92 Z"/>
    <circle {DOT} cx="156" cy="64" r="5"/>
    <path {THIN} d="M84 140 q20 14 40 0 q20 -14 40 0"/>'''


@art("물고기")
def _fish():
    return f'''
    <path {STROKE} d="M158 100 C158 62 118 44 82 52 C42 60 22 82 22 100
                       C22 118 42 140 82 148 C118 156 158 138 158 100 Z"/>
    <path {STROKE} d="M158 100 L214 62 L204 100 L214 138 Z"/>
    <path {STROKE} d="M78 56 L96 24 L112 58 Z"/>
    <circle {DOT} cx="56" cy="90" r="6"/>
    <path {THIN} d="M110 66 C102 84 102 116 110 134"/>
    <path {THIN} d="M132 76 C126 88 126 112 132 124"/>'''


@art("새")
def _bird():
    return f'''
    <path {STROKE} d="M64 128 C64 92 92 70 124 70 C158 70 182 94 182 126
                       C182 158 156 178 122 178 C88 178 64 160 64 128 Z"/>
    <circle {STROKE} cx="98" cy="66" r="30"/>
    <path {STROKE} d="M70 62 L34 74 L70 84 Z"/>
    <path {STROKE} d="M126 108 C154 96 178 104 186 120 C168 134 142 132 126 122 Z"/>
    <circle {DOT} cx="104" cy="58" r="5"/>
    <path {LINE} d="M110 178 v14 M144 176 v16"/>'''


@art("나무")
def _tree():
    return f'''
    <path {STROKE} d="M98 195 v-78 h44 v78 q-22 8 -44 0 Z"/>
    <circle {STROKE} cx="120" cy="58" r="50"/>
    <circle {STROKE} cx="66" cy="90" r="34"/>
    <circle {STROKE} cx="174" cy="90" r="34"/>'''


@art("포도")
def _grapes():
    return f'''
    <path {LINE} d="M120 56 v-22 q18 -10 30 -2"/>
    <path {STROKE} d="M126 40 C150 20 178 26 184 44 C160 54 136 52 126 40 Z"/>
    <circle {STROKE} cx="120" cy="76" r="22"/>
    <circle {STROKE} cx="88" cy="104" r="22"/>
    <circle {STROKE} cx="152" cy="104" r="22"/>
    <circle {STROKE} cx="120" cy="120" r="22"/>
    <circle {STROKE} cx="70" cy="142" r="22"/>
    <circle {STROKE} cx="170" cy="142" r="22"/>
    <circle {STROKE} cx="120" cy="160" r="22"/>'''


@art("사과")
def _apple():
    return f'''
    <path {STROKE} d="M120 66 C104 46 72 44 56 66 C36 94 46 156 78 180
                       C96 192 110 180 120 180 C130 180 144 192 162 180
                       C194 156 204 94 184 66 C168 44 136 46 120 66 Z"/>
    <path {LINE} d="M120 66 v-30"/>
    <path {STROKE} d="M124 44 C144 24 172 26 178 42 C158 58 132 58 124 44 Z"/>'''


@art("구름")
def _cloud():
    return f'''
    <path {STROKE} d="M62 158 C34 158 20 138 26 118 C32 100 52 94 66 100
                       C68 68 100 50 128 62 C146 46 178 52 186 78
                       C212 80 222 106 210 128 C202 146 184 158 162 158 Z"/>'''


@art("우산")
def _umbrella():
    return f'''
    <path {STROKE} d="M18 110 C18 62 64 30 120 30 C176 30 222 62 222 110
                       C196 96 178 96 154 110 C138 96 102 96 86 110 C62 96 44 96 18 110 Z"/>
    <path {LINE} d="M120 110 v58"/>
    <path {STROKE} d="M120 168 C120 190 96 194 88 178"/>'''


@art("모자")
def _hat():
    return f'''
    <ellipse {STROKE} cx="120" cy="146" rx="100" ry="28"/>
    <path {STROKE} d="M74 146 C68 100 88 58 120 58 C152 58 172 100 166 146 Z"/>
    <path {STROKE} d="M72 120 h96 v24 h-96 Z"/>
    <path {STROKE} d="M158 118 C178 104 196 114 198 132 C178 144 158 138 158 118 Z"/>'''


@art("기차")
def _train():
    return f'''
    <path {STROKE} d="M28 158 v-52 h74 v-46 h44 v46 h64 v52 Z"/>
    <rect {STROKE} x="48" y="118" width="34" height="28" rx="5"/>
    <rect {STROKE} x="118" y="74" width="26" height="26" rx="5"/>
    <rect {STROKE} x="166" y="118" width="34" height="28" rx="5"/>
    <path {STROKE} d="M62 60 h34 v-16 h-34 Z"/>
    <path {STROKE} d="M64 44 C58 30 68 20 79 20 C90 20 100 30 94 44 Z"/>
    <circle {STROKE} cx="66" cy="172" r="20"/>
    <circle {STROKE} cx="174" cy="172" r="20"/>
    <path {THIN} d="M14 190 h212"/>'''


@art("우유")
def _milk():
    # 갑(carton)으로 그렸더니 '집'으로 읽혔다. 빨대 꽂은 컵이 훨씬 분명하다.
    return f'''
    <path {STROKE} d="M62 56 h116 l-14 134 q-44 8 -88 0 Z"/>
    <path {LINE} d="M70 96 q50 12 100 0"/>
    <path {STROKE} d="M138 60 L166 14 L188 20 L156 62 Z"/>
    <ellipse {STROKE} cx="120" cy="56" rx="58" ry="14"/>'''


@art("바다")
def _sea():
    return f'''
    <circle {STROKE} cx="176" cy="56" r="30"/>
    <path {THIN} d="M176 12 v-8 M176 108 v8 M132 56 h-8 M220 56 h8
                    M145 25 l-6 -6 M207 87 l6 6 M207 25 l6 -6 M145 87 l-6 6"/>
    <path {LINE} d="M18 118 q26 -20 52 0 q26 20 52 0 q26 -20 52 0 q26 20 52 0"/>
    <path {LINE} d="M18 152 q26 -20 52 0 q26 20 52 0 q26 -20 52 0 q26 20 52 0"/>
    <path {LINE} d="M18 186 q26 -20 52 0 q26 20 52 0 q26 -20 52 0 q26 20 52 0"/>'''


@art("치마")
def _skirt():
    return f'''
    <path {STROKE} d="M78 46 h84 v22 h-84 Z"/>
    <path {STROKE} d="M78 68 h84 L206 182 q-86 22 -172 0 Z"/>
    <path {THIN} d="M104 76 L82 172 M132 76 L154 172 M118 76 v98"/>'''


@art("달")
def _moon():
    return f'''
    <path {STROKE} d="M148 26 C96 26 56 68 56 116 C56 164 96 196 148 190
                       C110 168 92 142 92 108 C92 74 112 44 148 26 Z"/>
    <path {THIN} d="M186 62 l0 -20 M176 52 l20 0 M204 130 l0 -14 M197 123 l14 0"/>'''


@art("곰")
def _bear():
    return f'''
    <circle {STROKE} cx="70" cy="72" r="24"/>
    <circle {STROKE} cx="170" cy="72" r="24"/>
    <circle {STROKE} cx="120" cy="122" r="58"/>
    <ellipse {STROKE} cx="120" cy="142" rx="30" ry="24"/>
    <path {STROKE} d="M120 132 l-10 -9 h20 Z"/>
    <path {LINE} d="M120 141 v8 M120 149 q-10 10 -18 2 M120 149 q10 10 18 2"/>
    <circle {DOT} cx="98" cy="106" r="6"/>
    <circle {DOT} cx="142" cy="106" r="6"/>'''


@art("집")
def _house():
    return f'''
    <path {STROKE} d="M46 190 v-84 h148 v84 Z"/>
    <path {STROKE} d="M28 106 L120 34 L212 106 Z"/>
    <path {STROKE} d="M102 190 v-56 h36 v56 Z"/>
    <rect {STROKE} x="60" y="124" width="30" height="30" rx="4"/>
    <rect {STROKE} x="150" y="124" width="30" height="30" rx="4"/>
    <path {STROKE} d="M158 68 v-30 h22 v46 Z"/>'''


@art("눈사람")
def _snowman():
    return f'''
    <circle {STROKE} cx="120" cy="146" r="46"/>
    <circle {STROKE} cx="120" cy="76" r="32"/>
    <path {STROKE} d="M88 50 h64 v10 h-64 Z"/>
    <path {STROKE} d="M96 50 v-24 h48 v24 Z"/>
    <path {STROKE} d="M120 78 L150 86 L120 92 Z"/>
    <circle {DOT} cx="108" cy="70" r="5"/>
    <circle {DOT} cx="132" cy="70" r="5"/>
    <circle {DOT} cx="120" cy="130" r="6"/>
    <circle {DOT} cx="120" cy="154" r="6"/>
    <path {LINE} d="M76 132 L36 112 M36 112 l-14 6 M36 112 l2 -16
                    M164 132 L204 112 M204 112 l14 6 M204 112 l-2 -16"/>'''


@art("연필")
def _pencil():
    return f'''
    <path {STROKE} d="M64 34 h112 v112 h-112 Z"/>
    <path {STROKE} d="M64 146 h112 L120 196 Z"/>
    <path {STROKE} d="M104 172 L120 196 L136 172 Z"/>
    <path {THIN} d="M102 34 v112 M138 34 v112"/>'''


def svg(name, size=None, cls="art"):
    """이름으로 그림 하나를 <svg> 로 꺼낸다.

    없는 이름을 부르면 조용히 빈 그림을 주지 않고 죽는다 — units.json 의
    오타를 빌드 때 잡으려는 것이다. (영어 저장소에서 조용한 실패로 한 번 크게 당했다)
    """
    if name not in ART:
        raise KeyError(f"그런 도안이 없습니다: {name!r}\n"
                       f"있는 것: {', '.join(sorted(ART))}")
    dim = f' width="{size}" height="{size * 200 // 240}"' if size else ""
    return (f'<svg class="{cls}" viewBox="0 0 240 200"{dim} '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{ART[name]}</svg>')


def names():
    return sorted(ART)


if __name__ == "__main__":
    print(f"도안 {len(ART)}개")
    for n in names():
        print(" ", n)
