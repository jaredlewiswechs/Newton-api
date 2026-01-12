"""
NEWTON LLM INTEGRATION - Wire to Existing Newton Systems
═══════════════════════════════════════════════════════════════════════════════

Integration layer connecting the LLM constraint governor to existing Newton
components:
- KineticForge (cinema/kinematic validation)
- ConstraintExtractor (NL→Formal conversion)
- CDL 3.0 (Constraint Definition Language)

This module provides factory functions and adapters for seamless integration.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional
import re

from .schema import Claim, Domain, ValidationResult
from .validators import DomainValidator, PhysicsValidator
from .engine import ValidatorRegistry, ConstraintEngine


# ═══════════════════════════════════════════════════════════════════════════════
# KINETIC FORGE ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

class KineticForgeAdapter:
    """
    Adapter to make KineticForge compatible with the LLM constraint system.

    Translates between KineticForge's verify() interface and the
    DomainValidator's validate() interface.
    """

    def __init__(self, kinetic_forge: Any):
        """
        Initialize adapter with a KineticForge instance.

        Args:
            kinetic_forge: Instance of newton.cinema.core.KineticForge
        """
        self.forge = kinetic_forge

    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Validate text through the kinetic forge.

        This is the interface that PhysicsValidator expects.

        Args:
            text: The physics claim text

        Returns:
            Dict with "overall_status" and "violations" keys
        """
        # Import here to avoid circular imports
        try:
            from ..cinema.core import SceneType

            # Default scene type for physics validation
            scene_type = SceneType.QUIET

            # Default user state
            user_state = {
                "silence_streak": 0,
                "mood_modifier": 1.0,
            }

            # Extract priority from text or use default
            priority = 0.5

            # Run verification
            proof = self.forge.verify(
                intent=text,
                priority=priority,
                scene_type=scene_type,
                user_state=user_state,
            )

            # Convert to expected format
            if proof.can_speak:
                return {
                    "overall_status": "verified",
                    "proof": {
                        "f": proof.f,
                        "g": proof.g,
                        "ratio": proof.ratio,
                        "hash": proof.proof_hash,
                    },
                }
            else:
                return {
                    "overall_status": "forbidden",
                    "violations": [{
                        "message": f"Kinematic constraint violated: f/g ratio {proof.ratio:.2f} exceeds threshold",
                        "rule": "kinematic_boundary",
                        "f": proof.f,
                        "g": proof.g,
                        "ratio": proof.ratio,
                    }],
                }

        except Exception as e:
            return {
                "overall_status": "error",
                "violations": [{
                    "message": f"Kinetic validation error: {str(e)}",
                    "rule": "validation_error",
                }],
            }


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT EXTRACTOR INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

class ExtractorValidator(DomainValidator):
    """
    Validator that uses Newton's ConstraintExtractor for NL validation.

    Extracts constraints from natural language and validates them against
    CDL specifications.
    """

    domain = Domain.UNKNOWN  # Multi-domain validator

    def __init__(self, extractor: Optional[Any] = None):
        """
        Initialize with optional ConstraintExtractor instance.

        Args:
            extractor: Optional ConstraintExtractor instance
        """
        self._extractor = extractor

    @property
    def extractor(self):
        """Lazy-load extractor."""
        if self._extractor is None:
            try:
                from ...core.constraint_extractor import ConstraintExtractor
                self._extractor = ConstraintExtractor()
            except ImportError:
                raise ImportError("Newton core constraint_extractor not available")
        return self._extractor

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a claim by extracting and checking constraints.

        This validator extracts constraints from natural language and
        verifies they are well-formed and internally consistent.
        """
        try:
            result = self.extractor.extract(claim.text)

            # Check if extraction was complete
            if not result.all_extractable:
                return ValidationResult(
                    valid=False,
                    domain=Domain.UNKNOWN,
                    rule="extraction_incomplete",
                    message=f"Ambiguities found: {', '.join(result.ambiguities)}",
                    details={
                        "ambiguities": result.ambiguities,
                        "assumptions": result.assumptions,
                    },
                )

            # Check if any constraints were extracted
            if not result.constraints:
                return ValidationResult(
                    valid=True,
                    domain=Domain.UNKNOWN,
                    rule="no_constraints",
                    message="No constraints to validate",
                )

            return ValidationResult(
                valid=True,
                domain=Domain.UNKNOWN,
                rule="extraction_complete",
                message=f"Extracted {len(result.constraints)} constraints",
                details={
                    "constraint_count": len(result.constraints),
                    "merkle_root": result.merkle_root,
                },
            )

        except Exception as e:
            return ValidationResult(
                valid=False,
                domain=Domain.UNKNOWN,
                rule="extraction_error",
                message=f"Extraction failed: {str(e)}",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# CDL VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════════

class CDLValidator(DomainValidator):
    """
    Validator that checks claims against CDL constraint specifications.

    Uses Newton's CDL 3.0 constraint language to evaluate claims.
    """

    domain = Domain.UNKNOWN

    def __init__(self, constraints: Optional[List[Any]] = None):
        """
        Initialize with optional CDL constraints.

        Args:
            constraints: List of CDL constraint objects
        """
        self.constraints = constraints or []

    def add_constraint(self, constraint: Any):
        """Add a CDL constraint."""
        self.constraints.append(constraint)

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a claim against CDL constraints.

        Each constraint is evaluated against the claim text.
        """
        if not self.constraints:
            return ValidationResult(
                valid=True,
                domain=Domain.UNKNOWN,
                rule="no_cdl_constraints",
                message="No CDL constraints configured",
            )

        for constraint in self.constraints:
            try:
                # CDL constraints have an evaluate() method
                if hasattr(constraint, 'evaluate'):
                    # Build context from claim
                    context = {
                        "text": claim.text,
                        "domain": claim.domain.value,
                        **claim.metadata,
                    }

                    if not constraint.evaluate(context):
                        message = getattr(constraint, 'message', 'CDL constraint violated')
                        return ValidationResult(
                            valid=False,
                            domain=Domain.UNKNOWN,
                            rule="cdl_constraint",
                            message=message,
                            details={"constraint": str(constraint)},
                        )

            except Exception as e:
                return ValidationResult(
                    valid=False,
                    domain=Domain.UNKNOWN,
                    rule="cdl_error",
                    message=f"CDL evaluation error: {str(e)}",
                )

        return ValidationResult(
            valid=True,
            domain=Domain.UNKNOWN,
            rule="cdl_pass",
            message="All CDL constraints satisfied",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_physics_validator_with_forge() -> PhysicsValidator:
    """
    Create a PhysicsValidator wired to Newton's KineticForge.

    Returns:
        PhysicsValidator with KineticForge adapter
    """
    try:
        from ..cinema.core import KineticForge
        forge = KineticForge()
        adapter = KineticForgeAdapter(forge)
        return PhysicsValidator(kinematic_validator=adapter)
    except ImportError:
        # Fallback to basic physics validator
        return PhysicsValidator()


def create_integrated_registry() -> ValidatorRegistry:
    """
    Create a ValidatorRegistry with Newton-integrated validators.

    Returns a registry with:
    - PhysicsValidator (with KineticForge if available)
    - MathValidator
    - LogicValidator
    - PolicyValidator
    - TemporalValidator
    - FinancialValidator
    """
    from .validators import (
        MathValidator,
        LogicValidator,
        PolicyValidator,
        TemporalValidator,
        FinancialValidator,
    )

    validators = [
        create_physics_validator_with_forge(),
        MathValidator(),
        LogicValidator(),
        PolicyValidator(),
        TemporalValidator(),
        FinancialValidator(),
    ]

    return ValidatorRegistry(validators)


def create_integrated_engine(
    llm: Optional[Any] = None,
    max_retries: int = 3,
) -> ConstraintEngine:
    """
    Create a ConstraintEngine with full Newton integration.

    Args:
        llm: Optional LLM client
        max_retries: Maximum repair iterations

    Returns:
        Fully integrated ConstraintEngine
    """
    registry = create_integrated_registry()
    return ConstraintEngine(
        registry=registry,
        llm=llm,
        max_retries=max_retries,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "KineticForgeAdapter",
    "ExtractorValidator",
    "CDLValidator",
    "create_physics_validator_with_forge",
    "create_integrated_registry",
    "create_integrated_engine",
]
