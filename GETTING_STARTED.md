# Getting Started with Newton

**January 5, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

```
                    ╭──────────────────────────────────────╮
                    │                                      │
                    │   🍎 Newton SDK                      │
                    │   Smalltalk is back.                 │
                    │                                      │
                    │   "Objects all the way down,         │
                    │    but with boundaries."             │
                    │                                      │
                    ╰──────────────────────────────────────╯
```

## Installation

### Option 1: One-Command Setup (Recommended)

```bash
# Clone and run the setup script
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
chmod +x setup_newton.sh
./setup_newton.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Run verification tests
- Confirm the server works

### Option 2: Manual Install

```bash
# The easy way (like Homebrew!)
pip install -e .

# With server support
pip install -e ".[server]"

# Everything
pip install -e ".[all]"
```

### Verify Installation

```bash
# Run the full system test (requires server running)
python newton_supercomputer.py &
python test_full_system.py

# Expected: 10/10 tests passed
```

**That's it.** You're ready.

**Having issues?** Jump to [🔧 Troubleshooting](#-troubleshooting)

---

## Choose Your Level

| Level | You Are | Start Here |
|-------|---------|------------|
| 🌱 **Seedling** | "What is this?" | [Level 1: Hello Newton](#level-1-hello-newton) |
| 🌿 **Sprout** | "I know Python basics" | [Level 2: Your First Blueprint](#level-2-your-first-blueprint) |
| 🌳 **Sapling** | "I want to build something" | [Level 3: Real World Apps](#level-3-real-world-apps) |
| 🌲 **Tree** | "I want to extend the language" | [Level 4: Language Design](#level-4-language-design) |
| 🏔️ **Mountain** | "I want to contribute" | [Level 5: Core Development](#level-5-core-development) |

---

## Level 1: Hello Newton
*For complete beginners. No experience needed.*

### What is Newton?

Newton is two things:

1. **tinyTalk** - A constraint language (like Smalltalk, but for safety)
2. **The Supercomputer** - A verified computation engine

The big idea: **Define what CANNOT happen, not what can.**

### Your First Command

```bash
newton demo
```

You'll see:
```
Creating BankAccount with $100...
Withdrawing $30... ✓
Withdrawing $50... ✓
Withdrawing $30... ✗ BLOCKED!

The 'no_overdraft' law prevented the forbidden state.
```

### What Just Happened?

The account had $20. Withdrawing $30 would make it -$10.
But we declared: **"negative balance cannot exist."**
So Newton stopped it. Before it happened. Not after.

**This is the "No-First" philosophy.**

---

## Level 2: Your First Blueprint
*For those who know basic Python.*

### The Four Sacred Words

tinyTalk has only four keywords:

| Word | Meaning | Example |
|------|---------|---------|
| `when` | "This is true" | `when(balance < 0, ...)` |
| `and` | "Also this" | `when(x > 0 and y > 0, ...)` |
| `fin` | "Stop here (can reopen)" | A pause |
| `finfr` | "FORBIDDEN. Cannot exist." | Ontological death |

### Create Your First Blueprint

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr

class Thermostat(Blueprint):
    """A thermostat that can't freeze or boil."""

    # Fields = State (Layer 1)
    temperature = field(float, default=20.0)

    # Laws = Constraints (Layer 0) - What CANNOT happen
    @law
    def no_freezing(self):
        when(self.temperature < 0, finfr)

    @law
    def no_boiling(self):
        when(self.temperature > 100, finfr)

    # Forges = Actions (Layer 1) - What CAN happen
    @forge
    def set_temp(self, new_temp):
        self.temperature = new_temp
        return f"Temperature set to {new_temp}°C"
```

### Use It

```python
t = Thermostat()

t.set_temp(22)    # ✓ "Temperature set to 22°C"
t.set_temp(50)    # ✓ "Temperature set to 50°C"
t.set_temp(-5)    # ✗ LawViolation: no_freezing
t.set_temp(150)   # ✗ LawViolation: no_boiling
```

### The Three Layers

```
╭─────────────────────────────────────────────────────╮
│  Layer 2: APPLICATION                               │
│  Your specific use case (Thermostat, BankAccount)   │
├─────────────────────────────────────────────────────┤
│  Layer 1: EXECUTIVE                                 │
│  Fields (state) + Forges (actions)                  │
├─────────────────────────────────────────────────────┤
│  Layer 0: GOVERNANCE                                │
│  Laws - The physics of your world                   │
│  What CANNOT happen. Ever. finfr.                   │
╰─────────────────────────────────────────────────────╯
```

---

## Level 3: Real World Apps
*For those ready to build.*

### Example: Financial Trading System

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr, Money

class TradingAccount(Blueprint):
    """A trading account that prevents insolvency."""

    cash = field(float, default=10000.0)
    positions = field(dict, default={})
    margin_used = field(float, default=0.0)

    # === GOVERNANCE (Layer 0) ===

    @law
    def no_negative_cash(self):
        """Can't have negative cash."""
        when(self.cash < 0, finfr)

    @law
    def margin_limit(self):
        """Can't exceed 50% margin."""
        when(self.margin_used > self.cash * 0.5, finfr)

    # === EXECUTIVE (Layer 1) ===

    @forge
    def buy(self, symbol: str, quantity: int, price: float):
        cost = quantity * price
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        return f"Bought {quantity} {symbol} @ ${price}"

    @forge
    def sell(self, symbol: str, quantity: int, price: float):
        if self.positions.get(symbol, 0) < quantity:
            raise ValueError("Not enough shares")
        revenue = quantity * price
        self.cash += revenue
        self.positions[symbol] -= quantity
        return f"Sold {quantity} {symbol} @ ${price}"
```

### Example: Teacher's Lesson Planner

```python
from newton_sdk import Newton

# Connect to Newton API
newton = Newton("http://localhost:8000")

# Generate a TEKS-aligned lesson plan
lesson = newton.education_lesson(
    grade=5,
    subject="math",
    teks_codes=["5.3A"],
    topic="Adding Fractions with Unlike Denominators",
    accommodations={"ell": True}
)

print(f"Lesson: {lesson['title']}")
for phase in lesson['phases']:
    print(f"  {phase['name']}: {phase['duration']}min")
    for activity in phase['activities']:
        print(f"    - {activity}")

# Generate PLC report for the class
report = newton.education_plc(
    campus="Example Elementary",
    grade=5,
    subject="math",
    scores=[85, 72, 90, 65, 88, 45, 92, 78, 80, 95],
    teks_codes=["5.3A", "5.3B"]
)

print(f"\nPLC Summary: {report['summary']}")
print(f"MAD Score: {report['statistics']['mad']}")
```

### Example: IoT Sensor Network

```python
from newton_sdk import Blueprint, field, law, forge, when, finfr, Celsius

class SensorNode(Blueprint):
    """An IoT sensor with safety bounds."""

    temperature = field(float, default=25.0)
    humidity = field(float, default=50.0)
    battery = field(float, default=100.0)
    alerts = field(list, default=[])

    @law
    def battery_critical(self):
        """Must maintain minimum battery."""
        when(self.battery < 5.0, finfr)

    @law
    def temperature_bounds(self):
        """Operating range: -40°C to 85°C."""
        when(self.temperature < -40 or self.temperature > 85, finfr)

    @forge
    def read_sensors(self, temp, humidity):
        self.temperature = temp
        self.humidity = humidity
        self.battery -= 0.1  # Reading costs power

        if temp > 50:
            self.alerts.append(f"High temp warning: {temp}°C")

        return {"temp": temp, "humidity": humidity}

    @forge
    def transmit(self):
        self.battery -= 1.0  # Transmitting costs more power
        return "Data transmitted"
```

### Connect to Newton Server

```python
from newton_sdk import Newton

# Start server in terminal: newton serve
newton = Newton("http://localhost:8000")

# Verified calculation
result = newton.calculate({"op": "+", "args": [100, 200]})
print(result.result)  # 300 (verified!)

# Check constraint
is_valid = newton.constraint(
    {"field": "balance", "operator": "ge", "value": 0},
    {"balance": 150}
)
print(is_valid.result)  # True

# Content safety
safe = newton.verify("Hello, world!")
print(safe.verified)  # True
```

---

## Level 4: Language Design
*For those who want to extend tinyTalk.*

### Add a New Matter Type

Matter types prevent unit confusion (remember Mars Climate Orbiter?).

```python
# In tinytalk_py/matter.py

from dataclasses import dataclass
from .matter import Matter

@dataclass
class Energy(Matter):
    """Energy value. Default unit: Joules."""
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
        """Convert to kilowatt-hours."""
        if self._unit == "kWh":
            return self
        return Energy(self._value / 3600000, "kWh")

# Convenience constructors
def Joules(value: float) -> Energy:
    return Energy(value, "J")

def Kilowatts(value: float) -> Energy:
    return Energy(value * 3600000, "J")
```

### Add a New Keyword

```python
# In tinytalk_py/core.py

def unless(condition: bool, result=None):
    """
    Inverse of 'when'. Triggers if condition is FALSE.

    Usage:
        unless(balance > 0, finfr)  # Must have positive balance
    """
    return when(not condition, result)
```

### Create a Domain-Specific Blueprint

```python
# gaming_sdk.py - A gaming domain extension

from newton_sdk import Blueprint, field, law, forge, when, finfr

class GameEntity(Blueprint):
    """Base class for all game entities."""

    health = field(float, default=100.0)
    max_health = field(float, default=100.0)
    alive = field(bool, default=True)

    @law
    def health_bounds(self):
        when(self.health > self.max_health, finfr)

    @law
    def death_is_final(self):
        when(not self.alive and self.health > 0, finfr)

    @forge
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.alive = False
        return f"Took {amount} damage, health: {self.health}"

    @forge
    def heal(self, amount):
        if not self.alive:
            raise ValueError("Cannot heal dead entity")
        self.health = min(self.max_health, self.health + amount)
        return f"Healed {amount}, health: {self.health}"
```

---

## 🔧 Troubleshooting

### Common Installation Issues

#### Problem: `./setup_newton.sh: Permission denied`

**Solution:**
```bash
chmod +x setup_newton.sh
./setup_newton.sh
```

Or run directly with bash:
```bash
bash setup_newton.sh
```

#### Problem: "Python 3.9+ required. Found: 3.7"

You need Python 3.9 or higher.

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
# Use it specifically
python3.10 -m venv venv
```

**On macOS:**
```bash
# With Homebrew
brew install python@3.10

# Verify
python3 --version
```

**On Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Install with "Add to PATH" checked
3. Verify with `python --version` in PowerShell

#### Problem: "pip: command not found"

**On Ubuntu/Debian:**
```bash
sudo apt install python3-pip
```

**On macOS:**
```bash
python3 -m ensurepip --upgrade
```

#### Problem: Server won't start - "Address already in use"

Something else is using port 8000.

**Find what's using it:**
```bash
# On Mac/Linux
lsof -i :8000
sudo kill -9 <PID>

# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Or use a different port:**
```bash
# Edit newton_supercomputer.py
# Change: uvicorn.run(app, host="0.0.0.0", port=8000)
# To:     uvicorn.run(app, host="0.0.0.0", port=8001)

# Or run with environment variable
PORT=8001 python newton_supercomputer.py
```

#### Problem: "ModuleNotFoundError: No module named 'fastapi'"

Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### Problem: Tests fail with ImportError

**Solution:**
```bash
# Install in development mode
pip install -e .

# This makes Newton SDK importable from anywhere in the project
```

### Platform-Specific Issues

#### macOS: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:**
```bash
# Install certificates
/Applications/Python\ 3.10/Install\ Certificates.command

# Or use certifi
pip install --upgrade certifi
```

#### macOS: "xcrun: error: invalid active developer path"

Xcode command line tools missing.

**Solution:**
```bash
xcode-select --install
```

#### Windows: "bash: command not found"

Windows doesn't have bash by default.

**Solution Option 1: Use PowerShell**
Replace bash commands with PowerShell equivalents:
- `source venv/bin/activate` → `venv\Scripts\activate`
- `./setup_newton.sh` → Install Git Bash or use WSL

**Solution Option 2: Use WSL2 (Recommended)**
```powershell
# Install WSL2
wsl --install

# Then follow Linux instructions inside WSL
```

**Solution Option 3: Use Git Bash**
1. Install [Git for Windows](https://git-scm.com/download/win)
2. Use Git Bash terminal
3. Run `bash setup_newton.sh`

#### Linux: "permission denied" errors

**Solution:**
```bash
# Don't use sudo with pip in venv
source venv/bin/activate
pip install -r requirements.txt

# If you need system Python packages
sudo apt install python3-dev build-essential
```

### Runtime Errors

#### Problem: "LawViolation" when running code

This is **expected behavior**! Laws are constraints that prevent invalid states.

**Example:**
```python
class Account(Blueprint):
    balance = field(float, default=100)
    
    @law
    def no_negative(self):
        when(self.balance < 0, finfr)
    
    @forge
    def withdraw(self, amount):
        self.balance -= amount

acc = Account()
acc.withdraw(150)  # ✗ LawViolation: no_negative
```

**This is correct!** The law prevented an invalid state (negative balance).

#### Problem: "finfr" error - what does this mean?

**`finfr`** means "final/for" - it's an **ontological death**. The state you tried to create **cannot exist** according to your laws.

This is not a bug - it's Newton protecting you from invalid states.

**Example:**
```python
@law
def temperature_bounds(self):
    when(self.temp < -273.15, finfr)  # Can't go below absolute zero
```

If code tries to set temperature to -300, `finfr` prevents it because that state is physically impossible.

#### Problem: Server returns 500 errors

**Check server logs:**
```bash
# See full error details
python newton_supercomputer.py

# Watch for errors in the terminal
```

**Common causes:**
1. Constraint violation in request
2. Invalid JSON format
3. Missing required fields
4. Database connection (if using external DB)

**Test with minimal request:**
```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'
```

### Testing Issues

#### Problem: Tests fail with "Server not running"

**Solution:**
```bash
# Terminal 1: Start server
python newton_supercomputer.py

# Terminal 2: Run tests
python test_full_system.py
```

#### Problem: Pytest not found

**Solution:**
```bash
source venv/bin/activate
pip install pytest hypothesis
```

#### Problem: "Import could not be resolved" in VSCode

**Solution:**
1. Select Python interpreter from venv:
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Python: Select Interpreter"
   - Choose `./venv/bin/python`

2. Or add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python"
}
```

### Getting Help

Still stuck? Here's how to get help:

1. **Check the docs:**
   - [QUICKSTART.md](QUICKSTART.md) - Ultra-quick setup
   - [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) - Complete guide
   - [DEVELOPERS.md](DEVELOPERS.md) - Development setup

2. **Run diagnostics:**
```bash
# Check Python version
python3 --version

# Check pip version  
pip --version

# Check virtual env
which python  # Should show path with 'venv' in it

# List installed packages
pip list

# Test imports
python -c "import fastapi; print('FastAPI OK')"
python -c "from tinytalk_py import Blueprint; print('tinyTalk OK')"
```

3. **Open an issue:**
   - Go to [GitHub Issues](https://github.com/jaredlewiswechs/Newton-api/issues)
   - Include:
     - OS and Python version
     - Full error message
     - Steps to reproduce
     - Output of diagnostic commands above

4. **Read the source:**
   Newton is open source. The code is the ultimate documentation:
   - `newton_supercomputer.py` - Main server
   - `tinytalk_py/__init__.py` - Python SDK
   - `core/` - Core engines (CDL, Logic, Forge, Vault, Ledger)

---

## Level 5: Core Development
*For contributors to Newton itself.*

### Repository Structure

```
Newton-api/
├── setup_newton.sh       # One-command setup script
├── test_full_system.py   # Full system integration test
├── newton_supercomputer.py  # Main API server
│
├── newton_sdk/           # The installable package
│   ├── __init__.py      # Main exports
│   ├── client.py        # Newton API client
│   ├── server.py        # Server launcher
│   └── cli.py           # Command line interface
│
├── tinytalk_py/          # The tinyTalk language
│   ├── core.py          # Blueprint, Law, Forge, when, finfr
│   ├── matter.py        # Typed values (Money, Temperature, etc.)
│   ├── engine.py        # KineticEngine for motion/animation
│   ├── education.py     # Education module (TEKS, NES, PLC)
│   └── jester.py        # Code constraint translator
│
├── newton_tlm/           # Topological Language Machine (NEW)
│   ├── newton_tlm.py    # ACID-compliant symbolic kernel
│   └── tests/           # 23 passing ACID compliance tests
│
├── newton_geometry/      # Topological Constraint Framework (NEW)
│   ├── geometry.py      # Constraint manifolds
│   └── tests/           # Geometric verification tests
│
├── core/                 # Newton Supercomputer internals
│   ├── cdl.py           # Constraint Definition Language
│   ├── logic.py         # Verified computation engine
│   ├── forge.py         # Content verification
│   ├── vault.py         # Encrypted storage
│   ├── ledger.py        # Immutable audit trail
│   ├── textgen.py       # Constraint-preserving text generation
│   └── cartridges.py    # Media specification cartridges
│
├── teachers-aide/        # Teacher's Aide PWA
│   ├── index.html       # Web application
│   ├── app.js           # Frontend logic
│   └── styles.css       # Newton theme
│
├── tests/                # Test suite (580+ tests)
└── docs/                 # Documentation
```

### Running Tests

```bash
# Full system test (visual, requires running server)
python newton_supercomputer.py &
python test_full_system.py

# All unit tests
pytest tests/ -v

# Newton TLM tests (ACID compliance)
pytest newton_tlm/tests/ -v

# Newton Geometry tests
pytest newton_geometry/tests/ -v

# Specific module
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=core --cov-report=html
```

### Test Results (January 2026)

| Test Suite | Results | What It Proves |
|------------|---------|----------------|
| TLM Tests | 23/23 | ACID compliance, determinism |
| Main Suite | 558/586 | Core functionality |
| Full System | 10/10 | All components connected |

### Development Workflow

```bash
# 1. Create a branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Test
pytest tests/ -v

# 4. Install locally
pip install -e .

# 5. Test the CLI
newton demo

# 6. Commit
git add .
git commit -m "Add my feature"

# 7. Push
git push -u origin feature/my-feature
```

### Key Design Principles

1. **Determinism** - Same input → same output, always
2. **Termination** - All computations must halt
3. **Auditability** - Every operation is logged
4. **No-First** - Define constraints, not procedures

---

## Quick Reference Card

```
╭────────────────────────────────────────────────────────────────╮
│  TINYTALK QUICK REFERENCE                                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  KEYWORDS                                                      │
│    when(condition, result)    Declare a fact                   │
│    finfr                      Forbidden state (blocks action)  │
│    fin                        Soft stop (can be caught)        │
│                                                                │
│  DECORATORS                                                    │
│    @law                       Define a constraint (Layer 0)    │
│    @forge                     Define an action (Layer 1)       │
│                                                                │
│  BLUEPRINT                                                     │
│    class MyThing(Blueprint):                                   │
│        value = field(type, default=x)                          │
│                                                                │
│  MATTER TYPES                                                  │
│    Money(100)           Celsius(22)         PSI(30)            │
│    Mass(50)             Fahrenheit(72)      Liters(10)         │
│    Distance(100)        Meters(50)          Kilograms(25)      │
│                                                                │
│  CLI COMMANDS                                                  │
│    newton serve         Start the server                       │
│    newton demo          Run interactive demo                   │
│    newton calc "2+3"    Quick calculation                      │
│    newton health        Check server status                    │
│                                                                │
│  EDUCATION ENDPOINTS                                           │
│    /education/lesson    Generate NES lesson plan               │
│    /education/slides    Generate slide deck                    │
│    /education/assess    Analyze student assessments            │
│    /education/plc       Generate PLC report                    │
│    /education/teks      Browse TEKS standards                  │
│                                                                │
╰────────────────────────────────────────────────────────────────╯
```

---

## The Philosophy

```
Traditional Programming:
  "Here's what to do, step by step."
  (Then hope nothing goes wrong)

tinyTalk Programming:
  "Here's what CANNOT happen."
  (Everything else is allowed)
```

**Smalltalk gave us objects.**
**tinyTalk gives us boundaries.**

The constraint IS the instruction.
The verification IS the computation.

Welcome to Newton. 🍎

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*"1 == 1. The cloud is weather. We're building shelter."*
