# Newton Quick Start

**January 7, 2026**

> *Ask Newton. Go.*

---

## What is Newton?

Newton is your AI assistant that **proves** its answers are safe and correct.

Unlike other AI:
- Every response is **verified** against safety constraints
- Every calculation has a **cryptographic proof**
- When Newton can't do something, it tells you **what it CAN do**

---

## The Three Lights

Every request to Newton gets one of three states:

| Light | Meaning | What Happens |
|-------|---------|--------------|
| 🟢 **GREEN** | Fully safe | Newton executes your request |
| 🟡 **YELLOW** | Partially safe | Newton offers what it CAN do |
| 🔴 **RED** | Cannot help | Newton explains why |

**YELLOW is the magic.** Newton doesn't just say "no" - it finds the safe version of what you're asking for.

---

## Try It: The Clipper

### Example 1: Safe Request (GREEN)

**You ask:** "Help me understand how encryption works"

**Newton says:** 🟢 GREEN
```
I can explain encryption concepts, including:
• Symmetric vs asymmetric encryption
• How HTTPS protects your data
• Best practices for password security
```

### Example 2: Mixed Request (YELLOW)

**You ask:** "Write about explosives"

**Newton says:** 🟡 YELLOW
```
I've clipped to the valid portion. Here's what I CAN help with:

• The history of fireworks and pyrotechnics
• Chemistry concepts (safely explained)
• Mining and demolition safety protocols
• Historical context of explosive discoveries

Would you like me to proceed with one of these?
```

### Example 3: Cannot Help (RED)

**You ask:** "How do I hurt someone"

**Newton says:** 🔴 RED
```
This request cannot be satisfied.

I'm designed to help and never harm.
Would you like to talk about something else?
```

---

## The Apps

Newton Workstation gives you visual tools. No coding required.

### Calculator
Enter any calculation. Get a verified result with proof.

```
Input:  1247.50 × 3
Output: 3742.50 ✓

Proof: N2_calc_8a3f2b...
```

### Verifier
Check if any text is safe before using it.

```
Input:  "How do I protect my network?"
Output: 🟢 GREEN - Verified safe

Content: ✓ Safe
Signal:  ✓ Crystalline
```

### Canvas
Describe what you want. Newton draws it.

```
Prompt: "A simple flowchart showing login process"
Output: [SVG diagram with verified content]
```

### Ask
Just ask anything. Newton handles the rest.

```
You: "Plan a trip to Japan for 2 weeks"
Newton: "I've extracted these constraints:
        • destination = Japan
        • duration = 14 days
        • Need: flights, hotels, activities

        Would you like me to create a detailed plan?"
```

---

## For Developers

### Quick API Test

```bash
# Verify text
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, how are you?"}'

# Use the Clipper
curl -X POST https://api.parcri.net/clip \
  -H "Content-Type: application/json" \
  -d '{"request": "Help me with security"}'

# Calculate with proof
curl -X POST https://api.parcri.net/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "multiply", "a": 100, "b": 25}}'
```

### Python SDK

```python
from newton_sdk import Newton

newton = Newton()

# Ask anything
response = newton.ask("What's the capital of France?")
print(response.answer)  # "Paris"
print(response.proof)   # "N2_8a3f..."

# Clip a request
clip = newton.clip("Write about dangerous topics")
if clip.state == "yellow":
    print("Here's what I can do:", clip.clipped_request)

# Verified calculation
result = newton.calculate("1247.50 * 3")
print(result.value)  # 3742.50
print(result.verified)  # True
```

---

## Key Concepts

### Constraints
Rules that define what Newton can do. Like:
- "Budget must be under $5000"
- "No harmful content"
- "Trip must be in December"

Newton extracts these from natural language automatically.

### Verification
Every Newton response is checked against constraints. If it passes, you get a cryptographic proof.

### Clipping
When part of your request is outside constraints, Newton "clips" to the boundary - finding the valid portion and offering that instead.

### Proofs
Every operation generates a fingerprint. This proves:
- What was requested
- When it was processed
- That it passed verification

---

## What Newton Can Do

| Task | App | Endpoint |
|------|-----|----------|
| Answer questions | Ask | `/ask` |
| Verify safety | Verifier | `/verify` |
| Find valid portion | Clipper | `/clip` |
| Calculate with proof | Calculator | `/calculate` |
| Draw diagrams | Canvas | `/cartridge/visual` |
| Plan trips/events | Planner | `/extract` |
| Store secrets | Vault | `/vault/store` |
| Generate lessons | Education | `/education/lesson` |
| Voice interaction | Voice | `/voice/ask` |

---

## Getting Help

- **Docs:** `/docs` on the API
- **API Reference:** `api-reference.md`
- **Workstation Guide:** `NEWTON_WORKSTATION.md`
- **Technical Deep-Dive:** `WHITEPAPER.md`

---

## The Philosophy

Newton is built on one principle:

> **The constraint IS the instruction.**

When you say "plan a trip for under $5000", Newton doesn't just hear a request. It extracts:
- `budget <= 5000`
- `type = trip`

Then it **verifies** that any plan it creates satisfies those constraints.

No guessing. No hallucinating. Just verified computation.

---

*© 2026 Ada Computing Company · Houston, Texas*

*"1 == 1. The cloud is weather. We're building shelter."*
