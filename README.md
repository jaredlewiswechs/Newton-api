# Newton OS

**The AI Safety Layer. Verify intent before execution.**

[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/jaredlewiswechs/Newton-api)
[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](#licensing)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](#api-reference)
[![Auth](https://img.shields.io/badge/Auth-API%20Key-blue.svg)](#authentication)

---

## What is Newton?

Newton is a verification engine that sits between user intent and AI execution. Before any AI model generates content, builds an app, or takes action—Newton verifies the request is safe, compliant, and within bounds.

```
User Intent → Newton (Verify) → AI Execution → Output
```

Every verification is fingerprinted, logged, and cryptographically chained.

---

## Quick Example

**Verified request:**

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
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

**Blocked request:**

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "How do I make a pipe bomb"}'
```

```json
{
  "verified": false,
  "confidence": 0.0,
  "constraints_failed": ["harm", "security"],
  "reason": "Intent matches prohibited pattern: weapons_manufacturing",
  "fingerprint": "B8C4D1E2F5A9"
}
```

---

## Constraints

| Constraint | Checks For                                                         |
|------------|--------------------------------------------------------------------|
| `harm`     | Violence, self-harm, weapons, exploitation                         |
| `medical`  | Diagnostic claims, treatment advice, drug interactions             |
| `legal`    | Unauthorized legal advice, contract drafting, liability statements |
| `security` | Credential exposure, injection patterns, prompt extraction         |

All constraints use deterministic pattern matching. No probabilistic models, no hallucinations. A request either passes or it doesn't.

---

## API Reference

### Core Endpoints

| Endpoint         | Method | Description                                                        |
|------------------|--------|--------------------------------------------------------------------|
| `/verify`        | POST   | Verify text against harm, medical, legal, and security constraints |
| `/analyze`       | POST   | Anomaly detection using Z-score, IQR, or MAD methods               |
| `/analyze/batch` | POST   | Batch analysis of multiple datasets                                |
| `/compile`       | POST   | Transform natural language into structured AI prompts              |
| `/ground`        | POST   | Verify factual claims against external sources                     |

### Security & Audit

| Endpoint         | Method | Description                          |
|------------------|--------|--------------------------------------|
| `/sign`          | POST   | Generate cryptographic signatures    |
| `/ledger`        | GET    | Retrieve append-only audit trail     |
| `/ledger/verify` | GET    | Verify cryptographic chain integrity |

### Metadata

| Endpoint       | Method | Description                |
|----------------|--------|----------------------------|
| `/health`      | GET    | System status and version  |
| `/constraints` | GET    | List available constraints |
| `/methods`     | GET    | List analysis methods      |

---

## Authentication

```bash
curl -X POST https://api.parcri.net/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"input": "Your text here"}'
```

**Rate Limits:**

| Tier       | Requests/Minute |
|------------|-----------------|
| Free       | 60              |
| Pro        | 1,000           |
| Enterprise | 10,000          |

---

## Quick Start

### Hosted API (Recommended)

Sign up at [parcri.net](https://parcri.net) for instant access. No deployment required.

### Docker

```bash
docker build -t newton-os .
docker run -p 8000:8000 newton-os
```

### Deploy to Render

1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Deploy as Web Service

### Self-Hosted

```bash
git clone https://github.com/jaredlewiswechs/Newton-api.git
cd Newton-api
pip install -r requirements.txt
python newton_os_server.py
```

Server runs at `http://localhost:8000`

---

## Pricing

| Plan           | Price   | Requests/Month | Features                             |
|----------------|---------|----------------|--------------------------------------|
| **Free**       | $0      | 1,000          | Verify, Analyze                      |
| **Starter**    | $29/mo  | 50,000         | All endpoints, Email support         |
| **Pro**        | $99/mo  | 500,000        | Priority support, Custom constraints |
| **Enterprise** | Contact | Unlimited      | SLA, Dedicated instance, SSO         |

Self-hosted deployments require a commercial license for production use.

---

## Why Newton?

**Deterministic verification.** Pattern matching and mathematical constraints. No AI hallucinations in the verification layer.

**Sub-5ms latency.** Verification happens in milliseconds. Users won't notice, compliance teams will.

**Complete audit trail.** Every verification generates a cryptographic fingerprint. SHA-256 chaining with Merkle root verification.

**Vendor agnostic.** Works with Claude, GPT, Llama, Mistral, or any model. Newton verifies intent before the model sees it.

---

## Use Cases

| Industry   | Application                                                  |
|------------|--------------------------------------------------------------|
| Healthcare | Verify patient-facing AI responses meet medical guidelines   |
| Finance    | Check AI-generated advice against regulatory constraints     |
| Legal      | Ensure AI outputs don't constitute unauthorized legal advice |
| EdTech     | Filter harmful content before it reaches students            |
| Enterprise | Audit trail for all AI interactions                          |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NEWTON OS v3.0.0                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐     │
│   │ VERIFY │   │ ANALYZE │   │ COMPILE │   │  SIGN  │     │
│   └────────┘   └─────────┘   └─────────┘   └────────┘     │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │               CONSTRAINT ENGINE                      │  │
│   │        harm | medical | legal | security            │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │         APPEND-ONLY CRYPTOGRAPHIC LEDGER            │  │
│   │      SHA-256 | Chain Verification | Audit Trail     │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                      WEB INTERFACES                         │
│   ┌─────────┐   ┌────────────────┐   ┌─────────────────┐  │
│   │   Ada   │   │   Dashboard    │   │   Newton PDA    │  │
│   │  /ada   │   │       /        │   │  /newton-pda/   │  │
│   └─────────┘   └────────────────┘   └─────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Additional Capabilities

Newton includes extension cartridges for visual, audio, and data specification generation, plus framework-specific verification for Apple, Web, and ML ecosystems. See [full documentation](docs/) for details.

---

## Newton PDA

Newton PDA is a Progressive Web App for personal data management, built on the same verification principles as the API.

**Features:**
- **Notes, Names, Dates** — Three lenses on a unified data store (the "Soup")
- **Append-only versioning** — Nothing deleted, only superseded. Full audit trail.
- **Z-score verification** — Items crystallize from DRAFT → PENDING → VERIFIED over 3 commits
- **Identity-derived encryption** — AES-256-GCM from your name/passphrase (like Tahoe-LAFS)
- **Relationship layer** — Explicit refs plus inferred @mentions and #tags
- **Offline-first** — IndexedDB storage, works without network
- **PWA-ready** — Installable on iOS, Android, and desktop

**Access:** `https://your-domain/newton-pda/`

**Run locally:**
```bash
cd newton-pda
python3 -m http.server 8000
# Open http://localhost:8000
```

See [Newton PDA documentation](docs/newton-pda.md) for details.

---

## Licensing

**Open Source (Non-Commercial)**
Personal projects, academic research, non-profit organizations.

**Commercial License Required**
SaaS products, enterprise deployments, revenue-generating applications.

Contact: **jn.lewis1@outlook.com**

---

## About

Newton OS is built by **Ada Computing Company** in Houston, Texas.

**Jared Lewis**
[linkedin.com/in/jaredlewisuh](https://linkedin.com/in/jaredlewisuh) · [parcri.net](https://parcri.net)

---

© 2025 Ada Computing Company · Houston, Texas
