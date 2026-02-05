"""Adanpedia witness example adapter.

Provides a simple interface to fetch anonymized, constraint-compliant
witness examples. For now this is a deterministic mock that can be
replaced by integration with `adan` services or a corpus backend.
"""
from typing import List, Dict, Optional

_MOCK_CORPUS = [
    {"id": "w1", "title": "Example: Intro + Background", "handle": "Introduction: context and thesis", "snippet": "[An admissible example intro skeleton]"},
    {"id": "w2", "title": "Example: Thematic approach", "handle": "Theme 1: definition & scope", "snippet": "[A thematic trajectory sample]"},
    {"id": "w3", "title": "Example: Chronological arc", "handle": "Early developments / background", "snippet": "[Chronological handle sample]"},
]


def _from_knowledge_store(handles: Optional[List[str]] = None, max_examples: int = 3) -> List[Dict]:
    try:
        from adan.knowledge_store import get_knowledge_store
        ks = get_knowledge_store()
        results = []
        if not handles:
            facts = ks.get_all()
            for f in facts[:max_examples]:
                results.append({"id": f.id, "title": f.key, "handle": f.key, "snippet": f.fact})
            return results

        for h in handles:
            found = ks.search(h, limit=1)
            if found:
                f = found[0]
                results.append({"id": f.id, "title": f.key, "handle": f.key, "snippet": f.fact})
        return results[:max_examples]
    except Exception:
        return []


def fetch_witness_examples(handles: Optional[List[str]] = None, max_examples: int = 3) -> List[Dict]:
    """Fetch examples from the Adan knowledge store when available, else fallback to mock corpus."""
    # Try real knowledge store first
    real = _from_knowledge_store(handles, max_examples)
    if real:
        return real

    # Fallback to mock
    if not handles:
        return _MOCK_CORPUS[:max_examples]
    results = []
    for h in handles:
        for doc in _MOCK_CORPUS:
            if doc["handle"].lower().startswith(h.lower().split(':')[0]):
                results.append(doc)
                break
    if not results:
        return _MOCK_CORPUS[:max_examples]
    return results[:max_examples]


__all__ = ["fetch_witness_examples"]
