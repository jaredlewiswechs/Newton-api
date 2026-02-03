"""
═══════════════════════════════════════════════════════════════════════════════
NINA DEVELOPER TOOLS (nina-forge)
Verification Engine for Newton Verified Computation

The formal constructs from:
"Newton as a Verified Computation Substrate"
Jared Lewis — parcRI Research / Ada Computing Company — Feb 2026

═══════════════════════════════════════════════════════════════════════════════
"""

from .forge import (
    Regime,
    RegimeType,
    TrustLabel,
    TrustLattice,
    DistortionMetric,
    GeometryMismatchError,
    Pipeline,
    PipelineResult,
    ExecutionBounds
)

__version__ = "0.1.0"
__all__ = [
    "Regime",
    "RegimeType", 
    "TrustLabel",
    "TrustLattice",
    "DistortionMetric",
    "GeometryMismatchError",
    "Pipeline",
    "PipelineResult",
    "ExecutionBounds"
]
