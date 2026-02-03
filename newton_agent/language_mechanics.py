#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
LANGUAGE MECHANICS
Synonyms, Antonyms, Typo Correction - Language as Trajectory Algebra

Synonyms  = Same trajectory, different parameterization (t → t')
Antonyms  = Inverse trajectory (f → 1/f, or trajectory reversal)
Typos     = Small perturbations from intended trajectory (error correction)
Thesaurus = The manifold of meaning-equivalent paths

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, List, Set, Optional, Tuple
import re
from difflib import SequenceMatcher, get_close_matches


# ═══════════════════════════════════════════════════════════════════════════════
# SYNONYM GROUPS (Same meaning, different surface form)
# These are trajectories through the same semantic point
# ═══════════════════════════════════════════════════════════════════════════════

SYNONYM_GROUPS: Dict[str, Set[str]] = {
    # Question words (intent detection)
    "who": {"who", "whom", "founder", "creator", "inventor", "author", "made by", "created by", "founded by"},
    "what": {"what", "which", "define", "meaning of", "definition"},
    "when": {"when", "what year", "what date", "what time", "year of", "date of"},
    "where": {"where", "location", "place", "located", "headquarters", "based in", "situated"},
    "why": {"why", "reason", "cause", "because", "how come"},
    "how": {"how", "method", "way to", "process", "steps to"},
    
    # Verbs of creation
    "create": {"create", "created", "make", "made", "build", "built", "found", "founded", 
               "establish", "established", "invent", "invented", "develop", "developed",
               "start", "started", "begin", "began", "launch", "launched"},
    
    # Verbs of location
    "locate": {"locate", "located", "based", "headquartered", "situated", "found in", "in"},
    
    # Time references
    "year": {"year", "date", "time", "when", "era", "period"},
    
    # Geography
    "capital": {"capital", "capital city", "seat of government", "main city"},
    "country": {"country", "nation", "state", "land"},
    "city": {"city", "town", "municipality", "metro", "urban area"},
    
    # Science
    "speed": {"speed", "velocity", "rate", "pace"},
    "constant": {"constant", "value", "number", "coefficient"},
    
    # Business
    "company": {"company", "corporation", "firm", "business", "enterprise", "organization", "org"},
    "founder": {"founder", "founders", "co-founder", "creator", "started by", "founded by"},
    "ceo": {"ceo", "chief executive", "head", "leader", "president"},
    
    # Common nouns
    "person": {"person", "individual", "someone", "one", "human"},
    "thing": {"thing", "object", "item", "entity"},
}

# Build reverse lookup: word -> canonical form
WORD_TO_CANONICAL: Dict[str, str] = {}
for canonical, synonyms in SYNONYM_GROUPS.items():
    for syn in synonyms:
        WORD_TO_CANONICAL[syn.lower()] = canonical


# ═══════════════════════════════════════════════════════════════════════════════
# ANTONYM PAIRS (Inverse trajectories)
# If A → B, then antonym(A) → ¬B (constraint inversion)
# ═══════════════════════════════════════════════════════════════════════════════

ANTONYM_PAIRS: List[Tuple[str, str]] = [
    # Boolean pairs
    ("true", "false"),
    ("yes", "no"),
    ("on", "off"),
    ("open", "closed"),
    ("start", "stop"),
    ("begin", "end"),
    ("first", "last"),
    
    # Directional
    ("up", "down"),
    ("left", "right"),
    ("north", "south"),
    ("east", "west"),
    ("in", "out"),
    ("inside", "outside"),
    ("above", "below"),
    ("over", "under"),
    ("before", "after"),
    ("forward", "backward"),
    
    # Magnitude
    ("big", "small"),
    ("large", "tiny"),
    ("high", "low"),
    ("fast", "slow"),
    ("hot", "cold"),
    ("heavy", "light"),
    ("loud", "quiet"),
    ("bright", "dark"),
    ("full", "empty"),
    ("more", "less"),
    ("many", "few"),
    ("all", "none"),
    ("always", "never"),
    
    # Quality
    ("good", "bad"),
    ("right", "wrong"),
    ("correct", "incorrect"),
    ("valid", "invalid"),
    ("true", "false"),
    ("positive", "negative"),
    ("success", "failure"),
    
    # State
    ("alive", "dead"),
    ("new", "old"),
    ("young", "old"),
    ("create", "destroy"),
    ("build", "demolish"),
    ("increase", "decrease"),
    ("rise", "fall"),
    ("grow", "shrink"),
]

# Build bidirectional antonym lookup
ANTONYMS: Dict[str, str] = {}
for a, b in ANTONYM_PAIRS:
    ANTONYMS[a] = b
    ANTONYMS[b] = a


# ═══════════════════════════════════════════════════════════════════════════════
# COMMON MISSPELLINGS (Typo correction)
# Small perturbations from the intended trajectory
# ═══════════════════════════════════════════════════════════════════════════════

COMMON_MISSPELLINGS: Dict[str, str] = {
    # Countries
    "frace": "france",
    "frnace": "france",
    "frannce": "france",
    "farnce": "france",
    "franec": "france",
    "germnay": "germany",
    "germeny": "germany",
    "austrailia": "australia",
    "australa": "australia",
    "britian": "britain",
    "brittain": "britain",
    "untied states": "united states",
    "unites states": "united states",
    "amercia": "america",
    "amrica": "america",
    "canad": "canada",
    "cananda": "canada",
    "japn": "japan",
    "japen": "japan",
    "chian": "china",
    "cina": "china",
    "russa": "russia",
    "russi": "russia",
    "brazl": "brazil",
    "braizl": "brazil",
    "mexco": "mexico",
    "meixco": "mexico",
    
    # Cities
    "paris": "paris",  # Already correct, but common
    "parsi": "paris",
    "tokoy": "tokyo",
    "tokoyo": "tokyo",
    "berln": "berlin",
    "londno": "london",
    "londn": "london",
    
    # Tech companies
    "googel": "google",
    "gogle": "google",
    "gooogle": "google",
    "mircosoft": "microsoft",
    "microsft": "microsoft",
    "mircrosoft": "microsoft",
    "aple": "apple",
    "appel": "apple",
    "amzon": "amazon",
    "amazn": "amazon",
    "tesle": "tesla",
    "telsa": "tesla",
    "facebok": "facebook",
    "facbook": "facebook",
    
    # Common words
    "teh": "the",
    "hte": "the",
    "adn": "and",
    "nad": "and",
    "taht": "that",
    "wiht": "with",
    "whta": "what",
    "waht": "what",
    "wat": "what",
    "wut": "what",
    "whats": "what is",
    "iz": "is",
    "iss": "is",
    "si": "is",
    "wehn": "when",
    "whn": "when",
    "hwo": "who",
    "woh": "who",
    "whre": "where",
    "wher": "where",
    "capitl": "capital",
    "captial": "capital",
    "captal": "capital",
    "captiol": "capital",
    "becuase": "because",
    "beacuse": "because",
    "recieve": "receive",
    "reciept": "receipt",
    "definately": "definitely",
    "seperately": "separately",
    "occured": "occurred",
    "occurance": "occurrence",
    
    # Science
    "plank": "planck",
    "planc": "planck",
    "avagadro": "avogadro",
    "avogrado": "avogadro",
    "boltzman": "boltzmann",
    "boltmann": "boltzmann",
    "gravitaional": "gravitational",
    "gravatational": "gravitational",
    
    # Programming
    "pyhton": "python",
    "pythn": "python",
    "pythno": "python",
    "javasript": "javascript",
    "javascirpt": "javascript",
    "javscript": "javascript",
}


# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE MECHANICS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class LanguageMechanics:
    """
    Language mechanics engine for query normalization and understanding.
    
    Treats language as trajectory algebra:
    - Synonyms: same point in meaning space
    - Antonyms: inverse/negation
    - Typos: perturbation correction
    """
    
    def __init__(self):
        self.corrections_made = 0
        self.synonyms_expanded = 0
    
    def correct_typos(self, text: str) -> Tuple[str, List[str]]:
        """
        Correct common typos in text.
        Returns (corrected_text, list_of_corrections).
        """
        corrections = []
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            clean_word = word.strip('?.,!;:')
            
            # Check direct misspelling lookup
            if clean_word in COMMON_MISSPELLINGS:
                correction = COMMON_MISSPELLINGS[clean_word]
                if correction != clean_word:
                    corrections.append(f"{clean_word} → {correction}")
                    self.corrections_made += 1
                # Preserve original punctuation
                corrected = word.replace(clean_word, correction)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words), corrections
    
    def fuzzy_match(self, word: str, candidates: List[str], threshold: float = 0.8) -> Optional[str]:
        """
        Find best fuzzy match for a word among candidates.
        Uses sequence matching for edit distance approximation.
        """
        word_lower = word.lower()
        matches = get_close_matches(word_lower, candidates, n=1, cutoff=threshold)
        return matches[0] if matches else None
    
    def get_synonyms(self, word: str) -> Set[str]:
        """Get all synonyms for a word."""
        word_lower = word.lower()
        
        # Find canonical form
        canonical = WORD_TO_CANONICAL.get(word_lower)
        if canonical:
            return SYNONYM_GROUPS.get(canonical, {word_lower})
        
        # Check if word is itself a canonical form
        if word_lower in SYNONYM_GROUPS:
            return SYNONYM_GROUPS[word_lower]
        
        return {word_lower}
    
    def get_antonym(self, word: str) -> Optional[str]:
        """Get antonym for a word (trajectory inversion)."""
        return ANTONYMS.get(word.lower())
    
    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with synonym variations.
        Returns list of equivalent queries.
        """
        variations = [query]
        query_lower = query.lower()
        
        # Find words that have synonyms
        for canonical, synonyms in SYNONYM_GROUPS.items():
            for syn in synonyms:
                if syn in query_lower and syn != canonical:
                    # Create variation with canonical form
                    variation = query_lower.replace(syn, canonical)
                    if variation not in variations:
                        variations.append(variation)
                        self.synonyms_expanded += 1
        
        return variations
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize a query for better matching:
        1. Fix typos
        2. Expand common patterns
        3. Standardize phrasing
        """
        # Step 1: Fix typos
        corrected, _ = self.correct_typos(query)
        
        # Step 2: Normalize question patterns
        normalized = corrected.lower().strip()
        
        # "founder of X" → "who founded X"
        normalized = re.sub(r'\bfounder of (\w+)', r'who founded \1', normalized)
        normalized = re.sub(r'\bfounders of (\w+)', r'who founded \1', normalized)
        normalized = re.sub(r'\bcreator of (\w+)', r'who created \1', normalized)
        
        # "X's capital" → "capital of X"
        normalized = re.sub(r"(\w+)'s capital", r'capital of \1', normalized)
        
        # "located in" → "where is"
        normalized = re.sub(r'where is (\w+) located', r'where is \1', normalized)
        
        # "what year did X" → "when did X"
        normalized = re.sub(r'what year did', 'when did', normalized)
        normalized = re.sub(r'what year was', 'when was', normalized)
        
        return normalized
    
    def detect_intent(self, query: str) -> Dict[str, any]:
        """
        Detect the intent/type of query.
        Returns dict with intent classification.
        """
        query_lower = query.lower()
        
        # Check for question word synonyms
        intent = {
            "type": "unknown",
            "entity_type": None,
            "action": None,
        }
        
        # WHO questions
        who_words = SYNONYM_GROUPS.get("who", set())
        if any(w in query_lower for w in who_words):
            intent["type"] = "who"
            intent["entity_type"] = "person"
            
        # WHEN questions  
        when_words = SYNONYM_GROUPS.get("when", set())
        if any(w in query_lower for w in when_words):
            intent["type"] = "when"
            intent["entity_type"] = "time"
            
        # WHERE questions
        where_words = SYNONYM_GROUPS.get("where", set())
        if any(w in query_lower for w in where_words):
            intent["type"] = "where"
            intent["entity_type"] = "location"
            
        # WHAT questions
        what_words = SYNONYM_GROUPS.get("what", set())
        if any(w in query_lower for w in what_words):
            intent["type"] = "what"
            
        # Detect action verbs
        create_words = SYNONYM_GROUPS.get("create", set())
        if any(w in query_lower for w in create_words):
            intent["action"] = "create"
            
        return intent
    
    def get_stats(self) -> Dict:
        return {
            "corrections_made": self.corrections_made,
            "synonyms_expanded": self.synonyms_expanded,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_language_mechanics: Optional[LanguageMechanics] = None

def get_language_mechanics() -> LanguageMechanics:
    global _language_mechanics
    if _language_mechanics is None:
        _language_mechanics = LanguageMechanics()
    return _language_mechanics


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    lm = LanguageMechanics()
    
    print("=" * 60)
    print("LANGUAGE MECHANICS TEST")
    print("Language IS trajectory algebra")
    print("=" * 60)
    
    # Typo correction
    print("\n📝 TYPO CORRECTION (Perturbation → Correction)")
    typo_tests = [
        "What is the capital of Frace?",
        "Who founded Googel?",
        "Waht is teh speed of light?",
        "When was Pyhton created?",
    ]
    for test in typo_tests:
        corrected, corrections = lm.correct_typos(test)
        print(f"  '{test}'")
        print(f"  → '{corrected}'")
        if corrections:
            print(f"     Fixed: {corrections}")
    
    # Query normalization
    print("\n🔄 QUERY NORMALIZATION")
    norm_tests = [
        "founder of Apple",
        "France's capital",
        "what year was Python created",
        "creator of Microsoft",
    ]
    for test in norm_tests:
        normalized = lm.normalize_query(test)
        print(f"  '{test}' → '{normalized}'")
    
    # Synonyms
    print("\n📚 SYNONYMS (Same trajectory, different form)")
    syn_tests = ["create", "who", "capital", "company"]
    for test in syn_tests:
        syns = lm.get_synonyms(test)
        print(f"  '{test}' ≡ {syns}")
    
    # Antonyms
    print("\n⟺ ANTONYMS (Inverse trajectory)")
    ant_tests = ["true", "up", "fast", "create", "open"]
    for test in ant_tests:
        ant = lm.get_antonym(test)
        print(f"  '{test}' ↔ '{ant}'")
    
    # Intent detection
    print("\n🎯 INTENT DETECTION")
    intent_tests = [
        "Who founded Google?",
        "When was Python created?",
        "Where is Apple headquartered?",
        "What is the speed of light?",
    ]
    for test in intent_tests:
        intent = lm.detect_intent(test)
        print(f"  '{test}' → {intent}")
    
    print(f"\n📊 Stats: {lm.get_stats()}")
