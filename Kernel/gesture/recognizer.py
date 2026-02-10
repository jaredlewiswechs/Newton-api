"""Gesture recognizers: click, pan, magnification, rotation, press.

Each recognizer receives events, maintains state, and calls a target/action
when the gesture is recognized.
"""
from __future__ import annotations
from typing import Optional, Callable, Tuple
from enum import Enum
import time

from Kernel.runtime.event import NSEvent, NSEventType


class NSGestureRecognizerState(Enum):
    POSSIBLE = 0
    BEGAN = 1
    CHANGED = 2
    ENDED = 3
    CANCELLED = 4
    FAILED = 5
    RECOGNIZED = 6  # alias for discrete gestures


class NSGestureRecognizer:
    """Base class for gesture recognizers."""

    def __init__(self, target: object = None, action: Optional[str] = None):
        self._target = target
        self._action = action
        self._state = NSGestureRecognizerState.POSSIBLE
        self._view = None  # set by NSView.add_gesture_recognizer
        self._enabled = True
        self._delegate = None
        self._location: Tuple[float, float] = (0.0, 0.0)

    @property
    def state(self) -> NSGestureRecognizerState:
        return self._state

    @state.setter
    def state(self, v: NSGestureRecognizerState):
        self._state = v

    @property
    def view(self):
        return self._view

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, v: bool):
        self._enabled = v

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, d):
        self._delegate = d

    def location_in_view(self, view=None) -> Tuple[float, float]:
        return self._location

    def recognize(self, event: NSEvent) -> bool:
        """Process an event. Return True if the gesture consumed the event."""
        return False

    def reset(self):
        self._state = NSGestureRecognizerState.POSSIBLE

    def _fire_action(self):
        if self._target and self._action:
            method = getattr(self._target, self._action, None)
            if method:
                method(self)


class NSClickGestureRecognizer(NSGestureRecognizer):
    """Recognizes single or multi-click gestures."""

    def __init__(self, target=None, action=None):
        super().__init__(target, action)
        self._number_of_clicks_required = 1
        self._button_mask = 1  # primary button
        self._click_count = 0
        self._last_click_time = 0.0
        self._double_click_interval = 0.3

    @property
    def number_of_clicks_required(self) -> int:
        return self._number_of_clicks_required

    @number_of_clicks_required.setter
    def number_of_clicks_required(self, v: int):
        self._number_of_clicks_required = v

    def recognize(self, event: NSEvent) -> bool:
        if event.type != NSEventType.MOUSE_DOWN:
            return False
        now = time.time()
        if event.location:
            self._location = event.location
        if now - self._last_click_time > self._double_click_interval:
            self._click_count = 0
        self._click_count += 1
        self._last_click_time = now
        if self._click_count >= self._number_of_clicks_required:
            self._state = NSGestureRecognizerState.RECOGNIZED
            self._fire_action()
            self._click_count = 0
            return True
        return False


class NSPanGestureRecognizer(NSGestureRecognizer):
    """Recognizes drag/pan gestures."""

    def __init__(self, target=None, action=None):
        super().__init__(target, action)
        self._translation: Tuple[float, float] = (0.0, 0.0)
        self._velocity: Tuple[float, float] = (0.0, 0.0)
        self._start_location: Optional[Tuple[float, float]] = None
        self._last_location: Optional[Tuple[float, float]] = None
        self._last_time: float = 0.0

    @property
    def translation(self) -> Tuple[float, float]:
        return self._translation

    @property
    def velocity(self) -> Tuple[float, float]:
        return self._velocity

    def set_translation(self, tx: float, ty: float):
        self._translation = (tx, ty)

    def recognize(self, event: NSEvent) -> bool:
        loc = event.location or (0, 0)
        self._location = loc
        now = time.time()

        if event.type == NSEventType.MOUSE_DOWN:
            self._start_location = loc
            self._last_location = loc
            self._last_time = now
            self._state = NSGestureRecognizerState.BEGAN
            self._translation = (0.0, 0.0)
            self._fire_action()
            return True

        if event.type == NSEventType.MOUSE_MOVE and self._start_location:
            dx = loc[0] - self._start_location[0]
            dy = loc[1] - self._start_location[1]
            self._translation = (dx, dy)
            dt = now - self._last_time if self._last_time else 1.0
            if dt > 0 and self._last_location:
                self._velocity = (
                    (loc[0] - self._last_location[0]) / dt,
                    (loc[1] - self._last_location[1]) / dt,
                )
            self._last_location = loc
            self._last_time = now
            self._state = NSGestureRecognizerState.CHANGED
            self._fire_action()
            return True

        if event.type == NSEventType.MOUSE_UP and self._start_location:
            self._state = NSGestureRecognizerState.ENDED
            self._fire_action()
            self._start_location = None
            return True

        return False


class NSMagnificationGestureRecognizer(NSGestureRecognizer):
    """Recognizes pinch/magnification gestures (placeholder for trackpad events)."""

    def __init__(self, target=None, action=None):
        super().__init__(target, action)
        self._magnification: float = 0.0

    @property
    def magnification(self) -> float:
        return self._magnification

    def recognize(self, event: NSEvent) -> bool:
        if event.user_info and 'magnification' in event.user_info:
            self._magnification = event.user_info['magnification']
            if event.location:
                self._location = event.location
            self._state = NSGestureRecognizerState.CHANGED
            self._fire_action()
            return True
        return False


class NSRotationGestureRecognizer(NSGestureRecognizer):
    """Recognizes rotation gestures (placeholder for trackpad events)."""

    def __init__(self, target=None, action=None):
        super().__init__(target, action)
        self._rotation: float = 0.0

    @property
    def rotation(self) -> float:
        return self._rotation

    def recognize(self, event: NSEvent) -> bool:
        if event.user_info and 'rotation' in event.user_info:
            self._rotation = event.user_info['rotation']
            if event.location:
                self._location = event.location
            self._state = NSGestureRecognizerState.CHANGED
            self._fire_action()
            return True
        return False


class NSPressGestureRecognizer(NSGestureRecognizer):
    """Recognizes long-press gestures."""

    def __init__(self, target=None, action=None):
        super().__init__(target, action)
        self._minimum_press_duration: float = 0.5
        self._press_start_time: float = 0.0
        self._pressing = False

    @property
    def minimum_press_duration(self) -> float:
        return self._minimum_press_duration

    @minimum_press_duration.setter
    def minimum_press_duration(self, v: float):
        self._minimum_press_duration = v

    def recognize(self, event: NSEvent) -> bool:
        if event.location:
            self._location = event.location
        if event.type == NSEventType.MOUSE_DOWN:
            self._press_start_time = time.time()
            self._pressing = True
            return False
        if event.type == NSEventType.MOUSE_UP and self._pressing:
            self._pressing = False
            elapsed = time.time() - self._press_start_time
            if elapsed >= self._minimum_press_duration:
                self._state = NSGestureRecognizerState.RECOGNIZED
                self._fire_action()
                return True
        return False
