# Projects

Three complete analyses. Each one is a small, real project: a notebook that goes from the raw file to
answers, and a Streamlit dashboard on the cleaned data. The notebook and the app import the same `charts.py`,
so every chart is written once.

| Project | Data | Question | Highlights |
|---|---|---|---|
| [01 · Titanic](01-titanic/) | 891 passengers | Who survived, and why? | ages filled from titles; a port effect that is mostly a class effect |
| [02 · World Happiness](02-world-happiness/) | 149 countries, 2021 | What goes with a happy country? | correlation vs causation; Egypt's score taken apart |
| [03 · Airbnb NYC](03-airbnb-nyc/) | 48,895 listings, 2019 | What sets the price of a night? | distance to the centre as a feature; a four-page app with a map |

Every project follows the same stages: first look, questions, cleaning, feature engineering, univariate,
bivariate and multivariate analysis, answers, conclusion. Run any dashboard from the repository folder:

```bash
uv run streamlit run 6-projects/01-titanic/streamlit_app.py
```

**Next:** the [final project](../7-final-project/): the same work on a dataset of your choice.
