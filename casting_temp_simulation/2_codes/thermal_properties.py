import json
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class SteelProperty:
    """钢种物性数据类"""

    lamda_s: float  # 固相热导率 (W/m·K)
    lamda_m: float  # 两相区热导率 (W/m·K)
    lamda_l: float  # 液相热导率 (W/m·K)
    c_s: float  # 固相比热容 (J/kg·K)
    c_m: float  # 两相区比热容 (J/kg·K)
    c_l: float  # 液相比热容 (J/kg·K)
    rho_s: float  # 固相密度 (kg/m3)
    rho_m: float  # 两相区密度 (kg/m3)
    rho_l: float  # 液相密度 (kg/m3)
    l_f: float  # 潜热 (J/kg)


def load_steel_properties(file_path: Optional[str] = None) -> Dict[str, SteelProperty]:
    """从JSON文件加载钢种物性参数

    Args:
        file_path: JSON文件路径，默认为同目录下的steel_properties.json

    Returns:
        钢种物性参数字典

    Raises:
        FileNotFoundError: 当JSON文件不存在时
        json.JSONDecodeError: 当JSON文件格式错误时
        ValueError: 当数据验证失败时
    """
    if file_path is None:
        file_path = str(Path(__file__).parent / "steel_properties.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 数据验证和转换
    steel_props = {}
    for steel_type, props in data.items():
        try:
            steel_props[steel_type] = SteelProperty(**props)
        except TypeError as e:
            raise ValueError(f"钢种 '{steel_type}' 属性不完整或类型错误: {str(e)}")

    return steel_props


# 加载钢种物性参数
try:
    steel_properties = load_steel_properties()
except Exception as e:
    # 如果加载失败，使用内置默认值
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


def compute_temperatures(composition, liquidus_formula=None, solidus_formula=None):
    """
    输入成分字典（例如：{'C': 0.1, 'Si': 0.2, ...}），返回不同公式的计算结果。
    支持的成分元素：C, Si, Mn, P, S, Ni, Cr, Mo, Cu, V, W, N, Al, Co, Fe等。

    Args:
        composition: 成分字典
        liquidus_formula: 指定使用的液相线公式名称，None表示计算所有公式
        solidus_formula: 指定使用的固相线公式名称，None表示计算所有公式

    Returns:
        如果指定了公式名称，则返回单个温度值
        如果未指定公式名称，则返回包含所有公式结果的字典
    """
    results = {"Liquidus": {}, "Solidus": {}}

    # 从JSON文件加载公式名称
    formula_file = Path(__file__).parent / "formula_names.json"
    try:
        with open(formula_file, "r", encoding="utf-8") as f:
            formula_data = json.load(f)

        # 校验JSON文件内容
        if not isinstance(formula_data, dict):
            raise ValueError("Invalid formula data format")

        required_keys = {"liquidus_formulas", "solidus_formulas"}
        if not required_keys.issubset(formula_data.keys()):
            raise ValueError("Missing required formula keys")

        if not (
            isinstance(formula_data["liquidus_formulas"], list)
            and isinstance(formula_data["solidus_formulas"], list)
        ):
            raise ValueError("Formulas should be lists")

        all_liquidus_formulas = formula_data["liquidus_formulas"]
        all_solidus_formulas = formula_data["solidus_formulas"]

    except Exception as e:
        print(f"Warning: Failed to load formula names ({str(e)}), using defaults")
        # 如果加载失败，使用内置默认值
        all_liquidus_formulas = [
            "1980_国外连铸新技术",
            "1988_商家K",
            "1989_日本广田连铸技术",
            "1990_连续铸钢手册_通用",
            "1990_连续铸钢手册_碳素钢",
            "1990_连续铸钢手册_特殊钢",
            "1994_连续铸钢原理与工艺",
            "1997_宝钢技术_平居公式",
            "2000_商家D_不锈钢1",
            "2000_商家D_不锈钢2",
            "2006_薄板坯连铸连轧",
            "2013_炼钢_通用",
            "1998_商家A_镀锡板",
            "2000_商家B_不锈钢",
            "2003_武钢_硅钢",
            "2007_连铸900问",
            "商家D_碳钢分段",
            "铸铁",
        ]
        all_solidus_formulas = [
            "1997_宝钢技术_平居公式",
            "2006_薄板坯连铸连轧",
            "2007_连铸900问",
            "2011_连续铸钢生产技术",
            "2012_钢铁",
        ]

    # 提取成分，缺失元素默认设为0
    def get_value(key):
        return composition.get(key, 0.0)

    # 完整元素提取(所有可能用到的元素)
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
    Ti = get_value("Ti")
    O = get_value("O")
    Nb = get_value("Nb")
    Ta = get_value("Ta")
    As = get_value("As")
    Sn = get_value("Sn")
    Zr = get_value("Zr")

    # -------------------------- 液相线公式 --------------------------
    # 如果指定了液相线公式，只计算指定的公式
    if liquidus_formula:
        if liquidus_formula not in all_liquidus_formulas:
            raise ValueError(f"无效的液相线公式名称: {liquidus_formula}")

        # 1. 1980年《国外连铸新技术》译文集(二)第14页
        if liquidus_formula == "1980_国外连铸新技术":
            return 1535 - (78 * C + 4.9 * Mn + 3.6 * Al + 7.6 * Si)

        # 2. 1988年商家K提供给某钢铁公司超低头板坯连铸机
        elif liquidus_formula == "1988_商家K":

            def liquidus_1988():
                base = 1536.6 - (
                    8 * Si
                    + 5 * Mn
                    + 5.5 * Cu
                    + 1.5 * Cr
                    + 4 * Ni
                    + 2 * Mo
                    + 18 * Ti
                    + 1
                )
                if C <= 0.5:
                    return base - 88 * C
                else:
                    return base - (0.5 * 88 + (C - 0.5) * 76)

            return liquidus_1988()

        # 3. 1989年《日本广田连铸技术》武钢二炼钢刘良春等编译第91页
        elif liquidus_formula == "1989_日本广田连铸技术":
            return 1536.6 - (
                88 * C
                + 25 * S
                + 5 * Cr
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 2 * Mo
                + 4 * Ni
                + 18 * Ti
                + 2 * V
            )

        # 4. 1990年《连续铸钢手册》冶金工业出版社81页 - 通用公式
        elif liquidus_formula == "1990_连续铸钢手册_通用":
            return 1539 - (
                70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + Cu + 4 * Ni + 1.5 * Cr
            )

        # 5. 1990年《连续铸钢手册》冶金工业出版社81页 - 碳素钢公式
        elif liquidus_formula == "1990_连续铸钢手册_碳素钢":

            def liquidus_1990_carbon():
                if C < 0.6:
                    return 1539 - (
                        90 * C
                        + 6.2 * Si
                        + 1.7 * Mn
                        + 28 * P
                        + 40 * S
                        + 2.6 * Cu
                        + 2.9 * Ni
                        + 1.8 * Cr
                        + 5.1 * Al
                    )
                else:
                    return 1534 - (
                        73 * C
                        + 12 * Si
                        + 3 * Mn
                        + 28 * P
                        + 30 * S
                        + 7 * Cu
                        + 3.5 * Ni
                        + Cr
                        + 3 * Al
                    )

            return liquidus_1990_carbon()

        # 6. 1990年《连续铸钢手册》冶金工业出版社81页 - 特殊钢种
        elif liquidus_formula == "1990_连续铸钢手册_特殊钢":
            return 1534 - (91 * C + 21 * Si + 3.5 * Mn + 4 * Ni + 0.65 * Cr + 3 * Mo)

        # 7. 1994年《连续铸钢原理与工艺》
        elif liquidus_formula == "1994_连续铸钢原理与工艺":
            return 1537 - (
                88 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 5 * Cu
                + 4 * Ni
                + 2 * Mo
                + 2 * V
                + 1.5 * Cr
            )

        # 8. 1997年《宝钢技术》第3期第20页日本人的"平居公式"
        elif liquidus_formula == "1997_宝钢技术_平居公式":
            return 1538 - (
                55 * C
                + 80 * C**2
                + 13 * Si
                + 4.8 * Mn
                + 1.5 * Cr
                + 4.3 * Ni
                + 30 * P
                + 30 * S
            )

        # 9. 2000年商家D给T钢铁公司不锈钢连铸机推荐公式
        elif liquidus_formula == "2000_商家D_不锈钢1":
            return 1536.6 - (
                90 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 3 * Al
                + 1.55 * Cr
                + 4 * Ni
                + 2 * Mo
                + 18 * Ti
                + 80 * N
                + 5 * Cu
            )
        elif liquidus_formula == "2000_商家D_不锈钢2":
            return 1536.6 - (
                90 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 5 * Cu
                + 4 * Ni
                + 1.55 * Cr
                + 2 * Mo
                + 18 * Ti
                + 80 * 0.0001 * (N * 10000 - 100)  # ppm转换
            )

        # 10. 2006年《薄板坯连铸连轧钢的组织性能控制》
        elif liquidus_formula == "2006_薄板坯连铸连轧":
            return 1537 - (
                65 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 2.7 * Al + 80 * O + 90 * N
            )

        # 11. 2013年《炼钢》第5期第66~67页通用公式
        elif liquidus_formula == "2013_炼钢_通用":
            return 1539 - (
                70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 4 * Ni + 1.5 * Cr
            )

        # 12. 1998年商家A提供给A钢铁公司板坯连铸机镀锡板计算公式
        elif liquidus_formula == "1998_商家A_镀锡板":
            return 1536.8 - (
                88 * C
                + 5 * Mn
                + 8 * Si
                + 30 * P
                + 25 * S
                + 5 * Cr
                + 2 * Mo
                + 4 * Ni
                + 18 * Ti
                + 2 * V
            )

        # 13. 2000年商家B给A钢铁公司不锈钢连铸机推荐公式
        elif liquidus_formula == "2000_商家B_不锈钢":

            def liquidus_2000_stainless():
                if C < 0.2:
                    return 1536 - (
                        65 * C
                        + 8 * Si
                        + 5 * Mn
                        + 30 * P
                        + 25 * S
                        + 1.7 * Al
                        + 5 * Cu
                        + 1.5 * Cr
                        + 4 * Ni
                        + 2 * V
                        + W
                        + 1.7 * Co
                        + 12.8 * Zr
                        + 7 * Nb
                        + 3 * Ta
                        + 14 * Ti
                        + 14 * As
                        + 10 * Sn
                    )
                elif 0.2 <= C <= 0.5:
                    return 1536 - (
                        88 * C
                        + 8 * Si
                        + 5 * Mn
                        + 30 * P
                        + 25 * S
                        + 1.7 * Al
                        + 5 * Cu
                        + 1.5 * Cr
                        + 4 * Ni
                        + 2 * V
                    )
                else:
                    return 1536 - (
                        9 * C
                        + 65 * C**2
                        + 10 * Si
                        + 6 * Mn
                        + 30 * P
                        + 30 * S
                        + 3 * Al
                        + 5 * Cu
                        + 1.5 * Cr
                        + 3.5 * Ni
                        + 2 * V
                    )

            return liquidus_2000_stainless()

        # 14. 2003年《武钢炼钢生产技术进步概况》硅钢公式
        elif liquidus_formula == "2003_武钢_硅钢":
            return 1539 - (
                65 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 5 * Cu
                + 4 * Ni
                + 2 * Mo
                + 2 * V
                + 1.5 * Cr
            )

        # 15. 2007年《品种钢、优特钢连铸900问》
        elif liquidus_formula == "2007_连铸900问":
            return 1539 - (
                70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 4 * Ni + 2 * Mo + 2 * V
            )

        # 16. 商家D碳钢板坯连铸机公式(分段碳系数)
        elif liquidus_formula == "商家D_碳钢分段":

            def liquidus_vendorD_carbon():
                if C <= 0.025:
                    factor = 90.0
                elif 0.025 < C <= 0.050:
                    factor = 82.0
                elif 0.050 < C <= 0.101:
                    factor = 86.0
                elif 0.101 < C <= 0.500:
                    factor = 88.4
                elif 0.500 < C <= 0.600:
                    factor = 86.1
                elif 0.600 < C <= 0.700:
                    factor = 84.2
                elif 0.700 < C <= 0.800:
                    factor = 83.2
                else:
                    factor = 82.3
                return 1536.6 - (
                    factor * C
                    + 8 * Si
                    + 5 * Mn
                    + 30 * P
                    + 25 * S
                    + 2 * Ti
                    + 2 * Mo
                    + 5 * Cu
                    + 4 * Ni
                    + 1.5 * Cr
                    + 5.1 * Al
                    + 90 * N
                )

            return liquidus_vendorD_carbon()

        # 17. 铸铁液相线温度
        elif liquidus_formula == "铸铁":
            return 1650 - 124.5 * C - 26.7 * (Si + 2.45 * P)

    # 2. 1988年商家K提供给某钢铁公司超低头板坯连铸机
    def liquidus_1988():
        base = 1536.6 - (
            8 * Si + 5 * Mn + 5.5 * Cu + 1.5 * Cr + 4 * Ni + 2 * Mo + 18 * Ti + 1
        )
        if C <= 0.5:
            return base - 88 * C
        else:
            return base - (0.5 * 88 + (C - 0.5) * 76)

    results["Liquidus"]["1988_商家K"] = liquidus_1988()

    # 3. 1989年《日本广田连铸技术》武钢二炼钢刘良春等编译第91页
    results["Liquidus"]["1989_日本广田连铸技术"] = 1536.6 - (
        88 * C
        + 25 * S
        + 5 * Cr
        + 8 * Si
        + 5 * Mn
        + 30 * P
        + 2 * Mo
        + 4 * Ni
        + 18 * Ti
        + 2 * V
    )

    # 4. 1990年《连续铸钢手册》冶金工业出版社81页 - 通用公式
    results["Liquidus"]["1990_连续铸钢手册_通用"] = 1539 - (
        70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + Cu + 4 * Ni + 1.5 * Cr
    )

    # 5. 1990年《连续铸钢手册》冶金工业出版社81页 - 碳素钢公式
    def liquidus_1990_carbon():
        if C < 0.6:
            return 1539 - (
                90 * C
                + 6.2 * Si
                + 1.7 * Mn
                + 28 * P
                + 40 * S
                + 2.6 * Cu
                + 2.9 * Ni
                + 1.8 * Cr
                + 5.1 * Al
            )
        else:
            return 1534 - (
                73 * C
                + 12 * Si
                + 3 * Mn
                + 28 * P
                + 30 * S
                + 7 * Cu
                + 3.5 * Ni
                + Cr
                + 3 * Al
            )

    results["Liquidus"]["1990_连续铸钢手册_碳素钢"] = liquidus_1990_carbon()

    # 6. 1990年《连续铸钢手册》冶金工业出版社81页 - 特殊钢种
    results["Liquidus"]["1990_连续铸钢手册_特殊钢"] = 1534 - (
        91 * C + 21 * Si + 3.5 * Mn + 4 * Ni + 0.65 * Cr + 3 * Mo
    )

    # 7. 1994年《连续铸钢原理与工艺》
    results["Liquidus"]["1994_连续铸钢原理与工艺"] = 1537 - (
        88 * C
        + 8 * Si
        + 5 * Mn
        + 30 * P
        + 25 * S
        + 5 * Cu
        + 4 * Ni
        + 2 * Mo
        + 2 * V
        + 1.5 * Cr
    )

    # 8. 1997年《宝钢技术》第3期第20页日本人的"平居公式"
    results["Liquidus"]["1997_宝钢技术_平居公式"] = 1538 - (
        55 * C + 80 * C**2 + 13 * Si + 4.8 * Mn + 1.5 * Cr + 4.3 * Ni + 30 * P + 30 * S
    )

    # 9. 2000年商家D给T钢铁公司不锈钢连铸机推荐公式
    results["Liquidus"]["2000_商家D_不锈钢1"] = 1536.6 - (
        90 * C
        + 8 * Si
        + 5 * Mn
        + 30 * P
        + 25 * S
        + 3 * Al
        + 1.55 * Cr
        + 4 * Ni
        + 2 * Mo
        + 18 * Ti
        + 80 * N
        + 5 * Cu
    )
    results["Liquidus"]["2000_商家D_不锈钢2"] = 1536.6 - (
        90 * C
        + 8 * Si
        + 5 * Mn
        + 30 * P
        + 25 * S
        + 5 * Cu
        + 4 * Ni
        + 1.55 * Cr
        + 2 * Mo
        + 18 * Ti
        + 80 * 0.0001 * (N * 10000 - 100)  # ppm转换
    )

    # 10. 2006年《薄板坯连铸连轧钢的组织性能控制》
    results["Liquidus"]["2006_薄板坯连铸连轧"] = 1537 - (
        65 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 2.7 * Al + 80 * O + 90 * N
    )

    # 11. 2013年《炼钢》第5期第66~67页通用公式
    results["Liquidus"]["2013_炼钢_通用"] = 1539 - (
        70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 4 * Ni + 1.5 * Cr
    )

    # 12. 1998年商家A提供给A钢铁公司板坯连铸机镀锡板计算公式
    results["Liquidus"]["1998_商家A_镀锡板"] = 1536.8 - (
        88 * C
        + 5 * Mn
        + 8 * Si
        + 30 * P
        + 25 * S
        + 5 * Cr
        + 2 * Mo
        + 4 * Ni
        + 18 * Ti
        + 2 * V
    )

    # 13. 2000年商家B给A钢铁公司不锈钢连铸机推荐公式
    def liquidus_2000_stainless():
        if C < 0.2:
            return 1536 - (
                65 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 1.7 * Al
                + 5 * Cu
                + 1.5 * Cr
                + 4 * Ni
                + 2 * V
                + W
                + 1.7 * Co
                + 12.8 * Zr
                + 7 * Nb
                + 3 * Ta
                + 14 * Ti
                + 14 * As
                + 10 * Sn
            )
        elif 0.2 <= C <= 0.5:
            return 1536 - (
                88 * C
                + 8 * Si
                + 5 * Mn
                + 30 * P
                + 25 * S
                + 1.7 * Al
                + 5 * Cu
                + 1.5 * Cr
                + 4 * Ni
                + 2 * V
            )
        else:
            return 1536 - (
                9 * C
                + 65 * C**2
                + 10 * Si
                + 6 * Mn
                + 30 * P
                + 30 * S
                + 3 * Al
                + 5 * Cu
                + 1.5 * Cr
                + 3.5 * Ni
                + 2 * V
            )

    results["Liquidus"]["2000_商家B_不锈钢"] = liquidus_2000_stainless()

    # 14. 2003年《武钢炼钢生产技术进步概况》硅钢公式
    results["Liquidus"]["2003_武钢_硅钢"] = 1539 - (
        65 * C
        + 8 * Si
        + 5 * Mn
        + 30 * P
        + 25 * S
        + 5 * Cu
        + 4 * Ni
        + 2 * Mo
        + 2 * V
        + 1.5 * Cr
    )

    # 15. 2007年《品种钢、优特钢连铸900问》
    results["Liquidus"]["2007_连铸900问"] = 1539 - (
        70 * C + 8 * Si + 5 * Mn + 30 * P + 25 * S + 4 * Ni + 2 * Mo + 2 * V
    )

    # 16. 商家D碳钢板坯连铸机公式(分段碳系数)
    def liquidus_vendorD_carbon():
        if C <= 0.025:
            factor = 90.0
        elif 0.025 < C <= 0.050:
            factor = 82.0
        elif 0.050 < C <= 0.101:
            factor = 86.0
        elif 0.101 < C <= 0.500:
            factor = 88.4
        elif 0.500 < C <= 0.600:
            factor = 86.1
        elif 0.600 < C <= 0.700:
            factor = 84.2
        elif 0.700 < C <= 0.800:
            factor = 83.2
        else:
            factor = 82.3
        return 1536.6 - (
            factor * C
            + 8 * Si
            + 5 * Mn
            + 30 * P
            + 25 * S
            + 2 * Ti
            + 2 * Mo
            + 5 * Cu
            + 4 * Ni
            + 1.5 * Cr
            + 5.1 * Al
            + 90 * N
        )

    results["Liquidus"]["商家D_碳钢分段"] = liquidus_vendorD_carbon()

    # 17. 铸铁液相线温度
    results["Liquidus"]["铸铁"] = 1650 - 124.5 * C - 26.7 * (Si + 2.45 * P)

    # -------------------------- 固相线公式 --------------------------
    # 1. 1997年《宝钢技术》第3期第20页日本人的"平居公式"
    def solidus_1997():
        base = (
            20.5 * Si + 6.5 * Mn + 2.0 * Cr + 11.5 * Ni + 5.5 * Al + 500 * P + 700 * S
        )
        if C <= 0.09:
            return 1538 - (478 * C + base)
        elif 0.09 < C <= 0.17:
            return 1495 - base
        else:
            return 1527 - (187.5 * C + base)

    # 如果指定了固相线公式，只计算指定的公式
    if solidus_formula:
        if solidus_formula not in all_solidus_formulas:
            raise ValueError(f"无效的固相线公式名称: {solidus_formula}")

        if solidus_formula == "1997_宝钢技术_平居公式":
            return solidus_1997()
        elif solidus_formula == "2006_薄板坯连铸连轧":
            return 1537 - (
                175 * C + 20 * Si + 30 * Mn + 280 * P + 575 * S + 7.5 * Al + 160 * O
            )
        elif solidus_formula == "2007_连铸900问":
            return 1534 - 2.29 * (
                80.5 * C
                + 17.8 * Si
                + 3.75 * Mn
                + 33.5 * P
                + 33.5 * S
                + 3 * N
                + 1.5 * Cr
                + 3.4 * Cu
                + 3.4 * Al
            )
        elif solidus_formula == "2011_连续铸钢生产技术":
            return 1471 - (
                25.2 * C
                + 12 * Si
                + 7.6 * Mn
                + 34 * P
                + 30 * S
                + 5 * Cu
                + 3.1 * Ni
                + 1.3 * Cr
                + 3.6 * Al
                + 2 * Mo
                + 2 * V
                + 18 * Ti
            )
        elif solidus_formula == "2012_钢铁":
            return 1536 - (
                175 * C
                + 20 * Si
                + 30 * Mn
                + 280 * P
                + 575 * S
                + 6.5 * Cr
                + 4 * V
                + 4.75 * Ni
                + 7.5 * Al
                + 2.5 * W
                + 40 * Ti
                + 5 * Mo
                + 60 * Nb
                + 160 * O
            )

    results["Solidus"]["1997_宝钢技术_平居公式"] = solidus_1997()

    # 2. 2006年《薄板坯连铸连轧钢的组织性能控制》
    results["Solidus"]["2006_薄板坯连铸连轧"] = 1537 - (
        175 * C + 20 * Si + 30 * Mn + 280 * P + 575 * S + 7.5 * Al + 160 * O
    )

    # 3. 2007年《品种钢、优特钢连铸900问》
    results["Solidus"]["2007_连铸900问"] = 1534 - 2.29 * (
        80.5 * C
        + 17.8 * Si
        + 3.75 * Mn
        + 33.5 * P
        + 33.5 * S
        + 3 * N
        + 1.5 * Cr
        + 3.4 * Cu
        + 3.4 * Al
    )

    # 4. 2011年《连续铸钢生产技术》
    results["Solidus"]["2011_连续铸钢生产技术"] = 1471 - (
        25.2 * C
        + 12 * Si
        + 7.6 * Mn
        + 34 * P
        + 30 * S
        + 5 * Cu
        + 3.1 * Ni
        + 1.3 * Cr
        + 3.6 * Al
        + 2 * Mo
        + 2 * V
        + 18 * Ti
    )

    # 5. 2012年《钢铁》第10期第28页
    results["Solidus"]["2012_钢铁"] = 1536 - (
        175 * C
        + 20 * Si
        + 30 * Mn
        + 280 * P
        + 575 * S
        + 6.5 * Cr
        + 4 * V
        + 4.75 * Ni
        + 7.5 * Al
        + 2.5 * W
        + 40 * Ti
        + 5 * Mo
        + 60 * Nb
        + 160 * O
    )

    return results


def plot_temperature_comparison(results):
    """绘制横向柱状图对比不同公式的温度预测"""
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    # 设置中文字体
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
    plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

    # 创建自定义布局 (1行2列)
    fig = plt.figure(figsize=(24, 10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

    # 获取并过滤数据(确保只包含钢的数据)
    liquids = {k: v for k, v in results["Liquidus"].items() if "铸铁" not in k}
    solids = {k: v for k, v in results["Solidus"].items() if "铸铁" not in k}

    if not liquids:
        raise ValueError("没有有效的液相线数据")
    if not solids:
        raise ValueError("没有有效的固相线数据")

    # 计算平均值
    liquid_avg = sum(liquids.values()) / len(liquids)
    solid_avg = sum(solids.values()) / len(solids)

    # 液相线绘图(钢材) - 左上
    ax1 = plt.subplot(gs[0, 0])
    sorted_liquids = sorted(liquids.items(), key=lambda x: x[1])
    names = [x[0] for x in sorted_liquids]
    values = [x[1] for x in sorted_liquids]

    # 使用渐变颜色和细条形
    cmap = plt.cm.viridis
    norm = plt.Normalize(min(values), max(values))
    colors = cmap(norm(values))

    plt.barh(names, values, height=0.6, color=colors)
    plt.title("钢的液相线温度比较", fontsize=16, pad=20)
    plt.xlabel("温度 (°C)", fontsize=14)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    # 添加平均值参考线
    plt.axvline(liquid_avg, color="red", linestyle="--", linewidth=2)
    plt.text(
        liquid_avg + 1,
        0.1,  # 调整到图表底部
        f"平均值: {liquid_avg:.1f}°C",
        color="blue",
        fontsize=15,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
    )

    # 固相线绘图(钢材) - 右上
    ax2 = plt.subplot(gs[0, 1])
    sorted_solids = sorted(solids.items(), key=lambda x: x[1])
    names = [x[0] for x in sorted_solids]
    values = [x[1] for x in sorted_solids]

    # 使用渐变颜色和细条形
    cmap = plt.cm.plasma
    norm = plt.Normalize(min(values), max(values))
    colors = cmap(norm(values))

    plt.barh(names, values, height=0.6, color=colors)
    plt.title("钢的固相线温度比较", fontsize=16, pad=20)
    plt.xlabel("温度 (°C)", fontsize=14)
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    # 添加平均值参考线
    plt.axvline(solid_avg, color="red", linestyle="--", linewidth=2)
    plt.text(
        solid_avg + 1,
        0.1,  # 调整到图表底部
        f"平均值: {solid_avg:.2f}°C",
        color="blue",
        fontsize=15,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
    )

    # 设置坐标轴范围(自动调整)
    def get_axis_range(values, margin=0.1):
        min_val = min(values)
        max_val = max(values)
        span = max_val - min_val
        return min_val - span * margin, max_val + span * margin

    ax1.set_xlim(*get_axis_range(liquids.values()))
    ax2.set_xlim(*get_axis_range(solids.values()))

    plt.tight_layout()
    plt.show()


class ThermalProperties:
    """钢的热物性计算类"""

    def __init__(
        self,
        kind: str,
        Ts: float,
        Tl: float,
        Tc: float = 1550,
        steel_props: Optional[Dict[str, SteelProperty]] = None,
    ):
        """初始化热物性计算器
        Args:
            kind: 钢种名称
            Ts: 固相线温度(K)
            Tl: 液相线温度(K)
            Tc: 临界温度(K)，默认为1550
            steel_props: 钢种物性字典，默认为None(使用全局steel_properties)
        """
        self.kind = kind
        self.Ts = Ts
        self.Tl = Tl
        self.Tc = Tc

        props_dict = steel_props if steel_props is not None else steel_properties
        if kind not in props_dict:
            raise RuntimeError(f"无效的钢种类型: {kind}")
        self.props = props_dict[kind]

    def get_phase(self, T: float) -> str:
        """获取当前温度下的相态
        Returns:
            "solid" - 固相
            "mushy" - 两相区
            "liquid" - 液相
        """
        if T >= self.Tl:
            return "liquid"
        elif T >= self.Ts:
            return "mushy"
        return "solid"

    def lamda_cal(self, T: float, position: float) -> float:
        """计算等效热导率(W/m·K)
        Args:
            T: 当前温度(K)
            position: 位置参数(0-3)
        """
        lamdal = self.props.lamda_l
        lamdas = self.props.lamda_s
        fs = (self.Tl - T) / (self.Tl - self.Ts) if self.Tl != self.Ts else 0

        def _Acon(T: float, position: float) -> float:
            """计算Acon修正系数"""
            if 1 > position >= 0:  # 位置0-1区域
                if T >= self.Tl:  # 液相区
                    return 6 - 4 * ((self.Tc - T) / (self.Tc - self.Tl))
                elif self.Tl >= T >= self.Ts:  # 两相区
                    return 2 - 2 * fs
            elif 3 > position >= 1:  # 位置1-3区域
                if T >= self.Tl:  # 液相区
                    return 1 - ((self.Tc - T) / (self.Tc - self.Tl))
                elif self.Tl >= T >= self.Ts:  # 两相区
                    return 0
            return 0

        phase = self.get_phase(T)
        if phase == "liquid":
            return (1 + _Acon(T, position)) * lamdal
        elif phase == "mushy":
            # 并联模型
            lamdapar = (1 + _Acon(T, position)) * (1 - fs) * lamdal + fs * lamdas
            # 串联模型
            lamdaser = ((1 + _Acon(T, position)) * lamdal * lamdas) / (
                (1 + _Acon(T, position)) * lamdal * fs + (1 - fs) * lamdas
            )
            return (lamdapar + lamdaser) / 2
        return lamdas

    def cp_cal(self, T: float) -> float:
        """计算比热容(J/kg·K)
        Args:
            T: 当前温度(K)
        """
        phase = self.get_phase(T)
        if phase == "liquid":
            return self.props.c_l
        elif phase == "mushy":
            return self.props.c_m
        return self.props.c_s

    def rho_cal(self, T: float) -> float:
        """计算密度(kg/m3)
        Args:
            T: 当前温度(K)
        """
        phase = self.get_phase(T)
        if phase == "liquid":
            return self.props.rho_l
        elif phase == "mushy":
            return self.props.rho_m
        return self.props.rho_s

    @staticmethod
    def compute_temperatures(composition, liquidus_formula=None, solidus_formula=None):
        """计算钢的液相线和固相线温度(调用外部函数)

        Args:
            composition: 成分字典
            liquidus_formula: 指定使用的液相线公式名称
            solidus_formula: 指定使用的固相线公式名称

        Returns:
            如果指定了公式名称，则返回单个温度值
            如果未指定公式名称，则返回包含所有公式结果的字典
        """
        return compute_temperatures(composition, liquidus_formula, solidus_formula)

    @staticmethod
    def plot_temperature_comparison(results):
        """绘制温度比较图(调用外部函数)"""
        plot_temperature_comparison(results)


if __name__ == "__main__":
    # 使用示例1：热物性计算
    steel_kind = "中碳钢"
    Ts = 1400  # 固相线温度(K)
    Tl = 1500  # 液相线温度(K)
    thermal = ThermalProperties(steel_kind, Ts, Tl)

    # 计算不同温度下的物性
    temperatures = [1300, 1450, 1600]  # 固相区、两相区、液相区温度
    position = 0.5  # 位置参数

    print(f"钢种: {steel_kind}")
    print("温度(K) | 相态     | 热导率(W/m·K) | 比热容(J/kg·K) | 密度(kg/m3)")
    print("-" * 70)

    for T in temperatures:
        phase = thermal.get_phase(T)
        lamda = thermal.lamda_cal(T, position)
        cp = thermal.cp_cal(T)
        rho = thermal.rho_cal(T)
        print(f"{T:7} | {phase:8} | {lamda:14.2f} | {cp:14.2f} | {rho:10.2f}")

    # 使用示例2：温度计算
    composition = {
        "C": 0.1,
        "Si": 0.2,
        "Mn": 0.5,
        "P": 0.01,
        "S": 0.005,
        "Cr": 0.3,
        "Ni": 0.1,
        "Mo": 0.05,
    }
    results = ThermalProperties.compute_temperatures(composition)
    ThermalProperties.plot_temperature_comparison(results)
    # print(results)
