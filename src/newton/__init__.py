"""
═══════════════════════════════════════════════════════════════════════════════
 newton - The Newton Supercomputer Python Package
═══════════════════════════════════════════════════════════════════════════════

Verified computation with the TinyTalk constraint language.
Built on the "No-First" philosophy: define what cannot happen.

Installation:
    pip install newton-computer          # Client only
    pip install newton-computer[server]  # With server
    pip install newton-computer[all]     # Everything

Quick Start:
    from newton import Blueprint, field, law, forge, when, finfr

    class BankAccount(Blueprint):
        balance = field(float, default=100.0)

        @law
        def no_overdraft(self):
            when(self.balance < 0, finfr)

        @forge
        def withdraw(self, amount):
            self.balance -= amount

    account = BankAccount()
    account.withdraw(50)   # Works: balance = 50
    account.withdraw(60)   # BLOCKED! Would violate no_overdraft law

Philosophy:
    Traditional: Try everything, catch errors afterward
    Newton: Define what cannot happen, execute safely

Documentation: https://github.com/jaredlewiswechs/Newton-api
"""

__version__ = "1.0.0"

# ═══════════════════════════════════════════════════════════════════════════════
# TinyTalk Core - The constraint language
# ═══════════════════════════════════════════════════════════════════════════════
from .tinytalk import (
    # Core primitives
    Blueprint,
    Law,
    LawResult,
    LawViolation,
    FinClosure,
    field,
    forge,
    law,
    when,
    fin,
    finfr,
    FINFR,
    FIN,
    # f/g Ratio Constraint System
    RatioResult,
    ratio,
    finfr_if_undefined,
    # Matter types (type-safe units)
    Matter,
    Money,
    Mass,
    Distance,
    Temperature,
    Pressure,
    Volume,
    FlowRate,
    Velocity,
    Time,
    Celsius,
    Fahrenheit,
    PSI,
    Meters,
    Kilograms,
    Liters,
    # Kinetic Engine (state transitions)
    KineticEngine,
    Presence,
    Delta,
    motion,
)

# ═══════════════════════════════════════════════════════════════════════════════
# LLM Constraint Governor - Domain-agnostic validation
# ═══════════════════════════════════════════════════════════════════════════════
from .llm import (
    # Schema
    Domain as LLMDomain,
    Claim,
    ClaimBatch,
    ValidationResult as LLMValidationResult,
    BatchValidationResult,
    # Validators
    DomainValidator,
    PhysicsValidator,
    MathValidator,
    LogicValidator,
    PolicyValidator,
    TemporalValidator,
    FinancialValidator,
    # Engine
    ValidatorRegistry,
    ConstraintEngine,
    GenerationResult,
    create_engine,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Client - Connect to Newton server
# ═══════════════════════════════════════════════════════════════════════════════
from .client import Newton, NewtonError

# ═══════════════════════════════════════════════════════════════════════════════
# Server launcher (optional dependency)
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from .server import serve
except ImportError:
    serve = None  # Server dependencies not installed

__all__ = [
    # Version
    "__version__",
    # Client
    "Newton",
    "NewtonError",
    "serve",
    # TinyTalk Core
    "Blueprint",
    "Law",
    "LawResult",
    "LawViolation",
    "FinClosure",
    "field",
    "forge",
    "law",
    "when",
    "fin",
    "finfr",
    "FINFR",
    "FIN",
    # Ratio System
    "RatioResult",
    "ratio",
    "finfr_if_undefined",
    # Matter types
    "Matter",
    "Money",
    "Mass",
    "Distance",
    "Temperature",
    "Pressure",
    "Volume",
    "FlowRate",
    "Velocity",
    "Time",
    "Celsius",
    "Fahrenheit",
    "PSI",
    "Meters",
    "Kilograms",
    "Liters",
    # Engine
    "KineticEngine",
    "Presence",
    "Delta",
    "motion",
    # LLM Constraint Governor
    "LLMDomain",
    "Claim",
    "ClaimBatch",
    "LLMValidationResult",
    "BatchValidationResult",
    "DomainValidator",
    "PhysicsValidator",
    "MathValidator",
    "LogicValidator",
    "PolicyValidator",
    "TemporalValidator",
    "FinancialValidator",
    "ValidatorRegistry",
    "ConstraintEngine",
    "GenerationResult",
    "create_engine",
]
