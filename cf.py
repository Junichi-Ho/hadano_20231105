import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime

@st.cache_data
def green_image(holenum,pfile): #ホールごとのイメージの取り込み
    im = "./pict/"+ pfile +("0"+holenum)[-2:]+".png"
    #st.sidebar.write(im)
    image = Image.open(im)
    caption = im[-6:-4]
    return image,caption

@st.cache_data 
def main_dataframe(csvfile): # Main Dataframe CSVファイルの読み込み
    # Index ＝ Dateに。Dateは時間をとりたいがわからない。
    df = pd.read_csv(csvfile)
    df["Date"]=pd.to_datetime(df["Date"], format="mixed")

    df["Year"] = df["Date"].apply(lambda x : x.strftime("%y"))
    df["Month"] = df["Date"].apply(lambda x : x.strftime("%m"))

    df["Date"]= df["Date"].dt.strftime("%y.%m.%d")
    #df = df.set_index("Date")
    #整数化
    columns_to_convert = ["OB", "Penalty", "Total", "1st", "2nd","green","approach","Double Total",
               "3 shot in 100","Total.1","Score.1"]
    for column in columns_to_convert:
        df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0).astype(int)

    return df


def main():
    st.write("this is function file for streamlit project")

if __name__ == "__main__":
    main()