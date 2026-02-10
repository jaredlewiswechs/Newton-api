"""GUI kernel primitives (lightweight implementations)"""
from .nsbezier import NSBezierPath, NSPoint, NSColor
from .colorspace import NSColorSpace
from .gradient import NSGradient
from .shadow import NSShadow

__all__ = ["NSBezierPath", "NSPoint", "NSColor", "NSColorSpace", "NSGradient", "NSShadow"]
