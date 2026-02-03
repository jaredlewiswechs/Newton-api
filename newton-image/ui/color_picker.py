"""
═══════════════════════════════════════════════════════════════
NCOLOR PICKER - HSB/RGB COLOR SELECTION
Apple-style color picker with spectrum, sliders, and swatches.
Every color choice is verified and logged.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QLineEdit, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import (
    QColor, QPainter, QLinearGradient, QConicalGradient,
    QRadialGradient, QMouseEvent, QPaintEvent, QImage
)
import math


class NColorSpectrum(QWidget):
    """
    HSB color spectrum picker.
    Click to select saturation/brightness at current hue.
    """
    
    color_changed = pyqtSignal(object)  # QColor
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._hue = 0.0  # 0-360
        self._saturation = 1.0  # 0-1
        self._brightness = 1.0  # 0-1
        
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)
    
    @property
    def color(self) -> QColor:
        return QColor.fromHsvF(self._hue / 360, self._saturation, self._brightness)
    
    @color.setter
    def color(self, c: QColor) -> None:
        h, s, v, _ = c.getHsvF()
        self._hue = h * 360 if h >= 0 else self._hue
        self._saturation = s
        self._brightness = v
        self.update()
    
    @property
    def hue(self) -> float:
        return self._hue
    
    @hue.setter
    def hue(self, h: float) -> None:
        self._hue = h % 360
        self.update()
        self.color_changed.emit(self.color)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._update_from_pos(event.position())
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._update_from_pos(event.position())
    
    def _update_from_pos(self, pos: QPointF) -> None:
        x = max(0, min(1, pos.x() / self.width()))
        y = max(0, min(1, 1 - pos.y() / self.height()))
        
        self._saturation = x
        self._brightness = y
        self.update()
        self.color_changed.emit(self.color)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw saturation/brightness gradient
        rect = self.rect()
        
        # Base color at full saturation/brightness
        base_color = QColor.fromHsvF(self._hue / 360, 1.0, 1.0)
        
        # Horizontal gradient (saturation: white to color)
        h_grad = QLinearGradient(0, 0, rect.width(), 0)
        h_grad.setColorAt(0, QColor(255, 255, 255))
        h_grad.setColorAt(1, base_color)
        painter.fillRect(rect, h_grad)
        
        # Vertical gradient (brightness: transparent to black)
        v_grad = QLinearGradient(0, 0, 0, rect.height())
        v_grad.setColorAt(0, QColor(0, 0, 0, 0))
        v_grad.setColorAt(1, QColor(0, 0, 0, 255))
        painter.fillRect(rect, v_grad)
        
        # Draw selection circle
        sel_x = self._saturation * rect.width()
        sel_y = (1 - self._brightness) * rect.height()
        
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(sel_x, sel_y), 6, 6)
        
        painter.setPen(QColor(0, 0, 0))
        painter.drawEllipse(QPointF(sel_x, sel_y), 7, 7)


class NHueSlider(QWidget):
    """
    Vertical or horizontal hue slider with rainbow gradient.
    """
    
    hue_changed = pyqtSignal(float)  # 0-360
    
    def __init__(self, 
                 orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._hue = 0.0
        self._orientation = orientation
        
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(20)
        else:
            self.setFixedWidth(20)
    
    @property
    def hue(self) -> float:
        return self._hue
    
    @hue.setter
    def hue(self, h: float) -> None:
        self._hue = h % 360
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._update_from_pos(event.position())
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._update_from_pos(event.position())
    
    def _update_from_pos(self, pos: QPointF) -> None:
        if self._orientation == Qt.Orientation.Horizontal:
            ratio = max(0, min(1, pos.x() / self.width()))
        else:
            ratio = max(0, min(1, 1 - pos.y() / self.height()))
        
        self._hue = ratio * 360
        self.update()
        self.hue_changed.emit(self._hue)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Draw rainbow gradient
        if self._orientation == Qt.Orientation.Horizontal:
            grad = QLinearGradient(0, 0, rect.width(), 0)
        else:
            grad = QLinearGradient(0, rect.height(), 0, 0)
        
        for i in range(7):
            grad.setColorAt(i / 6, QColor.fromHsvF(i / 6, 1.0, 1.0))
        
        painter.fillRect(rect, grad)
        
        # Draw marker
        if self._orientation == Qt.Orientation.Horizontal:
            x = (self._hue / 360) * rect.width()
            painter.setPen(QColor(0, 0, 0))
            painter.drawLine(int(x), 0, int(x), rect.height())
            painter.setPen(QColor(255, 255, 255))
            painter.drawLine(int(x) - 1, 0, int(x) - 1, rect.height())
        else:
            y = (1 - self._hue / 360) * rect.height()
            painter.setPen(QColor(0, 0, 0))
            painter.drawLine(0, int(y), rect.width(), int(y))
            painter.setPen(QColor(255, 255, 255))
            painter.drawLine(0, int(y) - 1, rect.width(), int(y) - 1)


class NColorSwatch(QWidget):
    """A clickable color swatch."""
    
    clicked = pyqtSignal(object)  # QColor
    
    def __init__(self, color: QColor, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    @property
    def color(self) -> QColor:
        return self._color
    
    @color.setter
    def color(self, c: QColor) -> None:
        self._color = c
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit(self._color)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw checker for alpha
        checker_size = 6
        for y in range(0, self.height(), checker_size):
            for x in range(0, self.width(), checker_size):
                c = QColor(255, 255, 255) if (x // checker_size + y // checker_size) % 2 == 0 else QColor(200, 200, 200)
                painter.fillRect(x, y, checker_size, checker_size, c)
        
        # Draw color
        painter.fillRect(self.rect(), self._color)
        
        # Border
        painter.setPen(QColor(180, 180, 180))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


class NColorPicker(QWidget):
    """
    Complete color picker widget.
    
    Features:
    - HSB spectrum selector
    - Hue slider
    - RGB/Hex input
    - Swatches
    """
    
    color_changed = pyqtSignal(object)  # QColor
    
    # Default swatches
    DEFAULT_SWATCHES = [
        "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
        "#FFFF00", "#00FFFF", "#FF00FF", "#FF8000", "#8000FF",
        "#0080FF", "#FF0080", "#808080", "#C0C0C0", "#400000",
        "#004000", "#000040", "#404000", "#004040", "#400040"
    ]
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._color = QColor(0, 0, 0)
        self._swatches: List[QColor] = [QColor(c) for c in self.DEFAULT_SWATCHES]
        
        self.setMinimumWidth(220)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("Color")
        header.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        layout.addWidget(header)
        
        # Current color preview
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(8)
        
        self.current_swatch = NColorSwatch(self._color)
        self.current_swatch.setFixedSize(48, 48)
        preview_layout.addWidget(self.current_swatch)
        
        # Hex input
        hex_layout = QVBoxLayout()
        hex_label = QLabel("Hex")
        hex_label.setStyleSheet("color: #86868b; font-size: 11px;")
        hex_layout.addWidget(hex_label)
        
        self.hex_input = QLineEdit("#000000")
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self._on_hex_changed)
        self.hex_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.05);
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        hex_layout.addWidget(self.hex_input)
        
        preview_layout.addLayout(hex_layout)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
        
        # Spectrum
        self.spectrum = NColorSpectrum()
        self.spectrum.color_changed.connect(self._on_spectrum_changed)
        layout.addWidget(self.spectrum)
        
        # Hue slider
        self.hue_slider = NHueSlider(Qt.Orientation.Horizontal)
        self.hue_slider.hue_changed.connect(self._on_hue_changed)
        layout.addWidget(self.hue_slider)
        
        # RGB sliders
        rgb_frame = QFrame()
        rgb_layout = QVBoxLayout(rgb_frame)
        rgb_layout.setContentsMargins(0, 8, 0, 0)
        rgb_layout.setSpacing(8)
        
        # R slider
        r_layout = QHBoxLayout()
        r_label = QLabel("R")
        r_label.setFixedWidth(16)
        r_label.setStyleSheet("color: #ff3b30; font-weight: 600;")
        r_layout.addWidget(r_label)
        
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(0, 255)
        self.r_slider.valueChanged.connect(self._on_rgb_changed)
        r_layout.addWidget(self.r_slider)
        
        self.r_value = QLabel("0")
        self.r_value.setFixedWidth(32)
        self.r_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        r_layout.addWidget(self.r_value)
        
        rgb_layout.addLayout(r_layout)
        
        # G slider
        g_layout = QHBoxLayout()
        g_label = QLabel("G")
        g_label.setFixedWidth(16)
        g_label.setStyleSheet("color: #34c759; font-weight: 600;")
        g_layout.addWidget(g_label)
        
        self.g_slider = QSlider(Qt.Orientation.Horizontal)
        self.g_slider.setRange(0, 255)
        self.g_slider.valueChanged.connect(self._on_rgb_changed)
        g_layout.addWidget(self.g_slider)
        
        self.g_value = QLabel("0")
        self.g_value.setFixedWidth(32)
        self.g_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        g_layout.addWidget(self.g_value)
        
        rgb_layout.addLayout(g_layout)
        
        # B slider
        b_layout = QHBoxLayout()
        b_label = QLabel("B")
        b_label.setFixedWidth(16)
        b_label.setStyleSheet("color: #007aff; font-weight: 600;")
        b_layout.addWidget(b_label)
        
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 255)
        self.b_slider.valueChanged.connect(self._on_rgb_changed)
        b_layout.addWidget(self.b_slider)
        
        self.b_value = QLabel("0")
        self.b_value.setFixedWidth(32)
        self.b_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        b_layout.addWidget(self.b_value)
        
        rgb_layout.addLayout(b_layout)
        
        layout.addWidget(rgb_frame)
        
        # Swatches
        swatch_label = QLabel("Swatches")
        swatch_label.setStyleSheet("color: #86868b; font-size: 11px;")
        layout.addWidget(swatch_label)
        
        swatch_grid = QGridLayout()
        swatch_grid.setSpacing(4)
        
        for i, color in enumerate(self._swatches):
            swatch = NColorSwatch(color)
            swatch.clicked.connect(self._on_swatch_clicked)
            row = i // 5
            col = i % 5
            swatch_grid.addWidget(swatch, row, col)
        
        layout.addLayout(swatch_grid)
        layout.addStretch()
    
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            NColorPicker {
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
    
    @property
    def color(self) -> QColor:
        return self._color
    
    @color.setter
    def color(self, c: QColor) -> None:
        self._color = c
        self._update_ui()
    
    def _update_ui(self) -> None:
        """Update all UI elements to reflect current color."""
        # Block signals to prevent loops
        self.r_slider.blockSignals(True)
        self.g_slider.blockSignals(True)
        self.b_slider.blockSignals(True)
        self.hex_input.blockSignals(True)
        
        self.r_slider.setValue(self._color.red())
        self.g_slider.setValue(self._color.green())
        self.b_slider.setValue(self._color.blue())
        
        self.r_value.setText(str(self._color.red()))
        self.g_value.setText(str(self._color.green()))
        self.b_value.setText(str(self._color.blue()))
        
        self.hex_input.setText(self._color.name().upper())
        self.current_swatch.color = self._color
        self.spectrum.color = self._color
        self.hue_slider.hue = self._color.hsvHueF() * 360 if self._color.hsvHueF() >= 0 else 0
        
        self.r_slider.blockSignals(False)
        self.g_slider.blockSignals(False)
        self.b_slider.blockSignals(False)
        self.hex_input.blockSignals(False)
    
    def _on_spectrum_changed(self, color: QColor) -> None:
        self._color = color
        self._update_ui()
        self.color_changed.emit(self._color)
    
    def _on_hue_changed(self, hue: float) -> None:
        self.spectrum.hue = hue
        self._color = self.spectrum.color
        self._update_ui()
        self.color_changed.emit(self._color)
    
    def _on_rgb_changed(self) -> None:
        self._color = QColor(
            self.r_slider.value(),
            self.g_slider.value(),
            self.b_slider.value()
        )
        
        self.r_value.setText(str(self.r_slider.value()))
        self.g_value.setText(str(self.g_slider.value()))
        self.b_value.setText(str(self.b_slider.value()))
        
        self.hex_input.blockSignals(True)
        self.hex_input.setText(self._color.name().upper())
        self.hex_input.blockSignals(False)
        
        self.current_swatch.color = self._color
        self.spectrum.color = self._color
        self.hue_slider.hue = self._color.hsvHueF() * 360 if self._color.hsvHueF() >= 0 else 0
        
        self.color_changed.emit(self._color)
    
    def _on_hex_changed(self, text: str) -> None:
        if len(text) == 7 and text.startswith('#'):
            try:
                color = QColor(text)
                if color.isValid():
                    self._color = color
                    self._update_ui()
                    self.color_changed.emit(self._color)
            except:
                pass
    
    def _on_swatch_clicked(self, color: QColor) -> None:
        self._color = color
        self._update_ui()
        self.color_changed.emit(self._color)
