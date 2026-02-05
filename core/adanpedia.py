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


def fetch_witness_examples(handles: Optional[List[str]] = None, max_examples: int = 3) -> List[Dict]:
    if not handles:
        return _MOCK_CORPUS[:max_examples]
    results = []
    for h in handles:
        for doc in _MOCK_CORPUS:
            if doc["handle"].lower().startswith(h.lower().split(':')[0]):
                results.append(doc)
                break
    if not results:
        # fallback: return first N
        return _MOCK_CORPUS[:max_examples]
    return results[:max_examples]


__all__ = ["fetch_witness_examples"]
