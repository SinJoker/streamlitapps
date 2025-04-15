import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

# 设置页面标题
st.title("钢坯二维导热计算")

# 定义材料的热物理参数
# 导热系数 (W/(m·K))
k = 40.0
# 比热容 (J/(kg·K))
c = 450.0
# 密度 (kg/m^3)
rho = 7800.0

# 定义计算区域的尺寸
# X方向长度 (m)
Lx = 0.5
# Y方向长度 (m)
Ly = 0.5

# 定义网格划分
# X方向网格数
Nx = 250
# Y方向网格数
Ny = 250

# 定义时间步长和总时间
# 时间步长 (s)
dt = 0.1
# 总时间 (s)
total_time = 1000.0

# 定义初始温度分布
# 初始温度 (K)
initial_temperature = 300.0

# 定义边界条件
# 左边界温度 (K)
left_boundary_temperature = 1000.0
# 右边界温度 (K)
right_boundary_temperature = 300.0
# 上边界温度 (K)
top_boundary_temperature = 1000.0
# 下边界温度 (K)
bottom_boundary_temperature = 300.0

# 定义空间步长
# X方向空间步长 (m)
dx = Lx / (Nx - 1)
# Y方向空间步长 (m)
dy = Ly / (Ny - 1)

# 定义热扩散系数
alpha = k / (rho * c)

# 定义初始温度场
T = np.full((Ny, Nx), initial_temperature)


# 定义边界条件函数
def apply_boundary_conditions(T):
    """
    应用边界条件到温度场
    """
    T[:, 0] = left_boundary_temperature
    T[:, -1] = right_boundary_temperature
    T[0, :] = top_boundary_temperature
    T[-1, :] = bottom_boundary_temperature


# 应用初始边界条件
apply_boundary_conditions(T)


# 定义微分方程右侧函数
def heat_equation(t, T_flat):
    """
    二维导热方程的右侧函数
    """
    T = T_flat.reshape((Ny, Nx))
    T_new = T.copy()

    for i in range(1, Ny - 1):
        for j in range(1, Nx - 1):
            T_new[i, j] = (
                T[i, j]
                + alpha * dt / dx**2 * (T[i, j + 1] - 2 * T[i, j] + T[i, j - 1])
                + alpha * dt / dy**2 * (T[i + 1, j] - 2 * T[i, j] + T[i - 1, j])
            )

    apply_boundary_conditions(T_new)
    return T_new.flatten()


# 定义时间点数组
t_eval = np.arange(0, total_time + dt, dt)

# 使用solve_ivp求解微分方程
sol = solve_ivp(heat_equation, [0, total_time], T.flatten(), t_eval=t_eval)

# 创建初始 plotly 图形
fig = go.Figure(data=[go.Heatmap(z=sol.y[:, 0].reshape((Ny, Nx)), colorscale="hot")])
fig.update_layout(
    title="时间: 0.00 s",
    xaxis_title="X (m)",
    yaxis_title="Y (m)",
    yaxis=dict(scaleanchor="x", scaleratio=1),
)

# 可视化结果
placeholder = st.empty()
for i, t in enumerate(t_eval):
    with placeholder.container():
        fig.data[0].z = sol.y[:, i].reshape((Ny, Nx))
        fig.update_layout(title=f"时间: {t:.2f} s")
        st.plotly_chart(fig, use_container_width=True)
