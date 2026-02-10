"""NSScreen — describes a display attached to the system."""
from __future__ import annotations
from typing import List, Optional

from Kernel.view.nsview import NSRect


class NSScreen:
    """Represents a physical display. In headless mode a single virtual screen is provided."""

    _screens: List[NSScreen] = []

    def __init__(self, frame: Optional[NSRect] = None, visible_frame: Optional[NSRect] = None,
                 backing_scale_factor: float = 2.0):
        self._frame = frame or NSRect(0, 0, 1920, 1080)
        self._visible_frame = visible_frame or NSRect(0, 25, 1920, 1055)
        self._backing_scale_factor = backing_scale_factor
        self._depth = 24
        self._localized_name = "Built-in Display"

    @property
    def frame(self) -> NSRect:
        return self._frame

    @property
    def visible_frame(self) -> NSRect:
        return self._visible_frame

    @property
    def backing_scale_factor(self) -> float:
        return self._backing_scale_factor

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def localized_name(self) -> str:
        return self._localized_name

    @classmethod
    def main_screen(cls) -> NSScreen:
        if not cls._screens:
            cls._screens.append(NSScreen())
        return cls._screens[0]

    @classmethod
    def screens(cls) -> List[NSScreen]:
        if not cls._screens:
            cls._screens.append(NSScreen())
        return list(cls._screens)

    def __repr__(self):
        return (f"<NSScreen {self._localized_name!r} "
                f"{self._frame.width}x{self._frame.height} @{self._backing_scale_factor}x>")
