import pandas as pd
import streamlit as st
import plotly.graph_objects as go

#pip install streamlit
#pip install openpyxl
#pip install

def load_and_prepare_data(file_path, sheet_name):
    # Excelシートを読み込む
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
    # 列名を変更
    df.columns = ['自己資本比率（％）' if '自己資本比率' in col else col for col in df.columns]
    # 自己資本の増減を計算
    df['自己資本増減（百万円）'] = df['自己資本（百万円）'].diff()
    return df

def plot_summary_table(df):
    # 必要な列を選択
    selected_columns = df[['年度', '売上高（百万円）', '営業益（百万円）', '最終益（百万円）', '修正1株益（円）', '修正1株配（円）']]
    st.write("サマリーテーブル")
    st.dataframe(selected_columns, hide_index=True)

def plot_final_profit_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['年度'], y=df['最終益（百万円）'], name='最終益（百万円）'))
    fig.update_layout(
        title_text='年度別 最終益（百万円）',
        xaxis_title='年度',
        yaxis_title='最終益（百万円）',
        barmode='group'
    )
    st.plotly_chart(fig)


def plot_data(df, sheet_name, y_axis_max):
    selected_columns = df[['年度', '総資産（百万円）','自己資本（百万円）', '自己資本比率（％）','剰余金（百万円）']]
    st.write(f"{sheet_name}シートのデータ")
    st.dataframe(selected_columns, hide_index=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['年度'], y=df['総資産（百万円）'], name='総資産（百万円）'))
    fig.add_trace(go.Bar(
        x=df['年度'], 
        y=df['自己資本（百万円）'], 
        name='自己資本（百万円）',
        text=[f'{delta}百万円<br>{rate}%' for delta, rate in zip(df['自己資本増減（百万円）'], df['自己資本比率（％）'])],
        textposition='outside',
        textfont=dict(size=14)
    ))
    fig.update_layout(
        yaxis=dict(range=[0, y_axis_max]),
        title_text=f'{sheet_name}: 年度別 総資本と自己資本',
        barmode='group'
    )
    st.plotly_chart(fig)

def select_company_and_load_data(position,df_company,file_path,sheet_names):
    selected_company = st.selectbox(
        f"{position}企業を選択してください",
        df_company["証券コード_企業名"],
        key=f"select_company_{position}"
    )
    selected_security_code=selected_company.split("_")[0]
    #st.write(f"選択された証券コード:{selected_security_code}")
    st.markdown(f"[株探ページリンク](https://kabutan.jp/stock/?code={selected_security_code})",unsafe_allow_html=True) 
    if selected_security_code in sheet_names:
        return load_and_prepare_data(file_path, selected_security_code), selected_security_code
    else:
        st.error(f"{selected_security_code}のデータは存在しません。")
        return None

def calculate_max_values(dfs):
    max_total_assets = max(df['総資産（百万円）'].max() for df in dfs if df is not None)
    max_equity = max(df['自己資本（百万円）'].max() for df in dfs if df is not None)
    return max(max_total_assets, max_equity) * 1.1

def display_financial_metrics(selected_security_code, df_index):
    # 選択された証券コードに対応する行を取得
    row = df_index[df_index['証券コード'] == int(selected_security_code)].iloc[0]
    # StreamlitのメトリクスでPER, PBR, 配当補正率を表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="PER", value=row["PER"])
    with col2:
        st.metric(label="PBR", value=row["PBR"])
    with col3:
        st.metric(label="配当補正率", value=f"{row['配当補正率']*100:.2f}%")
    
    st.write(f"株価:{row["現在値"]}")
    st.write(row["Note"])

def main():
    st.set_page_config(layout="wide")
    file_path = 'Comp_Camp.xlsx'
    # Indexシートを読み込む
    df_index = pd.read_excel(file_path, sheet_name='Index', header=1)
    df_index.dropna(subset=['証券コード'],inplace=True)
    df_index['証券コード'] = df_index['証券コード'].astype(int)
    # Streamlitのサイドバーにデータフレームを表示
    st.sidebar.write("企業リスト")
    st.sidebar.dataframe(df_index, hide_index=True)
    # 証券コードと企業名を結合して新しい列を追加
    df_company = df_index[['証券コード', '企業名']].copy()
    df_company['証券コード_企業名'] = df_company['証券コード'].astype(str) + '_' + df_company['企業名']
    sheet_names = pd.ExcelFile(file_path).sheet_names

    col1, col2 = st.columns(2)

    with col1:
        df_left, selected_security_code_left =select_company_and_load_data("左",df_company,file_path,sheet_names)
    with col2:
        df_right, selected_security_code_right =select_company_and_load_data("右",df_company,file_path,sheet_names)

    # main関数内での呼び出し例
    # df_indexを引数として渡す必要があるため、main関数内でこの関数を呼び出す
    with col1:
        display_financial_metrics(selected_security_code_left, df_index)
    with col2:
        display_financial_metrics(selected_security_code_right, df_index)
    col1, col2 = st.columns(2)

    # 新しい表とバーチャートを表示
    with col1:
        plot_summary_table(df_left)
        plot_final_profit_chart(df_left)

    with col2:
        plot_summary_table(df_right)
        plot_final_profit_chart(df_right)



    if df_left is not None and df_right is not None:
        y_axis_max = calculate_max_values([df_left,df_right])

    col1, col2 = st.columns(2)

    with col1:
        plot_data(df_left, selected_security_code_left, y_axis_max)

    with col2:
        plot_data(df_right, selected_security_code_right, y_axis_max)

if __name__ == "__main__":
    main()