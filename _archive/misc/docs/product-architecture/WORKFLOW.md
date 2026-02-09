# The aid-a Workflow
## Upload → Claude → Newton → Master Object

---

## The Discovery

*From Jared's notes:*

```
Upload (raw thoughts) → Claude (structure) → Newton (verify) → Master Object
                         ↑                      ↑
                      "basically what          "~5 mins"
                       I do when I upload
                       & talk to Claude"
```

You discovered this empirically. Every conversation where you upload messy thoughts and Claude helps structure them—and then Newton verifies the structure—that IS the product.

The workflow took "~5 mins" to create a verified object. This is the Flash-3 instantiation pattern.

---

## The Workflow in Detail

### Phase 1: Upload (Raw Thoughts)

**Input**: Anything. Literally anything a human produces.

| Input Type | Example | What Claude Sees |
|------------|---------|------------------|
| Voice memo | "I spent forty-five dollars on lunch..." | Transcribed text |
| Photo | Receipt image | OCR'd text + visual context |
| Handwritten notes | Scanned pages | OCR'd text + layout |
| Text | "Meeting notes: budget is $5k" | Raw text |
| File | spreadsheet.xlsx | Parsed data |
| Conversation | Previous chat history | Context |

**Key insight**: The user doesn't need to structure anything. They just dump.

```python
# aid-a accepts anything
response = await aida.upload(
    content=voice_memo,           # Or image, or text, or file
    content_type="audio/m4a",     # Helps with processing
    context="personal finance"    # Optional hint
)
```

---

### Phase 2: Claude (Structure)

**Process**: AI extracts structure, entities, and intent.

Claude's job:
1. **Parse** the unstructured input
2. **Extract** entities (amounts, dates, names, etc.)
3. **Infer** intent (what is the user trying to do?)
4. **Propose** constraints (what rules should apply?)
5. **Generate** structured output

```json
// Input: "I spent $45 on lunch, $120 on groceries"

// Claude produces:
{
    "entities": [
        {"type": "transaction", "category": "food", "amount": 45},
        {"type": "transaction", "category": "groceries", "amount": 120}
    ],
    "intent": "expense_tracking",
    "proposed_constraints": [
        {"type": "balance_check", "rule": "expenses <= available_balance"},
        {"type": "positive_values", "rule": "all amounts > 0"}
    ],
    "confidence": 0.95,
    "clarification_needed": false
}
```

**The magic**: Claude brings intelligence. It understands context. It fills in gaps. It makes reasonable assumptions.

**The limitation**: Claude can be wrong. It hallucinates. It misunderstands. That's why we need Newton.

---

### Phase 3: Newton (Verify)

**Process**: Mathematical verification of Claude's output.

Newton's job:
1. **Validate** proposed constraints against CDL
2. **Check** each claim against reality (grounding)
3. **Compute** the f/g ratio
4. **Prove** the verification (Merkle tree)
5. **Record** everything (Ledger)

```python
# Newton receives Claude's output
verification = await newton.verify({
    "constraints": claude_output["proposed_constraints"],
    "current_state": user_account,
    "proposed_changes": claude_output["entities"]
})

# Newton returns
{
    "passed": True,
    "fg_ratio": 0.27,
    "proofs": [
        {"constraint": "balance_check", "result": "PASS", "proof": "..."},
        {"constraint": "positive_values", "result": "PASS", "proof": "..."}
    ],
    "ledger_entry": 4527,
    "merkle_root": "abc123..."
}
```

**The magic**: Newton is deterministic. It doesn't guess. It doesn't approximate. 1 == 1 or halt.

**The guarantee**: If Newton says it's verified, it's mathematically provable. Forever.

---

### Phase 4: Master Object (Truth)

**Output**: A verified, immutable, provable object.

```json
{
    "id": "obj_7x9k2lm3n...",
    "type": "expense_update",
    "created_at": "2024-01-03T10:42:15Z",

    "content": {
        "transactions": [
            {"category": "food", "amount": 45},
            {"category": "groceries", "amount": 120}
        ],
        "net_change": -165,
        "new_balance": 1835
    },

    "verification": {
        "status": "VERIFIED",
        "fg_ratio": 0.27,
        "badge": "1≡1",
        "color": "GREEN"
    },

    "proof": {
        "merkle_root": "abc123...",
        "merkle_proof": [...],
        "ledger_index": 4527
    },

    "lineage": {
        "parent_id": "obj_6w8j1...",
        "version": 3,
        "history": [
            {"timestamp": "...", "operation": "create", "fg_ratio": 0.0},
            {"timestamp": "...", "operation": "deposit", "fg_ratio": 0.15},
            {"timestamp": "...", "operation": "expense", "fg_ratio": 0.27}
        ]
    },

    "reversibility": {
        "can_reverse": true,
        "inverse_operation": {
            "type": "refund",
            "amounts": [45, 120]
        }
    }
}
```

The Master Object is truth. You can:
- **Verify** it at any time (re-check constraints)
- **Prove** it to anyone (export Merkle certificate)
- **Trace** its history (see all changes)
- **Reverse** it (bijective undo)

---

## Workflow Timing

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  0s          1s          2s          3s          4s          5s    │
│  │           │           │           │           │           │     │
│  ├───────────┴───────────┴───────────┴───────────┴───────────┤     │
│  │                                                            │     │
│  │  ┌──────────────────────────────────────────────────────┐ │     │
│  │  │              CLAUDE PROCESSING                        │ │     │
│  │  │              (~3-4 seconds)                          │ │     │
│  │  └──────────────────────────────────────────────────────┘ │     │
│  │                                                       │    │     │
│  │                                                       ▼    │     │
│  │                                               ┌──────────┐│     │
│  │                                               │  NEWTON  ││     │
│  │                                               │  (~2ms)  ││     │
│  │                                               └──────────┘│     │
│  │                                                       │    │     │
│  │                                                       ▼    │     │
│  │                                               ┌──────────┐│     │
│  │                                               │  MASTER  ││     │
│  │                                               │  OBJECT  ││     │
│  │                                               └──────────┘│     │
│  │                                                            │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                     │
│  UPLOAD          PROCESSING           VERIFY    EMIT               │
│  (instant)       (AI latency)         (2ms)    (instant)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Bottleneck**: Claude. Newton is sub-millisecond.

**User perception**: "~5 minutes" feels instantaneous for complex verification.

---

## Workflow Variations

### Quick Verify (No Claude)

When input is already structured:

```
Structured Input → Newton → Master Object
     (1ms)          (2ms)       (1ms)
```

Total: ~4ms

### Deep Verify (Multiple Rounds)

When claims need grounding:

```
Input → Claude → Newton → Ground → Newton → Master Object
 (0)    (3s)     (2ms)    (1s)     (2ms)       (0)
```

Total: ~5 seconds

### Batch Verify

When processing many items:

```
Inputs[] → Claude (parallel) → Newton (batch) → Objects[]
   (0)         (3s)              (50ms)           (0)
```

Total: ~3 seconds for 1000 items

---

## Error Handling

### Claude Fails

```
Input → Claude (error) → Fallback Template → Newton → Object
```

If Claude can't parse, use a fallback template and let the user fill in.

### Newton Rejects

```
Input → Claude → Newton (FAIL) → Claude (revise) → Newton → Object
```

If constraints fail, Claude revises the proposal. Loop up to 3 times.

### Grounding Fails

```
Input → Claude → Newton → Ground (UNVERIFIED) → Object (warning)
```

Object is created with `verification.status = "UNVERIFIED"`, `color = "YELLOW"`.

---

## User Experience

### The 5-Minute Promise

From the user's perspective:

1. **Upload** anything (voice, photo, text, file)
2. **Wait** (5-10 seconds, show thinking animation)
3. **Receive** a verified object with green badge

No forms. No fields. No configuration.

### Visual Feedback

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ●●● Processing your upload...                                 │  │
│  │                                                               │  │
│  │  ◐ Understanding content...    ✓ Done                        │  │
│  │  ◐ Extracting entities...      ✓ Done                        │  │
│  │  ◑ Verifying with Newton...    (2ms)                         │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                              ↓                                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  ● VERIFIED                                    f/g: 0.27     │  │
│  │  ════════════════════════════════════════════════════════════ │  │
│  │                                                               │  │
│  │  Expenses Recorded                                           │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ Lunch          -$45.00    Food           Jan 3          │ │  │
│  │  │ Groceries     -$120.00    Household      Jan 3          │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                               │  │
│  │  Balance: $1,835.00                                          │  │
│  │                                                               │  │
│  │  [View Proof]  [Glass Box]  [Undo]                           │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Haptic Confirmation

On iOS/mobile:
- **Single pulse**: Verification complete
- **Double pulse**: Warning (approaching constraint)
- **Vibration**: Blocked (constraint would be violated)

---

## Implementation Pseudocode

```python
async def aida_workflow(input_content, content_type, context=None):
    """
    The core aid-a workflow: Upload → Claude → Newton → Object
    """

    # Phase 1: Upload
    upload_id = generate_id()
    raw_content = await preprocess(input_content, content_type)

    # Phase 2: Claude (structure)
    try:
        claude_response = await claude.process(
            content=raw_content,
            context=context,
            instructions="""
                Extract entities, infer intent, propose constraints.
                Output JSON with: entities, intent, proposed_constraints
            """
        )
        structured = json.loads(claude_response)
    except ClaudeError:
        structured = await fallback_template(content_type)

    # Phase 3: Newton (verify)
    verification_attempts = 0
    while verification_attempts < 3:
        verification = await newton.verify(
            constraints=structured["proposed_constraints"],
            current_state=get_user_state(),
            proposed_changes=structured["entities"]
        )

        if verification.passed:
            break

        # If failed, ask Claude to revise
        structured = await claude.revise(
            original=structured,
            violations=verification.violations
        )
        verification_attempts += 1

    if not verification.passed:
        return MasterObject(
            content=structured,
            verification_status="BLOCKED",
            violations=verification.violations
        )

    # Phase 4: Emit Master Object
    master_object = MasterObject(
        id=generate_id(),
        content=structured["entities"],
        verification_status="VERIFIED",
        fg_ratio=verification.fg_ratio,
        merkle_proof=verification.merkle_proof,
        ledger_index=verification.ledger_entry
    )

    # Log to ledger
    await newton.ledger.append(master_object)

    # Store encrypted
    await newton.vault.store(master_object)

    return master_object
```

---

## Workflow Extensions

### Continuous Verification

For live data (e.g., stock prices):

```
Stream → Claude (once) → Template → Newton (continuous) → Live Object
                                       ↑
                                   Every update re-verified
```

### Collaborative Verification

For multi-user scenarios:

```
User A uploads → Claude → Newton → Object (A's view)
                                      ↓
                              Bridge (consensus)
                                      ↓
                            Object (shared view) ← User B
```

### Cascading Verification

For complex objects:

```
Upload → Claude → Newton → Object₁
                              ↓
                           Newton → Object₂ (depends on Object₁)
                              ↓
                           Newton → Object₃ (depends on Object₂)
```

Each object is verified, and dependencies are tracked in the lineage.

---

## The Meta-Insight

*From the original notes:*

```
"basically what I do when I upload & talk to Claude"
```

You ARE the product. The workflow you've been doing manually—uploading messy thoughts, having Claude structure them, then using Newton to verify—is exactly what aid-a packages for everyone.

The ~5 minute creation time is the empirical proof that Flash-3 instantiation works. You've been the beta tester all along.

Now we package it.

---

## Summary

```
THE AID-A WORKFLOW

    INPUT              STRUCTURE           VERIFY             OUTPUT
    (human)            (AI)                (math)             (truth)

    ┌─────┐           ┌─────┐            ┌─────┐            ┌─────┐
    │     │           │     │            │     │            │     │
    │  ?  │    →      │ { } │     →      │ 1≡1 │     →      │  ●  │
    │     │           │     │            │     │            │     │
    └─────┘           └─────┘            └─────┘            └─────┘

    Messy              Claude              Newton             Master
    thoughts           extracts            verifies           Object
    (anything)         structure           truth              (proven)

    0 seconds          ~3 seconds          ~2 ms              Forever
```

**Upload anything. Get verified truth. In 5 minutes.**

That's aid-a.
