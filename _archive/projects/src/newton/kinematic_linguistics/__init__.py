"""
KINEMATIC LINGUISTICS v1.1
A Geometric Substrate for Semantic Reliability

PARCRI Real Intelligence - January 2026

Core Axiom: Language is a conserved geometric system.

This module treats natural language not as data but as geometry. By defining
words as assemblies of mechanical constraints (Glyphs) and concepts as vectors
in state space, we construct a semantic compiler that enforces physical
admissibility before execution.

Components:
    - GlyphRegistry: Complete A-Z kinematic mapping
    - PhonosemanticsRegistry: Letter cluster patterns (ST, FL, GL, SP)
    - WordAssemblyAnalyzer: Mechanical word decomposition
    - KinematicCompiler: Semantic constraint verification
    - DistortionIndexCalculator: Reality/language mismatch detection
    - AntonymAnalyzer: Geometric vs dictionary antonyms
    - HallucinationDetector: Unstable assembly detection

Usage:
    >>> from newton.kinematic_linguistics import WordAssemblyAnalyzer
    >>> assembly = WordAssemblyAnalyzer.analyze("TRUST")
    >>> print(assembly.mechanical_prediction)
    'Suspension bridge - anchored at both ends, braced, holds weight'

    >>> from newton.kinematic_linguistics import KinematicCompiler, CompilerRegime
    >>> compiler = KinematicCompiler(CompilerRegime.SAFETY_CRITICAL)
    >>> proof = compiler.compile("Execute trim adjustment")
    >>> print(proof.is_admissible)
    True

Philosophy:
    We must move from probabilistic AI (predicting the next token) to
    geometric AI (verifying the structural integrity of thought).
"""

__version__ = "1.1.0"

# Matter Types (Glyph Definitions)
from .matter import (
    GlyphMechanics,
    GlyphRole,
    GlyphRegistry,
    PhonosemanticsCluster,
    PhonosemanticsRegistry,
    StabilityClass,
    LetterPosition,
    WordAssemblyRole,
    WORD_GEOMETRY_EXAMPLES,
)

# Core Engines
from .core import (
    # Word Assembly
    WordVector,
    WordAssembly,
    WordAssemblyAnalyzer,
    # Distortion Analysis
    DistortionReport,
    DistortionIndexCalculator,
    # Antonym Analysis
    AntonymType,
    AntonymAnalysis,
    AntonymAnalyzer,
    # Compiler
    CompilerRegime,
    CompilationProof,
    StructuralFailure,
    KinematicCompiler,
    # Hallucination Detection
    HallucinationCheck,
    HallucinationDetector,
)

__all__ = [
    # Version
    "__version__",
    # Matter Types
    "GlyphMechanics",
    "GlyphRole",
    "GlyphRegistry",
    "PhonosemanticsCluster",
    "PhonosemanticsRegistry",
    "StabilityClass",
    "LetterPosition",
    "WordAssemblyRole",
    "WORD_GEOMETRY_EXAMPLES",
    # Word Assembly
    "WordVector",
    "WordAssembly",
    "WordAssemblyAnalyzer",
    # Distortion Analysis
    "DistortionReport",
    "DistortionIndexCalculator",
    # Antonym Analysis
    "AntonymType",
    "AntonymAnalysis",
    "AntonymAnalyzer",
    # Compiler
    "CompilerRegime",
    "CompilationProof",
    "StructuralFailure",
    "KinematicCompiler",
    # Hallucination Detection
    "HallucinationCheck",
    "HallucinationDetector",
]
