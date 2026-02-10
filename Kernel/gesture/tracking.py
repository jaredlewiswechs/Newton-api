"""NSTrackingArea — defines a region for mouse-tracking events."""
from __future__ import annotations
from typing import Optional, Any
from enum import IntFlag

from Kernel.view.nsview import NSRect


class NSTrackingAreaOptions(IntFlag):
    MOUSE_ENTERED_AND_EXITED = 1 << 0
    MOUSE_MOVED = 1 << 1
    CURSOR_UPDATE = 1 << 2
    ACTIVE_WHEN_FIRST_RESPONDER = 1 << 4
    ACTIVE_IN_KEY_WINDOW = 1 << 5
    ACTIVE_IN_ACTIVE_APP = 1 << 6
    ACTIVE_ALWAYS = 1 << 7
    ASSUME_INSIDE = 1 << 8
    IN_VISIBLE_RECT = 1 << 9
    ENABLED_DURING_MOUSE_DRAG = 1 << 10


class NSTrackingArea:
    """Defines a region of a view that generates mouse-tracking events."""

    def __init__(self, rect: Optional[NSRect] = None,
                 options: int = NSTrackingAreaOptions.MOUSE_ENTERED_AND_EXITED | NSTrackingAreaOptions.ACTIVE_ALWAYS,
                 owner: Any = None, user_info: Any = None):
        self._rect = rect or NSRect()
        self._options = options
        self._owner = owner  # typically the view, set by NSView.add_tracking_area
        self._user_info = user_info
        self._mouse_inside = False

    @property
    def rect(self) -> NSRect:
        return self._rect

    @property
    def options(self) -> int:
        return self._options

    @property
    def owner(self):
        return self._owner

    @property
    def user_info(self):
        return self._user_info

    def contains_point(self, x: float, y: float) -> bool:
        return self._rect.contains(x, y)

    def check_mouse(self, x: float, y: float):
        """Check if the mouse has entered or exited the tracking area.

        Returns 'entered', 'exited', 'moved', or None.
        """
        inside = self.contains_point(x, y)
        if inside and not self._mouse_inside:
            self._mouse_inside = True
            return 'entered'
        elif not inside and self._mouse_inside:
            self._mouse_inside = False
            return 'exited'
        elif inside and (self._options & NSTrackingAreaOptions.MOUSE_MOVED):
            return 'moved'
        return None

    def __repr__(self):
        return (f"<NSTrackingArea rect=({self._rect.x},{self._rect.y},"
                f"{self._rect.width},{self._rect.height}) options={self._options}>")
