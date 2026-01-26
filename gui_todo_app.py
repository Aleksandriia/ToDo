import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
import uuid


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo List с Напоминаниями")
        self.root.geometry("800x600")
        
        # Настройка минимального размера окна
        self.root.minsize(600, 400)

        # Имя файла для сохранения данных
        self.data_file = "todo_data.json"
        
        # Загрузка данных
        self.tasks = self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление списка задач
        self.refresh_task_list()
        
        # Запуск проверки напоминаний
        self.check_reminders()
    
    def check_reminders(self):
        """Проверка напоминаний и отображение уведомлений"""
        now = datetime.now()
        triggered_reminders = []
        
        for task in self.tasks:
            if task['reminder_time'] and not task['completed']:
                # Преобразуем строку даты в объект datetime
                try:
                    reminder_dt = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                    if reminder_dt <= now:
                        triggered_reminders.append(task)
                except ValueError:
                    try:
                        # Попробуем другой формат даты
                        reminder_dt = datetime.strptime(task['reminder_time'], '%d.%m.%Y %H:%M')
                        if reminder_dt <= now:
                            triggered_reminders.append(task)
                    except ValueError:
                        pass
        
        # Показываем уведомления для просроченных напоминаний
        for task in triggered_reminders:
            task['completed'] = True
            self.show_notification(f"Напоминание: {task['title']}", "Время выполнить задачу!")
        
        if triggered_reminders:
            self.save_data()
            self.refresh_task_list()
        
        # Запланировать следующую проверку через 1 минуту
        self.root.after(60000, self.check_reminders)
    
    def show_notification(self, title, message):
        """Показать всплывающее уведомление с звуком"""
        # Проигрываем системный звук уведомления
        self.root.bell()
        # Показываем всплывающее окно
        messagebox.showinfo(title, message)
    
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                return []
        else:
            return []
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Верхняя часть - кнопки управления
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Button(top_frame, text="Добавить задачу", command=self.add_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Редактировать задачу", command=self.edit_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Удалить задачу", command=self.delete_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Отметить как выполненное", command=self.mark_completed).pack(side=tk.LEFT, padx=(0, 5))
        
        # Средняя часть - список задач
        center_frame = ttk.Frame(self.root)
        center_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Создание TreeView для отображения задач
        columns = ("#", "Название", "Описание", "Выполнить до", "Напомнить", "Статус")
        self.tree = ttk.Treeview(center_frame, columns=columns, show="headings", height=15)
        
        # Определение заголовков
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Настройка ширины колонок с возможностью изменения
        self.tree.column("#", width=50, stretch=tk.NO)
        self.tree.column("Название", width=150, stretch=tk.YES)
        self.tree.column("Описание", width=200, stretch=tk.YES)
        self.tree.column("Выполнить до", width=120, stretch=tk.NO)
        self.tree.column("Напомнить", width=120, stretch=tk.NO)
        self.tree.column("Статус", width=80, stretch=tk.NO)
        
        # Добавление прокрутки
        scrollbar_y = ttk.Scrollbar(center_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(center_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Упаковка виджетов с правильным расположением
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Настройка веса сетки для растягивания
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        
        # Нижняя часть - информация
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.status_label = ttk.Label(bottom_frame, text="Всего задач: 0 | Выполнено: 0 | Не выполнено: 0")
        self.status_label.pack()
        
        # Привязка события двойного клика к редактированию задачи
        self.tree.bind("<Double-1>", lambda event: self.edit_task())
    
    def refresh_task_list(self):
        """Обновление списка задач в TreeView"""
        # Очистка текущего списка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление задач в список
        for i, task in enumerate(self.tasks):
            status = "Выполнена" if task['completed'] else "Не выполнена"
            
            # Преобразование дат в формат отображения
            due_date = task['due_date'] if task['due_date'] else ""
            reminder_time = task['reminder_time'] if task['reminder_time'] else ""
            
            self.tree.insert("", tk.END, values=(
                i + 1,
                task['title'],
                task['description'][:50] + "..." if len(task['description']) > 50 else task['description'],
                due_date,
                reminder_time,
                status
            ))
        
        # Обновление статуса
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task['completed'])
        pending_tasks = total_tasks - completed_tasks
        
        self.status_label.config(text=f"Всего задач: {total_tasks} | Выполнено: {completed_tasks} | Не выполнено: {pending_tasks}")
    
    def add_task(self):
        """Добавление новой задачи"""
        dialog = TaskDialog(self.root, title="Добавить задачу")
        if dialog.result:
            self.tasks.append(dialog.result)
            self.save_data()
            self.refresh_task_list()
    
    def edit_task(self):
        """Редактирование выбранной задачи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return
        
        # Получаем индекс выбранной задачи
        index = int(self.tree.item(selected_item)['values'][0]) - 1
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            dialog = TaskDialog(self.root, title="Редактировать задачу", task=task)
            if dialog.result:
                self.tasks[index] = dialog.result
                self.save_data()
                self.refresh_task_list()
    
    def delete_task(self):
        """Удаление выбранной задачи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return
        
        # Получаем индекс выбранной задачи
        index = int(self.tree.item(selected_item)['values'][0]) - 1
        if 0 <= index < len(self.tasks):
            if messagebox.askyesno("Подтверждение", "Вы действительно хотите удалить эту задачу?"):
                del self.tasks[index]
                self.save_data()
                self.refresh_task_list()
    
    def mark_completed(self):
        """Отметка задачи как выполненной"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для отметки как выполненной")
            return
        
        # Получаем индекс выбранной задачи
        index = int(self.tree.item(selected_item)['values'][0]) - 1
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            task['completed'] = not task['completed']
            self.save_data()
            self.refresh_task_list()


class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, task=None):
        self.task = task
        super().__init__(parent, title)
        self.result = None
    
    def body(self, master):
        """Создание тела диалогового окна"""
        # Поля ввода
        ttk.Label(master, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_entry = ttk.Entry(master, width=50)
        self.title_entry.grid(row=0, column=1, pady=2, padx=(10, 0), sticky="ew")
        
        ttk.Label(master, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_frame = ttk.Frame(master)
        self.desc_frame.grid(row=1, column=1, pady=2, padx=(10, 0), sticky="nsew")
        
        self.desc_text = tk.Text(self.desc_frame, width=50, height=4)
        desc_scrollbar = ttk.Scrollbar(self.desc_frame, orient=tk.VERTICAL, command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(master, text="Выполнить до (дд.мм.гггг чч:мм):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.due_entry = ttk.Entry(master, width=50)
        self.due_entry.grid(row=2, column=1, pady=2, padx=(10, 0), sticky="ew")
        
        ttk.Label(master, text="Напомнить (дд.мм.гггг чч:мм):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.reminder_entry = ttk.Entry(master, width=50)
        self.reminder_entry.grid(row=3, column=1, pady=2, padx=(10, 0), sticky="ew")
        
        # Настройка веса для растягивания
        master.columnconfigure(1, weight=1)
        master.rowconfigure(1, weight=1)
        
        # Заполнение полей если задача передана
        if self.task:
            self.title_entry.insert(0, self.task['title'])
            self.desc_text.insert(tk.END, self.task['description'])
            if self.task['due_date']:
                self.due_entry.insert(0, self.task['due_date'])
            if self.task['reminder_time']:
                self.reminder_entry.insert(0, self.task['reminder_time'])
        
        return self.title_entry  # фокус на первое поле
    
    def validate(self):
        """Проверка валидности введенных данных"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым")
            return False
        return True
    
    def apply(self):
        """Сохранение результатов"""
        # Получаем значения из полей
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        due_date = self.due_entry.get().strip() if self.due_entry.get().strip() else None
        reminder_time = self.reminder_entry.get().strip() if self.reminder_entry.get().strip() else None
        
        # Если это редактирование, сохраняем ID и статус выполнения
        if self.task:
            self.result = {
                'id': self.task['id'],
                'title': title,
                'description': description,
                'due_date': due_date,
                'reminder_time': reminder_time,
                'completed': self.task['completed']
            }
        else:
            # Новая задача
            self.result = {
                'id': str(uuid.uuid4()),
                'title': title,
                'description': description,
                'due_date': due_date,
                'reminder_time': reminder_time,
                'completed': False
            }


def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()