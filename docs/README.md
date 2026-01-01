# Newton Supercomputer Documentation

**Verified Computation. Ask Newton. Go.**

Welcome to the Newton Supercomputer documentation. Newton is a distributed verification system where the constraint IS the instruction and the verification IS the computation.

---

## Documentation Index

### Getting Started
- [Quick Start Guide](getting-started.md) - Get up and running in 5 minutes
- [Authentication](authentication.md) - API keys, rate limits, and security

### Core Concepts
- [Whitepaper](../WHITEPAPER.md) - Architecture and philosophy
- [Logic Engine](logic-engine.md) - Verified Turing complete computation
- [Technical Roadmap](ROADMAP.md) - Development phases and goals

### API Reference
- [API Overview](api-reference.md) - Complete API reference
- [Core Endpoints](endpoints/core.md) - Verify, Calculate, Constraint, Ground
- [Audit & Security](endpoints/audit.md) - Ledger, Vault, Certificates
- [Metadata](endpoints/metadata.md) - Health, Metrics, Examples

### Components

| Component | Documentation | Purpose |
|-----------|---------------|---------|
| **CDL** | [api-reference.md#constraint](api-reference.md#constraint) | Constraint Definition Language |
| **Logic** | [logic-engine.md](logic-engine.md) | Verified computation engine |
| **Forge** | [api-reference.md#verify](api-reference.md#verify) | Content verification |
| **Vault** | [api-reference.md#vault](api-reference.md#vault-store) | Encrypted storage |
| **Ledger** | [api-reference.md#ledger](api-reference.md#ledger) | Immutable audit trail |
| **Robust** | [api-reference.md#statistics](api-reference.md#statistics) | Adversarial statistics |

### Advanced Features
- [Extension Cartridges](cartridges.md) - Visual, Audio, Sequence, Data
- [Framework Verification](frameworks.md) - Apple, Web, ML framework constraints
- [Claim Grounding](grounding.md) - Fact-checking against external sources
- [Newton PDA](newton-pda.md) - Personal Data Assistant (PWA)

### Integration
- [Self-Hosting Guide](self-hosting.md) - Deploy Newton on your infrastructure
- [Environment Variables](configuration.md) - Configuration options

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [API Reference](api-reference.md) | Full endpoint documentation |
| [Logic Engine](logic-engine.md) | Verified computation guide |
| [Hosted API](https://newton-api.onrender.com) | Production deployment |
| [GitHub](https://github.com/jaredlewiswechs/Newton-api) | Source code |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWTON SUPERCOMPUTER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │   CDL   │  │  LOGIC  │  │  FORGE  │  │ ROBUST  │           │
│  │ (lang)  │  │ (calc)  │  │  (CPU)  │  │ (stats) │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       └────────────┴────────────┴────────────┘                 │
│                         │                                       │
│  ┌─────────┐  ┌────────┴────────┐  ┌─────────┐                │
│  │  VAULT  │  │     LEDGER      │  │ BRIDGE  │                │
│  │  (RAM)  │  │     (disk)      │  │  (bus)  │                │
│  └─────────┘  └─────────────────┘  └─────────┘                │
│                                                                 │
│                      ASK NEWTON                                 │
│                        /ask                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Component | Purpose | Key Feature |
|-----------|---------|-------------|
| **CDL** | Constraint Definition Language | Conditionals, temporal ops, aggregations |
| **Logic** | Verified Computation Engine | Turing complete with bounded loops |
| **Forge** | Verification Engine | Parallel constraint evaluation, <1ms |
| **Vault** | Encrypted Storage | AES-256-GCM, identity-derived keys |
| **Ledger** | Immutable History | Hash-chained, Merkle proofs |
| **Bridge** | Distributed Protocol | PBFT consensus, Byzantine fault tolerant |
| **Robust** | Adversarial Statistics | MAD over mean, locked baselines |

---

## Base URL

| Environment | URL |
|-------------|-----|
| **Hosted API** | `https://newton-api.onrender.com` |
| **Self-hosted** | `http://localhost:8000` |

---

## Quick Start

### 1. Calculate (Verified Computation)

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression": {"op": "+", "args": [2, 3]}}'
```

### 2. Verify (Content Safety)

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"input": "Help me write a business plan"}'
```

### 3. Ask Newton (Full Pipeline)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Is this safe to execute?"}'
```

---

## The Fundamental Law

```python
def newton(current, goal):
    return current == goal

# 1 == 1 → execute
# 1 != 1 → halt
```

This isn't a feature. It's the architecture.

---

## Guarantees

| Property | Implementation |
|----------|----------------|
| **Determinism** | Same input always produces same output |
| **Termination** | HaltChecker proves all constraints terminate |
| **Consistency** | No constraint can be both pass and fail |
| **Auditability** | Every verification in immutable ledger |
| **Adversarial Resistance** | MAD stats, locked baselines, source tracking |

---

## Version

Current version: **1.0.0**

---

© 2025-2026 Ada Computing Company · Houston, Texas

*"1 == 1. The cloud is weather. We're building shelter."*
