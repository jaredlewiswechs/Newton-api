"""NSAccessibility — accessibility elements, roles, and actions.

Provides a mirroring accessibility tree that can be built from
the view hierarchy. Each NSAccessibilityElement exposes role,
label, value, children, and supported actions.
"""
from __future__ import annotations
from typing import Optional, List, Any, Tuple


class NSAccessibilityRole:
    """Standard accessibility roles."""
    APPLICATION = "AXApplication"
    WINDOW = "AXWindow"
    SHEET = "AXSheet"
    DRAWER = "AXDrawer"
    GROUP = "AXGroup"
    BUTTON = "AXButton"
    RADIO_BUTTON = "AXRadioButton"
    CHECK_BOX = "AXCheckBox"
    SLIDER = "AXSlider"
    TEXT_FIELD = "AXTextField"
    TEXT_AREA = "AXTextArea"
    STATIC_TEXT = "AXStaticText"
    IMAGE = "AXImage"
    TABLE = "AXTable"
    ROW = "AXRow"
    COLUMN = "AXColumn"
    CELL = "AXCell"
    LIST = "AXList"
    OUTLINE = "AXOutline"
    SCROLL_AREA = "AXScrollArea"
    SCROLL_BAR = "AXScrollBar"
    TOOLBAR = "AXToolbar"
    TAB_GROUP = "AXTabGroup"
    SPLITTER = "AXSplitter"
    MENU = "AXMenu"
    MENU_ITEM = "AXMenuItem"
    MENU_BAR = "AXMenuBar"
    POP_UP_BUTTON = "AXPopUpButton"
    COMBO_BOX = "AXComboBox"
    PROGRESS_INDICATOR = "AXProgressIndicator"
    LINK = "AXLink"
    UNKNOWN = "AXUnknown"


class NSAccessibilityAction:
    """Standard accessibility actions."""
    PRESS = "AXPress"
    INCREMENT = "AXIncrement"
    DECREMENT = "AXDecrement"
    CONFIRM = "AXConfirm"
    CANCEL = "AXCancel"
    RAISE = "AXRaise"
    SHOW_MENU = "AXShowMenu"
    PICK = "AXPick"


class NSAccessibilityProtocol:
    """Mixin protocol that views implement to provide accessibility info."""

    def accessibility_role(self) -> str:
        return NSAccessibilityRole.UNKNOWN

    def accessibility_label(self) -> Optional[str]:
        return None

    def accessibility_value(self) -> Any:
        return None

    def accessibility_title(self) -> Optional[str]:
        return None

    def accessibility_help(self) -> Optional[str]:
        return None

    def accessibility_is_enabled(self) -> bool:
        return True

    def accessibility_is_focused(self) -> bool:
        return False

    def accessibility_children(self) -> List[Any]:
        return []

    def accessibility_parent(self) -> Any:
        return None

    def accessibility_frame(self) -> Tuple[float, float, float, float]:
        return (0, 0, 0, 0)

    def accessibility_supported_actions(self) -> List[str]:
        return []

    def accessibility_perform_action(self, action: str) -> bool:
        return False


class NSAccessibilityElement:
    """A node in the accessibility tree."""

    def __init__(self):
        self._role: str = NSAccessibilityRole.UNKNOWN
        self._label: Optional[str] = None
        self._value: Any = None
        self._title: Optional[str] = None
        self._help: Optional[str] = None
        self._enabled: bool = True
        self._focused: bool = False
        self._children: List[NSAccessibilityElement] = []
        self._parent: Optional[NSAccessibilityElement] = None
        self._frame: Tuple[float, float, float, float] = (0, 0, 0, 0)
        self._actions: List[str] = []
        self._source_view = None  # reference to the originating view

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, v: str):
        self._role = v

    @property
    def label(self) -> Optional[str]:
        return self._label

    @label.setter
    def label(self, v: Optional[str]):
        self._label = v

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, v: Any):
        self._value = v

    @property
    def title(self) -> Optional[str]:
        return self._title

    @title.setter
    def title(self, v: Optional[str]):
        self._title = v

    @property
    def help_text(self) -> Optional[str]:
        return self._help

    @help_text.setter
    def help_text(self, v: Optional[str]):
        self._help = v

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @is_enabled.setter
    def is_enabled(self, v: bool):
        self._enabled = v

    @property
    def is_focused(self) -> bool:
        return self._focused

    @is_focused.setter
    def is_focused(self, v: bool):
        self._focused = v

    @property
    def children(self) -> List[NSAccessibilityElement]:
        return self._children

    @property
    def parent(self) -> Optional[NSAccessibilityElement]:
        return self._parent

    @property
    def frame(self) -> Tuple[float, float, float, float]:
        return self._frame

    @frame.setter
    def frame(self, v: Tuple[float, float, float, float]):
        self._frame = v

    @property
    def supported_actions(self) -> List[str]:
        return list(self._actions)

    def add_child(self, child: NSAccessibilityElement):
        child._parent = self
        self._children.append(child)

    def remove_child(self, child: NSAccessibilityElement):
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def perform_action(self, action: str) -> bool:
        if action not in self._actions:
            return False
        if self._source_view and hasattr(self._source_view, 'accessibility_perform_action'):
            return self._source_view.accessibility_perform_action(action)
        return False

    def to_dict(self) -> dict:
        """Serialize the element tree to a dictionary."""
        return {
            'role': self._role,
            'label': self._label,
            'value': self._value,
            'title': self._title,
            'enabled': self._enabled,
            'focused': self._focused,
            'frame': self._frame,
            'actions': self._actions,
            'children': [c.to_dict() for c in self._children],
        }

    def __repr__(self):
        return f"<NSAccessibilityElement role={self._role} label={self._label!r}>"


def _role_for_view(view) -> str:
    """Infer accessibility role from view class name."""
    cls_name = type(view).__name__
    role_map = {
        'NSButton': NSAccessibilityRole.BUTTON,
        'NSTextField': NSAccessibilityRole.TEXT_FIELD,
        'NSTextView': NSAccessibilityRole.TEXT_AREA,
        'NSSlider': NSAccessibilityRole.SLIDER,
        'NSTableView': NSAccessibilityRole.TABLE,
        'NSOutlineView': NSAccessibilityRole.OUTLINE,
        'NSScrollView': NSAccessibilityRole.SCROLL_AREA,
        'NSStackView': NSAccessibilityRole.GROUP,
        'NSGridView': NSAccessibilityRole.GROUP,
        'NSSplitView': NSAccessibilityRole.SPLITTER,
        'NSSegmentedControl': NSAccessibilityRole.GROUP,
        'NSCollectionView': NSAccessibilityRole.LIST,
    }
    return role_map.get(cls_name, NSAccessibilityRole.GROUP)


def accessibility_tree_from_view(view) -> NSAccessibilityElement:
    """Build an accessibility tree by walking the view hierarchy."""
    elem = NSAccessibilityElement()
    elem._source_view = view

    if isinstance(view, NSAccessibilityProtocol):
        elem.role = view.accessibility_role()
        elem.label = view.accessibility_label()
        elem.value = view.accessibility_value()
        elem.title = view.accessibility_title()
        elem.is_enabled = view.accessibility_is_enabled()
        elem._actions = view.accessibility_supported_actions()
    else:
        elem.role = _role_for_view(view)
        # try to extract useful info
        if hasattr(view, 'title'):
            elem.label = getattr(view, 'title', None)
            if callable(elem.label):
                try:
                    elem.label = elem.label()
                except TypeError:
                    elem.label = None
        elif hasattr(view, 'string_value'):
            elem.value = getattr(view, 'string_value', None)
        if hasattr(view, '_frame'):
            f = view._frame
            elem.frame = (f.x, f.y, f.width, f.height)

    # recurse into subviews
    if hasattr(view, '_subviews'):
        for sv in view._subviews:
            child = accessibility_tree_from_view(sv)
            elem.add_child(child)

    return elem
