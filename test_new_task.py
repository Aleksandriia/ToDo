#!/usr/bin/env python3
"""
Test script to simulate adding a new task with the user's parameters
to verify that the issue is fixed.
"""

import json
import uuid
from datetime import datetime

def simulate_task_creation():
    print("Simulating task creation with user's parameters...")
    print("Title: Test")
    print("Description: Test")
    print("Due date: 26.01.2026 23:00")
    print("Reminder time: 26.01.2026 22:45")
    
    # Load existing tasks
    with open('/workspace/todo_data.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    print(f"\nLoaded {len(tasks)} existing tasks")
    
    # Add new task with user's parameters
    new_task = {
        'id': str(uuid.uuid4()),  # Use UUID like the GUI app does
        'title': 'Test',
        'description': 'Test',
        'due_date': '26.01.2026 23:00',
        'reminder_time': '26.01.2026 22:45',
        'completed': False,
        'reminder_shown': False  # New field we added
    }
    
    tasks.append(new_task)
    
    print(f"Added new task. Now there are {len(tasks)} tasks")
    
    # Save updated tasks
    with open('/workspace/todo_data.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)
    
    print("Saved updated task list.")
    
    # Now simulate checking for reminders (as the GUI app would do)
    print("\nSimulating reminder check...")
    current_time = datetime.now()
    print(f"Current time: {current_time}")
    
    triggered_reminders = []
    
    for task in tasks:
        if task.get('reminder_time') and not task.get('completed', False):
            # Check if reminder was already shown
            if task.get('reminder_shown', False):
                continue  # Skip if already shown
            
            # Try to parse the reminder time
            reminder_dt = None
            try:
                # Try different formats
                reminder_dt = datetime.strptime(task['reminder_time'], '%d.%m.%Y %H:%M')
            except ValueError:
                try:
                    reminder_dt = datetime.fromisoformat(task['reminder_time'].replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            if reminder_dt and reminder_dt <= current_time:
                triggered_reminders.append(task)
                task['reminder_shown'] = True  # Mark that notification was shown
                print(f"Triggered reminder for task: {task['title']} (ID: {task['id']})")
    
    if triggered_reminders:
        # Save changes after processing reminders
        with open('/workspace/todo_data.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
        print(f"Updated {len(triggered_reminders)} tasks with reminder_shown=True and saved to file.")
    
    # Show final state
    print("\nFinal task list:")
    for i, task in enumerate(tasks):
        print(f"{i+1}. ID: {task['id']}, Title: {task['title']}, Completed: {task.get('completed', False)}, Reminder shown: {task.get('reminder_shown', False)}")

if __name__ == "__main__":
    # Backup original file first
    import shutil
    shutil.copy2('/workspace/todo_data.json', '/workspace/todo_data_test_backup.json')
    print("Created backup of original todo_data.json")
    
    simulate_task_creation()
    
    print("\nTest completed. Check the updated todo_data.json file.")