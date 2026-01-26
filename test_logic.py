import unittest
from datetime import datetime
import sys
import os

# Добавим путь к рабочей директории
sys.path.append('/workspace')

# Импортируем необходимые модули из нашего приложения
from gui_todo_app import TodoApp, TaskDialog
import tkinter as tk
from unittest.mock import Mock, patch


class TestTodoAppLogic(unittest.TestCase):
    
    def setUp(self):
        # Создаем тестовое приложение
        root = tk.Tk()
        self.app = TodoApp(root)
    
    def tearDown(self):
        # Закрываем тестовое приложение
        self.app.root.destroy()

    def test_save_data_method_exists(self):
        """Проверяем, что метод сохранения данных существует"""
        self.assertTrue(hasattr(self.app, 'save_data'))
        self.assertTrue(callable(getattr(self.app, 'save_data')))
    
    def test_load_data_method_exists(self):
        """Проверяем, что метод загрузки данных существует"""
        self.assertTrue(hasattr(self.app, 'load_data'))
        self.assertTrue(callable(getattr(self.app, 'load_data')))

    @patch('tkinter.messagebox')
    def test_add_task(self, mock_messagebox):
        """Тестируем добавление задачи"""
        initial_count = len(self.app.tasks)
        
        # Мокаем диалог создания задачи
        with patch.object(TaskDialog, '__init__', return_value=None):
            with patch.object(TaskDialog, 'result', {'id': 'test_id', 'title': 'Test Task', 'description': 'Test Description', 'due_date': None, 'reminder_time': None, 'completed': False}):
                
                self.app.add_task()
                
                # Проверяем, что задача была добавлена
                self.assertEqual(len(self.app.tasks), initial_count + 1)
                if len(self.app.tasks) > initial_count:
                    self.assertEqual(self.app.tasks[-1]['title'], 'Test Task')

    @patch('tkinter.messagebox')
    def test_edit_task(self, mock_messagebox):
        """Тестируем редактирование задачи"""
        # Добавляем тестовую задачу
        test_task = {
            'id': 'test_id',
            'title': 'Original Title',
            'description': 'Original Description',
            'due_date': None,
            'reminder_time': None,
            'completed': False
        }
        self.app.tasks.append(test_task)
        
        # Мокаем выделение задачи в дереве
        mock_selection = [(0,)]  # Индекс первой задачи
        original_selection = self.app.tree.selection
        self.app.tree.selection = lambda: ['item1']  # Мокаем selection
        
        # Мокаем метод item для возврата значений
        original_item = self.app.tree.item
        self.app.tree.item = lambda *args: {'values': (1, 'Original Title', 'Original Desc...', '', '', 'Не выполнена')}
        
        # Мокаем диалог редактирования задачи
        with patch.object(TaskDialog, '__init__', return_value=None):
            with patch.object(TaskDialog, 'result', {'id': 'test_id', 'title': 'Updated Title', 'description': 'Updated Description', 'due_date': None, 'reminder_time': None, 'completed': True}):
                
                self.app.edit_task()
                
                # Проверяем, что задача была обновлена
                if len(self.app.tasks) > 0:
                    self.assertEqual(self.app.tasks[0]['title'], 'Updated Title')
                    self.assertTrue(self.app.tasks[0]['completed'])
        
        # Восстанавливаем оригинальные методы
        self.app.tree.selection = original_selection
        self.app.tree.item = original_item


class TestTaskDialogLogic(unittest.TestCase):
    
    def test_apply_selection_style_method_exists(self):
        """Проверяем, что метод применения стиля выделения существует"""
        # Создаем фиктивный объект TaskDialog для проверки метода
        class FakeDialog:
            def __init__(self):
                self.parent = tk.Tk()
        
        # Проверяем, что в классе TaskDialog есть метод apply_selection_style
        self.assertTrue(hasattr(TaskDialog, 'apply_selection_style'))
        self.assertTrue(callable(getattr(TaskDialog, 'apply_selection_style')))


def test_date_format_conversion():
    """Тест конвертации формата даты"""
    # Тестируем различные форматы дат
    from datetime import datetime
    
    # Тест 1: MM/DD/YYYY -> DD.MM.YYYY
    date_str = '01/15/2024'
    try:
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        converted = dt.strftime('%d.%m.%Y')
        print(f"Конвертация {date_str} -> {converted}")
        assert converted == '15.01.2024'
        print("✓ Конвертация MM/DD/YYYY -> DD.MM.YYYY работает")
    except ValueError:
        print("✗ Ошибка конвертации MM/DD/YYYY -> DD.MM.YYYY")
    
    # Тест 2: DD.MM.YYYY -> DD.MM.YYYY (без изменений)
    date_str = '15.01.2024'
    try:
        dt = datetime.strptime(date_str, '%d.%m.%Y')
        converted = dt.strftime('%d.%m.%Y')
        print(f"Формат {date_str} остается как {converted}")
        assert converted == '15.01.2024'
        print("✓ Формат DD.MM.YYYY сохраняется")
    except ValueError:
        print("✗ Ошибка с форматом DD.MM.YYYY")


if __name__ == '__main__':
    print("=== Тестирование логики приложения задач ===\n")
    
    # Тестирование конвертации дат
    test_date_format_conversion()
    print()
    
    # Запуск юнит-тестов
    unittest.main(argv=[''], exit=False, verbosity=2)