#!/usr/bin/env python3
"""units.json → list.html (부모용 목록).

지도(index.html)는 아이 화면이라 진도표를 넣지 않았다. 날짜·상태·필터처럼
'관리하는 것' 은 전부 이쪽에 둔다.

여기서만 할 수 있는 일이 하나 있다 — **진도 복사하기.** 기기에 저장된
도장을 units.json 에 옮겨 적을 수 있게 통째로 뽑아 준다. 이게 유일한
기기 간 동기화 수단이다.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import sheet   # noqa: E402
from build_map import KIND_LABEL, face  # noqa: E402

CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:var(--serif);color:var(--ink);background:#FBF7FD}
a{color:var(--rose)}
.wrap{max-width:900px;margin:0 auto;padding:24px 16px 60px}
h1{font-family:var(--round);font-weight:400;font-size:30px;margin:0;color:var(--ink)}
.lede{font-family:var(--hand);font-size:17px;color:var(--lilac);margin:4px 0 18px}
.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
.tools button{
  font-family:var(--round);font-size:15px;padding:8px 15px;border-radius:999px;
  border:2.5px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;
}
.tools button.on{background:var(--rose);border-color:#B93C6E;color:#fff}
.tools .sp{margin-left:auto}
table{width:100%;border-collapse:collapse;background:#fff;border:2.5px solid var(--ink);border-radius:12px;overflow:hidden}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid var(--line);font-size:14px}
th{background:#F7EFFA;font-family:var(--round);font-weight:400;color:#6B5675}
tr:last-child td{border-bottom:none}
td.n{width:44px;color:var(--lilac);font-family:var(--round)}
td.face{font-family:var(--round);font-size:18px}
td.zone{color:#7C6A86;font-size:13px}
.pill{font-size:12px;padding:2px 9px;border-radius:999px;border:1.5px solid}
.pill.done{background:#FFF0F6;border-color:var(--rose);color:var(--rose)}
.pill.todo{background:#F5F2F8;border-color:var(--line);color:#9A8AA6}
tr.hide{display:none}
.out{
  width:100%;min-height:120px;margin-top:14px;font-family:ui-monospace,monospace;
  font-size:13px;padding:11px;border:2px solid var(--line);border-radius:10px;display:none;
}
.out.on{display:block}
.tip{font-size:13px;color:#7C6A86;line-height:1.7;margin-top:18px;
     border-left:4px solid var(--lilac);padding-left:12px}
"""


def build(data=None):
    if data is None:
        data = json.load(open(os.path.join(ROOT, "units.json"), encoding="utf-8"))

    rows, seed, total = [], [], 0
    for g in data["groups"]:
        for u in g["units"]:
            n = u["n"]
            total += 1
            if u.get("status") == "done":
                seed.append(n)
            rows.append(
                f'<tr data-n="{n}">'
                f'<td class="n">{n}</td>'
                f'<td class="face">{sheet.esc(face(u))}</td>'
                f'<td class="zone">{sheet.esc(g["theme"])} · {KIND_LABEL[u["kind"]]}</td>'
                f'<td><span class="pill todo">아직</span></td>'
                f'<td><a href="print/unit{n:02d}.html">학습지</a></td>'
                f'</tr>')

    html = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{sheet.esc(data['course'])} · 부모용 목록</title>
<link rel="stylesheet" href="assets/fonts.css">
<style>{sheet.CSS}{CSS}</style>
</head><body><div class="wrap">
  <h1>부모용 목록</h1>
  <p class="lede">{sheet.esc(data['course'])} · 전체 {total}장 ·
     <a href="index.html">아이 화면(지도)으로</a></p>

  <div class="tools">
    <button data-f="all" class="on">전체</button>
    <button data-f="done">한 것</button>
    <button data-f="todo">안 한 것</button>
    <span class="sp"></span>
    <button id="copy">진도 복사하기</button>
  </div>

  <table>
    <thead><tr><th></th><th>내용</th><th>마당</th><th>상태</th><th>인쇄</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>

  <textarea class="out" id="out" readonly></textarea>

  <p class="tip">
    도장은 <b>이 브라우저에만</b> 저장됩니다. 다른 기기로 옮기려면
    「진도 복사하기」로 번호를 뽑아 <code>units.json</code> 의 해당 유닛을
    <code>"status": "done"</code> 으로 고치고 <code>python3 tools/build.py</code> 를 돌리세요.
    그러면 어느 기기에서 열어도 도장이 찍혀 있습니다.
  </p>
</div>

<script>
const SEED = {json.dumps(sorted(seed))};
const KEY = "kor-study-stamps-v1";

let done;
try{{
  const o = JSON.parse(localStorage.getItem(KEY) || "null");
  if(!o) done = new Set(SEED);
  else{{
    done = new Set(o.done || []);
    const seen = new Set(o.seed || []);
    SEED.forEach(n => {{ if(!seen.has(n)) done.add(n); }});
  }}
}}catch(e){{ done = new Set(SEED); }}

document.querySelectorAll("tbody tr").forEach(tr=>{{
  const on = done.has(+tr.dataset.n);
  const p = tr.querySelector(".pill");
  p.className = "pill " + (on ? "done" : "todo");
  p.textContent = on ? "했어요" : "아직";
  tr.dataset.state = on ? "done" : "todo";
}});

document.querySelectorAll("[data-f]").forEach(b=>{{
  b.onclick = ()=>{{
    document.querySelectorAll("[data-f]").forEach(x=>x.classList.remove("on"));
    b.classList.add("on");
    const f = b.dataset.f;
    document.querySelectorAll("tbody tr").forEach(tr=>{{
      tr.classList.toggle("hide", f !== "all" && tr.dataset.state !== f);
    }});
  }};
}});

document.getElementById("copy").onclick = ()=>{{
  const ns = [...done].sort((a,b)=>a-b);
  const out = document.getElementById("out");
  out.value = ns.length
    ? `units.json 에서 아래 번호의 유닛을 "status": "done" 으로 고치세요.\\n\\n`
      + ns.join(", ")
    : "아직 찍은 도장이 없습니다.";
  out.classList.add("on");
  out.select();
}};
</script>
</body></html>"""

    path = os.path.join(ROOT, "list.html")
    open(path, "w", encoding="utf-8").write(html)
    print(f"목록 → list.html ({total}장)")
    return path


if __name__ == "__main__":
    build()
