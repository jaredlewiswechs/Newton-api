"""NSTextStorage — the mutable attributed string backing a text view."""
from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple


class NSTextStorage:
    """Stores the text content and attributes for the text system.

    This is a simplified version: it stores plain text with per-range
    attribute dictionaries. For full rich text, this would wrap
    NSMutableAttributedString.
    """

    def __init__(self, string: str = ""):
        self._string = string
        # attributes stored as list of (range_start, range_end, attrs_dict)
        self._attributes: List[Tuple[int, int, Dict[str, Any]]] = []
        self._layout_managers: List[Any] = []  # NSLayoutManager instances
        self._delegate = None
        self._editing_count = 0

    @property
    def string(self) -> str:
        return self._string

    @string.setter
    def string(self, v: str):
        self.begin_editing()
        old_len = len(self._string)
        self._string = v
        self._edited(old_len, len(v))
        self.end_editing()

    @property
    def length(self) -> int:
        return len(self._string)

    def add_layout_manager(self, lm):
        if lm not in self._layout_managers:
            self._layout_managers.append(lm)
            lm._text_storage = self

    def remove_layout_manager(self, lm):
        if lm in self._layout_managers:
            self._layout_managers.remove(lm)

    @property
    def layout_managers(self):
        return list(self._layout_managers)

    # ── editing ───────────────────────────────────────────────────

    def begin_editing(self):
        self._editing_count += 1

    def end_editing(self):
        self._editing_count -= 1
        if self._editing_count <= 0:
            self._editing_count = 0
            self._notify_layout_managers()

    def _edited(self, old_length: int, new_length: int):
        pass

    def _notify_layout_managers(self):
        for lm in self._layout_managers:
            if hasattr(lm, 'text_storage_did_change'):
                lm.text_storage_did_change(self)

    # ── text mutations ────────────────────────────────────────────

    def replace_characters_in_range(self, start: int, length: int, string: str):
        self.begin_editing()
        old_len = len(self._string)
        self._string = self._string[:start] + string + self._string[start + length:]
        self._edited(old_len, len(self._string))
        self.end_editing()

    def insert_string(self, string: str, at: int):
        self.replace_characters_in_range(at, 0, string)

    def delete_characters_in_range(self, start: int, length: int):
        self.replace_characters_in_range(start, length, "")

    def append_string(self, string: str):
        self.insert_string(string, len(self._string))

    # ── attributes ────────────────────────────────────────────────

    def add_attribute(self, name: str, value: Any, range_start: int, range_length: int):
        self._attributes.append((range_start, range_start + range_length, {name: value}))

    def set_attributes(self, attrs: Dict[str, Any], range_start: int, range_length: int):
        # remove existing overlapping, then add new
        end = range_start + range_length
        self._attributes = [
            (s, e, a) for (s, e, a) in self._attributes
            if e <= range_start or s >= end
        ]
        self._attributes.append((range_start, end, dict(attrs)))

    def attributes_at_index(self, index: int) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for start, end, attrs in self._attributes:
            if start <= index < end:
                result.update(attrs)
        return result

    def attribute(self, name: str, at_index: int) -> Any:
        return self.attributes_at_index(at_index).get(name)

    # ── substring ─────────────────────────────────────────────────

    def substring_with_range(self, start: int, length: int) -> str:
        return self._string[start:start + length]

    @property
    def words(self) -> List[str]:
        return self._string.split()

    @property
    def lines(self) -> List[str]:
        return self._string.split('\n')

    def __repr__(self):
        preview = self._string[:40] + "..." if len(self._string) > 40 else self._string
        return f"<NSTextStorage length={len(self._string)} {preview!r}>"
