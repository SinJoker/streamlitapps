import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd


class h_vesus_w:
    def __init__(
        self,
        name,
        description,
    ):
        self.name = "水流密度对传热系数h的影响"
        self.description = "在二冷区，传热系数的数值有很多人进行了研究，给出了不同的实验关联式，以下是对各种实验关联式的汇总比较，方便读者使用。"

    def bohr(W, Ts, A=0.423, n=0.556):
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Ts, (int, float)):
                raise ValueError("W and Ts must be numeric values.")

            if not (1 <= W <= 7) or not (627 <= Ts <= 927):
                raise ValueError(
                    "W must be between 1 and 7, and Ts must be between 627 and 927."
                )

            # 计算并返回结果
            return A * W**n

        except ValueError as e:
            # 记录错误日志
            print(f"Error in bohr: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def moho(W, Ts, A=0.36, n=0.556):
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Ts, (int, float)):
                raise ValueError("W and Ts must be numeric values.")

            if not (0.8 <= W <= 2.5) or not (727 <= Ts <= 1027):
                raise ValueError(
                    "W must be between 0.8 and 2.5, and Ts must be between 727 and 1027."
                )

            # 计算并返回结果
            return A * W**n

        except ValueError as e:
            # 记录错误日志
            print(f"Error in moho: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def XGH(W, Tw, A=0.581, n=0.451):
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Tw, (int, float)):
                raise ValueError("W and Tw must be numeric values.")

            # 计算并返回结果
            return A * W**n * (1 - 0.0075 * Tw)

        except ValueError as e:
            # 记录错误日志
            print(f"Error in XGH: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def ZBTL(W, Ts, A=708, n=0.75):
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Ts, (int, float)):
                raise ValueError("W and Ts must be numeric values.")

            if not (1.67 <= W <= 41.7) or not (700 <= Ts <= 1200):
                raise ValueError(
                    "W must be between 1.67 and 41.7, and Ts must be between 700 and 1200."
                )

            # 计算并返回结果
            return (A * W**n * Ts ** (-1.2) + 0.116) * 4.187 / 3600 * 1000

        except ValueError as e:
            # 记录错误日志
            print(f"Error in ZBTL: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def Mihockel(W, A=0.0776, n=0.10):
        try:
            # 参数验证
            if not isinstance(W, (int, float)):
                raise ValueError("W must be numeric values.")

            if not (0 <= W <= 20.3):
                raise ValueError("W must be between 0 and 20.3.")

            # 计算并返回结果
            return A + W * n

        except ValueError as e:
            # 记录错误日志
            print(f"Error in Mihockel: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def Smit(W, Tw, A=1.57, n=0.55):  # kW/m^2/℃
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Tw, (int, float)):
                raise ValueError("W and Tw must be numeric values.")

            # 计算并返回结果
            return A * W**n * (1 - 0.0075 * Tw)

        except ValueError as e:
            # 记录错误日志
            print(f"Error in Smit: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e

    def Comcast(W, Tw, n=0.451):
        try:
            # 参数验证
            if not isinstance(W, (int, float)) or not isinstance(Tw, (int, float)):
                raise ValueError("W and Tw must be numeric values.")
            # 计算并返回结果
            return 0.875 * 5748 * (1 - 0.0075 * Tw) * W**n * 4.187 / 3600

        except ValueError as e:
            # 记录错误日志
            print(f"Error in Comcast: {e}")
            # 返回默认值或重新抛出异常
            return None  # 或者 raise e


# 常量
n = 20
Ts = 800


def makex(bottom_limit, top_limit, n=20):
    # 生成上下限之间均布的20个数
    numbers_bohr = np.linspace(bottom_limit, top_limit, n)
    # 转换为列表
    return numbers_bohr.tolist()


# bohr
x_bohr = makex(1, 7)
# bohr
y_bohr = []
for i in range(len(x_bohr)):
    y_bohr.append(h_vesus_w.bohr(W=x_bohr[i], Ts=800))

# moho
x_moho = makex(0.8, 2.5)
y_moho = []
for i in range(len(x_moho)):
    y_moho.append(h_vesus_w.moho(W=x_moho[i], Ts=800))

# XGH
x_xgh = makex(0, 41.7)
y_xgh = []
for i in range(len(x_xgh)):
    y_xgh.append(h_vesus_w.XGH(x_xgh[i], Tw=10))

# ZBTL
x_zbtl = makex(1.67, 41.7)
y_zbtl = []
for i in range(len(x_zbtl)):
    y_zbtl.append(h_vesus_w.ZBTL(x_zbtl[i], Ts=800))

# 米霍克尔
x_Mihockel = makex(0, 20.3)
y_Mihockel = []
for i in range(len(x_Mihockel)):
    y_Mihockel.append(h_vesus_w.Mihockel(x_Mihockel[i]))

x_Smit = makex(0, 41.7)
y_Smit = []
for i in range(len(x_Smit)):
    y_Smit.append(h_vesus_w.Smit(x_Smit[i], Tw=10))

# Comcast
x_Comcast = makex(0, 41.7)
y_Comcast = []
for i in range(len(x_Comcast)):
    y_Comcast.append(h_vesus_w.Comcast(x_Comcast[i], Tw=10))

# 绘图
fig = px.line()

fig.add_scatter(x=x_bohr, y=y_bohr, name="波尔", line=dict(color="blue"))
fig.add_scatter(x=x_moho, y=y_moho, name="莫霍", line=dict(color="red"))
fig.add_scatter(x=x_xgh, y=y_xgh, name="希格荷", line=dict(color="pink"))
fig.add_scatter(x=x_zbtl, y=y_zbtl, name="佐本太郎", line=dict(color="yellow"))
fig.add_scatter(
    x=x_Mihockel, y=y_Mihockel, name="米霍克尔(存疑)", line=dict(color="purple")
)
fig.add_scatter(x=x_Smit, y=y_Smit, name="施密特", line=dict(color="green"))
fig.add_scatter(
    x=x_Comcast, y=y_Comcast, name="康卡斯特(存疑)", line=dict(color="black")
)

fig.show()
