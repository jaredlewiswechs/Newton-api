# TinyTalk Programming Guide

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

<p align="center">
  <img src="https://img.shields.io/badge/tinyTalk-1.0-blue.svg" alt="TinyTalk 1.0">
  <img src="https://img.shields.io/badge/Newton-Supercomputer-green.svg" alt="Newton">
  <img src="https://img.shields.io/badge/Philosophy-No--First-orange.svg" alt="No-First">
</p>

<p align="center">
  <strong>The Complete Guide to Constraint-First Programming</strong><br>
  <em>Smalltalk is back. But this time, with boundaries.</em>
</p>

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Your First Program](#your-first-program)
4. [Core Concepts](#core-concepts)
5. [The Five Sacred Words](#the-five-sacred-words)
6. [Blueprints](#blueprints)
7. [Fields](#fields)
8. [Laws](#laws)
9. [Forges](#forges)
10. [Matter Types](#matter-types)
11. [The Kinetic Engine](#the-kinetic-engine)
12. [Ratio Constraints (f/g)](#ratio-constraints-fg)
13. [Reversible Shell](#reversible-shell)
14. [Basic Examples](#basic-examples)
14. [Intermediate Examples](#intermediate-examples)
15. [Advanced Examples](#advanced-examples)
16. [Real-World Applications](#real-world-applications)
17. [Testing TinyTalk Programs](#testing-tinytalk-programs)
18. [Performance Optimization](#performance-optimization)
19. [Extending TinyTalk](#extending-tinytalk)
20. [API Reference](#api-reference)
21. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is TinyTalk?

TinyTalk is a **constraint-first programming language** inspired by Smalltalk, designed for the Newton Supercomputer. Unlike traditional programming languages that explore every possible branch until finding an error ("Yes-First"), TinyTalk defines what **cannot** happen before execution ("No-First").

```
Traditional: "What can I do?" → Try everything → Catch errors
TinyTalk:    "What cannot happen?" → Define boundaries → Execute safely
```

### The Philosophy

**The constraint IS the instruction. The verification IS the computation.**

When you write TinyTalk, you're not writing scripts—you're defining the **physics of your world**. If a state violates your laws, it cannot exist. Period.

```python
def newton(current, goal):
    return current == goal

# 1 == 1 → execute
# 1 != 1 → halt
```

### Why TinyTalk?

| Problem | Traditional Solution | TinyTalk Solution |
|---------|---------------------|-------------------|
| Overdraft | Check balance, throw exception | Balance < 0 cannot exist |
| Collision | Detect collision, handle crash | Two objects same space forbidden |
| Overflow | Try/catch, hope for the best | Bounds defined, violation impossible |
| Race condition | Locks, mutexes, prayers | Conflicting states cannot coexist |

---

## Installation

### Quick Install (Recommended)

```bash
# Clone the Newton repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install dependencies
pip install -e .

# Verify installation
newton demo
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install requirements
pip install -r requirements.txt

# Add to Python path (add to ~/.bashrc or ~/.zshrc)
export PYTHONPATH="${PYTHONPATH}:/path/to/Newton-api"
```

### Verify Installation

```python
# test_install.py
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Test(Blueprint):
    value = field(int, default=0)

    @law
    def must_be_positive(self):
        when(self.value < 0, finfr)

    @forge
    def set_value(self, v):
        self.value = v

t = Test()
t.set_value(10)
print(f"Success! Value = {t.value}")
```

```bash
python test_install.py
# Output: Success! Value = 10
```

### Available Languages

TinyTalk is available in three languages:

| Language | Location | Import |
|----------|----------|--------|
| **Python** | `tinytalk_py/` | `from tinytalk_py import *` |
| **Ruby** | `tinytalk/ruby/` | `require_relative 'tinytalk'` |
| **R** | `tinytalk/r/` | `source("tinytalk.R")` |

---

## Your First Program

Let's build a simple bank account that **cannot** go negative:

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class BankAccount(Blueprint):
    """A bank account that cannot overdraft."""

    # State (Layer 1: Executive)
    balance = field(float, default=100.0)

    # Law (Layer 0: Governance)
    @law
    def no_overdraft(self):
        """Balance cannot be negative."""
        when(self.balance < 0, finfr)

    # Action (Layer 1: Executive)
    @forge
    def withdraw(self, amount):
        """Withdraw money from account."""
        self.balance -= amount
        return f"Withdrew ${amount}. Balance: ${self.balance}"

# Create account
account = BankAccount()
print(f"Starting balance: ${account.balance}")

# Valid withdrawal
result = account.withdraw(30)
print(result)  # "Withdrew $30. Balance: $70.0"

# Try to overdraft
try:
    account.withdraw(100)  # Would make balance -$30
except Exception as e:
    print(f"BLOCKED: {e}")
    print(f"Balance unchanged: ${account.balance}")  # Still $70
```

**Output:**
```
Starting balance: $100.0
Withdrew $30. Balance: $70.0
BLOCKED: Law 'no_overdraft' prevents this state (finfr)
Balance unchanged: $70.0
```

**What happened?**
1. The law `no_overdraft` defines that `balance < 0` triggers `finfr`
2. Before `withdraw(100)` executes, Newton projects the result
3. Projected balance would be -$30, violating the law
4. The forge never runs, state rolls back
5. Account stays at $70

This is **pre-execution verification**. The invalid state never exists.

---

## Core Concepts

### The Three-Layer Architecture

TinyTalk organizes code into three layers to prevent emergent behavior:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: APPLICATION                                        │
│  Your specific solution (BankAccount, Thermostat, Game)     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: EXECUTIVE (newtonScript)                          │
│  field() = State                                             │
│  forge() = Actions that mutate state                         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 0: GOVERNANCE (tinyTalk)                              │
│  law() = Physics/Constraints                                 │
│  finfr = Forbidden states (ontological death)                │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Name | Purpose | Cannot |
|-------|------|---------|--------|
| **L0** | Governance | Define impossible states | Execute code |
| **L1** | Executive | Define state and actions | Violate L0 |
| **L2** | Application | Combine into solutions | Exist outside bounds |

### The Blueprint Pattern

Everything in TinyTalk is a **Blueprint**—a template that defines:
- **Fields**: The state (what exists)
- **Laws**: The constraints (what cannot happen)
- **Forges**: The actions (what can change)

```python
class MyBlueprint(Blueprint):
    # Fields = State
    name = field(str, default="")
    value = field(int, default=0)

    # Laws = Constraints
    @law
    def my_constraint(self):
        when(self.value < 0, finfr)

    # Forges = Actions
    @forge
    def my_action(self, x):
        self.value = x
        return "done"
```

---

## The Five Sacred Words

TinyTalk has a frozen lexicon of five keywords. This prevents semantic drift.

### 1. `when` — Declares a Fact

`when` acknowledges what IS, not what might be. It doesn't ask "if"—it states "this is true."

```python
when(balance < 0, finfr)      # "When balance is negative, forbid"
when(temperature > 100, fin)   # "When temp exceeds 100, close"
when(is_valid)                 # Returns True/False
```

### 2. `and` — Combines Facts

`and` joins multiple conditions into a complex shape:

```python
@law
def collision_prevention(self):
    when(self.car_a_moving and self.car_b_moving, finfr)
```

### 3. `fin` — Closure (Can Reopen)

`fin` signals a stopping point that may be reopened later. It's a soft boundary.

```python
when(self.session_expired, fin)  # Session closed, can renew
```

### 4. `finfr` — Finality (Ontological Death)

`finfr` (pronounced "fin-fur") means the state is **forbidden forever**. If triggered, the operation cannot proceed.

```python
when(self.balance < 0, finfr)  # Negative balance cannot exist
```

### 5. `ratio` — Dimensional Analysis (f/g)

`ratio` defines constraints as ratios between two values:

```python
when(ratio(self.debt, self.equity) > 3.0, finfr)  # Max 3:1 leverage
```

---

## Blueprints

### Creating a Blueprint

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Counter(Blueprint):
    """A simple counter with bounds."""

    count = field(int, default=0)
    max_value = field(int, default=100)

    @law
    def within_bounds(self):
        when(self.count < 0 or self.count > self.max_value, finfr)

    @forge
    def increment(self):
        self.count += 1
        return self.count

    @forge
    def decrement(self):
        self.count -= 1
        return self.count
```

### Instantiating Blueprints

```python
# Default values
counter = Counter()
print(counter.count)  # 0

# Custom initial values
counter = Counter(count=50, max_value=200)
print(counter.count)  # 50
```

### Blueprint State

```python
# Get current state
state = counter._get_state()
print(state)  # {'count': 50, 'max_value': 200}

# String representation
print(counter)  # Counter(count=50, max_value=200)
```

---

## Fields

Fields define the **state** of a Blueprint. They are typed and have defaults.

### Basic Field Declaration

```python
class Person(Blueprint):
    name = field(str, default="Unknown")
    age = field(int, default=0)
    balance = field(float, default=0.0)
    active = field(bool, default=True)
```

### Field Types

| Type | Example | Notes |
|------|---------|-------|
| `int` | `field(int, default=0)` | Integers |
| `float` | `field(float, default=0.0)` | Decimals |
| `str` | `field(str, default="")` | Strings |
| `bool` | `field(bool, default=False)` | Booleans |
| `list` | `field(list, default=None)` | Lists (use None default) |
| `dict` | `field(dict, default=None)` | Dictionaries |
| `Money` | `field(Money, default=Money(0))` | Matter types |

### Type Safety

Fields enforce type checking:

```python
class Typed(Blueprint):
    count = field(int, default=0)

t = Typed()
t.count = 42       # OK
t.count = "100"    # Converts to int(100)
t.count = "hello"  # Raises TypeError
```

### Complex Fields

```python
class Container(Blueprint):
    items = field(list, default=None)
    metadata = field(dict, default=None)

    @forge
    def add_item(self, item):
        if self.items is None:
            self.items = []
        self.items.append(item)
```

---

## Laws

Laws define what **cannot** happen. They are evaluated before every forge execution.

### Basic Law

```python
@law
def must_be_positive(self):
    """Value must be positive."""
    when(self.value < 0, finfr)
```

### Multiple Conditions

```python
@law
def valid_range(self):
    """Value must be between 0 and 100."""
    when(self.value < 0 or self.value > 100, finfr)
```

### Multiple Laws

A Blueprint can have many laws. All are checked:

```python
class StrictAccount(Blueprint):
    balance = field(float, default=1000.0)
    daily_withdrawn = field(float, default=0.0)

    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)

    @law
    def daily_limit(self):
        when(self.daily_withdrawn > 500, finfr)

    @law
    def minimum_balance(self):
        when(self.balance < 100, finfr)
```

### Law with `fin` (Soft Closure)

```python
from tinytalk_py import fin, FinClosure

@law
def soft_limit(self):
    when(self.value >= 90, fin)  # Warning, not death

# Catch soft closure
try:
    obj.set_value(95)
except FinClosure:
    print("Approaching limit!")
```

### Law Evaluation Order

1. Forge is called
2. State changes are made (tentatively)
3. All laws are evaluated against new state
4. If any law triggers `finfr` → rollback, raise `LawViolation`
5. If any law triggers `fin` → rollback, raise `FinClosure`
6. If all laws pass → commit state change

---

## Forges

Forges are **actions** that mutate state. They are the only way to change a Blueprint.

### Basic Forge

```python
@forge
def set_value(self, new_value):
    self.value = new_value
    return "Value updated"
```

### Forge with Validation

Laws automatically validate, but you can add logic:

```python
@forge
def transfer(self, to_account, amount):
    if amount <= 0:
        return "Invalid amount"

    self.balance -= amount
    to_account.balance += amount
    return f"Transferred ${amount}"
```

### Return Values

Forges can return any value:

```python
@forge
def get_and_increment(self):
    old_value = self.count
    self.count += 1
    return old_value  # Returns value before increment
```

### Automatic Rollback

If a law is violated or an error occurs, state rolls back:

```python
class Safe(Blueprint):
    a = field(int, default=10)
    b = field(int, default=20)

    @law
    def sum_limit(self):
        when(self.a + self.b > 50, finfr)

    @forge
    def update_both(self, da, db):
        self.a += da  # Changed
        self.b += db  # Changed
        # If law violated here, BOTH changes roll back

safe = Safe()
try:
    safe.update_both(20, 20)  # Would make sum 60
except LawViolation:
    print(safe.a, safe.b)  # Still 10, 20
```

---

## Matter Types

Matter types provide **type-safe values with units**. They prevent unit confusion bugs like the Mars Climate Orbiter disaster.

### Available Matter Types

```python
from tinytalk_py import (
    Money,           # Currency
    Mass,            # Weight (kg)
    Distance,        # Length (m)
    Temperature,     # Heat (C, F, K)
    Pressure,        # Force/area (PSI)
    FlowRate,        # Volume/time (L/min)
    Velocity,        # Distance/time (m/s)
    Time,            # Duration (s)
    Volume,          # Space (L)
)
```

### Using Matter Types

```python
from tinytalk_py import Money, Celsius, PSI

# Create values
price = Money(100, "USD")
temp = Celsius(25)
pressure = PSI(14.7)

# Arithmetic (same types only)
total = Money(100) + Money(50)   # Money(150)
hot = Celsius(100) - Celsius(20)  # Celsius(80)

# Scalar multiplication
double = Money(100) * 2           # Money(200)
half = Money(100) / 2             # Money(50)

# Comparisons
Money(100) > Money(50)            # True
Celsius(100) >= Celsius(100)      # True
```

### Type Safety

Different Matter types cannot mix:

```python
money = Money(100)
mass = Mass(50)

money + mass      # TypeError!
money > mass      # TypeError!
money + 50        # TypeError! (use Money(50))
```

### Temperature Conversions

```python
from tinytalk_py import Celsius, Fahrenheit

c = Celsius(100)
f = c.to_fahrenheit()  # Temperature(212, "F")
k = c.to_kelvin()      # Temperature(373.15, "K")

# Comparisons work across units
Celsius(100) == Fahrenheit(212)  # True (same temperature)
```

### Matter in Blueprints

```python
class Wallet(Blueprint):
    balance = field(Money, default=Money(0))

    @law
    def no_debt(self):
        when(self.balance.value < 0, finfr)

    @forge
    def deposit(self, amount: Money):
        self.balance = self.balance + amount

    @forge
    def withdraw(self, amount: Money):
        self.balance = self.balance - amount

wallet = Wallet()
wallet.deposit(Money(100))
wallet.withdraw(Money(30))
print(wallet.balance)  # Money(70)
```

---

## The Kinetic Engine

The Kinetic Engine models **motion as math**. Animation is the delta between two states.

### Core Concepts

- **Presence**: A snapshot of state (the "before" or "after" card)
- **Delta**: The mathematical difference between presences
- **Motion**: Delta IS the motion—no guessing, just math

### Basic Motion

```python
from tinytalk_py import KineticEngine, Presence

engine = KineticEngine()

# Define start and end states
start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 100, 'y': 50})

# Calculate motion
result = engine.resolve_motion(start, end)
print(result)
# {
#   'status': 'synchronized',
#   'delta': {'x': {'from': 0, 'to': 100, 'delta': 100},
#             'y': {'from': 0, 'to': 50, 'delta': 50}},
#   'from': {'x': 0, 'y': 0},
#   'to': {'x': 100, 'y': 50}
# }
```

### Adding Boundaries

```python
engine = KineticEngine()

# Add boundary: x cannot exceed 80
engine.add_boundary(
    lambda d: d.changes.get('x', {}).get('to', 0) > 80,
    name="MaxX"
)

# Try motion that violates boundary
start = Presence({'x': 0})
end = Presence({'x': 100})  # Exceeds 80!

result = engine.resolve_motion(start, end)
print(result['status'])  # 'finfr'
print(result['reason'])  # "Boundary 'MaxX' violated"
```

### Interpolation

Generate frames between two states:

```python
engine = KineticEngine()

start = Presence({'x': 0, 'y': 0})
end = Presence({'x': 100, 'y': 100})

# Generate 10 intermediate frames
frames = engine.interpolate(start, end, steps=10)

for i, frame in enumerate(frames):
    print(f"Frame {i}: x={frame.state.get('x', 0):.1f}")

# Frame 0: x=0.0
# Frame 1: x=11.1
# Frame 2: x=22.2
# ...
# Frame 9: x=100.0
```

### Delta Calculation

```python
from tinytalk_py import Presence, Delta, motion

# Calculate delta between presences
start = Presence({'x': 10, 'y': 20, 'color': 'red'})
end = Presence({'x': 50, 'y': 80, 'color': 'blue'})

delta = end - start

print(delta.changes)
# {
#   'x': {'from': 10, 'to': 50, 'delta': 40},
#   'y': {'from': 20, 'to': 80, 'delta': 60},
#   'color': {'from': 'red', 'to': 'blue', 'delta': None}
# }

# Quick helper
delta = motion({'x': 0}, {'x': 100})
```

---

## Ratio Constraints (f/g)

**finfr = f/g** — Newton's core insight: every constraint is a ratio.

### The Philosophy

In physics, ratios define reality:
- Force/Mass = Acceleration
- Energy/Time = Power
- Distance/Time = Velocity

In TinyTalk:
- **f** = forge/fact/function (what you're trying to do)
- **g** = ground/goal/governance (what reality allows)
- **f/g > threshold** → finfr
- **f/g undefined (g=0)** → finfr (ontological death)

### Basic Ratio

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class LeverageGovernor(Blueprint):
    debt = field(float, default=0.0)
    equity = field(float, default=1000.0)

    @law
    def max_leverage(self):
        """Debt-to-equity cannot exceed 3:1"""
        when(ratio(self.debt, self.equity) > 3.0, finfr)

    @forge
    def borrow(self, amount):
        self.debt += amount

gov = LeverageGovernor()
gov.borrow(2000)   # OK (ratio = 2.0)
gov.borrow(1500)   # BLOCKED (would be 3.5)
```

### Undefined Ratios

When the denominator is zero, the ratio is undefined:

```python
from tinytalk_py import finfr_if_undefined

class SafeDivision(Blueprint):
    numerator = field(float, default=100.0)
    denominator = field(float, default=10.0)

    @law
    def valid_ratio(self):
        """Denominator cannot be zero"""
        finfr_if_undefined(self.numerator, self.denominator)

    @forge
    def set_denominator(self, value):
        self.denominator = value

safe = SafeDivision()
safe.set_denominator(5)   # OK
safe.set_denominator(0)   # BLOCKED (undefined ratio)
```

### RatioResult Class

```python
from tinytalk_py import RatioResult

r = RatioResult(500, 1000)  # f=500, g=1000
print(r.value)      # 0.5
print(r.undefined)  # False
print(r < 1.0)      # True
print(r > 0.3)      # True

# Undefined ratio
r_undef = RatioResult(100, 0)
print(r_undef.undefined)  # True
print(r_undef > 1.0)      # True (always exceeds)
print(r_undef <= 1.0)     # False (never satisfies)
```

### Real-World Ratio Examples

| Domain | Constraint | f | g | Threshold |
|--------|------------|---|---|-----------|
| Banking | No overdraft | withdrawal | balance | ≤ 1.0 |
| Finance | Leverage limit | debt | equity | ≤ 3.0 |
| Healthcare | Seizure safety | flicker_rate | safe_limit | < 1.0 |
| Education | Class size | students | capacity | ≤ 1.0 |
| Manufacturing | Defect rate | defects | total | < 0.01 |

---

## Reversible Shell

Newton operates as a **reversible state machine**. The shell reflects this through bijective command pairs—every action has an inverse.

### Command Pairs

| Action | Inverse | Meaning |
|--------|---------|---------|
| `try` | `untry` | Speculative execution with rollback |
| `split` | `join` | Branch creation / merge |
| `lock` | `unlock` | Commit / uncommit |
| `take` | `give` | Acquire / release resource |
| `open` | `close` | Begin / end scope |
| `remember` | `forget` | Persist / clear memory |
| `say` | `unsay` | Emit / retract signal |
| `peek` | — | Observe (no mutation, no inverse needed) |

### Basic Usage

```python
from core.shell import ReversibleShell

# Create a shell with initial state
shell = ReversibleShell({"balance": 1000})

# Take a resource
shell.take("user", "alice")          # → {"balance": 1000, "user": "alice"}

# Split into experimental branch
shell.split("experiment")            # Creates branch "experiment"

# Try something risky
shell.take("risk", 500)

# Peek without mutation
result = shell.peek()                # View current state

# Undo everything (reverse order)
shell.undo()                         # untake risk
shell.undo()                         # unsplit (back to main)

# State is exactly restored
assert shell.state == {"balance": 1000, "user": "alice"}
```

### The Bijection Principle

Users don't need to learn that Newton is reversible. They **feel** it because:
- `try` naturally has `untry`
- `split` naturally has `join`
- `take` naturally has `give`

The reversibility is in the grammar itself.

### Integration with Blueprint/Forge

The shell commands map to Blueprint operations:

```python
# Shell command        # Blueprint equivalent
shell.try_action(fn)   # @forge with state save/restore
shell.split("name")    # Create isolated branch
shell.lock("msg")      # Commit state (similar to ledger entry)
shell.remember(k, v)   # Persist to memory (vault-like)
```

See `core/shell.py` for the full implementation.

---

## Basic Examples

### Example 1: Temperature Controller

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, Celsius

class Thermostat(Blueprint):
    """A thermostat with safety limits."""

    current_temp = field(float, default=20.0)
    target_temp = field(float, default=22.0)
    min_temp = field(float, default=10.0)
    max_temp = field(float, default=30.0)

    @law
    def within_safe_range(self):
        """Temperature must stay in safe range."""
        when(self.target_temp < self.min_temp, finfr)
        when(self.target_temp > self.max_temp, finfr)

    @forge
    def set_target(self, temp):
        """Set target temperature."""
        self.target_temp = temp
        return f"Target set to {temp}°C"

    @forge
    def adjust(self, delta):
        """Adjust target by delta."""
        self.target_temp += delta
        return f"Adjusted to {self.target_temp}°C"

# Usage
thermo = Thermostat()
thermo.set_target(25)    # OK
thermo.adjust(3)         # OK (28°C)
thermo.adjust(5)         # BLOCKED (would be 33°C > 30°C)
```

### Example 2: Inventory Manager

```python
class Inventory(Blueprint):
    """Track inventory with minimum stock alerts."""

    stock = field(int, default=100)
    reserved = field(int, default=0)
    min_stock = field(int, default=10)

    @law
    def stock_non_negative(self):
        when(self.stock < 0, finfr)

    @law
    def reserved_within_stock(self):
        when(self.reserved > self.stock, finfr)

    @law
    def maintain_minimum(self):
        available = self.stock - self.reserved
        when(available < self.min_stock, finfr)

    @forge
    def reserve(self, quantity):
        self.reserved += quantity
        return f"Reserved {quantity}. Available: {self.stock - self.reserved}"

    @forge
    def fulfill(self, quantity):
        self.stock -= quantity
        self.reserved -= quantity
        return f"Fulfilled {quantity}. Stock: {self.stock}"

    @forge
    def restock(self, quantity):
        self.stock += quantity
        return f"Restocked {quantity}. Stock: {self.stock}"

inv = Inventory(stock=50)
inv.reserve(30)     # OK (available = 20)
inv.reserve(15)     # BLOCKED (would leave available = 5 < 10)
```

### Example 3: Simple State Machine

```python
class TrafficLight(Blueprint):
    """Traffic light with valid state transitions."""

    state = field(str, default="red")

    @law
    def valid_state(self):
        valid_states = ["red", "yellow", "green"]
        when(self.state not in valid_states, finfr)

    @forge
    def next(self):
        """Cycle to next state."""
        transitions = {
            "red": "green",
            "green": "yellow",
            "yellow": "red"
        }
        self.state = transitions[self.state]
        return self.state

light = TrafficLight()
print(light.next())  # green
print(light.next())  # yellow
print(light.next())  # red
```

---

## Intermediate Examples

### Example 4: Banking System

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio, Money

class BankAccount(Blueprint):
    """Full-featured bank account with multiple protections."""

    balance = field(float, default=0.0)
    daily_withdrawn = field(float, default=0.0)
    daily_limit = field(float, default=1000.0)
    account_type = field(str, default="checking")
    overdraft_protection = field(bool, default=False)
    overdraft_limit = field(float, default=0.0)

    @law
    def no_negative_balance(self):
        """Balance cannot go below overdraft limit."""
        min_allowed = -self.overdraft_limit if self.overdraft_protection else 0
        when(self.balance < min_allowed, finfr)

    @law
    def daily_withdrawal_limit(self):
        """Cannot exceed daily withdrawal limit."""
        when(self.daily_withdrawn > self.daily_limit, finfr)

    @forge
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount
        return {"action": "deposit", "amount": amount, "balance": self.balance}

    @forge
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal must be positive")
        self.balance -= amount
        self.daily_withdrawn += amount
        return {"action": "withdraw", "amount": amount, "balance": self.balance}

    @forge
    def transfer(self, to_account, amount):
        self.balance -= amount
        self.daily_withdrawn += amount
        to_account.balance += amount
        return {"action": "transfer", "amount": amount, "to": id(to_account)}

    @forge
    def reset_daily_limit(self):
        """Call at midnight to reset daily withdrawn."""
        self.daily_withdrawn = 0.0
        return "Daily limit reset"

# Usage
checking = BankAccount(balance=5000, daily_limit=500)
savings = BankAccount(balance=10000, account_type="savings")

checking.withdraw(200)           # OK
checking.withdraw(200)           # OK (daily = 400)
checking.withdraw(200)           # BLOCKED (would exceed daily limit)

checking.reset_daily_limit()
checking.transfer(savings, 1000) # OK
```

### Example 5: Game Character

```python
class GameCharacter(Blueprint):
    """RPG character with stats and constraints."""

    # Stats
    health = field(int, default=100)
    max_health = field(int, default=100)
    mana = field(int, default=50)
    max_mana = field(int, default=50)
    level = field(int, default=1)
    experience = field(int, default=0)

    # Position
    x = field(float, default=0.0)
    y = field(float, default=0.0)

    @law
    def health_bounds(self):
        when(self.health < 0, finfr)  # Can't go negative
        when(self.health > self.max_health, finfr)  # Can't exceed max

    @law
    def mana_bounds(self):
        when(self.mana < 0, finfr)
        when(self.mana > self.max_mana, finfr)

    @law
    def valid_level(self):
        when(self.level < 1 or self.level > 99, finfr)

    @law
    def position_bounds(self):
        """Stay within game world."""
        when(self.x < 0 or self.x > 1000, finfr)
        when(self.y < 0 or self.y > 1000, finfr)

    @forge
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return "defeated"
        return f"took {amount} damage, health: {self.health}"

    @forge
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        return f"healed {amount}, health: {self.health}"

    @forge
    def cast_spell(self, mana_cost):
        self.mana -= mana_cost
        return f"cast spell, mana: {self.mana}"

    @forge
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        return f"moved to ({self.x}, {self.y})"

    @forge
    def gain_exp(self, amount):
        self.experience += amount
        # Level up at 100 exp per level
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            self.max_health += 10
            self.max_mana += 5
        return f"gained {amount} exp, level: {self.level}"

hero = GameCharacter()
hero.move(100, 50)        # OK
hero.cast_spell(30)       # OK (mana: 20)
hero.cast_spell(30)       # BLOCKED (would be -10)
hero.gain_exp(250)        # Level up!
print(hero.level)         # 3
```

### Example 6: Task Queue

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime

class TaskQueue(Blueprint):
    """Priority task queue with limits."""

    tasks = field(list, default=None)
    max_tasks = field(int, default=100)
    processing = field(bool, default=False)

    @law
    def queue_limit(self):
        if self.tasks is not None:
            when(len(self.tasks) > self.max_tasks, finfr)

    @law
    def no_process_while_processing(self):
        """Prevent concurrent processing."""
        # This is checked but we control it via forge
        pass

    @forge
    def add_task(self, task, priority=5):
        if self.tasks is None:
            self.tasks = []
        self.tasks.append({
            "task": task,
            "priority": priority,
            "added": datetime.now().isoformat()
        })
        # Sort by priority (higher first)
        self.tasks.sort(key=lambda t: t["priority"], reverse=True)
        return f"Added task, queue size: {len(self.tasks)}"

    @forge
    def process_next(self):
        if not self.tasks or len(self.tasks) == 0:
            return None
        self.processing = True
        task = self.tasks.pop(0)
        self.processing = False
        return task

    @forge
    def clear(self):
        self.tasks = []
        return "Queue cleared"

queue = TaskQueue(max_tasks=5)
queue.add_task("email", priority=3)
queue.add_task("backup", priority=1)
queue.add_task("alert", priority=10)

print(queue.process_next())  # alert (highest priority)
print(queue.process_next())  # email
print(queue.process_next())  # backup
```

---

## Advanced Examples

### Example 7: Financial Risk Governor

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, ratio

class RiskGovernor(Blueprint):
    """
    Institutional-grade risk management.
    Used for trading desks and clearing houses.
    """

    # Portfolio state
    assets = field(float, default=1_000_000.0)
    liabilities = field(float, default=0.0)
    positions = field(dict, default=None)

    # Risk limits
    max_leverage = field(float, default=10.0)
    concentration_limit = field(float, default=0.25)  # 25% max per position
    var_limit = field(float, default=50000.0)  # Value at Risk limit

    # Tracking
    trade_count = field(int, default=0)

    @law
    def no_insolvency(self):
        """Liabilities cannot exceed assets."""
        when(self.liabilities > self.assets, finfr)

    @law
    def leverage_limit(self):
        """Position/equity ratio capped."""
        total_position = sum(
            abs(v) for v in (self.positions or {}).values()
        )
        equity = self.assets - self.liabilities
        if equity > 0:
            when(ratio(total_position, equity) > self.max_leverage, finfr)

    @law
    def concentration_check(self):
        """No single position > 25% of portfolio."""
        if self.positions:
            total = sum(abs(v) for v in self.positions.values())
            if total > 0:
                for symbol, value in self.positions.items():
                    when(ratio(abs(value), total) > self.concentration_limit, finfr)

    @forge
    def open_position(self, symbol, value):
        if self.positions is None:
            self.positions = {}
        self.positions[symbol] = self.positions.get(symbol, 0) + value
        self.liabilities += abs(value) * 0.1  # 10% margin
        self.trade_count += 1
        return {"symbol": symbol, "position": self.positions[symbol]}

    @forge
    def close_position(self, symbol):
        if self.positions and symbol in self.positions:
            value = self.positions.pop(symbol)
            self.liabilities -= abs(value) * 0.1
            return {"symbol": symbol, "closed": value}
        return None

    @forge
    def mark_to_market(self, prices):
        """Update positions with current prices."""
        pnl = 0
        for symbol, qty in (self.positions or {}).items():
            if symbol in prices:
                pnl += qty * prices[symbol]
        self.assets += pnl
        return {"pnl": pnl, "assets": self.assets}

# Usage
gov = RiskGovernor(assets=1_000_000)

# Open positions
gov.open_position("AAPL", 100_000)
gov.open_position("GOOGL", 150_000)
gov.open_position("MSFT", 200_000)

# This would violate concentration (would be 60% of portfolio)
try:
    gov.open_position("TSLA", 500_000)
except Exception as e:
    print("Blocked by concentration limit")

print(f"Total positions: {sum(gov.positions.values())}")
print(f"Trade count: {gov.trade_count}")
```

### Example 8: Distributed Consensus Simulator

```python
class ConsensusNode(Blueprint):
    """
    Simulates a Byzantine fault-tolerant consensus node.
    Implements simplified PBFT concepts.
    """

    node_id = field(str, default="node_0")
    state = field(str, default="idle")  # idle, pre-prepare, prepare, commit, final
    value = field(str, default=None)
    prepare_votes = field(int, default=0)
    commit_votes = field(int, default=0)
    total_nodes = field(int, default=4)

    @law
    def valid_state(self):
        valid = ["idle", "pre-prepare", "prepare", "commit", "final"]
        when(self.state not in valid, finfr)

    @law
    def quorum_for_prepare(self):
        """Cannot move to prepare without pre-prepare."""
        when(self.state == "prepare" and self.value is None, finfr)

    @law
    def quorum_for_commit(self):
        """Need 2f+1 prepares to commit (f = faulty nodes)."""
        f = (self.total_nodes - 1) // 3
        quorum = 2 * f + 1
        when(self.state == "commit" and self.prepare_votes < quorum, finfr)

    @law
    def quorum_for_final(self):
        """Need 2f+1 commits to finalize."""
        f = (self.total_nodes - 1) // 3
        quorum = 2 * f + 1
        when(self.state == "final" and self.commit_votes < quorum, finfr)

    @forge
    def pre_prepare(self, value):
        self.state = "pre-prepare"
        self.value = value
        return f"Pre-prepare: {value}"

    @forge
    def receive_prepare(self):
        self.prepare_votes += 1
        return f"Prepare votes: {self.prepare_votes}"

    @forge
    def move_to_prepare(self):
        self.state = "prepare"
        return "Moved to prepare phase"

    @forge
    def receive_commit(self):
        self.commit_votes += 1
        return f"Commit votes: {self.commit_votes}"

    @forge
    def move_to_commit(self):
        self.state = "commit"
        return "Moved to commit phase"

    @forge
    def finalize(self):
        self.state = "final"
        return f"Finalized with value: {self.value}"

# Simulate consensus
node = ConsensusNode(total_nodes=4)

node.pre_prepare("block_123")
node.move_to_prepare()

# Collect prepare votes (need 3 for quorum with 4 nodes)
node.receive_prepare()
node.receive_prepare()
node.receive_prepare()

node.move_to_commit()

# Collect commit votes
node.receive_commit()
node.receive_commit()
node.receive_commit()

node.finalize()
print(f"Consensus reached: {node.value}")
```

### Example 9: Physics Simulation

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr, KineticEngine, Presence

class PhysicsObject(Blueprint):
    """
    2D physics object with velocity, acceleration, and collision.
    """

    # Position
    x = field(float, default=0.0)
    y = field(float, default=0.0)

    # Velocity
    vx = field(float, default=0.0)
    vy = field(float, default=0.0)

    # Physical properties
    mass = field(float, default=1.0)
    radius = field(float, default=10.0)

    # World bounds
    world_width = field(float, default=800.0)
    world_height = field(float, default=600.0)

    @law
    def within_bounds(self):
        """Object must stay within world."""
        when(self.x - self.radius < 0, finfr)
        when(self.x + self.radius > self.world_width, finfr)
        when(self.y - self.radius < 0, finfr)
        when(self.y + self.radius > self.world_height, finfr)

    @law
    def speed_limit(self):
        """Maximum velocity."""
        speed = (self.vx**2 + self.vy**2)**0.5
        when(speed > 500, finfr)

    @law
    def positive_mass(self):
        when(self.mass <= 0, finfr)

    @forge
    def apply_force(self, fx, fy, dt=0.016):
        """Apply force for one frame (60fps = 0.016s)."""
        ax = fx / self.mass
        ay = fy / self.mass
        self.vx += ax * dt
        self.vy += ay * dt
        return {"vx": self.vx, "vy": self.vy}

    @forge
    def update(self, dt=0.016):
        """Update position based on velocity."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        return {"x": self.x, "y": self.y}

    @forge
    def bounce_x(self):
        """Reverse x velocity (hit wall)."""
        self.vx = -self.vx * 0.8  # 80% energy retained
        return self.vx

    @forge
    def bounce_y(self):
        """Reverse y velocity (hit wall)."""
        self.vy = -self.vy * 0.8
        return self.vy

# Simulation
ball = PhysicsObject(x=400, y=300, vx=100, vy=50)

for frame in range(100):
    # Apply gravity
    ball.apply_force(0, 500)  # gravity

    try:
        ball.update()
    except Exception:
        # Hit boundary, bounce
        if ball.x - ball.radius < 0 or ball.x + ball.radius > ball.world_width:
            ball.bounce_x()
        if ball.y - ball.radius < 0 or ball.y + ball.radius > ball.world_height:
            ball.bounce_y()

    if frame % 20 == 0:
        print(f"Frame {frame}: pos=({ball.x:.1f}, {ball.y:.1f})")
```

### Example 10: Education Lesson Planner

```python
class NESLessonPlan(Blueprint):
    """
    HISD New Education System compliant lesson plan.
    Enforces 50-minute structure with required phases.
    """

    # Lesson metadata
    title = field(str, default="")
    grade = field(int, default=5)
    subject = field(str, default="math")
    teks_codes = field(list, default=None)

    # Phase durations (minutes)
    opening = field(int, default=5)
    instruction = field(int, default=15)
    guided = field(int, default=15)
    independent = field(int, default=10)
    closing = field(int, default=5)

    # Content
    objective = field(str, default="")
    activities = field(list, default=None)
    materials = field(list, default=None)

    @law
    def total_50_minutes(self):
        """NES requires exactly 50 minutes."""
        total = self.opening + self.instruction + self.guided + self.independent + self.closing
        when(total != 50, finfr)

    @law
    def valid_phase_durations(self):
        """Each phase must have minimum time."""
        when(self.opening < 3, finfr)      # At least 3 min opening
        when(self.instruction < 10, finfr)  # At least 10 min instruction
        when(self.guided < 10, finfr)       # At least 10 min guided
        when(self.independent < 5, finfr)   # At least 5 min independent
        when(self.closing < 3, finfr)       # At least 3 min closing

    @law
    def has_teks(self):
        """Must have at least one TEKS standard."""
        when(self.teks_codes is None or len(self.teks_codes) == 0, finfr)

    @law
    def valid_grade(self):
        when(self.grade < 0 or self.grade > 12, finfr)

    @forge
    def set_phases(self, opening, instruction, guided, independent, closing):
        """Set all phase durations."""
        self.opening = opening
        self.instruction = instruction
        self.guided = guided
        self.independent = independent
        self.closing = closing
        return self._get_state()

    @forge
    def add_teks(self, code):
        if self.teks_codes is None:
            self.teks_codes = []
        self.teks_codes.append(code)
        return self.teks_codes

    @forge
    def generate_structure(self):
        """Generate lesson structure."""
        return {
            "title": self.title,
            "grade": self.grade,
            "subject": self.subject,
            "teks": self.teks_codes,
            "phases": [
                {"phase": "Opening", "duration": self.opening, "content": "Hook, objective, student restate"},
                {"phase": "Instruction", "duration": self.instruction, "content": "I Do - Teacher modeling"},
                {"phase": "Guided", "duration": self.guided, "content": "We Do - Collaborative practice"},
                {"phase": "Independent", "duration": self.independent, "content": "You Do - Solo practice"},
                {"phase": "Closing", "duration": self.closing, "content": "Exit ticket, closure"}
            ],
            "total_minutes": 50
        }

# Create a lesson
lesson = NESLessonPlan(title="Adding Fractions", grade=5, subject="math")
lesson.add_teks("5.3A")
lesson.add_teks("5.3B")

# This will fail - doesn't sum to 50
try:
    lesson.set_phases(5, 20, 20, 10, 10)  # = 65 minutes
except Exception as e:
    print("Invalid duration")

# This works
lesson.set_phases(5, 15, 15, 10, 5)  # = 50 minutes
structure = lesson.generate_structure()
print(f"Lesson: {structure['title']}")
print(f"TEKS: {structure['teks']}")
```

---

## Real-World Applications

### Finance: Trading Risk Management

TinyTalk prevents:
- Overleveraging
- Concentration risk
- Margin violations
- Unauthorized trades

```python
class TradingDesk(Blueprint):
    positions = field(dict, default=None)
    capital = field(float, default=10_000_000)

    @law
    def max_position_size(self):
        for pos in (self.positions or {}).values():
            when(abs(pos) > self.capital * 0.1, finfr)  # 10% max
```

### Healthcare: HIPAA Compliance

TinyTalk ensures:
- Access control enforcement
- Audit trail requirements
- Data minimization
- Consent verification

```python
class PatientRecord(Blueprint):
    data = field(dict, default=None)
    access_level_required = field(int, default=3)

    @law
    def require_consent(self):
        has_consent = self.data and self.data.get("consent_signed")
        when(not has_consent, finfr)
```

### Education: Curriculum Alignment

TinyTalk guarantees:
- TEKS standard alignment
- Time constraints (50-min lessons)
- Phase requirements
- Differentiation rules

### Manufacturing: Quality Control

TinyTalk enforces:
- Defect rate limits
- Temperature bounds
- Pressure safety
- Batch size constraints

### Gaming: Fair Play

TinyTalk prevents:
- Stat overflow exploits
- Position hacks
- Speed hacks
- Resource duplication

---

## Testing TinyTalk Programs

### Unit Testing with pytest

```python
import pytest
from tinytalk_py import LawViolation

def test_law_blocks_invalid_state():
    account = BankAccount(balance=100)

    with pytest.raises(LawViolation):
        account.withdraw(150)  # Would overdraft

    assert account.balance == 100  # Unchanged

def test_forge_succeeds_with_valid_state():
    account = BankAccount(balance=100)

    result = account.withdraw(50)

    assert account.balance == 50
    assert "Withdrew" in result

def test_rollback_preserves_state():
    obj = MultiField(a=10, b=20)

    try:
        obj.update_both(100, 100)  # Violates law
    except LawViolation:
        pass

    assert obj.a == 10
    assert obj.b == 20
```

### Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=1000))
def test_deposit_always_increases_balance(amount):
    account = BankAccount(balance=100)
    old_balance = account.balance

    account.deposit(amount)

    assert account.balance == old_balance + amount

@given(st.integers(min_value=0, max_value=100))
def test_withdraw_never_overdrafts(amount):
    account = BankAccount(balance=100)

    try:
        account.withdraw(amount)
        assert account.balance >= 0
    except LawViolation:
        assert account.balance == 100  # Unchanged
```

### Benchmarking

```python
import time

def benchmark_forge(blueprint, forge_name, iterations=10000):
    forge = getattr(blueprint, forge_name)

    start = time.perf_counter()
    for _ in range(iterations):
        try:
            forge()
        except:
            pass
    elapsed = time.perf_counter() - start

    ops_per_sec = iterations / elapsed
    print(f"{forge_name}: {ops_per_sec:.0f} ops/sec")

# Example
counter = Counter()
benchmark_forge(counter, 'increment')
# Output: increment: 50000 ops/sec
```

---

## Performance Optimization

### Best Practices

1. **Minimize law complexity**: Simple conditions evaluate faster
2. **Avoid expensive computations in laws**: Laws run on every forge
3. **Use appropriate field types**: Native types are faster than custom
4. **Batch operations**: Multiple changes in one forge is faster

### Law Optimization

```python
# Slow: Complex computation in law
@law
def slow_law(self):
    total = sum(expensive_calculation(x) for x in self.items)
    when(total > limit, finfr)

# Fast: Pre-compute and store
@forge
def add_item(self, item):
    self.total += item.value  # Incremental update
    self.items.append(item)

@law
def fast_law(self):
    when(self.total > limit, finfr)
```

### Benchmarks

| Operation | Speed | Notes |
|-----------|-------|-------|
| Law evaluation | 50,000+ ops/sec | Simple laws |
| Forge execution | 30,000+ ops/sec | With rollback support |
| Matter math | 100,000+ ops/sec | Type-safe arithmetic |
| Delta calculation | 80,000+ ops/sec | Presence difference |
| Motion resolution | 20,000+ ops/sec | With boundaries |

---

## Extending TinyTalk

This section is for **language maintainers** who want to extend TinyTalk.

### Architecture Overview

```
tinytalk_py/
├── __init__.py       # Public exports
├── core.py           # Blueprint, Law, Field, when, finfr, fin, ratio
├── matter.py         # Matter types (Money, Mass, etc.)
├── engine.py         # KineticEngine, Presence, Delta
├── education.py      # Education module
└── ...
```

### Adding a New Matter Type

1. Open `tinytalk_py/matter.py`
2. Add your Matter class:

```python
@dataclass
class Energy(Matter):
    """Energy value. Default unit: J (Joules)."""
    _value: float
    _unit: str = "J"

    def __init__(self, value: float, unit: str = "J"):
        self._value = float(value)
        self._unit = unit

    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    def to_calories(self) -> 'Energy':
        """Convert to calories."""
        if self._unit == "cal":
            return self
        elif self._unit == "J":
            return Energy(self._value / 4.184, "cal")
        return self

def Joules(value: float) -> Energy:
    """Create an Energy in Joules."""
    return Energy(value, "J")

def Calories(value: float) -> Energy:
    """Create an Energy in calories."""
    return Energy(value, "cal")
```

3. Export in `__init__.py`:

```python
from .matter import Energy, Joules, Calories
```

### Adding a New Law Type

1. Open `tinytalk_py/core.py`
2. Add new result type if needed:

```python
class LawResult(Enum):
    ALLOWED = "allowed"
    FIN = "fin"
    FINFR = "finfr"
    WARN = "warn"  # New: warning without blocking
```

3. Create exception class:

```python
class LawWarning(Exception):
    """Raised when a law triggers a warning."""
    def __init__(self, law_name: str, message: str = ""):
        self.law_name = law_name
        self.message = message
        super().__init__(self.message)
```

4. Update `when()` function:

```python
WARN = _Warn()
warn = WARN

def when(condition: bool, result: Any = None) -> bool:
    if result is FINFR and condition:
        raise LawViolation("inline", "finfr triggered")
    if result is FIN and condition:
        raise FinClosure("inline", "fin triggered")
    if result is WARN and condition:
        raise LawWarning("inline", "warning triggered")
    return condition
```

### Adding a New Blueprint Method

1. Add method to `Blueprint` class in `core.py`:

```python
class Blueprint(metaclass=BlueprintMeta):
    # ... existing code ...

    def validate(self) -> tuple[bool, list]:
        """
        Validate current state against all laws.
        Returns (valid, list of violations).
        """
        violations = []
        for law_obj in self._laws:
            triggered, result = law_obj.evaluate(self)
            if triggered:
                violations.append({
                    "law": law_obj.name,
                    "result": result.value
                })
        return len(violations) == 0, violations
```

### Creating a Domain Module

1. Create new file `tinytalk_py/my_domain.py`:

```python
"""
TinyTalk My Domain Module
"""

from .core import Blueprint, field, law, forge, when, finfr

class MyDomainBlueprint(Blueprint):
    """Base class for my domain."""

    domain_field = field(str, default="my_domain")

    @law
    def domain_law(self):
        """Domain-specific constraint."""
        pass

# Domain-specific utilities
def create_domain_object(**kwargs):
    """Factory function for domain objects."""
    return MyDomainBlueprint(**kwargs)
```

2. Export in `__init__.py`:

```python
from .my_domain import MyDomainBlueprint, create_domain_object
```

### Testing Extensions

```python
# tests/test_my_extension.py
import pytest
from tinytalk_py import Energy, Joules, Calories

def test_energy_creation():
    e = Joules(100)
    assert e.value == 100
    assert e.unit == "J"

def test_energy_conversion():
    j = Joules(4.184)
    c = j.to_calories()
    assert abs(c.value - 1.0) < 0.001

def test_energy_type_safety():
    from tinytalk_py import Money
    e = Joules(100)
    m = Money(100)

    with pytest.raises(TypeError):
        e + m
```

### Extension Guidelines

1. **Preserve the lexicon**: Don't add new keywords without careful consideration
2. **Maintain type safety**: All operations should be type-checked
3. **Follow the three-layer model**: Governance, Executive, Application
4. **Write comprehensive tests**: Including property-based tests
5. **Document thoroughly**: Include docstrings and examples
6. **Consider performance**: Laws are called frequently

### Process for Language Changes

1. **Proposal**: Create an issue describing the change
2. **Discussion**: Get feedback from maintainers
3. **Implementation**: Write code with tests
4. **Documentation**: Update this guide and other docs
5. **Review**: Submit PR for review
6. **Release**: Include in next version

---

## API Reference

### Core Module (`tinytalk_py.core`)

#### Classes

| Class | Description |
|-------|-------------|
| `Blueprint` | Base class for all TinyTalk objects |
| `Field` | Typed field descriptor |
| `Law` | Constraint definition |
| `LawResult` | Enum of law outcomes |
| `RatioResult` | Result of ratio calculation |
| `LawViolation` | Exception for finfr |
| `FinClosure` | Exception for fin |

#### Functions

| Function | Description |
|----------|-------------|
| `field(type, default)` | Create a field descriptor |
| `law` | Decorator for law methods |
| `forge` | Decorator for action methods |
| `when(condition, result)` | Declare a fact |
| `ratio(f, g)` | Calculate f/g ratio |
| `finfr_if_undefined(f, g)` | Trigger finfr if ratio undefined |

#### Constants

| Constant | Description |
|----------|-------------|
| `finfr` / `FINFR` | Ontological death marker |
| `fin` / `FIN` | Closure marker |

### Matter Module (`tinytalk_py.matter`)

#### Classes

| Class | Unit | Factory |
|-------|------|---------|
| `Money` | USD | `Money(value, unit)` |
| `Mass` | kg | `Kilograms(value)` |
| `Distance` | m | `Meters(value)` |
| `Temperature` | C/F/K | `Celsius(v)`, `Fahrenheit(v)` |
| `Pressure` | PSI | `PSI(value)` |
| `FlowRate` | L/min | `FlowRate(value)` |
| `Velocity` | m/s | `Velocity(value)` |
| `Time` | s | `Time(value)` |
| `Volume` | L | `Liters(value)` |

### Engine Module (`tinytalk_py.engine`)

#### Classes

| Class | Description |
|-------|-------------|
| `KineticEngine` | Motion resolution engine |
| `Presence` | State snapshot |
| `Delta` | State difference |

#### Functions

| Function | Description |
|----------|-------------|
| `motion(start, end)` | Quick delta calculation |

---

## Troubleshooting

### Common Errors

#### LawViolation: Law 'X' prevents this state

**Cause**: Your forge would create a state that violates a law.

**Solution**:
1. Check what state the forge would create
2. Ensure the state satisfies all laws
3. Add validation before the forge if needed

```python
# Before
account.withdraw(1000)  # Might violate

# After
if account.balance >= 1000:
    account.withdraw(1000)
else:
    print("Insufficient funds")
```

#### TypeError: Cannot add X and Y

**Cause**: Trying to mix different Matter types.

**Solution**: Use the same Matter type for operations.

```python
# Wrong
Money(100) + 50

# Right
Money(100) + Money(50)
```

#### Field type mismatch

**Cause**: Assigning wrong type to a field.

**Solution**: Ensure values match field types.

```python
# Wrong
obj.count = "hello"  # count is int

# Right
obj.count = 42
```

### Debugging Tips

1. **Check state before forge**:
```python
print(obj._get_state())
obj.some_forge()
```

2. **Validate manually**:
```python
valid, violations = obj.validate()
print(violations)
```

3. **Test laws in isolation**:
```python
obj.value = -10  # Set directly
try:
    obj.my_law()  # Call law directly
except LawViolation:
    print("Law would trigger")
```

4. **Use smaller forges**:
```python
# Instead of one big forge
@forge
def do_everything(self):
    self.a = 1
    self.b = 2
    self.c = 3

# Use smaller forges
@forge
def set_a(self, v): self.a = v

@forge
def set_b(self, v): self.b = v
```

### Getting Help

- **Documentation**: This guide and `TINYTALK_BIBLE.md`
- **Examples**: `examples/tinytalk_demo.py`
- **Tests**: `tests/test_tinytalk.py`
- **Issues**: GitHub issues
- **Contact**: jn.lewis1@outlook.com

---

## Conclusion

TinyTalk inverts programming. Instead of asking "what can happen?", you declare "what cannot happen." This makes your programs:

- **Safer**: Invalid states cannot exist
- **Clearer**: Constraints are explicit
- **Auditable**: Every law is documented
- **Provable**: Constraints can be formally verified

**The constraint IS the instruction. The verification IS the computation.**

```python
# This is TinyTalk
when(reality violates physics, finfr)
```

**finfr.**

---

<p align="center">
  <em>© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas</em><br>
  <em>"1 == 1. The cloud is weather. We're building shelter."</em>
</p>
