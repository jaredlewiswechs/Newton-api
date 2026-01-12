"""
═══════════════════════════════════════════════════════════════════════════════
 newton - The Newton Supercomputer Python Package
═══════════════════════════════════════════════════════════════════════════════

Verified computation with the TinyTalk constraint language.
Built on the "No-First" philosophy: define what cannot happen.

NEW: Ada - The Better ChatGPT
-----------------------------
Ada is a comprehensive AI assistant built on Newton's constraint verification.
Everything ChatGPT does, Ada does BETTER - with verified outputs.

Quick Start with Ada:
    from newton.ada import Ada

    ada = Ada()
    response = ada.chat("What is 2 + 2?")
    print(response.content)  # "2 + 2 = 4" (verified!)

    # Deep research
    report = ada.research("Latest advances in quantum computing")

    # Agent mode
    result = ada.agent("Find all Python files and count lines")

    # Canvas for code/docs
    doc = ada.canvas("Create a fibonacci function in Python")

Installation:
    pip install newton-computer          # Client only
    pip install newton-computer[server]  # With server
    pip install newton-computer[all]     # Everything

TinyTalk Quick Start:
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
# Kinematic Linguistics - Geometric Semantic Verification
# ═══════════════════════════════════════════════════════════════════════════════
from .kinematic_linguistics import (
    # Core Axiom: Language is a conserved geometric system
    GlyphMechanics,
    GlyphRegistry,
    PhonosemanticsCluster,
    PhonosemanticsRegistry,
    WordVector,
    WordAssembly,
    WordAssemblyAnalyzer,
    DistortionReport,
    DistortionIndexCalculator,
    AntonymType,
    AntonymAnalyzer,
    CompilerRegime,
    CompilationProof,
    KinematicCompiler,
    HallucinationDetector,
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

# ═══════════════════════════════════════════════════════════════════════════════
# Ada - The Better ChatGPT
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from .ada import (
        Ada,
        AdaConfig,
        AdaMode,
        AdaResponse,
        DeepResearch,
        MemoryStore,
        AdaAgent,
        Canvas,
        CodeSandbox,
        TaskScheduler,
        ConnectorRegistry,
        create_ada_app,
        ada_cli,
    )
    HAS_ADA = True
except ImportError:
    HAS_ADA = False
    Ada = None

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
    # Kinematic Linguistics
    "GlyphMechanics",
    "GlyphRegistry",
    "PhonosemanticsCluster",
    "PhonosemanticsRegistry",
    "WordVector",
    "WordAssembly",
    "WordAssemblyAnalyzer",
    "DistortionReport",
    "DistortionIndexCalculator",
    "AntonymType",
    "AntonymAnalyzer",
    "CompilerRegime",
    "CompilationProof",
    "KinematicCompiler",
    "HallucinationDetector",
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
    # Ada - The Better ChatGPT
    "Ada",
    "AdaConfig",
    "AdaMode",
    "AdaResponse",
    "DeepResearch",
    "MemoryStore",
    "AdaAgent",
    "Canvas",
    "CodeSandbox",
    "TaskScheduler",
    "ConnectorRegistry",
    "create_ada_app",
    "ada_cli",
    "HAS_ADA",
]
