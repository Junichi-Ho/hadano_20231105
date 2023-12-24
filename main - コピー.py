import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import cf
import plotly.graph_objects as go
import matplotlib.image as mpimg

st.set_page_config(layout="wide")

def calculate_metrics(df, column, condition):
    df_filtered = df[df[column].str.contains(condition, case=False, na=False)]
    return df_filtered.shape[0]

def calculate_metrics_numeric(df, column, value):
    df_filtered = df[df[column] > value]
    return df_filtered.shape[0]

def filter_dataframe(df, column, condition):
    return df[df[column].str.contains(condition, case=False, na=False)]

def is_short_hole(hole):
    short_hole = (4,7,10,17) #タプルで宣言
    return hole in short_hole

@st.cache_data
def generate_sub_dataframe(hole, df_holef): 
    # 1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    countTOB = pd.DataFrame() if is_short_hole(hole) else filter_dataframe(df_holef, "TR", "OB")
    OBnumbers = countTOB.shape[0]

    # 2ndShotのOB数
    count2OB = filter_dataframe(df_holef, "GR", "OB")
    # GIRのGreenOnの数
    countGon = filter_dataframe(df_holef, "GR", "GO")
    lastdateOB = "なし" if OBnumbers == 0 else countTOB.iloc[0]["Date"] #countTOB.iat[0,12]

    return countTOB, count2OB, countGon, OBnumbers, lastdateOB

@st.cache_data
def generate_sub_dataframe_ODB(hole, df_holef):#DoubleBoggy以上
    # ホール番号とそれに対応する値をマッピングする辞書、(Boggy,Par-2,OBアイコン,Parアイコン)
    hole_dict = {
        (4, 7, 10, 17): (4, 2, ":o:", ":three:"),
        (6, 8, 14, 18): (6, 4, ":ok_woman:", ":five:"),
        "default": (5, 3, ":ok_woman:", ":four:")
    }

    # ホール番号に対応する値を取得
    for key, value in hole_dict.items():
        if isinstance(key, tuple) and hole in key:
            hole_value, PH_value, iconOB, iconp = value
            break
    else:
        hole_value, PH_value, iconOB, iconp = hole_dict["default"]

    # データフレームのフィルタリング
    temp_hole = df_holef[df_holef[str(hole)] > hole_value] # Double boggy以上をフィルタリング
    df_db_on = df_holef[df_holef["PH"] > PH_value] # Double boggy "ON"以上をフィルタリング

    # 最後の日付の取得
    lastdate = "なし" if temp_hole.empty else temp_hole.iloc[0]["Date"]

    return temp_hole, df_db_on, lastdate, iconOB, iconp

@st.cache_data
def generate_sub_dataframe_HP(hole, df_holef):# Holeの位置高さと3pattのデータフレームの作成
    # ホール番号とそれに対応するアイコンをマッピングする辞書
    hole_icon_dict = {
        (12, 5, 4, 7, 16, 17): ":full_moon_with_face:",
        (2, 9, 10, 15): ":first_quarter_moon_with_face:",
        "default": ":new_moon_with_face:"
    }

    # ホール番号に対応するアイコンを取得
    for key, icon in hole_icon_dict.items():
        if isinstance(key, tuple) and hole in key:
            icon_visible_green = icon
            break
    else:
        icon_visible_green = hole_icon_dict["default"]

    # ３Patt
    df_temp_hole = df_holef[df_holef["PN"] > 2]
    lastdate_3 = "なし" if df_temp_hole.empty else df_temp_hole.iat[0,12]

    return icon_visible_green, df_temp_hole, lastdate_3



def get_filtered_dataframe(df_holef, countGon, hole):
    df_to_show = df_holef
    short_hole = (4,7,10,17) #タプルで宣言

    if hole not in short_hole:
        df_holef_F = filter_dataframe(df_holef, "TR", "F")
        countGon_F = filter_dataframe(countGon, "TR", "F")

        FONFON = st.checkbox("Only FW keep")
        GONGON = st.checkbox("Only Green On")

        if FONFON and GONGON:
            df_to_show = countGon_F
        elif GONGON:
            df_to_show = countGon
        elif FONFON:
            df_to_show = df_holef_F

    return df_to_show

def show_dataframe(hole, df_holef, countGon):
    #データフレームをFirst Patt視点で表示
    df_to_show = get_filtered_dataframe(df_holef, countGon, hole)
    display_list = ["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]
    st.dataframe(df_to_show[display_list].style.background_gradient(cmap="Greens"),hide_index=True)

@st.cache_data
def reference_dataframe(df_h, thisyear, hole):#メトリクス 比較のためのReference作成
    df_ref = df_h[df_h["y"].str.contains(str(thisyear), case=False, na=False)]
    ref_num = df_ref.shape[0]
    short_hole = (4,7,10,17) #タプルで宣言

    if hole in short_hole:
        TOB = 0 #Shortholeの1打目のOB数は Green OnのShot結果に記載している
    else:
        TOB = calculate_metrics(df_ref, "TR", "OB") #TeeshotのOB数

    ref_OB = TOB + calculate_metrics(df_ref, "GR", "OB") #green on のOB数
    ref_paron = ref_num - calculate_metrics(df_ref, "GR", "GO") #FixMe ref_paronはParONしていない値なので間違いを生みそう
    ref_3patt = calculate_metrics_numeric(df_ref, "PN", 2) #3pattの数

    return ref_num, ref_OB, ref_paron, ref_3patt


@st.cache_data
def gauge_view(totalobnumbers,base,df_3patt,df_db_on):
    # ゲージチャートの値を計算
    totalobnumbers_value = totalobnumbers * 2 / base
    df_db_on_value = (df_db_on.shape[0] - totalobnumbers) * 2 / base
    df_3patt_value = df_3patt.shape[0] / base
    #other_value = 1.1 - totalobnumbers_value - df_db_on_value - df_3patt_value
    # ゲージチャートの作成
    gauge_steps = [
        {'range': [0, totalobnumbers_value], 'color': "pink"},
        {'range': [totalobnumbers_value, totalobnumbers_value + df_db_on_value], 'color': "indianred"},
        {'range': [totalobnumbers_value + df_db_on_value, totalobnumbers_value + df_db_on_value + df_3patt_value], 'color': "firebrick"},
        {'range': [totalobnumbers_value + df_db_on_value + df_3patt_value, 1.1], 'color': "white"}
    ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=totalobnumbers_value + df_db_on_value + df_3patt_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "主要因 : OBs : ダボオン : 3パット", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [None, 0.85], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "red"},
            'steps': gauge_steps,
            'threshold': {'line': {'color': "green", 'width': 4}, 'thickness': 0.75, 'value': 0.5}
        }
    ))

    # サイズの調整
    fig.update_layout(autosize=False, width=300, height=300, paper_bgcolor="white", font={'color': "darkblue", 'family': "Arial"})

    return fig

@st.cache_data
def ref_GIR_iron(df_holef,hole):
    # "Comment"列からr-yard:が含まれる要素を抜き取り、数値に変換して"残りヤード"列に追加
    df_holef["残りヤード"] = df_holef["Comment"].str.extract(r'r-yard:\s*(\d+)').astype(float)

    # 指定の列を含むデータフレームを作成
    df_holef_temp = df_holef[df_holef["残りヤード"].notnull()]
    # 残りヤードを整数型に変換
    df_holef_temp["残りヤード"] = df_holef_temp["残りヤード"].astype(int)
    df_holef_temp = df_holef_temp[["残りヤード","G","GR","SN","PN",str(hole),"TR","PP","Date"]]
    df_holef_temp = df_holef_temp.sort_values(by="残りヤード", ascending=False)
    df_holef_temp_GO = df_holef_temp[df_holef_temp["GR"] == "GO"]
    df_holef_temp_GO["SN"] = df_holef_temp_GO["SN"].astype(int)
    return df_holef_temp_GO

@st.cache_data
def plot_teeing_club(df_holef,hole):
    club_list = list(df_holef["T"].unique())
    # "T"の要素別に頻度ヒストグラムを作成
    fig, ax = plt.subplots(figsize=(3, 3))
    for club in club_list:
        data = df_holef[df_holef["T"] == club][str(hole)]
        ax.hist(data, bins=15, alpha=0.5, label=club)
    ax.legend()

    return(club_list,fig)

@st.cache_data
def plot_teeing_club2(select_club,df_holef,hole): 
    # 選択されたTの要素=クラブのScoreヒストグラムを作成
    df_temp_bante = df_holef[df_holef["T"].isin([select_club])]
    fig3, ax3 = plt.subplots(figsize=(3,3))
    ax3.hist(df_temp_bante[str(hole)],bins=15,color="red")

    return(df_temp_bante,fig3)

def hole_selection():
    # イン アウト選択により絞り込む 
    out_in = st.radio("Out / In",("Out","In"), horizontal=True)
    # 選択に応じてホールのリストを変更
    hole_list = (1,2,3,4,5,6,7,8,9) if out_in == "Out" else (10,11,12,13,14,15,16,17,18)
    # ラジオボタンでホールを選択
    hole = st.radio(f"{out_in}", hole_list, horizontal=True)
    return hole

def the_latest_record(df):
    if st.sidebar.checkbox("最近のスコア表示"):
        st.sidebar.table(df[['Score','OB',"Out","In"]].head(10))

def selection_in_sidebar(df_h):
    # 年と月でフィルタリングするオプション
    for time_unit in ["y", "m"]:
        unit_list = list(df_h[time_unit].unique())
        default_list = ["23", "22"] if time_unit == "y" else unit_list
        selected_units = st.sidebar.multiselect(f"{time_unit}でFilterling", unit_list, default=default_list)
        df_h = df_h[df_h[time_unit].isin(selected_units)]

    return df_h

def detail_options(df_holef,hole,df_ODB,lastdateOB,OBnumbers,df_count2OB,df_countTOB,totalobnumbers,base,df_3patt,df_db_on):
    if(0): #function enabled/disabled option
        # 5 # #多様な深堀のためのデータ提供
        tabITG, tabIHN ,tabPP, tabHist, tabOBs, tab3P, tabdbs, tabmeter = st.tabs([" :man-golfing: "," :golf: "," :1234: "," :musical_score: ", " :ok_woman: ", " :field_hockey_stick_and_ball: ","DBon","meter"])
        with tabITG: #ホールイメージ TG00.png
            #reference GIRで使用する アイアンの過去良い軌跡
            df_holef_temp_GO = ref_GIR_iron(df_holef,hole)
            st.dataframe(df_holef_temp_GO[["残りヤード","G","SN","PN",str(hole),"TR","PP","Date"]].style.background_gradient(cmap="Blues"),hide_index=True)


            image = cf.green_image(str(hole),"TG")[0]
            caption = cf.green_image(str(hole),"TG")[1]
            st.image(image,caption=caption)


        with tabIHN: #グリーンイメージ HN00.png
            image = cf.green_image(str(hole),"HN")[0]
            caption = cf.green_image(str(hole),"HN")[1]
            st.image(image,caption=caption) 
            club_list = list(df_holef["G"].unique())
            # "T"の要素別に頻度ヒストグラムを作成
            fig, ax = plt.subplots(figsize=(3, 3))
            for club in club_list:
                data = df_holef[df_holef["G"] == club][str(hole)]
                ax.hist(data, bins=15, alpha=0.5, label=club)
            ax.legend()
            st.pyplot(fig, use_container_width=False)


            select_club = st.selectbox("Club選択",club_list)
            df_temp_bante = df_holef[df_holef["G"].isin([select_club])]
            fig3, ax3 = plt.subplots(figsize=(3,3))
            ax3.hist(df_temp_bante[str(hole)],bins=15,color="red")
            st.pyplot(fig3, use_container_width=False)
            df_temp_bante



        with tabPP: #PinポジでFilterするオプション　#Streamlitのマルチセレクト
            PP_list = list(df_holef["PP"].unique())
            #select_PP = st.multiselect("Pin PositionでFilterling",PP_list,default=PP_list)
            #df_holef = df_holef[(df_holef["PP"].isin(select_PP))]

            #文字列化 PP_listは整数なので、st.tabsに使えないので。
            str_list = [str(num) for num in PP_list]
            # タブの作成
            tabs = st.tabs(str_list)
            # 各タブにコンテンツを追加
            for i, tab in enumerate(tabs):
                with tab:
                    #st.write(f"This is the Dataframe filter by {str_list[0]}")
                    df_temp_hole = df_holef[df_holef["PP"] == PP_list[i] ]
                    st.write(f"数 {df_temp_hole.shape[0]}")
                    st.dataframe(df_temp_hole[["TR","Comment","G","GR","SN","PN",str(hole),"Date"]].style.background_gradient(cmap="Reds"),hide_index=True)

        with tabHist:# スコアの時系列図 
            subtab1, subtab2 = st.tabs(["chart","database"])
            with subtab1:
                st.caption("左が最新")
                df_areac = df_holef[[str(hole),"PN"]]
                st.line_chart(df_areac)
            with subtab2:
                st.write("DB On以上にフィルター")
                st.dataframe(df_ODB.style.background_gradient(cmap="Blues"),hide_index=True)

        with tabOBs:# OBの深堀 
            st.write(f":calendar:{lastdateOB}")
            st.metric(label="TeeingOB数",value=OBnumbers,)
            st.metric(label="2ndOB率",value=df_count2OB.shape[0],)
            df_countTOB
            #データフレーム表示
            with st.expander("データフレーム詳細"):
                st.write("データフレーム詳細")
                df_holef[[str(hole),"T","TR","GR","Comment","PP","SN","PN"]]

        with tab3P:# Pattの深堀 
            pattave = df_3patt["SN"].mean()
            patt3 = f"3 PATTの数 {df_3patt.shape[0]}  _ 3patt時の距離 {pattave:.2f} scatterchart"

            with st.expander(patt3):
                #グラフ設定 matplotlib
                fig, ax = plt.subplots()
                #scatter
                ax.scatter(
                    x=df_holef["SN"],
                    y=df_holef["PN"],
                    c=df_holef[str(hole)],
                    #c=df_holef[PP],
                    alpha=0.8,
                    #vmin=df_holef[str(hole)].min(),
                    #vmax=df_holef[str(hole)].max()
                    )
                st.pyplot(fig, use_container_width=True)

            #ヒストグラム
            with st.expander("1st Patt 残り歩数 ヒストグラム"):
                fig2, ax2 = plt.subplots()
                ax2.hist(df_holef["SN"],bins=30,)
                st.pyplot(fig2, use_container_width=True)

        with tabdbs:
            fig = gauge_view(totalobnumbers,base,df_3patt,df_db_on)
            # Streamlitでゲージチャートの表示
            st.plotly_chart(fig)
            df_db_on

        with tabmeter:
            club_list,fig = plot_teeing_club(df_holef,hole)
            st.pyplot(fig, use_container_width=False)

            select_club = st.selectbox("Club選択",club_list)
            df_temp_bante,fig3 = plot_teeing_club2(select_club,df_holef,hole)
            st.pyplot(fig3, use_container_width=False)
            st.dataframe(df_temp_bante)


def main():
    ### Start 基本データフレームの作成
    ######################
    #df_h = ホールにフィルター
    #df_holef = 年 月 PinPosition で Filterしたもの 
    ######################
    df = cf.main_dataframe()             #csvからデータフレームに取り込み
    hole = hole_selection()              #選択するホール番号
    df_h = cf.dataframe_by_hole(df,hole) #holeに関する情報にスライスし、データフレーム作成する。

    ######################
    # サイドバー表示      #
    #　sidebarを加える   #
    ######################
    the_latest_record(df) #最近のスコア表示
    #年や月でフィルタリングする。
    df_holef = selection_in_sidebar(df_h) #df_holef = 年 月 PinPosition で Filterしたもの 

    #############################
    ###ここから Subdataframeの生成
    #dataframeは 変数名に 必ず "df_" を加えることとする。
    #############################
    
    # fixme 要リファクタリング 3つのDatafleme 統合すべし

    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    df_countTOB,df_count2OB,df_countGon,OBnumbers,lastdateOB = generate_sub_dataframe(hole,df_holef)
    #overDBのデータフレーム、ダボオン以上 、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン
    df_ODB,df_db_on,lastdate,iconOB,iconp = generate_sub_dataframe_ODB(hole,df_holef)
    #グリーンが上にありピンが見えないホールなのかアイコン化する。
    icon_visible_green,df_3patt,lastdate_3 = generate_sub_dataframe_HP(hole,df_holef)

    #リファレンス 年間のデータを集計 年間ラウンド 年間OB Teeingのリザルト＋GIRのリザルトの合計のみ Hazard columnは含まず
    #GONしなかった数 3パットの数
    this_year = 23 #比較する年を記載する 2023年
    ref_num,ref_OB,ref_paron,ref_3patt = reference_dataframe(df_h,this_year,hole)

    ###################
    ### 表示       ####
    ###################
    # 1  # タイトルは、In/OUT Hole Number、回数 打数アベレージを記載
    bun_title = f"No.{str(hole)}  :golfer: {df_holef.shape[0]} {iconp} {df_holef[str(hole)].mean():.3f} "
    st.subheader(bun_title)

    #メトリクス
    base = df_holef.shape[0] if df_holef.shape[0] else 1000  # 分母で使用するので0にしない。
    totalobnumbers = OBnumbers + df_count2OB.shape[0]
    pattave = df_holef["PN"].mean()

    labelCB = f" patt {pattave:.2f}"
    meterG, percentageS, numberS = st.tabs([labelCB,":deer: ％",":deer: 数"])
    with meterG:
        fig = gauge_view(totalobnumbers,base,df_3patt,df_db_on)
        st.plotly_chart(fig)

    with percentageS:
       #アベレージ表示 （デフォルト）
        col1,col2,col3=st.columns((1,1,1))
        with col1:            
            dbon = (df_db_on.shape[0] - totalobnumbers) /base *100
            a = totalobnumbers/base*100
            b = ref_OB/ref_num*100
            st.metric(label=f"{iconOB} TOB {OBnumbers} : 2OB {df_count2OB.shape[0]}  __ DBon-2OB {dbon:.2f} %",value=f"{a:.1f}",delta=f"{b:.1f}")
            
        with col2:
            a = (df_holef.shape[0]-df_countGon.shape[0]-totalobnumbers)/(base-totalobnumbers)*100
            b = ref_paron/ref_num*100
            pattave=df_holef["SN"].mean()
            st.metric(
                label=f"{icon_visible_green} NOT GOn _ 1st Patt Ave {pattave:.2f}",
                value=f"{a:.1f}",delta=f"{b:.1f}")
            
        with col3:
            a = df_3patt.shape[0]/base*100
            b = ref_3patt/ref_num*100
            label = f":man-facepalming: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :calendar:{lastdate_3}"
            st.metric(label=label,value=f"{a:.1f}",delta=f"{b:.1f}")

    with numberS:
        #カウント表示
        col1,col2,col3=st.columns((1,1,1))
        with col1:
            dbon = df_db_on.shape[0] - totalobnumbers
            st.metric(label=f"{iconOB} TOB {OBnumbers} : 2OB {df_count2OB.shape[0]} : DBon-2OB {dbon}",value=totalobnumbers,delta=ref_OB)
            
        with col2:
            pattave=df_holef["SN"].mean()
            st.metric(
                label=f"{icon_visible_green} NOT GOn _ 1st Patt Ave {pattave:.2f}",
                value=df_holef.shape[0]-df_countGon.shape[0],delta=str(ref_paron))
            
        with col3:
            label = f":man-facepalming: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :field_hockey_stick_and_ball: :calendar:{lastdate_3}"
            st.metric(label=label,value=df_3patt.shape[0],delta=str(ref_3patt))

    # 3  # スコアのヒストグラム表示 
    if st.checkbox(f"Score_hist.: :skull: DB以上 {lastdate}"):
        fig, ax = plt.subplots()              #グラフ設定 matplotlib
        ax.hist(df_holef[str(hole)],bins=10,) #ヒストグラム
        st.pyplot(fig, use_container_width=True)

    # 4 # データフレーム表示
    with st.expander(f"Dataframe:ラウンド数は {str(df_holef.shape[0])} 回"):
        show_dataframe(hole,df_holef,df_countGon)




if __name__ == "__main__":
    main()
