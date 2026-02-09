#NewtonKnows

A code-level feature map of this repository, tied directly to computer science concepts.

> Note: this inventory was built from implementation files (APIs, engines, parsers, kernels, UIs), not just existing READMEs.

## 1) Core Runtime + API Surface (Newton Supercomputer)

### Featured capabilities from code
- **Unified FastAPI control plane** with endpoints for: verification, constraints, extraction, chatbot compilation, vault/ledger/policy/negotiation, interface generation, education workflows, teachers DB, voice, licensing, and telemetry.
- **Serverless-aware runtime behavior** (conditional scheduler startup, writable temp storage strategy).
- **Pipeline architecture** where `ask`, `verify`, `constraint`, `ground`, `calculate`, and domain cartridges are first-class API primitives.

### CS concepts
- **Distributed systems / service orchestration**: one façade coordinating many subsystems.
- **API design & protocol boundaries**: typed request/response models (Pydantic) and explicit endpoint taxonomy.
- **Reliability engineering**: environment-aware execution paths (serverless vs process mode).

---

## 2) tinyTalk Language + Formal Constraint Runtime

### Featured capabilities from code
- **Law-driven execution model** with `fin`/`finfr` semantics, law decorators, and controlled state transitions.
- **Blueprint + field + forge pattern** for declarative object modeling and constrained mutation.
- **Kinetic engine** with `Presence` → `Delta` motion computation, boundary checks, and interpolation frames.
- **Multi-implementation stack**:
  - Python implementation (`src/newton/tinytalk/*`)
  - C implementation (`tinytalk-lang/src/*.c` tokenizer/parser/runtime)
  - Objective-C implementation (`tinytalk-objc/*`)
  - IDE integration (`tinytalk-ide/*` + VSCode extension)

### CS concepts
- **Programming language design**: custom semantics for safety constraints.
- **Compilers/interpreters**: lexing, parsing, runtime execution across languages.
- **Formal methods**: illegal states represented as non-admissible computations.
- **State machines / transition systems**: motion as verifiable state delta.

---

## 3) Constraint Compilation + Governance Layer

### Featured capabilities from code
- **Constraint extractor** that converts fuzzy natural language into formalized constraints and verifies plans.
- **Chatbot compiler** that classifies request type/risk and chooses a governance decision (`answer`, `ask`, `defer`, `refuse`).
- **Jester analyzer** for code constraint analysis and source-language/kind taxonomies.

### CS concepts
- **NLP-to-IR compilation**: transforming text prompts into structured intermediate representations.
- **Policy engines**: rule-based decisioning under risk classes.
- **Program analysis**: static-ish categorization and constraint checking.

---

## 4) Cryptographic Integrity + Auditability

### Featured capabilities from code
- **Ledger + certificate style retrieval endpoints**.
- **Merkle anchor scheduling/proofs** and anchor introspection APIs.
- **Policy + negotiation endpoints** for approval workflows and access governance.
- **History verification hashes** in image editor undo/redo entries.

### CS concepts
- **Applied cryptography**: hash chains / Merkle proofs for tamper evidence.
- **Audit log design**: immutable or append-style accountability structures.
- **Security architecture**: policy enforcement and approval gating.

---

## 5) Knowledge + Education Tooling

### Featured capabilities from code
- **Education cartridge** APIs for lessons, slides, assessments, PLC workflows.
- **TEKS/standards libraries** and search endpoints.
- **Teacher’s Aide database model** for students, classrooms, assessments, interventions, and mastery tracking.
- **Gradebook/education modules in TinyTalk Python package**.

### CS concepts
- **Domain modeling**: educational entities + workflows encoded as typed data.
- **Information retrieval**: standards lookup and constrained search.
- **Decision support systems**: mastery and intervention recommendations.

---

## 6) Newton OS (TS + Python) Object-Graph Computing

### Featured capabilities from code
- **Object graph kernel** (`NObjectGraph`) with typed objects, relationship edges, mutation streams, and constraint-based querying.
- **Reactive architecture** using Rx streams for mutation observability.
- **Parallel Python implementation** (`newton-os-py`) demonstrating concept portability.

### CS concepts
- **Graph data structures**: node/edge-centered state management.
- **Reactive systems**: publish/subscribe event propagation.
- **Data model abstraction**: “query by constraint, not by path.”

---

## 7) Construct Studio (Constraint CAD for Governance)

### Featured capabilities from code
- **Matter/Capacity/Floor primitives** with unit-safe arithmetic and compatibility checks.
- **Force operator (`>>`)** to apply resources/loads against capacities.
- **Ontological death semantics** for invalid design branches.
- **Cartridges** for finance, risk, and infrastructure planning.

### CS concepts
- **Type systems + dimensional analysis** for safer arithmetic.
- **Constraint satisfaction / feasibility analysis**.
- **DSL-ish operator overloading** for domain modeling.

---

## 8) Newton Image (Desktop Graphics System)

### Featured capabilities from code
- **Document/layer/tool/filter subsystems**.
- **Verified undo/redo** via bounded history manager with hash-verifiable entries.
- **Qt signal-driven UI modules** (toolbar, canvas, inspector, adjustments, layers panel).

### CS concepts
- **Persistent state + command history**.
- **UI architecture patterns** (event-driven programming).
- **Integrity checks** in local state transitions.

---

## 9) Statsy DSL + Visualization

### Featured capabilities from code
- **Stats-focused DSL runtime** (`statsy.py`) plus web visualization adapter.
- **Example corpus** for hypotheses, visualization, stress and syntax edge cases.

### CS concepts
- **Domain-specific language design**.
- **Parser/runtime for data analysis expressions**.
- **Visualization pipeline integration**.

---

## 10) Client/Platform Surfaces

### Featured capabilities from code
- **CLI (`newton`)** with serve/calc/verify/health/demo/init lifecycle commands.
- **Web frontends** (mission-control, teachers-aide, frontend, voicepath).
- **iOS Swift app shell** with calculation/verification/dashboard/settings screens.
- **Game/demo apps** (gravity_wars, demos) for experiential validation.

### CS concepts
- **Human-computer interaction**: multiple interfaces over one computational core.
- **Cross-platform architecture**: shared backend contracts across web/CLI/mobile.
- **Software productization**: onboarding, deployment, and demo-first ergonomics.

---

## 11) Cross-Cutting CS Patterns Present Throughout

- **Formal verification mindset**: constraints are first-class executables, not comments.
- **Safe-state modeling**: invalid transitions are rejected before state commit.
- **Composable systems**: cartridges, modules, and endpoint families reveal plug-in architecture.
- **Language/toolchain experimentation**: one conceptual model implemented in Python, TypeScript, C, Objective-C, and Swift-adjacent interfaces.
- **Traceability over opacity**: ledgers, hashes, certificates, and endpoint-level introspection.

---

## 12) Quick “Feature Index” by Implementation Area

- `newton_supercomputer.py`: mega-API and system composition root.
- `src/newton/tinytalk/*`: tinyTalk language/runtime in Python.
- `tinytalk-lang/src/*`: C lexer/parser/runtime.
- `core/constraint_extractor.py`, `core/chatbot_compiler.py`: natural-language governance compiler stack.
- `newton-os/core/*`, `newton-os-py/core/*`: object-graph OS kernels.
- `construct-studio/*`: constraint CAD engine and governance cartridges.
- `newton-image/*`: image editor core + UI + verified history.
- `tinytalk_py/education.py`, `tinytalk_py/teachers_aide_db.py`: education and classroom intelligence.
- `statsy/*`: statistical DSL + web visualization.
- `ios/Newton/Sources/*`: iOS client feature surface.

If you want, I can generate a second pass that is strictly machine-counted (e.g., endpoint counts, module counts, class/function inventories) and append it as an “Appendix: Quantitative Inventory.”
