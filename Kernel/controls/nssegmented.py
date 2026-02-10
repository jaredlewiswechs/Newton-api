"""NSSegmentedControl — a horizontal control with multiple segments."""
from __future__ import annotations
from typing import Optional, List

from .nscontrol import NSControl
from Kernel.view.nsview import NSRect
from Kernel.runtime.event import NSEvent


class NSSegmentedControl(NSControl):
    """A segmented button bar."""

    def __init__(self, frame: Optional[NSRect] = None, labels: Optional[List[str]] = None):
        super().__init__(frame)
        self._labels: List[str] = labels or []
        self._selected_segment: int = 0
        self._segment_widths: List[float] = []
        self._segment_enabled: List[bool] = []
        self._tracking_mode = 0  # 0=select_one, 1=select_any, 2=momentary
        self._init_segments()

    def _init_segments(self):
        n = len(self._labels)
        self._segment_widths = [0.0] * n  # 0 = auto
        self._segment_enabled = [True] * n

    @property
    def segment_count(self) -> int:
        return len(self._labels)

    @segment_count.setter
    def segment_count(self, v: int):
        while len(self._labels) < v:
            self._labels.append("")
            self._segment_widths.append(0.0)
            self._segment_enabled.append(True)
        self._labels = self._labels[:v]
        self._segment_widths = self._segment_widths[:v]
        self._segment_enabled = self._segment_enabled[:v]

    @property
    def selected_segment(self) -> int:
        return self._selected_segment

    @selected_segment.setter
    def selected_segment(self, v: int):
        self._selected_segment = v

    def set_label(self, label: str, for_segment: int):
        if 0 <= for_segment < len(self._labels):
            self._labels[for_segment] = label

    def label_for_segment(self, segment: int) -> str:
        if 0 <= segment < len(self._labels):
            return self._labels[segment]
        return ""

    def set_enabled(self, enabled: bool, for_segment: int):
        if 0 <= for_segment < len(self._segment_enabled):
            self._segment_enabled[for_segment] = enabled

    def is_enabled_for_segment(self, segment: int) -> bool:
        if 0 <= segment < len(self._segment_enabled):
            return self._segment_enabled[segment]
        return False

    def set_width(self, width: float, for_segment: int):
        if 0 <= for_segment < len(self._segment_widths):
            self._segment_widths[for_segment] = width

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if not self._is_enabled or not event.location:
            return False
        x = event.location[0]
        n = len(self._labels)
        if n == 0:
            return False
        seg_w = self._frame.width / n
        idx = int(x / seg_w)
        idx = max(0, min(n - 1, idx))
        if self._segment_enabled[idx]:
            self._selected_segment = idx
            self.send_action()
        return True

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        n = len(self._labels)
        if n == 0:
            return ""
        seg_w = w / n
        parts = []
        for i, label in enumerate(self._labels):
            sx = i * seg_w
            fill = "#a0c0ff" if i == self._selected_segment else "#e0e0e0"
            parts.append(f'<rect x="{sx}" y="0" width="{seg_w}" height="{h}" '
                         f'fill="{fill}" stroke="#888" stroke-width="0.5" />')
            parts.append(f'<text x="{sx + seg_w / 2}" y="{h / 2 + 4}" '
                         f'text-anchor="middle" font-size="12" '
                         f'font-family="sans-serif">{label}</text>')
        return "\n".join(parts)
