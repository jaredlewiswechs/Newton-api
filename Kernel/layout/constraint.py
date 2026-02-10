"""NSLayoutConstraint, anchors, layout guides, and a simple constraint solver.

The solver is intentionally lightweight: it handles pin-to-edge, centering,
and fixed width/height constraints. For full AutoLayout semantics, a Cassowary
solver could be plugged in via the same API.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from enum import Enum, IntEnum


# ── enums ─────────────────────────────────────────────────────────

class NSLayoutRelation(IntEnum):
    LESS_THAN_OR_EQUAL = -1
    EQUAL = 0
    GREATER_THAN_OR_EQUAL = 1


class NSLayoutAttribute(IntEnum):
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    LEADING = 5
    TRAILING = 6
    WIDTH = 7
    HEIGHT = 8
    CENTER_X = 9
    CENTER_Y = 10
    NOT_AN_ATTRIBUTE = 0


class NSLayoutPriority:
    REQUIRED = 1000
    DEFAULT_HIGH = 750
    DRAG_THAT_CAN_RESIZE = 510
    DEFAULT_LOW = 250
    FITTINGSIZE_COMPRESSION = 50


# ── NSLayoutAnchor ────────────────────────────────────────────────

class NSLayoutAnchor:
    """Base class for layout anchors that can create constraints."""

    def __init__(self, item: Any, attribute: NSLayoutAttribute):
        self._item = item
        self._attribute = attribute

    def constraint_equal_to(self, other: NSLayoutAnchor, constant: float = 0.0) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.EQUAL,
            to_item=other._item, to_attribute=other._attribute,
            multiplier=1.0, constant=constant,
        )

    def constraint_greater_than_or_equal_to(self, other: NSLayoutAnchor, constant: float = 0.0) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.GREATER_THAN_OR_EQUAL,
            to_item=other._item, to_attribute=other._attribute,
            multiplier=1.0, constant=constant,
        )

    def constraint_less_than_or_equal_to(self, other: NSLayoutAnchor, constant: float = 0.0) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.LESS_THAN_OR_EQUAL,
            to_item=other._item, to_attribute=other._attribute,
            multiplier=1.0, constant=constant,
        )


class NSLayoutXAxisAnchor(NSLayoutAnchor):
    """Anchor for horizontal positions (left, right, leading, trailing, centerX)."""
    pass


class NSLayoutYAxisAnchor(NSLayoutAnchor):
    """Anchor for vertical positions (top, bottom, centerY)."""
    pass


class NSLayoutDimension(NSLayoutAnchor):
    """Anchor for size dimensions (width, height)."""

    def constraint_equal_to_constant(self, constant: float) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.EQUAL,
            to_item=None, to_attribute=NSLayoutAttribute.NOT_AN_ATTRIBUTE,
            multiplier=1.0, constant=constant,
        )

    def constraint_greater_than_or_equal_to_constant(self, constant: float) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.GREATER_THAN_OR_EQUAL,
            to_item=None, to_attribute=NSLayoutAttribute.NOT_AN_ATTRIBUTE,
            multiplier=1.0, constant=constant,
        )

    def constraint_less_than_or_equal_to_constant(self, constant: float) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.LESS_THAN_OR_EQUAL,
            to_item=None, to_attribute=NSLayoutAttribute.NOT_AN_ATTRIBUTE,
            multiplier=1.0, constant=constant,
        )

    def constraint_equal_to_anchor(self, other: NSLayoutDimension,
                                   multiplier: float = 1.0,
                                   constant: float = 0.0) -> NSLayoutConstraint:
        return NSLayoutConstraint(
            item=self._item, attribute=self._attribute,
            related_by=NSLayoutRelation.EQUAL,
            to_item=other._item, to_attribute=other._attribute,
            multiplier=multiplier, constant=constant,
        )


# ── NSLayoutConstraint ────────────────────────────────────────────

class NSLayoutConstraint:
    """Represents a single constraint: item.attr = toItem.toAttr * multiplier + constant."""

    def __init__(self, item: Any, attribute: NSLayoutAttribute,
                 related_by: NSLayoutRelation,
                 to_item: Any, to_attribute: NSLayoutAttribute,
                 multiplier: float = 1.0, constant: float = 0.0):
        self.first_item = item
        self.first_attribute = attribute
        self.relation = related_by
        self.second_item = to_item
        self.second_attribute = to_attribute
        self.multiplier = multiplier
        self.constant = constant
        self.priority: float = NSLayoutPriority.REQUIRED
        self.is_active = False
        self.identifier: Optional[str] = None

    def activate(self):
        self.is_active = True
        # auto-install on the nearest common ancestor
        if self.first_item and hasattr(self.first_item, 'add_constraint'):
            self.first_item.add_constraint(self)

    def deactivate(self):
        self.is_active = False
        if self.first_item and hasattr(self.first_item, 'remove_constraint'):
            self.first_item.remove_constraint(self)

    @staticmethod
    def activate_constraints(constraints: List[NSLayoutConstraint]):
        for c in constraints:
            c.activate()

    @staticmethod
    def deactivate_constraints(constraints: List[NSLayoutConstraint]):
        for c in constraints:
            c.deactivate()

    def __repr__(self):
        return (f"<NSLayoutConstraint {self.first_attribute.name} "
                f"{'=' if self.relation == 0 else '>=' if self.relation == 1 else '<='} "
                f"{self.second_attribute.name}*{self.multiplier}+{self.constant}>")


# ── Simple solver ─────────────────────────────────────────────────

def _get_attr_value(view, attr: NSLayoutAttribute) -> float:
    """Read a layout attribute value from a view's frame."""
    f = view.frame
    if attr == NSLayoutAttribute.LEFT or attr == NSLayoutAttribute.LEADING:
        return f.x
    if attr == NSLayoutAttribute.RIGHT or attr == NSLayoutAttribute.TRAILING:
        return f.x + f.width
    if attr == NSLayoutAttribute.TOP:
        return f.y
    if attr == NSLayoutAttribute.BOTTOM:
        return f.y + f.height
    if attr == NSLayoutAttribute.WIDTH:
        return f.width
    if attr == NSLayoutAttribute.HEIGHT:
        return f.height
    if attr == NSLayoutAttribute.CENTER_X:
        return f.x + f.width / 2
    if attr == NSLayoutAttribute.CENTER_Y:
        return f.y + f.height / 2
    return 0.0


def solve_constraints(constraints: List[NSLayoutConstraint], iterations: int = 4):
    """Apply constraints by iteratively adjusting view frames.

    This is a simple iterative solver suitable for pin/center/size constraints.
    For production use, swap in a Cassowary solver.
    """
    from Kernel.view.nsview import NSRect

    for _ in range(iterations):
        for c in constraints:
            if not c.is_active:
                continue
            view = c.first_item
            if view is None:
                continue
            # compute target value
            if c.second_item is not None:
                target = _get_attr_value(c.second_item, c.second_attribute) * c.multiplier + c.constant
            else:
                target = c.constant

            f = view.frame
            attr = c.first_attribute

            if attr in (NSLayoutAttribute.LEFT, NSLayoutAttribute.LEADING):
                w = f.width
                view.frame = NSRect(target, f.y, w, f.height)
            elif attr in (NSLayoutAttribute.RIGHT, NSLayoutAttribute.TRAILING):
                view.frame = NSRect(f.x, f.y, target - f.x, f.height)
            elif attr == NSLayoutAttribute.TOP:
                view.frame = NSRect(f.x, target, f.width, f.height)
            elif attr == NSLayoutAttribute.BOTTOM:
                view.frame = NSRect(f.x, f.y, f.width, target - f.y)
            elif attr == NSLayoutAttribute.WIDTH:
                view.frame = NSRect(f.x, f.y, target, f.height)
            elif attr == NSLayoutAttribute.HEIGHT:
                view.frame = NSRect(f.x, f.y, f.width, target)
            elif attr == NSLayoutAttribute.CENTER_X:
                view.frame = NSRect(target - f.width / 2, f.y, f.width, f.height)
            elif attr == NSLayoutAttribute.CENTER_Y:
                view.frame = NSRect(f.x, target - f.height / 2, f.width, f.height)


# ── NSLayoutGuide ─────────────────────────────────────────────────

class NSLayoutGuide:
    """A rectangular region in a view that can participate in Auto Layout."""

    def __init__(self):
        self._owning_view = None
        self._identifier: Optional[str] = None
        self._frame_x: float = 0.0
        self._frame_y: float = 0.0
        self._frame_width: float = 0.0
        self._frame_height: float = 0.0

    @property
    def owning_view(self):
        return self._owning_view

    @property
    def identifier(self) -> Optional[str]:
        return self._identifier

    @identifier.setter
    def identifier(self, v: str):
        self._identifier = v

    @property
    def frame(self):
        from Kernel.view.nsview import NSRect
        return NSRect(self._frame_x, self._frame_y,
                      self._frame_width, self._frame_height)

    # anchors
    @property
    def leading_anchor(self) -> NSLayoutXAxisAnchor:
        return NSLayoutXAxisAnchor(self, NSLayoutAttribute.LEADING)

    @property
    def trailing_anchor(self) -> NSLayoutXAxisAnchor:
        return NSLayoutXAxisAnchor(self, NSLayoutAttribute.TRAILING)

    @property
    def left_anchor(self) -> NSLayoutXAxisAnchor:
        return NSLayoutXAxisAnchor(self, NSLayoutAttribute.LEFT)

    @property
    def right_anchor(self) -> NSLayoutXAxisAnchor:
        return NSLayoutXAxisAnchor(self, NSLayoutAttribute.RIGHT)

    @property
    def top_anchor(self) -> NSLayoutYAxisAnchor:
        return NSLayoutYAxisAnchor(self, NSLayoutAttribute.TOP)

    @property
    def bottom_anchor(self) -> NSLayoutYAxisAnchor:
        return NSLayoutYAxisAnchor(self, NSLayoutAttribute.BOTTOM)

    @property
    def width_anchor(self) -> NSLayoutDimension:
        return NSLayoutDimension(self, NSLayoutAttribute.WIDTH)

    @property
    def height_anchor(self) -> NSLayoutDimension:
        return NSLayoutDimension(self, NSLayoutAttribute.HEIGHT)

    @property
    def center_x_anchor(self) -> NSLayoutXAxisAnchor:
        return NSLayoutXAxisAnchor(self, NSLayoutAttribute.CENTER_X)

    @property
    def center_y_anchor(self) -> NSLayoutYAxisAnchor:
        return NSLayoutYAxisAnchor(self, NSLayoutAttribute.CENTER_Y)
