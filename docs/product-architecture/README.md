# aid-a Product Architecture Documentation

*"The intersection of technology and liberal arts."* — Steve Jobs

---

## Overview

This documentation captures the product architecture vision for **aid-a**, Newton's consumer-facing layer. It was created in the voice of Steve Jobs (product vision) and Jony Ive (design principles).

---

## Documents

### 1. [AID-A_PRODUCT_VISION.md](./AID-A_PRODUCT_VISION.md)
The complete product vision, including:
- Steve's keynote (the pitch)
- Jony's design studio (the craft)
- Technical architecture
- One-page investor summary

### 2. [DESIGN_PRINCIPLES.md](./DESIGN_PRINCIPLES.md)
Jony Ive's design principles for aid-a:
- Verification as interface
- Silence as confidence
- Reversibility as reassurance
- Color as mathematics
- The f/g visual language

### 3. [FG_VISUAL_LANGUAGE.md](./FG_VISUAL_LANGUAGE.md)
Complete specification for the f/g ratio visualization:
- The glyph design
- Color specification
- Animation patterns
- Haptic feedback
- Platform implementations (iOS, Web, React)

### 4. [AID-A_STACK.md](./AID-A_STACK.md)
The vertical integration architecture:
- Layer 0: tinyTalk / Laws
- Layer 1: Newton Core
- Layer 2: Newton API
- Layer 3: aid-a Layer
- Layer 4: Consumer Apps
- Layer 5: Newton OS

### 5. [WORKFLOW.md](./WORKFLOW.md)
The core workflow documentation:
- Upload → Claude → Newton → Master Object
- Timing analysis
- User experience
- Implementation pseudocode

### 6. [MORPHIC_TO_NEWTON_EVOLUTION.md](./MORPHIC_TO_NEWTON_EVOLUTION.md)
The intellectual lineage from Morphic to Newton:
- Morphic's direct manipulation paradigm (Self/Squeak, 1990s)
- The evolution from "manipulate visible objects" to "manipulate verified objects"
- Generation mapping: Smalltalk → Morphic → Squeak → Scratch → Newton
- How Newton solves Morphic's "corruption problem"
- The Dynabook with proof

### 7. [BILL_ATKINSON_EXPLAINS_DRAWING.md](./BILL_ATKINSON_EXPLAINS_DRAWING.md)
Bill Atkinson's philosophy of verified strokes:
- The stroke IS the verification
- Touch as truth
- MacPaint to Newton

---

## The Core Insight

From Jared's original notes:

```
Upload (raw thoughts) → Claude (structure) → Newton (verify) → Master Object
                         ↑                      ↑
                      "basically what          "~5 mins"
                       I do when I upload
                       & talk to Claude"
```

**You discovered aid-a empirically.** The workflow you've been doing manually—uploading messy thoughts, having Claude structure them, using Newton to verify—IS the product.

---

## Quick Reference

### The Equation
```
f/g < threshold  → ALLOWED (green)
f/g ≈ threshold  → WARNING (amber)
f/g ≥ threshold  → FORBIDDEN (red)
g ≈ 0            → finfr (undefined)
```

### The Badge
```
1 ≡ 1
```
When you see this badge, the constraint has passed. Newton has verified. It's mathematically proven.

### The Promise
**Upload anything. Get verified truth. In 5 minutes.**

---

## Product Lineup

| Product | Target | Description |
|---------|--------|-------------|
| **aid-a Core** | Everyone | Upload → verify → object |
| **aid-a Glass Box** | Enterprise | Full transparency, audit trails |
| **aid-a Forge** | Developers | SDKs for verified apps |
| **Newton OS** | Future | Verification at the kernel |

---

## Status

- **Vision**: Documented
- **Architecture**: Designed
- **Core modules**: Implemented (162+ tests passing)
- **Consumer products**: In development

---

*"Stay hungry. Stay foolish. Stay verified."*
