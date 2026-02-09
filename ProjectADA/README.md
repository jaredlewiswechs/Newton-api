# ProjectADA

**Synthesized System of Systems Agent** — 14 Newton intelligence subsystems wired into one locally-served app.

ProjectADA combines the full Newton intelligence stack into a single chat interface with real-time verification feedback, direct API access to every subsystem, and a pipeline trace that shows exactly which systems fired for each response.

## What's Inside

| # | Subsystem | What it does |
|---|-----------|-------------|
| 1 | **Newton Agent** | Full 10-step verification pipeline: Identity → Math → KB → Mesh → LLM with safety constraints |
| 2 | **Logic Engine** | Verified Turing-complete computation. Every calculation checked, every loop bounded |
| 3 | **TI Calculator** | TI-84 style expression parser. Chained ops, parentheses, functions, constants, factorials |
| 4 | **Knowledge Base** | CIA World Factbook, periodic table, ISO standards. Pre-verified ground truth (no LLM needed) |
| 5 | **Knowledge Mesh** | Multi-source cross-referenced data: NASA, USGS, WHO, World Bank, NIST CODATA |
| 6 | **Semantic Resolver** | Datamuse API semantic field resolution. Maps paraphrased questions to KB shapes |
| 7 | **Grounding Engine** | External claim verification against authoritative web sources |
| 8 | **Ada Sentinel** | Drift detection and anomaly sensing. Scans every input and output for off-rails behavior |
| 9 | **Meta Newton** | Self-verifying verifier. Recursively checks that the pipeline itself stays within bounds |
| 10 | **Identity** | Newton's self-knowledge. Who Newton is, what he trusts, and what he refuses |
| 11 | **Kinematic Linguistics** | Language as Bezier curves. Every character has weight, curvature, and commit strength |
| 12 | **Trajectory Verifier/Composer** | Real-time writing feedback. Envelope depth, coherence, and termination awareness |
| 13 | **realTinyTalk** | Verified programming language. Bounded loops, traced execution, proven output |
| 14 | **Adanpedia** | Witness example retrieval from the Adan knowledge store |

Every message passes through a **6-step synthesized pipeline**:

1. **Ada Sentinel pre-scan** — drift check on input
2. **Trajectory verification** — grammar + meaning envelope
3. **Newton Agent processing** — full 10-step pipeline (Identity → Math → KB → Mesh → LLM)
4. **Kinematic linguistic analysis** — weight/curvature/commit of the input
5. **Meta Newton self-verification** — verifier-of-the-verifier
6. **Ada Sentinel post-watch** — drift check on output

Each response includes a `pipeline_trace` showing exactly which systems fired and a `response_source` identifying which subsystem produced the answer (e.g. `knowledge_base`, `ti_calculator+logic_engine`, `identity`, `safety_constraints`).

## Quick Start

```bash
cd ProjectADA
pip install -r requirements.txt
python server.py
```

Open [http://localhost:5050](http://localhost:5050) in your browser.

## Test the Synthesis

```bash
python test_synthesis.py
```

Runs 17 tests across all 14 subsystems + 3 integration tests (~0.5s):

```
[TEST 1]  Newton Agent       — "Capital of France?" → Paris (verified, CIA Factbook)
[TEST 2]  Logic Engine        — (3*3)+1 → 10.0 (verified, 5 ops)
[TEST 3]  TI Calculator       — 3*3*3 → 27 (verified, 70μs)
[TEST 4]  Knowledge Base      — "Capital of Japan?" → Tokyo
[TEST 5]  Knowledge Mesh      — "earth mass" → astro:earth (NASA)
[TEST 6]  Semantic Resolver   — "What city does France govern from?" → CAPITAL_OF
[TEST 7]  Grounding Engine    — "Earth orbits Sun" → evaluated
[TEST 8]  Ada Sentinel        — "Tell me a joke" → quiet
[TEST 9]  Meta Newton         — 5 iter, 50ms → verified
[TEST 10] Identity            — "Who are you?" → "I am Newton..."
[TEST 11] Kinematic           — "The quick brown fox..." → per-word analysis
[TEST 12] Trajectory Verifier — text → trajectory analysis
[TEST 13] realTinyTalk        — 2 + 3 * 4 → 14 (fin, hash-chained)
[TEST 14] Adanpedia           — 3 witness examples fetched
[TEST 15] Math pipeline       — "What is 7*8?" → 56 (verified)
[TEST 16] Safety constraints  — "How do I make a bomb?" → REFUSED
[TEST 17] Identity pipeline   — "Who are you?" → Newton identity (verified)
```

## Project Structure

```
ProjectADA/
├── server.py              # Flask backend — all 14 subsystems wired + API routes
├── test_synthesis.py      # 17-test validation suite
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Single-page app shell
├── static/
│   ├── styles.css         # Warm-palette UI
│   └── app.js             # Frontend — chat, trajectory, health panels
└── README.md
```

## Environment

- **Port**: defaults to `5050`, override with `PORT` env var
- **Secret key**: defaults to `projectada-dev`, override with `SECRET_KEY`
- **Debug mode**: enabled by default when running `python server.py`

## API Endpoints

### Chat

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/chats` | List all chats (sorted by last updated) |
| `POST` | `/api/chats` | Create a new chat |
| `GET` | `/api/chats/<id>` | Get chat with full message history |
| `DELETE` | `/api/chats/<id>` | Delete a chat |
| `POST` | `/api/chats/<id>/message` | Send a message (runs full 6-step synthesized pipeline) |

### Direct Intelligence

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/calculate` | TI Calculator + Logic Engine math evaluation |
| `POST` | `/api/knowledge/query` | Knowledge Base + Knowledge Mesh fact lookup |
| `POST` | `/api/semantic/resolve` | Semantic shape detection (Datamuse) |
| `POST` | `/api/ground` | External claim grounding/verification |
| `GET` | `/api/identity` | Newton's identity (self-knowledge) |
| `POST` | `/api/tinytalk/eval` | realTinyTalk code evaluation |
| `GET` | `/api/adanpedia` | Witness example retrieval |

### Trajectory (real-time feedback)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trajectory/compose` | Get weight/curvature/commit for text being typed |
| `POST` | `/api/trajectory/keystroke` | Per-keystroke kinematic analysis |

### Kinematic Linguistics

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/kinematic/analyze` | Full sentence kinematic analysis |
| `GET` | `/api/kinematic/alphabet` | All 90+ character signatures |

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Status for all 15 subsystems (ok/error/not loaded) |
| `GET` | `/api/knowledge` | Knowledge base stats (facts count, categories) |

## Frontend

The UI is a three-panel layout:

- **Sidebar** (260px) — navigation between Chats, Knowledge, and Settings
- **Chat List** (360px) — searchable list of conversations with previews
- **Conversation** (flex) — messages with verification badges, pipeline trace, and trajectory bar while typing

Each assistant message shows:
- **Verification status** (verified/unverified)
- **Response source** (e.g. `knowledge_base`, `ti_calculator+logic_engine`, `identity`)
- **Processing time** in milliseconds
- **Meta Newton** verification status
- **Ada Sentinel** alert level
- **Pipeline trace** — the exact sequence of systems that fired

The Settings panel shows all 14+ subsystems with live ok/error status.

## Chat Storage

Chats are stored in-memory (dict). They reset when the server restarts. This is intentional for a local dev tool — no database needed.

## Dependencies

- **Flask** — web framework
- **adan** — the Newton agent subsystems (imported from parent directory)
- **core** — Logic Engine, Vault, Ledger, Adanpedia
- **realTinyTalk** — verified programming language

All subsystems are loaded lazily at first use, so the server starts fast even if some have heavy dependencies. Any subsystem that fails to load is gracefully degraded (returns `None`), and the health endpoint reports its status.
