"""Push a lesson's notebook to Kaggle.

    python website/build/kaggle_push.py numpy          # one lesson
    python website/build/kaggle_push.py --all          # every lesson in course.json

Kaggle wants a folder with the notebook and a kernel-metadata.json next to it. The study folders
(1-foundations/, 3-pandas/, ...) stay clean, so the metadata lives in website/kaggle/<lesson>.json and
this script puts the two together in a temporary folder, then runs `kaggle kernels push` on it.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
COURSE = json.loads((ROOT / "website" / "build" / "course.json").read_text(encoding="utf-8"))


def push(slug):
    lesson = COURSE["lessons"][slug]
    meta_path = ROOT / "website" / "kaggle" / f"{slug}.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copyfile(ROOT / lesson["notebook"], tmp / meta["code_file"])
        shutil.copyfile(meta_path, tmp / "kernel-metadata.json")
        subprocess.run(["kaggle", "kernels", "push", "-p", str(tmp)], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--all":   # drafts (website/drafts/) are pushed only by name
        slugs = [s for s, l in COURSE["lessons"].items() if not l["notebook"].startswith("website/drafts/")]
    else:
        slugs = sys.argv[1:]
    for s in slugs:
        push(s)
