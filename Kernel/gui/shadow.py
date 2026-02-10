"""NSShadow shim with SVG filter output (feDropShadow)"""
from .nsbezier import NSColor

class NSShadow:
    def __init__(self, offset_x: float = 0.0, offset_y: float = 0.0, blur_radius: float = 0.0, color: NSColor = None):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blur_radius = blur_radius
        self.color = color or NSColor(0,0,0,1.0)

    def to_svg_filter(self, id: str = 's1') -> str:
        # feDropShadow params: dx, dy, stdDeviation, flood-color, flood-opacity
        flood_color = f"{self.color.r},{self.color.g},{self.color.b}"
        flood_opacity = f"{self.color.a}"
        stddev = self.blur_radius
        return (
            f'<filter id="{id}" x="-50%" y="-50%" width="200%" height="200%">\n'
            f'    <feDropShadow dx="{self.offset_x}" dy="{self.offset_y}" stdDeviation="{stddev}" flood-color="rgb({flood_color})" flood-opacity="{flood_opacity}" />\n'
            f'  </filter>'
        )
