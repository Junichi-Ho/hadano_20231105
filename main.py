import streamlit as st
import numpy as np
import pandas as pd


"hello world"

x = st.slider("x")
st.write(x, "xtimes2",2*x)

if st.sidebar.checkbox("Show dataframe"):
    df = pd.DataFrame({
        "からむ１":[1,2,3,4],
        "からむ２":[3,4,5,6]
    })
    st.sidebar.write(df)

option = st.sidebar.selectbox(
    "月で絞る",[9,10,11,12]
)
"あなたが選んだのは",option,"月"

chart_data = pd.DataFrame(
    np.random.randn(20,4),
    columns=["データ4","データ1","データ2","データ3"])


st.line_chart(chart_data)

map_data = pd.DataFrame(
    np.random.randn(1000,2)/[50,50] + [35.3894,139.20],
    columns=["lat","lon"]
)

st.map(map_data)