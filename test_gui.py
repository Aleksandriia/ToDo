#!/usr/bin/env python3
"""
Тестовый скрипт для проверки GUI приложения ToDo
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_todo_app import TodoApp

def test_gui():
    """Тестирование GUI приложения"""
    root = tk.Tk()
    root.title("Тестирование ToDo приложения")
    root.geometry("800x600")
    
    app = TodoApp(root)
    
    print("GUI запущен. Проверьте, что:")
    print("- При выделении текста в полях ввода (заголовок, время) используется голубой фон и черный текст")
    print("- При выделении текста в поле описания также используется голубой фон и черный текст")
    print("- Все задачи сохраняются при добавлении/редактировании")
    
    root.mainloop()

if __name__ == "__main__":
    test_gui()