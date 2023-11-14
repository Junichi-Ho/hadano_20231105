import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import datetime


# CSVファイルの読み込み
csvfile = "20231104_HatanoScore.csv"

# Index ＝ Dateに。Dateは時間をとりたいがわからない。
df = pd.read_csv(csvfile)
df["Date"]=pd.to_datetime(df["Date"], format="mixed")

df["Year"] = df["Date"].apply(lambda x : x.strftime("%y"))
df["Month"] = df["Date"].apply(lambda x : x.strftime("%m"))
#df = df.set_index("Date")

st.set_page_config(layout="wide")


#
# サイドバー表示
#　sidebarを加える
#

#最近のスコア表示
if st.sidebar.checkbox("最近のスコア表示"):
    df3 = df[['Score','OB',"Out","In"]]
    st.sidebar.write(df3)

#イン アウト選択により絞り込む （前中後にしたいが）
y = st.sidebar.radio("Out / In",("Out","In"), horizontal=True)
if y == "Out" :
    hole = st.sidebar.selectbox(
    "Hole",[1,2,3,4,5,6,7,8,9]
    )
else:
    hole = st.sidebar.selectbox(
    "Hole",[10,11,12,13,14,15,16,17,18]
    )


#多分いらない##########
filter_hole = str(hole),"Teeing番手","結果","GIR番手","結果.1","Hazard","Pin位置","歩数","Patt数","Patt数.1"
Hole = str(hole)
##############

####
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

#年でFilterするオプション
year_list = list(df_hole["Year"].unique())
default_list = ["23","22"]
#Streamlitのマルチセレクト
select_year = st.sidebar.multiselect("年でFilterling",year_list,default=default_list)
df_holef = df_hole[(df_hole["Year"].isin(select_year))]

#Ｇｒｅｅｎの画像表示
im = "./pict/HN"+("0"+str(hole))[-2:]+".png"
#st.sidebar.write(im)
image = Image.open(im)

st.sidebar.image(image, caption=im[-6:-4])

#PinポジでFilterするオプション
PP_list = list(df_hole[PP].unique())
#Streamlitのマルチセレクト
select_PP = st.sidebar.multiselect("Pin PositionでFilterling",PP_list,default=PP_list)
df_holef = df_holef[(df_holef[PP].isin(select_PP))]

#月でFilterするオプション
month_list = list(df_hole["Month"].unique())
#Streamlitのマルチセレクト
select_month = st.sidebar.multiselect("月でFilterling",month_list,default=month_list)
df_holef = df_holef[(df_holef["Month"].isin(select_month))]

###
###
###ここから
###
###


#x = st.slider("x")
#st.write(x, "xtimes2",2*x)

##メトリック表示
this_year = 2023 #比較する年を記載する
#TeeingShotのOB数
if hole == 17 or hole == 10 or hole == 4 or hole == 7:
    countTOB=0
    OBnumbers=0
    OBnumbers_latest=0
else:
    countTOB=df_holef[df_holef[T_result].str.contains("OB", case=False, na=False)]
    OBnumbers=countTOB.shape[0]
    OBnumbers_latest=countTOB[countTOB["Year"] == this_year].shape[0]
#2ndShotのOB数
count2OB=df_holef[df_holef[GIR_result].str.contains("OB", case=False, na=False)]
#GIRのGreenOnの数 #ParOn率に変更予定
countGon=df_holef[df_holef[GIR_result].str.contains("GO", case=False, na=False)]




pd.options.display.float_format = '{:.2f}'.format
bun_title = f"{str(hole)} 番ホール :golfer: {df_holef.shape[0]} 回 "
st.title(bun_title)

if OBnumbers == 0:
    lastdateOB = "なし"
else:
    lastdateOB = countTOB.iat[0,11]



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

#
# Holeの位置
#
if hole == 12 or hole == 5 or hole == 4 or hole == 7 or hole == 16 or hole == 17 :
    icon_visible_green = ":full_moon_with_face:"
else:
    icon_visible_green = ":new_moon_with_face:"


pd.options.display.float_format = '{:.2f}'.format
st.subheader(f"Score Average {iconp} {df_hole[str(hole)].mean()}")
st.write(f"DB以上:golf:{lastdate}")

#
# ３Patt
#
temp_hole = df_holef[df[PN] > 2 ]
if temp_hole.shape[0] == 0:
    lastdate = "なし"
else:
    lastdate = temp_hole.iat[0,11]

col1,col2,col3=st.columns((1,1,1))

with col1:
    totalobnumbers = OBnumbers + count2OB.shape[0]
    st.metric(
        label=f"{iconOB} OB 数",
        value=totalobnumbers,
    )
    with st.expander(f"TeeingOB {OBnumbers} :: 2nd OB {count2OB.shape[0]}"):
        st.text(f"最後のOBは、{lastdateOB}")
        st.metric(
            label="TeeingOB数",
            value=OBnumbers,
        )
        st.metric(
            label="2ndOB率",
            value=count2OB.shape[0],
        )

with col2:
    st.metric(
        label=f"{icon_visible_green} GreenOnしなかった数",
        value=df_holef.shape[0]-countGon.shape[0],
    )
    st.text(f"fairwaykeepできなかった数")
with col3:
    st.metric(
        label=":man-facepalming:3 Patt 数",
        value=temp_hole.shape[0],
    )
    st.text(f"1st Pattの平均{df_hole[SN].mean()}")
    st.text(f"最後の3pattは、{lastdate}")
    st.text(f"3patt時の距離{temp_hole[SN].mean()}")



# スコアの時系列図
with st.expander(f"Score時系列データ {df_holef[str(hole)].head(3)} "):
    df_areac = df_holef[[str(hole),PN]]
    st.line_chart(df_areac)

#開発用 Index一覧
#df.columns

#スコアのヒストグラム表示
with st.expander(f"Score_ヒストグラム:平均 {df_hole[str(hole)].mean()}"):
    #グラフ設定 matplotlib
    fig, ax = plt.subplots()

    #ヒストグラム
    ax.hist(df_holef[str(hole)],bins=10,)

    st.pyplot(fig, use_container_width=True)


#データフレーム表示
with st.expander(f"データフレーム:ラウンド数は {str(df_holef.shape[0])} 回"):
    filtercolumns = {PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"}
    if hole == 17 or hole == 10 or hole == 4 or hole == 7:
        df_holef[[PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"]]
    else:
        col1,col2=st.columns((1,1))
        with col1:
            FONFON = st.checkbox("Only FW keep")
        with col2:
            GONGON = st.checkbox("Only Green On")
        FONFON = int(FONFON)
        GONGON = int(GONGON) * 10
        showswitch = GONGON + FONFON
        df_holef_F=df_holef[df_holef[T_result].str.contains("F", case=False, na=False)]
        countGon_F=countGon[countGon[T_result].str.contains("F", case=False, na=False)]
        if showswitch == 11:
            countGon_F.shape[0]
            countGon_F[[PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"]]
        elif showswitch == 10:
            countGon.shape[0]
            countGon[[PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"]]
        elif showswitch == 1:
            df_holef_F.shape[0]
            df_holef_F[[PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"]]
        else:
            st.dataframe(df_holef[[PP,T_result,Haz,GIR,GIR_result,SN,PN,str(hole),"Date"]].style.background_gradient(cmap="Greens"),hide_index=True)

#df_holef.dtypes
#df_holeS = df_holef[[PN,SN,str(hole)]]
#df_holeS
#st.scatter_chart(data = df_holeS,x=SN,y=PN,color=str(hole))
#st.bar_chart(df_holeS,x=PN,y=SN)

with st.expander(f"patt_ScatterChart 3 PATTの数 {temp_hole.shape[0]}"):
    #グラフ設定 matplotlib
    fig, ax = plt.subplots()

    #scatter
    ax.scatter(
        x=df_holef[SN],
        y=df_holef[PN],
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
    ax2.hist(df_holef[SN],bins=30,)

    st.pyplot(fig2, use_container_width=True)

#データフレーム表示
st.write("データフレーム詳細")
df_holef[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN]]


col1,col2=st.columns((1,1))
with col1:
    #Ｇｒｅｅｎの画像表示
    tim = "./pict/TG"+("0"+str(hole))[-2:]+".png"
    #st.sidebar.write(im)
    timage = Image.open(tim)

    st.image(timage, caption=tim[-6:-4])
    

with col2:
    #Ｇｒｅｅｎの画像表示
    im = "./pict/HN"+("0"+str(hole))[-2:]+".png"
    #st.sidebar.write(im)
    image = Image.open(im)

    st.image(image, caption=im[-6:-4])
    #map_data = pd.DataFrame(
    #    np.random.randn(1000,2)/[50,50] + [35.3894,139.20],
    #    columns=["lat","lon"]
    #)
    #
    #st.map(map_data)


st.dataframe(df.style.background_gradient(cmap="Greens"),hide_index=True)

df2 = df[['Score','OB',"1"]]
df2

