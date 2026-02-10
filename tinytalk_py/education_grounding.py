"""
===============================================================================
 EDUCATION GROUNDING - Pattern Validation with Newton Grounding
===============================================================================

Uses Newton's grounding engine to validate educational patterns:
- Standard alignment verification
- Pedagogical pattern validation
- Research-backed practice verification
- Curriculum coherence checking

"Ground the pattern. Verify the practice. The constraint IS the pedagogy."

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
import re

# Import grounding engine
from core.grounding import GroundingEngine, TRUSTED_DOMAINS


# ===============================================================================
# EDUCATION-SPECIFIC TRUSTED SOURCES
# ===============================================================================

EDUCATION_TRUSTED_DOMAINS = [
    # Official standards bodies
    "tea.texas.gov",                    # Texas Education Agency
    "corestandards.org",                # Common Core State Standards
    "ed.gov",                           # US Department of Education
    "achieve.org",                      # Achieve (standards organization)

    # Research organizations
    "ies.ed.gov",                       # Institute of Education Sciences
    "nctm.org",                         # National Council of Teachers of Math
    "ncte.org",                         # National Council of Teachers of English
    "nsta.org",                         # National Science Teaching Association
    "reading.org",                      # International Literacy Association

    # Educational research
    "educationnext.org",                # Education Next
    "edweek.org",                       # Education Week
    "ascd.org",                         # ASCD (curriculum & supervision)

    # Universities with education programs
    "hgse.harvard.edu",                 # Harvard Graduate School of Education
    "tc.columbia.edu",                  # Teachers College, Columbia
    "stanford.edu/group/cset",          # Stanford Center for Education

    # Evidence-based practice
    "whatworks.ed.gov",                 # What Works Clearinghouse
    "bestevidence.org",                 # Best Evidence Encyclopedia
    "researchgate.net",                 # Research papers
    "jstor.org",                        # Academic journals
]


# ===============================================================================
# PEDAGOGICAL PATTERNS
# ===============================================================================

class PedagogicalPattern(Enum):
    """Research-backed pedagogical patterns."""
    GRADUAL_RELEASE = "gradual_release"       # I do, We do, You do
    EXPLICIT_INSTRUCTION = "explicit"          # Direct instruction
    INQUIRY_BASED = "inquiry"                  # Student-driven inquiry
    COOPERATIVE_LEARNING = "cooperative"       # Group work structures
    DIFFERENTIATED = "differentiated"          # Tiered instruction
    SCAFFOLDED = "scaffolded"                 # Support structures
    FORMATIVE_ASSESSMENT = "formative"         # Ongoing assessment
    MASTERY_LEARNING = "mastery"               # Mastery-based progression
    ZPD_ALIGNED = "zpd"                       # Zone of Proximal Development
    BACKWARD_DESIGN = "backward"               # Understanding by Design


@dataclass
class GroundedPattern:
    """A pedagogical pattern grounded in research."""
    pattern: PedagogicalPattern
    description: str
    research_basis: str
    effectiveness_rating: str  # high, moderate, emerging
    sources: List[str]
    key_practices: List[str]
    common_pitfalls: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern.value,
            "description": self.description,
            "research_basis": self.research_basis,
            "effectiveness": self.effectiveness_rating,
            "sources": self.sources,
            "key_practices": self.key_practices,
            "common_pitfalls": self.common_pitfalls
        }


# Pre-defined grounded patterns (from educational research)
GROUNDED_PATTERNS = {
    PedagogicalPattern.GRADUAL_RELEASE: GroundedPattern(
        pattern=PedagogicalPattern.GRADUAL_RELEASE,
        description="Gradual Release of Responsibility (I Do, We Do, You Do)",
        research_basis="Fisher & Frey (2008); Pearson & Gallagher (1983)",
        effectiveness_rating="high",
        sources=[
            "Fisher, D., & Frey, N. (2008). Better Learning Through Structured Teaching",
            "Pearson, P.D., & Gallagher, M.C. (1983). The instruction of reading comprehension"
        ],
        key_practices=[
            "Clear modeling with think-aloud",
            "Guided practice with immediate feedback",
            "Gradual reduction of scaffolding",
            "Student metacognition development"
        ],
        common_pitfalls=[
            "Skipping the 'We Do' phase",
            "Not enough modeling before practice",
            "Moving too quickly to independent practice"
        ]
    ),

    PedagogicalPattern.EXPLICIT_INSTRUCTION: GroundedPattern(
        pattern=PedagogicalPattern.EXPLICIT_INSTRUCTION,
        description="Explicit Instruction with systematic teaching of skills",
        research_basis="Archer & Hughes (2011); Rosenshine (2012)",
        effectiveness_rating="high",
        sources=[
            "Archer, A.L., & Hughes, C.A. (2011). Explicit Instruction: Effective and Efficient Teaching",
            "Rosenshine, B. (2012). Principles of Instruction"
        ],
        key_practices=[
            "Clear learning objectives stated upfront",
            "Step-by-step demonstration",
            "Frequent checks for understanding",
            "High success rate during practice"
        ],
        common_pitfalls=[
            "Assuming prior knowledge",
            "Too much information at once",
            "Insufficient practice opportunities"
        ]
    ),

    PedagogicalPattern.MASTERY_LEARNING: GroundedPattern(
        pattern=PedagogicalPattern.MASTERY_LEARNING,
        description="Mastery-based learning with prerequisite validation",
        research_basis="Bloom (1968); Guskey (2007); Kulik et al. (1990)",
        effectiveness_rating="high",
        sources=[
            "Bloom, B.S. (1968). Learning for mastery",
            "Guskey, T.R. (2007). Closing achievement gaps",
            "Kulik, C.L.C., Kulik, J.A., & Bangert-Drowns, R.L. (1990). Effectiveness of mastery learning"
        ],
        key_practices=[
            "Clear mastery criteria (80%+ threshold)",
            "Formative assessment at each checkpoint",
            "Corrective instruction for non-mastery",
            "Enrichment for those who achieve mastery"
        ],
        common_pitfalls=[
            "Setting threshold too low (<70%)",
            "Moving on before mastery achieved",
            "Not providing adequate reteach time"
        ]
    ),

    PedagogicalPattern.ZPD_ALIGNED: GroundedPattern(
        pattern=PedagogicalPattern.ZPD_ALIGNED,
        description="Zone of Proximal Development aligned instruction",
        research_basis="Vygotsky (1978); Wood, Bruner, & Ross (1976)",
        effectiveness_rating="high",
        sources=[
            "Vygotsky, L.S. (1978). Mind in Society",
            "Wood, D., Bruner, J.S., & Ross, G. (1976). The role of tutoring in problem solving"
        ],
        key_practices=[
            "Assess current independent level",
            "Identify zone between current and potential",
            "Provide scaffolding within ZPD",
            "Gradually remove supports as competence grows"
        ],
        common_pitfalls=[
            "Teaching too far above current level (frustration)",
            "Teaching at current level (no growth)",
            "Removing scaffolds too quickly"
        ]
    ),

    PedagogicalPattern.FORMATIVE_ASSESSMENT: GroundedPattern(
        pattern=PedagogicalPattern.FORMATIVE_ASSESSMENT,
        description="Ongoing formative assessment with feedback loops",
        research_basis="Black & Wiliam (1998); Hattie & Timperley (2007)",
        effectiveness_rating="high",
        sources=[
            "Black, P., & Wiliam, D. (1998). Inside the Black Box",
            "Hattie, J., & Timperley, H. (2007). The power of feedback"
        ],
        key_practices=[
            "Frequent low-stakes checks",
            "Immediate feedback to students",
            "Data-driven instructional adjustments",
            "Student self-assessment skills"
        ],
        common_pitfalls=[
            "Over-reliance on summative assessment",
            "Feedback that's too delayed",
            "Not using data to adjust instruction"
        ]
    ),

    PedagogicalPattern.DIFFERENTIATED: GroundedPattern(
        pattern=PedagogicalPattern.DIFFERENTIATED,
        description="Differentiated instruction for diverse learners",
        research_basis="Tomlinson (2001); Hall (2002)",
        effectiveness_rating="moderate",
        sources=[
            "Tomlinson, C.A. (2001). How to Differentiate Instruction in Mixed-Ability Classrooms",
            "Hall, T. (2002). Differentiated instruction. CAST"
        ],
        key_practices=[
            "Pre-assessment to determine readiness",
            "Flexible grouping strategies",
            "Multiple pathways to same learning goal",
            "Choice in process and product"
        ],
        common_pitfalls=[
            "Tracking students into fixed groups",
            "Only differentiating quantity, not complexity",
            "Overwhelming management complexity"
        ]
    ),

    PedagogicalPattern.BACKWARD_DESIGN: GroundedPattern(
        pattern=PedagogicalPattern.BACKWARD_DESIGN,
        description="Understanding by Design (Backward Design)",
        research_basis="Wiggins & McTighe (2005)",
        effectiveness_rating="high",
        sources=[
            "Wiggins, G., & McTighe, J. (2005). Understanding by Design"
        ],
        key_practices=[
            "Start with desired learning outcomes",
            "Determine acceptable evidence of learning",
            "Plan learning experiences and instruction",
            "Align assessments to standards"
        ],
        common_pitfalls=[
            "Activity-focused rather than outcome-focused",
            "Misalignment between assessment and objective",
            "Covering content without ensuring understanding"
        ]
    ),

    PedagogicalPattern.COOPERATIVE_LEARNING: GroundedPattern(
        pattern=PedagogicalPattern.COOPERATIVE_LEARNING,
        description="Structured cooperative learning strategies",
        research_basis="Johnson & Johnson (1999); Slavin (1995)",
        effectiveness_rating="high",
        sources=[
            "Johnson, D.W., & Johnson, R.T. (1999). Learning Together and Alone",
            "Slavin, R.E. (1995). Cooperative learning: Theory, research, and practice"
        ],
        key_practices=[
            "Positive interdependence",
            "Individual accountability",
            "Face-to-face interaction",
            "Social skills instruction",
            "Group processing"
        ],
        common_pitfalls=[
            "Unstructured group work",
            "No individual accountability",
            "Dominated by one student",
            "Social loafing"
        ]
    ),
}


# ===============================================================================
# EDUCATION GROUNDING ENGINE
# ===============================================================================

class EducationGroundingEngine:
    """
    Newton grounding engine specialized for education.

    Validates:
    - Standard alignment
    - Pedagogical pattern validity
    - Research-backed practices
    - Curriculum coherence
    """

    def __init__(self):
        self.base_engine = GroundingEngine()
        self._verification_count = 0

    def ground_pedagogical_pattern(
        self,
        pattern: PedagogicalPattern,
        implementation_description: str
    ) -> Dict[str, Any]:
        """
        Ground a pedagogical pattern against research.

        Args:
            pattern: The pedagogical pattern being implemented
            implementation_description: How the pattern is being implemented

        Returns:
            Grounding result with validation and recommendations
        """
        self._verification_count += 1

        grounded = GROUNDED_PATTERNS.get(pattern)
        if not grounded:
            return {
                "valid": False,
                "pattern": pattern.value,
                "message": f"Pattern '{pattern.value}' not found in grounded patterns",
                "recommendation": "Use a research-backed pedagogical pattern"
            }

        # Check implementation against key practices
        implementation_lower = implementation_description.lower()
        practices_found = []
        practices_missing = []

        for practice in grounded.key_practices:
            # Simple keyword matching (could be more sophisticated)
            practice_keywords = practice.lower().split()
            if any(kw in implementation_lower for kw in practice_keywords if len(kw) > 4):
                practices_found.append(practice)
            else:
                practices_missing.append(practice)

        alignment_score = len(practices_found) / len(grounded.key_practices) if grounded.key_practices else 0

        # Check for common pitfalls
        pitfalls_detected = []
        for pitfall in grounded.common_pitfalls:
            pitfall_keywords = pitfall.lower().split()
            if any(kw in implementation_lower for kw in pitfall_keywords if len(kw) > 4):
                pitfalls_detected.append(pitfall)

        return {
            "valid": alignment_score >= 0.5,
            "pattern": grounded.to_dict(),
            "implementation": implementation_description,
            "alignment_score": round(alignment_score, 2),
            "practices_found": practices_found,
            "practices_missing": practices_missing,
            "pitfalls_detected": pitfalls_detected,
            "effectiveness": grounded.effectiveness_rating,
            "recommendation": self._generate_recommendation(
                alignment_score, practices_missing, pitfalls_detected
            ),
            "timestamp": int(time.time() * 1000)
        }

    def ground_lesson_plan(self, lesson_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ground a lesson plan against research-backed practices.

        Args:
            lesson_plan: Lesson plan with phases, objectives, activities

        Returns:
            Comprehensive grounding result
        """
        self._verification_count += 1

        results = {
            "lesson_title": lesson_plan.get("title", "Untitled"),
            "patterns_detected": [],
            "alignment_issues": [],
            "recommendations": [],
            "overall_score": 0.0,
            "timestamp": int(time.time() * 1000)
        }

        # Check for Gradual Release pattern
        phases = lesson_plan.get("phases", [])
        phase_types = [p.get("phase", p.get("type", "")) for p in phases]

        if self._detect_gradual_release(phase_types):
            results["patterns_detected"].append({
                "pattern": "gradual_release",
                "confidence": "high",
                "evidence": "I Do/We Do/You Do structure detected"
            })

        # Check for explicit instruction elements
        if self._detect_explicit_instruction(lesson_plan):
            results["patterns_detected"].append({
                "pattern": "explicit_instruction",
                "confidence": "high",
                "evidence": "Clear objectives, modeling, guided practice detected"
            })

        # Check for formative assessment
        if self._detect_formative_assessment(lesson_plan):
            results["patterns_detected"].append({
                "pattern": "formative_assessment",
                "confidence": "high",
                "evidence": "Exit ticket and checks for understanding detected"
            })

        # Check for differentiation
        if self._detect_differentiation(lesson_plan):
            results["patterns_detected"].append({
                "pattern": "differentiation",
                "confidence": "moderate",
                "evidence": "Tiered activities or accommodations detected"
            })

        # Check for alignment issues
        objective = lesson_plan.get("objective", "")
        teks = lesson_plan.get("teks_alignment", lesson_plan.get("teks_codes", []))

        if not objective:
            results["alignment_issues"].append("Missing learning objective")
        if not teks:
            results["alignment_issues"].append("No standards alignment specified")

        # Check for assessment alignment
        assessment = lesson_plan.get("assessment", {})
        exit_ticket = assessment.get("exit_ticket", {})
        if not exit_ticket:
            results["alignment_issues"].append("No exit ticket defined")

        # Calculate overall score
        pattern_score = len(results["patterns_detected"]) * 0.25
        alignment_penalty = len(results["alignment_issues"]) * 0.15
        results["overall_score"] = round(min(1.0, max(0.0, pattern_score - alignment_penalty + 0.5)), 2)

        # Generate recommendations
        if not results["patterns_detected"]:
            results["recommendations"].append("Consider using explicit pedagogical patterns")
        if results["alignment_issues"]:
            results["recommendations"].append(f"Address: {', '.join(results['alignment_issues'])}")
        if results["overall_score"] >= 0.75:
            results["recommendations"].append("Lesson plan shows strong research alignment")

        return results

    def ground_standard(
        self,
        standard_code: str,
        standard_text: str
    ) -> Dict[str, Any]:
        """
        Verify a standard against official sources.

        Uses the base grounding engine to search for verification.
        """
        self._verification_count += 1

        # Build search query
        query = f"{standard_code} {standard_text[:100]}"

        # Use base engine with education domains prioritized
        result = self.base_engine.verify_claim(query)

        # Add education-specific context
        result["standard_code"] = standard_code
        result["standard_text"] = standard_text
        result["domain"] = "education"

        return result

    def validate_learning_progression(
        self,
        from_standard: str,
        to_standard: str,
        prerequisite_description: str
    ) -> Dict[str, Any]:
        """
        Validate that a learning progression makes sense.

        Checks if moving from one standard to another follows
        logical prerequisite relationships.
        """
        self._verification_count += 1

        # Build query for progression validation
        query = f"prerequisite for {to_standard} includes {from_standard}"
        result = self.base_engine.verify_claim(query)

        return {
            "from_standard": from_standard,
            "to_standard": to_standard,
            "prerequisite_description": prerequisite_description,
            "verification_status": result["status"],
            "confidence_score": result["confidence_score"],
            "sources": result.get("sources", []),
            "recommendation": "Valid progression" if result["status"] in ["VERIFIED", "LIKELY"] else "Review prerequisite relationship"
        }

    def _detect_gradual_release(self, phase_types: List[str]) -> bool:
        """Detect Gradual Release of Responsibility pattern."""
        phase_str = " ".join(phase_types).lower()
        indicators = ["instruction", "guided", "independent"]
        found = sum(1 for ind in indicators if ind in phase_str)
        return found >= 2

    def _detect_explicit_instruction(self, lesson_plan: Dict[str, Any]) -> bool:
        """Detect explicit instruction elements."""
        objective = str(lesson_plan.get("objective", "")).lower()
        phases = lesson_plan.get("phases", [])

        has_objective = bool(objective)
        has_modeling = any("model" in str(p).lower() or "demonstrate" in str(p).lower() for p in phases)
        has_practice = any("practice" in str(p).lower() or "guided" in str(p).lower() for p in phases)

        return has_objective and has_modeling and has_practice

    def _detect_formative_assessment(self, lesson_plan: Dict[str, Any]) -> bool:
        """Detect formative assessment elements."""
        assessment = lesson_plan.get("assessment", {})
        phases = lesson_plan.get("phases", [])

        has_exit_ticket = bool(assessment.get("exit_ticket"))
        has_checks = any(
            "check" in str(p).lower() or "formative" in str(p).lower()
            for p in phases
        )

        return has_exit_ticket or has_checks

    def _detect_differentiation(self, lesson_plan: Dict[str, Any]) -> bool:
        """Detect differentiation elements."""
        diff = lesson_plan.get("differentiation", {})
        accommodations = lesson_plan.get("accommodations", {})
        phases = lesson_plan.get("phases", [])

        has_diff_section = bool(diff) or bool(accommodations)
        has_diff_in_phases = any(
            p.get("differentiation") for p in phases if isinstance(p, dict)
        )

        return has_diff_section or has_diff_in_phases

    def _generate_recommendation(
        self,
        alignment_score: float,
        missing_practices: List[str],
        pitfalls: List[str]
    ) -> str:
        """Generate implementation recommendation."""
        if alignment_score >= 0.8:
            return "Strong alignment with research-backed practices. Continue implementation."
        elif alignment_score >= 0.5:
            if missing_practices:
                return f"Good foundation. Consider adding: {missing_practices[0]}"
            return "Adequate alignment. Review implementation fidelity."
        else:
            if pitfalls:
                return f"Warning: {pitfalls[0]}. Review implementation."
            return f"Low alignment. Focus on: {missing_practices[0] if missing_practices else 'research-backed practices'}"

    @property
    def verification_count(self) -> int:
        return self._verification_count


# ===============================================================================
# CONVENIENCE FUNCTIONS
# ===============================================================================

def ground_pattern(
    pattern: PedagogicalPattern,
    implementation: str
) -> Dict[str, Any]:
    """
    One-liner pattern grounding.

    >>> ground_pattern(PedagogicalPattern.GRADUAL_RELEASE, "I model, then we practice together")
    {'valid': True, 'alignment_score': 0.75, ...}
    """
    engine = EducationGroundingEngine()
    return engine.ground_pedagogical_pattern(pattern, implementation)


def ground_lesson(lesson_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    One-liner lesson grounding.

    >>> ground_lesson({"title": "Fractions", "phases": [...], "objective": "..."})
    {'patterns_detected': [...], 'overall_score': 0.85, ...}
    """
    engine = EducationGroundingEngine()
    return engine.ground_lesson_plan(lesson_plan)


def get_grounded_pattern(pattern: PedagogicalPattern) -> Optional[GroundedPattern]:
    """Get a pre-grounded pedagogical pattern."""
    return GROUNDED_PATTERNS.get(pattern)


def list_grounded_patterns() -> List[str]:
    """List all available grounded patterns."""
    return [p.value for p in GROUNDED_PATTERNS.keys()]


# ===============================================================================
# MODULE EXPORTS
# ===============================================================================

__all__ = [
    # Enums
    'PedagogicalPattern',

    # Data Classes
    'GroundedPattern',

    # Pre-defined patterns
    'GROUNDED_PATTERNS',

    # Engine
    'EducationGroundingEngine',

    # Convenience Functions
    'ground_pattern',
    'ground_lesson',
    'get_grounded_pattern',
    'list_grounded_patterns',
]
