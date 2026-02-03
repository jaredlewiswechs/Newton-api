# StationReadMe
## parcStation Architecture & Deployment Guide

> **The constraint IS the instruction. The verification IS the computation.**

parcStation is a modern reimagining of Apple's killed HyperCard/OpenDoc vision, built on Newton Supercomputer's verified computation substrate.

---

## What Is This?

parcStation is a **verified information environment** where:
- Every claim has a trust level (verified, partial, draft, unverified, disputed)
- Every piece of content is organized in **Stacks** (like HyperCard)
- Every operation is logged to an immutable **Ledger**
- An AI agent (Newton Agent) provides grounded, verifiable responses
- **Cartridges** provide pluggable knowledge modules (Wikipedia, arXiv, etc.)

Think of it as: **Notes app + HyperCard + Wolfram Alpha + immutable audit trail**

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              parcStation UI                                 │
│                      http://localhost:8082/index2.html                      │
│                                                                             │
│  ┌──────────────┐  ┌──────────────────────────┐  ┌────────────────────┐    │
│  │   Sidebar    │  │      Main Content        │  │    Chat Panel      │    │
│  │   Stacks     │  │  Stack Grid / Card View  │  │  Newton Agent      │    │
│  │   Status     │  │  Trust Badges, Sources   │  │  Grounded Chat     │    │
│  └──────────────┘  └──────────────────────────┘  └────────────────────┘    │
│                                                                             │
│                    ┌─────────────────────────────┐                          │
│                    │   Spotlight Search (⌘K)     │                          │
│                    │   Wikipedia, arXiv, Calc    │                          │
│                    └─────────────────────────────┘                          │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                    ╔═══════════════╪═══════════════╗
                    ║           HTTP/REST           ║
                    ╚═══════════════╪═══════════════╝
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      │                             │                             │
      ▼                             ▼                             ▼
┌───────────────┐         ┌─────────────────┐         ┌───────────────────┐
│    Newton     │         │  Newton Agent   │         │   Cartridges      │
│ Supercomputer │         │   (port 8091)   │         │   (port 8093)     │
│  (port 8000)  │         │                 │         │                   │
│               │         │  /chat          │         │  /wikipedia/*     │
│  /verify      │◄───────►│  /ground        │         │  /arxiv/*         │
│  /ground      │         │  /history       │         │  /calendar/*      │
│  /calculate   │         │  /stats         │         │  /code/*          │
│  /ledger      │         │  /models        │         │  /dictionary/*    │
│  /ask         │         │                 │         │  /export/*        │
└───────┬───────┘         └────────┬────────┘         └───────────────────┘
        │                          │                            │
        │                          ▼                            │
        │                 ┌─────────────────┐                   │
        │                 │     Ollama      │                   │
        │                 │  (port 11434)   │                   │
        │                 │   qwen2.5:3b    │                   │
        │                 └─────────────────┘                   │
        │                                                       │
        ▼                                                       ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                           External APIs (Free)                            │
│  Wikipedia API (no key) │ arXiv API (no key) │ Dictionary API (no key)   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Port Assignments

| Service | Port | Purpose | Required |
|---------|------|---------|----------|
| **Newton Supercomputer** | 8000 | Verified computation, grounding, ledger | ✅ Yes |
| **Newton Agent** | 8091 | AI chat with grounding | ✅ Yes |
| **Cartridges** | 8093 | Knowledge modules (Wikipedia, arXiv, etc.) | Optional |
| **UI Server** | 8082 | Static file serving | ✅ Yes |
| **Ollama** | 11434 | Local LLM inference | ✅ Yes (for Agent) |

---

## Quick Start (Local Development)

### Prerequisites
```bash
# Python 3.9+
python --version

# Ollama with qwen2.5
ollama pull qwen2.5:3b
ollama serve  # Keep running in background
```

### Start All Services (4 Terminals)

**Terminal 1: Newton Supercomputer**
```powershell
cd c:\Users\jnlew\Newton-api
python newton_supercomputer.py
# Runs on http://localhost:8000
```

**Terminal 2: Newton Agent**
```powershell
cd c:\Users\jnlew\Newton-api
python -m newton_agent.agent
# Runs on http://localhost:8091
```

**Terminal 3: Cartridges (Optional)**
```powershell
cd c:\Users\jnlew\Newton-api\parcstation
python cartridges.py
# Runs on http://localhost:8093
```

**Terminal 4: UI Server**
```powershell
cd c:\Users\jnlew\Newton-api\parcstation
python -m http.server 8082
# Serves UI at http://localhost:8082/index2.html
```

### One-Line Startup (Windows PowerShell)
```powershell
# Start all services in separate windows
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\jnlew\Newton-api; python newton_supercomputer.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\jnlew\Newton-api; python -m newton_agent.agent"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\jnlew\Newton-api\parcstation; python cartridges.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\Users\jnlew\Newton-api\parcstation; python -m http.server 8082"
```

### Verify Everything Works
```powershell
cd c:\Users\jnlew\Newton-api\parcstation
python test.py
# Should show: All 4 test suites passed
```

---

## Test Suite (TessTa)

The test suite validates all contracts before opening the UI:

```powershell
python test.py          # Run all tests
python test.py smoke    # Quick smoke test only
python test.py acid     # ACID compliance only
```

### Test Results Breakdown

| Suite | Tests | Purpose |
|-------|-------|---------|
| **Smoke** | 8 | Service health, basic API responses |
| **Contract** | 45 | HTML/CSS/JS structure, API contracts |
| **ACID** | 11 | Atomicity, Consistency, Isolation, Durability |
| **Cartridge** | 36 | Wikipedia, arXiv, Calendar, Export, Code, Dictionary |

**Pass criteria:** All 4 suites must pass before UI is safe to use.

---

## Configuration

### Frontend Config (`app2.js`)
```javascript
const CONFIG = {
    NEWTON_URL: 'http://localhost:8000',    // Newton Supercomputer
    AGENT_URL: 'http://localhost:8091',     // Newton Agent
    CARTRIDGE_URL: 'http://localhost:8093', // Cartridges
    STORAGE_KEY: 'parcstation_data'         // localStorage key
};
```

### Environment Variables (Agent)
```bash
export OLLAMA_MODEL=qwen2.5:3b           # LLM model
export OLLAMA_URL=http://localhost:11434 # Ollama endpoint
```

---

## API Reference

### Newton Supercomputer (port 8000)

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/verify` | POST | `{ input: string }` | `{ verified: bool }` |
| `/ground` | POST | `{ claim: string }` | `{ status, sources, confidence }` |
| `/calculate` | POST | `{ expression: {...} }` | `{ result: any, verified: bool }` |
| `/ledger` | GET | - | `{ entries: [], total_entries }` |
| `/ask` | POST | `{ question: string }` | Full pipeline result |
| `/health` | GET | - | `{ status: "healthy" }` |

### Newton Agent (port 8091)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | `{ message, ground_claims }` → AI response |
| `/chat/stream` | POST | Streaming response |
| `/history` | GET | Conversation history |
| `/stats` | GET | Agent statistics |
| `/models` | GET | Available Ollama models |
| `/health` | GET | Service health |

### Cartridges (port 8093)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/cartridge/wikipedia/summary` | POST | `{ query }` → Article summary |
| `/cartridge/wikipedia/search` | POST | `{ query }` → Search results |
| `/cartridge/arxiv/search` | POST | `{ query, max_results }` → Papers |
| `/cartridge/calendar/now` | GET | Current datetime |
| `/cartridge/calendar/parse` | POST | `{ text }` → Parsed date |
| `/cartridge/code/evaluate` | POST | `{ code }` → Verified result |
| `/cartridge/dictionary/define` | POST | `{ word }` → Definitions |
| `/cartridge/export/json` | POST | `{ stacks }` → JSON export |
| `/cartridge/export/markdown` | POST | `{ stacks }` → Markdown export |
| `/health` | GET | Service health |
| `/cartridges` | GET | List all cartridges |

---

## Spotlight Search (⌘K)

Press `Cmd+K` (Mac) or `Ctrl+K` (Windows) to open Spotlight:

| Prefix | Action | Example |
|--------|--------|---------|
| (none) | Search local stacks/cards | `research notes` |
| `wiki ` | Search Wikipedia | `wiki python language` |
| `arxiv ` | Search arXiv papers | `arxiv neural networks` |
| `= ` | Calculator | `= 2 + 3 * 4` |

**Keyboard navigation:**
- `↑↓` Navigate results
- `Enter` Select
- `Esc` Close

---

## Server Deployment

### Docker Compose (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  newton:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROUNDING_ENABLED=true
    
  agent:
    build: ./newton_agent
    ports:
      - "8091:8091"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - NEWTON_URL=http://newton:8000
    depends_on:
      - newton
      - ollama
    
  cartridges:
    build: ./parcstation
    command: python cartridges.py
    ports:
      - "8093:8093"
    
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    
  ui:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./parcstation:/usr/share/nginx/html:ro
    depends_on:
      - newton
      - agent
      - cartridges

volumes:
  ollama_data:
```

### Cloud Deployment (Render.com)

**Newton Supercomputer** (`render.yaml`):
```yaml
services:
  - type: web
    name: newton-supercomputer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn newton_supercomputer:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

**Update CONFIG for production:**
```javascript
const CONFIG = {
    NEWTON_URL: 'https://newton-supercomputer.onrender.com',
    AGENT_URL: 'https://newton-agent.onrender.com',
    CARTRIDGE_URL: 'https://parcstation-cartridges.onrender.com',
};
```

### Vercel (Frontend Only)

Deploy `parcstation/` directory as static site:
```bash
cd parcstation
vercel --prod
```

Update `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index2.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" }
      ]
    }
  ]
}
```

---

## File Structure

```
parcstation/
├── index2.html          # Main UI
├── style.css            # Design system
├── app2.js              # Application logic
├── cartridges.py        # Cartridge server
├── test.py              # Test runner
├── smoke.py             # Smoke tests
├── contract_test.py     # Contract tests
├── test_acid.py         # ACID compliance tests
├── test_cartridges.py   # Cartridge tests
├── StationReadMe.md     # This file
└── TessTa.md            # Test documentation
```

---

## Dependencies

### Python Requirements
```
# requirements.txt (parcstation)
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
aiohttp>=3.9.0
requests>=2.31.0
```

### System Requirements
- Python 3.9+
- Ollama (for Agent)
- 4GB RAM minimum (8GB recommended for LLM)

---

## Troubleshooting

### Service won't start
```powershell
# Check if port is in use
netstat -ano | findstr :8000

# Kill process on port
Stop-Process -Id <PID> -Force
```

### Wikipedia/arXiv not working
- Requires proper User-Agent header (handled in cartridges.py)
- Check internet connectivity
- Verify SSL certificates

### Ollama not responding
```powershell
# Check Ollama status
ollama list

# Pull model if missing
ollama pull qwen2.5:3b

# Restart Ollama
ollama serve
```

### Tests failing
```powershell
# Run individual test for details
python smoke.py
python contract_test.py
python test_acid.py
python test_cartridges.py
```

---

## Security Considerations

1. **Content Verification** - All content passes through Newton's safety checks
2. **Grounding** - Claims verified against external sources
3. **Immutable Audit** - Every operation logged to ledger
4. **Local LLM** - No data sent to cloud (Ollama runs locally)
5. **Bounded Execution** - All computations have hard limits
6. **CORS** - Enabled for local development, restrict in production

---

## License

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications

---

## Credits

- **Newton Supercomputer**: Verified computation engine
- **Newton Agent**: Self-verifying AI assistant  
- **Ollama**: Local LLM inference
- **Inspired by**: Apple HyperCard, OpenDoc, Apple Newton, Cyberdog

---

© 2026 Ada Computing Company · Houston, Texas

> "1 == 1. The cloud is weather. We're building shelter."

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
