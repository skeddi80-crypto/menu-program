from dataclasses import dataclass
from datetime import time
import re

@dataclass
class MenuItem:
    name: str
    price: float
    cook_time: time

def parse_menu_item(input_str: str):
    pattern = r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})'
    match = re.match(pattern, input_str.strip())
    
    if not match:
        return None

    name = match.group(1)
    price = float(match.group(2))
    hours = int(match.group(3))
    minutes = int(match.group(4))
    
    cook_time = time(hours, minutes)
    return MenuItem(name, price, cook_time)

def show_menu(items):
    """Функция для вывода меню"""
    if not items:
        print("\n📋 Меню пусто")
        return
    
    print("\n" + "="*50)
    print("ТЕКУЩЕЕ МЕНЮ:")
    print("="*50)
    for i, item in enumerate(items, 1):
        print(f"{i:2}. {item.name:<20} | {item.price:>5.2f} руб | {item.cook_time.strftime('%H:%M')}")
    print("="*50)
    print(f"Всего блюд: {len(items)}")

menu = []

print('🍽️  УПРАВЛЕНИЕ МЕНЮ')
print('='*50)
print('1 - Добавить новое блюдо')
print('2 - Показать всё меню')
print('stop - Завершить работу')
print('='*50 + '\n')

while True:
    print()  # Пустая строка для читаемости
    choice = input("Выберите действие (1, 2 или stop): ").strip()
    
    if choice.lower() == "stop":
        print("👋 Программа завершена")
        break
    
    elif choice == "1":
        print("\n--- ДОБАВЛЕНИЕ НОВОГО БЛЮДА ---")
        print('Формат: "Название" цена время(чч:мм)')
        print('Пример: "Борщ украинский" 5.75 01:30')
        
        user_input = input("Ввод: ").strip()
        
        if not user_input:
            print("❌ Пустой ввод")
            continue
            
        item = parse_menu_item(user_input)
        if item:
            menu.append(item)
            print(f"✅ Добавлено: {item.name}")
        else:
            print("❌ Неверный формат")
    
    elif choice == "2":
        show_menu(menu)
    
    else:
        print("❌ Неверный выбор. Введите 1, 2 или stop")