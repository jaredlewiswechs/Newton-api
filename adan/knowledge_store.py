#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SHARED KNOWLEDGE STORE
Persistent knowledge store shared between Adan, Adanpedia, and all components
═══════════════════════════════════════════════════════════════════════════════

This is the single source of truth for imported/added facts.
Stored as JSON on disk for persistence across restarts.
Uses fuzzy matching from language_mechanics for semantic search.
"""

import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from threading import Lock
from difflib import get_close_matches
import os

# Import language mechanics for fuzzy matching
try:
    from .language_mechanics import get_language_mechanics
    HAS_LANGUAGE_MECHANICS = True
except ImportError:
    HAS_LANGUAGE_MECHANICS = False

# Store file location - USE CANONICAL PATH
# This ensures ALL Newton components share the same knowledge store
try:
    import sys
    _newton_root = Path(__file__).parent.parent
    if str(_newton_root) not in sys.path:
        sys.path.insert(0, str(_newton_root))
    from newton_config import CANONICAL_KNOWLEDGE_STORE_PATH
    STORE_PATH = CANONICAL_KNOWLEDGE_STORE_PATH
except ImportError:
    # Fallback to local path if newton_config not available
    STORE_PATH = Path(__file__).parent / ".knowledge_store.json"

# Thread-safe lock
_lock = Lock()

@dataclass
class StoredFact:
    """A fact stored in the knowledge store."""
    id: str
    key: str
    fact: str
    category: str
    source: str
    source_url: str
    confidence: float
    added_at: float
    added_by: str  # "wikipedia", "manual", "system"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "StoredFact":
        return cls(**d)


class KnowledgeStore:
    """
    Persistent knowledge store.
    Thread-safe, file-backed, shared across all Adan components.
    """
    
    def __init__(self, store_path: Path = STORE_PATH):
        # Accept either string or Path
        if isinstance(store_path, str):
            store_path = Path(store_path)
        self.store_path = store_path
        self._facts: Dict[str, StoredFact] = {}
        self._load()
    
    def _load(self):
        """Load facts from disk."""
        with _lock:
            if self.store_path.exists():
                try:
                    with open(self.store_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._facts = {
                            k: StoredFact.from_dict(v) 
                            for k, v in data.get("facts", {}).items()
                        }
                except Exception as e:
                    print(f"Warning: Could not load knowledge store: {e}")
                    self._facts = {}
            else:
                self._facts = {}
    
    def _save(self):
        """Save facts to disk."""
        with _lock:
            data = {
                "facts": {k: v.to_dict() for k, v in self._facts.items()},
                "updated_at": time.time(),
                "count": len(self._facts)
            }
            with open(self.store_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
    
    def _generate_id(self, key: str) -> str:
        """Generate a unique ID for a fact."""
        return hashlib.md5(key.lower().encode()).hexdigest()[:12]
    
    def add(self, 
            key: str, 
            fact: str, 
            category: str, 
            source: str,
            source_url: str = "",
            confidence: float = 0.9,
            added_by: str = "manual") -> StoredFact:
        """Add a fact to the store."""
        fact_id = self._generate_id(key)
        
        stored = StoredFact(
            id=fact_id,
            key=key,
            fact=fact,
            category=category,
            source=source,
            source_url=source_url or "#",
            confidence=confidence,
            added_at=time.time(),
            added_by=added_by
        )
        
        with _lock:
            self._facts[fact_id] = stored
        
        self._save()
        return stored
    
    def get(self, fact_id: str) -> Optional[StoredFact]:
        """Get a fact by ID."""
        return self._facts.get(fact_id)
    
    def get_by_key(self, key: str) -> Optional[StoredFact]:
        """Get a fact by key."""
        fact_id = self._generate_id(key)
        return self._facts.get(fact_id)
    
    def search(self, query: str, limit: int = 10, threshold: float = 0.6) -> List[StoredFact]:
        """
        Search facts using fuzzy matching.
        
        Uses difflib's get_close_matches for fuzzy string matching,
        providing semantic-like search without embeddings.
        """
        query_lower = query.lower().strip()
        results = []
        scored_results = []
        
        # Build searchable keys (fact keys + first words of facts)
        key_to_fact = {}
        for fact in self._facts.values():
            key_to_fact[fact.key.lower()] = fact
            # Also index by first few words of fact
            first_words = ' '.join(fact.fact.split()[:5]).lower()
            key_to_fact[first_words] = fact
        
        # Try exact substring match first (fast path)
        for fact in self._facts.values():
            if (query_lower in fact.key.lower() or 
                query_lower in fact.fact.lower()):
                results.append(fact)
                if len(results) >= limit:
                    return results
        
        # If no exact matches, use fuzzy matching
        if not results:
            all_keys = list(key_to_fact.keys())
            matches = get_close_matches(query_lower, all_keys, n=limit, cutoff=threshold)
            for match in matches:
                fact = key_to_fact.get(match)
                if fact and fact not in results:
                    results.append(fact)
        
        return results[:limit]
    
    def get_all(self, category: str = None) -> List[StoredFact]:
        """Get all facts, optionally filtered by category."""
        if category:
            return [f for f in self._facts.values() if f.category == category]
        return list(self._facts.values())
    
    def get_by_category(self, category: str) -> List[StoredFact]:
        """Get facts by category."""
        return [f for f in self._facts.values() if f.category == category]
    
    def get_by_source(self, source: str) -> List[StoredFact]:
        """Get facts by source."""
        return [f for f in self._facts.values() if f.source == source]
    
    def get_categories(self) -> Dict[str, int]:
        """Get category counts."""
        cats = {}
        for f in self._facts.values():
            cats[f.category] = cats.get(f.category, 0) + 1
        return dict(sorted(cats.items()))
    
    def delete(self, fact_id: str) -> bool:
        """Delete a fact."""
        with _lock:
            if fact_id in self._facts:
                del self._facts[fact_id]
                self._save()
                return True
        return False
    
    def clear(self):
        """Clear all facts."""
        with _lock:
            self._facts = {}
            self._save()
    
    def count(self) -> int:
        """Get total fact count."""
        return len(self._facts)
    
    def stats(self) -> Dict:
        """Get store statistics."""
        return {
            "total_facts": len(self._facts),
            "categories": self.get_categories(),
            "sources": {s: len(self.get_by_source(s)) for s in set(f.source for f in self._facts.values())},
            "store_path": str(self.store_path),
            "file_exists": self.store_path.exists()
        }


# Singleton instance
_store: Optional[KnowledgeStore] = None

def get_knowledge_store() -> KnowledgeStore:
    """Get the singleton knowledge store instance."""
    global _store
    if _store is None:
        _store = KnowledgeStore()
    return _store


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    store = get_knowledge_store()
    print(f"Knowledge Store: {store.store_path}")
    print(f"Facts: {store.count()}")
    print(f"Categories: {store.get_categories()}")
