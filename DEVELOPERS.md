# Developer Guide

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

```
    ╭──────────────────────────────────────────────────────────╮
    │                                                          │
    │   Newton Developer Guide                                 │
    │                                                          │
    │   From zero to contributor.                              │
    │   Pick your level. Start building.                       │
    │                                                          │
    ╰──────────────────────────────────────────────────────────╯
```

---

## Pick Your Path

```
🌱 Seedling     →  Just want to use Newton
🌿 Sprout       →  Building apps with tinyTalk
🌳 Sapling      →  Extending the language
🌲 Tree         →  Contributing to core
🏔️ Mountain    →  Maintaining Newton
```

---

# 🌱 Seedling Level
*"I just want to use this thing"*

## Install

```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
pip install -e .
```

## Verify

```bash
newton demo
```

If you see the bank account demo, you're done. ✓

## Use It

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr

class MyThing(Blueprint):
    value = field(float, default=0.0)

    @law
    def must_be_positive(self):
        when(self.value < 0, finfr)

    @forge
    def set_value(self, v):
        self.value = v
```

**That's it.** You're a Newton user now.

---

# 🌿 Sprout Level
*"I want to build real applications"*

## IDE Setup

### VS Code (Recommended)

1. Install [VS Code](https://code.visualstudio.com/)
2. Install Python extension
3. Open Newton-api folder
4. Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "python3",
    "python.linting.enabled": true,
    "editor.formatOnSave": true
}
```

### PyCharm

1. Install [PyCharm Community](https://www.jetbrains.com/pycharm/)
2. Open Newton-api as project
3. Set Python interpreter to your venv

### RStudio (for R)

1. Open RStudio
2. Set working directory to Newton-api
3. `source("tinytalk/r/tinytalk.R")`

## Project Structure

```
Newton-api/
├── newton_sdk/       # 📦 The installable package
├── tinytalk_py/      # 🗣️ Python tinyTalk library
├── tinytalk/         # 💎📊 Ruby & R libraries
├── core/             # ⚙️ Newton Supercomputer internals
├── tests/            # 🧪 Test suite
├── docs/             # 📚 Documentation
└── examples/         # 💡 Example code
```

## Common Patterns

### Pattern 1: Resource Management

```python
class DatabaseConnection(Blueprint):
    connected = field(bool, default=False)
    queries_run = field(int, default=0)
    max_queries = field(int, default=1000)

    @law
    def must_be_connected(self):
        """Can't run queries if not connected."""
        when(self.queries_run > 0 and not self.connected, finfr)

    @law
    def query_limit(self):
        """Can't exceed query limit."""
        when(self.queries_run > self.max_queries, finfr)

    @forge
    def connect(self):
        self.connected = True
        return "Connected"

    @forge
    def query(self, sql):
        self.queries_run += 1
        return f"Executed: {sql}"
```

### Pattern 2: State Machine

```python
class OrderStatus(Blueprint):
    status = field(str, default="pending")
    paid = field(bool, default=False)
    shipped = field(bool, default=False)

    @law
    def cant_ship_unpaid(self):
        """Must be paid before shipping."""
        when(self.shipped and not self.paid, finfr)

    @law
    def valid_status_flow(self):
        """Status can only go forward."""
        invalid = (
            (self.status == "pending" and self.shipped) or
            (self.status == "cancelled" and (self.paid or self.shipped))
        )
        when(invalid, finfr)

    @forge
    def pay(self):
        self.paid = True
        self.status = "paid"

    @forge
    def ship(self):
        self.shipped = True
        self.status = "shipped"
```

### Pattern 3: Numeric Bounds

```python
class Percentage(Blueprint):
    value = field(float, default=0.0)

    @law
    def bounds(self):
        when(self.value < 0 or self.value > 100, finfr)

    @forge
    def set(self, v):
        self.value = v
```

---

# 🌳 Sapling Level
*"I want to extend the language"*

## Add a New Matter Type

**File:** `tinytalk_py/matter.py`

```python
@dataclass
class Energy(Matter):
    """Energy in Joules."""
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

    def to_kwh(self) -> 'Energy':
        return Energy(self._value / 3_600_000, "kWh")

def Joules(value: float) -> Energy:
    return Energy(value, "J")

def KilowattHours(value: float) -> Energy:
    return Energy(value * 3_600_000, "J")
```

**Don't forget:** Add to `__init__.py` exports!

## Add a New Keyword

**File:** `tinytalk_py/core.py`

```python
def unless(condition: bool, result=None):
    """
    Inverse of 'when'. Triggers if condition is FALSE.

    Usage:
        unless(balance > 0, finfr)
    """
    return when(not condition, result)

def must(condition: bool):
    """
    Shorthand for 'unless condition, finfr'.

    Usage:
        must(balance > 0)  # Balance must be positive
    """
    unless(condition, finfr)
```

## Create a Domain Extension

```python
# gaming.py - Gaming domain for tinyTalk

from newton_sdk import Blueprint, field, law, forge, when, finfr

class GameEntity(Blueprint):
    """Base for all game entities."""
    hp = field(float, default=100.0)
    max_hp = field(float, default=100.0)
    alive = field(bool, default=True)

    @law
    def hp_bounds(self):
        when(self.hp > self.max_hp, finfr)
        when(self.hp < 0, finfr)

    @law
    def death_consistency(self):
        when(self.hp == 0 and self.alive, finfr)
        when(self.hp > 0 and not self.alive, finfr)

    @forge
    def damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False
        return f"Took {amount} damage"

    @forge
    def heal(self, amount):
        if not self.alive:
            raise ValueError("Cannot heal dead entity")
        self.hp = min(self.max_hp, self.hp + amount)
        return f"Healed {amount}"


class Player(GameEntity):
    """A player with inventory."""
    gold = field(int, default=0)
    inventory = field(list, default=[])

    @law
    def no_negative_gold(self):
        when(self.gold < 0, finfr)

    @forge
    def buy(self, item, price):
        self.gold -= price
        self.inventory.append(item)
        return f"Bought {item}"
```

---

# 🌲 Tree Level
*"I want to contribute to Newton"*

## Development Setup

```bash
# Clone
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[all]"

# Run tests
pytest tests/ -v
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=core --cov-report=html

# Property-based tests
pytest tests/test_properties.py -v
```

## Code Style

- **Type hints** everywhere
- **Docstrings** for public functions
- **ASCII art headers** for major sections:

```python
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION NAME
# ═══════════════════════════════════════════════════════════════════════════════
```

## Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test
pytest tests/ -v

# 3. Commit with clear message
git commit -m "Add feature: description"

# 4. Push
git push -u origin feature/my-feature

# 5. Create PR on GitHub
```

## PR Guidelines

1. **One feature per PR**
2. **Tests must pass**
3. **Update docs if needed**
4. **Describe the change**

---

# 🏔️ Mountain Level
*"I want to maintain Newton"*

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    newton_sdk (Package)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   client    │  │   server    │  │        cli          │ │
│  │  (API)      │  │  (launch)   │  │    (commands)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    tinytalk_py (Language)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    core     │  │   matter    │  │       engine        │ │
│  │(Blueprint)  │  │  (Types)    │  │    (Kinetics)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    core/ (Supercomputer)                    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐  │
│  │  CDL   │ │ Logic  │ │ Forge  │ │ Vault  │ │  Ledger  │  │
│  └────────┘ └────────┘ └────────┘ └────────┘ └──────────┘  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────────┐   │
│  │ Bridge │ │ Robust │ │Ground  │ │     Cartridges     │   │
│  └────────┘ └────────┘ └────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| CDL | `core/cdl.py` | Constraint Definition Language |
| Logic | `core/logic.py` | Verified computation engine |
| Forge | `core/forge.py` | Content verification |
| Vault | `core/vault.py` | Encrypted storage |
| Ledger | `core/ledger.py` | Immutable audit trail |
| Bridge | `core/bridge.py` | Distributed consensus |

## Release Checklist

- [ ] All tests pass
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated
- [ ] Docs updated
- [ ] Git tag created

## Performance Testing

```bash
python performance_test.py
```

Expected results:
- Health check: < 5ms
- Simple verify: < 10ms
- Calculate: < 5ms

---

## Need Help?

| Question | Answer |
|----------|--------|
| "How do I...?" | Check [GETTING_STARTED.md](GETTING_STARTED.md) |
| "What is...?" | Check [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md) |
| "Found a bug" | Open an issue on GitHub |
| "Want to contribute" | Fork, branch, PR |

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

```
    "Smalltalk gave us objects.
     tinyTalk gives us boundaries.
     Newton gives us verification."

    Welcome to the team. 🍎
```
