"""NSWindow, NSWindowController, and NSPanel.

NSWindow owns a content view (the root of the view tree for that window),
manages a title, frame, and can route events into its view hierarchy.
"""
from __future__ import annotations
from typing import Optional, List, Any
from enum import IntFlag

from Kernel.view.nsview import NSView, NSRect
from Kernel.runtime.responder import NSResponder
from Kernel.runtime.event import NSEvent, NSEventType


class NSWindowStyleMask(IntFlag):
    BORDERLESS = 0
    TITLED = 1 << 0
    CLOSABLE = 1 << 1
    MINIATURIZABLE = 1 << 2
    RESIZABLE = 1 << 3
    FULL_SCREEN = 1 << 14
    UTILITY_WINDOW = 1 << 4


class NSWindowLevel:
    NORMAL = 0
    FLOATING = 3
    MODAL_PANEL = 8
    MAIN_MENU = 24
    STATUS = 25
    POP_UP_MENU = 101
    SCREEN_SAVER = 1000


class NSWindow(NSResponder):
    """A window that owns a content view tree and participates in the responder chain."""

    _all_windows: List[NSWindow] = []

    def __init__(self, content_rect: Optional[NSRect] = None,
                 style_mask: int = NSWindowStyleMask.TITLED | NSWindowStyleMask.CLOSABLE | NSWindowStyleMask.RESIZABLE,
                 title: str = "Window"):
        super().__init__()
        self._frame = content_rect or NSRect(0, 0, 480, 320)
        self._style_mask = style_mask
        self._title = title
        self._content_view = NSView(NSRect(0, 0, self._frame.width, self._frame.height))
        self._content_view._window = self
        self._is_visible = False
        self._is_key = False
        self._is_main = False
        self._level: int = NSWindowLevel.NORMAL
        self._delegate = None
        self._window_controller: Optional[NSWindowController] = None
        self._min_size = (0.0, 0.0)
        self._max_size = (float('inf'), float('inf'))
        self._background_color = None
        self._is_opaque = True
        self._alpha_value = 1.0
        self._toolbar = None
        self._first_responder: Optional[NSResponder] = None
        NSWindow._all_windows.append(self)

    # ── properties ────────────────────────────────────────────────

    @property
    def frame(self) -> NSRect:
        return self._frame

    @frame.setter
    def frame(self, r: NSRect):
        self._frame = r
        self._content_view.frame = NSRect(0, 0, r.width, r.height)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str):
        self._title = v

    @property
    def style_mask(self) -> int:
        return self._style_mask

    @property
    def content_view(self) -> NSView:
        return self._content_view

    @content_view.setter
    def content_view(self, v: NSView):
        self._content_view = v
        v._window = self

    @property
    def is_visible(self) -> bool:
        return self._is_visible

    @property
    def is_key_window(self) -> bool:
        return self._is_key

    @property
    def is_main_window(self) -> bool:
        return self._is_main

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, v: int):
        self._level = v

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, d):
        self._delegate = d

    @property
    def min_size(self):
        return self._min_size

    @min_size.setter
    def min_size(self, v):
        self._min_size = v

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, v):
        self._max_size = v

    @property
    def toolbar(self):
        return self._toolbar

    @toolbar.setter
    def toolbar(self, v):
        self._toolbar = v

    @property
    def first_responder(self) -> Optional[NSResponder]:
        return self._first_responder

    # ── actions ───────────────────────────────────────────────────

    def make_key_and_order_front(self, sender=None):
        self._is_visible = True
        self._is_key = True
        self._is_main = True

    def order_front(self, sender=None):
        self._is_visible = True

    def order_out(self, sender=None):
        self._is_visible = False

    def close(self):
        self._is_visible = False
        self._is_key = False
        self._is_main = False
        if self in NSWindow._all_windows:
            NSWindow._all_windows.remove(self)
        if self._delegate and hasattr(self._delegate, 'window_will_close'):
            self._delegate.window_will_close(self)

    def miniaturize(self, sender=None):
        self._is_visible = False

    def deminiaturize(self, sender=None):
        self._is_visible = True

    def make_first_responder(self, responder: Optional[NSResponder]) -> bool:
        if self._first_responder:
            if not self._first_responder.resign_first_responder():
                return False
        self._first_responder = responder
        if responder:
            responder.become_first_responder()
        return True

    def set_frame_origin(self, x: float, y: float):
        self._frame = NSRect(x, y, self._frame.width, self._frame.height)

    def set_content_size(self, width: float, height: float):
        self._frame = NSRect(self._frame.x, self._frame.y, width, height)
        self._content_view.frame = NSRect(0, 0, width, height)

    def center(self):
        """Center the window on the main screen (headless approximation)."""
        self._frame = NSRect(
            (1920 - self._frame.width) / 2,
            (1080 - self._frame.height) / 2,
            self._frame.width, self._frame.height,
        )

    # ── event routing ─────────────────────────────────────────────

    def send_event(self, event: NSEvent):
        """Route events into the content view tree via hit testing."""
        if event.location and event.type in (NSEventType.MOUSE_DOWN, NSEventType.MOUSE_UP, NSEventType.MOUSE_MOVE):
            hit = self._content_view.hit_test(event.location)
            if hit:
                return hit.send_event(event)
        # keyboard events go to first responder
        if event.type in (NSEventType.KEY_DOWN, NSEventType.KEY_UP):
            if self._first_responder:
                return self._first_responder.send_event(event)
        return super().send_event(event)

    # ── SVG rendering ─────────────────────────────────────────────

    def render_to_svg(self, include_chrome: bool = True) -> str:
        parts = []
        fw, fh = self._frame.width, self._frame.height
        chrome_h = 22 if include_chrome and (self._style_mask & NSWindowStyleMask.TITLED) else 0
        total_h = fh + chrome_h

        parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{fw}" '
                     f'height="{total_h}" viewBox="0 0 {fw} {total_h}">')

        if include_chrome and chrome_h:
            parts.append(f'<rect x="0" y="0" width="{fw}" height="{chrome_h}" '
                         f'fill="#e0e0e0" rx="6" />')
            # traffic lights
            for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
                parts.append(f'<circle cx="{14 + i * 20}" cy="{chrome_h // 2}" '
                             f'r="6" fill="{color}" />')
            # title
            parts.append(f'<text x="{fw / 2}" y="{chrome_h // 2 + 4}" '
                         f'text-anchor="middle" font-size="12" '
                         f'font-family="sans-serif">{self._title}</text>')

        # content area
        parts.append(f'<g transform="translate(0,{chrome_h})">')
        parts.append(self._content_view.render_tree())
        parts.append('</g>')
        parts.append('</svg>')
        return "\n".join(parts)

    @classmethod
    def windows(cls) -> List[NSWindow]:
        return list(cls._all_windows)

    def __repr__(self):
        return f"<NSWindow title={self._title!r} frame=({self._frame.x},{self._frame.y},{self._frame.width},{self._frame.height})>"


class NSPanel(NSWindow):
    """A special window for auxiliary controls (inspectors, dialogs)."""

    def __init__(self, content_rect=None, style_mask=NSWindowStyleMask.TITLED | NSWindowStyleMask.CLOSABLE | NSWindowStyleMask.UTILITY_WINDOW,
                 title="Panel"):
        super().__init__(content_rect, style_mask, title)
        self._is_floating_panel = True
        self._becomes_key_only_if_needed = True
        self.level = NSWindowLevel.FLOATING

    @property
    def is_floating_panel(self) -> bool:
        return self._is_floating_panel

    @is_floating_panel.setter
    def is_floating_panel(self, v: bool):
        self._is_floating_panel = v


class NSWindowController:
    """Manages an NSWindow and coordinates document-based workflows."""

    def __init__(self, window: Optional[NSWindow] = None):
        self._window = window
        if window:
            window._window_controller = self
        self._document = None
        self._should_close_document = False
        self._content_view_controller = None

    @property
    def window(self) -> Optional[NSWindow]:
        return self._window

    @window.setter
    def window(self, w: Optional[NSWindow]):
        self._window = w
        if w:
            w._window_controller = self

    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, d):
        self._document = d

    @property
    def content_view_controller(self):
        return self._content_view_controller

    @content_view_controller.setter
    def content_view_controller(self, vc):
        self._content_view_controller = vc
        if vc and self._window:
            self._window.content_view = vc.view

    def show_window(self, sender=None):
        if self._window:
            self._window.make_key_and_order_front(sender)

    def close(self):
        if self._window:
            self._window.close()

    def __repr__(self):
        return f"<NSWindowController window={self._window!r}>"
