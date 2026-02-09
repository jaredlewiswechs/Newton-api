"""
═══════════════════════════════════════════════════════════════
NTOOLBAR - APPLE HIG COMPLIANT TOOLBAR
Leading edge: Navigation. Center: Tools. Trailing: Actions.
Liquid Glass. Symbols without borders. Proper spacing.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QToolButton, 
    QButtonGroup, QFrame, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QPainter, QFont

import sys
sys.path.insert(0, '..')
from core.tools import ToolType


class NToolButton(QToolButton):
    """
    Apple HIG compliant tool button.
    
    - No borders (symbols only)
    - Hover/selection states
    - Proper sizing (44x44 minimum touch target)
    """
    
    def __init__(self, 
                 icon_text: str,
                 tooltip: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._icon_text = icon_text
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self.setFixedSize(36, 36)
        
        self._update_style()
    
    def _update_style(self) -> None:
        """Apply Apple HIG styling."""
        self.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
                font-size: 16px;
                color: #1d1d1f;
            }
            QToolButton:hover {
                background: rgba(0, 0, 0, 0.05);
            }
            QToolButton:pressed {
                background: rgba(0, 0, 0, 0.1);
            }
            QToolButton:checked {
                background: rgba(0, 122, 255, 0.15);
                color: #007aff;
            }
        """)
    
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw icon text (emoji/symbol)
        font = QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(16)
        painter.setFont(font)
        
        if self.isChecked():
            painter.setPen(QColor("#007aff"))
        else:
            painter.setPen(QColor("#1d1d1f"))
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._icon_text)


class NToolGroup(QFrame):
    """A group of related tools with visual separator."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        self.setStyleSheet("""
            NToolGroup {
                background: transparent;
            }
        """)


class NToolbar(QWidget):
    """
    Main toolbar following Apple HIG 2025.
    
    Layout:
    - Leading: Document controls
    - Center: Tool selection
    - Trailing: Actions (zoom, etc.)
    
    Style:
    - Liquid Glass background
    - Symbols without borders
    - Proper grouping and spacing
    """
    
    # Signals
    tool_selected = pyqtSignal(object)  # ToolType
    action_triggered = pyqtSignal(str)  # action name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._tool_buttons: Dict[ToolType, NToolButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        
        self.setFixedHeight(52)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self) -> None:
        """Create toolbar layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)
        
        # ═══════════════════════════════════════════════════════
        # LEADING EDGE - Document controls
        # ═══════════════════════════════════════════════════════
        
        leading = QHBoxLayout()
        leading.setSpacing(4)
        
        # New document
        btn_new = NToolButton("📄", "New Document (⌘N)")
        btn_new.setCheckable(False)
        btn_new.clicked.connect(lambda: self.action_triggered.emit("new"))
        leading.addWidget(btn_new)
        
        # Open
        btn_open = NToolButton("📂", "Open (⌘O)")
        btn_open.setCheckable(False)
        btn_open.clicked.connect(lambda: self.action_triggered.emit("open"))
        leading.addWidget(btn_open)
        
        # Save
        btn_save = NToolButton("💾", "Save (⌘S)")
        btn_save.setCheckable(False)
        btn_save.clicked.connect(lambda: self.action_triggered.emit("save"))
        leading.addWidget(btn_save)
        
        layout.addLayout(leading)
        
        # Separator
        layout.addWidget(self._create_separator())
        
        # ═══════════════════════════════════════════════════════
        # CENTER - Tool selection
        # ═══════════════════════════════════════════════════════
        
        center = QHBoxLayout()
        center.setSpacing(2)
        
        # Selection tools
        tools_select = [
            (ToolType.SELECT_RECT, "⬚", "Rectangular Marquee (M)"),
            (ToolType.MOVE, "✥", "Move Tool (V)"),
        ]
        
        for tool_type, icon, tip in tools_select:
            btn = self._create_tool_button(tool_type, icon, tip)
            center.addWidget(btn)
        
        center.addWidget(self._create_separator())
        
        # Paint tools
        tools_paint = [
            (ToolType.BRUSH, "🖌️", "Brush Tool (B)"),
            (ToolType.ERASER, "🧹", "Eraser Tool (E)"),
            (ToolType.FILL, "🪣", "Paint Bucket (G)"),
            (ToolType.GRADIENT, "🌈", "Gradient Tool (G)"),
        ]
        
        for tool_type, icon, tip in tools_paint:
            btn = self._create_tool_button(tool_type, icon, tip)
            center.addWidget(btn)
        
        center.addWidget(self._create_separator())
        
        # Utility tools
        tools_utility = [
            (ToolType.EYEDROPPER, "💧", "Eyedropper (I)"),
            (ToolType.TEXT, "T", "Text Tool (T)"),
            (ToolType.HAND, "✋", "Hand Tool (H)"),
            (ToolType.ZOOM, "🔍", "Zoom Tool (Z)"),
        ]
        
        for tool_type, icon, tip in tools_utility:
            btn = self._create_tool_button(tool_type, icon, tip)
            center.addWidget(btn)
        
        layout.addLayout(center)
        layout.addStretch()
        
        # ═══════════════════════════════════════════════════════
        # TRAILING EDGE - View controls and actions
        # ═══════════════════════════════════════════════════════
        
        trailing = QHBoxLayout()
        trailing.setSpacing(4)
        
        # Zoom controls
        btn_zoom_out = NToolButton("−", "Zoom Out")
        btn_zoom_out.setCheckable(False)
        btn_zoom_out.clicked.connect(lambda: self.action_triggered.emit("zoom_out"))
        trailing.addWidget(btn_zoom_out)
        
        # Zoom label
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 12px;
                font-weight: 500;
                padding: 0 8px;
            }
        """)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setMinimumWidth(50)
        trailing.addWidget(self.zoom_label)
        
        btn_zoom_in = NToolButton("+", "Zoom In")
        btn_zoom_in.setCheckable(False)
        btn_zoom_in.clicked.connect(lambda: self.action_triggered.emit("zoom_in"))
        trailing.addWidget(btn_zoom_in)
        
        trailing.addWidget(self._create_separator())
        
        # Fit view
        btn_fit = NToolButton("⊡", "Fit in View")
        btn_fit.setCheckable(False)
        btn_fit.clicked.connect(lambda: self.action_triggered.emit("fit"))
        trailing.addWidget(btn_fit)
        
        # Undo/Redo
        btn_undo = NToolButton("↩", "Undo (⌘Z)")
        btn_undo.setCheckable(False)
        btn_undo.clicked.connect(lambda: self.action_triggered.emit("undo"))
        trailing.addWidget(btn_undo)
        
        btn_redo = NToolButton("↪", "Redo (⌘⇧Z)")
        btn_redo.setCheckable(False)
        btn_redo.clicked.connect(lambda: self.action_triggered.emit("redo"))
        trailing.addWidget(btn_redo)
        
        layout.addLayout(trailing)
        
        # Select default tool
        if ToolType.BRUSH in self._tool_buttons:
            self._tool_buttons[ToolType.BRUSH].setChecked(True)
    
    def _create_tool_button(self, 
                           tool_type: ToolType,
                           icon: str,
                           tooltip: str) -> NToolButton:
        """Create a tool selection button."""
        btn = NToolButton(icon, tooltip)
        btn.clicked.connect(lambda: self._on_tool_clicked(tool_type))
        self._button_group.addButton(btn)
        self._tool_buttons[tool_type] = btn
        return btn
    
    def _create_separator(self) -> QFrame:
        """Create a visual separator."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        return sep
    
    def _apply_style(self) -> None:
        """Apply Apple HIG Liquid Glass styling."""
        self.setStyleSheet("""
            NToolbar {
                background: rgba(246, 246, 246, 0.92);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
    
    def _on_tool_clicked(self, tool_type: ToolType) -> None:
        """Handle tool button click."""
        self.tool_selected.emit(tool_type)
    
    def set_zoom(self, zoom: float) -> None:
        """Update zoom display."""
        self.zoom_label.setText(f"{int(zoom * 100)}%")
    
    def select_tool(self, tool_type: ToolType) -> None:
        """Programmatically select a tool."""
        if tool_type in self._tool_buttons:
            self._tool_buttons[tool_type].setChecked(True)
            self.tool_selected.emit(tool_type)
