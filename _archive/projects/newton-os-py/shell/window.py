"""
═══════════════════════════════════════════════════════════════
NWINDOW - VERIFIED WINDOW
A window is an NObject with visual representation.
Real dragging, resizing, minimize, maximize, close.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Callable, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSizeGrip, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QPoint, QSize, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont, QMouseEvent, QPaintEvent, QResizeEvent

from core.nobject import NObject
from core.shapes import rounded_squircle_path


class NWindowTitleBar(QWidget):
    """Draggable title bar with traffic lights."""
    
    close_clicked = pyqtSignal()
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    
    def __init__(self, title: str = "Untitled", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title
        self._dragging = False
        self._drag_pos = QPoint()
        
        self.setFixedHeight(32)
        self.setMouseTracking(True)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # Traffic lights container
        traffic_lights = QHBoxLayout()
        traffic_lights.setSpacing(8)
        
        # Close button (red)
        self.btn_close = self._make_traffic_light(QColor(255, 96, 92), "×")
        self.btn_close.clicked.connect(self.close_clicked.emit)
        traffic_lights.addWidget(self.btn_close)
        
        # Minimize button (yellow)
        self.btn_minimize = self._make_traffic_light(QColor(255, 189, 68), "−")
        self.btn_minimize.clicked.connect(self.minimize_clicked.emit)
        traffic_lights.addWidget(self.btn_minimize)
        
        # Maximize button (green)
        self.btn_maximize = self._make_traffic_light(QColor(39, 201, 63), "+")
        self.btn_maximize.clicked.connect(self.maximize_clicked.emit)
        traffic_lights.addWidget(self.btn_maximize)
        
        layout.addLayout(traffic_lights)
        
        # Spacer
        layout.addStretch()
        
        # Title
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Balance the layout
        spacer = QWidget()
        spacer.setFixedWidth(72)  # Same width as traffic lights
        layout.addWidget(spacer)
    
    def _make_traffic_light(self, color: QColor, symbol: str) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(14, 14)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: none;
                border-radius: 7px;
                font-size: 10px;
                color: transparent;
            }}
            QPushButton:hover {{
                color: rgba(0, 0, 0, 0.5);
            }}
        """)
        btn.setText(symbol)
        return btn
    
    def set_title(self, title: str) -> None:
        self._title = title
        self.title_label.setText(title)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._dragging = False
        event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.maximize_clicked.emit()
        event.accept()


class NWindow(QWidget):
    """
    A Newton OS window - an NObject with visual representation.
    
    Features:
    - Squircle corners (continuous curvature)
    - Draggable title bar
    - Resizable edges and corners
    - Traffic light buttons (close/minimize/maximize)
    - Drop shadow
    - All state stored as NObject properties
    """
    
    closed = pyqtSignal()
    minimized = pyqtSignal()
    maximized = pyqtSignal()
    
    def __init__(self, 
                 title: str = "Untitled",
                 width: int = 400,
                 height: int = 300,
                 parent: Optional[QWidget] = None):
        # Initialize QWidget
        super().__init__(parent)
        
        # Use composition for NObject
        self._nobject = NObject(object_type="NWindow")
        
        # Window flags for frameless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Store properties in NObject
        self._nobject.set_property('title', title)
        self._nobject.set_property('width', width)
        self._nobject.set_property('height', height)
        self._nobject.set_property('visible', True)
        self._nobject.set_property('minimized', False)
        self._nobject.set_property('maximized', False)
        self._nobject.set_property('z', 0)
        
        self._nobject.add_tag('window')
        self._nobject.add_tag('visible')
        
        # Geometry state
        self._normal_geometry = None
        self._corner_radius = 12
        self._is_maximized = False
        
        # Resize handling
        self._resizing = False
        self._resize_edge = None
        self._resize_margin = 8
        
        # Setup UI
        self._setup_ui()
        self.resize(width, height)
    
    # NObject convenience properties
    @property
    def id(self) -> str:
        return self._nobject.id
    
    def get_property(self, name: str, default=None):
        return self._nobject.get_property(name, default)
    
    def set_property(self, name: str, value):
        return self._nobject.set_property(name, value)
    
    def add_tag(self, tag: str):
        self._nobject.add_tag(tag)
    
    def remove_tag(self, tag: str):
        self._nobject.remove_tag(tag)
    
    def _setup_ui(self) -> None:
        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Container (for background painting)
        self._container = QFrame()
        self._container.setObjectName("windowContainer")
        self._container.setStyleSheet("""
            #windowContainer {
                background-color: rgba(245, 245, 247, 0.95);
                border-radius: 12px;
            }
        """)
        
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        self._title_bar = NWindowTitleBar(self.get_property('title'))
        self._title_bar.close_clicked.connect(self._on_close)
        self._title_bar.minimize_clicked.connect(self._on_minimize)
        self._title_bar.maximize_clicked.connect(self._on_maximize)
        container_layout.addWidget(self._title_bar)
        
        # Content area
        self._content = QFrame()
        self._content.setObjectName("windowContent")
        self._content.setStyleSheet("""
            #windowContent {
                background-color: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.addWidget(self._content, 1)
        
        # Size grip
        self._size_grip = QSizeGrip(self)
        self._size_grip.setFixedSize(16, 16)
        
        self._main_layout.addWidget(self._container)
    
    def set_title(self, title: str) -> None:
        """Set window title."""
        self._nobject.set_property('title', title)
        self._title_bar.set_title(title)
    
    def get_content_layout(self) -> QVBoxLayout:
        """Get the content area layout for adding widgets."""
        return self._content_layout
    
    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the window content."""
        self._content_layout.addWidget(widget)
    
    # ═══════════════════════════════════════════════════════════
    # WINDOW CONTROLS
    # ═══════════════════════════════════════════════════════════
    
    def _on_close(self) -> None:
        """Handle close button."""
        self.closed.emit()
        self._nobject.set_property('visible', False)
        self._nobject.remove_tag('visible')
        self.hide()
    
    def _on_minimize(self) -> None:
        """Handle minimize button."""
        self.minimized.emit()
        self._nobject.set_property('minimized', True)
        self.showMinimized()
    
    def _on_maximize(self) -> None:
        """Handle maximize button."""
        if self._is_maximized:
            # Restore
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
            self._is_maximized = False
            self._nobject.set_property('maximized', False)
        else:
            # Maximize
            self._normal_geometry = self.geometry()
            screen = QApplication.primaryScreen()
            if screen:
                available = screen.availableGeometry()
                # Leave room for dock (60px) and menubar (28px)
                self.setGeometry(
                    available.x(),
                    available.y() + 28,
                    available.width(),
                    available.height() - 88
                )
            self._is_maximized = True
            self._nobject.set_property('maximized', True)
        
        self.maximized.emit()
    
    # ═══════════════════════════════════════════════════════════
    # RESIZE HANDLING
    # ═══════════════════════════════════════════════════════════
    
    def _get_resize_edge(self, pos: QPoint) -> Optional[str]:
        """Determine which edge/corner is being hovered for resize."""
        rect = self.rect()
        m = self._resize_margin
        
        at_left = pos.x() < m
        at_right = pos.x() > rect.width() - m
        at_top = pos.y() < m
        at_bottom = pos.y() > rect.height() - m
        
        if at_top and at_left:
            return 'top-left'
        elif at_top and at_right:
            return 'top-right'
        elif at_bottom and at_left:
            return 'bottom-left'
        elif at_bottom and at_right:
            return 'bottom-right'
        elif at_left:
            return 'left'
        elif at_right:
            return 'right'
        elif at_top:
            return 'top'
        elif at_bottom:
            return 'bottom'
        
        return None
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_resize_edge(event.pos())
            if edge:
                self._resizing = True
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resizing and self._resize_edge:
            self._do_resize(event.globalPosition().toPoint())
            event.accept()
            return
        
        # Update cursor for resize hints
        edge = self._get_resize_edge(event.pos())
        if edge in ('left', 'right'):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in ('top', 'bottom'):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ('top-left', 'bottom-right'):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ('top-right', 'bottom-left'):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._resizing = False
        self._resize_edge = None
        super().mouseReleaseEvent(event)
    
    def _do_resize(self, global_pos: QPoint) -> None:
        """Perform resize based on edge being dragged."""
        if not self._resize_edge:
            return
        
        delta = global_pos - self._resize_start_pos
        geo = self._resize_start_geometry
        min_w, min_h = 200, 100
        
        new_x = geo.x()
        new_y = geo.y()
        new_w = geo.width()
        new_h = geo.height()
        
        if 'left' in self._resize_edge:
            new_w = max(min_w, geo.width() - delta.x())
            new_x = geo.x() + geo.width() - new_w
        if 'right' in self._resize_edge:
            new_w = max(min_w, geo.width() + delta.x())
        if 'top' in self._resize_edge:
            new_h = max(min_h, geo.height() - delta.y())
            new_y = geo.y() + geo.height() - new_h
        if 'bottom' in self._resize_edge:
            new_h = max(min_h, geo.height() + delta.y())
        
        self.setGeometry(new_x, new_y, new_w, new_h)
        self._nobject.set_property('width', new_w)
        self._nobject.set_property('height', new_h)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Reposition size grip on resize."""
        super().resizeEvent(event)
        self._size_grip.move(
            self.width() - self._size_grip.width() - 4,
            self.height() - self._size_grip.height() - 4
        )
    
    # ═══════════════════════════════════════════════════════════
    # PAINTING (Squircle!)
    # ═══════════════════════════════════════════════════════════
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint for squircle window shape and shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw shadow
        shadow_rect = QRectF(4, 4, self.width() - 4, self.height() - 4)
        shadow_path = rounded_squircle_path(shadow_rect, self._corner_radius, 4.0)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 30))
        
        # Main window shape (clipping path)
        rect = QRectF(0, 0, self.width() - 4, self.height() - 4)
        path = rounded_squircle_path(rect, self._corner_radius, 4.0)
        
        # Fill background
        painter.fillPath(path, QColor(245, 245, 247, 242))
        
        painter.end()
