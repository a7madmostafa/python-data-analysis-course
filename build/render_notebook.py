"""Render a lesson's executed notebook to site/<slug>/notebook/index.html, with a Zero Grad top bar.

    python build/render_notebook.py distribution
    python build/render_notebook.py --all
"""
from pathlib import Path
import json
import sys

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
COURSE = json.loads((ROOT / "build" / "course.json").read_text(encoding="utf-8"))

HEAD = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--zg-bg:#f5f2ea;--zg-ink:#1c1e22;--zg-muted:#5b616b;--zg-line:#ddd6c6;--zg-accent:#101f40;--zg-add:#2563eb}
body{background:var(--zg-bg)!important;font-family:Inter,system-ui,sans-serif}
.zg-bar{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--zg-bg) 90%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--zg-line);font-family:Inter,"Noto Sans Arabic",sans-serif}
.zg-in{max-width:1100px;margin:auto;padding:.55rem 16px;display:flex;gap:.75rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.zg-crumbs{display:flex;gap:.45rem;align-items:center;font-size:.9rem;direction:rtl}
.zg-crumbs a{color:var(--zg-muted);text-decoration:none}
.zg-crumbs .here{font-weight:700;color:var(--zg-ink)}
.zg-crumbs .sep{color:var(--zg-line)}
.zg-actions{display:flex;gap:.5rem}
.zg-btn{font-size:.85rem;border:1px solid var(--zg-line);background:#fffdf8;color:var(--zg-ink);border-radius:999px;padding:.3rem .9rem;text-decoration:none;white-space:nowrap}
.zg-btn.primary{background:var(--zg-accent);border-color:var(--zg-accent);color:#f5f2ea;font-weight:700}
main.jp-Notebook,body>.jp-Notebook{max-width:1100px;margin:1rem auto 4rem!important;background:#fffdf8;border:1px solid var(--zg-line);border-radius:14px;padding:1.5rem 1rem!important}
.jp-RenderedHTMLCommon{font-family:Inter,system-ui,sans-serif;font-size:15px;line-height:1.7}
.jp-RenderedHTMLCommon h1{color:var(--zg-accent)}
.jp-InputArea-editor,.jp-OutputArea-output pre{font-family:"JetBrains Mono",monospace!important}
img{max-width:100%;height:auto}
.jp-OutputArea-output{overflow-x:auto}
@media (max-width:640px){.jp-InputPrompt,.jp-OutputPrompt{display:none!important}}
</style>
"""

BAR = """
<header class="zg-bar"><div class="zg-in">
  <nav class="zg-crumbs" aria-label="أنت هنا"><a href="/">Zero Grad</a><span class="sep">›</span><a href="{base}/">كورس Data Analysis</a><span class="sep">›</span><a href="{base}/{slug}/">{title_ar}</a><span class="sep">›</span><span class="here">النوت بوك</span></nav>
  <div class="zg-actions"><a class="zg-btn" href="{base}/{slug}/">← الدرس</a><a class="zg-btn primary" href="{kaggle}" target="_blank" rel="noopener">Open in Kaggle</a></div>
</div></header>
"""


def kaggle_url(lesson):
    return f"https://www.kaggle.com/code/{COURSE['kaggle_user']}/{lesson['kaggle_slug']}"


def render(slug):
    lesson = COURSE["lessons"][slug]
    nb = nbformat.read(ROOT / lesson["notebook"], as_version=4)
    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = False
    html, _ = exporter.from_notebook_node(nb, resources={"metadata": {"name": lesson["title"]}})
    bar = BAR.format(base=COURSE["site_base"], slug=slug, title_ar=lesson["title_ar"], kaggle=kaggle_url(lesson))
    html = html.replace("</head>", HEAD + "</head>", 1)
    html = html.replace("<body", "<body data-zg", 1)
    i = html.index(">", html.index("<body data-zg")) + 1
    html = html[:i] + bar + html[i:]
    out = ROOT / "site" / slug / "notebook" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out, f"({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    slugs = list(COURSE["lessons"]) if "--all" in sys.argv else sys.argv[1:]
    for s in slugs:
        render(s)
