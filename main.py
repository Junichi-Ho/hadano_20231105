import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime

@st.cache_data
def green_image(holenum,pfile):
    im = "./pict/"+ pfile +("0"+holenum)[-2:]+".png"
    #st.sidebar.write(im)
    image = Image.open(im)
    caption = im[-6:-4]
    return image,caption

@st.cache_data
def main_dataframe(csvfile):
    # CSVファイルの読み込み

    # Index ＝ Dateに。Dateは時間をとりたいがわからない。
    df = pd.read_csv(csvfile)
    df["Date"]=pd.to_datetime(df["Date"], format="mixed")

    df["Year"] = df["Date"].apply(lambda x : x.strftime("%y"))
    df["Month"] = df["Date"].apply(lambda x : x.strftime("%m"))

    df["Date"]= df["Date"].dt.strftime("%y.%m.%d")
    #df = df.set_index("Date")
    return df

@st.cache_data
def dataframe_by_hole(df,hole):
    #多分いらない##########
    filter_hole = str(hole),"Teeing番手","結果","GIR番手","結果.1","Hazard","Pin位置","歩数","Patt数","Patt数.1"
    Hole = str(hole)
    ##############

    if hole > 1 :
        Teeing = "Teeing番手" + "." + str(hole-1)
        T_result = "結果" + "." + str((hole-1)*2)
        GIR = "GIR番手" + "." + str(hole-1)
        GIR_result = "結果" + "." + str((hole-1)*2+1)
        Haz = "Hazard" + "." + str(hole-1)
        PP = "Pin位置" + "." + str(hole-1)
        SN = "歩数" + "." + str(hole-1)
        PN = "Patt数" + "." + str((hole-1)*2)
    else:
        Teeing = "Teeing番手"
        T_result = "結果"
        GIR = "GIR番手"
        GIR_result = "結果" + ".1" 
        Haz = "Hazard"
        PP = "Pin位置"
        SN = "歩数"
        PN = "Patt数"

    df_hole = df[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN,"Year","Month","Date"]]
    rename_dict = {Teeing:"T",T_result:"TR",GIR:"G",GIR_result:"GR",Haz:"Comment",PP:"PP",SN:"SN",PN:"PN","Year":"y","Month":"m"}
    df_hole.rename(columns=rename_dict,inplace=True)
    return df_hole

@st.cache_data
def generate_sub_dataframe(hole,df_holef):
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
def generate_sub_dataframe_ODB(hole,df_holef):
    #
    #DoubleBoggy以上
    #
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        temp_hole = df_holef[df[str(hole)] > 4 ]
        iconOB = ":o:"
        iconp = ":three:"
    elif hole == 6 or hole == 8 or hole == 14 or hole == 18:
        temp_hole = df_holef[df[str(hole)] > 6 ]
        iconOB = ":ok_woman:"
        iconp = ":five:"
    else:
        temp_hole = df_holef[df[str(hole)] > 5 ]
        iconOB = ":ok_woman:"
        iconp = ":four:"

    if temp_hole.shape[0] == 0:
        lastdate = "なし"
    else:
        lastdate = temp_hole.iat[0,11] 

    #overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン 
    return(temp_hole,lastdate,iconOB,iconp)


@st.cache_data
def generate_sub_dataframe_HP(hole,df_holef):
    #
    # Holeの位置
    #
    if hole == 12 or hole == 5 or hole == 4 or hole == 7 or hole == 16 or hole == 17 :
        icon_visible_green = ":full_moon_with_face:"
    elif hole == 2 or hole == 9 or hole == 10 or hole == 15 :
        icon_visible_green = ":first_quarter_moon_with_face:"
    else:
        icon_visible_green = ":new_moon_with_face:"

    #
    # ３Patt
    #
    df_temp_hole = df_holef[df_holef["PN"] > 2 ]
    if df_temp_hole.shape[0] == 0:
        lastdate_3 = "なし"
    else:
        lastdate_3 = df_temp_hole.iat[0,11]
    
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



#ここからメイン

### Start 基本データフレームの作成
st.set_page_config(layout="wide")
df = main_dataframe("20231104_HatanoScore.csv")

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
    hole = st.sidebar.selectbox(
    "Hole",[1,2,3,4,5,6,7,8,9]
    )
else:
    hole = st.sidebar.selectbox(
    "Hole",[10,11,12,13,14,15,16,17,18]
    )

#holeに関する情報にスライスし、データフレーム作成する。
df_h = dataframe_by_hole(df,hole)

#年でFilterするオプション#Streamlitのマルチセレクト
year_list = list(df_h["y"].unique())
default_list = ["23","22"]
select_year = st.sidebar.multiselect("年でFilterling",year_list,default=default_list)
df_holef = df_h[(df_h["y"].isin(select_year))]

#Ｇｒｅｅｎの画像表示
image = green_image(str(hole),"HN")[0]
caption = green_image(str(hole),"HN")[1]
st.sidebar.image(image,caption=caption)

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

##メトリック表示
this_year = 2023 #比較する年を記載する

#1st OBのデータフレーム、2nd OBのデータフレーム、GIRのGonのデータフレーム,OB数と最後のOBになった日付データ
countTOB,count2OB,countGon,OBnumbers,lastdateOB = generate_sub_dataframe(hole,df_holef)
#dataframeは後でわかるようにdf_に変えること

#overDBのデータフレーム、最後にたたいたダボの日付, OBのアイコン(Par3の場合1stOBないから)、ParNumberアイコン
df_ODB,lastdate,iconOB,iconp = generate_sub_dataframe_ODB(hole,df_holef)
#dataframeは後でわかるようにdf_に変えること

#グリーンが上にありピンが見えないホールなのかアイコン化する。
icon_visible_green,df_3patt,lastdate_3 = generate_sub_dataframe_HP(hole,df_holef)

###################
### 表示       ####
###################

#タイトルは、In/OUT Hole Number、回数 打数アベレージを記載
bun_title = f"{out_in}{str(hole)}  :golfer: {df_holef.shape[0]} {iconp} {df_holef[str(hole)].mean():.3f} "
st.subheader(bun_title)

pattave = df_holef["PN"].mean()
labelCB = f":golf: patt {pattave:.2f} _ :skull: DB以上 {lastdate}"
if st.checkbox(label=labelCB):
    ##Ｇｒｅｅｎの画像表示
    image = green_image(str(hole),"HN")[0]
    caption = green_image(str(hole),"HN")[1]
    st.image(image,caption=caption)
    
col1,col2,col3=st.columns((1,1,1))
with col1:
    totalobnumbers = OBnumbers + count2OB.shape[0]
    st.metric(label=f"{iconOB} OB 数",value=totalobnumbers,)
    st.write(f"TOB {OBnumbers} : 2OB {count2OB.shape[0]}")
    
with col2:
    st.metric(
        label=f"{icon_visible_green} GreenOnしなかった数",
        value=df_holef.shape[0]-countGon.shape[0],)
    pattave=df_holef["SN"].mean()
    st.write(f"1st Pattの平均 {pattave:.2f}")
    #st.text(f"fairwaykeepできなかった数")

with col3:
    st.metric(label=":man-facepalming:3 Patt 数",value=df_3patt.shape[0],)
    st.write(f" :calendar:{lastdate_3}")


#開発用 Index一覧
#df.columns

#スコアのヒストグラム表示
with st.expander(f"Score_ヒストグラム:平均 {df_holef[str(hole)].mean():.3f}"):
    #グラフ設定 matplotlib
    fig, ax = plt.subplots()

    #ヒストグラム
    ax.hist(df_holef[str(hole)],bins=10,)

    st.pyplot(fig, use_container_width=True)


#データフレーム表示
with st.expander(f"データフレーム:ラウンド数は {str(df_holef.shape[0])} 回"):
    show_dataframe(hole,df_holef,countGon)

#df_holef.dtypes
#df_holeS = df_holef[[PN,SN,str(hole)]]
#df_holeS
#st.scatter_chart(data = df_holeS,x=SN,y=PN,color=str(hole))
#st.bar_chart(df_holeS,x=PN,y=SN)

labelPinPosition = "Pin Position別 解析"
if st.checkbox(label=labelPinPosition):
    #PinポジでFilterするオプション　#Streamlitのマルチセレクト
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
            st.dataframe(df_temp_hole[["PP","TR","Comment","G","GR","SN","PN",str(hole),"Date"]].style.background_gradient(cmap="Greens"),hide_index=True)




tab1, tab15 ,tab2, tab3, tab4 = st.tabs([":man-golfing:",":golf:","Score", "OB", "3Patt"])

with tab1:
    image = green_image(str(hole),"TG")[0]
    caption = green_image(str(hole),"TG")[1]
    st.image(image,caption=caption)

with tab15:
    image = green_image(str(hole),"HN")[0]
    caption = green_image(str(hole),"HN")[1]
    st.image(image,caption=caption) 

with tab2:

    # スコアの時系列図
    with st.expander(f"Score時系列{df_holef[str(hole)].head(3)} "):
        st.caption("左が最新")
        df_areac = df_holef[[str(hole),"PN"]]
        st.line_chart(df_areac)


with tab3:
    st.write(f":calendar:{lastdateOB}")
    st.metric(label="TeeingOB数",value=OBnumbers,)
    st.metric(label="2ndOB率",value=count2OB.shape[0],)
    #データフレーム表示
    with st.expander("データフレーム詳細"):
        st.write("データフレーム詳細")
        df_holef[[str(hole),"T","TR","GR","Comment","PP","SN","PN"]]

with tab4:
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



