"""
===============================================================================
 EDUCATION CDL - Constraint Definition Language for Learning
===============================================================================

Education-specific CDL 3.0 constraints for verified learning computation.

This module extends Newton's CDL with education domain constraints:
- Mastery thresholds (f/g ratio: attempt/readiness)
- Learning progression validation
- Assessment integrity checks
- Zone of Proximal Development (ZPD) constraints

"The mastery threshold IS the law. The f/g ratio IS the readiness."

(c) 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
===============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time
import hashlib

# Import CDL core
from core.cdl import (
    Domain, Operator, AtomicConstraint, RatioConstraint,
    CompositeConstraint, ConditionalConstraint, Constraint,
    EvaluationResult, CDLEvaluator, CDLParser, verify, ratio
)


# ===============================================================================
# EDUCATION DOMAIN
# ===============================================================================

class EducationDomain(Enum):
    """Education-specific constraint domains."""
    MASTERY = "mastery"                    # Skill mastery thresholds
    PROGRESSION = "progression"            # Learning path constraints
    ASSESSMENT = "assessment"              # Assessment integrity
    ACCOMMODATION = "accommodation"        # Student accommodations
    ZPD = "zone_of_proximal_development"  # Vygotsky's ZPD
    DIFFERENTIATION = "differentiation"    # Tiered instruction


# ===============================================================================
# EDUCATION CONSTRAINT PATTERNS
# ===============================================================================

@dataclass
class MasteryConstraint:
    """
    Mastery threshold constraint using f/g ratio analysis.

    f = student_score (what they achieved)
    g = mastery_threshold (what's required)

    When f/g >= 1.0 → mastery achieved
    When f/g < 1.0 → needs intervention
    """
    student_id: str
    standard_code: str
    score_field: str = "score"
    threshold_field: str = "threshold"
    mastery_threshold: float = 80.0
    domain: EducationDomain = EducationDomain.MASTERY
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            data = f"mastery:{self.student_id}:{self.standard_code}:{self.mastery_threshold}"
            self.id = f"MAST_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def to_ratio_constraint(self) -> RatioConstraint:
        """Convert to CDL RatioConstraint for evaluation."""
        return RatioConstraint(
            f_field=self.score_field,
            g_field=self.threshold_field,
            operator=Operator.RATIO_GE,
            threshold=1.0,
            domain=Domain.CUSTOM,
            message=f"Mastery not achieved for {self.standard_code}: score/threshold < 1.0",
            id=self.id
        )

    def evaluate(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate mastery status.

        Args:
            obj: Object with score and threshold fields

        Returns:
            Mastery evaluation result
        """
        score = obj.get(self.score_field, 0)
        threshold = obj.get(self.threshold_field, self.mastery_threshold)

        if threshold == 0:
            return {
                "mastered": False,
                "student_id": self.student_id,
                "standard_code": self.standard_code,
                "score": score,
                "threshold": threshold,
                "ratio": "undefined",
                "message": "finfr: Threshold cannot be zero",
                "classification": "invalid"
            }

        ratio = score / threshold

        # Classify mastery level
        if ratio >= 1.125:  # 90%+ when threshold is 80
            classification = "advanced"
        elif ratio >= 1.0:  # At threshold
            classification = "mastery"
        elif ratio >= 0.875:  # 70%+ when threshold is 80
            classification = "approaching"
        else:
            classification = "needs_reteach"

        return {
            "mastered": ratio >= 1.0,
            "student_id": self.student_id,
            "standard_code": self.standard_code,
            "score": score,
            "threshold": threshold,
            "ratio": round(ratio, 3),
            "percentage": round(score / threshold * 100, 1) if threshold > 0 else 0,
            "classification": classification,
            "message": f"Mastery {'achieved' if ratio >= 1.0 else 'not achieved'}: {score}/{threshold} = {ratio:.2f}"
        }


@dataclass
class ZPDConstraint:
    """
    Zone of Proximal Development constraint.

    Based on Vygotsky's theory that learning occurs in the zone between
    what a learner can do independently and what they can do with support.

    f = task_difficulty (what's being attempted)
    g = current_ability (what student can do independently)

    When 1.0 < f/g < 1.5 → In ZPD (optimal learning zone)
    When f/g <= 1.0 → Too easy (no growth)
    When f/g >= 1.5 → Too hard (frustration zone)
    """
    student_id: str
    current_ability: float
    task_difficulty: float
    zpd_lower: float = 1.0   # Lower bound of ZPD
    zpd_upper: float = 1.5   # Upper bound of ZPD
    domain: EducationDomain = EducationDomain.ZPD
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            data = f"zpd:{self.student_id}:{self.current_ability}:{self.task_difficulty}"
            self.id = f"ZPD_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def evaluate(self) -> Dict[str, Any]:
        """Evaluate if task is within ZPD."""
        if self.current_ability == 0:
            return {
                "in_zpd": False,
                "student_id": self.student_id,
                "ratio": "undefined",
                "zone": "invalid",
                "message": "finfr: Cannot evaluate ZPD without baseline ability",
                "recommendation": "Establish baseline ability first"
            }

        ratio = self.task_difficulty / self.current_ability

        if ratio < self.zpd_lower:
            zone = "comfort"
            recommendation = "Increase challenge level"
            in_zpd = False
        elif ratio > self.zpd_upper:
            zone = "frustration"
            recommendation = "Reduce challenge or provide more scaffolding"
            in_zpd = False
        else:
            zone = "zpd"
            recommendation = "Optimal learning zone - proceed with support"
            in_zpd = True

        return {
            "in_zpd": in_zpd,
            "student_id": self.student_id,
            "current_ability": self.current_ability,
            "task_difficulty": self.task_difficulty,
            "ratio": round(ratio, 3),
            "zone": zone,
            "zpd_range": [self.zpd_lower, self.zpd_upper],
            "message": f"Task/Ability ratio: {ratio:.2f} ({zone} zone)",
            "recommendation": recommendation
        }


@dataclass
class ProgressionConstraint:
    """
    Learning progression constraint.

    Ensures prerequisites are mastered before advancing.

    f = current_checkpoint_difficulty
    g = prerequisite_mastery_average

    When f/g > 1.0 → Not ready to advance (prerequisites not mastered)
    When f/g <= 1.0 → Ready to proceed
    """
    student_id: str
    target_checkpoint: str
    prerequisite_mastery: Dict[str, float]  # checkpoint_id -> mastery %
    target_difficulty: float = 1.0
    domain: EducationDomain = EducationDomain.PROGRESSION
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            data = f"prog:{self.student_id}:{self.target_checkpoint}"
            self.id = f"PROG_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def evaluate(self) -> Dict[str, Any]:
        """Evaluate readiness to proceed."""
        if not self.prerequisite_mastery:
            # No prerequisites = ready to proceed
            return {
                "ready": True,
                "student_id": self.student_id,
                "target_checkpoint": self.target_checkpoint,
                "ratio": 1.0,
                "message": "No prerequisites required",
                "gaps": []
            }

        # Calculate average prerequisite mastery (g)
        mastery_scores = list(self.prerequisite_mastery.values())
        avg_mastery = sum(mastery_scores) / len(mastery_scores) / 100  # Convert to 0-1

        if avg_mastery < 0.01:
            return {
                "ready": False,
                "student_id": self.student_id,
                "target_checkpoint": self.target_checkpoint,
                "ratio": "undefined",
                "message": "finfr: No prerequisite mastery (g ≈ 0)",
                "gaps": list(self.prerequisite_mastery.keys()),
                "recommendation": "Complete all prerequisites first"
            }

        ratio = self.target_difficulty / avg_mastery

        # Identify gaps (prerequisites below 80% mastery)
        gaps = [cp for cp, score in self.prerequisite_mastery.items() if score < 80]

        return {
            "ready": ratio <= 1.0,
            "student_id": self.student_id,
            "target_checkpoint": self.target_checkpoint,
            "prerequisite_average": round(avg_mastery * 100, 1),
            "target_difficulty": self.target_difficulty,
            "ratio": round(ratio, 3),
            "message": f"Readiness ratio: {ratio:.2f} {'(<= 1.0, ready)' if ratio <= 1.0 else '(> 1.0, not ready)'}",
            "gaps": gaps,
            "recommendation": "Proceed" if ratio <= 1.0 else f"Review: {', '.join(gaps)}"
        }


@dataclass
class AssessmentIntegrityConstraint:
    """
    Assessment integrity constraints.

    Ensures assessment data is valid and reliable.
    """
    assessment_id: str
    min_questions: int = 3
    max_time_seconds: int = 3600  # 1 hour
    min_completion_rate: float = 0.8  # 80% of questions answered
    domain: EducationDomain = EducationDomain.ASSESSMENT
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            data = f"assess:{self.assessment_id}"
            self.id = f"ASSESS_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def evaluate(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate assessment integrity.

        Args:
            obj: Assessment data with:
                - total_questions: int
                - answered_questions: int
                - time_elapsed_seconds: int
        """
        issues = []

        total = obj.get("total_questions", 0)
        answered = obj.get("answered_questions", 0)
        elapsed = obj.get("time_elapsed_seconds", 0)

        # Check minimum questions
        if total < self.min_questions:
            issues.append(f"Too few questions: {total} < {self.min_questions}")

        # Check completion rate
        completion_rate = answered / total if total > 0 else 0
        if completion_rate < self.min_completion_rate:
            issues.append(f"Low completion: {completion_rate:.1%} < {self.min_completion_rate:.1%}")

        # Check time
        if elapsed > self.max_time_seconds:
            issues.append(f"Exceeded time limit: {elapsed}s > {self.max_time_seconds}s")

        # Check for suspiciously fast completion (less than 10 sec per question)
        if total > 0 and elapsed < total * 10:
            issues.append(f"Suspiciously fast: {elapsed/total:.1f}s per question")

        return {
            "valid": len(issues) == 0,
            "assessment_id": self.assessment_id,
            "total_questions": total,
            "answered_questions": answered,
            "completion_rate": round(completion_rate, 3),
            "time_elapsed_seconds": elapsed,
            "issues": issues,
            "message": "Assessment valid" if not issues else f"Issues: {'; '.join(issues)}"
        }


@dataclass
class DifferentiationConstraint:
    """
    Differentiation tier constraint.

    Assigns students to appropriate instructional tiers based on mastery.

    Tiers:
    - Tier 3 (Intensive): < 60% mastery
    - Tier 2 (Strategic): 60-79% mastery
    - Tier 1 (Core): 80-89% mastery
    - Enrichment: 90%+ mastery
    """
    student_id: str
    mastery_score: float
    domain: EducationDomain = EducationDomain.DIFFERENTIATION
    id: Optional[str] = None

    # Tier thresholds
    tier3_threshold: float = 60.0
    tier2_threshold: float = 80.0
    enrichment_threshold: float = 90.0

    def __post_init__(self):
        if self.id is None:
            data = f"diff:{self.student_id}:{self.mastery_score}"
            self.id = f"DIFF_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"

    def evaluate(self) -> Dict[str, Any]:
        """Determine appropriate differentiation tier."""
        if self.mastery_score >= self.enrichment_threshold:
            tier = "enrichment"
            color = "blue"
            instruction = "Extension activities, peer tutoring, independent projects"
        elif self.mastery_score >= self.tier2_threshold:
            tier = "tier1"
            color = "green"
            instruction = "Grade-level core instruction, independent practice"
        elif self.mastery_score >= self.tier3_threshold:
            tier = "tier2"
            color = "yellow"
            instruction = "Strategic intervention, guided practice with scaffolds"
        else:
            tier = "tier3"
            color = "red"
            instruction = "Intensive intervention, small group with manipulatives"

        return {
            "student_id": self.student_id,
            "mastery_score": self.mastery_score,
            "tier": tier,
            "color": color,
            "instruction": instruction,
            "thresholds": {
                "tier3": f"< {self.tier3_threshold}%",
                "tier2": f"{self.tier3_threshold}-{self.tier2_threshold-1}%",
                "tier1": f"{self.tier2_threshold}-{self.enrichment_threshold-1}%",
                "enrichment": f">= {self.enrichment_threshold}%"
            }
        }


# ===============================================================================
# EDUCATION CDL EVALUATOR
# ===============================================================================

class EducationCDLEvaluator:
    """
    CDL Evaluator specialized for education constraints.

    Extends base CDL evaluation with education-specific patterns.
    """

    def __init__(self):
        self.base_evaluator = CDLEvaluator()
        self._evaluation_count = 0

    def evaluate_mastery(
        self,
        student_id: str,
        standard_code: str,
        score: float,
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """Evaluate mastery using f/g ratio."""
        constraint = MasteryConstraint(
            student_id=student_id,
            standard_code=standard_code,
            mastery_threshold=threshold
        )
        self._evaluation_count += 1
        return constraint.evaluate({"score": score, "threshold": threshold})

    def evaluate_zpd(
        self,
        student_id: str,
        current_ability: float,
        task_difficulty: float
    ) -> Dict[str, Any]:
        """Evaluate Zone of Proximal Development."""
        constraint = ZPDConstraint(
            student_id=student_id,
            current_ability=current_ability,
            task_difficulty=task_difficulty
        )
        self._evaluation_count += 1
        return constraint.evaluate()

    def evaluate_progression(
        self,
        student_id: str,
        target_checkpoint: str,
        prerequisite_mastery: Dict[str, float],
        target_difficulty: float = 1.0
    ) -> Dict[str, Any]:
        """Evaluate learning progression readiness."""
        constraint = ProgressionConstraint(
            student_id=student_id,
            target_checkpoint=target_checkpoint,
            prerequisite_mastery=prerequisite_mastery,
            target_difficulty=target_difficulty
        )
        self._evaluation_count += 1
        return constraint.evaluate()

    def evaluate_assessment_integrity(
        self,
        assessment_id: str,
        total_questions: int,
        answered_questions: int,
        time_elapsed_seconds: int
    ) -> Dict[str, Any]:
        """Evaluate assessment integrity."""
        constraint = AssessmentIntegrityConstraint(assessment_id=assessment_id)
        self._evaluation_count += 1
        return constraint.evaluate({
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "time_elapsed_seconds": time_elapsed_seconds
        })

    def evaluate_differentiation(
        self,
        student_id: str,
        mastery_score: float
    ) -> Dict[str, Any]:
        """Determine differentiation tier."""
        constraint = DifferentiationConstraint(
            student_id=student_id,
            mastery_score=mastery_score
        )
        self._evaluation_count += 1
        return constraint.evaluate()

    def batch_evaluate_class(
        self,
        students: List[Dict[str, Any]],
        standard_code: str,
        threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Evaluate an entire class on a standard.

        Args:
            students: List of {student_id, score} dicts
            standard_code: The standard being assessed
            threshold: Mastery threshold

        Returns:
            Class-level analysis with groupings
        """
        results = []
        tiers = {"tier3": [], "tier2": [], "tier1": [], "enrichment": []}

        for student in students:
            mastery = self.evaluate_mastery(
                student["student_id"],
                standard_code,
                student["score"],
                threshold
            )
            diff = self.evaluate_differentiation(
                student["student_id"],
                student["score"]
            )

            results.append({
                "student_id": student["student_id"],
                "score": student["score"],
                "mastery": mastery,
                "tier": diff["tier"]
            })

            tiers[diff["tier"]].append(student["student_id"])

        # Calculate class statistics
        scores = [s["score"] for s in students]
        n = len(scores)
        avg = sum(scores) / n if n > 0 else 0
        sorted_scores = sorted(scores)
        median = sorted_scores[n // 2] if n % 2 == 1 else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2

        mastery_count = sum(1 for s in students if s["score"] >= threshold)
        mastery_rate = (mastery_count / n * 100) if n > 0 else 0

        return {
            "standard_code": standard_code,
            "threshold": threshold,
            "statistics": {
                "count": n,
                "average": round(avg, 1),
                "median": round(median, 1),
                "mastery_count": mastery_count,
                "mastery_rate": round(mastery_rate, 1)
            },
            "tiers": {
                "tier3_intensive": tiers["tier3"],
                "tier2_strategic": tiers["tier2"],
                "tier1_core": tiers["tier1"],
                "enrichment": tiers["enrichment"]
            },
            "tier_counts": {
                "tier3": len(tiers["tier3"]),
                "tier2": len(tiers["tier2"]),
                "tier1": len(tiers["tier1"]),
                "enrichment": len(tiers["enrichment"])
            },
            "results": results,
            "timestamp": int(time.time() * 1000)
        }

    @property
    def evaluation_count(self) -> int:
        return self._evaluation_count


# ===============================================================================
# CONVENIENCE FUNCTIONS
# ===============================================================================

def verify_mastery(
    student_id: str,
    standard_code: str,
    score: float,
    threshold: float = 80.0
) -> Dict[str, Any]:
    """
    One-liner mastery verification.

    >>> verify_mastery("S001", "5.3A", 85)
    {'mastered': True, 'ratio': 1.0625, ...}
    """
    evaluator = EducationCDLEvaluator()
    return evaluator.evaluate_mastery(student_id, standard_code, score, threshold)


def verify_zpd(
    student_id: str,
    current_ability: float,
    task_difficulty: float
) -> Dict[str, Any]:
    """
    One-liner ZPD verification.

    >>> verify_zpd("S001", 70, 90)
    {'in_zpd': True, 'ratio': 1.286, 'zone': 'zpd', ...}
    """
    evaluator = EducationCDLEvaluator()
    return evaluator.evaluate_zpd(student_id, current_ability, task_difficulty)


def verify_progression(
    student_id: str,
    target_checkpoint: str,
    prerequisite_mastery: Dict[str, float],
    target_difficulty: float = 1.0
) -> Dict[str, Any]:
    """
    One-liner progression verification.

    >>> verify_progression("S001", "FRAC-05", {"FRAC-04": 85}, 2.5)
    {'ready': True, 'ratio': 0.588, ...}
    """
    evaluator = EducationCDLEvaluator()
    return evaluator.evaluate_progression(
        student_id, target_checkpoint, prerequisite_mastery, target_difficulty
    )


def get_differentiation_tier(student_id: str, score: float) -> Dict[str, Any]:
    """
    Get differentiation tier for a student.

    >>> get_differentiation_tier("S001", 75)
    {'tier': 'tier2', 'color': 'yellow', 'instruction': '...'}
    """
    evaluator = EducationCDLEvaluator()
    return evaluator.evaluate_differentiation(student_id, score)


# ===============================================================================
# MODULE EXPORTS
# ===============================================================================

__all__ = [
    # Enums
    'EducationDomain',

    # Constraint Classes
    'MasteryConstraint',
    'ZPDConstraint',
    'ProgressionConstraint',
    'AssessmentIntegrityConstraint',
    'DifferentiationConstraint',

    # Evaluator
    'EducationCDLEvaluator',

    # Convenience Functions
    'verify_mastery',
    'verify_zpd',
    'verify_progression',
    'get_differentiation_tier',
]
