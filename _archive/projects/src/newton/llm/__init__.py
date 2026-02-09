"""
NEWTON LLM CONSTRAINT GOVERNOR
═══════════════════════════════════════════════════════════════════════════════

Domain-Agnostic LLM Constraint Validation System

"LLM proposes → Validator decides → LLM repairs → repeat"

This module provides a universal constraint governance layer for LLM outputs.
The key insight: meaning lives in validators, not tokens.

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │                      ConstraintEngine                           │
    │  ┌─────────────┐    ┌──────────────────┐    ┌──────────────┐   │
    │  │   LLM       │───►│ ValidatorRegistry │───►│ Validators   │   │
    │  │  (proposes) │◄───│   (routes)        │◄───│ (decide)     │   │
    │  └─────────────┘    └──────────────────┘    └──────────────┘   │
    │         │                                          │            │
    │         │                                          │            │
    │         ▼                                          │            │
    │  ┌─────────────┐                                   │            │
    │  │   Repair    │◄──────────────────────────────────┘            │
    │  │   Prompt    │                                                │
    │  └─────────────┘                                                │
    └─────────────────────────────────────────────────────────────────┘

Components:
    - Claim: Universal schema for LLM outputs
    - ValidationResult: Verdict from domain validators
    - DomainValidator: Abstract interface for validators
    - ValidatorRegistry: Routes claims to validators
    - ConstraintEngine: The closed-loop generation engine

Validators:
    - PhysicsValidator: Kinematic/physical constraints
    - MathValidator: Symbolic equality (SymPy-powered)
    - LogicValidator: Propositional consistency
    - PolicyValidator: Rule table enforcement
    - TemporalValidator: Time ordering
    - FinancialValidator: Budget constraints

Quick Start:
    ```python
    from newton.llm import (
        Claim, Domain, ValidationResult,
        MathValidator, LogicValidator,
        ValidatorRegistry, ConstraintEngine,
        create_engine,
    )

    # Create validator registry
    registry = ValidatorRegistry([
        MathValidator(),
        LogicValidator(),
    ])

    # Validate a claim directly
    claim = Claim(text="2 + 2 = 4", domain=Domain.MATH)
    result = registry.validate(claim)
    print(result.valid)  # True

    # Or use the full engine with an LLM
    engine = create_engine(llm=my_llm_client)
    result = engine.generate("What is 2 + 2?")
    print(result.claims)  # ["2 + 2 = 4"]
    ```

Integration with Newton Core:
    ```python
    from newton.cinema.core import KineticForge
    from newton.llm import PhysicsValidator, ValidatorRegistry

    # Wire existing kinematic engine
    forge = KineticForge()
    physics = PhysicsValidator(kinematic_validator=forge)

    registry = ValidatorRegistry([physics])
    ```

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA - Core types
# ═══════════════════════════════════════════════════════════════════════════════
from .schema import (
    Domain,
    DomainLiteral,
    Claim,
    ClaimBatch,
    ValidationResult,
    BatchValidationResult,
    LLM_SYSTEM_PROMPT,
)

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATORS - Domain-specific validators
# ═══════════════════════════════════════════════════════════════════════════════
from .validators import (
    DomainValidator,
    PhysicsValidator,
    MathValidator,
    LogicValidator,
    PolicyValidator,
    TemporalValidator,
    FinancialValidator,
    CompositeValidator,
)

# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE - The constraint loop
# ═══════════════════════════════════════════════════════════════════════════════
from .engine import (
    ValidatorRegistry,
    ConstraintEngine,
    GenerationResult,
    LLMClient,
    MockLLM,
    build_repair_prompt,
    create_default_registry,
    create_engine,
)

# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION - Newton system adapters
# ═══════════════════════════════════════════════════════════════════════════════
from .integration import (
    KineticForgeAdapter,
    ExtractorValidator,
    CDLValidator,
    create_physics_validator_with_forge,
    create_integrated_registry,
    create_integrated_engine,
)

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Version
    "__version__",
    # Schema
    "Domain",
    "DomainLiteral",
    "Claim",
    "ClaimBatch",
    "ValidationResult",
    "BatchValidationResult",
    "LLM_SYSTEM_PROMPT",
    # Validators
    "DomainValidator",
    "PhysicsValidator",
    "MathValidator",
    "LogicValidator",
    "PolicyValidator",
    "TemporalValidator",
    "FinancialValidator",
    "CompositeValidator",
    # Engine
    "ValidatorRegistry",
    "ConstraintEngine",
    "GenerationResult",
    "LLMClient",
    "MockLLM",
    "build_repair_prompt",
    "create_default_registry",
    "create_engine",
    # Integration
    "KineticForgeAdapter",
    "ExtractorValidator",
    "CDLValidator",
    "create_physics_validator_with_forge",
    "create_integrated_registry",
    "create_integrated_engine",
]
