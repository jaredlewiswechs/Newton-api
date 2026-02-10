"""NSStackView and NSGridView — layout container views."""
from __future__ import annotations
from typing import Optional, List
from enum import Enum

from .nsview import NSView, NSRect


class NSUserInterfaceLayoutOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class NSStackViewDistribution(Enum):
    GRAVITY_AREAS = 0
    EQUAL_CENTERING = 1
    EQUAL_SPACING = 2
    FILL = 3
    FILL_EQUALLY = 4
    FILL_PROPORTIONALLY = 5


class NSStackView(NSView):
    """Arranges subviews in a horizontal or vertical stack."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._orientation = NSUserInterfaceLayoutOrientation.HORIZONTAL
        self._distribution = NSStackViewDistribution.FILL_EQUALLY
        self._spacing: float = 8.0
        self._edge_insets = (0.0, 0.0, 0.0, 0.0)  # top, left, bottom, right
        self._alignment = 0  # center
        self._arranged_subviews: List[NSView] = []

    @property
    def orientation(self) -> NSUserInterfaceLayoutOrientation:
        return self._orientation

    @orientation.setter
    def orientation(self, v: NSUserInterfaceLayoutOrientation):
        self._orientation = v
        self._layout_stack()

    @property
    def distribution(self) -> NSStackViewDistribution:
        return self._distribution

    @distribution.setter
    def distribution(self, v: NSStackViewDistribution):
        self._distribution = v
        self._layout_stack()

    @property
    def spacing(self) -> float:
        return self._spacing

    @spacing.setter
    def spacing(self, v: float):
        self._spacing = v
        self._layout_stack()

    @property
    def edge_insets(self):
        return self._edge_insets

    @edge_insets.setter
    def edge_insets(self, v):
        self._edge_insets = v
        self._layout_stack()

    def add_arranged_subview(self, view: NSView):
        self._arranged_subviews.append(view)
        self.add_subview(view)
        self._layout_stack()

    def remove_arranged_subview(self, view: NSView):
        if view in self._arranged_subviews:
            self._arranged_subviews.remove(view)
        view.remove_from_superview()
        self._layout_stack()

    def insert_arranged_subview(self, view: NSView, index: int):
        self._arranged_subviews.insert(index, view)
        self.add_subview(view)
        self._layout_stack()

    @property
    def arranged_subviews(self) -> List[NSView]:
        return list(self._arranged_subviews)

    def _layout_stack(self):
        n = len(self._arranged_subviews)
        if n == 0:
            return
        top, left, bottom, right = self._edge_insets
        if self._orientation == NSUserInterfaceLayoutOrientation.HORIZONTAL:
            avail = self._frame.width - left - right - self._spacing * (n - 1)
            each_w = avail / n if n else 0
            x = left
            for sv in self._arranged_subviews:
                sv.frame = NSRect(x, top, each_w, self._frame.height - top - bottom)
                x += each_w + self._spacing
        else:
            avail = self._frame.height - top - bottom - self._spacing * (n - 1)
            each_h = avail / n if n else 0
            y = top
            for sv in self._arranged_subviews:
                sv.frame = NSRect(left, y, self._frame.width - left - right, each_h)
                y += each_h + self._spacing

    def layout(self):
        self._layout_stack()
        super().layout()


class NSGridView(NSView):
    """A grid-based layout view that arranges subviews in rows and columns."""

    def __init__(self, frame: Optional[NSRect] = None, rows: int = 0, columns: int = 0):
        super().__init__(frame)
        self._rows: int = rows
        self._columns: int = columns
        self._cells: List[List[Optional[NSView]]] = [
            [None] * columns for _ in range(rows)
        ]
        self._row_spacing: float = 8.0
        self._column_spacing: float = 8.0

    @property
    def number_of_rows(self) -> int:
        return self._rows

    @property
    def number_of_columns(self) -> int:
        return self._columns

    @property
    def row_spacing(self) -> float:
        return self._row_spacing

    @row_spacing.setter
    def row_spacing(self, v: float):
        self._row_spacing = v

    @property
    def column_spacing(self) -> float:
        return self._column_spacing

    @column_spacing.setter
    def column_spacing(self, v: float):
        self._column_spacing = v

    def add_row(self, views: List[Optional[NSView]]):
        row = []
        for v in views:
            row.append(v)
            if v is not None:
                self.add_subview(v)
        while len(row) < self._columns:
            row.append(None)
        self._cells.append(row)
        self._rows += 1
        if len(views) > self._columns:
            self._columns = len(views)
            for r in self._cells[:-1]:
                while len(r) < self._columns:
                    r.append(None)
        self._layout_grid()

    def add_column(self, views: List[Optional[NSView]]):
        for i, v in enumerate(views):
            if i < self._rows:
                self._cells[i].append(v)
            else:
                new_row = [None] * self._columns + [v]
                self._cells.append(new_row)
                self._rows += 1
            if v is not None:
                self.add_subview(v)
        self._columns += 1
        for r in self._cells:
            while len(r) < self._columns:
                r.append(None)
        self._layout_grid()

    def cell_at(self, row: int, col: int) -> Optional[NSView]:
        if 0 <= row < self._rows and 0 <= col < self._columns:
            return self._cells[row][col]
        return None

    def _layout_grid(self):
        if self._rows == 0 or self._columns == 0:
            return
        avail_w = self._frame.width - self._column_spacing * (self._columns - 1)
        avail_h = self._frame.height - self._row_spacing * (self._rows - 1)
        cell_w = avail_w / self._columns
        cell_h = avail_h / self._rows
        for r in range(self._rows):
            for c in range(self._columns):
                v = self._cells[r][c]
                if v is not None:
                    v.frame = NSRect(
                        c * (cell_w + self._column_spacing),
                        r * (cell_h + self._row_spacing),
                        cell_w, cell_h,
                    )

    def layout(self):
        self._layout_grid()
        super().layout()
