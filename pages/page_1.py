import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image


image = Image.open("./pict/01_1m.png")

st.image(image, caption="イメージ")