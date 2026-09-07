#!/usr/bin/env python3
"""units.json → index.html (아이가 보는 진도 지도).

**아이 화면과 부모 화면을 반드시 나눈다.** 진도표·날짜·걸린 시간을 여기에
합치면 아이 화면이 관리 화면이 된다. 그런 화면은 아이가 안 연다.
관리용은 list.html 쪽이다.

도장은 두 군데에서 온다.
  · units.json 의 status:"done"  → 저장소 기록. 어느 기기에서나 같다
  · 브라우저 localStorage        → 아이가 직접 찍은 것. 그 기기에만

저장할 때 **그때의 씨앗 목록을 함께** 남겨 두고, 다음에 열 때 그 사이 새로
done 이 된 것만 더한다. 그래서 units.json 을 나중에 고쳐도 아이가 일부러
뺀 도장이 되살아나지 않는다.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import art      # noqa: E402
import sheet    # noqa: E402

CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:var(--serif);color:var(--ink);
  background:
    radial-gradient(circle at 12% 8%, #FFE9F3 0, transparent 45%),
    radial-gradient(circle at 88% 20%, #EEE6FB 0, transparent 40%),
    #FFF9FC;
  min-height:100vh;
}
a{color:inherit;text-decoration:none}

.wrap{max-width:1080px;margin:0 auto;padding:22px 18px 60px}

header.top{text-align:center;padding:20px 0 6px;position:relative}
header.top h1{
  font-family:var(--round);font-weight:400;font-size:clamp(30px,6vw,46px);
  margin:0;color:var(--rose);letter-spacing:-1px;
}
header.top p{font-family:var(--hand);font-size:19px;color:var(--lilac);margin:6px 0 0}
.guidebtn{
  position:absolute;right:0;top:22px;font-family:var(--round);font-size:15px;
  background:#fff;border:2.5px solid var(--lilac);color:var(--lilac);
  border-radius:999px;padding:7px 16px;cursor:pointer;box-shadow:0 3px 0 #E3D8F0;
}

/* 전체 진행 막대 */
.progress{margin:18px auto 6px;max-width:560px}
.bar{height:20px;border:2.5px solid var(--ink);border-radius:999px;background:#fff;overflow:hidden}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#F7B7D2,var(--rose));width:0;transition:width .5s}
.progress .cap{font-family:var(--round);text-align:center;margin-top:7px;color:var(--ink);font-size:16px}

/* 마당 */
.zone{margin:34px 0 0}
.zone > h2{
  font-family:var(--round);font-weight:400;font-size:22px;margin:0 0 4px;
  display:flex;align-items:center;gap:10px;color:var(--ink);
}
.zone > h2 .ico{font-size:26px}
.zone > h2 .cnt{cursor:pointer;text-decoration:none;
  font-size:14px;color:var(--lilac);background:#fff;border:2px solid var(--line);
  border-radius:999px;padding:2px 11px;margin-left:auto;
}
.zone .note{font-family:var(--hand);font-size:16px;color:#8C7A98;margin:0 0 12px}

.stones{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:12px}

/* 칸 하나 */
.stone{
  position:relative;background:#fff;border:3px solid var(--ink);border-radius:16px;
  padding:10px 8px 9px;text-align:center;cursor:pointer;
  box-shadow:0 4px 0 #E4D6EC;transition:transform .12s, box-shadow .12s;
}
.stone:hover,.stone:focus-visible{transform:translateY(-2px);box-shadow:0 6px 0 #E4D6EC;outline:none}
.stone .n{
  position:absolute;left:-5px;top:-9px;font-family:var(--round);font-size:13px;
  background:var(--lilac);color:#fff;border-radius:999px;padding:1px 8px;
}
.stone .face{font-family:var(--round);font-size:26px;line-height:1.15;margin:6px 0 3px;word-break:keep-all}
.stone .kind{font-size:11px;color:var(--lilac);font-family:var(--hand)}
.stone.done{background:#FFF3F8;border-color:var(--rose)}
.stone .stamp{
  position:absolute;right:-8px;bottom:-8px;width:40px;height:40px;
  opacity:0;transform:rotate(-18deg) scale(.4);transition:.25s;pointer-events:none;
}
.stone.done .stamp{opacity:1;transform:rotate(-14deg) scale(1)}
.stone.done .stamp svg *{stroke:var(--rose)}

/* 칸을 누르면 열리는 쪽지 */
dialog{
  border:3px solid var(--ink);border-radius:20px;padding:0;max-width:340px;width:88vw;
  box-shadow:0 10px 0 rgba(59,43,64,.15);background:#fff;
}
dialog::backdrop{background:rgba(59,43,64,.42)}
dialog .card{padding:20px 20px 18px;text-align:center}
dialog h3{font-family:var(--round);font-weight:400;font-size:26px;margin:2px 0 2px}
dialog .sub{font-family:var(--hand);color:var(--lilac);font-size:16px;margin:0 0 14px}
dialog .pic{width:120px;margin:0 auto 12px}
dialog .pic svg{width:100%;height:auto}
.btn{
  display:block;width:100%;font-family:var(--round);font-size:19px;padding:12px;
  border-radius:14px;border:3px solid var(--ink);margin-top:9px;cursor:pointer;background:#fff;
}
.btn.go{background:var(--gold);color:#fff;border-color:#C9862A;box-shadow:0 4px 0 #C9862A}
.btn.stampit{background:var(--rose);color:#fff;border-color:#B93C6E;box-shadow:0 4px 0 #B93C6E}
.btn.off{background:#F3EDF7;color:#9A8AA6;box-shadow:0 4px 0 #E0D6E8}
.btn.close{border-color:var(--line);color:var(--lilac);font-size:16px;padding:9px}

/* 안내 */
#guide{max-width:520px}
#guide .card{text-align:left}
#guide h3{text-align:center}
#guide ol{padding-left:20px;margin:0 0 12px;line-height:1.7;font-size:15px}
#guide h4{font-family:var(--round);font-weight:400;color:var(--rose);margin:14px 0 4px;font-size:17px}
#guide p{margin:0 0 8px;line-height:1.65;font-size:15px;color:#5C4A63}

.savewarn{
  display:none;margin:14px auto 0;max-width:560px;text-align:center;font-size:14px;
  color:#9A3B57;background:#FFECF2;border:2px solid #F3B9CC;border-radius:12px;padding:9px 12px;
}
.savewarn.on{display:block}

/* 색종이 */
.confetti{position:fixed;inset:0;pointer-events:none;z-index:9}
.confetti i{position:absolute;width:9px;height:14px;border-radius:2px;animation:fall 2.6s linear forwards}
@keyframes fall{
  0%{transform:translateY(-14vh) rotate(0);opacity:1}
  100%{transform:translateY(105vh) rotate(680deg);opacity:0}
}
@media (hover:none){.stone:hover{transform:none}}
@media print{.guidebtn,.confetti{display:none}}
"""


# 지도의 동작. f-string 밖에 둔다 — 안에 두면 자바스크립트의 { } 가
# 전부 치환 자리로 읽혀서 빌드가 죽는다.
JS = r"""
/* 저장이 막힌 브라우저가 있다. 읽기·쓰기를 전부 감싸고, 안 되면 화면에 알린다. */
let storageOK = true;
function readStore(){
  try{ return JSON.parse(localStorage.getItem(KEY) || "null"); }
  catch(e){ storageOK = false; return null; }
}
function writeStore(o){
  try{ localStorage.setItem(KEY, JSON.stringify(o)); }
  catch(e){ storageOK = false; document.getElementById("savewarn").classList.add("on"); }
}

/* units.json 이 나중에 늘어나도, 아이가 일부러 뺀 도장은 되살리지 않는다.
   그래서 '그때 본 씨앗 목록' 을 같이 저장해 두고 새로 늘어난 것만 더한다. */
let done = new Set();
(function load(){
  const o = readStore();
  if(!o){ done = new Set(SEED); }
  else{
    done = new Set(o.done || []);
    const seen = new Set(o.seed || []);
    SEED.forEach(n => { if(!seen.has(n)) done.add(n); });
  }
  if(!storageOK) document.getElementById("savewarn").classList.add("on");
})();
function save(){ writeStore({done:[...done], seed:SEED}); }

function paint(){
  document.querySelectorAll(".stone").forEach(el=>{
    el.classList.toggle("done", done.has(+el.dataset.n));
  });
  const pct = TOTAL ? Math.round(done.size/TOTAL*100) : 0;
  document.getElementById("fill").style.width = pct + "%";
  document.getElementById("cap").textContent =
    done.size ? `${done.size}장 완성 · 앞으로 ${TOTAL-done.size}장` : "첫 장을 열어 볼까요?";
}

/* ── 칸 누르면 쪽지 ── */
const dlg = document.getElementById("sheetDlg");
let cur = null;
document.querySelectorAll(".stone").forEach(el=>{
  el.addEventListener("click", ()=>{
    cur = +el.dataset.n;
    const m = META[cur];
    document.getElementById("dPic").innerHTML = PICS[m.art] || "";
    document.getElementById("dFace").textContent = m.face;
    document.getElementById("dSub").textContent = `${m.zone} · ${m.kind}`;
    document.getElementById("dGo").href = `print/unit${String(cur).padStart(2,"0")}.html`;
    const b = document.getElementById("dStamp");
    const has = done.has(cur);
    b.textContent = has ? "도장 빼기" : "도장 쾅! 찍기";
    b.className = "btn " + (has ? "off" : "stampit");
    dlg.showModal();
  });
});
document.getElementById("dClose").onclick = ()=> dlg.close();
document.getElementById("dStamp").onclick = ()=>{
  const zoneBefore = zoneDone(META[cur].zone);
  done.has(cur) ? done.delete(cur) : done.add(cur);
  save(); paint(); dlg.close();
  if(!zoneBefore && zoneDone(META[cur].zone)) confetti();
};

function zoneDone(zone){
  const ns = Object.keys(META).filter(n=>META[n].zone===zone).map(Number);
  return ns.length>0 && ns.every(n=>done.has(n));
}

/* ── 안내 ── */
const g = document.getElementById("guide");
document.getElementById("openGuide").onclick = ()=> g.showModal();
document.getElementById("gClose").onclick = ()=> g.close();

/* ── 마당을 다 채우면 색종이 ── */
function confetti(){
  const box = document.getElementById("confetti");
  const colors = ["#E0508A","#E8A33D","#A98BD0","#7FC8E8","#F7B7D2"];
  for(let i=0;i<70;i++){
    const s = document.createElement("i");
    s.style.left = Math.random()*100 + "vw";
    s.style.background = colors[i % colors.length];
    s.style.animationDelay = (Math.random()*.5) + "s";
    box.appendChild(s);
    setTimeout(()=> s.remove(), 3400);
  }
}

paint();
"""


def face(u):
    """칸에 크게 보이는 글자."""
    k = u["kind"]
    if k in ("jamo", "table"):
        return " ".join(u["chars"])
    if k == "word":
        return u["word"]
    return u["sentence"].rstrip(".!?")


KIND_LABEL = {"jamo": "쓰는 순서", "table": "글자 만들기",
              "word": "낱말 쓰기", "sentence": "문장 쓰기"}


def build(data=None):
    if data is None:
        data = json.load(open(os.path.join(ROOT, "units.json"), encoding="utf-8"))

    zones, seed, total, meta = [], [], 0, {}
    for g in data["groups"]:
        stones = []
        first = min(u['n'] for u in g['units'])
        for u in g["units"]:
            n = u["n"]
            total += 1
            if u.get("status") == "done":
                seed.append(n)
            meta[n] = {
                "face": face(u),
                "kind": KIND_LABEL[u["kind"]],
                "art": u.get("art", ""),
                "zone": g["theme"],
            }
            stones.append(
                f'<button class="stone" data-n="{n}">'
                f'<span class="n">{n}</span>'
                f'<div class="face">{sheet.esc(face(u))}</div>'
                f'<div class="kind">{KIND_LABEL[u["kind"]]}</div>'
                f'<span class="stamp">{art.svg("왕관")}</span>'
                f'</button>')
        zones.append(f"""
    <section class="zone" data-zone="{sheet.esc(g['theme'])}">
      <h2><span class="ico">{g['ico']}</span>{sheet.esc(g['theme'])}
          <a class="cnt" href="print/madang{first:02d}.html">{len(g['units'])}장 통째로 인쇄</a></h2>
      <p class="note">{sheet.esc(g['note'])}</p>
      <div class="stones">{''.join(stones)}</div>
    </section>""")

    # 쪽지에 보여 줄 그림들만 모아 둔다 (전부 넣으면 파일이 커진다)
    pics = {name: art.svg(name) for name in
            sorted({m["art"] for m in meta.values() if m["art"]})}

    consts = (f'const META = {json.dumps(meta, ensure_ascii=False)};\n'
              f'const PICS = {json.dumps(pics, ensure_ascii=False)};\n'
              f'const SEED = {json.dumps(sorted(seed))};\n'
              f'const TOTAL = {total};\n'
              'const KEY = "kor-study-stamps-v1";\n')

    html = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{sheet.esc(data['course'])}</title>
<link rel="stylesheet" href="assets/fonts.css">
<style>{sheet.CSS}{CSS}</style>
</head><body>
<div class="wrap">
  <header class="top">
    <button class="guidebtn" id="openGuide">📋 안내 보기</button>
    <h1>{sheet.esc(data['course'])}</h1>
    <p>{sheet.esc(data['subtitle'])}</p>
  </header>

  <div class="progress">
    <div class="bar"><i id="fill"></i></div>
    <div class="cap" id="cap"></div>
  </div>
  <div class="savewarn" id="savewarn">
    이 브라우저는 도장을 저장하지 못합니다. 시크릿 모드를 끄거나 다른 브라우저로 열어 주세요.
  </div>

  {''.join(zones)}
</div>

<dialog id="sheetDlg"><div class="card">
  <div class="pic" id="dPic"></div>
  <h3 id="dFace"></h3>
  <p class="sub" id="dSub"></p>
  <a class="btn go" id="dGo" href="#">학습지 열기</a>
  <button class="btn stampit" id="dStamp">도장 쾅! 찍기</button>
  <button class="btn close" id="dClose">닫기</button>
</div></dialog>

<dialog id="guide"><div class="card">
  <h3>이렇게 쓰세요</h3>
  <h4>하루 {data.get('minutes', 15)}분</h4>
  <ol>
    <li>칸을 눌러 <b>학습지를 열고 인쇄</b>합니다 (A4 한 장)</li>
    <li>아이가 <b>색칠부터</b> 합니다 — 연필을 오래 쥐는 연습입니다</li>
    <li>회색 글자를 따라 쓰고, 빈 칸에 혼자 써 봅니다</li>
    <li>다 하면 이 화면에서 <b>도장을 찍습니다</b></li>
  </ol>
  <h4>순서를 지켜 주세요</h4>
  <p>모음 → 자음 → 글자 만들기 → 낱말 → 문장 순서입니다.
     특히 <b>「글자 만들기」 마당이 고비</b>입니다. 못 읽는 칸이 많아도
     다음 마당으로 넘기지 말고 며칠 더 하세요.</p>
  <h4>학습지 맨 아래 점선 상자</h4>
  <p>부모용입니다. 아이가 틀렸을 때 <b>뭐라고 말해 줄지</b>를 그대로 읽으면 되게 적어 두었습니다.</p>
  <h4>도장은 이 기기에만 저장됩니다</h4>
  <p>다른 기기와 자동으로 맞춰지지 않습니다. 옮기려면 <a href="list.html">부모용 목록</a>에서
     진도를 복사해 <code>units.json</code> 에 옮겨 적으세요.</p>
  <button class="btn close" id="gClose">닫기</button>
</div></dialog>

<div class="confetti" id="confetti"></div>

<script>
{consts}{JS}</script>
</body></html>"""

    path = os.path.join(ROOT, "index.html")
    open(path, "w", encoding="utf-8").write(html)
    print(f"지도 → index.html ({total}장)")
    return path


if __name__ == "__main__":
    build()
