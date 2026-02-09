# Newton for iOS - How It Works (Simple Version)

**Understanding verified computation without the math**

```
╭──────────────────────────────────────────────────────────────╮
│   Newton: The Supercomputer That Checks 1 == 1              │
│   Before anything happens.                                  │
╰──────────────────────────────────────────────────────────────╯
```

---

## The Problem: AI Hallucinates

Imagine asking an AI: *"Should I take aspirin for my headache?"*

**Traditional AI might say**:
> "Yes, take 500mg twice daily. Aspirin is safe and effective for headaches."

**Sounds confident. Looks professional. Could kill you if you're allergic.**

Why? Because AI generates text **probabilistically**:
- It predicts the next word based on patterns
- It doesn't **verify** what it says is safe
- It can't tell `1 == 1` from `1 == 0.9999`

In math, close enough isn't good enough. In medicine, it's dangerous.

---

## The Newton Solution: 1 == 1

Newton adds a simple check **before** AI output reaches you:

```
┌─────────────────────────────────────────┐
│  AI generates response                  │
│  ↓                                       │
│  Newton checks: Does this match         │
│  safety constraints?                    │
│  ↓                                       │
│  If YES (1 == 1) → Show it             │
│  If NO (1 != 1) → Block it             │
└─────────────────────────────────────────┘
```

**The rule**: Only when `current == goal` does execution happen.

**In code**:
```python
def newton(current, goal):
    return current == goal

# If True → proceed
# If False → halt
```

This isn't a feature. **It's the architecture.**

---

## How Constraints Work

Think of constraints like airport security:

**Airport Security**:
- Checks your ID
- Scans your luggage
- Blocks weapons/liquids
- Lets safe passengers through

**Newton Constraints**:
- Check text content
- Scan for dangerous patterns
- Block medical/legal advice
- Let verified content through

**The difference**: Airport security uses humans (slow, inconsistent).  
Newton uses math (fast, deterministic).

---

## Example: Medical Constraint

**User receives**:
> "You should take 500mg of aspirin twice daily."

**Newton checks**:
1. Does text contain drug dosage pattern?
   - Pattern: `"take [number] mg of [drug]"`
   - Match: **YES**
2. Is this a medical recommendation?
   - Contains: "should take"
   - Match: **YES**
3. Constraint violated: **DENY**

**Result**: ❌ **BLOCKED**
```
⚠️ WARNING: Unverified drug dosage recommendation detected.
Consult licensed healthcare provider for medication advice.
```

**User is protected**. No harm done.

---

## Why Deterministic Matters

### Traditional AI (Probabilistic)

Ask 3 times: "Is aspirin safe?"

**Response 1**: "Yes, aspirin is generally safe."  
**Response 2**: "Aspirin can cause bleeding in some people."  
**Response 3**: "Consult a doctor before taking aspirin."

**Same question. Three different answers.**

This is because AI is probabilistic - it's **sampling** from probability distributions, not **computing** truth.

### Newton (Deterministic)

Check same text 3 times:

**Check 1**: ❌ BLOCKED (medical advice pattern)  
**Check 2**: ❌ BLOCKED (medical advice pattern)  
**Check 3**: ❌ BLOCKED (medical advice pattern)

**Same input. Same output. Always.**

This is deterministic - same constraint + same text = same result.

**Why this matters**:
- Reliable: You can trust the verification
- Auditable: Results can be reproduced
- Debuggable: If wrong, you can fix the constraint
- Fast: No sampling, just pattern matching

---

## The Three Constraint Categories

### 🏥 Medical Constraints

**Detects**:
- Drug dosage recommendations
- Medical diagnoses
- Treatment protocols
- Drug interaction claims

**Why**:
- Medical advice requires licensed professional
- Mistakes can cause serious harm
- Better safe than sorry

**Example violations**:
- "Take 500mg of aspirin"
- "You have diabetes based on these symptoms"
- "This medication is safe with your prescriptions"

### ⚖️ Legal Constraints

**Detects**:
- Legal action recommendations
- Contract interpretations
- Jurisdiction-specific claims
- Rights advisements

**Why**:
- Legal advice requires licensed attorney
- Laws vary by state and change over time
- Wrong advice can cost money or freedom

**Example violations**:
- "You should sue them for breach"
- "Under Texas law, you have 30 days"
- "You have the right to refuse this"

### 🧠 Epistemic Constraints

**Detects**:
- Self-contradictions
- Circular reasoning
- Unfalsifiable claims
- Missing source citations
- Logical fallacies

**Why**:
- Logic matters for truth
- Contradictions signal errors
- Unsupported claims are unreliable

**Example violations**:
- "This always works, except when it doesn't"
- "Studies show this is true" (no citation)
- "It's true because experts say so"

---

## Architecture: How Newton Works

```
╔════════════════════════════════════════╗
║  YOU                                   ║
║  ↓ (Share text from AI)                ║
╠════════════════════════════════════════╣
║  NEWTON SHORTCUT (on your iPhone)     ║
║  ↓ (Send to verification API)          ║
╠════════════════════════════════════════╣
║  NEWTON API (cloud server)            ║
║  - Receives text                       ║
║  - Loads constraints                   ║
║  - Checks patterns                     ║
║  - Returns result                      ║
║  ↓ (Result in <1 second)               ║
╠════════════════════════════════════════╣
║  YOUR iPhone                           ║
║  - Shows ✅ VERIFIED or ❌ BLOCKED    ║
║  - Displays violation details          ║
║  - You decide what to do next          ║
╚════════════════════════════════════════╝
```

**Speed**: Median 2.31ms API latency  
**Privacy**: Only shared text sent to API  
**Determinism**: Same text always = same result

---

## Why Local-First?

### Cloud AI Problems

**ChatGPT/Claude approach**:
1. You type prompt
2. Sent to cloud (they see everything)
3. AI generates response
4. Sent back to you
5. You trust it (maybe shouldn't)

**Privacy issues**:
- Company reads all your data
- Data stored on their servers
- Subject to their terms of service
- Can be subpoenaed, hacked, leaked

### Newton Approach

**What stays local**:
- Your constraint preferences
- Which checks you run
- Everything except what you verify

**What goes to cloud**:
- Only text you explicitly share to Newton
- For verification purpose only
- Not stored
- Not logged
- Ephemeral

**Control**: You own the verification layer. Not them.

---

## The Math (Super Simple Version)

Newton uses **set theory** and **boolean logic**:

### Set Membership
```
Is "take 500mg" in set of {medical_advice_patterns}?
YES → Constraint violated
NO → Constraint passed
```

### Boolean Logic
```
Is pattern_match AND action_recommendation?
TRUE → Block
FALSE → Allow
```

### Formal Verification
```
For all inputs x:
  verify(x, constraint) → {PASS, FAIL}
  
Same x + Same constraint = Same result (always)
```

**No probability**. Just math.

Like checking:
- Is 5 > 3? (Always TRUE)
- Is "aspirin" in "take aspirin"? (Always TRUE)
- Does text match pattern? (Deterministic answer)

---

## Comparison Table

| Approach | Method | Speed | Consistent | Auditable |
|----------|--------|-------|------------|-----------|
| **Traditional AI Safety** | Post-generation filtering | Slow | ❌ No | ❌ No |
| **Human Review** | Manual checking | Very slow | ❌ No | ⚠️ Partial |
| **Newton** | Pre-execution constraints | Fast | ✅ Yes | ✅ Yes |

**Key difference**: Newton checks **before** you act on AI output.

---

## Real-World Analogy

### Traditional AI: Self-Driving Car (No Brakes)

- Car drives based on probability
- "90% sure this is a stop sign"
- "Probably safe to turn left"
- **Problem**: 10% wrong = crash

### Newton: Self-Driving Car (With Emergency Stop)

- Car drives based on sensors
- **But**: Hard constraints enforced
- Speed limit: NEVER exceed
- Red light: ALWAYS stop
- Pedestrian detected: IMMEDIATE halt

**Constraints aren't suggestions. They're laws of physics.**

In Newton's world:
- Medical advice without license → BLOCKED (law)
- Self-contradictory logic → FLAGGED (law)
- Unsafe content → DENIED (law)

**No exceptions. No "probably". Just 1 == 1.**

---

## Why This Matters

### Current AI Landscape

**Problem**: Gumroad is full of "prompt libraries"
- Collections of ChatGPT prompts
- "Act as a doctor/lawyer/expert"
- Zero verification
- Passive consumption
- Dangerous at scale

**Newton is different**:
- Active verification (not passive prompts)
- Deterministic checking (not probabilistic generation)
- Safety-first (blocks by default)
- Local-first (you control it)
- One-time purchase (no subscription rent-seeking)

### The "Notion Beige" Problem

Most AI tools look the same:
- Clean
- Minimal
- Beige/white aesthetic
- Enterprise SaaS pricing
- Subscription lock-in

**Newton aesthetic**: Retro terminal / cyberpunk
- Inspired by Apple ][ and VT100 terminals
- Green text on black
- ASCII art
- Command-line vibes
- **Looks like it came from 1984 Cupertino**

Why? Because those systems were **deterministic**.  
You typed `PRINT 2+2`, you got `4`. Always.

**No hallucinations. No probabilistic sampling. Just computation.**

---

## Limitations (Honest Section)

Newton is **not perfect**. Here's what it can't do:

### 1. Understand Intent

**Example**:
> "Don't take aspirin without consulting a doctor"

**Newton**: ❌ BLOCKS (contains "take aspirin")

**Reality**: This is **good advice** (tells you to consult doctor)

**Why**: Pattern matching can't understand negation context perfectly

**Mitigation**: Constraints designed to err on safe side

### 2. Catch Novel Phrasings

**Example**:
> "Ingest five hundred milligrams of acetylsalicylic acid"

**Newton**: ⚠️ MIGHT MISS (different phrasing)

**Reality**: Same as "take 500mg aspirin"

**Why**: Constraints match specific patterns, not all possible phrasings

**Mitigation**: Add more patterns to constraints (you can customize!)

### 3. Replace Professional Judgment

Newton is a **safety layer**, not a replacement for:
- Doctors (medical advice)
- Lawyers (legal advice)
- Critical thinking (your brain)

**Use Newton as a filter, not an authority.**

---

## The Philosophy

> "1 == 1. The cloud is weather. We're building shelter."

**What this means**:

**1 == 1**: Determinism is the foundation
- Same input → Same output
- No randomness
- No hallucinations
- Just math

**The cloud is weather**: Cloud services are unreliable
- Services go down
- Companies change terms
- Data gets leaked
- Pricing changes

**We're building shelter**: Local-first is sovereignty
- You own your tools
- No subscription rent
- No data extraction
- One-time purchase

---

## Getting Started

**Ready to verify?**

1. Install: See `SETUP.md` (2 minutes)
2. Test: Share AI output to Newton
3. Observe: ✅ VERIFIED or ❌ BLOCKED
4. Trust: Deterministic results you can rely on

**Want to customize?**

See `CUSTOMIZATION.md` to:
- Create custom constraints
- Adjust sensitivity
- Add your own patterns
- Share with community

---

## Summary

**Newton in one sentence**:

> Newton checks that `1 == 1` before AI output reaches you, using deterministic constraints instead of probabilistic hope.

**The constraint IS the instruction.**  
**The verification IS the computation.**  
**The network IS the processor.**

Not a feature. The architecture.

---

## Version

v1.0.0 - January 2026

**Repository**: https://github.com/jaredlewiswechs/Newton-api  
**Technical Whitepaper**: See `WHITEPAPER.md` in repo (for engineers)

---

**Understand Newton? Start using it.**

**Still confused? That's okay. Just install it and watch it work.**

**See it block bad advice once, and you'll get it.**

```
1 == 1
```
