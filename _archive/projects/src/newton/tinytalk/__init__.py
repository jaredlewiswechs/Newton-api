"""
TinyTalk - The constraint-first programming language.

Built on the "No-First" philosophy: define what cannot happen, then execute safely.
"""

from .core import (
    # Core primitives
    Blueprint,
    Law,
    LawResult,
    LawViolation,
    FinClosure,
    Field,
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
)

from .matter import (
    # Base class
    Matter,
    # Financial
    Money,
    # Physical
    Mass,
    Distance,
    Volume,
    Pressure,
    FlowRate,
    Velocity,
    Time,
    # Temperature
    Temperature,
    Celsius,
    Fahrenheit,
    # Convenience constructors
    PSI,
    Meters,
    Kilograms,
    Liters,
)

from .engine import (
    KineticEngine,
    Presence,
    Delta,
    motion,
)

from .compositor import (
    # Primitives
    Rect,
    Color,
    BLACK,
    WHITE,
    TRANSPARENT,
    # Visual Elements
    VisualElement,
    # Constraints
    VisualConstraint,
    ConstraintPriority,
    ConstraintStatus,
    ConstraintResult,
    NoOverlap,
    NoOverlapGroup,
    MinContrast,
    FullyVisible,
    RelativePosition,
    EvenSpacing,
    MinSize,
    AspectRatio,
    # Solver
    ConstraintSolver,
    SolverResult,
    # Frame & Proof
    Frame,
    ConstraintProof,
    # Compositor
    CompositorBlueprint,
    KineticCompositor,
    # Utilities
    create_compositor,
    verify_frame,
    frame_to_presence,
)

__all__ = [
    # Core
    "Blueprint",
    "Law",
    "LawResult",
    "LawViolation",
    "FinClosure",
    "Field",
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
    "Volume",
    "Pressure",
    "FlowRate",
    "Velocity",
    "Time",
    "Temperature",
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
    # Compositor
    "Rect",
    "Color",
    "BLACK",
    "WHITE",
    "TRANSPARENT",
    "VisualElement",
    "VisualConstraint",
    "ConstraintPriority",
    "ConstraintStatus",
    "ConstraintResult",
    "NoOverlap",
    "NoOverlapGroup",
    "MinContrast",
    "FullyVisible",
    "RelativePosition",
    "EvenSpacing",
    "MinSize",
    "AspectRatio",
    "ConstraintSolver",
    "SolverResult",
    "Frame",
    "ConstraintProof",
    "CompositorBlueprint",
    "KineticCompositor",
    "create_compositor",
    "verify_frame",
    "frame_to_presence",
]
