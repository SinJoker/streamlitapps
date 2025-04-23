import matplotlib.pyplot as plt


def compute_temperatures(composition):
    """
    输入成分字典（例如：{'C': 0.1, 'Si': 0.2, ...}），返回不同公式的计算结果。
    支持的成分元素：C, Si, Mn, P, S, Ni, Cr, Mo, Cu, V, W, N, Al, Co, Fe等。
    """
    results = {"Liquidus": {}, "Solidus": {}}

    # 提取成分，缺失元素默认设为0
    def get_value(key):
        return composition.get(key, 0.0)

    # 常用元素提取
    C = get_value("C")
    Si = get_value("Si")
    Mn = get_value("Mn")
    P = get_value("P")
    S = get_value("S")
    Ni = get_value("Ni")
    Cr = get_value("Cr")
    Mo = get_value("Mo")
    Cu = get_value("Cu")
    V = get_value("V")
    W = get_value("W")
    N = get_value("N")
    Al = get_value("Al")
    Co = get_value("Co")
    Fe = get_value("Fe")

    # -------------------------- 液相线公式 --------------------------
    # 1. 经典公式（Mills & Cheng, 1996）
    results["Liquidus"]["Classic"] = (
        1538
        - 65 * C
        - 8 * Si
        - 5 * Mn
        - 30 * P
        - 25 * S
        - 4 * Ni
        - 2 * Mo
        - 2 * Cr
        - 4 * Cu
    )

    # 2. Li et al. (2020) 多元回归模型
    results["Liquidus"]["Li2020"] = (
        1535
        - 68 * C
        - 7.5 * Si
        - 6.2 * Mn
        - 28 * P
        - 22 * S
        - 5.1 * Cr
        - 3.8 * Ni
        - 3.0 * Mo
        - 1.9 * V
    )

    # 3. Wang et al. (2021) 机器学习辅助公式
    results["Liquidus"]["Wang2021"] = (
        1538 - 65 * C - 8 * Si - 5 * Mn + 0.5 * (Cr * Mo) - 2 * Ni
    )

    # 4. 奥氏体不锈钢公式（Ueshima et al.）
    results["Liquidus"]["Stainless_Austenitic"] = (
        1440 - 12 * Cr - 8 * Ni - 18 * Mo - 15 * Mn - 35 * C
    )

    # 5. 工具钢公式（Zhang et al., 2017）
    results["Liquidus"]["Tool_Steel"] = 1520 - 70 * C - 7 * Cr - 5 * V - 4 * W - 3 * Mo

    # 6. 双相不锈钢公式 (Sieurin et al., 2005)
    results["Liquidus"]["Duplex_Stainless"] = (
        1450 - 12 * Cr - 13 * Ni - 15 * Mn - 34 * C - 20 * Mo - 120 * N
    )

    # 7. 高碳钢公式 (Ohnaka, 1986)
    results["Liquidus"]["HighCarbon"] = (
        1536 - 90 * C - 8 * Si - 5 * Mn - 30 * P - 25 * S
    )

    # 8. 含铝钢公式 (Kubaschewski-Alcock, 1979)
    results["Liquidus"]["Al_Steel"] = (
        1538 - 65 * C - 8 * Si - 5 * Mn - 30 * P - 25 * S - 1.5 * Al
    )

    # 9. 高熵合金近似公式 (Guo et al., 2018)
    results["Liquidus"]["HighEntropy"] = (
        0.2 * (1538 - 65 * C)
        + 0.2 * (1495 - 30 * Co)
        + 0.2 * (1455 - 40 * Ni)
        + 0.2 * (1910 - 50 * Cr)
        + 0.2 * (1246 - 60 * Mn)
    )

    # -------------------------- 固相线公式 --------------------------
    # 1. 经典固相线公式（Mills & Cheng, 1996）
    results["Solidus"]["Classic"] = (
        1538
        - 200 * C
        - 12.3 * Si
        - 6.8 * Mn
        - 124 * P
        - 183 * S
        - 4.3 * Ni
        - 4.1 * Mo
        - 1.4 * Cr
        - 4.1 * Cu
    )

    # 2. 高合金钢近似公式
    results["Solidus"]["High_Alloy"] = 0.9 * results["Liquidus"]["Classic"]

    # 3. Smithells高合金钢公式 (1992)
    results["Solidus"]["Smithells"] = (
        1538 - 200 * C - 12.3 * Si - 6.8 * Mn - 183 * S - 4.1 * Ni - 4.1 * Mo
    )

    # 4. 双相不锈钢固相线 (Charles et al., 2010)
    results["Solidus"]["Duplex_Stainless"] = (
        1380 - 10 * Cr - 8 * Ni - 15 * Mn - 25 * C - 12 * Mo - 80 * N
    )

    # 5. 快速凝固合金模型 (Jones, 1982)
    results["Solidus"]["Rapid_Solidification"] = 0.85 * results["Liquidus"][
        "Classic"
    ] - 50 * (C**2)

    return results


def plot_temperature_comparison(results):
    """绘制横向柱状图对比不同公式的温度预测"""
    plt.figure(figsize=(18, 10))

    # 液相线绘图
    plt.subplot(1, 2, 1)
    liquids = results["Liquidus"]
    plt.barh(list(liquids.keys()), list(liquids.values()), color="skyblue")
    plt.title("Liquidus Temperature Comparison", fontsize=14, pad=20)
    plt.xlabel("Temperature (°C)", fontsize=12)
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # 固相线绘图
    plt.subplot(1, 2, 2)
    solids = results["Solidus"]
    plt.barh(list(solids.keys()), list(solids.values()), color="lightgreen")
    plt.title("Solidus Temperature Comparison", fontsize=14, pad=20)
    plt.xlabel("Temperature (°C)", fontsize=12)
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # 统一坐标轴范围
    all_temps = list(liquids.values()) + list(solids.values())
    margin = 0.1 * (max(all_temps) - min(all_temps))
    plt.subplot(1, 2, 1).set_xlim(min(all_temps) - margin, max(all_temps) + margin)
    plt.subplot(1, 2, 2).set_xlim(min(all_temps) - margin, max(all_temps) + margin)

    plt.tight_layout()
    plt.show()


# -------------------------- 示例用法 --------------------------
if __name__ == "__main__":
    # 示例1：低碳钢
    composition1 = {
        "C": 0.1,
        "Si": 0.2,
        "Mn": 0.5,
        "P": 0.01,
        "S": 0.005,
        "Cr": 0.3,
        "Ni": 0.1,
        "Mo": 0.05,
    }
    results1 = compute_temperatures(composition1)
    plot_temperature_comparison(results1)

    # 示例2：双相不锈钢
    composition2 = {"C": 0.03, "Cr": 22, "Ni": 5, "Mo": 3, "N": 0.15}
    results2 = compute_temperatures(composition2)
    plot_temperature_comparison(results2)

    # 示例3：高熵合金
    composition3 = {"Fe": 20, "Co": 20, "Ni": 20, "Cr": 20, "Mn": 20}
    results3 = compute_temperatures(composition3)
    plot_temperature_comparison(results3)
