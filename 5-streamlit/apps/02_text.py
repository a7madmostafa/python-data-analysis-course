"""02 · Text

    uv run streamlit run 5-streamlit/apps/02_text.py

Titles, headers, Markdown, code and formulas: what you wrote in notebook Markdown cells.
"""
import streamlit as st

st.title("The Titanic, April 1912")
st.header("A header: one per big part of the page")
st.subheader("A subheader: one per chart or table")
st.caption("A caption: small grey text for a source or a note. Data: 891 passengers of the Kaggle training file.")

st.divider()

# Markdown: the same syntax as a notebook Markdown cell
st.markdown("**Bold**, *italic*, ~~strikethrough~~ and `code`.")
st.markdown("> Women and children first.")
st.markdown("""
- Southampton → Cherbourg → Queenstown → New York
- 3 classes, 891 passengers in the file
- [The Streamlit docs](https://docs.streamlit.io)
""")

# Colours, emoji and Material icons inside Markdown
st.markdown(":green[Survived] or :red[died]: one column, two colours. 🚢")
st.markdown(":material/person: passengers · :material/payments: fares · :material/anchor: ports")
st.badge("Cleaned data", icon=":material/check:", color="green")

# Code and formulas
st.code('df = pd.read_csv("titanic.csv")\ndf.groupby("Pclass")["Survived"].mean()', language="python")
st.latex(r"\text{survival rate} = \frac{\text{survivors}}{\text{passengers}}")

# st.write takes almost anything and picks the right display
st.write("st.write works with text, numbers, tables and charts:", 891, "passengers")
