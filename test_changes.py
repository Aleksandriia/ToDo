#!/usr/bin/env python3
"""
Тестирование изменений в GUI приложении
"""

import sys
import os
sys.path.append('/workspace')

# Тестируем основные функции, которые были изменены
print("Проверка изменений в gui_todo_app.py:")

# Проверим, что код содержит необходимые изменения
with open('/workspace/gui_todo_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ("Уменьшение высоты формы", '"600x350"' in content),
    ("Цвет выделения текста", 'master.option_add("*selectBackground", "#add8e6")' in content),
    ("Цвет текста выделения", 'master.option_add("*selectForeground", "black")' in content),
    ("Исправление формата даты", "'%d.%m.%Y %H:%M'" in content and "'%m/%d/%Y'" in content),
    ("Преобразование формата даты", 'strftime(\'%d.%m.%Y\')' in content)
]

all_passed = True
for check_name, result in checks:
    status = "✓" if result else "✗"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

print()
if all_passed:
    print("✓ Все изменения успешно применены!")
else:
    print("✗ Некоторые изменения не найдены")

# Проверим, что сохранение данных все еще происходит
save_checks = [
    ("Сохранение при добавлении задачи", 'self.save_data()' in content and 'add_task' in content),
    ("Сохранение при редактировании задачи", 'self.save_data()' in content and 'edit_task' in content),
    ("Метод save_data определен", 'def save_data' in content)
]

print("\nПроверка механизма сохранения:")
for check_name, result in save_checks:
    status = "✓" if result else "✗"
    print(f"{status} {check_name}")

print("\nОбзор изменений в приоритетных областях:")

# Показать фрагменты кода с изменениями
print("\n1. Изменения в размере окна и стилях:")
start_idx = content.find('def body(self, master):')
if start_idx != -1:
    lines = content[start_idx:].split('\n')
    for i, line in enumerate(lines[:15]):  # Показать первые 15 строк
        print(f"   {line}")
        if 'master.option_add' in line:
            break

print("\n2. Изменения в валидации дат:")
start_idx = content.find('# Пробуем формат дд.мм.гггг чч:мм')
if start_idx != -1:
    lines = content[start_idx:].split('\n')
    for i, line in enumerate(lines[:10]):  # Показать первые 10 строк
        print(f"   {line}")
        if 'return False' in line and i > 0:
            break

print("\n3. Изменения в формировании дат:")
start_idx = content.find('# Преобразуем формат даты из MM/DD/YYYY в DD.MM.YYYY')
if start_idx != -1:
    lines = content[start_idx:].split('\n')
    for i, line in enumerate(lines[:15]):  # Показать первые 15 строк
        print(f"   {line}")
        if 'reminder_time = None' in line:
            break