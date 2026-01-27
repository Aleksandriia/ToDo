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


@app.route('/api/tasks/search')
def search_tasks():
    """API endpoint для поиска и фильтрации задач"""
    tasks = load_tasks()
    
    # Получаем параметры запроса
    search_query = request.args.get('q', '').lower()
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'default')
    
    # Фильтруем задачи по поисковому запросу
    if search_query:
        tasks = [task for task in tasks if search_query in task['title'].lower() or 
                 (task['description'] and search_query in task['description'].lower())]
    
    # Фильтруем по статусу
    if status_filter != 'all':
        if status_filter == 'completed':
            tasks = [task for task in tasks if task['completed']]
        elif status_filter == 'pending':
            tasks = [task for task in tasks if not task['completed']]
    
    # Сортируем задачи
    if sort_by == 'title':
        tasks = sorted(tasks, key=lambda x: x['title'].lower())
    elif sort_by == 'due_date':
        tasks = sorted(tasks, key=lambda x: (x['due_date'] or ''), reverse=True)
    elif sort_by == 'reminder_time':
        tasks = sorted(tasks, key=lambda x: (x['reminder_time'] or ''), reverse=True)
    elif sort_by == 'status':
        tasks = sorted(tasks, key=lambda x: x['completed'])  # False (not completed) будет первым
    
    return jsonify(tasks)


@app.route('/api/tasks/all')
def get_all_tasks():
    """API endpoint для получения всех задач без фильтрации"""
    tasks = load_tasks()
    return jsonify(tasks)

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

@app.route('/reminders')
def check_reminders():
    """Проверка напоминаний"""
    tasks = load_tasks()
    now = datetime.now()
    triggered_reminders = []
    
    for task in tasks:
        if task['reminder_time'] and not task['completed']:
            try:
                # Попробуем преобразовать дату из строки в datetime
                reminder_dt = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                if reminder_dt <= now and not task.get('reminder_triggered', False):
                    triggered_reminders.append(task)
                    task['reminder_triggered'] = True  # Отмечаем, что напоминание уже сработало
            except ValueError:
                try:
                    # Попробуем другой формат даты
                    reminder_dt = datetime.strptime(task['reminder_time'], '%d.%m.%Y %H:%M')
                    if reminder_dt <= now and not task.get('reminder_triggered', False):
                        triggered_reminders.append(task)
                        task['reminder_triggered'] = True  # Отмечаем, что напоминание уже сработало
                except ValueError:
                    pass
    
    if triggered_reminders:
        save_tasks(tasks)  # Сохраняем изменения, чтобы зафиксировать срабатывание напоминаний
    
    return jsonify({
        'reminders': triggered_reminders,
        'count': len(triggered_reminders)
    })

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
    
    app.run(debug=True, host='0.0.0.0', port=5000)