import streamlit as st

st.set_page_config(layout="wide")
st.header("钢物性参数")
col1, col2 = st.columns(spec=[3, 7], border=True)

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

    # 初始化百分比变量
    for elem in all_components:
        globals()[f"percent_{elem}"] = 0.0

    # 设置预设元素的百分比
    if spec in preset_elements:
        for elem, value in preset_elements[spec].items():
            globals()[f"percent_{elem}"] = value

    # 允许所有选项添加自定义成分
    selected_components = st.session_state.get("components", [])

    # 更新可用组件列表
    used_names = [comp["name"] for comp in selected_components]
    available_components = [c for c in all_components if c not in used_names]

    if st.button("添加成分"):
        if available_components:
            new_component = {"name": available_components[0], "percentage": 0.0}
            selected_components.append(new_component)
            st.session_state.components = selected_components
            st.rerun()

    for i, component in enumerate(selected_components):
        col1, col2, col3 = st.columns(
            [3, 3, 2], gap="small", vertical_alignment="bottom"
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
            # 动态更新变量
            var_name = f"percent_{new_name.replace(' ', '_')}"
            globals()[var_name] = component["percentage"]
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
        index=0,
    )

# 更新可用组件列表
used_names = [comp["name"] for comp in selected_components]
available_components = [c for c in all_components if c not in used_names]

# 计算液相线温度
t_l = 1538 - (
    percent_C * 55
    + percent_Si * 13
    + percent_Mn * 4.8
    + percent_P * 30
    + percent_S * 30
    + percent_Cr * 1  # 假设Cr的系数为0
    + percent_Ni * 1  # 假设Ni的系数为0
    + percent_Cu * 1  # 假设Cu的系数为0
    + percent_Mo * 1  # 假设Mo的系数为0
)

# 动态添加自定义成分的系数
for comp in selected_components:
    var_name = f"percent_{comp['name'].replace(' ', '_')}"
    if var_name in globals():
        # 假设自定义成分的系数为0，可以根据需要调整
        t_l -= globals()[var_name] * 0

st.write(f"液相线温度计算结果: {t_l:.1f}°C")
