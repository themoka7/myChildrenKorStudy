#!/usr/bin/env python3
"""Chromium 으로 HTML 을 실제로 렌더링한다.

인쇄물 저장소라서 **부모가 브라우저에서 인쇄 버튼을 눌렀을 때** 나오는 것이
정답이다. 그래서 검증도 같은 엔진(Chromium)으로 한다 — weasyprint 같은 다른
엔진으로 재면 실제 인쇄와 어긋난다.

  pdf_pages(html_path)   → 인쇄하면 몇 쪽인지. A4 1쪽을 넘겼는지 잡는 데 쓴다
  screenshot(html, out)  → 화면 그대로 PNG. 도안·지도를 눈으로 볼 때 쓴다
"""
import os
import shutil
import sys
import tempfile

# 이 컨테이너의 Playwright 는 브라우저를 자기 캐시에서 못 찾는다.
# PLAYWRIGHT_BROWSERS_PATH 아래에 미리 깔린 것을 직접 짚어 준다.
_CANDIDATES = [
    os.environ.get("CHROMIUM_PATH", ""),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
]


def chromium_path():
    for p in _CANDIDATES:
        if p and os.path.exists(p):
            return p
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for dirpath, _, files in os.walk(root):
        if "chrome" in files and dirpath.endswith("chrome-linux"):
            return os.path.join(dirpath, "chrome")
    for name in ("chromium", "chromium-browser", "google-chrome"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("Chromium 을 못 찾았습니다. CHROMIUM_PATH 환경변수로 짚어 주세요.")


def _browser(p):
    return p.chromium.launch(executable_path=chromium_path(),
                             args=["--no-sandbox", "--font-render-hinting=none"])


def _load(page, html, base_url=None):
    """문자열이면 임시 파일로 떨구고, 경로면 그대로 연다.

    set_content() 를 쓰면 base URL 이 없어서 상대경로 CSS·폰트가 안 붙는다.
    인쇄물은 폰트가 안 붙으면 레이아웃이 통째로 달라지므로 file:// 로 연다.
    """
    if os.path.exists(html):
        page.goto("file://" + os.path.abspath(html))
    else:
        d = base_url or tempfile.mkdtemp()
        f = os.path.join(d, "_render.html")
        open(f, "w", encoding="utf-8").write(html)
        page.goto("file://" + f)
    page.wait_for_load_state("networkidle")
    try:
        page.evaluate("document.fonts && document.fonts.ready")
    except Exception:
        pass


def pdf_bytes(html_path):
    """A4 로 인쇄한 PDF 바이트를 준다. 여백은 CSS 의 @page 가 정한다."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = _browser(p)
        page = b.new_page()
        _load(page, html_path)
        data = page.pdf(format="A4", print_background=True,
                        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                        prefer_css_page_size=True)
        b.close()
    return data


def pdf_pages(html_path):
    """인쇄했을 때의 쪽 수. 1쪽짜리 학습지가 2쪽이 되면 여기서 잡힌다."""
    import pymupdf
    doc = pymupdf.open(stream=pdf_bytes(html_path), filetype="pdf")
    try:
        return doc.page_count
    finally:
        doc.close()


def pdf_png(html_path, out, dpi=110):
    """인쇄 PDF 를 쪽마다 PNG 로. 눈으로 최종 확인할 때."""
    import pymupdf
    doc = pymupdf.open(stream=pdf_bytes(html_path), filetype="pdf")
    paths = []
    try:
        for i, page in enumerate(doc):
            path = out if doc.page_count == 1 else f"{out[:-4]}-{i + 1}.png"
            page.get_pixmap(dpi=dpi).save(path)
            paths.append(path)
    finally:
        doc.close()
    return paths


def screenshot(html, out, width=1200, height=900, full_page=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = _browser(p)
        page = b.new_page(viewport={"width": width, "height": height})
        _load(page, html)
        page.screenshot(path=out, full_page=full_page)
        b.close()
    return out
