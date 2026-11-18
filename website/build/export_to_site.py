"""Copy the course's site/ folder into the zero-grad website as /courses/da/.

    python website/build/export_to_site.py            # to ../zero-grad/site/courses/da
    python website/build/export_to_site.py <path>     # to another site folder

site/ here is laid out exactly as it is served (site/index.html is /courses/da/,
site/<lesson>/index.html is /courses/da/<lesson>/), so this is a plain mirror.
The course page, home page and sitemap links in zero-grad are edited there by hand.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "website" / "site"
DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "zero-grad" / "site" / "courses" / "da"

if __name__ == "__main__":
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SRC, DEST)
    files = [p for p in DEST.rglob("*") if p.is_file()]
    print(f"copied {len(files)} files to {DEST}")
