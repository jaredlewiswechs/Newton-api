"""
Newton CAD - Constraint-First Spatial Design
=============================================

The Floor of Newton: Where spatial design meets type theory.

In Newton CAD:
- Floor (g) = The ground plane, reality's constraint boundary
- Matter (f) = Building volumes, spatial intentions
- f/g ratio = Constraint utilization, visualized as color
- Force (>>) = Applying spatial matter to the floor

The ground IS the constraint. Buildings are matter applied against it.
When f/g >= 1, the space cannot exist - Ontological Death.

This is not CAD with constraints bolted on.
This is constraint geometry made visible.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

# Import Newton core primitives
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..core import Matter, Floor, Ratio, OntologicalDeath
except ImportError:
    from core import Matter, Floor, Ratio, OntologicalDeath


class FGState(Enum):
    """
    The f/g visual states from Newton's type theory.

    These map directly to constraint satisfaction levels
    and determine spatial visualization colors.
    """
    VERIFIED = "verified"      # f/g < 0.9θ  - GREEN, safe margin
    WARNING = "warning"        # 0.9θ ≤ f/g < θ - AMBER, approaching boundary
    FORBIDDEN = "forbidden"    # f/g ≥ θ - RED, constraint violated
    UNDEFINED = "undefined"    # g ≈ 0 - DEEP RED, ontological death (finfr)


@dataclass
class FGColors:
    """
    The f/g visual language color specification.
    From docs/product-architecture/FG_VISUAL_LANGUAGE.md
    """
    # Primary states
    VERIFIED: Tuple[int, int, int] = (0, 200, 83)      # #00C853
    WARNING: Tuple[int, int, int] = (255, 214, 0)      # #FFD600
    FORBIDDEN: Tuple[int, int, int] = (255, 23, 68)    # #FF1744
    UNDEFINED: Tuple[int, int, int] = (183, 28, 28)    # #B71C1C

    # Secondary states
    CHECKING: Tuple[int, int, int] = (41, 121, 255)    # #2979FF
    HISTORICAL: Tuple[int, int, int] = (176, 190, 197) # #B0BEC5
    PRISTINE: Tuple[int, int, int] = (255, 255, 255)   # #FFFFFF

    @classmethod
    def for_state(cls, state: FGState) -> Tuple[int, int, int]:
        """Get color for a given f/g state."""
        return {
            FGState.VERIFIED: cls.VERIFIED,
            FGState.WARNING: cls.WARNING,
            FGState.FORBIDDEN: cls.FORBIDDEN,
            FGState.UNDEFINED: cls.UNDEFINED,
        }.get(state, cls.HISTORICAL)

    @classmethod
    def for_ratio(cls, f: float, g: float, threshold: float = 1.0) -> Tuple[int, int, int]:
        """Get color based on f/g ratio."""
        state = cls.state_for_ratio(f, g, threshold)
        return cls.for_state(state)

    @staticmethod
    def state_for_ratio(f: float, g: float, threshold: float = 1.0) -> FGState:
        """Determine f/g state from ratio values."""
        if g <= 0:
            return FGState.UNDEFINED
        ratio = f / g
        if ratio >= threshold:
            return FGState.FORBIDDEN
        if ratio >= threshold * 0.9:
            return FGState.WARNING
        return FGState.VERIFIED


@dataclass
class SpatialMatter:
    """
    Matter with spatial extent - a volume in Newton CAD.

    This is the 'f' in the f/g ratio: what you're attempting
    to place in space against the Floor constraint.

    Properties:
        x, y: Position on the Floor (ground plane)
        z: Elevation above Floor (vertical position)
        width, depth: Horizontal extent
        height: Vertical extent (how much f pushes against g)
        capacity: How much of the Floor this matter claims
    """
    x: float
    y: float
    z: float  # Elevation - matters for the Floor relationship
    width: float
    depth: float
    height: float
    name: str = "space"
    space_type: str = "generic"
    color: Optional[Tuple[int, int, int]] = None

    # Constraint tracking
    capacity_used: float = 0.0    # f - what this space claims
    capacity_max: float = 0.0      # g - what's available

    @property
    def volume(self) -> float:
        """Total volume of this matter (cubic meters)."""
        return self.width * self.depth * self.height

    @property
    def footprint(self) -> float:
        """Area on the Floor (square meters)."""
        return self.width * self.depth

    @property
    def fg_ratio(self) -> float:
        """The f/g ratio for this space."""
        if self.capacity_max <= 0:
            return float('inf')
        return self.capacity_used / self.capacity_max

    @property
    def fg_state(self) -> FGState:
        """Current constraint state."""
        return FGColors.state_for_ratio(self.capacity_used, self.capacity_max)

    @property
    def is_grounded(self) -> bool:
        """Whether this matter touches the Floor (z=0)."""
        return self.z <= 0

    @property
    def floor_penetration(self) -> float:
        """How far below Floor (z=0) this matter extends. Negative = above floor."""
        return -self.z

    def to_matter(self) -> Matter:
        """Convert to Newton Matter primitive."""
        return Matter(self.footprint, "m²", self.name)


@dataclass
class SpatialFloor:
    """
    The Floor of Newton - the ground plane constraint.

    This is 'g' in the f/g ratio: reality's boundary.
    The ground plane at z=0 represents what reality allows.

    In spatial terms:
    - Total floor area = maximum capacity (g)
    - Used floor area = current load (f)
    - f/g ratio = how close to constraint violation

    The Floor is not just a surface - it's the constraint itself.
    """
    name: str
    width: float  # Total width available
    depth: float  # Total depth available
    area: float = field(init=False)  # g - total capacity
    used_area: float = 0.0  # f - current utilization

    # Spatial bounds
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0  # Always 0 - Floor IS at ground level

    # Matter applied to this Floor
    matter: List[SpatialMatter] = field(default_factory=list)

    def __post_init__(self):
        self.area = self.width * self.depth
        self.z = 0.0  # Floor is ALWAYS at z=0 - this is definitional

    @property
    def fg_ratio(self) -> float:
        """Overall f/g ratio for this Floor."""
        if self.area <= 0:
            return float('inf')
        return self.used_area / self.area

    @property
    def fg_state(self) -> FGState:
        """Current constraint state of the Floor."""
        return FGColors.state_for_ratio(self.used_area, self.area)

    @property
    def remaining_capacity(self) -> float:
        """How much area remains (g - f)."""
        return max(0, self.area - self.used_area)

    def can_accept(self, matter: SpatialMatter) -> bool:
        """Check if this Floor can accept the given spatial matter."""
        return self.used_area + matter.footprint <= self.area

    def apply_force(self, matter: SpatialMatter) -> Ratio:
        """
        Apply spatial matter to this Floor (the >> operator).

        This is Newton's Force applied to spatial design.
        Either the matter fits, or we get Ontological Death.
        """
        available = self.remaining_capacity
        fits = matter.footprint <= available

        ratio = Ratio(
            numerator=matter.footprint,
            denominator=available if available > 0 else 0.001,
            unit="m²",
            fits=fits,
            overflow=max(0, matter.footprint - available)
        )

        if fits:
            self.used_area += matter.footprint
            matter.capacity_used = matter.footprint
            matter.capacity_max = self.area
            self.matter.append(matter)
            return ratio
        else:
            raise OntologicalDeath(
                f"Spatial matter '{matter.name}' ({matter.footprint:.1f}m²) "
                f"exceeds Floor capacity ({available:.1f}m² remaining)",
                matter=matter.to_matter(),
                ratio=ratio
            )

    def to_floor(self) -> Floor:
        """Convert to Newton Floor primitive."""
        class DynamicFloor(Floor):
            area = Matter(self.area, "m²")
        DynamicFloor.__name__ = self.name
        return DynamicFloor()


@dataclass
class SpatialLevel:
    """
    A building level - a Floor with vertical position.

    Each level has its own Floor (constraint boundary).
    Basement levels (z < 0) are BELOW the ground Floor -
    they exist in constrained space carved from reality.
    """
    name: str
    elevation: float  # z position relative to ground Floor
    height: float     # vertical extent
    floor: SpatialFloor  # The constraint boundary for this level

    @property
    def is_basement(self) -> bool:
        """Whether this level is below the ground Floor."""
        return self.elevation < 0

    @property
    def is_at_grade(self) -> bool:
        """Whether this level is at ground Floor level."""
        return self.elevation == 0

    @property
    def fg_ratio(self) -> float:
        """f/g ratio for this level."""
        return self.floor.fg_ratio

    @property
    def fg_state(self) -> FGState:
        """Constraint state for this level."""
        return self.floor.fg_state


@dataclass
class NewtonBuilding:
    """
    A complete building in Newton CAD.

    A building is a collection of SpatialLevels,
    each with its own Floor constraint.

    The building as a whole has aggregate f/g metrics.
    """
    name: str
    levels: List[SpatialLevel] = field(default_factory=list)

    # Site constraints (the uber-Floor)
    site_area: float = 0.0  # Total buildable area (g)
    far: float = 1.0        # Floor Area Ratio limit

    @property
    def total_floor_area(self) -> float:
        """Total floor area across all levels (f)."""
        return sum(level.floor.used_area for level in self.levels)

    @property
    def gross_floor_area(self) -> float:
        """Gross floor area (GFA) - all level areas."""
        return sum(level.floor.area for level in self.levels)

    @property
    def building_fg_ratio(self) -> float:
        """Building-wide f/g ratio against FAR limit."""
        max_area = self.site_area * self.far
        if max_area <= 0:
            return float('inf')
        return self.gross_floor_area / max_area

    @property
    def building_fg_state(self) -> FGState:
        """Overall constraint state."""
        return FGColors.state_for_ratio(
            self.gross_floor_area,
            self.site_area * self.far
        )

    def add_level(self, level: SpatialLevel) -> None:
        """Add a level to the building."""
        self.levels.append(level)
        # Sort by elevation (basement first)
        self.levels.sort(key=lambda l: l.elevation)

    def get_level(self, name: str) -> Optional[SpatialLevel]:
        """Get level by name."""
        for level in self.levels:
            if level.name == name:
                return level
        return None

    def level_at_elevation(self, z: float) -> Optional[SpatialLevel]:
        """Get the level at a given elevation."""
        for level in self.levels:
            if level.elevation <= z < level.elevation + level.height:
                return level
        return None


# Helper functions for creating Newton CAD elements

def spatial_matter(
    x: float, y: float, z: float,
    width: float, depth: float, height: float,
    name: str = "space",
    space_type: str = "generic",
    color: Optional[Tuple[int, int, int]] = None
) -> SpatialMatter:
    """Create spatial matter (a volume)."""
    return SpatialMatter(x, y, z, width, depth, height, name, space_type, color)


def spatial_floor(
    name: str, width: float, depth: float,
    x: float = 0, y: float = 0
) -> SpatialFloor:
    """Create a spatial floor (constraint boundary)."""
    return SpatialFloor(name=name, width=width, depth=depth, x=x, y=y)


def apply_matter_to_floor(matter: SpatialMatter, floor: SpatialFloor) -> Ratio:
    """
    Apply spatial matter to a floor (>> operator).

    This is Newton's Force in spatial form.
    """
    return floor.apply_force(matter)


# The Force operator for SpatialMatter
def _spatial_rshift(self: SpatialMatter, floor: SpatialFloor) -> Ratio:
    """Enable matter >> floor syntax."""
    return floor.apply_force(self)

# Monkey-patch the >> operator onto SpatialMatter
SpatialMatter.__rshift__ = _spatial_rshift
