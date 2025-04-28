import unittest
import json
from pathlib import Path
from typing import Dict
from thermal_properties import (
    SteelProperty,
    load_steel_properties,
    compute_temperatures,
    ThermalProperties,
)
from boundary_condition import HeatTransferCalculator


class TestThermalProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """创建测试用的钢种物性JSON文件"""
        test_data = {
            "测试钢种": {
                "lamda_s": 30.0,
                "lamda_m": 35.0,
                "lamda_l": 40.0,
                "c_s": 600.0,
                "c_m": 650.0,
                "c_l": 700.0,
                "rho_s": 7500.0,
                "rho_m": 7300.0,
                "rho_l": 7100.0,
                "l_f": 250000.0,
            }
        }
        cls.test_file = Path(__file__).parent / "test_steel_properties.json"
        with open(cls.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # 加载测试数据到全局变量
        from thermal_properties import (
            load_steel_properties,
            steel_properties as global_steel_props,
        )

        global steel_properties
        test_props = load_steel_properties(cls.test_file)
        # 合并到全局变量中
        steel_properties = {**global_steel_props, **test_props}

    @classmethod
    def tearDownClass(cls):
        """删除测试文件"""
        cls.test_file.unlink(missing_ok=True)

    def test_load_steel_properties(self):
        """测试加载钢种物性"""
        props = load_steel_properties(self.test_file)
        print(f"\n加载的钢种数量: {len(props)}")
        print(f"测试钢种属性: {props['测试钢种'].__dict__}")
        self.assertIsInstance(props, dict)
        self.assertIn("测试钢种", props)
        self.assertIsInstance(props["测试钢种"], SteelProperty)

    def test_compute_temperatures(self):
        """测试温度计算"""
        composition = {"C": 0.1, "Si": 0.2}
        print(f"\n测试成分: {composition}")
        results = compute_temperatures(composition)

        print(f"液相线温度: {results['Liquidus']}")
        print(f"固相线温度: {results['Solidus']}")
        self.assertIsInstance(results, dict)
        self.assertIn("Liquidus", results)
        self.assertIn("Solidus", results)
        self.assertGreater(len(results["Liquidus"]), 0)
        self.assertGreater(len(results["Solidus"]), 0)

    def test_thermal_properties_class(self):
        """测试热物性计算类"""
        thermal = ThermalProperties(
            "测试钢种", 1400, 1500, steel_props=steel_properties
        )
        print(f"\n测试钢种: 测试钢种, 液相线: 1400℃, 固相线: 1500℃")

        # 测试相态判断
        print(f"1300℃相态: {thermal.get_phase(1300)}")
        print(f"1450℃相态: {thermal.get_phase(1450)}")
        print(f"1600℃相态: {thermal.get_phase(1600)}")
        self.assertEqual(thermal.get_phase(1300), "solid")
        self.assertEqual(thermal.get_phase(1450), "mushy")
        self.assertEqual(thermal.get_phase(1600), "liquid")

        # 测试物性计算
        cp = thermal.cp_cal(1300)
        rho = thermal.rho_cal(1450)
        lamda = thermal.lamda_cal(1450, 0.5)
        print(f"1300℃比热: {cp:.1f} J/kg·K")
        print(f"1450℃密度: {rho:.1f} kg/m³")
        print(f"1450℃导热系数: {lamda:.1f} W/m·K")
        self.assertAlmostEqual(cp, 600.0)
        self.assertAlmostEqual(rho, 7300.0)
        self.assertGreater(lamda, 30.0)

    def test_invalid_steel_type(self):
        """测试无效钢种类型"""
        invalid_type = "不存在的钢种"
        print(f"\n测试无效钢种: {invalid_type}")
        with self.assertRaises(RuntimeError):
            ThermalProperties(invalid_type, 1400, 1500)
        print("成功捕获无效钢种异常")


class TestBoundaryCondition(unittest.TestCase):
    """测试边界条件计算"""

    def setUp(self):
        self.calculator = HeatTransferCalculator()

    def test_air_cooling_heat_flux(self):
        """测试空冷区热流密度计算"""
        # 正常工况测试
        q1 = self.calculator.air_cooling_heat_flux(900, 20)
        print(f"\n空冷区热流密度(900℃,20℃): {q1:.2f} kW/m²")
        self.assertGreater(q1, 0)
        self.assertLess(q1, 100)  # 合理范围检查

        # 表面温度等于环境温度
        q2 = self.calculator.air_cooling_heat_flux(20, 20)
        print(f"表面温度等于环境温度(20℃,20℃): {q2:.2f} kW/m²")
        self.assertEqual(q2, 0)

        # 表面温度低于环境温度
        q3 = self.calculator.air_cooling_heat_flux(10, 20)
        print(f"表面温度高于环境温度(10℃,20℃): {q3:.2f} kW/m²")
        self.assertEqual(q3, 0)  # 应返回0而不是负值

        # 不同发射率测试
        q4 = self.calculator.air_cooling_heat_flux(900, 20, 0.5)
        q5 = self.calculator.air_cooling_heat_flux(900, 20, 0.9)
        print(f"发射率0.5时的热流密度: {q4:.2f} kW/m²")
        print(f"发射率0.9时的热流密度: {q5:.2f} kW/m²")
        self.assertGreater(q5, q4)  # 发射率越大热流密度越大

        # 高温测试
        q6 = self.calculator.air_cooling_heat_flux(1200, 20)
        print(f"高温工况(1200℃,20℃): {q6:.2f} kW/m²")
        self.assertGreater(q6, q1)  # 温度越高热流密度越大


if __name__ == "__main__":
    unittest.main()
