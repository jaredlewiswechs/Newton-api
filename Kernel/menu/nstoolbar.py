"""NSToolbar and NSToolbarItem — window toolbars."""
from __future__ import annotations
from typing import Optional, List, Any


class NSToolbarItemIdentifier:
    """Standard toolbar item identifiers."""
    SEPARATOR = "NSToolbarSeparatorItem"
    SPACE = "NSToolbarSpaceItem"
    FLEXIBLE_SPACE = "NSToolbarFlexibleSpaceItem"
    SHOW_COLORS = "NSToolbarShowColorsItem"
    SHOW_FONTS = "NSToolbarShowFontsItem"
    PRINT = "NSToolbarPrintItem"
    TOGGLE_SIDEBAR = "com.apple.NSToolbarToggleSidebarItem"


class NSToolbarItem:
    """A single item in a toolbar."""

    def __init__(self, identifier: str = ""):
        self._identifier = identifier
        self._label: str = ""
        self._palette_label: str = ""
        self._tool_tip: Optional[str] = None
        self._image = None
        self._target = None
        self._action: Optional[str] = None
        self._is_enabled = True
        self._tag: int = 0
        self._view = None
        self._min_size = (0.0, 0.0)
        self._max_size = (0.0, 0.0)
        self._is_bordered = False

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, v: str):
        self._label = v

    @property
    def palette_label(self) -> str:
        return self._palette_label

    @palette_label.setter
    def palette_label(self, v: str):
        self._palette_label = v

    @property
    def tool_tip(self) -> Optional[str]:
        return self._tool_tip

    @tool_tip.setter
    def tool_tip(self, v: Optional[str]):
        self._tool_tip = v

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

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, v: bool):
        self._is_enabled = v

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, v):
        self._view = v

    @property
    def is_bordered(self) -> bool:
        return self._is_bordered

    @is_bordered.setter
    def is_bordered(self, v: bool):
        self._is_bordered = v

    def perform_action(self) -> bool:
        if not self._is_enabled:
            return False
        if self._target and self._action:
            method = getattr(self._target, self._action, None)
            if method:
                method(self)
                return True
        return False

    def __repr__(self):
        return f"<NSToolbarItem {self._identifier!r} label={self._label!r}>"


class NSToolbar:
    """A toolbar displayed at the top of a window."""

    def __init__(self, identifier: str = ""):
        self._identifier = identifier
        self._items: List[NSToolbarItem] = []
        self._delegate = None
        self._is_visible = True
        self._display_mode = 0  # 0=default, 1=icon+label, 2=icon, 3=label
        self._size_mode = 0  # 0=default, 1=regular, 2=small
        self._allows_user_customization = True
        self._autosaves_configuration = False
        self._selected_item_identifier: Optional[str] = None

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def items(self) -> List[NSToolbarItem]:
        return list(self._items)

    @property
    def visible_items(self) -> List[NSToolbarItem]:
        return [i for i in self._items if self._is_visible]

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, d):
        self._delegate = d

    @property
    def is_visible(self) -> bool:
        return self._is_visible

    @is_visible.setter
    def is_visible(self, v: bool):
        self._is_visible = v

    @property
    def display_mode(self) -> int:
        return self._display_mode

    @display_mode.setter
    def display_mode(self, v: int):
        self._display_mode = v

    @property
    def selected_item_identifier(self) -> Optional[str]:
        return self._selected_item_identifier

    @selected_item_identifier.setter
    def selected_item_identifier(self, v: Optional[str]):
        self._selected_item_identifier = v

    def insert_item(self, identifier: str, at_index: int):
        item = NSToolbarItem(identifier)
        item.label = identifier
        self._items.insert(at_index, item)

    def remove_item_at_index(self, index: int):
        if 0 <= index < len(self._items):
            self._items.pop(index)

    def item_with_identifier(self, identifier: str) -> Optional[NSToolbarItem]:
        for item in self._items:
            if item.identifier == identifier:
                return item
        return None

    def validate_visible_items(self):
        """Validate toolbar items by calling validate on targets."""
        for item in self._items:
            if item.target and hasattr(item.target, 'validate_toolbar_item'):
                item.is_enabled = item.target.validate_toolbar_item(item)

    def __repr__(self):
        return f"<NSToolbar {self._identifier!r} items={len(self._items)}>"
