import streamlit as st

st.set_page_config(layout="wide")
st.header("钢物性参数")
col1, col2 = st.columns([3, 7])

with col1:
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
                    c["name"] == elem for c in st.session_state.get("components", [])
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
        col1, col2, col3 = st.columns(
            [1, 1, 1], gap="small", vertical_alignment="bottom"
        )
        with col1:
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
        with col2:
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
        with col3:
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

st.write(f"液相线温度计算结果: {t_l:.1f}°C")

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

st.write(f"固相线温度计算结果: {t_s:.1f}°C")
