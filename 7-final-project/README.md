# Final project

The chapters taught the tools and the [projects](../6-projects/) showed them at work. Now it is your
turn: one complete analysis of a dataset you have never seen, from the first look to a public dashboard.

## The task

Pick **one** of the six datasets below and build two things:

1. **An analysis notebook** that asks clear questions, cleans the data with every decision explained, explores
   it with the right charts, and ends with answers, conclusions and limitations.
2. **A Streamlit app** that lets someone else explore what you found.

**Required**, in one GitHub repository:

| What | Details |
|---|---|
| `analysis.ipynb` | the analysis notebook, executed, with its outputs saved |
| `app.py` | the Streamlit app |
| a public link | the app deployed on [Streamlit Community Cloud](https://share.streamlit.io) |

Everything else (how you organise the files, which tools you use around them) is your choice. The
structure below is a suggestion.

## Pick a dataset

Each dataset has its own page: what the data holds, where to download it, what to watch out for, questions
to start from and ideas for the app ([all datasets](https://zero-grad.com/courses/da/final-project/)).

| Dataset | The starting question |
|---|---|
| 🚦 [NYC Motor Vehicle Crashes](https://zero-grad.com/courses/da/final-project/datasets/nyc-crashes.html) | When and where do crashes happen in New York City, why, and who gets hurt? |
| 🚗 [Used Car Prices in Egypt](https://zero-grad.com/courses/da/final-project/datasets/egypt-used-cars.html) | What sets the price of a used car in Egypt, and how much did prices move in one year? |
| ❤️ [Heart Disease Indicators (CDC 2022)](https://zero-grad.com/courses/da/final-project/datasets/heart-health.html) | Which habits and health conditions go with having had a heart attack? |
| 💻 [Stack Overflow Developer Survey](https://zero-grad.com/courses/da/final-project/datasets/developer-survey.html) | Who writes code, in which languages, for how much, how do developers feel about AI, and how is all this changing? |
| 🏅 [120 Years of Olympic History](https://zero-grad.com/courses/da/final-project/datasets/olympic-medals.html) | Who wins Olympic medals, does hosting help, and how have Egypt and the Arab countries done? |
| 💼 [LinkedIn Job Postings (US, 2024)](https://zero-grad.com/courses/da/final-project/datasets/linkedin-jobs.html) | Which jobs and skills are in demand, what pays, and does remote work change anything? |

> The dataset pages are on the course website, [zero-grad.com/courses/da/final-project](https://zero-grad.com/courses/da/final-project/).

All six are real, recent and big enough to be interesting (tens of thousands of rows or more), and each needs
some cleaning. The questions on each page are a starting point: answer some, drop others, add your own.

## The workflow

Follow the same stages as the example projects:

| Stage | What it means |
|---|---|
| 1. First look | shape, types, a few rows, the meaning of every column, missing values |
| 2. Questions | 5–7 questions, each naming the columns it needs |
| 3. Cleaning | scope, types, missing values, duplicates, impossible values, outliers; a cleaning log |
| 4. Feature engineering | the columns that make the questions easier (dates, groups, ratios) |
| 5. Univariate | one column at a time: typical value, spread, shape |
| 6. Bivariate | two columns: what moves with what |
| 7. Multivariate | three or more: does the pattern hold inside groups? |
| 8. Answers | each question, answered with a number |
| 9. Conclusion | findings, limitations, next steps |
| App | the charts that carry the answers, with filters, in a Streamlit app |

## Suggested structure

```text
my-project/
├── analysis.ipynb       required: the analysis, executed, with outputs
├── app.py               required: the Streamlit app
├── README.md            suggested: the question, key findings, a screenshot, the live link, how to run it
├── data/                suggested: the cleaned data the app reads (not the raw download if it is large)
├── charts.py            optional: one function per chart, shared by the notebook and the app
├── pyproject.toml       recommended (uv): the dependencies
└── uv.lock              recommended (uv): their exact versions
```

Build it as its own GitHub repository, so it can be deployed on its own.

**`charts.py` (optional).** The example projects keep every chart in one function in `charts.py`, and both
the notebook and the app import it. A chart is then written once, looks the same in both places, and a fix
reaches both. It is a convenience, not a rule: drawing the charts directly in the notebook and in `app.py`
is fine.

**uv (recommended).** [uv](https://docs.astral.sh/uv/) records the exact version of every package in
`uv.lock`, so the project runs the same on your laptop, on someone else's, and on Community Cloud, which
installs from `uv.lock`; `uv sync` sets everything up in one command. Not mandatory: a `requirements.txt`
works too. Community Cloud does need **one** dependency file (`uv.lock`, `pyproject.toml` or
`requirements.txt`) next to `app.py` or at the root of the repository, or the deployed app will not find
pandas or Plotly.

## Before you call it finished

**Analysis**
- [ ] Every column used is explained, and every cleaning decision says *why*.
- [ ] Each question is answered with a number, not an impression.
- [ ] Each chart has a title that states the finding, readable axis labels, and a sentence below it.
- [ ] Comparisons use the right summary (median for skewed data, rates for groups of different sizes).
- [ ] At least one pattern is checked inside groups before it is trusted.
- [ ] The limitations are honest: what the data cannot tell.

**App**
- [ ] It opens without errors, and every chart reads the filtered data.
- [ ] An empty filter shows a message instead of a crash.
- [ ] The data is loaded once (`@st.cache_data`).
- [ ] It is deployed on Streamlit Community Cloud, and the link is in the README.

**Repository**
- [ ] It holds `analysis.ipynb` (with outputs) and `app.py`, and the README links to the live app.
- [ ] A fresh clone runs: `uv sync` then `uv run streamlit run app.py` (or `pip install -r requirements.txt`
      then `streamlit run app.py`).
- [ ] No file over 100 MB, no secrets, no `.venv/`.

## Examples to learn from

| Project | Data | What to look at |
|---|---|---|
| [Titanic](../6-projects/01-titanic/) | 891 passengers | missing ages filled by title; a port effect that is mostly a class effect |
| [World Happiness](../6-projects/02-world-happiness/) | 149 countries | correlation vs causation; one country under the microscope |
| [Airbnb NYC](../6-projects/03-airbnb-nyc/) | 48,895 listings | a multipage app with a map; distance as a feature |
