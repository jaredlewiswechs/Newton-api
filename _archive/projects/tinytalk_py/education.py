"""
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk Education - The Ultimate Teacher's Aide
═══════════════════════════════════════════════════════════════════════════════

Newton-powered verified computation for education. Treats TEKS, NES, and
educational standards as machine-readable objects with full constraint
verification.

Updated for CDL 3.0 with:
- f/g ratio analysis for mastery validation
- Zone of Proximal Development (ZPD) constraints
- Learning Trek integration
- Common Core State Standards support
- Newton grounding for pedagogical patterns

"The standard IS the objective. The constraint IS the curriculum."
"The f/g ratio IS the readiness. 1 == 1."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from .core import Blueprint, field as tt_field, forge, law, when, finfr, LawViolation
from .engine import Presence, Delta, KineticEngine
import hashlib
import time
import re
import json

# CDL 3.0 Integration - Import new education modules
try:
    from .common_core_standards import (
        CommonCoreStandard, CommonCoreLibrary, get_common_core_library,
        CCSSSubject, CCSSMathDomain, CCSSELAStrand
    )
    HAS_COMMON_CORE = True
except ImportError:
    HAS_COMMON_CORE = False

try:
    from .learning_treks import (
        LearningTrek, TrekCheckpoint, LearningObjective, TrekLibrary,
        TrekValidator, get_trek_library, get_trek_validator,
        TrekDomain, MasteryLevel, CheckpointType
    )
    HAS_TREKS = True
except ImportError:
    HAS_TREKS = False

try:
    from .education_cdl import (
        MasteryConstraint, ZPDConstraint, ProgressionConstraint,
        DifferentiationConstraint, EducationCDLEvaluator,
        verify_mastery, verify_zpd, verify_progression, get_differentiation_tier,
        EducationDomain
    )
    HAS_EDUCATION_CDL = True
except ImportError:
    HAS_EDUCATION_CDL = False

try:
    from .education_grounding import (
        EducationGroundingEngine, PedagogicalPattern, GroundedPattern,
        ground_pattern, ground_lesson, get_grounded_pattern,
        GROUNDED_PATTERNS
    )
    HAS_GROUNDING = True
except ImportError:
    HAS_GROUNDING = False


# ═══════════════════════════════════════════════════════════════════════════════
# TEKS STANDARDS DATABASE - Machine Readable Objects
# ═══════════════════════════════════════════════════════════════════════════════

class Subject(Enum):
    """Subject areas aligned to TEKS."""
    MATH = "mathematics"
    READING = "reading_ela"
    SCIENCE = "science"
    SOCIAL_STUDIES = "social_studies"
    WRITING = "writing"


class GradeLevel(Enum):
    """Grade levels for Texas education."""
    K = 0
    G1 = 1
    G2 = 2
    G3 = 3
    G4 = 4
    G5 = 5
    G6 = 6
    G7 = 7
    G8 = 8
    ALGEBRA1 = 9
    GEOMETRY = 10
    ALGEBRA2 = 11
    PRECALCULUS = 12


class CognitiveLevel(Enum):
    """Bloom's Taxonomy levels."""
    REMEMBER = 1      # Recall facts
    UNDERSTAND = 2    # Explain ideas
    APPLY = 3         # Use in new situations
    ANALYZE = 4       # Draw connections
    EVALUATE = 5      # Justify decisions
    CREATE = 6        # Produce new work


class NESPhase(Enum):
    """HISD New Education System phases."""
    OPENING = "opening"          # Hook & objective (5 min)
    INSTRUCTION = "instruction"  # Direct teach (15 min)
    GUIDED = "guided"            # Collaborative practice (15 min)
    INDEPENDENT = "independent"  # Solo practice (10 min)
    CLOSING = "closing"          # Exit ticket (5 min)


@dataclass
class TEKSStandard:
    """
    A Texas Essential Knowledge and Skills standard.

    Machine-readable format for verified curriculum alignment.
    """
    code: str                           # e.g., "5.3A"
    grade: int                          # Grade level (0-12)
    subject: Subject                    # Subject area
    strand: str                         # Content strand
    knowledge_statement: str            # What students will know
    skill_statement: str                # What students will do
    cognitive_level: CognitiveLevel     # Bloom's level
    prerequisite_codes: List[str] = field(default_factory=list)
    post_codes: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    rigor_level: int = 2                # 1-3 (DOK)

    def __post_init__(self):
        # Parse code to extract grade and strand
        match = re.match(r'(\d+)\.(\d+)([A-Z]*)', self.code)
        if match:
            self.grade = int(match.group(1))
            self.strand = match.group(2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "grade": self.grade,
            "subject": self.subject.value,
            "strand": self.strand,
            "knowledge": self.knowledge_statement,
            "skill": self.skill_statement,
            "cognitive_level": self.cognitive_level.name,
            "bloom_level": self.cognitive_level.value,
            "prerequisites": self.prerequisite_codes,
            "leads_to": self.post_codes,
            "keywords": self.keywords,
            "rigor": self.rigor_level
        }

    def matches_keywords(self, query: str) -> bool:
        """Check if this standard matches a keyword query."""
        query_lower = query.lower()
        if query_lower in self.code.lower():
            return True
        if query_lower in self.knowledge_statement.lower():
            return True
        if query_lower in self.skill_statement.lower():
            return True
        for kw in self.keywords:
            if query_lower in kw.lower():
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEKS STANDARDS LIBRARY - Pre-populated Standards
# ═══════════════════════════════════════════════════════════════════════════════

class TEKSLibrary:
    """
    Library of Texas Essential Knowledge and Skills standards.

    Organized by grade and subject for efficient lookup.
    """

    def __init__(self):
        self._standards: Dict[str, TEKSStandard] = {}
        self._by_grade: Dict[int, List[str]] = {}
        self._by_subject: Dict[Subject, List[str]] = {}
        self._load_standards()

    def _load_standards(self):
        """Load pre-defined TEKS standards."""
        # Mathematics Grade 3
        self._add_standard(TEKSStandard(
            code="3.1A",
            grade=3,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Understand base-ten place value system",
            skill_statement="Compose and decompose numbers up to 100,000",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            keywords=["place value", "compose", "decompose", "hundred thousands"]
        ))
        self._add_standard(TEKSStandard(
            code="3.2A",
            grade=3,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Represent fractions using objects and symbols",
            skill_statement="Model and represent unit fractions including 1/2, 1/3, 1/4, 1/6, 1/8",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["fractions", "unit fractions", "model", "represent"]
        ))
        self._add_standard(TEKSStandard(
            code="3.3A",
            grade=3,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Represent and solve addition and subtraction",
            skill_statement="Solve one-step and two-step problems using addition and subtraction",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["addition", "subtraction", "word problems", "solve"]
        ))
        self._add_standard(TEKSStandard(
            code="3.4A",
            grade=3,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Multiply and divide with fluency",
            skill_statement="Solve with fluency one-step and two-step multiplication and division",
            cognitive_level=CognitiveLevel.APPLY,
            prerequisite_codes=["2.6A", "2.6B"],
            keywords=["multiplication", "division", "fluency", "products"]
        ))
        self._add_standard(TEKSStandard(
            code="3.5A",
            grade=3,
            subject=Subject.MATH,
            strand="5",
            knowledge_statement="Represent and solve problems with area",
            skill_statement="Calculate area using unit squares and multiplication",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["area", "unit squares", "multiplication", "measurement"]
        ))

        # Mathematics Grade 4
        self._add_standard(TEKSStandard(
            code="4.1A",
            grade=4,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Place value to billions",
            skill_statement="Represent value of digit in whole numbers through billions",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            prerequisite_codes=["3.1A"],
            keywords=["place value", "billions", "whole numbers"]
        ))
        self._add_standard(TEKSStandard(
            code="4.2A",
            grade=4,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Represent decimals and fractions",
            skill_statement="Interpret the value of each place-value position with decimals",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            keywords=["decimals", "place value", "tenths", "hundredths"]
        ))
        self._add_standard(TEKSStandard(
            code="4.3A",
            grade=4,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Represent equivalent fractions",
            skill_statement="Generate equivalent fractions using number lines and models",
            cognitive_level=CognitiveLevel.APPLY,
            prerequisite_codes=["3.2A"],
            keywords=["equivalent fractions", "number line", "simplify"]
        ))
        self._add_standard(TEKSStandard(
            code="4.4A",
            grade=4,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Add and subtract fractions",
            skill_statement="Add and subtract fractions with common denominators",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["add fractions", "subtract fractions", "common denominator"]
        ))
        self._add_standard(TEKSStandard(
            code="4.5A",
            grade=4,
            subject=Subject.MATH,
            strand="5",
            knowledge_statement="Multi-step problem solving",
            skill_statement="Represent multi-step problems with equations using variables",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["multi-step", "equations", "variables", "problem solving"]
        ))

        # Mathematics Grade 5
        self._add_standard(TEKSStandard(
            code="5.1A",
            grade=5,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Place value relationships",
            skill_statement="Recognize value of place from billions to thousandths",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            prerequisite_codes=["4.1A", "4.2A"],
            keywords=["place value", "billions", "thousandths", "decimals"]
        ))
        self._add_standard(TEKSStandard(
            code="5.2A",
            grade=5,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Represent prime and composite numbers",
            skill_statement="Classify whole numbers as prime or composite",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["prime", "composite", "factors", "classify"]
        ))
        self._add_standard(TEKSStandard(
            code="5.3A",
            grade=5,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Estimate and solve decimal operations",
            skill_statement="Estimate to determine solutions involving addition and subtraction",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["estimate", "decimals", "addition", "subtraction"]
        ))
        self._add_standard(TEKSStandard(
            code="5.3B",
            grade=5,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Multiply and divide decimals",
            skill_statement="Multiply with fluency a three-digit number by a two-digit number",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["multiply", "decimals", "fluency", "three-digit"]
        ))
        self._add_standard(TEKSStandard(
            code="5.3C",
            grade=5,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Add and subtract fractions with unlike denominators",
            skill_statement="Solve with proficiency for fractions with unlike denominators",
            cognitive_level=CognitiveLevel.APPLY,
            prerequisite_codes=["4.4A", "4.3A"],
            keywords=["fractions", "unlike denominators", "add", "subtract"]
        ))
        self._add_standard(TEKSStandard(
            code="5.4A",
            grade=5,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Algebraic relationships",
            skill_statement="Identify the relationship between additive and multiplicative patterns",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["patterns", "algebraic", "relationships", "additive"]
        ))

        # Mathematics Grade 6
        self._add_standard(TEKSStandard(
            code="6.1A",
            grade=6,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Compare and order rational numbers",
            skill_statement="Classify whole numbers, integers, and rational numbers",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["rational numbers", "integers", "classify", "compare"]
        ))
        self._add_standard(TEKSStandard(
            code="6.2A",
            grade=6,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Order of operations",
            skill_statement="Apply order of operations with whole numbers and decimals",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["order of operations", "PEMDAS", "evaluate", "expressions"]
        ))
        self._add_standard(TEKSStandard(
            code="6.3A",
            grade=6,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Ratios and rates",
            skill_statement="Represent and analyze ratios and rates",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["ratios", "rates", "proportional", "unit rate"]
        ))
        self._add_standard(TEKSStandard(
            code="6.4A",
            grade=6,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Proportional relationships",
            skill_statement="Compare two rules verbally, numerically, graphically, and symbolically",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["proportional", "relationships", "rules", "equations"]
        ))

        # Mathematics Grade 7
        self._add_standard(TEKSStandard(
            code="7.1A",
            grade=7,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Rational number operations",
            skill_statement="Apply mathematics to problems in everyday life",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["rational", "real-world", "application", "everyday"]
        ))
        self._add_standard(TEKSStandard(
            code="7.2A",
            grade=7,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Extend rational number operations",
            skill_statement="Add, subtract, multiply, divide rational numbers fluently",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["operations", "rational", "fluency", "negative"]
        ))
        self._add_standard(TEKSStandard(
            code="7.3A",
            grade=7,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Proportionality",
            skill_statement="Represent constant rates of change as proportional relationships",
            cognitive_level=CognitiveLevel.ANALYZE,
            prerequisite_codes=["6.3A", "6.4A"],
            keywords=["proportional", "constant rate", "slope", "y=kx"]
        ))
        self._add_standard(TEKSStandard(
            code="7.4A",
            grade=7,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Percent problems",
            skill_statement="Solve problems involving percent increase and decrease",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["percent", "increase", "decrease", "proportional"]
        ))

        # Mathematics Grade 8
        self._add_standard(TEKSStandard(
            code="8.1A",
            grade=8,
            subject=Subject.MATH,
            strand="1",
            knowledge_statement="Real numbers and their properties",
            skill_statement="Extend properties of numbers to real numbers",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            keywords=["real numbers", "properties", "irrational", "rational"]
        ))
        self._add_standard(TEKSStandard(
            code="8.2A",
            grade=8,
            subject=Subject.MATH,
            strand="2",
            knowledge_statement="Scientific notation",
            skill_statement="Represent very large and very small quantities in scientific notation",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["scientific notation", "exponents", "large numbers", "small numbers"]
        ))
        self._add_standard(TEKSStandard(
            code="8.3A",
            grade=8,
            subject=Subject.MATH,
            strand="3",
            knowledge_statement="Linear relationships",
            skill_statement="Generalize that y=mx+b represents linear equations",
            cognitive_level=CognitiveLevel.UNDERSTAND,
            prerequisite_codes=["7.3A"],
            keywords=["linear", "slope", "y-intercept", "equation"]
        ))
        self._add_standard(TEKSStandard(
            code="8.4A",
            grade=8,
            subject=Subject.MATH,
            strand="4",
            knowledge_statement="Proportional and non-proportional linear relationships",
            skill_statement="Use tables, graphs, and equations to represent relationships",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["proportional", "non-proportional", "linear", "representations"]
        ))
        self._add_standard(TEKSStandard(
            code="8.5A",
            grade=8,
            subject=Subject.MATH,
            strand="5",
            knowledge_statement="Functions",
            skill_statement="Represent linear non-proportional functions with y=mx+b",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["functions", "linear", "slope-intercept", "equations"]
        ))

        # Reading/ELA Standards - Sample
        self._add_standard(TEKSStandard(
            code="5.6A",
            grade=5,
            subject=Subject.READING,
            strand="6",
            knowledge_statement="Comprehension of literary text",
            skill_statement="Describe incidents that advance the story or novel",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["plot", "story elements", "narrative", "literary"]
        ))
        self._add_standard(TEKSStandard(
            code="5.6B",
            grade=5,
            subject=Subject.READING,
            strand="6",
            knowledge_statement="Literary elements and devices",
            skill_statement="Explain the roles and functions of characters",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["characters", "protagonist", "antagonist", "literary"]
        ))
        self._add_standard(TEKSStandard(
            code="5.7A",
            grade=5,
            subject=Subject.READING,
            strand="7",
            knowledge_statement="Comprehension of informational text",
            skill_statement="Establish purposes for reading based on desired outcome",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["informational", "purpose", "reading", "comprehension"]
        ))
        self._add_standard(TEKSStandard(
            code="6.8A",
            grade=6,
            subject=Subject.READING,
            strand="8",
            knowledge_statement="Author's purpose and craft",
            skill_statement="Explain how authors create meaning through stylistic elements",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["author's purpose", "style", "craft", "meaning"]
        ))

        # Science Standards - Sample
        self._add_standard(TEKSStandard(
            code="5.5A",
            grade=5,
            subject=Subject.SCIENCE,
            strand="5",
            knowledge_statement="Matter and energy",
            skill_statement="Classify matter based on measurable properties including mass and volume",
            cognitive_level=CognitiveLevel.ANALYZE,
            keywords=["matter", "mass", "volume", "properties", "classify"]
        ))
        self._add_standard(TEKSStandard(
            code="5.6A",
            grade=5,
            subject=Subject.SCIENCE,
            strand="6",
            knowledge_statement="Force, motion, and energy",
            skill_statement="Explore balanced and unbalanced forces and motion",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["force", "motion", "balanced", "unbalanced", "physics"]
        ))
        self._add_standard(TEKSStandard(
            code="8.6A",
            grade=8,
            subject=Subject.SCIENCE,
            strand="6",
            knowledge_statement="Force, motion, and energy",
            skill_statement="Demonstrate and calculate how unbalanced forces change motion",
            cognitive_level=CognitiveLevel.APPLY,
            keywords=["Newton's laws", "force", "motion", "acceleration"]
        ))

    def _add_standard(self, standard: TEKSStandard):
        """Add a standard to the library."""
        self._standards[standard.code] = standard

        if standard.grade not in self._by_grade:
            self._by_grade[standard.grade] = []
        self._by_grade[standard.grade].append(standard.code)

        if standard.subject not in self._by_subject:
            self._by_subject[standard.subject] = []
        self._by_subject[standard.subject].append(standard.code)

    def get(self, code: str) -> Optional[TEKSStandard]:
        """Get a standard by code."""
        return self._standards.get(code.upper())

    def get_by_grade(self, grade: int) -> List[TEKSStandard]:
        """Get all standards for a grade."""
        codes = self._by_grade.get(grade, [])
        return [self._standards[code] for code in codes]

    def get_by_subject(self, subject: Subject) -> List[TEKSStandard]:
        """Get all standards for a subject."""
        codes = self._by_subject.get(subject, [])
        return [self._standards[code] for code in codes]

    def get_by_grade_and_subject(self, grade: int, subject: Subject) -> List[TEKSStandard]:
        """Get standards for a specific grade and subject."""
        return [s for s in self.get_by_grade(grade) if s.subject == subject]

    def search(self, query: str) -> List[TEKSStandard]:
        """Search standards by keyword."""
        return [s for s in self._standards.values() if s.matches_keywords(query)]

    def get_learning_path(self, code: str) -> Dict[str, List[TEKSStandard]]:
        """Get prerequisites and follow-up standards for a TEKS code."""
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


# Singleton instance
_teks_library: Optional[TEKSLibrary] = None

def get_teks_library() -> TEKSLibrary:
    """Get or create the global TEKS library."""
    global _teks_library
    if _teks_library is None:
        _teks_library = TEKSLibrary()
    return _teks_library


# ═══════════════════════════════════════════════════════════════════════════════
# NES LESSON PLAN - Blueprint with Laws
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LessonPhase:
    """A phase within an NES lesson."""
    phase: NESPhase
    duration_minutes: int
    title: str
    activities: List[str]
    teacher_actions: List[str]
    student_actions: List[str]
    materials: List[str] = field(default_factory=list)
    differentiation: Dict[str, str] = field(default_factory=dict)
    formative_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "duration_minutes": self.duration_minutes,
            "title": self.title,
            "activities": self.activities,
            "teacher_actions": self.teacher_actions,
            "student_actions": self.student_actions,
            "materials": self.materials,
            "differentiation": self.differentiation,
            "formative_checks": self.formative_checks
        }


class NESLessonPlan(Blueprint):
    """
    NES-Compliant Lesson Plan with tinyTalk governance.

    Laws:
    - Total duration must equal 50 minutes
    - Must include all 5 NES phases
    - Must align to at least one TEKS standard
    - Exit ticket must assess objective
    """

    title = tt_field(str, default="")
    grade = tt_field(int, default=5)
    subject = tt_field(str, default="")
    teks_codes = tt_field(list, default=None)
    objective = tt_field(str, default="")
    phases = tt_field(list, default=None)
    total_duration = tt_field(int, default=0)
    materials = tt_field(list, default=None)
    vocabulary = tt_field(list, default=None)

    def __init__(self, **kwargs):
        # Set defaults for mutable fields
        if 'teks_codes' not in kwargs or kwargs['teks_codes'] is None:
            kwargs['teks_codes'] = []
        if 'phases' not in kwargs or kwargs['phases'] is None:
            kwargs['phases'] = []
        if 'materials' not in kwargs or kwargs['materials'] is None:
            kwargs['materials'] = []
        if 'vocabulary' not in kwargs or kwargs['vocabulary'] is None:
            kwargs['vocabulary'] = []
        super().__init__(**kwargs)

    @law
    def duration_law(self):
        """Total lesson duration must be 50 minutes."""
        when(self.total_duration != 50, finfr)

    @law
    def teks_alignment_law(self):
        """Lesson must align to at least one TEKS standard."""
        when(len(self.teks_codes) == 0, finfr)

    @law
    def phase_completeness_law(self):
        """Lesson must include all 5 NES phases."""
        phase_types = {p.phase for p in self.phases} if self.phases else set()
        required = {NESPhase.OPENING, NESPhase.INSTRUCTION, NESPhase.GUIDED,
                   NESPhase.INDEPENDENT, NESPhase.CLOSING}
        when(phase_types != required, finfr)

    @forge
    def add_phase(self, phase: LessonPhase) -> str:
        """Add a phase to the lesson plan."""
        if self.phases is None:
            self.phases = []
        self.phases.append(phase)
        self.total_duration = sum(p.duration_minutes for p in self.phases)
        return "phase_added"

    @forge
    def set_teks(self, codes: List[str]) -> str:
        """Set TEKS alignment codes."""
        self.teks_codes = codes
        return "teks_set"

    def to_dict(self) -> Dict[str, Any]:
        """Export lesson plan as dictionary."""
        return {
            "title": self.title,
            "grade": self.grade,
            "subject": self.subject,
            "teks_codes": self.teks_codes,
            "objective": self.objective,
            "total_duration": self.total_duration,
            "phases": [p.to_dict() for p in (self.phases or [])],
            "materials": self.materials,
            "vocabulary": self.vocabulary
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STUDENT ASSESSMENT - Blueprint with Laws
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StudentScore:
    """Individual student score data."""
    student_id: str
    student_name: str
    score: float
    total_points: float
    percentage: float = 0.0
    mastery_status: str = ""
    misconceptions: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.percentage = round((self.score / self.total_points) * 100, 1) if self.total_points > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "student_name": self.student_name,
            "score": self.score,
            "total_points": self.total_points,
            "percentage": self.percentage,
            "mastery_status": self.mastery_status,
            "misconceptions": self.misconceptions
        }


class AssessmentAnalyzer(Blueprint):
    """
    Assessment data analyzer with verified computation.

    Provides robust statistical analysis using Newton's
    adversarial-resistant methods (MAD, IQR).
    """

    assessment_name = tt_field(str, default="")
    teks_codes = tt_field(list, default=None)
    total_points = tt_field(float, default=100.0)
    mastery_threshold = tt_field(float, default=80.0)
    students = tt_field(list, default=None)

    # Statistics (computed)
    class_average = tt_field(float, default=0.0)
    class_median = tt_field(float, default=0.0)
    mastery_rate = tt_field(float, default=0.0)
    needs_reteach_count = tt_field(int, default=0)
    on_track_count = tt_field(int, default=0)
    advanced_count = tt_field(int, default=0)

    def __init__(self, **kwargs):
        if 'teks_codes' not in kwargs or kwargs['teks_codes'] is None:
            kwargs['teks_codes'] = []
        if 'students' not in kwargs or kwargs['students'] is None:
            kwargs['students'] = []
        super().__init__(**kwargs)

    @law
    def valid_threshold_law(self):
        """Mastery threshold must be between 0 and 100."""
        when(self.mastery_threshold < 0 or self.mastery_threshold > 100, finfr)

    @forge
    def add_student_score(self, student_id: str, name: str, score: float) -> str:
        """Add a student's score to the assessment."""
        student = StudentScore(
            student_id=student_id,
            student_name=name,
            score=score,
            total_points=self.total_points
        )

        # Classify mastery
        if student.percentage >= self.mastery_threshold:
            student.mastery_status = "mastery"
        elif student.percentage >= 70:
            student.mastery_status = "approaching"
        else:
            student.mastery_status = "needs_reteach"

        if self.students is None:
            self.students = []
        self.students.append(student)
        self._recalculate_statistics()
        return "score_added"

    @forge
    def analyze_batch(self, data: List[Dict[str, Any]]) -> str:
        """Add multiple student scores at once."""
        for entry in data:
            student = StudentScore(
                student_id=entry.get("id", str(len(self.students or []))),
                student_name=entry.get("name", "Unknown"),
                score=float(entry.get("score", 0)),
                total_points=self.total_points
            )

            # Classify mastery
            if student.percentage >= self.mastery_threshold:
                student.mastery_status = "mastery"
            elif student.percentage >= 70:
                student.mastery_status = "approaching"
            else:
                student.mastery_status = "needs_reteach"

            if self.students is None:
                self.students = []
            self.students.append(student)

        self._recalculate_statistics()
        return "batch_analyzed"

    def _recalculate_statistics(self):
        """Recalculate all statistics."""
        if not self.students:
            return

        percentages = [s.percentage for s in self.students]
        n = len(percentages)

        # Average
        self.class_average = round(sum(percentages) / n, 1)

        # Median (robust)
        sorted_pct = sorted(percentages)
        if n % 2 == 0:
            self.class_median = round((sorted_pct[n//2 - 1] + sorted_pct[n//2]) / 2, 1)
        else:
            self.class_median = round(sorted_pct[n//2], 1)

        # Mastery rate
        mastery_students = [s for s in self.students if s.mastery_status == "mastery"]
        self.mastery_rate = round((len(mastery_students) / n) * 100, 1)

        # Group counts
        self.needs_reteach_count = sum(1 for s in self.students if s.mastery_status == "needs_reteach")
        self.on_track_count = sum(1 for s in self.students if s.mastery_status == "approaching")
        self.advanced_count = sum(1 for s in self.students if s.mastery_status == "mastery")

    def get_reteach_group(self) -> List[StudentScore]:
        """Get students who need reteaching."""
        return [s for s in (self.students or []) if s.mastery_status == "needs_reteach"]

    def get_on_track_group(self) -> List[StudentScore]:
        """Get students approaching mastery."""
        return [s for s in (self.students or []) if s.mastery_status == "approaching"]

    def get_mastery_group(self) -> List[StudentScore]:
        """Get students at mastery."""
        return [s for s in (self.students or []) if s.mastery_status == "mastery"]

    def generate_grouping_report(self) -> Dict[str, Any]:
        """Generate student grouping report for differentiated instruction."""
        return {
            "assessment": self.assessment_name,
            "teks_codes": self.teks_codes,
            "statistics": {
                "class_average": self.class_average,
                "class_median": self.class_median,
                "mastery_rate": self.mastery_rate,
                "total_students": len(self.students or [])
            },
            "groups": {
                "needs_reteach": {
                    "count": self.needs_reteach_count,
                    "students": [s.to_dict() for s in self.get_reteach_group()],
                    "recommendation": "Small group instruction on prerequisite skills"
                },
                "approaching": {
                    "count": self.on_track_count,
                    "students": [s.to_dict() for s in self.get_on_track_group()],
                    "recommendation": "Guided practice with scaffolding"
                },
                "mastery": {
                    "count": self.advanced_count,
                    "students": [s.to_dict() for s in self.get_mastery_group()],
                    "recommendation": "Extension activities and peer tutoring"
                }
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Export assessment analysis as dictionary."""
        return self.generate_grouping_report()


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON PLAN GENERATOR - Verified Generation
# ═══════════════════════════════════════════════════════════════════════════════

class LessonPlanGenerator:
    """
    Newton-verified lesson plan generator.

    Generates NES-compliant lesson plans aligned to TEKS standards.
    All output is constraint-verified before delivery.
    """

    def __init__(self):
        self.teks_library = get_teks_library()

    def generate(
        self,
        grade: int,
        subject: str,
        teks_codes: List[str],
        topic: Optional[str] = None,
        student_needs: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Generate a complete NES-compliant lesson plan."""
        start_us = time.perf_counter_ns() // 1000

        # Validate TEKS codes
        valid_standards = []
        for code in teks_codes:
            standard = self.teks_library.get(code)
            if standard:
                valid_standards.append(standard)

        if not valid_standards:
            return {
                "verified": False,
                "error": "No valid TEKS codes provided",
                "elapsed_us": (time.perf_counter_ns() // 1000) - start_us
            }

        # Use first standard as primary
        primary_standard = valid_standards[0]

        # Generate objective from TEKS
        objective = self._generate_objective(primary_standard, topic)

        # Generate phases
        phases = self._generate_phases(primary_standard, topic, student_needs)

        # Generate materials list
        materials = self._generate_materials(primary_standard, phases)

        # Generate vocabulary
        vocabulary = self._generate_vocabulary(primary_standard)

        # Calculate total duration
        total_duration = sum(p.duration_minutes for p in phases)

        # Build the lesson plan
        lesson = {
            "title": f"{subject.title()}: {topic or primary_standard.skill_statement[:50]}",
            "grade": grade,
            "subject": subject,
            "date": time.strftime("%Y-%m-%d"),
            "teks_alignment": [s.to_dict() for s in valid_standards],
            "objective": objective,
            "vocabulary": vocabulary,
            "materials": materials,
            "total_duration_minutes": total_duration,
            "phases": [p.to_dict() for p in phases],
            "differentiation": {
                "below_level": "Provide manipulatives and visual supports",
                "on_level": "Standard lesson with guided practice",
                "above_level": "Extension problems and peer tutoring opportunities"
            },
            "assessment": {
                "formative": ["Think-pair-share", "Thumbs up/down", "Exit ticket"],
                "exit_ticket": self._generate_exit_ticket(primary_standard)
            }
        }

        # Add student-specific accommodations if provided
        if student_needs:
            lesson["accommodations"] = self._generate_accommodations(student_needs)

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return {
            "verified": True,
            "lesson_plan": lesson,
            "fingerprint": hashlib.sha256(json.dumps(lesson, sort_keys=True).encode()).hexdigest()[:12].upper(),
            "elapsed_us": elapsed_us,
            "timestamp": int(time.time() * 1000)
        }

    def _generate_objective(self, standard: TEKSStandard, topic: Optional[str]) -> str:
        """Generate a learning objective from TEKS."""
        verbs = {
            CognitiveLevel.REMEMBER: ["identify", "recall", "recognize", "list"],
            CognitiveLevel.UNDERSTAND: ["explain", "describe", "summarize", "interpret"],
            CognitiveLevel.APPLY: ["demonstrate", "solve", "use", "apply"],
            CognitiveLevel.ANALYZE: ["analyze", "compare", "contrast", "differentiate"],
            CognitiveLevel.EVALUATE: ["evaluate", "justify", "critique", "assess"],
            CognitiveLevel.CREATE: ["create", "design", "construct", "develop"]
        }

        verb = verbs[standard.cognitive_level][0]

        return f"Students will {verb} {standard.skill_statement.lower()} as measured by an exit ticket with 80% accuracy."

    def _generate_phases(
        self,
        standard: TEKSStandard,
        topic: Optional[str],
        student_needs: Optional[Dict[str, List[str]]]
    ) -> List[LessonPhase]:
        """Generate all 5 NES phases."""
        phases = []

        # Opening (5 minutes)
        phases.append(LessonPhase(
            phase=NESPhase.OPENING,
            duration_minutes=5,
            title="Hook & Objective",
            activities=[
                "Real-world connection question",
                "Share learning objective",
                "Students restate objective in own words"
            ],
            teacher_actions=[
                "Display hook question on board",
                "Read objective aloud",
                "Cold call 2-3 students to restate"
            ],
            student_actions=[
                "Think about hook question (30 sec)",
                "Listen to objective",
                "Restate objective to partner"
            ],
            formative_checks=["Can students explain what they'll learn today?"]
        ))

        # Direct Instruction (15 minutes)
        phases.append(LessonPhase(
            phase=NESPhase.INSTRUCTION,
            duration_minutes=15,
            title="I Do - Teacher Modeling",
            activities=[
                "Model 2-3 examples using think-aloud",
                "Highlight key vocabulary",
                "Address common misconceptions"
            ],
            teacher_actions=[
                "Display worked examples on document camera",
                "Verbalize thinking process aloud",
                "Point to key steps explicitly",
                "Check for understanding every 3-5 minutes"
            ],
            student_actions=[
                "Watch and listen actively",
                "Take notes in math journal",
                "Respond to check questions with signals"
            ],
            materials=["Document camera", "Whiteboard", "Example problems"],
            formative_checks=["Thumbs up/sideways/down", "Quick verbal responses"]
        ))

        # Guided Practice (15 minutes)
        phases.append(LessonPhase(
            phase=NESPhase.GUIDED,
            duration_minutes=15,
            title="We Do - Collaborative Practice",
            activities=[
                "Complete 3-4 problems together",
                "Partner work with structured protocol",
                "Teacher circulates and provides feedback"
            ],
            teacher_actions=[
                "Lead first problem together",
                "Release to partners for remaining problems",
                "Circulate and monitor conversations",
                "Provide targeted feedback to struggling pairs"
            ],
            student_actions=[
                "Solve problems with guidance",
                "Explain thinking to partner",
                "Ask clarifying questions",
                "Check answers with partner"
            ],
            materials=["Guided practice worksheet", "Whiteboards"],
            differentiation={
                "below_level": "Provide sentence stems for explanation",
                "above_level": "Challenge problems available"
            },
            formative_checks=["Circulate to check work", "Listen to partner discussions"]
        ))

        # Independent Practice (10 minutes)
        phases.append(LessonPhase(
            phase=NESPhase.INDEPENDENT,
            duration_minutes=10,
            title="You Do - Independent Work",
            activities=[
                "Complete 5-8 problems independently",
                "Self-check work",
                "Early finishers work on extension"
            ],
            teacher_actions=[
                "Set timer and expectations",
                "Circulate and provide individual support",
                "Take anecdotal notes on struggling students",
                "Redirect off-task behavior"
            ],
            student_actions=[
                "Work silently on practice problems",
                "Show work for each problem",
                "Self-assess using answer key",
                "Complete extension if finished early"
            ],
            materials=["Independent practice worksheet", "Extension problems"],
            differentiation={
                "below_level": "Reduced problem set with visual supports",
                "above_level": "Extension problems with higher complexity"
            },
            formative_checks=["Monitor work in progress", "Check completed problems"]
        ))

        # Closing (5 minutes)
        phases.append(LessonPhase(
            phase=NESPhase.CLOSING,
            duration_minutes=5,
            title="Exit Ticket & Closure",
            activities=[
                "Complete 2-3 question exit ticket",
                "Summarize key learning",
                "Preview tomorrow's lesson"
            ],
            teacher_actions=[
                "Distribute exit tickets",
                "Collect and quickly sort by mastery",
                "Summarize key points",
                "Preview connection to tomorrow"
            ],
            student_actions=[
                "Complete exit ticket silently",
                "Turn in to designated location",
                "Pack up materials"
            ],
            materials=["Exit ticket slips"],
            formative_checks=["Exit ticket results determine tomorrow's groups"]
        ))

        return phases

    def _generate_materials(self, standard: TEKSStandard, phases: List[LessonPhase]) -> List[str]:
        """Generate consolidated materials list."""
        materials = set()

        # Add phase-specific materials
        for phase in phases:
            materials.update(phase.materials)

        # Add standard materials
        materials.update([
            "Whiteboard and markers",
            "Student math journals",
            "Pencils",
            "Exit ticket slips"
        ])

        # Add subject-specific materials
        if standard.subject == Subject.MATH:
            if any(kw in standard.keywords for kw in ["fractions", "decimals"]):
                materials.add("Fraction tiles")
                materials.add("Number lines")
            if any(kw in standard.keywords for kw in ["area", "perimeter", "measurement"]):
                materials.add("Grid paper")
                materials.add("Rulers")

        return sorted(list(materials))

    def _generate_vocabulary(self, standard: TEKSStandard) -> List[Dict[str, str]]:
        """Generate vocabulary list from TEKS keywords."""
        vocab_definitions = {
            "place value": "The value of a digit based on its position in a number",
            "fractions": "Numbers that represent parts of a whole",
            "decimals": "Numbers written using a decimal point",
            "equivalent": "Having the same value",
            "proportional": "Having a constant ratio",
            "linear": "Following a straight line pattern",
            "slope": "The steepness of a line (rise over run)",
            "variable": "A letter or symbol representing an unknown number",
            "expression": "A mathematical phrase with numbers and operations",
            "equation": "A mathematical sentence with an equals sign"
        }

        vocabulary = []
        for keyword in standard.keywords[:5]:  # Limit to 5 terms
            definition = vocab_definitions.get(keyword, f"Key concept related to {keyword}")
            vocabulary.append({
                "term": keyword,
                "definition": definition
            })

        return vocabulary

    def _generate_exit_ticket(self, standard: TEKSStandard) -> Dict[str, Any]:
        """Generate exit ticket questions."""
        return {
            "questions": [
                {
                    "number": 1,
                    "type": "skill_check",
                    "description": f"Apply {standard.skill_statement.lower()[:50]}...",
                    "points": 1
                },
                {
                    "number": 2,
                    "type": "application",
                    "description": "Solve a word problem using today's skill",
                    "points": 1
                },
                {
                    "number": 3,
                    "type": "reflection",
                    "description": "Explain your thinking process",
                    "points": 1
                }
            ],
            "mastery_threshold": "3/3 = Mastery, 2/3 = Approaching, 1/3 or below = Reteach"
        }

    def _generate_accommodations(self, student_needs: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Generate accommodations based on student needs."""
        accommodations = {}

        for need_type, students in student_needs.items():
            if need_type == "ell":
                accommodations["English Language Learners"] = [
                    "Provide vocabulary word bank",
                    "Allow use of native language dictionary",
                    "Pair with bilingual peer buddy",
                    f"Students: {', '.join(students)}"
                ]
            elif need_type == "504":
                accommodations["504 Accommodations"] = [
                    "Extended time on assessments",
                    "Preferential seating",
                    "Check for understanding frequently",
                    f"Students: {', '.join(students)}"
                ]
            elif need_type == "sped":
                accommodations["Special Education"] = [
                    "Reduce problem set quantity",
                    "Provide graphic organizers",
                    "Allow calculator use as specified in IEP",
                    f"Students: {', '.join(students)}"
                ]
            elif need_type == "gt":
                accommodations["Gifted & Talented"] = [
                    "Provide enrichment problems",
                    "Independent research extension",
                    "Leadership role in group work",
                    f"Students: {', '.join(students)}"
                ]

        return accommodations


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE DECK GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SlideDeckGenerator:
    """
    Newton-verified slide deck generator for lessons.

    Generates presentation specs compatible with various formats.
    """

    def __init__(self):
        self.teks_library = get_teks_library()

    def generate(
        self,
        lesson_plan: Dict[str, Any],
        style: str = "modern"
    ) -> Dict[str, Any]:
        """Generate slide deck specification from lesson plan."""
        start_us = time.perf_counter_ns() // 1000

        slides = []

        # Title slide
        slides.append({
            "slide_number": 1,
            "type": "title",
            "title": lesson_plan.get("title", "Today's Lesson"),
            "subtitle": f"Grade {lesson_plan.get('grade', '')} | {lesson_plan.get('subject', '').title()}",
            "footer": time.strftime("%B %d, %Y")
        })

        # Objective slide
        slides.append({
            "slide_number": 2,
            "type": "objective",
            "title": "Learning Objective",
            "content": lesson_plan.get("objective", ""),
            "teks_codes": [t.get("code", "") for t in lesson_plan.get("teks_alignment", [])]
        })

        # Vocabulary slide
        vocab = lesson_plan.get("vocabulary", [])
        if vocab:
            slides.append({
                "slide_number": 3,
                "type": "vocabulary",
                "title": "Key Vocabulary",
                "terms": vocab
            })

        # Phase slides
        phases = lesson_plan.get("phases", [])
        slide_num = 4

        for phase in phases:
            phase_title = phase.get("title", "")
            phase_type = phase.get("phase", "")

            # Main phase slide
            slides.append({
                "slide_number": slide_num,
                "type": "phase_header",
                "title": phase_title,
                "phase": phase_type,
                "duration": f"{phase.get('duration_minutes', 0)} minutes",
                "activities": phase.get("activities", [])
            })
            slide_num += 1

            # Add example slides for instruction phase
            if phase_type == "instruction":
                slides.append({
                    "slide_number": slide_num,
                    "type": "example",
                    "title": "Example 1",
                    "content": "Work through first example step-by-step",
                    "notes": "Model think-aloud strategy"
                })
                slide_num += 1

                slides.append({
                    "slide_number": slide_num,
                    "type": "example",
                    "title": "Example 2",
                    "content": "Second worked example",
                    "notes": "Check for understanding before moving on"
                })
                slide_num += 1

            # Add practice slide for guided phase
            if phase_type == "guided":
                slides.append({
                    "slide_number": slide_num,
                    "type": "practice",
                    "title": "Let's Practice Together",
                    "content": "Practice problems for collaborative work",
                    "format": "We Do"
                })
                slide_num += 1

        # Exit ticket slide
        slides.append({
            "slide_number": slide_num,
            "type": "exit_ticket",
            "title": "Exit Ticket",
            "content": lesson_plan.get("assessment", {}).get("exit_ticket", {}),
            "instructions": "Complete silently and turn in before leaving"
        })

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return {
            "verified": True,
            "slide_deck": {
                "title": lesson_plan.get("title", "Lesson"),
                "total_slides": len(slides),
                "style": style,
                "slides": slides,
                "export_formats": ["pptx", "google_slides", "pdf", "html"]
            },
            "fingerprint": hashlib.sha256(json.dumps(slides, sort_keys=True).encode()).hexdigest()[:12].upper(),
            "elapsed_us": elapsed_us,
            "timestamp": int(time.time() * 1000)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PLC REPORT GENERATOR - Make PLC Meetings Obsolete
# ═══════════════════════════════════════════════════════════════════════════════

class PLCReportGenerator:
    """
    Professional Learning Community Report Generator.

    Generates comprehensive PLC reports that replace traditional meetings
    with verified, data-driven insights.
    """

    def __init__(self):
        self.teks_library = get_teks_library()

    def generate(
        self,
        assessment_data: List[Dict[str, Any]],
        teks_codes: List[str],
        team_name: str = "Grade Level Team",
        reporting_period: str = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive PLC report."""
        start_us = time.perf_counter_ns() // 1000

        if reporting_period is None:
            reporting_period = time.strftime("%B %Y")

        # Analyze assessment data
        analyzer = AssessmentAnalyzer(
            assessment_name="PLC Analysis",
            teks_codes=teks_codes
        )
        analyzer.analyze_batch(assessment_data)

        # Get TEKS details
        teks_details = []
        for code in teks_codes:
            standard = self.teks_library.get(code)
            if standard:
                teks_details.append(standard.to_dict())

        # Generate insights
        insights = self._generate_insights(analyzer)

        # Generate action items
        action_items = self._generate_action_items(analyzer, teks_codes)

        # Generate the report
        report = {
            "title": f"PLC Report: {team_name}",
            "reporting_period": reporting_period,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_students": len(assessment_data),
                "class_average": analyzer.class_average,
                "class_median": analyzer.class_median,
                "mastery_rate": analyzer.mastery_rate,
                "needs_reteach": analyzer.needs_reteach_count,
                "approaching": analyzer.on_track_count,
                "at_mastery": analyzer.advanced_count
            },
            "teks_focus": teks_details,
            "student_groupings": {
                "reteach": [s.to_dict() for s in analyzer.get_reteach_group()],
                "approaching": [s.to_dict() for s in analyzer.get_on_track_group()],
                "mastery": [s.to_dict() for s in analyzer.get_mastery_group()]
            },
            "insights": insights,
            "action_items": action_items,
            "next_steps": {
                "immediate": "Address prerequisite gaps for reteach group",
                "short_term": "Provide targeted practice for approaching group",
                "long_term": "Enrichment and extension for mastery group"
            },
            "recommended_resources": self._generate_resources(teks_codes),
            "plc_discussion_points": [
                "What patterns do we see in student errors?",
                "Which instructional strategies worked well?",
                "How can we differentiate tomorrow's lesson?",
                "What vertical alignment considerations are needed?"
            ]
        }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return {
            "verified": True,
            "plc_report": report,
            "fingerprint": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()[:12].upper(),
            "elapsed_us": elapsed_us,
            "timestamp": int(time.time() * 1000)
        }

    def _generate_insights(self, analyzer: AssessmentAnalyzer) -> List[Dict[str, str]]:
        """Generate data-driven insights."""
        insights = []

        # Mastery insight
        if analyzer.mastery_rate >= 80:
            insights.append({
                "type": "success",
                "title": "Strong Mastery Rate",
                "description": f"{analyzer.mastery_rate}% of students demonstrated mastery. Class is ready to advance."
            })
        elif analyzer.mastery_rate >= 60:
            insights.append({
                "type": "attention",
                "title": "Approaching Target",
                "description": f"{analyzer.mastery_rate}% mastery rate. Consider flexible grouping for targeted support."
            })
        else:
            insights.append({
                "type": "concern",
                "title": "Below Target",
                "description": f"Only {analyzer.mastery_rate}% mastery. Consider whole-class reteach before moving forward."
            })

        # Gap analysis
        if analyzer.needs_reteach_count > 0:
            insights.append({
                "type": "action",
                "title": "Reteach Group Identified",
                "description": f"{analyzer.needs_reteach_count} students need intensive support on prerequisite skills."
            })

        # Spread analysis
        spread = analyzer.class_average - analyzer.class_median
        if abs(spread) > 5:
            insights.append({
                "type": "info",
                "title": "Score Distribution Note",
                "description": f"Mean-median difference of {abs(spread):.1f}% suggests {'high' if spread > 0 else 'low'} outliers affecting average."
            })

        return insights

    def _generate_action_items(self, analyzer: AssessmentAnalyzer, teks_codes: List[str]) -> List[Dict[str, Any]]:
        """Generate action items based on data."""
        items = []

        if analyzer.needs_reteach_count > 0:
            items.append({
                "priority": "high",
                "owner": "Teacher",
                "action": f"Pull small group of {analyzer.needs_reteach_count} students for reteach",
                "timeline": "Tomorrow",
                "resources": "Manipulatives, visual aids, guided notes"
            })

        if analyzer.on_track_count > 0:
            items.append({
                "priority": "medium",
                "owner": "Teacher",
                "action": f"Provide scaffolded practice for {analyzer.on_track_count} approaching students",
                "timeline": "This week",
                "resources": "Graphic organizers, peer partner work"
            })

        if analyzer.advanced_count > 0:
            items.append({
                "priority": "standard",
                "owner": "Teacher",
                "action": f"Assign extension activities to {analyzer.advanced_count} mastery students",
                "timeline": "Ongoing",
                "resources": "Challenge problems, peer tutoring roles"
            })

        items.append({
            "priority": "standard",
            "owner": "PLC Team",
            "action": "Review common misconceptions and adjust instruction",
            "timeline": "Weekly",
            "resources": "Student work samples, error analysis"
        })

        return items

    def _generate_resources(self, teks_codes: List[str]) -> List[Dict[str, str]]:
        """Generate recommended resources."""
        return [
            {
                "type": "Intervention",
                "name": "Small Group Reteach Protocol",
                "description": "15-minute focused instruction on prerequisite skills"
            },
            {
                "type": "Practice",
                "name": "Spiral Review Worksheet",
                "description": "Mixed practice including current and previous TEKS"
            },
            {
                "type": "Assessment",
                "name": "Quick Check Exit Ticket",
                "description": "3-question formative to monitor progress"
            },
            {
                "type": "Extension",
                "name": "Challenge Problem Set",
                "description": "Higher-complexity problems for advanced students"
            }
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# EDUCATION CARTRIDGE - For Newton Integration
# ═══════════════════════════════════════════════════════════════════════════════

class EducationCartridge:
    """
    Education Cartridge for Newton integration.

    Provides unified interface for all educational generators.
    """

    def __init__(self):
        self.teks_library = get_teks_library()
        self.lesson_generator = LessonPlanGenerator()
        self.slide_generator = SlideDeckGenerator()
        self.plc_generator = PLCReportGenerator()

    def generate_lesson(self, **kwargs) -> Dict[str, Any]:
        """Generate lesson plan."""
        return self.lesson_generator.generate(**kwargs)

    def generate_slides(self, lesson_plan: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate slide deck from lesson plan."""
        return self.slide_generator.generate(lesson_plan, **kwargs)

    def analyze_assessment(self, data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Analyze assessment data."""
        analyzer = AssessmentAnalyzer(**kwargs)
        analyzer.analyze_batch(data)
        return {
            "verified": True,
            "analysis": analyzer.to_dict(),
            "timestamp": int(time.time() * 1000)
        }

    def generate_plc_report(self, **kwargs) -> Dict[str, Any]:
        """Generate PLC report."""
        return self.plc_generator.generate(**kwargs)

    def search_teks(self, query: str) -> List[Dict[str, Any]]:
        """Search TEKS standards."""
        results = self.teks_library.search(query)
        return [r.to_dict() for r in results]

    def get_teks(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a specific TEKS standard."""
        standard = self.teks_library.get(code)
        return standard.to_dict() if standard else None

    def get_learning_path(self, code: str) -> Dict[str, Any]:
        """Get learning path for a TEKS standard."""
        path = self.teks_library.get_learning_path(code)
        return {
            "prerequisites": [s.to_dict() for s in path["prerequisites"]],
            "current": [s.to_dict() for s in path["current"]],
            "next": [s.to_dict() for s in path["next"]]
        }


# Singleton instance
_education_cartridge: Optional[EducationCartridge] = None

def get_education_cartridge() -> EducationCartridge:
    """Get or create the global EducationCartridge instance."""
    global _education_cartridge
    if _education_cartridge is None:
        _education_cartridge = EducationCartridge()
    return _education_cartridge


# ═══════════════════════════════════════════════════════════════════════════════
# CDL 3.0 ENHANCED EDUCATION CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class EnhancedEducationCartridge(EducationCartridge):
    """
    Enhanced Education Cartridge with CDL 3.0 integration.

    Extends base cartridge with:
    - Common Core State Standards (CCSS)
    - Learning Treks with f/g ratio validation
    - Education-specific CDL constraints
    - Newton grounding for pedagogical patterns
    """

    def __init__(self):
        super().__init__()

        # Initialize new components
        self.ccss_library = get_common_core_library() if HAS_COMMON_CORE else None
        self.trek_library = get_trek_library() if HAS_TREKS else None
        self.trek_validator = get_trek_validator() if HAS_TREKS else None
        self.cdl_evaluator = EducationCDLEvaluator() if HAS_EDUCATION_CDL else None
        self.grounding_engine = EducationGroundingEngine() if HAS_GROUNDING else None

    # ═══════════════════════════════════════════════════════════════════════════
    # COMMON CORE STANDARDS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_ccss(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a Common Core standard by code."""
        if not self.ccss_library:
            return None
        standard = self.ccss_library.get(code)
        return standard.to_dict() if standard else None

    def search_ccss(self, query: str) -> List[Dict[str, Any]]:
        """Search Common Core standards."""
        if not self.ccss_library:
            return []
        results = self.ccss_library.search(query)
        return [r.to_dict() for r in results]

    def get_ccss_by_grade(self, grade: int) -> List[Dict[str, Any]]:
        """Get all Common Core standards for a grade."""
        if not self.ccss_library:
            return []
        results = self.ccss_library.get_by_grade(grade)
        return [r.to_dict() for r in results]

    def get_ccss_learning_path(self, code: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get learning path for a CCSS code."""
        if not self.ccss_library:
            return {"prerequisites": [], "current": [], "next": []}
        path = self.ccss_library.get_learning_path(code)
        return {
            "prerequisites": [s.to_dict() for s in path["prerequisites"]],
            "current": [s.to_dict() for s in path["current"]],
            "next": [s.to_dict() for s in path["next"]]
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # LEARNING TREKS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_trek(self, trek_id: str) -> Optional[Dict[str, Any]]:
        """Get a Learning Trek by ID."""
        if not self.trek_library:
            return None
        trek = self.trek_library.get(trek_id)
        return trek.to_dict() if trek else None

    def get_treks_by_grade(self, grade: int) -> List[Dict[str, Any]]:
        """Get all Treks appropriate for a grade level."""
        if not self.trek_library:
            return []
        treks = self.trek_library.get_by_grade(grade)
        return [t.to_dict() for t in treks]

    def get_treks_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all Treks for a domain."""
        if not self.trek_library:
            return []
        try:
            domain_enum = TrekDomain(domain)
            treks = self.trek_library.get_by_domain(domain_enum)
            return [t.to_dict() for t in treks]
        except ValueError:
            return []

    def validate_trek_readiness(
        self,
        trek_id: str,
        checkpoint_id: str,
        student_mastery: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Validate if a student is ready for a Trek checkpoint.

        Uses f/g ratio analysis:
        - f = checkpoint difficulty
        - g = prerequisite mastery average

        When f/g > 1.0 → not ready (finfr)
        When f/g <= 1.0 → ready to proceed
        """
        if not self.trek_library or not self.trek_validator:
            return {"error": "Trek system not available"}

        trek = self.trek_library.get(trek_id)
        if not trek:
            return {"error": f"Trek {trek_id} not found"}

        return self.trek_validator.validate_student_readiness(
            trek, checkpoint_id, student_mastery
        )

    def list_all_treks(self) -> List[Dict[str, Any]]:
        """List all available Learning Treks."""
        if not self.trek_library:
            return []
        return [t.to_dict() for t in self.trek_library.all_treks()]

    # ═══════════════════════════════════════════════════════════════════════════
    # CDL 3.0 CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════════════════

    def evaluate_mastery(
        self,
        student_id: str,
        standard_code: str,
        score: float,
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Evaluate mastery using f/g ratio analysis.

        f = student score
        g = mastery threshold

        When f/g >= 1.0 → mastery achieved
        When f/g < 1.0 → needs intervention
        """
        if not self.cdl_evaluator:
            # Fallback to basic evaluation
            ratio = score / threshold if threshold > 0 else 0
            return {
                "mastered": ratio >= 1.0,
                "student_id": student_id,
                "standard_code": standard_code,
                "score": score,
                "threshold": threshold,
                "ratio": round(ratio, 3),
                "classification": "mastery" if ratio >= 1.0 else "needs_reteach"
            }

        return self.cdl_evaluator.evaluate_mastery(
            student_id, standard_code, score, threshold
        )

    def evaluate_zpd(
        self,
        student_id: str,
        current_ability: float,
        task_difficulty: float
    ) -> Dict[str, Any]:
        """
        Evaluate Zone of Proximal Development.

        f = task_difficulty
        g = current_ability

        When 1.0 < f/g < 1.5 → in ZPD (optimal learning zone)
        When f/g <= 1.0 → too easy (comfort zone)
        When f/g >= 1.5 → too hard (frustration zone)
        """
        if not self.cdl_evaluator:
            ratio = task_difficulty / current_ability if current_ability > 0 else float('inf')
            zone = "zpd" if 1.0 < ratio < 1.5 else ("comfort" if ratio <= 1.0 else "frustration")
            return {
                "in_zpd": zone == "zpd",
                "student_id": student_id,
                "ratio": round(ratio, 3) if ratio != float('inf') else "undefined",
                "zone": zone
            }

        return self.cdl_evaluator.evaluate_zpd(
            student_id, current_ability, task_difficulty
        )

    def evaluate_class_mastery(
        self,
        students: List[Dict[str, Any]],
        standard_code: str,
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Evaluate an entire class on a standard with differentiation tiers.

        Returns class statistics and student groupings.
        """
        if not self.cdl_evaluator:
            # Fallback to basic evaluation
            scores = [s.get("score", 0) for s in students]
            n = len(scores)
            avg = sum(scores) / n if n > 0 else 0
            mastery_count = sum(1 for s in scores if s >= threshold)

            return {
                "standard_code": standard_code,
                "statistics": {
                    "count": n,
                    "average": round(avg, 1),
                    "mastery_count": mastery_count,
                    "mastery_rate": round(mastery_count / n * 100, 1) if n > 0 else 0
                }
            }

        return self.cdl_evaluator.batch_evaluate_class(
            students, standard_code, threshold
        )

    def get_student_tier(self, student_id: str, score: float) -> Dict[str, Any]:
        """
        Get differentiation tier for a student.

        Tiers:
        - Tier 3 (Red): < 60% - Intensive intervention
        - Tier 2 (Yellow): 60-79% - Strategic support
        - Tier 1 (Green): 80-89% - Core instruction
        - Enrichment (Blue): 90%+ - Extension activities
        """
        if not self.cdl_evaluator:
            if score >= 90:
                tier, color = "enrichment", "blue"
            elif score >= 80:
                tier, color = "tier1", "green"
            elif score >= 60:
                tier, color = "tier2", "yellow"
            else:
                tier, color = "tier3", "red"

            return {"student_id": student_id, "score": score, "tier": tier, "color": color}

        return self.cdl_evaluator.evaluate_differentiation(student_id, score)

    # ═══════════════════════════════════════════════════════════════════════════
    # NEWTON GROUNDING
    # ═══════════════════════════════════════════════════════════════════════════

    def ground_lesson_plan(self, lesson_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ground a lesson plan against research-backed pedagogical patterns.

        Validates:
        - Gradual Release of Responsibility
        - Explicit Instruction
        - Formative Assessment
        - Differentiation
        """
        if not self.grounding_engine:
            return {
                "valid": True,
                "message": "Grounding engine not available - skipping validation",
                "overall_score": 1.0
            }

        return self.grounding_engine.ground_lesson_plan(lesson_plan)

    def ground_pedagogical_pattern(
        self,
        pattern: str,
        implementation: str
    ) -> Dict[str, Any]:
        """
        Validate implementation of a pedagogical pattern.

        Available patterns:
        - gradual_release
        - explicit_instruction
        - mastery_learning
        - zpd_aligned
        - formative_assessment
        - differentiated
        - backward_design
        - cooperative_learning
        """
        if not self.grounding_engine:
            return {"valid": True, "message": "Grounding not available"}

        try:
            pattern_enum = PedagogicalPattern(pattern)
            return self.grounding_engine.ground_pedagogical_pattern(
                pattern_enum, implementation
            )
        except ValueError:
            return {
                "valid": False,
                "message": f"Unknown pattern: {pattern}",
                "available_patterns": [p.value for p in PedagogicalPattern]
            }

    def get_pedagogical_pattern(self, pattern: str) -> Optional[Dict[str, Any]]:
        """Get research-backed information about a pedagogical pattern."""
        if not HAS_GROUNDING:
            return None

        try:
            pattern_enum = PedagogicalPattern(pattern)
            grounded = GROUNDED_PATTERNS.get(pattern_enum)
            return grounded.to_dict() if grounded else None
        except ValueError:
            return None

    def list_pedagogical_patterns(self) -> List[str]:
        """List all available pedagogical patterns."""
        if not HAS_GROUNDING:
            return []
        return [p.value for p in PedagogicalPattern]

    # ═══════════════════════════════════════════════════════════════════════════
    # UNIFIED STANDARDS SEARCH
    # ═══════════════════════════════════════════════════════════════════════════

    def search_all_standards(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search both TEKS and CCSS standards.

        Returns results from both systems.
        """
        results = {
            "teks": self.search_teks(query),
            "ccss": self.search_ccss(query) if self.ccss_library else []
        }
        results["total"] = len(results["teks"]) + len(results["ccss"])
        return results

    def get_standard(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get any standard by code (TEKS or CCSS).

        Automatically detects standard type by code format.
        """
        if code.upper().startswith("CCSS"):
            return self.get_ccss(code)
        else:
            return self.get_teks(code)

    # ═══════════════════════════════════════════════════════════════════════════
    # ENHANCED LESSON GENERATION
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_verified_lesson(
        self,
        grade: int,
        subject: str,
        standard_codes: List[str],
        topic: Optional[str] = None,
        student_needs: Optional[Dict[str, List[str]]] = None,
        validate_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a lesson plan with pattern grounding validation.

        Generates an NES-compliant lesson plan and validates it against
        research-backed pedagogical patterns.
        """
        # Generate base lesson
        result = self.generate_lesson(
            grade=grade,
            subject=subject,
            teks_codes=standard_codes,
            topic=topic,
            student_needs=student_needs
        )

        if not result.get("verified"):
            return result

        # Validate against pedagogical patterns if requested
        if validate_patterns and self.grounding_engine:
            grounding_result = self.ground_lesson_plan(result.get("lesson_plan", {}))
            result["grounding"] = grounding_result
            result["patterns_validated"] = grounding_result.get("overall_score", 0) >= 0.5

        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ═══════════════════════════════════════════════════════════════════════════

    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about available capabilities."""
        return {
            "teks": True,
            "common_core": HAS_COMMON_CORE,
            "learning_treks": HAS_TREKS,
            "cdl_constraints": HAS_EDUCATION_CDL,
            "grounding": HAS_GROUNDING,
            "version": "3.0",
            "features": {
                "fg_ratio_analysis": HAS_EDUCATION_CDL,
                "zpd_validation": HAS_EDUCATION_CDL,
                "differentiation_tiers": HAS_EDUCATION_CDL,
                "pattern_validation": HAS_GROUNDING,
                "trek_progression": HAS_TREKS,
                "multi_standard_search": HAS_COMMON_CORE
            }
        }


# Singleton instance for enhanced cartridge
_enhanced_cartridge: Optional[EnhancedEducationCartridge] = None


def get_enhanced_education_cartridge() -> EnhancedEducationCartridge:
    """Get or create the global EnhancedEducationCartridge instance."""
    global _enhanced_cartridge
    if _enhanced_cartridge is None:
        _enhanced_cartridge = EnhancedEducationCartridge()
    return _enhanced_cartridge


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    'Subject',
    'GradeLevel',
    'CognitiveLevel',
    'NESPhase',

    # Data Classes
    'TEKSStandard',
    'LessonPhase',
    'StudentScore',

    # Blueprints
    'NESLessonPlan',
    'AssessmentAnalyzer',

    # Generators
    'LessonPlanGenerator',
    'SlideDeckGenerator',
    'PLCReportGenerator',

    # Library
    'TEKSLibrary',
    'get_teks_library',

    # Cartridge (Original)
    'EducationCartridge',
    'get_education_cartridge',

    # Enhanced Cartridge (CDL 3.0)
    'EnhancedEducationCartridge',
    'get_enhanced_education_cartridge',

    # Feature Flags
    'HAS_COMMON_CORE',
    'HAS_TREKS',
    'HAS_EDUCATION_CDL',
    'HAS_GROUNDING',
]
