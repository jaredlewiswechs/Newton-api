#!/usr/bin/env python3
"""
Newton PDA - Level 5: Full Personal Digital Assistant
Complete PDA with contacts, tasks, notes, and calendar

Run: python examples/pda_level5.py
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime

# ============================================================
# CONTACT MANAGEMENT
# ============================================================

class Contact(Blueprint):
    """A person in your address book"""
    name = field(str, default="")
    phone = field(str, default="")
    email = field(str, default="")
    birthday = field(str, default="")  # YYYY-MM-DD
    notes = field(str, default="")
    category = field(str, default="personal")  # personal, work, family

    @law
    def must_have_name(self):
        when(self.name == "", finfr)

    @law
    def valid_category(self):
        valid = ["personal", "work", "family", "other"]
        when(self.category not in valid, finfr)

    @forge
    def update(self, **kwargs):
        """Update any fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return f"Updated {self.name}"


# ============================================================
# TASK MANAGEMENT
# ============================================================

class Task(Blueprint):
    """A todo item"""
    title = field(str, default="")
    due_date = field(str, default="")
    priority = field(int, default=3)
    completed = field(bool, default=False)
    tags = field(list, default=[])

    @law
    def must_have_title(self):
        when(self.title == "", finfr)

    @law
    def valid_priority(self):
        when(self.priority < 1 or self.priority > 3, finfr)

    @forge
    def complete(self):
        self.completed = True
        return f"Completed: {self.title}"

    @forge
    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
        return f"Tagged with: {tag}"


# ============================================================
# NOTES
# ============================================================

class Note(Blueprint):
    """A text note"""
    title = field(str, default="Untitled")
    content = field(str, default="")
    created = field(str, default="")
    modified = field(str, default="")
    pinned = field(bool, default=False)

    @law
    def not_empty(self):
        """Notes need some content"""
        when(self.title == "" and self.content == "", finfr)

    @forge
    def edit(self, new_content: str):
        self.content = new_content
        self.modified = datetime.now().isoformat()
        return "Note updated"

    @forge
    def pin(self):
        self.pinned = True
        return f"Pinned: {self.title}"


# ============================================================
# CALENDAR EVENT
# ============================================================

class Event(Blueprint):
    """A calendar event"""
    title = field(str, default="")
    date = field(str, default="")      # YYYY-MM-DD
    time = field(str, default="")      # HH:MM
    duration = field(int, default=60)  # minutes
    location = field(str, default="")
    reminder = field(int, default=15)  # minutes before

    @law
    def must_have_title(self):
        when(self.title == "", finfr)

    @law
    def must_have_date(self):
        when(self.date == "", finfr)

    @law
    def valid_duration(self):
        """Events must be 1 min to 24 hours"""
        when(self.duration < 1 or self.duration > 1440, finfr)

    @law
    def valid_reminder(self):
        """Reminder 0-1440 minutes (up to 1 day before)"""
        when(self.reminder < 0 or self.reminder > 1440, finfr)


# ============================================================
# THE PDA ITSELF
# ============================================================

class PDA(Blueprint):
    """Your Personal Digital Assistant"""
    owner = field(str, default="User")
    contacts = field(list, default=[])
    tasks = field(list, default=[])
    notes = field(list, default=[])
    events = field(list, default=[])

    # PDA-level constraints
    max_tasks = field(int, default=100)
    max_notes = field(int, default=500)

    @law
    def task_limit(self):
        """Don't let task list grow unbounded"""
        when(len(self.tasks) > self.max_tasks, finfr)

    @law
    def note_limit(self):
        """Don't let notes grow unbounded"""
        when(len(self.notes) > self.max_notes, finfr)

    # ---- Contact Methods ----

    @forge
    def add_contact(self, name: str, **kwargs):
        """Add a new contact"""
        contact = Contact()
        contact.name = name
        for key, value in kwargs.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        self.contacts.append(contact)
        return f"Added contact: {name}"

    @forge
    def find_contact(self, query: str):
        """Search contacts by name"""
        matches = [c for c in self.contacts
                   if query.lower() in c.name.lower()]
        return matches

    # ---- Task Methods ----

    @forge
    def add_task(self, title: str, priority: int = 3, due: str = ""):
        """Add a new task"""
        task = Task()
        task.title = title
        task.priority = priority
        task.due_date = due
        self.tasks.append(task)
        return f"Added task: {title}"

    @forge
    def pending_tasks(self):
        """Get incomplete tasks sorted by priority"""
        pending = [t for t in self.tasks if not t.completed]
        return sorted(pending, key=lambda t: t.priority)

    @forge
    def complete_task(self, title: str):
        """Mark a task as done by title"""
        for task in self.tasks:
            if task.title == title:
                task.complete()
                return f"Completed: {title}"
        return f"Task not found: {title}"

    # ---- Note Methods ----

    @forge
    def add_note(self, title: str, content: str = ""):
        """Create a new note"""
        note = Note()
        note.title = title
        note.content = content
        note.created = datetime.now().isoformat()
        note.modified = note.created
        self.notes.append(note)
        return f"Created note: {title}"

    @forge
    def pinned_notes(self):
        """Get all pinned notes"""
        return [n for n in self.notes if n.pinned]

    # ---- Event Methods ----

    @forge
    def add_event(self, title: str, date: str, time: str = "09:00",
                  duration: int = 60, location: str = ""):
        """Add a calendar event"""
        event = Event()
        event.title = title
        event.date = date
        event.time = time
        event.duration = duration
        event.location = location
        self.events.append(event)
        return f"Added event: {title} on {date}"

    @forge
    def events_on_date(self, date: str):
        """Get all events on a specific date"""
        return [e for e in self.events if e.date == date]

    # ---- Dashboard ----

    @forge
    def dashboard(self):
        """Get a quick status overview"""
        pending = len([t for t in self.tasks if not t.completed])
        urgent = len([t for t in self.tasks
                     if not t.completed and t.priority == 1])
        today = datetime.now().strftime("%Y-%m-%d")
        today_events = len(self.events_on_date(today))

        return {
            "contacts": len(self.contacts),
            "pending_tasks": pending,
            "urgent_tasks": urgent,
            "notes": len(self.notes),
            "today_events": today_events
        }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("NEWTON PDA - Full Demo")
    print("=" * 50)

    # Create your PDA
    pda = PDA()
    pda.owner = "Jared"
    print(f"\nWelcome, {pda.owner}!\n")

    # Add some contacts
    print("--- Adding Contacts ---")
    pda.add_contact("Mom", phone="555-1000", category="family")
    print("  Added: Mom (family)")
    pda.add_contact("Boss", phone="555-2000", email="boss@work.com", category="work")
    print("  Added: Boss (work)")
    pda.add_contact("Alex", phone="555-3000", category="personal")
    print("  Added: Alex (personal)")

    # Add some tasks
    print("\n--- Adding Tasks ---")
    pda.add_task("Review Newton docs", priority=1, due="2025-01-10")
    print("  Added: Review Newton docs [!] (due: 2025-01-10)")
    pda.add_task("Buy coffee", priority=3)
    print("  Added: Buy coffee [ ]")
    pda.add_task("Call Mom", priority=2, due="2025-01-08")
    print("  Added: Call Mom [-] (due: 2025-01-08)")

    # Add a note
    print("\n--- Adding Notes ---")
    pda.add_note("Newton Ideas", "The constraint IS the instruction!")
    print("  Added: Newton Ideas")

    # Add an event
    print("\n--- Adding Events ---")
    pda.add_event("Team Meeting", "2025-01-09", "10:00", duration=60, location="Zoom")
    print("  Added: Team Meeting (2025-01-09 at 10:00)")

    # Show dashboard
    print("\n" + "=" * 50)
    print("DASHBOARD")
    print("=" * 50)
    stats = pda.dashboard()
    print(f"  Contacts:      {stats['contacts']}")
    print(f"  Pending tasks: {stats['pending_tasks']} ({stats['urgent_tasks']} urgent)")
    print(f"  Notes:         {stats['notes']}")
    print(f"  Events today:  {stats['today_events']}")

    # Show pending tasks
    print("\n--- PENDING TASKS ---")
    for task in pda.pending_tasks():
        pri_label = {1: "[!]", 2: "[-]", 3: "[ ]"}[task.priority]
        due = f" (due: {task.due_date})" if task.due_date else ""
        print(f"  {pri_label} {task.title}{due}")

    # Complete a task
    print("\n--- COMPLETING A TASK ---")
    result = pda.complete_task("Buy coffee")
    print(f"  {result}")

    # Show updated tasks
    print("\n--- UPDATED TASKS ---")
    for task in pda.pending_tasks():
        pri_label = {1: "[!]", 2: "[-]", 3: "[ ]"}[task.priority]
        due = f" (due: {task.due_date})" if task.due_date else ""
        print(f"  {pri_label} {task.title}{due}")

    # Find a contact
    print("\n--- SEARCH: 'mom' ---")
    matches = pda.find_contact("mom")
    for c in matches:
        print(f"  Found: {c.name} ({c.phone}) [{c.category}]")

    # Show all contacts
    print("\n--- ALL CONTACTS ---")
    for c in pda.contacts:
        print(f"  {c.name}: {c.phone} [{c.category}]")

    print("\n" + "=" * 50)
    print("WHAT MAKES THIS SPECIAL")
    print("=" * 50)
    print("""
  Every action above was CONSTRAINT-VERIFIED:

  1. Contacts must have names (must_have_name law)
  2. Categories must be valid (valid_category law)
  3. Tasks must have titles (must_have_title law)
  4. Priorities must be 1-3 (valid_priority law)
  5. PDA can't exceed 100 tasks (task_limit law)
  6. PDA can't exceed 500 notes (note_limit law)
  7. Events must have dates (must_have_date law)
  8. Events duration 1-1440 min (valid_duration law)

  If ANY of these constraints would be violated,
  the operation is BLOCKED before it happens.

  No try/catch. No runtime errors. No invalid states.
  That's Newton.
""")
    print("=" * 50)
