from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Имя файла для хранения данных
DATA_FILE = 'todo_data.json'

def load_tasks():
    """Загрузка задач из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Сохранение задач в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    tasks = load_tasks()
    
    task = {
        'id': str(uuid.uuid4()),
        'title': request.form['title'],
        'description': request.form['description'],
        'due_date': request.form.get('due_date'),
        'reminder_time': request.form.get('reminder_time'),
        'completed': False
    }
    
    tasks.append(task)
    save_tasks(tasks)
    
    return redirect(url_for('index'))

@app.route('/edit/<task_id>', methods=['POST'])
def edit_task(task_id):
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = request.form['title']
            task['description'] = request.form['description']
            task['due_date'] = request.form.get('due_date')
            task['reminder_time'] = request.form.get('reminder_time')
            break
    
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/toggle/<task_id>')
def toggle_task(task_id):
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/api/tasks')
def api_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def api_task(task_id):
    tasks = load_tasks()
    
    if request.method == 'GET':
        task = next((t for t in tasks if t['id'] == task_id), None)
        return jsonify(task) if task else ('', 404)
    
    elif request.method == 'PUT':
        for task in tasks:
            if task['id'] == task_id:
                task.update(request.json)
                save_tasks(tasks)
                return jsonify(task)
        return ('', 404)
    
    elif request.method == 'DELETE':
        tasks = [t for t in tasks if t['id'] != task_id]
        save_tasks(tasks)
        return ('', 204)

if __name__ == '__main__':
    # Создаем папку templates, если она не существует
    os.makedirs('templates', exist_ok=True)
    
    # Создаем HTML-шаблон
    template_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ToDo List с Напоминаниями</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        
        h1 {
            color: #333;
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
        
        .form-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .tasks-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        button {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background: #0056b3;
        }
        
        .btn-edit {
            background: #28a745;
        }
        
        .btn-edit:hover {
            background: #1e7e34;
        }
        
        .btn-delete {
            background: #dc3545;
        }
        
        .btn-delete:hover {
            background: #c82333;
        }
        
        .btn-toggle {
            background: #ffc107;
            color: black;
        }
        
        .btn-toggle:hover {
            background: #e0a800;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .completed {
            text-decoration: line-through;
            color: #6c757d;
        }
        
        .task-actions {
            display: flex;
            gap: 5px;
        }
        
        .task-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .task-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .task-description {
            margin-bottom: 10px;
            color: #666;
        }
        
        .task-meta {
            font-size: 0.9em;
            color: #888;
        }
        
        .status-completed {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-pending {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <header>
        <h1>ToDo List с Напоминаниями</h1>
        <p>Управляйте своими задачами и напоминаниями</p>
    </header>
    
    <div class="container">
        <div class="form-container">
            <h2>Добавить новую задачу</h2>
            <form action="/add" method="post">
                <div class="form-group">
                    <label for="title">Название *</label>
                    <input type="text" id="title" name="title" required>
                </div>
                
                <div class="form-group">
                    <label for="description">Описание</label>
                    <textarea id="description" name="description"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="due_date">Выполнить до (дд.мм.гггг чч:мм)</label>
                    <input type="datetime-local" id="due_date" name="due_date">
                </div>
                
                <div class="form-group">
                    <label for="reminder_time">Напомнить (дд.мм.гггг чч:мм)</label>
                    <input type="datetime-local" id="reminder_time" name="reminder_time">
                </div>
                
                <button type="submit">Добавить задачу</button>
            </form>
        </div>
        
        <div class="tasks-container">
            <h2>Список задач</h2>
            
            {% if tasks %}
                <table>
                    <thead>
                        <tr>
                            <th>Статус</th>
                            <th>Название</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for task in tasks %}
                        <tr>
                            <td>
                                <span class="status-{{ 'completed' if task.completed else 'pending' }}">
                                    {{ 'Выполнена' if task.completed else 'Не выполнена' }}
                                </span>
                            </td>
                            <td>
                                <div class="{{ 'completed' if task.completed else '' }}">
                                    <strong>{{ task.title }}</strong><br>
                                    <small>{{ task.description[:100] }}{% if task.description|length > 100 %}...{% endif %}</small><br>
                                    {% if task.due_date %}<small>Срок: {{ task.due_date }}</small>{% endif %}
                                    {% if task.reminder_time %}<small>Напоминание: {{ task.reminder_time }}</small>{% endif %}
                                </div>
                            </td>
                            <td>
                                <div class="task-actions">
                                    <a href="/toggle/{{ task.id }}" class="btn btn-toggle">{{ 'Отменить' if task.completed else 'Выполнить' }}</a>
                                    <a href="#" onclick="fillEditForm('{{ task.id }}', '{{ task.title|e }}', '{{ task.description|e }}', '{{ task.due_date or '' }}', '{{ task.reminder_time or '' }}')" class="btn btn-edit">Изменить</a>
                                    <a href="/delete/{{ task.id }}" class="btn btn-delete">Удалить</a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>Список задач пуст. Добавьте первую задачу!</p>
            {% endif %}
        </div>
    </div>
    
    <!-- Форма редактирования (скрыта по умолчанию) -->
    <div class="container" id="edit-form" style="display:none;">
        <div class="form-container">
            <h2>Редактировать задачу</h2>
            <form id="edit-task-form" method="post">
                <input type="hidden" id="edit-id" name="id">
                <div class="form-group">
                    <label for="edit-title">Название *</label>
                    <input type="text" id="edit-title" name="title" required>
                </div>
                
                <div class="form-group">
                    <label for="edit-description">Описание</label>
                    <textarea id="edit-description" name="description"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="edit-due_date">Выполнить до (дд.мм.гггг чч:мм)</label>
                    <input type="datetime-local" id="edit-due_date" name="due_date">
                </div>
                
                <div class="form-group">
                    <label for="edit-reminder_time">Напомнить (дд.мм.гггг чч:мм)</label>
                    <input type="datetime-local" id="edit-reminder_time" name="reminder_time">
                </div>
                
                <button type="submit">Сохранить изменения</button>
                <button type="button" onclick="cancelEdit()">Отмена</button>
            </form>
        </div>
    </div>
    
    <script>
        function fillEditForm(id, title, description, dueDate, reminderTime) {
            document.getElementById('edit-id').value = id;
            document.getElementById('edit-title').value = title;
            document.getElementById('edit-description').value = description;
            document.getElementById('edit-due_date').value = dueDate.replace(' ', 'T');
            document.getElementById('edit-reminder_time').value = reminderTime.replace(' ', 'T');
            
            document.getElementById('edit-form').style.display = 'block';
            document.getElementById('edit-task-form').action = '/edit/' + id;
        }
        
        function cancelEdit() {
            document.getElementById('edit-form').style.display = 'none';
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    app.run(debug=True, host='0.0.0.0', port=5000)