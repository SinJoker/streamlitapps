import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

# UI
st.title("连铸结晶器区域钢壳厚度计算")
cols1, cols2 = st.columns(2, border=True)
with cols1:
    st.header("参数设定", divider="rainbow")
    col1, col2, col3 = st.columns(3)
    with col1:
        c1 = st.container()
        c1.caption("钢的物性参数")
        rho = c1.number_input(
            "密度（kg/m3）", min_value=7000.0, value=7850.0, step=50.0
        )
        c = c1.number_input("比热容 (kJ/kgK)", min_value=0.1, value=0.77, step=0.10)
        mu = (
            c1.number_input("粘度*1000 (kg/ms)", min_value=1, value=455, step=10) / 1000
        )
        steel_lambda = c1.number_input(
            "导热系数（W/mk）", min_value=1.0, value=24.0, step=2.0
        )
        L = c1.number_input("固化潜热（kJ/kg）", min_value=10.0, value=210.0, step=10.0)
        deltaT = c1.number_input(
            "钢水过热度（℃）", min_value=0.0, value=30.0, step=10.0
        )
        lvelocity = c1.number_input(
            "钢液对坯壳的冲击速度（m/s）",
            min_value=0.4,
            max_value=1.2,
            value=0.6,
            step=0.1,
            help="通常在0.4~1.2 m/s 之间",
        )
    with col2:
        c2 = st.container()
        c2.caption("结晶器尺寸参数")
        area = c2.number_input(
            "和冷却水的换热面积（m2）",
            min_value=0.1,
            value=2.64,
            step=0.1,
            help="设计确定参数",
        )
        length = (
            c2.number_input(
                "结晶器出口距离弯月面距离（cm）",
                min_value=50.0,
                value=70.0,
                step=10.0,
                help="设计确定参数",
            )
            / 100
        )
        ck = c2.number_input(
            "结晶器冷却强度（L/（minmm））", min_value=0.0, value=2.0, step=0.2
        )
    with col3:
        c3 = st.container()
        c3.caption("钢的尺寸参数")
        width = c3.number_input("宽度（mm）", min_value=10.0, value=1400.0, step=10.0)
        thickness = c3.number_input(
            "厚度（mm）", min_value=10.0, value=250.0, step=10.0
        )
        c3.caption("工艺参数")
        velocity = (
            c3.number_input("拉坯速度（m/min）", min_value=0.1, value=1.4, step=0.1)
            / 60
        )
        waterdelatT = c3.number_input(
            "冷却水进出口温差（℃）", min_value=0.0, value=8.0, step=1.0
        )
        cw = c3.number_input("水比热容 (kJ/kgK)", min_value=0.0, value=4.18, step=0.1)
        rhow = c3.number_input(
            "水密度（kg/m3）", min_value=0.0, value=1000.0, step=50.0
        )

with cols2:
    st.header("计算结果")

    # 数据计算
    I = 2 * (width + thickness) * ck / 60 / 1000  # m3/s

    def ht(z):
        return (
            2
            / 3
            * rho
            * c
            * lvelocity
            * (c * mu / steel_lambda) ** (-2 / 3)
            * (z * lvelocity * rho / mu) ** (-1 / 2)
        ) * 10

    location = [0]
    ezdf = [0]
    htdf = []
    for z in np.arange(0.05, length + 0.01, 0.01):
        heat_transfer = ht(z)
        htdf.append(heat_transfer)
        heat_transfer_mean = np.mean(htdf)
        # heat_transfer_mean = 9021
        ez = (
            z
            / rho
            / L
            / velocity
            * (
                cw * I * rhow / area * waterdelatT
                - 2 * heat_transfer_mean / 1000 * (deltaT) ** 0.5
            )
        )
        # tolerance = 1e-6
        # if abs(z - 0.80) < tolerance:
        #     st.write("x:", round(z, 2), "ht", round(heat_transfer_mean, 2))
        location.append(z * 100)
        ezdf.append(round(ez / 2 * 1000, 2))
    # 数据整理与输出
    data_df = pd.DataFrame(
        {"从弯月面向下的距离（cm）": location, "钢壳厚度（mm）": ezdf}
    )
    tradition = 20 * (z / velocity / 60) ** 0.5
    fig = px.line(data_frame=data_df, x="从弯月面向下的距离（cm）", y="钢壳厚度（mm）")
    st.plotly_chart(fig)
    st.write(
        "按照上海宝钢凝固系数与传统凝固平方根定律计算结果，结晶器出口钢壳厚度为：",
        round(tradition, 2),
        "mm。",
        "与图表中的结果的误差为：",
        abs(
            round(
                (ezdf[-1] - tradition) / tradition * 100,
                2,
            )
        ),
        "%",
    )
    with st.popover("查看与下载计算结果", use_container_width=True):
        st.data_editor(
            data_df,
            column_config={
                "widgets": st.column_config.Column(
                    "Streamlit Widgets",
                    help="Streamlit **widget** commands 🎈",
                    width="medium",
                    required=True,
                )
            },
            hide_index=True,
            num_rows="dynamic",
        )
