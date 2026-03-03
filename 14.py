from dataclasses import dataclass
from datetime import time
import re

@dataclass
class MenuItem:
    name: str
    price: float
    cook_time: time
    color: str  # поле из ветки color

def parse_menu_item(input_str: str):
    # Поддерживаем и цвет, и без цвета (из color)
    pattern = r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})(?:\s+([a-zA-Zа-яА-Я]+))?'
    match = re.match(pattern, input_str.strip())
    
    if not match:
        return None

    name = match.group(1)
    price = float(match.group(2))
    hours = int(match.group(3))
    minutes = int(match.group(4))
    color = match.group(5) if match.group(5) else "не указан"
    
    cook_time = time(hours, minutes)
    return MenuItem(name, price, cook_time, color)

def show_menu(items):
    """Функция для вывода меню (из menu)"""
    if not items:
        print("\nМеню пусто")
        return
    
    print("\n" + "="*70)
    print("ТЕКУЩЕЕ МЕНЮ:")
    print("="*70)
    for i, item in enumerate(items, 1):
        # Добавляем цвет в вывод (из color)
        print(f"{i:2}. {item.name:<20} | {item.price:>5.2f} руб | {item.cook_time.strftime('%H:%M')} | Цвет: {item.color}")
    print("="*70)
    print(f"Всего блюд: {len(items)}")

def main():
    """Основная функция программы"""
    menu = []
    
    print('УПРАВЛЕНИЕ МЕНЮ')
    print('='*70)
    print('1 - Добавить новое блюдо')
    print('2 - Показать всё меню')
    print('stop - Завершить работу')
    print('='*70)
    print('\nФормат ввода: "Название" цена время(чч:мм) [цвет]')
    print('Пример: "Борщ" 5.75 01:30 красный')
    print('Цвет можно не указывать\n')

    while True:
        print()
        choice = input("Выберите действие (1, 2 или stop): ").strip()
        
        if choice.lower() == "stop":
            print("Программа завершена")
            break
        
        elif choice == "1":
            print("\n--- ДОБАВЛЕНИЕ НОВОГО БЛЮДА ---")
            user_input = input("Ввод: ").strip()
            
            if not user_input:
                print("Пустой ввод")
                continue
                
            item = parse_menu_item(user_input)
            if item:
                menu.append(item)
                print(f"Добавлено: {item.name} (цвет: {item.color})")
            else:
                print("Неверный формат")
                print("Правильный формат: \"Название\" цена время(чч:мм) [цвет]")
        
        elif choice == "2":
            show_menu(menu)
        
        else:
            print("Неверный выбор. Введите 1, 2 или stop")

if __name__ == "__main__":
    main()