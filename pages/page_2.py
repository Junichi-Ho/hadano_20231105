import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sys
sys.path.append('../')  # 上位フォルダをパスに追加

import cf  # 上位フォルダにあるモジュールをインポート

@st.cache_data
def pickup_frame():
    df = cf.main_dataframe("20231104_HatanoScore.csv")
    df = df.copy()
    columns = ["Date","Year","Month",
               "Event","OB",
               "Penalty","Total","Score",
               "Out","In","Gon-Patt+36",
               "1st","2nd","green",
               "approach","Double Total",
               "3 shot in 100","Total.1","Score.1"
               ]
    df = df[columns]
    df["Year"] = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)
    df_event = df[["Date","Year","Month","Event","OB","Score"]]
    df_stadata = df[["Year","Month","OB","Penalty","Total","Score",
               "Out","In","Gon-Patt+36",
               "1st","2nd","green",
               "approach","Double Total",
               "3 shot in 100","Total.1","Score.1"]]

    return (df,df_event,df_stadata)

def sidebar_display(df,df_event,df_stadata):

    df3 = df[['Score','OB',"Out","In"]]
    st.sidebar.table(df3.head(10))

def average_per_year(df_stadata):
    # 'Year' 列でグループ化し、各列の平均値を計算
    df_yearly_average = df_stadata.groupby('Year').mean()
    df_grouped_size = df_stadata.groupby('Year').size()
    df_yearly_average["Count"]=df_grouped_size
    return df_yearly_average

def average_per_month(df_stadata):
    # 'Year' 列でグループ化し、各列の平均値を計算
    df_monthly_average = df_stadata.groupby('Month').mean()
    df_grouped_size = df_stadata.groupby('Month').size()
    df_monthly_average["Count"]=df_grouped_size
    return df_monthly_average


def plot_distribution(df_stadata, selected_years, selected_score_type):
    # 選択された年のデータのみをフィルタリング
    df_filtered = df_stadata[df_stadata['Year'].isin(selected_years)]

    # 選択されたスコアタイプと'Year'でグループ化し、各'Year'の出現頻度を計算
    df_grouped = df_filtered.groupby([selected_score_type, 'Year']).size().unstack(fill_value=0)

    # 'Year'で降順にソート
    df_grouped = df_grouped.sort_index(axis=1, ascending=False)

    # 積み上げバーチャートを描画
    df_grouped.plot(kind='bar', stacked=True)

    plt.title(f'{selected_score_type} Distribution by Year')
    plt.xlabel(selected_score_type)
    plt.ylabel('Frequency')

    # 凡例が存在する場合のみ削除
    #legend = plt.legend()
    #if legend:
    #    legend.remove()

    st.pyplot(plt)

#def plot_score_distribution(df_stadata):
    # 'Year'と'Score'でグループ化し、各'Score'の出現頻度を計算
#    df_grouped = df_stadata.groupby(['Year', 'Score']).size().unstack(fill_value=0)

    # 積み上げバーチャートを描画
#    fig, ax = plt.subplots()
#    bar = ax.bar(df_grouped.index, df_grouped.values, stacked=True)

    # 各バーの色をグラデーションにする
#    for i in range(len(bar)):
#        bar[i].set_color(mcolors.CSS4_COLORS[list(mcolors.CSS4_COLORS.keys())[i]])

#    plt.title('Yearly Distribution of Score')
#    plt.xlabel('Year')
#    plt.ylabel('Frequency')

#    st.pyplot(fig)

def main_display(df,df_event,df_stadata):
    df_yearly_average = average_per_year(df_stadata)
    df_monthly_average = average_per_month(df_stadata)

    st.title("STATS")
    #with st.expander(f"For Developping"):
    #    st.dataframe(df)
    
    with st.expander(f"年ごとのScore分布"):
        # 年の一覧を取得
        years = sorted(df_stadata['Year'].unique())

        # 最新の3年を取得
        latest_years = years[-3:]

        # ユーザーに年を選択させる（初期選択は最新の3年）
        selected_years = st.multiselect('Select years', options=years, default=latest_years)

        # ユーザーにスコアタイプを選択させる
        score_types = ['Score', 'Out', 'In']
        selected_score_type = st.radio('Select score type', options=score_types, index=0, horizontal=True)

        # 選択された年とスコアタイプに基づいてバーチャートを描画
        plot_distribution(df_stadata, selected_years, selected_score_type)

    DT_event, DT_stats, DT_year, DT_month = st.tabs(["event","Stats","year","month"])
    with DT_event:
        st.dataframe(df_event.style.background_gradient(cmap="Greens"),hide_index=True)

    with DT_stats: #st.expander(f"Stats表示"):
        st.dataframe(df_stadata.style.background_gradient(cmap="Blues"),hide_index=True)
    
    with DT_year: #st.expander(f"年ごとの集計"):
        st.dataframe(df_yearly_average.style.background_gradient(cmap="Oranges"))

    with DT_month: #st.expander(f"月ごとの集計"):
        st.dataframe(df_monthly_average.style.highlight_max(axis=0))



def main():
    df,df_event,df_stadata = pickup_frame()
    # "Gon-Patt+36nu"列を追加し、処理を行う
    #df_stadata["Gon-Patt+36nu"] = pd.to_numeric(df_stadata["Gon-Patt+36"].str.replace(r'[^\d-]+', '', regex=True), errors='coerce') + 30
    #df_stadata["Gon-Patt+36nu"] = pd.to_numeric(df_stadata["Gon-Patt+36"].str.replace(r'[^\d-]+', '', regex=True), errors='coerce').fillna(0) - 1 + 30
    #df_stadata["Gon-Patt+36nu"] = pd.to_numeric(df_stadata["Gon-Patt+36"].str.extract(r'(\d+)').fillna(0), errors='coerce').astype(int) - 1 + 30
    #df_stadata["Gon-Patt+36nu"] = df_stadata["Gon-Patt+36"].astype(int) + 30
    df_stadata["Gon-Patt+36"] = pd.to_numeric(df_stadata["Gon-Patt+36"], errors='coerce').fillna(0).astype(int) + 30
    #df_stadata
    sidebar_display(df,df_event,df_stadata)
    main_display(df,df_event,df_stadata)
    


if __name__ == "__main__":
    main()