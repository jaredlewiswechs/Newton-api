#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CONFIGURATION - SINGLE SOURCE OF TRUTH
All Newton/Adan components must use these canonical paths.
═══════════════════════════════════════════════════════════════════════════════

This prevents data fragmentation across:
- adan/
- adan_portable/adan/
- newton_agent/
- nina/

All paths are relative to this file's parent directory (Newton-api root).

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL ROOT
# ═══════════════════════════════════════════════════════════════════════════════

# Newton-api root directory (where this file lives)
NEWTON_ROOT = Path(__file__).parent.resolve()


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL KNOWLEDGE STORE
# Single .knowledge_store.json for ALL components
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_KNOWLEDGE_STORE_PATH = NEWTON_ROOT / "adan" / ".knowledge_store.json"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL KNOWLEDGE BASE MODULE
# Use adan/ as the authoritative knowledge base
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_ADAN_PATH = NEWTON_ROOT / "adan"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL CACHE DIRECTORY
# Single .newton_cache for embeddings, etc.
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_CACHE_PATH = NEWTON_ROOT / ".newton_cache"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_knowledge_store_path() -> Path:
    """Get the canonical knowledge store path."""
    return CANONICAL_KNOWLEDGE_STORE_PATH


def get_adan_path() -> Path:
    """Get the canonical adan module path."""
    return CANONICAL_ADAN_PATH


def get_cache_path() -> Path:
    """Get the canonical cache path."""
    CANONICAL_CACHE_PATH.mkdir(exist_ok=True)
    return CANONICAL_CACHE_PATH


def ensure_adan_in_path():
    """Ensure canonical adan is in sys.path."""
    import sys
    adan_str = str(CANONICAL_ADAN_PATH.parent)
    if adan_str not in sys.path:
        sys.path.insert(0, adan_str)


# ═══════════════════════════════════════════════════════════════════════════════
# PRINT CONFIG (for debugging)
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

NEWTON_ROOT:                   {NEWTON_ROOT}
CANONICAL_KNOWLEDGE_STORE:     {CANONICAL_KNOWLEDGE_STORE_PATH}
CANONICAL_ADAN_PATH:           {CANONICAL_ADAN_PATH}
CANONICAL_CACHE_PATH:          {CANONICAL_CACHE_PATH}

Knowledge Store Exists:        {CANONICAL_KNOWLEDGE_STORE_PATH.exists()}
Adan Path Exists:              {CANONICAL_ADAN_PATH.exists()}
═══════════════════════════════════════════════════════════════════════════════
    """)
