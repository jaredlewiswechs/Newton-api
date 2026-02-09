"""
KINEMATIC LINGUISTICS - MATTER TYPES
A Geometric Substrate for Semantic Reliability

PARCRI Real Intelligence - January 2026
Specification v1.1 (Validated Refinements)

This module defines the core data structures for treating language as geometry:
  - Glyphs: Characters with intrinsic mechanical properties
  - Phonosemantic Clusters: Letter combinations with consistent mechanical meaning
  - Stability Classes: Categorical glyph classification
  - Mechanical Roles: Position-dependent letter functions

Core Axiom: Language is a conserved geometric system.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


# ==================================================================================
# GLYPH MECHANICAL PROPERTIES (Section 2.1 of Specification)
# ==================================================================================

@dataclass(frozen=True)
class GlyphMechanics:
    """
    Immutable mechanical properties of a letterform.

    Each glyph possesses intrinsic mechanical properties derived from its topology.
    These properties emerge from the physical constraints the shape embodies.

    v1.1 Addition: consonant flag for weighted analysis.
    """
    topology: str              # Physical shape description
    physical_property: str     # What the form represents mechanically
    vector_type: str           # Force/motion classification
    stability: float           # Derived stability score (0.0-1.0)
    mechanical_role: str       # Primary mechanical function in word assembly
    is_consonant: bool         # True for consonants (2x semantic weight in v1.1)

    def __post_init__(self):
        if not 0.0 <= self.stability <= 1.0:
            raise ValueError(f"Stability must be in [0.0, 1.0], got {self.stability}")


class GlyphRole(Enum):
    """Position-dependent mechanical role classifications."""
    ANCHOR = "anchor"           # T, H, B - Fixed boundary points
    BRACE = "brace"             # R, X - Diagonal resistance, torsional support
    CONTAINER = "container"     # O, U, B, D - Volume/capacity holders
    FLOW = "flow"               # L, S, F - Directional movement
    BRIDGE = "bridge"           # A, H, N - Span connections
    LEVER = "lever"             # F, P, K - Force application
    WAVE = "wave"               # M, W, Y - Oscillatory patterns
    GATE = "gate"               # G, C - Flow control/capture
    AXIS = "axis"               # I, J - Linear alignment
    CUT = "cut"                 # K, Z, X - Severing/terminal actions


class GlyphRegistry:
    """
    The complete kinematic mapping of the Latin alphabet.

    From Section 2.1: Each character possesses intrinsic mechanical properties
    derived from its topology. These properties are not assigned arbitrarily
    but emerge from the physical constraints the shape embodies.

    v1.1 Update: Includes is_consonant for weighted analysis.
    """

    GLYPHS: Dict[str, GlyphMechanics] = {
        'A': GlyphMechanics(
            topology="Triangular frame, crossbar",
            physical_property="Stability, load distribution",
            vector_type="Static equilibrium",
            stability=0.9,
            mechanical_role="Bridge/Shield - Pyramidal deflection, protects beneath",
            is_consonant=False  # Vowel
        ),
        'B': GlyphMechanics(
            topology="Vertical spine, dual lobes",
            physical_property="Containment, redundancy",
            vector_type="Volume storage",
            stability=0.8,
            mechanical_role="Container/Block - Dual containment provides redundancy",
            is_consonant=True
        ),
        'C': GlyphMechanics(
            topology="Open arc",
            physical_property="Reception, incomplete enclosure",
            vector_type="Directional aperture",
            stability=0.4,
            mechanical_role="Arc/Gate - Directional curve, guides output vector",
            is_consonant=True
        ),
        'D': GlyphMechanics(
            topology="Vertical spine, single lobe",
            physical_property="Weight, mass concentration",
            vector_type="Gravitational load",
            stability=0.7,
            mechanical_role="Mass/Weight - Heavy initial load, depth",
            is_consonant=True
        ),
        'E': GlyphMechanics(
            topology="Vertical with horizontal tiers",
            physical_property="Layering, stratification",
            vector_type="Hierarchical distribution",
            stability=0.5,
            mechanical_role="Layers/Ejection - Stratified levels, release outward",
            is_consonant=False  # Vowel
        ),
        'F': GlyphMechanics(
            topology="Vertical post, cantilever arms",
            physical_property="Reach, leverage",
            vector_type="Moment arm",
            stability=0.4,
            mechanical_role="Lever/Tool/Fence - Applies leverage, defines boundary",
            is_consonant=True
        ),
        'G': GlyphMechanics(
            topology="Arc with inward hook",
            physical_property="Capture, gating",
            vector_type="Flow control",
            stability=0.6,
            mechanical_role="Gate/Trap - Captures, controls flow",
            is_consonant=True
        ),
        'H': GlyphMechanics(
            topology="Two pillars, crossbeam",
            physical_property="Bridging, connection",
            vector_type="Tensile span",
            stability=0.85,
            mechanical_role="Bridge/Structure - Dual vertical support, spans gaps",
            is_consonant=True
        ),
        'I': GlyphMechanics(
            topology="Vertical line",
            physical_property="Axis, alignment",
            vector_type="Linear direction",
            stability=0.3,
            mechanical_role="Axis/Strut/Pin/Ray - Pure vertical alignment",
            is_consonant=False  # Vowel
        ),
        'J': GlyphMechanics(
            topology="Vertical with curved base",
            physical_property="Descent, collection",
            vector_type="Gravitational flow",
            stability=0.35,
            mechanical_role="Hook/Descent - Collects at bottom",
            is_consonant=True
        ),
        'K': GlyphMechanics(
            topology="Vertical with acute diagonals",
            physical_property="Shear, cutting action",
            vector_type="Kinetic impact",
            stability=0.4,
            mechanical_role="Cut/Buckle/Impact - Severs, decides, terminates",
            is_consonant=True
        ),
        'L': GlyphMechanics(
            topology="Vertical to horizontal bend",
            physical_property="Flow redirection, pooling",
            vector_type="Liquid dynamics",
            stability=0.5,
            mechanical_role="Flow/Beam/Gravity - Redirects, pools at bottom",
            is_consonant=True
        ),
        'M': GlyphMechanics(
            topology="Double peak, stable base",
            physical_property="Oscillation, wave stability",
            vector_type="Harmonic frequency",
            stability=0.7,
            mechanical_role="Wave/Stable Hum - Continuous oscillation with stability",
            is_consonant=True
        ),
        'N': GlyphMechanics(
            topology="Two verticals, diagonal bridge",
            physical_property="Transfer, passage",
            vector_type="State transition",
            stability=0.6,
            mechanical_role="Bridge/Passage/Gate - Transfer between states",
            is_consonant=True
        ),
        'O': GlyphMechanics(
            topology="Closed loop",
            physical_property="Complete containment",
            vector_type="Volume enclosure",
            stability=0.9,
            mechanical_role="Eye/Flywheel/Loop - Complete containment, stores momentum",
            is_consonant=False  # Vowel
        ),
        'P': GlyphMechanics(
            topology="Vertical spine, top bulb",
            physical_property="Pressure, potential",
            vector_type="Stored energy",
            stability=0.7,
            mechanical_role="Pressure Bulb - Stores potential energy",
            is_consonant=True
        ),
        'Q': GlyphMechanics(
            topology="Closed loop with tail",
            physical_property="Containment with release",
            vector_type="Controlled discharge",
            stability=0.75,
            mechanical_role="Container with escape - Mostly closed with release valve",
            is_consonant=True
        ),
        'R': GlyphMechanics(
            topology="Vertical, bulb, diagonal leg",
            physical_property="Resistance, bracing",
            vector_type="Force opposition",
            stability=0.8,
            mechanical_role="Brace/Grinder/Resistance - Prevents tipping, converts motion to work",
            is_consonant=True
        ),
        'S': GlyphMechanics(
            topology="Sinuous curve",
            physical_property="Slip, flexibility",
            vector_type="Low friction coefficient",
            stability=0.2,
            mechanical_role="Spring/Bond/Slip - Shock absorption, flexible connection",
            is_consonant=True
        ),
        'T': GlyphMechanics(
            topology="Vertical post, horizontal cap",
            physical_property="Hard stop, limit",
            vector_type="Impact boundary",
            stability=0.85,
            mechanical_role="Post/Stop/Anchor - Hard boundary, establishes fixed limits",
            is_consonant=True
        ),
        'U': GlyphMechanics(
            topology="Open vessel",
            physical_property="Reception, holding",
            vector_type="Capacity volume",
            stability=0.7,
            mechanical_role="Vessel/Basin - Receives and holds weight",
            is_consonant=False  # Vowel
        ),
        'V': GlyphMechanics(
            topology="Converging lines",
            physical_property="Focus, concentration",
            vector_type="Vector convergence",
            stability=0.6,
            mechanical_role="Focus/Convergence - Directs energy to point",
            is_consonant=True
        ),
        'W': GlyphMechanics(
            topology="Double valley",
            physical_property="Wave, instability",
            vector_type="Oscillatory motion",
            stability=0.3,
            mechanical_role="Wave/Wobble - Unstable oscillation",
            is_consonant=True
        ),
        'X': GlyphMechanics(
            topology="Intersecting diagonals",
            physical_property="Cross-bracing, locking",
            vector_type="Torsional rigidity",
            stability=0.9,
            mechanical_role="Lock/Brace - Cross-brace prevents twisting, marks completion",
            is_consonant=True
        ),
        'Y': GlyphMechanics(
            topology="Branching fork",
            physical_property="Distribution, splitting",
            vector_type="Flow bifurcation",
            stability=0.5,
            mechanical_role="Fork/Junction - Distribution (terminal) or meeting point (structural)",
            is_consonant=True  # Consonant when structural, sometimes vowel
        ),
        'Z': GlyphMechanics(
            topology="Angular zigzag",
            physical_property="Rapid direction change",
            vector_type="Energy dissipation",
            stability=0.2,
            mechanical_role="Zigzag/Cut - Rapid direction change, energy dissipation",
            is_consonant=True
        ),
    }

    # Sets for quick classification
    VOWELS: Set[str] = {'A', 'E', 'I', 'O', 'U'}
    CONSONANTS: Set[str] = set(GLYPHS.keys()) - VOWELS

    # Stability class sets (from Section 2.1)
    HIGH_STABILITY: Set[str] = {'A', 'B', 'H', 'O', 'R', 'T', 'X', 'Q'}  # 0.7+
    MEDIUM_STABILITY: Set[str] = {'D', 'E', 'G', 'L', 'M', 'N', 'P', 'U', 'V', 'Y'}  # 0.5-0.69
    LOW_STABILITY: Set[str] = {'C', 'F', 'I', 'J', 'K', 'S', 'W', 'Z'}  # < 0.5

    # Glyph function categories (from specification tables)
    ANCHORS: Set[str] = {'T', 'H', 'B', 'M', 'X', 'A'}  # Provide stability
    DESTABILIZERS: Set[str] = {'S', 'L', 'W', 'Y', 'C'}  # Introduce instability
    PRESSURE_GLYPHS: Set[str] = {'P', 'F', 'K', 'R'}  # Energy/force application
    VOLUME_GLYPHS: Set[str] = {'O', 'U', 'B', 'D'}  # Containment

    @classmethod
    def get(cls, glyph: str) -> Optional[GlyphMechanics]:
        """Retrieve mechanics for a glyph."""
        return cls.GLYPHS.get(glyph.upper())

    @classmethod
    def stability(cls, glyph: str) -> float:
        """Get stability score for a glyph (0.5 for non-alphabetic)."""
        upper = glyph.upper()
        if upper in cls.GLYPHS:
            return cls.GLYPHS[upper].stability
        return 0.5

    @classmethod
    def is_consonant(cls, glyph: str) -> bool:
        """Check if glyph is a consonant."""
        return glyph.upper() in cls.CONSONANTS

    @classmethod
    def is_vowel(cls, glyph: str) -> bool:
        """Check if glyph is a vowel."""
        return glyph.upper() in cls.VOWELS


# ==================================================================================
# PHONOSEMANTIC CLUSTERS (Section 4 of Specification)
# ==================================================================================

@dataclass(frozen=True)
class PhonosemanticsCluster:
    """
    A letter combination with consistent mechanical meaning across the lexicon.

    These clusters function as semantic primitives that carry consistent
    mechanical meaning across the lexicon.
    """
    pattern: str                 # The cluster pattern (e.g., "ST", "FL-")
    position: str                # "initial", "terminal", or "any"
    mechanical_meaning: str      # What the cluster encodes mechanically
    description: str             # Detailed mechanical explanation
    examples: Tuple[str, ...]    # Example words demonstrating the pattern


class PhonosemanticsRegistry:
    """
    Registry of phonosemantic clusters from Section 4.

    Systematic patterns emerge in letter combinations that function
    as semantic primitives carrying consistent mechanical meaning.
    """

    CLUSTERS: Dict[str, PhonosemanticsCluster] = {
        # Section 4.1: The ST Anchor (Static Friction)
        "-ST": PhonosemanticsCluster(
            pattern="-ST",
            position="terminal",
            mechanical_meaning="Static Friction / Stopping State",
            description="S provides approach curve, T provides hard boundary. "
                       "Words terminating in -ST consistently encode stopping or standing states.",
            examples=("REST", "TEST", "LAST", "PAST", "FAST", "TRUST")
        ),

        # Section 4.2: The FL Vector (Planar Flow)
        "FL-": PhonosemanticsCluster(
            pattern="FL-",
            position="initial",
            mechanical_meaning="Planar Flow / Surface Movement",
            description="F provides leading edge, L provides flow direction. "
                       "Words initiating with FL- describe surface movement and liquid dynamics.",
            examples=("FLOW", "FLY", "FLAT", "FLAME", "FLOOR", "FLEE")
        ),

        # Section 4.3: The GL Vector (Viscous Flow)
        "GL-": PhonosemanticsCluster(
            pattern="GL-",
            position="initial",
            mechanical_meaning="Viscous Flow / Gated Flow",
            description="GL- is FL- with a gate (G) prefix. The flow is captured, slowed, or made viscous.",
            examples=("GLUE", "GLOOM", "GLARE", "GLACIER", "GLASS")
        ),

        # Section 4.4: The SP Vector (Radial Emission)
        "SP-": PhonosemanticsCluster(
            pattern="SP-",
            position="initial",
            mechanical_meaning="Radial Emission / Pressure Release",
            description="S (source curve) + P (pressure). Energy radiates outward from a point.",
            examples=("SPEAK", "SPARK", "SPREAD", "SPEED", "SPACE", "SPIT")
        ),

        # Additional clusters identified from specification examples
        "TR-": PhonosemanticsCluster(
            pattern="TR-",
            position="initial",
            mechanical_meaning="Braced Transfer / Structural Movement",
            description="T (anchor) + R (brace). Movement with structural support.",
            examples=("TRUST", "TREE", "TRACK", "TRAIN", "TRADE")
        ),

        "BR-": PhonosemanticsCluster(
            pattern="BR-",
            position="initial",
            mechanical_meaning="Breaking / Rupture",
            description="B (block) + R (grind). Force meeting resistance leading to rupture.",
            examples=("BREAK", "BRICK", "BRANCH", "BRIDGE", "BRIGHT")
        ),

        "-NK": PhonosemanticsCluster(
            pattern="-NK",
            position="terminal",
            mechanical_meaning="Anchored Cut / Decisive End",
            description="N (passage) + K (cut). State passes through then severs decisively.",
            examples=("THINK", "DRINK", "SINK", "LINK", "BANK")
        ),

        "-ND": PhonosemanticsCluster(
            pattern="-ND",
            position="terminal",
            mechanical_meaning="Grounded Passage / Weighted End",
            description="N (passage) + D (weight). Transfer to grounded state.",
            examples=("LAND", "HAND", "SEND", "MIND", "BOND")
        ),

        "CR-": PhonosemanticsCluster(
            pattern="CR-",
            position="initial",
            mechanical_meaning="Curved Resistance / Impact Through Arc",
            description="C (arc) + R (resistance). Curved motion meeting force.",
            examples=("CRASH", "CRUSH", "CRACK", "CREST", "CREATE")
        ),

        "DR-": PhonosemanticsCluster(
            pattern="DR-",
            position="initial",
            mechanical_meaning="Weight with Resistance / Heavy Flow",
            description="D (mass) + R (resistance). Heavy movement against friction.",
            examples=("DREAM", "DRIVE", "DRAFT", "DRAIN", "DRAW")
        ),
    }

    @classmethod
    def detect_clusters(cls, word: str) -> List[PhonosemanticsCluster]:
        """
        Detect all phonosemantic clusters present in a word.

        Args:
            word: The word to analyze

        Returns:
            List of detected clusters
        """
        upper = word.upper()
        detected = []

        for pattern, cluster in cls.CLUSTERS.items():
            if cluster.position == "initial":
                # Check if word starts with pattern (minus the -)
                check_pattern = pattern.rstrip('-')
                if upper.startswith(check_pattern):
                    detected.append(cluster)
            elif cluster.position == "terminal":
                # Check if word ends with pattern (minus the -)
                check_pattern = pattern.lstrip('-')
                if upper.endswith(check_pattern):
                    detected.append(cluster)
            else:  # "any" position
                check_pattern = pattern.strip('-')
                if check_pattern in upper:
                    detected.append(cluster)

        return detected

    @classmethod
    def get_cluster(cls, pattern: str) -> Optional[PhonosemanticsCluster]:
        """Get cluster by pattern name."""
        return cls.CLUSTERS.get(pattern)


# ==================================================================================
# WORD GEOMETRY CLASSIFICATIONS
# ==================================================================================

class StabilityClass(Enum):
    """Categorical stability classification."""
    HIGH = "high"       # 0.7-1.0: A, B, H, O, R, T, X, Q
    MEDIUM = "medium"   # 0.5-0.69: D, E, G, L, M, N, P, U, V, Y
    LOW = "low"         # 0.0-0.49: C, F, I, J, K, S, W, Z


class LetterPosition(Enum):
    """Position in word assembly mechanics."""
    INITIAL = "initial"       # First letter - establishes primary load path
    MEDIAL = "medial"         # Middle letters - provide bracing and flow
    TERMINAL = "terminal"     # Last letter - determines output state


@dataclass(frozen=True)
class WordAssemblyRole:
    """
    Position-specific mechanical role in word assembly.

    From Section 2.2: The sequence matters: initial letters establish the primary
    load path, medial letters provide bracing and flow, terminal letters
    determine the output state.
    """
    letter: str
    position: LetterPosition
    glyph_mechanics: GlyphMechanics
    position_weight: float  # Weight based on position importance

    @property
    def weighted_stability(self) -> float:
        """Stability weighted by position importance."""
        return self.glyph_mechanics.stability * self.position_weight


# ==================================================================================
# COMMON WORD GEOMETRIES (Appendix B)
# ==================================================================================

WORD_GEOMETRY_EXAMPLES: Dict[str, Dict[str, str]] = {
    "LOVE": {
        "assembly": "L (flow) + O (contain) + V (focus) + E (layers)",
        "prediction": "Flow into containment, focused through layers"
    },
    "HATE": {
        "assembly": "H (structure) + A (frame) + T (stop) + E (out)",
        "prediction": "Rigid structure stopped, expelling outward"
    },
    "HELP": {
        "assembly": "H (bridge) + E (layers) + L (flow) + P (pressure)",
        "prediction": "Bridge through layers, flow pressure to target"
    },
    "HARM": {
        "assembly": "H (structure) + A (frame) + R (grind) + M (wave)",
        "prediction": "Structure ground by oscillating force"
    },
    "WORK": {
        "assembly": "W (wave) + O (loop) + R (resist) + K (cut)",
        "prediction": "Oscillation through cycle meeting resistance"
    },
    "PLAY": {
        "assembly": "P (pressure) + L (flow) + A (frame) + Y (fork)",
        "prediction": "Pressure flows through frame, distributes"
    },
    "THINK": {
        "assembly": "T (stop) + H (bridge) + I (align) + N (pass) + K (cut)",
        "prediction": "Stop, bridge, align, pass through, decide (cut)"
    },
    "FEEL": {
        "assembly": "F (reach) + E (layers) + E (layers) + L (flow)",
        "prediction": "Reaching through multiple layers, flowing"
    },
    "TRUST": {
        "assembly": "T (post) + R (brace) + U (vessel) + S (bond) + T (post)",
        "prediction": "Suspension bridge - anchored at both ends, braced, holds weight"
    },
    "FORCE": {
        "assembly": "F (lever) + O (flywheel) + R (grinder) + C (arc) + E (ejection)",
        "prediction": "Leverage to momentum to work to direction to release"
    },
    "DREAM": {
        "assembly": "D (mass) + R (roller) + E (layers) + A (bridge) + M (wave)",
        "prediction": "Heavy sub-surface flowing state through strata"
    },
    "SAFE": {
        "assembly": "S (spring) + A (shield) + F (fence) + E (shelves)",
        "prediction": "Shock absorption, deflection, perimeter, redundancy"
    },
    "FIX": {
        "assembly": "F (tool) + I (strut) + X (lock)",
        "prediction": "Three-step repair: reach in, insert support, lock down"
    },
}


# ==================================================================================
# EXPORTS
# ==================================================================================

__all__ = [
    # Core Types
    "GlyphMechanics",
    "GlyphRole",
    "GlyphRegistry",
    # Phonosemantics
    "PhonosemanticsCluster",
    "PhonosemanticsRegistry",
    # Classifications
    "StabilityClass",
    "LetterPosition",
    "WordAssemblyRole",
    # Reference Data
    "WORD_GEOMETRY_EXAMPLES",
]
