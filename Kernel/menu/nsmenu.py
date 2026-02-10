"""NSMenu and NSMenuItem — application and context menus."""
from __future__ import annotations
from typing import Optional, List, Any


class NSMenuItem:
    """A single item in a menu."""

    def __init__(self, title: str = "", action: Optional[str] = None,
                 key_equivalent: str = ""):
        self._title = title
        self._action = action
        self._key_equivalent = key_equivalent
        self._key_equivalent_modifier_mask = 0
        self._target = None
        self._tag: int = 0
        self._state: int = 0  # 0=off, 1=on, -1=mixed
        self._is_enabled = True
        self._is_hidden = False
        self._is_alternate = False
        self._submenu: Optional[NSMenu] = None
        self._represented_object: Any = None
        self._indentation_level: int = 0
        self._tool_tip: Optional[str] = None
        self._image = None
        self._is_separator = False
        self._menu: Optional[NSMenu] = None

    @classmethod
    def separator(cls) -> NSMenuItem:
        item = cls()
        item._is_separator = True
        item._is_enabled = False
        return item

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str):
        self._title = v

    @property
    def action(self) -> Optional[str]:
        return self._action

    @action.setter
    def action(self, v: Optional[str]):
        self._action = v

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        self._target = v

    @property
    def key_equivalent(self) -> str:
        return self._key_equivalent

    @key_equivalent.setter
    def key_equivalent(self, v: str):
        self._key_equivalent = v

    @property
    def tag(self) -> int:
        return self._tag

    @tag.setter
    def tag(self, v: int):
        self._tag = v

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, v: int):
        self._state = v

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, v: bool):
        self._is_enabled = v

    @property
    def is_hidden(self) -> bool:
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, v: bool):
        self._is_hidden = v

    @property
    def submenu(self) -> Optional[NSMenu]:
        return self._submenu

    @submenu.setter
    def submenu(self, m: Optional[NSMenu]):
        self._submenu = m

    @property
    def has_submenu(self) -> bool:
        return self._submenu is not None

    @property
    def represented_object(self):
        return self._represented_object

    @represented_object.setter
    def represented_object(self, v):
        self._represented_object = v

    @property
    def is_separator_item(self) -> bool:
        return self._is_separator

    def perform_action(self) -> bool:
        if not self._is_enabled or self._is_separator:
            return False
        if self._target and self._action:
            method = getattr(self._target, self._action, None)
            if method:
                method(self)
                return True
        return False

    def __repr__(self):
        if self._is_separator:
            return "<NSMenuItem separator>"
        return f"<NSMenuItem {self._title!r} key={self._key_equivalent!r}>"


class NSMenu:
    """A menu containing menu items."""

    def __init__(self, title: str = ""):
        self._title = title
        self._items: List[NSMenuItem] = []
        self._delegate = None
        self._supermenu: Optional[NSMenu] = None
        self._autoenables_items = True
        self._minimum_width: float = 0.0

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str):
        self._title = v

    @property
    def items(self) -> List[NSMenuItem]:
        return list(self._items)

    @property
    def number_of_items(self) -> int:
        return len(self._items)

    @property
    def supermenu(self) -> Optional[NSMenu]:
        return self._supermenu

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, d):
        self._delegate = d

    def add_item(self, item: NSMenuItem):
        item._menu = self
        self._items.append(item)

    def add_item_with_title(self, title: str, action: Optional[str] = None,
                            key_equivalent: str = "") -> NSMenuItem:
        item = NSMenuItem(title, action, key_equivalent)
        self.add_item(item)
        return item

    def insert_item(self, item: NSMenuItem, at_index: int):
        item._menu = self
        self._items.insert(at_index, item)

    def remove_item(self, item: NSMenuItem):
        if item in self._items:
            self._items.remove(item)

    def remove_item_at_index(self, index: int):
        if 0 <= index < len(self._items):
            self._items.pop(index)

    def item_at_index(self, index: int) -> Optional[NSMenuItem]:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def item_with_title(self, title: str) -> Optional[NSMenuItem]:
        for item in self._items:
            if item.title == title:
                return item
        return None

    def item_with_tag(self, tag: int) -> Optional[NSMenuItem]:
        for item in self._items:
            if item.tag == tag:
                return item
        return None

    def index_of_item(self, item: NSMenuItem) -> int:
        try:
            return self._items.index(item)
        except ValueError:
            return -1

    def remove_all_items(self):
        self._items.clear()

    def perform_key_equivalent(self, key: str, modifiers: int = 0) -> bool:
        """Attempt to match a key equivalent in this menu or its submenus."""
        for item in self._items:
            if item.key_equivalent == key:
                return item.perform_action()
            if item.has_submenu:
                if item.submenu.perform_key_equivalent(key, modifiers):
                    return True
        return False

    def __repr__(self):
        return f"<NSMenu {self._title!r} items={len(self._items)}>"
