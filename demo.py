#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа возможностей приложения ToDo
"""

from todo_app import TodoList
import datetime

def demo():
    print("=== Демонстрация ToDo-приложения с напоминаниями ===\n")
    
    # Создаем экземпляр списка задач
    todo_list = TodoList("demo_data.json")
    
    # Добавляем несколько задач
    print("1. Добавляем задачи...")
    
    # Задача без срока и напоминания
    todo_list.add_task("Изучить Python", "Пройти базовый курс по Python")
    
    # Задача с датой выполнения
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    todo_list.add_task("Купить продукты", "Молоко, хлеб, яйца", due_date=tomorrow)
    
    # Задача с напоминанием
    next_hour = datetime.datetime.now() + datetime.timedelta(hours=1)
    todo_list.add_task("Встреча с другом", "Обсудить совместный проект", reminder_time=next_hour)
    
    # Задача с датой выполнения и напоминанием
    due_in_two_days = datetime.datetime.now() + datetime.timedelta(days=2)
    reminder_in_one_day = datetime.datetime.now() + datetime.timedelta(days=1)
    todo_list.add_task("Подготовить презентацию", "Создать слайды для встречи", due_date=due_in_two_days, reminder_time=reminder_in_one_day)
    
    print()
    
    # Показываем все задачи
    print("2. Все задачи:")
    todo_list.list_tasks()
    
    # Помечаем одну задачу как выполненную
    print("3. Отмечаем первую задачу как выполненную:")
    if todo_list.tasks:
        first_task_id = todo_list.tasks[0].id
        todo_list.mark_completed(first_task_id)
    
    print()
    
    # Показываем невыполненные задачи
    print("4. Невыполненные задачи:")
    todo_list.list_tasks(show_completed=False)
    
    # Проверяем ближайшие напоминания
    print("5. Ближайшие напоминания:")
    upcoming = todo_list.get_upcoming_reminders()
    if upcoming:
        for task in upcoming:
            print(f"  - {task} (напоминание: {task.reminder_time.strftime('%d.%m.%Y %H:%M')})")
    else:
        print("  Нет ближайших напоминаний.")
    
    print()
    
    # Сохраняем данные
    todo_list.save_to_file()
    
    print("\n=== Демонстрация завершена ===")

if __name__ == "__main__":
    demo()