#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NINA KNOWLEDGE INTEGRATION
Bridge to adan_portable's verified knowledge base

This module integrates Nina with the adan_portable knowledge system:
- KnowledgeBase: Pre-verified CIA Factbook, NIST, etc.
- KnowledgeStore: Dynamically added/imported facts
- QueryParser: Kinematic shape-based query parsing

CRITICAL: Nina does NOT reimplement the KB - it USES adan_portable's KB!
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

# Add adan_portable to path
ADAN_PATH = Path(__file__).parent.parent.parent.parent / "adan_portable"
if str(ADAN_PATH) not in sys.path:
    sys.path.insert(0, str(ADAN_PATH))

# Import adan_portable knowledge system
try:
    from adan.knowledge_base import (
        KnowledgeBase, 
        get_knowledge_base,
        VerifiedFact,
        COUNTRY_CAPITALS,
        COUNTRY_POPULATIONS,
        COUNTRY_LANGUAGES,
        COUNTRY_CURRENCIES,
        SCIENTIFIC_CONSTANTS,
        PERIODIC_TABLE,
        COMPANY_FACTS,
        ACRONYMS,
    )
    HAS_KB = True
except ImportError as e:
    print(f"[NINA] Warning: Could not import adan.knowledge_base: {e}")
    HAS_KB = False

try:
    from adan.knowledge_store import (
        KnowledgeStore,
        get_knowledge_store,
        StoredFact,
    )
    HAS_STORE = True
except ImportError as e:
    print(f"[NINA] Warning: Could not import adan.knowledge_store: {e}")
    HAS_STORE = False

try:
    from adan.query_parser import (
        KinematicQueryParser,
        get_query_parser,
        QueryShape as AdanQueryShape,
        ParsedQuery as AdanParsedQuery,
    )
    HAS_PARSER = True
except ImportError as e:
    print(f"[NINA] Warning: Could not import adan.query_parser: {e}")
    HAS_PARSER = False

try:
    from adan.knowledge_sources import (
        Source,
        SourceTier,
        SOURCES,
    )
    HAS_SOURCES = True
except ImportError as e:
    print(f"[NINA] Warning: Could not import adan.knowledge_sources: {e}")
    HAS_SOURCES = False


@dataclass
class NinaFact:
    """
    A fact retrieved from the knowledge system.
    Wraps adan's VerifiedFact with Nina-specific metadata.
    """
    value: Any
    fact_text: str
    category: str
    source: str
    source_url: str
    confidence: float
    query_tier: str  # Which tier matched: "store", "shape", "semantic", "keyword"
    
    @classmethod
    def from_verified_fact(cls, vf: 'VerifiedFact', tier: str = "keyword") -> 'NinaFact':
        """Create NinaFact from adan's VerifiedFact."""
        # Extract the key value from the fact text
        # For "The capital of France is Paris." -> value = "Paris"
        value = vf.fact  # Default to full fact
        
        return cls(
            value=value,
            fact_text=vf.fact,
            category=vf.category,
            source=vf.source,
            source_url=vf.source_url,
            confidence=vf.confidence,
            query_tier=tier
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "fact": self.fact_text,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "confidence": self.confidence,
            "tier": self.query_tier
        }


class NinaKnowledge:
    """
    Nina's interface to the adan_portable knowledge system.
    
    This is the SINGLE SOURCE OF TRUTH for Nina's knowledge.
    It does NOT duplicate or reimplement - it BRIDGES to adan_portable.
    
    Features:
    - Five-tier kinematic query resolution
    - Shared persistent knowledge store
    - Pre-verified authoritative facts
    - Query shape recognition
    """
    
    def __init__(self):
        # Initialize adan_portable components
        self._kb: Optional['KnowledgeBase'] = None
        self._store: Optional['KnowledgeStore'] = None
        self._parser: Optional['KinematicQueryParser'] = None
        
        if HAS_KB:
            self._kb = get_knowledge_base()
        
        if HAS_STORE:
            self._store = get_knowledge_store()
        
        if HAS_PARSER:
            self._parser = get_query_parser()
        
        # Stats
        self.queries = 0
        self.hits = 0
    
    @property
    def is_available(self) -> bool:
        """Check if knowledge system is available."""
        return self._kb is not None
    
    def query(self, question: str) -> Optional[NinaFact]:
        """
        Query the knowledge base.
        
        This delegates to adan's KnowledgeBase.query() which implements
        the 5-tier kinematic semantics:
            0. STORE: Shared knowledge store
            1. SHAPE: Kinematic query parsing
            2. SEMANTIC: Datamuse semantic field resolution
            3. KEYWORD: Traditional pattern matching
            4. EMBEDDING: Vector search (if available)
        
        Returns:
            NinaFact if found, None otherwise
        """
        self.queries += 1
        
        if not self._kb:
            return None
        
        result = self._kb.query(question)
        
        if result:
            self.hits += 1
            # Determine which tier hit
            tier = "keyword"  # Default
            if hasattr(self._kb, 'store_hits') and self._kb.store_hits > 0:
                tier = "store"
            elif hasattr(self._kb, 'shape_hits') and self._kb.shape_hits > 0:
                tier = "shape"
            elif hasattr(self._kb, 'semantic_hits') and self._kb.semantic_hits > 0:
                tier = "semantic"
            
            return NinaFact.from_verified_fact(result, tier)
        
        return None
    
    def parse_query(self, question: str) -> Optional['AdanParsedQuery']:
        """
        Parse a query into its kinematic shape.
        
        Returns the adan ParsedQuery with shape, slot, and confidence.
        """
        if not self._parser:
            return None
        
        return self._parser.parse(question)
    
    def _normalize_country(self, country: str) -> str:
        """Normalize country name for lookup."""
        country_lower = country.lower().strip()
        # Remove common articles and prepositions that parser might capture
        prefixes = [
            "the ", "a ", "an ",           # articles
            "of ", "of the ", "for ",      # prepositions
            "in ", "in the ",              # prepositions
            "from ", "from the ",          # prepositions
        ]
        for prefix in prefixes:
            if country_lower.startswith(prefix):
                country_lower = country_lower[len(prefix):]
        return country_lower.strip()
    
    def get_capital(self, country: str) -> Optional[str]:
        """Direct lookup: Get capital of a country."""
        if not HAS_KB:
            return None
        country_lower = self._normalize_country(country)
        return COUNTRY_CAPITALS.get(country_lower)
    
    def get_population(self, country: str) -> Optional[Tuple[int, int]]:
        """Direct lookup: Get population of a country."""
        if not HAS_KB:
            return None
        country_lower = self._normalize_country(country)
        return COUNTRY_POPULATIONS.get(country_lower)
    
    def get_language(self, country: str) -> Optional[List[str]]:
        """Direct lookup: Get languages of a country."""
        if not HAS_KB:
            return None
        country_lower = self._normalize_country(country)
        return COUNTRY_LANGUAGES.get(country_lower)
    
    def get_currency(self, country: str) -> Optional[Tuple[str, str]]:
        """Direct lookup: Get currency of a country."""
        if not HAS_KB:
            return None
        country_lower = self._normalize_country(country)
        return COUNTRY_CURRENCIES.get(country_lower)
    
    def get_constant(self, name: str) -> Optional[Dict[str, Any]]:
        """Direct lookup: Get scientific constant."""
        if not HAS_KB:
            return None
        name_lower = name.lower().strip()
        return SCIENTIFIC_CONSTANTS.get(name_lower)
    
    def get_element(self, name: str) -> Optional[Tuple]:
        """Direct lookup: Get element info from periodic table."""
        if not HAS_KB:
            return None
        name_lower = name.lower().strip()
        return PERIODIC_TABLE.get(name_lower)
    
    def get_company(self, name: str) -> Optional[Dict[str, Any]]:
        """Direct lookup: Get company info."""
        if not HAS_KB:
            return None
        name_lower = name.lower().strip()
        return COMPANY_FACTS.get(name_lower)
    
    def get_acronym(self, acronym: str) -> Optional[Tuple[str, str]]:
        """Direct lookup: Get acronym expansion."""
        if not HAS_KB:
            return None
        acronym_lower = acronym.lower().strip()
        return ACRONYMS.get(acronym_lower)
    
    def add_fact(
        self,
        key: str,
        fact: str,
        category: str,
        source: str = "user",
        source_url: str = "",
        confidence: float = 0.8
    ) -> bool:
        """
        Add a fact to the shared knowledge store.
        
        This persists across restarts and is shared with Adanpedia.
        """
        if not self._store:
            return False
        
        try:
            self._store.add(
                key=key,
                fact=fact,
                category=category,
                source=source,
                source_url=source_url,
                confidence=confidence,
                added_by="nina"
            )
            return True
        except Exception as e:
            print(f"[NINA] Failed to add fact: {e}")
            return False
    
    def search_store(self, query: str, limit: int = 10) -> List['StoredFact']:
        """
        Search the knowledge store.
        
        Uses fuzzy matching to find relevant facts.
        """
        if not self._store:
            return []
        
        return self._store.search(query, limit=limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge system statistics."""
        stats = {
            "nina_queries": self.queries,
            "nina_hits": self.hits,
            "hit_rate": round(self.hits / max(1, self.queries), 3),
            "available": self.is_available
        }
        
        if self._kb:
            stats.update({
                "kb_queries": self._kb.queries,
                "kb_hits": self._kb.hits,
                "kb_store_hits": getattr(self._kb, 'store_hits', 0),
                "kb_shape_hits": getattr(self._kb, 'shape_hits', 0),
                "kb_semantic_hits": getattr(self._kb, 'semantic_hits', 0),
                "kb_keyword_hits": getattr(self._kb, 'keyword_hits', 0),
            })
        
        if self._store:
            stats["store_count"] = self._store.count()
        
        return stats


# Global instance
_nina_knowledge: Optional[NinaKnowledge] = None

def get_nina_knowledge() -> NinaKnowledge:
    """Get the global Nina knowledge instance."""
    global _nina_knowledge
    if _nina_knowledge is None:
        _nina_knowledge = NinaKnowledge()
    return _nina_knowledge


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("NINA KNOWLEDGE INTEGRATION TEST")
    print("Bridging to adan_portable's verified KB")
    print("=" * 70)
    
    knowledge = NinaKnowledge()
    
    print(f"\n📚 Knowledge system available: {knowledge.is_available}")
    
    if not knowledge.is_available:
        print("❌ Cannot run tests - adan_portable KB not available")
        sys.exit(1)
    
    # Test queries
    test_questions = [
        "What is the capital of France?",
        "What is the population of Japan?",
        "Who founded Apple?",
        "What does DNA stand for?",
        "What is the speed of light?",
    ]
    
    print("\n🔍 Testing queries:")
    for q in test_questions:
        result = knowledge.query(q)
        if result:
            print(f"\n❓ {q}")
            print(f"   ✅ {result.fact_text}")
            print(f"   📁 {result.category} | Tier: {result.query_tier}")
        else:
            print(f"\n❓ {q}")
            print(f"   ❌ No match")
    
    # Test direct lookups
    print("\n🎯 Direct lookups:")
    print(f"   Capital of Germany: {knowledge.get_capital('germany')}")
    print(f"   Population of USA: {knowledge.get_population('usa')}")
    print(f"   Languages of India: {knowledge.get_language('india')}")
    
    # Stats
    print(f"\n📊 Stats: {knowledge.get_stats()}")
