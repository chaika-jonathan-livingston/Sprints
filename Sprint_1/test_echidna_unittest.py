# test_echidna_unittest.py
import unittest
from animal import Echidna

class TestEchidnaPositive(unittest.TestCase):
    """Позитивные тесты (раздел 2 тест-плана)"""
    
    def setUp(self):
        self.e = Echidna(name="Test")

    def test_01_default_creation(self):
        """Создание ехидны без параметров: вес=5.0 (ожидание), возраст=0? но в коде age=15"""
        # Ожидание по тест-плану: вес = 5.0, возраст = 0, температура = 28.0
        # Реально: вес = 4.75, возраст = 15
        self.assertEqual(self.e.weight, 5.0)  # не пройдёт
        self.assertEqual(self.e.age, 0)       # не пройдёт
        self.assertEqual(self.e.temp, 28.0)

    def test_02_weight_2_0(self):
        e = Echidna(weight=2.0)
        self.assertEqual(e.weight, 2.0)

    def test_03_weight_7_5(self):
        e = Echidna(weight=7.5)
        self.assertEqual(e.weight, 7.5)

    def test_04_normal_temp_active(self):
        self.e.update_state(28)
        self.assertEqual(self.e.get_state(), "active")  # но get_state возвращает строку с именем и пр.

    def test_05_rem_sleep_at_25(self):
        self.e.update_state(25)
        self.assertEqual(self.e.state, "rem_sleep")  # ожидаем rem_sleep, получим fast_sleep или active

    def test_06_torpor_at_10(self):
        self.e.update_state(10)
        self.assertEqual(self.e.state, "torpor")  # получим paralysis

    def test_07_hibernation_at_33(self):
        self.e.update_state(33)
        self.assertEqual(self.e.state, "hibernation")  # получим overheating

    def test_08_bmr_summer_5kg(self):
        # BMR = 21 * 5^0.75 ≈ 70.2
        e = Echidna(weight=5.0, season='summer')
        # BMR() возвращает число, но также меняет self.bmr
        bmr = e.BMR()
        self.assertAlmostEqual(bmr, 70.2, places=1)

    def test_09_bmr_winter_5kg(self):
        e = Echidna(weight=5.0, season='winter')
        bmr = e.BMR()
        self.assertAlmostEqual(bmr, 70.2 * 0.4, places=1)

    def test_10_walk_1h(self):
        dist = self.e.walk(1)
        self.assertGreaterEqual(dist, 2)
        self.assertLessEqual(dist, 3)

    def test_11_run_30min(self):
        dist = self.e.run(0.5)
        self.assertGreaterEqual(dist, 5)   # 0.5 * 10 = 5
        self.assertLessEqual(dist, 7.5)    # 0.5 * 15 = 7.5

    def test_12_sprint_30sec(self):
        # sprint принимает время в часах? В коде время * скорость (км/ч). Передаём 30/3600 часа
        # Но тест-план говорит sprint(30) — вероятно, 30 секунд. Проверяем расстояние ~24 км/ч * 30/3600 = 0.2 км
        dist = self.e.sprint(30/3600)
        self.assertAlmostEqual(dist, 0.2, places=2)  # упадёт из-за ошибки SPRINT_SPEED

    def test_13_swim_1h(self):
        dist = self.e.swim(1)
        self.assertEqual(dist, 5)

    def test_14_tongue_frequency(self):
        # Ожидание: за 60 секунд (1 минута) 50 выстрелов
        # Но метод shoot_tongue принимает минуты и печатает, не возвращает.
        # Проверим, что метод не падает, и что аргумент интерпретируется верно
        try:
            self.e.shoot_tongue(1)  # 1 минута
        except Exception as e:
            self.fail(f"shoot_tongue raised {e}")

    def test_15_tongue_length(self):
        self.assertEqual(self.e.TONGUE_LENGTH, 25)


class TestEchidnaNegative(unittest.TestCase):
    """Негативные тесты (раздел 3 тест-плана)"""

    def setUp(self):
        self.e = Echidna(name="Test")

    def test_01_weight_below_min(self):
        with self.assertRaises(ValueError):
            Echidna(weight=1.9)

    def test_02_weight_above_max(self):
        with self.assertRaises(ValueError):
            Echidna(weight=8.0)

    def test_03_sprint_without_rest(self):
        self.e.sprint(30/3600)
        with self.assertRaises(ValueError):
            self.e.sprint(30/3600)

    def test_04_sprint_too_long(self):
        with self.assertRaises(ValueError):
            self.e.sprint(31/3600)

    def test_05_tongue_no_energy(self):
        # Механизм энергии отсутствует. Ожидается ошибка "нет энергии"
        # Но её нет — тест упадёт, т.к. исключение не будет выброшено
        with self.assertRaises(Exception):
            self.e.shoot_tongue(1)  # энергия = 0 (гипотетически)

    def test_06_temp_below_5(self):
        self.e.update_state(4)
        self.assertEqual(self.e.state, "too_cold")  # получим "critical"

    def test_07_temp_above_35(self):
        self.e.update_state(36)
        self.assertEqual(self.e.state, "overheat")  # получим "overheating" (имя другое)


class TestEchidnaBoundary(unittest.TestCase):
    """Граничные значения (раздел 4 тест-плана)"""

    def setUp(self):
        self.e = Echidna()

    def test_01_weight_lower_bound_ok(self):
        e1 = Echidna(weight=2.0)
        e2 = Echidna(weight=2.001)
        self.assertEqual(e1.weight, 2.0)
        self.assertEqual(e2.weight, 2.001)

    def test_02_weight_upper_bound_ok(self):
        e1 = Echidna(weight=7.499)
        e2 = Echidna(weight=7.5)
        self.assertEqual(e1.weight, 7.499)
        self.assertEqual(e2.weight, 7.5)

    def test_03_weight_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Echidna(weight=1.999)
        with self.assertRaises(ValueError):
            Echidna(weight=7.501)

    def test_04_temp_25_boundary(self):
        # 25.0 -> rem_sleep, 25.1 -> active (согласно таблице состояний)
        self.e.update_state(25.0)
        self.assertEqual(self.e.state, "rem_sleep")
        self.e.update_state(25.1)
        self.assertEqual(self.e.state, "active")

    def test_05_temp_15_boundary(self):
        # 15.0 -> torpor, 15.1 -> active (или другое?)
        self.e.update_state(15.0)
        self.assertEqual(self.e.state, "torpor")
        self.e.update_state(15.1)
        # По таблице состояний: >15 до 25 - active? В требованиях нечётко, оставим как ожидание
        self.assertIn(self.e.state, ["active"])

    def test_06_temp_5_boundary(self):
        self.e.update_state(5.0)
        self.assertEqual(self.e.state, "torpor")
        self.e.update_state(4.9)
        self.assertEqual(self.e.state, "too_cold")

    def test_07_temp_32_boundary(self):
        self.e.update_state(32.0)
        self.assertEqual(self.e.state, "active")
        self.e.update_state(32.1)
        self.assertEqual(self.e.state, "hibernation")

    def test_08_sprint_duration_boundary(self):
        # 30.0 сек - ок, 30.1 сек - ошибка
        self.e.sprint(30/3600)
        with self.assertRaises(ValueError):
            self.e.sprint(30.1/3600)

    def test_09_walk_speed_bounds(self):
        # Проверим, что walk возвращает расстояние от 2 до 3 км/ч
        for _ in range(20):
            dist = self.e.walk(1)
            self.assertGreaterEqual(dist, 2.0)
            self.assertLessEqual(dist, 3.0)

    def test_10_run_speed_bounds(self):
        for _ in range(20):
            dist = self.e.run(1)
            self.assertGreaterEqual(dist, 10.0)
            self.assertLessEqual(dist, 15.0)


if __name__ == '__main__':
    unittest.main()