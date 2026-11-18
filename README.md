# Python Data Analysis Course

From NumPy to interactive dashboards: solved notebooks, four complete projects, and a final project to
build on your own. Everything runs on real data and every notebook is saved with its outputs, so you can
read it on GitHub before running anything.

Each lesson also has a page (in Arabic) with the explanation, diagrams and interactive charts:
[zero-grad.com/courses/da](https://zero-grad.com/courses/da/).

## Study map

Work through the folders in order. Each notebook ends with a pointer to the next one.

| Part | Notebooks | What you learn |
|---|---|---|
| **[1. Foundations](1-foundations/)** | [1. introduction](1-foundations/01_intro.ipynb) · [2. linear algebra](1-foundations/02_linear_algebra.ipynb) · [3. statistics](1-foundations/03_statistics.ipynb) | what data analysis is and its workflow, data types; vectors, matrices and a table as a matrix; centre, spread, outliers, skew |
| **[2. NumPy](2-numpy/)** | [NumPy](2-numpy/numpy.ipynb) | arrays vs lists, dtype and NaN, reshape, indexing and views, boolean masks, aggregation and axis, broadcasting, sorting |
| **[3. pandas](3-pandas/)** | [1. basics](3-pandas/01_pandas_basics.ipynb) · [2. grouping and joining](3-pandas/02_grouping_joining.ipynb) · [3. cleaning](3-pandas/03_cleaning.ipynb) | Series and DataFrames, loading, inspecting, selecting, filtering, sorting; groupby, pivot tables, concat and merge; missing values, duplicates, types, text keys, impossible values |
| **[4. Visualization](4-visualization/)** | [1. principles](4-visualization/01_principles.ipynb) · [2. Matplotlib](4-visualization/02_matplotlib.ipynb) · [3. Seaborn](4-visualization/03_seaborn.ipynb) · [4. Plotly](4-visualization/04_plotly.ipynb) · [5. more charts](4-visualization/05_more_charts.ipynb) · [6. mini EDA](4-visualization/06_mini_eda.ipynb) | which chart answers which question; static, statistical and interactive charts; reading statistical charts; one question answered end to end |
| **[5. Streamlit](5-streamlit/)** | [guide](5-streamlit/README.md) · 12 small apps · a multipage app | turning an analysis into a web app with filters, caching, state, pages, and free deployment |
| **[6. Projects](6-projects/)** | [Titanic](6-projects/01-titanic/) · [World Happiness](6-projects/02-world-happiness/) · [Airbnb NYC](6-projects/03-airbnb-nyc/) · Bike Sharing (coming) | complete analyses, each with a notebook and a dashboard that share one `charts.py` |
| **[7. Final project](7-final-project/)** | [the brief](7-final-project/README.md) · [the datasets](https://zero-grad.com/courses/da/final-project/) | your own analysis and app, on one of six real datasets |

## The stages of an analysis

Every project here follows the same path. It is a loop, not a line: exploring often reveals new quality
problems, so you go back and clean again.

| # | Stage | Where it is practised |
|---|---|---|
| 1 | Collect and load | pandas basics; every project |
| 2 | Inspect quality | pandas basics; the first look of every project |
| 3 | Clean and transform | pandas cleaning; the cleaning sections of the projects |
| 4 | Join and reshape | pandas grouping and joining |
| 5 | Explore (EDA) | statistics; mini EDA; the projects |
| 6 | Visualize | the visualization part |
| 7 | Communicate | Streamlit; the dashboards and READMEs of the projects |

## Data

All datasets are in [`data/`](data/):

| File | Used in | Source |
|---|---|---|
| `nilecart/` | foundations, pandas, visualization | NileCart, a made-up online shop in Cairo (prices in EGP), generated with planted errors for the cleaning lesson. Also on Kaggle: [nilecart-sales](https://www.kaggle.com/datasets/a7madmostafa/nilecart-sales) |
| `titanic.csv` | Streamlit, Titanic project | [Kaggle: Titanic](https://www.kaggle.com/competitions/titanic/data) (training file) |
| `world_happiness_2021.csv` | Plotly, World Happiness project | [World Happiness Report 2021](https://www.kaggle.com/datasets/ajaypalsinghlo/world-happiness-report-2021) |
| `airbnb/` | Plotly, Airbnb project | [New York City Airbnb Open Data 2019](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data), from Inside Airbnb |

The cleaned files (`*_clean.csv`, `airbnb/airbnb_cleaned.csv`) are written by the project notebooks and read by their dashboards.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.13; `uv.lock` pins every package version.

1. Install uv once: macOS / Linux `curl -LsSf https://astral.sh/uv/install.sh | sh`, Windows (PowerShell)
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`, or `pip install uv`.
2. In this folder, create the environment (uv downloads Python 3.13 if needed):

   ```bash
   uv sync
   ```

3. Open the notebooks:

   ```bash
   uv run jupyter lab
   ```

4. Run any app, for example:

   ```bash
   uv run streamlit run 6-projects/01-titanic/streamlit_app.py
   ```

Prefer pip? `pip install numpy pandas matplotlib seaborn plotly streamlit statsmodels missingno jupyterlab`
works too, without the pinned versions.

## The website

[`website/`](website/) holds what builds the lesson pages on zero-grad.com and the Kaggle copies of the
notebooks. You don't need it to study; see [website/README.md](website/README.md).
