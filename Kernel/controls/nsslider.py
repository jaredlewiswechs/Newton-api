"""NSSlider — a continuous or discrete slider control."""
from __future__ import annotations
from typing import Optional

from .nscontrol import NSControl
from Kernel.view.nsview import NSRect
from Kernel.runtime.event import NSEvent, NSEventType


class NSSlider(NSControl):
    """A slider (horizontal or vertical) that selects a value in a range."""

    def __init__(self, frame: Optional[NSRect] = None, value: float = 0.0,
                 min_value: float = 0.0, max_value: float = 1.0):
        super().__init__(frame)
        self._double_value = value
        self._min_value = min_value
        self._max_value = max_value
        self._number_of_tick_marks = 0
        self._allows_tick_mark_values_only = False
        self._is_vertical: Optional[bool] = None  # auto-detect from frame
        self._tick_mark_position = 0  # 0=below, 1=above
        self._tracking_value = False

    @property
    def double_value(self) -> float:
        return self._double_value

    @double_value.setter
    def double_value(self, v: float):
        self._double_value = max(self._min_value, min(self._max_value, v))
        if self._allows_tick_mark_values_only and self._number_of_tick_marks > 1:
            self._double_value = self.closest_tick_mark_value(self._double_value)

    @property
    def float_value(self) -> float:
        return float(self._double_value)

    @float_value.setter
    def float_value(self, v: float):
        self.double_value = v

    @property
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, v: float):
        self._min_value = v

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, v: float):
        self._max_value = v

    @property
    def number_of_tick_marks(self) -> int:
        return self._number_of_tick_marks

    @number_of_tick_marks.setter
    def number_of_tick_marks(self, v: int):
        self._number_of_tick_marks = v

    @property
    def allows_tick_mark_values_only(self) -> bool:
        return self._allows_tick_mark_values_only

    @allows_tick_mark_values_only.setter
    def allows_tick_mark_values_only(self, v: bool):
        self._allows_tick_mark_values_only = v

    @property
    def is_vertical(self) -> bool:
        if self._is_vertical is not None:
            return self._is_vertical
        return self._frame.height > self._frame.width

    def tick_mark_value_at_index(self, index: int) -> float:
        if self._number_of_tick_marks <= 1:
            return self._min_value
        step = (self._max_value - self._min_value) / (self._number_of_tick_marks - 1)
        return self._min_value + step * index

    def closest_tick_mark_value(self, value: float) -> float:
        if self._number_of_tick_marks <= 1:
            return value
        best = self._min_value
        best_dist = abs(value - best)
        for i in range(self._number_of_tick_marks):
            tv = self.tick_mark_value_at_index(i)
            d = abs(value - tv)
            if d < best_dist:
                best = tv
                best_dist = d
        return best

    def _value_for_position(self, pos: float) -> float:
        if self.is_vertical:
            ratio = pos / self._frame.height if self._frame.height else 0
        else:
            ratio = pos / self._frame.width if self._frame.width else 0
        ratio = max(0.0, min(1.0, ratio))
        return self._min_value + ratio * (self._max_value - self._min_value)

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if not self._is_enabled:
            return False
        self._tracking_value = True
        if event.location:
            pos = event.location[1] if self.is_vertical else event.location[0]
            self.double_value = self._value_for_position(pos)
        if self._is_continuous:
            self.send_action()
        return True

    def handle_mouse_move(self, event: NSEvent) -> bool:
        if not self._tracking_value:
            return False
        if event.location:
            pos = event.location[1] if self.is_vertical else event.location[0]
            self.double_value = self._value_for_position(pos)
        if self._is_continuous:
            self.send_action()
        return True

    def handle_mouse_up(self, event: NSEvent) -> bool:
        if self._tracking_value:
            self._tracking_value = False
            self.send_action()
            return True
        return False

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        parts = []
        if self.is_vertical:
            track_x = w / 2 - 2
            parts.append(f'<rect x="{track_x}" y="0" width="4" height="{h}" '
                         f'fill="#ddd" rx="2" />')
            ratio = (self._double_value - self._min_value) / max(1e-9, self._max_value - self._min_value)
            knob_y = ratio * h
            parts.append(f'<circle cx="{w / 2}" cy="{knob_y}" r="8" '
                         f'fill="white" stroke="#888" stroke-width="1" />')
        else:
            track_y = h / 2 - 2
            parts.append(f'<rect x="0" y="{track_y}" width="{w}" height="4" '
                         f'fill="#ddd" rx="2" />')
            ratio = (self._double_value - self._min_value) / max(1e-9, self._max_value - self._min_value)
            knob_x = ratio * w
            parts.append(f'<circle cx="{knob_x}" cy="{h / 2}" r="8" '
                         f'fill="white" stroke="#888" stroke-width="1" />')
        # tick marks
        if self._number_of_tick_marks > 1:
            for i in range(self._number_of_tick_marks):
                tv = self.tick_mark_value_at_index(i)
                r = (tv - self._min_value) / max(1e-9, self._max_value - self._min_value)
                if self.is_vertical:
                    ty = r * h
                    parts.append(f'<line x1="{w / 2 - 4}" y1="{ty}" '
                                 f'x2="{w / 2 + 4}" y2="{ty}" stroke="#aaa" />')
                else:
                    tx = r * w
                    parts.append(f'<line x1="{tx}" y1="{h / 2 - 4}" '
                                 f'x2="{tx}" y2="{h / 2 + 4}" stroke="#aaa" />')
        return "\n".join(parts)

    def __repr__(self):
        return f"<NSSlider value={self._double_value} range=[{self._min_value},{self._max_value}]>"
