# Legacy Code

Historical implementations preserved for reference.

## Contents

| File | Description |
|------|-------------|
| `newton_os_server.py` | Original Python server (v1-v2) |
| `newton_public.py` | Public API subset |
| `newton_api.rb` | Ruby implementation |
| `adapter_universal.rb` | Universal adapter |
| `ada.html` | Ada conversational interface |
| `newton_dashboard.html` | State machine dashboard |
| `newton-pda/` | Personal Data Assistant PWA |
| `services/` | TypeScript service definitions |

## Current Implementation

The active Newton Supercomputer implementation is in:

- `newton_supercomputer.py` - Main API server
- `core/` - Core modules (CDL, Logic, Forge, Vault, Ledger, Bridge, Robust)
- `frontend/` - Cloudflare Pages frontend

## Migration Notes

The legacy code uses the original verification patterns. The new implementation in `core/` provides:

- CDL 3.0 with conditionals and temporal operators
- Verified Turing complete Logic Engine
- PBFT distributed consensus
- Adversarial-resistant statistics
- Merkle tree audit proofs

---

*Preserved for historical reference. Not actively maintained.*
