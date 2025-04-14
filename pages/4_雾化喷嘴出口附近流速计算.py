import streamlit as st
import math
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")
st.header("雾化喷嘴出口附近流速计算", divider="rainbow")
col1, col2 = st.columns([2, 8], border=True)

with col1:
    con1 = st.container()
    con1.caption("参数输入")
    velocity0 = con1.number_input(
        "水滴出口流速 (m/s)", min_value=0.0, value=1.0, step=1.0
    )
    rhoair = con1.number_input("大气密度 kg/m3", min_value=0.0, value=1.29, step=0.1)
    rhowater = con1.number_input(
        "水滴密度 kg/m3", min_value=0.0, value=1000.0, step=100.0
    )
    diameterdrop = con1.number_input(
        "水滴直径 μm", min_value=50.0, value=150.0, step=10.0
    )
    fluxwater = (
        con1.number_input("喷淋水流量 L/min", min_value=1.0, value=10.0, step=5.0)
        / 1000
        / 60
    )
    con2 = st.container()
    length = con2.number_input(
        "需要查看的出口范围", min_value=0.0, value=300.0, step=10.0
    )

with col2:

    numbers_location = np.linspace(start=0, stop=length, num=100)
    locations = numbers_location.tolist()
    velocitys = []
    for i in range(len(locations)):
        velocitys.append(
            velocity0
            * math.exp(
                -0.33
                * (rhoair / rhowater)
                * locations[i]
                / 1000
                * diameterdrop
                / 1000000
                / fluxwater**2
            )
        )

    fig = px.line()
    fig.add_scatter(x=locations, y=velocitys, name="流速（m/s）")
    fig.update_layout(title="出口流速随位置的变化关系(m/s)", height=550)
    st.plotly_chart(fig)
