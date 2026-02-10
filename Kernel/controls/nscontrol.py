"""NSControl — base class for controls using the target/action pattern.

Also includes NSCell and NSActionCell for cell-based controls.
"""
from __future__ import annotations
from typing import Optional, Any

from Kernel.view.nsview import NSView, NSRect
from Kernel.runtime.event import NSEvent, NSEventType


class NSCell:
    """Basic cell used by cell-based controls."""

    def __init__(self):
        self._string_value: str = ""
        self._int_value: int = 0
        self._float_value: float = 0.0
        self._object_value: Any = None
        self._is_enabled = True
        self._is_highlighted = False
        self._is_editable = False
        self._is_selectable = False
        self._state: int = 0  # 0=off, 1=on, -1=mixed
        self._tag: int = 0

    @property
    def string_value(self) -> str:
        return self._string_value

    @string_value.setter
    def string_value(self, v: str):
        self._string_value = v

    @property
    def int_value(self) -> int:
        return self._int_value

    @int_value.setter
    def int_value(self, v: int):
        self._int_value = v

    @property
    def float_value(self) -> float:
        return self._float_value

    @float_value.setter
    def float_value(self, v: float):
        self._float_value = v

    @property
    def object_value(self):
        return self._object_value

    @object_value.setter
    def object_value(self, v):
        self._object_value = v

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, v: int):
        self._state = v


class NSActionCell(NSCell):
    """A cell that can fire a target/action."""

    def __init__(self):
        super().__init__()
        self._target = None
        self._action: Optional[str] = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        self._target = v

    @property
    def action(self) -> Optional[str]:
        return self._action

    @action.setter
    def action(self, v: Optional[str]):
        self._action = v


class NSControl(NSView):
    """Base class for controls. Provides target/action, enabled state, and value access."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._target = None
        self._action: Optional[str] = None
        self._is_enabled = True
        self._is_continuous = False
        self._string_value: str = ""
        self._int_value: int = 0
        self._float_value: float = 0.0
        self._object_value: Any = None
        self._cell: Optional[NSActionCell] = None
        self._font = None  # NSFont

    # ── target / action ───────────────────────────────────────────

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        self._target = v

    @property
    def action(self) -> Optional[str]:
        return self._action

    @action.setter
    def action(self, v: Optional[str]):
        self._action = v

    def send_action(self, action: Optional[str] = None, to: Any = None) -> bool:
        act = action or self._action
        tgt = to or self._target
        if tgt and act:
            method = getattr(tgt, act, None)
            if method:
                method(self)
                return True
        return False

    # ── enabled ───────────────────────────────────────────────────

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, v: bool):
        self._is_enabled = v

    @property
    def is_continuous(self) -> bool:
        return self._is_continuous

    @is_continuous.setter
    def is_continuous(self, v: bool):
        self._is_continuous = v

    # ── values ────────────────────────────────────────────────────

    @property
    def string_value(self) -> str:
        return self._string_value

    @string_value.setter
    def string_value(self, v: str):
        self._string_value = v

    @property
    def int_value(self) -> int:
        return self._int_value

    @int_value.setter
    def int_value(self, v: int):
        self._int_value = v

    @property
    def float_value(self) -> float:
        return self._float_value

    @float_value.setter
    def float_value(self, v: float):
        self._float_value = v

    @property
    def object_value(self):
        return self._object_value

    @object_value.setter
    def object_value(self, v):
        self._object_value = v

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, f):
        self._font = f

    # ── event handling ────────────────────────────────────────────

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if not self._is_enabled:
            return False
        return self.send_action()

    def __repr__(self):
        return f"<NSControl frame=({self._frame.x},{self._frame.y},{self._frame.width},{self._frame.height})>"
