"""05 · Widgets: the tour

    uv run streamlit run 5-streamlit/apps/05_widgets.py

Every widget RETURNS a value, like input() in plain Python.
Change one and the script reruns with the new value. Watch the line printed under each widget.
"""
import streamlit as st

st.title("Widgets: every input Streamlit gives you")

st.header("Click")
clicked = st.button("Button")                       # True only in the rerun right after the click
st.write("button →", clicked)
agree = st.checkbox("Checkbox: show children only")
st.write("checkbox →", agree)
on = st.toggle("Toggle: same idea, looks like a switch")
st.write("toggle →", on)

st.header("Choose one")
sex = st.radio("Radio: sex", ["male", "female"], horizontal=True)
st.write("radio →", sex)
port = st.selectbox("Selectbox: port", ["Southampton", "Cherbourg", "Queenstown"])
st.write("selectbox →", port)

st.header("Choose many")
classes = st.multiselect("Multiselect: classes", [1, 2, 3], default=[1, 2])
st.write("multiselect →", classes)

st.header("Numbers")
age = st.slider("Slider: one value", 0, 80, 30)
st.write("slider →", age)
ages = st.slider("Slider: a range (give a tuple as the default)", 0, 80, (18, 60))
st.write("range slider →", ages)
size = st.select_slider("Select slider: ordered labels", ["Alone", "Small family", "Big family"])
st.write("select_slider →", size)
fare = st.number_input("Number input: fare (£)", min_value=0.0, max_value=520.0, value=32.0, step=0.5)
st.write("number_input →", fare)

st.header("Text, dates and files")
name = st.text_input("Text input: search a name", placeholder="e.g. Allen")
st.write("text_input →", name)
note = st.text_area("Text area: longer text")
st.write("text_area →", note)
day = st.date_input("Date input", value="1912-04-15")
st.write("date_input →", day)
hour = st.time_input("Time input", value="02:20")
st.write("time_input →", hour)
file = st.file_uploader("File uploader: a CSV", type="csv")
st.write("file_uploader →", file.name if file else None)
