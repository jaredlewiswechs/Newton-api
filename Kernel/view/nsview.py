"""NSView and NSViewController — the core of the view tree.

NSView provides:
 - frame / bounds geometry
 - subview management (add, remove, reorder)
 - coordinate conversion between view-local and superview
 - hit-testing (deepest subview under a point)
 - responder-chain integration (NSView IS-A NSResponder)
 - draw() hook that returns SVG fragment for compositing
 - hidden / alpha / needs_display flags
 - tag-based lookup
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import uuid

from Kernel.runtime.responder import NSResponder
from Kernel.runtime.event import NSEvent


# ── geometry helpers ──────────────────────────────────────────────

@dataclass
class NSRect:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    def contains(self, px: float, py: float) -> bool:
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))


@dataclass
class NSSize:
    width: float = 0.0
    height: float = 0.0


# ── NSView ────────────────────────────────────────────────────────

class NSView(NSResponder):
    """A rectangular area in a window that draws content and handles events."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__()
        self._frame = frame or NSRect()
        self._bounds = NSRect(0, 0, self._frame.width, self._frame.height)
        self._subviews: List[NSView] = []
        self._superview: Optional[NSView] = None
        self._window = None  # set by NSWindow when the view is installed
        self._hidden = False
        self._alpha: float = 1.0
        self._needs_display = True
        self._tag: int = 0
        self._identifier: str = uuid.uuid4().hex[:8]
        self._background_color = None  # Optional NSColor
        self._tracking_areas: list = []
        self._gesture_recognizers: list = []
        self._layer = None  # placeholder for layer-backed views
        self._autoresizes_subviews = True
        self._autoresizing_mask = 0  # NSAutoresizingMaskOptions
        self._constraints: list = []
        self._layout_guides: list = []
        self._tooltip: Optional[str] = None

    # ── geometry ──────────────────────────────────────────────────

    @property
    def frame(self) -> NSRect:
        return self._frame

    @frame.setter
    def frame(self, r: NSRect):
        old = self._frame
        self._frame = r
        self._bounds = NSRect(0, 0, r.width, r.height)
        if self._autoresizes_subviews:
            self._resize_subviews(old, r)
        self.set_needs_display()

    @property
    def bounds(self) -> NSRect:
        return self._bounds

    @bounds.setter
    def bounds(self, r: NSRect):
        self._bounds = r

    @property
    def frame_origin(self) -> Tuple[float, float]:
        return (self._frame.x, self._frame.y)

    @property
    def frame_size(self) -> NSSize:
        return NSSize(self._frame.width, self._frame.height)

    # ── subview management ────────────────────────────────────────

    @property
    def subviews(self) -> List[NSView]:
        return list(self._subviews)

    @property
    def superview(self) -> Optional[NSView]:
        return self._superview

    def add_subview(self, view: NSView):
        if view._superview is not None:
            view.remove_from_superview()
        view._superview = self
        view._window = self._window
        view.next_responder = self  # responder chain: view → superview
        self._subviews.append(view)
        self._propagate_window(view, self._window)
        self.set_needs_display()

    def add_subview_positioned(self, view: NSView, relative_to: Optional[NSView],
                               above: bool = True):
        if view._superview is not None:
            view.remove_from_superview()
        view._superview = self
        view._window = self._window
        view.next_responder = self
        if relative_to is not None and relative_to in self._subviews:
            idx = self._subviews.index(relative_to)
            if above:
                self._subviews.insert(idx + 1, view)
            else:
                self._subviews.insert(idx, view)
        else:
            self._subviews.append(view)
        self._propagate_window(view, self._window)
        self.set_needs_display()

    def remove_from_superview(self):
        if self._superview is not None:
            self._superview._subviews.remove(self)
            self._superview.set_needs_display()
        self._superview = None
        self._propagate_window(self, None)
        self.next_responder = None

    def _propagate_window(self, view: NSView, window):
        view._window = window
        for sv in view._subviews:
            self._propagate_window(sv, window)

    def sort_subviews(self, key=None):
        """Sort subviews; key receives an NSView and returns a sort value."""
        if key:
            self._subviews.sort(key=key)

    # ── z-order helpers ───────────────────────────────────────────

    def bring_subview_to_front(self, view: NSView):
        if view in self._subviews:
            self._subviews.remove(view)
            self._subviews.append(view)

    def send_subview_to_back(self, view: NSView):
        if view in self._subviews:
            self._subviews.remove(view)
            self._subviews.insert(0, view)

    # ── coordinate conversion ─────────────────────────────────────

    def convert_point_to(self, point: Tuple[float, float], to_view: Optional[NSView]) -> Tuple[float, float]:
        """Convert a point from this view's coordinate system to to_view's (or window if None)."""
        # convert to window coords first
        wx, wy = self._to_window_coords(point[0], point[1])
        if to_view is None:
            return (wx, wy)
        return to_view._from_window_coords(wx, wy)

    def convert_point_from(self, point: Tuple[float, float], from_view: Optional[NSView]) -> Tuple[float, float]:
        """Convert a point from from_view's coordinate system (or window) to this view."""
        if from_view is None:
            return self._from_window_coords(point[0], point[1])
        wx, wy = from_view._to_window_coords(point[0], point[1])
        return self._from_window_coords(wx, wy)

    def _to_window_coords(self, x: float, y: float) -> Tuple[float, float]:
        wx = x + self._frame.x
        wy = y + self._frame.y
        if self._superview:
            return self._superview._to_window_coords(wx, wy)
        return (wx, wy)

    def _from_window_coords(self, wx: float, wy: float) -> Tuple[float, float]:
        if self._superview:
            wx, wy = self._superview._from_window_coords(wx, wy)
        return (wx - self._frame.x, wy - self._frame.y)

    # ── hit testing ───────────────────────────────────────────────

    def hit_test(self, point: Tuple[float, float]) -> Optional[NSView]:
        """Return deepest visible subview containing *point* (in superview coords),
        or self if the point is inside this view but no subview claims it,
        or None if the point is outside."""
        if self._hidden or self._alpha <= 0:
            return None
        # point is in superview coordinates; check against frame
        px, py = point
        if not self._frame.contains(px, py):
            return None
        # convert to local coords
        local_x = px - self._frame.x
        local_y = py - self._frame.y
        # iterate subviews back-to-front (last = topmost)
        for sv in reversed(self._subviews):
            hit = sv.hit_test((local_x, local_y))
            if hit is not None:
                return hit
        return self

    def is_descendant_of(self, view: NSView) -> bool:
        v = self
        while v is not None:
            if v is view:
                return True
            v = v._superview
        return False

    # ── display / drawing ─────────────────────────────────────────

    @property
    def is_hidden(self) -> bool:
        return self._hidden

    @is_hidden.setter
    def is_hidden(self, val: bool):
        self._hidden = val

    @property
    def alpha_value(self) -> float:
        return self._alpha

    @alpha_value.setter
    def alpha_value(self, val: float):
        self._alpha = max(0.0, min(1.0, val))

    @property
    def needs_display(self) -> bool:
        return self._needs_display

    def set_needs_display(self, flag: bool = True):
        self._needs_display = flag

    @property
    def tag(self) -> int:
        return self._tag

    @tag.setter
    def tag(self, v: int):
        self._tag = v

    def view_with_tag(self, tag: int) -> Optional[NSView]:
        if self._tag == tag:
            return self
        for sv in self._subviews:
            found = sv.view_with_tag(tag)
            if found:
                return found
        return None

    @property
    def identifier(self) -> str:
        return self._identifier

    @identifier.setter
    def identifier(self, v: str):
        self._identifier = v

    # ── draw hook (override in subclasses) ────────────────────────

    def draw(self, rect: Optional[NSRect] = None) -> str:
        """Return an SVG fragment representing this view's content.
        Subclasses override this to provide custom drawing."""
        parts = []
        # background
        if self._background_color:
            rgba = self._background_color.to_rgba()
            parts.append(
                f'<rect x="0" y="0" width="{self._bounds.width}" '
                f'height="{self._bounds.height}" fill="{rgba}" />'
            )
        return "\n".join(parts)

    def render_tree(self) -> str:
        """Recursively render this view and all subviews to an SVG group."""
        if self._hidden:
            return ""
        parts = []
        opacity = f' opacity="{self._alpha}"' if self._alpha < 1.0 else ''
        parts.append(
            f'<g transform="translate({self._frame.x},{self._frame.y})"{opacity} '
            f'data-view-id="{self._identifier}">'
        )
        parts.append(self.draw())
        for sv in self._subviews:
            parts.append(sv.render_tree())
        parts.append('</g>')
        return "\n".join(parts)

    # ── tracking areas & gesture recognizers ──────────────────────

    def add_tracking_area(self, area):
        self._tracking_areas.append(area)
        area._owner = self

    def remove_tracking_area(self, area):
        if area in self._tracking_areas:
            self._tracking_areas.remove(area)

    @property
    def tracking_areas(self):
        return list(self._tracking_areas)

    def add_gesture_recognizer(self, recognizer):
        self._gesture_recognizers.append(recognizer)
        recognizer._view = self

    def remove_gesture_recognizer(self, recognizer):
        if recognizer in self._gesture_recognizers:
            self._gesture_recognizers.remove(recognizer)

    @property
    def gesture_recognizers(self):
        return list(self._gesture_recognizers)

    # ── constraints ───────────────────────────────────────────────

    def add_constraint(self, constraint):
        self._constraints.append(constraint)

    def add_constraints(self, constraints):
        self._constraints.extend(constraints)

    def remove_constraint(self, constraint):
        if constraint in self._constraints:
            self._constraints.remove(constraint)

    @property
    def constraints(self):
        return list(self._constraints)

    def add_layout_guide(self, guide):
        guide._owning_view = self
        self._layout_guides.append(guide)

    @property
    def layout_guides(self):
        return list(self._layout_guides)

    def layout(self):
        """Perform layout. Override in subclasses for custom layout."""
        self.layout_subtree()

    def layout_subtree(self):
        for sv in self._subviews:
            sv.layout()

    # ── event routing (override NSResponder) ──────────────────────

    def send_event(self, event: NSEvent):
        """Route events through gesture recognizers first, then responder chain."""
        for gr in self._gesture_recognizers:
            if gr.enabled and gr.recognize(event):
                return True
        return super().send_event(event)

    # ── autoresize ────────────────────────────────────────────────

    def _resize_subviews(self, old: NSRect, new: NSRect):
        """Placeholder for autoresizing mask logic."""
        pass

    # ── tooltip ───────────────────────────────────────────────────

    @property
    def tool_tip(self) -> Optional[str]:
        return self._tooltip

    @tool_tip.setter
    def tool_tip(self, v: Optional[str]):
        self._tooltip = v

    def __repr__(self):
        return (f"<NSView id={self._identifier} frame=({self._frame.x},{self._frame.y},"
                f"{self._frame.width},{self._frame.height}) subs={len(self._subviews)}>")


# ── NSViewController ──────────────────────────────────────────────

class NSViewController:
    """Manages an NSView and its lifecycle."""

    def __init__(self):
        self._view: Optional[NSView] = None
        self._title: Optional[str] = None
        self._children: List[NSViewController] = []
        self._parent: Optional[NSViewController] = None
        self._represented_object: Any = None

    @property
    def view(self) -> NSView:
        if self._view is None:
            self.load_view()
            self.view_did_load()
        return self._view

    @view.setter
    def view(self, v: NSView):
        self._view = v

    @property
    def title(self) -> Optional[str]:
        return self._title

    @title.setter
    def title(self, v: Optional[str]):
        self._title = v

    @property
    def represented_object(self):
        return self._represented_object

    @represented_object.setter
    def represented_object(self, v):
        self._represented_object = v

    def load_view(self):
        """Create the controller's view. Override in subclasses."""
        if self._view is None:
            self._view = NSView(NSRect(0, 0, 100, 100))

    def view_did_load(self):
        """Called after the view is loaded. Override for setup."""
        pass

    def view_will_appear(self):
        pass

    def view_did_appear(self):
        pass

    def view_will_disappear(self):
        pass

    def view_did_disappear(self):
        pass

    # ── child controller management ───────────────────────────────

    def add_child(self, child: NSViewController):
        child._parent = self
        self._children.append(child)

    def remove_from_parent(self):
        if self._parent:
            self._parent._children.remove(self)
            self._parent = None

    @property
    def children(self) -> List[NSViewController]:
        return list(self._children)

    @property
    def parent(self) -> Optional[NSViewController]:
        return self._parent

    def __repr__(self):
        return f"<NSViewController title={self._title!r}>"
