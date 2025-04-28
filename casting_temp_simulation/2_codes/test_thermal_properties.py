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
        self.assertIsInstance(props, dict)
        self.assertIn("测试钢种", props)
        self.assertIsInstance(props["测试钢种"], SteelProperty)

    def test_compute_temperatures(self):
        """测试温度计算"""
        composition = {"C": 0.1, "Si": 0.2}
        results = compute_temperatures(composition)

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

        # 测试相态判断
        self.assertEqual(thermal.get_phase(1300), "solid")
        self.assertEqual(thermal.get_phase(1450), "mushy")
        self.assertEqual(thermal.get_phase(1600), "liquid")

        # 测试物性计算
        self.assertAlmostEqual(thermal.cp_cal(1300), 600.0)
        self.assertAlmostEqual(thermal.rho_cal(1450), 7300.0)
        self.assertGreater(thermal.lamda_cal(1450, 0.5), 30.0)

    def test_invalid_steel_type(self):
        """测试无效钢种类型"""
        with self.assertRaises(RuntimeError):
            ThermalProperties("不存在的钢种", 1400, 1500)


if __name__ == "__main__":
    unittest.main()
