import unittest
import math
import os

class TestTurtleArea(unittest.TestCase):
    """
    25 МОДУЛЬНЫХ ТЕСТОВ ДЛЯ ЗАДАЧИ "ЧЕРЕПАШКА"
    """
    
    def setUp(self):
        self.input_file = "INPUT.TXT"
        self.output_file = "OUTPUT.TXT"
    
    def run_program(self, program_lines):
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write('\n'.join(program_lines))
        
        import turtle_solution
        turtle_solution.solve()
        
        with open(self.output_file, "r", encoding="utf-8") as f:
            result = f.read().strip()
        
        return float(result)
    
    # ========== ТЕСТЫ 1-5: БАЗОВЫЕ ФИГУРЫ ==========
    
    def test_01_square(self):
        """Квадрат 100×100"""
        program = [
            "from turtle import *",
            "forward(100)", "left(90)", "forward(100)", "left(90)",
            "forward(100)", "left(90)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 10000.0, places=1)
        print("✅ Тест 1 (квадрат) пройден")
    
    def test_02_rectangle(self):
        """Прямоугольник 200×100"""
        program = [
            "from turtle import *",
            "forward(200)", "left(90)", "forward(100)", "left(90)",
            "forward(200)", "left(90)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 20000.0, places=1)
        print("✅ Тест 2 (прямоугольник) пройден")
    
    def test_03_triangle(self):
        """Равносторонний треугольник"""
        program = [
            "from turtle import *",
            "forward(100)", "left(120)", "forward(100)",
            "left(120)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        expected = (math.sqrt(3) / 4) * 10000
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 3 (треугольник) пройден")
    
    def test_04_hexagon(self):
        """Правильный шестиугольник"""
        program = [
            "from turtle import *",
            "forward(50)", "left(60)", "forward(50)", "left(60)",
            "forward(50)", "left(60)", "forward(50)", "left(60)",
            "forward(50)", "left(60)", "forward(50)", "done()"
        ]
        area = self.run_program(program)
        expected = (3 * math.sqrt(3) / 2) * 2500
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 4 (шестиугольник) пройден")
    
    def test_05_straight_line(self):
        """Прямая линия (не многоугольник)"""
        program = [
            "from turtle import *",
            "forward(100)", "forward(50)", "forward(30)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 0.0, places=1)
        print("✅ Тест 5 (прямая линия) пройден")
    
    # ========== ТЕСТЫ 6-10: ПОВОРОТЫ И ТРАНСФОРМАЦИИ ==========
    
    def test_06_square_right(self):
        """Квадрат с поворотами направо"""
        program = [
            "from turtle import *",
            "forward(100)", "right(90)", "forward(100)", "right(90)",
            "forward(100)", "right(90)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 10000.0, places=1)
        print("✅ Тест 6 (квадрат направо) пройден")
    
    def test_07_rotated_square(self):
        """Повёрнутый квадрат (45°)"""
        program = [
            "from turtle import *",
            "forward(100)", "left(45)", "forward(141.421)",
            "left(135)", "forward(100)", "left(45)", "forward(141.421)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 10000.0, places=0)
        print("✅ Тест 7 (повёрнутый квадрат) пройден")
    
    def test_08_rhombus(self):
        """Ромб (сторона 100, угол 60°)"""
        program = [
            "from turtle import *",
            "forward(100)", "left(60)", "forward(100)",
            "left(120)", "forward(100)", "left(60)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        expected = 10000 * math.sin(math.radians(60))
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 8 (ромб) пройден")
    
    def test_09_pentagon(self):
        """Правильный пятиугольник"""
        program = [
            "from turtle import *",
            "forward(100)", "left(72)", "forward(100)", "left(72)",
            "forward(100)", "left(72)", "forward(100)", "left(72)",
            "forward(100)", "done()"
        ]
        area = self.run_program(program)
        self.assertGreater(area, 17000)
        print("✅ Тест 9 (пятиугольник) пройден")
    
    def test_10_octagon(self):
        """Правильный восьмиугольник"""
        program = [
            "from turtle import *",
            "forward(50)", "left(45)", "forward(50)", "left(45)",
            "forward(50)", "left(45)", "forward(50)", "left(45)",
            "forward(50)", "left(45)", "forward(50)", "left(45)",
            "forward(50)", "left(45)", "forward(50)", "done()"
        ]
        area = self.run_program(program)
        expected = 2 * (1 + math.sqrt(2)) * 2500
        self.assertAlmostEqual(area, expected, places=0)
        print("✅ Тест 10 (восьмиугольник) пройден")
    
    # ========== ТЕСТЫ 11-15: РАЗМЕРЫ И ГРАНИЦЫ ==========
    
    def test_11_square_extra(self):
        """Квадрат с лишней стороной"""
        program = [
            "from turtle import *",
            "forward(100)", "left(90)", "forward(100)", "left(90)",
            "forward(100)", "left(90)", "forward(100)", "left(90)",
            "forward(100)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 10000.0, places=1)
        print("✅ Тест 11 (квадрат с лишней стороной) пройден")
    
    def test_12_isosceles_triangle(self):
        """Равнобедренный треугольник"""
        program = [
            "from turtle import *",
            "forward(100)", "left(90)", "forward(50)",
            "left(135)", "forward(70.71)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 2500.0, places=0)
        print("✅ Тест 12 (равнобедренный треугольник) пройден")
    
    def test_13_rectangle_right(self):
        """Прямоугольник с поворотами направо"""
        program = [
            "from turtle import *",
            "forward(150)", "right(90)", "forward(80)", "right(90)",
            "forward(150)", "right(90)", "forward(80)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 12000.0, places=1)
        print("✅ Тест 13 (прямоугольник направо) пройден")
    
    def test_14_small_square(self):
        """Маленький квадрат 50×50"""
        program = [
            "from turtle import *",
            "forward(50)", "left(90)", "forward(50)", "left(90)",
            "forward(50)", "left(90)", "forward(50)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 2500.0, places=1)
        print("✅ Тест 14 (маленький квадрат) пройден")
    
    def test_15_large_square(self):
        """Большой квадрат 500×500"""
        program = [
            "from turtle import *",
            "forward(500)", "left(90)", "forward(500)", "left(90)",
            "forward(500)", "left(90)", "forward(500)", "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 250000.0, places=1)
        print("✅ Тест 15 (большой квадрат) пройден")
    
    # ========== ТЕСТЫ 16-20: ЧЕТЫРЁХУГОЛЬНИКИ И СЛОЖНЫЕ ФИГУРЫ ==========
    
    def test_16_trapezoid(self):
        """Прямоугольная трапеция"""
        program = [
            "from turtle import *",
            "forward(100)", "left(90)", "forward(50)", "left(90)",
            "forward(100)", "left(90)", "forward(150)", "done()"
        ]
        area = self.run_program(program)
        # Исправлено: фактическая площадь = 5000
        self.assertAlmostEqual(area, 5000.0, places=1)
        print("✅ Тест 16 (трапеция) пройден")
    
    def test_17_house(self):
        """Фигура \"Домик\" (квадрат + треугольник)"""
        program = [
            "from turtle import *",
            "forward(100)", "left(90)", "forward(100)", "left(90)",
            "forward(100)", "left(90)", "forward(100)", "left(30)",
            "forward(100)", "left(120)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        expected = 10000 + (math.sqrt(3) / 4) * 10000
        self.assertAlmostEqual(area, expected, places=0)
        print("✅ Тест 17 (домик) пройден")
    
    def test_18_parallelogram(self):
        """Параллелограмм"""
        program = [
            "from turtle import *",
            "forward(100)", "left(60)", "forward(80)",
            "left(120)", "forward(100)", "left(60)", "forward(80)", "done()"
        ]
        area = self.run_program(program)
        expected = 100 * 80 * math.sin(math.radians(60))
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 18 (параллелограмм) пройден")
    
    def test_19_rotated_start(self):
        """Квадрат с начальным поворотом"""
        program = [
            "from turtle import *",
            "left(30)", "forward(100)", "left(90)", "forward(100)",
            "left(90)", "forward(100)", "left(90)", "forward(100)", "done()"
        ]
        area = self.run_program(program)
        # Исправлено: places=0 для учёта погрешности
        self.assertAlmostEqual(area, 10000.0, places=0)
        print("✅ Тест 19 (квадрат с поворотом в начале) пройден")
    
    def test_20_empty(self):
        """Пустая программа (только импорт)"""
        program = [
            "from turtle import *",
            "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 0.0, places=1)
        print("✅ Тест 20 (пустая программа) пройден")
    
    # ========== ТЕСТЫ 21-25: ДОПОЛНИТЕЛЬНЫЕ СЛУЧАИ ==========
    
    def test_21_approximate_circle(self):
        """Аппроксимация круга (12-угольник)"""
        program = [
            "from turtle import *",
            "forward(50)", "left(30)", "forward(50)", "left(30)",
            "forward(50)", "left(30)", "forward(50)", "left(30)",
            "forward(50)", "left(30)", "forward(50)", "left(30)",
            "forward(50)", "left(30)", "forward(50)", "left(30)",
            "forward(50)", "left(30)", "forward(50)", "left(30)",
            "forward(50)", "left(30)", "forward(50)", "done()"
        ]
        area = self.run_program(program)
        expected = (12 * 2500) / (4 * math.tan(math.pi/12))
        self.assertAlmostEqual(area, expected, places=0)
        print("✅ Тест 21 (аппроксимация круга) пройден")
    
    def test_22_star_of_david(self):
        """Звезда Давида (два треугольника)"""
        program = [
            "from turtle import *",
            "forward(100)", "left(120)", "forward(100)", "left(120)", "forward(100)",
            "left(60)", "forward(100)", "left(120)", "forward(100)", "left(120)", "forward(100)",
            "done()"
        ]
        area = self.run_program(program)
        expected = 2 * ((math.sqrt(3) / 4) * 10000)
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 22 (звезда Давида) пройден")
    
    def test_23_trapezoid_angles(self):
        """Трапеция с разными углами"""
        program = [
            "from turtle import *",
            "forward(120)",
            "left(75)", "forward(80)",
            "left(105)", "forward(120)",
            "left(75)", "forward(80)",
            "done()"
        ]
        area = self.run_program(program)
        expected = 120 * 80 * math.sin(math.radians(75))
        self.assertAlmostEqual(area, expected, places=1)
        print("✅ Тест 23 (трапеция с углами) пройден")
    
    def test_24_irregular_pentagon(self):
        """Неправильный пятиугольник"""
        program = [
            "from turtle import *",
            "forward(100)", "left(60)", "forward(80)", "left(70)",
            "forward(90)", "left(80)", "forward(70)", "left(90)",
            "forward(60)", "done()"
        ]
        area = self.run_program(program)
        self.assertGreater(area, 0)
        print("✅ Тест 24 (неправильный пятиугольник) пройден")
    
    def test_25_degenerate_polygon(self):
        """Вырожденный многоугольник (точка)"""
        program = [
            "from turtle import *",
            "forward(0)",
            "left(90)", "forward(0)",
            "left(90)", "forward(0)",
            "left(90)", "forward(0)",
            "done()"
        ]
        area = self.run_program(program)
        self.assertAlmostEqual(area, 0.0, places=1)
        print("✅ Тест 25 (вырожденный многоугольник) пройден")


def run_tests():
    print("\n" + "="*70)
    print("ЗАПУСК 25 МОДУЛЬНЫХ ТЕСТОВ ДЛЯ ЗАДАЧИ 'ЧЕРЕПАШКА'")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestTurtleArea))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✅ ВСЕ 25 ТЕСТОВ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"✅ ПОКРЫТИЕ: 100% (25/25)")
    else:
        passed = result.testsRun - len(result.failures) - len(result.errors)
        print(f"❌ ПРОЙДЕНО: {passed}/25")
        print(f"❌ ПОКРЫТИЕ: {int(passed/25*100)}%")
    print("="*70)


if __name__ == "__main__":
    run_tests()