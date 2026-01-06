# Newton API Intro Course
## Building a PDA (Personal Digital Assistant) App

**For people who know some code but find Newton "different"**

---

## Why Newton Feels Different

You're right - Newton IS different. Here's the key insight:

| Regular Code | Newton Code |
|--------------|-------------|
| "Do this, then that, then check if it worked" | "Define what's NOT allowed, then do stuff" |
| Errors happen at runtime | Invalid states can't exist |
| You catch problems | Newton prevents problems |

**Think of it like this:**
- Regular code = "Try to walk through the minefield carefully"
- Newton code = "Remove all the mines first, then walk wherever"

---

## Course Overview

We'll build a PDA app step by step:

1. **Level 1**: Basic Contact (your first Blueprint)
2. **Level 2**: Adding Laws (what can't happen)
3. **Level 3**: Adding Forges (guarded actions)
4. **Level 4**: Task Management with constraints
5. **Level 5**: Full PDA with calendar, notes, and sync

Each level builds on the last. Let's go!

---

# Level 1: Your First Blueprint (A Contact)

## What's a Blueprint?

A Blueprint is like a class, but with built-in safety rails. It holds data that Newton protects.

```python
# File: pda_level1.py
from tinytalk_py import Blueprint, field

class Contact(Blueprint):
    """A contact in your PDA"""
    name = field(str, default="")
    phone = field(str, default="")
    email = field(str, default="")

# Create a contact
friend = Contact()
friend.name = "Alex"
friend.phone = "555-1234"
friend.email = "alex@email.com"

print(f"Contact: {friend.name}, {friend.phone}")
```

**What just happened?**
- `Blueprint` = Newton's safe container for data
- `field` = A slot that holds typed data
- We created a contact and set its values

**Try it yourself:**
1. Create the file
2. Run it: `python pda_level1.py`
3. Add more fields like `birthday` or `address`

---

# Level 2: Adding Laws (The Magic Part)

## What's a Law?

A Law defines what CANNOT happen. This is where Newton gets interesting.

```python
# File: pda_level2.py
from tinytalk_py import Blueprint, field, law, when, finfr

class Contact(Blueprint):
    """A contact with rules"""
    name = field(str, default="")
    phone = field(str, default="")
    email = field(str, default="")

    @law
    def must_have_name(self):
        """Every contact needs a name - can't be empty"""
        when(self.name == "", finfr)

    @law
    def valid_phone_format(self):
        """Phone must have at least 7 characters"""
        when(len(self.phone) > 0 and len(self.phone) < 7, finfr)

# This works fine
friend = Contact()
friend.name = "Alex"
friend.phone = "555-1234"
print(f"Created: {friend.name}")

# This would be BLOCKED by the law:
# bad_contact = Contact()
# bad_contact.name = ""  # BLOCKED! must_have_name prevents this
# bad_contact.phone = "123"  # BLOCKED! too short
```

**The key words:**
- `@law` = Decorator that marks a constraint rule
- `when(condition, finfr)` = "When this condition is true, BLOCK it"
- `finfr` = "finality" - this state cannot exist

**Why this matters:**
In regular code, you'd write `if name == "": raise Error`. But that checks AFTER you try.
Newton prevents the invalid state from ever happening.

---

# Level 3: Adding Forges (Guarded Actions)

## What's a Forge?

A Forge is an action that automatically checks all Laws before running.

```python
# File: pda_level3.py
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Contact(Blueprint):
    """A contact with guarded actions"""
    name = field(str, default="Unknown")
    phone = field(str, default="")
    email = field(str, default="")
    notes = field(str, default="")
    favorite = field(bool, default=False)

    @law
    def must_have_name(self):
        when(self.name == "", finfr)

    @law
    def valid_phone_format(self):
        when(len(self.phone) > 0 and len(self.phone) < 7, finfr)

    @forge
    def update_phone(self, new_phone: str):
        """Change the phone number - Laws are auto-checked!"""
        self.phone = new_phone
        return f"Updated phone to {new_phone}"

    @forge
    def add_note(self, note: str):
        """Add a note about this contact"""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note
        return f"Note added"

    @forge
    def toggle_favorite(self):
        """Mark or unmark as favorite"""
        self.favorite = not self.favorite
        return f"Favorite: {self.favorite}"

# Usage
contact = Contact()
contact.name = "Sam"

# These work - Laws pass
contact.update_phone("555-7890")
contact.add_note("Met at coffee shop")
contact.toggle_favorite()

print(f"{contact.name}: {contact.phone}")
print(f"Favorite: {contact.favorite}")
print(f"Notes: {contact.notes}")

# This would be BLOCKED:
# contact.update_phone("123")  # Too short! Law blocks it
```

**What's happening:**
- `@forge` = A method that's guarded by all `@law` rules
- Before the forge runs, Newton checks every law
- If any law would be violated, the forge is BLOCKED
- You don't write try/catch - Newton handles it

---

# Level 4: Task Management

Now let's add tasks to our PDA. This shows more complex constraints.

```python
# File: pda_level4.py
from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime, timedelta

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

    @law
    def no_complete_without_date(self):
        """Can't mark complete if no due date was set"""
        when(self.completed and self.due_date == "", finfr)

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
        """Prevent priority overload"""
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


# Usage
my_list = TaskList()

# Create some tasks
task1 = Task()
task1.title = "Buy groceries"
task1.set_due("2025-01-10")
task1.set_priority(2)

task2 = Task()
task2.title = "Call mom"
task2.set_due("2025-01-08")
task2.set_priority(1)

# Add to list
my_list.add_task(task1)
my_list.add_task(task2)

print(f"Task list: {my_list.name}")
for task in my_list.tasks:
    status = "[DONE]" if task.completed else "[    ]"
    pri = {1: "!", 2: "-", 3: " "}[task.priority]
    print(f"  {status} [{pri}] {task.title} (due: {task.due_date})")

# Complete a task
task1.mark_done()
print(f"\nAfter completing '{task1.title}':")
for task in my_list.tasks:
    status = "[DONE]" if task.completed else "[    ]"
    print(f"  {status} {task.title}")
```

**New concepts:**
- Tasks have interconnected laws (can't complete without due date)
- TaskList has *aggregate* constraints (max urgent tasks)
- Laws can look at related data

---

# Level 5: Full PDA System

Now let's put it all together into a real PDA.

```python
# File: pda_level5.py
"""
Newton PDA - A Personal Digital Assistant
Built with constraint-first design
"""

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
    print("NEWTON PDA - Demo")
    print("=" * 50)

    # Create your PDA
    pda = PDA()
    pda.owner = "Jared"

    # Add some contacts
    pda.add_contact("Mom", phone="555-1000", category="family")
    pda.add_contact("Boss", phone="555-2000", email="boss@work.com", category="work")
    pda.add_contact("Alex", phone="555-3000", category="personal")

    # Add some tasks
    pda.add_task("Review Newton docs", priority=1, due="2025-01-10")
    pda.add_task("Buy coffee", priority=3)
    pda.add_task("Call Mom", priority=2, due="2025-01-08")

    # Add a note
    pda.add_note("Newton Ideas", "The constraint IS the instruction!")

    # Add an event
    pda.add_event("Team Meeting", "2025-01-09", "10:00", duration=60, location="Zoom")

    # Show dashboard
    print("\n--- DASHBOARD ---")
    stats = pda.dashboard()
    print(f"Contacts: {stats['contacts']}")
    print(f"Pending tasks: {stats['pending_tasks']} ({stats['urgent_tasks']} urgent)")
    print(f"Notes: {stats['notes']}")
    print(f"Events today: {stats['today_events']}")

    # Show pending tasks
    print("\n--- PENDING TASKS ---")
    for task in pda.pending_tasks():
        pri_label = {1: "[!]", 2: "[-]", 3: "[ ]"}[task.priority]
        due = f" (due: {task.due_date})" if task.due_date else ""
        print(f"  {pri_label} {task.title}{due}")

    # Complete a task
    print("\n--- COMPLETING A TASK ---")
    result = pda.complete_task("Buy coffee")
    print(result)

    # Show updated tasks
    print("\n--- UPDATED TASKS ---")
    for task in pda.pending_tasks():
        pri_label = {1: "[!]", 2: "[-]", 3: "[ ]"}[task.priority]
        print(f"  {pri_label} {task.title}")

    # Find a contact
    print("\n--- SEARCH CONTACTS ---")
    matches = pda.find_contact("mom")
    for c in matches:
        print(f"  Found: {c.name} ({c.phone})")

    print("\n" + "=" * 50)
    print("That's Newton PDA!")
    print("Every action above was constraint-verified.")
    print("=" * 50)
```

---

# Key Takeaways

## The Three Things That Make Newton Different

### 1. Laws Define the Impossible
```python
@law
def must_have_name(self):
    when(self.name == "", finfr)  # Empty names CAN'T EXIST
```
You don't catch errors. You prevent them from being possible.

### 2. Forges Are Guarded Actions
```python
@forge
def add_contact(self, name: str):
    # All laws are checked BEFORE this runs
    # If any law would fail, this never executes
    self.contacts.append(...)
```
No try/catch needed. Invalid operations are blocked.

### 3. Constraints Are Composable
```python
class PDA(Blueprint):
    @law
    def task_limit(self):
        when(len(self.tasks) > 100, finfr)
```
System-level constraints protect the whole app.

---

## Quick Reference

| Concept | What It Does | Example |
|---------|--------------|---------|
| `Blueprint` | Safe data container | `class Contact(Blueprint):` |
| `field` | Typed data slot | `name = field(str, default="")` |
| `@law` | Define impossibility | `when(bad_thing, finfr)` |
| `@forge` | Guarded action | `def save(self): ...` |
| `when(x, finfr)` | "If X, block it" | `when(self.age < 0, finfr)` |
| `finfr` | Finality - can't exist | Sentinel value |

---

## Running the Examples

```bash
# Level 1 - Basic contact
python pda_level1.py

# Level 2 - With laws
python pda_level2.py

# Level 3 - With forges
python pda_level3.py

# Level 4 - Task management
python pda_level4.py

# Level 5 - Full PDA
python pda_level5.py
```

---

## What's Next?

After this course, explore:

1. **Reversible Shell** - Undo any operation perfectly
2. **Ledger** - Every action is cryptographically logged
3. **Policy Engine** - Add approval workflows
4. **Cartridges** - Generate verified media

See: `GETTING_STARTED.md` for more learning paths.

---

## Your Hardware Setup

**Old Computer + LaCie SSD + Ethernet = Perfect for Newton!**

Newton runs with:
- 2.31ms median latency
- 46.5 microsecond internal processing
- No GPU required
- Minimal RAM needs

You could run Newton as a local service and access it from any device on your apartment network!

```bash
# Start Newton server
python newton_supercomputer.py

# It runs at http://your-computer-ip:8000
# Access from phone, tablet, other computers
```

---

*Course created for the Newton API project*
*"The constraint IS the instruction. The verification IS the computation."*
