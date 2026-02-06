"""Simple adapter for adanpedia and knowledge-store access.

Provides a stable shim so the teacher's aide service can fetch witness
examples or bridge to `adan_portable` when available.
"""
from typing import List, Dict, Optional

try:
    # Prefer the core adapter if present
    from core.adanpedia import fetch_witness_examples as _core_fetch
except Exception:
    _core_fetch = None

_has_portable_store = False
_portable_get_store = None
try:
    # Try to import the adan_portable knowledge store
    from adan.knowledge_store import get_knowledge_store as _portable_get_store
    _has_portable_store = True
    _portable_get_store = _portable_get_store
except Exception:
    _has_portable_store = False


def fetch_examples(handles: Optional[List[str]] = None, max_examples: int = 3) -> List[Dict]:
    """Return witness/example documents.

    Tries the core `adanpedia` adapter first, then the `adan_portable` store,
    and finally falls back to lightweight mock behavior.
    """
    if _core_fetch:
        try:
            return _core_fetch(handles=handles, max_examples=max_examples)
        except Exception:
            pass

    # If adan_portable store is available, query it for handles
    if _has_portable_store and _portable_get_store:
        try:
            ks = _portable_get_store()
            results = []
            if not handles:
                facts = ks.get_all()
                for f in facts[:max_examples]:
                    results.append({"id": f.id, "title": f.key, "handle": f.key, "snippet": f.fact})
                return results

            for h in handles:
                found = ks.search(h, limit=max_examples)
                for f in found:
                    results.append({"id": f.id, "title": f.key, "handle": f.key, "snippet": f.fact})
            if results:
                return results[:max_examples]
        except Exception:
            pass

    # Fallback simple mock
    MOCK = [
        {"id": "m1", "title": "Example Intro", "handle": "intro", "snippet": "[intro sample]"},
        {"id": "m2", "title": "Worked Example", "handle": "worked", "snippet": "[worked example]"},
    ]
    if not handles:
        return MOCK[:max_examples]
    out = []
    for h in handles:
        for d in MOCK:
            if h.lower() in d["handle"]:
                out.append(d)
                break
    return out[:max_examples]


__all__ = ["fetch_examples"]
