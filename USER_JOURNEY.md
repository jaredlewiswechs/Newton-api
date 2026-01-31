# Newton User Journey

**A step-by-step guide through your Newton experience.**

```
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🍎 Your Newton Journey                                     │
│                                                              │
│   From "What is this?" to "I built something!"              │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

---

## The Journey Map

```
START
  │
  ├─► 📖 Read This (5 min)
  │   Understand what Newton is
  │   
  ├─► 🚀 Install (5 min)
  │   Run ./setup_newton.sh
  │   See it work
  │   
  ├─► 🎮 Try Examples (15 min)
  │   Run demos
  │   See Newton in action
  │   
  ├─► 📚 Learn Basics (30 min)
  │   Understand laws, forges, blueprints
  │   Write your first constraint
  │   
  ├─► 🛠️ Build Something (2 hours)
  │   Create your first real blueprint
  │   Test it
  │   Deploy it
  │   
  └─► 🌟 Master Newton (ongoing)
      Advanced patterns
      Contribute back
      Share what you built
```

---

## Phase 1: Understanding (5 minutes)

### Start Here

Read [QUICKSTART.md](QUICKSTART.md) to understand:
- What Newton is
- Why it's different
- How to install it

**Key Concepts to Grasp:**
1. **Constraints first** - Define what CANNOT happen
2. **Verification before execution** - Check before doing
3. **finfr** - Ontological death (forbidden states)

**Mental Model:**
```
Traditional: "Here's how to do it" (procedural)
Newton:      "Here's what can't happen" (declarative)
```

---

## Phase 2: Installation (5 minutes)

### Quick Install

```bash
# 1. Clone
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# 2. Setup (does everything)
./setup_newton.sh

# 3. Verify
python verify_setup.py
```

### What Should Happen

```
✓ Python 3.9+
✓ pip installed
✓ Virtual environment active
✓ FastAPI installed
✓ All dependencies ready
✓ Server can start
```

**If something fails:** Jump to [Troubleshooting](GETTING_STARTED.md#-troubleshooting)

---

## Phase 3: First Taste (15 minutes)

### Start the Server

```bash
# Terminal 1
python newton_supercomputer.py
```

### Try It

```bash
# Terminal 2: Health check
curl http://localhost:8000/health

# Verify something
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'

# Calculate something
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'
```

### Run a Demo

```bash
# See a simple bank account demo
python examples/demo_bank_account.py
```

**What to notice:**
- Withdrawals are blocked BEFORE they create invalid states
- No exception handling needed
- The constraint prevents the problem

---

## Phase 4: Learn the Basics (30 minutes)

### Read the Tutorial

Open [GETTING_STARTED.md](GETTING_STARTED.md) and follow **Level 1** and **Level 2**.

### Key Lessons

#### Lesson 1: The Four Keywords

```python
when    # "This is true"
and     # "Also this"
fin     # "Stop here (soft)"
finfr   # "FORBIDDEN (hard)"
```

#### Lesson 2: Blueprint Structure

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class MyThing(Blueprint):
    # State
    value = field(int, default=0)
    
    # Constraints
    @law
    def no_negatives(self):
        when(self.value < 0, finfr)
    
    # Actions
    @forge
    def increment(self):
        self.value += 1
```

#### Lesson 3: The Three Layers

```
Layer 0: Laws (what CANNOT happen)
Layer 1: State + Actions (what CAN happen)
Layer 2: Your application (how you use it)
```

### Practice Exercise

Create a simple thermostat:

```python
class Thermostat(Blueprint):
    temperature = field(float, default=20.0)
    
    @law
    def safe_range(self):
        when(self.temperature < 0, finfr)
        when(self.temperature > 100, finfr)
    
    @forge
    def set_temp(self, temp):
        self.temperature = temp

# Try it
t = Thermostat()
t.set_temp(22)    # ✓ Works
t.set_temp(-5)    # ✗ Blocked!
t.set_temp(150)   # ✗ Blocked!
```

---

## Phase 5: Build Something (2 hours)

### Choose Your Project

Pick something you understand:

**Beginner Ideas:**
- Todo list with max items
- Counter that can't go negative
- Temperature sensor with safe bounds

**Intermediate Ideas:**
- Bank account with overdraft protection
- Inventory system with capacity limits
- API rate limiter

**Advanced Ideas:**
- Trading system with risk limits
- IoT device mesh with health checks
- Lesson planner with TEKS compliance

### Development Process

```bash
# 1. Create your blueprint file
touch my_project.py

# 2. Define your constraints FIRST
class MyProject(Blueprint):
    @law
    def my_constraint(self):
        # What CANNOT happen?
        pass

# 3. Add state and actions
    value = field(type)
    
    @forge
    def my_action(self):
        # What CAN happen?
        pass

# 4. Test it
python my_project.py

# 5. Verify constraints work
# Try to violate a law
# Should be blocked!
```

### Testing Checklist

- [ ] Can create instance
- [ ] Can call forges successfully
- [ ] Laws prevent invalid states
- [ ] Constraints tested with boundary values
- [ ] No way to create forbidden states

---

## Phase 6: Master Newton (ongoing)

### Advanced Topics

#### 1. Transaction Management

```python
from newton_tlm import NewtonTLM

tlm = NewtonTLM()
tlm.begin(instance)
# ... make changes ...
tlm.commit(instance)  # or rollback()
```

#### 2. Matter Types

```python
from tinytalk_py import Money, Celsius, Mass

price = field(Money)
temp = field(Celsius)
weight = field(Mass)
```

#### 3. Distributed Systems

```python
# Bridge: Byzantine fault tolerant consensus
# 3f+1 nodes
# PBFT algorithm
```

#### 4. Grounding (External Evidence)

```python
# Verify claims against external sources
result = newton.ground(
    claim="Paris is the capital of France",
    sources=["wikipedia", "britannica"]
)
```

#### 5. Cohen-Sutherland Clipping

```python
# Find what CAN be done when request is partially invalid
result = newton.clip(
    request="Help me with chemistry homework and make explosives"
)
# Returns: "I can help with chemistry homework"
```

### Read Advanced Docs

- [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) - Complete language
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [WHITEPAPER.md](WHITEPAPER.md) - Technical deep dive
- [DEVELOPERS.md](DEVELOPERS.md) - Contributing guide

---

## Success Milestones

Track your progress:

### Milestone 1: Setup Complete ✓
- [ ] Newton installed
- [ ] Server runs
- [ ] Tests pass
- [ ] Understand finfr

### Milestone 2: First Blueprint ✓
- [ ] Created a blueprint
- [ ] Added laws
- [ ] Added forges
- [ ] Laws work (prevent invalid states)

### Milestone 3: Real Application ✓
- [ ] Built something useful
- [ ] Tested edge cases
- [ ] Deployed it
- [ ] Someone else used it

### Milestone 4: Contributor ✓
- [ ] Found a bug
- [ ] Fixed something
- [ ] Added a feature
- [ ] Submitted PR

---

## Common Pitfalls

### Pitfall 1: Not Testing Constraints

❌ **Wrong:**
```python
@law
def no_negatives(self):
    when(self.value < 0, finfr)

# Never test if it actually prevents negatives
```

✓ **Right:**
```python
@law
def no_negatives(self):
    when(self.value < 0, finfr)

# TEST IT
def test():
    obj = MyClass()
    with pytest.raises(LawViolation):
        obj.value = -1  # Should be blocked
```

### Pitfall 2: Checking in Actions Instead of Laws

❌ **Wrong:**
```python
@forge
def withdraw(self, amount):
    if self.balance - amount < 0:
        raise ValueError("Overdraft")
    self.balance -= amount
```

✓ **Right:**
```python
@law
def no_overdraft(self):
    when(self.balance < 0, finfr)

@forge
def withdraw(self, amount):
    self.balance -= amount  # Law handles it
```

### Pitfall 3: Using Raw Numbers

❌ **Wrong:**
```python
temperature = field(float)  # Celsius? Fahrenheit? Kelvin?
```

✓ **Right:**
```python
from tinytalk_py import Celsius
temperature = field(Celsius)  # Clear units
```

---

## Next Steps by Role

### For Students/Educators
- Try the NES demos: `python examples/nes_helper_demo.py`
- Read education docs: `docs/INTRO_COURSE.md`
- Use for lesson planning

### For Developers
- Read [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md)
- Study [ARCHITECTURE.md](ARCHITECTURE.md)
- Build an API integration

### For Researchers
- Read [WHITEPAPER.md](WHITEPAPER.md)
- Study [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md)
- Explore [GLASS_BOX.md](GLASS_BOX.md)

### For Contributors
- Read [DEVELOPERS.md](DEVELOPERS.md)
- Check open issues on GitHub
- Join discussions

---

## Getting Help

### Quick Help

1. **Having issues?** → [Troubleshooting](GETTING_STARTED.md#-troubleshooting)
2. **Don't understand something?** → [QUICKSTART.md](QUICKSTART.md)
3. **Need examples?** → `examples/` directory

### Community

- **GitHub Issues:** Report bugs or ask questions
- **Discussions:** Share what you built
- **Pull Requests:** Contribute improvements

### Resources

| Resource | Best For |
|----------|----------|
| [QUICKSTART.md](QUICKSTART.md) | Absolute beginners |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Learning Newton |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understanding design |
| [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) | Language reference |
| [DEVELOPERS.md](DEVELOPERS.md) | Contributing code |

---

## Your Journey Checklist

Track what you've accomplished:

- [ ] Installed Newton
- [ ] Ran first demo
- [ ] Understood finfr
- [ ] Read QUICKSTART.md
- [ ] Created first blueprint
- [ ] Added first law
- [ ] Added first forge
- [ ] Tested constraints
- [ ] Built first app
- [ ] Deployed something
- [ ] Read ARCHITECTURE.md
- [ ] Contributed back

---

**The constraint IS the instruction.**

Now go build something impossible to break! 🍎

---

© 2025-2026 Jared Nashon Lewis · Newton · tinyTalk · Ada Computing Company
