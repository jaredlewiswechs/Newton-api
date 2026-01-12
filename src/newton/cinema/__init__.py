"""
NEWTON CINEMA COMPANION v2.0 - KINEMATIC EDITION
═══════════════════════════════════════════════════════════════════════════════

A kinematically aware cinema companion that treats movie scenes as a
Constraint Polytope. Newton calculates Interaction Demand (f) against
Narrative Gravity (g) to determine whether to speak or remain silent.

"The silence IS the instruction."

Key Components:
  - GlyphGeometry: Mechanical properties of letterforms
  - KinematicLinguistics: Linguistic instability analysis
  - KineticForge: f/g ratio verification engine
  - KinematicCinemaCompanion: Executive companion with damping

Example Usage:
    >>> from newton.cinema import KinematicCinemaCompanion, SceneType
    >>> companion = KinematicCinemaCompanion()
    >>> spoken, proof = companion.evaluate_intent(
    ...     "The lighting here is strictly Bauhaus.",
    ...     priority=0.8,
    ...     scene_type=SceneType.QUIET
    ... )
    >>> print(f"Spoken: {spoken}, Ratio: {proof.ratio:.2f}")
"""

from .matter import (
    # Glyph Types
    GlyphProperties,
    GlyphGeometry,
    StabilityClass,
    STABILITY_CLASSES,
    DAMPING_SUBSTITUTIONS,
)

from .core import (
    # Result Types
    ForgeResult,
    KinematicProof,
    SpeechEvent,
    # Scene Classification
    SceneType,
    # Engines
    KinematicLinguistics,
    KineticForge,
    KinematicCinemaCompanion,
)


__version__ = "2.0.0"

__all__ = [
    # Version
    "__version__",
    # Matter Types
    "GlyphProperties",
    "GlyphGeometry",
    "StabilityClass",
    "STABILITY_CLASSES",
    "DAMPING_SUBSTITUTIONS",
    # Core Types
    "ForgeResult",
    "KinematicProof",
    "SpeechEvent",
    "SceneType",
    # Engines
    "KinematicLinguistics",
    "KineticForge",
    "KinematicCinemaCompanion",
]
