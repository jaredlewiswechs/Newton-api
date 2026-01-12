"""
NEWTON CINEMA COMPANION - MATTER TYPES
═══════════════════════════════════════════════════════════════════════════════

Glyph Geometry: The mechanical properties of letterforms as kinematic entities.

Each glyph possesses:
  - Topology: Physical shape characteristics
  - Physical Property: What the form represents mechanically
  - Vector Type: The type of force/motion it embodies
  - Stability: Derived mechanical stability score (0.0-1.0)

The stability score determines how much "noise" or "demand" a letter
contributes to spoken language in a constrained social space.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# GLYPH GEOMETRY (From Newton Typography Specification)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class GlyphProperties:
    """Immutable kinematic properties of a letterform."""
    topology: str           # Physical shape description
    physical_property: str  # Mechanical meaning
    vector_type: str        # Force/motion classification
    stability: float        # Derived stability score (0.0-1.0)

    def __post_init__(self):
        if not 0.0 <= self.stability <= 1.0:
            raise ValueError(f"Stability must be in [0.0, 1.0], got {self.stability}")


class GlyphGeometry:
    """
    The complete kinematic mapping of the Latin alphabet.

    Stability Derivation:
      - High stability (0.8-1.0): Closed loops, stable bases, symmetric forms
      - Medium stability (0.5-0.7): Partial enclosure, directional forms
      - Low stability (0.2-0.4): Open curves, dynamic/unstable shapes

    Usage:
        >>> props = GlyphGeometry.get('A')
        >>> props.stability
        0.9
        >>> props.topology
        'Triangular frame, crossbar'
    """

    # The canonical glyph-to-properties mapping
    GLYPHS: Dict[str, GlyphProperties] = {
        'A': GlyphProperties(
            topology="Triangular frame, crossbar",
            physical_property="Stability, load distribution",
            vector_type="Static equilibrium",
            stability=0.9  # Highest stability - perfect triangular structure
        ),
        'B': GlyphProperties(
            topology="Vertical spine, dual lobes",
            physical_property="Containment, redundancy",
            vector_type="Volume storage",
            stability=0.8  # High - dual containment provides redundancy
        ),
        'C': GlyphProperties(
            topology="Open arc",
            physical_property="Reception, incomplete enclosure",
            vector_type="Directional aperture",
            stability=0.4  # Low - open form lacks closure
        ),
        'D': GlyphProperties(
            topology="Vertical spine, single lobe",
            physical_property="Weight, mass concentration",
            vector_type="Gravitational load",
            stability=0.7  # Medium-high - single but closed containment
        ),
        'E': GlyphProperties(
            topology="Vertical with horizontal tiers",
            physical_property="Layering, stratification",
            vector_type="Hierarchical distribution",
            stability=0.5  # Medium - cantilevered arms reduce stability
        ),
        'F': GlyphProperties(
            topology="Vertical post, cantilever arms",
            physical_property="Reach, leverage",
            vector_type="Moment arm",
            stability=0.4  # Low - unbalanced cantilever
        ),
        'G': GlyphProperties(
            topology="Arc with inward hook",
            physical_property="Capture, gating",
            vector_type="Flow control",
            stability=0.6  # Medium - partial enclosure with direction
        ),
        'H': GlyphProperties(
            topology="Two pillars, crossbeam",
            physical_property="Bridging, connection",
            vector_type="Tensile span",
            stability=0.85  # High - dual vertical support
        ),
        'I': GlyphProperties(
            topology="Vertical line",
            physical_property="Axis, alignment",
            vector_type="Linear direction",
            stability=0.3  # Low - minimal structural complexity
        ),
        'J': GlyphProperties(
            topology="Vertical with curved base",
            physical_property="Descent, collection",
            vector_type="Gravitational flow",
            stability=0.35  # Low - unstable hook
        ),
        'K': GlyphProperties(
            topology="Vertical with acute diagonals",
            physical_property="Shear, cutting action",
            vector_type="Kinetic impact",
            stability=0.4  # Low - angular tension
        ),
        'L': GlyphProperties(
            topology="Vertical to horizontal bend",
            physical_property="Flow redirection, pooling",
            vector_type="Liquid dynamics",
            stability=0.5  # Medium - right angle provides base
        ),
        'M': GlyphProperties(
            topology="Double peak, stable base",
            physical_property="Oscillation, wave stability",
            vector_type="Harmonic frequency",
            stability=0.7  # Medium-high - wide stable base
        ),
        'N': GlyphProperties(
            topology="Two verticals, diagonal bridge",
            physical_property="Transfer, passage",
            vector_type="State transition",
            stability=0.6  # Medium - diagonal creates motion
        ),
        'O': GlyphProperties(
            topology="Closed loop",
            physical_property="Complete containment",
            vector_type="Volume enclosure",
            stability=0.9  # Highest - perfect closure
        ),
        'P': GlyphProperties(
            topology="Vertical spine, top bulb",
            physical_property="Pressure, potential",
            vector_type="Stored energy",
            stability=0.7  # Medium-high - top-heavy but grounded
        ),
        'Q': GlyphProperties(
            topology="Closed loop with tail",
            physical_property="Containment with release",
            vector_type="Controlled discharge",
            stability=0.75  # High - mostly closed
        ),
        'R': GlyphProperties(
            topology="Vertical, bulb, diagonal leg",
            physical_property="Resistance, bracing",
            vector_type="Force opposition",
            stability=0.8  # High - triangulated support
        ),
        'S': GlyphProperties(
            topology="Sinuous curve",
            physical_property="Slip, flexibility",
            vector_type="Low friction coefficient",
            stability=0.3  # Low - no stable orientation
        ),
        'T': GlyphProperties(
            topology="Vertical post, horizontal cap",
            physical_property="Hard stop, limit",
            vector_type="Impact boundary",
            stability=0.85  # High - clear terminal structure
        ),
        'U': GlyphProperties(
            topology="Open vessel",
            physical_property="Reception, holding",
            vector_type="Capacity volume",
            stability=0.7  # Medium-high - basin structure
        ),
        'V': GlyphProperties(
            topology="Converging lines",
            physical_property="Focus, concentration",
            vector_type="Vector convergence",
            stability=0.6  # Medium - convergent but open
        ),
        'W': GlyphProperties(
            topology="Double valley",
            physical_property="Wave, instability",
            vector_type="Oscillatory motion",
            stability=0.4  # Low - unstable oscillation
        ),
        'X': GlyphProperties(
            topology="Intersecting diagonals",
            physical_property="Cross-bracing, locking",
            vector_type="Torsional rigidity",
            stability=0.9  # High - cross-braced structure
        ),
        'Y': GlyphProperties(
            topology="Branching fork",
            physical_property="Distribution, splitting",
            vector_type="Flow bifurcation",
            stability=0.5  # Medium - branch point instability
        ),
        'Z': GlyphProperties(
            topology="Angular zigzag",
            physical_property="Rapid direction change",
            vector_type="Energy dissipation",
            stability=0.3  # Low - high-energy angular form
        ),
    }

    @classmethod
    def get(cls, glyph: str) -> GlyphProperties:
        """
        Retrieve kinematic properties for a glyph.

        Args:
            glyph: Single uppercase letter A-Z

        Returns:
            GlyphProperties for the glyph

        Raises:
            KeyError: If glyph not in alphabet
        """
        return cls.GLYPHS[glyph.upper()]

    @classmethod
    def stability(cls, glyph: str) -> float:
        """
        Get stability score for a glyph (convenience method).

        Args:
            glyph: Single character

        Returns:
            Stability score [0.0-1.0], or 0.5 for non-alphabetic
        """
        upper = glyph.upper()
        if upper in cls.GLYPHS:
            return cls.GLYPHS[upper].stability
        return 0.5  # Neutral stability for non-alphabetic

    @classmethod
    def analyze_word(cls, word: str) -> Tuple[float, str]:
        """
        Analyze a word's kinematic stability.

        Returns:
            Tuple of (average_stability, dominant_vector_type)
        """
        clean = word.upper()
        if not clean:
            return (0.5, "Neutral")

        stabilities = []
        vector_counts: Dict[str, int] = {}

        for char in clean:
            if char in cls.GLYPHS:
                props = cls.GLYPHS[char]
                stabilities.append(props.stability)
                vector_counts[props.vector_type] = vector_counts.get(props.vector_type, 0) + 1

        avg_stability = sum(stabilities) / len(stabilities) if stabilities else 0.5
        dominant_vector = max(vector_counts.items(), key=lambda x: x[1])[0] if vector_counts else "Neutral"

        return (avg_stability, dominant_vector)


# ═══════════════════════════════════════════════════════════════════════════════
# STABILITY CLASSES (Derived from Glyph Geometry)
# ═══════════════════════════════════════════════════════════════════════════════

class StabilityClass(Enum):
    """Classification of glyph stability for quick lookup."""
    HIGH = "high"       # 0.7-1.0: A, B, H, O, R, T, X
    MEDIUM = "medium"   # 0.5-0.69: D, E, G, L, M, N, P, Q, U, V, Y
    LOW = "low"         # 0.0-0.49: C, F, I, J, K, S, W, Z


# Precomputed stability classes
STABILITY_CLASSES: Dict[str, StabilityClass] = {
    char: (
        StabilityClass.HIGH if props.stability >= 0.7
        else StabilityClass.MEDIUM if props.stability >= 0.5
        else StabilityClass.LOW
    )
    for char, props in GlyphGeometry.GLYPHS.items()
}


# ═══════════════════════════════════════════════════════════════════════════════
# DAMPING SUBSTITUTION MAP (For Kinematic Damping)
# ═══════════════════════════════════════════════════════════════════════════════

# Words that can be substituted for kinematic stability improvement
# Maps unstable words (high S, Z, I content) to stable alternatives
DAMPING_SUBSTITUTIONS: Dict[str, str] = {
    # S-heavy -> Stable replacements
    "STRESSFUL": "HEAVY",
    "SCENE": "PART",
    "SCARE": "FEAR",
    "SCARY": "DARK",
    "SUSPENSE": "TENSION",
    "SINISTER": "OMINOUS",
    "SCREAMING": "LOUD",
    "SUBTLE": "QUIET",

    # I-heavy -> Balanced replacements
    "INCREDIBLE": "GREAT",
    "INTERESTING": "NOTED",
    "INSANE": "WILD",
    "INTENSE": "POWERFUL",
    "INTRICATE": "DETAILED",

    # Z-heavy -> Stable replacements
    "CRAZY": "BOLD",
    "AMAZING": "GRAND",
    "BIZARRE": "ODD",

    # Mixed unstable -> Stable
    "ABSOLUTELY": "TRULY",
    "ESSENTIALLY": "REALLY",
    "BASICALLY": "MAINLY",
    "SERIOUSLY": "DEEPLY",
    "OBVIOUSLY": "CLEARLY",

    # Exclamatory -> Measured
    "WOW": "GOOD",
    "WHOA": "WAIT",
    "YIKES": "WELL",
}


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "GlyphProperties",
    "GlyphGeometry",
    "StabilityClass",
    "STABILITY_CLASSES",
    "DAMPING_SUBSTITUTIONS",
]
