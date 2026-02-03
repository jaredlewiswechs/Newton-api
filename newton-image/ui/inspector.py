"""
═══════════════════════════════════════════════════════════════
NINSPECTOR - CONTEXT-AWARE PROPERTY PANEL
Shows tool options, layer properties, or document info.
Apple HIG compliant inspector panel.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QSpinBox, QCheckBox, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

import sys
sys.path.insert(0, '..')
from core.tools import NTool, ToolType, NBrushTool, NEraserTool, BrushSettings


class NBrushOptionsPanel(QWidget):
    """Options panel for brush-based tools."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._tool: Optional[NTool] = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Size
        size_layout = QVBoxLayout()
        size_header = QHBoxLayout()
        
        size_label = QLabel("Size")
        size_label.setStyleSheet("color: #86868b; font-size: 11px;")
        size_header.addWidget(size_label)
        
        self.size_value = QLabel("10 px")
        self.size_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        size_header.addWidget(self.size_value)
        size_header.addStretch()
        
        size_layout.addLayout(size_header)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 500)
        self.size_slider.setValue(10)
        self.size_slider.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_slider)
        
        layout.addLayout(size_layout)
        
        # Hardness
        hardness_layout = QVBoxLayout()
        hardness_header = QHBoxLayout()
        
        hardness_label = QLabel("Hardness")
        hardness_label.setStyleSheet("color: #86868b; font-size: 11px;")
        hardness_header.addWidget(hardness_label)
        
        self.hardness_value = QLabel("100%")
        self.hardness_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        hardness_header.addWidget(self.hardness_value)
        hardness_header.addStretch()
        
        hardness_layout.addLayout(hardness_header)
        
        self.hardness_slider = QSlider(Qt.Orientation.Horizontal)
        self.hardness_slider.setRange(0, 100)
        self.hardness_slider.setValue(100)
        self.hardness_slider.valueChanged.connect(self._on_hardness_changed)
        hardness_layout.addWidget(self.hardness_slider)
        
        layout.addLayout(hardness_layout)
        
        # Opacity
        opacity_layout = QVBoxLayout()
        opacity_header = QHBoxLayout()
        
        opacity_label = QLabel("Opacity")
        opacity_label.setStyleSheet("color: #86868b; font-size: 11px;")
        opacity_header.addWidget(opacity_label)
        
        self.opacity_value = QLabel("100%")
        self.opacity_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        opacity_header.addWidget(self.opacity_value)
        opacity_header.addStretch()
        
        opacity_layout.addLayout(opacity_header)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        
        layout.addLayout(opacity_layout)
        
        # Flow
        flow_layout = QVBoxLayout()
        flow_header = QHBoxLayout()
        
        flow_label = QLabel("Flow")
        flow_label.setStyleSheet("color: #86868b; font-size: 11px;")
        flow_header.addWidget(flow_label)
        
        self.flow_value = QLabel("100%")
        self.flow_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        flow_header.addWidget(self.flow_value)
        flow_header.addStretch()
        
        flow_layout.addLayout(flow_header)
        
        self.flow_slider = QSlider(Qt.Orientation.Horizontal)
        self.flow_slider.setRange(1, 100)
        self.flow_slider.setValue(100)
        self.flow_slider.valueChanged.connect(self._on_flow_changed)
        flow_layout.addWidget(self.flow_slider)
        
        layout.addLayout(flow_layout)
        
        # Smoothing
        smoothing_layout = QVBoxLayout()
        smoothing_header = QHBoxLayout()
        
        smoothing_label = QLabel("Smoothing")
        smoothing_label.setStyleSheet("color: #86868b; font-size: 11px;")
        smoothing_header.addWidget(smoothing_label)
        
        self.smoothing_value = QLabel("50%")
        self.smoothing_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        smoothing_header.addWidget(self.smoothing_value)
        smoothing_header.addStretch()
        
        smoothing_layout.addLayout(smoothing_header)
        
        self.smoothing_slider = QSlider(Qt.Orientation.Horizontal)
        self.smoothing_slider.setRange(0, 100)
        self.smoothing_slider.setValue(50)
        self.smoothing_slider.valueChanged.connect(self._on_smoothing_changed)
        smoothing_layout.addWidget(self.smoothing_slider)
        
        layout.addLayout(smoothing_layout)
        
        # Pressure sensitivity
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(0, 0, 0, 0.1);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        self.pressure_size = QCheckBox("Size follows pressure")
        self.pressure_size.setChecked(True)
        self.pressure_size.stateChanged.connect(self._on_pressure_changed)
        self.pressure_size.setStyleSheet("color: #1d1d1f; font-size: 12px;")
        layout.addWidget(self.pressure_size)
        
        self.pressure_opacity = QCheckBox("Opacity follows pressure")
        self.pressure_opacity.setChecked(True)
        self.pressure_opacity.stateChanged.connect(self._on_pressure_changed)
        self.pressure_opacity.setStyleSheet("color: #1d1d1f; font-size: 12px;")
        layout.addWidget(self.pressure_opacity)
        
        layout.addStretch()
    
    def set_tool(self, tool: NTool) -> None:
        """Set the tool to configure."""
        self._tool = tool
        if hasattr(tool, 'settings'):
            settings = tool.settings
            self.size_slider.setValue(settings.size)
            self.hardness_slider.setValue(int(settings.hardness * 100))
            self.opacity_slider.setValue(int(settings.opacity * 100))
            self.flow_slider.setValue(int(settings.flow * 100))
            self.smoothing_slider.setValue(int(settings.smoothing * 100))
            self.pressure_size.setChecked(settings.pressure_size)
            self.pressure_opacity.setChecked(settings.pressure_opacity)
    
    def _on_size_changed(self, value: int) -> None:
        self.size_value.setText(f"{value} px")
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.size = value
        self.settings_changed.emit()
    
    def _on_hardness_changed(self, value: int) -> None:
        self.hardness_value.setText(f"{value}%")
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.hardness = value / 100
        self.settings_changed.emit()
    
    def _on_opacity_changed(self, value: int) -> None:
        self.opacity_value.setText(f"{value}%")
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.opacity = value / 100
        self.settings_changed.emit()
    
    def _on_flow_changed(self, value: int) -> None:
        self.flow_value.setText(f"{value}%")
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.flow = value / 100
        self.settings_changed.emit()
    
    def _on_smoothing_changed(self, value: int) -> None:
        self.smoothing_value.setText(f"{value}%")
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.smoothing = value / 100
        self.settings_changed.emit()
    
    def _on_pressure_changed(self) -> None:
        if self._tool and hasattr(self._tool, 'settings'):
            self._tool.settings.pressure_size = self.pressure_size.isChecked()
            self._tool.settings.pressure_opacity = self.pressure_opacity.isChecked()
        self.settings_changed.emit()


class NDocumentInfoPanel(QWidget):
    """Panel showing document information."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Document info
        self.name_label = QLabel("No Document")
        self.name_label.setStyleSheet("""
            color: #1d1d1f;
            font-size: 13px;
            font-weight: 500;
        """)
        layout.addWidget(self.name_label)
        
        self.size_label = QLabel("—")
        self.size_label.setStyleSheet("color: #86868b; font-size: 12px;")
        layout.addWidget(self.size_label)
        
        self.layer_count_label = QLabel("0 layers")
        self.layer_count_label.setStyleSheet("color: #86868b; font-size: 12px;")
        layout.addWidget(self.layer_count_label)
        
        layout.addStretch()
    
    def set_document(self, doc) -> None:
        """Update with document info."""
        if doc:
            self.name_label.setText(doc.name)
            self.size_label.setText(f"{doc.width} × {doc.height} px")
            self.layer_count_label.setText(f"{doc.layer_count} layers")
        else:
            self.name_label.setText("No Document")
            self.size_label.setText("—")
            self.layer_count_label.setText("0 layers")


class NInspector(QWidget):
    """
    Context-aware inspector panel.
    
    Shows different options based on:
    - Selected tool
    - Active layer
    - Document state
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setMinimumWidth(220)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header
        self.header = QLabel("Inspector")
        self.header.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.header)
        
        # Stacked widget for different panels
        self.stack = QStackedWidget()
        
        # Document info panel (index 0)
        self.doc_panel = NDocumentInfoPanel()
        self.stack.addWidget(self.doc_panel)
        
        # Brush options panel (index 1)
        self.brush_panel = NBrushOptionsPanel()
        self.stack.addWidget(self.brush_panel)
        
        layout.addWidget(self.stack)
    
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            NInspector {
                background: rgba(246, 246, 246, 0.95);
            }
            QSlider::groove:horizontal {
                background: rgba(0, 0, 0, 0.1);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #007aff;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)
    
    def set_tool(self, tool: NTool) -> None:
        """Update inspector for selected tool."""
        if tool.tool_type in (ToolType.BRUSH, ToolType.ERASER):
            self.header.setText(f"{tool.name} Options")
            self.brush_panel.set_tool(tool)
            self.stack.setCurrentIndex(1)
        else:
            self.header.setText("Inspector")
            self.stack.setCurrentIndex(0)
    
    def set_document(self, doc) -> None:
        """Update inspector with document info."""
        self.doc_panel.set_document(doc)
