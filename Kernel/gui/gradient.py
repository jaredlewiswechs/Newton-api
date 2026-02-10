"""Basic NSGradient implementation that can serialize to SVG gradient defs."""
from typing import List, Optional
from .nsbezier import NSColor

class NSGradient:
    def __init__(self, colors: List[NSColor], locations: Optional[List[float]] = None):
        if locations and len(locations) != len(colors):
            raise ValueError('colors and locations length mismatch')
        self.colors = list(colors)
        if locations:
            self.locations = list(locations)
        else:
            # distribute evenly
            n = len(colors)
            self.locations = [i/(n-1) if n>1 else 0.0 for i in range(n)]

    def to_svg_def(self, id: str = 'g1', linear: bool = True, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 0, cx: float = 50, cy: float = 50, r: float = 50) -> str:
        """Return an SVG gradient definition string.

        For linear gradients, uses x1,y1,x2,y2. For radial, uses cx,cy,r.
        """
        stops = []
        for loc, col in zip(self.locations, self.colors):
            offset = f"{loc*100}%"
            stop_color = col.to_rgba()
            stops.append(f'<stop offset="{offset}" stop-color="{stop_color}" />')
        stops_str = '\n    '.join(stops)
        if linear:
            return f'<linearGradient id="{id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">\n    {stops_str}\n  </linearGradient>'
        else:
            return f'<radialGradient id="{id}" cx="{cx}" cy="{cy}" r="{r}">\n    {stops_str}\n  </radialGradient>'

    # convenience factory
    @classmethod
    def gradient_with_start_and_end_color(cls, start: NSColor, end: NSColor):
        return cls([start, end], [0.0, 1.0])
