# Legacy Code

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Historical implementations preserved for reference.

**Note**: Legacy code does not include the **finfr = f/g** ratio constraint system. See the current implementation for dimensional analysis features.

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

The active Newton Supercomputer implementation (v1.2.0) is in:

- `newton_supercomputer.py` - Main API server
- `core/` - Core modules (CDL, Logic, Forge, Vault, Ledger, Bridge, Robust)
- `tinytalk_py/` - tinyTalk constraint language with f/g ratio support
- `frontend/` - Cloudflare Pages frontend

## Migration Notes

The legacy code uses the original verification patterns. The new implementation in `core/` provides:

- **CDL 3.0** with conditionals, temporal operators, and **f/g ratio constraints**
- Verified Turing complete Logic Engine
- PBFT distributed consensus
- Adversarial-resistant statistics
- Merkle tree audit proofs

### New in v1.2.0: f/g Ratio Constraints

The current implementation includes dimensional analysis via **finfr = f/g**:

```python
# Legacy pattern (still works)
when(balance < 0, finfr)

# New ratio pattern (v1.2.0)
when(ratio(withdrawal, balance) > 1.0, finfr)
```

Ratio operators: `ratio_lt`, `ratio_le`, `ratio_gt`, `ratio_ge`, `ratio_eq`, `ratio_ne`

---

© 2025-2026 Jared Nashon Lewis · Jared Lewis Conglomerate · parcRI · Newton · tinyTalk · Ada Computing Company · Houston, Texas

*Preserved for historical reference. Not actively maintained. finfr = f/g.*
