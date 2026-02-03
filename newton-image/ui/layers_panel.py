"""
═══════════════════════════════════════════════════════════════
NLAYERS PANEL - PHOTOSHOP-STYLE LAYER MANAGEMENT
Drag to reorder. Click to select. Double-click to rename.
Every layer is an NObject with verified state.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QSlider,
    QComboBox, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QColor, QPainter, QPixmap, QDrag, QFont

import sys
sys.path.insert(0, '..')
from core.document import NDocument, NLayer, BlendMode


class NLayerThumbnail(QWidget):
    """Thumbnail preview of a layer."""
    
    def __init__(self, layer: NLayer, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layer = layer
        self.setFixedSize(40, 40)
        layer.changed.connect(self.update)
    
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Draw checker background
        checker_size = 5
        for y in range(0, self.height(), checker_size):
            for x in range(0, self.width(), checker_size):
                color = QColor(255, 255, 255) if (x // checker_size + y // checker_size) % 2 == 0 else QColor(200, 200, 200)
                painter.fillRect(x, y, checker_size, checker_size, color)
        
        # Draw layer thumbnail
        pixmap = self._layer.to_pixmap().scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        x = (self.width() - pixmap.width()) // 2
        y = (self.height() - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        
        # Border
        painter.setPen(QColor(180, 180, 180))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


class NLayerItem(QFrame):
    """
    A single layer item in the layers panel.
    
    Shows:
    - Visibility toggle
    - Thumbnail
    - Name (editable)
    - Opacity indicator
    """
    
    clicked = pyqtSignal(object)  # NLayer
    visibility_toggled = pyqtSignal(object, bool)  # NLayer, visible
    double_clicked = pyqtSignal(object)  # NLayer
    
    def __init__(self, layer: NLayer, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layer = layer
        self._selected = False
        
        self.setFixedHeight(52)
        self._setup_ui()
        self._apply_style()
        
        # Connect signals
        layer.name_changed.connect(self._on_name_changed)
        layer.visibility_changed.connect(self._on_visibility_changed)
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Visibility toggle
        self.btn_visibility = QPushButton("👁")
        self.btn_visibility.setFixedSize(24, 24)
        self.btn_visibility.setCheckable(True)
        self.btn_visibility.setChecked(self._layer.visible)
        self.btn_visibility.clicked.connect(self._toggle_visibility)
        self.btn_visibility.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:!checked {
                opacity: 0.3;
            }
        """)
        layout.addWidget(self.btn_visibility)
        
        # Thumbnail
        self.thumbnail = NLayerThumbnail(self._layer)
        layout.addWidget(self.thumbnail)
        
        # Name and info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.name_label = QLabel(self._layer.name)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        info_layout.addWidget(self.name_label)
        
        # Opacity label
        opacity_text = f"{int(self._layer.opacity * 100)}%"
        self.opacity_label = QLabel(opacity_text)
        self.opacity_label.setStyleSheet("""
            QLabel {
                color: #86868b;
                font-size: 11px;
            }
        """)
        info_layout.addWidget(self.opacity_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Lock indicator
        if self._layer.locked:
            lock_label = QLabel("🔒")
            lock_label.setStyleSheet("font-size: 12px;")
            layout.addWidget(lock_label)
    
    def _apply_style(self) -> None:
        self._update_style()
    
    def _update_style(self) -> None:
        if self._selected:
            self.setStyleSheet("""
                NLayerItem {
                    background: rgba(0, 122, 255, 0.15);
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                NLayerItem {
                    background: transparent;
                    border-radius: 8px;
                }
                NLayerItem:hover {
                    background: rgba(0, 0, 0, 0.05);
                }
            """)
    
    @property
    def layer(self) -> NLayer:
        return self._layer
    
    @property
    def selected(self) -> bool:
        return self._selected
    
    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value
        self._update_style()
    
    def _toggle_visibility(self) -> None:
        self._layer.visible = self.btn_visibility.isChecked()
        self.visibility_toggled.emit(self._layer, self._layer.visible)
    
    def _on_name_changed(self, name: str) -> None:
        self.name_label.setText(name)
    
    def _on_visibility_changed(self, visible: bool) -> None:
        self.btn_visibility.setChecked(visible)
    
    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._layer)
    
    def mouseDoubleClickEvent(self, event) -> None:
        self.double_clicked.emit(self._layer)


class NLayersPanel(QWidget):
    """
    Photoshop-style layers panel.
    
    Features:
    - Layer list with thumbnails
    - Blend mode selector
    - Opacity slider
    - Layer actions (add, delete, duplicate, merge)
    """
    
    # Signals
    layer_selected = pyqtSignal(object)  # NLayer
    layer_added = pyqtSignal()
    layer_removed = pyqtSignal(object)  # NLayer
    layer_duplicated = pyqtSignal(object)  # NLayer
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._document: Optional[NDocument] = None
        self._layer_items: List[NLayerItem] = []
        
        self.setMinimumWidth(240)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("Layers")
        header.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        layout.addWidget(header)
        
        # Blend mode selector
        blend_layout = QHBoxLayout()
        blend_layout.setSpacing(8)
        
        blend_label = QLabel("Blend:")
        blend_label.setStyleSheet("color: #86868b; font-size: 11px;")
        blend_layout.addWidget(blend_label)
        
        self.blend_combo = QComboBox()
        for mode in BlendMode:
            self.blend_combo.addItem(mode.value.replace('_', ' ').title(), mode)
        self.blend_combo.currentIndexChanged.connect(self._on_blend_changed)
        self.blend_combo.setStyleSheet("""
            QComboBox {
                background: rgba(0, 0, 0, 0.05);
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        blend_layout.addWidget(self.blend_combo)
        
        layout.addLayout(blend_layout)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.setSpacing(8)
        
        opacity_label = QLabel("Opacity:")
        opacity_label.setStyleSheet("color: #86868b; font-size: 11px;")
        opacity_layout.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.opacity_slider.setStyleSheet("""
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
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_value = QLabel("100%")
        self.opacity_value.setFixedWidth(36)
        self.opacity_value.setStyleSheet("color: #1d1d1f; font-size: 11px;")
        opacity_layout.addWidget(self.opacity_value)
        
        layout.addLayout(opacity_layout)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(0, 0, 0, 0.1);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        
        # Layer list scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        
        self.layer_container = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_container)
        self.layer_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_layout.setSpacing(4)
        self.layer_layout.addStretch()
        
        scroll.setWidget(self.layer_container)
        layout.addWidget(scroll)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(4)
        
        # Add layer
        btn_add = QPushButton("+")
        btn_add.setFixedSize(32, 32)
        btn_add.setToolTip("Add Layer")
        btn_add.clicked.connect(self._on_add_layer)
        btn_add.setStyleSheet(self._action_button_style())
        actions_layout.addWidget(btn_add)
        
        # Delete layer
        btn_delete = QPushButton("−")
        btn_delete.setFixedSize(32, 32)
        btn_delete.setToolTip("Delete Layer")
        btn_delete.clicked.connect(self._on_delete_layer)
        btn_delete.setStyleSheet(self._action_button_style())
        actions_layout.addWidget(btn_delete)
        
        # Duplicate layer
        btn_duplicate = QPushButton("⧉")
        btn_duplicate.setFixedSize(32, 32)
        btn_duplicate.setToolTip("Duplicate Layer")
        btn_duplicate.clicked.connect(self._on_duplicate_layer)
        btn_duplicate.setStyleSheet(self._action_button_style())
        actions_layout.addWidget(btn_duplicate)
        
        # Merge down
        btn_merge = QPushButton("⬇")
        btn_merge.setFixedSize(32, 32)
        btn_merge.setToolTip("Merge Down")
        btn_merge.clicked.connect(self._on_merge_down)
        btn_merge.setStyleSheet(self._action_button_style())
        actions_layout.addWidget(btn_merge)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
    
    def _action_button_style(self) -> str:
        return """
            QPushButton {
                background: rgba(0, 0, 0, 0.05);
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                color: #1d1d1f;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background: rgba(0, 0, 0, 0.15);
            }
        """
    
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            NLayersPanel {
                background: rgba(246, 246, 246, 0.95);
                border-left: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
    
    @property
    def document(self) -> Optional[NDocument]:
        return self._document
    
    @document.setter
    def document(self, doc: Optional[NDocument]) -> None:
        self._document = doc
        if doc:
            doc.layer_added.connect(self._on_document_layer_added)
            doc.layer_removed.connect(self._on_document_layer_removed)
            doc.layers_reordered.connect(self._refresh_layers)
            doc.layer_selected.connect(self._on_layer_selected_external)
        self._refresh_layers()
    
    def _refresh_layers(self) -> None:
        """Rebuild the layer list."""
        # Clear existing items
        for item in self._layer_items:
            self.layer_layout.removeWidget(item)
            item.deleteLater()
        self._layer_items.clear()
        
        if not self._document:
            return
        
        # Add layers in reverse order (top to bottom)
        for layer in reversed(self._document.layers):
            item = NLayerItem(layer)
            item.clicked.connect(self._on_layer_clicked)
            item.double_clicked.connect(self._on_layer_double_clicked)
            item.visibility_toggled.connect(self._on_visibility_toggled)
            
            if layer == self._document.active_layer:
                item.selected = True
            
            self.layer_layout.insertWidget(0, item)
            self._layer_items.append(item)
    
    def _on_layer_clicked(self, layer: NLayer) -> None:
        """Handle layer selection."""
        if self._document:
            self._document.active_layer = layer
        
        # Update selection state
        for item in self._layer_items:
            item.selected = (item.layer == layer)
        
        # Update controls
        self.opacity_slider.setValue(int(layer.opacity * 100))
        
        for i in range(self.blend_combo.count()):
            if self.blend_combo.itemData(i) == layer.blend_mode:
                self.blend_combo.setCurrentIndex(i)
                break
        
        self.layer_selected.emit(layer)
    
    def _on_layer_double_clicked(self, layer: NLayer) -> None:
        """Handle layer double-click (rename)."""
        # Could show rename dialog
        pass
    
    def _on_visibility_toggled(self, layer: NLayer, visible: bool) -> None:
        """Handle visibility toggle."""
        if self._document:
            self._document.changed.emit()
    
    def _on_layer_selected_external(self, layer: NLayer) -> None:
        """Handle external layer selection."""
        for item in self._layer_items:
            item.selected = (item.layer == layer)
        
        if layer:
            self.opacity_slider.setValue(int(layer.opacity * 100))
    
    def _on_document_layer_added(self, layer: NLayer) -> None:
        """Handle layer added to document."""
        self._refresh_layers()
    
    def _on_document_layer_removed(self, layer_id: str) -> None:
        """Handle layer removed from document."""
        self._refresh_layers()
    
    def _on_blend_changed(self, index: int) -> None:
        """Handle blend mode change."""
        if self._document and self._document.active_layer:
            mode = self.blend_combo.itemData(index)
            self._document.active_layer.blend_mode = mode
    
    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change."""
        self.opacity_value.setText(f"{value}%")
        if self._document and self._document.active_layer:
            self._document.active_layer.opacity = value / 100
    
    def _on_add_layer(self) -> None:
        """Add new layer."""
        if self._document:
            self._document.add_layer()
            self.layer_added.emit()
    
    def _on_delete_layer(self) -> None:
        """Delete selected layer."""
        if self._document and self._document.active_layer:
            layer = self._document.active_layer
            self._document.remove_layer(layer)
            self.layer_removed.emit(layer)
    
    def _on_duplicate_layer(self) -> None:
        """Duplicate selected layer."""
        if self._document and self._document.active_layer:
            new_layer = self._document.duplicate_layer(self._document.active_layer)
            if new_layer:
                self.layer_duplicated.emit(new_layer)
    
    def _on_merge_down(self) -> None:
        """Merge selected layer down."""
        if self._document and self._document.active_layer:
            self._document.merge_down(self._document.active_layer)
