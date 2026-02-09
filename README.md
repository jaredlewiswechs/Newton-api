# Newton Supercomputer

**Verified Computation with Constraint Language (tinyTalk)**

[![Vercel](https://img.shields.io/badge/deployed%20on-Vercel-black.svg)](#deploy-to-vercel)
[![License](https://img.shields.io/badge/license-Dual%20License-blue.svg)](#license)

> **Free for education & research. Commercial license required for business use.**

---

## Projects

| Project | Description | Location |
|---------|-------------|----------|
| **realTinyTalk** | Production tinyTalk runtime — Smalltalk-inspired constraint language | [`realTinyTalk/`](realTinyTalk/) |
| **Newton Agent** | 14-subsystem intelligence agent with verified computation | [`newton_agent/`](newton_agent/) |
| **Project ADA** | System-of-systems agent app synthesizing all 14 subsystems | [`ProjectADA/`](ProjectADA/) |
| **Nina** | Nina system — API, app, consumer/developer interfaces | [`nina/`](nina/) |
| **Adan Portable** | Lightweight portable Adan distribution | [`adan_portable/`](adan_portable/) |
| **Newton Teacher's Aide** | Offline-capable educational tool for classrooms | [`teachers-aide/`](teachers-aide/) |

## Quick Start

```bash
# Install
pip install -e .

# Run the API locally
newton serve

# Run tinyTalk
newton demo
```

## Deploy to Vercel

The API deploys to Vercel as a single serverless function:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Configuration is in [`vercel.json`](vercel.json) — Python 3.12 runtime, all routes hit `/api/index.py`.

For the **Teacher's Aide** standalone deploy, see [`newton-teachers-aide-deploy/`](newton-teachers-aide-deploy/).

## Repo Structure

```
Newton-api/
├── api/                  # Vercel serverless entry point
├── core/                 # Core Python modules (API backend)
├── newton_supercomputer.py  # Main API implementation
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel deployment config
│
├── realTinyTalk/         # Production tinyTalk runtime
├── newton_agent/         # Newton Agent (14 subsystems)
├── ProjectADA/           # Project ADA agent app
├── nina/                 # Nina system
├── adan/                 # Adan core (knowledge base, agent)
├── adan_portable/        # Portable Adan distribution
├── teachers-aide/        # Newton Teacher's Aide
├── newton-teachers-aide-deploy/  # Standalone deploy package
│
├── newton_core/          # Rust verification core (AIDA)
├── newton_tlm/           # Transaction Ledger Manager (ACID)
├── newton_kernel/        # Kernel execution layer
├── newton_geometry/      # Geometric operations
├── tests/                # Test suite
│
└── _archive/             # Archived projects & docs (not deployed)
```

## Core Infrastructure

- **`newton_core/`** — Rust-based AIDA verification engine
- **`newton_tlm/`** — ACID-compliant Transaction Ledger Manager
- **`newton_kernel/`** — Constraint execution kernel
- **`newton_geometry/`** — Graph, hypergraph, manifold, topology operations

## Tests

```bash
pytest tests/
```

## Archive

Older projects and documentation have been moved to `_archive/`. Nothing in `_archive/` is deployed to Vercel. All git history is preserved.

## License

Dual licensed — free for education/research, commercial license required for business use. See [LICENSE](LICENSE).
