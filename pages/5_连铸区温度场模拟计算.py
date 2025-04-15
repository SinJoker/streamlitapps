import streamlit as st

st.set_page_config(layout="wide")
st.title("连铸区温度场模拟计算")
tab1, tab2, tab3 = st.tabs(["🎢工艺及介质参数", "🧰设备参数", "▶️钢物性参数及计算条件"])

with tab1:  # process
    with st.form("工艺及介质参数设置"):
        process_kind = st.selectbox(
            "浇筑钢种",
            (
                "高碳钢",
                "中碳钢",
                "低碳钢",
                "高合金钢",
                "中合金钢",
                "低合金钢",
                "包晶钢",
                "包晶合金钢",
            ),
        )
        process_casting_temp = st.number_input(
            "浇筑温度 (℃)", min_value=1400.0, value=1520.0, step=10.0
        )
        process_casting_velocity = st.number_input(
            "拉坯速度 (m/min)", min_value=0.0, value=1.3, step=0.1
        )
        process_casting_convection_fix_K = st.number_input(
            "结晶器对流换热密度修正系数 ", min_value=0.0, value=1, step=0.1
        )

        submitted = st.form_submit_button("提交")
# with tab2:
#     with st.form("设备参数设置"):

# with tab3:
#     with st.form("钢物性参数及计算条件设置"):
