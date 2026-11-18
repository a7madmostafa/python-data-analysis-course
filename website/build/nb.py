"""Tiny helpers to write a notebook from a list of cells, then run it in place."""
from pathlib import Path
import subprocess
import sys

import nbformat as nbf


def md(text):
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text):
    return nbf.v4.new_code_cell(text.strip("\n"))


def write(cells, path, title):
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata["title"] = title
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, path)
    return path


def execute(path):
    path = Path(path)
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
                    "--ExecutePreprocessor.timeout=300", path.name], cwd=path.parent, check=True)
