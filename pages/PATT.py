import streamlit as st
import numpy as np
import math
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
    # NaNを除外してから処理
    combined_df = combined_df.dropna(subset=["SN"])
    
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


def filter_for_drilldown(combined_df):
    st.write("ホール マルチセレクト")
    st.write("年 マルチセレクト")
    st.write("Pin Position")
    #年でFilterするオプション#Streamlitのマルチセレクト
    year_list = list(combined_df["y"].unique())
    default_list = ["23","22"]
    select_year = st.multiselect("年でFilterling",year_list,default=default_list)
    combined_df2 = combined_df[(combined_df["y"].isin(select_year))]

    return combined_df2

@st.cache_data
def crosstab_data_options(combined_df,normalize,ruiseki,display_float,optimize_range_min,optimize_range_max):
    # pd.crosstabを使用して"PN"の構成分布図を作成
    # display_float = 1, 小数点以下ついているものは表示しない （頻度少ないのと 横軸が短い距離の値が多くなる）
    # normalize: "index" 横で100になるnormalization, "all" 全てで100になるNormalization, False 何もしない
    # optimize_range_max, min SNで未満 以上、範囲を狭めないのであれば、-1にする。
    crosstab_data = pd.crosstab(combined_df['SN'], combined_df['PN'], normalize=normalize)
    #crosstab_data
    crosstab_data.index = crosstab_data.index.astype(float)
    if(ruiseki):
        crosstab_data = crosstab_data.cumsum(axis=0)  # 累積和を計算
    if(display_float):
        crosstab_data = crosstab_data[crosstab_data.index % 1 == 0]
    if(optimize_range_min > -0.1 ):
        crosstab_data = crosstab_data[crosstab_data.index > optimize_range_min]
    if(optimize_range_max > -0.1):
        crosstab_data = crosstab_data[crosstab_data.index < optimize_range_max ]

    #crosstab_data
    return crosstab_data

@st.cache_data
def bar_figure(crosstab_data):
    # 積み上げチャートを描画
    fig, ax = plt.subplots(figsize=(10, 6))
    crosstab_data.plot(kind='bar', stacked=True, ax=ax, width=1 , align="center")  # Barの幅を調整
    #crosstab_data
    return fig



def main_display(combined_df):
    #combined_df
    st.title("Patt")
    
    #Filter
    with st.expander("Filter FilterはサイドバーでなくMainで引き出しにした方がよいDrill Down時は,高頻度でアクセスするので。"):
        combined_df2 = filter_for_drilldown(combined_df)

    st.header("Graph")
    st.write("距離別 Patt数 積み上げ100％割合グラフ")

    st.write("Filter")
    # pd.crosstabを使用して"PN"の構成分布図を作成    
    crosstab_data = crosstab_data_options(combined_df2,"index",False,True,0,21) #SN PNでクロス集計
    fig = bar_figure(crosstab_data) #描画
    st.pyplot(fig) # グラフをStreamlitで表示

    st.write("全数")
    # pd.crosstabを使用して"PN"の構成分布図を作成    
    crosstab_data1 = crosstab_data_options(combined_df,"index",False,True,0,21) #SN PNでクロス集計
    fig = bar_figure(crosstab_data1) #描画
    st.pyplot(fig) # グラフをStreamlitで表示

    tab1, tab2, tab3, tab4 = st.tabs(["count","2","3","detail"])
    with tab1:
        st.write("距離別累積頻度チャート")

        st.write("Filter")
        # pd.crosstabを使用して"PN"の構成分布図を作成（累積）
        crosstab_data = crosstab_data_options(combined_df2,"all",True,True,0,21)
        fig = bar_figure(crosstab_data) #描画
        st.pyplot(fig) # グラフをStreamlitで表示


        st.write("全数")
        # pd.crosstabを使用して"PN"の構成分布図を作成（累積）
        crosstab_dataAll = crosstab_data_options(combined_df,"all",True,True,0,21)
        fig = bar_figure(crosstab_dataAll) #描画
        st.pyplot(fig) # グラフをStreamlitで表示

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
        st.write("距離別頻度バーチャート")
        ## pd.crosstabを使用してクロス集計テーブルを作成
        crosstab_data4 = crosstab_data_options(combined_df,False,False,True,0,21)
        fig = bar_figure(crosstab_data4) #描画
        st.pyplot(fig) # グラフをStreamlitで表示

        st.write("hole別 Patt数 バーチャート")
        st.write("hole別 距離数 バーチャート")
    with tab3:
        st.write("ホール別パット数")
    with tab4:
        st.write("全距離別パット数割合")
        # pd.crosstabを使用して"PN"の構成分布図を作成    
        crosstab_data1 = crosstab_data_options(combined_df,"index",False,True,-1,-1) #SN PNでクロス集計
        fig = bar_figure(crosstab_data1) #描画
        st.pyplot(fig) # グラフをStreamlitで表示
        # pd.crosstabを使用して"PN"の構成分布図を作成    
        crosstab_data1 = crosstab_data_options(combined_df,"all",True,True,-1,-1) #SN PNでクロス集計
        fig = bar_figure(crosstab_data1) #描画
        st.pyplot(fig) # グラフをStreamlitで表示

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