import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os


def setup_ui():
    """设置连铸区温度场模拟的UI界面"""
    st.set_page_config(layout="wide")
    st.title("连铸区温度场模拟计算")

    # 初始化session state
    if "components" not in st.session_state:
        st.session_state.components = []

    tab1, tab2, tab3 = st.tabs(["钢物性参数", "工艺及设备参数", "计算参数"])

    # 从json文件读取钢种物性参数和预设元素
    json_path = os.path.join(os.path.dirname(__file__), "steel_properties.json")
    with open(json_path, "r", encoding="utf-8") as f:
        steel_data = json.load(f)
        steel_properties = {
            k: v
            for k, v in steel_data.items()
            if k not in ["preset_elements", "all_components"]
        }
        preset_elements = steel_data["preset_elements"]
        all_components = steel_data["all_components"]

    with tab1:
        with st.form("steel_properties_form"):
            col1, col2 = st.columns([3, 7], gap="small", border=True)
            with col1:
                st.header("钢物性参数设置")
                spec = st.selectbox("选择一个钢种：", list(preset_elements.keys()))

                # 使用从JSON文件读取的元素列表

                # 初始化元素百分比字典
                element_percentages = {elem: 0.0 for elem in all_components}

                # 设置预设元素的百分比并添加到selected_components
                if spec in preset_elements:
                    # 按照all_components顺序添加元素
                    for elem in all_components:
                        if elem in preset_elements[spec]:
                            value = preset_elements[spec][elem]
                            element_percentages[elem] = value
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
                available_components = [
                    c for c in all_components if c not in used_names
                ]

                # 成分管理逻辑
                if st.button("添加成分") and available_components:
                    # 添加第一个可用元素
                    elem = next(
                        (e for e in all_components if e in available_components), None
                    )
                    if elem:
                        selected_components.append(
                            {
                                "name": elem,
                                "percentage": 0.0,
                                "id": f"{len(selected_components)}_{id(elem)}",
                            }
                        )
                        st.session_state.components = selected_components
                        st.rerun()

                # 显示和编辑现有成分
                for i, comp in enumerate(selected_components):
                    with st.container(border=True):
                        cols = st.columns([1, 1, 1], gap="small")

                        # 成分名称选择
                        with cols[0]:
                            current_name = comp["name"]
                            if current_name not in available_components:
                                available_components.insert(0, current_name)

                            new_name = st.selectbox(
                                f"成分名称 {i+1}",
                                available_components,
                                index=available_components.index(current_name),
                                key=f"name_{comp['id']}",
                            )
                            if new_name != current_name:
                                comp["name"] = new_name
                                st.rerun()

                        # 百分比输入
                        with cols[1]:
                            comp["percentage"] = st.number_input(
                                f"百分比 {i+1} %",
                                min_value=0.0,
                                value=comp["percentage"],
                                step=0.01,
                                key=f"percentage_{comp['id']}",
                            )
                            element_percentages[new_name] = comp["percentage"]

                        # 删除按钮
                        with cols[2]:
                            if st.button(
                                "🗑️ 删除成分",  # 使用图标代替文字
                                key=f"delete_{comp['id']}",
                                help=f"删除成分 {comp['name']}",
                                use_container_width=True,
                            ):
                                selected_components.pop(i)
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
                available_components = [
                    c for c in all_components if c not in used_names
                ]

                # 计算液相线温度(T_liquidus)
                # 使用元素百分比字典(element_percentages)获取各元素含量
                # 不同钢种采用不同的计算公式:
                if kind in ["低碳钢", "中碳钢", "高碳钢"]:
                    # 碳钢计算公式(来源:钢铁冶金学标准公式)
                    t_l = 1538 - (
                        element_percentages["C"] * 55  # 碳元素系数
                        + element_percentages["C"]
                        * element_percentages["C"]
                        * 80  # 碳元素二次项
                        + element_percentages["Si"] * 13  # 硅元素系数
                        + element_percentages["Mn"] * 4.8  # 锰元素系数
                        + element_percentages["Cr"] * 1.5  # 铬元素系数
                        + element_percentages["Ni"] * 4.3  # 镍元素系数
                        + element_percentages["P"] * 30  # 磷元素系数
                        + element_percentages["S"] * 20  # 硫元素系数
                    )
                elif kind == "高合金钢" and spec == "奥氏体不锈钢(不锈钢304/316)":
                    # 不锈钢专用计算公式(来源:不锈钢冶金特性研究)
                    t_l = 1536.6 - (
                        element_percentages["C"] * 90  # 碳元素系数(不锈钢中影响更大)
                        + element_percentages["Si"] * 8  # 硅元素系数
                        + element_percentages["Mn"] * 5  # 锰元素系数
                        + element_percentages["P"] * 30  # 磷元素系数
                        + element_percentages["S"] * 25  # 硫元素系数
                        + element_percentages["Al"] * 3  # 铝元素系数
                        + element_percentages["Cr"] * 1.5  # 铬元素系数(不锈钢关键元素)
                        + element_percentages["Mo"] * 2  # 钼元素系数
                        + element_percentages["Ti"] * 18  # 钛元素系数
                        + element_percentages["N"] * 80  # 氮元素系数
                        + element_percentages["Cu"] * 5  # 铜元素系数
                    )

                # 计算固相线温度(T_solidus)
                # 通用计算公式(适用于所有钢种)
                t_s = 1510 - (
                    element_percentages["C"] * 50  # 碳元素系数
                    + element_percentages["Si"] * 7  # 硅元素系数
                    + element_percentages["Mn"] * 4.5  # 锰元素系数
                    + element_percentages["P"] * 25  # 磷元素系数
                    + element_percentages["S"] * 20  # 硫元素系数
                    + element_percentages["Al"] * 2.5  # 铝元素系数
                    + element_percentages["Cr"] * 1.2  # 铬元素系数
                    + element_percentages["Mo"] * 1.8  # 钼元素系数
                    + element_percentages["Ti"] * 15  # 钛元素系数
                    + element_percentages["N"] * 70  # 氮元素系数
                    + element_percentages["Cu"] * 4  # 铜元素系数
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

            submited = st.form_submit_button("数据提交")
        if submited:
            st.rerun()
    # 工艺及设备参数 (tab2)
    with tab2:
        st.header("连铸工艺参数设置")
        col1, col2, col3 = st.columns([0.15, 0.15, 0.7])

        with col1:
            st.subheader("结晶器参数")
            casting_speed = st.number_input(
                "拉坯速度 (m/min)", min_value=0.1, value=1.2, step=0.1
            )
            heat_flow_factor = st.number_input(
                "热流密度修正系数", min_value=0.1, value=1.0, step=0.1
            )
            width = st.number_input("断面宽度 (mm)", min_value=100, value=1000, step=10)
            thickness = st.number_input(
                "断面厚度 (mm)", min_value=50, value=200, step=5
            )
            steel_height = st.number_input(
                "钢液高度 (mm)", min_value=100, value=500, step=10
            )
            mold_length = st.number_input(
                "结晶器高度 (mm)", min_value=700, value=1000, step=100
            )

        with col2:
            st.subheader("二冷区参数")
            spray_zones = st.number_input("分区数目", min_value=1, value=5, step=1)
            water_flows = [
                st.number_input(
                    f"分区{i+1}水量 (L/min)", min_value=0.0, value=20.0, step=1.0
                )
                for i in range(spray_zones)
            ]
            water_temps = [
                st.number_input(
                    f"分区{i+1}水温 (°C)", min_value=10.0, value=25.0, step=1.0
                )
                for i in range(spray_zones)
            ]

        with col3:
            st.subheader("参数显示")
            st.write(f"当前拉坯速度: {casting_speed} m/min")
            st.write(f"结晶器长度: {mold_length} mm")
            st.write("二冷区水量分配:")
            for i in range(spray_zones):
                st.write(f"分区{i+1}: {water_flows[i]} L/min, {water_temps[i]} °C")

            # 预留图形显示区域
            st.subheader("二冷区结构示意图")
            # st.image("placeholder.png")  # 替换为实际图像路径

    # 计算参数 (tab3)
    with tab3:
        st.header("计算控制参数")
        col1, col2 = st.columns([0.15, 0.85])

        with col1:
            st.subheader("计算设置")
            mesh_size = st.number_input("空间步长 (mm)", min_value=1, value=10, step=1)
            time_step = st.number_input(
                "时间步长 (s)", min_value=0.1, value=1.0, step=0.1
            )
            init_btn = st.button("初始化")
            calc_btn = st.button("开始计算")

        with col2:
            st.subheader("计算结果")
            # 预留热图显示区域
            st.write("结晶器进出口热图:")
            # st.image("placeholder.png")  # 替换为实际图像路径
            st.write("各二冷区分区热图:")
            # st.image("placeholder.png")  # 替换为实际图像路径

    return {
        "steel_properties": steel_properties,
        "tab1": tab1,
        "tab2": tab2,
        "tab3": tab3,
        "kind": kind,
        "t_l": t_l,
        "t_s": t_s,
        "casting_speed": casting_speed,
        "mold_length": mold_length,
        "spray_zones": spray_zones,
        "water_flow": water_flow,
        "spray_density": spray_density,
        "water_temp": water_temp,
        "mesh_size": mesh_size,
        "time_step": time_step,
        "max_iter": max_iter,
        "tolerance": tolerance,
        "auto_save": auto_save,
    }


setup_ui()
