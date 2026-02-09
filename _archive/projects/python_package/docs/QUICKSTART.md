# Newton Quick Start Guide

Get started with Newton in 5 minutes.

## Installation

```bash
pip install newton-computer
```

## Your First Blueprint (2 minutes)

Create a file called `first.py`:

```python
from newton import Blueprint, field, law, forge, when, finfr

class Counter(Blueprint):
    """A counter that can never go negative."""

    count = field(int, default=0)

    @law
    def must_be_positive(self):
        when(self.count < 0, finfr)

    @forge
    def increment(self):
        self.count += 1

    @forge
    def decrement(self):
        self.count -= 1


# Try it
counter = Counter()
print(f"Starting: {counter.count}")  # 0

counter.increment()
counter.increment()
print(f"After 2 increments: {counter.count}")  # 2

counter.decrement()
print(f"After decrement: {counter.count}")  # 1

counter.decrement()
print(f"After decrement: {counter.count}")  # 0

# This will be BLOCKED
try:
    counter.decrement()  # Would make count = -1
except Exception as e:
    print(f"Blocked: {e}")
    print(f"Count is still: {counter.count}")  # Still 0!
```

Run it:
```bash
python first.py
```

Output:
```
Starting: 0
After 2 increments: 2
After decrement: 1
After decrement: 0
Blocked: Law 'must_be_positive' prevents this state (finfr)
Count is still: 0
```

## Understanding the Code

### Blueprint
```python
class Counter(Blueprint):
```
`Blueprint` is the base class for all Newton objects. It automatically enforces laws before state changes.

### field()
```python
count = field(int, default=0)
```
Declare typed state. `field(type, default=value)` creates a managed field.

### @law
```python
@law
def must_be_positive(self):
    when(self.count < 0, finfr)
```
Laws define forbidden states. When the condition is true, `finfr` (finality) is triggered.

### @forge
```python
@forge
def decrement(self):
    self.count -= 1
```
Forges are mutations. Before they complete, all laws are checked. If any law triggers `finfr`, the forge is rolled back.

### finfr
"Finality" - the state *cannot* exist. Not "shouldn't", *cannot*.

## Type-Safe Units

Prevent unit confusion:

```python
from newton import Money, Mass

budget = Money(1000)
weight = Mass(50)

total = budget + Money(500)  # OK
# total = budget + weight    # TypeError! Different types
```

## The "No-First" Philosophy

| Traditional | Newton |
|-------------|--------|
| Try, then catch errors | Define what cannot happen |
| Validate after mutation | Prevent before mutation |
| Hope for the best | Guarantee the invariant |

## Next Steps

1. **Run the demo**: `newton demo`
2. **Create a project**: `newton init my_project`
3. **Read the full guide**: [TinyTalk Programming Guide](../TINYTALK_PROGRAMMING_GUIDE.md)
4. **Explore examples**: [examples/](../examples/)

## Common Patterns

### Bank Account (Classic)
```python
class BankAccount(Blueprint):
    balance = field(float, default=100.0)

    @law
    def no_overdraft(self):
        when(self.balance < 0, finfr)

    @forge
    def withdraw(self, amount):
        self.balance -= amount
```

### Bounded Value
```python
class Temperature(Blueprint):
    celsius = field(float, default=20.0)

    @law
    def not_too_cold(self):
        when(self.celsius < -273.15, finfr)  # Absolute zero

    @law
    def not_too_hot(self):
        when(self.celsius > 1000, finfr)  # Safety limit
```

### Resource Pool
```python
class ConnectionPool(Blueprint):
    available = field(int, default=10)
    in_use = field(int, default=0)

    @law
    def no_negative_available(self):
        when(self.available < 0, finfr)

    @forge
    def acquire(self):
        self.available -= 1
        self.in_use += 1

    @forge
    def release(self):
        self.available += 1
        self.in_use -= 1
```

## Getting Help

- GitHub: https://github.com/jaredlewiswechs/Newton-api
- Issues: https://github.com/jaredlewiswechs/Newton-api/issues
