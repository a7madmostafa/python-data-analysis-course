# Streamlit

A notebook is a good place to analyse data and a bad place to share it: most people who need the answer will never open Jupyter. **Streamlit** turns a Python script into a web page with filters, tables and charts. It needs no HTML and no JavaScript: one `.py` file and one command.

| Way to share an analysis | Good for | Limit |
|---|---|---|
| Notebook | the analyst | needs Python and Jupyter to read |
| Static report (PDF, slides) | a fixed answer | no filters, no follow-up questions |
| BI tool (Power BI, Tableau) | company dashboards | separate tool, separate skills, licences |
| **Streamlit app** | an interactive page from your own pandas and Plotly code | one page per script, not a full website |

[`apps/`](apps/) holds twelve small apps, **one new idea each**, on the Titanic passenger list. The complete dashboards are in the [projects](../6-projects/).

## Running an app

From the repository folder (the one with `pyproject.toml`), after `uv sync` (see the [main README](../README.md)):

```bash
uv run streamlit run 5-streamlit/apps/01_hello.py
```

The app opens at http://localhost:8501. Edit the file and save: the page offers **Rerun** (or choose **Always rerun**). Stop the app with `Ctrl + C` in the terminal.

> ⚠️ A Streamlit app is not started with `python app.py` and does not run inside a notebook cell. Always `streamlit run`.

## The core idea: the script reruns

Streamlit runs your script **from top to bottom**, and it runs it **again from the top every time someone touches a widget**. Each widget simply returns its current value:

```python
age = st.slider("Age", 0, 80, 30)        # an int, like input(), but in a browser
st.write("Passengers older than", age, ":", (df["Age"] > age).sum())
```

There are no callbacks to wire: move the slider, the script reruns with the new `age`, and the page updates. Almost everything below follows from this one rule.

## The apps

| App | The idea |
|---|---|
| [`01_hello.py`](apps/01_hello.py) | the script reruns from the top on every click |
| [`02_text.py`](apps/02_text.py) | title, header, markdown, code, LaTeX, `st.write` |
| [`03_data.py`](apps/03_data.py) | `st.dataframe`, `column_config`, `st.table`, `st.metric` |
| [`04_charts.py`](apps/04_charts.py) | quick charts, `st.map`, `st.plotly_chart`, `st.pyplot` |
| [`05_widgets.py`](apps/05_widgets.py) | every input widget and the value it returns |
| [`06_filters.py`](apps/06_filters.py) | widgets → a filtered DataFrame → numbers and charts |
| [`07_layout.py`](apps/07_layout.py) | sidebar, columns, tabs, expander, container |
| [`08_status_media.py`](apps/08_status_media.py) | messages, spinner, progress, status, images |
| [`09_cache.py`](apps/09_cache.py) | `@st.cache_data` |
| [`10_state.py`](apps/10_state.py) | `st.session_state`, widget keys |
| [`11_form.py`](apps/11_form.py) | `st.form`: many widgets, one rerun |
| [`12_download.py`](apps/12_download.py) | `st.download_button` |

### Charts

Three families: Streamlit's own quick charts (`st.bar_chart`, `st.line_chart`, `st.map`) take a table and draw it in one line; `st.plotly_chart(fig)` shows any Plotly figure; `st.pyplot(fig)` shows a Matplotlib or Seaborn figure. In apps, prefer **Plotly**: hover and zoom come for free.

### The dashboard pattern

Almost every dashboard has the same three steps, shown in `06_filters.py`:

1. **widgets** in the sidebar return the user's choices;
2. **one boolean mask per widget**, combined with `&`, gives a filtered DataFrame;
3. **numbers and charts** are computed from that filtered DataFrame only.

```python
classes = st.sidebar.multiselect("Class", [1, 2, 3], default=[1, 2, 3])
ages = st.sidebar.slider("Age", 0, 80, (0, 80))

view = df[df["Pclass"].isin(classes) & df["Age"].between(*ages)]

st.metric("Passengers", len(view))
st.plotly_chart(px.histogram(view, x="Age"))
```

Check for an empty selection (`if view.empty: st.warning(...); st.stop()`) so the charts never receive zero rows.

### Cache: don't redo the slow work

Because every click reruns the whole script, `pd.read_csv` runs on every click too. With a big file, a database or an API that is slow. `@st.cache_data` remembers what a function returned for the same arguments:

```python
@st.cache_data
def load_data(path):
    return pd.read_csv(path)
```

`09_cache.py` makes the loader sleep two seconds, so the difference is easy to feel.

### Session state: the app's memory

A plain variable is reset on every rerun, so a counter written as `count = 0; if st.button("Add one"): count += 1` never gets past 1. `st.session_state` is a dictionary that **survives reruns** (one per browser tab):

```python
if "count" not in st.session_state:      # only on the very first run
    st.session_state.count = 0
if st.button("Add one"):
    st.session_state.count += 1
st.write(st.session_state.count)
```

A widget with `key="name"` also stores its value in `st.session_state["name"]`.

### Forms: many widgets, one rerun

Inside `with st.form("name"):` nothing reruns until the form's submit button is clicked. Use a form when the user fills several fields and only the final combination matters.

## A complete app

The [projects](../6-projects/) hold complete dashboards. A one-page app with tabs is enough for most of them (see [Titanic](../6-projects/01-titanic/streamlit_app.py)); the [Airbnb NYC](../6-projects/03-airbnb-nyc/) dashboard grows into several pages:

```text
03-airbnb-nyc/
├── streamlit_app.py        the entrypoint: data, shared sidebar filters, st.navigation
├── views/                  one file per page (overview, prices, map, listings)
├── charts.py               one function per chart, shared with the notebook
└── .streamlit/config.toml  the theme
```

**Several pages.** The entrypoint is the frame and the pages are the pictures: what `streamlit_app.py` draws (the sidebar filters) appears on every page, and `st.navigation([...]).run()` runs the file of the page the user clicked. The filtered data is shared with the pages through `st.session_state`.

**A theme.** `.streamlit/config.toml` sets the colours of every widget (`primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `font`).

**Its own folder.** A deployed app needs its code, its data and its dependency files (`pyproject.toml` + `uv.lock`) where the server can find them. Inside this repository the projects share the root `data/` and `pyproject.toml`; a stand-alone project keeps them in its own folder, as described in the [final project](../7-final-project/).

## Projects with uv

[uv](https://docs.astral.sh/uv/) manages a project's Python version and packages in one tool.

| Step | Command |
|---|---|
| Install uv, once | macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh \| sh` · Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` · or `pip install uv` |
| Start a project | `uv init my-app` then `cd my-app` |
| Add packages | `uv add streamlit pandas plotly` (writes `pyproject.toml` and `uv.lock`) |
| Set up an existing project | `uv sync` |
| Run anything in it | `uv run streamlit run streamlit_app.py` |

`uv.lock` records the exact version of every package. Commit it with the code, and every machine (a teammate's laptop, the deployment server) builds the same environment. Without it, `pip install pandas` gives a different version next year, and the app can break.

## Deploy for free: Streamlit Community Cloud

1. Push the app folder to GitHub, with `pyproject.toml` and `uv.lock`.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub.
3. **Create app**: pick the repository, the branch, the path of `streamlit_app.py`, and Python 3.13 under *Advanced settings*.
4. **Deploy**. A minute later the app is live at `https://<name>.streamlit.app`.

After that, every `git push` updates the app by itself. Errors and `print()` output are under **Manage app → logs**. Free apps go to sleep after a few quiet days; the next visitor wakes them up.

---

**Next:** [Projects](../6-projects/): four complete analyses, each with a notebook and a Streamlit app.
