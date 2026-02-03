# StationReadMe
## parcStation Architecture

> **The constraint IS the instruction. The verification IS the computation.**

parcStation is a modern reimagining of Apple's killed HyperCard/OpenDoc vision, built on Newton Supercomputer's verified computation substrate.

---

## What Is This?

parcStation is a **verified information environment** where:
- Every claim has a trust level (verified, partial, draft, unverified, disputed)
- Every piece of content is organized in **Stacks** (like HyperCard)
- Every operation is logged to an immutable **Ledger**
- An AI agent (Newton Agent) provides grounded, verifiable responses

Think of it as: **Notes app + HyperCard + Wolfram Alpha + immutable audit trail**

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              parcStation UI                                 │
│                         (index2.html + app2.js)                             │
│                                                                             │
│  ┌──────────────┐  ┌──────────────────────────┐  ┌────────────────────┐    │
│  │   Sidebar    │  │      Main Content        │  │    Chat Panel      │    │
│  │              │  │                          │  │                    │    │
│  │  • Stacks    │  │  Stack Grid / Card View  │  │  Newton Agent      │    │
│  │  • Cartridges│  │                          │  │  Conversations     │    │
│  │  • Status    │  │  Trust Badges, Sources   │  │                    │    │
│  └──────────────┘  └──────────────────────────┘  └────────────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST
                                    │
         ┌──────────────────────────┴───────────────────────────┐
         │                                                      │
         ▼                                                      ▼
┌─────────────────────────┐                      ┌─────────────────────────┐
│   Newton Supercomputer  │                      │     Newton Agent        │
│      (port 8000)        │                      │      (port 8091)        │
│                         │                      │                         │
│  /verify   - Content    │                      │  /chat    - AI chat     │
│  /ground   - Claims     │◄────────────────────►│  /ground  - Verify      │
│  /calculate- Math       │                      │  /history - Memory      │
│  /ledger   - Audit      │                      │  /stats   - Metrics     │
│  /ask      - Pipeline   │                      │  /models  - LLM list    │
└─────────────────────────┘                      └─────────────────────────┘
         │                                                      │
         │                                                      │
         ▼                                                      ▼
┌─────────────────────────┐                      ┌─────────────────────────┐
│    Core Components      │                      │    Ollama (qwen2.5)     │
│                         │                      │      (port 11434)       │
│  CDL   - Constraints    │                      │                         │
│  Logic - Computation    │                      │  Local LLM inference    │
│  Forge - Verification   │                      │  No cloud dependency    │
│  Vault - Encryption     │                      │                         │
│  Ledger- Immutability   │                      │                         │
└─────────────────────────┘                      └─────────────────────────┘
```

---

## Dependencies

### Frontend (UI)

| File | Purpose |
|------|---------|
| `index2.html` | Main HTML structure - sidebar, content area, chat panel |
| `style.css` | Design system - CSS variables, glassmorphism, animations |
| `app2.js` | Application logic - API clients, state management, rendering |

**External:**
- Google Fonts (Inter) - Typography
- No frameworks (vanilla JS)

### Backend Services

| Service | Port | Purpose |
|---------|------|---------|
| Newton Supercomputer | 8000 | Verified computation, grounding, ledger |
| Newton Agent | 8091 | AI chat with grounding, conversation memory |
| Ollama | 11434 | Local LLM (qwen2.5:3b) |
| UI Server | 8082 | Static file serving |

### Python Dependencies

**Newton Supercomputer:**
```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
googlesearch-python>=1.2.5
```

**Newton Agent:**
```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
aiohttp>=3.9.0
ollama (via HTTP)
```

**Test Suite:**
```
requests>=2.31.0
aiohttp>=3.9.0
pytest>=7.4.4 (optional)
```

---

## Component Details

### 1. UI Layer (`index2.html`, `style.css`, `app2.js`)

#### HTML Structure
```html
<div class="app">
    <aside class="sidebar">        <!-- Navigation -->
    <main class="main">            <!-- Content -->
    <div class="chat-panel">       <!-- Newton Agent chat -->
    <button class="chat-fab">      <!-- Chat toggle button -->
    <div class="sheet-overlay">    <!-- Modal backdrop -->
    <div class="sheet">            <!-- Modal content -->
</div>
```

#### CSS Design System
```css
/* Colors */
--bg-primary: #0F0F10;       /* Dark background */
--bg-secondary: #1A1A1B;     /* Card background */
--glass-bg: rgba(255,255,255,0.03);  /* Glassmorphism */
--accent: #6366F1;           /* Primary accent */

/* Trust Colors */
--verified: #10B981;         /* Green - fully verified */
--partial: #F59E0B;          /* Amber - partially verified */
--draft: #6B7280;            /* Gray - draft/pending */
--unverified: #EF4444;       /* Red - failed verification */
--disputed: #EC4899;         /* Pink - conflicting sources */
```

#### JavaScript Classes
```javascript
class NewtonClient        // HTTP client for Newton Supercomputer
class NewtonAgentClient   // HTTP client for Newton Agent
class DataStore           // localStorage persistence layer
class ParcStationApp      // Main application controller
```

### 2. Newton Supercomputer (port 8000)

**Core Endpoints:**

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/verify` | POST | `{ input: string }` | `{ verified: bool }` |
| `/ground` | POST | `{ claim: string }` | `{ status, sources, confidence }` |
| `/calculate` | POST | `{ expression: object }` | `{ result: any }` |
| `/ledger` | GET | - | `{ entries: [], total_entries }` |
| `/ask` | POST | `{ question: string }` | Full pipeline result |
| `/health` | GET | - | `{ status: "healthy" }` |
| `/metrics` | GET | - | Performance statistics |

**Core Modules:**

| Module | Purpose |
|--------|---------|
| `core/cdl.py` | Constraint Definition Language - declarative constraints |
| `core/logic.py` | Verified computation engine - Turing complete with bounds |
| `core/forge.py` | Parallel constraint evaluation (<1ms) |
| `core/vault.py` | AES-256-GCM encrypted storage |
| `core/ledger.py` | Hash-chained immutable audit trail |
| `core/grounding.py` | Web search for claim verification |
| `core/robust.py` | Adversarial statistics (MAD over mean) |

### 3. Newton Agent (port 8091)

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send message, get AI response |
| `/chat/stream` | POST | Streaming response |
| `/ground` | POST | Verify a specific claim |
| `/history` | GET | Conversation history |
| `/stats` | GET | Agent statistics |
| `/models` | GET | Available Ollama models |
| `/model` | POST | Switch LLM model |
| `/health` | GET | Service health |

**Key Features:**
- Every response is grounded against sources
- Conversation stored as hash-chain (immutable)
- Calls Newton Supercomputer for verification
- Uses local Ollama for LLM inference

### 4. Data Model

#### Stack
```javascript
{
    id: "stack_abc123",
    title: "Research Notes",
    cards: [...],
    created: 1706900000000,
    modified: 1706900000000
}
```

#### Card
```javascript
{
    id: "card_xyz789",
    content: "Python was created by Guido van Rossum",
    trust: "verified",  // verified | partial | draft | unverified | disputed
    sources: [
        { url: "https://...", title: "Wikipedia", tier: "official" }
    ],
    created: 1706900000000,
    modified: 1706900000000
}
```

#### Trust Levels
| Level | Meaning | Color |
|-------|---------|-------|
| `verified` | All claims verified with official sources | Green |
| `partial` | Some claims verified | Amber |
| `draft` | Not yet verified | Gray |
| `unverified` | Verification failed | Red |
| `disputed` | Conflicting sources found | Pink |

---

## Data Flow

### Creating a Card

```
User types content
        │
        ▼
┌───────────────────┐
│   app2.js         │
│   handleAddCard() │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐         ┌─────────────────────┐
│  Newton /verify   │────────►│  Content safety     │
│                   │         │  check              │
└─────────┬─────────┘         └─────────────────────┘
          │
          ▼
┌───────────────────┐         ┌─────────────────────┐
│  Newton /ground   │────────►│  Web search for     │
│                   │         │  sources            │
└─────────┬─────────┘         └─────────────────────┘
          │
          ▼
┌───────────────────┐
│  DataStore.save() │────────► localStorage
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Newton /ledger   │────────► Immutable audit trail
└───────────────────┘
```

### Chat with Agent

```
User sends message
        │
        ▼
┌───────────────────┐
│  Agent /chat      │
│  { message,       │
│    ground_claims} │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐         ┌─────────────────────┐
│  Ollama (qwen)    │────────►│  Generate response  │
│  localhost:11434  │         │                     │
└─────────┬─────────┘         └─────────────────────┘
          │
          ▼
┌───────────────────┐         ┌─────────────────────┐
│  Newton /ground   │────────►│  Verify claims in   │
│                   │         │  response           │
└─────────┬─────────┘         └─────────────────────┘
          │
          ▼
┌───────────────────┐
│  Hash-chain       │────────► Conversation ledger
│  append           │
└───────────────────┘
```

---

## Possible Extensions

### 1. Cartridge System
**Status:** Partially implemented

Like HyperCard's XCMDs - pluggable functionality:
```javascript
const calculatorCartridge = {
    id: 'calculator',
    name: 'Calculator',
    icon: '🔢',
    evaluate: (expression) => newton.calculate(expression)
};
```

Potential cartridges:
- **Wolfram** - Computational knowledge
- **Wikipedia** - Encyclopedia grounding
- **arXiv** - Academic paper search
- **Code** - Run verified code snippets
- **Calendar** - Time-aware constraints

### 2. Collaborative Stacks
**Status:** Not implemented

- Multiple users editing same stack
- Conflict resolution via Newton consensus
- Real-time sync with WebSocket

### 3. Export Formats
**Status:** Not implemented

- Export stack as PDF with verification certificates
- Export as Markdown with source links
- Export as JSON for backup/restore

### 4. Voice Interface
**Status:** Separate project (voicepath/)

- Speech-to-text for card creation
- Text-to-speech for reading cards
- Voice commands for navigation

### 5. Mobile App
**Status:** Separate project (newton-phone/)

- iOS/Android native apps
- Offline-first with sync
- Share stacks via QR code

### 6. Desktop App
**Status:** Possible via Electron/Tauri

- Native window management
- System-level hotkeys
- File system integration

### 7. Self-Hosted Knowledge Base
**Status:** Possible extension

- Import Markdown/Obsidian vaults
- Local embeddings for semantic search
- Private grounding against personal docs

### 8. Smart Contracts
**Status:** Conceptual

Newton's verified computation could power:
- Provably correct contract execution
- Auditable business logic
- Deterministic state machines

---

## Starting Services

### All Services (Recommended)
```bash
# Terminal 1: Newton Supercomputer
python newton_supercomputer.py

# Terminal 2: Newton Agent  
cd newton_agent && python server.py

# Terminal 3: UI Server
python -m http.server 8082 -d parcstation

# Terminal 4: Ollama (if not running)
ollama serve
```

### Quick Test
```bash
cd parcstation
python test.py
# If SAFE → open http://localhost:8082/index2.html
```

---

## Configuration

### API URLs (in app2.js)
```javascript
const CONFIG = {
    NEWTON_URL: 'http://localhost:8000',
    AGENT_URL: 'http://localhost:8091',
    STORAGE_KEY: 'parcstation_data'
};
```

### Agent Model (environment variable)
```bash
export OLLAMA_MODEL=qwen2.5:3b
export OLLAMA_URL=http://localhost:11434
```

---

## Security Considerations

1. **Content Verification** - All content passes through Newton's safety checks
2. **Grounding** - Claims verified against external sources
3. **Immutable Audit** - Every operation logged to ledger
4. **Local LLM** - No data sent to cloud (Ollama runs locally)
5. **Bounded Execution** - All computations have hard limits

---

## License

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

---

## Credits

- **Newton Supercomputer**: Verified computation engine
- **Newton Agent**: Self-verifying AI assistant
- **Ollama**: Local LLM inference
- **Inspired by**: Apple HyperCard, OpenDoc, Apple Newton

---

© 2026 Ada Computing Company · Houston, Texas

> "1 == 1. The cloud is weather. We're building shelter."
