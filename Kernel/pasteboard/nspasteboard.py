"""NSPasteboard — the system pasteboard (clipboard) abstraction."""
from __future__ import annotations
from typing import Optional, List, Any, Dict


class NSPasteboardType:
    STRING = "public.utf8-plain-text"
    HTML = "public.html"
    RTF = "public.rtf"
    PDF = "com.adobe.pdf"
    PNG = "public.png"
    TIFF = "public.tiff"
    FILE_URL = "public.file-url"
    URL = "public.url"
    COLOR = "com.apple.cocoa.pasteboard.color"
    SOUND = "com.apple.cocoa.pasteboard.sound"
    MULTIPLE_TEXT_SELECTION = "com.apple.cocoa.pasteboard.multiple-text-selection"
    FIND_PANEL_SEARCH = "com.apple.cocoa.pasteboard.find"


class NSPasteboardItem:
    """A single item on the pasteboard with typed representations."""

    def __init__(self):
        self._types: Dict[str, Any] = {}

    def set_string(self, string: str, for_type: str = NSPasteboardType.STRING):
        self._types[for_type] = string

    def string_for_type(self, type: str) -> Optional[str]:
        v = self._types.get(type)
        return str(v) if v is not None else None

    def set_data(self, data: bytes, for_type: str):
        self._types[for_type] = data

    def data_for_type(self, type: str) -> Optional[bytes]:
        v = self._types.get(type)
        return v if isinstance(v, bytes) else None

    @property
    def types(self) -> List[str]:
        return list(self._types.keys())

    def set_property_list(self, plist: Any, for_type: str):
        self._types[for_type] = plist

    def property_list_for_type(self, type: str) -> Any:
        return self._types.get(type)


class NSPasteboard:
    """System pasteboard for copy/paste operations.

    Supports named pasteboards (general, drag, find) and
    multiple typed items.
    """

    _pasteboards: Dict[str, NSPasteboard] = {}

    def __init__(self, name: str = "general"):
        self._name = name
        self._items: List[NSPasteboardItem] = []
        self._change_count: int = 0

    @classmethod
    def general(cls) -> NSPasteboard:
        if 'general' not in cls._pasteboards:
            cls._pasteboards['general'] = cls('general')
        return cls._pasteboards['general']

    @classmethod
    def pasteboard_with_name(cls, name: str) -> NSPasteboard:
        if name not in cls._pasteboards:
            cls._pasteboards[name] = cls(name)
        return cls._pasteboards[name]

    @property
    def name(self) -> str:
        return self._name

    @property
    def change_count(self) -> int:
        return self._change_count

    @property
    def pasteboard_items(self) -> List[NSPasteboardItem]:
        return list(self._items)

    @property
    def types(self) -> List[str]:
        all_types = set()
        for item in self._items:
            all_types.update(item.types)
        return sorted(all_types)

    def clear_contents(self) -> int:
        self._items.clear()
        self._change_count += 1
        return self._change_count

    def write_objects(self, objects: List[Any]) -> bool:
        self._change_count += 1
        for obj in objects:
            item = NSPasteboardItem()
            if isinstance(obj, str):
                item.set_string(obj)
            elif isinstance(obj, NSPasteboardItem):
                item = obj
            elif hasattr(obj, 'pasteboard_property_list'):
                item.set_property_list(obj.pasteboard_property_list(), NSPasteboardType.STRING)
            self._items.append(item)
        return True

    def set_string(self, string: str, for_type: str = NSPasteboardType.STRING) -> bool:
        self.clear_contents()
        item = NSPasteboardItem()
        item.set_string(string, for_type)
        self._items.append(item)
        return True

    def string_for_type(self, type: str = NSPasteboardType.STRING) -> Optional[str]:
        for item in self._items:
            s = item.string_for_type(type)
            if s is not None:
                return s
        return None

    def set_data(self, data: bytes, for_type: str) -> bool:
        item = NSPasteboardItem()
        item.set_data(data, for_type)
        self._items.append(item)
        return True

    def data_for_type(self, type: str) -> Optional[bytes]:
        for item in self._items:
            d = item.data_for_type(type)
            if d is not None:
                return d
        return None

    def can_read_item_with_data_conforming_to_types(self, types: List[str]) -> bool:
        available = set(self.types)
        return bool(available.intersection(types))

    def __repr__(self):
        return f"<NSPasteboard {self._name!r} items={len(self._items)} change={self._change_count}>"
