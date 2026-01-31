# Complete Beginner's Guide to Newton

```
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   🍎 Newton for Absolute Beginners                          │
│                                                              │
│   Everything you can do with Newton                         │
│   Step-by-step examples and guides                          │
│   No prior experience needed!                               │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

**Welcome to Newton!** This guide will teach you everything Newton can do, with complete step-by-step examples. By the end, you'll be able to build verified applications that are impossible to break.

---

## Table of Contents

1. [What is Newton?](#what-is-newton)
2. [Installation](#installation)
3. [Your First Steps](#your-first-steps)
4. [Core Concepts](#core-concepts)
5. [Everything You Can Do with Newton](#everything-you-can-do-with-newton)
6. [Step-by-Step Tutorials](#step-by-step-tutorials)
7. [Complete Example Applications](#complete-example-applications)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## What is Newton?

Newton is a **verified computation system** where:
- **The constraint IS the instruction** - You define what CANNOT happen, not what can
- **The verification IS the computation** - Every operation is verified before execution
- **The network IS the processor** - Distributed verification across nodes

### Why Newton is Different

**Traditional Programming:**
```python
# Hope it works, check after
balance = 100
balance -= 150  # Oops, now it's -50!
if balance < 0:
    raise Error("Overdraft!")  # Too late!
```

**Newton Programming:**
```python
# Define what CANNOT happen, enforce BEFORE
class Account(Blueprint):
    balance = field(float, default=100)
    
    @law  # This state is FORBIDDEN
    def no_overdraft(self):
        when(self.balance < 0, finfr)
    
    @forge
    def withdraw(self, amount):
        self.balance -= amount  # Checked BEFORE it happens!
```

Newton stops invalid states **before they exist**, not after.

### What Can You Build?

- ✅ Financial systems (no overdrafts, no insolvency)
- ✅ Educational tools (TEKS-aligned lesson plans, grading)
- ✅ IoT systems (sensor bounds, battery management)
- ✅ Healthcare apps (privacy-first, HIPAA compliance)
- ✅ Trading systems (risk limits, margin requirements)
- ✅ Any application where **correctness matters**

---

## Installation

### Prerequisites

- **Python 3.9 or higher** (check with `python3 --version`)
- **10 minutes** of your time
- **Internet connection** (for downloading packages)

That's it! No database, no Docker, no cloud account needed.

### Option 1: One-Command Setup (Recommended)

**On Mac/Linux:**
```bash
# 1. Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# 2. Run the setup script
chmod +x setup_newton.sh
./setup_newton.sh
```

**On Windows:**
```powershell
# 1. Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# 2. Run with Git Bash (or use manual setup below)
bash setup_newton.sh
```

### Option 2: Manual Setup (All Platforms)

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install Newton
pip install -e .

# 4. Verify installation
python verify_setup.py
```

### Verify It Works

```bash
# Start the server
python newton_supercomputer.py
```

You should see:
```
INFO: Started server process
INFO: Uvicorn running on http://127.0.0.1:8000
```

**✅ Success!** Newton is now running.

---

## Your First Steps

Let's verify Newton is working by trying some simple commands.

### Step 1: Check Health

**Open a new terminal** (keep the server running) and run:

```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "ok",
  "timestamp": "2026-01-31T20:40:12.012Z",
  "version": "1.3.0"
}
```

### Step 2: Verify Content

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!"}'
```

**Expected Output:**
```json
{
  "verified": true,
  "elapsed_us": 1250,
  "safe": true
}
```

### Step 3: Calculate Something

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'
```

**Expected Output:**
```json
{
  "result": 5,
  "verified": true,
  "elapsed_us": 250
}
```

**🎉 All three work?** You're ready to learn!

---

## Core Concepts

Before diving into examples, let's understand Newton's core concepts.

### 1. Blueprints

A **Blueprint** is like a class, but with laws (constraints).

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Thermostat(Blueprint):
    temperature = field(float, default=20.0)
```

### 2. Laws (Layer 0 - Governance)

**Laws** define what CANNOT happen. They are checked BEFORE any action.

```python
@law
def no_freezing(self):
    when(self.temperature < 0, finfr)  # Can't go below 0°C
```

### 3. Forges (Layer 1 - Executive)

**Forges** are actions that can modify state. Laws are checked before execution.

```python
@forge
def set_temp(self, new_temp):
    self.temperature = new_temp
    return f"Temperature set to {new_temp}°C"
```

### 4. The Four Keywords

| Keyword | Meaning | Usage |
|---------|---------|-------|
| `when` | "If this is true" | `when(condition, result)` |
| `finfr` | "Forbidden state" | `when(balance < 0, finfr)` |
| `fin` | "Soft stop" | Can be caught/reopened |
| `and` | "Also this" | Combine conditions |

### 5. The Three Layers

```
╭─────────────────────────────────────────────────────╮
│  Layer 2: APPLICATION                               │
│  Your specific use case                             │
├─────────────────────────────────────────────────────┤
│  Layer 1: EXECUTIVE                                 │
│  Fields (state) + Forges (actions)                  │
├─────────────────────────────────────────────────────┤
│  Layer 0: GOVERNANCE                                │
│  Laws - What CANNOT happen. Ever. finfr.            │
╰─────────────────────────────────────────────────────╯
```

---

## Everything You Can Do with Newton

Here's a complete list of Newton's capabilities with examples.

### 1. Content Verification

Verify that content is safe and appropriate.

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "This is safe content"}'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/verify",
    json={"input": "Is this content safe?"}
)
print(response.json()["verified"])  # True
```

### 2. Verified Computation

Perform calculations with guaranteed correctness and bounded execution.

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [10, 20]}}'
```

**Available Operations:**
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**` (power)
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Logic: `and`, `or`, `not`
- Control: `if`, `for`, `while`
- Functions: `sum`, `min`, `max`, `abs`

**Example - Conditional:**
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "if", "args": [{"op": ">", "args": [10, 5]}, "greater", "smaller"]}}'
```

**Example - Loop:**
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "for", "args": ["i", 1, 5, {"op": "*", "args": [{"var": "i"}, 2]}]}}'
# Result: [2, 4, 6, 8, 10]
```

### 3. Constraint Checking (CDL)

Check if data satisfies constraints using Constraint Definition Language.

```bash
curl -X POST http://localhost:8000/constraint \
  -H "Content-Type: application/json" \
  -d '{
    "constraint": {"field": "age", "operator": "ge", "value": 18},
    "data": {"age": 25}
  }'
```

**Available Operators:**
- **Comparison:** `eq`, `ne`, `lt`, `gt`, `le`, `ge`
- **String:** `contains`, `matches` (regex), `startswith`, `endswith`
- **Set:** `in`, `not_in`
- **Existence:** `exists`, `empty`
- **Temporal:** `within`, `after`, `before`
- **Aggregation:** `sum_lt`, `count_gt`, `avg_le`, etc.

**Example - Complex Constraint:**
```bash
curl -X POST http://localhost:8000/constraint \
  -H "Content-Type: application/json" \
  -d '{
    "constraint": {
      "field": "email",
      "operator": "matches",
      "value": "^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$"
    },
    "data": {"email": "user@example.com"}
  }'
```

### 4. Batch Verification

Verify multiple items at once for efficiency.

```bash
curl -X POST http://localhost:8000/verify/batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      "First text to verify",
      "Second text to verify",
      "Third text to verify"
    ]
  }'
```

### 5. Ground Claims in Evidence

Ground claims in external evidence (web search, documents).

```bash
curl -X POST http://localhost:8000/ground \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "The Eiffel Tower is in Paris",
    "max_results": 3
  }'
```

**Response:**
```json
{
  "grounded": true,
  "confidence": 0.95,
  "sources": [
    {"url": "https://...", "snippet": "..."}
  ]
}
```

### 6. Encrypted Storage (Vault)

Store and retrieve encrypted data securely.

**Store Data:**
```bash
curl -X POST http://localhost:8000/vault/store \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my-secret",
    "value": "sensitive data",
    "identity": "user123"
  }'
```

**Retrieve Data:**
```bash
curl -X POST http://localhost:8000/vault/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my-secret",
    "identity": "user123"
  }'
```

**Features:**
- AES-256-GCM encryption
- Identity-derived keys
- Automatic expiration (configurable)
- Tamper-evident

### 7. Immutable Audit Trail (Ledger)

Every operation is recorded in an immutable ledger.

**View Ledger:**
```bash
curl http://localhost:8000/ledger
```

**Get Specific Entry with Merkle Proof:**
```bash
curl http://localhost:8000/ledger/5
```

**Export Verification Certificate:**
```bash
curl http://localhost:8000/ledger/certificate/5
```

### 8. Robust Statistics

Adversarial-resistant statistics using MAD (Median Absolute Deviation).

```bash
curl -X POST http://localhost:8000/statistics \
  -H "Content-Type: application/json" \
  -d '{
    "data": [10, 12, 11, 10, 100, 11, 12],
    "baseline": 10.5
  }'
```

**Response:**
```json
{
  "mad": 1.0,
  "median": 11.0,
  "modified_z_scores": [...],
  "outliers": [100],
  "threshold": 10.5
}
```

**Use Cases:**
- Detecting anomalies
- Adversarial-resistant grading
- Fraud detection
- Sensor validation

### 9. Education Features

Newton includes powerful education tools for teachers.

#### Generate TEKS-Aligned Lesson Plan

```bash
curl -X POST http://localhost:8000/education/lesson \
  -H "Content-Type: application/json" \
  -d '{
    "grade": 5,
    "subject": "math",
    "teks_codes": ["5.3A"],
    "topic": "Adding Fractions with Unlike Denominators",
    "duration": 45,
    "accommodations": ["ell", "gt"]
  }'
```

#### Generate PLC Report

```bash
curl -X POST http://localhost:8000/education/plc \
  -H "Content-Type: application/json" \
  -d '{
    "campus": "Example Elementary",
    "grade": 5,
    "subject": "math",
    "scores": [85, 72, 90, 65, 88, 45, 92, 78, 80, 95],
    "teks_codes": ["5.3A", "5.3B"]
  }'
```

#### Browse TEKS Standards

```bash
curl http://localhost:8000/education/teks?grade=5&subject=math
```

#### Teacher's Aide Features

Newton includes a complete Teacher's Aide system:
- Student progress tracking
- Grade book management
- Intervention planning
- Accommodation tracking
- Assessment analysis

Access at: http://localhost:8000/teachers

### 10. Cartridge System

Newton's cartridge system provides specification-based media generation.

#### Visual Cartridge (Images)

```bash
curl -X POST http://localhost:8000/cartridge/visual \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "width": 800,
      "height": 600,
      "background": "#FFFFFF",
      "elements": [
        {"type": "circle", "x": 400, "y": 300, "radius": 50, "fill": "#FF0000"}
      ]
    }
  }'
```

#### Sound Cartridge (Audio)

```bash
curl -X POST http://localhost:8000/cartridge/sound \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "frequency": 440,
      "duration": 1.0,
      "waveform": "sine"
    }
  }'
```

#### Sequence Cartridge (Animations)

```bash
curl -X POST http://localhost:8000/cartridge/sequence \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "frames": [
        {"x": 0, "y": 0},
        {"x": 100, "y": 0},
        {"x": 100, "y": 100}
      ],
      "fps": 30
    }
  }'
```

### 11. Interface Builder

Build user interfaces programmatically.

```bash
curl -X POST http://localhost:8000/interface/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "form",
    "layout": "vertical",
    "components": [
      {"type": "text_input", "label": "Name", "required": true},
      {"type": "email_input", "label": "Email"},
      {"type": "button", "label": "Submit", "style": "primary"}
    ]
  }'
```

**Interface Types:**
- Forms
- Dashboards
- Cards
- Lists
- Navigation

### 12. Policy Engine (Glass Box)

Define and enforce policies with full transparency.

```bash
curl -X POST http://localhost:8000/policy/define \
  -H "Content-Type: application/json" \
  -d '{
    "type": "rate_limit",
    "action": "allow",
    "parameters": {
      "max_requests": 100,
      "window": "1h"
    }
  }'
```

### 13. Chatbot Compiler

Compile chatbot specifications into executable bots.

```bash
curl -X POST http://localhost:8000/chatbot/compile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SupportBot",
    "personality": "helpful",
    "constraints": [
      "Never provide medical advice",
      "Always ask for clarification"
    ]
  }'
```

### 14. Code Constraint Analysis (Jester)

Analyze code to extract and verify constraints.

```bash
curl -X POST http://localhost:8000/jester/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def withdraw(balance, amount):\n    if balance - amount < 0:\n        raise ValueError(\"Insufficient funds\")\n    return balance - amount"
  }'
```

### 15. Voice Interface

Process voice commands and generate responses.

```bash
curl -X POST http://localhost:8000/voice/process \
  -H "Content-Type: application/json" \
  -d '{
    "command": "What is the weather today?",
    "context": {"location": "Houston"}
  }'
```

---

## Step-by-Step Tutorials

### Tutorial 1: Your First Blueprint

Let's create a simple thermostat that enforces temperature bounds.

**Step 1: Create the file**

Create a file called `my_thermostat.py`:

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class Thermostat(Blueprint):
    """A thermostat that enforces safe temperature bounds."""
    
    # Field - the state
    temperature = field(float, default=20.0)
    
    # Law - what CANNOT happen
    @law
    def safe_range(self):
        # Can't freeze (below 0°C)
        when(self.temperature < 0, finfr)
        # Can't boil (above 100°C)
        when(self.temperature > 100, finfr)
    
    # Forge - what CAN happen
    @forge
    def set_temperature(self, new_temp):
        self.temperature = new_temp
        return f"Temperature set to {new_temp}°C"
```

**Step 2: Use it**

```python
# Create a thermostat
thermo = Thermostat()
print(f"Initial: {thermo.temperature}°C")

# Set valid temperature
result = thermo.set_temperature(22)
print(result)  # "Temperature set to 22°C"

# Try to freeze (will be blocked!)
try:
    thermo.set_temperature(-10)
except Exception as e:
    print(f"Blocked: {e}")  # LawViolation: safe_range

# Try to boil (will be blocked!)
try:
    thermo.set_temperature(150)
except Exception as e:
    print(f"Blocked: {e}")  # LawViolation: safe_range
```

**Step 3: Run it**

```bash
python my_thermostat.py
```

**Expected Output:**
```
Initial: 20.0°C
Temperature set to 22°C
Blocked: LawViolation: safe_range
Blocked: LawViolation: safe_range
```

**🎉 You just built your first verified component!**

### Tutorial 2: Bank Account with No Overdrafts

Let's build a bank account that prevents overdrafts.

**Step 1: Create `my_bank.py`**

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class BankAccount(Blueprint):
    """A bank account that prevents overdrafts."""
    
    balance = field(float, default=0.0)
    transactions = field(list, default=[])
    
    @law
    def no_overdraft(self):
        """Balance can never go negative."""
        when(self.balance < 0, finfr)
    
    @forge
    def deposit(self, amount):
        """Deposit money."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.transactions.append(f"Deposit: +${amount}")
        return f"Deposited ${amount}. New balance: ${self.balance}"
    
    @forge
    def withdraw(self, amount):
        """Withdraw money (prevented if would overdraft)."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance -= amount
        self.transactions.append(f"Withdrawal: -${amount}")
        return f"Withdrew ${amount}. New balance: ${self.balance}"
    
    @forge
    def get_statement(self):
        """Get account statement."""
        return {
            "balance": self.balance,
            "transactions": self.transactions
        }
```

**Step 2: Use it**

```python
# Create account
account = BankAccount()

# Deposit money
print(account.deposit(100))  # ✓ "Deposited $100. New balance: $100"
print(account.deposit(50))   # ✓ "Deposited $50. New balance: $150"

# Withdraw (valid)
print(account.withdraw(30))  # ✓ "Withdrew $30. New balance: $120"

# Try to overdraft (blocked!)
try:
    account.withdraw(150)    # ✗ Would make balance -$30
except Exception as e:
    print(f"Prevented: {e}")

# Get statement
statement = account.get_statement()
print(f"Final balance: ${statement['balance']}")
print("Transactions:")
for tx in statement['transactions']:
    print(f"  {tx}")
```

**Step 3: Run it**

```bash
python my_bank.py
```

**Expected Output:**
```
Deposited $100. New balance: $100
Deposited $50. New balance: $150
Withdrew $30. New balance: $120
Prevented: LawViolation: no_overdraft
Final balance: $120
Transactions:
  Deposit: +$100
  Deposit: +$50
  Withdrawal: -$30
```

### Tutorial 3: IoT Sensor with Safety Bounds

Let's create an IoT sensor that enforces operating bounds.

**Step 1: Create `my_sensor.py`**

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime

class TemperatureSensor(Blueprint):
    """IoT temperature sensor with safety bounds."""
    
    temperature = field(float, default=25.0)
    humidity = field(float, default=50.0)
    battery = field(float, default=100.0)
    readings = field(list, default=[])
    alerts = field(list, default=[])
    
    # === LAWS (What CANNOT happen) ===
    
    @law
    def operating_range(self):
        """Sensor operating range: -40°C to 85°C."""
        when(self.temperature < -40, finfr)
        when(self.temperature > 85, finfr)
    
    @law
    def humidity_range(self):
        """Humidity range: 0% to 100%."""
        when(self.humidity < 0, finfr)
        when(self.humidity > 100, finfr)
    
    @law
    def battery_critical(self):
        """Battery can't go below 5%."""
        when(self.battery < 5.0, finfr)
    
    # === FORGES (What CAN happen) ===
    
    @forge
    def read_sensors(self, temp, humidity):
        """Take a sensor reading."""
        # Update values
        self.temperature = temp
        self.humidity = humidity
        self.battery -= 0.1  # Reading costs power
        
        # Record reading
        reading = {
            "timestamp": datetime.now().isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "battery": self.battery
        }
        self.readings.append(reading)
        
        # Check for alerts
        if temp > 50:
            alert = f"HIGH TEMP: {temp}°C"
            self.alerts.append(alert)
            return {"status": "warning", "alert": alert, **reading}
        
        if self.battery < 20:
            alert = f"LOW BATTERY: {self.battery}%"
            self.alerts.append(alert)
            return {"status": "warning", "alert": alert, **reading}
        
        return {"status": "ok", **reading}
    
    @forge
    def transmit(self):
        """Transmit data (uses more power)."""
        self.battery -= 1.0
        return {
            "transmitted": len(self.readings),
            "battery_remaining": self.battery
        }
    
    @forge
    def get_summary(self):
        """Get sensor summary."""
        return {
            "current_temp": self.temperature,
            "current_humidity": self.humidity,
            "battery": self.battery,
            "total_readings": len(self.readings),
            "alerts": self.alerts
        }
```

**Step 2: Use it**

```python
# Create sensor
sensor = TemperatureSensor()

# Take readings
print("Reading 1:", sensor.read_sensors(22.5, 45.0))
print("Reading 2:", sensor.read_sensors(28.0, 52.0))
print("Reading 3:", sensor.read_sensors(55.0, 60.0))  # High temp alert!

# Transmit data
print("Transmit:", sensor.transmit())

# Try invalid reading (will be blocked!)
try:
    sensor.read_sensors(-50, 30)  # Below operating range
except Exception as e:
    print(f"Blocked: {e}")

# Get summary
summary = sensor.get_summary()
print(f"\nSummary:")
print(f"  Temperature: {summary['current_temp']}°C")
print(f"  Humidity: {summary['current_humidity']}%")
print(f"  Battery: {summary['battery']}%")
print(f"  Readings: {summary['total_readings']}")
print(f"  Alerts: {summary['alerts']}")
```

**Step 3: Run it**

```bash
python my_sensor.py
```

### Tutorial 4: Using the REST API

Let's build a Python client that uses Newton's REST API.

**Step 1: Create `newton_client.py`**

```python
import requests
import json

class NewtonClient:
    """Simple Newton API client."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health(self):
        """Check server health."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def verify(self, text):
        """Verify content."""
        response = requests.post(
            f"{self.base_url}/verify",
            json={"input": text}
        )
        return response.json()
    
    def calculate(self, expression):
        """Perform verified calculation."""
        response = requests.post(
            f"{self.base_url}/calculate",
            json={"expression": expression}
        )
        return response.json()
    
    def check_constraint(self, constraint, data):
        """Check if data satisfies constraint."""
        response = requests.post(
            f"{self.base_url}/constraint",
            json={"constraint": constraint, "data": data}
        )
        return response.json()
    
    def vault_store(self, key, value, identity):
        """Store encrypted data."""
        response = requests.post(
            f"{self.base_url}/vault/store",
            json={"key": key, "value": value, "identity": identity}
        )
        return response.json()
    
    def vault_retrieve(self, key, identity):
        """Retrieve encrypted data."""
        response = requests.post(
            f"{self.base_url}/vault/retrieve",
            json={"key": key, "identity": identity}
        )
        return response.json()
    
    def statistics(self, data, baseline=None):
        """Compute robust statistics."""
        payload = {"data": data}
        if baseline is not None:
            payload["baseline"] = baseline
        response = requests.post(
            f"{self.base_url}/statistics",
            json=payload
        )
        return response.json()


# Example usage
if __name__ == "__main__":
    newton = NewtonClient()
    
    # 1. Health check
    print("1. Health Check:")
    print(newton.health())
    print()
    
    # 2. Verify content
    print("2. Verify Content:")
    result = newton.verify("This is a test message")
    print(f"Verified: {result['verified']}")
    print()
    
    # 3. Calculate
    print("3. Calculate 10 + 20:")
    result = newton.calculate({"op": "+", "args": [10, 20]})
    print(f"Result: {result['result']}")
    print()
    
    # 4. Check constraint
    print("4. Check age >= 18:")
    result = newton.check_constraint(
        constraint={"field": "age", "operator": "ge", "value": 18},
        data={"age": 25}
    )
    print(f"Satisfies: {result['result']}")
    print()
    
    # 5. Vault operations
    print("5. Vault - Store and Retrieve:")
    newton.vault_store("my-secret", "sensitive data", "user123")
    result = newton.vault_retrieve("my-secret", "user123")
    print(f"Retrieved: {result['value']}")
    print()
    
    # 6. Statistics
    print("6. Robust Statistics:")
    result = newton.statistics([10, 12, 11, 10, 100, 11, 12])
    print(f"Median: {result['median']}")
    print(f"MAD: {result['mad']}")
    print(f"Outliers: {result['outliers']}")
```

**Step 2: Run it**

```bash
# Make sure Newton server is running!
python newton_supercomputer.py &

# Run the client
python newton_client.py
```

### Tutorial 5: Building a Grade Book System

Let's build a complete grade book system for teachers.

**Step 1: Create `gradebook.py`**

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class GradeBook(Blueprint):
    """A grade book system with validation."""
    
    students = field(dict, default={})
    assignments = field(list, default=[])
    
    # === LAWS ===
    
    @law
    def valid_grades(self):
        """All grades must be 0-100."""
        for student_id, grades in self.students.items():
            for grade in grades.values():
                when(grade < 0, finfr)
                when(grade > 100, finfr)
    
    # === FORGES ===
    
    @forge
    def add_student(self, student_id, name):
        """Add a new student."""
        if student_id in self.students:
            raise ValueError(f"Student {student_id} already exists")
        self.students[student_id] = {
            "name": name,
            "grades": {}
        }
        return f"Added student: {name}"
    
    @forge
    def add_assignment(self, assignment_name, max_points=100):
        """Add a new assignment."""
        if assignment_name in self.assignments:
            raise ValueError(f"Assignment {assignment_name} already exists")
        self.assignments.append({
            "name": assignment_name,
            "max_points": max_points
        })
        return f"Added assignment: {assignment_name}"
    
    @forge
    def record_grade(self, student_id, assignment_name, grade):
        """Record a grade."""
        if student_id not in self.students:
            raise ValueError(f"Student {student_id} not found")
        if assignment_name not in [a["name"] for a in self.assignments]:
            raise ValueError(f"Assignment {assignment_name} not found")
        
        self.students[student_id]["grades"][assignment_name] = grade
        return f"Recorded {grade} for {self.students[student_id]['name']} on {assignment_name}"
    
    @forge
    def get_student_average(self, student_id):
        """Calculate student's average."""
        if student_id not in self.students:
            raise ValueError(f"Student {student_id} not found")
        
        grades = list(self.students[student_id]["grades"].values())
        if not grades:
            return 0.0
        return sum(grades) / len(grades)
    
    @forge
    def get_class_report(self):
        """Generate class report."""
        report = []
        for student_id, data in self.students.items():
            avg = self.get_student_average(student_id)
            report.append({
                "id": student_id,
                "name": data["name"],
                "average": avg,
                "assignments_completed": len(data["grades"])
            })
        return sorted(report, key=lambda x: x["average"], reverse=True)


# Example usage
if __name__ == "__main__":
    # Create grade book
    gradebook = GradeBook()
    
    # Add students
    gradebook.add_student("001", "Alice Johnson")
    gradebook.add_student("002", "Bob Smith")
    gradebook.add_student("003", "Carol Davis")
    
    # Add assignments
    gradebook.add_assignment("Quiz 1")
    gradebook.add_assignment("Homework 1")
    gradebook.add_assignment("Midterm Exam")
    
    # Record grades
    gradebook.record_grade("001", "Quiz 1", 95)
    gradebook.record_grade("001", "Homework 1", 88)
    gradebook.record_grade("001", "Midterm Exam", 92)
    
    gradebook.record_grade("002", "Quiz 1", 78)
    gradebook.record_grade("002", "Homework 1", 85)
    gradebook.record_grade("002", "Midterm Exam", 80)
    
    gradebook.record_grade("003", "Quiz 1", 100)
    gradebook.record_grade("003", "Homework 1", 95)
    gradebook.record_grade("003", "Midterm Exam", 98)
    
    # Try invalid grade (will be blocked!)
    try:
        gradebook.record_grade("001", "Quiz 1", 150)
    except Exception as e:
        print(f"Blocked: {e}")
    
    # Generate report
    print("\nClass Report:")
    print(f"{'Rank':<6} {'Name':<15} {'Average':<8} {'Completed'}")
    print("-" * 45)
    for i, student in enumerate(gradebook.get_class_report(), 1):
        print(f"{i:<6} {student['name']:<15} {student['average']:<8.1f} {student['assignments_completed']}")
```

**Step 2: Run it**

```bash
python gradebook.py
```

---

## Complete Example Applications

### Example 1: Trading Account with Margin Limits

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class TradingAccount(Blueprint):
    """Trading account with risk management."""
    
    cash = field(float, default=10000.0)
    positions = field(dict, default={})
    margin_used = field(float, default=0.0)
    
    @law
    def no_negative_cash(self):
        when(self.cash < 0, finfr)
    
    @law
    def margin_limit(self):
        """Can't exceed 50% margin."""
        when(self.margin_used > self.cash * 0.5, finfr)
    
    @forge
    def buy(self, symbol, quantity, price):
        cost = quantity * price
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        return f"Bought {quantity} {symbol} @ ${price}"
    
    @forge
    def sell(self, symbol, quantity, price):
        if self.positions.get(symbol, 0) < quantity:
            raise ValueError("Not enough shares")
        revenue = quantity * price
        self.cash += revenue
        self.positions[symbol] -= quantity
        return f"Sold {quantity} {symbol} @ ${price}"
    
    @forge
    def get_portfolio_value(self, prices):
        """Calculate total portfolio value."""
        stock_value = sum(
            self.positions.get(symbol, 0) * prices.get(symbol, 0)
            for symbol in self.positions
        )
        return self.cash + stock_value


# Usage
account = TradingAccount()
print(account.buy("AAPL", 10, 150))  # Buy 10 shares at $150
print(account.buy("GOOGL", 5, 2800))  # Buy 5 shares at $2800
print(account.sell("AAPL", 5, 160))   # Sell 5 shares at $160

portfolio_value = account.get_portfolio_value({
    "AAPL": 160,
    "GOOGL": 2850
})
print(f"Portfolio value: ${portfolio_value}")
```

### Example 2: Healthcare Patient Record

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr
from datetime import datetime

class PatientRecord(Blueprint):
    """HIPAA-compliant patient record."""
    
    patient_id = field(str, default="")
    name = field(str, default="")
    vitals = field(dict, default={})
    medications = field(list, default=[])
    access_log = field(list, default=[])
    
    @law
    def vital_bounds(self):
        """Vital signs must be within plausible ranges."""
        if "heart_rate" in self.vitals:
            hr = self.vitals["heart_rate"]
            when(hr < 30, finfr)   # Too low
            when(hr > 250, finfr)  # Too high
        
        if "blood_pressure_systolic" in self.vitals:
            bp = self.vitals["blood_pressure_systolic"]
            when(bp < 50, finfr)
            when(bp > 250, finfr)
        
        if "temperature" in self.vitals:
            temp = self.vitals["temperature"]
            when(temp < 32.0, finfr)  # Hypothermia
            when(temp > 43.0, finfr)  # Hyperthermia
    
    @forge
    def update_vitals(self, provider_id, **vitals):
        """Update vital signs."""
        self.vitals.update(vitals)
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider_id,
            "action": "update_vitals",
            "data": vitals
        })
        return "Vitals updated"
    
    @forge
    def add_medication(self, provider_id, medication, dosage):
        """Add medication."""
        self.medications.append({
            "name": medication,
            "dosage": dosage,
            "prescribed_at": datetime.now().isoformat(),
            "prescribed_by": provider_id
        })
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider_id,
            "action": "prescribe_medication",
            "medication": medication
        })
        return f"Prescribed {medication}"
    
    @forge
    def get_access_log(self):
        """Get HIPAA audit trail."""
        return self.access_log


# Usage
patient = PatientRecord()
patient.patient_id = "P12345"
patient.name = "John Doe"

# Update vitals
patient.update_vitals(
    "DR001",
    heart_rate=72,
    blood_pressure_systolic=120,
    blood_pressure_diastolic=80,
    temperature=37.0
)

# Prescribe medication
patient.add_medication("DR001", "Aspirin", "81mg daily")

# Try invalid vitals (will be blocked!)
try:
    patient.update_vitals("DR001", heart_rate=300)
except Exception as e:
    print(f"Blocked: {e}")

# Get audit log
print("Access Log:")
for entry in patient.get_access_log():
    print(f"  {entry['timestamp']} - {entry['provider']}: {entry['action']}")
```

### Example 3: Smart Home Automation

```python
from tinytalk_py import Blueprint, field, law, forge, when, finfr

class SmartHome(Blueprint):
    """Smart home automation with safety constraints."""
    
    temperature = field(float, default=20.0)
    lights = field(dict, default={})
    doors = field(dict, default={})
    security_armed = field(bool, default=False)
    
    @law
    def comfort_range(self):
        """Temperature comfort range."""
        when(self.temperature < 15, finfr)
        when(self.temperature > 30, finfr)
    
    @law
    def security_lockdown(self):
        """When armed, all doors must be locked."""
        if self.security_armed:
            for door, status in self.doors.items():
                when(status == "unlocked", finfr)
    
    @forge
    def set_temperature(self, temp):
        """Set thermostat."""
        self.temperature = temp
        return f"Temperature set to {temp}°C"
    
    @forge
    def set_light(self, room, brightness):
        """Control lights (0-100)."""
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be 0-100")
        self.lights[room] = brightness
        return f"{room} light set to {brightness}%"
    
    @forge
    def lock_door(self, door):
        """Lock a door."""
        self.doors[door] = "locked"
        return f"{door} locked"
    
    @forge
    def unlock_door(self, door):
        """Unlock a door (only if not armed)."""
        if self.security_armed:
            raise ValueError("Cannot unlock door while security is armed")
        self.doors[door] = "unlocked"
        return f"{door} unlocked"
    
    @forge
    def arm_security(self):
        """Arm security system (all doors must be locked)."""
        # Lock all doors first
        for door in self.doors:
            self.doors[door] = "locked"
        self.security_armed = True
        return "Security armed"
    
    @forge
    def disarm_security(self):
        """Disarm security system."""
        self.security_armed = False
        return "Security disarmed"
    
    @forge
    def evening_mode(self):
        """Evening routine."""
        self.set_temperature(21)
        self.set_light("living_room", 70)
        self.set_light("bedroom", 30)
        return "Evening mode activated"


# Usage
home = SmartHome()

# Initialize doors
home.doors = {"front": "unlocked", "back": "unlocked", "garage": "locked"}

# Set up lights
home.set_light("living_room", 100)
home.set_light("bedroom", 0)

# Lock doors
home.lock_door("front")
home.lock_door("back")

# Arm security
print(home.arm_security())

# Try to unlock door while armed (will be blocked!)
try:
    home.unlock_door("front")
except Exception as e:
    print(f"Blocked: {e}")

# Evening mode
home.disarm_security()
print(home.evening_mode())
```

---

## Troubleshooting

### Installation Issues

#### "Python 3.9+ required"

**Solution:** Install Python 3.9 or higher.

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

**macOS:**
```bash
brew install python@3.10
```

**Windows:**
Download from https://www.python.org/downloads/

#### "pip: command not found"

**Ubuntu/Debian:**
```bash
sudo apt install python3-pip
```

**macOS:**
```bash
python3 -m ensurepip --upgrade
```

#### "./setup_newton.sh: Permission denied"

**Solution:**
```bash
chmod +x setup_newton.sh
./setup_newton.sh
```

Or run directly:
```bash
bash setup_newton.sh
```

### Server Issues

#### "Address already in use" (Port 8000)

Something else is using port 8000.

**Find and kill the process:**

**Mac/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Or use a different port:**
```bash
PORT=8001 python newton_supercomputer.py
```

#### "ModuleNotFoundError: No module named 'fastapi'"

Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Runtime Issues

#### "LawViolation" errors

This is **expected behavior!** Laws prevent invalid states.

**Example:**
```python
@law
def no_overdraft(self):
    when(self.balance < 0, finfr)
```

If code tries to make balance negative, `finfr` blocks it. This is correct!

#### Understanding "finfr"

**`finfr`** means "final/for" - it's an **ontological death**. The state you tried to create **cannot exist** according to your laws.

This is not a bug - it's Newton protecting you.

#### Server returns 500 errors

**Check server logs:**
```bash
python newton_supercomputer.py
# Watch for errors in the terminal
```

**Common causes:**
1. Invalid constraint in request
2. Malformed JSON
3. Missing required fields

**Test with minimal request:**
```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "test"}'
```

### Testing Issues

#### "Server not running" when testing

**Solution:**
```bash
# Terminal 1: Start server
python newton_supercomputer.py

# Terminal 2: Run tests
python test_full_system.py
```

#### Pytest not found

**Solution:**
```bash
source venv/bin/activate
pip install pytest hypothesis
```

### Platform-Specific Issues

#### macOS: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:**
```bash
/Applications/Python\ 3.10/Install\ Certificates.command
```

#### macOS: "xcrun: error: invalid active developer path"

**Solution:**
```bash
xcode-select --install
```

#### Windows: "bash: command not found"

**Solution:** Use PowerShell or install WSL2:

**Option 1: PowerShell equivalents**
- `source venv/bin/activate` → `venv\Scripts\activate`
- Use PowerShell for all commands

**Option 2: Install WSL2**
```powershell
wsl --install
```

Then use Linux commands inside WSL.

#### Linux: Permission errors

**Solution:**
```bash
# Don't use sudo with pip in venv
source venv/bin/activate
pip install -r requirements.txt

# If you need system packages
sudo apt install python3-dev build-essential
```

### Getting Help

Still stuck? Here's how to get help:

1. **Check the docs:**
   - [QUICKSTART.md](QUICKSTART.md) - Quick setup
   - [GETTING_STARTED.md](GETTING_STARTED.md) - Complete tutorial
   - [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) - Language guide

2. **Run diagnostics:**
```bash
python verify_setup.py
```

3. **Check Python version:**
```bash
python3 --version  # Should be 3.9+
pip --version
which python       # Should show venv path
```

4. **Open an issue:**
   Go to https://github.com/jaredlewiswechs/Newton-api/issues
   Include:
   - OS and Python version
   - Full error message
   - Steps to reproduce

---

## Next Steps

### Continue Learning

1. **Read the Philosophy:**
   - [TINYTALK_BIBLE.md](TINYTALK_BIBLE.md) - The "No-First" philosophy
   - [WHITEPAPER.md](WHITEPAPER.md) - Technical foundations

2. **Master the Language:**
   - [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) - Complete guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design

3. **Try Advanced Examples:**
   - `examples/` directory has real working code
   - Run `python examples/newton_full_demo.py`

4. **Build Something Real:**
   - Start with a simple blueprint
   - Add laws one at a time
   - Test thoroughly
   - Deploy with confidence

### Explore More Features

- **Education Tools:** Build lesson planners, grade books, PLC reports
- **IoT Systems:** Create sensor networks with safety bounds
- **Financial Apps:** Build trading systems, payment processors
- **Healthcare:** HIPAA-compliant patient records
- **Smart Homes:** Automation with safety constraints

### Join the Community

- **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **GitHub:** https://github.com/jaredlewiswechs/Newton-api
- **Report Issues:** Open a GitHub issue

### Advanced Topics

Once you're comfortable with basics:

1. **Newton TLM** - Topological Language Machine (ACID compliance)
2. **Newton Geometry** - Topological constraint framework
3. **Cartridge System** - Media specification cartridges
4. **Policy Engine** - Glass Box transparency
5. **Interface Builder** - Programmatic UI generation

---

## Quick Reference

### Four Keywords

```python
when(condition, result)  # "If this is true"
finfr                    # "Forbidden state"
fin                      # "Soft stop"
and                      # "Also this"
```

### Blueprint Structure

```python
class MyBlueprint(Blueprint):
    # Fields (state)
    value = field(type, default=x)
    
    # Laws (constraints)
    @law
    def my_law(self):
        when(condition, finfr)
    
    # Forges (actions)
    @forge
    def my_action(self):
        # Do something
        return result
```

### API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check server status |
| `/verify` | POST | Verify content |
| `/calculate` | POST | Verified computation |
| `/constraint` | POST | Check constraints |
| `/vault/store` | POST | Store encrypted data |
| `/vault/retrieve` | POST | Retrieve encrypted data |
| `/ledger` | GET | View audit trail |
| `/statistics` | POST | Robust statistics |
| `/ground` | POST | Ground claims |
| `/education/lesson` | POST | Generate lesson plan |
| `/education/plc` | POST | Generate PLC report |

### CLI Commands

```bash
newton serve        # Start the server
newton demo         # Run interactive demo
newton calc "2+3"   # Quick calculation
newton health       # Check server status
```

---

## Summary

You've learned:

✅ What Newton is and why it's different  
✅ How to install and set up Newton  
✅ Core concepts: Blueprints, Laws, Forges  
✅ The four keywords: when, finfr, fin, and  
✅ How to use all Newton features  
✅ How to build complete applications  
✅ How to troubleshoot common issues  

**The constraint IS the instruction. The verification IS the computation.**

Now go build something impossible to break! 🍎

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*"1 == 1. The cloud is weather. We're building shelter."*
