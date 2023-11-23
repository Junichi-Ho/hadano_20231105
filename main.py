import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime
import cf
import plotly.graph_objects as go

#@st.cache_data
#def green_image(holenum,pfile): #ホールごとのイメージの取り込み
#    im = "./pict/"+ pfile +("0"+holenum)[-2:]+".png"
#    #st.sidebar.write(im)
#    image = Image.open(im)
#    caption = im[-6:-4]
#    return image,caption

@st.cache_data 
def main_dataframe(csvfile): # Main Dataframe CSVファイルの読み込み
    # Index ＝ Dateに。Dateは時間をとりたいがわからない。
    df = pd.read_csv(csvfile)
    df["Date"]=pd.to_datetime(df["Date"], format="mixed")

    df["Year"] = df["Date"].apply(lambda x : x.strftime("%y"))
    df["Month"] = df["Date"].apply(lambda x : x.strftime("%m"))

    df["Date"]= df["Date"].dt.strftime("%y.%m.%d")
    #df = df.set_index("Date")
    return df

@st.cache_data
def dataframe_by_hole(df,hole): # ホールごとのデータフレームの作成
    #ホールごとの左のデータを成型する。 str(hole),"Teeing番手","結果","GIR番手","結果.1","Hazard","Pin位置","歩数","Patt数","Patt数.1"
    #ホールごとのデータフレーム df_holeの整形
    if hole > 1 :
        Teeing = "Teeing番手" + "." + str(hole-1)
        T_result = "結果" + "." + str((hole-1)*2)
        GIR = "GIR番手" + "." + str(hole-1)
        GIR_result = "結果" + "." + str((hole-1)*2+1)
        Haz = "Hazard" + "." + str(hole-1)
        PP = "Pin位置" + "." + str(hole-1)
        SN = "歩数" + "." + str(hole-1)
        PN = "Patt数" + "." + str((hole-1)*2)
        PH = "Patt数" + "." + str((hole-1)*2+1)
    else:
        Teeing = "Teeing番手"
        T_result = "結果"
        GIR = "GIR番手"
        GIR_result = "結果" + ".1" 
        Haz = "Hazard"
        PP = "Pin位置"
        SN = "歩数"
        PN = "Patt数"
        PH = "Patt数" + ".1"
    df_hole = df[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN,PH,"Year","Month","Date"]]
    rename_dict = {Teeing:"T",T_result:"TR",GIR:"G",GIR_result:"GR",Haz:"Comment",PP:"PP",SN:"SN",PN:"PN",PH:"PH","Year":"y","Month":"m"}
    df_hole = df_hole.copy()
    df_hole.rename(columns=rename_dict,inplace=True)
    return df_hole

@st.cache_data
def generate_sub_dataframe(hole,df_holef): #OB x2 、GIR Dataframe、Dateを作成
    #3つのDataframe,2つのデータ
    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    #TeeingShotのOB数
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        countTOB=0
        OBnumbers=0
        #OBnumbers_latest=0
    else:
        countTOB=df_holef[df_holef["TR"].str.contains("OB", case=False, na=False)]
        OBnumbers=countTOB.shape[0]
        #OBnumbers_latest=countTOB[countTOB["y"] == this_year].shape[0]
    #2ndShotのOB数
    count2OB=df_holef[df_holef["GR"].str.contains("OB", case=False, na=False)]
    #GIRのGreenOnの数 #ParOn率に変更予定
    countGon=df_holef[df_holef["GR"].str.contains("GO", case=False, na=False)]

    if OBnumbers == 0:
        lastdateOB = "なし"
    else:
        lastdateOB = countTOB.iat[0,11]
    #3つのDataframe,2つのデータ
    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    return(countTOB,count2OB,countGon,OBnumbers,lastdateOB)

@st.cache_data
def generate_sub_dataframe_ODB(hole,df_holef):#DoubleBoggy以上
    #DoubleBoggy以上
    #overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン 
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        temp_hole = df_holef[df_holef[str(hole)] > 4 ]
        df_db_on = df_holef[df_holef["PH"] > 2]
        iconOB = ":o:"
        iconp = ":three:"
    elif hole == 6 or hole == 8 or hole == 14 or hole == 18:
        temp_hole = df_holef[df_holef[str(hole)] > 6 ]
        df_db_on = df_holef[df_holef["PH"] > 4]
        iconOB = ":ok_woman:"
        iconp = ":five:"
    else:
        temp_hole = df_holef[df_holef[str(hole)] > 5 ]
        df_db_on = df_holef[df_holef["PH"] > 3]
        iconOB = ":ok_woman:"
        iconp = ":four:"

    if temp_hole.shape[0] == 0:
        lastdate = "なし"
    else:
        lastdate = temp_hole.iat[0,12] 

    #overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン 
    return(temp_hole,df_db_on,lastdate,iconOB,iconp)


@st.cache_data
def generate_sub_dataframe_HP(hole,df_holef):# Holeの位置高さと3pattのデータフレームの作成
    # Holeの位置高さ
    if hole == 12 or hole == 5 or hole == 4 or hole == 7 or hole == 16 or hole == 17 :
        icon_visible_green = ":full_moon_with_face:"
    elif hole == 2 or hole == 9 or hole == 10 or hole == 15 :
        icon_visible_green = ":first_quarter_moon_with_face:"
    else:
        icon_visible_green = ":new_moon_with_face:"

    # ３Patt
    #
    df_temp_hole = df_holef[df_holef["PN"] > 2 ]
    if df_temp_hole.shape[0] == 0:
        lastdate_3 = "なし"
    else:
        lastdate_3 = df_temp_hole.iat[0,12]

    return(icon_visible_green,df_temp_hole,lastdate_3)

#キャッシュ入れるとCheckboxの整合性が取れない警告出る。
def show_dataframe(hole,df_holef,countGon):
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        df_holef[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
    else:
        col1,col2=st.columns((1,1))
        with col1:
            FONFON = st.checkbox("Only FW keep")
        with col2:
            GONGON = st.checkbox("Only Green On")
        FONFON = int(FONFON)
        GONGON = int(GONGON) * 10
        showswitch = GONGON + FONFON
        df_holef_F=df_holef[df_holef["TR"].str.contains("F", case=False, na=False)]
        countGon_F=countGon[countGon["TR"].str.contains("F", case=False, na=False)]
        if showswitch == 11:
            countGon_F.shape[0]
            countGon_F[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        elif showswitch == 10:
            countGon.shape[0]
            countGon[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        elif showswitch == 1:
            df_holef_F.shape[0]
            df_holef_F[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]]
        else:
            st.dataframe(df_holef[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]].style.background_gradient(cmap="Greens"),hide_index=True)

@st.cache_data
def reference_dataframe(df_h,thisyear,hole):#メトリクス 比較のためのReference作成
    df_ref = df_h[df_h["y"].str.contains(str(thisyear),case=False,na=False)]
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        TOB = 0
    else:
        df_refOB = df_ref[df_ref["TR"].str.contains("OB", case=False, na=False)]
        TOB = df_refOB.shape[0] 
    df_ref2O = df_ref[df_ref["GR"].str.contains("OB", case=False, na=False)]
    df_refFW = df_ref[df_ref["GR"].str.contains("GO", case=False, na=False)]
    df_ref3P = df_ref[df_ref["PN"] > 2 ]
    ref_num = df_ref.shape[0]
    ref_OB = TOB + df_ref2O.shape[0]
    ref_paron = df_ref.shape[0]-df_refFW.shape[0]
    ref_3patt = df_ref3P.shape[0]
    return(ref_num,ref_OB,ref_paron,ref_3patt)

@st.cache_data
def gauge_view(totalobnumbers,base,df_3patt,df_db_on):
    # ゲージチャートの値を計算
    totalobnumbers_value = totalobnumbers * 2 / base
    df_db_on_value = (df_db_on.shape[0] - totalobnumbers) * 2 / base
    df_3patt_value = df_3patt.shape[0] / base
    other_value = 1.1 - totalobnumbers_value - df_db_on_value - df_3patt_value
    # ゲージチャートの作成
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = totalobnumbers_value + df_db_on_value + df_3patt_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Factor"},
        gauge = {
            'axis': {'range': [None, 0.8]},
            'steps' : [
                {'range': [0, totalobnumbers_value], 'color': "yellow"},
                {'range': [totalobnumbers_value, totalobnumbers_value + df_db_on_value], 'color': "yellowgreen"},
                {'range': [totalobnumbers_value + df_db_on_value, totalobnumbers_value + df_db_on_value + df_3patt_value], 'color': "lime"},
                {'range': [totalobnumbers_value + df_db_on_value + df_3patt_value, 1.1], 'color': "black"}],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0.5}
        }
    ))
    # サイズの調整
    fig.update_layout(autosize=False, width=300, height=300)
    return fig

def taihi():
    labelPinPosition = " ％ / 数 "+labelCB 
    if st.toggle(label=labelPinPosition):
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
    else:
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

def main():

    #ここからメイン

    ### Start 基本データフレームの作成
    st.set_page_config(layout="wide")
    df = cf.main_dataframe("20231104_HatanoScore.csv")
    
    #######################
    # サイドバー表示       #
    #　sidebarを加える    #
    ######################
    #df_h = ホールにフィルター
    #df_holef = 年 月 PinPosition で Filterしたもの 
    ######################
    #最近のスコア表示
    if st.sidebar.checkbox("最近のスコア表示"):
        df3 = df[['Score','OB',"Out","In"]]
        st.sidebar.table(df3.head(10))

    

    #イン アウト選択により絞り込む （前中後にしたいが）
    out_in = st.sidebar.radio("Out / In",("Out","In"), horizontal=True)
    if out_in == "Out" :
        #hole = st.sidebar.selectbox(
        #"Hole",[1,2,3,4,5,6,7,8,9]
        #)
        hole = st.sidebar.radio("Out = Par5_6, 8",(1,2,3,4,5,6,7,8,9), horizontal=True)
    else:
        hole = st.sidebar.radio("In = Par5_14,18",(10,11,12,13,14,15,16,17,18), horizontal=True)

    #holeに関する情報にスライスし、データフレーム作成する。
    df_h = dataframe_by_hole(df,hole)

    #年でFilterするオプション#Streamlitのマルチセレクト
    year_list = list(df_h["y"].unique())
    default_list = ["23","22"]
    select_year = st.sidebar.multiselect("年でFilterling",year_list,default=default_list)
    df_holef = df_h[(df_h["y"].isin(select_year))]

    #Ｇｒｅｅｎの画像表示
    #image = green_image(str(hole),"HN")[0]
    #caption = green_image(str(hole),"HN")[1]
    #st.sidebar.image(image,caption=caption)

    #PinポジでFilterするオプション　#Streamlitのマルチセレクト
    #PP_list = list(df_h["PP"].unique())
    #select_PP = st.sidebar.multiselect("Pin PositionでFilterling",PP_list,default=PP_list)
    #df_holef = df_holef[(df_holef["PP"].isin(select_PP))]

    #月でFilterするオプション　#Streamlitのマルチセレクト
    month_list = list(df_h["m"].unique())
    select_month = st.sidebar.multiselect("月でFilterling",month_list,default=month_list)
    df_holef = df_holef[(df_holef["m"].isin(select_month))]

    ####
    #hole =ホール integer
    #df_h = ホールにフィルター
    #df_holef = 年 月 PinPosition で Filterしたもの 
    #####

    ###
    ###ここから メイン表示
    ###
    ###

    ##

    #1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
    df_countTOB,df_count2OB,df_countGon,OBnumbers,lastdateOB = generate_sub_dataframe(hole,df_holef)
    #dataframeは後でわかるようにdf_に変えること

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
    bun_title = f"{out_in}{str(hole)}  :golfer: {df_holef.shape[0]} {iconp} {df_holef[str(hole)].mean():.3f} "
    st.subheader(bun_title)

    # 2  # メトリクス       
    if df_holef.shape[0]:
        base = df_holef.shape[0]
    else:
        base = 1000 #分母で使用するので0にしない。
    totalobnumbers = OBnumbers + df_count2OB.shape[0]

    pattave = df_holef["PN"].mean()
    labelCB = f" patt {pattave:.2f}"


    meterG, percentageS, numberS = st.tabs([labelCB,":deer: ％",":deer: 数"])
    with meterG:
        # Streamlitでゲージチャートの表示
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
    with st.expander(f"Score_hist.: :skull: DB以上 {lastdate}"):
        #グラフ設定 matplotlib
        fig, ax = plt.subplots()
        #ヒストグラム
        ax.hist(df_holef[str(hole)],bins=10,)
        st.pyplot(fig, use_container_width=True)

    # 4 # データフレーム表示
    with st.expander(f"Dataframe:ラウンド数は {str(df_holef.shape[0])} 回"):
        show_dataframe(hole,df_holef,df_countGon)

    # 5 # #多様な深堀のためのデータ提供
    tabdbs, tabITG, tabIHN ,tabPP, tabHist, tabOBs, tab3P, tabmeter = st.tabs(["DBon"," :man-golfing: "," :golf: "," :1234: "," :musical_score: ", " :ok_woman: ", " :field_hockey_stick_and_ball: ","meter"])
    with tabITG: #ホールイメージ TG00.png
        image = cf.green_image(str(hole),"TG")[0]
        caption = cf.green_image(str(hole),"TG")[1]
        st.image(image,caption=caption)

    with tabIHN: #グリーンイメージ HN00.png
        image = cf.green_image(str(hole),"HN")[0]
        caption = cf.green_image(str(hole),"HN")[1]
        st.image(image,caption=caption) 

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
        fig = gauge_view(totalobnumbers,base,df_3patt,df_db_on)
        # Streamlitでゲージチャートの表示
        st.plotly_chart(fig)

    ################ メモ 不採用ログ 過去ログ###############################################
    #df_holef.dtypes
    #df_holeS = df_holef[[PN,SN,str(hole)]]
    #df_holeS
    #st.scatter_chart(data = df_holeS,x=SN,y=PN,color=str(hole))
    #st.bar_chart(df_holeS,x=PN,y=SN)

    #if st.checkbox(label=labelCB):
        ##Ｇｒｅｅｎの画像表示
    #    image = green_image(str(hole),"HN")[0]
    #    caption = green_image(str(hole),"HN")[1]
    #    st.image(image,caption=caption)
    #    st.snow()

    # 5 # #PP別 データ提供
    #labelPinPosition = " PP別 解析_" + labelCB 
    #if st.toggle(label=labelPinPosition):


if __name__ == "__main__":
    main()
