"""NSFont, NSFontDescriptor, NSFontManager — font selection and metrics."""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class NSFontTraitMask:
    BOLD = 1 << 1
    ITALIC = 1 << 0
    CONDENSED = 1 << 6
    EXPANDED = 1 << 5
    MONOSPACE = 1 << 10


@dataclass
class NSFontDescriptor:
    """Describes a font by its attributes."""
    family: str = "Helvetica"
    size: float = 12.0
    traits: int = 0
    weight: float = 0.0  # -1.0 to 1.0, 0 = regular

    def font_descriptor_with_face(self, face: str) -> NSFontDescriptor:
        d = NSFontDescriptor(family=self.family, size=self.size, traits=self.traits, weight=self.weight)
        return d

    def font_descriptor_with_size(self, size: float) -> NSFontDescriptor:
        return NSFontDescriptor(family=self.family, size=size, traits=self.traits, weight=self.weight)

    def font_descriptor_with_symbolic_traits(self, traits: int) -> NSFontDescriptor:
        return NSFontDescriptor(family=self.family, size=self.size, traits=traits, weight=self.weight)


class NSFont:
    """Represents a font with family, size, and traits."""

    def __init__(self, name: str = "Helvetica", size: float = 12.0):
        self._name = name
        self._size = size
        self._descriptor = NSFontDescriptor(family=name, size=size)
        # approximate metrics (based on typical font metrics)
        self._ascender = size * 0.8
        self._descender = size * -0.2
        self._leading = size * 0.1
        self._cap_height = size * 0.7
        self._x_height = size * 0.5

    @property
    def font_name(self) -> str:
        return self._name

    @property
    def point_size(self) -> float:
        return self._size

    @property
    def display_name(self) -> str:
        return self._name

    @property
    def family_name(self) -> str:
        return self._descriptor.family

    @property
    def font_descriptor(self) -> NSFontDescriptor:
        return self._descriptor

    @property
    def ascender(self) -> float:
        return self._ascender

    @property
    def descender(self) -> float:
        return self._descender

    @property
    def leading(self) -> float:
        return self._leading

    @property
    def cap_height(self) -> float:
        return self._cap_height

    @property
    def x_height(self) -> float:
        return self._x_height

    @property
    def line_height(self) -> float:
        return self._ascender - self._descender + self._leading

    def advancement_for_glyph(self, glyph: str) -> float:
        """Approximate character width (monospace assumption for simplicity)."""
        return self._size * 0.6

    def bounding_rect_for_glyph(self, glyph: str):
        """Return (x, y, width, height) bounding rect for a glyph."""
        return (0, self._descender, self._size * 0.6, self._ascender - self._descender)

    # ── factory methods ───────────────────────────────────────────

    @classmethod
    def system_font(cls, size: float = 13.0) -> NSFont:
        return cls("System", size)

    @classmethod
    def bold_system_font(cls, size: float = 13.0) -> NSFont:
        f = cls("System Bold", size)
        f._descriptor = NSFontDescriptor(family="System", size=size, traits=NSFontTraitMask.BOLD, weight=0.4)
        return f

    @classmethod
    def user_font(cls, size: float = 13.0) -> NSFont:
        return cls("Helvetica", size)

    @classmethod
    def user_fixed_pitch_font(cls, size: float = 13.0) -> NSFont:
        f = cls("Menlo", size)
        f._descriptor = NSFontDescriptor(family="Menlo", size=size, traits=NSFontTraitMask.MONOSPACE)
        return f

    @classmethod
    def label_font(cls, size: float = 10.0) -> NSFont:
        return cls("System", size)

    @classmethod
    def message_font(cls, size: float = 13.0) -> NSFont:
        return cls("System", size)

    @classmethod
    def title_bar_font(cls, size: float = 13.0) -> NSFont:
        return cls("System", size)

    @classmethod
    def menu_font(cls, size: float = 14.0) -> NSFont:
        return cls("System", size)

    def font_with_size(self, size: float) -> NSFont:
        return NSFont(self._name, size)

    def __repr__(self):
        return f"<NSFont {self._name!r} {self._size}pt>"

    def to_svg_attrs(self) -> str:
        """Return SVG font attributes for text elements."""
        return f'font-family="{self._descriptor.family}" font-size="{self._size}"'


class NSFontManager:
    """Manages available fonts (simplified)."""

    _shared: Optional[NSFontManager] = None

    def __init__(self):
        self._available_fonts = [
            "Helvetica", "Helvetica-Bold", "Times-Roman", "Courier",
            "Menlo", "System", "System Bold",
        ]

    @classmethod
    def shared(cls) -> NSFontManager:
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    @property
    def available_fonts(self) -> List[str]:
        return list(self._available_fonts)

    def font_with_family(self, family: str, traits: int = 0, weight: int = 5,
                         size: float = 12.0) -> NSFont:
        return NSFont(family, size)

    def convert_font(self, font: NSFont, to_have_trait: int) -> NSFont:
        name = font.font_name
        if to_have_trait & NSFontTraitMask.BOLD:
            name = name + " Bold"
        return NSFont(name, font.point_size)
