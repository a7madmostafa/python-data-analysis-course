"""Render a lesson's executed notebook to site/<slug>/notebook/index.html, with a Zero Grad top bar.

The page has a light and a dark theme, like the rest of zero-grad.com: it follows the device until the
reader picks one with the toggle (the site's /assets/js/theme.js, same saved choice as the other pages).

    python website/build/render_notebook.py stats
    python website/build/render_notebook.py --all
"""
from pathlib import Path
import json
import re
import sys

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[2]
COURSE = json.loads((ROOT / "website" / "build" / "course.json").read_text(encoding="utf-8"))

HEAD = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>
<script src="/assets/js/theme.js"></script>
<meta name="theme-color" content="#f5f2ea" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141414" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--zg-bg:#f5f2ea;--zg-surface:#fffdf8;--zg-ink:#1c1e22;--zg-muted:#5b616b;--zg-line:#ddd6c6;--zg-accent:#101f40;--zg-on-accent:#f5f2ea;--zg-add:#2563eb}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--zg-bg:#141414;--zg-surface:#1d1d1d;--zg-ink:#ececec;--zg-muted:#a1a1a1;--zg-line:#333;--zg-accent:#f5f2ea;--zg-on-accent:#141414;--zg-add:#60a5fa}}
:root[data-theme="dark"]{--zg-bg:#141414;--zg-surface:#1d1d1d;--zg-ink:#ececec;--zg-muted:#a1a1a1;--zg-line:#333;--zg-accent:#f5f2ea;--zg-on-accent:#141414;--zg-add:#60a5fa}
body{background:var(--zg-bg)!important;font-family:Inter,system-ui,sans-serif}
.zg-bar{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--zg-bg) 90%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--zg-line);font-family:Inter,"Noto Sans Arabic",sans-serif}
.zg-in{max-width:1100px;margin:auto;padding:.55rem 16px;display:flex;gap:.75rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.zg-crumbs{display:flex;gap:.45rem;align-items:center;font-size:.9rem;direction:rtl}
.zg-crumbs a{color:var(--zg-muted);text-decoration:none}
.zg-crumbs .here{font-weight:700;color:var(--zg-ink)}
.zg-crumbs .sep{color:var(--zg-line)}
.zg-actions{display:flex;gap:.5rem;align-items:center}
.zg-theme{width:34px;height:34px;border-radius:999px;border:1px solid var(--zg-line);background:var(--zg-surface);color:var(--zg-ink);display:grid;place-items:center;cursor:pointer;padding:0}
.zg-theme svg{width:17px;height:17px}.zg-theme .i-sun{display:none}
:root[data-theme="dark"] .zg-theme .i-sun{display:block}:root[data-theme="dark"] .zg-theme .i-moon{display:none}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .zg-theme .i-sun{display:block}:root:not([data-theme="light"]) .zg-theme .i-moon{display:none}}
.zg-btn{font-size:.85rem;border:1px solid var(--zg-line);background:var(--zg-surface);color:var(--zg-ink);border-radius:999px;padding:.3rem .9rem;text-decoration:none;white-space:nowrap}
.zg-btn.primary{background:var(--zg-accent);border-color:var(--zg-accent);color:var(--zg-on-accent);font-weight:700}
main.jp-Notebook,body>.jp-Notebook{max-width:1100px;margin:1rem auto 4rem!important;background:var(--zg-surface);border:1px solid var(--zg-line);border-radius:14px;padding:1.5rem 1rem!important}
.jp-RenderedHTMLCommon{font-family:Inter,system-ui,sans-serif;font-size:15px;line-height:1.7}
.jp-RenderedHTMLCommon h1{color:var(--zg-accent)}
.jp-InputArea-editor,.jp-OutputArea-output pre{font-family:"JetBrains Mono",monospace!important}
img{max-width:100%;height:auto}
/* charts are drawn on white: in the dark theme they sit on a white card */
:root[data-theme="dark"] .jp-OutputArea-output img{background:#fff;border-radius:8px;padding:4px}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .jp-OutputArea-output img{background:#fff;border-radius:8px;padding:4px}}
.jp-OutputArea-output{overflow-x:auto}
@media (max-width:640px){.jp-InputPrompt,.jp-OutputPrompt{display:none!important}}
</style>
"""

BAR = """
<header class="zg-bar"><div class="zg-in">
  <nav class="zg-crumbs" aria-label="أنت هنا"><a href="/">Zero Grad</a><span class="sep">›</span><a href="{base}/">كورس Data Analysis</a><span class="sep">›</span><a href="{base}/{slug}/">{title_ar}</a><span class="sep">›</span><span class="here">النوت بوك</span></nav>
  <div class="zg-actions"><a class="zg-btn" href="{base}/{slug}/">← الدرس</a><a class="zg-btn primary" href="{kaggle}" target="_blank" rel="noopener">{open_label}</a><button class="zg-theme" type="button" data-theme-toggle aria-label="Switch to dark mode"><svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button></div>
</div></header>
"""


def kaggle_url(lesson):
    """Kaggle when the lesson is on Kaggle, otherwise the notebook on GitHub (saved with its outputs)."""
    if lesson.get("kaggle_slug"):
        return f"https://www.kaggle.com/code/{COURSE['kaggle_user']}/{lesson['kaggle_slug']}"
    return "https://github.com/a7madmostafa/python-data-analysis-course/blob/main/" + lesson["notebook"]


# JupyterLab's own colours sit in one `:root {...}` block of the lab template; the dark one is scoped to the dark theme
SYNC = """
<script>
(function () {
  // keep JupyterLab's light/dark flag in step with the page theme (some of its CSS keys on it)
  var root = document.documentElement, media = matchMedia("(prefers-color-scheme: dark)");
  function sync() {
    var t = root.getAttribute("data-theme"), dark = t ? t === "dark" : media.matches;
    document.body.setAttribute("data-jp-theme-light", dark ? "false" : "true");
  }
  document.addEventListener("DOMContentLoaded", sync);
  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  media.addEventListener("change", sync);
})();
</script>
"""


def dark_theme_css(nb):
    html, _ = HTMLExporter(template_name="lab", theme="dark").from_notebook_node(nb)
    block = next(s for s in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S) if "--jp-layout-color0:" in s)
    body = block[block.index("{", block.index(":root")):]
    return ('<style>\n@media (prefers-color-scheme: dark){:root:not([data-theme="light"])' + body + '}\n'
            ':root[data-theme="dark"]' + body + "\n</style>\n")


def render(slug):
    lesson = COURSE["lessons"][slug]
    nb = nbformat.read(ROOT / lesson["notebook"], as_version=4)
    exporter = HTMLExporter(template_name="lab")
    exporter.exclude_input_prompt = False
    html, _ = exporter.from_notebook_node(nb, resources={"metadata": {"name": lesson["title"]}})
    bar = BAR.format(base=COURSE["site_base"], slug=slug, title_ar=lesson["title_ar"], kaggle=kaggle_url(lesson),
                     open_label="Open in Kaggle" if lesson.get("kaggle_slug") else "Open on GitHub")
    html = html.replace("</head>", dark_theme_css(nb) + HEAD + SYNC + "</head>", 1)
    html = html.replace("<body", "<body data-zg", 1)
    i = html.index(">", html.index("<body data-zg")) + 1
    html = html[:i] + bar + html[i:]
    out = ROOT / "website" / "site" / slug / "notebook" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out, f"({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    slugs = [s for s, l in COURSE["lessons"].items() if l.get("notebook")] if "--all" in sys.argv else sys.argv[1:]
    for s in slugs:
        render(s)
