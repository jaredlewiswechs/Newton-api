"""
Ada Tasks & Scheduling System
==============================

Schedule recurring tasks with verification.
Like ChatGPT Tasks but with reliability guarantees.
"""

import hashlib
import threading
import time
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import json
import os
import re

from .schema import (
    ScheduledTask,
    TaskFrequency,
    TaskResult,
    TaskStatus,
)


class CronParser:
    """
    Parses cron expressions for scheduling.

    Supports standard cron format: minute hour day month weekday
    """

    @staticmethod
    def parse(expression: str) -> Dict[str, List[int]]:
        """Parse a cron expression."""
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expression}")

        fields = ["minute", "hour", "day", "month", "weekday"]
        ranges = [
            (0, 59),   # minute
            (0, 23),   # hour
            (1, 31),   # day
            (1, 12),   # month
            (0, 6),    # weekday (0 = Sunday)
        ]

        result = {}
        for i, (field, part) in enumerate(zip(fields, parts)):
            min_val, max_val = ranges[i]
            result[field] = CronParser._parse_field(part, min_val, max_val)

        return result

    @staticmethod
    def _parse_field(field: str, min_val: int, max_val: int) -> List[int]:
        """Parse a single cron field."""
        if field == "*":
            return list(range(min_val, max_val + 1))

        if "/" in field:
            base, step = field.split("/")
            step = int(step)
            if base == "*":
                return list(range(min_val, max_val + 1, step))
            start = int(base)
            return list(range(start, max_val + 1, step))

        if "-" in field:
            start, end = map(int, field.split("-"))
            return list(range(start, end + 1))

        if "," in field:
            return [int(x) for x in field.split(",")]

        return [int(field)]

    @staticmethod
    def matches(parsed: Dict[str, List[int]], dt: datetime) -> bool:
        """Check if a datetime matches a parsed cron expression."""
        return (
            dt.minute in parsed["minute"] and
            dt.hour in parsed["hour"] and
            dt.day in parsed["day"] and
            dt.month in parsed["month"] and
            dt.weekday() in parsed["weekday"]
        )

    @staticmethod
    def next_run(parsed: Dict[str, List[int]], after: datetime) -> datetime:
        """Calculate the next run time after a given datetime."""
        # Start from the next minute
        candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Search for the next matching time (max 1 year)
        max_iterations = 365 * 24 * 60  # 1 year in minutes
        for _ in range(max_iterations):
            if CronParser.matches(parsed, candidate):
                return candidate
            candidate += timedelta(minutes=1)

        raise ValueError("Could not find next run time within 1 year")


class TaskRunner:
    """
    Executes scheduled tasks.

    Uses the Ada engine to process task prompts and
    returns verified results.
    """

    def __init__(self, engine: Any = None):
        self.engine = engine

    def run(self, task: ScheduledTask) -> TaskResult:
        """
        Run a scheduled task.

        Args:
            task: The task to run

        Returns:
            TaskResult with output
        """
        start_time = datetime.now()

        result = TaskResult(
            task_id=task.id,
            task_name=task.name,
            status=TaskStatus.RUNNING,
            output="",
            started_at=start_time,
        )

        try:
            # Execute the task prompt using the engine
            if self.engine:
                response = self.engine.generate(
                    prompt=task.prompt,
                    verify=True,
                )
                result.output = response.content
                result.status = TaskStatus.COMPLETED
            else:
                # Mock execution
                result.output = f"Executed task: {task.name}\nPrompt: {task.prompt}"
                result.status = TaskStatus.COMPLETED

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - start_time).total_seconds()

        return result


class TaskStore:
    """
    Persistent storage for scheduled tasks.
    """

    def __init__(self, storage_file: str = ".ada_tasks.json"):
        self.storage_file = storage_file
        self._tasks: Dict[str, ScheduledTask] = {}
        self._results: List[TaskResult] = []
        self._load()

    def add(self, task: ScheduledTask):
        """Add a task."""
        self._tasks[task.id] = task
        self._save()

    def get(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def remove(self, task_id: str) -> bool:
        """Remove a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save()
            return True
        return False

    def list_tasks(self) -> List[ScheduledTask]:
        """List all tasks."""
        return list(self._tasks.values())

    def update(self, task: ScheduledTask):
        """Update a task."""
        self._tasks[task.id] = task
        self._save()

    def add_result(self, result: TaskResult):
        """Store a task result."""
        self._results.append(result)
        # Keep only last 100 results
        self._results = self._results[-100:]
        self._save()

    def get_results(
        self,
        task_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[TaskResult]:
        """Get task results."""
        results = self._results
        if task_id:
            results = [r for r in results if r.task_id == task_id]
        return results[-limit:]

    def _save(self):
        """Save to disk."""
        data = {
            "tasks": [t.to_dict() for t in self._tasks.values()],
            "results": [r.to_dict() for r in self._results],
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Load from disk."""
        if not os.path.exists(self.storage_file):
            return

        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)

            for task_data in data.get("tasks", []):
                task = ScheduledTask(
                    id=task_data.get("id"),
                    name=task_data["name"],
                    description=task_data.get("description", ""),
                    prompt=task_data["prompt"],
                    frequency=TaskFrequency(task_data["frequency"]),
                    cron_expression=task_data.get("cron_expression"),
                    enabled=task_data.get("enabled", True),
                )
                if task_data.get("next_run"):
                    task.next_run = datetime.fromisoformat(task_data["next_run"])
                if task_data.get("last_run"):
                    task.last_run = datetime.fromisoformat(task_data["last_run"])
                self._tasks[task.id] = task

        except (json.JSONDecodeError, FileNotFoundError):
            pass


class TaskScheduler:
    """
    Schedules and manages recurring tasks.

    Features:
    - Cron-style scheduling
    - Simple frequency options
    - Persistent task storage
    - Notification support
    - Result history

    Why this is BETTER than ChatGPT Tasks:
    1. Full cron expression support
    2. Verified task outputs
    3. Complete history tracking
    4. Notification callbacks
    """

    def __init__(
        self,
        engine: Any = None,
        storage_file: str = ".ada_tasks.json",
        auto_start: bool = False,
    ):
        self.engine = engine
        self.runner = TaskRunner(engine)
        self.store = TaskStore(storage_file)

        # Notification callbacks
        self._on_complete: Optional[Callable[[TaskResult], None]] = None
        self._on_error: Optional[Callable[[TaskResult], None]] = None

        # Scheduler thread
        self._running = False
        self._thread: Optional[threading.Thread] = None

        if auto_start:
            self.start()

    def schedule(
        self,
        prompt: str,
        name: str,
        frequency: str = "daily",
        description: str = "",
        cron_expression: Optional[str] = None,
        notify_on_complete: bool = True,
        notify_email: Optional[str] = None,
    ) -> ScheduledTask:
        """
        Schedule a new task.

        Args:
            prompt: What Ada should do when the task runs
            name: Task name
            frequency: How often (once, hourly, daily, weekly, monthly, custom)
            description: Task description
            cron_expression: Custom cron expression (for frequency="custom")
            notify_on_complete: Whether to send notification
            notify_email: Email for notifications

        Returns:
            Created ScheduledTask

        Example:
            >>> scheduler.schedule(
            ...     "Summarize today's AI news",
            ...     name="Daily AI Summary",
            ...     frequency="daily"
            ... )
        """
        # Parse frequency
        freq = TaskFrequency(frequency.lower())

        # Generate cron expression if not custom
        if freq != TaskFrequency.CUSTOM:
            cron_expression = self._frequency_to_cron(freq)

        task = ScheduledTask(
            name=name,
            description=description or f"Scheduled task: {name}",
            prompt=prompt,
            frequency=freq,
            cron_expression=cron_expression,
            notify_on_complete=notify_on_complete,
            notify_email=notify_email,
        )

        # Calculate next run time
        if cron_expression:
            parsed = CronParser.parse(cron_expression)
            task.next_run = CronParser.next_run(parsed, datetime.now())

        self.store.add(task)
        return task

    def unschedule(self, task_id: str) -> bool:
        """
        Remove a scheduled task.

        Args:
            task_id: ID of task to remove

        Returns:
            True if removed, False if not found
        """
        return self.store.remove(task_id)

    def pause(self, task_id: str) -> bool:
        """Pause a task (disable without removing)."""
        task = self.store.get(task_id)
        if task:
            task.enabled = False
            self.store.update(task)
            return True
        return False

    def resume(self, task_id: str) -> bool:
        """Resume a paused task."""
        task = self.store.get(task_id)
        if task:
            task.enabled = True
            # Recalculate next run
            if task.cron_expression:
                parsed = CronParser.parse(task.cron_expression)
                task.next_run = CronParser.next_run(parsed, datetime.now())
            self.store.update(task)
            return True
        return False

    def run_now(self, task_id: str) -> TaskResult:
        """
        Run a task immediately.

        Args:
            task_id: ID of task to run

        Returns:
            TaskResult with output
        """
        task = self.store.get(task_id)
        if not task:
            return TaskResult(
                task_id=task_id,
                task_name="Unknown",
                status=TaskStatus.FAILED,
                output="",
                error="Task not found",
            )

        result = self.runner.run(task)
        self._handle_result(task, result)
        return result

    def list_tasks(
        self,
        enabled_only: bool = False,
    ) -> List[ScheduledTask]:
        """List scheduled tasks."""
        tasks = self.store.list_tasks()
        if enabled_only:
            tasks = [t for t in tasks if t.enabled]
        return tasks

    def get_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[TaskResult]:
        """Get task execution history."""
        return self.store.get_results(task_id, limit)

    def start(self):
        """Start the scheduler background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def on_complete(self, callback: Callable[[TaskResult], None]):
        """Set callback for task completion."""
        self._on_complete = callback

    def on_error(self, callback: Callable[[TaskResult], None]):
        """Set callback for task errors."""
        self._on_error = callback

    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._running:
            now = datetime.now()

            for task in self.store.list_tasks():
                if not task.enabled:
                    continue

                if task.next_run and now >= task.next_run:
                    # Run the task
                    result = self.runner.run(task)
                    self._handle_result(task, result)

                    # Calculate next run
                    if task.frequency != TaskFrequency.ONCE and task.cron_expression:
                        parsed = CronParser.parse(task.cron_expression)
                        task.next_run = CronParser.next_run(parsed, now)
                    else:
                        task.enabled = False  # Disable one-time tasks

                    task.last_run = now
                    task.run_count += 1
                    self.store.update(task)

            # Check every minute
            time.sleep(60)

    def _handle_result(self, task: ScheduledTask, result: TaskResult):
        """Handle a task result."""
        self.store.add_result(result)

        if result.status == TaskStatus.COMPLETED:
            if self._on_complete:
                self._on_complete(result)

            if task.notify_on_complete:
                self._send_notification(task, result)
        else:
            if self._on_error:
                self._on_error(result)

    def _send_notification(self, task: ScheduledTask, result: TaskResult):
        """Send notification for completed task."""
        # In production, send email or push notification
        # For now, just log
        pass

    def _frequency_to_cron(self, freq: TaskFrequency) -> str:
        """Convert frequency to cron expression."""
        expressions = {
            TaskFrequency.ONCE: "0 0 * * *",       # Midnight (will only run once)
            TaskFrequency.HOURLY: "0 * * * *",    # Every hour
            TaskFrequency.DAILY: "0 9 * * *",     # 9 AM daily
            TaskFrequency.WEEKLY: "0 9 * * 1",    # 9 AM Monday
            TaskFrequency.MONTHLY: "0 9 1 * *",   # 9 AM 1st of month
        }
        return expressions.get(freq, "0 0 * * *")

    def stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        tasks = self.store.list_tasks()
        results = self.store.get_results(limit=100)

        completed = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == TaskStatus.FAILED)

        return {
            "total_tasks": len(tasks),
            "enabled_tasks": sum(1 for t in tasks if t.enabled),
            "total_runs": len(results),
            "successful_runs": completed,
            "failed_runs": failed,
            "success_rate": f"{completed / len(results):.1%}" if results else "N/A",
            "scheduler_running": self._running,
        }
