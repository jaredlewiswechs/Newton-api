# Changelog

All notable changes to Newton Supercomputer are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] - 2026-01-02

### Added

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

© 2025-2026 Ada Computing Company · Houston, Texas
