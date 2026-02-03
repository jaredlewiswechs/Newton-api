#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
VERIFIED KNOWLEDGE BASE
Pre-verified facts from authoritative sources (CIA World Factbook, etc.)
═══════════════════════════════════════════════════════════════════════════════

These facts are considered GROUND TRUTH - no LLM needed.
Source: CIA World Factbook, ISO standards, official government data.

Search Strategy (Three-Tier Kinematic Semantics):
1. SHAPE: Kinematic query parsing (~0ms) - questions as equations
2. SEMANTIC: Datamuse semantic field resolution (~200ms) - when patterns miss
3. KEYWORD: Traditional keyword matching (~1ms) - fallback
4. EMBEDDING: Vector search (~100ms) - last resort

"The question has shape. The KB has shape. Match shapes, fill slots."
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import re

# Import language mechanics for typo correction and query normalization
try:
    from .language_mechanics import get_language_mechanics
    HAS_LANGUAGE_MECHANICS = True
except ImportError:
    HAS_LANGUAGE_MECHANICS = False

# Import kinematic query parser (shape-based)
try:
    from .query_parser import get_query_parser, QueryShape, ParsedQuery
    HAS_QUERY_PARSER = True
except ImportError:
    HAS_QUERY_PARSER = False

# Import semantic resolver (Datamuse API)
try:
    from .semantic_resolver import SemanticResolver
    HAS_SEMANTIC_RESOLVER = True
except ImportError:
    HAS_SEMANTIC_RESOLVER = False

# Import embeddings for semantic search fallback
try:
    from .embeddings import get_embedding_engine, SemanticMatch
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False


@dataclass
class VerifiedFact:
    """A pre-verified fact with provenance."""
    fact: str
    category: str
    source: str
    source_url: str
    confidence: float = 1.0  # 1.0 = absolute certainty
    
    def to_dict(self) -> Dict:
        return {
            "fact": self.fact,
            "category": self.category,
            "source": self.source,
            "source_url": self.source_url,
            "confidence": self.confidence,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CIA WORLD FACTBOOK DATA
# Source: https://www.cia.gov/the-world-factbook/
# ═══════════════════════════════════════════════════════════════════════════════

COUNTRY_CAPITALS: Dict[str, str] = {
    # Major countries
    "france": "Paris",
    "germany": "Berlin",
    "italy": "Rome",
    "spain": "Madrid",
    "portugal": "Lisbon",
    "united kingdom": "London",
    "uk": "London",
    "england": "London",
    "ireland": "Dublin",
    "netherlands": "Amsterdam",
    "belgium": "Brussels",
    "switzerland": "Bern",
    "austria": "Vienna",
    "poland": "Warsaw",
    "czech republic": "Prague",
    "czechia": "Prague",
    "hungary": "Budapest",
    "romania": "Bucharest",
    "bulgaria": "Sofia",
    "greece": "Athens",
    "turkey": "Ankara",
    "russia": "Moscow",
    "ukraine": "Kyiv",
    "sweden": "Stockholm",
    "norway": "Oslo",
    "finland": "Helsinki",
    "denmark": "Copenhagen",
    
    # Americas
    "united states": "Washington, D.C.",
    "usa": "Washington, D.C.",
    "us": "Washington, D.C.",
    "america": "Washington, D.C.",
    "canada": "Ottawa",
    "mexico": "Mexico City",
    "brazil": "Brasília",
    "argentina": "Buenos Aires",
    "chile": "Santiago",
    "colombia": "Bogotá",
    "peru": "Lima",
    "venezuela": "Caracas",
    "cuba": "Havana",
    
    # Asia
    "china": "Beijing",
    "japan": "Tokyo",
    "south korea": "Seoul",
    "korea": "Seoul",
    "north korea": "Pyongyang",
    "india": "New Delhi",
    "pakistan": "Islamabad",
    "bangladesh": "Dhaka",
    "indonesia": "Jakarta",
    "thailand": "Bangkok",
    "vietnam": "Hanoi",
    "philippines": "Manila",
    "malaysia": "Kuala Lumpur",
    "singapore": "Singapore",
    "taiwan": "Taipei",
    
    # Middle East
    "israel": "Jerusalem",
    "saudi arabia": "Riyadh",
    "iran": "Tehran",
    "iraq": "Baghdad",
    "egypt": "Cairo",
    "united arab emirates": "Abu Dhabi",
    "uae": "Abu Dhabi",
    "qatar": "Doha",
    "kuwait": "Kuwait City",
    
    # Africa
    "south africa": "Pretoria",
    "nigeria": "Abuja",
    "kenya": "Nairobi",
    "ethiopia": "Addis Ababa",
    "morocco": "Rabat",
    "algeria": "Algiers",
    "tunisia": "Tunis",
    
    # Oceania
    "australia": "Canberra",
    "new zealand": "Wellington",
}

CONTINENTS: Dict[str, str] = {
    "africa": "Africa is a continent, not a country. It contains 54 undisputed sovereign states.",
    "asia": "Asia is the largest continent, not a country. It contains 48 undisputed sovereign states.",
    "europe": "Europe is a continent, not a country. It contains 44 undisputed sovereign states.",
    "north america": "North America is a continent, not a country. It contains 23 undisputed sovereign states.",
    "south america": "South America is a continent, not a country. It contains 12 undisputed sovereign states.",
    "antarctica": "Antarctica is a continent, not a country. It has no permanent population.",
    "oceania": "Oceania is a geographic region/continent, not a single country.",
}

COUNTRY_POPULATIONS: Dict[str, tuple[int, int]] = {
    # (population, year)
    "china": (1_400_000_000, 2024),
    "india": (1_420_000_000, 2024),
    "united states": (335_000_000, 2024),
    "indonesia": (277_000_000, 2024),
    "pakistan": (240_000_000, 2024),
    "brazil": (216_000_000, 2024),
    "nigeria": (230_000_000, 2024),
    "bangladesh": (173_000_000, 2024),
    "russia": (144_000_000, 2024),
    "japan": (124_000_000, 2024),
    "mexico": (130_000_000, 2024),
    "germany": (84_000_000, 2024),
    "france": (68_000_000, 2024),
    "uk": (67_000_000, 2024),
    "italy": (59_000_000, 2024),
    "canada": (40_000_000, 2024),
    "australia": (26_000_000, 2024),
}

COUNTRY_LANGUAGES: Dict[str, List[str]] = {
    "france": ["French"],
    "germany": ["German"],
    "spain": ["Spanish", "Catalan", "Basque", "Galician"],
    "italy": ["Italian"],
    "japan": ["Japanese"],
    "china": ["Mandarin Chinese"],
    "brazil": ["Portuguese"],
    "russia": ["Russian"],
    "india": ["Hindi", "English"],
    "united states": ["English"],
    "mexico": ["Spanish"],
    "canada": ["English", "French"],
}

COUNTRY_CURRENCIES: Dict[str, tuple[str, str]] = {
    # (currency name, code)
    "united states": ("US Dollar", "USD"),
    "usa": ("US Dollar", "USD"),
    "european union": ("Euro", "EUR"),
    "france": ("Euro", "EUR"),
    "germany": ("Euro", "EUR"),
    "italy": ("Euro", "EUR"),
    "spain": ("Euro", "EUR"),
    "japan": ("Japanese Yen", "JPY"),
    "united kingdom": ("British Pound", "GBP"),
    "uk": ("British Pound", "GBP"),
    "china": ("Chinese Yuan", "CNY"),
    "india": ("Indian Rupee", "INR"),
    "russia": ("Russian Ruble", "RUB"),
    "brazil": ("Brazilian Real", "BRL"),
    "canada": ("Canadian Dollar", "CAD"),
    "australia": ("Australian Dollar", "AUD"),
    "mexico": ("Mexican Peso", "MXN"),
    "south korea": ("South Korean Won", "KRW"),
    "switzerland": ("Swiss Franc", "CHF"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SCIENTIFIC CONSTANTS
# Source: NIST, CODATA
# ═══════════════════════════════════════════════════════════════════════════════

SCIENTIFIC_CONSTANTS: Dict[str, tuple[float, str, str]] = {
    # (value, unit, description)
    "speed of light": (299_792_458, "m/s", "Speed of light in vacuum"),
    "c": (299_792_458, "m/s", "Speed of light in vacuum"),
    "gravitational constant": (6.67430e-11, "m³/(kg·s²)", "Gravitational constant"),
    "g": (9.80665, "m/s²", "Standard gravity"),
    "planck constant": (6.62607015e-34, "J·s", "Planck constant"),
    "planck's constant": (6.62607015e-34, "J·s", "Planck constant"),
    "avogadro number": (6.02214076e23, "mol⁻¹", "Avogadro constant"),
    "avogadro's number": (6.02214076e23, "mol⁻¹", "Avogadro constant"),
    "avogadro constant": (6.02214076e23, "mol⁻¹", "Avogadro constant"),
    "boltzmann constant": (1.380649e-23, "J/K", "Boltzmann constant"),
    "boltzmann's constant": (1.380649e-23, "J/K", "Boltzmann constant"),
    "electron mass": (9.1093837015e-31, "kg", "Electron mass"),
    "proton mass": (1.67262192369e-27, "kg", "Proton mass"),
    "elementary charge": (1.602176634e-19, "C", "Elementary charge"),
    "pi": (3.14159265358979323846, "", "Pi"),
    "e": (2.71828182845904523536, "", "Euler's number"),
    "golden ratio": (1.61803398874989484820, "", "Golden ratio (phi)"),
    # Water properties
    "boiling point of water": (100, "°C (212°F)", "Boiling point of water at standard pressure"),
    "freezing point of water": (0, "°C (32°F)", "Freezing point of water at standard pressure"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# GENERAL KNOWLEDGE FACTS
# Source: Standard references
# ═══════════════════════════════════════════════════════════════════════════════

GENERAL_FACTS: Dict[str, tuple[Any, str, str]] = {
    # Time units
    "days in a year": (365, "days", "Days in a standard year (366 in leap year)"),
    "days in year": (365, "days", "Days in a standard year (366 in leap year)"),
    "hours in a day": (24, "hours", "Hours in one day"),
    "hours in day": (24, "hours", "Hours in one day"),
    "minutes in an hour": (60, "minutes", "Minutes in one hour"),
    "minutes in hour": (60, "minutes", "Minutes in one hour"),
    "seconds in a minute": (60, "seconds", "Seconds in one minute"),
    "seconds in minute": (60, "seconds", "Seconds in one minute"),
    "months in a year": (12, "months", "Months in one year"),
    "months in year": (12, "months", "Months in one year"),
    "weeks in a year": (52, "weeks", "Weeks in one year (approximately)"),
    "days in a week": (7, "days", "Days in one week"),
    # Solar system
    "planets in solar system": (8, "planets", "Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune"),
    "planets in our solar system": (8, "planets", "Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune"),
    "largest planet": ("Jupiter", "", "Jupiter is the largest planet in our solar system"),
    "smallest planet": ("Mercury", "", "Mercury is the smallest planet in our solar system"),
    "closest planet to sun": ("Mercury", "", "Mercury is the closest planet to the Sun"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# ACRONYMS & ABBREVIATIONS
# Source: Standard definitions
# ═══════════════════════════════════════════════════════════════════════════════

ACRONYMS: Dict[str, tuple[str, str]] = {
    # Computing
    "html": ("HyperText Markup Language", "Standard markup language for web pages"),
    "css": ("Cascading Style Sheets", "Style sheet language for web pages"),
    "cpu": ("Central Processing Unit", "The main processor of a computer"),
    "gpu": ("Graphics Processing Unit", "Specialized processor for graphics"),
    "ram": ("Random Access Memory", "Computer's short-term memory"),
    "api": ("Application Programming Interface", "Interface for software communication"),
    "url": ("Uniform Resource Locator", "Web address"),
    "http": ("HyperText Transfer Protocol", "Protocol for web communication"),
    "https": ("HyperText Transfer Protocol Secure", "Secure web protocol"),
    "sql": ("Structured Query Language", "Database query language"),
    "json": ("JavaScript Object Notation", "Data interchange format"),
    "xml": ("Extensible Markup Language", "Markup language for data"),
    "ip": ("Internet Protocol", "Network addressing protocol"),
    "tcp": ("Transmission Control Protocol", "Network communication protocol"),
    "ai": ("Artificial Intelligence", "Machine intelligence"),
    "ml": ("Machine Learning", "Subset of AI using statistical learning"),
    "llm": ("Large Language Model", "AI model trained on text data"),
    "os": ("Operating System", "System software managing hardware"),
    "ide": ("Integrated Development Environment", "Software development tool"),
    # General
    "nasa": ("National Aeronautics and Space Administration", "US space agency"),
    "fbi": ("Federal Bureau of Investigation", "US federal law enforcement"),
    "cia": ("Central Intelligence Agency", "US intelligence agency"),
    "nist": ("National Institute of Standards and Technology", "US standards agency"),
    "iso": ("International Organization for Standardization", "International standards body"),
    # Biology
    "dna": ("Deoxyribonucleic Acid", "Molecule carrying genetic instructions"),
    "rna": ("Ribonucleic Acid", "Molecule essential for gene expression"),
    "atp": ("Adenosine Triphosphate", "Energy currency of cells"),
    "mrna": ("Messenger RNA", "Carries genetic info from DNA to ribosomes"),
    # Math/Science
    "si": ("International System of Units", "Modern metric system"),
    "mit": ("Massachusetts Institute of Technology", "Research university"),
    "ieee": ("Institute of Electrical and Electronics Engineers", "Professional association"),
    "stem": ("Science, Technology, Engineering, Mathematics", "Academic disciplines"),
    # Economics
    "gdp": ("Gross Domestic Product", "Total value of goods/services produced"),
    "gnp": ("Gross National Product", "Total value produced by residents"),
    "imf": ("International Monetary Fund", "International financial institution"),
    # Medical
    "cpr": ("Cardiopulmonary Resuscitation", "Emergency life-saving procedure"),
    "mri": ("Magnetic Resonance Imaging", "Medical imaging technique"),
    "ct": ("Computed Tomography", "Medical imaging using X-rays"),
    "ekg": ("Electrocardiogram", "Test measuring heart electrical activity"),
    "ecg": ("Electrocardiogram", "Test measuring heart electrical activity"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PERIODIC TABLE - ALL 118 ELEMENTS
# Source: IUPAC Periodic Table 2024
# ═══════════════════════════════════════════════════════════════════════════════

# Element: (symbol, atomic_number, atomic_mass, category)
PERIODIC_TABLE: Dict[str, tuple[str, int, float, str]] = {
    # Period 1
    "hydrogen": ("H", 1, 1.008, "nonmetal"),
    "helium": ("He", 2, 4.003, "noble gas"),
    # Period 2
    "lithium": ("Li", 3, 6.941, "alkali metal"),
    "beryllium": ("Be", 4, 9.012, "alkaline earth metal"),
    "boron": ("B", 5, 10.81, "metalloid"),
    "carbon": ("C", 6, 12.01, "nonmetal"),
    "nitrogen": ("N", 7, 14.01, "nonmetal"),
    "oxygen": ("O", 8, 16.00, "nonmetal"),
    "fluorine": ("F", 9, 19.00, "halogen"),
    "neon": ("Ne", 10, 20.18, "noble gas"),
    # Period 3
    "sodium": ("Na", 11, 22.99, "alkali metal"),
    "magnesium": ("Mg", 12, 24.31, "alkaline earth metal"),
    "aluminum": ("Al", 13, 26.98, "post-transition metal"),
    "aluminium": ("Al", 13, 26.98, "post-transition metal"),  # British spelling
    "silicon": ("Si", 14, 28.09, "metalloid"),
    "phosphorus": ("P", 15, 30.97, "nonmetal"),
    "sulfur": ("S", 16, 32.07, "nonmetal"),
    "sulphur": ("S", 16, 32.07, "nonmetal"),  # British spelling
    "chlorine": ("Cl", 17, 35.45, "halogen"),
    "argon": ("Ar", 18, 39.95, "noble gas"),
    # Period 4
    "potassium": ("K", 19, 39.10, "alkali metal"),
    "calcium": ("Ca", 20, 40.08, "alkaline earth metal"),
    "scandium": ("Sc", 21, 44.96, "transition metal"),
    "titanium": ("Ti", 22, 47.87, "transition metal"),
    "vanadium": ("V", 23, 50.94, "transition metal"),
    "chromium": ("Cr", 24, 52.00, "transition metal"),
    "manganese": ("Mn", 25, 54.94, "transition metal"),
    "iron": ("Fe", 26, 55.85, "transition metal"),
    "cobalt": ("Co", 27, 58.93, "transition metal"),
    "nickel": ("Ni", 28, 58.69, "transition metal"),
    "copper": ("Cu", 29, 63.55, "transition metal"),
    "zinc": ("Zn", 30, 65.38, "transition metal"),
    "gallium": ("Ga", 31, 69.72, "post-transition metal"),
    "germanium": ("Ge", 32, 72.63, "metalloid"),
    "arsenic": ("As", 33, 74.92, "metalloid"),
    "selenium": ("Se", 34, 78.97, "nonmetal"),
    "bromine": ("Br", 35, 79.90, "halogen"),
    "krypton": ("Kr", 36, 83.80, "noble gas"),
    # Period 5
    "rubidium": ("Rb", 37, 85.47, "alkali metal"),
    "strontium": ("Sr", 38, 87.62, "alkaline earth metal"),
    "yttrium": ("Y", 39, 88.91, "transition metal"),
    "zirconium": ("Zr", 40, 91.22, "transition metal"),
    "niobium": ("Nb", 41, 92.91, "transition metal"),
    "molybdenum": ("Mo", 42, 95.95, "transition metal"),
    "technetium": ("Tc", 43, 98.00, "transition metal"),
    "ruthenium": ("Ru", 44, 101.07, "transition metal"),
    "rhodium": ("Rh", 45, 102.91, "transition metal"),
    "palladium": ("Pd", 46, 106.42, "transition metal"),
    "silver": ("Ag", 47, 107.87, "transition metal"),
    "cadmium": ("Cd", 48, 112.41, "transition metal"),
    "indium": ("In", 49, 114.82, "post-transition metal"),
    "tin": ("Sn", 50, 118.71, "post-transition metal"),
    "antimony": ("Sb", 51, 121.76, "metalloid"),
    "tellurium": ("Te", 52, 127.60, "metalloid"),
    "iodine": ("I", 53, 126.90, "halogen"),
    "xenon": ("Xe", 54, 131.29, "noble gas"),
    # Period 6
    "cesium": ("Cs", 55, 132.91, "alkali metal"),
    "caesium": ("Cs", 55, 132.91, "alkali metal"),  # British spelling
    "barium": ("Ba", 56, 137.33, "alkaline earth metal"),
    "lanthanum": ("La", 57, 138.91, "lanthanide"),
    "cerium": ("Ce", 58, 140.12, "lanthanide"),
    "praseodymium": ("Pr", 59, 140.91, "lanthanide"),
    "neodymium": ("Nd", 60, 144.24, "lanthanide"),
    "promethium": ("Pm", 61, 145.00, "lanthanide"),
    "samarium": ("Sm", 62, 150.36, "lanthanide"),
    "europium": ("Eu", 63, 151.96, "lanthanide"),
    "gadolinium": ("Gd", 64, 157.25, "lanthanide"),
    "terbium": ("Tb", 65, 158.93, "lanthanide"),
    "dysprosium": ("Dy", 66, 162.50, "lanthanide"),
    "holmium": ("Ho", 67, 164.93, "lanthanide"),
    "erbium": ("Er", 68, 167.26, "lanthanide"),
    "thulium": ("Tm", 69, 168.93, "lanthanide"),
    "ytterbium": ("Yb", 70, 173.05, "lanthanide"),
    "lutetium": ("Lu", 71, 174.97, "lanthanide"),
    "hafnium": ("Hf", 72, 178.49, "transition metal"),
    "tantalum": ("Ta", 73, 180.95, "transition metal"),
    "tungsten": ("W", 74, 183.84, "transition metal"),
    "rhenium": ("Re", 75, 186.21, "transition metal"),
    "osmium": ("Os", 76, 190.23, "transition metal"),
    "iridium": ("Ir", 77, 192.22, "transition metal"),
    "platinum": ("Pt", 78, 195.08, "transition metal"),
    "gold": ("Au", 79, 196.97, "transition metal"),
    "mercury": ("Hg", 80, 200.59, "transition metal"),
    "thallium": ("Tl", 81, 204.38, "post-transition metal"),
    "lead": ("Pb", 82, 207.2, "post-transition metal"),
    "bismuth": ("Bi", 83, 208.98, "post-transition metal"),
    "polonium": ("Po", 84, 209.00, "metalloid"),
    "astatine": ("At", 85, 210.00, "halogen"),
    "radon": ("Rn", 86, 222.00, "noble gas"),
    # Period 7
    "francium": ("Fr", 87, 223.00, "alkali metal"),
    "radium": ("Ra", 88, 226.00, "alkaline earth metal"),
    "actinium": ("Ac", 89, 227.00, "actinide"),
    "thorium": ("Th", 90, 232.04, "actinide"),
    "protactinium": ("Pa", 91, 231.04, "actinide"),
    "uranium": ("U", 92, 238.03, "actinide"),
    "neptunium": ("Np", 93, 237.00, "actinide"),
    "plutonium": ("Pu", 94, 244.00, "actinide"),
    "americium": ("Am", 95, 243.00, "actinide"),
    "curium": ("Cm", 96, 247.00, "actinide"),
    "berkelium": ("Bk", 97, 247.00, "actinide"),
    "californium": ("Cf", 98, 251.00, "actinide"),
    "einsteinium": ("Es", 99, 252.00, "actinide"),
    "fermium": ("Fm", 100, 257.00, "actinide"),
    "mendelevium": ("Md", 101, 258.00, "actinide"),
    "nobelium": ("No", 102, 259.00, "actinide"),
    "lawrencium": ("Lr", 103, 266.00, "actinide"),
    "rutherfordium": ("Rf", 104, 267.00, "transition metal"),
    "dubnium": ("Db", 105, 268.00, "transition metal"),
    "seaborgium": ("Sg", 106, 269.00, "transition metal"),
    "bohrium": ("Bh", 107, 270.00, "transition metal"),
    "hassium": ("Hs", 108, 277.00, "transition metal"),
    "meitnerium": ("Mt", 109, 278.00, "unknown"),
    "darmstadtium": ("Ds", 110, 281.00, "unknown"),
    "roentgenium": ("Rg", 111, 282.00, "unknown"),
    "copernicium": ("Cn", 112, 285.00, "transition metal"),
    "nihonium": ("Nh", 113, 286.00, "unknown"),
    "flerovium": ("Fl", 114, 289.00, "post-transition metal"),
    "moscovium": ("Mc", 115, 290.00, "unknown"),
    "livermorium": ("Lv", 116, 293.00, "unknown"),
    "tennessine": ("Ts", 117, 294.00, "unknown"),
    "oganesson": ("Og", 118, 294.00, "noble gas"),
}

# Symbol to element name (reverse lookup)
ELEMENT_SYMBOLS: Dict[str, str] = {v[0].lower(): k for k, v in PERIODIC_TABLE.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# CHEMISTRY NOTATION - How to read chemical formulas
# Source: IUPAC nomenclature
# ═══════════════════════════════════════════════════════════════════════════════

CHEMICAL_NOTATION: Dict[str, str] = {
    # Subscript meanings
    "subscript": "Number after element symbol indicates atom count. H₂O = 2 hydrogen, 1 oxygen",
    "coefficient": "Number before formula indicates molecules. 2H₂O = 2 molecules of water",
    "parentheses": "Group atoms together. Ca(OH)₂ = 1 calcium, 2 oxygen, 2 hydrogen",
    # Common patterns
    "h2o": "H₂O = 2 Hydrogen atoms + 1 Oxygen atom = Water",
    "co2": "CO₂ = 1 Carbon atom + 2 Oxygen atoms = Carbon Dioxide",
    "nacl": "NaCl = 1 Sodium atom + 1 Chlorine atom = Salt",
    "ch4": "CH₄ = 1 Carbon atom + 4 Hydrogen atoms = Methane",
    "o2": "O₂ = 2 Oxygen atoms bonded = Molecular Oxygen (what we breathe)",
    "h2so4": "H₂SO₄ = 2 Hydrogen + 1 Sulfur + 4 Oxygen = Sulfuric Acid",
}


# ═══════════════════════════════════════════════════════════════════════════════
# BIOLOGY FUNDAMENTALS
# Source: Standard biology textbooks, NIH
# ═══════════════════════════════════════════════════════════════════════════════

BIOLOGY_FACTS: Dict[str, tuple[str, str]] = {
    # Cell parts (organelles)
    "mitochondria": ("Powerhouse of the cell", "Produces ATP through cellular respiration"),
    "mitochondrion": ("Powerhouse of the cell", "Produces ATP through cellular respiration"),
    "powerhouse of the cell": ("Mitochondria", "Organelle that produces ATP energy"),
    "nucleus": ("Control center of the cell", "Contains DNA and controls cell activities"),
    "ribosome": ("Protein factory", "Synthesizes proteins from mRNA instructions"),
    "endoplasmic reticulum": ("Transport network", "Processes and transports proteins"),
    "golgi apparatus": ("Packaging center", "Modifies and packages proteins for transport"),
    "cell membrane": ("Protective barrier", "Controls what enters/exits the cell"),
    "cytoplasm": ("Cell fluid", "Gel-like substance where organelles float"),
    "chloroplast": ("Photosynthesis site", "Converts sunlight to energy in plants"),
    "vacuole": ("Storage container", "Stores water, nutrients, and waste"),
    "lysosome": ("Recycling center", "Breaks down waste and cellular debris"),
    
    # Key processes
    "photosynthesis": ("6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂", "Plants convert sunlight, water, and CO₂ into glucose and oxygen"),
    "cellular respiration": ("C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ATP", "Cells convert glucose and oxygen into energy, CO₂, and water"),
    "dna replication": ("DNA → 2 DNA copies", "Process where DNA makes a copy of itself before cell division"),
    "transcription": ("DNA → mRNA", "DNA code is copied into messenger RNA"),
    "translation": ("mRNA → Protein", "Ribosomes read mRNA to build proteins"),
    
    # DNA/RNA
    "dna bases": ("A, T, G, C", "Adenine, Thymine, Guanine, Cytosine - the 4 DNA nucleotides"),
    "rna bases": ("A, U, G, C", "Adenine, Uracil, Guanine, Cytosine - the 4 RNA nucleotides"),
    "base pairing": ("A-T, G-C (DNA); A-U, G-C (RNA)", "Complementary base pairs in nucleic acids"),
    "double helix": ("DNA structure", "Two strands wound around each other discovered by Watson & Crick"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# MATH NOTATION & SYMBOLS
# Source: Mathematical conventions
# ═══════════════════════════════════════════════════════════════════════════════

MATH_NOTATION: Dict[str, tuple[str, str]] = {
    # Calculus
    "derivative": ("d/dx or f'(x)", "Rate of change of a function"),
    "derivative of x^2": ("2x", "Using power rule: d/dx(x^n) = nx^(n-1)"),
    "derivative of x^3": ("3x²", "Using power rule: d/dx(x^n) = nx^(n-1)"),
    "derivative of sin(x)": ("cos(x)", "Derivative of sine is cosine"),
    "derivative of cos(x)": ("-sin(x)", "Derivative of cosine is negative sine"),
    "derivative of e^x": ("e^x", "e^x is its own derivative"),
    "derivative of ln(x)": ("1/x", "Derivative of natural log"),
    "integral": ("∫ or antiderivative", "Reverse of derivative, finds area under curve"),
    "integral of x": ("x²/2 + C", "Antiderivative of x"),
    "integral of 1/x": ("ln|x| + C", "Antiderivative of 1/x is natural log"),
    "integral of x^n": ("x^(n+1)/(n+1) + C", "Power rule for integration (n ≠ -1)"),
    
    # Symbols
    "sigma": ("Σ", "Summation - add up a series"),
    "pi symbol": ("π", "Ratio of circumference to diameter ≈ 3.14159"),
    "infinity": ("∞", "Without bound, larger than any number"),
    "delta": ("Δ or δ", "Change in a quantity"),
    "theta": ("θ", "Commonly used for angles"),
    "alpha": ("α", "First letter of Greek alphabet, often a constant"),
    "beta": ("β", "Second letter of Greek alphabet"),
    "lambda": ("λ", "Wavelength in physics, anonymous functions in CS"),
    "sqrt": ("√", "Square root symbol"),
    "not equal": ("≠", "Not equal to"),
    "approximately": ("≈", "Approximately equal to"),
    "less than or equal": ("≤", "Less than or equal to"),
    "greater than or equal": ("≥", "Greater than or equal to"),
    "therefore": ("∴", "Therefore, it follows that"),
    "because": ("∵", "Because, since"),
    
    # Common formulas
    "quadratic formula": ("x = (-b ± √(b²-4ac)) / 2a", "Solves ax² + bx + c = 0"),
    "pythagorean theorem": ("a² + b² = c²", "Relationship of sides in right triangle"),
    "distance formula": ("d = √((x₂-x₁)² + (y₂-y₁)²)", "Distance between two points"),
    "slope formula": ("m = (y₂-y₁)/(x₂-x₁)", "Slope of a line between two points"),
    "area of circle": ("A = πr²", "Area equals pi times radius squared"),
    "circumference": ("C = 2πr", "Circumference equals 2 pi times radius"),
    "volume of sphere": ("V = (4/3)πr³", "Volume of a sphere"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS UNITS (SI System)
# Source: NIST, International Bureau of Weights and Measures
# ═══════════════════════════════════════════════════════════════════════════════

SI_UNITS: Dict[str, tuple[str, str, str]] = {
    # Base SI units: (symbol, quantity, definition)
    "meter": ("m", "length", "Base unit of length"),
    "kilogram": ("kg", "mass", "Base unit of mass"),
    "second": ("s", "time", "Base unit of time"),
    "ampere": ("A", "electric current", "Base unit of electric current"),
    "kelvin": ("K", "temperature", "Base unit of thermodynamic temperature"),
    "mole": ("mol", "amount of substance", "Base unit, 6.022×10²³ particles"),
    "candela": ("cd", "luminous intensity", "Base unit of light intensity"),
    
    # Derived units
    "newton": ("N", "force", "kg⋅m/s² - force to accelerate 1kg at 1m/s²"),
    "joule": ("J", "energy", "N⋅m - work done by 1N force over 1m"),
    "watt": ("W", "power", "J/s - rate of energy transfer"),
    "volt": ("V", "voltage", "W/A - electric potential"),
    "ohm": ("Ω", "resistance", "V/A - electrical resistance"),
    "hertz": ("Hz", "frequency", "1/s - cycles per second"),
    "pascal": ("Pa", "pressure", "N/m² - force per unit area"),
    "coulomb": ("C", "electric charge", "A⋅s - amount of electric charge"),
}

SI_PREFIXES: Dict[str, tuple[str, float]] = {
    "tera": ("T", 1e12),
    "giga": ("G", 1e9),
    "mega": ("M", 1e6),
    "kilo": ("k", 1e3),
    "hecto": ("h", 1e2),
    "deca": ("da", 1e1),
    "deci": ("d", 1e-1),
    "centi": ("c", 1e-2),
    "milli": ("m", 1e-3),
    "micro": ("μ", 1e-6),
    "nano": ("n", 1e-9),
    "pico": ("p", 1e-12),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS LAWS & EQUATIONS
# Source: Physics textbooks, NIST
# ═══════════════════════════════════════════════════════════════════════════════

PHYSICS_LAWS: Dict[str, tuple[str, str]] = {
    # Newton's Laws (multiple forms for matching)
    "newton first law": ("An object at rest stays at rest, an object in motion stays in motion unless acted upon by an external force", "Law of Inertia"),
    "newton's first law": ("An object at rest stays at rest, an object in motion stays in motion unless acted upon by an external force", "Law of Inertia"),
    "first law of motion": ("An object at rest stays at rest, an object in motion stays in motion unless acted upon by an external force", "Law of Inertia"),
    "law of inertia": ("An object at rest stays at rest, an object in motion stays in motion unless acted upon by an external force", "Newton's First Law"),
    
    "newton second law": ("F = ma (Force equals mass times acceleration)", "Fundamental law of motion"),
    "newton's second law": ("F = ma (Force equals mass times acceleration)", "Fundamental law of motion"),
    "second law of motion": ("F = ma (Force equals mass times acceleration)", "Fundamental law of motion"),
    "f=ma": ("Force equals mass times acceleration", "Newton's Second Law"),
    
    "newton third law": ("Every action has an equal and opposite reaction", "Action-reaction pairs"),
    "newton's third law": ("Every action has an equal and opposite reaction", "Action-reaction pairs"),
    "third law of motion": ("Every action has an equal and opposite reaction", "Action-reaction pairs"),
    
    # Other fundamental laws
    "law of gravity": ("F = Gm₁m₂/r²", "Gravitational force between two masses"),
    "ohm's law": ("V = IR (Voltage equals current times resistance)", "Fundamental electrical law"),
    "ohm law": ("V = IR (Voltage equals current times resistance)", "Fundamental electrical law"),
    "coulomb's law": ("F = kq₁q₂/r²", "Electric force between charges"),
    "coulomb law": ("F = kq₁q₂/r²", "Electric force between charges"),
    
    # Equations
    "kinetic energy": ("KE = ½mv²", "Energy of motion"),
    "potential energy": ("PE = mgh", "Energy due to position in gravity"),
    "momentum": ("p = mv", "Mass times velocity"),
    "work": ("W = Fd", "Force times distance"),
    "power": ("P = W/t", "Work divided by time"),
    "density": ("ρ = m/V", "Mass divided by volume"),
    "pressure": ("P = F/A", "Force divided by area"),
    "wave equation": ("v = fλ", "Velocity equals frequency times wavelength"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# CHEMISTRY
# Source: IUPAC, periodic table
# ═══════════════════════════════════════════════════════════════════════════════

CHEMICAL_FORMULAS: Dict[str, tuple[str, str]] = {
    # Common compounds
    "water": ("H₂O", "Dihydrogen monoxide"),
    "carbon dioxide": ("CO₂", "Carbon dioxide"),
    "oxygen": ("O₂", "Molecular oxygen"),
    "nitrogen": ("N₂", "Molecular nitrogen"),
    "salt": ("NaCl", "Sodium chloride"),
    "table salt": ("NaCl", "Sodium chloride"),
    "sugar": ("C₁₂H₂₂O₁₁", "Sucrose"),
    "methane": ("CH₄", "Methane"),
    "ammonia": ("NH₃", "Ammonia"),
    # Adding more common compounds
    "glucose": ("C₆H₁₂O₆", "Simple sugar, energy source"),
    "ethanol": ("C₂H₅OH", "Alcohol"),
    "acetic acid": ("CH₃COOH", "Vinegar"),
    "sulfuric acid": ("H₂SO₄", "Strong acid"),
    "hydrochloric acid": ("HCl", "Stomach acid"),
    "sodium hydroxide": ("NaOH", "Lye, strong base"),
    "calcium carbonate": ("CaCite", "Limestone, chalk"),
    "hydrogen peroxide": ("H₂O₂", "Disinfectant"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORICAL DATES
# Source: Encyclopedia Britannica, official records
# ═══════════════════════════════════════════════════════════════════════════════

HISTORICAL_DATES: Dict[str, tuple[str, str]] = {
    # (date/year, description)
    "python created": ("1991", "Python programming language first released by Guido van Rossum"),
    "python released": ("1991", "Python 0.9.0 released February 1991"),
    "javascript created": ("1995", "JavaScript created by Brendan Eich at Netscape"),
    "java created": ("1995", "Java released by Sun Microsystems"),
    "c created": ("1972", "C programming language developed by Dennis Ritchie"),
    "world wide web": ("1989", "World Wide Web invented by Tim Berners-Lee at CERN"),
    "internet created": ("1969", "ARPANET, precursor to internet, established"),
    "first iphone": ("2007", "Apple released the first iPhone on June 29, 2007"),
    "moon landing": ("1969", "Apollo 11 landed on the Moon on July 20, 1969"),
    "wwii ended": ("1945", "World War II ended September 2, 1945"),
    "world war ii end": ("1945", "World War II ended September 2, 1945"),
    "world war 2 end": ("1945", "World War II ended September 2, 1945"),
    "ww2 ended": ("1945", "World War II ended September 2, 1945"),
    "wwi ended": ("1918", "World War I ended November 11, 1918"),
    "world war i end": ("1918", "World War I ended November 11, 1918"),
    "declaration of independence": ("1776", "US Declaration of Independence signed July 4, 1776"),
    "french revolution": ("1789", "French Revolution began July 14, 1789"),
    "berlin wall fall": ("1989", "Berlin Wall fell on November 9, 1989"),
    "berlin wall fell": ("1989", "Berlin Wall fell on November 9, 1989"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY/ORGANIZATION FACTS
# Source: Official company records, SEC filings
# ═══════════════════════════════════════════════════════════════════════════════

COMPANY_FACTS: Dict[str, Dict[str, Any]] = {
    "apple": {
        "founded": "1976",
        "founders": ["Steve Jobs", "Steve Wozniak", "Ronald Wayne"],
        "headquarters": "Cupertino, California",
        "ceo": "Tim Cook",
    },
    "microsoft": {
        "founded": "1975",
        "founders": ["Bill Gates", "Paul Allen"],
        "headquarters": "Redmond, Washington",
        "ceo": "Satya Nadella",
    },
    "google": {
        "founded": "1998",
        "founders": ["Larry Page", "Sergey Brin"],
        "headquarters": "Mountain View, California",
        "parent": "Alphabet Inc.",
    },
    "amazon": {
        "founded": "1994",
        "founders": ["Jeff Bezos"],
        "headquarters": "Seattle, Washington",
    },
    "anthropic": {
        "founded": "2021",
        "founders": ["Dario Amodei", "Daniela Amodei"],
        "headquarters": "San Francisco, California",
        "known_for": "Claude AI assistant",
    },
    "openai": {
        "founded": "2015",
        "founders": ["Sam Altman", "Elon Musk", "others"],
        "headquarters": "San Francisco, California",
        "known_for": "ChatGPT, GPT-4",
    },
    "tesla": {
        "founded": "2003",
        "founders": ["Martin Eberhard", "Marc Tarpenning"],
        "headquarters": "Austin, Texas",
        "ceo": "Elon Musk",
    },
    "meta": {
        "founded": "2004",
        "founders": ["Mark Zuckerberg"],
        "headquarters": "Menlo Park, California",
        "formerly": "Facebook",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeBase:
    """
    Pre-verified knowledge base for instant fact retrieval.
    No LLM needed for known facts.
    
    Search Strategy (Three-Tier Kinematic Semantics):
    1. SHAPE: Kinematic query parsing (~0ms) - questions as equations
    2. SEMANTIC: Datamuse semantic field resolution (~200ms) - when patterns miss
    3. KEYWORD: Traditional keyword matching (~1ms) - fallback
    4. EMBEDDING: Vector search (~100ms) - last resort
    
    "The question has shape. The KB has shape. Match shapes, fill slots."
    """
    
    CIA_FACTBOOK_URL = "https://www.cia.gov/the-world-factbook/"
    NIST_URL = "https://www.nist.gov/pml/fundamental-physical-constants"
    
    def __init__(self, enable_embeddings: bool = True):
        self.queries = 0
        self.hits = 0
        self.shape_hits = 0       # Tier 1: Kinematic parser
        self.semantic_hits = 0    # Tier 2: Datamuse semantic fields
        self.keyword_hits = 0     # Tier 3: Traditional keyword matching
        self.embedding_hits = 0   # Tier 4: Vector embeddings
        self.typo_corrections = 0
        
        # Initialize language mechanics if available
        self._lm = get_language_mechanics() if HAS_LANGUAGE_MECHANICS else None
        
        # Initialize kinematic query parser (Tier 1)
        self._parser = get_query_parser() if HAS_QUERY_PARSER else None
        
        # Initialize semantic resolver (Tier 2)
        self._semantic = SemanticResolver() if HAS_SEMANTIC_RESOLVER else None
        
        # Initialize embedding engine (Tier 4) - lazy loaded
        self._embeddings = None
        self._embeddings_indexed = False
        self._enable_embeddings = enable_embeddings and HAS_EMBEDDINGS
    
    def _ensure_embeddings_indexed(self):
        """Lazy-load and index facts for semantic search."""
        if not self._enable_embeddings or self._embeddings_indexed:
            return
        
        try:
            self._embeddings = get_embedding_engine()
            if self._embeddings.is_available():
                # Build searchable facts from our data
                facts_to_index = self._build_searchable_facts()
                self._embeddings.index_facts(facts_to_index)
                self._embeddings_indexed = True
        except Exception:
            self._embeddings = None
    
    def _build_searchable_facts(self) -> Dict[str, str]:
        """Build dictionary of searchable facts for embedding."""
        facts = {}
        
        # Capitals
        for country, capital in COUNTRY_CAPITALS.items():
            facts[f"capital_{country}"] = f"The capital of {country.title()} is {capital}."
        
        # Scientific constants
        for const, (value, unit, desc) in SCIENTIFIC_CONSTANTS.items():
            if unit:
                facts[f"science_{const}"] = f"{desc}: {value} {unit}"
            else:
                facts[f"science_{const}"] = f"{desc}: {value}"
        
        # Historical dates
        for event, (date, desc) in HISTORICAL_DATES.items():
            facts[f"history_{event}"] = f"{desc} ({date})."
        
        # Acronyms
        for acronym, (expansion, desc) in ACRONYMS.items():
            facts[f"acronym_{acronym}"] = f"{acronym.upper()} stands for {expansion}. {desc}."
        
        # Biology
        for topic, (fact, description) in BIOLOGY_FACTS.items():
            facts[f"biology_{topic}"] = f"{fact}. {description}"
        
        # Physics
        for law, (statement, formula) in PHYSICS_LAWS.items():
            facts[f"physics_{law}"] = f"{statement}. {formula}" if formula else statement
        
        # Elements
        for element, (symbol, num, mass, category) in PERIODIC_TABLE.items():
            facts[f"element_{element}"] = f"{element.title()} ({symbol}) is element {num} with atomic mass {mass}. It is a {category}."
        
        # Chemical notation
        for formula, explanation in CHEMICAL_NOTATION.items():
            facts[f"notation_{formula}"] = explanation
        
        return facts
    
    def query(self, question: str) -> Optional[VerifiedFact]:
        """
        Query the knowledge base for a verified fact.
        Returns None if fact not found.
        
        Three-Tier Kinematic Semantics:
        1. SHAPE: Kinematic query parsing (~0ms) - questions as equations
        2. SEMANTIC: Datamuse semantic field resolution (~200ms)
        3. KEYWORD: Traditional keyword matching (~1ms)
        4. EMBEDDING: Vector search (~100ms) - last resort
        """
        self.queries += 1
        question_lower = question.lower().strip()
        
        # Apply typo correction and normalization if available
        if self._lm:
            corrected, corrections = self._lm.correct_typos(question_lower)
            if corrections:
                self.typo_corrections += len(corrections)
                question_lower = corrected
            # Normalize the query (e.g., "founder of X" → "who founded X")
            question_lower = self._lm.normalize_query(question_lower)
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 1: KINEMATIC SHAPE PARSING (~0ms)
        # "The question has shape. The KB has shape. Match shapes, fill slots."
        # ═══════════════════════════════════════════════════════════════════════
        if self._parser:
            result = self._query_by_shape(question_lower)
            if result:
                self.hits += 1
                self.shape_hits += 1
                return result
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 2: SEMANTIC FIELD RESOLUTION (~200ms)
        # "Beauty is in the eye of the beholder - meaning is contextual overlap."
        # ═══════════════════════════════════════════════════════════════════════
        if self._semantic:
            result = self._query_by_semantic_field(question, question_lower)
            if result:
                self.hits += 1
                self.semantic_hits += 1
                return result
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 3: KEYWORD MATCHING (~1ms)
        # Traditional pattern matching - still valuable for exact matches
        # ═══════════════════════════════════════════════════════════════════════
        result = (
            self._query_capital(question_lower) or
            self._query_geographic_misconception(question_lower) or
            self._query_population(question_lower) or
            self._query_language(question_lower) or
            self._query_currency(question_lower) or
            self._query_scientific(question_lower) or
            self._query_general(question_lower) or
            self._query_acronym(question_lower) or
            self._query_chemistry(question_lower) or
            self._query_element(question_lower) or
            self._query_chemical_notation(question_lower) or
            self._query_biology(question_lower) or
            self._query_math_notation(question_lower) or
            self._query_physics(question_lower) or
            self._query_si_units(question_lower) or
            self._query_historical(question_lower) or
            self._query_company(question_lower)
        )
        
        if result:
            self.hits += 1
            self.keyword_hits += 1
            return result
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 4: EMBEDDING SEARCH (~100ms)
        # Last resort - when structure is truly ambiguous
        # ═══════════════════════════════════════════════════════════════════════
        result = self._query_embedding(question_lower)
        if result:
            self.hits += 1
            self.embedding_hits += 1
        
        return result
    
    def _query_by_shape(self, question: str) -> Optional[VerifiedFact]:
        """
        Tier 1: Kinematic query parsing.
        Questions are incomplete equations seeking their terminus.
        """
        if not self._parser:
            return None
        
        parsed = self._parser.parse(question)
        
        # Only use if we have good confidence
        if parsed.confidence < 0.7 or parsed.shape == QueryShape.UNKNOWN:
            return None
        
        slot = parsed.slot
        if not slot:
            return None
        
        # Direct shape-to-KB lookup
        if parsed.shape == QueryShape.CAPITAL_OF:
            if slot in COUNTRY_CAPITALS:
                return VerifiedFact(
                    fact=f"The capital of {slot.title()} is {COUNTRY_CAPITALS[slot]}.",
                    category="geography",
                    source="CIA World Factbook (shape-matched)",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=parsed.confidence,
                )
        
        elif parsed.shape == QueryShape.FOUNDER_OF:
            if slot in COMPANY_FACTS:
                founders = COMPANY_FACTS[slot].get("founders", [])
                if founders:
                    return VerifiedFact(
                        fact=f"{slot.title()} was founded by {', '.join(founders)}.",
                        category="company",
                        source="Official Company Records (shape-matched)",
                        source_url="",
                        confidence=parsed.confidence,
                    )
        
        elif parsed.shape == QueryShape.FOUNDED_WHEN:
            if slot in COMPANY_FACTS:
                year = COMPANY_FACTS[slot].get("founded")
                if year:
                    return VerifiedFact(
                        fact=f"{slot.title()} was founded in {year}.",
                        category="company",
                        source="Official Company Records (shape-matched)",
                        source_url="",
                        confidence=parsed.confidence,
                    )
        
        elif parsed.shape == QueryShape.POPULATION_OF:
            if slot in COUNTRY_POPULATIONS:
                pop, year = COUNTRY_POPULATIONS[slot]
                return VerifiedFact(
                    fact=f"The population of {slot.title()} is approximately {pop:,} ({year} estimate).",
                    category="geography",
                    source="CIA World Factbook (shape-matched)",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=parsed.confidence,
                )
        
        elif parsed.shape == QueryShape.ATOMIC_NUMBER:
            if slot in PERIODIC_TABLE:
                symbol, num, mass, category = PERIODIC_TABLE[slot]
                return VerifiedFact(
                    fact=f"The atomic number of {slot.title()} is {num}.",
                    category="chemistry",
                    source="IUPAC Periodic Table (shape-matched)",
                    source_url="https://iupac.org/",
                    confidence=parsed.confidence,
                )
        
        elif parsed.shape == QueryShape.ACRONYM_EXPANSION:
            if slot in ACRONYMS:
                expansion, desc = ACRONYMS[slot]
                return VerifiedFact(
                    fact=f"{slot.upper()} stands for {expansion}. {desc}",
                    category="definition",
                    source="Standard Definitions (shape-matched)",
                    source_url="",
                    confidence=parsed.confidence,
                )
        
        elif parsed.shape == QueryShape.PHYSICS_LAW:
            # Try to match "first", "second", "third" etc.
            for law_name, (statement, formula) in PHYSICS_LAWS.items():
                if slot in law_name:
                    return VerifiedFact(
                        fact=f"{statement}" + (f" Formula: {formula}" if formula else ""),
                        category="physics",
                        source="Physics Fundamentals (shape-matched)",
                        source_url="https://physics.nist.gov/",
                        confidence=parsed.confidence,
                    )
        
        elif parsed.shape == QueryShape.FORMULA_MEANING:
            if slot in CHEMICAL_NOTATION:
                return VerifiedFact(
                    fact=CHEMICAL_NOTATION[slot],
                    category="chemistry",
                    source="IUPAC Nomenclature (shape-matched)",
                    source_url="https://iupac.org/",
                    confidence=parsed.confidence,
                )
        
        return None
    
    def _query_by_semantic_field(self, question_original: str, question_lower: str) -> Optional[VerifiedFact]:
        """
        Tier 2: Semantic field resolution using Datamuse API.
        Beauty is in the eye of the beholder - meaning is contextual overlap.
        """
        if not self._semantic:
            return None
        
        # Detect shape from semantic field
        shape = self._semantic.detect_shape(question_original)
        if not shape:
            return None
        
        # Extract entity
        entity = self._semantic.extract_entity(question_original)
        if not entity:
            return None
        
        entity_lower = entity.lower()
        
        # Route to appropriate KB based on semantic shape
        if shape == "CAPITAL_OF":
            if entity_lower in COUNTRY_CAPITALS:
                return VerifiedFact(
                    fact=f"The capital of {entity} is {COUNTRY_CAPITALS[entity_lower]}.",
                    category="geography",
                    source="CIA World Factbook (semantic-resolved)",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=0.85,  # Slightly lower confidence for semantic
                )
        
        elif shape == "FOUNDER_OF":
            if entity_lower in COMPANY_FACTS:
                founders = COMPANY_FACTS[entity_lower].get("founders", [])
                if founders:
                    return VerifiedFact(
                        fact=f"{entity} was founded by {', '.join(founders)}.",
                        category="company",
                        source="Official Company Records (semantic-resolved)",
                        source_url="",
                        confidence=0.85,
                    )
        
        elif shape == "POPULATION_OF":
            if entity_lower in COUNTRY_POPULATIONS:
                pop, year = COUNTRY_POPULATIONS[entity_lower]
                return VerifiedFact(
                    fact=f"The population of {entity} is approximately {pop:,} ({year} estimate).",
                    category="geography",
                    source="CIA World Factbook (semantic-resolved)",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=0.85,
                )
        
        elif shape == "LANGUAGE_OF":
            if entity_lower in COUNTRY_LANGUAGES:
                languages = COUNTRY_LANGUAGES[entity_lower]
                return VerifiedFact(
                    fact=f"The official language(s) of {entity} are: {', '.join(languages)}.",
                    category="geography",
                    source="CIA World Factbook (semantic-resolved)",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=0.85,
                )
        
        return None
    
    def _query_embedding(self, question: str) -> Optional[VerifiedFact]:
        """
        Tier 4: Embedding search fallback.
        Last resort - when structure is truly ambiguous.
        """
        if not self._enable_embeddings:
            return None
        
        # Lazy-load embeddings on first embedding query
        self._ensure_embeddings_indexed()
        
        if not self._embeddings or not self._embeddings.is_available():
            return None
        
        match = self._embeddings.find_best_match(question)
        if not match:
            return None
        
        # Return fact with similarity score in confidence
        return VerifiedFact(
            fact=match.text,
            category="embedding_match",
            source="Knowledge Base (Embedding)",
            source_url="",
            confidence=match.similarity,  # Similarity score as confidence
        )
    
    def _extract_country(self, text: str) -> Optional[str]:
        """Extract country name from question."""
        # Common patterns
        patterns = [
            r"capital of (\w+[\w\s]*)",
            r"(\w+[\w\s]*)'s capital",
            r"in (\w+[\w\s]*)",
            r"of (\w+[\w\s]*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                country = match.group(1).strip().lower()
                # Clean up
                country = country.rstrip('?.,!')
                if country in COUNTRY_CAPITALS:
                    return country
        
        # Direct lookup
        for country in COUNTRY_CAPITALS:
            if country in text:
                return country
        
        return None
    
    def _query_capital(self, question: str) -> Optional[VerifiedFact]:
        """Query for capital cities."""
        if "capital" not in question:
            return None
        
        country = self._extract_country(question)
        if country and country in COUNTRY_CAPITALS:
            capital = COUNTRY_CAPITALS[country]
            return VerifiedFact(
                fact=f"The capital of {country.title()} is {capital}.",
                category="geography",
                source="CIA World Factbook",
                source_url=self.CIA_FACTBOOK_URL,
                confidence=1.0,
            )
        return None

    def _query_geographic_misconception(self, question: str) -> Optional[VerifiedFact]:
        """Check for common geographic misconceptions (e.g. capital of a continent)."""
        # Check specifically for "capital of [continent]"
        if "capital" in question:
            for continent, fact in CONTINENTS.items():
                if continent in question:
                    return VerifiedFact(
                        fact=fact,
                        category="geography",
                        source="CIA World Factbook",
                        source_url=self.CIA_FACTBOOK_URL,
                        confidence=1.0,
                    )
        return None
    
    def _query_population(self, question: str) -> Optional[VerifiedFact]:
        """Query for population data."""
        if "population" not in question:
            return None
        
        for country, (pop, year) in COUNTRY_POPULATIONS.items():
            if country in question:
                formatted = f"{pop:,}"
                return VerifiedFact(
                    fact=f"The population of {country.title()} is approximately {formatted} ({year} estimate).",
                    category="demographics",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=0.95,  # Estimates
                )
        return None
    
    def _query_language(self, question: str) -> Optional[VerifiedFact]:
        """Query for official languages."""
        if "language" not in question and "speak" not in question:
            return None
        
        for country, languages in COUNTRY_LANGUAGES.items():
            if country in question:
                lang_str = ", ".join(languages)
                return VerifiedFact(
                    fact=f"The official language(s) of {country.title()}: {lang_str}.",
                    category="linguistics",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=1.0,
                )
        return None
    
    def _query_currency(self, question: str) -> Optional[VerifiedFact]:
        """Query for currencies."""
        if "currency" not in question and "money" not in question:
            return None
        
        for country, (name, code) in COUNTRY_CURRENCIES.items():
            if country in question:
                return VerifiedFact(
                    fact=f"The currency of {country.title()} is the {name} ({code}).",
                    category="economics",
                    source="ISO 4217",
                    source_url="https://www.iso.org/iso-4217-currency-codes.html",
                    confidence=1.0,
                )
        return None
    
    def _query_scientific(self, question: str) -> Optional[VerifiedFact]:
        """Query for scientific constants."""
        # Only match if specifically asking about constants/values
        if not any(word in question for word in [
            "constant", "value of", "what is pi", "what is e", 
            "speed of light", "gravity", "number", "planck", 
            "avogadro", "boltzmann", "boiling", "freezing", "point"
        ]):
            return None
            
        for const_name, (value, unit, desc) in SCIENTIFIC_CONSTANTS.items():
            # Require word boundary match for short names
            if len(const_name) <= 2:
                pattern = r'\b' + re.escape(const_name) + r'\b'
                if not re.search(pattern, question):
                    continue
            elif const_name in question:
                pass
            else:
                continue
                
            if unit:
                fact_str = f"{desc}: {value} {unit}"
            else:
                fact_str = f"{desc}: {value}"
            return VerifiedFact(
                fact=fact_str,
                category="science",
                source="NIST CODATA",
                source_url=self.NIST_URL,
                confidence=1.0,
            )
        return None
    
    def _query_historical(self, question: str) -> Optional[VerifiedFact]:
        """Query for historical dates."""
        for event, (date, desc) in HISTORICAL_DATES.items():
            # Use word boundary check to avoid false matches (e.g., "c created" matching "rust created")
            words = event.split()
            if len(words) == 1:
                # Single word events need word boundary
                pattern = r'\b' + re.escape(event) + r'\b'
                if not re.search(pattern, question):
                    continue
            else:
                # Multi-word events: all words must be present
                if not all(re.search(r'\b' + re.escape(word) + r'\b', question) for word in words):
                    continue
            
            return VerifiedFact(
                fact=f"{desc} ({date}).",
                category="history",
                source="Encyclopedia Britannica",
                source_url="https://www.britannica.com/",
                confidence=1.0,
            )
        return None
    
    def _query_company(self, question: str) -> Optional[VerifiedFact]:
        """Query for company facts."""
        for company, facts in COMPANY_FACTS.items():
            if company in question:
                # WHO questions - founders (check FIRST, before "when/founded")
                if "who" in question or "founder" in question:
                    founders = ", ".join(facts.get("founders", ["Unknown"]))
                    return VerifiedFact(
                        fact=f"{company.title()} was founded by {founders}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
                # WHEN questions - founding year
                if "founded" in question or "when" in question or "created" in question or "year" in question:
                    return VerifiedFact(
                        fact=f"{company.title()} was founded in {facts['founded']}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
                # WHERE questions - headquarters
                if "headquarters" in question or "located" in question or "where" in question:
                    return VerifiedFact(
                        fact=f"{company.title()} is headquartered in {facts.get('headquarters', 'Unknown')}.",
                        category="business",
                        source="Company records",
                        source_url=f"https://en.wikipedia.org/wiki/{company.title()}",
                        confidence=1.0,
                    )
        return None
    
    def _query_general(self, question: str) -> Optional[VerifiedFact]:
        """Query for general knowledge facts."""
        for fact_key, (value, unit, desc) in GENERAL_FACTS.items():
            # Check if all key words from fact_key appear in question
            key_words = fact_key.split()
            if all(word in question for word in key_words):
                if isinstance(value, str):
                    fact_str = f"{desc}."
                else:
                    fact_str = f"There are {value} {unit}. {desc}."
                return VerifiedFact(
                    fact=fact_str,
                    category="general",
                    source="Standard Reference",
                    source_url="https://en.wikipedia.org/",
                    confidence=1.0,
                )
        return None
    
    def _query_acronym(self, question: str) -> Optional[VerifiedFact]:
        """Query for acronym definitions."""
        # Match "what does X stand for" or "what is X"
        if not any(phrase in question for phrase in ["stand for", "what is", "what does", "meaning of"]):
            return None
        
        for acronym, (expansion, desc) in ACRONYMS.items():
            # Check if acronym is in question with word boundary
            pattern = r'\b' + re.escape(acronym) + r'\b'
            if re.search(pattern, question):
                return VerifiedFact(
                    fact=f"{acronym.upper()} stands for {expansion}. {desc}.",
                    category="acronyms",
                    source="Standard Definition",
                    source_url="https://en.wikipedia.org/",
                    confidence=1.0,
                )
        return None
    
    def _query_chemistry(self, question: str) -> Optional[VerifiedFact]:
        """Query for chemical formulas."""
        if not any(phrase in question for phrase in ["chemical", "formula", "symbol", "molecule"]):
            return None
        
        for compound, (formula, name) in CHEMICAL_FORMULAS.items():
            if compound in question:
                return VerifiedFact(
                    fact=f"The chemical formula for {compound} is {formula} ({name}).",
                    category="chemistry",
                    source="IUPAC",
                    source_url="https://iupac.org/",
                    confidence=1.0,
                )
        return None
    
    def _query_element(self, question: str) -> Optional[VerifiedFact]:
        """Query for periodic table elements."""
        # Check for element-related keywords
        if not any(word in question for word in [
            "element", "atomic", "symbol", "mass", "number", "periodic",
            "hydrogen", "helium", "carbon", "oxygen", "nitrogen", "gold", 
            "silver", "iron", "copper", "sodium", "chlorine", "potassium"
        ]):
            return None
        
        # Check for element by name
        for element, (symbol, atomic_num, mass, category) in PERIODIC_TABLE.items():
            if element in question:
                return VerifiedFact(
                    fact=f"{element.title()} ({symbol}) is element {atomic_num} with atomic mass {mass}. It is a {category}.",
                    category="chemistry",
                    source="IUPAC Periodic Table",
                    source_url="https://iupac.org/what-we-do/periodic-table-of-elements/",
                    confidence=1.0,
                )
        
        # Check for element by symbol
        for symbol_lower, element in ELEMENT_SYMBOLS.items():
            pattern = r'\b' + re.escape(symbol_lower) + r'\b'
            if re.search(pattern, question):
                symbol, atomic_num, mass, category = PERIODIC_TABLE[element]
                return VerifiedFact(
                    fact=f"{element.title()} ({symbol}) is element {atomic_num} with atomic mass {mass}. It is a {category}.",
                    category="chemistry",
                    source="IUPAC Periodic Table",
                    source_url="https://iupac.org/what-we-do/periodic-table-of-elements/",
                    confidence=1.0,
                )
        
        return None
    
    def _query_chemical_notation(self, question: str) -> Optional[VerifiedFact]:
        """Query for chemical notation explanations (like H2O)."""
        # Check for notation-related keywords
        if not any(word in question for word in [
            "mean", "notation", "formula", "h2o", "co2", "nacl", "h2so4",
            "molecule", "atoms", "compound", "what is", "explain"
        ]):
            return None
        
        for formula, explanation in CHEMICAL_NOTATION.items():
            if formula in question:
                return VerifiedFact(
                    fact=explanation,
                    category="chemistry",
                    source="IUPAC Chemistry Notation",
                    source_url="https://iupac.org/",
                    confidence=1.0,
                )
        
        return None
    
    def _query_biology(self, question: str) -> Optional[VerifiedFact]:
        """Query for biology facts (cells, DNA, processes)."""
        # Check for biology-related keywords
        if not any(word in question for word in [
            "cell", "dna", "rna", "mitochondria", "nucleus", "ribosome",
            "photosynthesis", "respiration", "replication", "protein",
            "organelle", "membrane", "chloroplast", "atp", "adenine",
            "thymine", "cytosine", "guanine", "uracil", "biology"
        ]):
            return None
        
        for topic, (fact, description) in BIOLOGY_FACTS.items():
            if topic in question:
                return VerifiedFact(
                    fact=f"{fact}. {description}",
                    category="biology",
                    source="NIH/Biology Textbooks",
                    source_url="https://www.ncbi.nlm.nih.gov/",
                    confidence=1.0,
                )
        
        return None
    
    def _query_math_notation(self, question: str) -> Optional[VerifiedFact]:
        """Query for mathematical notation and symbols."""
        # Check for math-related keywords
        if not any(word in question for word in [
            "derivative", "integral", "sigma", "delta", "sum", "infinity",
            "pythagorean", "quadratic", "formula", "theorem", "equation",
            "symbol", "notation", "math", "calculus", "∑", "∫", "∆", "√"
        ]):
            return None
        
        for concept, (meaning, example) in MATH_NOTATION.items():
            if concept in question:
                if example:
                    return VerifiedFact(
                        fact=f"{meaning} Example: {example}",
                        category="mathematics",
                        source="Mathematical Standards",
                        source_url="https://mathworld.wolfram.com/",
                        confidence=1.0,
                    )
                else:
                    return VerifiedFact(
                        fact=meaning,
                        category="mathematics",
                        source="Mathematical Standards",
                        source_url="https://mathworld.wolfram.com/",
                        confidence=1.0,
                    )
        
        return None
    
    def _query_physics(self, question: str) -> Optional[VerifiedFact]:
        """Query for physics laws and equations."""
        # Check for physics-related keywords
        if not any(word in question for word in [
            "newton", "law", "motion", "force", "energy", "momentum",
            "kinetic", "potential", "ohm", "voltage", "current", "resistance",
            "f=ma", "physics", "equation", "inertia", "acceleration"
        ]):
            return None
        
        # Prioritize longer/more specific matches first
        sorted_laws = sorted(PHYSICS_LAWS.keys(), key=len, reverse=True)
        for law in sorted_laws:
            if law in question:
                statement, formula = PHYSICS_LAWS[law]
                if formula:
                    return VerifiedFact(
                        fact=f"{statement} Formula: {formula}",
                        category="physics",
                        source="Physics Fundamentals",
                        source_url="https://physics.nist.gov/",
                        confidence=1.0,
                    )
                else:
                    return VerifiedFact(
                        fact=statement,
                        category="physics",
                        source="Physics Fundamentals",
                        source_url="https://physics.nist.gov/",
                        confidence=1.0,
                    )
        
        return None
    
    def _query_si_units(self, question: str) -> Optional[VerifiedFact]:
        """Query for SI units and prefixes."""
        # Check for unit-related keywords
        if not any(word in question for word in [
            "unit", "meter", "kilogram", "second", "ampere", "kelvin", "mole",
            "candela", "newton", "joule", "watt", "pascal", "hertz", "volt",
            "si", "measurement", "prefix", "kilo", "mega", "giga", "milli", "micro"
        ]):
            return None
        
        # Check SI units
        for unit_name, (symbol, quantity, definition) in SI_UNITS.items():
            if unit_name in question:
                return VerifiedFact(
                    fact=f"The {unit_name} ({symbol}) is the SI unit of {quantity}. {definition}",
                    category="physics",
                    source="BIPM SI Units",
                    source_url="https://www.bipm.org/en/measurement-units",
                    confidence=1.0,
                )
        
        # Check SI prefixes
        for prefix, (symbol, factor) in SI_PREFIXES.items():
            if prefix in question:
                return VerifiedFact(
                    fact=f"The SI prefix {prefix} ({symbol}) means {factor}.",
                    category="physics",
                    source="BIPM SI Prefixes",
                    source_url="https://www.bipm.org/en/measurement-units",
                    confidence=1.0,
                )
        
        return None
    
    def verify_statement(self, statement: str) -> Optional[tuple[bool, VerifiedFact]]:
        """
        Verify if a statement matches known facts.
        Returns (is_correct, fact) or None if can't verify.
        """
        statement_lower = statement.lower()
        
        # Check capitals
        for country, capital in COUNTRY_CAPITALS.items():
            if country in statement_lower and "capital" in statement_lower:
                is_correct = capital.lower() in statement_lower
                fact = VerifiedFact(
                    fact=f"The capital of {country.title()} is {capital}.",
                    category="geography",
                    source="CIA World Factbook",
                    source_url=self.CIA_FACTBOOK_URL,
                    confidence=1.0,
                )
                return (is_correct, fact)
        
        return None
    
    def get_stats(self) -> Dict:
        stats = {
            "queries": self.queries,
            "hits": self.hits,
            "hit_rate": self.hits / max(1, self.queries),
            "tier_1_shape_hits": self.shape_hits,
            "tier_2_semantic_hits": self.semantic_hits,
            "tier_3_keyword_hits": self.keyword_hits,
            "tier_4_embedding_hits": self.embedding_hits,
            "typo_corrections": self.typo_corrections,
            "parser_enabled": self._parser is not None,
            "semantic_enabled": self._semantic is not None,
            "embeddings_enabled": self._enable_embeddings,
            "embeddings_indexed": self._embeddings_indexed,
        }
        
        # Add embedding engine stats if available
        if self._embeddings and self._embeddings_indexed:
            stats["embedding_stats"] = self._embeddings.get_stats()
        
        return stats


# Global instance
_knowledge_base: Optional[KnowledgeBase] = None

def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    kb = KnowledgeBase()
    
    test_questions = [
        # Geography
        "What is the capital of France?",
        "What is the capital of Japan?",
        # History/Companies
        "When was Python created?",
        "Who founded Apple?",
        # Science
        "What is the speed of light?",
        "What language do they speak in Brazil?",
        "What is the population of India?",
        # NEW: Elements
        "What is the atomic number of carbon?",
        "What element has the symbol Au?",
        "Tell me about oxygen",
        # NEW: Chemical Notation
        "What does H2O mean?",
        "Explain the formula CO2",
        # NEW: Biology
        "What is the mitochondria?",
        "What is photosynthesis?",
        "What does DNA stand for?",
        # NEW: Math
        "What is the derivative symbol?",
        "What is the quadratic formula?",
        "What does sigma mean in math?",
        # NEW: Physics
        "What is Newton's first law?",
        "What is Ohm's law?",
        # NEW: SI Units
        "What is a joule?",
        "What does the prefix kilo mean?",
    ]
    
    print("=" * 60)
    print("KNOWLEDGE BASE TEST")
    print("=" * 60)
    
    hits = 0
    for q in test_questions:
        print(f"\n❓ {q}")
        result = kb.query(q)
        if result:
            print(f"   ✓ {result.fact}")
            print(f"   📚 Source: {result.source}")
            hits += 1
        else:
            print("   ✗ Not in knowledge base")
    
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {hits}/{len(test_questions)} questions answered")
    print(f"📊 Stats: {kb.get_stats()}")
