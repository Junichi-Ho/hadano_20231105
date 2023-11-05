import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

# CSVファイルの読み込み
csvfile = "20231104_HatanoScore.csv"

# Index ＝ Dateに。Dateは時間をとりたいがわからない。
df = pd.read_csv(csvfile)
df["Date"]=pd.to_datetime(df["Date"], format="mixed")

df["Year"] = df["Date"].apply(lambda x : x.strftime("%y"))
df["Month"] = df["Date"].apply(lambda x : x.strftime("%m"))
df = df.set_index("Date")

#
# サイドバー表示
#　sidebarを加える

#イン アウト選択により絞り込む （前中後にしたいが）
y = st.sidebar.radio("",("Out","In"))
if y == "Out" :
    hole = st.sidebar.selectbox(
    "Hole",[1,2,3,4,5,6,7,8,9]
    )
else:
    hole = st.sidebar.selectbox(
    "Hole",[10,11,12,13,14,15,16,17,18]
    )

#月絞り　未実装
#option = st.sidebar.selectbox(
#    "月で絞る(未実装)",[9,10,11,12]
#)
#st.sidebar.write("あなたが選んだのは",option,"月")

#最近のスコア表示
if st.sidebar.checkbox("最近のスコア表示"):
    df3 = df[['Score','OB',"Out","In"]]
    st.sidebar.write(df3)

###
###ここから
###
bun_title = str(hole) + "番ホールを表示"
st.caption(bun_title)



#x = st.slider("x")
#st.write(x, "xtimes2",2*x)

filter_hole = str(hole),"Teeing番手","結果","GIR番手","結果.1","Hazard","Pin位置","歩数","Patt数","Patt数.1"
Hole = str(hole)
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


df_hole = df[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN,"Year","Month"]]
#年でFilterするオプション
year_list = list(df_hole["Year"].unique())
#Streamlitのマルチセレクト
select_year = st.sidebar.multiselect("年でFilterling",year_list,default=year_list)
df_holef = df_hole[(df_hole["Year"].isin(select_year))]

#月でFilterするオプション
month_list = list(df_hole["Month"].unique())
#Streamlitのマルチセレクト
select_month = st.sidebar.multiselect("月でFilterling",month_list,default=month_list)
df_holef = df_holef[(df_holef["Month"].isin(select_month))]

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


col1,col2,col3=st.columns((1,1,1))
##メトリック表示
with col1:
    st.metric(
        label="TeeingOB率 Left(未実装)",
        value="12",
        delta="0.3"
    )
    st.metric(
        label="2ndOB率 Left(未実装)",
        value="12",
        delta="0.3"
    )
with col2:
    st.metric(
        label="TeeingOB率 Right(未実装)",
        value="12",
        delta="0.3"
    )
    st.metric(
        label="2ndOB率 Right(未実装)",
        value="12",
        delta="0.3"
    )
with col3:
    st.metric(
        label="ParOn率(未実装)",
        value="12",
        delta="0.3"
    )
    st.metric(
        label="FWKeep率(未実装)",
        value="12",
        delta="0.3"
    )





# スコアの時系列図
df_areac = df_holef[[str(hole),PN]]
st.area_chart(df_areac)

df_holef[[str(hole),Teeing,T_result,GIR,GIR_result,Haz,PP,SN,PN]]

#開発用 Index一覧
#df.columns



col1,col2=st.columns((1,1))
with col1:
    #Ｇｒｅｅｎの画像表示
    tim = "./pict/TG"+("0"+str(hole))[-2:]+".png"
    #st.sidebar.write(im)
    timage = Image.open(tim)

    st.image(timage, caption=tim[-6:-4])
    

with col2:
    map_data = pd.DataFrame(
        np.random.randn(1000,2)/[50,50] + [35.3894,139.20],
        columns=["lat","lon"]
    )

    st.map(map_data)

df

df2 = df[['Score','OB',"1"]]
df2

