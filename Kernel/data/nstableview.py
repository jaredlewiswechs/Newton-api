"""NSTableView — a column-based data view."""
from __future__ import annotations
from typing import Optional, List, Any, Protocol

from Kernel.view.nsview import NSView, NSRect


class NSTableViewDataSource(Protocol):
    """Protocol for providing data to a table view."""
    def number_of_rows(self, table_view: NSTableView) -> int: ...
    def object_value_for(self, table_view: NSTableView, column: NSTableColumn, row: int) -> Any: ...


class NSTableViewDelegate(Protocol):
    """Protocol for customizing table view behavior."""
    def view_for_table_column(self, table_view: NSTableView, column: NSTableColumn, row: int) -> Optional[NSView]: ...


class NSTableColumn:
    """A column in an NSTableView."""

    def __init__(self, identifier: str = ""):
        self._identifier = identifier
        self._title = identifier
        self._width: float = 100.0
        self._min_width: float = 40.0
        self._max_width: float = 1000.0
        self._is_hidden = False
        self._is_editable = False
        self._sort_descriptor_prototype = None
        self._header_cell = None
        self._table_view = None
        self._resizing_mask = 1  # user resizable

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, v: str):
        self._title = v

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, v: float):
        self._width = max(self._min_width, min(self._max_width, v))

    @property
    def min_width(self) -> float:
        return self._min_width

    @min_width.setter
    def min_width(self, v: float):
        self._min_width = v

    @property
    def max_width(self) -> float:
        return self._max_width

    @max_width.setter
    def max_width(self, v: float):
        self._max_width = v

    @property
    def is_hidden(self) -> bool:
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, v: bool):
        self._is_hidden = v

    @property
    def is_editable(self) -> bool:
        return self._is_editable

    @is_editable.setter
    def is_editable(self, v: bool):
        self._is_editable = v

    def __repr__(self):
        return f"<NSTableColumn {self._identifier!r} w={self._width}>"


class NSTableView(NSView):
    """A table that displays rows of data in columns."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._columns: List[NSTableColumn] = []
        self._data_source = None
        self._delegate = None
        self._row_height: float = 24.0
        self._intercell_spacing = (3.0, 2.0)  # width, height
        self._selected_row_indexes: List[int] = []
        self._allows_multiple_selection = False
        self._allows_empty_selection = True
        self._allows_column_reordering = True
        self._allows_column_resizing = True
        self._uses_alternating_row_background_colors = False
        self._grid_style_mask = 0
        self._header_view = None
        self._corner_view = None
        self._sort_descriptors: list = []
        self._number_of_rows: int = 0
        self._cached_rows: List[List[Any]] = []

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
    def intercell_spacing(self):
        return self._intercell_spacing

    @intercell_spacing.setter
    def intercell_spacing(self, v):
        self._intercell_spacing = v

    @property
    def number_of_rows(self) -> int:
        if self._data_source:
            return self._data_source.number_of_rows(self)
        return self._number_of_rows

    @property
    def number_of_columns(self) -> int:
        return len(self._columns)

    @property
    def columns(self) -> List[NSTableColumn]:
        return list(self._columns)

    @property
    def selected_row(self) -> int:
        return self._selected_row_indexes[0] if self._selected_row_indexes else -1

    @property
    def selected_row_indexes(self) -> List[int]:
        return list(self._selected_row_indexes)

    def add_table_column(self, column: NSTableColumn):
        column._table_view = self
        self._columns.append(column)

    def remove_table_column(self, column: NSTableColumn):
        if column in self._columns:
            self._columns.remove(column)

    def column_with_identifier(self, identifier: str) -> Optional[NSTableColumn]:
        for c in self._columns:
            if c.identifier == identifier:
                return c
        return None

    def select_row_indexes(self, indexes: List[int], extending: bool = False):
        if not extending:
            self._selected_row_indexes.clear()
        for i in indexes:
            if i not in self._selected_row_indexes:
                self._selected_row_indexes.append(i)

    def deselect_row(self, row: int):
        if row in self._selected_row_indexes:
            self._selected_row_indexes.remove(row)

    def deselect_all(self, sender=None):
        self._selected_row_indexes.clear()

    def reload_data(self):
        self._cached_rows.clear()
        if self._data_source:
            n = self._data_source.number_of_rows(self)
            for r in range(n):
                row_data = []
                for col in self._columns:
                    row_data.append(self._data_source.object_value_for(self, col, r))
                self._cached_rows.append(row_data)
        self.set_needs_display()

    def row_at_point(self, point) -> int:
        y = point[1] if isinstance(point, (tuple, list)) else point
        header_h = 20.0
        row = int((y - header_h) / (self._row_height + self._intercell_spacing[1]))
        if 0 <= row < self.number_of_rows:
            return row
        return -1

    def handle_mouse_down(self, event) -> bool:
        if event.location:
            row = self.row_at_point(event.location)
            if row >= 0:
                self.select_row_indexes([row])
                self.send_action()
                return True
        return False

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        parts = []
        parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="white" stroke="#ccc" />')
        # header
        x = 0.0
        header_h = 20.0
        for col in self._columns:
            if col.is_hidden:
                continue
            parts.append(f'<rect x="{x}" y="0" width="{col.width}" height="{header_h}" '
                         f'fill="#f0f0f0" stroke="#ccc" stroke-width="0.5" />')
            parts.append(f'<text x="{x + 4}" y="14" font-size="11" '
                         f'font-family="sans-serif" font-weight="bold">{col.title}</text>')
            x += col.width + self._intercell_spacing[0]
        # rows
        if self._data_source:
            self.reload_data()
        for r, row_data in enumerate(self._cached_rows):
            ry = header_h + r * (self._row_height + self._intercell_spacing[1])
            bg = "#d0e0ff" if r in self._selected_row_indexes else (
                "#f8f8f8" if r % 2 and self._uses_alternating_row_background_colors else "white"
            )
            parts.append(f'<rect x="0" y="{ry}" width="{w}" height="{self._row_height}" fill="{bg}" />')
            cx = 0.0
            for ci, col in enumerate(self._columns):
                if col.is_hidden:
                    continue
                val = row_data[ci] if ci < len(row_data) else ""
                parts.append(f'<text x="{cx + 4}" y="{ry + 16}" font-size="12" '
                             f'font-family="sans-serif">{val}</text>')
                cx += col.width + self._intercell_spacing[0]
        return "\n".join(parts)

    def __repr__(self):
        return f"<NSTableView cols={len(self._columns)} rows={self.number_of_rows}>"
