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
]
