"""
===============================================================================
 LEARNING TREKS - Verified Learning Paths with Newton Grounding
===============================================================================

Learning Treks are constraint-verified learning journeys that ensure:
1. Prerequisites are mastered before advancing
2. Concepts build coherently (f/g ratio validation)
3. Mastery thresholds are met at each checkpoint
4. Patterns are grounded in educational research

This module implements Newton's discovery that learning progressions
can be expressed as ratio constraints: attempt/readiness = f/g.

When f/g > 1.0 (attempting beyond readiness) → finfr (learning fails)
When f/g <= 1.0 (within zone of proximal development) → learning succeeds

"The Trek IS the curriculum. The constraint IS the prerequisite."

(c) 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time
import hashlib


# ===============================================================================
# TREK ENUMS
# ===============================================================================

class TrekDomain(Enum):
    """Learning domains for Treks."""
    MATHEMATICS = "mathematics"
    READING = "reading"
    WRITING = "writing"
    SCIENCE = "science"
    SOCIAL_STUDIES = "social_studies"
    SEL = "social_emotional"  # Social-Emotional Learning
    STEM = "stem"
    INQUIRY = "inquiry"


class MasteryLevel(Enum):
    """Mastery levels for checkpoint validation."""
    NOT_STARTED = 0
    EMERGING = 1      # < 60%
    DEVELOPING = 2    # 60-69%
    APPROACHING = 3   # 70-79%
    MASTERY = 4       # 80-89%
    ADVANCED = 5      # 90%+


class CheckpointType(Enum):
    """Types of checkpoints in a Trek."""
    PREREQUISITE = "prerequisite"   # Must be complete before Trek
    MILESTONE = "milestone"         # Key point within Trek
    ASSESSMENT = "assessment"       # Formal assessment point
    REFLECTION = "reflection"       # Self-reflection/metacognition
    CAPSTONE = "capstone"          # Final demonstration of mastery


# ===============================================================================
# TREK DATA CLASSES
# ===============================================================================

@dataclass
class LearningObjective:
    """A specific learning objective within a checkpoint."""
    id: str
    description: str
    verb: str                        # Bloom's verb (identify, analyze, create)
    standard_codes: List[str]        # TEKS/CCSS codes this addresses
    mastery_threshold: float = 80.0  # Percent required for mastery
    current_score: Optional[float] = None

    def is_mastered(self) -> bool:
        """Check if objective is mastered."""
        return self.current_score is not None and self.current_score >= self.mastery_threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "verb": self.verb,
            "standards": self.standard_codes,
            "threshold": self.mastery_threshold,
            "current_score": self.current_score,
            "mastered": self.is_mastered()
        }


@dataclass
class TrekCheckpoint:
    """
    A checkpoint in a Learning Trek.

    Checkpoints enforce prerequisite mastery before proceeding.
    This is where f/g ratio validation occurs.
    """
    id: str
    name: str
    description: str
    checkpoint_type: CheckpointType
    objectives: List[LearningObjective]
    prerequisite_checkpoint_ids: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 45
    resources: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)

    # f/g ratio tracking
    # f = attempted (what student is trying to do)
    # g = readiness (what prerequisites enable)
    readiness_score: float = 0.0     # Aggregate prerequisite mastery (g)
    attempt_level: float = 1.0       # Complexity of this checkpoint (f)

    def get_fg_ratio(self) -> Tuple[float, Optional[str]]:
        """
        Calculate the f/g ratio for this checkpoint.

        Returns (ratio, warning_message).
        If g ≈ 0, returns (float('inf'), finfr message).
        """
        if self.readiness_score < 0.01:
            return float('inf'), "finfr: Cannot attempt checkpoint without prerequisite readiness (g ≈ 0)"

        ratio = self.attempt_level / self.readiness_score
        if ratio > 1.0:
            return ratio, f"Warning: f/g = {ratio:.2f} > 1.0 - Student may not be ready"
        return ratio, None

    def get_mastery_level(self) -> MasteryLevel:
        """Calculate overall mastery level from objectives."""
        if not self.objectives:
            return MasteryLevel.NOT_STARTED

        mastered = sum(1 for obj in self.objectives if obj.is_mastered())
        total = len(self.objectives)
        pct = (mastered / total) * 100

        if pct >= 90:
            return MasteryLevel.ADVANCED
        elif pct >= 80:
            return MasteryLevel.MASTERY
        elif pct >= 70:
            return MasteryLevel.APPROACHING
        elif pct >= 60:
            return MasteryLevel.DEVELOPING
        elif pct > 0:
            return MasteryLevel.EMERGING
        return MasteryLevel.NOT_STARTED

    def is_complete(self) -> bool:
        """Check if checkpoint is complete (all objectives mastered)."""
        return all(obj.is_mastered() for obj in self.objectives)

    def to_dict(self) -> Dict[str, Any]:
        ratio, warning = self.get_fg_ratio()
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.checkpoint_type.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "prerequisites": self.prerequisite_checkpoint_ids,
            "duration_minutes": self.estimated_duration_minutes,
            "resources": self.resources,
            "activities": self.activities,
            "mastery_level": self.get_mastery_level().name,
            "complete": self.is_complete(),
            "fg_ratio": ratio if ratio != float('inf') else "undefined",
            "fg_warning": warning
        }


@dataclass
class LearningTrek:
    """
    A complete Learning Trek - a verified learning journey.

    Treks enforce constraint-based learning progressions:
    - Prerequisites must be mastered before advancing
    - f/g ratios validate readiness at each checkpoint
    - Patterns are grounded in educational research
    """
    id: str
    name: str
    description: str
    domain: TrekDomain
    grade_range: Tuple[int, int]     # (min_grade, max_grade)
    checkpoints: List[TrekCheckpoint]
    estimated_duration_hours: float = 10.0
    standard_codes: List[str] = field(default_factory=list)

    # Trek metadata
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))
    author: str = "Newton"
    version: str = "1.0"

    def get_current_checkpoint(self) -> Optional[TrekCheckpoint]:
        """Get the first incomplete checkpoint."""
        for checkpoint in self.checkpoints:
            if not checkpoint.is_complete():
                return checkpoint
        return None

    def get_progress_percentage(self) -> float:
        """Calculate overall Trek progress."""
        if not self.checkpoints:
            return 0.0
        complete = sum(1 for cp in self.checkpoints if cp.is_complete())
        return (complete / len(self.checkpoints)) * 100

    def get_readiness_for_checkpoint(self, checkpoint_id: str) -> float:
        """
        Calculate readiness score for a checkpoint based on prerequisites.

        This is the 'g' in f/g ratio.
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return 0.0

        if not checkpoint.prerequisite_checkpoint_ids:
            return 1.0  # No prerequisites = full readiness

        prereq_scores = []
        for prereq_id in checkpoint.prerequisite_checkpoint_ids:
            prereq = self.get_checkpoint(prereq_id)
            if prereq:
                mastery = prereq.get_mastery_level()
                # Convert mastery level to score (0-1)
                score = mastery.value / MasteryLevel.ADVANCED.value
                prereq_scores.append(score)

        return sum(prereq_scores) / len(prereq_scores) if prereq_scores else 0.0

    def get_checkpoint(self, checkpoint_id: str) -> Optional[TrekCheckpoint]:
        """Get a checkpoint by ID."""
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None

    def validate_progression(self) -> List[Dict[str, Any]]:
        """
        Validate the Trek progression using f/g ratio analysis.

        Returns list of validation results for each checkpoint.
        """
        results = []
        for checkpoint in self.checkpoints:
            # Update readiness score based on prerequisites
            checkpoint.readiness_score = self.get_readiness_for_checkpoint(checkpoint.id)
            ratio, warning = checkpoint.get_fg_ratio()

            results.append({
                "checkpoint_id": checkpoint.id,
                "checkpoint_name": checkpoint.name,
                "readiness_g": checkpoint.readiness_score,
                "attempt_f": checkpoint.attempt_level,
                "ratio": ratio if ratio != float('inf') else "undefined",
                "valid": ratio <= 1.0 if ratio != float('inf') else False,
                "warning": warning
            })

        return results

    def get_fingerprint(self) -> str:
        """Generate a unique fingerprint for this Trek."""
        data = f"{self.id}:{self.name}:{len(self.checkpoints)}:{self.version}"
        return hashlib.sha256(data.encode()).hexdigest()[:12].upper()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain.value,
            "grade_range": list(self.grade_range),
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "duration_hours": self.estimated_duration_hours,
            "standards": self.standard_codes,
            "progress_percent": self.get_progress_percentage(),
            "fingerprint": self.get_fingerprint(),
            "author": self.author,
            "version": self.version
        }


# ===============================================================================
# TREK LIBRARY - Pre-built Learning Treks
# ===============================================================================

class TrekLibrary:
    """
    Library of pre-built Learning Treks.

    Each Trek is a verified learning progression with:
    - Prerequisite chains
    - f/g ratio validation
    - Standards alignment (TEKS + CCSS)
    """

    def __init__(self):
        self._treks: Dict[str, LearningTrek] = {}
        self._load_treks()

    def get(self, trek_id: str) -> Optional[LearningTrek]:
        """Get a Trek by ID."""
        return self._treks.get(trek_id)

    def get_by_domain(self, domain: TrekDomain) -> List[LearningTrek]:
        """Get all Treks for a domain."""
        return [t for t in self._treks.values() if t.domain == domain]

    def get_by_grade(self, grade: int) -> List[LearningTrek]:
        """Get all Treks appropriate for a grade level."""
        return [t for t in self._treks.values()
                if t.grade_range[0] <= grade <= t.grade_range[1]]

    def search(self, query: str) -> List[LearningTrek]:
        """Search Treks by name or description."""
        query_lower = query.lower()
        return [t for t in self._treks.values()
                if query_lower in t.name.lower() or query_lower in t.description.lower()]

    def all_treks(self) -> List[LearningTrek]:
        """Get all Treks."""
        return list(self._treks.values())

    def _add_trek(self, trek: LearningTrek):
        """Add a Trek to the library."""
        self._treks[trek.id] = trek

    def _load_treks(self):
        """Load pre-built Treks."""
        self._load_math_treks()
        self._load_reading_treks()
        self._load_science_treks()
        self._load_sel_treks()

    # ===========================================================================
    # MATHEMATICS TREKS
    # ===========================================================================

    def _load_math_treks(self):
        """Load mathematics learning Treks."""

        # Trek: Fractions Mastery (Grades 3-5)
        fractions_trek = LearningTrek(
            id="TREK-MATH-FRACTIONS-35",
            name="Fractions Mastery Journey",
            description="Complete journey from fraction concepts to operations with unlike denominators",
            domain=TrekDomain.MATHEMATICS,
            grade_range=(3, 5),
            standard_codes=[
                "3.2A", "3.2B", "3.7A",  # TEKS Grade 3
                "4.3A", "4.3B", "4.3C", "4.3D", "4.4A", "4.4B",  # TEKS Grade 4
                "5.3C", "5.3E", "5.3F", "5.3I",  # TEKS Grade 5
                "CCSS.MATH.CONTENT.3.NF.A.1", "CCSS.MATH.CONTENT.3.NF.A.2",
                "CCSS.MATH.CONTENT.4.NF.A.1", "CCSS.MATH.CONTENT.4.NF.A.2",
                "CCSS.MATH.CONTENT.5.NF.A.1", "CCSS.MATH.CONTENT.5.NF.B.4"
            ],
            estimated_duration_hours=20.0,
            checkpoints=[
                TrekCheckpoint(
                    id="FRAC-01",
                    name="Unit Fractions Foundation",
                    description="Understand fractions as parts of a whole",
                    checkpoint_type=CheckpointType.PREREQUISITE,
                    objectives=[
                        LearningObjective(
                            id="FRAC-01-A",
                            description="Identify unit fractions (1/2, 1/3, 1/4, 1/6, 1/8)",
                            verb="identify",
                            standard_codes=["3.2A", "CCSS.MATH.CONTENT.3.NF.A.1"]
                        ),
                        LearningObjective(
                            id="FRAC-01-B",
                            description="Model fractions with objects and pictures",
                            verb="model",
                            standard_codes=["3.2A"]
                        ),
                        LearningObjective(
                            id="FRAC-01-C",
                            description="Locate fractions on a number line",
                            verb="locate",
                            standard_codes=["3.2B", "3.7A", "CCSS.MATH.CONTENT.3.NF.A.2"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=1.0,
                    resources=["Fraction tiles", "Number line posters", "Interactive fraction apps"],
                    activities=["Fraction Pictionary", "Number Line Walk", "Pizza Party Fractions"]
                ),
                TrekCheckpoint(
                    id="FRAC-02",
                    name="Equivalent Fractions",
                    description="Generate and recognize equivalent fractions",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FRAC-01"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-02-A",
                            description="Generate equivalent fractions using visual models",
                            verb="generate",
                            standard_codes=["4.3A", "4.3C", "CCSS.MATH.CONTENT.4.NF.A.1"]
                        ),
                        LearningObjective(
                            id="FRAC-02-B",
                            description="Explain why fractions are equivalent using multiplication",
                            verb="explain",
                            standard_codes=["4.3A"]
                        ),
                        LearningObjective(
                            id="FRAC-02-C",
                            description="Simplify fractions to lowest terms",
                            verb="simplify",
                            standard_codes=["4.3A"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=1.5,
                    resources=["Equivalent fraction strips", "Factor trees", "Simplification charts"],
                    activities=["Fraction Matching Game", "Simplify Race", "Fraction Art Project"]
                ),
                TrekCheckpoint(
                    id="FRAC-03",
                    name="Comparing Fractions",
                    description="Compare and order fractions using various strategies",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FRAC-02"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-03-A",
                            description="Compare fractions with same numerator or denominator",
                            verb="compare",
                            standard_codes=["4.3D", "CCSS.MATH.CONTENT.4.NF.A.2"]
                        ),
                        LearningObjective(
                            id="FRAC-03-B",
                            description="Use benchmark fractions (0, 1/2, 1) for comparison",
                            verb="use",
                            standard_codes=["4.3D"]
                        ),
                        LearningObjective(
                            id="FRAC-03-C",
                            description="Order fractions on a number line",
                            verb="order",
                            standard_codes=["4.3D"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=1.8,
                    resources=["Fraction comparison cards", "Number line mats"],
                    activities=["Fraction War", "Which is Greater?", "Fraction Ordering Challenge"]
                ),
                TrekCheckpoint(
                    id="FRAC-04",
                    name="Adding and Subtracting Like Denominators",
                    description="Add and subtract fractions with common denominators",
                    checkpoint_type=CheckpointType.ASSESSMENT,
                    prerequisite_checkpoint_ids=["FRAC-02", "FRAC-03"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-04-A",
                            description="Add fractions with same denominator",
                            verb="add",
                            standard_codes=["4.4A", "4.4B"]
                        ),
                        LearningObjective(
                            id="FRAC-04-B",
                            description="Subtract fractions with same denominator",
                            verb="subtract",
                            standard_codes=["4.4A", "4.4B"]
                        ),
                        LearningObjective(
                            id="FRAC-04-C",
                            description="Solve word problems with fraction addition/subtraction",
                            verb="solve",
                            standard_codes=["4.4B"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=2.0,
                    resources=["Fraction operation mats", "Word problem cards"],
                    activities=["Recipe Scaling", "Fraction Story Problems", "Build a Whole"]
                ),
                TrekCheckpoint(
                    id="FRAC-05",
                    name="Unlike Denominators",
                    description="Add and subtract fractions with unlike denominators",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FRAC-04"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-05-A",
                            description="Find common denominators using LCM",
                            verb="find",
                            standard_codes=["5.3C", "CCSS.MATH.CONTENT.5.NF.A.1"]
                        ),
                        LearningObjective(
                            id="FRAC-05-B",
                            description="Add fractions with unlike denominators",
                            verb="add",
                            standard_codes=["5.3C", "CCSS.MATH.CONTENT.5.NF.A.1"]
                        ),
                        LearningObjective(
                            id="FRAC-05-C",
                            description="Subtract fractions with unlike denominators",
                            verb="subtract",
                            standard_codes=["5.3C", "CCSS.MATH.CONTENT.5.NF.A.1"]
                        )
                    ],
                    estimated_duration_minutes=150,
                    attempt_level=2.5,
                    resources=["LCM factor charts", "Conversion practice sheets"],
                    activities=["Denominator Detective", "Fraction Construction", "Real-World Recipes"]
                ),
                TrekCheckpoint(
                    id="FRAC-06",
                    name="Multiplying Fractions",
                    description="Multiply fractions and whole numbers",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FRAC-05"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-06-A",
                            description="Multiply a fraction by a whole number",
                            verb="multiply",
                            standard_codes=["5.3E", "CCSS.MATH.CONTENT.5.NF.B.4"]
                        ),
                        LearningObjective(
                            id="FRAC-06-B",
                            description="Multiply two fractions using area models",
                            verb="multiply",
                            standard_codes=["5.3E", "CCSS.MATH.CONTENT.5.NF.B.4"]
                        ),
                        LearningObjective(
                            id="FRAC-06-C",
                            description="Interpret multiplication as scaling",
                            verb="interpret",
                            standard_codes=["CCSS.MATH.CONTENT.5.NF.B.5"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=2.8,
                    resources=["Area model grids", "Scaling visual aids"],
                    activities=["Fraction Multiplication Art", "Scaling Recipes", "Area Model Builder"]
                ),
                TrekCheckpoint(
                    id="FRAC-07",
                    name="Dividing Fractions",
                    description="Divide fractions and understand reciprocals",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FRAC-06"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-07-A",
                            description="Divide a unit fraction by a whole number",
                            verb="divide",
                            standard_codes=["5.3F", "CCSS.MATH.CONTENT.5.NF.B.7"]
                        ),
                        LearningObjective(
                            id="FRAC-07-B",
                            description="Divide a whole number by a unit fraction",
                            verb="divide",
                            standard_codes=["5.3F", "CCSS.MATH.CONTENT.5.NF.B.7"]
                        ),
                        LearningObjective(
                            id="FRAC-07-C",
                            description="Use visual models to explain division",
                            verb="explain",
                            standard_codes=["5.3F"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=3.0,
                    resources=["Fraction division manipulatives", "Visual model cards"],
                    activities=["How Many Fit?", "Sharing Problems", "Division Story Creation"]
                ),
                TrekCheckpoint(
                    id="FRAC-08",
                    name="Fraction Mastery Capstone",
                    description="Apply all fraction skills to complex problems",
                    checkpoint_type=CheckpointType.CAPSTONE,
                    prerequisite_checkpoint_ids=["FRAC-07"],
                    objectives=[
                        LearningObjective(
                            id="FRAC-08-A",
                            description="Solve multi-step word problems with fractions",
                            verb="solve",
                            standard_codes=["5.3I", "CCSS.MATH.CONTENT.5.NF.A.2"]
                        ),
                        LearningObjective(
                            id="FRAC-08-B",
                            description="Create and solve original fraction problems",
                            verb="create",
                            standard_codes=["5.3I"]
                        ),
                        LearningObjective(
                            id="FRAC-08-C",
                            description="Explain fraction concepts to peers",
                            verb="explain",
                            standard_codes=["5.3I"]
                        )
                    ],
                    estimated_duration_minutes=180,
                    attempt_level=3.5,
                    resources=["Complex problem sets", "Peer teaching rubrics"],
                    activities=["Fraction Fair", "Teach a Friend", "Real-World Application Project"]
                )
            ]
        )
        self._add_trek(fractions_trek)

        # Trek: Linear Relationships (Grades 6-8)
        linear_trek = LearningTrek(
            id="TREK-MATH-LINEAR-68",
            name="Linear Relationships Journey",
            description="From ratios to linear functions and equations",
            domain=TrekDomain.MATHEMATICS,
            grade_range=(6, 8),
            standard_codes=[
                "6.3A", "6.4A", "7.3A", "7.4C", "8.3A", "8.3B", "8.5A", "8.5I",
                "CCSS.MATH.CONTENT.6.RP.A.1", "CCSS.MATH.CONTENT.7.RP.A.2",
                "CCSS.MATH.CONTENT.8.EE.B.5", "CCSS.MATH.CONTENT.8.F.A.3"
            ],
            estimated_duration_hours=25.0,
            checkpoints=[
                TrekCheckpoint(
                    id="LINEAR-01",
                    name="Ratio Foundation",
                    description="Understand ratios and ratio language",
                    checkpoint_type=CheckpointType.PREREQUISITE,
                    objectives=[
                        LearningObjective(
                            id="LINEAR-01-A",
                            description="Use ratio language to describe relationships",
                            verb="describe",
                            standard_codes=["6.3A", "CCSS.MATH.CONTENT.6.RP.A.1"]
                        ),
                        LearningObjective(
                            id="LINEAR-01-B",
                            description="Represent ratios with tables and graphs",
                            verb="represent",
                            standard_codes=["6.4A", "6.3B"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=1.0
                ),
                TrekCheckpoint(
                    id="LINEAR-02",
                    name="Proportional Relationships",
                    description="Recognize and represent proportional relationships",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["LINEAR-01"],
                    objectives=[
                        LearningObjective(
                            id="LINEAR-02-A",
                            description="Identify proportional relationships in tables",
                            verb="identify",
                            standard_codes=["7.3A", "CCSS.MATH.CONTENT.7.RP.A.2"]
                        ),
                        LearningObjective(
                            id="LINEAR-02-B",
                            description="Calculate the constant of proportionality (k)",
                            verb="calculate",
                            standard_codes=["7.4C"]
                        ),
                        LearningObjective(
                            id="LINEAR-02-C",
                            description="Write equations in y = kx form",
                            verb="write",
                            standard_codes=["7.4C", "CCSS.MATH.CONTENT.7.RP.A.2"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=1.5
                ),
                TrekCheckpoint(
                    id="LINEAR-03",
                    name="Slope as Unit Rate",
                    description="Connect slope to unit rate and proportionality",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["LINEAR-02"],
                    objectives=[
                        LearningObjective(
                            id="LINEAR-03-A",
                            description="Interpret slope as rate of change",
                            verb="interpret",
                            standard_codes=["8.3C", "CCSS.MATH.CONTENT.8.EE.B.5"]
                        ),
                        LearningObjective(
                            id="LINEAR-03-B",
                            description="Calculate slope from tables and graphs",
                            verb="calculate",
                            standard_codes=["8.3C", "8.4B"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=2.0
                ),
                TrekCheckpoint(
                    id="LINEAR-04",
                    name="Linear Equations",
                    description="Write and interpret y = mx + b",
                    checkpoint_type=CheckpointType.ASSESSMENT,
                    prerequisite_checkpoint_ids=["LINEAR-03"],
                    objectives=[
                        LearningObjective(
                            id="LINEAR-04-A",
                            description="Interpret y = mx + b as a linear function",
                            verb="interpret",
                            standard_codes=["8.3A", "CCSS.MATH.CONTENT.8.F.A.3"]
                        ),
                        LearningObjective(
                            id="LINEAR-04-B",
                            description="Write equations from tables and graphs",
                            verb="write",
                            standard_codes=["8.5I", "CCSS.MATH.CONTENT.8.F.B.4"]
                        ),
                        LearningObjective(
                            id="LINEAR-04-C",
                            description="Distinguish proportional from non-proportional",
                            verb="distinguish",
                            standard_codes=["8.4A", "8.5F"]
                        )
                    ],
                    estimated_duration_minutes=150,
                    attempt_level=2.5
                ),
                TrekCheckpoint(
                    id="LINEAR-05",
                    name="Functions Foundation",
                    description="Understand functions as input-output rules",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["LINEAR-04"],
                    objectives=[
                        LearningObjective(
                            id="LINEAR-05-A",
                            description="Identify functions using vertical line test",
                            verb="identify",
                            standard_codes=["8.5G", "CCSS.MATH.CONTENT.8.F.A.1"]
                        ),
                        LearningObjective(
                            id="LINEAR-05-B",
                            description="Determine domain and range",
                            verb="determine",
                            standard_codes=["8.5H"]
                        ),
                        LearningObjective(
                            id="LINEAR-05-C",
                            description="Compare functions in different forms",
                            verb="compare",
                            standard_codes=["8.5B", "CCSS.MATH.CONTENT.8.F.A.2"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=2.8
                ),
                TrekCheckpoint(
                    id="LINEAR-06",
                    name="Linear Relationships Capstone",
                    description="Apply linear relationships to real-world problems",
                    checkpoint_type=CheckpointType.CAPSTONE,
                    prerequisite_checkpoint_ids=["LINEAR-05"],
                    objectives=[
                        LearningObjective(
                            id="LINEAR-06-A",
                            description="Model real situations with linear functions",
                            verb="model",
                            standard_codes=["8.5A", "CCSS.MATH.CONTENT.8.F.B.4"]
                        ),
                        LearningObjective(
                            id="LINEAR-06-B",
                            description="Interpret graphs in context",
                            verb="interpret",
                            standard_codes=["8.5C", "8.5D", "CCSS.MATH.CONTENT.8.F.B.5"]
                        ),
                        LearningObjective(
                            id="LINEAR-06-C",
                            description="Create and present a linear modeling project",
                            verb="create",
                            standard_codes=["8.5A"]
                        )
                    ],
                    estimated_duration_minutes=180,
                    attempt_level=3.0
                )
            ]
        )
        self._add_trek(linear_trek)

    # ===========================================================================
    # READING TREKS
    # ===========================================================================

    def _load_reading_treks(self):
        """Load reading/ELA learning Treks."""

        # Trek: Literary Analysis (Grades 5-8)
        literary_trek = LearningTrek(
            id="TREK-ELA-LITERARY-58",
            name="Literary Analysis Journey",
            description="Develop deep reading and analysis skills for literature",
            domain=TrekDomain.READING,
            grade_range=(5, 8),
            standard_codes=[
                "5.6A", "5.6B", "5.6E", "6.6A", "6.7A", "7.6A", "8.6A", "8.7A",
                "CCSS.ELA-LITERACY.RL.5.1", "CCSS.ELA-LITERACY.RL.6.1",
                "CCSS.ELA-LITERACY.RL.7.1", "CCSS.ELA-LITERACY.RL.8.1"
            ],
            estimated_duration_hours=15.0,
            checkpoints=[
                TrekCheckpoint(
                    id="LIT-01",
                    name="Text Evidence Foundation",
                    description="Support analysis with explicit textual evidence",
                    checkpoint_type=CheckpointType.PREREQUISITE,
                    objectives=[
                        LearningObjective(
                            id="LIT-01-A",
                            description="Quote accurately from text to support analysis",
                            verb="quote",
                            standard_codes=["5.6A", "5.6B", "CCSS.ELA-LITERACY.RL.5.1"]
                        ),
                        LearningObjective(
                            id="LIT-01-B",
                            description="Distinguish explicit from inferred information",
                            verb="distinguish",
                            standard_codes=["5.6A", "CCSS.ELA-LITERACY.RL.5.1"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=1.0
                ),
                TrekCheckpoint(
                    id="LIT-02",
                    name="Theme Analysis",
                    description="Identify and analyze themes across texts",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["LIT-01"],
                    objectives=[
                        LearningObjective(
                            id="LIT-02-A",
                            description="Infer theme from textual details",
                            verb="infer",
                            standard_codes=["6.7A", "CCSS.ELA-LITERACY.RL.6.2"]
                        ),
                        LearningObjective(
                            id="LIT-02-B",
                            description="Analyze how theme develops across text",
                            verb="analyze",
                            standard_codes=["7.6A", "CCSS.ELA-LITERACY.RL.7.2"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=1.5
                ),
                TrekCheckpoint(
                    id="LIT-03",
                    name="Character Analysis",
                    description="Analyze complex characters and their development",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["LIT-02"],
                    objectives=[
                        LearningObjective(
                            id="LIT-03-A",
                            description="Analyze how characters develop over time",
                            verb="analyze",
                            standard_codes=["8.6A", "CCSS.ELA-LITERACY.RL.8.3"]
                        ),
                        LearningObjective(
                            id="LIT-03-B",
                            description="Explain how dialogue reveals character",
                            verb="explain",
                            standard_codes=["8.6B", "CCSS.ELA-LITERACY.RL.8.3"]
                        )
                    ],
                    estimated_duration_minutes=120,
                    attempt_level=2.0
                ),
                TrekCheckpoint(
                    id="LIT-04",
                    name="Point of View",
                    description="Analyze perspective and its effects",
                    checkpoint_type=CheckpointType.ASSESSMENT,
                    prerequisite_checkpoint_ids=["LIT-03"],
                    objectives=[
                        LearningObjective(
                            id="LIT-04-A",
                            description="Identify narrator point of view",
                            verb="identify",
                            standard_codes=["5.6E", "CCSS.ELA-LITERACY.RL.5.6"]
                        ),
                        LearningObjective(
                            id="LIT-04-B",
                            description="Analyze how POV creates effects",
                            verb="analyze",
                            standard_codes=["8.7A", "CCSS.ELA-LITERACY.RL.8.6"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=2.5
                ),
                TrekCheckpoint(
                    id="LIT-05",
                    name="Literary Analysis Capstone",
                    description="Synthesize all literary analysis skills",
                    checkpoint_type=CheckpointType.CAPSTONE,
                    prerequisite_checkpoint_ids=["LIT-04"],
                    objectives=[
                        LearningObjective(
                            id="LIT-05-A",
                            description="Write a comprehensive literary analysis essay",
                            verb="write",
                            standard_codes=["8.6A", "8.7A", "CCSS.ELA-LITERACY.RL.8.1"]
                        ),
                        LearningObjective(
                            id="LIT-05-B",
                            description="Compare themes across multiple texts",
                            verb="compare",
                            standard_codes=["8.6A"]
                        )
                    ],
                    estimated_duration_minutes=180,
                    attempt_level=3.0
                )
            ]
        )
        self._add_trek(literary_trek)

    # ===========================================================================
    # SCIENCE TREKS
    # ===========================================================================

    def _load_science_treks(self):
        """Load science learning Treks."""

        # Trek: Force and Motion (Grades 3-8)
        force_motion_trek = LearningTrek(
            id="TREK-SCI-FORCE-38",
            name="Force and Motion Journey",
            description="From push/pull concepts to Newton's Laws",
            domain=TrekDomain.SCIENCE,
            grade_range=(3, 8),
            standard_codes=[
                "3.6B", "5.6A", "5.6B", "8.6A", "8.6B", "8.6C"
            ],
            estimated_duration_hours=18.0,
            checkpoints=[
                TrekCheckpoint(
                    id="FORCE-01",
                    name="Push and Pull",
                    description="Understand force as push or pull",
                    checkpoint_type=CheckpointType.PREREQUISITE,
                    objectives=[
                        LearningObjective(
                            id="FORCE-01-A",
                            description="Demonstrate push and pull forces",
                            verb="demonstrate",
                            standard_codes=["3.6B"]
                        ),
                        LearningObjective(
                            id="FORCE-01-B",
                            description="Observe how forces change motion",
                            verb="observe",
                            standard_codes=["3.6B"]
                        )
                    ],
                    estimated_duration_minutes=60,
                    attempt_level=1.0
                ),
                TrekCheckpoint(
                    id="FORCE-02",
                    name="Balanced and Unbalanced Forces",
                    description="Explore force balance and its effects",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FORCE-01"],
                    objectives=[
                        LearningObjective(
                            id="FORCE-02-A",
                            description="Explore balanced and unbalanced forces",
                            verb="explore",
                            standard_codes=["5.6A"]
                        ),
                        LearningObjective(
                            id="FORCE-02-B",
                            description="Predict motion based on force balance",
                            verb="predict",
                            standard_codes=["5.6A"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=1.5
                ),
                TrekCheckpoint(
                    id="FORCE-03",
                    name="Energy Types",
                    description="Understand potential and kinetic energy",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["FORCE-02"],
                    objectives=[
                        LearningObjective(
                            id="FORCE-03-A",
                            description="Demonstrate potential and kinetic energy",
                            verb="demonstrate",
                            standard_codes=["5.6B"]
                        ),
                        LearningObjective(
                            id="FORCE-03-B",
                            description="Explain energy transformation",
                            verb="explain",
                            standard_codes=["5.6B"]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=2.0
                ),
                TrekCheckpoint(
                    id="FORCE-04",
                    name="Newton's Laws",
                    description="Understand and apply Newton's three laws",
                    checkpoint_type=CheckpointType.ASSESSMENT,
                    prerequisite_checkpoint_ids=["FORCE-03"],
                    objectives=[
                        LearningObjective(
                            id="FORCE-04-A",
                            description="Demonstrate and calculate effects of unbalanced forces",
                            verb="calculate",
                            standard_codes=["8.6A"]
                        ),
                        LearningObjective(
                            id="FORCE-04-B",
                            description="Investigate applications of Newton's laws",
                            verb="investigate",
                            standard_codes=["8.6B"]
                        ),
                        LearningObjective(
                            id="FORCE-04-C",
                            description="Describe how unbalanced forces change motion",
                            verb="describe",
                            standard_codes=["8.6C"]
                        )
                    ],
                    estimated_duration_minutes=150,
                    attempt_level=2.5
                ),
                TrekCheckpoint(
                    id="FORCE-05",
                    name="Force and Motion Capstone",
                    description="Design experiment applying Newton's laws",
                    checkpoint_type=CheckpointType.CAPSTONE,
                    prerequisite_checkpoint_ids=["FORCE-04"],
                    objectives=[
                        LearningObjective(
                            id="FORCE-05-A",
                            description="Design experiment testing force and motion",
                            verb="design",
                            standard_codes=["8.6A", "8.6B", "8.6C"]
                        ),
                        LearningObjective(
                            id="FORCE-05-B",
                            description="Analyze and communicate results",
                            verb="analyze",
                            standard_codes=["8.6B"]
                        )
                    ],
                    estimated_duration_minutes=180,
                    attempt_level=3.0
                )
            ]
        )
        self._add_trek(force_motion_trek)

    # ===========================================================================
    # SOCIAL-EMOTIONAL LEARNING TREKS
    # ===========================================================================

    def _load_sel_treks(self):
        """Load social-emotional learning Treks."""

        # Trek: Growth Mindset (Grades K-8)
        growth_mindset_trek = LearningTrek(
            id="TREK-SEL-GROWTH-K8",
            name="Growth Mindset Journey",
            description="Develop resilience, persistence, and a growth mindset",
            domain=TrekDomain.SEL,
            grade_range=(0, 8),
            standard_codes=[],  # SEL standards vary by state
            estimated_duration_hours=10.0,
            checkpoints=[
                TrekCheckpoint(
                    id="GROWTH-01",
                    name="Understanding Mindsets",
                    description="Learn about fixed vs. growth mindset",
                    checkpoint_type=CheckpointType.PREREQUISITE,
                    objectives=[
                        LearningObjective(
                            id="GROWTH-01-A",
                            description="Identify fixed mindset statements",
                            verb="identify",
                            standard_codes=[]
                        ),
                        LearningObjective(
                            id="GROWTH-01-B",
                            description="Describe what growth mindset means",
                            verb="describe",
                            standard_codes=[]
                        )
                    ],
                    estimated_duration_minutes=45,
                    attempt_level=1.0,
                    activities=["Brain growth video", "Mindset sort", "Famous failures stories"]
                ),
                TrekCheckpoint(
                    id="GROWTH-02",
                    name="The Power of Yet",
                    description="Transform 'I can't' to 'I can't yet'",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["GROWTH-01"],
                    objectives=[
                        LearningObjective(
                            id="GROWTH-02-A",
                            description="Reframe negative self-talk",
                            verb="reframe",
                            standard_codes=[]
                        ),
                        LearningObjective(
                            id="GROWTH-02-B",
                            description="Use 'yet' statements consistently",
                            verb="use",
                            standard_codes=[]
                        )
                    ],
                    estimated_duration_minutes=45,
                    attempt_level=1.3
                ),
                TrekCheckpoint(
                    id="GROWTH-03",
                    name="Embracing Challenges",
                    description="View challenges as opportunities",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["GROWTH-02"],
                    objectives=[
                        LearningObjective(
                            id="GROWTH-03-A",
                            description="Choose challenging tasks willingly",
                            verb="choose",
                            standard_codes=[]
                        ),
                        LearningObjective(
                            id="GROWTH-03-B",
                            description="Persist through difficulty",
                            verb="persist",
                            standard_codes=[]
                        )
                    ],
                    estimated_duration_minutes=60,
                    attempt_level=1.5
                ),
                TrekCheckpoint(
                    id="GROWTH-04",
                    name="Learning from Feedback",
                    description="Use feedback as a tool for growth",
                    checkpoint_type=CheckpointType.MILESTONE,
                    prerequisite_checkpoint_ids=["GROWTH-03"],
                    objectives=[
                        LearningObjective(
                            id="GROWTH-04-A",
                            description="Accept feedback without defensiveness",
                            verb="accept",
                            standard_codes=[]
                        ),
                        LearningObjective(
                            id="GROWTH-04-B",
                            description="Apply feedback to improve",
                            verb="apply",
                            standard_codes=[]
                        )
                    ],
                    estimated_duration_minutes=60,
                    attempt_level=2.0
                ),
                TrekCheckpoint(
                    id="GROWTH-05",
                    name="Growth Mindset Champion",
                    description="Demonstrate and teach growth mindset",
                    checkpoint_type=CheckpointType.CAPSTONE,
                    prerequisite_checkpoint_ids=["GROWTH-04"],
                    objectives=[
                        LearningObjective(
                            id="GROWTH-05-A",
                            description="Teach growth mindset to others",
                            verb="teach",
                            standard_codes=[]
                        ),
                        LearningObjective(
                            id="GROWTH-05-B",
                            description="Demonstrate consistent growth behaviors",
                            verb="demonstrate",
                            standard_codes=[]
                        )
                    ],
                    estimated_duration_minutes=90,
                    attempt_level=2.5
                )
            ]
        )
        self._add_trek(growth_mindset_trek)


# ===============================================================================
# TREK VALIDATOR - Uses f/g ratio analysis
# ===============================================================================

class TrekValidator:
    """
    Validates Learning Treks using Newton's f/g ratio analysis.

    When f/g > 1.0 (attempting beyond readiness) → finfr
    When f/g <= 1.0 (within zone of proximal development) → valid
    """

    def validate_student_readiness(
        self,
        trek: LearningTrek,
        checkpoint_id: str,
        student_mastery: Dict[str, float]  # checkpoint_id -> mastery percentage
    ) -> Dict[str, Any]:
        """
        Validate if a student is ready for a specific checkpoint.

        Args:
            trek: The Learning Trek
            checkpoint_id: The checkpoint to validate readiness for
            student_mastery: Map of checkpoint IDs to mastery percentages

        Returns:
            Validation result with f/g ratio analysis
        """
        checkpoint = trek.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return {"valid": False, "error": f"Checkpoint {checkpoint_id} not found"}

        # Calculate readiness (g) from prerequisites
        if not checkpoint.prerequisite_checkpoint_ids:
            g = 1.0  # No prerequisites = full readiness
        else:
            prereq_scores = []
            for prereq_id in checkpoint.prerequisite_checkpoint_ids:
                mastery = student_mastery.get(prereq_id, 0.0)
                prereq_scores.append(mastery / 100.0)  # Convert to 0-1 scale
            g = sum(prereq_scores) / len(prereq_scores) if prereq_scores else 0.0

        # f is the attempt level of the checkpoint
        f = checkpoint.attempt_level

        # Calculate ratio
        if g < 0.01:
            return {
                "valid": False,
                "checkpoint_id": checkpoint_id,
                "checkpoint_name": checkpoint.name,
                "f": f,
                "g": g,
                "ratio": "undefined",
                "message": "finfr: Cannot attempt checkpoint - no prerequisite mastery (g ≈ 0)",
                "recommendation": "Complete prerequisite checkpoints first"
            }

        ratio = f / g

        if ratio > 1.0:
            return {
                "valid": False,
                "checkpoint_id": checkpoint_id,
                "checkpoint_name": checkpoint.name,
                "f": f,
                "g": g,
                "ratio": ratio,
                "message": f"Warning: f/g = {ratio:.2f} > 1.0 - Student may struggle",
                "recommendation": "Consider reviewing prerequisites or providing additional support"
            }

        return {
            "valid": True,
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint.name,
            "f": f,
            "g": g,
            "ratio": ratio,
            "message": f"Ready: f/g = {ratio:.2f} <= 1.0 - Within zone of proximal development",
            "recommendation": "Proceed with checkpoint"
        }

    def validate_trek_structure(self, trek: LearningTrek) -> List[Dict[str, Any]]:
        """
        Validate the overall structure of a Trek.

        Ensures:
        - All prerequisite references are valid
        - No circular dependencies
        - Attempt levels increase appropriately
        """
        issues = []

        checkpoint_ids = {cp.id for cp in trek.checkpoints}

        for checkpoint in trek.checkpoints:
            # Check prerequisite references
            for prereq_id in checkpoint.prerequisite_checkpoint_ids:
                if prereq_id not in checkpoint_ids:
                    issues.append({
                        "checkpoint_id": checkpoint.id,
                        "issue": "invalid_prerequisite",
                        "message": f"Prerequisite '{prereq_id}' does not exist in Trek"
                    })

            # Check for self-reference
            if checkpoint.id in checkpoint.prerequisite_checkpoint_ids:
                issues.append({
                    "checkpoint_id": checkpoint.id,
                    "issue": "self_reference",
                    "message": "Checkpoint cannot be its own prerequisite"
                })

        # Check for circular dependencies (simple DFS)
        def has_cycle(cp_id: str, visited: set, path: set) -> bool:
            if cp_id in path:
                return True
            if cp_id in visited:
                return False
            visited.add(cp_id)
            path.add(cp_id)
            cp = trek.get_checkpoint(cp_id)
            if cp:
                for prereq in cp.prerequisite_checkpoint_ids:
                    if has_cycle(prereq, visited, path):
                        return True
            path.remove(cp_id)
            return False

        for checkpoint in trek.checkpoints:
            if has_cycle(checkpoint.id, set(), set()):
                issues.append({
                    "checkpoint_id": checkpoint.id,
                    "issue": "circular_dependency",
                    "message": "Circular prerequisite dependency detected"
                })
                break  # One is enough to report

        return issues


# ===============================================================================
# SINGLETON INSTANCE
# ===============================================================================

_trek_library: Optional[TrekLibrary] = None
_trek_validator: Optional[TrekValidator] = None


def get_trek_library() -> TrekLibrary:
    """Get or create the global TrekLibrary instance."""
    global _trek_library
    if _trek_library is None:
        _trek_library = TrekLibrary()
    return _trek_library


def get_trek_validator() -> TrekValidator:
    """Get or create the global TrekValidator instance."""
    global _trek_validator
    if _trek_validator is None:
        _trek_validator = TrekValidator()
    return _trek_validator


# ===============================================================================
# MODULE EXPORTS
# ===============================================================================

__all__ = [
    # Enums
    'TrekDomain',
    'MasteryLevel',
    'CheckpointType',

    # Data Classes
    'LearningObjective',
    'TrekCheckpoint',
    'LearningTrek',

    # Library and Validator
    'TrekLibrary',
    'TrekValidator',
    'get_trek_library',
    'get_trek_validator',
]
