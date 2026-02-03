"""
═══════════════════════════════════════════════════════════════
SHAPES - SQUIRCLE GEOMETRY
"Squares and circles suck" - Newton OS Philosophy
Everything is a continuous curve.
═══════════════════════════════════════════════════════════════
"""

from typing import Tuple, Optional
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPainterPath, QColor, QPen, QBrush, QPainter
import math


def superellipse_point(cx: float, cy: float, 
                       rx: float, ry: float,
                       n: float, theta: float) -> Tuple[float, float]:
    """
    Calculate a point on a superellipse (Lamé curve).
    
    |x/rx|^n + |y/ry|^n = 1
    
    Args:
        cx, cy: Center point
        rx, ry: Radii in x and y directions
        n: Exponent (2 = ellipse, 4+ = squircle, ∞ = rectangle)
        theta: Angle in radians
    
    Returns:
        (x, y) point on the curve
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    # Handle the exponent for continuous curve
    exp = 2.0 / n
    
    x = cx + rx * math.copysign(abs(cos_t) ** exp, cos_t)
    y = cy + ry * math.copysign(abs(sin_t) ** exp, sin_t)
    
    return (x, y)


def squircle_path(rect: QRectF, 
                  n: float = 4.0,
                  segments: int = 64) -> QPainterPath:
    """
    Create a QPainterPath for a squircle (superellipse).
    
    Args:
        rect: Bounding rectangle
        n: Squircle exponent (4 is classic iOS-style)
        segments: Number of line segments (more = smoother)
    
    Returns:
        QPainterPath representing the squircle
    """
    path = QPainterPath()
    
    cx = rect.center().x()
    cy = rect.center().y()
    rx = rect.width() / 2
    ry = rect.height() / 2
    
    # Generate points around the curve
    points = []
    for i in range(segments):
        theta = (2 * math.pi * i) / segments
        x, y = superellipse_point(cx, cy, rx, ry, n, theta)
        points.append(QPointF(x, y))
    
    # Build path
    if points:
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.closeSubpath()
    
    return path


def rounded_squircle_path(rect: QRectF,
                          corner_radius: float,
                          n: float = 4.0,
                          segments_per_corner: int = 16) -> QPainterPath:
    """
    Create a squircle with specified corner radius.
    Like CSS border-radius but with continuous curvature.
    
    Args:
        rect: Bounding rectangle
        corner_radius: Radius of corners
        n: Squircle exponent
        segments_per_corner: Smoothness of each corner
    
    Returns:
        QPainterPath with squircle corners
    """
    path = QPainterPath()
    
    x = rect.x()
    y = rect.y()
    w = rect.width()
    h = rect.height()
    r = min(corner_radius, w / 2, h / 2)
    
    # If radius is too small, just use regular rounded rect
    if r < 2:
        path.addRoundedRect(rect, r, r)
        return path
    
    # Start at top-left, after corner
    path.moveTo(x + r, y)
    
    # Top edge
    path.lineTo(x + w - r, y)
    
    # Top-right corner (squircle arc)
    _add_squircle_corner(path, x + w - r, y, r, r, n, 
                         -math.pi/2, 0, segments_per_corner)
    
    # Right edge  
    path.lineTo(x + w, y + h - r)
    
    # Bottom-right corner
    _add_squircle_corner(path, x + w - r, y + h - r, r, r, n,
                         0, math.pi/2, segments_per_corner)
    
    # Bottom edge
    path.lineTo(x + r, y + h)
    
    # Bottom-left corner
    _add_squircle_corner(path, x + r, y + h - r, r, r, n,
                         math.pi/2, math.pi, segments_per_corner)
    
    # Left edge
    path.lineTo(x, y + r)
    
    # Top-left corner
    _add_squircle_corner(path, x + r, y + r, r, r, n,
                         math.pi, 3*math.pi/2, segments_per_corner)
    
    path.closeSubpath()
    return path


def _add_squircle_corner(path: QPainterPath,
                         cx: float, cy: float,
                         rx: float, ry: float,
                         n: float,
                         start_angle: float,
                         end_angle: float,
                         segments: int) -> None:
    """Add a squircle corner arc to a path."""
    for i in range(1, segments + 1):
        t = i / segments
        theta = start_angle + t * (end_angle - start_angle)
        x, y = superellipse_point(cx, cy, rx, ry, n, theta)
        path.lineTo(x, y)


class Squircle:
    """
    A drawable squircle with fill and stroke.
    
    The visual foundation of Newton OS UI.
    """
    
    def __init__(self,
                 rect: QRectF,
                 n: float = 4.0,
                 fill_color: Optional[QColor] = None,
                 stroke_color: Optional[QColor] = None,
                 stroke_width: float = 1.0,
                 corner_radius: Optional[float] = None):
        self.rect = rect
        self.n = n
        self.fill_color = fill_color or QColor(255, 255, 255)
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.corner_radius = corner_radius
        
        self._path: Optional[QPainterPath] = None
        self._rebuild_path()
    
    def _rebuild_path(self) -> None:
        """Rebuild the path when geometry changes."""
        if self.corner_radius is not None:
            self._path = rounded_squircle_path(
                self.rect, self.corner_radius, self.n
            )
        else:
            self._path = squircle_path(self.rect, self.n)
    
    def set_rect(self, rect: QRectF) -> None:
        """Update the bounding rectangle."""
        self.rect = rect
        self._rebuild_path()
    
    def set_n(self, n: float) -> None:
        """Update the squircle exponent."""
        self.n = n
        self._rebuild_path()
    
    def path(self) -> QPainterPath:
        """Get the QPainterPath."""
        if self._path is None:
            self._rebuild_path()
        return self._path
    
    def contains(self, point: QPointF) -> bool:
        """Check if point is inside the squircle."""
        return self.path().contains(point)
    
    def draw(self, painter: QPainter) -> None:
        """Draw the squircle."""
        painter.save()
        
        # Fill
        if self.fill_color:
            painter.setBrush(QBrush(self.fill_color))
        else:
            painter.setBrush(QBrush())
        
        # Stroke
        if self.stroke_color:
            painter.setPen(QPen(self.stroke_color, self.stroke_width))
        else:
            painter.setPen(QPen(QColor(0, 0, 0, 0)))
        
        painter.drawPath(self.path())
        painter.restore()


# ═══════════════════════════════════════════════════════════════
# PRESET SHAPES
# ═══════════════════════════════════════════════════════════════

def window_shape(rect: QRectF) -> QPainterPath:
    """Standard Newton OS window shape."""
    return rounded_squircle_path(rect, corner_radius=12, n=4.0)


def button_shape(rect: QRectF) -> QPainterPath:
    """Standard button shape - softer squircle."""
    return rounded_squircle_path(rect, corner_radius=8, n=4.5)


def icon_shape(rect: QRectF) -> QPainterPath:
    """App icon shape - iOS-style squircle."""
    return squircle_path(rect, n=5.0)


def dock_shape(rect: QRectF) -> QPainterPath:
    """Dock background shape."""
    return rounded_squircle_path(rect, corner_radius=16, n=4.0)
