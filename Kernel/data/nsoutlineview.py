"""NSOutlineView — a hierarchical data view (tree table)."""
from __future__ import annotations
from typing import Optional, List, Any, Protocol, Dict

from Kernel.view.nsview import NSView, NSRect


class NSOutlineViewDataSource(Protocol):
    def number_of_children(self, item: Any, outline_view: Any) -> int: ...
    def child(self, index: int, of_item: Any, outline_view: Any) -> Any: ...
    def is_item_expandable(self, item: Any, outline_view: Any) -> bool: ...
    def object_value_for(self, outline_view: Any, column: Any, item: Any) -> Any: ...


class NSOutlineViewDelegate(Protocol):
    pass


class NSOutlineView(NSView):
    """A tree-based outline view showing hierarchical data."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._data_source = None
        self._delegate = None
        self._row_height: float = 24.0
        self._indentation_per_level: float = 16.0
        self._expanded_items: set = set()
        self._selected_row_indexes: List[int] = []
        self._allows_multiple_selection = False
        self._outline_column = None
        self._flat_rows: List[dict] = []  # cached flat representation

    @property
    def data_source(self):
        return self._data_source

    @data_source.setter
    def data_source(self, ds):
        self._data_source = ds

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, d):
        self._delegate = d

    @property
    def row_height(self) -> float:
        return self._row_height

    @row_height.setter
    def row_height(self, v: float):
        self._row_height = v

    @property
    def indentation_per_level(self) -> float:
        return self._indentation_per_level

    @indentation_per_level.setter
    def indentation_per_level(self, v: float):
        self._indentation_per_level = v

    @property
    def number_of_rows(self) -> int:
        self._rebuild_flat()
        return len(self._flat_rows)

    def expand_item(self, item: Any, expand_children: bool = False):
        item_id = id(item)
        self._expanded_items.add(item_id)
        if expand_children and self._data_source:
            n = self._data_source.number_of_children(item, self)
            for i in range(n):
                child = self._data_source.child(i, item, self)
                if self._data_source.is_item_expandable(child, self):
                    self.expand_item(child, True)
        self._rebuild_flat()

    def collapse_item(self, item: Any, collapse_children: bool = False):
        item_id = id(item)
        self._expanded_items.discard(item_id)
        self._rebuild_flat()

    def is_item_expanded(self, item: Any) -> bool:
        return id(item) in self._expanded_items

    def is_expandable(self, item: Any) -> bool:
        if self._data_source:
            return self._data_source.is_item_expandable(item, self)
        return False

    def item_at_row(self, row: int) -> Any:
        self._rebuild_flat()
        if 0 <= row < len(self._flat_rows):
            return self._flat_rows[row]['item']
        return None

    def row_for_item(self, item: Any) -> int:
        self._rebuild_flat()
        for i, entry in enumerate(self._flat_rows):
            if entry['item'] is item:
                return i
        return -1

    def level_for_row(self, row: int) -> int:
        self._rebuild_flat()
        if 0 <= row < len(self._flat_rows):
            return self._flat_rows[row]['level']
        return -1

    def reload_data(self):
        self._flat_rows.clear()
        self._rebuild_flat()
        self.set_needs_display()

    def _rebuild_flat(self):
        if not self._data_source:
            return
        self._flat_rows.clear()
        self._walk(None, 0)

    def _walk(self, parent: Any, level: int):
        n = self._data_source.number_of_children(parent, self)
        for i in range(n):
            child = self._data_source.child(i, parent, self)
            expandable = self._data_source.is_item_expandable(child, self)
            expanded = id(child) in self._expanded_items
            self._flat_rows.append({
                'item': child,
                'level': level,
                'expandable': expandable,
                'expanded': expanded,
            })
            if expandable and expanded:
                self._walk(child, level + 1)

    def select_row_indexes(self, indexes: List[int], extending: bool = False):
        if not extending:
            self._selected_row_indexes.clear()
        for i in indexes:
            if i not in self._selected_row_indexes:
                self._selected_row_indexes.append(i)

    def draw(self, rect=None) -> str:
        self._rebuild_flat()
        w, h = self._bounds.width, self._bounds.height
        parts = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="white" stroke="#ccc" />']
        for r, entry in enumerate(self._flat_rows):
            ry = r * self._row_height
            indent = entry['level'] * self._indentation_per_level
            bg = "#d0e0ff" if r in self._selected_row_indexes else "white"
            parts.append(f'<rect x="0" y="{ry}" width="{w}" height="{self._row_height}" fill="{bg}" />')
            # disclosure triangle
            if entry['expandable']:
                tri = "▼" if entry['expanded'] else "▶"
                parts.append(f'<text x="{indent + 4}" y="{ry + 16}" font-size="10">{tri}</text>')
            label = str(entry['item'])
            parts.append(f'<text x="{indent + 20}" y="{ry + 16}" font-size="12" '
                         f'font-family="sans-serif">{label}</text>')
        return "\n".join(parts)

    def __repr__(self):
        return f"<NSOutlineView rows={self.number_of_rows}>"
