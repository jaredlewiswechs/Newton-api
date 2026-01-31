# Newton Supercomputer - Examples Guide

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   📚 Newton Examples - Learn by Doing                        │
    │                                                              │
    │   "The constraint IS the instruction."                      │
    │   "Show me the code."                                       │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

**Complete examples for every Newton feature**

This guide shows you exactly how to use each part of Newton Supercomputer, with real working code examples.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core Verification](#core-verification)
- [Cartridge System](#cartridge-system) ⭐
- [Constraint Definition Language (CDL)](#constraint-definition-language-cdl)
- [Logic Engine](#logic-engine)
- [Vault (Encrypted Storage)](#vault-encrypted-storage)
- [Ledger (Audit Trail)](#ledger-audit-trail)
- [Statistics & Robust Methods](#statistics--robust-methods)
- [Education Features](#education-features)
- [Voice Interface](#voice-interface)
- [Chatbot Compiler](#chatbot-compiler)
- [Interface Builder](#interface-builder)
- [Policy Engine](#policy-engine)
- [Complete Applications](#complete-applications)

---

## Quick Start

### Using cURL

```bash
# Start Newton server
python newton_supercomputer.py

# Health check
curl http://localhost:8000/health

# Verify content
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "What is 2+2?"}'

# Calculate
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 2]}}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Verify content
response = requests.post(
    f"{BASE_URL}/verify",
    json={"input": "What is the capital of France?"}
)
print(response.json())
# {'verified': True, 'elapsed_us': 1236, ...}

# Calculate
response = requests.post(
    f"{BASE_URL}/calculate",
    json={"expression": {"op": "+", "args": [2, 2]}}
)
print(response.json())
# {'result': 4, 'verified': True, ...}
```

---

## Core Verification

### Forge - Content Verification

Verify content before processing:

```python
import requests

def verify_content(text):
    """Verify content is safe and appropriate"""
    response = requests.post(
        "http://localhost:8000/verify",
        json={"input": text}
    )
    result = response.json()
    return result["verified"], result

# Example 1: Safe content
verified, result = verify_content("What is Python?")
print(f"Verified: {verified}")  # True

# Example 2: Batch verification
response = requests.post(
    "http://localhost:8000/verify/batch",
    json={
        "inputs": [
            "Hello world",
            "Teach me math",
            "Explain photosynthesis"
        ]
    }
)
results = response.json()
for i, r in enumerate(results["results"]):
    print(f"Input {i+1}: Verified={r['verified']}")
```

---

## Cartridge System

The Cartridge System is Newton's way of generating different types of content with built-in verification.

### Auto-Detect Cartridge

Let Newton automatically choose the right cartridge:

```python
import requests

def auto_detect(intent):
    """Auto-detect and use appropriate cartridge"""
    response = requests.post(
        "http://localhost:8000/cartridge/auto",
        json={"intent": intent}
    )
    return response.json()

# Example 1: App development intent -> Rosetta
result = auto_detect("Create a todo list app for iOS")
print(f"Cartridge: {result['cartridge_type']}")  # 'rosetta'
print(f"Platform: {result.get('target_platform', 'N/A')}")  # 'ios'

# Example 2: Visual intent -> Visual cartridge
result = auto_detect("Design a minimalist logo with circles")
print(f"Cartridge: {result['cartridge_type']}")  # 'visual'

# Example 3: Data intent -> Data cartridge
result = auto_detect("Create a schema for user profiles")
print(f"Cartridge: {result['cartridge_type']}")  # 'data'
```

### Visual Cartridge

Generate visual designs with constraints:

```python
import requests

def create_visual(intent, style="modern", constraints=None):
    """Create visual designs"""
    payload = {
        "intent": intent,
        "style": style
    }
    if constraints:
        payload["constraints"] = constraints
    
    response = requests.post(
        "http://localhost:8000/cartridge/visual",
        json=payload
    )
    return response.json()

# Example 1: Logo design
result = create_visual(
    intent="Create a logo for a tech startup",
    style="minimalist",
    constraints={
        "colors": ["#0066CC", "#FFFFFF"],
        "max_elements": 3
    }
)
print(f"Design: {result['design']}")
print(f"Verified: {result['verified']}")

# Example 2: UI mockup
result = create_visual(
    intent="Design a login screen",
    style="modern",
    constraints={
        "platform": "mobile",
        "orientation": "portrait"
    }
)

# Example 3: Icon set
result = create_visual(
    intent="Create icons for navigation: home, search, profile",
    style="flat",
    constraints={
        "size": "24x24",
        "format": "svg"
    }
)
```

### Sound Cartridge

Generate audio with verification:

```python
import requests

def create_sound(intent, style="clean", duration_ms=1000):
    """Generate sound effects or audio"""
    response = requests.post(
        "http://localhost:8000/cartridge/sound",
        json={
            "intent": intent,
            "style": style,
            "duration_ms": duration_ms
        }
    )
    return response.json()

# Example 1: Notification sound
result = create_sound(
    intent="Generate a pleasant notification sound",
    style="soft",
    duration_ms=500
)
print(f"Sound generated: {result['verified']}")

# Example 2: Alert sound
result = create_sound(
    intent="Create an urgent alert sound",
    style="attention",
    duration_ms=1000
)

# Example 3: Success chime
result = create_sound(
    intent="Make a success confirmation chime",
    style="positive",
    duration_ms=300
)
```

### Sequence Cartridge

Generate workflows and sequences:

```python
import requests

def create_sequence(intent, type="workflow"):
    """Generate sequences, workflows, or processes"""
    response = requests.post(
        "http://localhost:8000/cartridge/sequence",
        json={
            "intent": intent,
            "type": type
        }
    )
    return response.json()

# Example 1: User onboarding
result = create_sequence(
    intent="Create a user onboarding flow",
    type="workflow"
)
print(f"Steps: {len(result['sequence']['steps'])}")
for step in result['sequence']['steps']:
    print(f"  - {step['name']}: {step['action']}")

# Example 2: Payment process
result = create_sequence(
    intent="Design a secure checkout process",
    type="transactional"
)

# Example 3: Tutorial sequence
result = create_sequence(
    intent="Build a product tour for new users",
    type="interactive"
)
```

### Data Cartridge

Generate data schemas and structures:

```python
import requests

def create_schema(intent, format="json"):
    """Generate data schemas"""
    response = requests.post(
        "http://localhost:8000/cartridge/data",
        json={
            "intent": intent,
            "format": format
        }
    )
    return response.json()

# Example 1: User profile schema
result = create_schema(
    intent="Design a schema for user profiles",
    format="json"
)
print(f"Schema: {result['schema']}")
print(f"Fields: {list(result['schema']['properties'].keys())}")

# Example 2: Product catalog
result = create_schema(
    intent="Create a database schema for an e-commerce catalog",
    format="sql"
)
print(f"Tables: {result['schema']['tables']}")

# Example 3: API response structure
result = create_schema(
    intent="Define response format for a weather API",
    format="json"
)
```

### Rosetta Compiler

Cross-platform code generation:

```python
import requests

def compile_app(intent, platform, language=None):
    """Compile application for target platform"""
    payload = {
        "intent": intent,
        "target_platform": platform
    }
    if language:
        payload["language"] = language
    
    response = requests.post(
        "http://localhost:8000/cartridge/rosetta",
        json=payload
    )
    return response.json()

# Example 1: iOS app in Swift
result = compile_app(
    intent="Build a todo list app",
    platform="ios",
    language="swift"
)
print(f"Code generated for {result['target_platform']}")
print(f"Verified: {result['verified']}")
print(f"\nCode preview:\n{result['code'][:200]}...")

# Example 2: Android app in Kotlin
result = compile_app(
    intent="Create a notes app with categories",
    platform="android",
    language="kotlin"
)

# Example 3: Web app
result = compile_app(
    intent="Build a calculator web app",
    platform="web",
    language="javascript"
)

# Example 4: Desktop app
result = compile_app(
    intent="Create a simple text editor",
    platform="desktop",
    language="python"
)
```

### Complete Cartridge Example

Full workflow using multiple cartridges:

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Auto-detect what we need
intent = "Create a mobile app for tracking daily habits"
auto_result = requests.post(
    f"{BASE_URL}/cartridge/auto",
    json={"intent": intent}
).json()

print(f"Detected need for: {auto_result['cartridge_type']}")

# Step 2: Generate data schema
schema = requests.post(
    f"{BASE_URL}/cartridge/data",
    json={
        "intent": "Design data model for habit tracking app",
        "format": "json"
    }
).json()

print(f"\nData schema created with fields:")
for field in schema['schema']['properties'].keys():
    print(f"  - {field}")

# Step 3: Generate UI design
ui_design = requests.post(
    f"{BASE_URL}/cartridge/visual",
    json={
        "intent": "Design habit tracker interface",
        "style": "modern",
        "constraints": {
            "platform": "mobile",
            "primary_color": "#4CAF50"
        }
    }
).json()

print(f"\nUI design: {ui_design['design']}")

# Step 4: Compile for platform
code = requests.post(
    f"{BASE_URL}/cartridge/rosetta",
    json={
        "intent": "Build habit tracker app",
        "target_platform": "ios",
        "language": "swift",
        "schema": schema['schema']
    }
).json()

print(f"\nCode generated: {len(code['code'])} characters")
print(f"Verified: {code['verified']}")

# Step 5: Generate sounds for notifications
sound = requests.post(
    f"{BASE_URL}/cartridge/sound",
    json={
        "intent": "Create habit completion sound",
        "style": "positive",
        "duration_ms": 500
    }
).json()

print(f"\nSound generated: {sound['verified']}")

print("\n✓ Complete app generated with all assets!")
```

---

## Constraint Definition Language (CDL)

### Basic Constraints

```python
import requests

def check_constraint(constraint, obj):
    """Evaluate constraint against object"""
    response = requests.post(
        "http://localhost:8000/constraint",
        json={
            "constraint": constraint,
            "object": obj
        }
    )
    return response.json()

# Example 1: Age verification
result = check_constraint(
    constraint={"field": "age", "operator": "ge", "value": 18},
    obj={"age": 25}
)
print(f"Age check passed: {result['passed']}")  # True

# Example 2: String matching
result = check_constraint(
    constraint={"field": "status", "operator": "eq", "value": "active"},
    obj={"status": "active"}
)
print(f"Status check: {result['passed']}")  # True

# Example 3: Numeric comparison
result = check_constraint(
    constraint={"field": "balance", "operator": "gt", "value": 0},
    obj={"balance": 1000.50}
)
print(f"Balance positive: {result['passed']}")  # True
```

### Ratio Constraints (f/g)

Financial and dimensional analysis:

```python
import requests

def check_ratio(f_field, g_field, operator, threshold, obj):
    """Check ratio constraint (f/g relationship)"""
    response = requests.post(
        "http://localhost:8000/constraint",
        json={
            "constraint": {
                "f_field": f_field,
                "g_field": g_field,
                "operator": operator,
                "threshold": threshold
            },
            "object": obj
        }
    )
    return response.json()

# Example 1: Debt-to-assets ratio
result = check_ratio(
    f_field="debt",
    g_field="assets",
    operator="ratio_le",
    threshold=0.5,
    obj={"debt": 100000, "assets": 300000}
)
print(f"Debt/Assets = {100000/300000:.2f} ≤ 0.5: {result['passed']}")  # True

# Example 2: Cost-to-revenue ratio
result = check_ratio(
    f_field="costs",
    g_field="revenue",
    operator="ratio_lt",
    threshold=0.7,
    obj={"costs": 50000, "revenue": 100000}
)
print(f"Cost efficiency check: {result['passed']}")  # True

# Example 3: Utilization rate
result = check_ratio(
    f_field="used",
    g_field="capacity",
    operator="ratio_le",
    threshold=0.9,
    obj={"used": 850, "capacity": 1000}
)
print(f"Utilization OK: {result['passed']}")  # True
```

### Complex Constraints

```python
import requests

# Example: Multi-field validation
def validate_transaction(transaction):
    """Validate transaction with multiple constraints"""
    
    constraints = [
        # Amount must be positive
        {
            "constraint": {"field": "amount", "operator": "gt", "value": 0},
            "object": transaction
        },
        # Must have valid recipient
        {
            "constraint": {"field": "recipient", "operator": "exists"},
            "object": transaction
        },
        # Balance sufficient
        {
            "constraint": {
                "f_field": "amount",
                "g_field": "balance",
                "operator": "ratio_le",
                "threshold": 1.0
            },
            "object": transaction
        }
    ]
    
    results = []
    for c in constraints:
        response = requests.post(
            "http://localhost:8000/constraint",
            json=c
        )
        results.append(response.json()['passed'])
    
    return all(results)

# Test transaction
txn = {
    "amount": 500,
    "recipient": "user@example.com",
    "balance": 1000
}

valid = validate_transaction(txn)
print(f"Transaction valid: {valid}")  # True
```

---

## Logic Engine

### Basic Calculations

```python
import requests

def calculate(expression):
    """Execute verified calculation"""
    response = requests.post(
        "http://localhost:8000/calculate",
        json={"expression": expression}
    )
    return response.json()

# Example 1: Arithmetic
result = calculate({"op": "+", "args": [10, 5]})
print(f"10 + 5 = {result['result']}")  # 15

result = calculate({"op": "*", "args": [6, 7]})
print(f"6 * 7 = {result['result']}")  # 42

# Example 2: Comparisons
result = calculate({"op": ">", "args": [10, 5]})
print(f"10 > 5 = {result['result']}")  # True

# Example 3: Boolean logic
result = calculate({"op": "and", "args": [True, False]})
print(f"True AND False = {result['result']}")  # False
```

### Conditional Logic

```python
import requests

# Example 1: If-then-else
result = requests.post(
    "http://localhost:8000/calculate",
    json={
        "expression": {
            "op": "if",
            "args": [
                {"op": ">", "args": [10, 5]},  # condition
                "greater",  # then
                "not greater"  # else
            ]
        }
    }
).json()
print(f"Result: {result['result']}")  # 'greater'

# Example 2: Nested conditionals
result = requests.post(
    "http://localhost:8000/calculate",
    json={
        "expression": {
            "op": "if",
            "args": [
                {"op": ">=", "args": [85, 90]},
                "A",
                {
                    "op": "if",
                    "args": [
                        {"op": ">=", "args": [85, 80]},
                        "B",
                        "C"
                    ]
                }
            ]
        }
    }
).json()
print(f"Grade: {result['result']}")  # 'B'
```

### Loops (Bounded)

```python
import requests

# Example 1: Simple loop
result = requests.post(
    "http://localhost:8000/calculate",
    json={
        "expression": {
            "op": "for",
            "args": [
                "i",  # variable
                0,    # start
                5,    # end (exclusive)
                {"op": "*", "args": [{"var": "i"}, 2]}  # body
            ]
        }
    }
).json()
print(f"Results: {result['result']}")  # [0, 2, 4, 6, 8]

# Example 2: Sum with loop
result = requests.post(
    "http://localhost:8000/calculate",
    json={
        "expression": {
            "op": "for",
            "args": [
                "n",
                1,
                6,
                {"var": "n"}
            ]
        }
    }
).json()
numbers = result['result']
total = sum(numbers)
print(f"Sum of 1-5: {total}")  # 15
```

### Get Examples

```python
import requests

# Get example expressions
response = requests.post(
    "http://localhost:8000/calculate/examples",
    json={"category": "basic"}
)
examples = response.json()

print("Available examples:")
for ex in examples['examples']:
    print(f"  - {ex['name']}: {ex['expression']}")
```

---

## Vault (Encrypted Storage)

### Storing Encrypted Data

```python
import requests

def store_secret(identity, passphrase, data):
    """Store encrypted data"""
    response = requests.post(
        "http://localhost:8000/vault/store",
        json={
            "identity": identity,
            "passphrase": passphrase,
            "data": data,
            "metadata": {"timestamp": "2026-01-31"}
        }
    )
    return response.json()

# Store user credentials
result = store_secret(
    identity="user@example.com",
    passphrase="secure-password-123",
    data={
        "api_key": "sk-abc123...",
        "secret_token": "token-xyz789..."
    }
)

print(f"Stored: {result['success']}")
print(f"Entry ID: {result['entry_id']}")
print(f"Owner ID: {result['owner_id']}")
```

### Retrieving Encrypted Data

```python
import requests

def retrieve_secret(identity, passphrase, entry_id):
    """Retrieve encrypted data"""
    response = requests.post(
        "http://localhost:8000/vault/retrieve",
        json={
            "identity": identity,
            "passphrase": passphrase,
            "entry_id": entry_id
        }
    )
    return response.json()

# Retrieve data
result = retrieve_secret(
    identity="user@example.com",
    passphrase="secure-password-123",
    entry_id="V_ABC123..."
)

print(f"Retrieved: {result['success']}")
print(f"Data: {result['data']}")
```

---

## Ledger (Audit Trail)

### View Ledger

```python
import requests

# Get full ledger
response = requests.get("http://localhost:8000/ledger")
ledger = response.json()

print(f"Total entries: {len(ledger['entries'])}")
print(f"Chain valid: {ledger['chain_valid']}")
print(f"Merkle root: {ledger['merkle_root']}")

# Show recent entries
for entry in ledger['entries'][-5:]:
    print(f"\n{entry['index']}: {entry['operation']}")
    print(f"  Hash: {entry['hash'][:16]}...")
    print(f"  Timestamp: {entry['timestamp']}")
```

### Get Merkle Proof

```python
import requests

# Get proof for specific entry
response = requests.get("http://localhost:8000/ledger/10")
entry = response.json()

print(f"Entry {entry['index']}: {entry['operation']}")
print(f"Merkle proof: {entry['merkle_proof']}")
print(f"Verified: {entry['verified']}")
```

### Export Certificate

```python
import requests

# Get verification certificate
response = requests.get("http://localhost:8000/ledger/certificate/10")
cert = response.json()

print(f"Certificate for entry {cert['entry_index']}")
print(f"Operation: {cert['operation']}")
print(f"Timestamp: {cert['timestamp']}")
print(f"Merkle root: {cert['merkle_root']}")
print(f"Proof: {cert['merkle_proof']}")
```

---

## Statistics & Robust Methods

### Robust Statistics

```python
import requests

def robust_stats(values):
    """Calculate robust statistics"""
    response = requests.post(
        "http://localhost:8000/statistics",
        json={
            "values": values,
            "method": "robust"
        }
    )
    return response.json()

# Example with outliers
data = [1, 2, 3, 4, 5, 100]  # 100 is outlier
result = robust_stats(data)

print("Robust statistics:")
print(f"  MAD: {result['result']['mad']}")
print(f"  Median: {result['result']['median']}")
print(f"  Q1: {result['result']['q1']}")
print(f"  Q3: {result['result']['q3']}")

# Compare to traditional
print(f"\nMean (affected by outlier): {sum(data)/len(data):.2f}")
print(f"Median (robust): {result['result']['median']}")
```

---

## Education Features

### Generate Lesson Plan

```python
import requests

def create_lesson(grade, subject, teks_codes, topic=None):
    """Generate NES-compliant lesson plan"""
    response = requests.post(
        "http://localhost:8000/education/lesson",
        json={
            "grade": grade,
            "subject": subject,
            "teks_codes": teks_codes,
            "topic": topic
        }
    )
    return response.json()

# Example: 8th grade math lesson
lesson = create_lesson(
    grade=8,
    subject="Math",
    teks_codes=["8.7.C"],  # Pythagorean Theorem
    topic="Pythagorean Theorem"
)

print(f"Lesson: {lesson['title']}")
print(f"Duration: {lesson['duration']} minutes")
print(f"TEKS aligned: {lesson['teks_codes']}")
print(f"\nObjectives:")
for obj in lesson['objectives']:
    print(f"  - {obj}")
```

### Analyze Assessment

```python
import requests

def analyze_assessment(name, teks_codes, students):
    """Analyze assessment results"""
    response = requests.post(
        "http://localhost:8000/education/assess",
        json={
            "assessment_name": name,
            "teks_codes": teks_codes,
            "total_points": 100.0,
            "mastery_threshold": 80.0,
            "students": students
        }
    )
    return response.json()

# Example assessment data
students = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 78},
    {"name": "Charlie", "score": 88},
    {"name": "Diana", "score": 92}
]

analysis = analyze_assessment(
    name="Fractions Quiz",
    teks_codes=["5.3.A", "5.3.B"],
    students=students
)

print(f"Class average: {analysis['average']:.1f}")
print(f"Mastery rate: {analysis['mastery_rate']:.1f}%")
print(f"Students needing intervention: {analysis['intervention_needed']}")
```

---

## Voice Interface

### Voice Intent Recognition

```python
import requests

def recognize_intent(text):
    """Recognize voice command intent"""
    response = requests.post(
        "http://localhost:8000/voice/intent",
        json={"text": text}
    )
    return response.json()

# Example voice commands
commands = [
    "What's the weather today?",
    "Set a timer for 10 minutes",
    "Play some music",
    "Calculate 15% tip on $80"
]

for cmd in commands:
    result = recognize_intent(cmd)
    print(f"Command: {cmd}")
    print(f"  Intent: {result['intent']}")
    print(f"  Confidence: {result['confidence']}")
    print()
```

---

## Chatbot Compiler

### Compile Safe Chatbot Response

```python
import requests

def chatbot_response(user_input):
    """Get safe, verified chatbot response"""
    response = requests.post(
        "http://localhost:8000/chatbot/compile",
        json={"input": user_input}
    )
    return response.json()

# Example 1: Safe question
result = chatbot_response("What is Python?")
print(f"Input: {result['input']}")
print(f"Decision: {result['decision']}")
print(f"Response: {result['response']}")

# Example 2: Medical question (deferred)
result = chatbot_response("I have a headache, what medicine should I take?")
print(f"\nMedical question:")
print(f"Decision: {result['decision']}")  # 'defer'
print(f"Reason: {result['reason']}")

# Example 3: Harmful request (refused)
result = chatbot_response("How do I hack a website?")
print(f"\nHarmful request:")
print(f"Decision: {result['decision']}")  # 'refuse'
```

### Classify User Input

```python
import requests

def classify_input(text):
    """Classify user input without generating response"""
    response = requests.post(
        "http://localhost:8000/chatbot/classify",
        json={"input": text}
    )
    return response.json()

# Classify different types
inputs = [
    "What is 2+2?",
    "Should I invest in stocks?",
    "How do I make explosives?"
]

for inp in inputs:
    result = classify_input(inp)
    print(f"\nInput: {inp}")
    print(f"Type: {result['type']}")
    print(f"Risk: {result['risk_level']}")
    print(f"Should answer: {result['should_answer']}")
```

---

## Interface Builder

### Build from Template

```python
import requests

def build_interface(template_id, variables):
    """Build interface from template"""
    response = requests.post(
        "http://localhost:8000/interface/build",
        json={
            "template_id": template_id,
            "variables": variables,
            "output_format": "json"
        }
    )
    return response.json()

# Example: Login form
interface = build_interface(
    template_id="form-basic",
    variables={
        "title": "Sign In",
        "submit_label": "Login",
        "fields": ["email", "password"]
    }
)

print(f"Interface: {interface['type']}")
print(f"Components: {len(interface['components'])}")
```

### List Available Templates

```python
import requests

# Get all templates
response = requests.get("http://localhost:8000/interface/templates")
templates = response.json()

print("Available templates:")
for template in templates['templates']:
    print(f"  - {template['id']}: {template['name']}")
    print(f"    {template['description']}")
```

---

## Policy Engine

### Create Policy

```python
import requests

def create_policy(policy_id, name, condition):
    """Create a verification policy"""
    response = requests.post(
        "http://localhost:8000/policy",
        json={
            "id": policy_id,
            "name": name,
            "type": "input_validation",
            "action": "allow",
            "condition": condition
        }
    )
    return response.json()

# Example: Age verification policy
policy = create_policy(
    policy_id="age-verification",
    name="Minimum Age Check",
    condition={
        "field": "age",
        "operator": "ge",
        "value": 18
    }
)

print(f"Policy created: {policy['name']}")
```

### List Policies

```python
import requests

response = requests.get("http://localhost:8000/policy")
policies = response.json()

print(f"Active policies: {len(policies['policies'])}")
for policy in policies['policies']:
    print(f"  - {policy['name']}: {policy['type']}")
```

---

## Complete Applications

### Todo App (Full Stack)

```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Generate data schema
schema = requests.post(
    f"{BASE_URL}/cartridge/data",
    json={
        "intent": "Create schema for todo items",
        "format": "json"
    }
).json()

print("✓ Data schema created")

# Step 2: Generate UI
ui = requests.post(
    f"{BASE_URL}/cartridge/visual",
    json={
        "intent": "Design todo app interface",
        "style": "clean",
        "constraints": {"platform": "web"}
    }
).json()

print("✓ UI design created")

# Step 3: Generate code
code = requests.post(
    f"{BASE_URL}/cartridge/rosetta",
    json={
        "intent": "Build todo app",
        "target_platform": "web",
        "language": "javascript"
    }
).json()

print("✓ Code generated")
print(f"\nVerified: {code['verified']}")
print(f"Code length: {len(code['code'])} characters")
```

### E-Commerce Product Validator

```python
import requests

def validate_product(product):
    """Validate product with multiple constraints"""
    
    BASE_URL = "http://localhost:8000"
    
    # Check price is positive
    price_check = requests.post(
        f"{BASE_URL}/constraint",
        json={
            "constraint": {"field": "price", "operator": "gt", "value": 0},
            "object": product
        }
    ).json()
    
    # Check stock is non-negative
    stock_check = requests.post(
        f"{BASE_URL}/constraint",
        json={
            "constraint": {"field": "stock", "operator": "ge", "value": 0},
            "object": product
        }
    ).json()
    
    # Check discount ratio
    if "discount" in product and "price" in product:
        discount_check = requests.post(
            f"{BASE_URL}/constraint",
            json={
                "constraint": {
                    "f_field": "discount",
                    "g_field": "price",
                    "operator": "ratio_lt",
                    "threshold": 1.0
                },
                "object": product
            }
        ).json()
    else:
        discount_check = {"passed": True}
    
    # Log to ledger
    valid = all([
        price_check['passed'],
        stock_check['passed'],
        discount_check['passed']
    ])
    
    # Store in vault if valid
    if valid:
        vault_result = requests.post(
            f"{BASE_URL}/vault/store",
            json={
                "identity": "product-validator",
                "passphrase": "validator-key",
                "data": product
            }
        ).json()
        print(f"✓ Product stored: {vault_result['entry_id']}")
    
    return valid

# Test product
product = {
    "name": "Laptop",
    "price": 999.99,
    "stock": 50,
    "discount": 100.00
}

valid = validate_product(product)
print(f"Product valid: {valid}")
```

---

## Next Steps

1. **Try the examples** - Copy and run these examples
2. **Read the guides** - Check [TESTING.md](TESTING.md) and [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
3. **Build something** - Combine features to create your own app
4. **Explore more** - See `/examples` directory for complete demos

---

## Support

- **Documentation**: [README.md](README.md) for overview
- **Testing**: [TESTING.md](TESTING.md) for test instructions
- **Windows**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows users
- **Programming**: [TINYTALK_PROGRAMMING_GUIDE.md](TINYTALK_PROGRAMMING_GUIDE.md) for tinyTalk

---

**Last Updated:** January 31, 2026

**Newton Version:** 1.3.0

**The constraint IS the instruction. 1 == 1.**
