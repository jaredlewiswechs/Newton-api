"""
═══════════════════════════════════════════════════════════════
NADJUSTMENTS - IMAGE ADJUSTMENT PANEL
Brightness, contrast, saturation, and more.
All filters are Newton-bounded computations.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

import sys
sys.path.insert(0, '..')
from core.filters import (
    FilterType, BrightnessFilter, ContrastFilter, 
    SaturationFilter, GrayscaleFilter, InvertFilter,
    SepiaFilter, BlurFilter, PosterizeFilter
)


class NAdjustmentSlider(QWidget):
    """A labeled slider for adjustment values."""
    
    value_changed = pyqtSignal(int)
    
    def __init__(self, 
                 name: str,
                 min_val: int = -100,
                 max_val: int = 100,
                 default: int = 0,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._name = name
        self._default = default
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        
        label = QLabel(name)
        label.setStyleSheet("color: #86868b; font-size: 11px;")
        header.addWidget(label)
        
        self.value_label = QLabel(str(default))
        self.value_label.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        self.value_label.setMinimumWidth(32)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self.value_label)
        
        layout.addLayout(header)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
    
    @property
    def value(self) -> int:
        return self.slider.value()
    
    @value.setter
    def value(self, v: int) -> None:
        self.slider.setValue(v)
    
    def reset(self) -> None:
        self.slider.setValue(self._default)
    
    def _on_value_changed(self, value: int) -> None:
        self.value_label.setText(str(value))
        self.value_changed.emit(value)


class NAdjustmentsPanel(QWidget):
    """
    Image adjustment controls panel.
    
    Provides sliders for:
    - Brightness
    - Contrast
    - Saturation
    - Hue
    
    And quick filters:
    - Grayscale
    - Invert
    - Sepia
    - Blur
    - Posterize
    """
    
    # Signals
    adjustment_changed = pyqtSignal(str, int)  # adjustment_name, value
    filter_applied = pyqtSignal(object)  # FilterType
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.setMinimumWidth(220)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Adjustments")
        header.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        layout.addWidget(header)
        
        # ═══════════════════════════════════════════════════════
        # ADJUSTMENT SLIDERS
        # ═══════════════════════════════════════════════════════
        
        # Brightness
        self.brightness = NAdjustmentSlider("Brightness", -100, 100, 0)
        self.brightness.value_changed.connect(
            lambda v: self.adjustment_changed.emit("brightness", v)
        )
        layout.addWidget(self.brightness)
        
        # Contrast
        self.contrast = NAdjustmentSlider("Contrast", -100, 100, 0)
        self.contrast.value_changed.connect(
            lambda v: self.adjustment_changed.emit("contrast", v)
        )
        layout.addWidget(self.contrast)
        
        # Saturation
        self.saturation = NAdjustmentSlider("Saturation", -100, 100, 0)
        self.saturation.value_changed.connect(
            lambda v: self.adjustment_changed.emit("saturation", v)
        )
        layout.addWidget(self.saturation)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(0, 0, 0, 0.1);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        # ═══════════════════════════════════════════════════════
        # QUICK FILTERS
        # ═══════════════════════════════════════════════════════
        
        filters_label = QLabel("Quick Filters")
        filters_label.setStyleSheet("color: #86868b; font-size: 11px;")
        layout.addWidget(filters_label)
        
        # Filter buttons grid
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(8)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        
        btn_grayscale = self._create_filter_button("Grayscale", FilterType.GRAYSCALE)
        row1.addWidget(btn_grayscale)
        
        btn_invert = self._create_filter_button("Invert", FilterType.INVERT)
        row1.addWidget(btn_invert)
        
        filters_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        
        btn_sepia = self._create_filter_button("Sepia", FilterType.SEPIA)
        row2.addWidget(btn_sepia)
        
        btn_posterize = self._create_filter_button("Posterize", FilterType.POSTERIZE)
        row2.addWidget(btn_posterize)
        
        filters_layout.addLayout(row2)
        
        layout.addLayout(filters_layout)
        
        # Blur slider
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: rgba(0, 0, 0, 0.1);")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)
        
        self.blur = NAdjustmentSlider("Blur Radius", 0, 50, 0)
        self.blur.value_changed.connect(
            lambda v: self.adjustment_changed.emit("blur", v)
        )
        layout.addWidget(self.blur)
        
        # Apply button
        btn_apply = QPushButton("Apply Adjustments")
        btn_apply.clicked.connect(self._on_apply)
        btn_apply.setStyleSheet("""
            QPushButton {
                background: #007aff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0066d6;
            }
            QPushButton:pressed {
                background: #0055b3;
            }
        """)
        layout.addWidget(btn_apply)
        
        # Reset button
        btn_reset = QPushButton("Reset All")
        btn_reset.clicked.connect(self.reset_all)
        btn_reset.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.05);
                color: #1d1d1f;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        layout.addWidget(btn_reset)
        
        layout.addStretch()
    
    def _create_filter_button(self, name: str, filter_type: FilterType) -> QPushButton:
        """Create a filter button."""
        btn = QPushButton(name)
        btn.clicked.connect(lambda: self.filter_applied.emit(filter_type))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.05);
                color: #1d1d1f;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background: rgba(0, 0, 0, 0.15);
            }
        """)
        return btn
    
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            NAdjustmentsPanel {
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
    
    def _on_apply(self) -> None:
        """Apply current adjustments."""
        # Emit a signal to trigger application
        # The main window will handle the actual filter application
        pass
    
    def reset_all(self) -> None:
        """Reset all adjustments to default."""
        self.brightness.reset()
        self.contrast.reset()
        self.saturation.reset()
        self.blur.reset()
    
    def get_adjustments(self) -> dict:
        """Get current adjustment values."""
        return {
            'brightness': self.brightness.value,
            'contrast': self.contrast.value,
            'saturation': self.saturation.value,
            'blur': self.blur.value
        }
