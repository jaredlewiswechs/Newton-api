"""
═══════════════════════════════════════════════════════════════
NDOCK - THE DOCK
Magnifying dock with app launchers.
Each dock item is an NObject.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List, Callable, Dict, Any
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QMouseEvent, QPaintEvent, QFont, QPixmap, QIcon

from core.nobject import NObject
from core.shapes import dock_shape, icon_shape


class DockItem(QWidget):
    """A single dock item - clickable app launcher."""
    
    clicked = pyqtSignal()
    
    def __init__(self, 
                 name: str,
                 icon: str = "🔲",
                 color: QColor = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Use composition for NObject
        self._nobject = NObject(object_type="DockItem")
        self._nobject.set_property('name', name)
        self._nobject.set_property('icon', icon)
        self._nobject.set_property('running', False)
        self._nobject.add_tag('dock-item')
        
        self._icon = icon
        self._name = name
        self._color = color or QColor(100, 100, 100)
        self._base_size = 48
        self._current_size = self._base_size
        self._hovered = False
        self._running = False
        
        self.setFixedSize(self._base_size + 8, self._base_size + 20)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Forward to NObject."""
        return self._nobject.get_property(name, default)
    
    def set_running(self, running: bool) -> None:
        """Set the running state (shows dot indicator)."""
        self._running = running
        self._nobject.set_property('running', running)
        if running:
            self._nobject.add_tag('running')
        else:
            self._nobject.remove_tag('running')
        self.update()
    
    def set_magnification(self, factor: float) -> None:
        """Set magnification factor (1.0 = normal, up to ~1.5 = magnified)."""
        self._current_size = int(self._base_size * factor)
        new_height = self._current_size + 20
        self.setFixedSize(self._current_size + 8, new_height)
        self.update()
    
    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
    
    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Icon background (squircle)
        icon_rect = QRectF(
            (self.width() - self._current_size) / 2,
            4,
            self._current_size,
            self._current_size
        )
        
        # Draw squircle background
        path = icon_shape(icon_rect)
        
        # Gradient or solid color
        bg_color = self._color
        if self._hovered:
            bg_color = bg_color.lighter(120)
        
        painter.fillPath(path, bg_color)
        
        # Draw icon (emoji for now)
        font_size = max(12, int(self._current_size * 0.5))
        painter.setFont(QFont("Segoe UI Emoji", font_size))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, self._icon)
        
        # Running indicator dot
        if self._running:
            dot_y = icon_rect.bottom() + 6
            dot_x = self.width() / 2
            painter.setBrush(QColor(80, 80, 80))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(dot_x - 2, dot_y, 4, 4))
        
        painter.end()


class NDock(QWidget):
    """
    The Newton OS Dock.
    
    Features:
    - Magnification on hover (like macOS)
    - Squircle app icons
    - Running app indicators
    - Smooth animations
    """
    
    app_launched = pyqtSignal(str)  # app name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Use composition for NObject
        self._nobject = NObject(object_type="NDock")
        self._nobject.add_tag('dock')
        self._nobject.add_tag('system')
        
        self._items: List[DockItem] = []
        self._magnification_range = 100  # pixels on each side
        self._max_magnification = 1.4
        
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 8, 12, 8)
        self._layout.setSpacing(4)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setFixedHeight(76)
    
    def add_item(self, name: str, icon: str = "🔲", 
                 color: QColor = None,
                 callback: Optional[Callable] = None) -> DockItem:
        """Add an item to the dock."""
        item = DockItem(name, icon, color, self)
        
        if callback:
            item.clicked.connect(callback)
        item.clicked.connect(lambda: self.app_launched.emit(name))
        
        self._items.append(item)
        self._layout.addWidget(item)
        
        self._update_size()
        return item
    
    def get_item(self, name: str) -> Optional[DockItem]:
        """Get a dock item by name."""
        for item in self._items:
            if item.get_property('name') == name:
                return item
        return None
    
    def _update_size(self) -> None:
        """Update dock width based on items."""
        total_width = len(self._items) * 56 + 24
        self.setFixedWidth(max(200, total_width))
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Apply magnification based on mouse position."""
        mouse_x = event.pos().x()
        
        for item in self._items:
            # Get item center
            item_center = item.x() + item.width() / 2
            distance = abs(mouse_x - item_center)
            
            if distance < self._magnification_range:
                # Calculate magnification (closer = bigger)
                factor = 1.0 + (self._max_magnification - 1.0) * (
                    1.0 - distance / self._magnification_range
                )
                item.set_magnification(factor)
            else:
                item.set_magnification(1.0)
        
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event) -> None:
        """Reset magnification when mouse leaves."""
        for item in self._items:
            item.set_magnification(1.0)
        super().leaveEvent(event)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw dock background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dock background (frosted glass effect)
        rect = QRectF(0, 0, self.width(), self.height())
        path = dock_shape(rect)
        
        # Semi-transparent background
        painter.fillPath(path, QColor(255, 255, 255, 180))
        
        # Border
        painter.setPen(QColor(200, 200, 200, 100))
        painter.drawPath(path)
        
        painter.end()
