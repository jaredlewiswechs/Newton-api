# NEWTON DEPLOYMENT PACKAGE
## Ada Computing Company · December 2025

---

## OVERVIEW

Newton is a deterministic state machine that governs AI execution. The system ensures no AI vendor (Claude, GPT, Groq, or local models) can execute until intent has been verified through the Z-score protocol.

**Architecture Summary**

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   USER INTENT                                                       │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────┐                                                   │
│   │   NEWTON    │  ← The Kernel (State Machine API)                │
│   │   KERNEL    │     Hosted on Render                             │
│   └──────┬──────┘                                                   │
│          │                                                          │
│          │  Z-Score Loop: 10.0 → 6.67 → 3.33 → 0.0                 │
│          │                                                          │
│          ▼                                                          │
│   ┌─────────────┐                                                   │
│   │  UNIVERSAL  │  ← The Adapter (Vendor Agnostic)                 │
│   │   ADAPTER   │     Runs locally or on server                    │
│   └──────┬──────┘                                                   │
│          │                                                          │
│    ┌─────┴─────┬─────────────┬─────────────┐                       │
│    ▼           ▼             ▼             ▼                        │
│ [Claude]   [Groq]       [OpenAI]      [Ollama]                     │
│  Remote     Remote       Remote        Local                       │
│                                                                     │
│   All vendors treated as commodity compute.                        │
│   Newton decides WHEN they execute.                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**The Invariant:** `1 == 1` — Intent equals execution only when Z-score reaches zero.

---

## FILE MANIFEST

| File | Purpose | Deploy Location |
|------|---------|-----------------|
| `newton_api.rb` | The Kernel | Render (Web Service) |
| `adapter_universal.rb` | Vendor Bridge | Local machine or server |
| `newton_dashboard.html` | Visualization | Static hosting or local |
| `Gemfile` | Dependencies | With API |
| `render.yaml` | Render config | Root of repo |

---

## STEP 1: DEPLOY THE KERNEL TO RENDER

### 1.1 Create the API File

Save `newton_api.rb` (provided below) to a new GitHub repository.

### 1.2 Create the Gemfile

```ruby
# Gemfile
source 'https://rubygems.org'

ruby '3.2.0'

gem 'sinatra', '~> 3.0'
gem 'sinatra-contrib', '~> 3.0'
gem 'puma', '~> 6.0'
gem 'json'
```

### 1.3 Create the Render Configuration

```yaml
# render.yaml
services:
  - type: web
    name: newton-kernel
    runtime: ruby
    buildCommand: bundle install
    startCommand: bundle exec ruby newton_api.rb
    envVars:
      - key: PORT
        value: 4567
      - key: NEWTON_STORAGE
        value: /tmp/newton
```

### 1.4 Deploy to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will detect the `render.yaml` and configure automatically
5. Click "Create Web Service"
6. Wait for deployment (approximately 2-3 minutes)
7. Copy your URL: `https://newton-kernel-xxxx.onrender.com`

### 1.5 Verify Deployment

```bash
curl https://newton-kernel-xxxx.onrender.com/health
```

Expected response:
```json
{"status":"ok","version":"1.0.0"}
```

---

## STEP 2: CONFIGURE THE UNIVERSAL ADAPTER

### 2.1 Set Environment Variables

```bash
# Required
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

### 2.2 Run the Adapter

```bash
ruby adapter_universal.rb
```

### 2.3 Test the Flow

```
Newton (Anthropic Claude)> Clean my inbox

══ SOVEREIGN TRANSACTION (Anthropic Claude) ══
Intent: "Clean my inbox"
   [PENDING] Z: 6.67 | FP: A3F9B2C8
>  Verify? (y/n): y
   [PENDING] Z: 3.33 | FP: A3F9B2C8
>  Verify? (y/n): y
   [VERIFIED] Z: 0.00
   [✓] VERIFIED. 1 == 1.
   [-] Engaging Anthropic Claude...
   [>] Action: {"tool":"gmail","action":"archive","query":"older_than:30d"}
   [✓] COMMITTED. ID: X_7B3F2A1C
```

---

## STEP 3: OPTIONAL DASHBOARD

Host `newton_dashboard.html` on any static hosting service (Netlify, Vercel, GitHub Pages) or open locally in a browser. Update the `NEWTON_HOST` constant in the JavaScript to point to your deployed kernel.

For local testing, the dashboard runs entirely client-side with a simulated Newton engine.

---

## API REFERENCE

### POST /make
Commit an intent to the ledger. Each commit lowers the Z-score by 3.33.

**Request:**
```json
{
  "owner": "Jared",
  "intent": "Clean my inbox"
}
```

**Response:**
```json
{
  "id": "N_A3F9B2C8",
  "intent": "Clean my inbox",
  "z": 6.67,
  "status": "PENDING",
  "fingerprint": "A3F9B2C8E1D4",
  "timestamp": 1735654320,
  "remaining": 2
}
```

### GET /verify/:fingerprint?owner=X
Check if a fingerprint exists and its current status.

### GET /audit/:owner
Retrieve the complete ledger for an owner.

### POST /execute
Execute an action against a verified intent.

**Request:**
```json
{
  "owner": "Jared",
  "fingerprint": "A3F9B2C8E1D4",
  "action": {"tool": "gmail", "action": "archive"}
}
```

### POST /package
Export all verified intents as a signed payload for sharing or backup.

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

1. The Vault encrypts all ledger data with AES-256 using the owner name as key derivation input
2. API keys are never sent to the Newton kernel—they stay in the adapter
3. For production, add authentication to the Newton API endpoints
4. Consider rate limiting on `/make` to prevent abuse

---

## NEXT STEPS

1. **Enterprise Pilot:** Deploy to a regulated industry client (healthcare, finance, legal)
2. **Mobile App:** Wrap the adapter in a React Native or Swift app
3. **Multi-Party Consensus:** Replace manual verification with multi-signature from separate systems
4. **Billing Integration:** Add Stripe metering on `/execute` calls

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
