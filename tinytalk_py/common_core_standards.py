"""
===============================================================================
 COMMON CORE STATE STANDARDS (CCSS) DATABASE
 National Standards for Mathematics and English Language Arts
===============================================================================

Complete Common Core State Standards database for K-12 education.
Organized by domain, cluster, and grade for efficient lookup.

The Common Core State Standards (CCSS) are educational benchmarks adopted
by 41+ states. This module provides machine-readable standards for:
- Mathematics (K-8 + High School)
- English Language Arts (K-12)

Source: Common Core State Standards Initiative (corestandards.org)

(c) 2025-2026 Jared Lewis - Ada Computing Company - Houston, Texas
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


# ===============================================================================
# COMMON CORE ENUMS
# ===============================================================================

class CCSSSubject(Enum):
    """Common Core subject areas."""
    MATH = "mathematics"
    ELA = "english_language_arts"
    LITERACY = "literacy"  # Content area literacy (science, social studies)


class CCSSMathDomain(Enum):
    """Mathematics domains in Common Core."""
    # K-5 Domains
    CC = "counting_and_cardinality"      # K only
    OA = "operations_and_algebraic"
    NBT = "number_base_ten"
    NF = "number_fractions"              # 3-5
    MD = "measurement_and_data"
    G = "geometry"

    # 6-8 Domains
    RP = "ratios_proportional"           # 6-7
    NS = "number_system"                 # 6-8
    EE = "expressions_and_equations"     # 6-8
    SP = "statistics_and_probability"    # 6-8
    F = "functions"                      # 8

    # High School Domains
    HSN = "hs_number_quantity"
    HSA = "hs_algebra"
    HSF = "hs_functions"
    HSG = "hs_geometry"
    HSS = "hs_statistics"


class CCSSELAStrand(Enum):
    """ELA strands in Common Core."""
    RL = "reading_literature"
    RI = "reading_informational"
    RF = "reading_foundational"          # K-5 only
    W = "writing"
    SL = "speaking_listening"
    L = "language"


class CCSSSMPractice(Enum):
    """Standards for Mathematical Practice (SMP) - cross-cutting practices."""
    SMP1 = "make_sense_persevere"
    SMP2 = "reason_abstractly"
    SMP3 = "construct_arguments"
    SMP4 = "model_mathematics"
    SMP5 = "use_tools"
    SMP6 = "attend_precision"
    SMP7 = "look_for_structure"
    SMP8 = "express_regularity"


# ===============================================================================
# COMMON CORE STANDARD DATA CLASS
# ===============================================================================

@dataclass
class CommonCoreStandard:
    """
    A Common Core State Standard.

    Machine-readable format for verified curriculum alignment.
    """
    code: str                           # e.g., "CCSS.MATH.CONTENT.5.NBT.A.1"
    grade: int                          # Grade level (0=K, 1-12, 13=HS)
    subject: CCSSSubject                # Subject area
    domain: str                         # Domain code (OA, NBT, etc.)
    cluster: str                        # Cluster description
    standard_text: str                  # Full standard text
    cognitive_demand: str               # memorize, procedures, concepts, problem_solving

    # Learning progression
    prerequisite_codes: List[str] = field(default_factory=list)
    post_codes: List[str] = field(default_factory=list)

    # Cross-references
    teks_equivalents: List[str] = field(default_factory=list)  # Texas standards
    smp_practices: List[str] = field(default_factory=list)     # Math practices

    # Metadata
    keywords: List[str] = field(default_factory=list)
    example_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "grade": self.grade,
            "subject": self.subject.value,
            "domain": self.domain,
            "cluster": self.cluster,
            "standard_text": self.standard_text,
            "cognitive_demand": self.cognitive_demand,
            "prerequisites": self.prerequisite_codes,
            "leads_to": self.post_codes,
            "teks_equivalents": self.teks_equivalents,
            "smp_practices": self.smp_practices,
            "keywords": self.keywords,
            "examples": self.example_tasks
        }

    def matches_keywords(self, query: str) -> bool:
        """Check if this standard matches a keyword query."""
        query_lower = query.lower()
        if query_lower in self.code.lower():
            return True
        if query_lower in self.standard_text.lower():
            return True
        if query_lower in self.cluster.lower():
            return True
        for kw in self.keywords:
            if query_lower in kw.lower():
                return True
        return False


# ===============================================================================
# COMMON CORE LIBRARY
# ===============================================================================

class CommonCoreLibrary:
    """
    Library of Common Core State Standards.

    Organized by grade, subject, and domain for efficient lookup.
    """

    def __init__(self):
        self._standards: Dict[str, CommonCoreStandard] = {}
        self._by_grade: Dict[int, List[str]] = {}
        self._by_domain: Dict[str, List[str]] = {}
        self._by_subject: Dict[CCSSSubject, List[str]] = {}
        self._load_standards()

    def _add_standard(self, standard: CommonCoreStandard):
        """Add a standard to the library."""
        self._standards[standard.code] = standard

        if standard.grade not in self._by_grade:
            self._by_grade[standard.grade] = []
        self._by_grade[standard.grade].append(standard.code)

        if standard.domain not in self._by_domain:
            self._by_domain[standard.domain] = []
        self._by_domain[standard.domain].append(standard.code)

        if standard.subject not in self._by_subject:
            self._by_subject[standard.subject] = []
        self._by_subject[standard.subject].append(standard.code)

    def get(self, code: str) -> Optional[CommonCoreStandard]:
        """Get a standard by code."""
        return self._standards.get(code.upper().replace(" ", "."))

    def get_by_grade(self, grade: int) -> List[CommonCoreStandard]:
        """Get all standards for a grade."""
        codes = self._by_grade.get(grade, [])
        return [self._standards[code] for code in codes]

    def get_by_domain(self, domain: str) -> List[CommonCoreStandard]:
        """Get all standards for a domain."""
        codes = self._by_domain.get(domain, [])
        return [self._standards[code] for code in codes]

    def get_by_subject(self, subject: CCSSSubject) -> List[CommonCoreStandard]:
        """Get all standards for a subject."""
        codes = self._by_subject.get(subject, [])
        return [self._standards[code] for code in codes]

    def search(self, query: str) -> List[CommonCoreStandard]:
        """Search standards by keyword."""
        return [s for s in self._standards.values() if s.matches_keywords(query)]

    def get_learning_path(self, code: str) -> Dict[str, List[CommonCoreStandard]]:
        """Get prerequisites and follow-up standards."""
        standard = self.get(code)
        if not standard:
            return {"prerequisites": [], "current": [], "next": []}

        prerequisites = [self.get(c) for c in standard.prerequisite_codes if self.get(c)]
        next_standards = [self.get(c) for c in standard.post_codes if self.get(c)]

        return {
            "prerequisites": prerequisites,
            "current": [standard],
            "next": next_standards
        }

    def all_codes(self) -> List[str]:
        """Get all standard codes."""
        return list(self._standards.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        return {
            "total_standards": len(self._standards),
            "by_grade": {g: len(codes) for g, codes in self._by_grade.items()},
            "by_domain": {d: len(codes) for d, codes in self._by_domain.items()},
            "by_subject": {s.value: len(codes) for s, codes in self._by_subject.items()}
        }

    def _load_standards(self):
        """Load pre-defined Common Core standards."""
        self._load_math_k_2()
        self._load_math_3_5()
        self._load_math_6_8()
        self._load_ela_k_5()
        self._load_ela_6_8()

    # ===========================================================================
    # MATHEMATICS K-2
    # ===========================================================================

    def _load_math_k_2(self):
        """Load K-2 Mathematics standards."""

        # Kindergarten - Counting and Cardinality
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.A.1",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Know number names and the count sequence",
            standard_text="Count to 100 by ones and by tens",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.1.NBT.A.1"],
            teks_equivalents=["K.2A"],
            keywords=["counting", "100", "ones", "tens", "sequence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.A.2",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Know number names and the count sequence",
            standard_text="Count forward beginning from a given number within the known sequence",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.K.CC.A.1"],
            keywords=["count forward", "given number", "sequence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.A.3",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Know number names and the count sequence",
            standard_text="Write numbers from 0 to 20. Represent a number of objects with a written numeral 0-20",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.1.NBT.A.1"],
            teks_equivalents=["K.2B"],
            keywords=["write numbers", "numerals", "0-20", "represent"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.B.4",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Count to tell the number of objects",
            standard_text="Understand the relationship between numbers and quantities; connect counting to cardinality",
            cognitive_demand="concepts",
            teks_equivalents=["K.2C", "K.2D"],
            keywords=["cardinality", "quantities", "one-to-one", "correspondence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.B.5",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Count to tell the number of objects",
            standard_text="Count to answer 'how many?' questions about as many as 20 things",
            cognitive_demand="procedures",
            teks_equivalents=["K.2C"],
            keywords=["how many", "count", "20", "objects"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.C.6",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Compare numbers",
            standard_text="Identify whether the number of objects in one group is greater than, less than, or equal to the number of objects in another group",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.1.NBT.B.3"],
            teks_equivalents=["K.2G"],
            keywords=["compare", "greater than", "less than", "equal"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.CC.C.7",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="CC",
            cluster="Compare numbers",
            standard_text="Compare two numbers between 1 and 10 presented as written numerals",
            cognitive_demand="concepts",
            keywords=["compare", "numerals", "1-10"]
        ))

        # Kindergarten - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.OA.A.1",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand addition as putting together and adding to",
            standard_text="Represent addition and subtraction with objects, fingers, mental images, drawings, sounds, acting out situations, verbal explanations, expressions, or equations",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.1.OA.A.1"],
            teks_equivalents=["K.3A"],
            keywords=["addition", "subtraction", "represent", "objects"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.OA.A.2",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand addition as putting together and adding to",
            standard_text="Solve addition and subtraction word problems within 10",
            cognitive_demand="problem_solving",
            teks_equivalents=["K.3B"],
            keywords=["word problems", "addition", "subtraction", "within 10"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.OA.A.3",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand addition as putting together and adding to",
            standard_text="Decompose numbers less than or equal to 10 into pairs in more than one way",
            cognitive_demand="concepts",
            keywords=["decompose", "pairs", "number bonds", "10"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.OA.A.4",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand addition as putting together and adding to",
            standard_text="Find the number that makes 10 when added to any given number from 1 to 9",
            cognitive_demand="procedures",
            keywords=["make 10", "pairs", "addition"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.K.OA.A.5",
            grade=0,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand addition as putting together and adding to",
            standard_text="Fluently add and subtract within 5",
            cognitive_demand="memorize",
            post_codes=["CCSS.MATH.CONTENT.1.OA.C.6"],
            keywords=["fluency", "add", "subtract", "within 5"]
        ))

        # Grade 1 - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.OA.A.1",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Represent and solve problems involving addition and subtraction",
            standard_text="Use addition and subtraction within 20 to solve word problems involving situations of adding to, taking from, putting together, taking apart, and comparing",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.K.OA.A.1", "CCSS.MATH.CONTENT.K.OA.A.2"],
            post_codes=["CCSS.MATH.CONTENT.2.OA.A.1"],
            teks_equivalents=["1.3B", "1.3F"],
            smp_practices=["SMP1", "SMP2", "SMP4"],
            keywords=["word problems", "addition", "subtraction", "20", "joining", "separating"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.OA.B.3",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand and apply properties of operations",
            standard_text="Apply properties of operations as strategies to add and subtract",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.2.NBT.B.5"],
            keywords=["commutative", "associative", "properties", "strategies"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.OA.C.5",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Add and subtract within 20",
            standard_text="Relate counting to addition and subtraction",
            cognitive_demand="concepts",
            keywords=["counting", "addition", "subtraction", "relate"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.OA.C.6",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Add and subtract within 20",
            standard_text="Add and subtract within 20, demonstrating fluency for addition and subtraction within 10",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.K.OA.A.5"],
            post_codes=["CCSS.MATH.CONTENT.2.OA.B.2"],
            teks_equivalents=["1.3D"],
            keywords=["fluency", "add", "subtract", "within 20", "within 10"]
        ))

        # Grade 1 - Number and Operations in Base Ten
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.NBT.A.1",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Extend the counting sequence",
            standard_text="Count to 120, starting at any number less than 120",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.K.CC.A.1", "CCSS.MATH.CONTENT.K.CC.A.3"],
            post_codes=["CCSS.MATH.CONTENT.2.NBT.A.2"],
            teks_equivalents=["1.2B", "1.5A"],
            keywords=["count", "120", "sequence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.NBT.B.2",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand place value",
            standard_text="Understand that the two digits of a two-digit number represent amounts of tens and ones",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.2.NBT.A.1"],
            keywords=["place value", "tens", "ones", "two-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.NBT.B.3",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand place value",
            standard_text="Compare two two-digit numbers based on meanings of the tens and ones digits",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.K.CC.C.6"],
            keywords=["compare", "two-digit", "place value"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.1.NBT.C.4",
            grade=1,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to add and subtract",
            standard_text="Add within 100, including a two-digit number and a one-digit number",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.2.NBT.B.5"],
            keywords=["add", "100", "two-digit", "one-digit"]
        ))

        # Grade 2 - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.OA.A.1",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Represent and solve problems involving addition and subtraction",
            standard_text="Use addition and subtraction within 100 to solve one- and two-step word problems",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.1.OA.A.1"],
            post_codes=["CCSS.MATH.CONTENT.3.OA.D.8"],
            teks_equivalents=["2.4C"],
            keywords=["word problems", "two-step", "100", "addition", "subtraction"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.OA.B.2",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Add and subtract within 20",
            standard_text="Fluently add and subtract within 20 using mental strategies",
            cognitive_demand="memorize",
            prerequisite_codes=["CCSS.MATH.CONTENT.1.OA.C.6"],
            post_codes=["CCSS.MATH.CONTENT.3.OA.C.7"],
            teks_equivalents=["2.4A"],
            keywords=["fluency", "mental math", "add", "subtract", "20"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.OA.C.3",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Work with equal groups of objects",
            standard_text="Determine whether a group of objects has an odd or even number of members",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.3.OA.D.9"],
            keywords=["odd", "even", "groups", "pairs"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.OA.C.4",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Work with equal groups of objects",
            standard_text="Use addition to find the total number of objects arranged in rectangular arrays",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.3.OA.A.1"],
            teks_equivalents=["2.6A", "2.6B"],
            keywords=["arrays", "rows", "columns", "addition", "multiplication"]
        ))

        # Grade 2 - Number and Operations in Base Ten
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.NBT.A.1",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand place value",
            standard_text="Understand that the three digits of a three-digit number represent amounts of hundreds, tens, and ones",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.1.NBT.B.2"],
            post_codes=["CCSS.MATH.CONTENT.3.NBT.A.1"],
            teks_equivalents=["2.2A", "2.2B"],
            keywords=["place value", "hundreds", "tens", "ones", "three-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.NBT.A.2",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand place value",
            standard_text="Count within 1000; skip-count by 5s, 10s, and 100s",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.1.NBT.A.1"],
            teks_equivalents=["1.5B"],
            keywords=["count", "1000", "skip count", "5s", "10s", "100s"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.NBT.A.4",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand place value",
            standard_text="Compare two three-digit numbers using >, =, and < symbols",
            cognitive_demand="procedures",
            teks_equivalents=["2.2D"],
            keywords=["compare", "symbols", "greater than", "less than", "equal"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.NBT.B.5",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to add and subtract",
            standard_text="Fluently add and subtract within 100 using strategies based on place value",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.1.NBT.C.4", "CCSS.MATH.CONTENT.1.OA.B.3"],
            post_codes=["CCSS.MATH.CONTENT.3.NBT.A.2"],
            teks_equivalents=["2.4B"],
            keywords=["fluency", "add", "subtract", "100", "place value", "regrouping"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.2.NBT.B.7",
            grade=2,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to add and subtract",
            standard_text="Add and subtract within 1000, using concrete models, drawings, and strategies based on place value",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.3.NBT.A.2"],
            keywords=["add", "subtract", "1000", "models", "place value"]
        ))

    # ===========================================================================
    # MATHEMATICS GRADES 3-5
    # ===========================================================================

    def _load_math_3_5(self):
        """Load grades 3-5 Mathematics standards."""

        # Grade 3 - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.A.1",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Represent and solve problems involving multiplication and division",
            standard_text="Interpret products of whole numbers, e.g., interpret 5 x 7 as the total number of objects in 5 groups of 7 objects each",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.OA.C.4"],
            post_codes=["CCSS.MATH.CONTENT.4.OA.A.1"],
            teks_equivalents=["3.4B"],
            keywords=["multiplication", "interpret", "groups", "products"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.A.2",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Represent and solve problems involving multiplication and division",
            standard_text="Interpret whole-number quotients of whole numbers, e.g., interpret 56 / 8 as the number of objects in each share when 56 objects are partitioned equally into 8 shares",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.4.OA.A.2"],
            teks_equivalents=["3.4J"],
            keywords=["division", "quotient", "partition", "equal groups"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.A.3",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Represent and solve problems involving multiplication and division",
            standard_text="Use multiplication and division within 100 to solve word problems",
            cognitive_demand="problem_solving",
            post_codes=["CCSS.MATH.CONTENT.4.OA.A.3"],
            teks_equivalents=["3.4E", "3.4K"],
            keywords=["word problems", "multiplication", "division", "100"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.B.5",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand properties of multiplication and the relationship between multiplication and division",
            standard_text="Apply properties of operations as strategies to multiply and divide",
            cognitive_demand="concepts",
            keywords=["properties", "commutative", "associative", "distributive"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.B.6",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Understand properties of multiplication and the relationship between multiplication and division",
            standard_text="Understand division as an unknown-factor problem",
            cognitive_demand="concepts",
            teks_equivalents=["3.4H"],
            keywords=["division", "unknown factor", "inverse"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.C.7",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Multiply and divide within 100",
            standard_text="Fluently multiply and divide within 100, using strategies and the relationship between multiplication and division",
            cognitive_demand="memorize",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.OA.B.2"],
            post_codes=["CCSS.MATH.CONTENT.4.NBT.B.5"],
            teks_equivalents=["3.4F"],
            keywords=["fluency", "multiplication facts", "division facts", "100"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.D.8",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Solve problems involving the four operations",
            standard_text="Solve two-step word problems using the four operations",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.OA.A.1"],
            post_codes=["CCSS.MATH.CONTENT.4.OA.A.3"],
            teks_equivalents=["3.4K"],
            keywords=["two-step", "word problems", "four operations"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.OA.D.9",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Solve problems involving the four operations",
            standard_text="Identify arithmetic patterns and explain them using properties of operations",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.OA.C.3"],
            post_codes=["CCSS.MATH.CONTENT.4.OA.C.5"],
            teks_equivalents=["3.4I"],
            keywords=["patterns", "arithmetic", "properties"]
        ))

        # Grade 3 - Number and Operations in Base Ten
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NBT.A.1",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Use place value understanding to round whole numbers to the nearest 10 or 100",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.NBT.A.1"],
            post_codes=["CCSS.MATH.CONTENT.4.NBT.A.3"],
            teks_equivalents=["3.3B"],
            keywords=["round", "nearest 10", "nearest 100", "place value"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NBT.A.2",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Fluently add and subtract within 1000 using strategies and algorithms based on place value",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.2.NBT.B.5", "CCSS.MATH.CONTENT.2.NBT.B.7"],
            post_codes=["CCSS.MATH.CONTENT.4.NBT.B.4"],
            keywords=["fluency", "add", "subtract", "1000", "algorithms"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NBT.A.3",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Multiply one-digit whole numbers by multiples of 10 in the range 10-90",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.4.NBT.B.5"],
            teks_equivalents=["3.4G"],
            keywords=["multiply", "multiples of 10", "one-digit"]
        ))

        # Grade 3 - Number and Operations: Fractions
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NF.A.1",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Develop understanding of fractions as numbers",
            standard_text="Understand a fraction 1/b as the quantity formed by 1 part when a whole is partitioned into b equal parts",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.4.NF.A.1"],
            teks_equivalents=["3.2A"],
            keywords=["fractions", "unit fractions", "partition", "equal parts"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NF.A.2",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Develop understanding of fractions as numbers",
            standard_text="Understand a fraction as a number on the number line; represent fractions on a number line diagram",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.4.NF.A.2"],
            teks_equivalents=["3.2B", "3.7A"],
            keywords=["fractions", "number line", "represent"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.3.NF.A.3",
            grade=3,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Develop understanding of fractions as numbers",
            standard_text="Explain equivalence of fractions and compare fractions by reasoning about their size",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.4.NF.A.1", "CCSS.MATH.CONTENT.4.NF.A.2"],
            keywords=["equivalent fractions", "compare", "reasoning"]
        ))

        # Grade 4 - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.OA.A.1",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Use the four operations with whole numbers to solve problems",
            standard_text="Interpret a multiplication equation as a comparison, e.g., interpret 35 = 5 x 7 as a statement that 35 is 5 times as many as 7",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.OA.A.1"],
            keywords=["multiplicative comparison", "times as many", "equations"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.OA.A.2",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Use the four operations with whole numbers to solve problems",
            standard_text="Multiply or divide to solve word problems involving multiplicative comparison",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.OA.A.2"],
            keywords=["word problems", "multiplicative comparison", "division"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.OA.A.3",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Use the four operations with whole numbers to solve problems",
            standard_text="Solve multi-step word problems using the four operations, including problems with remainders",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.OA.A.3", "CCSS.MATH.CONTENT.3.OA.D.8"],
            post_codes=["CCSS.MATH.CONTENT.5.NBT.B.6"],
            teks_equivalents=["4.4H"],
            keywords=["multi-step", "word problems", "remainders", "four operations"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.OA.B.4",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Gain familiarity with factors and multiples",
            standard_text="Find all factor pairs for a whole number in the range 1-100. Recognize that a whole number is a multiple of each of its factors. Determine whether a given whole number in the range 1-100 is prime or composite",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.5.NF.B.5"],
            keywords=["factors", "multiples", "prime", "composite", "factor pairs"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.OA.C.5",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Generate and analyze patterns",
            standard_text="Generate a number or shape pattern that follows a given rule. Identify apparent features of the pattern that were not explicit in the rule itself",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.OA.D.9"],
            post_codes=["CCSS.MATH.CONTENT.5.OA.B.3"],
            keywords=["patterns", "rules", "generate", "analyze"]
        ))

        # Grade 4 - Number and Operations in Base Ten
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.A.1",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Generalize place value understanding for multi-digit whole numbers",
            standard_text="Recognize that in a multi-digit whole number, a digit in one place represents ten times what it represents in the place to its right",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.5.NBT.A.1"],
            teks_equivalents=["4.1A"],
            keywords=["place value", "ten times", "multi-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.A.2",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Generalize place value understanding for multi-digit whole numbers",
            standard_text="Read and write multi-digit whole numbers using base-ten numerals, number names, and expanded form",
            cognitive_demand="procedures",
            teks_equivalents=["4.1B"],
            keywords=["expanded form", "word form", "standard form", "multi-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.A.3",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Generalize place value understanding for multi-digit whole numbers",
            standard_text="Use place value understanding to round multi-digit whole numbers to any place",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.NBT.A.1"],
            post_codes=["CCSS.MATH.CONTENT.5.NBT.A.4"],
            teks_equivalents=["4.4G"],
            keywords=["round", "place value", "estimate"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.B.4",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Fluently add and subtract multi-digit whole numbers using the standard algorithm",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.NBT.A.2"],
            keywords=["fluency", "standard algorithm", "add", "subtract", "multi-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.B.5",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Multiply a whole number of up to four digits by a one-digit whole number, and multiply two two-digit numbers",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.OA.C.7", "CCSS.MATH.CONTENT.3.NBT.A.3"],
            post_codes=["CCSS.MATH.CONTENT.5.NBT.B.5"],
            teks_equivalents=["4.4C", "4.4D"],
            keywords=["multiply", "four-digit", "two-digit", "algorithms"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NBT.B.6",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Use place value understanding and properties of operations to perform multi-digit arithmetic",
            standard_text="Find whole-number quotients and remainders with up to four-digit dividends and one-digit divisors",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.5.NBT.B.6"],
            teks_equivalents=["4.4E", "4.4F"],
            keywords=["divide", "quotients", "remainders", "four-digit"]
        ))

        # Grade 4 - Number and Operations: Fractions
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.A.1",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Extend understanding of fraction equivalence and ordering",
            standard_text="Explain why a fraction a/b is equivalent to a fraction (n x a)/(n x b) by using visual fraction models",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.NF.A.1", "CCSS.MATH.CONTENT.3.NF.A.3"],
            teks_equivalents=["4.3A", "4.3C"],
            keywords=["equivalent fractions", "visual models", "multiply"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.A.2",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Extend understanding of fraction equivalence and ordering",
            standard_text="Compare two fractions with different numerators and different denominators",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.3.NF.A.2", "CCSS.MATH.CONTENT.3.NF.A.3"],
            teks_equivalents=["4.3D"],
            keywords=["compare", "fractions", "benchmark", "common denominator"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.B.3",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Build fractions from unit fractions",
            standard_text="Understand a fraction a/b with a > 1 as a sum of fractions 1/b",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.5.NF.A.1"],
            teks_equivalents=["4.3B"],
            keywords=["decompose", "unit fractions", "sum"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.B.4",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Build fractions from unit fractions",
            standard_text="Apply and extend previous understandings of multiplication to multiply a fraction by a whole number",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.5.NF.B.4"],
            keywords=["multiply", "fraction", "whole number"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.C.5",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Understand decimal notation for fractions, and compare decimal fractions",
            standard_text="Express a fraction with denominator 10 as an equivalent fraction with denominator 100",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.5.NBT.A.3"],
            teks_equivalents=["4.2A", "4.2B"],
            keywords=["decimals", "tenths", "hundredths", "equivalent"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.C.6",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Understand decimal notation for fractions, and compare decimal fractions",
            standard_text="Use decimal notation for fractions with denominators 10 or 100",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.5.NBT.A.3"],
            keywords=["decimals", "notation", "fractions"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.4.NF.C.7",
            grade=4,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Understand decimal notation for fractions, and compare decimal fractions",
            standard_text="Compare two decimals to hundredths by reasoning about their size",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.5.NBT.A.3"],
            teks_equivalents=["4.2C"],
            keywords=["compare", "decimals", "hundredths"]
        ))

        # Grade 5 - Operations and Algebraic Thinking
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.OA.A.1",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Write and interpret numerical expressions",
            standard_text="Use parentheses, brackets, or braces in numerical expressions, and evaluate expressions with these symbols",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.6.EE.A.1"],
            teks_equivalents=["5.3J", "5.4E", "5.4F"],
            keywords=["parentheses", "brackets", "order of operations", "evaluate"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.OA.A.2",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Write and interpret numerical expressions",
            standard_text="Write simple expressions that record calculations with numbers, and interpret numerical expressions without evaluating them",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.6.EE.A.2"],
            teks_equivalents=["5.4B"],
            keywords=["expressions", "write", "interpret"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.OA.B.3",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="OA",
            cluster="Analyze patterns and relationships",
            standard_text="Generate two numerical patterns using two given rules. Identify apparent relationships between corresponding terms",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.OA.C.5"],
            post_codes=["CCSS.MATH.CONTENT.6.EE.B.9"],
            teks_equivalents=["5.4A", "5.4C", "5.4D"],
            keywords=["patterns", "relationships", "ordered pairs", "graph"]
        ))

        # Grade 5 - Number and Operations in Base Ten
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.A.1",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand the place value system",
            standard_text="Recognize that in a multi-digit number, a digit in one place represents 10 times as much as it represents in the place to its right and 1/10 of what it represents in the place to its left",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NBT.A.1"],
            teks_equivalents=["5.1A"],
            keywords=["place value", "10 times", "1/10", "decimals"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.A.3",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand the place value system",
            standard_text="Read, write, and compare decimals to thousandths",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NF.C.5", "CCSS.MATH.CONTENT.4.NF.C.6", "CCSS.MATH.CONTENT.4.NF.C.7"],
            teks_equivalents=["5.1B"],
            keywords=["decimals", "thousandths", "read", "write", "compare"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.A.4",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Understand the place value system",
            standard_text="Use place value understanding to round decimals to any place",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NBT.A.3"],
            teks_equivalents=["5.3K"],
            keywords=["round", "decimals", "place value"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.B.5",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Perform operations with multi-digit whole numbers and with decimals to hundredths",
            standard_text="Fluently multiply multi-digit whole numbers using the standard algorithm",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NBT.B.5"],
            teks_equivalents=["5.3B"],
            keywords=["multiply", "fluency", "standard algorithm", "multi-digit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.B.6",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Perform operations with multi-digit whole numbers and with decimals to hundredths",
            standard_text="Find whole-number quotients of whole numbers with up to four-digit dividends and two-digit divisors",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NBT.B.6", "CCSS.MATH.CONTENT.4.OA.A.3"],
            teks_equivalents=["5.3D"],
            keywords=["divide", "two-digit divisor", "quotients"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NBT.B.7",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NBT",
            cluster="Perform operations with multi-digit whole numbers and with decimals to hundredths",
            standard_text="Add, subtract, multiply, and divide decimals to hundredths",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.6.NS.B.3"],
            teks_equivalents=["5.3A", "5.3G", "5.3H"],
            keywords=["decimals", "add", "subtract", "multiply", "divide"]
        ))

        # Grade 5 - Number and Operations: Fractions
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NF.A.1",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Use equivalent fractions as a strategy to add and subtract fractions",
            standard_text="Add and subtract fractions with unlike denominators by replacing given fractions with equivalent fractions",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NF.B.3"],
            post_codes=["CCSS.MATH.CONTENT.6.NS.A.1"],
            teks_equivalents=["5.3C"],
            keywords=["add fractions", "subtract fractions", "unlike denominators", "equivalent"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NF.A.2",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Use equivalent fractions as a strategy to add and subtract fractions",
            standard_text="Solve word problems involving addition and subtraction of fractions referring to the same whole",
            cognitive_demand="problem_solving",
            teks_equivalents=["5.3I"],
            keywords=["word problems", "fractions", "add", "subtract"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NF.B.4",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Apply and extend previous understandings of multiplication and division",
            standard_text="Apply and extend previous understandings of multiplication to multiply a fraction or whole number by a fraction",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.NF.B.4"],
            post_codes=["CCSS.MATH.CONTENT.6.NS.A.1"],
            teks_equivalents=["5.3E"],
            keywords=["multiply", "fractions", "whole number"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NF.B.5",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Apply and extend previous understandings of multiplication and division",
            standard_text="Interpret multiplication as scaling (resizing)",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.4.OA.B.4"],
            keywords=["scaling", "multiplication", "resize", "fractions"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.5.NF.B.7",
            grade=5,
            subject=CCSSSubject.MATH,
            domain="NF",
            cluster="Apply and extend previous understandings of multiplication and division",
            standard_text="Apply and extend previous understandings of division to divide unit fractions by whole numbers and whole numbers by unit fractions",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.6.NS.A.1"],
            teks_equivalents=["5.3F"],
            keywords=["divide", "unit fractions", "whole numbers"]
        ))

    # ===========================================================================
    # MATHEMATICS GRADES 6-8
    # ===========================================================================

    def _load_math_6_8(self):
        """Load grades 6-8 Mathematics standards."""

        # Grade 6 - Ratios and Proportional Relationships
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.RP.A.1",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Understand ratio concepts and use ratio reasoning to solve problems",
            standard_text="Understand the concept of a ratio and use ratio language to describe a ratio relationship between two quantities",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.7.RP.A.1"],
            teks_equivalents=["6.3A", "6.3B"],
            keywords=["ratio", "relationship", "describe", "quantities"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.RP.A.2",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Understand ratio concepts and use ratio reasoning to solve problems",
            standard_text="Understand the concept of a unit rate a/b associated with a ratio a:b with b != 0",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.7.RP.A.1"],
            teks_equivalents=["6.3C", "6.3D"],
            keywords=["unit rate", "ratio", "per unit"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.RP.A.3",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Understand ratio concepts and use ratio reasoning to solve problems",
            standard_text="Use ratio and rate reasoning to solve real-world and mathematical problems",
            cognitive_demand="problem_solving",
            post_codes=["CCSS.MATH.CONTENT.7.RP.A.2", "CCSS.MATH.CONTENT.7.RP.A.3"],
            teks_equivalents=["6.3E", "6.4B", "6.4C", "6.5A", "6.5B", "6.5C"],
            keywords=["ratio reasoning", "rate", "percent", "tables", "graphs"]
        ))

        # Grade 6 - The Number System
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.NS.A.1",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of multiplication and division to divide fractions by fractions",
            standard_text="Interpret and compute quotients of fractions, and solve word problems involving division of fractions by fractions",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.5.NF.A.1", "CCSS.MATH.CONTENT.5.NF.B.4", "CCSS.MATH.CONTENT.5.NF.B.7"],
            keywords=["divide fractions", "quotients", "word problems"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.NS.B.3",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Compute fluently with multi-digit numbers and find common factors and multiples",
            standard_text="Fluently add, subtract, multiply, and divide multi-digit decimals using the standard algorithm for each operation",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.5.NBT.B.7"],
            keywords=["decimals", "fluency", "standard algorithm", "four operations"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.NS.C.5",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of numbers to the system of rational numbers",
            standard_text="Understand that positive and negative numbers are used together to describe quantities having opposite directions or values",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.7.NS.A.1"],
            teks_equivalents=["6.1A"],
            keywords=["positive", "negative", "integers", "opposite"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.NS.C.6",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of numbers to the system of rational numbers",
            standard_text="Understand a rational number as a point on the number line",
            cognitive_demand="concepts",
            teks_equivalents=["6.1B"],
            keywords=["rational numbers", "number line", "coordinate"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.NS.C.7",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of numbers to the system of rational numbers",
            standard_text="Understand ordering and absolute value of rational numbers",
            cognitive_demand="concepts",
            keywords=["ordering", "absolute value", "rational numbers"]
        ))

        # Grade 6 - Expressions and Equations
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.A.1",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Apply and extend previous understandings of arithmetic to algebraic expressions",
            standard_text="Write and evaluate numerical expressions involving whole-number exponents",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.5.OA.A.1"],
            teks_equivalents=["6.2A"],
            keywords=["exponents", "evaluate", "expressions"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.A.2",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Apply and extend previous understandings of arithmetic to algebraic expressions",
            standard_text="Write, read, and evaluate expressions in which letters stand for numbers",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.5.OA.A.2"],
            post_codes=["CCSS.MATH.CONTENT.7.EE.A.1"],
            teks_equivalents=["6.2B", "6.2C"],
            keywords=["variables", "expressions", "evaluate", "substitute"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.A.3",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Apply and extend previous understandings of arithmetic to algebraic expressions",
            standard_text="Apply the properties of operations to generate equivalent expressions",
            cognitive_demand="procedures",
            post_codes=["CCSS.MATH.CONTENT.7.EE.A.1"],
            teks_equivalents=["6.2D", "6.2E"],
            keywords=["equivalent expressions", "properties", "distributive"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.B.6",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Reason about and solve one-variable equations and inequalities",
            standard_text="Use variables to represent numbers and write expressions when solving a real-world or mathematical problem",
            cognitive_demand="concepts",
            post_codes=["CCSS.MATH.CONTENT.7.EE.B.4"],
            keywords=["variables", "expressions", "real-world"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.B.7",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Reason about and solve one-variable equations and inequalities",
            standard_text="Solve real-world and mathematical problems by writing and solving equations of the form x + p = q and px = q",
            cognitive_demand="problem_solving",
            post_codes=["CCSS.MATH.CONTENT.7.EE.B.4"],
            keywords=["equations", "solve", "one-variable"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.6.EE.B.9",
            grade=6,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Represent and analyze quantitative relationships between dependent and independent variables",
            standard_text="Use variables to represent two quantities in a real-world problem that change in relationship to one another",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.5.OA.B.3"],
            post_codes=["CCSS.MATH.CONTENT.7.RP.A.2"],
            teks_equivalents=["6.4A"],
            keywords=["variables", "dependent", "independent", "relationship"]
        ))

        # Grade 7 - Ratios and Proportional Relationships
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.RP.A.1",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Analyze proportional relationships and use them to solve real-world and mathematical problems",
            standard_text="Compute unit rates associated with ratios of fractions",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.RP.A.1", "CCSS.MATH.CONTENT.6.RP.A.2"],
            teks_equivalents=["7.3A", "7.3B"],
            keywords=["unit rates", "fractions", "complex fractions"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.RP.A.2",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Analyze proportional relationships and use them to solve real-world and mathematical problems",
            standard_text="Recognize and represent proportional relationships between quantities",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.RP.A.3", "CCSS.MATH.CONTENT.6.EE.B.9"],
            post_codes=["CCSS.MATH.CONTENT.8.EE.B.5"],
            teks_equivalents=["7.4A", "7.4B", "7.4C"],
            keywords=["proportional", "constant of proportionality", "y = kx"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.RP.A.3",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="RP",
            cluster="Analyze proportional relationships and use them to solve real-world and mathematical problems",
            standard_text="Use proportional relationships to solve multistep ratio and percent problems",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.RP.A.3"],
            teks_equivalents=["7.4D", "7.5A", "7.5B", "7.5C"],
            keywords=["percent", "markup", "markdown", "tax", "tip", "interest"]
        ))

        # Grade 7 - The Number System
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.NS.A.1",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of operations with fractions",
            standard_text="Apply and extend previous understandings of addition and subtraction to add and subtract rational numbers",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.NS.C.5"],
            post_codes=["CCSS.MATH.CONTENT.8.NS.A.1"],
            teks_equivalents=["7.1B", "7.2A", "7.2B"],
            keywords=["integers", "add", "subtract", "rational numbers"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.NS.A.2",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of operations with fractions",
            standard_text="Apply and extend previous understandings of multiplication and division to multiply and divide rational numbers",
            cognitive_demand="procedures",
            keywords=["multiply", "divide", "rational numbers", "integers"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.NS.A.3",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Apply and extend previous understandings of operations with fractions",
            standard_text="Solve real-world and mathematical problems involving the four operations with rational numbers",
            cognitive_demand="problem_solving",
            keywords=["four operations", "rational numbers", "problem solving"]
        ))

        # Grade 7 - Expressions and Equations
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.EE.A.1",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Use properties of operations to generate equivalent expressions",
            standard_text="Apply properties of operations as strategies to add, subtract, factor, and expand linear expressions with rational coefficients",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.EE.A.2", "CCSS.MATH.CONTENT.6.EE.A.3"],
            post_codes=["CCSS.MATH.CONTENT.8.EE.C.7"],
            teks_equivalents=["7.6A", "7.6B"],
            keywords=["expressions", "factor", "expand", "like terms"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.7.EE.B.4",
            grade=7,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Solve real-life and mathematical problems using numerical and algebraic expressions and equations",
            standard_text="Use variables to represent quantities in a real-world or mathematical problem, and construct simple equations and inequalities to solve problems",
            cognitive_demand="problem_solving",
            prerequisite_codes=["CCSS.MATH.CONTENT.6.EE.B.6", "CCSS.MATH.CONTENT.6.EE.B.7"],
            post_codes=["CCSS.MATH.CONTENT.8.EE.C.7"],
            keywords=["equations", "inequalities", "solve", "real-world"]
        ))

        # Grade 8 - The Number System
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.NS.A.1",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Know that there are numbers that are not rational, and approximate them by rational numbers",
            standard_text="Know that numbers that are not rational are called irrational. Understand informally that every number has a decimal expansion",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.7.NS.A.1"],
            teks_equivalents=["8.1A", "8.1B"],
            keywords=["irrational", "rational", "decimal expansion"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.NS.A.2",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="NS",
            cluster="Know that there are numbers that are not rational, and approximate them by rational numbers",
            standard_text="Use rational approximations of irrational numbers to compare the size of irrational numbers and locate them on a number line diagram",
            cognitive_demand="procedures",
            keywords=["irrational", "approximate", "number line", "compare"]
        ))

        # Grade 8 - Expressions and Equations
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.A.1",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Work with radicals and integer exponents",
            standard_text="Know and apply the properties of integer exponents to generate equivalent numerical expressions",
            cognitive_demand="procedures",
            teks_equivalents=["8.2A"],
            keywords=["exponents", "integer exponents", "properties", "equivalent"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.A.3",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Work with radicals and integer exponents",
            standard_text="Use numbers expressed in the form of a single digit times an integer power of 10 to estimate very large or very small quantities",
            cognitive_demand="procedures",
            teks_equivalents=["8.2B", "8.2C"],
            keywords=["scientific notation", "estimate", "powers of 10"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.B.5",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Understand the connections between proportional relationships, lines, and linear equations",
            standard_text="Graph proportional relationships, interpreting the unit rate as the slope of the graph. Compare two different proportional relationships represented in different ways",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.7.RP.A.2"],
            post_codes=["CCSS.MATH.CONTENT.8.EE.B.6"],
            teks_equivalents=["8.3A", "8.4A", "8.4B"],
            keywords=["graph", "proportional", "slope", "unit rate"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.B.6",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Understand the connections between proportional relationships, lines, and linear equations",
            standard_text="Use similar triangles to explain why the slope m is the same between any two distinct points on a non-vertical line in the coordinate plane",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.MATH.CONTENT.8.EE.B.5"],
            teks_equivalents=["8.3B", "8.3C"],
            keywords=["similar triangles", "slope", "y = mx + b", "linear"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.C.7",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Analyze and solve linear equations and pairs of simultaneous linear equations",
            standard_text="Solve linear equations in one variable",
            cognitive_demand="procedures",
            prerequisite_codes=["CCSS.MATH.CONTENT.7.EE.A.1", "CCSS.MATH.CONTENT.7.EE.B.4"],
            keywords=["linear equations", "one variable", "solve"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.EE.C.8",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="EE",
            cluster="Analyze and solve linear equations and pairs of simultaneous linear equations",
            standard_text="Analyze and solve pairs of simultaneous linear equations",
            cognitive_demand="procedures",
            keywords=["systems", "simultaneous", "linear equations", "solve"]
        ))

        # Grade 8 - Functions
        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.F.A.1",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="F",
            cluster="Define, evaluate, and compare functions",
            standard_text="Understand that a function is a rule that assigns to each input exactly one output",
            cognitive_demand="concepts",
            teks_equivalents=["8.5A", "8.5G"],
            keywords=["function", "input", "output", "rule"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.F.A.2",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="F",
            cluster="Define, evaluate, and compare functions",
            standard_text="Compare properties of two functions each represented in a different way (algebraically, graphically, numerically in tables, or by verbal descriptions)",
            cognitive_demand="concepts",
            teks_equivalents=["8.4C", "8.5B", "8.5F"],
            keywords=["compare", "functions", "representations"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.F.A.3",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="F",
            cluster="Define, evaluate, and compare functions",
            standard_text="Interpret the equation y = mx + b as defining a linear function, whose graph is a straight line",
            cognitive_demand="concepts",
            teks_equivalents=["8.5H", "8.5I"],
            keywords=["linear function", "y = mx + b", "slope-intercept"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.F.B.4",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="F",
            cluster="Use functions to model relationships between quantities",
            standard_text="Construct a function to model a linear relationship between two quantities",
            cognitive_demand="problem_solving",
            keywords=["construct", "model", "linear", "function"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.MATH.CONTENT.8.F.B.5",
            grade=8,
            subject=CCSSSubject.MATH,
            domain="F",
            cluster="Use functions to model relationships between quantities",
            standard_text="Describe qualitatively the functional relationship between two quantities by analyzing a graph",
            cognitive_demand="concepts",
            teks_equivalents=["8.5C", "8.5D"],
            keywords=["describe", "graph", "analyze", "functional relationship"]
        ))

    # ===========================================================================
    # ELA GRADES K-5
    # ===========================================================================

    def _load_ela_k_5(self):
        """Load K-5 ELA standards."""

        # Kindergarten - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.K.1",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="With prompting and support, ask and answer questions about key details in a text",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.1.1"],
            keywords=["questions", "key details", "text", "prompting"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.K.2",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="With prompting and support, retell familiar stories, including key details",
            cognitive_demand="procedures",
            post_codes=["CCSS.ELA-LITERACY.RL.1.2"],
            keywords=["retell", "stories", "key details"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.K.3",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="With prompting and support, identify characters, settings, and major events in a story",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.1.3"],
            keywords=["characters", "settings", "events", "story"]
        ))

        # Kindergarten - Reading: Foundational Skills
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RF.K.1",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RF",
            cluster="Print Concepts",
            standard_text="Demonstrate understanding of the organization and basic features of print",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RF.1.1"],
            keywords=["print concepts", "left to right", "words", "letters"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RF.K.2",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RF",
            cluster="Phonological Awareness",
            standard_text="Demonstrate understanding of spoken words, syllables, and sounds (phonemes)",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RF.1.2"],
            keywords=["phonological awareness", "rhymes", "syllables", "sounds"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RF.K.3",
            grade=0,
            subject=CCSSSubject.ELA,
            domain="RF",
            cluster="Phonics and Word Recognition",
            standard_text="Know and apply grade-level phonics and word analysis skills in decoding words",
            cognitive_demand="procedures",
            post_codes=["CCSS.ELA-LITERACY.RF.1.3"],
            keywords=["phonics", "decoding", "consonants", "vowels"]
        ))

        # Grade 1 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.1.1",
            grade=1,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Ask and answer questions about key details in a text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.K.1"],
            post_codes=["CCSS.ELA-LITERACY.RL.2.1"],
            keywords=["questions", "key details", "text"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.1.2",
            grade=1,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Retell stories, including key details, and demonstrate understanding of their central message or lesson",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.K.2"],
            post_codes=["CCSS.ELA-LITERACY.RL.2.2"],
            keywords=["retell", "central message", "lesson", "moral"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.1.3",
            grade=1,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Describe characters, settings, and major events in a story, using key details",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.K.3"],
            post_codes=["CCSS.ELA-LITERACY.RL.2.3"],
            keywords=["describe", "characters", "settings", "events"]
        ))

        # Grade 3 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.3.1",
            grade=3,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Ask and answer questions to demonstrate understanding of a text, referring explicitly to the text as the basis for the answers",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.4.1"],
            teks_equivalents=["3.6A"],
            keywords=["questions", "explicit", "text evidence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.3.2",
            grade=3,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Recount stories, including fables, folktales, and myths from diverse cultures; determine the central message, lesson, or moral",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.4.2"],
            keywords=["recount", "central message", "moral", "fables", "myths"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.3.3",
            grade=3,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Describe characters in a story and explain how their actions contribute to the sequence of events",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.4.3"],
            teks_equivalents=["3.6B", "3.6C"],
            keywords=["characters", "actions", "sequence", "events"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.3.4",
            grade=3,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Determine the meaning of words and phrases as they are used in a text, distinguishing literal from nonliteral language",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.4.4"],
            keywords=["vocabulary", "literal", "nonliteral", "figurative"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.3.5",
            grade=3,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Refer to parts of stories, dramas, and poems when writing or speaking about a text",
            cognitive_demand="procedures",
            post_codes=["CCSS.ELA-LITERACY.RL.4.5"],
            keywords=["chapter", "scene", "stanza", "text structure"]
        ))

        # Grade 5 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.5.1",
            grade=5,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Quote accurately from a text when explaining what the text says explicitly and when drawing inferences from the text",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.6.1"],
            teks_equivalents=["5.6A", "5.6B"],
            keywords=["quote", "explicit", "inferences", "text evidence"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.5.2",
            grade=5,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Determine a theme of a story, drama, or poem from details in the text, including how characters in a story or drama respond to challenges",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.6.2"],
            keywords=["theme", "characters", "challenges", "summarize"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.5.3",
            grade=5,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Compare and contrast two or more characters, settings, or events in a story or drama, drawing on specific details in the text",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.6.3"],
            teks_equivalents=["5.6C", "5.6D"],
            keywords=["compare", "contrast", "characters", "settings", "events"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.5.4",
            grade=5,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Determine the meaning of words and phrases as they are used in a text, including figurative language such as metaphors and similes",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.6.4"],
            teks_equivalents=["5.7C"],
            keywords=["figurative language", "metaphor", "simile", "vocabulary"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.5.6",
            grade=5,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Describe how a narrator's or speaker's point of view influences how events are described",
            cognitive_demand="concepts",
            post_codes=["CCSS.ELA-LITERACY.RL.6.6"],
            teks_equivalents=["5.6E"],
            keywords=["point of view", "narrator", "perspective"]
        ))

    # ===========================================================================
    # ELA GRADES 6-8
    # ===========================================================================

    def _load_ela_6_8(self):
        """Load grades 6-8 ELA standards."""

        # Grade 6 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.6.1",
            grade=6,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Cite textual evidence to support analysis of what the text says explicitly as well as inferences drawn from the text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.5.1"],
            post_codes=["CCSS.ELA-LITERACY.RL.7.1"],
            teks_equivalents=["6.6A"],
            keywords=["cite", "textual evidence", "inferences", "analysis"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.6.2",
            grade=6,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Determine a theme or central idea of a text and how it is conveyed through particular details; provide a summary of the text distinct from personal opinions or judgments",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.5.2"],
            post_codes=["CCSS.ELA-LITERACY.RL.7.2"],
            teks_equivalents=["6.7A"],
            keywords=["theme", "central idea", "summary", "details"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.6.3",
            grade=6,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Describe how a particular story's or drama's plot unfolds in a series of episodes as well as how the characters respond or change as the plot moves toward a resolution",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.5.3"],
            post_codes=["CCSS.ELA-LITERACY.RL.7.3"],
            teks_equivalents=["6.6B", "6.6C"],
            keywords=["plot", "episodes", "characters", "resolution"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.6.4",
            grade=6,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Determine the meaning of words and phrases as they are used in a text, including figurative and connotative meanings; analyze the impact of a specific word choice on meaning and tone",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.5.4"],
            post_codes=["CCSS.ELA-LITERACY.RL.7.4"],
            teks_equivalents=["6.8A"],
            keywords=["figurative", "connotative", "word choice", "tone"]
        ))

        # Grade 7 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.7.1",
            grade=7,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Cite several pieces of textual evidence to support analysis of what the text says explicitly as well as inferences drawn from the text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.6.1"],
            post_codes=["CCSS.ELA-LITERACY.RL.8.1"],
            teks_equivalents=["7.6A"],
            keywords=["cite", "multiple evidence", "inferences", "analysis"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.7.2",
            grade=7,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Determine a theme or central idea of a text and analyze its development over the course of the text; provide an objective summary of the text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.6.2"],
            post_codes=["CCSS.ELA-LITERACY.RL.8.2"],
            keywords=["theme development", "central idea", "objective summary"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.7.3",
            grade=7,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Analyze how particular elements of a story or drama interact",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.6.3"],
            post_codes=["CCSS.ELA-LITERACY.RL.8.3"],
            teks_equivalents=["7.6B"],
            keywords=["analyze", "story elements", "interact"]
        ))

        # Grade 8 - Reading: Literature
        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.8.1",
            grade=8,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Cite the textual evidence that most strongly supports an analysis of what the text says explicitly as well as inferences drawn from the text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.7.1"],
            teks_equivalents=["8.6A"],
            keywords=["cite", "strongest evidence", "analysis", "inferences"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.8.2",
            grade=8,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Determine a theme or central idea of a text and analyze its development over the course of the text, including its relationship to the characters, setting, and plot; provide an objective summary of the text",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.7.2"],
            keywords=["theme", "development", "characters", "setting", "plot"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.8.3",
            grade=8,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Key Ideas and Details",
            standard_text="Analyze how particular lines of dialogue or incidents in a story or drama propel the action, reveal aspects of a character, or provoke a decision",
            cognitive_demand="concepts",
            prerequisite_codes=["CCSS.ELA-LITERACY.RL.7.3"],
            teks_equivalents=["8.6B"],
            keywords=["dialogue", "incidents", "action", "character"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.8.4",
            grade=8,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Determine the meaning of words and phrases as they are used in a text, including figurative and connotative meanings; analyze the impact of specific word choices on meaning and tone, including analogies or allusions to other texts",
            cognitive_demand="concepts",
            teks_equivalents=["8.7B"],
            keywords=["figurative", "connotative", "analogies", "allusions", "tone"]
        ))

        self._add_standard(CommonCoreStandard(
            code="CCSS.ELA-LITERACY.RL.8.6",
            grade=8,
            subject=CCSSSubject.ELA,
            domain="RL",
            cluster="Craft and Structure",
            standard_text="Analyze how differences in the points of view of the characters and the audience or reader create such effects as suspense or humor",
            cognitive_demand="concepts",
            teks_equivalents=["8.7A"],
            keywords=["point of view", "perspective", "suspense", "humor", "dramatic irony"]
        ))


# ===============================================================================
# SINGLETON INSTANCE
# ===============================================================================

_common_core_library: Optional[CommonCoreLibrary] = None


def get_common_core_library() -> CommonCoreLibrary:
    """Get or create the global CommonCoreLibrary instance."""
    global _common_core_library
    if _common_core_library is None:
        _common_core_library = CommonCoreLibrary()
    return _common_core_library


# ===============================================================================
# MODULE EXPORTS
# ===============================================================================

__all__ = [
    # Enums
    'CCSSSubject',
    'CCSSMathDomain',
    'CCSSELAStrand',
    'CCSSSMPractice',

    # Data Class
    'CommonCoreStandard',

    # Library
    'CommonCoreLibrary',
    'get_common_core_library',
]
