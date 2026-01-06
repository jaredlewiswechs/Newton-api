# Geometric Constraint Semantics

**Human constraint verification happens geometrically before semantically.**

---

## Core Thesis

Newton's constraints are written by humans and must be verified by humans. The geometry of symbols carries cognitive load before meaning is parsed. This document formalizes the relationship between glyph shapes and constraint semantics to ensure notation design is part of system correctness.

```
TRADITIONAL PATH:
  Symbol → Parse → Understand Meaning → Verify

ACTUAL COGNITIVE PATH:
  Symbol → Recognize Shape → Feel Correctness → Parse → Verify

Newton optimizes for the actual path.
```

---

## Part I: The Embeddings Distinction

### What Newton Is Not

Modern AI systems convert everything into numerical embeddings—768-dimensional vectors where relationships become cosine similarities in abstract space. This approach captures statistical patterns rather than mathematical proofs. A language model can generate plausible responses that violate logical constraints because embeddings represent "likely given training data" rather than "verified as logically valid."

### What Newton Is

Newton's architecture begins with **geometric constraints** and proceeds through **verification of spatial relationships**. These are mathematically dual approaches:

| Embeddings Paradigm | Geometric Paradigm |
|---------------------|-------------------|
| Numerical vectors | Spatial structures |
| Probability distributions | Constraint boundaries |
| Cosine similarity | Set membership |
| Gradient descent optimization | Boundary verification |
| "Approximately correct" | "Provably satisfies" |

The f/g ratio is not a numerical score to be optimized. It is a geometric relationship that either remains within valid bounds or enters the finfr state.

### Why This Matters

A shape either satisfies spatial constraints or it does not. A polygon either closes or it does not. An intersection either exists or it does not. These are **decidable properties** that can be verified mathematically rather than approximated statistically.

```
Embeddings: "This text is 0.87 similar to compliant text"
Newton:     "This state is inside the feasible polytope" or "finfr"
```

---

## Part II: Geometric Primitives in Glyphs

Every character humans read contains geometric information that the visual cortex processes before the language center engages. Newton's notation leverages this by aligning glyph geometry with semantic intent.

### The Seven Primitives

#### 1. Closed Forms (o, O, 0, @, Q)

```
Geometric Property: Complete enclosure
Cognitive Signal:   Wholeness, boundedness, cycle completion
Constraint Use:     Completeness checks, invariants, loops, containment

    ╭───╮
    │   │  ← Nothing escapes
    ╰───╯     Everything accounted for
```

**Semantic Mapping:**
- States that must remain intact
- Complete sets
- Invariant preservation
- Cyclic processes

#### 2. Open Curves (c, C, (, ), {, })

```
Geometric Property: Partial enclosure, directional opening
Cognitive Signal:   Flow, transition, partial state
Constraint Use:     State transitions, partial fulfillment, ranges

    ╭───
    │      ← Entry/exit point exists
    ╰───     Process in flight
```

**Semantic Mapping:**
- Boundaries with entry/exit
- Processes in progress
- Partial constraint satisfaction
- Range bounds (open on one side)

#### 3. Straight Lines (l, I, 1, |, -, =)

```
Geometric Property: No curvature, clear direction
Cognitive Signal:   Boundary, axis, binary choice
Constraint Use:     Thresholds, identity, equality, atomicity

    ─────────  ← Hard boundary
               No ambiguity
```

**Semantic Mapping:**
- Hard limits
- Binary states (true/false)
- Axes of measurement
- Equality assertions

#### 4. Intersections (x, X, +, *, t, T)

```
Geometric Property: Multiple paths meeting
Cognitive Signal:   Decision point, combination, choice
Constraint Use:     Branching logic, AND/OR operations, selection

        │
    ────┼────  ← Multiple paths converge
        │        Decision required
```

**Semantic Mapping:**
- Conditional branches
- Combination rules (AND/OR)
- Selection points
- Path convergence

#### 5. Hooks/Terminals (f, r, j, g, y)

```
Geometric Property: Direction change with endpoint
Cognitive Signal:   Action with resolution, grasping, termination
Constraint Use:     Actions, effects, finality, state capture

    ─┐
     │   ← Direction changes
     ╰     Something is caught/held
```

**Semantic Mapping:**
- Operations that conclude
- Terminal conditions
- State capture/freeze
- Finality markers

#### 6. Bridges (n, m, h, u, w)

```
Geometric Property: Connected strokes, continuation
Cognitive Signal:   Flow continuation, linking
Constraint Use:     Sequential operations, state propagation

    ╭─╮ ╭─╮
    │ │ │ │  ← Continuous connection
    │ ╰─╯ │     Flow maintains
```

**Semantic Mapping:**
- Chained conditions
- Sequential dependencies
- State propagation
- Continuation of process

#### 7. Points/Dots (i, j, !, ?, .)

```
Geometric Property: Minimal, atomic marker
Cognitive Signal:   Identity, emphasis, interrogation, termination
Constraint Use:     Atomic facts, assertions, queries, endpoints

    •  ← Singular
       Atomic
       Identity marker
```

**Semantic Mapping:**
- Atomic values
- Identity checks
- Singular points
- Termination marks

---

## Part III: Newton Keyword Analysis

### `when` — Conditional Entry

```
w: bridge (continuation)
h: bridge (linking)
e: open curve (entry)
n: bridge (continuation)
```

**Geometric Reading:** Multiple bridges with entry point

**Semantic Meaning:** "If this path exists, follow it"

**Alignment Score:** ✓ EXCELLENT

The shape suggests conditional flow—bridges that only activate if the entry curve permits passage.

### `and` — Constraint Combination

```
a: closed at top, open bottom (partial containment)
n: bridge (continuation)
d: closed loop with ascender
```

**Geometric Reading:** Containment + continuation + closure

**Semantic Meaning:** "Combine constraints, all must hold"

**Alignment Score:** ✓ GOOD

Bridges suggest linking multiple conditions; closure suggests completeness requirement.

### `fin` — Valid Completion

```
f: hook (action/forward)
i: point (atomic identity)
n: bridge (continuation)
```

**Geometric Reading:** Action → identity → continuation

**Semantic Meaning:** "Execute and proceed"

**Alignment Score:** ✓ GOOD

The continuation suggests valid states can flow forward. However, `fin` could feel like it continues rather than terminates.

### `finfr` — Ontological Impossibility

```
f: hook (action)
i: point (identity)
n: bridge (continuation attempt)
f: hook (action again)
r: terminal curve (resolution/turn back)
```

**Geometric Reading:** Action → identity → bridge → action → STOP/TURN

**Semantic Meaning:** "Tried to continue, hit wall, turned back"

**Alignment Score:** ✓✓ EXCELLENT

```
    f-i-n-f-r
    ↓ ↓ ↓ ↓ ↓
    try
      identity
        continue
          try again
            BLOCKED → turn back
```

**This is Newton's best geometric-semantic match.** The double hook with terminal turn perfectly encodes "attempted action that cannot continue." The shape **is** the meaning.

---

## Part IV: Constraint Naming Guidelines

### Rule 1: Match Shape to Semantic Structure

**For Containment Constraints** (must stay within bounds):

```
PREFER: quota, bound, pool, scope, dome, orbit
        (words with closed forms)

AVOID:  reject, limit, halt
        (words with terminals where closure is needed)
```

**For Sequential Constraints** (A then B then C):

```
PREFER: chain, then, when, run, flow, through
        (words with bridges)

AVOID:  switch, branch, split
        (words with intersections where flow is needed)
```

**For Terminal Conditions** (hard stops):

```
PREFER: halt, stop, fail, finfr, end, freeze
        (words with hooks/terminals)

AVOID:  continue, maintain, flow
        (words with bridges where termination is needed)
```

**For Identity/Equality**:

```
PREFER: is, id, one, this, same
        (words with straight lines and points)

AVOID:  seems, about, around
        (words with curves where precision is needed)
```

**For Choice Points**:

```
PREFER: or, xor, pick, switch, fork
        (words with intersections)

AVOID:  then, and, next
        (words with pure bridges where branching is needed)
```

### Rule 2: Visual Density = Computational Density

The visual weight of a word should match its computational complexity.

```
LIGHT WORDS (lots of whitespace): i, l, if, it, is
  Use for: Simple checks, atomic values, lightweight guards

MEDIUM WORDS: when, then, and, fin, check
  Use for: Standard constraints, common operations

HEAVY WORDS (dense geometry): finfr, proof, commit, transaction
  Use for: Complex state changes, system boundaries, terminal conditions
```

**Anti-patterns:**

```
❌ Using light word for heavy semantics:
   x → "complex transaction rollback procedure"

✓ Using appropriate weight:
   rollback → transaction reversal
   revert → state restoration
```

### Rule 3: Avoid Geometric Contradictions

Some English words have geometric structure that contradicts their meaning:

```
CONTRADICTORY ENCODING:

"open"  — feels closed (has closed loop in 'o')
"stop"  — has continuation bridge ('p' flows downward)
"flow"  — has terminal hook ('f')

ALIGNED ENCODING:

"halt"  — has terminal forms (h-hook, l-line, t-cross)
"pool"  — has closed loops (p-loop, oo-double closure, l-boundary)
"when"  — has bridges (w-double arch, n-arch)
```

---

## Part V: Font and Presentation Guidelines

Since Newton constraints are verified visually before being parsed semantically, typography directly impacts verification accuracy.

### Constraint Definition Source Code

```
RECOMMENDED: SF Mono, Menlo, JetBrains Mono, Fira Code

PROPERTIES REQUIRED:
  - High geometric clarity
  - Strong distinction between closed/open forms
  - Clear terminals on hooks (f, r, j, g, y)
  - Consistent stroke weight
  - Distinct 0/O, 1/l/I, rn/m differentiation
```

**Why Monospace:** Each character occupies equal space, making geometric patterns scannable at consistent rhythm.

### f/g Ratio Display

```
RECOMMENDED: SF Pro Rounded, Inter, Roboto

PROPERTIES REQUIRED:
  - Geometric number forms (0-9 with clear closure)
  - Strong visual weight for ratios
  - Smooth curves reinforce "within bounds" feeling
  - Clear decimal alignment
```

### Status Text (Green/Yellow/Red Indicators)

```
RECOMMENDED: SF Pro Text (medium weight), Inter (medium)

PROPERTIES REQUIRED:
  - Clear at small sizes (12-14px)
  - Geometric consistency with ratio display
  - Pairs well with color encoding
```

### Color-Geometry Integration

The existing f/g visual language maps colors to constraint states. Extend this with geometric reinforcement:

```
GREEN (f/g < 0.9θ) — VERIFIED
  Typography: Rounded, flowing forms
  Smooth curves suggest "within bounds"
  Closed shapes suggest "complete"

YELLOW (0.9θ ≤ f/g < θ) — WARNING
  Typography: Angular forms
  Intersections suggest "decision point"
  Hooks suggest "attention needed"

RED (f/g ≥ θ) — FORBIDDEN
  Typography: Sharp, terminal forms
  Hard edges suggest "boundary hit"
  Broken shapes suggest "cannot continue"

DEEP RED (g ≈ 0) — FINFR
  Typography: Heavy stroke, isolated
  Single X mark (intersection with no outlet)
  "Nothing possible here"
```

---

## Part VI: Geometric Linting

A constraint named contrary to its geometric semantics creates cognitive dissonance during human review. Newton should lint constraint names for geometric-semantic alignment.

### Specification

```python
# geometric_lint.py - Analyze constraint names for alignment

class GeometricFeatures:
    """Geometric analysis of a word's glyphs."""

    closed_forms: float      # 0.0-1.0, ratio of closed shapes
    open_curves: float       # 0.0-1.0, ratio of open curves
    straight_lines: float    # 0.0-1.0, ratio of straight elements
    intersections: float     # 0.0-1.0, ratio of crossing shapes
    hooks_terminals: float   # 0.0-1.0, ratio of terminal forms
    bridges: float           # 0.0-1.0, ratio of bridge shapes
    points: float            # 0.0-1.0, ratio of point/dot forms
    visual_density: str      # 'light', 'medium', 'heavy'

class SemanticType(Enum):
    CONTAINMENT = "containment"   # Must stay within bounds
    SEQUENTIAL = "sequential"     # A then B then C
    TERMINAL = "terminal"         # Hard stop
    IDENTITY = "identity"         # Equality check
    CHOICE = "choice"            # Branching decision

def lint_constraint_name(name: str, semantic_type: SemanticType) -> LintReport:
    """Check geometric-semantic alignment."""

    features = analyze_glyphs(name)
    warnings = []

    if semantic_type == SemanticType.CONTAINMENT:
        if features.closed_forms < 0.3:
            warnings.append(
                f"'{name}' suggests containment but lacks closed shapes. "
                f"Consider: quota, bound, pool, scope"
            )

    if semantic_type == SemanticType.TERMINAL:
        if features.hooks_terminals < 0.2:
            warnings.append(
                f"'{name}' suggests termination but lacks terminal forms. "
                f"Consider: halt, stop, finfr, end"
            )

    if semantic_type == SemanticType.SEQUENTIAL:
        if features.bridges < 0.3:
            warnings.append(
                f"'{name}' suggests sequence but lacks bridges. "
                f"Consider: chain, then, when, flow"
            )

    if semantic_type == SemanticType.IDENTITY:
        if features.straight_lines < 0.2 and features.points < 0.2:
            warnings.append(
                f"'{name}' suggests identity but lacks linear/point forms. "
                f"Consider: is, same, id, one"
            )

    if semantic_type == SemanticType.CHOICE:
        if features.intersections < 0.2:
            warnings.append(
                f"'{name}' suggests choice but lacks intersections. "
                f"Consider: or, fork, pick, switch"
            )

    return LintReport(name=name, warnings=warnings, features=features)
```

### Example Output

```
$ newton lint cartridge user_authentication.cdl

Analyzing constraint names...

✓ when_valid_token
  Type: sequential
  Features: bridges=0.6, open_curves=0.3
  Good: bridges suggest conditional flow

✓ token_expired
  Type: terminal
  Features: hooks=0.4, closed=0.3
  Good: terminal forms match finality

⚠ proceed_if_authorized
  Type: sequential
  Features: bridges=0.2, closed=0.4
  Warning: Heavy visual density for simple guard
  Suggest: auth_ok, has_auth, can_proceed

✓ finfr_invalid_session
  Type: terminal
  Features: hooks=0.6, bridges=0.3
  Excellent: terminal forms match impossibility

Summary: 3 passed, 1 warning, 0 errors
```

---

## Part VII: The Deep Implication

### Notation Design Is System Correctness

What this analysis reveals:

1. **Badly-named constraints cause cognitive dissonance** even when logically correct
2. **Geometric encoding affects debugging speed** — humans scan shapes before parsing meaning
3. **Visual presentation affects error rates** — misaligned geometry → misread constraints
4. **Typography choices impact verification accuracy** — not just UX polish

### For Newton Specifically

Since Newton performs verification at **constraint-definition time**, and constraints are **human-written**, the geometric encoding quality directly impacts:

| Quality Dimension | Impact |
|-------------------|--------|
| Error spotting speed | How quickly humans notice mistakes |
| System trust | How confidently humans rely on verification |
| Cartridge maintainability | How easily code survives time |
| Onboarding efficiency | How quickly new developers understand |

### The Cognitive Path

```
Traditional Software:
  Code → Compile → Runtime Error → Debug → Fix

Newton:
  Constraint → Visual Check → Geometric Lint → Parse → Verify → Execute

The geometric check happens before parsing.
The lint catches misalignment before verification.
The visual presentation aids human review.

Error prevention shifts left.
```

---

## Part VIII: Integration with Newton Architecture

### Connection to Six Geometric Structures

The geometric constraint semantics formalized here integrate with Newton's topological framework:

**Constraint Polytope:**
- Glyph geometry previews polytope structure
- Closed-form words suggest bounded feasibility regions
- Terminal words suggest half-space boundaries

**Decision Simplex:**
- Choice-point glyphs align with simplex vertices
- The four decisions (REFUSE, DEFER, ASK, ANSWER) can be notated with appropriate geometry

**Governance Lattice:**
- Monotonic safety uses terminal forms (can only go UP)
- Bridge words for lateral movement
- Point words for fixed positions

**Expand/Reduce Manifold:**
- Text space uses full glyph variety
- Constraint space favors precise forms
- Reduction preserves geometric essence

**Computation Graph:**
- Path notation uses bridges (flow)
- Node notation uses points (position)
- Edge notation uses lines (connection)

**Module Hypergraph:**
- Module names follow density rules
- Channel names follow bridge patterns
- The 9-node architecture benefits from geometric consistency

### Implementation Path

1. **Lint at constraint definition** — `newton lint` checks geometric alignment
2. **Suggest at authoring** — IDE support offers geometrically-aligned alternatives
3. **Visualize at review** — Render constraints with geometric analysis overlay
4. **Enforce at cartridge registration** — Optional strict mode rejects misaligned names

---

## Summary

Human cognition processes symbol geometry before semantic meaning. Newton's constraint notation should leverage this by:

1. **Matching glyph shapes to semantic intent** — closed forms for containment, hooks for terminals
2. **Aligning visual density with computational complexity** — light words for simple checks
3. **Avoiding geometric contradictions** — no open-shaped "closed" constraints
4. **Using appropriate typography** — monospace for code, geometric forms for ratios
5. **Linting for alignment** — automated checks catch mismatches

The keyword `finfr` exemplifies perfect geometric-semantic alignment. Its shape encodes "tried to continue, hit wall, turned back" before the meaning is parsed. This is the standard Newton notation should maintain.

---

**Geometry precedes semantics.**

**The shape is the first verification.**

**Newton starts with shapes, not numbers.**

---

*Related Documents:*
- [f/g Visual Language Specification](../product-architecture/FG_VISUAL_LANGUAGE.md)
- [Newton Geometry README](../../newton_geometry/README.md)
- [Constraint Definition Language](../../core/cdl.py)
- [TinyTalk Programming Guide](../../TINYTALK_PROGRAMMING_GUIDE.md)
