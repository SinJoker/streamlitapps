import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("连铸区温度场模拟计算")

tab1, tab2, tab3 = st.tabs(["钢物性参数", "工艺及设备参数", "计算参数"])

with tab1:
    col1, col2 = st.columns([0.2, 0.8], border=True)

    with col1:
        st.subheader("钢种参数")
        steel_type = st.selectbox(
            "浇筑钢种",
            [
                "低碳钢",
                "中碳钢",
                "高碳钢",
                "低合金钢",
                "中合金钢",
                "高合金钢",
                "包晶钢",
                "包晶合金钢",
            ],
        )
        frequently_used = st.selectbox(
            "根据一些常用的钢种确定钢的成分",
            [
                "Q235",
                "20#",
                "不锈钢304",
            ],
        )
        liquidus_temp = st.number_input("液相线温度(℃)", value=1520)
        solidus_temp = st.number_input("固相线温度(℃)", value=1450)
        conductivity = st.number_input("热导率(W/m·K)", value=30.0)
        heat_capacity = st.number_input("比热容(J/kg·K)", value=750.0)
        density = st.number_input("密度(kg/m³)", value=7800.0)

    with col2:
        st.subheader("参数显示")
        steel_properties = pd.DataFrame(
            {
                "参数": [
                    "钢种",
                    # "浇筑温度",
                    "液相线温度",
                    "固相线温度",
                    "热导率",
                    "比热容",
                    "密度",
                ],
                "值": [
                    steel_type,
                    # f"{pouring_temp}℃",
                    f"{liquidus_temp}℃",
                    f"{solidus_temp}℃",
                    f"{conductivity} W/m·K",
                    f"{heat_capacity} J/kg·K",
                    f"{density} kg/m³",
                ],
            }
        )
        st.table(steel_properties)

with tab2:
    col1, col2, col3 = st.columns([0.15, 0.15, 0.7], border=True)

    with col1:
        st.subheader("结晶器参数")
        pouring_temp = st.number_input("浇筑温度(℃)", value=1550)
        casting_speed = st.number_input("拉坯速度(m/min)", value=1.2)
        heat_flux_factor = st.number_input("热流密度修正系数", value=1.0)
        width = st.number_input("断面宽度(mm)", value=200)
        thickness = st.number_input("断面厚度(mm)", value=20)
        steel_height = st.number_input("钢液高度(mm)", value=800)

    with col2:
        st.subheader("二冷区参数")
        zones = st.number_input("分区数目", min_value=1, max_value=10, value=5)

        water_flows = []
        water_temps = []
        for i in range(zones):
            water_flows.append(
                st.number_input(f"分区{i+1}冷却水量(L/min)", key=f"flow_{i}")
            )
            water_temps.append(
                st.number_input(f"分区{i+1}冷却水温度(℃)", key=f"temp_{i}")
            )

    with col3:
        st.subheader("参数显示")

        mold_params = pd.DataFrame(
            {
                "参数": [
                    "拉坯速度",
                    "热流密度修正系数",
                    "断面宽度",
                    "断面厚度",
                    "钢液高度",
                ],
                "值": [
                    f"{casting_speed} m/min",
                    heat_flux_factor,
                    f"{width} mm",
                    f"{thickness} mm",
                    f"{steel_height} mm",
                ],
            }
        )
        st.table(mold_params)

        st.subheader("二冷区结构")
        fig = px.bar(
            x=range(1, zones + 1),
            y=water_flows,
            labels={"x": "分区编号", "y": "冷却水量(L/min)"},
            title="二冷区冷却水量分布",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns([0.15, 0.85], border=True)

    with col1:
        st.subheader("计算设置")
        space_step = st.number_input("空间步长(mm)", value=5.0)
        time_step = st.number_input("时间步长(s)", value=0.1)

        if st.button("初始化计算"):
            st.session_state.initialized = True
            st.success("计算已初始化")

        if st.button("开始计算"):
            if "initialized" in st.session_state:
                st.session_state.calculated = True
                st.success("计算完成")
            else:
                st.warning("请先初始化计算")

    with col2:
        st.subheader("计算结果")

        if "calculated" in st.session_state:
            st.success("温度场计算结果")

            # 模拟温度场数据
            x = np.linspace(0, 200, 50)
            y = np.linspace(0, 800, 50)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(X / 10) * np.cos(Y / 10) * 100 + 1000

            fig = go.Figure(
                data=go.Contour(
                    z=Z, x=x, y=y, colorscale="Hot", colorbar=dict(title="温度(℃)")
                )
            )
            fig.update_layout(
                title="连铸坯温度场分布",
                xaxis_title="宽度方向(mm)",
                yaxis_title="高度方向(mm)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("请先完成计算")
