"""NSTextView — an editable, scrollable text view."""
from __future__ import annotations
from typing import Optional, List, Tuple

from Kernel.view.nsview import NSView, NSRect
from Kernel.runtime.event import NSEvent, NSEventType
from .nsfont import NSFont
from .nstextstorage import NSTextStorage
from .nslayoutmanager import NSLayoutManager, NSTextContainer


class NSTextView(NSView):
    """A multi-line editable text view backed by NSTextStorage + NSLayoutManager."""

    def __init__(self, frame: Optional[NSRect] = None, text: str = ""):
        super().__init__(frame)
        # set up the text system
        self._text_storage = NSTextStorage(text)
        self._layout_manager = NSLayoutManager()
        self._text_container = NSTextContainer()
        if frame:
            from Kernel.view.nsview import NSSize
            self._text_container.size = NSSize(frame.width, frame.height)
        self._text_storage.add_layout_manager(self._layout_manager)
        self._layout_manager.add_text_container(self._text_container)
        self._text_container._text_view = self

        self._font = NSFont.system_font(13.0)
        self._text_color = None
        self._background_color_tv = None
        self._is_editable = True
        self._is_selectable = True
        self._is_rich_text = False
        self._is_field_editor = False
        self._insertion_point: int = len(text)
        self._selection_range: Tuple[int, int] = (len(text), 0)  # (start, length)
        self._delegate = None
        self._allows_undo = True
        self._is_automatically_link_detection_enabled = False
        self._uses_find_bar = False
        self._continuous_spell_checking_enabled = False

    # ── text content ──────────────────────────────────────────────

    @property
    def string(self) -> str:
        return self._text_storage.string

    @string.setter
    def string(self, v: str):
        self._text_storage.string = v
        self._insertion_point = len(v)

    @property
    def text_storage(self) -> NSTextStorage:
        return self._text_storage

    @property
    def layout_manager(self) -> NSLayoutManager:
        return self._layout_manager

    @property
    def text_container(self) -> NSTextContainer:
        return self._text_container

    @property
    def font(self) -> NSFont:
        return self._font

    @font.setter
    def font(self, f: NSFont):
        self._font = f
        self._layout_manager._char_width = f.point_size * 0.6
        self._layout_manager._line_height = f.line_height
        self._layout_manager._needs_layout = True

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, c):
        self._text_color = c

    @property
    def is_editable(self) -> bool:
        return self._is_editable

    @is_editable.setter
    def is_editable(self, v: bool):
        self._is_editable = v

    @property
    def is_selectable(self) -> bool:
        return self._is_selectable

    @is_selectable.setter
    def is_selectable(self, v: bool):
        self._is_selectable = v

    @property
    def is_rich_text(self) -> bool:
        return self._is_rich_text

    @is_rich_text.setter
    def is_rich_text(self, v: bool):
        self._is_rich_text = v

    # ── selection ─────────────────────────────────────────────────

    @property
    def selected_range(self) -> Tuple[int, int]:
        return self._selection_range

    @selected_range.setter
    def selected_range(self, v: Tuple[int, int]):
        self._selection_range = v
        self._insertion_point = v[0] + v[1]

    def select_all(self, sender=None):
        self._selection_range = (0, len(self._text_storage.string))
        self._insertion_point = len(self._text_storage.string)

    @property
    def insertion_point(self) -> int:
        return self._insertion_point

    # ── editing ───────────────────────────────────────────────────

    def insert_text(self, text: str):
        if not self._is_editable:
            return
        start, length = self._selection_range
        self._text_storage.replace_characters_in_range(start, length, text)
        self._insertion_point = start + len(text)
        self._selection_range = (self._insertion_point, 0)
        self.set_needs_display()

    def delete_backward(self, sender=None):
        if not self._is_editable:
            return
        start, length = self._selection_range
        if length > 0:
            self._text_storage.delete_characters_in_range(start, length)
            self._insertion_point = start
        elif self._insertion_point > 0:
            self._text_storage.delete_characters_in_range(self._insertion_point - 1, 1)
            self._insertion_point -= 1
        self._selection_range = (self._insertion_point, 0)
        self.set_needs_display()

    def delete_forward(self, sender=None):
        if not self._is_editable:
            return
        start, length = self._selection_range
        if length > 0:
            self._text_storage.delete_characters_in_range(start, length)
            self._insertion_point = start
        elif self._insertion_point < len(self._text_storage.string):
            self._text_storage.delete_characters_in_range(self._insertion_point, 1)
        self._selection_range = (self._insertion_point, 0)
        self.set_needs_display()

    # ── event handling ────────────────────────────────────────────

    def handle_key_down(self, event: NSEvent) -> bool:
        if not self._is_editable:
            return False
        if event.user_info:
            key = event.user_info.get('key', '')
            if key == 'backspace':
                self.delete_backward()
                return True
            elif key == 'delete':
                self.delete_forward()
                return True
            elif key == 'left':
                self._insertion_point = max(0, self._insertion_point - 1)
                self._selection_range = (self._insertion_point, 0)
                return True
            elif key == 'right':
                self._insertion_point = min(len(self._text_storage.string), self._insertion_point + 1)
                self._selection_range = (self._insertion_point, 0)
                return True
            elif len(key) == 1 or key in ('enter', 'return'):
                text = '\n' if key in ('enter', 'return') else key
                self.insert_text(text)
                return True
        return False

    def handle_mouse_down(self, event: NSEvent) -> bool:
        if event.location:
            idx = self._layout_manager.character_index_for_point(
                event.location, self._text_container)
            self._insertion_point = idx
            self._selection_range = (idx, 0)
        if self._window:
            self._window.make_first_responder(self)
        return True

    # ── drawing ───────────────────────────────────────────────────

    def draw(self, rect=None) -> str:
        self._layout_manager.ensure_layout()
        w, h = self._bounds.width, self._bounds.height
        parts = []
        # background
        parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="white" '
                     f'stroke="#aaa" stroke-width="1" />')
        # render each layout line
        text = self._text_storage.string
        for line in self._layout_manager._lines:
            chunk = text[line.char_start:line.char_end]
            # escape XML
            chunk = chunk.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            ty = line.origin_y + line.height * 0.75
            parts.append(f'<text x="{line.origin_x}" y="{ty}" '
                         f'font-size="{self._font.point_size}" '
                         f'font-family="{self._font.family_name}">{chunk}</text>')
        return "\n".join(parts)

    def __repr__(self):
        preview = self._text_storage.string[:30]
        return f"<NSTextView len={len(self._text_storage.string)} {preview!r}...>"
