#!/usr/bin/env python3
"""
Приложение ToDo-листа с напоминаниями
"""

import datetime
import json
from typing import List, Dict, Optional


class Task:
    """Класс для представления задачи"""
    
    def __init__(self, title: str, description: str = "", due_date: Optional[datetime.datetime] = None, reminder_time: Optional[datetime.datetime] = None):
        self.id = id(self)  # Простой способ генерации ID
        self.title = title
        self.description = description
        self.due_date = due_date
        self.reminder_time = reminder_time
        self.completed = False
        self.created_at = datetime.datetime.now()
    
    def to_dict(self) -> Dict:
        """Преобразовать задачу в словарь для сохранения"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Создать задачу из словаря"""
        task = cls.__new__(cls)
        task.id = data['id']
        task.title = data['title']
        task.description = data['description']
        task.due_date = datetime.datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        task.reminder_time = datetime.datetime.fromisoformat(data['reminder_time']) if data['reminder_time'] else None
        task.completed = data['completed']
        task.created_at = datetime.datetime.fromisoformat(data['created_at'])
        return task
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        due_str = f", срок: {self.due_date.strftime('%d.%m.%Y %H:%M')}" if self.due_date else ""
        return f"[{status}] {self.title}{due_str}"


class TodoList:
    """Класс для управления списком задач"""
    
    def __init__(self, filename: str = "todo_data.json"):
        self.tasks: List[Task] = []
        self.filename = filename
        self.load_from_file()
    
    def add_task(self, title: str, description: str = "", due_date: Optional[datetime.datetime] = None, reminder_time: Optional[datetime.datetime] = None):
        """Добавить новую задачу"""
        task = Task(title, description, due_date, reminder_time)
        self.tasks.append(task)
        print(f"Задача '{title}' добавлена!")
        return task
    
    def remove_task(self, task_id: int):
        """Удалить задачу по ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                removed_task = self.tasks.pop(i)
                print(f"Задача '{removed_task.title}' удалена!")
                return True
        print("Задача не найдена!")
        return False
    
    def mark_completed(self, task_id: int):
        """Отметить задачу как выполненную"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                print(f"Задача '{task.title}' отмечена как выполненная!")
                return True
        print("Задача не найдена!")
        return False
    
    def list_tasks(self, show_completed: bool = True):
        """Вывести список задач"""
        if not self.tasks:
            print("Список задач пуст!")
            return
        
        print("\n--- Список задач ---")
        for task in self.tasks:
            if show_completed or not task.completed:
                print(task)
        print("--------------------\n")
    
    def get_upcoming_reminders(self) -> List[Task]:
        """Получить задачи с напоминаниями, которые скоро наступят"""
        now = datetime.datetime.now()
        upcoming = []
        
        for task in self.tasks:
            if task.reminder_time and task.reminder_time >= now and not task.completed:
                if (task.reminder_time - now).total_seconds() <= 3600:  # В течение часа
                    upcoming.append(task)
        
        return upcoming
    
    def save_to_file(self):
        """Сохранить задачи в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)
        print("Данные сохранены!")
    
    def load_from_file(self):
        """Загрузить задачи из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
            print("Данные загружены!")
        except FileNotFoundError:
            print("Файл данных не найден, будет создан новый список задач.")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            self.tasks = []


def parse_datetime(date_str: str) -> Optional[datetime.datetime]:
    """Преобразовать строку даты в объект datetime"""
    try:
        # Попробуем разные форматы даты
        formats = [
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    except Exception:
        return None


def main():
    """Основная функция приложения"""
    todo_list = TodoList()
    
    print("Добро пожаловать в приложение ToDo с напоминаниями!")
    
    while True:
        print("\nВыберите действие:")
        print("1. Добавить задачу")
        print("2. Просмотреть все задачи")
        print("3. Отметить задачу как выполненную")
        print("4. Удалить задачу")
        print("5. Проверить напоминания")
        print("6. Сохранить и выйти")
        
        choice = input("Введите номер действия: ").strip()
        
        if choice == "1":
            title = input("Название задачи: ")
            description = input("Описание (необязательно): ")
            
            due_date_str = input("Срок выполнения (дд.мм.гггг чч:мм или дд.мм.гггг): ")
            due_date = parse_datetime(due_date_str) if due_date_str else None
            
            reminder_str = input("Время напоминания (дд.мм.гггг чч:мм или дд.мм.гггг): ")
            reminder_time = parse_datetime(reminder_str) if reminder_str else None
            
            todo_list.add_task(title, description, due_date, reminder_time)
        
        elif choice == "2":
            show_completed = input("Показать выполненные задачи? (y/n): ").lower() != 'n'
            todo_list.list_tasks(show_completed)
        
        elif choice == "3":
            todo_list.list_tasks(False)  # Показываем только невыполненные
            try:
                task_id = int(input("ID задачи для отметки как выполненной: "))
                todo_list.mark_completed(task_id)
            except ValueError:
                print("Неверный ID задачи!")
        
        elif choice == "4":
            todo_list.list_tasks()
            try:
                task_id = int(input("ID задачи для удаления: "))
                todo_list.remove_task(task_id)
            except ValueError:
                print("Неверный ID задачи!")
        
        elif choice == "5":
            upcoming = todo_list.get_upcoming_reminders()
            if upcoming:
                print("\nБлижайшие напоминания:")
                for task in upcoming:
                    print(f"- {task} (напоминание: {task.reminder_time.strftime('%d.%m.%Y %H:%M')})")
            else:
                print("Нет ближайших напоминаний.")
        
        elif choice == "6":
            todo_list.save_to_file()
            print("До свидания!")
            break
        
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()