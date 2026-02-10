"""NSSplitView — a view that arranges subviews side by side with dividers."""
from __future__ import annotations
from typing import Optional, List
from enum import Enum

from .nsview import NSView, NSRect


class NSSplitViewDividerStyle(Enum):
    THICK = 0
    THIN = 1
    PANE_SPLITTER = 2


class NSSplitView(NSView):
    """Arranges subviews horizontally or vertically with draggable dividers."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._is_vertical = True  # True = side-by-side (vertical divider)
        self._divider_style = NSSplitViewDividerStyle.THICK
        self._divider_thickness: float = 8.0
        self._delegate = None
        self._arrangement_subviews: List[NSView] = []

    @property
    def is_vertical(self) -> bool:
        return self._is_vertical

    @is_vertical.setter
    def is_vertical(self, v: bool):
        self._is_vertical = v
        self._layout_arranged()

    @property
    def divider_style(self) -> NSSplitViewDividerStyle:
        return self._divider_style

    @divider_style.setter
    def divider_style(self, v: NSSplitViewDividerStyle):
        self._divider_style = v
        if v == NSSplitViewDividerStyle.THIN:
            self._divider_thickness = 1.0
        else:
            self._divider_thickness = 8.0

    @property
    def divider_thickness(self) -> float:
        return self._divider_thickness

    def add_arranged_subview(self, view: NSView):
        self._arrangement_subviews.append(view)
        self.add_subview(view)
        self._layout_arranged()

    def remove_arranged_subview(self, view: NSView):
        if view in self._arrangement_subviews:
            self._arrangement_subviews.remove(view)
        view.remove_from_superview()
        self._layout_arranged()

    @property
    def arranged_subviews(self) -> List[NSView]:
        return list(self._arrangement_subviews)

    def set_position(self, position: float, divider_index: int):
        """Set the position of a specific divider."""
        if divider_index < 0 or divider_index >= len(self._arrangement_subviews) - 1:
            return
        self._layout_arranged(positions={divider_index: position})

    def _layout_arranged(self, positions: Optional[dict] = None):
        n = len(self._arrangement_subviews)
        if n == 0:
            return
        total_divider = self._divider_thickness * max(0, n - 1)
        if self._is_vertical:
            avail = self._frame.width - total_divider
            each = avail / n if n else 0
            x = 0.0
            for i, sv in enumerate(self._arrangement_subviews):
                w = each
                if positions and i > 0 and (i - 1) in positions:
                    w = positions[i - 1] - x
                sv.frame = NSRect(x, 0, w, self._frame.height)
                x += w + self._divider_thickness
        else:
            avail = self._frame.height - total_divider
            each = avail / n if n else 0
            y = 0.0
            for i, sv in enumerate(self._arrangement_subviews):
                h = each
                if positions and i > 0 and (i - 1) in positions:
                    h = positions[i - 1] - y
                sv.frame = NSRect(0, y, self._frame.width, h)
                y += h + self._divider_thickness

    def draw(self, rect=None) -> str:
        parts = [super().draw(rect)]
        n = len(self._arrangement_subviews)
        for i in range(n - 1):
            sv = self._arrangement_subviews[i]
            if self._is_vertical:
                dx = sv.frame.x + sv.frame.width
                parts.append(
                    f'<rect x="{dx}" y="0" width="{self._divider_thickness}" '
                    f'height="{self._frame.height}" fill="#cccccc" class="divider" />'
                )
            else:
                dy = sv.frame.y + sv.frame.height
                parts.append(
                    f'<rect x="0" y="{dy}" width="{self._frame.width}" '
                    f'height="{self._divider_thickness}" fill="#cccccc" class="divider" />'
                )
        return "\n".join(parts)
