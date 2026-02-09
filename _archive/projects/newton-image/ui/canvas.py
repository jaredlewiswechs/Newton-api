"""
═══════════════════════════════════════════════════════════════
NCANVAS - THE CREATIVE SURFACE
Where pixels meet verification.
Smooth pan, zoom, and infinite creativity.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Tuple, List
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QImage, QPixmap,
    QMouseEvent, QWheelEvent, QPaintEvent, QKeyEvent,
    QTransform, QCursor
)

import sys
sys.path.insert(0, '..')
from core.document import NDocument, NLayer
from core.tools import NTool, ToolType, NBrushTool, NEraserTool, NEyedropperTool


class NCanvas(QWidget):
    """
    The main canvas widget for image editing.
    
    Features:
    - Smooth pan and zoom
    - Tool interactions
    - Layer-aware rendering
    - Checker pattern for transparency
    """
    
    # Signals
    tool_used = pyqtSignal(str, object)  # tool_name, stroke data
    color_picked = pyqtSignal(object)  # QColor
    zoom_changed = pyqtSignal(float)
    position_changed = pyqtSignal(int, int)  # x, y in document coords
    
    # Zoom limits
    MIN_ZOOM = 0.1
    MAX_ZOOM = 32.0
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Document
        self._document: Optional[NDocument] = None
        
        # View transform
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        
        # Interaction state
        self._dragging = False
        self._panning = False
        self._space_pressed = False
        self._last_pos: Optional[QPointF] = None
        
        # Current tool
        self._tool: Optional[NTool] = None
        
        # Colors
        self._foreground_color = QColor(0, 0, 0)
        self._background_color = QColor(255, 255, 255)
        
        # Stroke buffer for undo
        self._stroke_buffer: Optional[QImage] = None
        
        # Setup
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(400, 300)
        
        # Background colors (checkerboard for transparency)
        self._checker_light = QColor(255, 255, 255)
        self._checker_dark = QColor(204, 204, 204)
        self._checker_size = 16
        
        # Canvas background
        self._canvas_bg = QColor(83, 83, 83)  # Dark gray like Photoshop
    
    # ═══════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════
    
    @property
    def document(self) -> Optional[NDocument]:
        return self._document
    
    @document.setter
    def document(self, doc: Optional[NDocument]) -> None:
        self._document = doc
        if doc:
            doc.changed.connect(self._on_document_changed)
            self._center_document()
        self.update()
    
    @property
    def zoom(self) -> float:
        return self._zoom
    
    @zoom.setter
    def zoom(self, value: float) -> None:
        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, value))
        if self._zoom != value:
            self._zoom = value
            self.zoom_changed.emit(value)
            self.update()
    
    @property
    def tool(self) -> Optional[NTool]:
        return self._tool
    
    @tool.setter
    def tool(self, t: Optional[NTool]) -> None:
        if self._tool:
            self._tool.cancel_stroke()
        self._tool = t
        self._update_cursor()
    
    @property
    def foreground_color(self) -> QColor:
        return self._foreground_color
    
    @foreground_color.setter
    def foreground_color(self, color: QColor) -> None:
        self._foreground_color = color
        if isinstance(self._tool, NBrushTool):
            self._tool.color = color
    
    @property
    def background_color(self) -> QColor:
        return self._background_color
    
    @background_color.setter
    def background_color(self, color: QColor) -> None:
        self._background_color = color
    
    # ═══════════════════════════════════════════════════════════
    # COORDINATE TRANSFORMS
    # ═══════════════════════════════════════════════════════════
    
    def widget_to_document(self, pos: QPointF) -> QPointF:
        """Convert widget coordinates to document coordinates."""
        return QPointF(
            (pos.x() - self._pan_x) / self._zoom,
            (pos.y() - self._pan_y) / self._zoom
        )
    
    def document_to_widget(self, pos: QPointF) -> QPointF:
        """Convert document coordinates to widget coordinates."""
        return QPointF(
            pos.x() * self._zoom + self._pan_x,
            pos.y() * self._zoom + self._pan_y
        )
    
    def _get_document_rect(self) -> QRectF:
        """Get the document rectangle in widget coordinates."""
        if not self._document:
            return QRectF()
        
        return QRectF(
            self._pan_x,
            self._pan_y,
            self._document.width * self._zoom,
            self._document.height * self._zoom
        )
    
    # ═══════════════════════════════════════════════════════════
    # VIEW CONTROLS
    # ═══════════════════════════════════════════════════════════
    
    def _center_document(self) -> None:
        """Center the document in the view."""
        if not self._document:
            return
        
        doc_w = self._document.width * self._zoom
        doc_h = self._document.height * self._zoom
        
        self._pan_x = (self.width() - doc_w) / 2
        self._pan_y = (self.height() - doc_h) / 2
    
    def fit_in_view(self) -> None:
        """Zoom to fit document in view."""
        if not self._document:
            return
        
        margin = 40
        available_w = self.width() - margin * 2
        available_h = self.height() - margin * 2
        
        zoom_w = available_w / self._document.width
        zoom_h = available_h / self._document.height
        
        self.zoom = min(zoom_w, zoom_h)
        self._center_document()
        self.update()
    
    def zoom_in(self) -> None:
        """Zoom in by 25%."""
        self.zoom *= 1.25
    
    def zoom_out(self) -> None:
        """Zoom out by 25%."""
        self.zoom /= 1.25
    
    def zoom_to_100(self) -> None:
        """Reset to 100% zoom."""
        self.zoom = 1.0
        self._center_document()
        self.update()
    
    # ═══════════════════════════════════════════════════════════
    # TOOL INTERACTIONS
    # ═══════════════════════════════════════════════════════════
    
    def _start_stroke(self, pos: QPointF) -> None:
        """Begin a paint stroke."""
        if not self._document or not self._tool or not self._document.active_layer:
            return
        
        layer = self._document.active_layer
        doc_pos = self.widget_to_document(pos)
        
        # Handle eyedropper separately - doesn't need layer unlock
        if isinstance(self._tool, NEyedropperTool):
            color = self._tool.sample(layer.image, doc_pos)
            self.color_picked.emit(color)
            return
        
        if layer.locked:
            return
        
        # Save layer state for undo
        from PyQt6.QtCore import QBuffer, QIODevice
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        layer.image.save(buffer, "PNG")
        self._stroke_buffer = bytes(buffer.data())
        
        # Begin stroke
        self._tool.begin_stroke(doc_pos)
        self._dragging = True
    
    def _continue_stroke(self, pos: QPointF) -> None:
        """Continue a paint stroke."""
        if not self._dragging or not self._tool or not self._document:
            return
        
        layer = self._document.active_layer
        if not layer or layer.locked:
            return
        
        doc_pos = self.widget_to_document(pos)
        self._tool.continue_stroke(doc_pos)
        
        # Apply stroke segment
        if isinstance(self._tool, NBrushTool):
            points = self._tool._stroke_points[-2:] if len(self._tool._stroke_points) >= 2 else []
            if len(points) == 2:
                self._tool.paint_stroke(layer.image, points)
                layer.changed.emit()
        elif isinstance(self._tool, NEraserTool):
            points = self._tool._stroke_points[-2:] if len(self._tool._stroke_points) >= 2 else []
            if len(points) == 2:
                self._tool.erase_stroke(layer.image, points)
                layer.changed.emit()
    
    def _end_stroke(self) -> None:
        """End a paint stroke."""
        if not self._dragging or not self._tool:
            self._dragging = False
            return
        
        points = self._tool.end_stroke()
        self._dragging = False
        
        if self._stroke_buffer and self._document and self._document.active_layer:
            # Record to history (would connect to history manager)
            self.tool_used.emit(self._tool.name, {
                'layer_id': self._document.active_layer.id,
                'points': [(p.x(), p.y()) for p in points],
                'before_state': self._stroke_buffer
            })
        
        self._stroke_buffer = None
    
    def _update_cursor(self) -> None:
        """Update cursor based on current tool."""
        if self._space_pressed or self._panning:
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        elif self._tool:
            if self._tool.tool_type in (ToolType.BRUSH, ToolType.ERASER):
                # Could create custom brush cursor
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            elif self._tool.tool_type == ToolType.MOVE:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            elif self._tool.tool_type == ToolType.EYEDROPPER:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            elif self._tool.tool_type in (ToolType.SELECT_RECT, ToolType.SELECT_LASSO):
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    # ═══════════════════════════════════════════════════════════
    # EVENTS
    # ═══════════════════════════════════════════════════════════
    
    def _on_document_changed(self) -> None:
        """Handle document changes."""
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = QPointF(event.position())
        
        if event.button() == Qt.MouseButton.MiddleButton or self._space_pressed:
            # Begin panning
            self._panning = True
            self._last_pos = pos
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        elif event.button() == Qt.MouseButton.LeftButton:
            # Tool interaction
            self._start_stroke(pos)
            self._last_pos = pos
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = QPointF(event.position())
        
        if self._panning and self._last_pos:
            # Pan the view
            delta = pos - self._last_pos
            self._pan_x += delta.x()
            self._pan_y += delta.y()
            self._last_pos = pos
            self.update()
        elif self._dragging:
            # Continue stroke
            self._continue_stroke(pos)
            self._last_pos = pos
        else:
            # Just moving - update position display
            doc_pos = self.widget_to_document(pos)
            self.position_changed.emit(int(doc_pos.x()), int(doc_pos.y()))
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton or self._panning:
            self._panning = False
            self._update_cursor()
        elif event.button() == Qt.MouseButton.LeftButton:
            self._end_stroke()
        
        self._last_pos = None
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        # Zoom centered on cursor
        pos = QPointF(event.position())
        doc_pos_before = self.widget_to_document(pos)
        
        # Calculate zoom delta
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 1 / 1.1
        
        self._zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self._zoom * factor))
        
        # Adjust pan to keep cursor position stable
        doc_pos_after = self.widget_to_document(pos)
        self._pan_x += (doc_pos_after.x() - doc_pos_before.x()) * self._zoom
        self._pan_y += (doc_pos_after.y() - doc_pos_before.y()) * self._zoom
        
        self.zoom_changed.emit(self._zoom)
        self.update()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = True
            self._update_cursor()
        elif event.key() == Qt.Key.Key_0:
            self.zoom_to_100()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = False
            self._update_cursor()
        else:
            super().keyReleaseEvent(event)
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._document:
            self._center_document()
    
    # ═══════════════════════════════════════════════════════════
    # PAINTING
    # ═══════════════════════════════════════════════════════════
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Draw background
        painter.fillRect(self.rect(), self._canvas_bg)
        
        if not self._document:
            # Draw "No document" message
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "No document open\nFile → New to create")
            return
        
        # Get document rect
        doc_rect = self._get_document_rect()
        
        # Draw document shadow
        shadow_offset = 4
        shadow_rect = doc_rect.adjusted(shadow_offset, shadow_offset, 
                                        shadow_offset, shadow_offset)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 60))
        
        # Draw checkerboard for transparency
        self._draw_checker(painter, doc_rect)
        
        # Draw document
        rendered = self._document.render_to_pixmap()
        painter.drawPixmap(doc_rect.toRect(), rendered)
        
        # Draw document border
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(doc_rect)
        
        # Draw brush cursor preview if applicable
        if self._tool and self._tool.tool_type in (ToolType.BRUSH, ToolType.ERASER):
            if hasattr(self._tool, 'settings'):
                cursor_pos = self.mapFromGlobal(QCursor.pos())
                size = self._tool.settings.size * self._zoom
                painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(
                    QPointF(cursor_pos.x(), cursor_pos.y()),
                    size / 2, size / 2
                )
                painter.setPen(QPen(QColor(0, 0, 0, 180), 1))
                painter.drawEllipse(
                    QPointF(cursor_pos.x(), cursor_pos.y()),
                    size / 2 - 1, size / 2 - 1
                )
    
    def _draw_checker(self, painter: QPainter, rect: QRectF) -> None:
        """Draw transparency checkerboard."""
        painter.save()
        painter.setClipRect(rect)
        
        size = self._checker_size * self._zoom
        size = max(4, min(32, size))  # Clamp size
        
        cols = int(rect.width() / size) + 2
        rows = int(rect.height() / size) + 2
        
        for row in range(rows):
            for col in range(cols):
                x = rect.x() + col * size
                y = rect.y() + row * size
                
                color = self._checker_light if (row + col) % 2 == 0 else self._checker_dark
                painter.fillRect(QRectF(x, y, size, size), color)
        
        painter.restore()
