import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

def sidebar_display():
    st.sidebar.write("高頻度でアクセスしない。たまに確認するものを記載すべし")
    st.sidebar.write("説明 とか")
    st.sidebar.write("気づきメモ とか")

def main_display():
    st.title("Patt")
    with st.expander("Filter FilterはサイドバーでなくMainで引き出しにした方がよいDrill Down時は,高頻度でアクセスするので。"):
        st.write("ホール マルチセレクト")
        st.write("年 マルチセレクト")
        st.write("Pin Position")

    st.header("Graph")
    st.subheader("距離別 Patt数 積み上げ100％割合グラフ")
    tab1, tab2, tab3, tab4 = st.tabs(["1","2","3","4"])
    with tab1:
        st.write("距離別頻度バーチャート")
    with tab2:
        st.write("hole別 Patt数 バーチャート")
        st.write("hole別 距離数 バーチャート")
    with tab3:
        st.write("そのた")
    with tab4:
        st.write("そのた")


def main():
    #df,df_event,df_stadata = pickup_frame()
    #sidebar_display(df,df_event,df_stadata)
    #main_display(df,df_event,df_stadata)
    sidebar_display()
    main_display()


if __name__ == "__main__":
    main()