"""NSCollectionView — a grid-based collection of items."""
from __future__ import annotations
from typing import Optional, List, Any, Protocol, Tuple

from Kernel.view.nsview import NSView, NSRect


class NSCollectionViewDataSource(Protocol):
    def number_of_items_in_section(self, collection_view: Any, section: int) -> int: ...
    def number_of_sections(self, collection_view: Any) -> int: ...
    def item_for(self, collection_view: Any, index_path: Tuple[int, int]) -> Any: ...


class NSCollectionViewItem(NSView):
    """A single item in a collection view."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._identifier: str = ""
        self._is_selected = False
        self._represented_object: Any = None
        self._text_field = None
        self._image_view = None

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, v: bool):
        self._is_selected = v

    @property
    def represented_object(self):
        return self._represented_object

    @represented_object.setter
    def represented_object(self, v):
        self._represented_object = v

    def draw(self, rect=None) -> str:
        w, h = self._bounds.width, self._bounds.height
        bg = "#d0e0ff" if self._is_selected else "#f0f0f0"
        label = str(self._represented_object) if self._represented_object else ""
        return (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="4" fill="{bg}" '
                f'stroke="#ccc" />'
                f'<text x="{w / 2}" y="{h / 2 + 4}" text-anchor="middle" '
                f'font-size="11" font-family="sans-serif">{label}</text>')


class NSCollectionView(NSView):
    """A grid-based view for displaying a collection of items."""

    def __init__(self, frame: Optional[NSRect] = None):
        super().__init__(frame)
        self._data_source = None
        self._delegate = None
        self._item_size = (80.0, 80.0)  # (width, height)
        self._min_item_size = (50.0, 50.0)
        self._max_item_size = (200.0, 200.0)
        self._inter_item_spacing: float = 8.0
        self._line_spacing: float = 8.0
        self._section_insets = (10.0, 10.0, 10.0, 10.0)  # top, left, bottom, right
        self._selection_indexes: List[Tuple[int, int]] = []
        self._allows_multiple_selection = False
        self._allows_empty_selection = True
        self._is_selectable = True
        self._items: List[NSCollectionViewItem] = []
        self._registered_classes: dict = {}

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
    def item_size(self):
        return self._item_size

    @item_size.setter
    def item_size(self, v):
        self._item_size = v

    @property
    def selection_index_paths(self) -> List[Tuple[int, int]]:
        return list(self._selection_indexes)

    def register_class(self, cls, identifier: str):
        self._registered_classes[identifier] = cls

    def make_item(self, identifier: str, index_path: Tuple[int, int]) -> NSCollectionViewItem:
        cls = self._registered_classes.get(identifier, NSCollectionViewItem)
        item = cls(NSRect(0, 0, self._item_size[0], self._item_size[1]))
        item._identifier = identifier
        return item

    def reload_data(self):
        # clear old items
        for item in self._items:
            item.remove_from_superview()
        self._items.clear()

        if not self._data_source:
            return

        top, left, bottom, right = self._section_insets
        num_sections = 1
        if hasattr(self._data_source, 'number_of_sections'):
            num_sections = self._data_source.number_of_sections(self)

        iw, ih = self._item_size
        avail_w = self._frame.width - left - right
        cols = max(1, int((avail_w + self._inter_item_spacing) / (iw + self._inter_item_spacing)))

        y = top
        for section in range(num_sections):
            n = self._data_source.number_of_items_in_section(self, section)
            for i in range(n):
                col = i % cols
                row = i // cols
                ix = left + col * (iw + self._inter_item_spacing)
                iy = y + row * (ih + self._line_spacing)
                item = NSCollectionViewItem(NSRect(ix, iy, iw, ih))
                index_path = (section, i)
                if self._data_source and hasattr(self._data_source, 'item_for'):
                    obj = self._data_source.item_for(self, index_path)
                    item.represented_object = obj
                item.is_selected = index_path in self._selection_indexes
                self._items.append(item)
                self.add_subview(item)
            if n > 0:
                total_rows = (n + cols - 1) // cols
                y += total_rows * (ih + self._line_spacing) + self._line_spacing
        self.set_needs_display()

    def select_items(self, index_paths: List[Tuple[int, int]], extending: bool = False):
        if not extending:
            self._selection_indexes.clear()
        for ip in index_paths:
            if ip not in self._selection_indexes:
                self._selection_indexes.append(ip)
        for item in self._items:
            item.is_selected = False
        for ip in self._selection_indexes:
            # find the item for this index path
            for item in self._items:
                if item.represented_object and ip in self._selection_indexes:
                    item.is_selected = True

    def item_at_index_path(self, index_path: Tuple[int, int]) -> Optional[NSCollectionViewItem]:
        section, idx = index_path
        flat_idx = idx  # simplified: single section
        if 0 <= flat_idx < len(self._items):
            return self._items[flat_idx]
        return None

    def handle_mouse_down(self, event) -> bool:
        if event.location:
            x, y = event.location
            for i, item in enumerate(self._items):
                if item.frame.contains(x, y):
                    ip = (0, i)
                    self.select_items([ip])
                    return True
        return False

    def __repr__(self):
        return f"<NSCollectionView items={len(self._items)}>"
