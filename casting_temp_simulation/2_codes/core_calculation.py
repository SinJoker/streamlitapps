import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_conductivity(T):

    conductivity = (0.45041 - 1.7057 / 10000 * T) * 100

    return conductivity


def get_density(T):

    density = (7.8137 - 3.3481 / 10000 * T) * 1000

    return density


def get_specific_heat(T):

    specific_heat = (0.10971 + 5.4016 / 100000 * T) * 4184
    # specific_heat = 0.10971 * 4184

    return specific_heat


def solve_transient_heat_conduction(
    Lx,
    Ly,
    nx,
    ny,
    h_top,
    h_right,
    T_inf_top,
    T_inf_right,
    dt,
    total_time,
    initial_temp=1550,  # 使用全局定义的初始温度
    tol=1e-6,  # 使用全局定义的容差
):
    """
    二维瞬态热传导问题求解（显式格式）

    参数:
        Lx, Ly: 区域长度和宽度 [m]
        nx, ny: x和y方向的网格数
        h_top, h_right: 对流换热系数 [W/(m²·K)]
        T_inf_top, T_inf_right: 环境温度 [K]
        dt: 时间步长 [s]
        total_time: 总模拟时间 [s]
        initial_temp: 初始温度 [K]
        tol: 收敛容差（用于稳态检测）
    """
    # 网格生成
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)
    x = np.linspace(0, Lx, nx)
    y = np.linspace(0, Ly, ny)
    X, Y = np.meshgrid(x, y)

    # 初始热扩散率检查（使用初始温度下的物性参数）
    k_init = get_conductivity(initial_temp)
    rho_init = get_density(initial_temp)
    cp_init = get_specific_heat(initial_temp)
    alpha_init = k_init / (rho_init * cp_init)
    Fo_x = alpha_init * dt / dx**2
    Fo_y = alpha_init * dt / dy**2
    if Fo_x > 0.5 or Fo_y > 0.5:
        raise ValueError(
            f"时间步长过大，需满足 Fourier数 <= 0.5 (当前 Fo_x={Fo_x:.2f}, Fo_y={Fo_y:.2f})"
        )

    # 初始化温度场
    T = np.zeros((ny, nx)) + initial_temp
    T_old = T.copy()

    # 时间步进
    n_steps = int(total_time / dt)
    time_history = []
    temp_history = []

    print(f"开始模拟，总时间步数: {n_steps}，总时间: {total_time}s")
    print(f"初始温度场: {initial_temp}℃")
    print(f"环境温度: 顶部={T_inf_top}℃，右侧={T_inf_right}℃")

    for n in range(n_steps):
        if n % 100 == 0 or n == n_steps - 1:
            k_min = get_conductivity(np.min(T))
            k_max = get_conductivity(np.max(T))
            print(f"\n时间步 {n}/{n_steps} (时间={n*dt:.2f}s)")
            print(f"温度范围: {np.min(T):.1f}℃ ~ {np.max(T):.1f}℃")
            print(f"导热系数范围: {k_min:.2f} ~ {k_max:.2f} W/(m·K)")
        T_old = T.copy()

        # 内部节点 - 显式离散
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                # 获取当前温度下的物性参数
                k = get_conductivity(T_old[j, i])
                rho = get_density(T_old[j, i])
                cp = get_specific_heat(T_old[j, i])
                alpha = k / (rho * cp)

                T[j, i] = T_old[j, i] + alpha * dt * (
                    (T_old[j, i + 1] - 2 * T_old[j, i] + T_old[j, i - 1]) / dx**2
                    + (T_old[j + 1, i] - 2 * T_old[j, i] + T_old[j - 1, i]) / dy**2
                )

        # 获取当前时间段的边界条件设置
        current_segment = next(
            (
                seg
                for seg in boundary_time_segments
                if seg["start"] <= n * dt < seg["end"]
            ),
            boundary_time_segments[-1],
        )
        current_type = current_segment["type"]

        # 边界条件处理
        # 底部 (对称边界)
        T[0, :] = T[1, :]
        # 左侧 (对称边界)
        T[:, 0] = T[:, 1]

        # 顶部边界
        j = ny - 1
        if current_type == "third_kind":
            # 第三类边界条件
            for i in range(1, nx - 1):
                k = get_conductivity(T[j, i])
                T[j, i] = (k * T[j - 1, i] + h_top * dy * T_inf_top) / (k + h_top * dy)
        else:
            # 第二类边界条件
            current_q = current_segment.get("q_top", q_top)
            for i in range(1, nx - 1):
                k = get_conductivity(T[j, i])
                T[j, i] = T[j - 1, i] + current_q * dy / k

        # 右侧边界
        i = nx - 1
        if current_type == "third_kind":
            # 第三类边界条件
            for j in range(1, ny - 1):
                k = get_conductivity(T[j, i])
                T[j, i] = (k * T[j, i - 1] + h_right * dx * T_inf_right) / (
                    k + h_right * dx
                )
        else:
            # 第二类边界条件
            current_q = current_segment.get("q_right", q_right)
            for j in range(1, ny - 1):
                k = get_conductivity(T[j, i])
                T[j, i] = T[j, i - 1] + current_q * dx / k

        # 角点处理
        k = get_conductivity(T[ny - 1, nx - 1])
        if current_type == "third_kind":
            T[ny - 1, nx - 1] = (
                k * (T[ny - 1, nx - 2] + T[ny - 2, nx - 1])
                + h_top * dy * T_inf_top
                + h_right * dx * T_inf_right
            ) / (2 * k + h_top * dy + h_right * dx)
        else:
            current_q_top = current_segment.get("q_top", q_top)
            current_q_right = current_segment.get("q_right", q_right)
            T[ny - 1, nx - 1] = (
                k * (T[ny - 1, nx - 2] + T[ny - 2, nx - 1])
                + current_q_top * dy
                + current_q_right * dx
            ) / (2 * k)

        # 记录时间和温度（可选）
        if n % 100 == 0:
            time_history.append(n * dt)
            temp_history.append(T.copy())

        # 稳态检测
        if np.max(np.abs(T - T_old)) < tol:
            print(f"\n稳态在 t = {n*dt:.2f}s 达到")
            print(f"最终温度范围: {np.min(T):.1f}℃ ~ {np.max(T):.1f}℃")
            break

    return X, Y, T, time_history, temp_history


# ====================== 模拟参数设置 ======================
# 几何参数
Lx = 82.5e-3  # x方向长度 [m]
Ly = 82.5e-3  # y方向长度 [m]
nx = 61  # x方向网格数 (建议奇数)
ny = 61  # y方向网格数 (建议奇数)

# 材料相变参数
initial_temp = 1550  # 初始温度 [℃]
liquid_temp = 1520  # 液相线温度 [℃]
solid_temp = 1450  # 固相线温度 [℃]
temp_size = liquid_temp - solid_temp  # 凝固区间大小

# 边界条件参数
boundary_type = "third_kind"  # "third_kind"或"second_kind"
h_top = 100.0  # 顶部对流换热系数 [W/(m²·K)] (第三类边界)
h_right = 100.0  # 右侧对流换热系数 [W/(m²·K)] (第三类边界)
T_inf_top = 10.0  # 顶部环境温度 [℃] (第三类边界)
T_inf_right = 10.0  # 右侧环境温度 [℃] (第三类边界)
q_top = 0.0  # 顶部热流密度 [W/m²] (第二类边界)
q_right = 0.0  # 右侧热流密度 [W/m²] (第二类边界)

# 时间参数
dt = 0.02  # 时间步长 [s] (需满足稳定性条件)
total_time = 5 * 60  # 总模拟时间 [s]
tol = 1e-6  # 稳态检测容差
# 从JSON文件加载边界条件配置
import json

try:
    with open("boundary_config.json", "r", encoding="utf-8") as f:
        boundary_config = json.load(f)
    boundary_time_segments = boundary_config["segments"]
    total_time = boundary_config["total_time"]
except FileNotFoundError:
    raise FileNotFoundError(
        "未找到boundary_config.json配置文件，" "请先运行boundary_config.py生成配置文件"
    )


# ====================== 参数说明 ======================
# 1. 网格数nx,ny建议取奇数以便有中心点
# 2. 时间步长dt需满足Fourier数<=0.5的稳定性条件
# 3. 初始温度应高于液相线温度
# 4. 对流换热系数h值影响冷却速率

# 求解
X, Y, T_final, time_history, temp_history = solve_transient_heat_conduction(
    Lx,
    Ly,
    nx,
    ny,
    h_top,
    h_right,
    T_inf_top,
    T_inf_right,
    dt,
    total_time,
    initial_temp,
)

# 创建对称的温度场
full_T = np.vstack((np.flipud(T_final), T_final))
full_T = np.hstack((np.fliplr(full_T), full_T))
full_X = np.hstack((-np.fliplr(X), X))
full_Y = np.vstack((-np.flipud(Y), Y))

# 创建plotly图形
fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        f"Final Temperature (t={total_time}s)",
        "Temperature at Center Point",
    ),
)

# 温度场等高线图
fig.add_trace(
    go.Contour(
        x=full_X[0, :],
        y=full_Y[:, 0],
        z=full_T,
        zmin=900,
        zmax=1600,
        colorscale="Jet",
        colorbar=dict(title="Temperature (℃)"),
        contours=dict(
            coloring="heatmap",
            start=liquid_temp,
            end=solid_temp,
            size=temp_size,
            showlabels=True,  # 显示等值线标签
            labelfont=dict(size=12, color="white"),  # 设置标签字体
            labelformat="%s℃",  # 设置标签格式
            # labels=["液相线", "固相线"],  # 自定义等值线标签
        ),
    ),
    row=1,
    col=1,
)
fig.update_xaxes(title_text="x (m)", row=1, col=1)
fig.update_yaxes(title_text="y (m)", row=1, col=1)

# 中心点温度变化曲线
center_i, center_j = 0, 0
center_temp = [T[center_i, center_j] for T in temp_history]
fig.add_trace(
    go.Scatter(x=time_history, y=center_temp, mode="lines", line=dict(color="red")),
    row=1,
    col=2,
)
fig.update_xaxes(title_text="Time (s)", row=1, col=2)
fig.update_yaxes(title_text="Temperature (℃)", row=1, col=2)

fig.update_layout(height=500, width=1000, showlegend=False)
fig.write_html("heat_conduction_2d.html")
fig.show()
