"""Build the brand-free copy of the final-project pages for GitHub Pages.

    python website/build/build_pages.py            # writes _site/
    python website/build/build_pages.py <out_dir>

website/site/final-project/ is the one source (the Zero Grad version, served at
zero-grad.com/courses/da/final-project/). This script copies it and strips every Zero Grad
mention (top-bar crumbs, footer, meta tags, the site-wide theme script and icon), so the page
can be shared on its own. The GitHub Action in .github/workflows/pages.yml runs it on every
push and publishes the result. It stops with an error if any "zero grad" text is left.
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "website" / "site" / "final-project"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"

# light/dark: what /assets/js/theme.js does on zero-grad.com, inline because it isn't served here
THEME = """<script>
(function () {
  var KEY = "fp-theme", root = document.documentElement;
  try { var s = localStorage.getItem(KEY); if (s) root.setAttribute("data-theme", s); } catch (e) {}
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-theme-toggle]"); if (!b) return;
    var cur = root.getAttribute("data-theme") || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    var next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
  });
})();
</script>"""


def clean(html):
    drop = ('property="og:image"', 'property="og:url"', 'rel="canonical"', 'rel="icon"')
    html = "\n".join(l for l in html.split("\n") if not any(d in l for d in drop))
    html = html.replace('<script src="/assets/js/theme.js"></script>', THEME)
    html = html.replace("<title>Final Project · Python Data Analysis · Zero Grad</title>", "<title>Final Project · Suggested Datasets</title>")
    html = html.replace(" · Final Project · Zero Grad", " · Final Project")
    html = html.replace('content="Final Project · Final Project"', 'content="Final Project · Suggested Datasets"')
    html = html.replace('content="summary_large_image"', 'content="summary"')   # no preview image here
    html = html.replace("The final project of the Zero Grad Python Data Analysis course: pick", "Final project: pick")
    html = re.sub(r'<a class="home" href="/">Zero Grad</a><span class="sep">›</span>'
                  r'<a class="course" href="/courses/da/">Data Analysis</a><span class="sep">›</span>', "", html)
    html = html.replace("Zero Grad · Python Data Analysis · Final project.", "Final project.")
    return html


if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    left = []
    for p in [*OUT.rglob("*.html"), *OUT.rglob("*.css")]:
        t = p.read_text(encoding="utf-8")
        if p.suffix == ".html":
            t = clean(t)
            p.write_text(t, encoding="utf-8", newline="")
        if re.search(r"zero[\s-]?grad", t, re.I):
            left.append(p.name)
    if left:
        sys.exit(f"Zero Grad text left in: {', '.join(left)}")
    print("built", OUT)
