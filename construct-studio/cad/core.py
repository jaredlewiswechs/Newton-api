"""
CAD Core Data Model
===================

Buildings are composed of Levels.
Levels contain Spaces.
Spaces are bounded by Walls.
Everything is constraint-validated.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import uuid
import json


class SpaceType(Enum):
    """Types of architectural spaces."""
    # Work
    OFFICE = "office"
    OPEN_OFFICE = "open_office"
    STUDIO = "studio"
    LAB = "lab"
    WORKSHOP = "workshop"
    FORGE = "forge"

    # Common
    LOBBY = "lobby"
    RECEPTION = "reception"
    LOUNGE = "lounge"
    COMMONS = "commons"
    CORRIDOR = "corridor"
    ATRIUM = "atrium"

    # Meeting
    CONFERENCE = "conference"
    MEETING = "meeting"
    BOARDROOM = "boardroom"

    # Amenities
    CAFE = "cafe"
    KITCHEN = "kitchen"
    DINING = "dining"
    GYM = "gym"
    WELLNESS = "wellness"

    # Support
    RESTROOM = "restroom"
    STORAGE = "storage"
    MECHANICAL = "mechanical"
    SERVER = "server"
    UTILITY = "utility"

    # Special
    LIBRARY = "library"
    THEATER = "theater"
    GALLERY = "gallery"

    # Outdoor
    COURTYARD = "courtyard"
    TERRACE = "terrace"
    GARDEN = "garden"
    POCKET_PARK = "pocket_park"
    GREEN = "green"

    # Entry
    ENTRY = "entry"
    VESTIBULE = "vestibule"
    GRAND_ENTRY = "grand_entry"

    # Circulation
    STAIR = "stair"
    ELEVATOR = "elevator"
    RAMP = "ramp"


# Color palette for space types
SPACE_COLORS: Dict[SpaceType, str] = {
    # Work - Blues
    SpaceType.OFFICE: "#4A90D9",
    SpaceType.OPEN_OFFICE: "#5BA3EC",
    SpaceType.STUDIO: "#3D7AB8",
    SpaceType.LAB: "#2E5F8A",
    SpaceType.WORKSHOP: "#6B8FAD",
    SpaceType.FORGE: "#8B4513",

    # Common - Greens
    SpaceType.LOBBY: "#7CB342",
    SpaceType.RECEPTION: "#8BC34A",
    SpaceType.LOUNGE: "#9CCC65",
    SpaceType.COMMONS: "#AED581",
    SpaceType.CORRIDOR: "#E0E0E0",
    SpaceType.ATRIUM: "#C5E1A5",

    # Meeting - Purples
    SpaceType.CONFERENCE: "#9575CD",
    SpaceType.MEETING: "#B39DDB",
    SpaceType.BOARDROOM: "#7E57C2",

    # Amenities - Oranges/Yellows
    SpaceType.CAFE: "#FFB74D",
    SpaceType.KITCHEN: "#FFA726",
    SpaceType.DINING: "#FFCC80",
    SpaceType.GYM: "#FF7043",
    SpaceType.WELLNESS: "#FFAB91",

    # Support - Grays
    SpaceType.RESTROOM: "#BDBDBD",
    SpaceType.STORAGE: "#9E9E9E",
    SpaceType.MECHANICAL: "#757575",
    SpaceType.SERVER: "#616161",
    SpaceType.UTILITY: "#424242",

    # Special - Teals
    SpaceType.LIBRARY: "#4DB6AC",
    SpaceType.THEATER: "#26A69A",
    SpaceType.GALLERY: "#80CBC4",

    # Outdoor - Grass greens
    SpaceType.COURTYARD: "#81C784",
    SpaceType.TERRACE: "#A5D6A7",
    SpaceType.GARDEN: "#66BB6A",
    SpaceType.POCKET_PARK: "#4CAF50",
    SpaceType.GREEN: "#43A047",

    # Entry - Warm
    SpaceType.ENTRY: "#FFCA28",
    SpaceType.VESTIBULE: "#FFD54F",
    SpaceType.GRAND_ENTRY: "#FFC107",

    # Circulation - Light gray
    SpaceType.STAIR: "#CFD8DC",
    SpaceType.ELEVATOR: "#B0BEC5",
    SpaceType.RAMP: "#ECEFF1",
}


@dataclass
class Point:
    """A 2D point."""
    x: float
    y: float

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Point':
        return Point(self.x * scalar, self.y * scalar)

    def tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Rect:
    """A rectangle defined by position and size."""
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def area(self) -> float:
        return self.width * self.height

    def contains(self, point: Point) -> bool:
        return (self.left <= point.x <= self.right and
                self.top <= point.y <= self.bottom)

    def intersects(self, other: 'Rect') -> bool:
        return not (self.right < other.left or
                   self.left > other.right or
                   self.bottom < other.top or
                   self.top > other.bottom)

    def tuple(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def corners(self) -> List[Point]:
        return [
            Point(self.x, self.y),
            Point(self.x + self.width, self.y),
            Point(self.x + self.width, self.y + self.height),
            Point(self.x, self.y + self.height),
        ]


@dataclass
class Wall:
    """A wall segment."""
    start: Point
    end: Point
    thickness: float = 0.3  # meters
    exterior: bool = False

    @property
    def length(self) -> float:
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return (dx ** 2 + dy ** 2) ** 0.5


@dataclass
class Door:
    """A door opening."""
    position: Point
    width: float = 0.9  # meters
    wall: Optional[Wall] = None
    double: bool = False
    label: str = ""


@dataclass
class Window:
    """A window opening."""
    position: Point
    width: float = 1.2  # meters
    height: float = 1.5  # meters
    wall: Optional[Wall] = None


@dataclass
class Furniture:
    """A furniture item."""
    name: str
    bounds: Rect
    rotation: float = 0  # degrees
    color: str = "#8B4513"


@dataclass
class Space:
    """
    An architectural space (room).

    Spaces are the primary unit of design.
    Each space has a type, bounds, and optional subdivisions.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    space_type: SpaceType = SpaceType.OFFICE
    bounds: Rect = field(default_factory=lambda: Rect(0, 0, 5, 5))

    # Optional
    label: str = ""
    capacity: int = 0

    # Sub-elements
    doors: List[Door] = field(default_factory=list)
    windows: List[Window] = field(default_factory=list)
    furniture: List[Furniture] = field(default_factory=list)

    # Styling
    color_override: Optional[str] = None

    @property
    def area(self) -> float:
        """Area in square meters."""
        return self.bounds.area

    @property
    def color(self) -> str:
        """Get the color for this space."""
        if self.color_override:
            return self.color_override
        return SPACE_COLORS.get(self.space_type, "#CCCCCC")

    @property
    def display_name(self) -> str:
        """Name to display on floor plan."""
        if self.label:
            return self.label
        if self.name:
            return self.name
        return self.space_type.value.replace("_", " ").title()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.space_type.value,
            "bounds": {
                "x": self.bounds.x,
                "y": self.bounds.y,
                "width": self.bounds.width,
                "height": self.bounds.height,
            },
            "area": self.area,
            "label": self.label,
        }


@dataclass
class Zone:
    """
    A zone groups multiple spaces under a functional category.

    Zones help organize the floor plan into logical areas.
    """

    name: str
    spaces: List[Space] = field(default_factory=list)
    color: Optional[str] = None

    @property
    def total_area(self) -> float:
        return sum(s.area for s in self.spaces)

    def add_space(self, space: Space) -> None:
        self.spaces.append(space)


@dataclass
class Level:
    """
    A building level (floor).

    Each level contains spaces, walls, and circulation elements.
    Levels are stacked vertically in a building.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "Level 1"
    elevation: float = 0.0  # meters above ground
    height: float = 4.0  # floor-to-floor height

    # Building footprint
    bounds: Rect = field(default_factory=lambda: Rect(0, 0, 50, 50))

    # Contents
    spaces: List[Space] = field(default_factory=list)
    zones: List[Zone] = field(default_factory=list)
    walls: List[Wall] = field(default_factory=list)

    # Metadata
    is_basement: bool = False
    is_roof: bool = False

    @property
    def total_area(self) -> float:
        return sum(s.area for s in self.spaces)

    @property
    def gross_area(self) -> float:
        return self.bounds.area

    @property
    def efficiency(self) -> float:
        """Net to gross ratio."""
        if self.gross_area == 0:
            return 0
        return self.total_area / self.gross_area

    def add_space(self, space: Space) -> Space:
        """Add a space to this level."""
        self.spaces.append(space)
        return space

    def add_zone(self, zone: Zone) -> Zone:
        """Add a zone to this level."""
        self.zones.append(zone)
        return zone

    def get_space(self, name: str) -> Optional[Space]:
        """Find a space by name."""
        for space in self.spaces:
            if space.name == name:
                return space
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "elevation": self.elevation,
            "height": self.height,
            "bounds": {
                "x": self.bounds.x,
                "y": self.bounds.y,
                "width": self.bounds.width,
                "height": self.bounds.height,
            },
            "spaces": [s.to_dict() for s in self.spaces],
            "total_area": self.total_area,
            "gross_area": self.gross_area,
            "efficiency": self.efficiency,
        }


@dataclass
class Building:
    """
    A complete building design.

    Buildings contain multiple levels stacked vertically.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "New Building"

    # Location
    address: str = ""
    site_area: float = 0.0  # square meters

    # Levels
    levels: List[Level] = field(default_factory=list)

    # Site elements
    site_spaces: List[Space] = field(default_factory=list)  # Outdoor spaces

    # Metadata
    architect: str = ""
    client: str = ""
    date: str = ""

    @property
    def total_area(self) -> float:
        """Total floor area across all levels."""
        return sum(level.total_area for level in self.levels)

    @property
    def gross_area(self) -> float:
        """Gross floor area across all levels."""
        return sum(level.gross_area for level in self.levels)

    @property
    def num_levels(self) -> int:
        return len(self.levels)

    def add_level(self, level: Level) -> Level:
        """Add a level to the building."""
        self.levels.append(level)
        return level

    def get_level(self, name: str) -> Optional[Level]:
        """Find a level by name."""
        for level in self.levels:
            if level.name == name:
                return level
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "levels": [l.to_dict() for l in self.levels],
            "total_area": self.total_area,
            "gross_area": self.gross_area,
            "num_levels": self.num_levels,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        """Print building summary."""
        lines = [
            f"",
            f"╔{'═'*50}╗",
            f"║  {self.name:^46}  ║",
            f"╠{'═'*50}╣",
            f"║  Levels: {self.num_levels:<39} ║",
            f"║  Gross Area: {self.gross_area:,.0f} m²{' '*(27-len(f'{self.gross_area:,.0f}'))} ║",
            f"║  Net Area: {self.total_area:,.0f} m²{' '*(29-len(f'{self.total_area:,.0f}'))} ║",
            f"╠{'═'*50}╣",
        ]

        for level in self.levels:
            lines.append(f"║  {level.name:<20} {level.total_area:>8,.0f} m² ({level.efficiency:.0%}) ║")

        lines.append(f"╚{'═'*50}╝")
        lines.append("")

        return "\n".join(lines)


# Convenience builders

def space(
    name: str,
    space_type: SpaceType,
    x: float,
    y: float,
    width: float,
    height: float,
    **kwargs
) -> Space:
    """Quick space builder."""
    return Space(
        name=name,
        space_type=space_type,
        bounds=Rect(x, y, width, height),
        **kwargs
    )


def level(
    name: str,
    width: float,
    height: float,
    elevation: float = 0,
    **kwargs
) -> Level:
    """Quick level builder."""
    return Level(
        name=name,
        bounds=Rect(0, 0, width, height),
        elevation=elevation,
        **kwargs
    )


def building(name: str, **kwargs) -> Building:
    """Quick building builder."""
    return Building(name=name, **kwargs)
