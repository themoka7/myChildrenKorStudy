#!/usr/bin/env python3
"""44장을 통째로 담은 **파일 하나** 를 만든다 → app.html

왜 필요한가 — GitHub Pages 는 저장소를 공개로 바꾸고 설정에서 한 번 켜야
동작한다. 그 전까지는 주소로 열 수가 없다. 그런데 부모가 실제로 원하는 건
**휴대폰에서 열어서 프린터로 보내는 것** 하나다.

그래서 지도 + 학습지 44장 + 글꼴을 파일 하나에 다 넣었다. 이 파일만 있으면
인터넷 없이도, 저장소 없이도, 열어서 인쇄까지 된다. 메일로 보내도 되고
클라우드에 올려도 된다.

인쇄는 화면에 띄운 그 한 장만 나간다 (`@media print`). 마당 단추를 쓰면
그 마당 전체가 나간다.

    python3 tools/build_app.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import art          # noqa: E402
import sheet        # noqa: E402
from build_map import KIND_LABEL, face  # noqa: E402

# 저장소의 팔레트를 그대로 쓴다. 학습지·지도·이 앱이 한 덩어리로 보여야 한다.
# 다만 종이(.page)만은 **어느 테마에서도 흰 종이**다 — 인쇄 미리보기니까.
CSS = """
:root{
  --bg:#FFF9FC; --bg2:#FFFFFF; --fg:#3B2B40; --dim:#7C6A86;
  --edge:#E7DCEE; --shadow:rgba(59,43,64,.13);
}
:root:not([data-theme="light"]){
  @media (prefers-color-scheme: dark){
    --bg:#221A27; --bg2:#2C2233; --fg:#F3ECF6; --dim:#B6A6C0;
    --edge:#3E3145; --shadow:rgba(0,0,0,.45);
  }
}
:root[data-theme="dark"]{
  --bg:#221A27; --bg2:#2C2233; --fg:#F3ECF6; --dim:#B6A6C0;
  --edge:#3E3145; --shadow:rgba(0,0,0,.45);
}

*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg);color:var(--fg);
  font-family:var(--serif);
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
}
button{font:inherit;color:inherit;cursor:pointer}
:focus-visible{outline:3px solid var(--rose);outline-offset:2px;border-radius:4px}

.shell{max-width:1080px;margin:0 auto;padding:20px 16px 64px}

/* ── 머리 ─────────────────────────────────────── */
.masthead{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding:14px 0 4px}
.masthead h1{
  font-family:var(--round);font-weight:400;letter-spacing:-.5px;
  font-size:clamp(28px,5.4vw,40px);margin:0;color:var(--rose);
}
.masthead .tagline{font-family:var(--hand);font-size:18px;color:var(--dim)}
.masthead .guide{
  margin-left:auto;font-family:var(--round);font-size:15px;
  background:var(--bg2);border:2.5px solid var(--edge);color:var(--dim);
  border-radius:999px;padding:7px 16px;
}

.meter{margin:16px 0 4px;display:flex;align-items:center;gap:12px}
.meter .track{
  flex:1;height:18px;border:2.5px solid var(--fg);border-radius:999px;
  background:var(--bg2);overflow:hidden;
}
.meter .track i{display:block;height:100%;width:0;background:linear-gradient(90deg,#F7B7D2,var(--rose));transition:width .45s}
.meter .count{font-family:var(--round);font-size:16px;white-space:nowrap;font-variant-numeric:tabular-nums}

.warn{
  display:none;margin:12px 0 0;font-size:14px;color:#9A3B57;
  background:#FFECF2;border:2px solid #F3B9CC;border-radius:12px;padding:9px 13px;
}
.warn.on{display:block}

/* ── 마당 ─────────────────────────────────────── */
.zone{margin-top:32px}
.zone-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.zone-head h2{
  font-family:var(--round);font-weight:400;font-size:21px;margin:0;
  display:flex;align-items:center;gap:9px;
}
.zone-head .ico{font-size:24px}
.zone-head .bundle{
  margin-left:auto;font-family:var(--round);font-size:14px;
  background:transparent;border:2px solid var(--edge);color:var(--dim);
  border-radius:999px;padding:4px 13px;
}
.zone-note{font-family:var(--hand);font-size:16px;color:var(--dim);margin:5px 0 12px;max-width:62ch}

.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:11px}
.tile{
  position:relative;background:var(--bg2);border:3px solid var(--fg);border-radius:15px;
  padding:11px 7px 9px;text-align:center;
  box-shadow:0 4px 0 var(--shadow);transition:transform .12s,box-shadow .12s;
}
.tile:hover{transform:translateY(-2px);box-shadow:0 6px 0 var(--shadow)}
@media (hover:none){.tile:hover{transform:none;box-shadow:0 4px 0 var(--shadow)}}
.tile .num{
  position:absolute;left:-4px;top:-9px;font-family:var(--round);font-size:12px;
  background:var(--lilac);color:#fff;border-radius:999px;padding:1px 8px;
}
.tile .what{font-family:var(--round);font-size:24px;line-height:1.15;margin:5px 0 3px;word-break:keep-all}
.tile .how{font-family:var(--hand);font-size:12px;color:var(--dim)}
.tile.done{border-color:var(--rose)}
.tile .mark{
  position:absolute;right:-7px;bottom:-7px;width:36px;height:36px;
  opacity:0;transform:rotate(-16deg) scale(.4);transition:.22s;pointer-events:none;
}
.tile.done .mark{opacity:1;transform:rotate(-13deg) scale(1)}
.tile.done .mark svg *{stroke:var(--rose)}

/* ── 학습지 보기 ─────────────────────────────── */
.viewer{
  position:fixed;inset:0;z-index:20;background:var(--bg);
  display:none;flex-direction:column;
}
.viewer.on{display:flex}
.bar{
  display:flex;align-items:center;gap:8px;padding:9px 12px;
  background:var(--bg2);border-bottom:2px solid var(--edge);flex:none;flex-wrap:wrap;
}
.bar .who{font-family:var(--round);font-size:17px;margin-right:auto}
.bar .who small{font-family:var(--hand);color:var(--dim);font-size:14px;margin-left:8px}
.bar button{
  font-family:var(--round);font-size:15px;border-radius:11px;padding:8px 15px;
  border:2.5px solid var(--fg);background:var(--bg2);
}
.bar button.print{background:var(--gold);color:#fff;border-color:#C9862A}
.bar button.stamp{background:var(--rose);color:#fff;border-color:#B93C6E}
.bar button.stamp.off{background:transparent;color:var(--dim);border-color:var(--edge)}
.bar button.step{padding:8px 13px}
.bar button[disabled]{opacity:.35;cursor:default}

.stage{flex:1;overflow:auto;padding:16px;display:grid;place-items:start center;background:var(--bg)}
.paper{
  transform-origin:top center;
  filter:drop-shadow(0 6px 18px var(--shadow));
}
/* 종이는 어느 테마에서도 흰 종이다. 인쇄될 물건의 미리보기니까. */
.paper .page{background:#fff;color:#3B2B40}

/* ── 안내 ─────────────────────────────────────── */
dialog{
  border:3px solid var(--fg);border-radius:18px;padding:0;max-width:540px;width:90vw;
  background:var(--bg2);color:var(--fg);
}
dialog::backdrop{background:rgba(34,26,39,.55)}
dialog .body{padding:22px}
dialog h3{font-family:var(--round);font-weight:400;font-size:24px;margin:0 0 14px;color:var(--rose)}
dialog h4{font-family:var(--round);font-weight:400;font-size:17px;margin:16px 0 5px}
dialog p,dialog li{line-height:1.65;font-size:15px;color:var(--fg);margin:0 0 8px}
dialog ol{padding-left:20px;margin:0}
dialog .close{
  width:100%;margin-top:16px;font-family:var(--round);font-size:16px;padding:10px;
  border-radius:12px;border:2.5px solid var(--edge);background:transparent;color:var(--dim);
}

/* ── 인쇄 ─────────────────────────────────────── */
@media print{
  .shell,.bar,dialog,.warn{display:none !important}
  .viewer{position:static;display:block !important}
  .stage{overflow:visible;padding:0;display:block;background:#fff}
  .paper{transform:none !important;filter:none}
  .paper .page{break-after:page}
  .paper .page:last-child{break-after:auto}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none !important;transition:none !important}
}

/* 색종이 */
.confetti{position:fixed;inset:0;pointer-events:none;z-index:30}
.confetti i{position:absolute;width:9px;height:14px;border-radius:2px;animation:fall 2.6s linear forwards}
@keyframes fall{
  0%{transform:translateY(-14vh) rotate(0);opacity:1}
  100%{transform:translateY(105vh) rotate(680deg);opacity:0}
}
@media print{.confetti{display:none}}
"""

JS = r"""
const KEY = "kor-study-stamps-v1";
let storageOK = true;

function load(){
  let o = null;
  try{ o = JSON.parse(localStorage.getItem(KEY) || "null"); }
  catch(e){ storageOK = false; }
  if(!o) return new Set(SEED);
  const d = new Set(o.done || []);
  const seen = new Set(o.seed || []);
  // units.json 이 나중에 늘어나도, 아이가 일부러 뺀 도장은 되살리지 않는다.
  SEED.forEach(n => { if(!seen.has(n)) d.add(n); });
  return d;
}
function save(){
  try{ localStorage.setItem(KEY, JSON.stringify({done:[...done], seed:SEED})); }
  catch(e){ storageOK = false; showWarn(); }
}
function showWarn(){ document.getElementById("warn").classList.add("on"); }

let done = load();
if(!storageOK) showWarn();

const $ = s => document.querySelector(s);
const paper = $("#paper");
const viewer = $("#viewer");
let cur = null;          // 지금 보고 있는 유닛 번호 (마당 인쇄 중이면 null)

function paint(){
  document.querySelectorAll(".tile").forEach(t=>{
    t.classList.toggle("done", done.has(+t.dataset.n));
  });
  $("#fill").style.width = (ORDER.length ? done.size/ORDER.length*100 : 0) + "%";
  $("#count").textContent = done.size
    ? `${done.size} / ${ORDER.length}장`
    : `${ORDER.length}장`;
}

/* ── 학습지 한 장 보기 ── */
function open(n){
  cur = n;
  paper.innerHTML = SHEETS[n];
  const m = META[n];
  $("#who").innerHTML = `${m.what}<small>${m.zone} · ${m.how}</small>`;
  const i = ORDER.indexOf(n);
  $("#prev").disabled = i <= 0;
  $("#next").disabled = i >= ORDER.length - 1;
  $("#stampBtn").hidden = false;
  syncStamp();
  viewer.classList.add("on");
  document.body.style.overflow = "hidden";
  fit();
}

/* ── 마당 통째로 ── */
function openZone(theme){
  cur = null;
  const ns = ORDER.filter(n => META[n].zone === theme);
  paper.innerHTML = ns.map(n => SHEETS[n]).join("");
  $("#who").innerHTML = `${theme}<small>${ns.length}장 · 통째로 인쇄</small>`;
  $("#prev").disabled = $("#next").disabled = true;
  $("#stampBtn").hidden = true;
  viewer.classList.add("on");
  document.body.style.overflow = "hidden";
  fit();
}

function close(){
  viewer.classList.remove("on");
  document.body.style.overflow = "";
  paper.innerHTML = "";
  cur = null;
}

/* A4(210mm) 를 화면 너비에 맞춰 줄인다. 인쇄할 때는 CSS 가 되돌린다. */
function fit(){
  const mm = 210 * 96 / 25.4;
  const avail = $("#stage").clientWidth - 32;
  const k = Math.min(1, avail / mm);
  paper.style.transform = `scale(${k})`;
  // scale 은 자리를 안 줄여서 아래가 텅 빈다. 높이를 손으로 맞춰 준다.
  const h = paper.getBoundingClientRect().height;
  paper.style.marginBottom = (h * (k - 1)) + "px";
}
addEventListener("resize", fit);

function syncStamp(){
  const b = $("#stampBtn");
  const has = done.has(cur);
  b.textContent = has ? "도장 뺐다 놓기" : "도장 쾅!";
  b.classList.toggle("off", has);
}

function zoneFull(theme){
  const ns = ORDER.filter(n => META[n].zone === theme);
  return ns.length > 0 && ns.every(n => done.has(n));
}

$("#stampBtn").onclick = ()=>{
  const theme = META[cur].zone;
  const before = zoneFull(theme);
  done.has(cur) ? done.delete(cur) : done.add(cur);
  save(); paint(); syncStamp();
  if(!before && zoneFull(theme)) confetti();
};
$("#printBtn").onclick = ()=> print();
$("#closeBtn").onclick = close;
$("#prev").onclick = ()=> open(ORDER[ORDER.indexOf(cur) - 1]);
$("#next").onclick = ()=> open(ORDER[ORDER.indexOf(cur) + 1]);

document.querySelectorAll(".tile").forEach(t=>{
  t.onclick = ()=> open(+t.dataset.n);
});
document.querySelectorAll(".bundle").forEach(b=>{
  b.onclick = ()=> openZone(b.dataset.zone);
});

addEventListener("keydown", e=>{
  if(!viewer.classList.contains("on")) return;
  if(e.key === "Escape") close();
  if(e.key === "ArrowLeft" && !$("#prev").disabled) $("#prev").click();
  if(e.key === "ArrowRight" && !$("#next").disabled) $("#next").click();
});

const g = $("#guide");
$("#guideBtn").onclick = ()=> g.showModal();
$("#guideClose").onclick = ()=> g.close();

function confetti(){
  const box = $("#confetti");
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


def build(data=None, out=None, artifact=False):
    """artifact=True 면 <html>·<head>·<body> 를 뺀 알맹이만 낸다.

    Artifact 로 발행하면 그쪽에서 껍데기를 씌우기 때문에, 껍데기를 같이
    넘기면 문서가 이중으로 감싸진다.
    """
    if data is None:
        data = json.load(open(os.path.join(ROOT, "units.json"), encoding="utf-8"))

    pairs = sorted(((u, g) for g in data["groups"] for u in g["units"]),
                   key=lambda p: p[0]["n"])
    total = len(pairs)

    sheets, meta, order, seed = {}, {}, [], []
    zones = []
    for g in data["groups"]:
        tiles = []
        for u in sorted(g["units"], key=lambda u: u["n"]):
            n = u["n"]
            order.append(n)
            if u.get("status") == "done":
                seed.append(n)
            sheets[n] = sheet.build_page(u, g, total)
            meta[n] = {"what": face(u), "how": KIND_LABEL[u["kind"]],
                       "zone": g["theme"]}
            tiles.append(
                f'<button class="tile" data-n="{n}">'
                f'<span class="num">{n}</span>'
                f'<div class="what">{sheet.esc(face(u))}</div>'
                f'<div class="how">{KIND_LABEL[u["kind"]]}</div>'
                f'<span class="mark">{art.svg("왕관")}</span></button>')
        zones.append(f"""
    <section class="zone">
      <div class="zone-head">
        <h2><span class="ico">{g['ico']}</span>{sheet.esc(g['theme'])}</h2>
        <button class="bundle" data-zone="{sheet.esc(g['theme'])}">{len(g['units'])}장 통째로 인쇄</button>
      </div>
      <p class="zone-note">{sheet.esc(g['note'])}</p>
      <div class="tiles">{''.join(tiles)}</div>
    </section>""")

    fonts = open(os.path.join(ROOT, "assets", "fonts.css"), encoding="utf-8").read()

    consts = (f"const SHEETS = {json.dumps(sheets, ensure_ascii=False)};\n"
              f"const META = {json.dumps(meta, ensure_ascii=False)};\n"
              f"const ORDER = {json.dumps(order)};\n"
              f"const SEED = {json.dumps(sorted(seed))};\n")

    shell_open = ("" if artifact else
                  '<!doctype html>\n<html lang="ko"><head>\n'
                  '<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width,initial-scale=1">\n')
    shell_close = "" if artifact else "</head><body>\n"

    html = f"""{shell_open}<title>{sheet.esc(data['course'])}</title>
<style>{fonts}</style>
<style>{sheet.CSS}{CSS}</style>
{shell_close}
<div class="shell">
  <header class="masthead">
    <h1>{sheet.esc(data['course'])}</h1>
    <span class="tagline">{sheet.esc(data['subtitle'])}</span>
    <button class="guide" id="guideBtn">📋 안내 보기</button>
  </header>

  <div class="meter">
    <div class="track"><i id="fill"></i></div>
    <span class="count" id="count"></span>
  </div>
  <p class="warn" id="warn">이 브라우저는 도장을 저장하지 못합니다.
     시크릿 모드를 끄거나 다른 브라우저로 열어 주세요. 학습지 인쇄는 그대로 됩니다.</p>

  {''.join(zones)}
</div>

<div class="viewer" id="viewer">
  <div class="bar">
    <span class="who" id="who"></span>
    <button class="step" id="prev" aria-label="앞 장">‹</button>
    <button class="step" id="next" aria-label="다음 장">›</button>
    <button class="stamp" id="stampBtn">도장 쾅!</button>
    <button class="print" id="printBtn">인쇄</button>
    <button id="closeBtn">닫기</button>
  </div>
  <div class="stage" id="stage"><div class="paper" id="paper"></div></div>
</div>

<dialog id="guide"><div class="body">
  <h3>이렇게 쓰세요</h3>
  <ol>
    <li>칸을 눌러 학습지를 열고 <b>인쇄</b>를 누릅니다 (A4 한 장)</li>
    <li>아이가 <b>색칠부터</b> 합니다 — 연필을 오래 쥐는 연습입니다</li>
    <li>회색 글자를 따라 쓰고, 빈 칸에 혼자 써 봅니다</li>
    <li>다 하면 <b>도장</b>을 찍습니다</li>
  </ol>
  <h4>순서를 지켜 주세요</h4>
  <p>모음 → 자음 → 글자 만들기 → 낱말 → 문장 순서입니다.
     특히 <b>「글자 만들기」 마당이 고비</b>입니다. 못 읽는 칸이 많아도
     다음 마당으로 넘기지 말고 며칠 더 하세요.</p>
  <h4>학습지 맨 아래 점선 상자</h4>
  <p>부모용입니다. 아이가 틀렸을 때 <b>뭐라고 말해 줄지</b>를
     그대로 읽으면 되게 적어 두었습니다.</p>
  <h4>「새 글자」 딱지</h4>
  <p>순서상 아직 안 가르친 글자가 필요한 장에 붙습니다.
     아이가 못 읽는 게 <b>당연하다</b>는 표시이니, 먼저 읽어 주세요.</p>
  <h4>도장은 이 기기에만 저장됩니다</h4>
  <p>다른 기기와 자동으로 맞춰지지 않습니다.</p>
  <button class="close" id="guideClose">닫기</button>
</div></dialog>

<div class="confetti" id="confetti"></div>

<script>
{consts}{JS}
</script>
{"" if artifact else "</body></html>"}"""

    out = out or os.path.join(ROOT, "app.html")
    open(out, "w", encoding="utf-8").write(html)
    kb = os.path.getsize(out) / 1024
    print(f"앱 → {os.path.relpath(out, ROOT)} ({kb:.0f}KB · 학습지 {total}장 내장)")
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", action="store_true",
                    help="Artifact 발행용 — 껍데기 태그를 빼고 낸다")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    build(out=a.out, artifact=a.artifact)
