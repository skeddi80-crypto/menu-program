import unittest
import os
import tempfile
from datetime import time
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lab4_menu import MenuItem, FileManager, Model, ValidationError, ParseError

class TestMenuItem(unittest.TestCase):
    def setUp(self):
        self.obj = MenuItem("Борщ", 5.75, time(1,30), "красный")
    
    def test_creation(self):
        self.assertEqual(self.obj.name, "Борщ")
        print("Тест 1: Создание объекта")
    
    def test_empty_name(self):
        with self.assertRaises(ValidationError):
            MenuItem("", 5.75, time(1,30), "красный")
        print("Тест 2: Пустое название")
    
    def test_zero_price(self):
        with self.assertRaises(ValidationError):
            MenuItem("Борщ", 0, time(1,30), "красный")
        print("Тест 3: Цена = 0")
    
    def test_negative_price(self):
        with self.assertRaises(ValidationError):
            MenuItem("Борщ", -5.75, time(1,30), "красный")
        print("Тест 4: Отрицательная цена")
    
    def test_from_str_valid(self):
        obj = MenuItem.from_str('"Борщ" 5.75 01:30 красный')
        self.assertEqual(obj.name, "Борщ")
        print("Тест 5: Парсинг корректной строки")
    
    def test_from_str_no_color(self):
        obj = MenuItem.from_str('"Борщ" 5.75 01:30')
        self.assertEqual(obj.color, "не указан")
        print("Тест 6: Парсинг без цвета")
    
    def test_from_str_no_quotes(self):
        with self.assertRaises(ParseError):
            MenuItem.from_str('Борщ 5.75 01:30')
        print("Тест 7: Ошибка - нет кавычек")
    
    def test_from_str_invalid_time(self):
        with self.assertRaises(ParseError):
            MenuItem.from_str('"Борщ" 5.75 25:61')
        print("Тест 8: Ошибка - неверное время")
    
    def test_to_list(self):
        lst = self.obj.to_list()
        self.assertEqual(lst[0], "Борщ")
        print("Тест 9: Преобразование в список")

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp.close()
        self.fm = FileManager(self.temp.name)
    
    def tearDown(self):
        if os.path.exists(self.temp.name): os.unlink(self.temp.name)
    
    def test_save_and_load(self):
        obj = MenuItem("Борщ", 5.75, time(1,30), "красный")
        self.fm.save([obj])
        objs = self.fm.load()
        self.assertEqual(len(objs), 1)
        print("Тест 10: Сохранение и загрузка")
    
    def test_load_invalid_lines(self):
        with open(self.temp.name, 'w', encoding='utf-8') as f:
            f.write('"Борщ" 5.75 01:30 красный\n')
            f.write('Борщ 5.75 01:30\n')  # некорректная
        objs = self.fm.load()
        self.assertEqual(len(objs), 1)
        print("Тест 11: Пропуск некорректных строк")

class TestModel(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp.close()
        self.model = Model(self.temp.name)
    
    def tearDown(self):
        if os.path.exists(self.temp.name): os.unlink(self.temp.name)
    
    def test_add(self):
        self.model.add("Борщ", 5.75, time(1,30), "красный")
        self.assertEqual(len(self.model.get_all()), 1)
        print("Тест 12: Добавление объекта")
    
    def test_add_invalid(self):
        with self.assertRaises(ValidationError):
            self.model.add("", 5.75, time(1,30), "красный")
        print("Тест 13: Ошибка при добавлении")
    
    def test_delete(self):
        self.model.add("Борщ", 5.75, time(1,30), "красный")
        self.model.delete(0)
        self.assertEqual(len(self.model.get_all()), 0)
        print("Тест 14: Удаление объекта")
    
    def test_persistence(self):
        self.model.add("Борщ", 5.75, time(1,30), "красный")
        new_model = Model(self.temp.name)
        self.assertEqual(len(new_model.get_all()), 1)
        print("Тест 15: Сохранение между сессиями")

def run_tests():
    print("\n" + "="*50)
    print("ЗАПУСК ТЕСТОВ ДЛЯ ПРОГРАММЫ УПРАВЛЕНИЯ МЕНЮ")
    print("="*50 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestMenuItem))
    suite.addTests(loader.loadTestsFromTestCase(TestFileManager))
    suite.addTests(loader.loadTestsFromTestCase(TestModel))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*50)
    if result.wasSuccessful():
        print(f"✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ({result.testsRun} тестов)")
        return True
    else:
        print(f"❌ ПРОЙДЕНО: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun}")
        print("="*50)
        return False

if __name__ == "__main__":
    result = run_tests()
    exit(0 if result else 1)