from dataclasses import dataclass
from datetime import time
import re

@dataclass
class MenuItem:
    name: str
    price: float
    cook_time: time
    color: str  # НОВОЕ ПОЛЕ

def parse_menu_item(input_str: str):
    # Обновляем регулярное выражение для поддержки цвета
    pattern = r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})(?:\s+([a-zA-Zа-яА-Я]+))?'
    match = re.match(pattern, input_str.strip())
    
    if not match:
        return None

    name = match.group(1)
    price = float(match.group(2))
    hours = int(match.group(3))
    minutes = int(match.group(4))
    color = match.group(5) if match.group(5) else "не указан"  # Если цвет не указан
    
    cook_time = time(hours, minutes)
    return MenuItem(name, price, cook_time, color)

menu = []

print('ВВОД МЕНЮ')
print('='*50)
print('Формат: "Название" цена время(чч:мм) [цвет]')
print('Пример: "Борщ украинский" 5.75 01:30 красный')
print('Для завершения введите: stop')
print('='*50 + '\n')

while True:
    user_input = input("Ввод: ").strip()

    if user_input.lower() == "stop":
        break
    
    if not user_input:
        continue

    item = parse_menu_item(user_input)
    if item:
        menu.append(item)
        print(f"✅ Добавлено: {item.name} (цвет: {item.color})\n")
    else:
        print("❌ Неверный формат. Попробуйте снова.\n")

if menu:
    print("\n" + "="*60)
    print("СФОРМИРОВАННОЕ МЕНЮ:")
    print("="*60)
    for i, item in enumerate(menu, 1):
        print(f"{i:2}. {item.name:<20} | {item.price:>5.2f} руб | {item.cook_time.strftime('%H:%M')} | Цвет: {item.color}")
    print("="*60)
    print(f"Всего блюд: {len(menu)}")
else:
    print("\nМеню пусто (ни одного блюда не добавлено)")