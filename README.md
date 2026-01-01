# Newton OS

**The AI Safety Layer. Verify intent before execution.**

[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/jaredlewiswechs/Newton-api)
[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](#licensing)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](#api-reference)
[![Auth](https://img.shields.io/badge/Auth-API%20Key-blue.svg)](#authentication)
[![Frameworks](https://img.shields.io/badge/Frameworks-10%2B-purple.svg)](#framework-verification)

---

## What is Newton?

Newton is a **verification engine** that sits between user intent and AI execution. Before any AI model generates content, builds an app, or takes action—Newton verifies the request is safe, compliant, and within bounds.

```
User Intent → Newton (Verify) → AI Execution → Output
```

**The Problem:** AI systems execute whatever they're asked. No guardrails. No audit trail. No compliance.

**The Solution:** Newton intercepts intent, checks it against configurable constraints, and only allows verified requests through. Every verification is fingerprinted and logged.

---

## Features

### Intent Verification
Check any text against harm, medical, legal, and security constraints before processing.

```bash
curl -X POST https://your-newton-api.com/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Help me write a business plan"}'
```

```json
{
  "verified": true,
  "confidence": 92.3,
  "constraints_passed": ["harm", "medical", "legal", "security"],
  "fingerprint": "A7F3B2C8E1D4"
}
```

### Anomaly Detection (THIA)
Detect outliers in numerical data using Z-score, IQR, or MAD methods. Perfect for fraud detection, quality control, and monitoring.

```bash
curl -X POST https://your-newton-api.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"data": [45.2, 46.1, 102.4, 45.8], "method": "zscore"}'
```

### App Compiler (Rosetta)
Transform natural language into structured specifications for AI code generation. Includes App Store and Human Interface Guidelines verification.

```bash
curl -X POST https://your-newton-api.com/compile \
  -H "Content-Type: application/json" \
  -d '{"intent": "Build a fitness app with workout tracking"}'
```

---

## Use Cases

| Industry | Application |
|----------|-------------|
| **Healthcare** | Verify patient-facing AI responses meet medical guidelines |
| **Finance** | Check AI-generated advice against regulatory constraints |
| **Legal** | Ensure AI outputs don't constitute unauthorized legal advice |
| **EdTech** | Filter harmful content before it reaches students |
| **Enterprise** | Audit trail for all AI interactions in your organization |

---

## API Reference

### Core Verification

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verify` | POST | Verify text against harm, medical, legal, and security constraints |
| `/analyze` | POST | THIA anomaly detection (Z-score, IQR, MAD methods) |
| `/analyze/batch` | POST | Batch analysis of multiple datasets |
| `/compile` | POST | Rosetta compiler: natural language to AI-ready prompts |

### Extension Cartridges

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cartridge/visual` | POST | SVG generation with dimension constraints |
| `/cartridge/sound` | POST | Audio specs with frequency/duration limits |
| `/cartridge/sequence` | POST | Video/animation specs with frame constraints |
| `/cartridge/data` | POST | Report generation with statistical bounds |

### Security & Audit

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign` | POST | Generate cryptographic signatures for payloads |
| `/ledger` | GET | Append-only audit trail with chain verification |
| `/ledger/verify` | GET | Verify integrity of the cryptographic ledger chain |
| `/frameworks/verify` | POST | Verify intent against Apple framework constraints |

### Metadata

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status, version, and capabilities |
| `/constraints` | GET | List available content constraints |
| `/methods` | GET | List THIA analysis methods |
| `/frameworks` | GET | List Apple frameworks by category |
| `/frameworks/constraints` | GET | List framework-specific constraints |

### Authentication

Newton v3.0 includes built-in API key authentication and rate limiting.

```bash
# With API key authentication enabled
curl -X POST https://your-newton-api.com/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "Help me write a business plan"}'
```

**Configuration:**
```bash
# Enable authentication (default: disabled for development)
export NEWTON_AUTH_ENABLED=true

# Set enterprise API key
export NEWTON_ENTERPRISE_KEY=your-secret-key

# Custom API keys (JSON format)
export NEWTON_API_KEYS='{"key1": {"owner": "user1", "tier": "pro", "rate_limit": 1000}}'
```

**Rate Limits by Tier:**
| Tier | Requests/Minute |
|------|-----------------|
| Free | 60 |
| Pro | 1,000 |
| Enterprise | 10,000 |

---

## Quick Start

### Option 1: Hosted API (Recommended)

Sign up at [parcri.net](https://parcri.net) for instant API access. No deployment required.

### Option 2: Self-Hosted (Python)

```bash
# Clone the repository
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api

# Install dependencies
pip install -r requirements.txt

# Run the server
python newton_os_server.py
```

Server runs at `http://localhost:8000`

### Option 3: Ruby Kernel + Universal Adapter

For vendor-agnostic AI execution with the Z-score verification loop:

```bash
# Install Ruby dependencies
bundle install

# Deploy kernel to Render (or run locally)
ruby newton_api.rb  # Runs on port 4567

# Configure and run the adapter
export NEWTON_HOST="https://your-newton-kernel.onrender.com"
export VENDOR="claude"  # or groq, openai, local
export NEWTON_KEY="your-api-key"
ruby adapter_universal.rb
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions.

### Option 4: Docker

```bash
docker build -t newton-os .
docker run -p 8000:8000 newton-os
```

### Option 5: Deploy to Render

1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Deploy as Web Service
4. Your API is live

---

## Pricing

| Plan | Price | Requests/Month | Features |
|------|-------|----------------|----------|
| **Free** | $0 | 1,000 | Verify, Analyze |
| **Starter** | $29/mo | 50,000 | All endpoints, Email support |
| **Pro** | $99/mo | 500,000 | Priority support, Custom constraints |
| **Enterprise** | Contact | Unlimited | SLA, Dedicated instance, SSO |

*Self-hosted deployments require a commercial license for production use.*

---

## Why Newton?

### Deterministic Verification
No AI hallucinations. Newton uses pattern matching and mathematical constraints. `1 == 1`—always.

### Sub-5ms Latency
Verification happens in milliseconds. Your users won't notice, but your compliance team will thank you.

### Complete Audit Trail
Every verification generates a cryptographic fingerprint. Know exactly what was checked and when.

### Vendor Agnostic
Works with Claude, GPT, Llama, Mistral, or any AI. Newton doesn't care what model you use—it verifies intent before the model sees it.

---

## Extension Cartridges

Newton's constraint engine extends to any domain with definable bounds:

| Cartridge | Input | Constraints | Output |
|-----------|-------|-------------|--------|
| **Visual** | Design intent | Dimension/color bounds | SVG specification |
| **Sound** | Audio intent | Frequency/duration limits | WAV specification |
| **Sequence** | Animation intent | Frame/timing constraints | Video specification |
| **Data** | Report intent | Statistical bounds | Report specification |

```bash
# Example: Generate a visual specification
curl -X POST https://your-newton-api.com/cartridge/visual \
  -H "Content-Type: application/json" \
  -d '{"intent": "Create a dashboard with progress indicators", "width": 800, "height": 600}'
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NEWTON OS v3.0.0                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  VERIFY  │    │ ANALYZE  │    │ COMPILE  │    │   SIGN   │ │
│  │  Intent  │    │   THIA   │    │ Rosetta  │    │  Crypto  │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  EXTENSION CARTRIDGES                    │   │
│  │       visual | sound | sequence | data                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CONSTRAINT ENGINE                     │   │
│  │  harm | medical | legal | security | app_store | hig    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              APPEND-ONLY CRYPTOGRAPHIC LEDGER            │   │
│  │       SHA-256 | Chain Verification | Audit Trail        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Framework Verification

Newton v3.0 includes safety constraints for 10+ frameworks across Apple, Web, and ML ecosystems.

### Supported Frameworks

| Category | Frameworks |
|----------|------------|
| **Apple** | HealthKit, SwiftUI, ARKit, CoreML |
| **Web** | React, Node.js, Django, Flask |
| **ML/AI** | TensorFlow, PyTorch |

### Usage

```bash
# Verify intent against framework-specific constraints
curl -X POST "https://your-newton-api.com/frameworks/verify?intent=Build+an+app+with+torch.load&framework=pytorch"
```

### Example Constraints

**PyTorch Security:**
- Blocks untrusted `torch.load()` (arbitrary code execution risk)
- Requires model checksum validation
- Enforces confidence score display

**React Security:**
- Blocks `dangerouslySetInnerHTML` with user input
- Requires ARIA labels for accessibility
- Enforces XSS protection patterns

**TensorFlow ML Safety:**
- Blocks claims of "100% accuracy"
- Requires human oversight for critical decisions
- Enforces bias testing documentation

---

## Persistent Ledger

Newton v3.0 features an immutable, cryptographically-chained audit trail with Merkle root verification.

```bash
# Configure persistent storage
export NEWTON_LEDGER_PATH=/var/newton/ledger.json

# Verify chain integrity
curl https://your-newton-api.com/ledger/verify
```

```json
{
  "valid": true,
  "entries": 1247,
  "message": "Chain intact - all entries verified",
  "merkle_root": "A7B3C8F2E1D4"
}
```

**Features:**
- SHA-256 cryptographic chaining
- Merkle root computation for bulk verification
- Tamper detection via hash mismatch
- Persistent JSON storage (database-ready interface)

---

## Licensing

**Open Source (Non-Commercial)**
- Personal projects
- Academic research
- Non-profit organizations

**Commercial License Required**
- SaaS products
- Enterprise deployments
- Revenue-generating applications

Contact: **Jn.Lewis1@outlook.com**

---

## About

Newton OS is built by **Ada Computing Company** in Houston, Texas.

We believe AI should be safe by default. Newton is the verification layer that makes it possible.

**Jared Lewis**
- Email: Jn.Lewis1@outlook.com
- LinkedIn: [linkedin.com/in/jaredlewisuh](https://linkedin.com/in/jaredlewisuh)
- Web: [parcri.net](https://parcri.net)

---

## The Math

```
DW_AXIS = 2048
THRESHOLD = 1024
1 == 1
```

Intent equals execution only when verification passes. The math is solid.

---

© 2025 Ada Computing Company · Jared Lewis Conglomerate · Houston, Texas
