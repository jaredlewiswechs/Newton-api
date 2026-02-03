# Nina Architecture Report

> **Nina**: Newton Intelligence and Natural Assistant  
> A contemporary reimagining of the Apple Newton MessagePad (1993-1998)  
> Built on verified computation substrate

---

## Build Report (Live)

| Component | Status | Tests | Notes |
|-----------|--------|-------|-------|
| Architecture | ✅ | - | This document |
| Consumer UI | 🔄 | - | PDA interface |
| Developer Forge | 🔄 | - | Verification tools |
| Regime System | ⏳ | ⏳ | From paper Section 10.1 |
| Distortion Metric | ⏳ | ⏳ | D(w,a) = d(v(a), g(w)) |
| Trust Lattice | ⏳ | ⏳ | IFC upgrade mechanism |
| Pipeline | ⏳ | ⏳ | 9-stage compiler |

---

## 1. Design Philosophy

### Apple Newton (1993)
- Notes, Names, Dates core apps
- Handwriting recognition (famously problematic)
- NewtonScript programming language
- "Soup" data storage
- First device to be called a "PDA"

### Nina (2026)
- **Verification-first**: Every input verified before commit
- **Regime-aware**: Context determines what's admissible
- **Proof-relevant**: Answers include derivation traces
- **Kinematic**: Language treated as geometry

---

## 2. Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────┐
│                         NINA                                     │
├─────────────────────────────┬───────────────────────────────────┤
│     CONSUMER (nina-pda)     │      DEVELOPER (nina-forge)       │
├─────────────────────────────┼───────────────────────────────────┤
│  📝 Notes                   │  🔧 Regime System                 │
│  👥 Names                   │  📐 Distortion Metric             │
│  📅 Dates                   │  🔒 Trust Lattice                 │
│  🔢 Calculator              │  ⚙️ Compiler Pipeline              │
│  ✓ Verify                   │  🧪 Test Suite                    │
├─────────────────────────────┼───────────────────────────────────┤
│  HTML/CSS/JS                │  Python                           │
│  Touch/Voice Input          │  CLI/API                          │
│  Visual Feedback            │  Formal Verification              │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## 3. File Structure

```
nina/
├── ARCHITECTURE.md          # This file (build report)
├── README.md                # User documentation
│
├── consumer/                # CONSUMER-FACING (nina-pda)
│   ├── index.html          # Main PDA interface
│   ├── styles/
│   │   └── nina-pda.css    # PDA styling
│   └── scripts/
│       ├── nina-pda.js     # Main app controller
│       └── apps/
│           ├── notes.js    # Notes application
│           ├── names.js    # Contacts application
│           ├── dates.js    # Calendar application
│           ├── calc.js     # Calculator
│           └── verify.js   # Verification assistant
│
├── developer/               # DEVELOPER-FACING (nina-forge)
│   ├── __init__.py
│   ├── forge/              # Core verification engine
│   │   ├── __init__.py
│   │   ├── regime.py       # Regime system (Section 10.1)
│   │   ├── distortion.py   # Distortion metric (Section 10.2)
│   │   ├── trust.py        # Trust lattice (Section 7)
│   │   └── pipeline.py     # Compiler pipeline (Section 10.3)
│   └── sdk/
│       └── nina_sdk.py     # Developer SDK
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_regime.py
│   ├── test_distortion.py
│   ├── test_trust.py
│   └── test_pipeline.py
│
└── server.py               # Development server
```

---

## 4. Theoretical Foundation (from Paper)

### 4.1 Regime System (Section 10.1)
```
R = (domain_rules, authority, ambiguity_tolerance, ...)
```
A regime parameterizes admissibility - effectively a mode-dependent type/effect environment.

### 4.2 Distortion Metric (Section 10.2)
```
D(w, a) = d(v(a), g(w))

where:
  g(w) = glyph-derived mechanical signature of word/command
  v(a) = physics/action vector of actual commanded behavior
  d    = metric or divergence function
```

**Rule (GeometryMismatchError):**
If D(w,a) > θ(R), reject as inadmissible and suggest alternatives.

### 4.3 Trust Lattice (Section 7)
```
UNTRUSTED ⊏ TRUSTED

Policy:
- No implicit cast UNTRUSTED → TRUSTED
- upgrade(y) allowed iff Verify(y) = true
```

### 4.4 Compiler Pipeline (Section 10.3)
1. Intent Lock (choose regime R)
2. Parse (shape grammar / kinematic query parsing)
3. Abstract Interpretation (semantic field resolution)
4. Geometric Check (glyph/vector admissibility under R)
5. Verify/Upgrade (trust lattice)
6. Execute under bounds
7. Log provenance
8. Meta-check invariants
9. Return (value, trace)

---

## 5. API Contracts

### Consumer → Developer Bridge

```javascript
// Consumer calls developer verification
const result = await NinaForge.verify({
  input: "What is the capital of France?",
  regime: "factual",
  bounds: { timeout_ms: 1000 }
});

// Returns
{
  value: "Paris",
  trace: [...],
  trust_label: "TRUSTED",
  bounds_report: { ops: 42, time_ms: 12 },
  ledger_proof: "0x..."
}
```

### Developer Forge API

```python
from nina.developer.forge import Regime, Pipeline, TrustLabel

# Create a regime
regime = Regime(
    domain="factual",
    authority="knowledge_base",
    ambiguity_tolerance=0.1,
    distortion_threshold=0.3
)

# Run pipeline
result = Pipeline(regime).process("What is 2+2?")
assert result.trust_label == TrustLabel.TRUSTED
```

---

## 6. Test Strategy

| Test File | Coverage |
|-----------|----------|
| test_regime.py | Regime creation, switching, constraints |
| test_distortion.py | D(w,a) metric, threshold rejection |
| test_trust.py | Upgrade rules, label propagation |
| test_pipeline.py | End-to-end 9-stage pipeline |

---

## 7. Changelog

- **2026-02-03**: Initial architecture, consumer/developer separation defined

---

*Nina: Verification is the feature.*
