import streamlit as st
import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
import seaborn as sns
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

@st.cache_data
def create_dataframe_from():
    df = cf.main_dataframe("20231104_HatanoScore.csv")
    # 空のリストを作成
    dfs = []

    # forループでdf1を作成し、リストに追加
    for i in range(1, 19):
        temp_df = cf.dataframe_by_hole(df, i)
        rename_dict = {str(i): "Score"}
        temp_df = temp_df.rename(columns=rename_dict)
        temp_df["hole"] = i
        dfs.append(temp_df)
    # リストに追加されたデータフレームを縦に結合
    combined_df = pd.concat(dfs, ignore_index=True)
    
    return combined_df

def sidebar_display(combined_df):

    st.sidebar.write("高頻度でアクセスしない。たまに確認するものを記載すべし")
    st.sidebar.write("説明 とか")
    st.sidebar.write("気づきメモ とか")
    st.sidebar.markdown("---")

    # "PN"列の平均を表示
    pn_mean = combined_df["PN"].mean()
    st.sidebar.write(f"平均パット{pn_mean:.3f}")
    #st.write(combined_df["PN"].value_counts())
    #st.table(combined_df.groupby("PN")["SN"].mean())

    # "PN"毎の頻度と"SN"の平均を1つのテーブルで表示
    summary_table = combined_df.groupby("PN").agg({'SN': ['count',  'mean']})
    st.sidebar.table(summary_table)

def main_display(combined_df):
    #combined_df
    st.title("Patt")
    with st.expander("Filter FilterはサイドバーでなくMainで引き出しにした方がよいDrill Down時は,高頻度でアクセスするので。"):
        st.write("ホール マルチセレクト")
        st.write("年 マルチセレクト")
        #年でFilterするオプション#Streamlitのマルチセレクト
        year_list = list(combined_df["y"].unique())
        default_list = ["23","22"]
        select_year = st.multiselect("年でFilterling",year_list,default=default_list)
        combined_df2 = combined_df[(combined_df["y"].isin(select_year))]
        st.write("Pin Position")

    st.header("Graph")
    st.write("距離別 Patt数 積み上げ100％割合グラフ")

    # pd.crosstabを使用して"PN"の構成分布図を作成
    crosstab_data = pd.crosstab(combined_df['SN'], combined_df['PN'], normalize='index')
    #crosstab_data
    crosstab_data.index = crosstab_data.index.astype(float)
    crosstab_data = crosstab_data[crosstab_data.index % 1 == 0]
    crosstab_data = crosstab_data[crosstab_data.index > 0]
    crosstab_data1 = crosstab_data[crosstab_data.index < 21 ]

    # 積み上げチャートを描画
    fig, ax = plt.subplots(figsize=(10, 6))

    crosstab_data1.plot(kind='bar', stacked=True, ax=ax, width=1 , align="center")  # Barの幅を調整
    #crosstab_data

    # グラフをStreamlitで表示
    st.pyplot()


    tab1, tab2, tab3, tab4 = st.tabs(["count","2","3","detail"])
    with tab1:
        st.write("距離別頻度バーチャート")
        ## pd.crosstabを使用してクロス集計テーブルを作成
        crosstab_data2 = pd.crosstab(combined_df['SN'], combined_df['PN'])
        crosstab_data2 = crosstab_data2[crosstab_data2.index % 1 == 0]
        crosstab_data2 = crosstab_data2[crosstab_data2.index > 0]
        crosstab_data4 = crosstab_data2[crosstab_data2.index < 21 ]

        # 積み上げチャートを描画
        fig, ax = plt.subplots(figsize=(10, 6))

        crosstab_data4.plot(kind='bar', stacked=True, ax=ax, width=1 , align="center")  # Barの幅を調整
        #crosstab_data

        # グラフをStreamlitで表示
        st.pyplot(fig)


        ## クロス集計テーブルをグラフ化
        #crosstab_data2.plot(kind='bar', stacked=True)


        ###Seaboneによる積み上げ。
        ## PN列を小さい順に並べ替え
        #combined_df2 = combined_df.sort_values('PN', ascending=True)
        ## カラーパレットを定義
        #colors = ["blue", "orange", "green", "red", "black"]
        ## "PN"毎の積み上げヒストグラフを描画
        #sns.histplot(data=combined_df2, x="SN", hue="PN", multiple="stack", palette=colors)
        ## グラフをMatplotlibのFigureオブジェクトに変換
        #fig = plt.gcf()
        ## Streamlitで表示
        #st.pyplot(fig)



    with tab2:
        st.write("hole別 Patt数 バーチャート")
        st.write("hole別 距離数 バーチャート")
    with tab3:
        st.write("ホール別パット数")
    with tab4:
        st.write("20歩以下 距離別パット数割合")
        # 積み上げチャートを描画
        fig, ax = plt.subplots(figsize=(10, 6))
        crosstab_data.plot(kind='bar', stacked=True, ax=ax, width=1 , align="center")  # Barの幅を調整 
        # グラフをStreamlitで表示
        st.pyplot(fig)
        # 積み上げチャートを描画
        fig, ax = plt.subplots(figsize=(10, 6))

        crosstab_data2.plot(kind='bar', stacked=True, ax=ax, width=1 , align="center")  # Barの幅を調整
        #crosstab_data

        # グラフをStreamlitで表示
        st.pyplot(fig)
    
        # "SN"列の出現率を計算
    #sn_value_counts = combined_df["SN"].value_counts(normalize=True)

    # 棒グラフを描画
    #st.bar_chart(sn_value_counts)
    # ヒストグラムを描画
    #fig, ax = plt.subplots()
    #ax.hist(combined_df["SN"], bins='auto')
    #st.pyplot(fig)


def main():
    #各ホール盾持ちデータの取得
    combined_df = create_dataframe_from()
    #SideBar表示
    sidebar_display(combined_df)
    #MainDisplayへ飛ぶ
    main_display(combined_df)


if __name__ == "__main__":
    main()