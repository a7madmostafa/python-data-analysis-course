"""Push a lesson's notebook to Kaggle.

    python website/build/kaggle_push.py numpy          # one lesson
    python website/build/kaggle_push.py --all          # every lesson in course.json that has a kaggle_slug
    python website/build/kaggle_push.py --code         # create / update the project-code dataset (the charts.py files)

Kaggle wants a folder with the notebook and a kernel-metadata.json next to it. The study folders
(1-foundations/, 3-pandas/, ...) stay clean, so the metadata lives in website/kaggle/<lesson>.json and
this script puts the two together in a temporary folder, then runs `kaggle kernels push` on it.

Lessons 1-8 find their data under /kaggle/input themselves. The notebooks from 4-visualization/02_matplotlib on
and the projects read ../data/... and import a charts.py next to them, so for those a "kaggle_setup" entry in
course.json adds one cell at the top of the copy that is pushed (the notebook in the repo is not changed):
it installs the repo's pinned versions, copies the attached Kaggle files into the repo layout under
/kaggle/working/course, and moves into the notebook's folder. Locally that cell does nothing.

    "kaggle_setup": {"folder": "6-projects/01-titanic",
                     "files": {"train.csv": "titanic.csv"},          # file found under /kaggle/input -> data/...
                     "code": "charts_titanic.py"}                     # from the project-code dataset -> ./charts.py
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

import nbformat

ROOT = Path(__file__).resolve().parents[2]
COURSE = json.loads((ROOT / "website" / "build" / "course.json").read_text(encoding="utf-8"))
CODE_DATASET = f"{COURSE['kaggle_user']}/zero-grad-da-project-code"
CODE_FILES = {"charts_titanic.py": "6-projects/01-titanic/charts.py",
              "charts_happiness.py": "6-projects/02-world-happiness/charts.py",
              "charts_airbnb.py": "6-projects/03-airbnb-nyc/charts.py"}
PINS = "matplotlib==3.10.0 seaborn==0.13.2 plotly==5.24.1 streamlit==1.67.0 statsmodels==0.14.4 scipy==1.15.3"

SETUP = '''# Kaggle setup: rebuild the folder layout this notebook expects (../data/..., charts.py next to it).
# Added to the Kaggle copy only; on a laptop with the course repo this cell does nothing.
import os, shutil, subprocess, sys
from pathlib import Path

if Path("/kaggle/input").exists():
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *"{pins}".split()], check=True)
    def find(name):
        return next(p for p in Path("/kaggle/input").rglob(name) if p.is_file())
    root = Path("/kaggle/working/course")
    for src, dst in {files!r}.items():
        (root / "data" / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(find(src), root / "data" / dst)
    here = root / "{folder}"
    here.mkdir(parents=True, exist_ok=True)
    if {code!r}:
        shutil.copyfile(find({code!r}), here / "charts.py")
    os.chdir(here)
    print("working in", here)'''


def setup_cell(s):
    return nbformat.v4.new_code_cell(SETUP.format(pins=PINS, files=s.get("files", {}), folder=s["folder"], code=s.get("code", "")))


def push(slug):
    lesson = COURSE["lessons"][slug]
    meta_path = ROOT / "website" / "kaggle" / f"{slug}.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if lesson.get("kaggle_setup"):
            nb = nbformat.read(ROOT / lesson["notebook"], as_version=4)
            first_code = next(i for i, c in enumerate(nb.cells) if c.cell_type == "code")
            nb.cells.insert(first_code, setup_cell(lesson["kaggle_setup"]))
            nbformat.write(nb, tmp / meta["code_file"])
        else:
            shutil.copyfile(ROOT / lesson["notebook"], tmp / meta["code_file"])
        shutil.copyfile(meta_path, tmp / "kernel-metadata.json")
        subprocess.run(["kaggle", "kernels", "push", "-p", str(tmp)], check=True)


def push_code():
    """The three charts.py files as one small dataset, so the project notebooks can import them on Kaggle."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name, src in CODE_FILES.items():
            shutil.copyfile(ROOT / src, tmp / name)
        (tmp / "dataset-metadata.json").write_text(json.dumps({
            "id": CODE_DATASET, "title": "Zero Grad DA: project code", "licenses": [{"name": "MIT"}],
            "subtitle": "The charts.py modules of the course's three projects",
            "description": "One `charts.py` per project of the Zero Grad Python Data Analysis course (Titanic, World Happiness, "
                           "Airbnb NYC): one function per Plotly chart, shared by the analysis notebook and the Streamlit app. "
                           "Attached to the project notebooks so they can `import charts` on Kaggle.\n\n"
                           "Source: https://github.com/a7madmostafa/python-data-analysis-course"}, indent=2), encoding="utf-8")
        exists = subprocess.run(["kaggle", "datasets", "status", CODE_DATASET], capture_output=True, text=True).returncode == 0
        cmd = (["kaggle", "datasets", "version", "-p", str(tmp), "-m", "update"] if exists
               else ["kaggle", "datasets", "create", "-p", str(tmp), "--public"])
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--code":
        push_code()
        sys.exit()
    if sys.argv[1] == "--all":   # only the lessons that are on Kaggle (have a kaggle_slug)
        slugs = [s for s, l in COURSE["lessons"].items() if l.get("kaggle_slug")]
    else:
        slugs = sys.argv[1:]
    for s in slugs:
        push(s)
