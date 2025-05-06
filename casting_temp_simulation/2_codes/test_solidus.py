"""固相线温度公式测试脚本"""

import json
from thermal_properties import compute_temperatures

# 测试成分数据
test_composition = {
    "C": 0.1,
    "Si": 0.2,
    "Mn": 0.5,
    "P": 0.01,
    "S": 0.005,
    "Cr": 0.3,
    "Ni": 0.1,
    "Mo": 0.05,
    "Al": 0.02,
    "N": 0.002,
    "Cu": 0.1,
    "V": 0.01,
    "W": 0.01,
    "Ti": 0.01,
    "Nb": 0.01,
    "O": 0.0005,
}

# 加载公式名称
with open(
    "casting_temp_simulation/2_codes/formula_names.json", "r", encoding="utf-8"
) as f:
    formula_data = json.load(f)
    solidus_formulas = formula_data["solidus_formulas"]

print("固相线公式测试结果:")
print("=" * 50)

# 测试每个固相线公式
for formula in solidus_formulas:
    result = compute_temperatures(
        test_composition, solidus_formula=formula, kind="中碳钢"
    )
    print(f"公式: {formula}")
    print(f"固相线温度: {result['solidus']:.2f}°C")
    print("-" * 50)

print("\n所有公式平均值测试:")
avg_result = compute_temperatures(test_composition, kind="中碳钢")
print(f"平均固相线温度: {avg_result['solidus']:.2f}°C")
