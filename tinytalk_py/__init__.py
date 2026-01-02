"""
═══════════════════════════════════════════════════════════════════════════════
 tinytalk_py - tinyTalk for Python
═══════════════════════════════════════════════════════════════════════════════

The "No-First" constraint language. Define what cannot happen.

Usage:
    import sys
    sys.path.insert(0, 'path/to/Newton-api')

    from tinytalk_py import Blueprint, field, law, forge, when, finfr

    class RiskGovernor(Blueprint):
        assets = field(float, default=1000.0)
        liabilities = field(float, default=0.0)

        @law
        def insolvency(self):
            when(self.liabilities > self.assets, finfr)

        @forge
        def execute_trade(self, amount):
            self.liabilities += amount
            return "cleared"

    gov = RiskGovernor()
    gov.execute_trade(500)   # Works: liabilities=500
    gov.execute_trade(600)   # Raises LawViolation
"""

import os as _os
import sys as _sys

# Allow both relative and absolute imports
_dir = _os.path.dirname(_os.path.abspath(__file__))
if _dir not in _sys.path:
    _sys.path.insert(0, _dir)

try:
    # Try relative imports first (when installed as package)
    from .core import (
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
    )

    from .matter import (
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
    )

    from .engine import (
        KineticEngine,
        Presence,
        Delta,
    )
except ImportError:
    # Fall back to absolute imports (when running directly)
    from core import (
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
    )

    from matter import (
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
    )

    from engine import (
        KineticEngine,
        Presence,
        Delta,
    )

__version__ = "1.0.0"
__all__ = [
    # Core
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
