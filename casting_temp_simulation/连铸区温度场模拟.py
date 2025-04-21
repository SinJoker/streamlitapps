import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("连铸区温度场模拟计算")

tab1, tab2, tab3 = st.tabs(["钢物性参数", "工艺及设备参数", "计算参数"])

with tab1:

    # 钢种物性参数数据
    steel_properties = {
        "高合金钢": {
            "lamda_s": 29.008,
            "lamda_m": 35.470,
            "lamda_l": 35.470,
            "c_s": 658.811,
            "c_m": 650,
            "c_l": 691.667,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
        "低合金钢": {
            "lamda_s": 31.333,
            "lamda_m": 41.270,
            "lamda_l": 41.270,
            "c_s": 665.311,
            "c_m": 700,
            "c_l": 743.5,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
        "中合金钢": {
            "lamda_s": 30.672,
            "lamda_m": 39.955,
            "lamda_l": 39.955,
            "c_s": 661.975,
            "c_m": 700,
            "c_l": 740.556,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 274950,
        },
        "包晶合金钢": {
            "lamda_s": 30.667,
            "lamda_m": 39.075,
            "lamda_l": 39.075,
            "c_s": 664.083,
            "c_m": 700,
            "c_l": 753.571,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
        "高碳钢": {
            "lamda_s": 29.008,
            "lamda_m": 35.470,
            "lamda_l": 35.470,
            "c_s": 658.811,
            "c_m": 650,
            "c_l": 691.667,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
        "低碳钢": {
            "lamda_s": 31.333,
            "lamda_m": 41.270,
            "lamda_l": 41.270,
            "c_s": 665.311,
            "c_m": 700,
            "c_l": 743.5,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
        "中碳钢": {
            "lamda_s": 30.672,
            "lamda_m": 39.955,
            "lamda_l": 39.955,
            "c_s": 661.975,
            "c_m": 700,
            "c_l": 740.556,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 274950,
        },
        "包晶钢": {
            "lamda_s": 31.041,
            "lamda_m": 41.700,
            "lamda_l": 41.700,
            "c_s": 663.641,
            "c_m": 700,
            "c_l": 740,
            "rho_s": 7600,
            "rho_m": 7400,
            "rho_l": 7200,
            "l_f": 270000,
        },
    }
    col1, col2 = st.columns([3, 7], gap="small", border=True)

    with col1:
        st.header("钢物性参数设置")
        # 定义预设元素
        preset_elements = {
            "Q235": {"C": 0.2, "Si": 0.35, "Mn": 1.40, "P": 0.045, "S": 0.05},
            "20#": {
                "C": 0.23,
                "Si": 0.37,
                "Mn": 0.65,
                "P": 0.035,
                "S": 0.035,
                "Cr": 0.25,
                "Ni": 0.30,
                "Cu": 0.25,
            },
            "奥氏体不锈钢(不锈钢304/316)": {"Cr": 20.0, "Ni": 12.0, "Mo": 3.0},
            "其它": {},
        }

        spec = st.selectbox("选择一个钢种：", list(preset_elements.keys()))

        # 初始化所有元素变量
        all_components = [
            "C",  # 碳 (Carbon)
            "Mn",  # 锰 (Manganese)
            "Si",  # 硅 (Silicon)
            "Cr",  # 铬 (Chromium)
            "Ni",  # 镍 (Nickel)
            "Mo",  # 钼 (Molybdenum)
            "V",  # 钒 (Vanadium)
            "W",  # 钨 (Tungsten)
            "Ti",  # 钛 (Titanium)
            "Al",  # 铝 (Aluminum)
            "Cu",  # 铜 (Copper)
            "B",  # 硼 (Boron)
            "N",  # 氮 (Nitrogen)
            "P",  # 磷 (Phosphorus)
            "S",  # 硫 (Sulfur)
        ]

        # 显式初始化所有元素百分比变量
        percent_C = percent_Mn = percent_Si = percent_Cr = percent_Ni = 0.0
        percent_Mo = percent_V = percent_W = percent_Ti = percent_Al = 0.0
        percent_Cu = percent_B = percent_N = percent_P = percent_S = 0.0

        # 设置预设元素的百分比并添加到selected_components
        if spec in preset_elements:
            # 按照all_components顺序添加元素
            for elem in all_components:
                if elem in preset_elements[spec]:
                    value = preset_elements[spec][elem]
                    globals()[f"percent_{elem}"] = value
                    # 如果元素不在已选列表中，则添加
                    if not any(
                        c["name"] == elem
                        for c in st.session_state.get("components", [])
                    ):
                        new_component = {"name": elem, "percentage": value}
                        if "components" not in st.session_state:
                            st.session_state.components = []
                        st.session_state.components.append(new_component)

        # 允许所有选项添加自定义成分
        selected_components = st.session_state.get("components", [])

        # 更新可用组件列表
        used_names = [comp["name"] for comp in selected_components]
        available_components = [c for c in all_components if c not in used_names]

        if st.button("添加成分"):
            if available_components:
                # 按照all_components顺序找到第一个可用的元素
                for elem in all_components:
                    if elem in available_components:
                        new_component = {"name": elem, "percentage": 0.0}
                        selected_components.append(new_component)
                        st.session_state.components = selected_components
                        st.rerun()
                        break

        for i, component in enumerate(selected_components):
            col1_sub, col2_sub, col3_sub = st.columns(
                [1, 1, 1], gap="small", vertical_alignment="bottom"
            )
            with col1_sub:
                # 为每个组件生成唯一ID
                if "id" not in component:
                    component["id"] = (
                        str(len(selected_components)) + "_" + str(id(component))
                    )

                # 确保当前组件名称在可用列表中
                current_name = component["name"]
                if current_name not in available_components:
                    available_components.insert(0, current_name)

                new_name = st.selectbox(
                    f"成分名称 {i+1}",
                    available_components,
                    index=available_components.index(current_name),
                    key=f"name_{component['id']}",
                )

                # 如果名称有变化，更新状态
                if new_name != current_name:
                    component["name"] = new_name
                    st.rerun()
            with col2_sub:
                component["percentage"] = st.number_input(
                    f"百分比 {i+1} %",
                    min_value=0.0,
                    value=component["percentage"],
                    step=0.01,
                    key=f"percentage_{id(component)}",
                )
                # 显式更新变量
                if new_name == "C":
                    percent_C = component["percentage"]
                elif new_name == "Mn":
                    percent_Mn = component["percentage"]
                elif new_name == "Si":
                    percent_Si = component["percentage"]
                elif new_name == "Cr":
                    percent_Cr = component["percentage"]
                elif new_name == "Ni":
                    percent_Ni = component["percentage"]
                elif new_name == "Mo":
                    percent_Mo = component["percentage"]
                elif new_name == "V":
                    percent_V = component["percentage"]
                elif new_name == "W":
                    percent_W = component["percentage"]
                elif new_name == "Ti":
                    percent_Ti = component["percentage"]
                elif new_name == "Al":
                    percent_Al = component["percentage"]
                elif new_name == "Cu":
                    percent_Cu = component["percentage"]
                elif new_name == "B":
                    percent_B = component["percentage"]
                elif new_name == "N":
                    percent_N = component["percentage"]
                elif new_name == "P":
                    percent_P = component["percentage"]
                elif new_name == "S":
                    percent_S = component["percentage"]
            with col3_sub:
                st.write("")  # 确保垂直对齐
                if st.button(
                    f"删除 {i+1}",
                    key=f"delete_{component['id']}",
                    use_container_width=True,
                ):
                    del selected_components[i]
                    st.session_state.components = selected_components
                    st.rerun()

        # 根据钢种设置默认index
        default_index = 5 if spec == "奥氏体不锈钢(不锈钢304/316)" else 0
        kind = st.selectbox(
            "钢的类型",
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
            index=default_index,
        )
    with col2:
        st.header("钢物性参数清单")

        # 更新可用组件列表
        used_names = [comp["name"] for comp in selected_components]
        available_components = [c for c in all_components if c not in used_names]

        # 计算液相线温度
        if kind in ["低碳钢", "中碳钢", "高碳钢"]:
            # 碳钢计算公式
            t_l = 1538 - (
                percent_C * 55
                + percent_C * percent_C * 80  # C²项
                + percent_Si * 13
                + percent_Mn * 4.8
                + percent_Cr * 1.5
                + percent_Ni * 4.3
                + percent_P * 30
                + percent_S * 20
            )
        elif kind == "高合金钢" and spec == "奥氏体不锈钢(不锈钢304/316)":
            # 其他钢种计算公式
            t_l = 1536.6 - (
                percent_C * 90
                + percent_Si * 8
                + percent_Mn * 5
                + percent_P * 30
                + percent_S * 25
                + percent_Al * 3
                + percent_Cr * 1.5  # 假设Cr的系数为0
                + percent_Mo * 2  # 假设Mo的系数为0
                + percent_Ti * 18  # 假设Mo的系数为0
                + percent_N * 80  # 假设Ni的系数为0
                + percent_Cu * 5  # 假设Cu的系数为0
            )

        # 计算固相线温度
        t_s = 1510 - (
            percent_C * 50
            + percent_Si * 7
            + percent_Mn * 4.5
            + percent_P * 25
            + percent_S * 20
            + percent_Al * 2.5
            + percent_Cr * 1.2
            + percent_Mo * 1.8
            + percent_Ti * 15
            + percent_N * 70
            + percent_Cu * 4
        )

        col2_subcol1, col2_subcol2 = col2.columns([1, 1], gap="medium")
        with col2_subcol1:
            # 显示当前钢种的物性参数表格
            st.write(f"{kind}物性参数:")
            props = steel_properties[kind]
            df = pd.DataFrame(
                {
                    "参数": [
                        "液相线温度",
                        "固相线温度",
                        "导热系数(s)",
                        "导热系数(m)",
                        "导热系数(l)",
                        "比热容(s)",
                        "比热容(m)",
                        "比热容(l)",
                        "密度(s)",
                        "密度(m)",
                        "密度(l)",
                        "潜热",
                    ],
                    "值": [
                        t_l,
                        t_s,
                        props["lamda_s"],
                        props["lamda_m"],
                        props["lamda_l"],
                        props["c_s"],
                        props["c_m"],
                        props["c_l"],
                        props["rho_s"],
                        props["rho_m"],
                        props["rho_l"],
                        props["l_f"],
                    ],
                    "单位": [
                        "℃",
                        "℃",
                        "W/(m·K)",
                        "W/(m·K)",
                        "W/(m·K)",
                        "J/(kg·K)",
                        "J/(kg·K)",
                        "J/(kg·K)",
                        "kg/m³",
                        "kg/m³",
                        "kg/m³",
                        "J/kg",
                    ],
                }
            )
            st.dataframe(df, hide_index=True, use_container_width=True)
        with col2_subcol2:
            st.write(f"{kind}几个随着温度变化的物性参数:")


with tab2:
    tab2_col1, tab2_col2, tab2_col3 = st.columns([3, 6, 14], border=True)

    with tab2_col1:
        st.subheader("结晶器参数")
        pouring_temp = st.number_input("浇筑温度(℃)", value=1550)
        casting_speed = st.number_input("拉坯速度(m/min)", value=1.2)
        heat_flux_factor = st.number_input("热流密度修正系数", value=1.0)
        width = st.number_input("断面宽度(mm)", value=200)
        thickness = st.number_input("断面厚度(mm)", value=20)
        steel_height = st.number_input("钢液高度(mm)", value=800)

    with tab2_col2:
        st.subheader("二冷区参数")
        zones = st.number_input("分区数目", min_value=1, max_value=10, value=5)

        water_flows = []
        water_temps = []
        for i in range(zones):
            col1, col2 = st.columns(2)
            with col1:
                water_flows.append(
                    st.number_input(
                        f"分区{i+1}冷却水量(L/min)",
                        key=f"flow_{i}",
                        value=30.0,
                        step=5.0,
                    )
                )
            with col2:
                water_temps.append(
                    st.number_input(
                        f"分区{i+1}冷却水温度(℃)", key=f"temp_{i}", value=10.0, step=2.0
                    )
                )

    with tab2_col3:
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
                    casting_speed,
                    heat_flux_factor,
                    width,
                    thickness,
                    steel_height,
                ],
                "单位": [
                    "m/min",
                    "-",
                    "mm",
                    "mm",
                    "mm",
                ],
            }
        )
        st.table(mold_params)

        st.subheader("二冷区结构")
        fig = go.Figure()

        # 添加水量柱状图
        fig.add_trace(
            go.Bar(
                x=list(range(1, zones + 1)),
                y=water_flows,
                name="冷却水量",
                marker_color="blue",
            )
        )

        # 添加温度折线图(使用次y轴)
        fig.add_trace(
            go.Scatter(
                x=list(range(1, zones + 1)),
                y=water_temps,
                name="冷却水温",
                line=dict(color="red"),
                yaxis="y2",
            )
        )

        # 更新布局
        fig.update_layout(
            title="二冷区冷却参数分布",
            xaxis_title="分区编号",
            yaxis_title="冷却水量(L/min)",
            yaxis=dict(showgrid=False),
            yaxis2=dict(
                title="冷却水温(℃)", overlaying="y", side="right", showgrid=False
            ),
            legend=dict(x=0.05, y=0.05, bgcolor="rgba(255,255,255,0.5)"),
        )

        st.plotly_chart(fig, use_container_width=True)

with tab3:
    tab3_col1, tab3_col2 = st.columns([0.15, 0.85], border=True)

    with tab3_col1:
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

    with tab3_col2:
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
