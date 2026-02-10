"""NSTextField — a single-line text input or label control."""
from __future__ import annotations
from typing import Optional

from .nscontrol import NSControl
from Kernel.view.nsview import NSRect
from Kernel.runtime.event import NSEvent, NSEventType


class NSTextField(NSControl):
    """A single-line editable text field or static label."""

    def __init__(self, frame: Optional[NSRect] = None, string_value: str = ""):
        super().__init__(frame)
        self._string_value = string_value
        self._placeholder_string: Optional[str] = None
        self._is_editable = True
        self._is_selectable = True
        self._is_bezeled = True
        self._is_bordered = True
        self._draws_background = True
        self._text_color = None  # NSColor
        self._background_color_field = None
        self._alignment: int = 0  # 0=left, 1=center, 2=right
        self._line_break_mode: int = 0
        self._maximum_number_of_lines: int = 1
        self._delegate = None
        self._cursor_position: int = len(string_value)

    @property
    def placeholder_string(self) -> Optional[str]:
        return self._placeholder_string

    @placeholder_string.setter
    def placeholder_string(self, v: Optional[str]):
        self._placeholder_string = v

    @property
    def is_editable(self) -> bool:
        return self._is_editable

    @is_editable.setter
    def is_editable(self, v: bool):
        self._is_editable = v

    @property
    def is_selectable(self) -> bool:
        return self._is_selectable

    @is_selectable.setter
    def is_selectable(self, v: bool):
        self._is_selectable = v

    @property
    def is_bezeled(self) -> bool:
        return self._is_bezeled

    @is_bezeled.setter
    def is_bezeled(self, v: bool):
        self._is_bezeled = v

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, c):
        self._text_color = c

    @property
    def alignment(self) -> int:
        return self._alignment

    @alignment.setter
    def alignment(self, v: int):
        self._alignment = v

    @property
    def maximum_number_of_lines(self) -> int:
        return self._maximum_number_of_lines

    @maximum_number_of_lines.setter
    def maximum_number_of_lines(self, v: int):
        self._maximum_number_of_lines = v

    # ── label factory ─────────────────────────────────────────────

    @classmethod
    def label_with_string(cls, text: str) -> NSTextField:
        tf = cls(string_value=text)
        tf._is_editable = False
        tf._is_bezeled = False
        tf._is_bordered = False
        tf._draws_background = False
        return tf

    @classmethod
    def wrapping_label_with_string(cls, text: str) -> NSTextField:
        tf = cls.label_with_string(text)
        tf._maximum_number_of_lines = 0  # unlimited
        return tf

    # ── editing ───────────────────────────────────────────────────

    def handle_key_down(self, event: NSEvent) -> bool:
        if not self._is_editable or not self._is_enabled:
            return False
        if event.user_info:
            key = event.user_info.get('key', '')
            if key == 'backspace' and self._cursor_position > 0:
                self._string_value = (self._string_value[:self._cursor_position - 1]
                                      + self._string_value[self._cursor_position:])
                self._cursor_position -= 1
            elif key == 'enter' or key == 'return':
                self.send_action()
            elif len(key) == 1:
                self._string_value = (self._string_value[:self._cursor_position]
                                      + key + self._string_value[self._cursor_position:])
                self._cursor_position += 1
            self.set_needs_display()
            return True
        return False

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if not self._is_enabled:
            return False
        # clicking a text field makes it first responder
        if self._window:
            self._window.make_first_responder(self)
        return True

    def select_text(self, sender=None):
        self._cursor_position = len(self._string_value)

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        parts = []
        if self._draws_background and self._is_bezeled:
            parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" '
                         f'fill="white" stroke="#aaa" stroke-width="1" rx="3" />')
        display_text = self._string_value or self._placeholder_string or ""
        color = "#000"
        if not self._string_value and self._placeholder_string:
            color = "#999"
        anchor = "start"
        tx = 4
        if self._alignment == 1:
            anchor = "middle"
            tx = w / 2
        elif self._alignment == 2:
            anchor = "end"
            tx = w - 4
        parts.append(f'<text x="{tx}" y="{h / 2 + 4}" text-anchor="{anchor}" '
                     f'font-size="13" font-family="sans-serif" fill="{color}">'
                     f'{display_text}</text>')
        return "\n".join(parts)

    def __repr__(self):
        return f"<NSTextField value={self._string_value!r} editable={self._is_editable}>"
