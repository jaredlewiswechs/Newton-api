"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN BÉZIER — Visual Connection Language
═══════════════════════════════════════════════════════════════════════════════

Every relationship in Nina Desktop is a Bézier curve.

    source ──────────╮
                     │
                     ╰──────────► target

Curves can be:
- Linear (straight line)
- Quadratic (one control point)
- Cubic (two control points, the classic Bézier)

The curve shape encodes relationship semantics:
- Tight curves = strong dependency
- Loose curves = weak association
- Color/dash = relationship type

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import math
import hashlib
import json


# ═══════════════════════════════════════════════════════════════════════════════
# POINT TYPE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Point:
    """2D point in Foghorn coordinate space."""
    x: float
    y: float
    
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Point':
        return Point(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Point':
        return self * scalar
    
    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point."""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)
    
    def lerp(self, other: 'Point', t: float) -> 'Point':
        """Linear interpolation to another point."""
        return Point(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Point':
        return cls(d["x"], d["y"])
    
    @classmethod
    def origin(cls) -> 'Point':
        return cls(0.0, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# CURVE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class CurveType(Enum):
    """Type of Bézier curve."""
    LINEAR = "linear"           # Straight line (P0 to P3)
    QUADRATIC = "quadratic"     # One control point (P0, P1, P3)
    CUBIC = "cubic"             # Two control points (P0, P1, P2, P3)


class RelationshipStyle(Enum):
    """Visual style for relationship curves."""
    SOLID = "solid"             # Strong connection
    DASHED = "dashed"           # Weak connection
    DOTTED = "dotted"           # Tentative connection
    DOUBLE = "double"           # Bidirectional


# ═══════════════════════════════════════════════════════════════════════════════
# BÉZIER CURVE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BezierCurve:
    """
    Bézier curve representing a relationship between objects.
    
    Uses cubic Bézier by default (two control points).
    
    P0 ────────────────────── P3
         ╰── P1          P2 ──╯
    
    t=0 at P0, t=1 at P3
    """
    start: Point                    # P0: Source anchor
    end: Point                      # P3: Target anchor  
    control1: Optional[Point] = None  # P1: First control point
    control2: Optional[Point] = None  # P2: Second control point
    
    # Metadata
    source_hash: str = ""
    target_hash: str = ""
    relationship: str = "links_to"
    style: RelationshipStyle = RelationshipStyle.SOLID
    color: str = "#666666"
    width: float = 2.0
    
    def __post_init__(self):
        """Auto-generate control points if not provided."""
        if self.control1 is None or self.control2 is None:
            self._auto_control_points()
    
    def _auto_control_points(self):
        """Generate smooth control points automatically."""
        # Distance between endpoints
        dist = self.start.distance_to(self.end)
        
        # Direction vector
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        
        # Perpendicular offset for aesthetic curves
        # Control points are offset perpendicular to the line
        offset = dist * 0.25
        
        # If mostly horizontal, use vertical control offsets
        if abs(dx) > abs(dy):
            self.control1 = Point(
                self.start.x + dx * 0.33,
                self.start.y
            )
            self.control2 = Point(
                self.end.x - dx * 0.33,
                self.end.y
            )
        else:
            # Mostly vertical, use horizontal control offsets
            self.control1 = Point(
                self.start.x,
                self.start.y + dy * 0.33
            )
            self.control2 = Point(
                self.end.x,
                self.end.y - dy * 0.33
            )
    
    @property
    def curve_type(self) -> CurveType:
        """Determine curve type from control points."""
        if self.control1 is None and self.control2 is None:
            return CurveType.LINEAR
        elif self.control2 is None:
            return CurveType.QUADRATIC
        else:
            return CurveType.CUBIC
    
    def point_at(self, t: float) -> Point:
        """
        Get point on curve at parameter t (0 to 1).
        
        Uses De Casteljau's algorithm for numerical stability.
        """
        t = max(0.0, min(1.0, t))  # Clamp to [0, 1]
        
        if self.curve_type == CurveType.LINEAR:
            return self.start.lerp(self.end, t)
        
        elif self.curve_type == CurveType.QUADRATIC:
            # Quadratic: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P3
            p0, p1, p3 = self.start, self.control1, self.end
            u = 1 - t
            return u * u * p0 + 2 * u * t * p1 + t * t * p3
        
        else:
            # Cubic: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
            p0, p1, p2, p3 = self.start, self.control1, self.control2, self.end
            u = 1 - t
            return (u * u * u * p0 + 
                    3 * u * u * t * p1 + 
                    3 * u * t * t * p2 + 
                    t * t * t * p3)
    
    def tangent_at(self, t: float) -> Point:
        """
        Get tangent vector at parameter t.
        
        Useful for arrows and labels.
        """
        t = max(0.0, min(1.0, t))
        
        if self.curve_type == CurveType.LINEAR:
            return self.end - self.start
        
        elif self.curve_type == CurveType.QUADRATIC:
            p0, p1, p3 = self.start, self.control1, self.end
            u = 1 - t
            # Derivative: B'(t) = 2(1-t)(P1-P0) + 2t(P3-P1)
            return 2 * u * (p1 - p0) + 2 * t * (p3 - p1)
        
        else:
            p0, p1, p2, p3 = self.start, self.control1, self.control2, self.end
            u = 1 - t
            # Derivative: B'(t) = 3(1-t)²(P1-P0) + 6(1-t)t(P2-P1) + 3t²(P3-P2)
            return (3 * u * u * (p1 - p0) + 
                    6 * u * t * (p2 - p1) + 
                    3 * t * t * (p3 - p2))
    
    def sample(self, segments: int = 32) -> List[Point]:
        """
        Sample curve into a polyline.
        
        Returns list of points for rendering.
        """
        return [self.point_at(t / segments) for t in range(segments + 1)]
    
    def length(self, samples: int = 64) -> float:
        """
        Approximate arc length of curve.
        
        Uses sampling for speed (analytical is complex for cubic).
        """
        points = self.sample(samples)
        total = 0.0
        for i in range(len(points) - 1):
            total += points[i].distance_to(points[i + 1])
        return total
    
    def midpoint(self) -> Point:
        """Get the midpoint of the curve (t=0.5)."""
        return self.point_at(0.5)
    
    def bbox(self, samples: int = 32) -> Tuple[Point, Point]:
        """
        Get bounding box of curve.
        
        Returns (min_point, max_point).
        """
        points = self.sample(samples)
        
        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        
        return Point(min_x, min_y), Point(max_x, max_y)
    
    def to_svg_path(self) -> str:
        """
        Convert to SVG path string.
        
        M = move to
        L = line to
        Q = quadratic curve
        C = cubic curve
        """
        if self.curve_type == CurveType.LINEAR:
            return f"M {self.start.x} {self.start.y} L {self.end.x} {self.end.y}"
        
        elif self.curve_type == CurveType.QUADRATIC:
            return (f"M {self.start.x} {self.start.y} "
                   f"Q {self.control1.x} {self.control1.y} "
                   f"{self.end.x} {self.end.y}")
        
        else:
            return (f"M {self.start.x} {self.start.y} "
                   f"C {self.control1.x} {self.control1.y} "
                   f"{self.control2.x} {self.control2.y} "
                   f"{self.end.x} {self.end.y}")
    
    def hash(self) -> str:
        """Deterministic hash for this curve."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "control1": self.control1.to_dict() if self.control1 else None,
            "control2": self.control2.to_dict() if self.control2 else None,
            "source_hash": self.source_hash,
            "target_hash": self.target_hash,
            "relationship": self.relationship,
            "style": self.style.value,
            "color": self.color,
            "width": self.width,
            "curve_type": self.curve_type.value,
            "svg_path": self.to_svg_path(),
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'BezierCurve':
        """Deserialize from dictionary."""
        return cls(
            start=Point.from_dict(d["start"]),
            end=Point.from_dict(d["end"]),
            control1=Point.from_dict(d["control1"]) if d.get("control1") else None,
            control2=Point.from_dict(d["control2"]) if d.get("control2") else None,
            source_hash=d.get("source_hash", ""),
            target_hash=d.get("target_hash", ""),
            relationship=d.get("relationship", "links_to"),
            style=RelationshipStyle(d.get("style", "solid")),
            color=d.get("color", "#666666"),
            width=d.get("width", 2.0),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CURVE FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

class CurveFactory:
    """
    Factory for creating Bézier curves with semantic meaning.
    
    Different relationship types get different curve styles.
    """
    
    # Relationship → Style mapping
    STYLE_MAP = {
        "links_to": (RelationshipStyle.SOLID, "#666666"),
        "references": (RelationshipStyle.SOLID, "#3366cc"),
        "depends_on": (RelationshipStyle.SOLID, "#cc3366"),
        "derived_from": (RelationshipStyle.DASHED, "#33cc66"),
        "cites": (RelationshipStyle.DOTTED, "#cccc33"),
        "related_to": (RelationshipStyle.DASHED, "#999999"),
        "precedes": (RelationshipStyle.SOLID, "#6633cc"),
        "follows": (RelationshipStyle.SOLID, "#cc6633"),
    }
    
    @classmethod
    def create(
        cls,
        start: Point,
        end: Point,
        source_hash: str = "",
        target_hash: str = "",
        relationship: str = "links_to",
    ) -> BezierCurve:
        """
        Create a curve with appropriate styling for the relationship.
        """
        style, color = cls.STYLE_MAP.get(
            relationship, 
            (RelationshipStyle.SOLID, "#666666")
        )
        
        return BezierCurve(
            start=start,
            end=end,
            source_hash=source_hash,
            target_hash=target_hash,
            relationship=relationship,
            style=style,
            color=color,
        )
    
    @classmethod
    def create_from_objects(
        cls,
        source_pos: Tuple[float, float],
        target_pos: Tuple[float, float],
        source_hash: str,
        target_hash: str,
        relationship: str = "links_to",
    ) -> BezierCurve:
        """
        Create a curve between two object positions.
        """
        return cls.create(
            start=Point(*source_pos),
            end=Point(*target_pos),
            source_hash=source_hash,
            target_hash=target_hash,
            relationship=relationship,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CURVE STORE
# ═══════════════════════════════════════════════════════════════════════════════

class CurveStore:
    """
    In-memory store for Bézier curves.
    
    Indexed by source and target for fast lookup.
    """
    
    def __init__(self):
        self._curves: Dict[str, BezierCurve] = {}  # hash → curve
        self._by_source: Dict[str, List[str]] = {}  # source_hash → [curve_hashes]
        self._by_target: Dict[str, List[str]] = {}  # target_hash → [curve_hashes]
    
    def add(self, curve: BezierCurve) -> str:
        """Add a curve, return its hash."""
        h = curve.hash()
        self._curves[h] = curve
        
        # Index by source
        if curve.source_hash:
            if curve.source_hash not in self._by_source:
                self._by_source[curve.source_hash] = []
            self._by_source[curve.source_hash].append(h)
        
        # Index by target
        if curve.target_hash:
            if curve.target_hash not in self._by_target:
                self._by_target[curve.target_hash] = []
            self._by_target[curve.target_hash].append(h)
        
        return h
    
    def get(self, hash: str) -> Optional[BezierCurve]:
        """Get curve by hash."""
        return self._curves.get(hash)
    
    def get_from_source(self, source_hash: str) -> List[BezierCurve]:
        """Get all curves originating from a source."""
        hashes = self._by_source.get(source_hash, [])
        return [self._curves[h] for h in hashes if h in self._curves]
    
    def get_to_target(self, target_hash: str) -> List[BezierCurve]:
        """Get all curves pointing to a target."""
        hashes = self._by_target.get(target_hash, [])
        return [self._curves[h] for h in hashes if h in self._curves]
    
    def get_all(self) -> List[BezierCurve]:
        """Get all curves."""
        return list(self._curves.values())
    
    def delete(self, hash: str) -> bool:
        """Delete a curve."""
        curve = self._curves.get(hash)
        if not curve:
            return False
        
        # Remove from indices
        if curve.source_hash in self._by_source:
            self._by_source[curve.source_hash] = [
                h for h in self._by_source[curve.source_hash] if h != hash
            ]
        if curve.target_hash in self._by_target:
            self._by_target[curve.target_hash] = [
                h for h in self._by_target[curve.target_hash] if h != hash
            ]
        
        del self._curves[hash]
        return True
    
    def count(self) -> int:
        """Total curves."""
        return len(self._curves)
    
    def export(self) -> List[Dict]:
        """Export all curves as dictionaries."""
        return [c.to_dict() for c in self._curves.values()]


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL STORE
# ═══════════════════════════════════════════════════════════════════════════════

_curve_store: Optional[CurveStore] = None


def get_curve_store() -> CurveStore:
    """Get the global curve store."""
    global _curve_store
    if _curve_store is None:
        _curve_store = CurveStore()
    return _curve_store


# ═══════════════════════════════════════════════════════════════════════════════
# SVG RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def render_curves_svg(curves: List[BezierCurve], width: int = 800, height: int = 600) -> str:
    """
    Render a list of curves as an SVG string.
    
    This can be displayed in a browser or UI component.
    """
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    ]
    
    # Define dash patterns
    svg_parts.append("""
    <defs>
        <pattern id="dash" patternUnits="userSpaceOnUse" width="10" height="1">
            <line x1="0" y1="0" x2="5" y2="0" stroke="black" stroke-width="1"/>
        </pattern>
    </defs>
    """)
    
    for curve in curves:
        # Determine stroke-dasharray based on style
        dash = ""
        if curve.style == RelationshipStyle.DASHED:
            dash = ' stroke-dasharray="10,5"'
        elif curve.style == RelationshipStyle.DOTTED:
            dash = ' stroke-dasharray="2,3"'
        
        svg_parts.append(
            f'<path d="{curve.to_svg_path()}" '
            f'fill="none" stroke="{curve.color}" '
            f'stroke-width="{curve.width}"{dash}/>'
        )
        
        # Add arrowhead at end
        end = curve.end
        tangent = curve.tangent_at(1.0)
        angle = math.atan2(tangent.y, tangent.x)
        
        # Arrowhead size
        arrow_size = 8
        a1 = Point(
            end.x - arrow_size * math.cos(angle - 0.4),
            end.y - arrow_size * math.sin(angle - 0.4)
        )
        a2 = Point(
            end.x - arrow_size * math.cos(angle + 0.4),
            end.y - arrow_size * math.sin(angle + 0.4)
        )
        
        svg_parts.append(
            f'<polygon points="{end.x},{end.y} {a1.x},{a1.y} {a2.x},{a2.y}" '
            f'fill="{curve.color}"/>'
        )
    
    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)
