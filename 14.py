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
    match = re.match(pattern, input_str.strip())  # .strip() добавить
    
    if not match:
        return None

    name = match.group(1)
    price = float(match.group(2))
    hours = int(match.group(3))
    minutes = int(match.group(4))
    
    cook_time = time(hours, minutes)
    return MenuItem(name, price, cook_time)

menu = []

print('ВВОД МЕНЮ')
print('='*40)
print('Формат: "Название" цена время(чч:мм)')
print('Пример: "Борщ украинский" 5.75 01:30')
print('Для завершения введите: stop')
print('='*40 + '\n')

while True:
    user_input = input("Ввод: ").strip()  # .strip() добавить

    if user_input.lower() == "stop":
        break
    
    if not user_input:  # Пропускаем пустой ввод
        continue

    item = parse_menu_item(user_input)
    if item:
        menu.append(item)
        print(f"Добавлено: {item.name}\n")
    else:
        print("Неверный формат. Попробуйте снова.\n")

if menu:  # Проверяем, есть ли объекты
    print("\n" + "="*40)
    print("СФОРМИРОВАННОЕ МЕНЮ:")
    print("="*40)
    for i, item in enumerate(menu, 1):
        print(f"{i:2}. {item.name:<20} | {item.price:>5.2f} руб | {item.cook_time.strftime('%H:%M')}")
    print("="*40)
    print(f"Всего блюд: {len(menu)}")
else:
    print("\nМеню пусто (ни одного блюда не добавлено)")