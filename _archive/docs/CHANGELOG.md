# Changelog

**February 1, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

All notable changes to Newton Supercomputer are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.2] - 2026-02-05

### Added

- RealTinyTalk: interactive three-way merge UI with Base/Local/Remote panes, per-hunk chooser, and inline conflict accept buttons (Accept Base / Accept Local / Accept Remote).
- Server-side 3-way merge now uses `git merge-file` when available for a robust merge fallback, with a local algorithm fallback.

### Changed

- Polished merge visuals: hunk highlighting, gutter accents, and inline widgets for fast conflict resolution.

---

## [1.3.1] - 2026-02-01

### Changed

#### Vercel Deployment (Primary Platform)
Newton is now deployed on **Vercel** as the primary platform:

- **Serverless deployment** - Zero-config from GitHub
- **Global edge CDN** - Fast worldwide access
- **Automatic HTTPS** - SSL certificates included
- **vercel.json** - Configuration for rewrites
- **api/index.py** - ASGI entry point for FastAPI

#### Documentation Updates
- Updated all README files for Vercel deployment
- Updated DEPLOYMENT.md with Vercel as primary option
- Updated APP_INVENTORY.md with new deployment info
- Updated QUICK_DEPLOY.md with Vercel instructions
- Updated shared-config.js for Vercel detection

#### Serverless Compatibility
- Automatic detection of Vercel environment
- Background thread disabling in serverless mode
- Serverless-safe ledger storage using /tmp

---

## [1.3.0] - 2026-01-09

### Added

#### Newton Core Phase 1 - Rust Projection Engine (#201)
The mathematical bedrock for Aid-a (Assistive Intelligence for Design Autonomy):

- **`newton_core/`** - New Rust crate for high-performance constraint projection
  - `AIDA_SPEC.md` - Frozen constitution document defining all contracts
  - `src/linalg.rs` - Vector type with arithmetic operations
  - `src/primitives.rs` - NTObject, Bounds, FGState, Delta types
  - `src/constraints/` - Constraint trait implementations
    - `BoxBounds` - min ≤ x ≤ max per dimension
    - `LinearConstraint` - a·x ≤ b (halfspace)
    - `CollisionConstraint` - no overlap with other objects
    - `DiscreteConstraint` - x ∈ {v1, v2, ..., vn}
  - `src/projection/` - Projection algorithms
    - Dykstra's algorithm for convex constraint intersections
    - Halfspace projection (O(1))
    - Weighted projection respecting dimension importance
    - Convex relaxation for nonconvex constraints
  - `src/candidates.rs` - Local search, snap candidates, boundary candidates
  - `src/aida.rs` - Main suggestion engine with `suggest()` entry point

- **Aid-a Contract Guarantees:**
  1. **Validity** - All suggestions satisfy all constraints
  2. **Determinism** - Identical inputs produce identical outputs
  3. **Termination** - Completes within bounded time/iterations
  4. **Non-empty** - Returns at least one suggestion if feasible

- **Testing:** 122+ tests passing
  - 7 property tests using proptest (10K+ cases each)
  - 10 adversarial tests for edge cases (thin slabs, oscillation, skewed weights)
  - 4 doc tests
  - Benchmarks with Criterion for projection and candidate generation

- **CI/CD:** `.github/workflows/aida-contract.yml` for contract enforcement

#### Newton Fact-Checker for GPT Market Analysis (#202)
Using Newton's constraint logic to verify AI claims:

- **`fact_check_gpt.py`** - Standalone fact-checker
- **`fact_check_gpt_standalone.py`** - No-dependency version
- Verifies GPT's claims about Newton's market presence against actual evidence

**Results:**
| Claim | Evidence | Status |
|-------|----------|--------|
| Energy/EV | 0% | FABRICATED |
| Smart Cities | 0% | FABRICATED |
| Traffic | 18% | FABRICATED (claimed "strongest") |
| Education | 95% | MISSED (actual strongest) |
| AI Safety | 97% | MISSED |
| Developer Tools | 97% | MISSED |

*"The constraint IS the instruction. The evidence IS the truth."*

#### Construct Studio v0.1 - Constraint-First Execution Environment (#196, #197, #198)
A Logic CAD Tool where the constraint IS the instruction:

- **`construct-studio/`** - New module for business physics simulation
  - `core.py` - Matter, Floor, Force, Ratio, ConstructError
  - `ledger.py` - Immutable audit trail
  - `engine.py` - Simulation engine
  - `cli.py` - Interactive REPL
  - `cartridges/` - Domain modules
    - `finance.py` - Corporate cards, budgets
    - `infrastructure.py` - Deployment quotas
    - `risk.py` - Probability budgets
  - `ui/index.html` - Visual CAD interface

- **Core Concepts:**
  - **Matter** - Typed value with units (e.g., `Matter(1500, "USD")`)
  - **Floor** - Constraint container (boundary of valid design space)
  - **Force (>>)** - Physics operator applying Matter to Floor
  - **Ontological Death** - Invalid states cannot exist

- **Key Insight:** Pre-approval by physics, not by process.

#### HyperCard 2026 - Complete Modern Remake (#195)
A complete HyperCard implementation for Swift Playgrounds:

- **`examples/HyperCard2026.swift`** - 2,500+ lines of pure Swift
  - Card & Stack Management
  - PencilKit Drawing
  - Drag-and-Drop UI Elements
  - HyperTalk-Inspired Scripting
  - Card Transitions (Dissolve, Wipe, Push, etc.)
  - Newton Avenue AI Assistant
  - Sound & Media Support
  - Properties Inspector
  - Script Editor with Syntax Highlighting
  - Undo/Redo Support
  - Search Across Stacks
  - Import/Export Capabilities

*"The Dynabook dream, realized in Swift."*

### Fixed

#### Frontend Mobile Navigation (#200)
- Added mobile navigation menu
- Added "All Apps" section for quick access
- Improved responsive layout

#### CAD Basement Grounding (#199)
- Fixed basement levels grounding in 3D renders
- Proper Z-axis positioning for underground structures

### Test Results

| Test Suite | Results | Status |
|------------|---------|--------|
| Newton Core (Rust) | 122/122 | ✓ 100% |
| Newton TLM (ACID) | 23/23 | ✓ 100% |
| Main Test Suite | 558/586 | ✓ 95% |
| Full System Test | 10/10 | ✓ 100% |

**Total Tests:** 700+ passing

---

## [1.2.1] - 2026-01-07

### Added

#### Cohen-Sutherland Constraint Clipping Model (#183)
Semantic constraint clipping - not just pass/fail, but finding what CAN be done:

- **`/clip` endpoint** - Apply Cohen-Sutherland inspired clipping to requests
  - GREEN: Both endpoints inside constraint bounds → execute fully
  - YELLOW: Mixed validity → clip to boundary, execute valid portion
  - RED: Both endpoints outside bounds → finfr (truly impossible)

- **ClipState enum** - Three-state model for constraint satisfaction
- **ClipResult dataclass** - Rich response with negotiation, not just pass/fail
- **Clippable constraints** - Harm, medical, legal boundaries with alternatives
- This is the key insight: **Don't just reject. Find what CAN be done.**

#### Morphic to Newton Evolution Documentation (#182)
Computer science grade analysis of Newton's lineage:

- **`docs/product-architecture/MORPHIC_TO_NEWTON_EVOLUTION.md`** - 410 lines
  - From Morphic (Self/Squeak) direct manipulation to Newton verified manipulation
  - Generation 0-4: Smalltalk → Self → Squeak → Scratch → Newton
  - The f/g ratio as visual Morphic state
  - "What you see is what you've verified"
  - Complete mapping: Halo → Constraint Glyph, Step → Verification Loop
  - The Dynabook with proof

#### Auto-Discovering Newton SDK v3.0 (#181)
Single-file SDK with automatic endpoint discovery:

- **`sdk/newton.py`** - Drop-in Python SDK
  - Auto-discovers all 115 endpoints from `/openapi.json`
  - 15 namespaces: cartridge, education, teachers, voice, vault, ledger, jester, etc.
  - NewtonResponse with `.success`, `.data`, `.verified`, `.merkle_root`
  - Error hierarchy: NewtonError, NewtonConnectionError, NewtonAuthError
  - CLI mode with `python newton.py`
  - Only dependency: `requests`

- **Usage**:
  ```python
  from newton import Newton
  n = Newton()
  result = n.ask("Is this safe?")
  ```

---

## [1.2.0] - 2026-01-06

### Added

#### Newton API Intro Course - 5-Level PDA Tutorial (#173)
Complete educational course for building a Personal Digital Assistant:

- **`docs/INTRO_COURSE.md`** - 5-level progressive tutorial (752 lines)
  - Level 1: Basic Blueprint - State and structure
  - Level 2: Laws - Constraints that cannot be broken
  - Level 3: Forges - Actions that respect laws
  - Level 4: Task Management - Multi-object coordination
  - Level 5: Full PDA - Complete personal assistant

- **New Example Files** (5 runnable demos)
  - `examples/pda_level1.py` - Basic Blueprint demo
  - `examples/pda_level2.py` - Laws demo
  - `examples/pda_level3.py` - Forges demo
  - `examples/pda_level4.py` - Task Management demo
  - `examples/pda_level5.py` - Full PDA demo

#### R/RStudio Quickstart Guide (#172)
Integration guide for R users:

- **`RSTUDIO_QUICKSTART.md`** - Complete R integration guide (298 lines)
  - Local mode using tinyTalk
  - Remote mode using Newton API client
  - Trading risk management demo
  - Type safety with Matter types (Money, Mass, Distance)
  - Runnable examples for R/RStudio

#### Newton Typed Dictionary - Words Become Laws (#170)
Constraint-aware dictionary system:

- **`core/typed_dictionary.py`** - Typed dictionary implementation (43KB)
  - Every word carries semantic constraints
  - Algebraic properties and type constraints
  - Legal implications for vocabulary
  - Type-safe vocabulary with mathematical guarantees

#### PARADOX Detection Phase (#168)
Contradiction detection in Newton TLM:

- Added PARADOX phase to phase system (0→9→0)
- Detects when two constraints create impossible state (1 == 0)
- Halts at PARADOX phase rather than computing invalid results
- Newton's answer to the halting problem

#### Newton Setup Scripts - One-Command Installation
- **`setup_newton.sh`** - Comprehensive setup script for local installation
  - Creates Python virtual environment
  - Installs all dependencies from requirements.txt
  - Runs verification tests (TLM + core tests)
  - Tests server startup and endpoint health
  - Provides quick reference commands on completion

- **`test_full_system.py`** - Full system integration test
  - Tests all 10 major Newton subsystems
  - Health check, Forge verification, CDL constraints
  - Logic engine, Ledger, Cartridges (auto, rosetta, visual)
  - Robust statistics, Ratio constraints (f/g)
  - Colorized output with timing information
  - Exit code indicates pass/fail for CI/CD

#### Newton TLM - Topological Language Machine (#158)
New symbolic computation kernel with ACID compliance:

- **Phase System** (0→9→0)
  - Phase 0: IDLE - Ready, no mutations
  - Phase 1: INGEST - Accept input
  - Phase 2: PARSE - Structure input
  - Phase 3: CRYSTALLIZE - Form patterns
  - Phase 4: DIFFUSE - Spread activation
  - Phase 5: CONVERGE - Stabilize
  - Phase 6: VERIFY - Check constraints (1==1)
  - Phase 7: COMMIT - Apply changes
  - Phase 8: REFLECT - Learn from results
  - Phase 9: Return to IDLE

- **ACID Compliance**
  - Atomicity: Transactions complete fully or rollback
  - Consistency: Deterministic execution
  - Isolation: Independent instances
  - Durability: Export/replay with ledger persistence

- **Newton Compliance (N1-N7)**
  - N1: Determinism - Same input → same output
  - N2: Boundary enforcement - Phase limits respected
  - N3: Diffability - Hash-chained ledger tracking
  - N4: Reversibility - Snapshot/restore capability
  - N5: Phase loop - 0→9→0 cycle guaranteed
  - N6: 1==1 invariant - Goal registry verification
  - N7: Ledger integrity - Cryptographic verification

- **23 passing tests** proving all invariants

#### Newton Geometry - Topological Constraint Framework (#163)
Mathematical foundation for constraint systems:

- **TopologicalSpace** - Base manifold for constraints
- **ConstraintManifold** - Geometric constraint representation
- **MorphismFunctor** - Structure-preserving transformations
- **GeometricVerifier** - Topological invariant verification
- **newton_geometry/tests/** - Comprehensive test coverage

#### Newton TextGen - Constraint-Preserving Text Projection (#159)
Text generation that cannot hallucinate:

- **Core Guarantee**: `Expand . Reduce = Identity`
- **Styles**: formal, technical, educational, minimal
- **TextConstraint** class for structured constraints
- If text cannot reduce to source constraint → REJECTED
- Enables law-aware documentation without semantic drift

### Fixed

- **27 Failing Tests Resolved** (#171)
  - Fixed chatbot, constraints, and dictionary test failures
  - Updated test references for new module structure
  - All affected tests now passing

- **Test Import Path** - Fixed `tests/test_ratio_constraints.py` import
  - Changed `from core import` to `from tinytalk_py.core import`
  - Resolves module path conflict with core/ package

- **Mobile Responsive CSS** (#162)
  - Fixed Teacher's Aide dark mode
  - Fixed Interface Builder mobile layout
  - Improved touch targets and spacing

### Changed

- **Repository Cleanup** (#161)
  - Consolidated codebase structure
  - Improved module organization
  - Updated import paths for consistency

### Test Results

| Test Suite | Results | Status |
|------------|---------|--------|
| Newton TLM (ACID) | 23/23 | ✓ 100% |
| Main Test Suite | 558/586 | ✓ 95% |
| Full System Test | 10/10 | ✓ 100% |

---

## [1.1.0] - 2026-01-02

### Added

#### Teacher's Aide Database - Classroom Management for Teachers

Complete classroom management system with automatic differentiation, designed to make teachers' lives easier:

- **Student Management** (`/teachers/students/*`)
  - Track students with accommodations (ELL, SPED, 504, GT, Dyslexia, RTI)
  - Add students individually or in batch
  - Search by name with partial matching
  - Automatic mastery tracking per TEKS standard

- **Classroom Management** (`/teachers/classrooms/*`)
  - Create classrooms with grade, subject, and teacher info
  - Manage class rosters
  - Track current TEKS focus
  - Get class roster sorted by last name

- **Assessment Tracking** (`/teachers/assessments/*`)
  - Create assessments linked to TEKS codes
  - Enter scores by student ID or **by name (quick-scores)**
  - Automatic calculation of class average and mastery rate
  - Student grouping after each assessment

- **Auto-Differentiation** - The Key Feature!
  - Students automatically grouped into 4 tiers:
    - **Tier 3 (Needs Reteach)**: Below 70% - Small group with teacher
    - **Tier 2 (Approaching)**: 70-79% - Guided practice with scaffolds
    - **Tier 1 (Mastery)**: 80-89% - Standard instruction
    - **Enrichment (Advanced)**: 90%+ - Extension activities
  - Groups update automatically after each assessment
  - Includes instruction recommendations per tier

- **Intervention Plans** (`/teachers/interventions`)
  - Create intervention plans for student groups
  - Auto-populate students from current grouping
  - Track progress with notes

- **Extended TEKS Database**
  - 188 TEKS standards (K-8)
  - Covers Math, Reading/ELA, Science, Social Studies
  - Filter by grade and subject
  - Statistics endpoint for database info

- **Data Persistence**
  - Save database to JSON file
  - Load database from JSON file
  - Portable data for backup and transfer

#### New Files
- `tinytalk_py/teachers_aide_db.py` (1,115 lines)
- `tinytalk_py/teks_database.py` (1,334 lines)

#### New Endpoints (20+)
- `/teachers/db` - Database summary
- `/teachers/students` - Student CRUD
- `/teachers/classrooms` - Classroom management
- `/teachers/classrooms/{id}/groups` - **Get differentiated groups**
- `/teachers/classrooms/{id}/reteach` - Get reteach group
- `/teachers/assessments` - Assessment management
- `/teachers/assessments/{id}/scores` - Enter scores by ID
- `/teachers/assessments/{id}/quick-scores` - Enter scores by name
- `/teachers/interventions` - Intervention planning
- `/teachers/teks` - Extended TEKS (188 standards)
- `/teachers/teks/stats` - TEKS statistics
- `/teachers/db/save` - Save database
- `/teachers/db/load` - Load database
- `/teachers/info` - API documentation

---

#### Cartridge Layer - Media Specification Generation

Newton now generates verified specifications for media content through the Cartridge system:

- **Visual Cartridge** (`/cartridge/visual`) - SVG/image specifications
  - Max 4096x4096 resolution, 1000 elements, 256 colors
  - Auto-detects elements (circle, rect, text, polygon, etc.)
  - Style and color scheme parsing

- **Sound Cartridge** (`/cartridge/sound`) - Audio specifications
  - Max 5 minutes duration, 1-22050 Hz frequency range
  - Sample rates: 22050, 44100, 48000, 96000 Hz
  - Sound type detection (tone, melody, ambient, voice, etc.)

- **Sequence Cartridge** (`/cartridge/sequence`) - Video/animation specifications
  - Max 10 minutes, up to 8K resolution, 1-120 fps
  - Transition detection (fade, cut, wipe, zoom)
  - Type detection (video, animation, slideshow, timelapse)

- **Data Cartridge** (`/cartridge/data`) - Report specifications
  - Max 100,000 rows, formats: JSON, CSV, Markdown, HTML
  - Report type detection (financial, analytics, trend, etc.)
  - Built-in statistics calculation

- **Rosetta Compiler** (`/cartridge/rosetta`) - Code generation prompts
  - Platforms: iOS, iPadOS, macOS, watchOS, visionOS, tvOS, web, Android
  - Languages: Swift, Python, TypeScript
  - Auto-detects frameworks (HealthKit, CoreML, ARKit, etc.)
  - App Store and security constraint verification

- **Auto Cartridge** (`/cartridge/auto`) - Automatic type detection and compilation

- **Cartridge Info** (`/cartridge/info`) - Get cartridge information

#### Core Changes
- New `core/cartridges.py` module (1,015 lines)
- `CartridgeManager` for unified cartridge access
- All cartridge operations recorded in immutable ledger
- Safety constraint verification on all intents

---

## [1.0.0] - 2026-01-01

### Genesis

```
Flash-3 Instantiated // 50 seconds // AI Studio
The Interface Singularity: Full frontend instantiation in 50s.
```

**The market price of generated code is zero. The value is in the triggering, verification, and ownership of the keys.**

### Added

#### Core Components
- **CDL 3.0** - Constraint Definition Language with temporal, conditional, and aggregation operators
- **Logic Engine** - Verified Turing-complete computation with bounded execution
- **Forge** - Parallel verification engine with sub-millisecond latency
- **Vault** - AES-256-GCM encrypted storage with identity-derived keys
- **Ledger** - Append-only, hash-chained audit trail with Merkle proofs
- **Bridge** - PBFT-inspired Byzantine fault-tolerant consensus
- **Robust** - Adversarial-resistant statistics (MAD, locked baselines)
- **Grounding** - Claim verification against external sources

#### Glass Box Layer
- **Policy Engine** - Policy-as-code enforcement (pre/post operation)
- **Negotiator** - Human-in-the-loop approval workflows
- **Merkle Anchor** - Scheduled proof generation and export
- **Vault Client** - Provenance logging for all operations

#### Tahoe Kernel
- **newton_os.rb** - Knowledge Base with origin truth
- **newton_tahoe.rb** - PixelEngine with genesis mark

#### API (30+ Endpoints)
- `/ask` - Full verification pipeline
- `/verify` - Content safety verification
- `/calculate` - Verified computation
- `/constraint` - CDL constraint evaluation
- `/ground` - Claim grounding
- `/statistics` - Robust statistical analysis
- `/vault/store`, `/vault/retrieve` - Encrypted storage
- `/ledger`, `/ledger/{index}` - Audit trail
- `/policy` - Policy management
- `/negotiator/*` - Approval workflows
- `/merkle/*` - Proof generation

#### Infrastructure
- FastAPI server with OpenAPI documentation
- CLI verification tool (`cli_verifier.py`)
- Web frontend (PWA)
- Render.com deployment configuration
- Docker support
- Comprehensive test suite (47 tests)

### Proven Properties
- **Determinism** - Same input → same output, always
- **Termination** - HaltChecker proves all constraints terminate
- **Consistency** - No constraint can both pass and fail
- **Auditability** - Every operation in immutable ledger
- **Adversarial Resistance** - MAD stats, locked baselines
- **Byzantine Tolerance** - Consensus survives f=(n-1)/3 faulty nodes
- **Bounded Execution** - No infinite loops, no stack overflow
- **Cryptographic Integrity** - Hash chains, Merkle proofs

---

## [0.x] - 2025 (Legacy)

Historical Ruby implementation preserved in `legacy/` directory.

- `newton_api.rb` - Original Sinatra-based API
- `adapter_universal.rb` - Universal vendor adapter
- `newton_os_server.py` - Python v1-v2 experiments

---

## The Invariant

```
1 == 1
```

Every version. Every commit. Every verification.

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas
