"""
═══════════════════════════════════════════════════════════════════════════════
 Newton SDK - Verified Computation Engine
═══════════════════════════════════════════════════════════════════════════════

Installation:
    pip install newton-sdk          # Client only
    pip install newton-sdk[server]  # With server
    pip install newton-sdk[all]     # Everything

Usage:
    from newton_sdk import Newton, Blueprint, field, law, forge, when, finfr

    # Connect to Newton server
    newton = Newton("http://localhost:8000")
    result = newton.calculate({"op": "+", "args": [2, 3]})

    # Or use tinyTalk locally
    class MyBlueprint(Blueprint):
        value = field(float, default=0.0)

        @law
        def must_be_positive(self):
            when(self.value < 0, finfr)

        @forge
        def set_value(self, v):
            self.value = v
"""

__version__ = "1.0.0"

# Import tinyTalk components
import os as _os
import sys as _sys

# Add tinytalk_py to path
_sdk_dir = _os.path.dirname(_os.path.abspath(__file__))
_root_dir = _os.path.dirname(_sdk_dir)
_tinytalk_dir = _os.path.join(_root_dir, "tinytalk_py")

if _tinytalk_dir not in _sys.path:
    _sys.path.insert(0, _tinytalk_dir)

# Import from tinytalk
try:
    from tinytalk_py import (
        # Core
        Blueprint,
        Law,
        LawResult,
        field,
        forge,
        law,
        when,
        fin,
        finfr,
        FINFR,
        FIN,
        LawViolation,
        FinClosure,
        # Matter types
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
        # Engine
        KineticEngine,
        Presence,
        Delta,
    )
except ImportError:
    # Fallback for when tinytalk_py isn't available
    pass

# Import Newton client
from .client import Newton, NewtonError

# Import server launcher
from .server import serve

__all__ = [
    # SDK
    "__version__",
    "Newton",
    "NewtonError",
    "serve",
    # tinyTalk Core
    "Blueprint",
    "Law",
    "LawResult",
    "field",
    "forge",
    "law",
    "when",
    "fin",
    "finfr",
    "FINFR",
    "FIN",
    "LawViolation",
    "FinClosure",
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
]
