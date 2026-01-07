# Newton SDK v3.0 - Auto-Discovering

**Like numpy, but for verified AI.**

```python
from newton import Newton
n = Newton()

# That's it. It auto-discovers all 115 endpoints.
```

## Installation

```bash
# From PyPI (coming soon)
pip install newton-sdk

# From GitHub
pip install git+https://github.com/jaredlewiswechs/Newton-api.git#subdirectory=sdk

# Or just copy newton.py anywhere
curl -O https://raw.githubusercontent.com/jaredlewiswechs/Newton-api/main/sdk/newton.py
```

## Quick Start

```python
from newton import Newton

n = Newton()

# Core verification
result = n.ask("What is quantum computing?")
verified = n.verify("user input", constraints=["safe", "no_profanity"])

# Verified computation
answer = n.calculate("sum([x**2 for x in range(100)])")

# Statistics with anomaly detection
stats = n.statistics([1, 2, 3, 4, 100])  # Detects 100 as outlier
```

## Auto-Discovery Magic

When you update GitHub → Render deploys → SDK automatically knows:

```python
n = Newton()
n.endpoints()  # Lists all 115 discovered endpoints
n.refresh()    # Re-fetch from API if new endpoints added
```

The SDK fetches `/openapi.json` on init and dynamically creates methods.

## Namespaces (15 total)

### Cartridge - Verified Media Generation

```python
# Visual (SVG)
svg = n.cartridge.visual("a red circle on blue background")

# Sound (Audio spec)
audio = n.cartridge.sound("peaceful piano melody", duration_ms=30000)

# Sequence (Video/Animation)
video = n.cartridge.sequence("bouncing ball", duration_seconds=5, fps=30)

# Data (Reports)
report = n.cartridge.data("sales summary", data=sales_data, format="markdown")

# Rosetta (Code Generation)
code = n.cartridge.rosetta("todo app", target_platform="iOS", language="Swift")

# Auto-detect
result = n.cartridge.auto("draw me a chart of monthly sales")
```

### Education - Teacher Support

```python
# Generate lesson plan
lesson = n.education.lesson(
    grade=3,
    subject="math",
    topic="fractions",
    teks_codes=["3.3A", "3.3B"]
)

# Generate slides
slides = n.education.slides(lesson_plan=lesson.data)

# Analyze assessment
analysis = n.education.assess(
    students=student_data,
    assessment_name="Unit 3 Test",
    mastery_threshold=0.8
)
```

### Teachers - Classroom Database

```python
# Create student
student = n.teachers.students(first_name="Jane", last_name="Doe", grade=3)

# Create classroom
classroom = n.teachers.classrooms(name="3A", grade=3, subject="Math")

# Auto-differentiated groups
groups = n.teachers.groups(classroom_id="3A")
# Returns: Tier 3 (reteach), Tier 2 (approaching), Tier 1 (mastery), Enrichment
```

### Voice - MOAD (Mother Of All Demos)

```python
# Natural language to verified app
app = n.voice.ask("build me a todo app with dark mode")

# Streaming
for chunk in n.voice.stream("create a weather dashboard"):
    print(chunk)

# Parse intent
intent = n.voice.intent("I want to track my expenses")
```

### Vault - Encrypted Storage

```python
# Store
entry = n.vault.store(
    identity="user@example.com",
    passphrase="secret",
    data={"api_key": "sensitive"}
)

# Retrieve
data = n.vault.retrieve(
    identity="user@example.com",
    passphrase="secret",
    entry_id=entry.data["entry_id"]
)
```

### Ledger - Immutable Audit Trail

```python
# Get entries
entries = n.ledger.entries(limit=100)

# Get certificate for proof
cert = n.ledger.certificate(index=42)
```

### Jester - Code Constraint Analyzer

```python
# Analyze code for constraints
analysis = n.jester.analyze(code="""
def divide(a, b):
    return a / b
""")
# Detects: requires b != 0

# Get CDL output
cdl = n.jester.cdl(code=source_code)
```

### Interface Builder - Verified UI

```python
# List templates
templates = n.interface.templates(type="dashboard")

# Build from template
ui = n.interface.build(
    template_id="todo-app",
    variables={"title": "My Tasks"}
)
```

### Chatbot - Type-Safe Constraints

```python
# Process through constraint pipeline
response = n.chatbot.compile(input="Tell me about Newton")

# Classify input
classification = n.chatbot.classify(input="How do I use the API?")
```

### Extract - Fuzzy to Formal

```python
# Extract constraints from natural language
constraints = n.extract.constraints(
    text="Users must be over 18 and have a valid email"
)

# Verify against constraints
result = n.extract.verify(
    plan="Allow user with age 16",
    extraction_id=constraints.data["id"]
)
```

### Policy, Negotiator, Merkle - Glass Box

```python
# Governance rules
n.policy.list()
n.policy.add(id="no-pii", name="Block PII", type="deny", condition="contains_pii")

# Human-in-the-loop
request = n.negotiator.request(operation="delete_all", reason="Cleanup")
n.negotiator.approve(request.data["id"], approver="admin")

# Cryptographic anchoring
n.merkle.anchors()
proof = n.merkle.proof(index=42)
```

### License & Auth

```python
# Verify license (from Gumroad)
result = n.license.verify(license_key="YOUR-KEY")
api_key = result.data["api_key"]

# Use with auth
n = Newton(api_key=api_key)

# parcCloud auth
n.parccloud.signup(email="user@example.com", password="secret", name="User")
n.parccloud.signin(email="user@example.com", password="secret")
```

## Discovery Commands

```python
# List all endpoints
n.endpoints()

# Filter endpoints
n.endpoints("cartridge")  # Only cartridge endpoints
n.endpoints("POST")       # Only POST endpoints

# Full capability report
caps = n.capabilities()
print(caps["endpoint_count"])  # 115
print(caps["namespaces"])

# Help
n.help()              # General help
n.help("cartridge")   # Cartridge help
n.help("all")         # All namespaces

# Refresh discovery
n.refresh()  # Re-fetch from API
```

## Response Object

All methods return `NewtonResponse`:

```python
result = n.ask("Hello")

result.success        # True/False
result.data           # Response data
result.verified       # Was it verified?
result.constraints_checked  # Which constraints
result.ledger_index   # Audit trail index
result.merkle_root    # Cryptographic proof
result.latency_ms     # Response time

# Dict-style access
result["key"]
result.key

# Convert to dict
result.to_dict()
```

## Module-Level Convenience

```python
import newton

newton.connect()  # Uses default URL
newton.ask("Hello!")
newton.verify("Safe text")
```

## CLI Mode

```bash
python newton.py
# Starts interactive mode with 'n' instance available
```

## Configuration

```python
n = Newton(
    base_url="https://your-instance.com",  # Custom URL
    api_key="your-key",                     # Authentication
    auto_discover=True,                     # Fetch OpenAPI on init (default)
    timeout=30,                             # Request timeout
    verify_ssl=True,                        # SSL verification
    debug=True                              # Enable debug logging
)
```

## Error Handling

```python
from newton import (
    NewtonError,           # Base exception
    NewtonConnectionError, # Connection failed
    NewtonAuthError,       # Auth required
    NewtonRateLimitError,  # Rate limited
    NewtonValidationError, # Validation failed
    NewtonVerificationFailed  # Constraint violation
)

try:
    result = n.ask("Hello")
except NewtonConnectionError:
    print("Newton is waking up (free tier)")
except NewtonAuthError:
    print("Need API key")
```

## How Auto-Discovery Works

1. On `Newton()` init, SDK fetches `/openapi.json`
2. Parses all paths and creates Python methods
3. Organizes into namespaces (cartridge, education, etc.)
4. Falls back to hardcoded endpoints if API unavailable

When you push to GitHub:
- Render auto-deploys
- Next `Newton()` init sees new endpoints
- Or call `n.refresh()` to update

## Performance

Newton API stats (from README):
- Median latency: 2.31ms
- Internal: 46.5μs
- Throughput: 605 req/sec
- 638x faster than Stripe

## Single File

Just `newton.py` - drop it anywhere:

```python
# In your project
from newton import Newton

# Or system-wide
import sys
sys.path.append("/path/to/newton")
from newton import Newton
```

Only dependency: `requests`

---

**Newton Verified Computation Engine**
*Every answer verified. Every operation logged. Every proof anchored.*
