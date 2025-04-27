import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class HeatTransferCalculator:
    def __init__(self):
        """初始化换热系数计算器"""
        pass

    def mold_heat_flux(self, t):
        """计算结晶器热流密度
        参数:
            t: 在结晶器内的时间(s)
        返回:
            热流密度(kW/m²)
        """
        # 公式1: φ = A - B√t
        A = 2680  # kW/m²
        B = 276  # kW/m²·s^0.5
        return A - B * np.sqrt(t)

    def mold_heat_flux_alternative(self, Q_L, delta_T, B, v_g, L_M, Z):
        """计算结晶器热流密度(替代公式)
        参数:
            Q_L: 内弧铜板的通水量(m³/s)
            delta_T: 内弧铜板进出口水温差(℃)
            B: 板坯宽度(m)
            v_g: 拉坯速度(m/s)
            L_M: 结晶器有效长度(m)
            Z: 距离弯月面距离(m)
        返回:
            热流密度(kW/m²)
        """
        K1 = (3 * Q_L * delta_T * 4.18685) / (
            4 * B * (v_g**0.56) * (1 - np.exp(-1.5 * L_M))
        )
        return K1 * 2 * (v_g**0.56) * np.exp(-1.5 * Z) * 1e6

    def secondary_cooling_h(self, V, T_s, T_w, method="Mitsutsuka"):
        """计算二冷区换热系数
        参数:
            V: 水量密度(L/m²·s)
            T_s: 板坯表面温度(℃)
            T_w: 冷却水温度(℃)
            method: 计算方法选择
        返回:
            换热系数(kW/m²·K)
        """
        V = max(V, 0.001)  # 避免零或负值

        if method == "Mitsutsuka":
            # E.Mitsutsuka公式
            n = 0.7  # 0.65<n<0.75
            b = 0.0065  # 0.005<b<0.008
            h = (V**n) * (1 - b * T_w)

        elif method == "Shimada":
            # M.Shimada公式
            h = 1.57 * (V**0.55) * (1 - 0.0075 * T_w)

        elif method == "Miikar_0.276":
            # E.Miikar公式(0.276MPa)
            h = 0.0776 * V

        elif method == "Miikar_0.620":
            # E.Miikar公式(0.620MPa)
            h = 0.1 * V

        elif method == "Ishiguro":
            # M.Ishiguro公式
            h = 0.581 * (V**0.451) * (1 - 0.0075 * T_w)

        elif method == "Bolle_Moureou":
            # E.Bolle Moureou公式
            if 1 < V < 7 and 627 < T_s < 927:
                h = 0.423 * (V**0.556)
            elif 0.8 < V < 2.5 and 727 < T_s < 1027:
                h = 0.360 * (V**0.556)
            else:
                h = 0

        elif method == "Sasaki":
            # K.Sasaki公式(需要转换为kW/m²·K)
            h_kcal = 708 * (V**0.75) * (T_s**-1.2) + 0.116
            h = h_kcal * 1.163 / 1000  # 转换为kW/m²·K

        elif method == "Mizikar":
            # E.Mizikar公式
            h = 0.076 - 0.10 * V

        elif method == "Mizikar":
            # E.Mizikar公式 (单位已转换为kW/m²·K)
            h = (0.076 - 0.10 * V) * 1.163 / 1000  # kcal/m²·h·℃ → kW/m²·K

        elif method == "Sasaki":
            # K.Sasaki公式(需要转换为kW/m²·K)
            h_kcal = 708 * (V**0.75) * (T_s**-1.2) + 0.116
            h = h_kcal * 1.163 / 1000  # 转换为kW/m²·K

        elif method == "Concast":
            # Concast公式 (单位已转换为kW/m²·K)
            h_kcal = 0.875 * 5748 * (1 - 0.0075 * T_w) * (V**0.451)
            h = h_kcal * 1.163 / 1000  # 转换为kW/m²·K

        elif method == "BUIST":
            # BUIST公式 (单位已转换为kW/m²·K)
            if 4.5 < V < 20:
                h_kcal = 0.35 * V + 0.13
                h = h_kcal * 1.163 / 1000  # 转换为kW/m²·K
            else:
                h = 0

        elif method == "CaiKaike":
            # 蔡开科公式 (单位已转换为kW/m²·K)
            h_kcal = 2.25e4 * (1 - 0.00075 * T_w) * (V**0.55)
            h = h_kcal * 1.163 / 1000  # 转换为k W/m²·K

        elif method == "ZhangKeqiang":
            # 张克强公式(0.25MPa压力)
            if T_s == 900:
                h = 0.37 + 0.35 * (V**0.954)
            else:
                h = 0

        elif method == "Billet":
            # 方坯二次冷却区公式
            if T_s > 900:
                h = 1.095e12 * (T_s**-4.15) * (V**0.75)
            elif 500 < T_s <= 900:
                h = 3.78e3 * (T_s**-1.34) * (V**0.785)
            else:
                h = 3.78e3 * (500**-1.34) * (V**0.785)

        elif method == "Sasaki_K":
            # 佐佐木宽太郎公式(T_s=600~900℃)
            if 600 <= T_s <= 900:
                h_kcal = 2.293e8 * (V**0.616) * (T_s**-2.445)
                h = h_kcal * 1.163 / 1000
            elif 900 < T_s <= 1200:
                h_kcal = 2.830e7 * (V**0.75) * (T_s**-1.2)
                h = h_kcal * 1.163 / 1000
            else:
                h = 0

        elif method == "Concast_Journal":
            # Concast期刊公式(默认压力0.276MPa)
            h_kcal = 9.0 * (0.276**0.2) * (V**0.75)
            h = h_kcal * 1.163 / 1000

        elif method == "Tegurashi":
            # 手鸠俊雄公式(默认空气流量密度10 NL/m²·s, KT=1.0)
            W_a = 10  # NL/m²·s
            K_T = 1.0
            h_kcal = 280.56 * (W_a**0.1373) * (V**0.75) * K_T
            h = h_kcal * 1.163 / 1000

        elif method == "Nippon_Steel":
            # 新日铁PMD公式
            h_kcal = 9.0 * (V**0.85) + 100
            h = h_kcal * 1.163 / 1000

        elif method == "Okamura":
            # 冈村一男公式(默认va=21.5m/s, Th=293K)
            v_a = 21.5  # m/s
            T_h = 293  # K
            h_rad = 5.67e-8 * 0.8 * ((T_s + 273) ** 4 - T_h**4) / (T_s + 273 - T_h)
            h = (5.35 * (T_s**0.12) * (V**0.52) * (v_a**0.37) + h_rad) / 1000

        elif method == "Kashima":
            # 鹿岛3号板坯连铸机公式(默认va=20m/s, z=1)
            v_a = 20  # m/s
            z = 1
            h_kcal = 10**1.48 * (V**0.6293) * (T_s**-0.1358) * (v_a**0.2734) * z
            h = h_kcal * 1.163 / 1000

        elif method == "Hitachi":
            # 日立造船技报公式
            h_kcal = 70.4 * (V**0.31343)
            h = h_kcal * 1.163 / 1000

        elif method == "Muller_Jeachar":
            # H.Muller Jeachar公式 (单位已转换为kW/m²·K)
            # 默认uc=21.5m/s (11≤uc≤32m/s)
            uc = 21.5  # m/s
            h_kcal = 0.42 * (V**0.35) * (uc**0.5)
            h = h_kcal * 1.163 / 1000  # 转换为kW/m²·K

        else:
            raise ValueError(f"未知的计算方法: {method}")

        return max(h, 0)  # 确保非负

    def plot_heat_transfer(self):
        """绘制换热系数随水量密度变化的曲线"""
        V = np.linspace(0, 50, 100)  # 水量密度范围: 0-50 L/m²·s
        T_w = 20  # 默认冷却水温度20℃
        T_s = 1300  # 默认板坯表面温度900℃

        # 创建子图
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                "结晶器热流密度随时间变化",
                "二冷区换热系数随水量密度变化 (T_s=900℃, T_w=20℃)",
            ),
        )

        # 结晶器热流密度
        t = np.linspace(0, 60, 100)  # 时间范围: 0-60s
        phi = self.mold_heat_flux(t)
        fig.add_trace(
            go.Scatter(x=t, y=phi, name="结晶器热流密度", line=dict(color="blue")),
            row=1,
            col=1,
        )

        # 二冷区换热系数
        methods = [
            "Mitsutsuka",  # 0.65<n<0.75, 0.005<b<0.008, V=10~10.3
            "Shimada",  # 无明确范围限制
            "Miikar_0.276",  # 0<V<20.3
            "Miikar_0.620",  # 0<V<20.3
            "Ishiguro",  # 无明确范围限制
            "Bolle_Moureou",  # 1<V<7且627<T_s<927或0.8<V<2.5且727<T_s<1027
            "Mizikar",  # 0<V<20.3
            "Sasaki",  # 1.67<V<41.7且700<T_s<1200
            "Concast",  # 无明确范围限制
            "BUIST",  # 4.5<V<20
            "CaiKaike",  # 无明确范围限制
            "ZhangKeqiang",  # T_s=900℃, p_a=0.25MPa
            "Billet",  # 分温度区间
            "Sasaki_K",  # 600<=T_s<=900或900<T_s<=1200
            "Concast_Journal",  # 无明确范围限制
            "Tegurashi",  # 无明确范围限制
            "Nippon_Steel",  # 无明确范围限制
            "Okamura",  # 无明确范围限制
            "Kashima",  # 无明确范围限制
            "Hitachi",  # 无明确范围限制
            "Muller_Jeachar",  # 0.3≤V≤9.0且11≤uc≤32m/s
        ]
        colors = [
            "red",
            "green",
            "purple",
            "darkviolet",
            "darkorange",
            "dodgerblue",
            "cyan",
            "magenta",
            "yellow",
            "lime",
            "pink",
            "brown",
            "gray",
            "olive",
            "teal",
            "navy",
            "maroon",
            "gold",
            "silver",
            "indigo",
        ]

        # 创建有效范围掩码
        valid_ranges = {
            "Mitsutsuka": (10, 10.3),
            "Miikar_0.276": (0, 20.3),
            "Miikar_0.620": (0, 20.3),
            "Bolle_Moureou": (0.8, 7),  # 两个区间合并处理
            "Mizikar": (0, 20.3),
            "Sasaki": (1.67, 41.7),
            "Concast": (0, np.inf),
            "BUIST": (4.5, 20),
            "CaiKaike": (0, np.inf),
            "ZhangKeqiang": (0, np.inf),  # 仅T_s=900℃
            "Billet": (0, np.inf),  # 已在方法中处理
            "Sasaki_K": (0, np.inf),  # 已在方法中处理
            "Muller_Jeachar": (0.3, 9.0),  # uc默认取21.5m/s
        }

        for method, color in zip(methods, colors):
            h = []
            x_valid = []
            for v in V:
                # 检查水量密度是否在有效范围内
                if method in valid_ranges:
                    v_min, v_max = valid_ranges[method]
                    if v < v_min or v > v_max:
                        continue

                h_val = self.secondary_cooling_h(v, T_s, T_w, method)
                if h_val > 0:  # 只添加有效值
                    h.append(h_val)
                    x_valid.append(v)

            if x_valid:  # 只有有效数据时才添加曲线
                fig.add_trace(
                    go.Scatter(
                        x=x_valid,
                        y=h,
                        name=method,
                        line=dict(color=color),
                        hovertemplate="水量密度: %{x:.2f} L/m²·s<br>换热系数: %{y:.2f} kW/m²·K<extra></extra>",
                    ),
                    row=2,
                    col=1,
                )

        # 更新图表布局
        fig.update_layout(
            height=800,
            showlegend=True,
            font=dict(family="SimHei", size=12),
            title_text="连铸区换热系数分析",
        )

        # 更新x轴和y轴标签
        fig.update_xaxes(title_text="时间 (s)", row=1, col=1)
        fig.update_yaxes(title_text="热流密度 (kW/m²)", row=1, col=1)
        fig.update_xaxes(title_text="水量密度 (L/m²·s)", row=2, col=1)
        fig.update_yaxes(title_text="换热系数 (kW/m²·K)", row=2, col=1)

        return fig


# 示例用法
if __name__ == "__main__":
    calculator = HeatTransferCalculator()
    fig = calculator.plot_heat_transfer()
    fig.show()
