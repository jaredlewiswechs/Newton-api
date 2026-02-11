# Newton: Constraint-Geometric Computing Through Bézier Primitives — A Unified Architecture for Verified Intelligent Agents, Human-Computer Interaction, and Formal Specification

**Jared Lewis**
Ada Computing Company, Houston, Texas

**Abstract.** We present Newton, a constraint-geometric computing system developed over approximately sixty days in late 2025 and early 2026 that unifies verified computation, intelligent agent design, and human-computer interaction under a single theoretical primitive: the Bézier curve. Newton inverts the traditional compute-then-verify paradigm by treating constraints as first-class instructions, verification as the computation itself, and cryptographic ledgers as memory. The system introduces several novel contributions: (1) *Kinematic Linguistics*, a framework that models natural language as Bézier trajectories through meaning space where grammar defines the admissible region Ω; (2) a *Constraint Definition Language* (CDL 3.0) with ratio-dimensional analysis (f/g) that unifies financial, epistemic, temporal, and identity constraint domains; (3) a *Foghorn Visual Connection Language* in which every relationship between interface objects is a semantically-typed Bézier curve; (4) a 10-step verified agent pipeline with recursive self-verification (Meta-Newton) and continuous anomaly sensing (Ada Sentinel); and (5) *realTinyTalk*, a verified programming language with bounded execution guarantees. We situate Newton within sixty years of constraint programming research — from Sutherland's Sketchpad (1963) through Waltz filtering (1975), ThingLab (1979), and CLP(X) (1987) — and demonstrate that the Bézier curve serves as a universal primitive connecting interaction design, formal verification, computational linguistics, and distributed consensus. The system comprises approximately 60,000 lines of Python and Rust across 14 integrated subsystems, deployed as both serverless functions and traditional services. We argue that Newton represents a new class of *constraint-geometric systems* in which the mathematical object governing visual aesthetics, linguistic structure, and logical proof is one and the same.

**Keywords:** constraint logic programming, Bézier curves, verified computation, human-computer interaction, intelligent agents, kinematic linguistics, formal specification, self-verifying systems

---

## 1. Introduction

The history of computing is punctuated by systems that refuse to separate what a program *does* from what it *means*. Ivan Sutherland's Sketchpad (1963) treated geometric constraints as executable specifications [1]. Douglas Engelbart's "Mother of All Demos" (1968) demonstrated that interaction itself could be a medium of thought [2]. Alan Kay's Smalltalk (1972) unified objects, messages, and the programming environment into a single reflective substrate [3]. Each of these systems recognized that the boundary between specification, computation, and interaction is artificial — a boundary maintained by convention, not necessity.

Newton is a system built on the premise that this boundary can be dissolved entirely, and that the mathematical object capable of dissolving it already exists: the Bézier curve.

A Bézier curve is defined by anchor points and control handles. It is evaluable at any parameter *t* ∈ [0, 1]. It admits tangent vectors, curvature analysis, arc length computation, and bounding box extraction. It can be rendered visually, composed algebraically, and intersected geometrically. Critically, it is the native primitive of every modern vector graphics system, font renderer, and path-based UI framework.

We observe that these same properties — anchoring, control, parameterization, boundary analysis, and composition — describe not only visual curves but also:

- **Linguistic structure**, where subjects anchor (P₀), verbs define motion (the curve), and objects terminate (P₃);
- **Constraint satisfaction**, where feasible regions are bounded envelopes and solutions are points on admissible trajectories;
- **Agent decision-making**, where inputs are initial states, policies are control handles, and actions are commitments;
- **Interface relationships**, where connections between objects carry semantic weight encoded in curve shape.

Newton exploits this observation systematically. The result is a 14-subsystem architecture — approximately 60,000 lines of Python and Rust — in which Bézier geometry serves as the connective tissue between a constraint definition language, a verified programming language, an intelligent agent pipeline, a natural language processor, a cryptographic audit ledger, a distributed consensus protocol, and a visual interface system.

This paper makes the following contributions:

1. **Kinematic Linguistics** (§4): A theory of natural language as parameterized Bézier trajectories, where each symbol carries kinematic properties (weight, curvature, commit strength) and grammar defines an admissible region Ω in trajectory space.

2. **Constraint Definition Language 3.0** (§5): A domain-specialized constraint specification system with ratio-dimensional analysis (f/g), temporal aggregation windows, and a formal halt checker that proves constraint termination at parse time.

3. **Foghorn Visual Connection Language** (§6): An interaction paradigm in which every relationship between interface objects is a typed Bézier curve, with curve shape encoding semantic strength and dependency type.

4. **Verified Agent Architecture** (§7): A 10-step pipeline integrating anomaly detection (Ada Sentinel), recursive self-verification (Meta-Newton), grounded knowledge retrieval, and bounded computation — all unified through constraint checking rather than heuristic filtering.

5. **realTinyTalk** (§8): A Smalltalk-inspired programming language with bounded execution, formal verification, and foreign function interfaces, designed for educational and safety-critical contexts.

6. **Theoretical Synthesis** (§3): A formal argument that Bézier curves constitute a *universal primitive* for constraint-geometric systems, connecting Sutherland's geometric constraints, Kay's message-passing objects, and modern constraint logic programming under a single mathematical framework.

### 1.1 Context: Sixty Days, Fourteen Subsystems

Newton was developed between approximately December 2025 and February 2026. The compressed timeline is itself theoretically significant: it suggests that when a unifying primitive is identified, system complexity grows *compositionally* rather than *combinatorially*. Each new subsystem (agent, language, interface, education, game engine) reused the same constraint-geometric vocabulary rather than introducing new abstractions. This compositional property — what we term *primitive reuse* — is a direct consequence of the Bézier curve's versatility and is discussed further in §9.

### 1.2 Philosophical Foundation

Three axioms govern Newton's design:

> **Axiom 1.** The constraint IS the instruction.
> **Axiom 2.** The verification IS the computation.
> **Axiom 3.** The network IS the processor.

These are not metaphors. In Newton, a constraint object *is* evaluated as an instruction by the Forge engine. The act of verifying a claim against the knowledge base *is* the computational work performed. And distributed consensus across Bridge nodes *is* the processing that produces trusted results. The system contains no layer where "real computation" happens separately from verification — they are the same operation.

This design philosophy traces to a fundamental observation about modern AI systems: Large Language Models are powerful generators but unreliable governors. Newton addresses this by placing constraint verification *around* generation, ensuring that every output — whether from an LLM, a knowledge base, or a mathematical engine — passes through the same formal verification pipeline.

---

## 2. Related Work

Newton draws from and extends several decades of research across constraint programming, formal verification, human-computer interaction, and intelligent agent design. We organize related work along the theoretical lineage that Newton synthesizes.

### 2.1 Constraint Programming: From Sketchpad to CLP(X)

**Sketchpad** (Sutherland, 1963) [1] introduced constraint-based graphical editing, where geometric relationships (parallelism, perpendicularity, distance) were declared as constraints and maintained through relaxation solving. Sketchpad established two principles that Newton inherits: (a) constraints as specifications rather than procedures, and (b) the inseparability of visual representation from computational meaning.

**Waltz filtering** (1975) [4] introduced arc consistency as a pruning technique for constraint satisfaction, demonstrating that constraint propagation could dramatically reduce search spaces. Newton's CDL evaluator implements arc consistency as an early-termination optimization, achieving 2.31ms p99 latency for constraint evaluation.

**ThingLab** (Borning, 1979) [5] extended Sketchpad's ideas into the Smalltalk environment, introducing multi-way constraints and graphical simulation. Newton's realTinyTalk language is directly inspired by ThingLab's integration of constraints into an object-oriented programming language, and the Smalltalk-derived syntax (`law`, `forge`, `show`, `reply`) reflects this lineage.

**Propagator networks** (Steele & Sussman, 1980; Radul & Sussman, 2009) [6, 7] modeled computation as autonomous propagators communicating through shared cells, converging to fixed-point solutions. Newton's Forge engine implements a parallel propagator architecture with thread-pool execution and fixed-point convergence detection.

**CLP(X)** (Jaffar & Lassez, 1987) [8] established the theoretical framework of Constraint Logic Programming parameterized by computational domain. Newton's CDL 3.0 directly implements this pattern: constraints are parameterized by domain (FINANCIAL, HEALTH, EPISTEMIC, TEMPORAL, IDENTITY, COMMUNICATION, CUSTOM), each with domain-specific operators and evaluation semantics.

**Dykstra's algorithm** (1983) [9] provided a method for projecting points onto intersections of convex sets through alternating projections with correction vectors. Newton implements Dykstra's algorithm in Rust (`newton_core`) as the geometric foundation for constraint satisfaction, projecting arbitrary states onto the intersection of constraint boundaries.

### 2.2 Human-Computer Interaction

**Engelbart's NLS** (1968) [2] demonstrated that computing systems could augment human intellect through real-time interactive collaboration, hypertext, and multimedia. Newton's voice interface subsystem (MOAD — "Mother Of All Demos") explicitly references Engelbart's vision, extending it with constraint-verified natural language processing.

**Direct manipulation** (Shneiderman, 1983) [10] established principles for interfaces where objects are continuously visible, actions are rapid and reversible, and results are immediately apparent. Newton's Foghorn Visual Connection Language extends direct manipulation by making the *relationships between objects* — not just the objects themselves — directly visible and manipulable as Bézier curves.

**Instrumental interaction** (Beaudouin-Lafon, 2000) [11] proposed that interaction should be modeled through instruments that mediate between users and domain objects. Newton's Bézier-curve relationships function as instruments in this sense: they are first-class objects that users can create, modify, inspect, and verify, mediating between knowledge objects in the Nina interface.

### 2.3 Bézier Curves in Computing

Pierre Bézier (1962) and Paul de Casteljau (1959) independently developed the mathematical framework for parametric curves defined by control points [12, 13]. While Bézier curves have been extensively used in computer graphics, CAD, font rendering, and animation, their application as a *semantic primitive* — encoding meaning, not just shape — is, to our knowledge, novel to Newton.

Prior work on curve-based semantics includes **shape grammars** (Stiny & Gips, 1972) [14], which used geometric transformations to generate designs, and **space syntax** (Hillier & Hanson, 1984) [15], which analyzed architectural relationships through graph-geometric measures. Newton extends these ideas by using Bézier curves simultaneously for visual rendering, semantic encoding, linguistic modeling, and constraint geometry — a unification we term *constraint-geometric computing*.

### 2.4 Verified and Safe AI Systems

**Constitutional AI** (Bai et al., 2022) [16] introduced the idea of training AI systems with explicit behavioral constraints. Newton takes a fundamentally different approach: rather than training constraints into model weights (which can be circumvented), Newton enforces constraints *externally* through formal verification at every stage of the agent pipeline. The constraint is not learned — it is checked.

**Tool-augmented language models** (Schick et al., 2023) [17] demonstrated that LLMs could be enhanced with external tools for calculation, search, and verification. Newton inverts this relationship: the verification system is primary, and the LLM is an *optional* component used only when verified sources (knowledge base, logic engine, semantic resolver) are insufficient. In Newton's knowledge hierarchy, the LLM is consulted last, not first.

### 2.5 Self-Referential and Meta-Verification Systems

The problem of verifying the verifier — *Quis custodiet ipsos custodes?* (Juvenal, c. 100 CE) — has been addressed in formal methods through **proof-carrying code** (Necula, 1997) [18], **certified compilers** (Leroy, 2009) [19], and **reflective architectures** (Smith, 1982) [20]. Newton's Meta-Newton subsystem implements bounded recursive self-verification: the verifier verifies itself, but recursion is bounded (MAX_META_DEPTH = 3) to prevent infinite regress. This is, to our knowledge, the first system to combine recursive meta-verification with constraint logic programming and cryptographic audit trails.

---

## 3. Theoretical Foundation: Bézier Curves as Universal Primitives

We now formalize the central theoretical claim of this paper: that Bézier curves serve as a *universal primitive* for constraint-geometric computing, connecting visual representation, linguistic structure, constraint satisfaction, and agent decision-making under a single mathematical framework.

### 3.1 The Cubic Bézier as Computational Object

A cubic Bézier curve B(t) is defined by four points:

```
B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃,  t ∈ [0, 1]
```

where P₀ is the start anchor, P₃ is the end anchor, and P₁, P₂ are control handles. This definition admits the following computational operations:

| Operation | Definition | Complexity |
|-----------|-----------|------------|
| Point evaluation | B(t) for given t | O(1) |
| Tangent vector | B'(t) = 3(1-t)²(P₁-P₀) + 6(1-t)t(P₂-P₁) + 3t²(P₃-P₂) | O(1) |
| Arc length | ∫₀¹ ‖B'(t)‖ dt (numerical) | O(n) for n samples |
| Bounding box | Convex hull of {P₀, P₁, P₂, P₃} (tight: extrema) | O(1) |
| Subdivision | De Casteljau at parameter t | O(1) |
| Composition | Concatenation at shared anchor | O(1) |
| Intersection | Recursive subdivision + tolerance | O(n log n) |
| Hashing | SHA-256(P₀, P₁, P₂, P₃, metadata) | O(1) |

### 3.2 Four Interpretations of a Single Curve

Newton exploits the fact that a single Bézier curve admits four simultaneous interpretations:

**Interpretation 1: Visual Path.** In the Foghorn rendering system, B(t) defines a visual connection between interface objects. The SVG path `M P₀ C P₁ P₂ P₃` is rendered directly. Curve shape (tight vs. loose), style (solid, dashed, dotted), and color encode relationship semantics. This is the classical use of Bézier curves in computer graphics.

**Interpretation 2: Linguistic Trajectory.** In Kinematic Linguistics, P₀ represents the subject (anchor), the curve B(t) represents the verb (motion through meaning space), and P₃ represents the object (terminus/commitment). Control handles P₁, P₂ represent modifiers (adjectives, adverbs) that shape the trajectory without changing its endpoints. Grammar Ω defines the admissible region; a sentence is grammatical if its trajectory remains inside Ω.

**Interpretation 3: Constraint Boundary.** In the CDL evaluator, the curve defines a boundary of the feasible region. Points inside the curve satisfy the constraint; points outside violate it. Dykstra's algorithm projects arbitrary points onto the nearest feasible point on the constraint intersection — which is geometrically a point on (or inside) the Bézier-bounded region.

**Interpretation 4: Decision Trajectory.** In the agent pipeline, P₀ represents the initial state (user input), P₃ represents the target state (verified response), and the control handles represent the policy parameters (safety constraints, knowledge sources) that shape the path from input to output. The 10-step pipeline is a parameterized traversal of this decision curve.

### 3.3 The Isomorphism

These four interpretations are not merely analogies. They share identical mathematical structure:

| Component | Visual | Linguistic | Constraint | Agent |
|-----------|--------|-----------|------------|-------|
| P₀ (anchor) | Source object | Subject | Current state | User input |
| P₁ (handle) | Curvature control | Modifier 1 | Constraint param | Safety filter |
| P₂ (handle) | Curvature control | Modifier 2 | Constraint param | Knowledge source |
| P₃ (terminus) | Target object | Object | Goal state | Verified response |
| t ∈ [0,1] | Path parameter | Time/position | Relaxation param | Pipeline step |
| B(t) | Rendered point | Word at position | Feasible point | Intermediate state |
| B'(t) | Tangent/arrow | Semantic direction | Gradient | Action direction |
| Ω | Viewport bounds | Grammar | Feasible region | Safety envelope |

This structural isomorphism means that operations defined for one interpretation automatically transfer to the others. Subdivision of a visual curve corresponds to grammatical phrase boundaries. Intersection of constraint boundaries corresponds to the agent's consensus across verification steps. Bounding box computation for a linguistic trajectory corresponds to the semantic field of a sentence.

### 3.4 Formal Definition: Constraint-Geometric System

We define a *constraint-geometric system* as a tuple (𝒫, Ω, B, V, L) where:

- **𝒫** is a set of Bézier primitives (curves, points, control handles)
- **Ω** is the admissible region (the set of constraint-satisfying states)
- **B**: 𝒫 → Ω is the boundary function mapping primitives to constraint boundaries
- **V**: Ω × Ω → {⊤, ⊥} is the verification function (constraint checking)
- **L**: 𝒫* → H is the ledger function mapping sequences of operations to hash-chained records

A system is *constraint-geometric* if all of the following hold:

1. **Geometric grounding**: Every constraint in Ω has a geometric interpretation as a region bounded by elements of 𝒫.
2. **Verification-as-computation**: V(x, Ω) is the primary computational operation; all other operations are derived from or gated by V.
3. **Ledger integrity**: L is append-only, hash-chained, and admits O(log n) membership proofs (Merkle trees).
4. **Primitive reuse**: The same elements of 𝒫 are used for visual rendering, semantic encoding, and constraint definition.

Newton satisfies all four conditions, as demonstrated in §4–§8.

---

## 4. Kinematic Linguistics: Language as Bézier Trajectory

Kinematic Linguistics is Newton's framework for treating natural language as parameterized trajectories through a constraint-bounded meaning space. The core insight is that the articulatory phonetics of speech — the physical motion of mouth, tongue, and breath — already constitutes a kinematic system, and this kinematics maps naturally onto Bézier curve parameters.

### 4.1 The Kinematic Alphabet

Each symbol in the writing system is assigned a *kinematic signature* (σ) consisting of:

```
σ = (symbol, type, weight, curvature, commit_strength, is_anchor, is_terminus,
     opens_envelope, closes_envelope, phonetic_desc)
```

where:

- **weight** ∈ [0, 1]: The degree to which the symbol displaces the trajectory (how much it "moves" the control handle H₂).
- **curvature** ∈ [-1, 1]: The degree to which the symbol bends the trajectory. Positive curvature opens outward; negative curvature closes inward.
- **commit_strength** ∈ [0, 1]: Proximity to P₃ (terminus). High commit strength indicates finality, certainty, or closure.

Symbols are classified into seven types: VOWEL (open trajectories), CONSONANT (constraints on breath), DIGIT (quantity as motion), OPERATOR (grammar of transformation), COMMIT (P₃ markers), QUERY (verification requests), and CONTAINER (local Ω definitions).

### 4.2 Phonetic-Geometric Correspondence

The mapping from phonetics to geometry is not arbitrary. It reflects the physical kinematics of speech production:

**Vowels** define the open space of the trajectory — the admissible region itself:
- **'a'** (open front): Origin, anchor point (P₀). Weight 0.7, curvature 0.3. The mouth opens wide — maximum admissible space.
- **'i'** (high front): Terminus, pure commitment (P₃). Weight 0.3, commit 0.8. The mouth narrows to a point — convergence.
- **'o'** (back rounded): Full envelope (Ω as shape). Weight 0.8, curvature 0.9. The mouth rounds — enclosing a bounded region.

**Consonants** constrain the breath, partitioning the trajectory into bounded segments:
- **Labials** (b, p, m): Anchor points (P₀). Lips close completely — bounded explosion from a defined start.
- **Dentals/alveolars** (t, d, n): Handle adjustments (H₁). Tongue tip precisely positions the control point — "t" is the *Newton gate*, a decision point with commit strength 0.9.
- **Velars** (k, g): Leverage handles (H₂). Back-tongue contact provides maximum curvature control.

**Punctuation** carries the deepest kinematic significance:
- **'.'** (period): P₃ COMMIT. Weight 0.0, commit 1.0. The trajectory terminates. The sentence is *decided*.
- **'?'** (question): VERIFICATION QUERY. Commit 0.1. The trajectory does not terminate — it requests verification of admissibility.
- **':'** (colon): THE f/g RATIO. The dimensional analysis operator. Weight 0.5, curvature 0.0. It divides without bending.

### 4.3 Trajectory Analysis

Given a text string, the `KinematicAnalyzer` computes the trajectory by accumulating kinematic properties character by character:

```
For each character cᵢ in text:
    σᵢ = SIGNATURES[cᵢ]
    cumulative_weight += σᵢ.weight
    cumulative_curvature += σᵢ.curvature
    max_commit = max(max_commit, σᵢ.commit_strength)
    envelope_depth += (1 if σᵢ.opens_envelope else 0)
                    - (1 if σᵢ.closes_envelope else 0)
```

The resulting `Trajectory` object captures:
- **Total weight**: Aggregate displacement (semantic "mass" of the utterance)
- **Total curvature**: Net bending (positive = expansive, negative = contractive)
- **Max commit**: Peak commitment level (how strongly the text asserts)
- **Envelope balance**: Whether all opened Ω's are closed (grammatical completeness)
- **is_committed**: Whether the trajectory terminates at P₃ (sentence ends with '.' or '!')
- **is_query**: Whether the trajectory ends with a verification request ('?')

### 4.4 Grammar as Admissible Region

The key theoretical contribution of Kinematic Linguistics is the treatment of grammar as a constraint surface Ω in trajectory space. A sentence is *grammatical* if and only if its trajectory lies entirely within Ω.

This formulation naturally handles Chomsky's famous example [21]:

> *"Colorless green ideas sleep furiously."*

This sentence is:
- **Syntactically inside grammar Ω**: The trajectory is well-formed. Envelope balance is zero. The sentence commits (period). Subject → verb → adverb structure is preserved.
- **Semantically outside meaning Ω**: The trajectory enters a region where semantic constraints are violated ("colorless" contradicts "green"; "ideas" cannot "sleep").

In Newton's framework, these are simply *two different constraint surfaces* — both geometric, both expressible as Bézier-bounded regions, but defined over different dimensions of the trajectory space. Syntactic Ω constrains the *shape* of the trajectory; semantic Ω constrains its *position* in meaning space. The sentence traces a valid shape through an invalid region.

### 4.5 Real-Time Composition

The `TrajectoryComposer` extends this analysis to real-time text input, providing per-keystroke feedback on the evolving trajectory. As a user types, the system continuously reports:

- Current envelope depth (are all brackets closed?)
- Commitment status (has the sentence terminated?)
- Kinematic summary (weight, curvature, commitment profile)
- Semantic field compatibility (does this word fit the established trajectory?)

This creates a form of *kinematic feedback* — the linguistic equivalent of force feedback in haptic interfaces — where the user can sense the geometric properties of their language as they produce it.

---

## 5. CDL 3.0: Constraint Definition Language with Ratio-Dimensional Analysis

The Constraint Definition Language (CDL) is Newton's formal specification language for expressing, composing, and evaluating constraints across seven domains. CDL 3.0 introduces ratio-dimensional analysis as its central innovation.

### 5.1 The f/g Ratio

Every real-world constraint can be expressed as a ratio between two quantities:

```
f/g   where f = forge (what you attempt) and g = ground (what reality permits)
```

The letters f and g are chosen deliberately:
- **f** = forge, fact, function — the numerator, representing intention, claim, or action
- **g** = ground, goal, governance — the denominator, representing reality, truth, or limit

The ratio f/g admits four fundamental states:

| Condition | Interpretation | Newton Action |
|-----------|---------------|---------------|
| f/g < 1 | Within bounds | Execute (GREEN) |
| f/g = 1 | At boundary | Execute with caution (YELLOW) |
| f/g > 1 | Beyond bounds | Clip or refuse (YELLOW/RED) |
| g → 0 | Undefined | **finfr** — ontological death |

The term **finfr** (from Old Norse, roughly "to find" or "to come to an end") denotes the condition where the denominator approaches zero — the constraint becomes undefined, and the system enters an ontologically impossible state. In financial terms: infinite leverage. In epistemic terms: a claim with no ground truth. In linguistic terms: a sentence with no referent.

### 5.2 Constraint Types

CDL 3.0 defines four constraint types:

**Atomic Constraints** are single, indivisible comparisons:
```python
AtomicConstraint(field="balance", operator=Operator.GE, value=0, domain=Domain.FINANCIAL)
```

**Composite Constraints** combine atomic constraints with logical operators:
```python
CompositeConstraint(operator=BooleanOp.AND, constraints=[c1, c2, c3])
```

**Conditional Constraints** implement if-then logic:
```python
ConditionalConstraint(condition=c1, then_constraint=c2, else_constraint=c3)
```

**Ratio Constraints** express f/g dimensional analysis:
```python
RatioConstraint(f_field="liabilities", g_field="assets",
                operator=Operator.RATIO_LE, threshold=1.0)
```

### 5.3 Temporal Aggregation

CDL 3.0 extends constraints into the time domain through windowed aggregation:

```python
AtomicConstraint(field="transactions", operator=Operator.COUNT_LT, value=10,
                 window="24h", group_by="user_id")
```

This enables rate limiting, velocity checking, and behavioral analysis as first-class constraint operations. Supported aggregations include SUM, COUNT, and AVG, each with LT/LE/GT/GE comparators over configurable time windows (maximum: 1 year).

### 5.4 The Seven Domains

Constraints are parameterized by domain, following the CLP(X) pattern [8]:

| Domain | Example Constraint | f/g Interpretation |
|--------|-------------------|-------------------|
| FINANCIAL | withdrawal ≤ balance | spending / capacity |
| COMMUNICATION | message length ≤ limit | content / channel capacity |
| HEALTH | dosage ≤ safe_max | prescribed / tolerable |
| EPISTEMIC | confidence ≥ threshold | evidence / claim strength |
| TEMPORAL | deadline ≥ now | time needed / time available |
| IDENTITY | claimed_role ∈ permitted_roles | claimed / verified |
| CUSTOM | user-defined | user-defined |

### 5.5 Halt Checking

CDL 3.0 includes a formal halt checker (`HaltChecker`) that proves constraint termination at parse time — before evaluation begins. The halt checker enforces:

- Maximum aggregation window (1 year)
- Maximum composite constraint depth (1000 sub-constraints)
- No recursive constraint references
- Bounded temporal windows

This constitutes Newton's practical answer to the halting problem: rather than solving it in general (which is undecidable), Newton restricts the constraint language to a decidable subset and proves termination within that subset.

### 5.6 Cohen-Sutherland Constraint Clipping

When a request partially satisfies constraints, Newton does not simply reject it. Instead, it applies a variant of the Cohen-Sutherland line clipping algorithm [22] to constraint space:

- **GREEN**: Request fully inside Ω → execute entirely
- **YELLOW**: Request partially inside Ω → clip to feasible boundary, offer the valid portion
- **RED**: Request fully outside Ω → finfr (impossible to satisfy)

This "don't just reject — find what CAN be done" philosophy distinguishes Newton from binary pass/fail verification systems.

---

## 6. Foghorn: Visual Connection Language

Foghorn is Newton's interaction paradigm, directly inspired by NeXTSTEP (1989) [23] and reimagined through constraint-geometric principles. Its central innovation is that every relationship between interface objects is a first-class Bézier curve.

### 6.1 Curves as Relationships

In traditional interfaces, relationships between objects are implicit — encoded in layout proximity, shared labels, or invisible data bindings. Foghorn makes relationships *visible, inspectable, and verifiable* by representing each one as a cubic Bézier curve:

```
source ──────────╮
                  │
                  ╰──────────► target
```

Curve properties encode relationship semantics:

| Property | Visual Effect | Semantic Meaning |
|----------|--------------|-----------------|
| Curvature (tight) | Sharply curved | Strong dependency |
| Curvature (loose) | Gently curved | Weak association |
| Style (solid) | Continuous line | Confirmed relationship |
| Style (dashed) | Interrupted line | Tentative relationship |
| Style (dotted) | Point sequence | Hypothetical relationship |
| Color | Relationship type | Domain-specific category |
| Width | Prominence | Relationship importance |

### 6.2 Relationship Types

The `CurveFactory` maps semantic relationship types to visual styles:

| Relationship | Style | Color | Interpretation |
|-------------|-------|-------|----------------|
| `links_to` | Solid | Gray | General connection |
| `references` | Solid | Blue | Citation/reference |
| `depends_on` | Solid | Red | Hard dependency |
| `derived_from` | Dashed | Green | Derivation |
| `cites` | Dotted | Yellow | Academic citation |
| `related_to` | Dashed | Gray | Weak association |
| `precedes` | Solid | Purple | Temporal ordering |
| `follows` | Solid | Orange | Temporal succession |

### 6.3 Automatic Control Point Generation

When the user creates a relationship without specifying control handles, Foghorn auto-generates aesthetically appropriate control points:

```python
if abs(dx) > abs(dy):   # Mostly horizontal
    P₁ = (source.x + dx*0.33, source.y)
    P₂ = (target.x - dx*0.33, target.y)
else:                     # Mostly vertical
    P₁ = (source.x, source.y + dy*0.33)
    P₂ = (target.x, target.y - dy*0.33)
```

This 1/3-offset heuristic produces visually smooth curves that follow the predominant direction of the connection, consistent with typographic and cartographic conventions for Bézier curve aesthetics.

### 6.4 The CurveStore: Indexed Relationship Graph

Foghorn maintains a `CurveStore` — an in-memory graph indexed by both source and target hashes:

```python
_curves:    hash → BezierCurve          # O(1) lookup by curve hash
_by_source: source_hash → [curve_hashes] # O(1) outgoing edges
_by_target: target_hash → [curve_hashes] # O(1) incoming edges
```

This enables constant-time queries for: "What does this object connect to?", "What connects to this object?", and "Does this specific relationship exist?" — the three fundamental operations of relationship navigation.

### 6.5 SVG Rendering with Semantic Arrows

Foghorn renders curves as SVG paths with directional arrowheads computed from the tangent vector at t = 1.0:

```python
tangent = curve.tangent_at(1.0)
angle = atan2(tangent.y, tangent.x)
arrowhead_1 = end - arrow_size * (cos(angle - 0.4), sin(angle - 0.4))
arrowhead_2 = end - arrow_size * (cos(angle + 0.4), sin(angle + 0.4))
```

The arrowhead direction is always tangent to the curve at its terminus, ensuring visual accuracy regardless of curve shape. This contrasts with naive approaches that compute arrow direction from endpoint positions, producing incorrect angles on highly curved relationships.

### 6.6 Connection to Nina Desktop

The Nina system — Newton Intelligence and Natural Assistant — implements a consumer-facing PDA interface inspired by the Apple Newton MessagePad (1993–1998) [24] and rebuilt on constraint-geometric principles. Nina's five core applications (Notes, Names, Dates, Calculator, Verify) all use Foghorn curves to visualize relationships between data objects, creating a unified interaction surface where data connections are as visible and manipulable as the data itself.

---

## 7. Verified Agent Architecture

Newton's agent subsystem implements a 10-step verified pipeline that integrates anomaly detection, constraint checking, knowledge retrieval, computation, and recursive self-verification into a single coherent architecture.

### 7.1 The Knowledge Hierarchy

Newton establishes a strict priority ordering for response generation:

```
Identity (self-knowledge) > Mathematics (logic engine) > Knowledge Base (verified facts)
> Knowledge Mesh (multi-source) > Grounding Engine (external) > LLM (generative)
```

This hierarchy inverts the typical AI architecture, where a large language model is the primary response mechanism. In Newton, the LLM is the *last resort*, consulted only when all verified sources fail. This design ensures that responses are grounded in formal verification whenever possible, with probabilistic generation used only for genuinely novel or creative queries.

### 7.2 The 10-Step Pipeline

Each user query traverses the following verified pipeline:

| Step | Component | Function | Gate Condition |
|------|-----------|----------|---------------|
| 1 | Ada Sentinel | Pre-scan for anomalies | Whisper level < CRITICAL |
| 2 | Input Logger | Hash-chain input to ledger | Always passes |
| 3 | Safety Constraints | Check against 5 constraint domains | All constraints satisfied |
| 4 | Constraint Gate | Block if safety violated | GREEN or YELLOW status |
| 5 | Response Generator | Generate via knowledge hierarchy | At least one source responds |
| 6 | Ada Sentinel | Post-scan response for drift | Whisper level < ALARM |
| 7 | Grounding Engine | Verify factual claims externally | Claims grounded or flagged |
| 8 | Meta-Newton | Verify the verification pipeline itself | Recursive check passes |
| 9 | Response Logger | Hash-chain output to ledger | Always passes |
| 10 | Final Response | Return with provenance metadata | Complete |

### 7.3 The Ada Sentinel: Canine Intuition for AI Safety

Ada is Newton's continuous anomaly detection system, named after Ada Lovelace (1815–1852), who first recognized that computation extends beyond calculation [25]. Ada operates on a different principle than formal verification: she senses *quickly* rather than verifying *completely*.

The design metaphor is a dog's nose: not a laboratory analysis, but an instantaneous threat assessment. Ada detects:

- **Semantic drift**: Meaning has shifted from established baseline
- **Factual drift**: Facts have changed (temporal sensitivity)
- **Contradiction patterns**: Text contains "always...never" or "100% certain...but maybe"
- **Excessive confidence**: Suspiciously high certainty levels (a red flag for unverified claims)
- **Behavioral anomalies**: Usage patterns deviate from established baselines

Ada communicates through `Whisper` objects — quiet signals at five alert levels (QUIET, NOTICE, ALERT, ALARM, CRITICAL). She is not a gatekeeper but a sentinel: she observes and reports, allowing the formal verification systems to make the final decision.

The `DriftDetector` maintains `Baseline` objects for known-good states. Each verification *strengthens* the baseline (increasing `verification_count`), while detected drift weakens it. This creates an adaptive immune system: the more a fact is verified, the harder it is to drift.

### 7.4 Meta-Newton: The Self-Verifying Verifier

Meta-Newton addresses the ancient philosophical problem of verifier trust — *Quis custodiet ipsos custodes?* — through bounded recursive verification:

```
Meta-Newton verifies:
    1. SYNTACTIC:    Is the pipeline structure valid?
    2. SEMANTIC:     Are constraint meanings consistent?
    3. OPERATIONAL:  Are all operations bounded?
    4. TEMPORAL:     Are time constraints respected?
    5. CHAIN:        Is the hash chain intact?
    6. RECURSIVE:    Does this verification verify itself?
```

Recursion is bounded at MAX_META_DEPTH = 3 to prevent infinite regress. This is a principled choice: three levels of meta-verification (verify → verify-the-verifier → verify-the-meta-verifier) provide practical confidence in verification integrity without the theoretical impossibility of unbounded self-reference.

Meta-Newton's constraints include:
- **bounded_iterations**: No constraint evaluation may exceed iteration limits
- **bounded_recursion**: No function may exceed recursion depth
- **bounded_memory**: No operation may exceed memory allocation
- **hash_chain_integrity**: The ledger must form a valid chain
- **constraint_satisfaction**: All evaluated constraints must produce definite results

### 7.5 The Chatbot Compiler: Governance Over Generation

Newton's `ChatbotCompiler` implements a four-stage compilation pipeline for natural language interaction:

1. **Classification**: Input is classified by request type (FACTUAL, OPINION, CREATIVE, TECHNICAL, PERSONAL, HARMFUL) and risk level (SAFE, CAUTION, RISKY, BLOCKED).
2. **Constraint Checking**: Classified input is checked against domain-specific constraints (medical deferral, legal deferral, financial caution).
3. **Response Generation**: If constraints pass, response is generated through the knowledge hierarchy.
4. **Response Validation**: Generated response is re-checked against output constraints.

The key insight is stated directly in the source: *"LLMs are great generators. They are terrible governors."* Newton separates these roles architecturally: the LLM generates; the constraint system governs.

---

## 8. realTinyTalk: A Verified Programming Language

realTinyTalk is a Smalltalk-inspired programming language designed for verified, bounded execution. It serves as both Newton's internal scripting language and an educational tool for teaching computation within safety constraints.

### 8.1 Design Philosophy

realTinyTalk inherits Smalltalk's message-passing paradigm [3] while adding formal verification guarantees:

```tinytalk
law square(x)          -- 'law' declares a pure function (no side effects)
    reply x * x        -- 'reply' returns (not 'return' — the word matters)
end

forge process(data)    -- 'forge' declares a function with side effects
    let result = square(data)
    show(result)        -- 'show' is output (not 'print' — visibility, not printing)
    reply result
end
```

The vocabulary is deliberate: `law` (not `function`) emphasizes that pure functions are *laws* — they must always hold. `forge` (not `method`) emphasizes that impure operations *forge* new state. `reply` (not `return`) emphasizes response rather than control flow. `show` (not `print`) emphasizes making visible rather than mechanical output.

### 8.2 Bounded Execution Model

Every realTinyTalk execution operates within formal bounds:

```python
class ExecutionBounds:
    max_iterations:     1,000,000   # No infinite loops
    max_recursion_depth: 100        # No stack overflow
    max_operations:     1,000,000   # No computational explosion
    max_memory_bytes:   100,000,000 # 100MB ceiling
    timeout_seconds:    30.0        # Wall-clock limit
```

These bounds constitute Newton's practical resolution of the halting problem: rather than deciding whether an arbitrary program halts (undecidable in general), Newton restricts execution to a bounded subset of computation that is *guaranteed* to halt. Any program that attempts to exceed these bounds is terminated with a descriptive error — not an infinite hang.

### 8.3 Type System and Natural Language Operators

realTinyTalk includes operators designed to bridge formal logic and natural expression:

| Operator | Meaning | Traditional Equivalent |
|----------|---------|----------------------|
| `has` | Contains element | `in` (Python) |
| `hasnt` | Does not contain | `not in` |
| `isin` | Is contained by | Reverse `in` |
| `islike` | Pattern matches | `=~` (Perl/Ruby) |

Additionally, realTinyTalk supports *step chain operations* inspired by dplyr [26]:

```tinytalk
data >> _filter(age > 18) >> _sort("name") >> _take(10)
```

These compose naturally, creating pipelines that read left-to-right as sequences of transformations — a design that aligns with the Bézier trajectory metaphor (P₀ → transformations → P₃).

### 8.4 Foreign Function Interface

realTinyTalk includes an FFI supporting Python, C, Go, Rust, and JavaScript interop, enabling Newton to leverage existing library ecosystems while maintaining verification guarantees at the boundary:

```tinytalk
import "math" from python
let result = math.sqrt(144)
```

FFI calls are themselves bounded and logged to the ledger, ensuring that external operations do not bypass Newton's verification pipeline.

### 8.5 Nine-Stage Compilation in Nina

When realTinyTalk is executed within the Nina system, it passes through a nine-stage compiler pipeline:

1. **Intent lock**: Determine what the code is trying to do
2. **Parse**: Lexical analysis and recursive descent parsing
3. **Abstract interpretation**: Static analysis for type safety
4. **Geometric check**: Verify code structure against admissible patterns
5. **Verify/upgrade**: Formal verification, trust level assignment
6. **Execute**: Bounded runtime evaluation
7. **Log**: Record execution trace to ledger
8. **Meta-check**: Meta-Newton verifies the compilation itself
9. **Return**: Produce verified result with provenance

---

## 9. Architectural Properties

### 9.1 Primitive Reuse and Compositional Growth

Newton's development over sixty days produced 14 subsystems totaling approximately 60,000 lines of code. This pace was enabled by *primitive reuse*: each new subsystem reused the Bézier curve vocabulary, the constraint evaluation engine, and the hash-chained ledger rather than introducing new abstractions.

| Subsystem | Lines | Bézier Usage | Constraint Usage | Ledger Usage |
|-----------|-------|-------------|-----------------|-------------|
| Newton Agent | 900 | Decision trajectory | Safety gates | Input/output hashing |
| Logic Engine | 1,200 | — | Bounded execution | Operation tracing |
| CDL Evaluator | 1,200 | Feasibility regions | Core evaluation | Evaluation records |
| Knowledge Base | 2,901 | — | Fact verification | Fact provenance |
| Kinematic Linguistics | 600 | Linguistic trajectories | Grammar Ω | — |
| Foghorn Bézier | 562 | Visual connections | Relationship semantics | Curve hashing |
| Ada Sentinel | 650 | — | Drift thresholds | Baseline tracking |
| Meta-Newton | 651 | — | Recursive verification | Chain integrity |
| realTinyTalk | 3,000+ | — | Bounded execution | Execution logs |
| Chatbot Compiler | 1,200 | — | Response governance | Decision audit |
| Constraint Extractor | 1,200 | — | NL → CDL conversion | Extraction proofs |
| Bridge (PBFT) | 800+ | — | Consensus constraints | Distributed ledger |
| Nina PDA | 1,500+ | UI relationships | All constraint types | All ledger types |
| Education | 2,000+ | — | Curriculum constraints | Assessment records |

The table reveals that while not every subsystem uses all three primitives, the *vocabulary* remains consistent. A developer working on the agent subsystem speaks the same language (constraints, verification, commitment) as one working on the education system or the visual interface. This is the practical consequence of identifying a universal primitive: it creates a shared language across otherwise unrelated domains.

### 9.2 Cryptographic Audit Infrastructure

Newton's ledger implements an append-only, hash-chained record with Merkle tree proofs:

```
Entry₀ (prev_hash = "0"×64)
  ↓
Entry₁ (prev_hash = SHA256(Entry₀))
  ↓
Entry₂ (prev_hash = SHA256(Entry₁))
  ↓  ...
EntryN (prev_hash = SHA256(EntryN₋₁))
```

Each entry contains: index, timestamp, operation type, payload hash, result (pass/fail/error), previous hash, and entry hash. The Merkle tree overlay enables O(log n) inclusion proofs for external auditors without revealing the full ledger contents.

The Vault subsystem provides AES-256-GCM encryption for constraint storage, with owner-derived keys (PBKDF2, 100,000 iterations). This creates *data sovereignty*: constraints are owned by their creators, encrypted at rest, and accessible only with the owner's key.

### 9.3 Distributed Consensus via PBFT

Newton's Bridge subsystem implements Practical Byzantine Fault Tolerance [27] for distributed constraint verification:

- **Fault tolerance**: Tolerates f = ⌊(n-1)/3⌋ Byzantine (arbitrarily faulty) nodes
- **Consensus phases**: PREPARE → COMMIT → DECIDED (three-phase protocol)
- **Quorum size**: ⌊2n/3⌋ + 1 nodes must agree
- **Sybil resistance**: Minimum stake requirement (MIN_STAKE = 1000) prevents identity flooding

This enables Newton to operate as a distributed verification network where no single node is trusted, but the collective achieves consensus on constraint satisfaction.

### 9.4 Performance Characteristics

Despite the overhead of formal verification, Newton achieves practical latencies:

| Operation | Latency (p99) | Notes |
|-----------|--------------|-------|
| Constraint projection (2D) | < 0.1ms | Rust `newton_core` |
| Constraint projection (8D) | < 0.3ms | Dykstra's algorithm |
| Constraint projection (32D) | < 0.5ms | Linear convergence |
| CDL evaluation | 2.31ms | With arc consistency |
| Candidate verification (N=24) | < 2ms | Parallel evaluation |
| Full constraint suggest | < 5ms | End-to-end pipeline |
| Semantic resolution | ~200ms | Datamuse API (network) |

The critical observation is that verification adds milliseconds, not seconds. The constraint-geometric approach enables sub-5ms verification for most operations, making verified computation practical for real-time interactive systems.

---

## 10. The Education Connection: Constraints as Curriculum

Newton's education subsystem demonstrates that the constraint-geometric framework extends naturally to pedagogical design, treating educational standards as machine-verifiable constraint objects.

### 10.1 TEKS as Formal Constraints

Texas Essential Knowledge and Skills (TEKS) standards — the state curriculum requirements — are encoded as constraint objects with measurable criteria:

```python
TEKSStandard(
    code="111.39.c.2.A",
    description="Graph the functions f(x)=√x, f(x)=1/x, ...",
    grade_level=11,
    bloom_level=BloomLevel.APPLY,
    prerequisites=["111.39.c.1.A"],
    measurable_criteria=["identify parent functions", "graph transformations"]
)
```

### 10.2 The f/g Ratio in Education

The f/g ratio maps directly to educational assessment:

- **f** = student's demonstrated performance
- **g** = mastery threshold for the standard

| f/g Range | Interpretation | Pedagogical Action |
|-----------|---------------|-------------------|
| f/g < 0.5 | Far below mastery | Scaffold prerequisites |
| 0.5 ≤ f/g < 1.0 | Approaching mastery | Targeted instruction |
| **1.0 ≤ f/g < 1.5** | **Zone of Proximal Development** | **Optimal challenge** |
| f/g ≥ 1.5 | Beyond mastery | Extend with enrichment |

The Zone of Proximal Development (ZPD), Vygotsky's concept of the region where learning is most productive [28], maps precisely to the constraint boundary where 1.0 ≤ f/g < 1.5. This is not a metaphor: the student's trajectory through the curriculum is literally a path through constraint space, and the ZPD is the boundary region where constraints are challenging but satisfiable.

### 10.3 Bloom's Taxonomy as Verification Levels

Bloom's revised taxonomy [29] maps to verification depth:

| Bloom Level | Verification Depth | Newton Equivalent |
|-------------|-------------------|-------------------|
| Remember | Syntactic check | Pattern matching |
| Understand | Semantic check | Meaning verification |
| Apply | Operational check | Execution with bounds |
| Analyze | Structural check | Component decomposition |
| Evaluate | Meta-verification | Recursive checking |
| Create | Full pipeline | Unconstrained generation + verification |

This mapping means that Newton can assess student work at the appropriate cognitive level: a "Remember" task requires only pattern matching, while an "Evaluate" task requires the full meta-verification pipeline.

---

## 11. Discussion

### 11.1 What Newton Is Not

Newton is not a theorem prover in the tradition of Coq [30] or Lean [31]. It does not generate machine-checked proofs of mathematical theorems. Its verification guarantees are bounded: constraints are checked within defined limits, execution is bounded by explicit parameters, and self-verification recurses to a fixed depth.

Newton is not a replacement for large language models. It is a *governance layer* that ensures LLM outputs (when used) satisfy formal constraints. The relationship is complementary: LLMs generate; Newton verifies.

Newton is not a blockchain. While it uses hash chains and Merkle trees, the ledger is not distributed by default (the Bridge subsystem enables distribution but is not required). The cryptographic infrastructure serves *auditability*, not decentralized consensus.

### 11.2 The Accidental Architecture

The author describes Newton's development as "accidental" — patterns that emerged from sixty days of intensive building rather than top-down architectural planning. This is theoretically significant. The fact that Bézier curves, constraint logic, and hash-chained ledgers naturally recurred across 14 subsystems without being mandated by a master plan suggests that these primitives have *intrinsic universality*: they are not imposed on the problem domains but discovered within them.

This resonates with Christopher Alexander's concept of *pattern languages* [32] — recurring solutions that emerge from the structure of problems rather than the preferences of designers. Newton's constraint-geometric vocabulary may represent a pattern language for verified computing systems.

### 11.3 Limitations and Future Work

**Kinematic Linguistics** currently operates at the character level, lacking word-level and phrase-level trajectory composition. Future work should integrate distributional semantics (word embeddings) with kinematic signatures to enable trajectory analysis at multiple linguistic scales.

**The f/g ratio**, while powerful for binary constraint checking, does not yet support multi-objective optimization where multiple ratios must be balanced simultaneously. Pareto-optimal constraint satisfaction across multiple f/g dimensions is a natural extension.

**Distributed verification** via the Bridge subsystem has been implemented but not evaluated at scale. Empirical measurements of consensus latency, fault tolerance under adversarial conditions, and network partition behavior remain as future work.

**Formal proofs** of the constraint-geometric isomorphism (§3.3) are presented informally. A fully mechanized proof in a system like Lean or Agda would strengthen the theoretical contribution.

### 11.4 Broader Implications

Newton suggests a design methodology for AI systems: rather than training safety constraints into model weights (where they can be circumvented through prompt engineering or fine-tuning), enforce them *externally* through formal verification systems that cannot be bypassed by the model. The constraint is not a suggestion — it is the law.

The Bézier-as-universal-primitive observation suggests that other geometric objects (NURBS, subdivision surfaces, simplicial complexes) might serve similar unifying roles in other domains. The general principle — *find a mathematical object that admits simultaneous interpretation across visual, semantic, logical, and interactive dimensions* — may be a productive research direction for constraint-geometric computing.

---

## 12. Conclusion

Newton demonstrates that a single mathematical primitive — the cubic Bézier curve — can unify visual interaction design, natural language analysis, constraint satisfaction, and intelligent agent architecture into a coherent computational system. The system's three axioms — *the constraint IS the instruction, the verification IS the computation, the network IS the processor* — are not philosophical aspirations but architectural realities implemented across 14 subsystems and approximately 60,000 lines of code.

The contributions are both theoretical and practical. Theoretically, Newton establishes the concept of *constraint-geometric computing*, where visual, linguistic, and logical operations share a common geometric vocabulary. The Kinematic Linguistics framework demonstrates that language can be analyzed as parameterized trajectories through constraint-bounded meaning spaces. The f/g ratio provides a universal dimensional analysis for constraint reasoning.

Practically, Newton achieves sub-5ms verification latency for most constraint operations, implements a 10-step verified agent pipeline that places formal verification around (not inside) language model generation, and provides cryptographic audit trails with O(log n) membership proofs.

Perhaps most significantly, Newton was built in sixty days by a single developer — not despite its complexity, but *because* of its conceptual unity. When you identify the right primitive, composition replaces complexity. The Bézier curve is not merely a drawing tool. It is a way of thinking about the relationship between intention and constraint, between what we attempt and what reality permits, between P₀ and P₃.

The curve IS the computation.

---

## References

[1] I. E. Sutherland, "Sketchpad: A Man-Machine Graphical Communication System," in *Proceedings of the AFIPS Spring Joint Computer Conference*, 1963, pp. 329–346.

[2] D. C. Engelbart and W. K. English, "A Research Center for Augmenting Human Intellect," in *Proceedings of the AFIPS Fall Joint Computer Conference*, 1968, pp. 395–410.

[3] A. Kay, "The Early History of Smalltalk," in *ACM SIGPLAN Notices*, vol. 28, no. 3, 1993, pp. 69–95.

[4] D. L. Waltz, "Understanding Line Drawings of Scenes with Shadows," in *The Psychology of Computer Vision*, P. H. Winston, Ed. New York: McGraw-Hill, 1975, pp. 19–91.

[5] A. Borning, "ThingLab: A Constraint-Oriented Simulation Laboratory," Ph.D. dissertation, Stanford University, 1979.

[6] G. J. Sussman and G. L. Steele Jr., "CONSTRAINTS: A Language for Expressing Almost-Hierarchical Descriptions," *Artificial Intelligence*, vol. 14, no. 1, pp. 1–39, 1980.

[7] A. Radul and G. J. Sussman, "The Art of the Propagator," MIT CSAIL Technical Report, 2009.

[8] J. Jaffar and J.-L. Lassez, "Constraint Logic Programming," in *Proceedings of the 14th ACM SIGACT-SIGPLAN Symposium on Principles of Programming Languages*, 1987, pp. 111–119.

[9] R. L. Dykstra, "An Algorithm for Restricted Least Squares Regression," *Journal of the American Statistical Association*, vol. 78, no. 384, pp. 837–842, 1983.

[10] B. Shneiderman, "Direct Manipulation: A Step Beyond Programming Languages," *IEEE Computer*, vol. 16, no. 8, pp. 57–69, 1983.

[11] M. Beaudouin-Lafon, "Instrumental Interaction: An Interaction Model for Designing Post-WIMP User Interfaces," in *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems*, 2000, pp. 446–453.

[12] P. Bézier, "Définition numérique des courbes et surfaces I," *Automatisme*, vol. 11, no. 12, pp. 625–632, 1966.

[13] P. de Casteljau, "Outillages méthodes calcul," Technical Report, André Citroën Automobiles SA, Paris, 1959.

[14] G. Stiny and J. Gips, "Shape Grammars and the Generative Specification of Painting and Sculpture," in *IFIP Congress*, 1972, pp. 1460–1465.

[15] B. Hillier and J. Hanson, *The Social Logic of Space*. Cambridge: Cambridge University Press, 1984.

[16] Y. Bai et al., "Constitutional AI: Harmlessness from AI Feedback," arXiv preprint arXiv:2212.08073, 2022.

[17] T. Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools," in *Advances in Neural Information Processing Systems*, 2023.

[18] G. C. Necula, "Proof-Carrying Code," in *Proceedings of the 24th ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages*, 1997, pp. 106–119.

[19] X. Leroy, "Formal Verification of a Realistic Compiler," *Communications of the ACM*, vol. 52, no. 7, pp. 107–115, 2009.

[20] B. C. Smith, "Reflection and Semantics in a Procedural Language," Ph.D. dissertation, MIT, 1982.

[21] N. Chomsky, *Syntactic Structures*. The Hague: Mouton, 1957.

[22] J. D. Foley, A. van Dam, S. K. Feiner, and J. F. Hughes, *Computer Graphics: Principles and Practice*, 2nd ed. Addison-Wesley, 1990.

[23] NeXTSTEP Operating System, NeXT Computer, Inc., 1989.

[24] Apple Computer, Inc., "Newton MessagePad," 1993.

[25] A. A. Lovelace, "Notes on L. F. Menabrea's 'Sketch of the Analytical Engine Invented by Charles Babbage, Esq.'," in *Taylor's Scientific Memoirs*, vol. 3, 1843, pp. 666–731.

[26] H. Wickham, R. François, L. Henry, and K. Müller, "dplyr: A Grammar of Data Manipulation," R package version 1.0, 2023.

[27] M. Castro and B. Liskov, "Practical Byzantine Fault Tolerance," in *Proceedings of the Third Symposium on Operating Systems Design and Implementation*, 1999, pp. 173–186.

[28] L. S. Vygotsky, *Mind in Society: The Development of Higher Psychological Processes*. Cambridge, MA: Harvard University Press, 1978.

[29] L. W. Anderson and D. R. Krathwohl, Eds., *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy of Educational Objectives*. New York: Longman, 2001.

[30] The Coq Development Team, "The Coq Proof Assistant," INRIA, 2024.

[31] L. de Moura et al., "The Lean 4 Theorem Prover and Programming Language," in *Proceedings of the 28th International Conference on Automated Deduction*, 2021, pp. 625–635.

[32] C. Alexander, *A Pattern Language: Towns, Buildings, Construction*. New York: Oxford University Press, 1977.

---

**Appendix A: System Metrics**

| Metric | Value |
|--------|-------|
| Total source lines (Python) | ~55,000 |
| Total source lines (Rust) | ~5,000 |
| Subsystems | 14 |
| Constraint domains | 7 |
| CDL operators | 30+ |
| Knowledge base facts | 2,901 verified entries |
| Kinematic signatures | 50+ symbols |
| Agent pipeline steps | 10 |
| Meta-verification depth | 3 (bounded) |
| Execution bounds (max iterations) | 1,000,000 |
| Execution bounds (max memory) | 100 MB |
| Execution bounds (timeout) | 30 seconds |
| Ledger max entries (in-memory) | 10,000 |
| Vault encryption | AES-256-GCM |
| Key derivation | PBKDF2, 100,000 iterations |
| PBFT fault tolerance | f = ⌊(n-1)/3⌋ |
| Deployment targets | Vercel, AWS Lambda, Render |

**Appendix B: The Newton Lexicon**

| Term | Definition |
|------|-----------|
| **finfr** | Ontological death; the state where g → 0 and the constraint becomes undefined |
| **law** | A pure function in realTinyTalk (always holds, no side effects) |
| **forge** | (v.) To evaluate constraints; (n.) the constraint evaluation engine; (adj.) impure function |
| **Ω** | The admissible region; the set of states satisfying all active constraints |
| **P₀** | Anchor point; subject; initial state; source object |
| **P₃** | Terminus point; object; goal state; target object |
| **H₁, H₂** | Control handles; modifiers; policy parameters; curvature controls |
| **f/g** | The ratio of attempt to reality; forge to ground; claim to truth |
| **Whisper** | Ada Sentinel's communication unit; a quiet signal of potential anomaly |
| **Commit** | Trajectory termination; sentence ending; transaction finalization |

---

*© 2026 Jared Lewis, Ada Computing Company, Houston, Texas. This paper describes the Newton system (v1.2.1) as implemented in the Newton-api repository. Dual licensed: free for education and research; commercial license required for business use.*
