"""Drag and drop: NSDraggingInfo, NSDraggingItem, NSDraggingSession, NSDragOperation."""
from __future__ import annotations
from typing import Optional, List, Any, Tuple
from enum import IntFlag

from .nspasteboard import NSPasteboard


class NSDragOperation(IntFlag):
    NONE = 0
    COPY = 1
    LINK = 2
    GENERIC = 4
    PRIVATE = 8
    MOVE = 16
    DELETE = 32
    EVERY = 0xFFFFFFFF


class NSDraggingItem:
    """An item being dragged."""

    def __init__(self, pasteboard_writer: Any = None):
        self._pasteboard_writer = pasteboard_writer
        self._dragging_frame = (0.0, 0.0, 32.0, 32.0)  # x, y, w, h
        self._image_components: list = []

    @property
    def dragging_frame(self):
        return self._dragging_frame

    @dragging_frame.setter
    def dragging_frame(self, v):
        self._dragging_frame = v

    @property
    def item(self):
        return self._pasteboard_writer


class NSDraggingInfo:
    """Information about a drag operation in progress."""

    def __init__(self):
        self._dragging_pasteboard = NSPasteboard.pasteboard_with_name("drag")
        self._dragging_source: Any = None
        self._dragging_source_operation_mask = NSDragOperation.EVERY
        self._dragging_location: Tuple[float, float] = (0.0, 0.0)
        self._dragging_sequence_number: int = 0
        self._number_of_valid_items_for_drop: int = 0
        self._dragging_destination: Any = None
        self._animation_indicator = 0

    @property
    def dragging_pasteboard(self) -> NSPasteboard:
        return self._dragging_pasteboard

    @property
    def dragging_source(self):
        return self._dragging_source

    @property
    def dragging_source_operation_mask(self) -> NSDragOperation:
        return self._dragging_source_operation_mask

    @property
    def dragging_location(self) -> Tuple[float, float]:
        return self._dragging_location

    @dragging_location.setter
    def dragging_location(self, v: Tuple[float, float]):
        self._dragging_location = v


class NSDraggingSession:
    """Manages a drag session."""

    def __init__(self, items: Optional[List[NSDraggingItem]] = None,
                 source: Any = None, pasteboard: Optional[NSPasteboard] = None):
        self._dragging_items = items or []
        self._source = source
        self._pasteboard = pasteboard or NSPasteboard.pasteboard_with_name("drag")
        self._dragging_location: Tuple[float, float] = (0.0, 0.0)
        self._animates_on_cancel_or_fail = True
        self._dragging_formation = 0  # default

    @property
    def dragging_pasteboard(self) -> NSPasteboard:
        return self._pasteboard

    @property
    def dragging_items(self) -> List[NSDraggingItem]:
        return list(self._dragging_items)

    @property
    def dragging_location(self) -> Tuple[float, float]:
        return self._dragging_location

    @dragging_location.setter
    def dragging_location(self, v: Tuple[float, float]):
        self._dragging_location = v


# ── Dragging destination protocol (mixin) ─────────────────────────

class NSDraggingDestination:
    """Mixin protocol for views that accept drops."""

    def dragging_entered(self, info: NSDraggingInfo) -> NSDragOperation:
        return NSDragOperation.NONE

    def dragging_updated(self, info: NSDraggingInfo) -> NSDragOperation:
        return NSDragOperation.NONE

    def dragging_exited(self, info: NSDraggingInfo):
        pass

    def prepare_for_drag_operation(self, info: NSDraggingInfo) -> bool:
        return True

    def perform_drag_operation(self, info: NSDraggingInfo) -> bool:
        return False

    def conclude_drag_operation(self, info: NSDraggingInfo):
        pass


class NSDraggingSource:
    """Mixin protocol for views that initiate drags."""

    def dragging_session_will_begin(self, session: NSDraggingSession, at: Tuple[float, float]):
        pass

    def dragging_session_moved_to(self, session: NSDraggingSession, point: Tuple[float, float]):
        pass

    def dragging_session_ended(self, session: NSDraggingSession, point: Tuple[float, float],
                               operation: NSDragOperation):
        pass

    def dragging_session_source_operation_mask(self, session: NSDraggingSession,
                                                context: Any) -> NSDragOperation:
        return NSDragOperation.NONE
