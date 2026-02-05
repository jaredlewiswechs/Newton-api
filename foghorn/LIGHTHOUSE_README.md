# 🏠 Lighthouse README

## Project Foghorn: Nina Desktop

```
═══════════════════════════════════════════════════════════════════════════════
   ██╗     ██╗ ██████╗ ██╗  ██╗████████╗██╗  ██╗ ██████╗ ██╗   ██╗███████╗███████╗
   ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝██║  ██║██╔═══██╗██║   ██║██╔════╝██╔════╝
   ██║     ██║██║  ███╗███████║   ██║   ███████║██║   ██║██║   ██║███████╗█████╗  
   ██║     ██║██║   ██║██╔══██║   ██║   ██╔══██║██║   ██║██║   ██║╚════██║██╔══╝  
   ███████╗██║╚██████╔╝██║  ██║   ██║   ██║  ██║╚██████╔╝╚██████╔╝███████║███████╗
   ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
                                                                                  
   Nina Desktop — A Verified Computing Environment
   Branch: foghorn/nina-desktop
═══════════════════════════════════════════════════════════════════════════════
```

> "The constraint IS the instruction. The verification IS the computation."

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Architecture Overview](#architecture-overview)
3. [The Kernel](#the-kernel)
4. [Object System](#object-system)
5. [User Interface](#user-interface)
6. [Server & API](#server--api)
7. [Integrated Engines](#integrated-engines)
8. [Styling System](#styling-system)
9. [Applications](#applications)
10. [File Structure](#file-structure)
11. [Running the System](#running-the-system)
12. [Roadmap](#roadmap)

---

## Philosophy

Nina Desktop is **verified computing made visual**. Every window, every card, every calculation flows through Newton's verification engine. The UI isn't decoration—it's the interface to deterministic truth.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Traditional Computing          Nina Desktop                   │
│   ─────────────────────          ────────────                   │
│   Input → Process → Output       Input → Verify → Compute →    │
│                                         ↓           ↓          │
│                                      Constraint   Proof         │
│                                         ↓           ↓          │
│                                      ← ← ← ← ← ← ← ←           │
│                                         Output                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Core Tenets:**
- Every operation is bounded and terminates
- Every result can be verified
- Every interaction leaves an audit trail
- The UI reflects the state of verified truth

---

## Architecture Overview

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           NINA DESKTOP ARCHITECTURE                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                         PRESENTATION LAYER                              │  ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  ║
║  │  │ Menu Bar │ │ Sidebar  │ │ Windows  │ │Inspector │ │   Dock   │      │  ║
║  │  │  (Nina)  │ │(Objects) │ │  (Apps)  │ │ (Detail) │ │  (Apps)  │      │  ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  ║
║  │                          desktop.js + desktop.css                       │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                     │                                         ║
║                                     ▼                                         ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                          SERVER LAYER (server.py)                       │  ║
║  │  ┌───────────────────────────────────────────────────────────────────┐  │  ║
║  │  │                     HTTP Server (port 8000)                       │  │  ║
║  │  │  /foghorn/cards    /foghorn/ground    /foghorn/calculate          │  │  ║
║  │  │  /foghorn/verify   /foghorn/semantic  /foghorn/kinematics         │  │  ║
║  │  └───────────────────────────────────────────────────────────────────┘  │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                     │                                         ║
║                                     ▼                                         ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                          KERNEL LAYER                                   │  ║
║  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │  ║
║  │  │    Nina     │ │   Newton    │ │     Ada     │ │   Ollama    │       │  ║
║  │  │   Kernel    │ │   Logic     │ │  Sentinel   │ │   + Qwen    │       │  ║
║  │  │  (Regime)   │ │  (Engine)   │ │ (Watchdog)  │ │   (AI)      │       │  ║
║  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │  ║
║  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       │  ║
║  │  │  Kinematic  │ │  Semantic   │ │  Adanpedia  │                       │  ║
║  │  │ Linguistics │ │  Resolver   │ │ (Knowledge) │                       │  ║
║  │  └─────────────┘ └─────────────┘ └─────────────┘                       │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                     │                                         ║
║                                     ▼                                         ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                          CORE LAYER (Newton)                            │  ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  ║
║  │  │   CDL    │ │  Forge   │ │  Vault   │ │  Ledger  │ │  Bridge  │      │  ║
║  │  │Constraint│ │ Verify   │ │Encrypted │ │  Audit   │ │Consensus │      │  ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## The Kernel

### Nina Kernel (`nina/developer/forge/`)

The Nina kernel provides **Pipeline** and **Regime** abstractions for structured computation:

```python
from nina.developer.forge import Pipeline, Regime, RegimeType

# A Regime defines how computation proceeds
regime = Regime(
    type=RegimeType.SEQUENTIAL,
    constraints=["bounded", "verified"]
)

# A Pipeline chains verified operations
pipeline = Pipeline(regime=regime)
pipeline.add_stage("parse", parser)
pipeline.add_stage("verify", verifier)
pipeline.add_stage("compute", engine)

result = pipeline.execute(input_data)
```

**Regime Types:**
- `SEQUENTIAL` — Steps execute in order
- `PARALLEL` — Steps execute concurrently (bounded)
- `REACTIVE` — Steps respond to events
- `VERIFIED` — Each step produces a proof

### Knowledge Base (`nina/developer/forge/knowledge.py`)

```python
from nina.developer.forge.knowledge import get_nina_knowledge

knowledge = get_nina_knowledge()
# Returns structured facts, patterns, and inference rules
```

---

## Object System

### Foghorn Objects (`foghorn/__init__.py`)

Everything in Nina Desktop is an **Object**. Objects are content-addressable, immutable, and verifiable.

```
╔═══════════════════════════════════════════════════════════════╗
║                      FOGHORN OBJECT TYPES                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📝 Card          — Rich text with metadata                   ║
║  🔍 Query         — Search/filter definition                  ║
║  📊 ResultSet     — Materialized query results                ║
║  📁 FileAsset     — External file reference                   ║
║  ✓  Task          — Action with verification                  ║
║  🧾 Receipt       — Proof of completed operation              ║
║  🔗 LinkCurve     — Bézier relationship between objects       ║
║  📋 Rule          — Constraint or policy definition           ║
║  📍 MapPlace      — Geographic location                       ║
║  🛣️  Route         — Path between places                       ║
║  ⚡ Automation    — Triggered action sequence                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Object Identity

Every object has a **content-derived hash**:

```python
from foghorn import Card

card = Card(
    title="Welcome to Nina",
    body="This is verified computing.",
    tags=["intro", "welcome"]
)

print(card.hash)  # SHA-256: 12b8b1a98dd13294...
print(card.short_id)  # 12b8b1a9
```

### Object Store (`foghorn/objects.py`)

```python
from foghorn.objects import get_object_store

store = get_object_store()
store.add(card)
store.add(query)

# Retrieve by hash
obj = store.get("12b8b1a98dd13294")

# Filter by type
cards = store.filter(type="card")
```

---

## User Interface

### Wireframe Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ⭐ Nina   File   Edit   View   Objects   Services   Window   Help    8:00 PM│
├──────────┬─────────────────────────────────────────────────────────────────┤
│          │                                                                 │
│ Workspace│    ┌──────────────────────────────────────┐                     │
│ ─────────│    │ ● ● ●              Search            │                     │
│          │    ├──────────────────────────────────────┤                     │
│ [All]    │    │ ┌────────────────────────────────┐   │                     │
│ Cards    │    │ │ Search with Adanpedia...       │   │                     │
│ Queries  │    │ └────────────────────────────────┘   │                     │
│ Files    │    │                                      │                     │
│          │    │ [🧠 Semantic] [📁 Local] [📐 Kinematic]│                     │
│ ─────────│    │                                      │                     │
│ 📝 Welcome│    │         🧠                           │                     │
│ 📝 Getting│    │    Search results appear here       │                     │
│          │    │                                      │                     │
│          │    └──────────────────────────────────────┘                     │
│          │                                                                 │
│          │                                                                 │
├──────────┴─────────────────────────────────────────────────────────────────┤
│                                                                            │
│            📁   🗂️   🔍   🗺️   🔢   ✓   🐕   📚   │   🔬   ⚙️              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### UI Components

| Component | Element | Purpose |
|-----------|---------|---------|
| **Menu Bar** | `#menubar` | System menu, clock, status |
| **Sidebar** | `#sidebar` | Object browser with filters |
| **Windows Container** | `#windows-container` | Floating app windows |
| **Inspector** | `#inspector` | Object detail panel |
| **Dock** | `#dock` | App launcher (bottom) |
| **Command Palette** | `#command-palette` | ⌘K quick actions |

### Window Anatomy

```
┌─────────────────────────────────────────────────────────┐
│ ● ● ●                    Window Title            [═][□] │  ← Title bar with traffic lights
├─────────────────────────────────────────────────────────┤
│                                                         │
│                                                         │
│                    Window Content                       │  ← .window-content
│                                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                      ◢  │  ← Resize handle
└─────────────────────────────────────────────────────────┘
```

**Window Features:**
- Draggable by title bar
- Resizable from corner
- Traffic light buttons (close/minimize/maximize)
- Frosted glass background
- Squircle corners (Apple HIG)

---

## Server & API

### Server (`foghorn/shell/server.py`)

The server exposes a REST API at `http://localhost:8000`:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              API ENDPOINTS                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  OBJECTS                                                                      ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  GET  /foghorn/cards           — List all cards                               ║
║  POST /foghorn/card            — Create new card                              ║
║  GET  /foghorn/card/:id        — Get card by ID                               ║
║                                                                               ║
║  VERIFICATION                                                                 ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  POST /foghorn/verify          — Verify content integrity                     ║
║  POST /foghorn/ground          — Fact-check a claim (local → AI)              ║
║  POST /foghorn/constraint      — Evaluate CDL constraint                      ║
║                                                                               ║
║  COMPUTATION                                                                  ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  POST /foghorn/calculate       — Verified math (TI-84 style)                  ║
║  POST /foghorn/calculate/examples — Get expression examples                   ║
║                                                                               ║
║  KNOWLEDGE                                                                    ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  POST /foghorn/semantic        — Semantic search + Adanpedia                  ║
║  POST /foghorn/kinematics      — Kinematic text analysis                      ║
║                                                                               ║
║  SYSTEM                                                                       ║
║  ────────────────────────────────────────────────────────────────────────     ║
║  GET  /health                  — Server health check                          ║
║  GET  /index.html              — Nina Desktop UI                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Startup Sequence

```
✓ Nina kernel loaded
✓ Newton Logic Engine loaded
✓ Ada Sentinel loaded
✓ Kinematic Linguistics loaded
✓ Semantic Resolver + Adanpedia loaded
✓ Ollama + qwen2.5:3b loaded
🗂️  Adding demo objects...
   4 objects ready

🖥️  Starting Nina Desktop at http://localhost:8000/index.html
   API available at http://localhost:8000/foghorn/*
```

---

## Integrated Engines

### Newton Logic Engine (`core/logic.py`)

The verified computation engine. Every calculation is bounded and deterministic.

```python
from core.logic import LogicEngine, ExecutionBounds

bounds = ExecutionBounds(
    max_iterations=10000,
    max_recursion_depth=100,
    max_operations=1000000,
    timeout_seconds=30.0
)

engine = LogicEngine(bounds)
result = engine.evaluate({
    "op": "+",
    "args": [2, {"op": "*", "args": [3, 4]}]
})
# result = 14, with proof of termination
```

### Ada Sentinel (`adan/ada.py`)

Watchdog for statistical anomalies. Uses MAD (Median Absolute Deviation) instead of mean for robustness against adversarial inputs.

```python
from adan.ada import Ada, Baseline

ada = Ada()
baseline = Baseline(values=[100, 102, 98, 101, 99])
alert = ada.check(current=150, baseline=baseline)
# alert.triggered = True, alert.deviation = 4.5σ
```

### Kinematic Linguistics (`adan/kinematic_linguistics.py`)

Analyzes text through the physics of letterforms. Each character has:
- **Weight** — Visual mass
- **Curvature** — Bend of strokes
- **Commit Strength** — Finality of form

```python
from adan.kinematic_linguistics import SIGNATURES

sig = SIGNATURES['a']
# sig.weight = 0.6
# sig.curvature = 0.8
# sig.is_anchor = True
```

**Character Types:**
- **Anchors** — High weight, stable (a, d, g, o, q)
- **Terminals** — End strokes (e, s, t)
- **Handles** — Low weight, connective (i, l, r)

### Semantic Resolver (`adan/semantic_resolver.py`)

Uses Datamuse API for semantic similarity without LLM costs.

```python
from adan.semantic_resolver import SemanticResolver

resolver = SemanticResolver()
similar = resolver.means_like("happy", max_results=5)
# ["joyful", "content", "pleased", "delighted", "cheerful"]
```

### Adanpedia (`adan/knowledge_store.py`)

Local knowledge base with fuzzy search.

```python
from adan.knowledge_store import KnowledgeStore

store = KnowledgeStore()
store.add("Texas", "Texas is a state in the United States.", source="geography")
facts = store.search("Texas France", limit=5)
```

### Ollama Integration

AI fact-checking via local LLM (qwen2.5:3b).

```
┌─────────────────────────────────────────────────────────────┐
│                    FACT-CHECK PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Claim: "Texas is in France"                                │
│                    │                                        │
│                    ▼                                        │
│  ┌─────────────────────────────────┐                        │
│  │  PHASE 1: Local Knowledge       │  ~30ms                 │
│  │  • Adanpedia lookup             │                        │
│  │  • Hardcoded geo facts          │                        │
│  │  • Pattern matching             │                        │
│  └─────────────────────────────────┘                        │
│                    │                                        │
│         Found? ────┼──── Yes ──→ Return immediately         │
│                    │                                        │
│                    ▼ No                                     │
│  ┌─────────────────────────────────┐                        │
│  │  PHASE 2: Ollama AI             │  ~10-30 seconds        │
│  │  • qwen2.5:3b inference         │                        │
│  │  • JSON response parsing        │                        │
│  └─────────────────────────────────┘                        │
│                    │                                        │
│                    ▼                                        │
│  Result: { verdict: "FALSE", reasoning: "..." }             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Styling System

### Design Tokens (`desktop.css`)

The UI follows **Apple Human Interface Guidelines** with a verified computing aesthetic.

```css
:root {
    /* Colors — Vibrancy System */
    --bg-desktop: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --bg-window: rgba(255, 255, 255, 0.88);
    --bg-vibrancy: rgba(255, 255, 255, 0.75);
    --bg-dock: transparent;
    
    /* Squircle Radii — Apple Style */
    --radius-xs: 6px;
    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 18px;
    --radius-xl: 22px;
    --radius-window: 12px;
    --radius-icon: 12px;
    --radius-dock: 28px;
    
    /* Typography — SF Pro Feel */
    --font-system: -apple-system, BlinkMacSystemFont, 'SF Pro', 'Segoe UI', system-ui;
    
    /* Motion — Bézier Curves */
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --duration-normal: 200ms;
}
```

### Visual Hierarchy

```
╔═══════════════════════════════════════════════════════════════╗
║                      DEPTH LAYERS                              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  z-index: 1000  │  Command Palette (modal)                    ║
║  z-index: 500   │  Dock                                       ║
║  z-index: 100+  │  Windows (stacking order)                   ║
║  z-index: 50    │  Inspector panel                            ║
║  z-index: 10    │  Sidebar                                    ║
║  z-index: 1     │  Desktop background                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Dock Behavior

```css
#dock {
    position: fixed;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    pointer-events: none;  /* Click-through to windows behind */
}

.dock-container {
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    pointer-events: none;
}

.dock-item {
    pointer-events: auto;  /* Re-enable for icons only */
}

.dock-item:hover {
    transform: translateY(-8px) scale(1.15);
}
```

---

## Applications

### Built-in Apps

| Icon | App | Description |
|------|-----|-------------|
| 📁 | **Workspace** | Object browser toggle |
| 🗂️ | **Cards** | Create/view cards |
| 🔍 | **Search** | Semantic + Local + Kinematic search |
| 🗺️ | **Maps** | Geographic objects |
| 🔢 | **Calculator** | TI-84 style verified math |
| ✓ | **Verifier** | Content hash verification |
| 🐕 | **Sentinel** | Ada watchdog status |
| 📚 | **Grounding** | AI fact-checker |
| 🔬 | **Inspector** | Object detail view |
| ⚙️ | **Services** | System services panel |

### Search App Modes

```
┌─────────────────────────────────────────────────────────┐
│  [🧠 Semantic]  [📁 Local]  [📐 Kinematic]               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Semantic:  Uses Datamuse API + Adanpedia               │
│             Finds related concepts, synonyms            │
│                                                         │
│  Local:     Searches workspace objects                  │
│             Cards, queries, files                       │
│                                                         │
│  Kinematic: Analyzes text letterform physics            │
│             Shows anchors, terminals, handles           │
│             Visualizes character weights                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Calculator Operations

```
Basic:     + - * / 
Powers:    ^ sqrt
Trig:      sin cos tan
Logs:      log ln
Special:   ! (factorial)
           % (modulo)
           
All calculations bounded by ExecutionBounds.
All results include verification proof.
```

---

## File Structure

```
foghorn/
├── __init__.py              # Object type definitions
├── objects.py               # ObjectStore implementation
├── LIGHTHOUSE_README.md     # This document
│
└── shell/
    ├── server.py            # HTTP server + API handlers
    ├── index.html           # Desktop HTML structure
    ├── desktop.js           # UI controller + app logic
    └── desktop.css          # Apple HIG styling (2500+ lines)

nina/
└── developer/
    └── forge/
        ├── __init__.py      # Pipeline, Regime exports
        └── knowledge.py     # Knowledge base

adan/
├── ada.py                   # Sentinel watchdog
├── kinematic_linguistics.py # Letterform physics
├── semantic_resolver.py     # Datamuse integration
└── knowledge_store.py       # Adanpedia

core/
├── logic.py                 # Newton Logic Engine
├── cdl.py                   # Constraint Definition Language
├── forge.py                 # Verification engine
├── vault.py                 # Encrypted storage
├── ledger.py                # Immutable audit trail
└── bridge.py                # Distributed consensus
```

---

## Running the System

### Prerequisites

```bash
# Python 3.9+
pip install fastapi uvicorn requests hypothesis

# Ollama (for AI fact-checking)
# Download from https://ollama.ai
ollama pull qwen2.5:3b
```

### Start the Server

```bash
cd Newton-api

# Start Ollama (separate terminal)
ollama serve

# Start Nina Desktop
python foghorn/shell/server.py
```

### Access

```
Browser:  http://localhost:8000/index.html
API:      http://localhost:8000/foghorn/*
```

### Test API

```bash
# Fact-check (local knowledge)
curl -X POST http://localhost:8000/foghorn/ground \
  -H "Content-Type: application/json" \
  -d '{"claim": "Texas is in France"}'
# → { "verdict": "FALSE", "ai_powered": false, "elapsed_us": 30000 }

# Fact-check (requires AI)
curl -X POST http://localhost:8000/foghorn/ground \
  -H "Content-Type: application/json" \
  -d '{"claim": "The moon is made of cheese"}'
# → { "verdict": "FALSE", "ai_powered": true, "elapsed_us": 12000000 }

# Verified calculation
curl -X POST http://localhost:8000/foghorn/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": "sqrt(144) + sin(0)"}'
# → { "result": 12.0, "verified": true }
```

---

## Roadmap

### Phase 1: Foundation ✓
- [x] Object system (Cards, Queries, etc.)
- [x] Apple HIG styling
- [x] Window management
- [x] Dock with apps
- [x] Newton Logic Engine integration

### Phase 2: Intelligence ✓
- [x] Kinematic Linguistics
- [x] Semantic Resolver + Adanpedia
- [x] Ollama AI integration
- [x] Two-phase fact-checking (local → AI)

### Phase 3: Verification (In Progress)
- [ ] CDL constraint editor
- [ ] Ledger integration for audit trail
- [ ] Vault for encrypted storage
- [ ] Merkle proofs in UI

### Phase 4: Distribution
- [ ] Bridge consensus protocol
- [ ] Multi-user sync
- [ ] Conflict resolution
- [ ] Federated knowledge graphs

### Phase 5: Platform
- [ ] Plugin architecture
- [ ] Custom app development
- [ ] API documentation portal
- [ ] Desktop app (Electron/Tauri)

---

## Credits

**Project Foghorn** is part of the **Newton Supercomputer** ecosystem.

```
Newton Supercomputer
├── Newton Core (verification engine)
├── Ada Sentinel (anomaly detection)
├── Kinematic Linguistics (text physics)
└── Nina Desktop (verified UI) ← You are here
```

---

## License

See main repository LICENSE for terms.

---

```
═══════════════════════════════════════════════════════════════════════════════
   "1 == 1. The cloud is weather. We're building shelter."
═══════════════════════════════════════════════════════════════════════════════
```
