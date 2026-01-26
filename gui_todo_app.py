import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
import uuid
try:
    from tkcalendar import DateEntry
except ImportError:
    # Если tkcalendar не установлен, будем использовать простые поля ввода
    DateEntry = None


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo List с Напоминаниями")
        self.root.geometry("800x600")
        
        # Настройка минимального размера окна
        self.root.minsize(800, 600)

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
                # Проверяем, было ли уже показано уведомление для этой задачи
                if task.get('reminder_shown', False):
                    continue  # Пропускаем, если уже показывали уведомление
                
                # Пытаемся распознать формат даты
                try:
                    reminder_dt = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                    if reminder_dt <= now:
                        triggered_reminders.append(task)
                        task['reminder_shown'] = True  # Отмечаем, что уведомление было показано
                except ValueError:
                    try:
                        # Пробуем другой формат даты
                        reminder_dt = datetime.strptime(task['reminder_time'], '%d.%m.%Y %H:%M')
                        if reminder_dt <= now:
                            triggered_reminders.append(task)
                            task['reminder_shown'] = True  # Отмечаем, что уведомление было показано
                    except ValueError:
                        pass
        
        # Показываем уведомления для просроченных напоминаний
        for task in triggered_reminders:
            self.show_notification(f"Напоминание: {task['title']}", "Время выполнить задачу!")
        
        if triggered_reminders:
            self.save_data()
            # Обновляем интерфейс, чтобы отобразить изменения
            self.root.after(0, self.refresh_task_list)
        
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
        # Настройка стиля для TreeView
        style = ttk.Style()
        style.map("Treeview", 
                  background=[('selected', '#add8e6')],  # Голубой цвет для выделения
                  foreground=[('selected', 'black')])   # Черный цвет текста для выделения
        
        # Верхняя часть - кнопки управления
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Button(top_frame, text="Добавить задачу", command=self.add_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Редактировать задачу", command=self.edit_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="Удалить задачу", command=self.delete_task).pack(side=tk.LEFT, padx=(0, 5))
        self.mark_button = ttk.Button(top_frame, text="Отметить как выполненное", command=self.mark_completed)
        self.mark_button.pack(side=tk.LEFT, padx=(0, 5))
        
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
        self.tree.column("Выполнить до", width=120, stretch=tk.YES)
        self.tree.column("Напомнить", width=120, stretch=tk.YES)
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
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.update_mark_button_text())
    
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
        
        # Обновляем текст кнопки выполнения в зависимости от выделенной задачи
        self.update_mark_button_text()
    
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
    
    def update_mark_button_text(self):
        """Обновление текста кнопки выполнения в зависимости от выделенной задачи"""
        selected_item = self.tree.selection()
        if selected_item:
            index = int(self.tree.item(selected_item)['values'][0]) - 1
            if 0 <= index < len(self.tasks):
                task = self.tasks[index]
                if task['completed']:
                    self.mark_button.config(text="Отменить выполнение")
                else:
                    self.mark_button.config(text="Отметить как выполненное")
        else:
            self.mark_button.config(text="Отметить как выполненное")

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
    
    def buttonbox(self):
        """Создание кнопок диалогового окна с измененным текстом"""
        box = ttk.Frame(self)
        
        w = ttk.Button(box, text="Сохранить", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Отмена", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        
        box.pack()
    
    def initial_focus_set(self):
        """Установка фокуса на первое поле ввода"""
        self.title_entry.focus_set()
    
    def body(self, master):
        """Создание тела диалогового окна"""
        # Установка фиксированного размера окна
        self.geometry("600x400")
        self.resizable(False, False)  # Запрет изменения размера
        
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
        
        # Добавляем поля для выбора даты и времени (с проверкой доступности DateEntry)
        if DateEntry is not None:
            # Используем календарь и поля ввода времени
            ttk.Label(master, text="Выполнить до:").grid(row=2, column=0, sticky=tk.W, pady=2)
            datetime_frame_due = ttk.Frame(master)
            datetime_frame_due.grid(row=2, column=1, pady=2, padx=(10, 0), sticky="ew")
            
            # Для даты выполнения
            ttk.Label(datetime_frame_due, text="Дата:").pack(anchor=tk.W)
            self.due_date_picker = DateEntry(datetime_frame_due, width=12, background='darkblue', foreground='white', borderwidth=2)
            self.due_date_picker.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(datetime_frame_due, text="Время (ЧЧ:ММ):").pack(anchor=tk.W)
            self.due_time_entry = ttk.Entry(datetime_frame_due, width=10)
            self.due_time_entry.pack(fill=tk.X)
            
            # Для напоминания
            ttk.Label(master, text="Напомнить:").grid(row=3, column=0, sticky=tk.W, pady=2)
            datetime_frame_reminder = ttk.Frame(master)
            datetime_frame_reminder.grid(row=3, column=1, pady=2, padx=(10, 0), sticky="ew")
            
            ttk.Label(datetime_frame_reminder, text="Дата:").pack(anchor=tk.W)
            self.reminder_date_picker = DateEntry(datetime_frame_reminder, width=12, background='darkblue', foreground='white', borderwidth=2)
            self.reminder_date_picker.pack(fill=tk.X, pady=(0, 5))
            
            ttk.Label(datetime_frame_reminder, text="Время (ЧЧ:ММ):").pack(anchor=tk.W)
            self.reminder_time_entry = ttk.Entry(datetime_frame_reminder, width=10)
            self.reminder_time_entry.pack(fill=tk.X)
        else:
            # Используем старый способ ввода даты вручную
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
            
            if DateEntry is not None:
                # Заполняем поля с календарем
                if self.task['due_date']:
                    # Парсим дату из строки в формат dd.mm.yyyy HH:MM
                    try:
                        dt = datetime.strptime(self.task['due_date'], '%d.%m.%Y %H:%M')
                        self.due_date_picker.set_date(dt.date())
                        self.due_time_entry.insert(0, dt.strftime('%H:%M'))
                    except ValueError:
                        try:
                            # Пробуем ISO формат
                            dt = datetime.fromisoformat(self.task['due_date'].replace('Z', '+00:00'))
                            self.due_date_picker.set_date(dt.date())
                            self.due_time_entry.insert(0, dt.strftime('%H:%M'))
                        except ValueError:
                            pass
                
                if self.task['reminder_time']:
                    try:
                        dt = datetime.strptime(self.task['reminder_time'], '%d.%m.%Y %H:%M')
                        self.reminder_date_picker.set_date(dt.date())
                        self.reminder_time_entry.insert(0, dt.strftime('%H:%M'))
                    except ValueError:
                        try:
                            # Пробуем ISO формат
                            dt = datetime.fromisoformat(self.task['reminder_time'].replace('Z', '+00:00'))
                            self.reminder_date_picker.set_date(dt.date())
                            self.reminder_time_entry.insert(0, dt.strftime('%H:%M'))
                        except ValueError:
                            pass
            else:
                # Заполняем старые поля ввода
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
            
        if DateEntry is not None:
            # Проверяем формат времени, если введены даты
            due_date_val = self.due_date_picker.get() if hasattr(self, 'due_date_picker') else ""
            due_time_val = self.due_time_entry.get().strip() if hasattr(self, 'due_time_entry') else ""
            reminder_date_val = self.reminder_date_picker.get() if hasattr(self, 'reminder_date_picker') else ""
            reminder_time_val = self.reminder_time_entry.get().strip() if hasattr(self, 'reminder_time_entry') else ""
            
            # Формируем полные даты
            due_datetime_str = f"{due_date_val} {due_time_val}" if due_date_val and due_time_val else ""
            reminder_datetime_str = f"{reminder_date_val} {reminder_time_val}" if reminder_date_val and reminder_time_val else ""
            
            if due_datetime_str:
                try:
                    datetime.strptime(due_datetime_str, '%m/%d/%Y %H:%M')
                except ValueError:
                    try:
                        # Пробуем другой формат даты
                        datetime.strptime(due_datetime_str, '%d.%m.%Y %H:%M')
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Неверный формат даты выполнения: {due_datetime_str}. Используйте формат дд.мм.гггг чч:мм")
                        return False
                        
            if reminder_datetime_str:
                try:
                    datetime.strptime(reminder_datetime_str, '%m/%d/%Y %H:%M')
                except ValueError:
                    try:
                        # Пробуем другой формат даты
                        datetime.strptime(reminder_datetime_str, '%d.%m.%Y %H:%M')
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Неверный формат времени напоминания: {reminder_datetime_str}. Используйте формат дд.мм.гггг чч:мм")
                        return False
        else:
            # Проверяем формат дат, если они введены (старый способ)
            due_date = self.due_entry.get().strip()
            reminder_time = self.reminder_entry.get().strip()
            
            if due_date:
                try:
                    datetime.strptime(due_date, '%d.%m.%Y %H:%M')
                except ValueError:
                    try:
                        # Пробуем ISO формат
                        datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Неверный формат даты выполнения: {due_date}. Используйте формат дд.мм.гггг чч:мм")
                        return False
                        
            if reminder_time:
                try:
                    datetime.strptime(reminder_time, '%d.%m.%Y %H:%M')
                except ValueError:
                    try:
                        # Пробуем ISO формат
                        datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Неверный формат времени напоминания: {reminder_time}. Используйте формат дд.мм.гггг чч:мм")
                        return False
        
        return True
    
    def apply(self):
        """Сохранение результатов"""
        # Получаем значения из полей
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        
        if DateEntry is not None:
            # Формируем даты из новых полей
            due_date_val = self.due_date_picker.get() if hasattr(self, 'due_date_picker') else ""
            due_time_val = self.due_time_entry.get().strip() if hasattr(self, 'due_time_entry') else ""
            reminder_date_val = self.reminder_date_picker.get() if hasattr(self, 'reminder_date_picker') else ""
            reminder_time_val = self.reminder_time_entry.get().strip() if hasattr(self, 'reminder_time_entry') else ""
            
            due_date = f"{due_date_val} {due_time_val}" if due_date_val and due_time_val else None
            reminder_time = f"{reminder_date_val} {reminder_time_val}" if reminder_date_val and reminder_time_val else None
        else:
            # Получаем значения из старых полей
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