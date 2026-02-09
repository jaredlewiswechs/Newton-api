# Newton Tutorials

Learn Newton step by step with these tutorials.

## Beginner Tutorials

### 1. Hello Newton
**File:** `examples/basic/01_hello_newton.py`

Your first Newton program - the classic bank account that can't overdraft. Learn the core concepts:
- Blueprint
- field()
- @law
- @forge
- finfr

### 2. Matter Types
**File:** `examples/basic/02_matter_types.py`

Prevent unit confusion with type-safe values:
- Money, Mass, Distance
- Temperature with conversions
- Why type safety matters

### 3. Thermostat
**File:** `examples/basic/03_thermostat.py`

Multiple laws working together for bounded values:
- Upper and lower bounds
- Multiple @law decorators
- Incremental changes

## Intermediate Tutorials

### 4. Trading System
**File:** `examples/intermediate/04_trading_system.py`

Real-world financial risk management:
- Position limits
- Leverage constraints
- ratio() for proportional limits

### 5. Inventory Management
**File:** `examples/intermediate/05_inventory.py`

Business logic with stock control:
- Reservation system
- Multi-field constraints
- Nested Blueprints

### 6. API Client
**File:** `examples/intermediate/06_api_client.py`

Connect to Newton servers:
- Newton client
- Verified calculations
- Constraint evaluation

## Advanced Tutorials

### 7. Kinetic Game
**File:** `examples/advanced/07_kinetic_game.py`

Game physics with the Kinetic Engine:
- Presence and Delta
- Boundary checks
- Interpolation for animation

### 8. Ratio Constraints
**File:** `examples/advanced/08_ratio_constraints.py`

Advanced f/g dimensional analysis:
- ratio() function
- finfr_if_undefined()
- Leverage and safety systems

### 9. Custom Matter Types
**File:** `examples/advanced/09_custom_matter.py`

Extend the type system:
- Creating new Matter subclasses
- Unit conversions
- Domain-specific types

## Running the Tutorials

```bash
# Clone the examples
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api/python_package/examples

# Run any tutorial
python basic/01_hello_newton.py
python intermediate/04_trading_system.py
python advanced/07_kinetic_game.py
```

## Learning Path

### Week 1: Foundations
1. Read the [Quick Start Guide](../QUICKSTART.md)
2. Complete tutorials 1-3
3. Practice creating simple Blueprints

### Week 2: Real Applications
1. Complete tutorials 4-6
2. Connect to a Newton server
3. Build a simple application

### Week 3: Advanced Topics
1. Complete tutorials 7-9
2. Create custom Matter types
3. Explore the Kinetic Engine

## Getting Help

- [API Reference](../api/TINYTALK_REFERENCE.md)
- [GitHub Issues](https://github.com/jaredlewiswechs/Newton-api/issues)
- [TinyTalk Programming Guide](https://github.com/jaredlewiswechs/Newton-api/blob/main/TINYTALK_PROGRAMMING_GUIDE.md)
