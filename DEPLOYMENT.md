# NEWTON DEPLOYMENT PACKAGE
## Ada Computing Company · January 2026

---

## OVERVIEW

Newton OS v3.0.0 is a deterministic verification engine that governs AI execution. The system ensures no AI vendor (Claude, GPT, Groq, or local models) can execute until intent has been verified.

**Architecture Summary**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEWTON OS v3.0.0                            │
│                                                                     │
│   USER INTENT                                                       │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────┐                                                   │
│   │   NEWTON    │  ← Python FastAPI (Primary)                      │
│   │     API     │     newton_os_server.py                          │
│   └──────┬──────┘                                                   │
│          │                                                          │
│          │  Deterministic Constraint Verification                   │
│          │  harm | medical | legal | security                       │
│          │                                                          │
│          ▼                                                          │
│   ┌─────────────┐                                                   │
│   │  OPTIONAL   │  ← Ruby Adapter (Local use)                      │
│   │   ADAPTER   │     adapter_universal.rb                         │
│   └──────┬──────┘                                                   │
│          │                                                          │
│    ┌─────┴─────┬─────────────┬─────────────┐                       │
│    ▼           ▼             ▼             ▼                        │
│ [Claude]   [Groq]       [OpenAI]      [Ollama]                     │
│  Remote     Remote       Remote        Local                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**The Invariant:** `1 == 1` — Execute only when verification passes.

---

## FILE MANIFEST

| File | Purpose | Deploy Location |
|------|---------|-----------------|
| `newton_os_server.py` | **Primary API (Python)** | Render / Docker / Server |
| `requirements.txt` | Python dependencies | With API |
| `render.yaml` | Render config | Root of repo |
| `Dockerfile` | Docker deployment | Container environments |
| `core/grounding.py` | Claim verification engine | With API |
| `newton-pda/` | Personal Data Assistant (PWA) | Static hosting |
| `ada.html` | Verification interface | Served by API at `/ada` |
| `newton_dashboard.html` | Dashboard visualization | Served by API at `/` |
| `adapter_universal.rb` | Vendor bridge (optional) | Local machine |
| `newton_api.rb` | Legacy Ruby kernel | Alternative deployment |

---

## STEP 1: DEPLOY TO RENDER (RECOMMENDED)

The repository includes a `render.yaml` preconfigured for Python deployment.

### 1.1 Deploy to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will detect the `render.yaml` and configure automatically
5. Click "Create Web Service"
6. Wait for deployment (approximately 2-3 minutes)
7. Copy your URL: `https://newton-kernel-xxxx.onrender.com`

### 1.2 Verify Deployment

```bash
curl https://newton-kernel-xxxx.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "3.0.0",
  "engine": "Newton OS 3.0.0",
  "uptime_seconds": 123.45
}
```

### 1.3 Test Verification

```bash
curl -X POST https://newton-kernel-xxxx.onrender.com/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Help me write a business plan"}'
```

---

## STEP 2: ALTERNATIVE DEPLOYMENTS

### Docker

```bash
docker build -t newton-os .
docker run -p 8000:8000 newton-os
```

### Local Python

```bash
pip install -r requirements.txt
python newton_os_server.py
# Server runs at http://localhost:8000
```

### Uvicorn (Production)

```bash
pip install -r requirements.txt
uvicorn newton_os_server:app --host 0.0.0.0 --port 8000
```

---

## STEP 3: NEWTON PDA (PWA)

Newton PDA is included in the `newton-pda/` folder. It's a standalone Progressive Web App that can be deployed to any static hosting.

### Deploy Options

**Option A: Serve from Newton API**

Configure your web server to serve `/newton-pda/` as a static path.

**Option B: Separate Static Hosting**

Deploy the `newton-pda/` folder to Netlify, Vercel, GitHub Pages, or any static host.

**Option C: Local Development**

```bash
cd newton-pda
python3 -m http.server 8000
# Open http://localhost:8000
```

### Features

- **Encrypted Storage**: AES-256-GCM encryption derived from name/passphrase
- **Offline-First**: IndexedDB persistence, works without network
- **Z-Score Verification**: Items crystallize from DRAFT → PENDING → VERIFIED
- **Append-Only**: Full version history, nothing ever deleted
- **PWA**: Installable on iOS, Android, and desktop

---

## STEP 4: OPTIONAL VENDOR ADAPTER (RUBY)

For local AI vendor integration, use the Ruby adapter.

### 4.1 Set Environment Variables

```bash
export NEWTON_HOST="https://newton-kernel-xxxx.onrender.com"
export NEWTON_OWNER="Jared"

# Choose ONE vendor
export VENDOR="claude"
export NEWTON_KEY="sk-ant-xxxxx"  # Your Anthropic key

# OR for Groq (faster, cheaper)
export VENDOR="groq"
export NEWTON_KEY="gsk_xxxxx"  # Your Groq key

# OR for local (fully sovereign)
export VENDOR="local"
# No key needed, but Ollama must be running
```

### 4.2 Run the Adapter

```bash
bundle install
ruby adapter_universal.rb
```

---

## API REFERENCE (PYTHON)

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verify` | POST | Verify intent against constraints |
| `/analyze` | POST | Anomaly detection (Z-score, IQR, MAD) |
| `/compile` | POST | Natural language to AI prompt |
| `/ground` | POST | Fact-check claims against sources |

### Cartridge Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cartridge/visual` | POST | SVG generation with constraints |
| `/cartridge/sound` | POST | Audio specification |
| `/cartridge/sequence` | POST | Video/animation specification |
| `/cartridge/data` | POST | Report specification |

### Audit Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign` | POST | Cryptographic signatures |
| `/ledger` | GET | Retrieve audit trail |
| `/ledger/verify` | GET | Verify chain integrity |

### Framework Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/frameworks` | GET | List supported frameworks |
| `/frameworks/constraints` | GET | Get framework constraints |
| `/frameworks/verify` | POST | Verify against framework rules |

### Metadata Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status |
| `/constraints` | GET | List constraints |
| `/methods` | GET | List analysis methods |

### Web Interfaces

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Newton Dashboard |
| `/ada` | GET | Ada verification interface |

See [full documentation](docs/) for request/response details.

---

## VENDOR COMPARISON

| Vendor | Speed | Cost | Sovereignty | Best For |
|--------|-------|------|-------------|----------|
| Claude | ~1.5s | $$$  | Remote | Complex reasoning, strict JSON |
| Groq   | ~0.2s | $    | Remote | Speed-critical tasks |
| OpenAI | ~1.0s | $$   | Remote | Standard compatibility |
| Ollama | ~2.0s | Free | Local  | Full sovereignty, offline |

**Recommendation:** Start with Groq for speed during development. Use Claude for production tasks requiring precision. Deploy Ollama for fully sovereign operation.

---

## TROUBLESHOOTING

**"Connection Failed" on adapter startup**
- Verify your NEWTON_HOST URL is correct
- Check that the Render service is running (not sleeping)
- Ensure you're using HTTPS

**"Vendor failed" after verification**
- Check your API key is valid
- Verify the vendor service is accessible
- For local: ensure Ollama is running (`ollama serve`)

**Z-score not decreasing**
- Ensure you're using the exact same intent string each time
- Check that the owner matches across commits

---

## SECURITY NOTES

1. **Newton API**: Deterministic pattern matching for constraint verification (no probabilistic models)
2. **Newton PDA**: AES-256-GCM encryption derived from name/passphrase (PBKDF2 key derivation)
3. **Ledger**: Append-only cryptographic chain with SHA-256 hashing
4. **API Keys**: For production, set `NEWTON_AUTH_ENABLED=true` and configure `NEWTON_API_KEYS`
5. **Rate Limiting**: Built-in rate limiting (100/min default, configurable by tier)

---

## ENVIRONMENT VARIABLES

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `NEWTON_STORAGE` | Storage directory | /tmp/newton |
| `NEWTON_AUTH_ENABLED` | Enable API key auth | false |
| `NEWTON_API_KEYS` | Comma-separated API keys | - |
| `GOOGLE_API_KEY` | For grounding engine | - |
| `GOOGLE_CSE_ID` | For grounding engine | - |

---

## CONTACT

**Jared Lewis**
Ada Computing Company
Houston, Texas

Email: Jn.Lewis1@outlook.com
LinkedIn: linkedin.com/in/jaredlewisuh
Web: parcri.net

---

**1 == 1**

*The math is solid.*
