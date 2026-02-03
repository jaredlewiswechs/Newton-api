#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
KINEMATIC QUERY PARSER
Questions are incomplete equations seeking their terminus.

The question HAS shape. The KB HAS shape. Match shapes, fill slots.
═══════════════════════════════════════════════════════════════════════════════

Input is ALWAYS a query:
  - "capital of France"     →  seeking CAPITALS[France]
  - "who founded Apple"     →  seeking COMPANIES[Apple].founders
  - "The earth is flat"     →  verifying against FACTS
  - "H2O"                   →  lookup or verify FORMULAS[H2O]

The pattern IS the path. The slot IS the coordinate. The KB IS the space.
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
import re


class QueryShape(Enum):
    """The geometric shape of a query - what it's seeking."""
    
    # Lookup shapes (seeking a value)
    CAPITAL_OF = "capital_of"           # capital(X) = ?
    POPULATION_OF = "population_of"     # population(X) = ?
    LANGUAGE_OF = "language_of"         # language(X) = ?
    CURRENCY_OF = "currency_of"         # currency(X) = ?
    
    FOUNDER_OF = "founder_of"           # founder(X) = ?
    FOUNDED_WHEN = "founded_when"       # founded_year(X) = ?
    HEADQUARTERS_OF = "headquarters_of" # hq(X) = ?
    
    ELEMENT_INFO = "element_info"       # element(X) = ?
    ATOMIC_NUMBER = "atomic_number"     # atomic_num(X) = ?
    ELEMENT_SYMBOL = "element_symbol"   # symbol(X) = ?
    
    ACRONYM_EXPANSION = "acronym_expansion"  # expand(X) = ?
    FORMULA_MEANING = "formula_meaning"      # meaning(X) = ?
    
    CONSTANT_VALUE = "constant_value"   # constant(X) = ?
    HISTORICAL_DATE = "historical_date" # date(X) = ?
    
    PHYSICS_LAW = "physics_law"         # law(X) = ?
    MATH_NOTATION = "math_notation"     # notation(X) = ?
    BIOLOGY_FACT = "biology_fact"       # bio(X) = ?
    SI_UNIT = "si_unit"                 # unit(X) = ?
    
    # Verification shapes (checking a claim)
    VERIFY_FACT = "verify_fact"         # verify(statement) = bool
    
    # Unknown - needs LLM or broader search
    UNKNOWN = "unknown"


@dataclass
class ParsedQuery:
    """A query parsed into its kinematic components."""
    original: str
    shape: QueryShape
    slot: Optional[str]           # The variable being queried
    slot_secondary: Optional[str] # Sometimes need two slots
    confidence: float             # How confident in this parse
    pattern_matched: str          # Which pattern matched
    
    def to_dict(self) -> Dict:
        return {
            "original": self.original,
            "shape": self.shape.value,
            "slot": self.slot,
            "confidence": self.confidence,
            "pattern": self.pattern_matched,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY PATTERNS
# Each pattern maps to a KB shape
# ═══════════════════════════════════════════════════════════════════════════════

# Pattern: (regex, QueryShape, slot_group_index, confidence)
QUERY_PATTERNS: List[Tuple[str, QueryShape, int, float]] = [
    # === CAPITALS ===
    # Note: (?:the )? after of/for to not capture articles in country name
    (r"(?:what(?:'s| is) )?(?:the )?capital (?:of |for )?(?:the )?(.+?)(?:\?)?$", QueryShape.CAPITAL_OF, 1, 0.95),
    (r"(.+?)(?:'s| 's) capital(?:\?)?$", QueryShape.CAPITAL_OF, 1, 0.90),
    (r"capital (?:city )?(?:of )?(?:the )?(.+?)(?:\?)?$", QueryShape.CAPITAL_OF, 1, 0.85),
    
    # === POPULATION ===
    (r"(?:what(?:'s| is) )?(?:the )?population (?:of |for )?(?:the )?(.+?)(?:\?)?$", QueryShape.POPULATION_OF, 1, 0.95),
    (r"how many people (?:live |are )?in (?:the )?(.+?)(?:\?)?$", QueryShape.POPULATION_OF, 1, 0.90),
    
    # === LANGUAGE ===
    (r"(?:what )?language(?:s)? (?:do they |does |is )?(?:speak |spoken )?(?:in )?(.+?)(?:\?)?$", QueryShape.LANGUAGE_OF, 1, 0.90),
    (r"(?:what )?(?:do they |does )?speak in (.+?)(?:\?)?$", QueryShape.LANGUAGE_OF, 1, 0.85),
    
    # === CURRENCY ===
    (r"(?:what(?:'s| is) )?(?:the )?currency (?:of |in |for )?(.+?)(?:\?)?$", QueryShape.CURRENCY_OF, 1, 0.95),
    
    # === FOUNDERS ===
    (r"who (?:founded|started|created|built) (.+?)(?:\?)?$", QueryShape.FOUNDER_OF, 1, 0.95),
    (r"(?:who(?:'s| is| are) )?(?:the )?founders? (?:of )?(.+?)(?:\?)?$", QueryShape.FOUNDER_OF, 1, 0.90),
    (r"(.+?) (?:was )?founded by(?:\?)?$", QueryShape.FOUNDER_OF, 1, 0.80),
    
    # === FOUNDED WHEN ===
    (r"when was (.+?) (?:founded|started|created)(?:\?)?$", QueryShape.FOUNDED_WHEN, 1, 0.95),
    (r"(?:what )?year (?:was )?(.+?) (?:founded|started|created)(?:\?)?$", QueryShape.FOUNDED_WHEN, 1, 0.90),
    (r"(.+?) (?:was )?(?:founded|created) (?:in |when)(?:\?)?$", QueryShape.FOUNDED_WHEN, 1, 0.80),
    
    # === HEADQUARTERS ===
    (r"where (?:is|are) (.+?) (?:headquartered|located|based)(?:\?)?$", QueryShape.HEADQUARTERS_OF, 1, 0.95),
    (r"(?:what(?:'s| is) )?(?:the )?headquarters (?:of )?(.+?)(?:\?)?$", QueryShape.HEADQUARTERS_OF, 1, 0.90),
    
    # === ELEMENTS ===
    (r"(?:what(?:'s| is) )?(?:the )?atomic number (?:of |for )?(.+?)(?:\?)?$", QueryShape.ATOMIC_NUMBER, 1, 0.95),
    (r"(?:what )?element (?:has |is )?(?:the )?symbol (.+?)(?:\?)?$", QueryShape.ELEMENT_SYMBOL, 1, 0.95),
    (r"(?:tell me about |what is |info (?:on |about )?)(?:the element )?(.+?)(?:\?)?$", QueryShape.ELEMENT_INFO, 1, 0.70),
    
    # === ACRONYMS ===
    (r"what does (.+?) stand for(?:\?)?$", QueryShape.ACRONYM_EXPANSION, 1, 0.95),
    (r"(?:what(?:'s| is) )?(.+?) (?:stand for|mean|acronym)(?:\?)?$", QueryShape.ACRONYM_EXPANSION, 1, 0.85),
    (r"(?:define |meaning of )(.+?)(?:\?)?$", QueryShape.ACRONYM_EXPANSION, 1, 0.70),
    
    # === CHEMICAL FORMULAS ===
    (r"(?:what does |explain |what is )?(h2o|co2|nacl|h2so4|ch4|nh3|c6h12o6)(?:\?)?$", QueryShape.FORMULA_MEANING, 1, 0.95),
    (r"(?:what does |what is )?(?:the )?(?:formula |molecule )(.+?) (?:mean|represent)(?:\?)?$", QueryShape.FORMULA_MEANING, 1, 0.85),
    
    # === CONSTANTS ===
    (r"(?:what(?:'s| is) )?(?:the )?(speed of light|gravitational constant|planck|avogadro|pi|e)(?:\?)?$", QueryShape.CONSTANT_VALUE, 1, 0.95),
    (r"(?:value of |what is )(pi|e|c|g|h)(?:\?)?$", QueryShape.CONSTANT_VALUE, 1, 0.90),
    
    # === HISTORICAL ===
    (r"when was (.+?) (?:created|invented|discovered|released|founded)(?:\?)?$", QueryShape.HISTORICAL_DATE, 1, 0.90),
    (r"(?:what )?year (?:was |did )(.+?)(?:\?)?$", QueryShape.HISTORICAL_DATE, 1, 0.80),
    
    # === PHYSICS ===
    (r"(?:what(?:'s| is) )?(?:newton(?:'s)? )?(first|second|third) law(?:\?)?$", QueryShape.PHYSICS_LAW, 1, 0.95),
    (r"(?:what(?:'s| is) )?(ohm(?:'s)?|coulomb(?:'s)?|newton(?:'s)?) law(?:\?)?$", QueryShape.PHYSICS_LAW, 1, 0.95),
    (r"(?:what(?:'s| is) )?(kinetic energy|potential energy|momentum|f=ma)(?:\?)?$", QueryShape.PHYSICS_LAW, 1, 0.90),
    
    # === MATH ===
    (r"(?:what(?:'s| is) )?(?:the )?(derivative|integral|quadratic formula|pythagorean)(?:\?)?$", QueryShape.MATH_NOTATION, 1, 0.90),
    (r"(?:what does )?(sigma|delta|pi|sum|integral)(?: mean| symbol)?(?:\?)?$", QueryShape.MATH_NOTATION, 1, 0.85),
    
    # === BIOLOGY ===
    (r"(?:what(?:'s| is) )?(?:the )?(mitochondria|nucleus|ribosome|chloroplast|photosynthesis|dna replication)(?:\?)?$", QueryShape.BIOLOGY_FACT, 1, 0.90),
    (r"(?:what(?:'s| is) )?(powerhouse of the cell)(?:\?)?$", QueryShape.BIOLOGY_FACT, 1, 0.95),
    
    # === SI UNITS ===
    (r"(?:what(?:'s| is) )?(?:a |the )?(joule|newton|watt|pascal|hertz|volt|ampere|meter|kilogram|second)(?:\?)?$", QueryShape.SI_UNIT, 1, 0.90),
    (r"(?:what does )?(?:the )?prefix (kilo|mega|giga|tera|milli|micro|nano) mean(?:\?)?$", QueryShape.SI_UNIT, 1, 0.90),
]


class KinematicQueryParser:
    """
    Parse queries into their kinematic shape.
    
    A query is an incomplete equation. This finds:
    - The SHAPE (what kind of lookup/verification)
    - The SLOT (the variable to fill)
    - The PATH (which KB structure to traverse)
    """
    
    def __init__(self):
        # Compile patterns for efficiency
        self._compiled = [(re.compile(p, re.IGNORECASE), shape, group, conf) 
                          for p, shape, group, conf in QUERY_PATTERNS]
    
    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a query into its kinematic components.
        
        Returns the shape, slot, and confidence of the parse.
        """
        query_clean = query.strip().lower()
        
        # Try each pattern
        for pattern, shape, group, confidence in self._compiled:
            match = pattern.search(query_clean)
            if match:
                slot = match.group(group).strip() if group <= len(match.groups()) else None
                return ParsedQuery(
                    original=query,
                    shape=shape,
                    slot=slot,
                    slot_secondary=None,
                    confidence=confidence,
                    pattern_matched=pattern.pattern,
                )
        
        # No pattern matched - unknown shape
        # But extract potential slot (nouns) for verification queries
        return ParsedQuery(
            original=query,
            shape=QueryShape.UNKNOWN,
            slot=self._extract_potential_slot(query_clean),
            slot_secondary=None,
            confidence=0.0,
            pattern_matched="",
        )
    
    def _extract_potential_slot(self, query: str) -> Optional[str]:
        """Extract potential slot from unknown query."""
        # Remove common words, keep nouns/proper nouns
        stop_words = {'what', 'is', 'the', 'a', 'an', 'of', 'for', 'in', 'to', 
                      'how', 'when', 'where', 'who', 'why', 'does', 'do', 'did',
                      'can', 'could', 'would', 'should', 'will', 'are', 'was', 'were'}
        words = [w for w in re.findall(r'\b\w+\b', query) if w not in stop_words]
        return ' '.join(words) if words else None
    
    def get_kb_path(self, parsed: ParsedQuery) -> Optional[str]:
        """
        Get the KB path for a parsed query.
        Returns the dictionary/function name to query.
        """
        shape_to_kb = {
            QueryShape.CAPITAL_OF: "COUNTRY_CAPITALS",
            QueryShape.POPULATION_OF: "COUNTRY_POPULATIONS",
            QueryShape.LANGUAGE_OF: "COUNTRY_LANGUAGES",
            QueryShape.CURRENCY_OF: "COUNTRY_CURRENCIES",
            QueryShape.FOUNDER_OF: "COMPANY_FACTS.founders",
            QueryShape.FOUNDED_WHEN: "COMPANY_FACTS.founded",
            QueryShape.HEADQUARTERS_OF: "COMPANY_FACTS.headquarters",
            QueryShape.ELEMENT_INFO: "PERIODIC_TABLE",
            QueryShape.ATOMIC_NUMBER: "PERIODIC_TABLE.atomic_num",
            QueryShape.ELEMENT_SYMBOL: "ELEMENT_SYMBOLS",
            QueryShape.ACRONYM_EXPANSION: "ACRONYMS",
            QueryShape.FORMULA_MEANING: "CHEMICAL_NOTATION",
            QueryShape.CONSTANT_VALUE: "SCIENTIFIC_CONSTANTS",
            QueryShape.HISTORICAL_DATE: "HISTORICAL_DATES",
            QueryShape.PHYSICS_LAW: "PHYSICS_LAWS",
            QueryShape.MATH_NOTATION: "MATH_NOTATION",
            QueryShape.BIOLOGY_FACT: "BIOLOGY_FACTS",
            QueryShape.SI_UNIT: "SI_UNITS",
        }
        return shape_to_kb.get(parsed.shape)


# Global instance
_parser: Optional[KinematicQueryParser] = None

def get_query_parser() -> KinematicQueryParser:
    global _parser
    if _parser is None:
        _parser = KinematicQueryParser()
    return _parser


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = KinematicQueryParser()
    
    test_queries = [
        # Capitals
        "What is the capital of France?",
        "capital of Japan",
        "Germany's capital",
        
        # Founders
        "Who founded Apple?",
        "founders of Google",
        
        # Elements
        "atomic number of carbon",
        "element with symbol Au",
        
        # Acronyms
        "What does DNA stand for?",
        "API meaning",
        
        # Formulas
        "what does H2O mean",
        "explain CO2",
        
        # Physics
        "Newton's first law",
        "what is Ohm's law",
        
        # Unknown (should fallback)
        "What city does France govern from?",
        "tell me something interesting",
    ]
    
    print("=" * 70)
    print("KINEMATIC QUERY PARSER TEST")
    print("Questions are incomplete equations seeking terminus")
    print("=" * 70)
    
    for q in test_queries:
        parsed = parser.parse(q)
        kb_path = parser.get_kb_path(parsed)
        
        print(f"\n❓ {q}")
        print(f"   Shape: {parsed.shape.value}")
        print(f"   Slot:  {parsed.slot}")
        print(f"   KB:    {kb_path or 'UNKNOWN'}")
        print(f"   Conf:  {parsed.confidence:.2f}")
