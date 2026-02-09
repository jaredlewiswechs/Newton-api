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

# Import shared knowledge store for dynamically added facts
try:
    from .knowledge_store import get_knowledge_store
    HAS_KNOWLEDGE_STORE = True
except ImportError:
    HAS_KNOWLEDGE_STORE = False

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

# Import semantic resolver (Datamuse API) - Tier 2 semantic fields
try:
    from .semantic_resolver import SemanticResolver
    HAS_SEMANTIC_RESOLVER = True
except ImportError:
    HAS_SEMANTIC_RESOLVER = False

# Import Wikipedia facts (auto-scraped)
try:
    from .wikipedia_facts import WIKIPEDIA_FACTS
    HAS_WIKIPEDIA_FACTS = True
except ImportError:
    HAS_WIKIPEDIA_FACTS = False
    WIKIPEDIA_FACTS = {}


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
    # Europe (44 countries)
    "albania": "Tirana",
    "andorra": "Andorra la Vella",
    "armenia": "Yerevan",
    "austria": "Vienna",
    "azerbaijan": "Baku",
    "belarus": "Minsk",
    "belgium": "Brussels",
    "bosnia and herzegovina": "Sarajevo",
    "bosnia": "Sarajevo",
    "bulgaria": "Sofia",
    "croatia": "Zagreb",
    "cyprus": "Nicosia",
    "czech republic": "Prague",
    "czechia": "Prague",
    "denmark": "Copenhagen",
    "estonia": "Tallinn",
    "finland": "Helsinki",
    "france": "Paris",
    "georgia": "Tbilisi",
    "germany": "Berlin",
    "greece": "Athens",
    "hungary": "Budapest",
    "iceland": "Reykjavik",
    "ireland": "Dublin",
    "italy": "Rome",
    "kazakhstan": "Astana",
    "kosovo": "Pristina",
    "latvia": "Riga",
    "liechtenstein": "Vaduz",
    "lithuania": "Vilnius",
    "luxembourg": "Luxembourg City",
    "malta": "Valletta",
    "moldova": "Chisinau",
    "monaco": "Monaco",
    "montenegro": "Podgorica",
    "netherlands": "Amsterdam",
    "north macedonia": "Skopje",
    "macedonia": "Skopje",
    "norway": "Oslo",
    "poland": "Warsaw",
    "portugal": "Lisbon",
    "romania": "Bucharest",
    "russia": "Moscow",
    "san marino": "San Marino",
    "serbia": "Belgrade",
    "slovakia": "Bratislava",
    "slovenia": "Ljubljana",
    "spain": "Madrid",
    "sweden": "Stockholm",
    "switzerland": "Bern",
    "turkey": "Ankara",
    "ukraine": "Kyiv",
    "united kingdom": "London",
    "uk": "London",
    "england": "London",
    "scotland": "Edinburgh",
    "wales": "Cardiff",
    "northern ireland": "Belfast",
    "vatican city": "Vatican City",
    "vatican": "Vatican City",
    
    # North America (23 countries)
    "antigua and barbuda": "Saint John's",
    "bahamas": "Nassau",
    "barbados": "Bridgetown",
    "belize": "Belmopan",
    "canada": "Ottawa",
    "costa rica": "San José",
    "cuba": "Havana",
    "dominica": "Roseau",
    "dominican republic": "Santo Domingo",
    "el salvador": "San Salvador",
    "grenada": "Saint George's",
    "guatemala": "Guatemala City",
    "haiti": "Port-au-Prince",
    "honduras": "Tegucigalpa",
    "jamaica": "Kingston",
    "mexico": "Mexico City",
    "nicaragua": "Managua",
    "panama": "Panama City",
    "saint kitts and nevis": "Basseterre",
    "saint lucia": "Castries",
    "saint vincent and the grenadines": "Kingstown",
    "trinidad and tobago": "Port of Spain",
    "united states": "Washington, D.C.",
    "usa": "Washington, D.C.",
    "us": "Washington, D.C.",
    "america": "Washington, D.C.",
    
    # South America (12 countries)
    "argentina": "Buenos Aires",
    "bolivia": "La Paz",
    "brazil": "Brasília",
    "chile": "Santiago",
    "colombia": "Bogotá",
    "ecuador": "Quito",
    "guyana": "Georgetown",
    "paraguay": "Asunción",
    "peru": "Lima",
    "suriname": "Paramaribo",
    "uruguay": "Montevideo",
    "venezuela": "Caracas",
    
    # Asia (48 countries)
    "afghanistan": "Kabul",
    "bahrain": "Manama",
    "bangladesh": "Dhaka",
    "bhutan": "Thimphu",
    "brunei": "Bandar Seri Begawan",
    "cambodia": "Phnom Penh",
    "china": "Beijing",
    "india": "New Delhi",
    "indonesia": "Jakarta",
    "iran": "Tehran",
    "iraq": "Baghdad",
    "israel": "Jerusalem",
    "japan": "Tokyo",
    "jordan": "Amman",
    "korea": "Seoul",
    "south korea": "Seoul",
    "north korea": "Pyongyang",
    "kuwait": "Kuwait City",
    "kyrgyzstan": "Bishkek",
    "laos": "Vientiane",
    "lebanon": "Beirut",
    "malaysia": "Kuala Lumpur",
    "maldives": "Malé",
    "mongolia": "Ulaanbaatar",
    "myanmar": "Naypyidaw",
    "burma": "Naypyidaw",
    "nepal": "Kathmandu",
    "oman": "Muscat",
    "pakistan": "Islamabad",
    "palestine": "Ramallah",
    "philippines": "Manila",
    "qatar": "Doha",
    "saudi arabia": "Riyadh",
    "singapore": "Singapore",
    "sri lanka": "Sri Jayawardenepura Kotte",
    "syria": "Damascus",
    "taiwan": "Taipei",
    "tajikistan": "Dushanbe",
    "thailand": "Bangkok",
    "timor-leste": "Dili",
    "east timor": "Dili",
    "turkmenistan": "Ashgabat",
    "united arab emirates": "Abu Dhabi",
    "uae": "Abu Dhabi",
    "uzbekistan": "Tashkent",
    "vietnam": "Hanoi",
    "yemen": "Sana'a",
    
    # Africa (54 countries)
    "algeria": "Algiers",
    "angola": "Luanda",
    "benin": "Porto-Novo",
    "botswana": "Gaborone",
    "burkina faso": "Ouagadougou",
    "burundi": "Gitega",
    "cameroon": "Yaoundé",
    "cape verde": "Praia",
    "cabo verde": "Praia",
    "central african republic": "Bangui",
    "chad": "N'Djamena",
    "comoros": "Moroni",
    "congo": "Brazzaville",
    "democratic republic of the congo": "Kinshasa",
    "drc": "Kinshasa",
    "djibouti": "Djibouti",
    "egypt": "Cairo",
    "equatorial guinea": "Malabo",
    "eritrea": "Asmara",
    "eswatini": "Mbabane",
    "swaziland": "Mbabane",
    "ethiopia": "Addis Ababa",
    "gabon": "Libreville",
    "gambia": "Banjul",
    "ghana": "Accra",
    "guinea": "Conakry",
    "guinea-bissau": "Bissau",
    "ivory coast": "Yamoussoukro",
    "cote d'ivoire": "Yamoussoukro",
    "kenya": "Nairobi",
    "lesotho": "Maseru",
    "liberia": "Monrovia",
    "libya": "Tripoli",
    "madagascar": "Antananarivo",
    "malawi": "Lilongwe",
    "mali": "Bamako",
    "mauritania": "Nouakchott",
    "mauritius": "Port Louis",
    "morocco": "Rabat",
    "mozambique": "Maputo",
    "namibia": "Windhoek",
    "niger": "Niamey",
    "nigeria": "Abuja",
    "rwanda": "Kigali",
    "sao tome and principe": "São Tomé",
    "senegal": "Dakar",
    "seychelles": "Victoria",
    "sierra leone": "Freetown",
    "somalia": "Mogadishu",
    "south africa": "Pretoria",
    "south sudan": "Juba",
    "sudan": "Khartoum",
    "tanzania": "Dodoma",
    "togo": "Lomé",
    "tunisia": "Tunis",
    "uganda": "Kampala",
    "zambia": "Lusaka",
    "zimbabwe": "Harare",
    
    # Oceania (14 countries)
    "australia": "Canberra",
    "fiji": "Suva",
    "kiribati": "Tarawa",
    "marshall islands": "Majuro",
    "micronesia": "Palikir",
    "nauru": "Yaren",
    "new zealand": "Wellington",
    "palau": "Ngerulmud",
    "papua new guinea": "Port Moresby",
    "samoa": "Apia",
    "solomon islands": "Honiara",
    "tonga": "Nukuʻalofa",
    "tuvalu": "Funafuti",
    "vanuatu": "Port Vila",
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
    # (population, year) - Top 50 by population
    "india": (1_425_000_000, 2024),
    "china": (1_410_000_000, 2024),
    "united states": (335_000_000, 2024),
    "usa": (335_000_000, 2024),
    "indonesia": (277_000_000, 2024),
    "pakistan": (240_000_000, 2024),
    "brazil": (216_000_000, 2024),
    "nigeria": (230_000_000, 2024),
    "bangladesh": (173_000_000, 2024),
    "russia": (144_000_000, 2024),
    "japan": (124_000_000, 2024),
    "mexico": (130_000_000, 2024),
    "ethiopia": (127_000_000, 2024),
    "philippines": (117_000_000, 2024),
    "egypt": (112_000_000, 2024),
    "vietnam": (100_000_000, 2024),
    "dr congo": (99_000_000, 2024),
    "turkey": (85_000_000, 2024),
    "iran": (89_000_000, 2024),
    "germany": (84_000_000, 2024),
    "thailand": (72_000_000, 2024),
    "france": (68_000_000, 2024),
    "united kingdom": (68_000_000, 2024),
    "uk": (68_000_000, 2024),
    "tanzania": (67_000_000, 2024),
    "south africa": (60_000_000, 2024),
    "italy": (59_000_000, 2024),
    "myanmar": (55_000_000, 2024),
    "kenya": (55_000_000, 2024),
    "south korea": (52_000_000, 2024),
    "colombia": (52_000_000, 2024),
    "spain": (48_000_000, 2024),
    "argentina": (46_000_000, 2024),
    "uganda": (48_000_000, 2024),
    "algeria": (45_000_000, 2024),
    "sudan": (48_000_000, 2024),
    "ukraine": (38_000_000, 2024),
    "iraq": (44_000_000, 2024),
    "afghanistan": (42_000_000, 2024),
    "poland": (37_000_000, 2024),
    "canada": (40_000_000, 2024),
    "morocco": (37_000_000, 2024),
    "saudi arabia": (36_000_000, 2024),
    "uzbekistan": (36_000_000, 2024),
    "peru": (34_000_000, 2024),
    "angola": (36_000_000, 2024),
    "malaysia": (34_000_000, 2024),
    "mozambique": (33_000_000, 2024),
    "ghana": (34_000_000, 2024),
    "yemen": (34_000_000, 2024),
    "nepal": (30_000_000, 2024),
    "venezuela": (29_000_000, 2024),
    "australia": (26_000_000, 2024),
    "north korea": (26_000_000, 2024),
    "taiwan": (24_000_000, 2024),
    "syria": (22_000_000, 2024),
    "netherlands": (18_000_000, 2024),
    "chile": (20_000_000, 2024),
    "belgium": (12_000_000, 2024),
    "sweden": (11_000_000, 2024),
    "portugal": (10_000_000, 2024),
    "greece": (10_000_000, 2024),
    "czech republic": (11_000_000, 2024),
    "czechia": (11_000_000, 2024),
    "hungary": (10_000_000, 2024),
    "austria": (9_000_000, 2024),
    "switzerland": (9_000_000, 2024),
    "israel": (10_000_000, 2024),
    "norway": (5_500_000, 2024),
    "ireland": (5_100_000, 2024),
    "new zealand": (5_100_000, 2024),
    "singapore": (6_000_000, 2024),
    "finland": (5_500_000, 2024),
    "denmark": (6_000_000, 2024),
    "iceland": (380_000, 2024),
    "luxembourg": (660_000, 2024),
    "malta": (520_000, 2024),
    "vatican city": (800, 2024),
    "monaco": (40_000, 2024),
    "san marino": (34_000, 2024),
    "liechtenstein": (39_000, 2024),
}

COUNTRY_LANGUAGES: Dict[str, List[str]] = {
    # Major official languages
    "france": ["French"],
    "germany": ["German"],
    "spain": ["Spanish", "Catalan", "Basque", "Galician"],
    "italy": ["Italian"],
    "japan": ["Japanese"],
    "china": ["Mandarin Chinese"],
    "brazil": ["Portuguese"],
    "russia": ["Russian"],
    "india": ["Hindi", "English", "Bengali", "Telugu", "Marathi", "Tamil", "Urdu"],
    "united states": ["English", "Spanish"],
    "usa": ["English", "Spanish"],
    "mexico": ["Spanish"],
    "canada": ["English", "French"],
    "argentina": ["Spanish"],
    "colombia": ["Spanish"],
    "peru": ["Spanish", "Quechua", "Aymara"],
    "chile": ["Spanish"],
    "venezuela": ["Spanish"],
    "portugal": ["Portuguese"],
    "netherlands": ["Dutch"],
    "belgium": ["Dutch", "French", "German"],
    "switzerland": ["German", "French", "Italian", "Romansh"],
    "austria": ["German"],
    "poland": ["Polish"],
    "czech republic": ["Czech"],
    "czechia": ["Czech"],
    "hungary": ["Hungarian"],
    "romania": ["Romanian"],
    "bulgaria": ["Bulgarian"],
    "greece": ["Greek"],
    "turkey": ["Turkish"],
    "ukraine": ["Ukrainian"],
    "sweden": ["Swedish"],
    "norway": ["Norwegian"],
    "finland": ["Finnish", "Swedish"],
    "denmark": ["Danish"],
    "iceland": ["Icelandic"],
    "ireland": ["English", "Irish"],
    "united kingdom": ["English", "Welsh", "Scottish Gaelic"],
    "uk": ["English", "Welsh", "Scottish Gaelic"],
    "south korea": ["Korean"],
    "korea": ["Korean"],
    "north korea": ["Korean"],
    "vietnam": ["Vietnamese"],
    "thailand": ["Thai"],
    "indonesia": ["Indonesian"],
    "philippines": ["Filipino", "English"],
    "malaysia": ["Malay", "English", "Chinese", "Tamil"],
    "singapore": ["English", "Malay", "Mandarin", "Tamil"],
    "pakistan": ["Urdu", "English", "Punjabi", "Sindhi", "Pashto"],
    "bangladesh": ["Bengali"],
    "iran": ["Persian", "Farsi"],
    "iraq": ["Arabic", "Kurdish"],
    "egypt": ["Arabic"],
    "saudi arabia": ["Arabic"],
    "israel": ["Hebrew", "Arabic"],
    "south africa": ["English", "Zulu", "Xhosa", "Afrikaans"],
    "nigeria": ["English", "Hausa", "Yoruba", "Igbo"],
    "kenya": ["Swahili", "English"],
    "ethiopia": ["Amharic", "Oromo", "Tigrinya"],
    "morocco": ["Arabic", "Berber", "French"],
    "algeria": ["Arabic", "Berber", "French"],
    "australia": ["English"],
    "new zealand": ["English", "Maori"],
}

COUNTRY_CURRENCIES: Dict[str, tuple[str, str]] = {
    # (currency name, code)
    "united states": ("US Dollar", "USD"),
    "usa": ("US Dollar", "USD"),
    "european union": ("Euro", "EUR"),
    "eu": ("Euro", "EUR"),
    # Eurozone countries
    "france": ("Euro", "EUR"),
    "germany": ("Euro", "EUR"),
    "italy": ("Euro", "EUR"),
    "spain": ("Euro", "EUR"),
    "portugal": ("Euro", "EUR"),
    "netherlands": ("Euro", "EUR"),
    "belgium": ("Euro", "EUR"),
    "austria": ("Euro", "EUR"),
    "ireland": ("Euro", "EUR"),
    "finland": ("Euro", "EUR"),
    "greece": ("Euro", "EUR"),
    "luxembourg": ("Euro", "EUR"),
    "slovenia": ("Euro", "EUR"),
    "slovakia": ("Euro", "EUR"),
    "estonia": ("Euro", "EUR"),
    "latvia": ("Euro", "EUR"),
    "lithuania": ("Euro", "EUR"),
    "malta": ("Euro", "EUR"),
    "cyprus": ("Euro", "EUR"),
    "croatia": ("Euro", "EUR"),
    # Non-Euro Europe
    "united kingdom": ("British Pound", "GBP"),
    "uk": ("British Pound", "GBP"),
    "switzerland": ("Swiss Franc", "CHF"),
    "sweden": ("Swedish Krona", "SEK"),
    "norway": ("Norwegian Krone", "NOK"),
    "denmark": ("Danish Krone", "DKK"),
    "poland": ("Polish Zloty", "PLN"),
    "czech republic": ("Czech Koruna", "CZK"),
    "czechia": ("Czech Koruna", "CZK"),
    "hungary": ("Hungarian Forint", "HUF"),
    "romania": ("Romanian Leu", "RON"),
    "bulgaria": ("Bulgarian Lev", "BGN"),
    "russia": ("Russian Ruble", "RUB"),
    "ukraine": ("Ukrainian Hryvnia", "UAH"),
    "turkey": ("Turkish Lira", "TRY"),
    "iceland": ("Icelandic Krona", "ISK"),
    # Asia
    "japan": ("Japanese Yen", "JPY"),
    "china": ("Chinese Yuan", "CNY"),
    "india": ("Indian Rupee", "INR"),
    "south korea": ("South Korean Won", "KRW"),
    "korea": ("South Korean Won", "KRW"),
    "north korea": ("North Korean Won", "KPW"),
    "singapore": ("Singapore Dollar", "SGD"),
    "hong kong": ("Hong Kong Dollar", "HKD"),
    "taiwan": ("New Taiwan Dollar", "TWD"),
    "thailand": ("Thai Baht", "THB"),
    "vietnam": ("Vietnamese Dong", "VND"),
    "indonesia": ("Indonesian Rupiah", "IDR"),
    "malaysia": ("Malaysian Ringgit", "MYR"),
    "philippines": ("Philippine Peso", "PHP"),
    "pakistan": ("Pakistani Rupee", "PKR"),
    "bangladesh": ("Bangladeshi Taka", "BDT"),
    "saudi arabia": ("Saudi Riyal", "SAR"),
    "uae": ("UAE Dirham", "AED"),
    "united arab emirates": ("UAE Dirham", "AED"),
    "qatar": ("Qatari Riyal", "QAR"),
    "kuwait": ("Kuwaiti Dinar", "KWD"),
    "israel": ("Israeli Shekel", "ILS"),
    "iran": ("Iranian Rial", "IRR"),
    "iraq": ("Iraqi Dinar", "IQD"),
    # Americas
    "canada": ("Canadian Dollar", "CAD"),
    "mexico": ("Mexican Peso", "MXN"),
    "brazil": ("Brazilian Real", "BRL"),
    "argentina": ("Argentine Peso", "ARS"),
    "colombia": ("Colombian Peso", "COP"),
    "chile": ("Chilean Peso", "CLP"),
    "peru": ("Peruvian Sol", "PEN"),
    "venezuela": ("Venezuelan Bolivar", "VES"),
    # Africa
    "south africa": ("South African Rand", "ZAR"),
    "nigeria": ("Nigerian Naira", "NGN"),
    "egypt": ("Egyptian Pound", "EGP"),
    "kenya": ("Kenyan Shilling", "KES"),
    "morocco": ("Moroccan Dirham", "MAD"),
    # Oceania
    "australia": ("Australian Dollar", "AUD"),
    "new zealand": ("New Zealand Dollar", "NZD"),
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
    # Computing & Technology
    "html": ("HyperText Markup Language", "Standard markup language for web pages"),
    "css": ("Cascading Style Sheets", "Style sheet language for web pages"),
    "cpu": ("Central Processing Unit", "The main processor of a computer"),
    "gpu": ("Graphics Processing Unit", "Specialized processor for graphics"),
    "ram": ("Random Access Memory", "Computer's short-term memory"),
    "rom": ("Read-Only Memory", "Non-volatile computer memory"),
    "ssd": ("Solid State Drive", "Fast storage using flash memory"),
    "hdd": ("Hard Disk Drive", "Storage using magnetic platters"),
    "usb": ("Universal Serial Bus", "Standard for connecting peripherals"),
    "hdmi": ("High-Definition Multimedia Interface", "Audio/video interface"),
    "api": ("Application Programming Interface", "Interface for software communication"),
    "sdk": ("Software Development Kit", "Development tools for platforms"),
    "url": ("Uniform Resource Locator", "Web address"),
    "uri": ("Uniform Resource Identifier", "String identifying a resource"),
    "http": ("HyperText Transfer Protocol", "Protocol for web communication"),
    "https": ("HyperText Transfer Protocol Secure", "Secure web protocol"),
    "ftp": ("File Transfer Protocol", "Protocol for transferring files"),
    "ssh": ("Secure Shell", "Protocol for secure network access"),
    "vpn": ("Virtual Private Network", "Encrypted network connection"),
    "lan": ("Local Area Network", "Network in a limited area"),
    "wan": ("Wide Area Network", "Network covering large area"),
    "wifi": ("Wireless Fidelity", "Wireless local networking"),
    "sql": ("Structured Query Language", "Database query language"),
    "nosql": ("Not Only SQL", "Non-relational database systems"),
    "json": ("JavaScript Object Notation", "Data interchange format"),
    "xml": ("Extensible Markup Language", "Markup language for data"),
    "yaml": ("YAML Ain't Markup Language", "Human-readable data format"),
    "csv": ("Comma-Separated Values", "Plain text data format"),
    "pdf": ("Portable Document Format", "Document format by Adobe"),
    "jpeg": ("Joint Photographic Experts Group", "Image compression format"),
    "jpg": ("Joint Photographic Experts Group", "Image compression format"),
    "png": ("Portable Network Graphics", "Lossless image format"),
    "gif": ("Graphics Interchange Format", "Animated image format"),
    "svg": ("Scalable Vector Graphics", "Vector image format"),
    "mp3": ("MPEG Audio Layer 3", "Audio compression format"),
    "mp4": ("MPEG-4 Part 14", "Multimedia container format"),
    "ip": ("Internet Protocol", "Network addressing protocol"),
    "tcp": ("Transmission Control Protocol", "Network communication protocol"),
    "udp": ("User Datagram Protocol", "Fast network protocol"),
    "dns": ("Domain Name System", "Internet naming system"),
    "dhcp": ("Dynamic Host Configuration Protocol", "Network configuration protocol"),
    "ssl": ("Secure Sockets Layer", "Security protocol (deprecated)"),
    "tls": ("Transport Layer Security", "Security protocol"),
    "ai": ("Artificial Intelligence", "Machine intelligence"),
    "ml": ("Machine Learning", "Subset of AI using statistical learning"),
    "dl": ("Deep Learning", "Neural network-based machine learning"),
    "nlp": ("Natural Language Processing", "AI for understanding language"),
    "cv": ("Computer Vision", "AI for understanding images"),
    "llm": ("Large Language Model", "AI model trained on text data"),
    "gpt": ("Generative Pre-trained Transformer", "Type of language model"),
    "cnn": ("Convolutional Neural Network", "Neural network for images"),
    "rnn": ("Recurrent Neural Network", "Neural network for sequences"),
    "gan": ("Generative Adversarial Network", "Neural network for generation"),
    "os": ("Operating System", "System software managing hardware"),
    "ios": ("iPhone Operating System", "Apple mobile operating system"),
    "ide": ("Integrated Development Environment", "Software development tool"),
    "gui": ("Graphical User Interface", "Visual interface for users"),
    "cli": ("Command Line Interface", "Text-based interface"),
    "ux": ("User Experience", "Overall experience with product"),
    "ui": ("User Interface", "Point of interaction"),
    "crud": ("Create, Read, Update, Delete", "Basic database operations"),
    "rest": ("Representational State Transfer", "Web API architecture"),
    "ajax": ("Asynchronous JavaScript and XML", "Web development technique"),
    "mvc": ("Model-View-Controller", "Software design pattern"),
    "oop": ("Object-Oriented Programming", "Programming paradigm"),
    "agile": ("Agile Software Development", "Iterative development methodology"),
    "ci": ("Continuous Integration", "Automated code integration"),
    "cd": ("Continuous Deployment", "Automated deployment"),
    "devops": ("Development Operations", "Software delivery practices"),
    "saas": ("Software as a Service", "Cloud software delivery"),
    "paas": ("Platform as a Service", "Cloud platform delivery"),
    "iaas": ("Infrastructure as a Service", "Cloud infrastructure delivery"),
    "iot": ("Internet of Things", "Network of connected devices"),
    "ar": ("Augmented Reality", "Digital overlay on real world"),
    "vr": ("Virtual Reality", "Immersive digital environment"),
    "nft": ("Non-Fungible Token", "Unique digital asset"),
    "qr": ("Quick Response", "Type of barcode"),
    "aws": ("Amazon Web Services", "Cloud computing platform"),
    "gcp": ("Google Cloud Platform", "Cloud computing platform"),
    
    # Government & Organizations
    "nasa": ("National Aeronautics and Space Administration", "US space agency"),
    "esa": ("European Space Agency", "European space agency"),
    "fbi": ("Federal Bureau of Investigation", "US federal law enforcement"),
    "cia": ("Central Intelligence Agency", "US intelligence agency"),
    "nsa": ("National Security Agency", "US signals intelligence"),
    "dhs": ("Department of Homeland Security", "US security department"),
    "doj": ("Department of Justice", "US legal department"),
    "fda": ("Food and Drug Administration", "US food/drug regulator"),
    "cdc": ("Centers for Disease Control and Prevention", "US health agency"),
    "epa": ("Environmental Protection Agency", "US environmental regulator"),
    "sec": ("Securities and Exchange Commission", "US financial regulator"),
    "ftc": ("Federal Trade Commission", "US consumer protection"),
    "fcc": ("Federal Communications Commission", "US communications regulator"),
    "nist": ("National Institute of Standards and Technology", "US standards agency"),
    "iso": ("International Organization for Standardization", "International standards body"),
    "un": ("United Nations", "International organization"),
    "who": ("World Health Organization", "UN health agency"),
    "nato": ("North Atlantic Treaty Organization", "Military alliance"),
    "eu": ("European Union", "Political/economic union"),
    "opec": ("Organization of the Petroleum Exporting Countries", "Oil cartel"),
    "wto": ("World Trade Organization", "Trade organization"),
    
    # Biology & Chemistry
    "dna": ("Deoxyribonucleic Acid", "Molecule carrying genetic instructions"),
    "rna": ("Ribonucleic Acid", "Molecule essential for gene expression"),
    "atp": ("Adenosine Triphosphate", "Energy currency of cells"),
    "adp": ("Adenosine Diphosphate", "Product of ATP hydrolysis"),
    "mrna": ("Messenger RNA", "Carries genetic info from DNA to ribosomes"),
    "trna": ("Transfer RNA", "Brings amino acids to ribosome"),
    "rrna": ("Ribosomal RNA", "Component of ribosomes"),
    "gmo": ("Genetically Modified Organism", "Organism with altered DNA"),
    "pcr": ("Polymerase Chain Reaction", "DNA amplification technique"),
    "crispr": ("Clustered Regularly Interspaced Short Palindromic Repeats", "Gene editing technology"),
    "ph": ("Potential of Hydrogen", "Measure of acidity"),
    
    # Math & Science
    "si": ("International System of Units", "Modern metric system"),
    "mit": ("Massachusetts Institute of Technology", "Research university"),
    "caltech": ("California Institute of Technology", "Research university"),
    "ieee": ("Institute of Electrical and Electronics Engineers", "Professional association"),
    "acm": ("Association for Computing Machinery", "Computer science society"),
    "stem": ("Science, Technology, Engineering, Mathematics", "Academic disciplines"),
    "pi": ("π (pi)", "Ratio of circumference to diameter"),
    "sqrt": ("Square Root", "Mathematical function"),
    "sin": ("Sine", "Trigonometric function"),
    "cos": ("Cosine", "Trigonometric function"),
    "tan": ("Tangent", "Trigonometric function"),
    "log": ("Logarithm", "Inverse of exponentiation"),
    "ln": ("Natural Logarithm", "Logarithm base e"),
    
    # Economics & Business
    "gdp": ("Gross Domestic Product", "Total value of goods/services produced"),
    "gnp": ("Gross National Product", "Total value produced by residents"),
    "cpi": ("Consumer Price Index", "Measure of inflation"),
    "ppi": ("Producer Price Index", "Wholesale inflation measure"),
    "imf": ("International Monetary Fund", "International financial institution"),
    "fed": ("Federal Reserve", "US central bank"),
    "ecb": ("European Central Bank", "EU central bank"),
    "ipo": ("Initial Public Offering", "First stock sale to public"),
    "ceo": ("Chief Executive Officer", "Top executive"),
    "cfo": ("Chief Financial Officer", "Top financial executive"),
    "cto": ("Chief Technology Officer", "Top technology executive"),
    "coo": ("Chief Operating Officer", "Top operations executive"),
    "hr": ("Human Resources", "Personnel department"),
    "b2b": ("Business to Business", "Commerce between businesses"),
    "b2c": ("Business to Consumer", "Commerce with consumers"),
    "roi": ("Return on Investment", "Profitability measure"),
    "kpi": ("Key Performance Indicator", "Performance metric"),
    "etf": ("Exchange-Traded Fund", "Investment fund type"),
    "401k": ("401(k) Plan", "US retirement savings plan"),
    "ira": ("Individual Retirement Account", "US retirement account"),
    
    # Medical
    "cpr": ("Cardiopulmonary Resuscitation", "Emergency life-saving procedure"),
    "aed": ("Automated External Defibrillator", "Device to restore heart rhythm"),
    "mri": ("Magnetic Resonance Imaging", "Medical imaging technique"),
    "ct": ("Computed Tomography", "Medical imaging using X-rays"),
    "pet": ("Positron Emission Tomography", "Nuclear medicine imaging"),
    "ekg": ("Electrocardiogram", "Test measuring heart electrical activity"),
    "ecg": ("Electrocardiogram", "Test measuring heart electrical activity"),
    "eeg": ("Electroencephalogram", "Brain electrical activity test"),
    "emg": ("Electromyography", "Muscle electrical activity test"),
    "iv": ("Intravenous", "Delivery into veins"),
    "ed": ("Emergency Department", "Hospital emergency room"),
    "er": ("Emergency Room", "Hospital emergency department"),
    "icu": ("Intensive Care Unit", "Critical care hospital unit"),
    "bp": ("Blood Pressure", "Force of blood on vessel walls"),
    "bmi": ("Body Mass Index", "Weight-to-height ratio"),
    "hiv": ("Human Immunodeficiency Virus", "Virus causing AIDS"),
    "aids": ("Acquired Immunodeficiency Syndrome", "Disease caused by HIV"),
    "covid": ("Coronavirus Disease", "Disease caused by SARS-CoV-2"),
    "adhd": ("Attention Deficit Hyperactivity Disorder", "Neurodevelopmental disorder"),
    "ptsd": ("Post-Traumatic Stress Disorder", "Anxiety disorder"),
    "ocd": ("Obsessive-Compulsive Disorder", "Mental health condition"),
    
    # Military
    "awol": ("Absent Without Official Leave", "Unauthorized absence"),
    "pow": ("Prisoner of War", "Captured military personnel"),
    "mia": ("Missing in Action", "Unaccounted military personnel"),
    "kia": ("Killed in Action", "Died in combat"),
    "vet": ("Veteran", "Former military member"),
    
    # Common Abbreviations
    "asap": ("As Soon As Possible", "Immediately"),
    "fyi": ("For Your Information", "Informational note"),
    "etc": ("Et Cetera", "And so forth"),
    "vs": ("Versus", "Against"),
    "aka": ("Also Known As", "Alternative name"),
    "diy": ("Do It Yourself", "Self-made"),
    "faq": ("Frequently Asked Questions", "Common questions list"),
    "rsvp": ("Répondez S'il Vous Plaît", "Please respond"),
    "eta": ("Estimated Time of Arrival", "Expected arrival time"),
    "tbd": ("To Be Determined", "Not yet decided"),
    "tba": ("To Be Announced", "Not yet announced"),
    "n/a": ("Not Applicable", "Does not apply"),
    "dob": ("Date of Birth", "Birth date"),
    "ssn": ("Social Security Number", "US identification number"),
    "pin": ("Personal Identification Number", "Security code"),
    "atm": ("Automated Teller Machine", "Cash machine"),
    "gps": ("Global Positioning System", "Satellite navigation"),
    "am": ("Ante Meridiem", "Before noon"),
    "pm": ("Post Meridiem", "After noon"),
    "bc": ("Before Christ", "Years before year 1"),
    "ad": ("Anno Domini", "Years after year 1"),
    "bce": ("Before Common Era", "Secular BC"),
    "ce": ("Common Era", "Secular AD"),
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
# STATISTICS CONCEPTS
# Source: Standard statistics textbooks, NIST Handbook of Statistics
# ═══════════════════════════════════════════════════════════════════════════════

STATISTICS_CONCEPTS: Dict[str, tuple[str, str]] = {
    # Descriptive Statistics
    "mean": ("x̄ = Σx / n", "Average value - sum of all values divided by count"),
    "average": ("x̄ = Σx / n", "Mean - sum of all values divided by count"),
    "median": ("Middle value when sorted", "50th percentile - robust to outliers"),
    "mode": ("Most frequent value", "Value that appears most often in a dataset"),
    "standard deviation": ("σ = √(Σ(x - x̄)² / n)", "Measure of spread - average distance from the mean"),
    "std": ("σ = √(Σ(x - x̄)² / n)", "Standard deviation - measure of data spread"),
    "variance": ("σ² = Σ(x - x̄)² / n", "Square of standard deviation - average squared deviation from mean"),
    "range": ("max - min", "Difference between largest and smallest values"),
    "iqr": ("Q3 - Q1", "Interquartile range - spread of middle 50% of data"),
    "interquartile range": ("Q3 - Q1", "Difference between 75th and 25th percentiles"),
    "quartile": ("Q1=25%, Q2=50%, Q3=75%", "Values dividing data into four equal parts"),
    "percentile": ("Value below which X% of data falls", "E.g., 90th percentile means 90% of data is below"),
    
    # Robust Statistics
    "mad": ("MAD = median(|x - median(x)|)", "Median Absolute Deviation - robust measure of spread"),
    "median absolute deviation": ("MAD = median(|x - median(x)|)", "Robust alternative to standard deviation"),
    "trimmed mean": ("Mean after removing outliers", "Average computed after removing extreme values"),
    "winsorized mean": ("Mean with outliers capped", "Average where extremes are replaced with percentile values"),
    "robust mean": ("Outlier-resistant average", "Mean computed using robust methods (MAD-based)"),
    "outlier": ("Value far from typical data", "Usually defined as > 3 MAD or > 2-3 standard deviations"),
    
    # Hypothesis Testing
    "t-test": ("Compares means of two groups", "Tests if two sample means are significantly different"),
    "t test": ("Compares means of two groups", "Tests if two sample means are significantly different"),
    "p-value": ("Probability under null hypothesis", "Chance of observing data if null hypothesis is true"),
    "p value": ("Probability under null hypothesis", "Lower p-value = stronger evidence against null"),
    "null hypothesis": ("H₀: No effect/difference", "Assumption that there is no real effect"),
    "alternative hypothesis": ("H₁: Effect exists", "What we're trying to prove"),
    "significance level": ("α, typically 0.05", "Threshold for rejecting null hypothesis"),
    "alpha": ("α, typically 0.05", "Probability threshold for statistical significance"),
    "confidence interval": ("Range likely containing true value", "E.g., 95% CI means 95% confident true value is in range"),
    
    # Correlation & Regression
    "correlation": ("r = Σ((x-x̄)(y-ȳ)) / (n·σx·σy)", "Measure of linear relationship between variables (-1 to 1)"),
    "correlation coefficient": ("r ∈ [-1, 1]", "Strength and direction of linear relationship"),
    "pearson correlation": ("r = cov(X,Y) / (σx·σy)", "Most common correlation measure for continuous data"),
    "r-squared": ("R² = explained variance / total variance", "Proportion of variance explained by model (0 to 1)"),
    "r squared": ("R² ∈ [0, 1]", "Coefficient of determination - goodness of fit"),
    "linear regression": ("y = mx + b", "Fits a line to predict y from x"),
    "regression": ("y = β₀ + β₁x + ε", "Statistical model predicting outcome from predictors"),
    "slope": ("β₁ = Δy/Δx", "Change in y for one unit change in x"),
    "intercept": ("β₀ = y when x = 0", "Value of y when all predictors are zero"),
    
    # ANOVA
    "anova": ("Compares means across groups", "Analysis of Variance - tests if any group means differ"),
    "f-test": ("F = between-group variance / within-group variance", "Compares variances in ANOVA"),
    "f test": ("F = MSB / MSW", "Tests if variance between groups exceeds within groups"),
    
    # Distributions
    "normal distribution": ("Bell curve, μ and σ", "Symmetric distribution where mean = median = mode"),
    "gaussian": ("N(μ, σ²)", "Normal distribution - most common in nature"),
    "z-score": ("z = (x - μ) / σ", "Number of standard deviations from the mean"),
    "z score": ("z = (x - μ) / σ", "Standardized value showing distance from mean"),
    "chi-square": ("χ² test for categorical data", "Tests if observed frequencies match expected"),
    "chi square": ("χ² = Σ(O-E)²/E", "Compares observed vs expected frequencies"),
    
    # Time Series
    "moving average": ("Smoothed average over window", "Average of last n observations for trend detection"),
    "exponential smoothing": ("Weighted average favoring recent", "Gives more weight to recent observations"),
    "ar": ("AutoRegressive", "Model using past values to predict future"),
    "ma": ("Moving Average", "Model using past errors to predict future"),
    "arima": ("AutoRegressive Integrated Moving Average", "Model with differencing and ARMA components"),
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
    # Technology History
    "python created": ("1991", "Python programming language first released by Guido van Rossum"),
    "python released": ("1991", "Python 0.9.0 released February 1991"),
    "javascript created": ("1995", "JavaScript created by Brendan Eich at Netscape"),
    "java created": ("1995", "Java released by Sun Microsystems"),
    "c created": ("1972", "C programming language developed by Dennis Ritchie"),
    "c++ created": ("1983", "C++ developed by Bjarne Stroustrup"),
    "rust created": ("2010", "Rust programming language first appeared"),
    "go created": ("2009", "Go programming language released by Google"),
    "world wide web": ("1989", "World Wide Web invented by Tim Berners-Lee at CERN"),
    "internet created": ("1969", "ARPANET, precursor to internet, established"),
    "first iphone": ("2007", "Apple released the first iPhone on June 29, 2007"),
    "first android": ("2008", "First Android phone (HTC Dream) released October 2008"),
    "first computer": ("1946", "ENIAC, first general-purpose electronic computer, completed"),
    "first transistor": ("1947", "Transistor invented at Bell Labs"),
    "first microprocessor": ("1971", "Intel 4004, first commercial microprocessor"),
    "first email": ("1971", "First email sent by Ray Tomlinson"),
    "google founded": ("1998", "Google founded by Larry Page and Sergey Brin"),
    "facebook launched": ("2004", "Facebook launched by Mark Zuckerberg"),
    "twitter launched": ("2006", "Twitter launched"),
    "chatgpt released": ("2022", "ChatGPT released by OpenAI on November 30, 2022"),
    "first ai": ("1956", "Artificial Intelligence term coined at Dartmouth Conference"),
    
    # Space Exploration
    "moon landing": ("1969", "Apollo 11 landed on the Moon on July 20, 1969"),
    "apollo 11": ("1969", "First humans walked on the Moon, July 20, 1969"),
    "first satellite": ("1957", "Sputnik 1, first artificial satellite, launched October 4, 1957"),
    "sputnik launched": ("1957", "Soviet Union launched Sputnik 1"),
    "first human in space": ("1961", "Yuri Gagarin became first human in space, April 12, 1961"),
    "yuri gagarin": ("1961", "First human in space, April 12, 1961"),
    "first spacewalk": ("1965", "Alexei Leonov performed first spacewalk"),
    "mars rover landing": ("1997", "Mars Pathfinder landed with Sojourner rover"),
    "hubble launched": ("1990", "Hubble Space Telescope launched April 24, 1990"),
    "james webb launched": ("2021", "James Webb Space Telescope launched December 25, 2021"),
    "iss completed": ("2011", "International Space Station assembly completed"),
    "challenger disaster": ("1986", "Space Shuttle Challenger disaster, January 28, 1986"),
    "columbia disaster": ("2003", "Space Shuttle Columbia disaster, February 1, 2003"),
    
    # World Wars
    "wwi started": ("1914", "World War I began July 28, 1914"),
    "world war i start": ("1914", "World War I began July 28, 1914"),
    "wwi ended": ("1918", "World War I ended November 11, 1918"),
    "world war i end": ("1918", "World War I ended November 11, 1918"),
    "wwii started": ("1939", "World War II began September 1, 1939"),
    "world war ii start": ("1939", "World War II began September 1, 1939"),
    "wwii ended": ("1945", "World War II ended September 2, 1945"),
    "world war ii end": ("1945", "World War II ended September 2, 1945"),
    "world war 2 end": ("1945", "World War II ended September 2, 1945"),
    "ww2 ended": ("1945", "World War II ended September 2, 1945"),
    "d-day": ("1944", "D-Day invasion of Normandy, June 6, 1944"),
    "pearl harbor": ("1941", "Attack on Pearl Harbor, December 7, 1941"),
    "hiroshima": ("1945", "Atomic bomb dropped on Hiroshima, August 6, 1945"),
    "nagasaki": ("1945", "Atomic bomb dropped on Nagasaki, August 9, 1945"),
    "vj day": ("1945", "Victory over Japan Day, August 15, 1945"),
    "ve day": ("1945", "Victory in Europe Day, May 8, 1945"),
    
    # American History
    "declaration of independence": ("1776", "US Declaration of Independence signed July 4, 1776"),
    "american independence": ("1776", "United States declared independence July 4, 1776"),
    "us constitution": ("1787", "US Constitution signed September 17, 1787"),
    "bill of rights": ("1791", "US Bill of Rights ratified December 15, 1791"),
    "civil war started": ("1861", "American Civil War began April 12, 1861"),
    "civil war ended": ("1865", "American Civil War ended April 9, 1865"),
    "slavery abolished": ("1865", "13th Amendment abolished slavery in US"),
    "emancipation proclamation": ("1863", "Emancipation Proclamation issued January 1, 1863"),
    "lincoln assassination": ("1865", "Abraham Lincoln assassinated April 14, 1865"),
    "kennedy assassination": ("1963", "JFK assassinated November 22, 1963"),
    "mlk assassination": ("1968", "Martin Luther King Jr. assassinated April 4, 1968"),
    "i have a dream": ("1963", "MLK's 'I Have a Dream' speech, August 28, 1963"),
    "september 11": ("2001", "9/11 terrorist attacks, September 11, 2001"),
    "9/11": ("2001", "Terrorist attacks on World Trade Center and Pentagon"),
    
    # European History
    "french revolution": ("1789", "French Revolution began July 14, 1789"),
    "bastille day": ("1789", "Storming of the Bastille, July 14, 1789"),
    "napoleon defeated": ("1815", "Napoleon defeated at Waterloo, June 18, 1815"),
    "berlin wall built": ("1961", "Berlin Wall construction began August 13, 1961"),
    "berlin wall fall": ("1989", "Berlin Wall fell on November 9, 1989"),
    "berlin wall fell": ("1989", "Berlin Wall fell on November 9, 1989"),
    "soviet union collapse": ("1991", "Soviet Union dissolved December 26, 1991"),
    "ussr collapse": ("1991", "USSR officially dissolved December 26, 1991"),
    "russian revolution": ("1917", "Russian Revolution, October 1917"),
    "magna carta": ("1215", "Magna Carta signed June 15, 1215"),
    "black death": ("1347", "Black Death reached Europe in 1347"),
    "renaissance began": ("1400", "Renaissance period began in Italy ~1400"),
    "printing press invented": ("1440", "Gutenberg printing press invented ~1440"),
    "columbus america": ("1492", "Christopher Columbus reached Americas October 12, 1492"),
    "brexit": ("2020", "UK officially left the European Union January 31, 2020"),
    
    # Ancient History
    "rome founded": ("-753", "Rome traditionally founded 753 BC"),
    "rome fell": ("476", "Fall of Western Roman Empire, 476 AD"),
    "pyramids built": ("-2560", "Great Pyramid of Giza built ~2560 BC"),
    "alexander died": ("-323", "Alexander the Great died 323 BC"),
    "jesus birth": ("0", "Traditional year of Jesus Christ's birth"),
    "muhammad born": ("570", "Prophet Muhammad born ~570 AD"),
    "buddha born": ("-563", "Siddhartha Gautama (Buddha) born ~563 BC"),
    
    # Science & Medicine
    "penicillin discovered": ("1928", "Alexander Fleming discovered penicillin"),
    "dna structure": ("1953", "Watson and Crick discovered DNA structure"),
    "theory of relativity": ("1905", "Einstein published special relativity"),
    "general relativity": ("1915", "Einstein published general relativity"),
    "theory of evolution": ("1859", "Darwin published Origin of Species"),
    "electricity discovered": ("1752", "Benjamin Franklin's kite experiment"),
    "x-rays discovered": ("1895", "Wilhelm Röntgen discovered X-rays"),
    "first vaccine": ("1796", "Edward Jenner developed smallpox vaccine"),
    "covid pandemic": ("2020", "COVID-19 pandemic began in early 2020"),
    "first covid vaccine": ("2020", "First COVID-19 vaccines approved December 2020"),
    
    # Civil Rights & Social
    "women suffrage us": ("1920", "19th Amendment gave US women right to vote"),
    "civil rights act": ("1964", "Civil Rights Act signed July 2, 1964"),
    "apartheid ended": ("1994", "Apartheid ended in South Africa"),
    "mandela freed": ("1990", "Nelson Mandela released from prison February 11, 1990"),
    "mandela president": ("1994", "Nelson Mandela became South Africa's first Black president"),
    
    # Modern Events
    "titanic sank": ("1912", "RMS Titanic sank April 15, 1912"),
    "hindenburg disaster": ("1937", "Hindenburg airship disaster May 6, 1937"),
    "chernobyl disaster": ("1986", "Chernobyl nuclear disaster April 26, 1986"),
    "fukushima disaster": ("2011", "Fukushima nuclear disaster March 11, 2011"),
    "first world cup": ("1930", "First FIFA World Cup held in Uruguay"),
    "first olympics modern": ("1896", "First modern Olympics held in Athens"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# COMPANY/ORGANIZATION FACTS
# Source: Official company records, SEC filings
# ═══════════════════════════════════════════════════════════════════════════════

COMPANY_FACTS: Dict[str, Dict[str, Any]] = {
    # Big Tech
    "apple": {
        "founded": "1976",
        "founders": ["Steve Jobs", "Steve Wozniak", "Ronald Wayne"],
        "headquarters": "Cupertino, California",
        "ceo": "Tim Cook",
        "industry": "Technology",
    },
    "microsoft": {
        "founded": "1975",
        "founders": ["Bill Gates", "Paul Allen"],
        "headquarters": "Redmond, Washington",
        "ceo": "Satya Nadella",
        "industry": "Technology",
    },
    "google": {
        "founded": "1998",
        "founders": ["Larry Page", "Sergey Brin"],
        "headquarters": "Mountain View, California",
        "parent": "Alphabet Inc.",
        "industry": "Technology",
    },
    "alphabet": {
        "founded": "2015",
        "founders": ["Larry Page", "Sergey Brin"],
        "headquarters": "Mountain View, California",
        "subsidiaries": ["Google", "YouTube", "Waymo", "DeepMind"],
        "industry": "Technology",
    },
    "amazon": {
        "founded": "1994",
        "founders": ["Jeff Bezos"],
        "headquarters": "Seattle, Washington",
        "ceo": "Andy Jassy",
        "industry": "E-commerce, Cloud Computing",
    },
    "meta": {
        "founded": "2004",
        "founders": ["Mark Zuckerberg", "Eduardo Saverin", "Andrew McCollum", "Dustin Moskovitz", "Chris Hughes"],
        "headquarters": "Menlo Park, California",
        "formerly": "Facebook",
        "ceo": "Mark Zuckerberg",
        "industry": "Social Media",
    },
    "facebook": {
        "founded": "2004",
        "founders": ["Mark Zuckerberg"],
        "headquarters": "Menlo Park, California",
        "now_called": "Meta",
        "industry": "Social Media",
    },
    
    # AI Companies
    "anthropic": {
        "founded": "2021",
        "founders": ["Dario Amodei", "Daniela Amodei"],
        "headquarters": "San Francisco, California",
        "known_for": "Claude AI assistant",
        "industry": "Artificial Intelligence",
    },
    "openai": {
        "founded": "2015",
        "founders": ["Sam Altman", "Elon Musk", "Greg Brockman", "Ilya Sutskever", "Wojciech Zaremba", "John Schulman"],
        "headquarters": "San Francisco, California",
        "known_for": "ChatGPT, GPT-4, DALL-E",
        "ceo": "Sam Altman",
        "industry": "Artificial Intelligence",
    },
    "deepmind": {
        "founded": "2010",
        "founders": ["Demis Hassabis", "Shane Legg", "Mustafa Suleyman"],
        "headquarters": "London, England",
        "parent": "Alphabet Inc.",
        "known_for": "AlphaGo, AlphaFold",
        "industry": "Artificial Intelligence",
    },
    "nvidia": {
        "founded": "1993",
        "founders": ["Jensen Huang", "Chris Malachowsky", "Curtis Priem"],
        "headquarters": "Santa Clara, California",
        "ceo": "Jensen Huang",
        "known_for": "GPUs, AI chips",
        "industry": "Semiconductors",
    },
    
    # Electric Vehicles & Space
    "tesla": {
        "founded": "2003",
        "founders": ["Martin Eberhard", "Marc Tarpenning"],
        "headquarters": "Austin, Texas",
        "ceo": "Elon Musk",
        "industry": "Electric Vehicles, Energy",
    },
    "spacex": {
        "founded": "2002",
        "founders": ["Elon Musk"],
        "headquarters": "Hawthorne, California",
        "ceo": "Elon Musk",
        "known_for": "Falcon 9, Starship, Starlink",
        "industry": "Aerospace",
    },
    "rivian": {
        "founded": "2009",
        "founders": ["RJ Scaringe"],
        "headquarters": "Irvine, California",
        "industry": "Electric Vehicles",
    },
    "lucid": {
        "founded": "2007",
        "founders": ["Sam Weng", "Bernard Tse"],
        "headquarters": "Newark, California",
        "industry": "Electric Vehicles",
    },
    
    # Social Media & Entertainment
    "twitter": {
        "founded": "2006",
        "founders": ["Jack Dorsey", "Noah Glass", "Biz Stone", "Evan Williams"],
        "headquarters": "San Francisco, California",
        "now_called": "X",
        "industry": "Social Media",
    },
    "x": {
        "founded": "2006",
        "formerly": "Twitter",
        "headquarters": "San Francisco, California",
        "owner": "Elon Musk",
        "industry": "Social Media",
    },
    "netflix": {
        "founded": "1997",
        "founders": ["Reed Hastings", "Marc Randolph"],
        "headquarters": "Los Gatos, California",
        "ceo": "Ted Sarandos, Greg Peters",
        "industry": "Streaming",
    },
    "spotify": {
        "founded": "2006",
        "founders": ["Daniel Ek", "Martin Lorentzon"],
        "headquarters": "Stockholm, Sweden",
        "ceo": "Daniel Ek",
        "industry": "Music Streaming",
    },
    "tiktok": {
        "founded": "2016",
        "parent": "ByteDance",
        "headquarters": "Los Angeles, California (US), Singapore",
        "industry": "Social Media",
    },
    "bytedance": {
        "founded": "2012",
        "founders": ["Zhang Yiming"],
        "headquarters": "Beijing, China",
        "known_for": "TikTok, Douyin",
        "industry": "Technology",
    },
    "snapchat": {
        "founded": "2011",
        "founders": ["Evan Spiegel", "Bobby Murphy", "Reggie Brown"],
        "headquarters": "Santa Monica, California",
        "parent": "Snap Inc.",
        "industry": "Social Media",
    },
    "discord": {
        "founded": "2015",
        "founders": ["Jason Citron", "Stan Vishnevskiy"],
        "headquarters": "San Francisco, California",
        "industry": "Communication",
    },
    "reddit": {
        "founded": "2005",
        "founders": ["Steve Huffman", "Alexis Ohanian"],
        "headquarters": "San Francisco, California",
        "ceo": "Steve Huffman",
        "industry": "Social Media",
    },
    "linkedin": {
        "founded": "2002",
        "founders": ["Reid Hoffman", "Allen Blue", "Konstantin Guericke", "Eric Ly", "Jean-Luc Vaillant"],
        "headquarters": "Sunnyvale, California",
        "parent": "Microsoft",
        "industry": "Professional Networking",
    },
    "pinterest": {
        "founded": "2009",
        "founders": ["Ben Silbermann", "Paul Sciarra", "Evan Sharp"],
        "headquarters": "San Francisco, California",
        "industry": "Social Media",
    },
    "youtube": {
        "founded": "2005",
        "founders": ["Chad Hurley", "Steve Chen", "Jawed Karim"],
        "headquarters": "San Bruno, California",
        "parent": "Google/Alphabet",
        "industry": "Video Streaming",
    },
    
    # E-commerce & Retail
    "ebay": {
        "founded": "1995",
        "founders": ["Pierre Omidyar"],
        "headquarters": "San Jose, California",
        "industry": "E-commerce",
    },
    "shopify": {
        "founded": "2006",
        "founders": ["Tobias Lütke", "Daniel Weinand", "Scott Lake"],
        "headquarters": "Ottawa, Canada",
        "industry": "E-commerce",
    },
    "alibaba": {
        "founded": "1999",
        "founders": ["Jack Ma"],
        "headquarters": "Hangzhou, China",
        "industry": "E-commerce",
    },
    "walmart": {
        "founded": "1962",
        "founders": ["Sam Walton"],
        "headquarters": "Bentonville, Arkansas",
        "industry": "Retail",
    },
    "costco": {
        "founded": "1983",
        "founders": ["James Sinegal", "Jeffrey Brotman"],
        "headquarters": "Issaquah, Washington",
        "industry": "Retail",
    },
    "target": {
        "founded": "1902",
        "founders": ["George Dayton"],
        "headquarters": "Minneapolis, Minnesota",
        "industry": "Retail",
    },
    
    # Finance & Payments
    "paypal": {
        "founded": "1998",
        "founders": ["Peter Thiel", "Max Levchin", "Luke Nosek", "Elon Musk"],
        "headquarters": "San Jose, California",
        "industry": "Fintech",
    },
    "stripe": {
        "founded": "2010",
        "founders": ["Patrick Collison", "John Collison"],
        "headquarters": "San Francisco, California",
        "industry": "Fintech",
    },
    "square": {
        "founded": "2009",
        "founders": ["Jack Dorsey", "Jim McKelvey"],
        "headquarters": "San Francisco, California",
        "now_called": "Block",
        "industry": "Fintech",
    },
    "block": {
        "founded": "2009",
        "founders": ["Jack Dorsey", "Jim McKelvey"],
        "headquarters": "San Francisco, California",
        "formerly": "Square",
        "industry": "Fintech",
    },
    "visa": {
        "founded": "1958",
        "headquarters": "San Francisco, California",
        "industry": "Financial Services",
    },
    "mastercard": {
        "founded": "1966",
        "headquarters": "Purchase, New York",
        "industry": "Financial Services",
    },
    "coinbase": {
        "founded": "2012",
        "founders": ["Brian Armstrong", "Fred Ehrsam"],
        "headquarters": "San Francisco, California",
        "industry": "Cryptocurrency",
    },
    "robinhood": {
        "founded": "2013",
        "founders": ["Vlad Tenev", "Baiju Bhatt"],
        "headquarters": "Menlo Park, California",
        "industry": "Fintech",
    },
    
    # Enterprise Software
    "salesforce": {
        "founded": "1999",
        "founders": ["Marc Benioff", "Parker Harris"],
        "headquarters": "San Francisco, California",
        "ceo": "Marc Benioff",
        "industry": "Enterprise Software",
    },
    "oracle": {
        "founded": "1977",
        "founders": ["Larry Ellison", "Bob Miner", "Ed Oates"],
        "headquarters": "Austin, Texas",
        "ceo": "Safra Catz",
        "industry": "Enterprise Software",
    },
    "sap": {
        "founded": "1972",
        "founders": ["Dietmar Hopp", "Hasso Plattner", "Claus Wellenreuther", "Klaus Tschira", "Hans-Werner Hector"],
        "headquarters": "Walldorf, Germany",
        "industry": "Enterprise Software",
    },
    "adobe": {
        "founded": "1982",
        "founders": ["John Warnock", "Charles Geschke"],
        "headquarters": "San Jose, California",
        "known_for": "Photoshop, Acrobat, Creative Cloud",
        "industry": "Software",
    },
    "ibm": {
        "founded": "1911",
        "headquarters": "Armonk, New York",
        "industry": "Technology",
        "known_for": "Mainframes, Watson",
    },
    "intel": {
        "founded": "1968",
        "founders": ["Gordon Moore", "Robert Noyce"],
        "headquarters": "Santa Clara, California",
        "industry": "Semiconductors",
    },
    "amd": {
        "founded": "1969",
        "founders": ["Jerry Sanders"],
        "headquarters": "Santa Clara, California",
        "industry": "Semiconductors",
    },
    "cisco": {
        "founded": "1984",
        "founders": ["Leonard Bosack", "Sandy Lerner"],
        "headquarters": "San Jose, California",
        "industry": "Networking",
    },
    "vmware": {
        "founded": "1998",
        "founders": ["Diane Greene", "Mendel Rosenblum", "Scott Devine", "Edward Wang", "Edouard Bugnion"],
        "headquarters": "Palo Alto, California",
        "industry": "Software",
    },
    "zoom": {
        "founded": "2011",
        "founders": ["Eric Yuan"],
        "headquarters": "San Jose, California",
        "ceo": "Eric Yuan",
        "industry": "Communication",
    },
    "slack": {
        "founded": "2009",
        "founders": ["Stewart Butterfield", "Eric Costello", "Cal Henderson", "Serguei Mourachov"],
        "headquarters": "San Francisco, California",
        "parent": "Salesforce",
        "industry": "Communication",
    },
    "dropbox": {
        "founded": "2007",
        "founders": ["Drew Houston", "Arash Ferdowsi"],
        "headquarters": "San Francisco, California",
        "industry": "Cloud Storage",
    },
    "atlassian": {
        "founded": "2002",
        "founders": ["Mike Cannon-Brookes", "Scott Farquhar"],
        "headquarters": "Sydney, Australia",
        "known_for": "Jira, Confluence, Trello",
        "industry": "Software",
    },
    "github": {
        "founded": "2008",
        "founders": ["Tom Preston-Werner", "Chris Wanstrath", "PJ Hyett", "Scott Chacon"],
        "headquarters": "San Francisco, California",
        "parent": "Microsoft",
        "industry": "Software Development",
    },
    "gitlab": {
        "founded": "2011",
        "founders": ["Dmitriy Zaporozhets", "Sid Sijbrandij"],
        "headquarters": "San Francisco, California",
        "industry": "Software Development",
    },
    
    # Ride-sharing & Delivery
    "uber": {
        "founded": "2009",
        "founders": ["Travis Kalanick", "Garrett Camp"],
        "headquarters": "San Francisco, California",
        "ceo": "Dara Khosrowshahi",
        "industry": "Transportation",
    },
    "lyft": {
        "founded": "2012",
        "founders": ["Logan Green", "John Zimmer"],
        "headquarters": "San Francisco, California",
        "industry": "Transportation",
    },
    "doordash": {
        "founded": "2013",
        "founders": ["Tony Xu", "Stanley Tang", "Andy Fang", "Evan Moore"],
        "headquarters": "San Francisco, California",
        "industry": "Food Delivery",
    },
    "instacart": {
        "founded": "2012",
        "founders": ["Apoorva Mehta", "Max Mullen", "Brandon Leonardo"],
        "headquarters": "San Francisco, California",
        "industry": "Grocery Delivery",
    },
    "airbnb": {
        "founded": "2008",
        "founders": ["Brian Chesky", "Joe Gebbia", "Nathan Blecharczyk"],
        "headquarters": "San Francisco, California",
        "ceo": "Brian Chesky",
        "industry": "Hospitality",
    },
    
    # Gaming
    "nintendo": {
        "founded": "1889",
        "founders": ["Fusajiro Yamauchi"],
        "headquarters": "Kyoto, Japan",
        "known_for": "Mario, Zelda, Switch",
        "industry": "Gaming",
    },
    "sony": {
        "founded": "1946",
        "founders": ["Masaru Ibuka", "Akio Morita"],
        "headquarters": "Tokyo, Japan",
        "known_for": "PlayStation, Electronics",
        "industry": "Electronics, Gaming",
    },
    "activision": {
        "founded": "1979",
        "founders": ["David Crane", "Larry Kaplan", "Alan Miller", "Bob Whitehead"],
        "headquarters": "Santa Monica, California",
        "parent": "Microsoft",
        "industry": "Gaming",
    },
    "electronic arts": {
        "founded": "1982",
        "founders": ["Trip Hawkins"],
        "headquarters": "Redwood City, California",
        "known_for": "FIFA, Madden, The Sims",
        "industry": "Gaming",
    },
    "ea": {
        "founded": "1982",
        "founders": ["Trip Hawkins"],
        "headquarters": "Redwood City, California",
        "full_name": "Electronic Arts",
        "industry": "Gaming",
    },
    "epic games": {
        "founded": "1991",
        "founders": ["Tim Sweeney"],
        "headquarters": "Cary, North Carolina",
        "known_for": "Fortnite, Unreal Engine",
        "industry": "Gaming",
    },
    "valve": {
        "founded": "1996",
        "founders": ["Gabe Newell", "Mike Harrington"],
        "headquarters": "Bellevue, Washington",
        "known_for": "Steam, Half-Life, Portal",
        "industry": "Gaming",
    },
    "roblox": {
        "founded": "2004",
        "founders": ["David Baszucki", "Erik Cassel"],
        "headquarters": "San Mateo, California",
        "industry": "Gaming",
    },
    
    # Automotive
    "ford": {
        "founded": "1903",
        "founders": ["Henry Ford"],
        "headquarters": "Dearborn, Michigan",
        "industry": "Automotive",
    },
    "general motors": {
        "founded": "1908",
        "founders": ["William C. Durant"],
        "headquarters": "Detroit, Michigan",
        "industry": "Automotive",
    },
    "gm": {
        "founded": "1908",
        "full_name": "General Motors",
        "headquarters": "Detroit, Michigan",
        "industry": "Automotive",
    },
    "toyota": {
        "founded": "1937",
        "founders": ["Kiichiro Toyoda"],
        "headquarters": "Toyota City, Japan",
        "industry": "Automotive",
    },
    "volkswagen": {
        "founded": "1937",
        "headquarters": "Wolfsburg, Germany",
        "industry": "Automotive",
    },
    "bmw": {
        "founded": "1916",
        "headquarters": "Munich, Germany",
        "full_name": "Bayerische Motoren Werke",
        "industry": "Automotive",
    },
    "mercedes-benz": {
        "founded": "1926",
        "headquarters": "Stuttgart, Germany",
        "parent": "Mercedes-Benz Group",
        "industry": "Automotive",
    },
    
    # Aerospace
    "boeing": {
        "founded": "1916",
        "founders": ["William Boeing"],
        "headquarters": "Arlington, Virginia",
        "industry": "Aerospace",
    },
    "lockheed martin": {
        "founded": "1995",
        "headquarters": "Bethesda, Maryland",
        "industry": "Aerospace, Defense",
    },
    "northrop grumman": {
        "founded": "1994",
        "headquarters": "Falls Church, Virginia",
        "industry": "Aerospace, Defense",
    },
    "blue origin": {
        "founded": "2000",
        "founders": ["Jeff Bezos"],
        "headquarters": "Kent, Washington",
        "industry": "Aerospace",
    },
    
    # Healthcare & Pharma
    "pfizer": {
        "founded": "1849",
        "founders": ["Charles Pfizer", "Charles Erhart"],
        "headquarters": "New York City, New York",
        "industry": "Pharmaceuticals",
    },
    "johnson & johnson": {
        "founded": "1886",
        "founders": ["Robert Wood Johnson I", "James Wood Johnson", "Edward Mead Johnson"],
        "headquarters": "New Brunswick, New Jersey",
        "industry": "Healthcare",
    },
    "moderna": {
        "founded": "2010",
        "founders": ["Derrick Rossi", "Noubar Afeyan", "Robert Langer", "Kenneth Chien"],
        "headquarters": "Cambridge, Massachusetts",
        "known_for": "mRNA vaccines",
        "industry": "Biotechnology",
    },
    
    # Food & Beverage
    "coca-cola": {
        "founded": "1892",
        "founders": ["Asa Griggs Candler"],
        "headquarters": "Atlanta, Georgia",
        "industry": "Beverages",
    },
    "pepsi": {
        "founded": "1898",
        "founders": ["Caleb Bradham"],
        "headquarters": "Purchase, New York",
        "parent": "PepsiCo",
        "industry": "Beverages",
    },
    "pepsico": {
        "founded": "1965",
        "headquarters": "Purchase, New York",
        "industry": "Food & Beverages",
    },
    "mcdonald's": {
        "founded": "1940",
        "founders": ["Richard McDonald", "Maurice McDonald"],
        "headquarters": "Chicago, Illinois",
        "industry": "Fast Food",
    },
    "starbucks": {
        "founded": "1971",
        "founders": ["Jerry Baldwin", "Zev Siegl", "Gordon Bowker"],
        "headquarters": "Seattle, Washington",
        "industry": "Coffee",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeBase:
    """
    Pre-verified knowledge base for instant fact retrieval.
    No LLM needed for known facts.
    
    Search Strategy (Five-Tier Kinematic Semantics):
    0. SHARED STORE: Check dynamically added facts (~0ms)
    1. SHAPE: Kinematic query parsing (~0ms) - questions as equations
    2. SEMANTIC: Datamuse semantic field resolution (~200ms) - when patterns miss
    3. KEYWORD: Traditional keyword matching (~1ms) - fallback
    4. EMBEDDING: Vector search (~100ms) - last resort
    
    "The question has shape. The KB has shape. Match shapes, fill slots."
    """
    
    CIA_FACTBOOK_URL = "https://www.cia.gov/the-world-factbook/"
    NIST_URL = "https://www.nist.gov/pml/fundamental-physical-constants"
    
    def __init__(self):
        self.queries = 0
        self.hits = 0
        self.store_hits = 0       # Tier 0: Shared knowledge store
        self.shape_hits = 0       # Tier 1: Kinematic parser
        self.semantic_hits = 0    # Tier 2: Datamuse semantic fields
        self.keyword_hits = 0     # Tier 3: Traditional keyword matching
        self.typo_corrections = 0
        
        # Initialize shared knowledge store (Tier 0) - dynamically added facts
        self._store = get_knowledge_store() if HAS_KNOWLEDGE_STORE else None
        
        # Initialize language mechanics if available
        self._lm = get_language_mechanics() if HAS_LANGUAGE_MECHANICS else None
        
        # Initialize kinematic query parser (Tier 1)
        self._parser = get_query_parser() if HAS_QUERY_PARSER else None
        
        # Initialize semantic resolver (Tier 2) - Datamuse semantic fields
        self._semantic = SemanticResolver() if HAS_SEMANTIC_RESOLVER else None
    
    def query(self, question: str) -> Optional[VerifiedFact]:
        """
        Query the knowledge base for a verified fact.
        Returns None if fact not found.
        
        Kinematic Query Pipeline (Priority Order):
        1. SHAPE: Kinematic query parsing (~0ms) - questions as equations
        2. CURATED: Hand-verified facts (scientific, geography, etc.) - HIGHEST trust
        3. SEMANTIC: Datamuse semantic field resolution (~200ms)
        4. STORE: Shared knowledge store - dynamically added facts (lower trust)
        
        'The question has shape. The KB has shape. Match shapes, fill slots.'
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
        # TIER 2: CURATED KEYWORD MATCHING (~1ms)
        # Hand-verified facts from CIA Factbook, NIST, etc. - HIGHEST TRUST
        # These MUST come before fuzzy Wikipedia matches
        # ═══════════════════════════════════════════════════════════════════════
        result = (
            self._query_capital(question_lower) or
            self._query_geographic_misconception(question_lower) or
            self._query_population(question_lower) or
            self._query_language(question_lower) or
            self._query_currency(question_lower) or
            self._query_scientific(question_lower) or
            self._query_statistics(question_lower) or
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
        # TIER 3: SEMANTIC FIELD RESOLUTION (~200ms)
        # "Beauty is in the eye of the beholder - meaning is contextual overlap."
        # ═══════════════════════════════════════════════════════════════════════
        if self._semantic:
            result = self._query_by_semantic_field(question, question_lower)
            if result:
                self.hits += 1
                self.semantic_hits += 1
                return result
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 4: SHARED KNOWLEDGE STORE (~5ms)
        # Dynamically added facts from Adanpedia, Wikipedia imports
        # LOWER TRUST - only after curated facts fail
        # ═══════════════════════════════════════════════════════════════════════
        if self._store:
            result = self._query_shared_store(question, question_lower)
            if result:
                self.hits += 1
                self.store_hits += 1
                return result
        
        # ═══════════════════════════════════════════════════════════════════════
        # TIER 5: WIKIPEDIA FACTS (~1ms)
        # Auto-scraped Wikipedia facts - LOWEST priority
        # ═══════════════════════════════════════════════════════════════════════
        result = self._query_wikipedia(question_lower)
        if result:
            self.hits += 1
            self.keyword_hits += 1
            return result
        
        # No match found - LLM fallback would happen at agent level
        return None
    
    def _query_shared_store(self, question: str, question_lower: str) -> Optional[VerifiedFact]:
        """
        Tier 0: Query the shared knowledge store for dynamically added facts.
        These are facts added via Adanpedia, Wikipedia imports, or other sources.
        
        IMPORTANT: Only return results with STRONG relevance.
        Low-quality fuzzy matches cause wrong answers.
        """
        if not self._store:
            return None
        
        # Extract key terms from the question
        # Try common patterns: "What is X?", "Tell me about X", etc.
        key_patterns = [
            r"what is (?:the )?(.+?)[\?\.]?$",
            r"tell me about (.+?)[\?\.]?$",
            r"who is (.+?)[\?\.]?$",
            r"when was (.+?)[\?\.]?$",
            r"where is (.+?)[\?\.]?$",
            r"(.+?)[\?\.]?$",  # Fallback: just the question
        ]
        
        search_terms = []
        for pattern in key_patterns:
            match = re.match(pattern, question_lower)
            if match:
                term = match.group(1).strip()
                if term and len(term) > 2:
                    search_terms.append(term)
                    break
        
        # Also add the raw question
        search_terms.append(question_lower)
        
        # Search the store - use HIGH threshold to avoid irrelevant matches
        for term in search_terms:
            # First try exact key match
            stored = self._store.get(term)
            if stored:
                return VerifiedFact(
                    fact=stored.fact,
                    category=stored.category,
                    source=stored.source,
                    source_url=stored.source_url,
                    confidence=stored.confidence
                )
            
            # Search with strict threshold (0.85) and validate relevance
            results = self._store.search(term, limit=3, threshold=0.85)
            if results:
                # Additional relevance check: key words from query must appear in fact
                term_words = set(term.split())
                for stored in results:
                    fact_lower = stored.fact.lower()
                    key_lower = stored.key.lower()
                    # At least 50% of query words must appear in fact or key
                    matching_words = sum(1 for w in term_words if w in fact_lower or w in key_lower)
                    if len(term_words) > 0 and matching_words / len(term_words) >= 0.5:
                        return VerifiedFact(
                            fact=stored.fact,
                            category=stored.category,
                            source=stored.source,
                            source_url=stored.source_url,
                            confidence=stored.confidence
                        )
        
        return None
    
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
    
    def _query_statistics(self, question: str) -> Optional[VerifiedFact]:
        """Query for statistics concepts and definitions."""
        # Check for statistics-related keywords
        if not any(word in question for word in [
            "mean", "median", "mode", "standard deviation", "std", "variance",
            "average", "correlation", "regression", "t-test", "t test", "anova",
            "p-value", "p value", "confidence", "hypothesis", "outlier", "mad",
            "quartile", "percentile", "iqr", "z-score", "z score", "r-squared",
            "r squared", "chi-square", "chi square", "f-test", "f test",
            "normal distribution", "gaussian", "statistics", "statistical"
        ]):
            return None
        
        for concept, (formula, description) in STATISTICS_CONCEPTS.items():
            if concept in question:
                return VerifiedFact(
                    fact=f"{formula}. {description}",
                    category="statistics",
                    source="NIST Handbook of Statistics",
                    source_url="https://www.itl.nist.gov/div898/handbook/",
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
    
    def _query_wikipedia(self, question: str) -> Optional[VerifiedFact]:
        """
        Query the Wikipedia facts database (auto-scraped).
        
        These facts are scraped from Wikipedia using the Newton Wiki Scraper
        with diff-based deduplication. They extend the main KB with additional
        knowledge from Wikipedia's vast corpus.
        
        IMPORTANT: Only return results with STRONG relevance (>= 3 word overlap).
        """
        if not HAS_WIKIPEDIA_FACTS or not WIKIPEDIA_FACTS:
            return None
        
        question_words = set(w for w in question.split() if len(w) > 2)
        
        # Try direct key match first (must have 3+ common words)
        for key, (fact, category, url) in WIKIPEDIA_FACTS.items():
            key_lower = key.lower()
            key_words = set(w for w in key_lower.split() if len(w) > 2)
            
            # Strong match: key contained in question or vice versa
            if key_lower in question and len(key_lower) > 5:
                return VerifiedFact(
                    fact=fact,
                    category=category,
                    source="Wikipedia (auto-scraped)",
                    source_url=url,
                    confidence=0.85,
                )
            
            # Word overlap: at least 3 words in common
            overlap = len(question_words & key_words)
            if overlap >= 3:
                return VerifiedFact(
                    fact=fact,
                    category=category,
                    source="Wikipedia (auto-scraped)",
                    source_url=url,
                    confidence=0.75,
                )
        
        # Secondary pass: find best match with at least 2 overlapping words
        # AND the main subject must match
        best_match = None
        best_score = 0
        
        for key, (fact, category, url) in WIKIPEDIA_FACTS.items():
            key_words = set(w for w in key.lower().split() if len(w) > 2)
            overlap = len(question_words & key_words)
            
            # Must have at least 2 word overlap AND overlap must be > 50% of question words
            if overlap >= 2 and len(question_words) > 0:
                relevance = overlap / len(question_words)
                if relevance >= 0.5 and overlap > best_score:
                    best_score = overlap
                    best_match = (fact, category, url)
        
        if best_match:
            fact, category, url = best_match
            return VerifiedFact(
                fact=fact,
                category=category,
                source="Wikipedia (auto-scraped)",
                source_url=url,
                confidence=0.70,
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
        """
        Get knowledge base statistics.
        
        Kinematic Semantics Pipeline:
        - Tier 0: Shared store (dynamically added facts)
        - Tier 1: Shape matching (kinematic query parsing)
        - Tier 2: Semantic fields (Datamuse resolution)
        - Tier 3: Keyword matching (pattern fallback)
        """
        stats = {
            "queries": self.queries,
            "hits": self.hits,
            "hit_rate": self.hits / max(1, self.queries),
            "tier_0_store_hits": self.store_hits,
            "tier_1_shape_hits": self.shape_hits,
            "tier_2_semantic_hits": self.semantic_hits,
            "tier_3_keyword_hits": self.keyword_hits,
            "typo_corrections": self.typo_corrections,
            "store_enabled": self._store is not None,
            "store_facts": self._store.count() if self._store else 0,
            "parser_enabled": self._parser is not None,
            "semantic_enabled": self._semantic is not None,
        }
        
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
