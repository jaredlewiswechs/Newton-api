"""NSButton — a standard push button control."""
from __future__ import annotations
from typing import Optional
from enum import Enum

from .nscontrol import NSControl
from Kernel.view.nsview import NSRect
from Kernel.runtime.event import NSEvent, NSEventType


class NSButtonType(Enum):
    MOMENTARY_LIGHT = 0
    PUSH_ON_PUSH_OFF = 1
    TOGGLE = 2
    SWITCH = 3  # checkbox
    RADIO = 4
    MOMENTARY_CHANGE = 5
    ON_OFF = 6
    MOMENTARY_PUSH_IN = 7


class NSBezelStyle(Enum):
    ROUNDED = 1
    REGULAR_SQUARE = 2
    DISCLOSURE = 5
    SHADOWLESS_SQUARE = 6
    CIRCULAR = 7
    TEXTURED_SQUARE = 8
    HELP_BUTTON = 9
    SMALL_SQUARE = 10
    TEXTURED_ROUNDED = 11
    ROUND_RECT = 12
    RECESSED = 13
    ROUNDED_DISCLOSURE = 14
    INLINE = 15


class NSButton(NSControl):
    """A push button, toggle, checkbox, or radio button."""

    def __init__(self, frame: Optional[NSRect] = None, title: str = "Button"):
        super().__init__(frame)
        self._title = title
        self._alternate_title = ""
        self._image = None
        self._alternate_image = None
        self._button_type = NSButtonType.MOMENTARY_PUSH_IN
        self._bezel_style = NSBezelStyle.ROUNDED
        self._state: int = 0  # 0=off, 1=on, -1=mixed
        self._is_bordered = True
        self._is_transparent = False
        self._key_equivalent = ""
        self._key_equivalent_modifier_mask = 0
        self._allows_mixed_state = False
        self._show_border_on_hover = False
        self._content_tint_color = None

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str):
        self._title = v

    @property
    def alternate_title(self) -> str:
        return self._alternate_title

    @alternate_title.setter
    def alternate_title(self, v: str):
        self._alternate_title = v

    @property
    def button_type(self) -> NSButtonType:
        return self._button_type

    def set_button_type(self, bt: NSButtonType):
        self._button_type = bt

    @property
    def bezel_style(self) -> NSBezelStyle:
        return self._bezel_style

    @bezel_style.setter
    def bezel_style(self, v: NSBezelStyle):
        self._bezel_style = v

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, v: int):
        self._state = v

    @property
    def is_bordered(self) -> bool:
        return self._is_bordered

    @is_bordered.setter
    def is_bordered(self, v: bool):
        self._is_bordered = v

    @property
    def key_equivalent(self) -> str:
        return self._key_equivalent

    @key_equivalent.setter
    def key_equivalent(self, v: str):
        self._key_equivalent = v

    @property
    def allows_mixed_state(self) -> bool:
        return self._allows_mixed_state

    @allows_mixed_state.setter
    def allows_mixed_state(self, v: bool):
        self._allows_mixed_state = v

    def set_next_state(self):
        if self._allows_mixed_state:
            self._state = (self._state + 2) % 3 - 1  # cycles: 0 → 1 → -1 → 0
        else:
            self._state = 0 if self._state else 1

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if not self._is_enabled:
            return False
        if self._button_type in (NSButtonType.TOGGLE, NSButtonType.SWITCH,
                                  NSButtonType.RADIO, NSButtonType.PUSH_ON_PUSH_OFF,
                                  NSButtonType.ON_OFF):
            self.set_next_state()
        self.send_action()
        return True

    def handle_key_down(self, event: NSEvent) -> bool:
        if self._key_equivalent and event.user_info:
            key = event.user_info.get('key', '')
            if key == self._key_equivalent:
                self.handle_mouse_down(event)
                return True
        return False

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        bg = "#e0e0e0" if self._state == 0 else "#a0c0ff"
        border = "stroke='#888' stroke-width='1'" if self._is_bordered else ""
        parts = [
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="4" '
            f'fill="{bg}" {border} />',
            f'<text x="{w / 2}" y="{h / 2 + 4}" text-anchor="middle" '
            f'font-size="13" font-family="sans-serif">{self._title}</text>',
        ]
        return "\n".join(parts)

    def __repr__(self):
        return f"<NSButton title={self._title!r} state={self._state}>"
