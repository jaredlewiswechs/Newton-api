"""NSLayoutManager and NSTextContainer — text layout engine."""
from __future__ import annotations
from typing import Optional, List, Tuple, Any

from Kernel.view.nsview import NSRect, NSSize


class NSTextContainer:
    """Defines the region where text is laid out."""

    def __init__(self, size: Optional[NSSize] = None):
        self._size = size or NSSize(1e7, 1e7)  # effectively unbounded
        self._line_fragment_padding: float = 5.0
        self._maximum_number_of_lines: int = 0  # 0 = unlimited
        self._layout_manager = None
        self._text_view = None
        self._width_tracks_text_view = True
        self._height_tracks_text_view = False
        self._exclusion_paths: list = []

    @property
    def size(self) -> NSSize:
        return self._size

    @size.setter
    def size(self, v: NSSize):
        self._size = v

    @property
    def line_fragment_padding(self) -> float:
        return self._line_fragment_padding

    @line_fragment_padding.setter
    def line_fragment_padding(self, v: float):
        self._line_fragment_padding = v

    @property
    def maximum_number_of_lines(self) -> int:
        return self._maximum_number_of_lines

    @maximum_number_of_lines.setter
    def maximum_number_of_lines(self, v: int):
        self._maximum_number_of_lines = v

    @property
    def layout_manager(self):
        return self._layout_manager

    @property
    def text_view(self):
        return self._text_view

    @property
    def exclusion_paths(self):
        return list(self._exclusion_paths)

    @exclusion_paths.setter
    def exclusion_paths(self, v):
        self._exclusion_paths = list(v)


class _LayoutLine:
    """Internal representation of a laid-out line of text."""
    __slots__ = ('char_start', 'char_end', 'origin_x', 'origin_y', 'width', 'height')

    def __init__(self, char_start: int, char_end: int, x: float, y: float, w: float, h: float):
        self.char_start = char_start
        self.char_end = char_end
        self.origin_x = x
        self.origin_y = y
        self.width = w
        self.height = h


class NSLayoutManager:
    """Lays out text from an NSTextStorage into NSTextContainers.

    This is a simplified line-break layout manager. It:
    - Breaks text at newlines and wraps at the container width.
    - Computes line fragment rects.
    - Supports glyph-to-character and character-to-glyph mapping.
    """

    def __init__(self):
        self._text_storage = None
        self._text_containers: List[NSTextContainer] = []
        self._lines: List[_LayoutLine] = []
        self._needs_layout = True
        self._delegate = None
        self._char_width = 7.8  # approximate monospace char width at 13pt
        self._line_height = 17.0  # approximate line height at 13pt

    @property
    def text_storage(self):
        return self._text_storage

    @text_storage.setter
    def text_storage(self, ts):
        if self._text_storage:
            self._text_storage.remove_layout_manager(self)
        self._text_storage = ts
        if ts:
            ts.add_layout_manager(self)
        self._needs_layout = True

    def add_text_container(self, tc: NSTextContainer):
        tc._layout_manager = self
        self._text_containers.append(tc)
        self._needs_layout = True

    def remove_text_container(self, tc: NSTextContainer):
        if tc in self._text_containers:
            self._text_containers.remove(tc)

    @property
    def text_containers(self) -> List[NSTextContainer]:
        return list(self._text_containers)

    def text_storage_did_change(self, ts):
        self._needs_layout = True

    # ── layout ────────────────────────────────────────────────────

    def ensure_layout(self):
        if not self._needs_layout:
            return
        self._perform_layout()
        self._needs_layout = False

    def _perform_layout(self):
        self._lines.clear()
        if not self._text_storage or not self._text_containers:
            return
        text = self._text_storage.string
        if not text:
            return
        tc = self._text_containers[0]
        max_width = tc.size.width - 2 * tc.line_fragment_padding
        chars_per_line = max(1, int(max_width / self._char_width)) if max_width > 0 else len(text)

        y = 0.0
        idx = 0
        line_count = 0
        while idx < len(text):
            # find next newline
            nl = text.find('\n', idx)
            if nl == -1:
                nl = len(text)
            segment = text[idx:nl]
            # wrap segment
            while len(segment) > 0:
                chunk = segment[:chars_per_line]
                end_idx = idx + len(chunk)
                w = len(chunk) * self._char_width
                self._lines.append(_LayoutLine(idx, end_idx, tc.line_fragment_padding, y, w, self._line_height))
                y += self._line_height
                line_count += 1
                if tc.maximum_number_of_lines and line_count >= tc.maximum_number_of_lines:
                    return
                idx += len(chunk)
                segment = segment[len(chunk):]
            # account for the newline character
            if nl < len(text):
                idx = nl + 1
            else:
                break

    # ── queries ───────────────────────────────────────────────────

    @property
    def number_of_glyphs(self) -> int:
        return len(self._text_storage.string) if self._text_storage else 0

    def used_rect_for_text_container(self, tc: NSTextContainer) -> NSRect:
        self.ensure_layout()
        if not self._lines:
            return NSRect(0, 0, 0, 0)
        max_w = max(l.width for l in self._lines)
        total_h = self._lines[-1].origin_y + self._lines[-1].height
        return NSRect(0, 0, max_w + 2 * tc.line_fragment_padding, total_h)

    def line_fragment_rect(self, glyph_index: int) -> Optional[NSRect]:
        self.ensure_layout()
        for line in self._lines:
            if line.char_start <= glyph_index < line.char_end:
                return NSRect(line.origin_x, line.origin_y, line.width, line.height)
        return None

    def glyph_range_for_text_container(self, tc: NSTextContainer) -> Tuple[int, int]:
        self.ensure_layout()
        if not self._lines:
            return (0, 0)
        return (self._lines[0].char_start, self._lines[-1].char_end)

    def character_index_for_point(self, point: Tuple[float, float],
                                  text_container: NSTextContainer) -> int:
        self.ensure_layout()
        x, y = point
        for line in self._lines:
            if line.origin_y <= y < line.origin_y + line.height:
                char_offset = int((x - line.origin_x) / self._char_width)
                char_offset = max(0, min(char_offset, line.char_end - line.char_start - 1))
                return line.char_start + char_offset
        # past the end
        if self._lines:
            return self._lines[-1].char_end
        return 0

    def bounding_rect_for_glyph_range(self, start: int, length: int) -> NSRect:
        self.ensure_layout()
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = 0.0, 0.0
        end = start + length
        for line in self._lines:
            if line.char_end <= start or line.char_start >= end:
                continue
            ls = max(start, line.char_start) - line.char_start
            le = min(end, line.char_end) - line.char_start
            lx = line.origin_x + ls * self._char_width
            lw = (le - ls) * self._char_width
            min_x = min(min_x, lx)
            min_y = min(min_y, line.origin_y)
            max_x = max(max_x, lx + lw)
            max_y = max(max_y, line.origin_y + line.height)
        if min_x == float('inf'):
            return NSRect(0, 0, 0, 0)
        return NSRect(min_x, min_y, max_x - min_x, max_y - min_y)

    def __repr__(self):
        return f"<NSLayoutManager lines={len(self._lines)} glyphs={self.number_of_glyphs}>"
