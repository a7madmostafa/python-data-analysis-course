"""Build a lesson page, website/site/<slug>/index.html, from its content in website/build/pages/<slug>.html.

The lessons from Matplotlib on are written as content fragments: the shell (head, theme, top bar, hero with the
notebook buttons, table of contents, pager, shared widget helpers) is the same on every page and lives here and in
pages/_shell.css, the same look as the hand-written pages of lessons 1-8.

A fragment starts with a JSON meta block, then the <section class="sec"> blocks, then optionally one <style> and
one <script>. "primary": [label, url] replaces the notebook button (for a lesson without a notebook), and
"no_rendered_notebook": true drops the "show the notebook here" button. The script runs inside the page's IIFE, after the helpers ($, $$, cssv, head, setup, text, axes,
onRedraw, PAL, nf) and must define `function main() {...}`, called once the page has loaded.

    <!--meta {"title": "Matplotlib", "h1": "Matplotlib", "title_ar": "Matplotlib", "lead": "...",
              "description": "...", "next_soon": "Seaborn"} -->

The prev / next links follow the lesson order in course.json; when the next lesson isn't in course.json yet,
the pager shows `next_soon` greyed out.

    python website/build/lesson_page.py matplotlib
    python website/build/lesson_page.py --all          # every lesson that has a fragment
"""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
COURSE = json.loads((ROOT / "website" / "build" / "course.json").read_text(encoding="utf-8"))
PAGES = ROOT / "website" / "build" / "pages"
BASE = COURSE["site_base"]
REPO = "https://github.com/a7madmostafa/python-data-analysis-course/blob/main/"
DATASET = "https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales"


def notebook_url(lesson):
    """Kaggle when the lesson is on Kaggle, otherwise the notebook on GitHub (saved with its outputs)."""
    if lesson.get("kaggle_slug"):
        return f"https://www.kaggle.com/code/{COURSE['kaggle_user']}/{lesson['kaggle_slug']}", "📓 افتح النوت بوك على Kaggle"
    return REPO + lesson["notebook"], "📓 النوت بوك على GitHub"


HELPERS = r"""
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const nf = v => Math.round(v).toLocaleString("en");
function head(title, hint, badge = "جرّب بنفسك") { return `<div class="widget-head"><span class="badge">${badge}</span><h3>${title}</h3></div><p class="hint">${hint}</p>`; }
function setup(cv, h) {
  const dpr = window.devicePixelRatio || 1, w = cv.clientWidth || 300;
  cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); cv.style.height = h + "px";
  const ctx = cv.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.direction = "ltr";
  return { ctx, w, h };
}
const redrawers = []; const onRedraw = f => redrawers.push(f);
let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => redrawers.forEach(f => f()), 120); });
const PAL = () => [cssv("--c1"), cssv("--c3"), cssv("--bad"), cssv("--c2"), cssv("--c4"), cssv("--muted")];
function text(ctx, t, x, y, { col = "--muted", font = "11px Inter, sans-serif", align = "left", base = "alphabetic" } = {}) {
  ctx.fillStyle = col.startsWith("--") ? cssv(col) : col; ctx.font = font; ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(t, x, y);
}
function axes(ctx, x0, y0, x1, y1) { ctx.strokeStyle = cssv("--line"); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0, y1); ctx.lineTo(x1, y1); ctx.stroke(); }
function segPick(root, attr, onPick) {
  $$(`[${attr}]`, root).forEach(b => b.onclick = () => { $$(`[${attr}]`, root).forEach(x => x.setAttribute("aria-pressed", x === b)); onPick(b.getAttribute(attr)); });
}
"""

CHROME = r"""
function chrome() {
  $$(".codetabs").forEach(box => $$(".seg button", box).forEach(b => b.onclick = () => {
    $$(".seg button", box).forEach(x => x.setAttribute("aria-pressed", x === b));
    $$("pre", box).forEach(p => p.hidden = p.dataset.lib !== b.dataset.lib);
  }));
  const toc = $("#tocList"), links = {};
  $$("section.sec").forEach(sec => {
    const li = document.createElement("li"), a = document.createElement("a");
    a.href = "#" + sec.id; a.textContent = $("h2", sec).textContent.replace(/^\d+/, "").trim();
    li.appendChild(a); toc.appendChild(li); links[sec.id] = a;
  });
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { Object.values(links).forEach(a => a.classList.remove("active")); links[e.target.id].classList.add("active"); } }), { rootMargin: "-30% 0px -60% 0px" });
  $$("section.sec").forEach(s => io.observe(s));
  window.addEventListener("scroll", () => { const h = document.documentElement; $("#progress").style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight) * 100) + "%"; }, { passive: true });
  new MutationObserver(() => redrawers.forEach(f => f())).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => redrawers.forEach(f => f()));
}
"""


def lesson_link(slug):
    return f"{BASE}/{slug}/"


def build(slug):
    src = (PAGES / f"{slug}.html").read_text(encoding="utf-8")
    m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", src, re.S)
    meta = json.loads(m.group(1))
    body = src[m.end():]
    style = "".join(re.findall(r"<style>(.*?)</style>", body, re.S))
    script = "".join(re.findall(r"<script>(.*?)</script>", body, re.S))
    body = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", body, flags=re.S).strip()

    lesson = COURSE["lessons"][slug]
    order = list(COURSE["lessons"])
    i = order.index(slug)
    prev = order[i - 1] if i > 0 else None
    nxt = order[i + 1] if i + 1 < len(order) else None
    t_ar = lambda s: COURSE["lessons"][s]["title_ar"]
    if meta.get("primary"):          # a lesson without a notebook (Streamlit, the projects) names its own main link
        nb_label, nb_url = meta["primary"]
    else:
        nb_url, nb_label = notebook_url(lesson)
    title_ar = html.escape(lesson["title_ar"])

    top_prev = (f'<a class="iconbtn" href="{lesson_link(prev)}" aria-label="الدرس اللي فات: {html.escape(t_ar(prev))}" title="الدرس اللي فات: {html.escape(t_ar(prev))}">→</a>'
                if prev else '<span class="iconbtn off" aria-hidden="true">→</span>')
    top_next = (f'<a class="iconbtn" href="{lesson_link(nxt)}" aria-label="الدرس الجاي: {html.escape(t_ar(nxt))}" title="الدرس الجاي: {html.escape(t_ar(nxt))}">←</a>'
                if nxt else '<span class="iconbtn off" aria-hidden="true">←</span>')
    pg_prev = (f'<a class="pg" href="{lesson_link(prev)}"><span>→ الدرس اللي فات</span><b>{html.escape(t_ar(prev))}</b></a>'
               if prev else '<span class="pg off"><span>→ الدرس اللي فات</span><b>ده أول درس</b></span>')
    pg_next = (f'<a class="pg next" href="{lesson_link(nxt)}"><span>الدرس الجاي ←</span><b>{html.escape(t_ar(nxt))}</b></a>'
               if nxt else f'<span class="pg next off"><span>الدرس الجاي ←</span><b>{html.escape(meta.get("next_soon", "قريبًا"))}</b></span>')

    data_btn = (f'<a class="nb-btn" href="{meta["data_url"]}" target="_blank" rel="noopener">{meta.get("data_label", "🗂️ الداتا")}</a>'
                if meta.get("data_url") else f'<a class="nb-btn" href="{DATASET}" target="_blank" rel="noopener">🗂️ داتا NileCart على Kaggle</a>')
    has_nb = lesson.get("notebook") and not meta.get("no_rendered_notebook")
    buttons = (f'<a class="nb-btn primary" href="{nb_url}" target="_blank" rel="noopener">{nb_label}</a>'
               + ('<a class="nb-btn" href="notebook/">👀 اعرض النوت بوك هنا</a>' if has_nb else "")
               + "".join(f'<a class="nb-btn" href="{u}" target="_blank" rel="noopener">{l}</a>' for l, u in meta.get("extra_links", []))
               + data_btn)
    footer = meta.get("footer", "الداتا: NileCart، متجر وهمي في القاهرة، بالجنيه المصري.<br>\n      كل الأرقام في الدرس من نفس الداتا اللي في النوت بوك.")
    desc = html.escape(meta["description"])
    page = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta["title"])}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title_ar} · Zero Grad">
<meta property="og:description" content="{html.escape(meta.get("og_description", meta["description"]))}">
<meta property="og:image" content="https://zero-grad.com/assets/img/link-preview-zerograd-1200x630.png">
<meta property="og:url" content="https://zero-grad.com{lesson_link(slug)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://zero-grad.com{lesson_link(slug)}">
<link rel="icon" href="/assets/img/zero-grad-app-icon.svg" type="image/svg+xml">
<script src="/assets/js/theme.js"></script>
<link rel="apple-touch-icon" href="/assets/img/zero-grad-app-icon-512.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#f5f2ea" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141414" media="(prefers-color-scheme: dark)">
<script src="/assets/js/pwa.js" defer></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Noto+Sans+Arabic:wght@400;500;700&family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
{(PAGES / "_shell.css").read_text(encoding="utf-8")}{style.strip()}
</style>
</head>
<body>
<div id="progress"></div>
<header class="topbar">
  <div class="topbar-in">
    <nav class="crumbs" aria-label="أنت هنا"><a class="home" href="/">Zero Grad</a><span class="sep">›</span><a class="course" href="{BASE}/">كورس Data Analysis</a><span class="sep">›</span><span class="here">{title_ar}</span></nav>
    <div class="top-actions">
      {top_prev}{top_next}
      <button class="iconbtn" id="themeBtn" type="button" data-theme-toggle aria-label="تغيير الثيم" title="فاتح / غامق">◐</button>
    </div>
  </div>
</header>

<div class="wrap">
  <nav class="toc" aria-label="المحتوى"><ol id="tocList"></ol></nav>
  <main>
    <div class="hero">
      <div class="kicker">Zero Grad · كورس Data Analysis · {html.escape(meta.get("kicker", "Visualization"))}</div>
      <h1>{html.escape(meta["h1"])}</h1>
      <p class="lead">{meta["lead"]}</p>
      <div class="nb-links">
        {buttons}
      </div>
    </div>

{body}

    <nav class="pager" aria-label="التنقل بين الدروس">{pg_prev}<a class="pg all" href="{BASE}/"><span>كورس Data Analysis</span><b>كل الدروس</b></a>{pg_next}</nav>

    <footer>
      {footer}
    </footer>
  </main>
</div>

{"".join(f'<script src="{s}"></script>{chr(10)}' for s in meta.get("scripts", []))}<script>
(() => {{
"use strict";
{HELPERS}
{CHROME}
{script.strip()}

window.addEventListener("DOMContentLoaded", () => {{ chrome(); {"main();" if "function main" in script else ""} }});
}})();
</script>
</body>
</html>
"""
    out = ROOT / "website" / "site" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="")
    print("wrote", out, f"({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    slugs = [p.stem for p in sorted(PAGES.glob("*.html")) if not p.stem.startswith("_")] if "--all" in sys.argv else sys.argv[1:]
    for s in slugs:
        build(s)
