#!/usr/bin/env python3
"""
Newton PDA - Level 4: Task Management
More complex constraints with interconnected rules

Run: python examples/pda_level4.py
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime

class Task(Blueprint):
    """A task with deadline constraints"""
    title = field(str, default="")
    due_date = field(str, default="")  # ISO format: "2025-01-15"
    priority = field(int, default=3)    # 1=high, 2=medium, 3=low
    completed = field(bool, default=False)

    @law
    def must_have_title(self):
        """Tasks need titles"""
        when(self.title == "", finfr)

    @law
    def valid_priority(self):
        """Priority must be 1, 2, or 3"""
        when(self.priority < 1 or self.priority > 3, finfr)

    @forge
    def set_priority(self, level: int):
        """Set priority 1-3"""
        self.priority = level
        labels = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}
        return f"Priority set to {labels.get(level, level)}"

    @forge
    def mark_done(self):
        """Complete the task"""
        self.completed = True
        return f"Task '{self.title}' completed!"

    @forge
    def set_due(self, date_str: str):
        """Set due date (YYYY-MM-DD format)"""
        self.due_date = date_str
        return f"Due date set to {date_str}"


class TaskList(Blueprint):
    """A list of tasks with aggregate constraints"""
    name = field(str, default="My Tasks")
    max_high_priority = field(int, default=5)  # Can't have too many urgent tasks
    tasks = field(list, default=[])

    @law
    def not_too_many_urgent(self):
        """Prevent priority overload - max 5 high-priority tasks"""
        high_count = sum(1 for t in self.tasks if t.priority == 1 and not t.completed)
        when(high_count > self.max_high_priority, finfr)

    @forge
    def add_task(self, task: Task):
        """Add a task to the list"""
        self.tasks.append(task)
        return f"Added: {task.title}"

    @forge
    def get_pending(self):
        """Get all incomplete tasks"""
        pending = [t for t in self.tasks if not t.completed]
        return pending

    @forge
    def get_by_priority(self, priority: int):
        """Get tasks by priority level"""
        return [t for t in self.tasks if t.priority == priority and not t.completed]


if __name__ == "__main__":
    print("=== Level 4: Task Management ===\n")

    # Create the task list
    my_list = TaskList()
    print(f"Created: {my_list.name}")
    print(f"Max high-priority tasks allowed: {my_list.max_high_priority}\n")

    # Create some tasks
    print("--- Adding Tasks ---")

    task1 = Task()
    task1.title = "Buy groceries"
    task1.set_due("2025-01-10")
    task1.set_priority(2)
    my_list.add_task(task1)
    print(f"Added: {task1.title} (priority: {task1.priority})")

    task2 = Task()
    task2.title = "Call mom"
    task2.set_due("2025-01-08")
    task2.set_priority(1)
    my_list.add_task(task2)
    print(f"Added: {task2.title} (priority: {task2.priority})")

    task3 = Task()
    task3.title = "Review Newton docs"
    task3.set_due("2025-01-09")
    task3.set_priority(1)
    my_list.add_task(task3)
    print(f"Added: {task3.title} (priority: {task3.priority})")

    task4 = Task()
    task4.title = "Walk the dog"
    task4.set_priority(3)
    my_list.add_task(task4)
    print(f"Added: {task4.title} (priority: {task4.priority})")

    # Display tasks
    print(f"\n--- All Tasks ({len(my_list.tasks)}) ---")
    for task in my_list.tasks:
        status = "[DONE]" if task.completed else "[    ]"
        pri = {1: "!", 2: "-", 3: " "}[task.priority]
        due = f" (due: {task.due_date})" if task.due_date else ""
        print(f"  {status} [{pri}] {task.title}{due}")

    # Show high priority tasks
    print("\n--- High Priority Tasks ---")
    high_pri = my_list.get_by_priority(1)
    print(f"Currently have {len(high_pri)} high-priority tasks (max: {my_list.max_high_priority})")
    for task in high_pri:
        print(f"  [!] {task.title}")

    # Complete a task
    print("\n--- Completing a Task ---")
    result = task2.mark_done()
    print(result)

    # Show updated list
    print("\n--- Updated Tasks ---")
    for task in my_list.tasks:
        status = "[DONE]" if task.completed else "[    ]"
        pri = {1: "!", 2: "-", 3: " "}[task.priority]
        print(f"  {status} [{pri}] {task.title}")

    print("\n--- Aggregate Constraints ---")
    print("The TaskList has a law: not_too_many_urgent")
    print("If you try to add more than 5 high-priority tasks,")
    print("the add_task forge would be BLOCKED!")
