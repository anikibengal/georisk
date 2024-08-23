import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 設置頁面配置
st.set_page_config(
    layout='wide',
    page_title='GPR Index Dashboard'
)

# 隱藏Streamlit的預設頁腳和標題
st.markdown(
    """
    <style>
        footer {display: none}
        [data-testid="stHeader"] {display: none}
    </style>
    """, unsafe_allow_html=True
)

# 資料路徑
data_path = r'C:\Users\user\Desktop\GPR\data\latest_data.xlsx'
transposed_data_path = r'C:\Users\user\Desktop\GPR\data\transposed_data.xlsx'
data_gpr_daily_recent = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
#r'C:\Users\user\Desktop\GPR\data\data_gpr_daily_recent.xls'

# 設置儀表板標題
title_col, emp_col = st.columns([1, 0.2])

with title_col:
    st.markdown('<p class="dashboard_title">Geopolitical Risk (GPR) Index Dashboard</p>', unsafe_allow_html=True)


# 加載自定義CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 創建標籤頁
tab1, tab2 = st.tabs(["**Daily**", "**Country**"])


# 讀取資料
try:
    latest_data = pd.read_excel(data_path)
    transposed_data = pd.read_excel(transposed_data_path)
    gpr_daily = pd.read_excel(data_gpr_daily_recent)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# 取GPRD, GPRD_ACT, GPRD_THREAT, date欄位，並將date移到第一欄
gpr_daily = gpr_daily[['date', 'GPRD', 'GPRD_ACT', 'GPRD_THREAT']]

# 獲取最新日期的值和前一天的值
latest_row = gpr_daily.iloc[-1]
previous_row = gpr_daily.iloc[-2]

# 計算delta值
delta_gprd = latest_row['GPRD'] - previous_row['GPRD']
delta_gprd_act = latest_row['GPRD_ACT'] - previous_row['GPRD_ACT']
delta_gprd_threat = latest_row['GPRD_THREAT'] - previous_row['GPRD_THREAT']

# 在 "Daily" 標籤頁中放置 QQ_col 和 line_col
with tab1:
    QQ_col, line_col = st.columns([0.3, 1.5])

    with QQ_col:
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(f"Date:{latest_row['date'].strftime('%Y-%m-%d')}")
        st.metric(label="**GPRD**", value=f"{latest_row['GPRD']:.2f}", delta=f"{delta_gprd:.2f}", delta_color="inverse")
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        st.metric(label="**GPRD_ACT**", value=f"{latest_row['GPRD_ACT']:.2f}", delta=f"{delta_gprd_act:.2f}", delta_color="inverse")
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        st.metric(label="**GPRD_THREAT**", value=f"{latest_row['GPRD_THREAT']:.2f}", delta=f"{delta_gprd_threat:.2f}", delta_color="inverse")

    with line_col:
        # 過濾日期在2020年之後的數據
        gpr_daily_filtered = gpr_daily[gpr_daily['date'] >= '2024-01-01']

        # 繪製GPRD, GPRD_ACT, GPRD_THREAT的線圖
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=gpr_daily_filtered['date'], y=gpr_daily_filtered['GPRD'], mode='lines', name='GPRD'))
        fig.add_trace(go.Scatter(x=gpr_daily_filtered['date'], y=gpr_daily_filtered['GPRD_ACT'], mode='lines', name='GPRD_ACT'))
        fig.add_trace(go.Scatter(x=gpr_daily_filtered['date'], y=gpr_daily_filtered['GPRD_THREAT'], mode='lines', name='GPRD_THREAT'))

        fig.update_layout(
            title="GPR Daily Metrics (2024 and after)",
            legend_title="Metrics",
            margin=dict(l=20, r=20, t=40, b=20),
            colorway=px.colors.qualitative.Prism  # 可以更改為其他配色方案，如 Plotly, Dark2, Antique, Prism, Vivid
        )

        st.plotly_chart(fig, use_container_width=True)

# 在 "Country" 標籤頁中放置 chart_col 和 data_col
with tab2:
    chart_col, data_col = st.columns([1.6, 0.7])

    # 確保資料中有Country和GPR欄位
    if 'Country' in latest_data.columns and 'GPR' in latest_data.columns:
        with chart_col:
            # 繪製地圖
            try:
                fig = px.choropleth(latest_data.sort_values('GPR'), 
                                    locations="Country",
                                    locationmode='country names',
                                    color="GPR",
                                    hover_name="Country",
                                    color_continuous_scale=px.colors.sequential.Greens,
                                    custom_data=['Country', 'GPR'],
                                    labels={'GPR': 'GPR Index'},
                                    title="Monthly Geopolitical Risk (GPR) Index by Country")

                hovertemp = "<b><span style='font-size:20px;color:#A94438'>%{customdata[0]}</span></b><br>"
                hovertemp += "GPR Index: %{customdata[1]:.2f}<br>"
                fig.update_traces(hovertemplate=hovertemp)

                fig.update_layout(
                    title={
                        'text': "Monthly Geopolitical Risk (GPR) Index by Country",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    geo=dict(
                        showframe=False,
                        showcoastlines=True,
                        coastlinecolor="Black",
                        projection_type='miller'
                    ),
                    coloraxis_colorbar=dict(
                        title="GPR Index",
                        tickvals=[0, 20, 40, 60, 80, 100],
                        ticktext=["0", "20", "40", "60", "80", "100"]
                    ),
                    margin=dict(l=20, r=20, t=40, b=20),
                )

                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating map: {e}")
    else:
        st.error("Data does not contain 'Country' and 'GPR' columns.")

    # 格式化第2個到第14個列的表頭為YYYY-MM
    new_columns = []
    for i, col in enumerate(transposed_data.columns):
        if 1 <= i < 14:
            try:
                new_col = pd.to_datetime(col, errors='raise').strftime('%Y-%m')
            except (ValueError, TypeError):
                new_col = col
            new_columns.append(new_col)
        else:
            new_columns.append(col)
    transposed_data.columns = new_columns

    # 添加views_history列
    transposed_data['views_history'] = transposed_data.iloc[:, 1:14].apply(pd.to_numeric, errors='coerce').fillna(0).values.tolist()

    # 取第一欄和第14欄之後的欄位
    filtered_data = pd.concat([transposed_data.iloc[:, [0]], transposed_data.iloc[:, 13:]], axis=1)

    # 移除 MoM, YTD, YoY 欄位
    columns_to_remove = [filtered_data.columns[2], filtered_data.columns[3], filtered_data.columns[4], filtered_data.columns[5], filtered_data.columns[6]]
    filtered_data = filtered_data.drop(columns=columns_to_remove)

    # 隱藏索引並顯示資料表
    with data_col:
        st.dataframe(
            filtered_data,
            column_config={
                **{str(col): st.column_config.DateColumn(str(col), format="YYYY-MM") for col in transposed_data.columns[1:13]},
                "views_history": st.column_config.LineChartColumn(
                    "Views (past 12 months)", y_min=0
                ),
            },
            hide_index=True,
            height=470
        )