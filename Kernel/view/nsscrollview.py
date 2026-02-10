"""NSScrollView and NSClipView — scrollable container views."""
from __future__ import annotations
from typing import Optional

from .nsview import NSView, NSRect


class NSClipView(NSView):
    """A view that clips its content to its bounds and provides scrolling offset."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._document_view: Optional[NSView] = None
        self._draws_background = True

    @property
    def document_view(self) -> Optional[NSView]:
        return self._document_view

    @document_view.setter
    def document_view(self, view: Optional[NSView]):
        if self._document_view is not None:
            self._document_view.remove_from_superview()
        self._document_view = view
        if view is not None:
            self.add_subview(view)

    def scroll_to_point(self, x: float, y: float):
        """Scroll so that (x, y) of the document view is at the clip origin."""
        self._bounds = NSRect(x, y, self._bounds.width, self._bounds.height)
        self.set_needs_display()

    @property
    def document_visible_rect(self) -> NSRect:
        return NSRect(self._bounds.x, self._bounds.y,
                      self._frame.width, self._frame.height)


class NSScrollView(NSView):
    """A scrollable container that manages a clip view, scroll bars, and optional rulers."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._content_view = NSClipView(NSRect(0, 0,
                                               frame.width if frame else 0,
                                               frame.height if frame else 0))
        self.add_subview(self._content_view)
        self._has_vertical_scroller = True
        self._has_horizontal_scroller = True
        self._autohides_scrollers = True
        self._scroll_offset_x: float = 0.0
        self._scroll_offset_y: float = 0.0

    @property
    def content_view(self) -> NSClipView:
        return self._content_view

    @property
    def document_view(self) -> Optional[NSView]:
        return self._content_view.document_view

    @document_view.setter
    def document_view(self, view: Optional[NSView]):
        self._content_view.document_view = view

    @property
    def has_vertical_scroller(self) -> bool:
        return self._has_vertical_scroller

    @has_vertical_scroller.setter
    def has_vertical_scroller(self, v: bool):
        self._has_vertical_scroller = v

    @property
    def has_horizontal_scroller(self) -> bool:
        return self._has_horizontal_scroller

    @has_horizontal_scroller.setter
    def has_horizontal_scroller(self, v: bool):
        self._has_horizontal_scroller = v

    def scroll_to(self, x: float, y: float):
        self._scroll_offset_x = x
        self._scroll_offset_y = y
        self._content_view.scroll_to_point(x, y)

    @property
    def document_visible_rect(self) -> NSRect:
        return self._content_view.document_visible_rect

    def draw(self, rect=None) -> str:
        parts = [super().draw(rect)]
        if self._has_vertical_scroller:
            parts.append(f'<!-- vertical scroller at x={self._frame.width - 12} -->')
        if self._has_horizontal_scroller:
            parts.append(f'<!-- horizontal scroller at y={self._frame.height - 12} -->')
        return "\n".join(parts)
