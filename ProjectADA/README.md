# ProjectADA

**System of Systems Agent** — Four Newton subsystems wired into one locally-served app.

ProjectADA combines Ada Sentinel, Meta Newton, Kinematic Linguistics, and the Trajectory Composer into a single chat interface with real-time verification feedback.

## What's Inside

| Subsystem | What it does |
|---|---|
| **Ada Sentinel** | Drift detection and anomaly sensing. Scans every input and output for off-rails behavior. |
| **Meta Newton** | Self-verifying verifier. Recursively checks that the verification pipeline itself stays within bounds. |
| **Kinematic Linguistics** | Language as Bezier curves. Every character has weight, curvature, and commit strength — no one else has this. |
| **Trajectory Composer** | Real-time writing feedback. Envelope depth, semantic coherence, and termination awareness while you type. |

Every message passes through a **5-step pipeline**:

1. Ada Sentinel pre-scan (drift check on input)
2. Trajectory verification (grammar + meaning envelope)
3. Newton Agent processing (10-step verified response)
4. Meta Newton self-verification (verifier-of-the-verifier)
5. Ada Sentinel post-watch (drift check on output)

## Quick Start

```bash
cd ProjectADA
pip install -r requirements.txt
python server.py
```

Open [http://localhost:5050](http://localhost:5050) in your browser.

## Development

### Project Structure

```
ProjectADA/
├── server.py              # Flask backend — all API routes and adan wiring
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Single-page app shell
├── static/
│   ├── styles.css         # Warm-palette UI (matches mockup)
│   └── app.js             # Frontend logic — chat, trajectory, panels
└── README.md
```

### Environment

- **Port**: defaults to `5050`, override with `PORT` env var
- **Secret key**: defaults to `projectada-dev`, override with `SECRET_KEY`
- **Debug mode**: enabled by default when running `python server.py`

### API Endpoints

#### Chat

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/chats` | List all chats (sorted by last updated) |
| `POST` | `/api/chats` | Create a new chat |
| `GET` | `/api/chats/<id>` | Get chat with full message history |
| `DELETE` | `/api/chats/<id>` | Delete a chat |
| `POST` | `/api/chats/<id>/message` | Send a message (runs full 5-step pipeline) |

#### Trajectory (real-time feedback)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/trajectory/compose` | Get weight/curvature/commit for text being typed |
| `POST` | `/api/trajectory/keystroke` | Per-keystroke kinematic analysis |

#### Kinematic Linguistics

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/kinematic/analyze` | Full sentence kinematic analysis |
| `GET` | `/api/kinematic/alphabet` | All 90+ character signatures |

#### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Component status for all 6 subsystems |
| `GET` | `/api/knowledge` | Knowledge base stats (facts count, categories) |

### Frontend

The UI is a three-panel layout:

- **Sidebar** (260px) — navigation between Chats, Knowledge, and Settings
- **Chat List** (360px) — searchable list of conversations with previews
- **Conversation** (flex) — messages with verification badges, trajectory bar while typing

The trajectory bar shows real-time metrics as you type (debounced at 200ms):
- **Weight** — how "heavy" your text is kinematically
- **Curvature** — Bezier curve complexity of your language
- **Commit** — how close the text is to a termination point
- **Depth** — envelope nesting depth

### Chat Storage

Chats are stored in-memory (dict). They reset when the server restarts. This is intentional for a local dev tool — no database needed.

## Dependencies

- **Flask** — web framework
- **adan** — the Newton agent subsystems (imported from parent directory automatically)

The `adan` package is loaded lazily at first use, so the server starts fast even if some subsystems have heavy dependencies.
