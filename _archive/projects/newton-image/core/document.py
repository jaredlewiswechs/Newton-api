"""
═══════════════════════════════════════════════════════════════
NDOCUMENT - THE VERIFIED IMAGE
A document is an NObject containing layers.
Every change is tracked, verified, and reversible.
═══════════════════════════════════════════════════════════════
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QPointF, QRectF, QSize
from PyQt6.QtGui import QImage, QColor, QPainter, QPixmap
import uuid
import time


class BlendMode(Enum):
    """Photoshop-style blend modes."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    HARD_LIGHT = "hard_light"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"
    HUE = "hue"
    SATURATION = "saturation"
    COLOR = "color"
    LUMINOSITY = "luminosity"


class LayerType(Enum):
    """Types of layers."""
    RASTER = "raster"
    VECTOR = "vector"
    TEXT = "text"
    ADJUSTMENT = "adjustment"
    GROUP = "group"
    SMART_OBJECT = "smart_object"


@dataclass
class LayerState:
    """Immutable snapshot of layer state for history."""
    id: str
    name: str
    visible: bool
    locked: bool
    opacity: float
    blend_mode: BlendMode
    position: Tuple[int, int]
    image_data: bytes  # Compressed PNG data


class NLayer(QObject):
    """
    A layer in the Newton Image document.
    
    NLayers are NObjects - they have:
    - Identity (UUID)
    - Properties (opacity, blend mode, etc.)
    - Relationships (parent document, mask, linked layers)
    - Verified state changes
    """
    
    # Signals
    changed = pyqtSignal()
    visibility_changed = pyqtSignal(bool)
    opacity_changed = pyqtSignal(float)
    blend_mode_changed = pyqtSignal(object)
    name_changed = pyqtSignal(str)
    position_changed = pyqtSignal(int, int)
    
    def __init__(self, 
                 name: str = "Layer",
                 width: int = 800,
                 height: int = 600,
                 layer_type: LayerType = LayerType.RASTER,
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Identity
        self._id = str(uuid.uuid4())
        self._name = name
        self._type = layer_type
        self._created = time.time()
        
        # Visual properties
        self._visible = True
        self._locked = False
        self._opacity = 1.0
        self._blend_mode = BlendMode.NORMAL
        
        # Position (for layer transforms)
        self._x = 0
        self._y = 0
        
        # The actual image data - RGBA
        self._image = QImage(width, height, QImage.Format.Format_ARGB32)
        self._image.fill(QColor(0, 0, 0, 0))  # Transparent
        
        # Mask (optional)
        self._mask: Optional[QImage] = None
        self._mask_enabled = False
        
        # For tracking modifications
        self._modified = False
        
    # ═══════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            self._name = value
            self.name_changed.emit(value)
            self.changed.emit()
    
    @property
    def layer_type(self) -> LayerType:
        return self._type
    
    @property
    def visible(self) -> bool:
        return self._visible
    
    @visible.setter
    def visible(self, value: bool) -> None:
        if self._visible != value:
            self._visible = value
            self.visibility_changed.emit(value)
            self.changed.emit()
    
    @property
    def locked(self) -> bool:
        return self._locked
    
    @locked.setter
    def locked(self, value: bool) -> None:
        self._locked = value
        self.changed.emit()
    
    @property
    def opacity(self) -> float:
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float) -> None:
        value = max(0.0, min(1.0, value))
        if self._opacity != value:
            self._opacity = value
            self.opacity_changed.emit(value)
            self.changed.emit()
    
    @property
    def blend_mode(self) -> BlendMode:
        return self._blend_mode
    
    @blend_mode.setter
    def blend_mode(self, value: BlendMode) -> None:
        if self._blend_mode != value:
            self._blend_mode = value
            self.blend_mode_changed.emit(value)
            self.changed.emit()
    
    @property
    def position(self) -> Tuple[int, int]:
        return (self._x, self._y)
    
    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        if (self._x, self._y) != value:
            self._x, self._y = value
            self.position_changed.emit(self._x, self._y)
            self.changed.emit()
    
    @property
    def image(self) -> QImage:
        return self._image
    
    @property
    def size(self) -> QSize:
        return self._image.size()
    
    @property
    def width(self) -> int:
        return self._image.width()
    
    @property
    def height(self) -> int:
        return self._image.height()
    
    # ═══════════════════════════════════════════════════════════
    # IMAGE OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def get_painter(self) -> QPainter:
        """Get a painter for drawing on this layer."""
        return QPainter(self._image)
    
    def fill(self, color: QColor) -> None:
        """Fill layer with solid color."""
        if not self._locked:
            self._image.fill(color)
            self._modified = True
            self.changed.emit()
    
    def clear(self) -> None:
        """Clear layer to transparent."""
        if not self._locked:
            self._image.fill(QColor(0, 0, 0, 0))
            self._modified = True
            self.changed.emit()
    
    def set_image(self, image: QImage) -> None:
        """Replace layer content with new image."""
        if not self._locked:
            # Scale to layer size if needed
            if image.size() != self._image.size():
                image = image.scaled(self._image.size(), 
                                     aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio,
                                     transformMode=Qt.TransformationMode.SmoothTransformation)
            self._image = image.convertToFormat(QImage.Format.Format_ARGB32)
            self._modified = True
            self.changed.emit()
    
    def to_pixmap(self) -> QPixmap:
        """Convert layer to QPixmap for display."""
        return QPixmap.fromImage(self._image)
    
    def get_state(self) -> LayerState:
        """Capture current state for undo/history."""
        import io
        from PyQt6.QtCore import QBuffer, QIODevice
        
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        self._image.save(buffer, "PNG")
        
        return LayerState(
            id=self._id,
            name=self._name,
            visible=self._visible,
            locked=self._locked,
            opacity=self._opacity,
            blend_mode=self._blend_mode,
            position=(self._x, self._y),
            image_data=bytes(buffer.data())
        )
    
    def restore_state(self, state: LayerState) -> None:
        """Restore from a previous state."""
        self._name = state.name
        self._visible = state.visible
        self._locked = state.locked
        self._opacity = state.opacity
        self._blend_mode = state.blend_mode
        self._x, self._y = state.position
        
        # Restore image from compressed data
        from PyQt6.QtCore import QBuffer, QIODevice
        buffer = QBuffer()
        buffer.setData(state.image_data)
        buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self._image.loadFromData(buffer.data())
        
        self.changed.emit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize layer metadata (not image data)."""
        return {
            'id': self._id,
            'name': self._name,
            'type': self._type.value,
            'visible': self._visible,
            'locked': self._locked,
            'opacity': self._opacity,
            'blend_mode': self._blend_mode.value,
            'position': (self._x, self._y),
            'size': (self._image.width(), self._image.height())
        }


# Import Qt enum
from PyQt6.QtCore import Qt


class NDocument(QObject):
    """
    A Newton Image document.
    
    The document is the top-level NObject containing:
    - Layers (ordered stack)
    - Canvas properties (size, color mode, resolution)
    - History (verified undo/redo)
    
    Every operation is tracked in the Newton Ledger.
    """
    
    # Signals
    changed = pyqtSignal()
    layer_added = pyqtSignal(object)  # NLayer
    layer_removed = pyqtSignal(str)   # layer_id
    layer_selected = pyqtSignal(object)  # NLayer or None
    layers_reordered = pyqtSignal()
    canvas_resized = pyqtSignal(int, int)
    
    def __init__(self,
                 name: str = "Untitled",
                 width: int = 1920,
                 height: int = 1080,
                 background: QColor = QColor(255, 255, 255),
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Document identity
        self._id = str(uuid.uuid4())
        self._name = name
        self._created = time.time()
        self._modified = time.time()
        
        # Canvas properties
        self._width = width
        self._height = height
        self._background = background
        self._dpi = 72
        
        # Layer stack (bottom to top)
        self._layers: List[NLayer] = []
        self._active_layer: Optional[NLayer] = None
        
        # Selection
        self._selection: Optional[QImage] = None  # Mask image
        
        # Create default background layer
        self._create_background_layer()
        
    def _create_background_layer(self) -> None:
        """Create the default background layer."""
        bg = NLayer("Background", self._width, self._height, parent=self)
        bg.fill(self._background)
        # Don't lock by default so user can draw immediately
        bg.locked = False
        self._layers.append(bg)
        self._active_layer = bg
        bg.changed.connect(self._on_layer_changed)
    
    def _on_layer_changed(self) -> None:
        """Handle layer changes."""
        self._modified = time.time()
        self.changed.emit()
    
    # ═══════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self.changed.emit()
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def size(self) -> QSize:
        return QSize(self._width, self._height)
    
    @property
    def layers(self) -> List[NLayer]:
        return self._layers.copy()
    
    @property
    def active_layer(self) -> Optional[NLayer]:
        return self._active_layer
    
    @active_layer.setter
    def active_layer(self, layer: Optional[NLayer]) -> None:
        if layer is None or layer in self._layers:
            self._active_layer = layer
            self.layer_selected.emit(layer)
    
    @property
    def layer_count(self) -> int:
        return len(self._layers)
    
    # ═══════════════════════════════════════════════════════════
    # LAYER OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def add_layer(self, name: str = "Layer", 
                  above: Optional[NLayer] = None,
                  layer_type: LayerType = LayerType.RASTER) -> NLayer:
        """Add a new layer to the document."""
        layer = NLayer(name, self._width, self._height, layer_type, parent=self)
        layer.changed.connect(self._on_layer_changed)
        
        if above and above in self._layers:
            idx = self._layers.index(above) + 1
            self._layers.insert(idx, layer)
        else:
            self._layers.append(layer)
        
        self._active_layer = layer
        self.layer_added.emit(layer)
        self.layer_selected.emit(layer)
        self.changed.emit()
        
        return layer
    
    def remove_layer(self, layer: NLayer) -> bool:
        """Remove a layer from the document."""
        if layer in self._layers and len(self._layers) > 1:
            idx = self._layers.index(layer)
            self._layers.remove(layer)
            layer.changed.disconnect(self._on_layer_changed)
            
            # Select adjacent layer
            if self._active_layer == layer:
                new_idx = min(idx, len(self._layers) - 1)
                self._active_layer = self._layers[new_idx]
                self.layer_selected.emit(self._active_layer)
            
            self.layer_removed.emit(layer.id)
            self.changed.emit()
            return True
        return False
    
    def duplicate_layer(self, layer: NLayer) -> Optional[NLayer]:
        """Duplicate a layer."""
        if layer in self._layers:
            new_layer = self.add_layer(f"{layer.name} copy", above=layer)
            new_layer.set_image(layer.image.copy())
            new_layer.opacity = layer.opacity
            new_layer.blend_mode = layer.blend_mode
            return new_layer
        return None
    
    def move_layer(self, layer: NLayer, new_index: int) -> bool:
        """Move layer to new position in stack."""
        if layer in self._layers:
            self._layers.remove(layer)
            new_index = max(0, min(new_index, len(self._layers)))
            self._layers.insert(new_index, layer)
            self.layers_reordered.emit()
            self.changed.emit()
            return True
        return False
    
    def merge_down(self, layer: NLayer) -> Optional[NLayer]:
        """Merge layer with the one below it."""
        if layer in self._layers:
            idx = self._layers.index(layer)
            if idx > 0:
                below = self._layers[idx - 1]
                
                # Composite layer onto below
                painter = QPainter(below.image)
                painter.setOpacity(layer.opacity)
                painter.drawImage(layer._x, layer._y, layer.image)
                painter.end()
                
                # Remove top layer
                self.remove_layer(layer)
                below.changed.emit()
                
                return below
        return None
    
    def flatten(self) -> NLayer:
        """Flatten all layers into one."""
        result = QImage(self._width, self._height, QImage.Format.Format_ARGB32)
        result.fill(self._background)
        
        painter = QPainter(result)
        for layer in self._layers:
            if layer.visible:
                painter.setOpacity(layer.opacity)
                painter.drawImage(layer._x, layer._y, layer.image)
        painter.end()
        
        # Clear all layers and create new flattened one
        self._layers.clear()
        flat_layer = NLayer("Flattened", self._width, self._height, parent=self)
        flat_layer.set_image(result)
        flat_layer.changed.connect(self._on_layer_changed)
        self._layers.append(flat_layer)
        self._active_layer = flat_layer
        
        self.changed.emit()
        return flat_layer
    
    # ═══════════════════════════════════════════════════════════
    # RENDERING
    # ═══════════════════════════════════════════════════════════
    
    def render(self) -> QImage:
        """Render all layers to a single image."""
        result = QImage(self._width, self._height, QImage.Format.Format_ARGB32)
        result.fill(self._background)
        
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        for layer in self._layers:
            if layer.visible and layer.opacity > 0:
                painter.setOpacity(layer.opacity)
                # TODO: Implement blend modes
                painter.drawImage(layer._x, layer._y, layer.image)
        
        painter.end()
        return result
    
    def render_to_pixmap(self) -> QPixmap:
        """Render to QPixmap for display."""
        return QPixmap.fromImage(self.render())
    
    # ═══════════════════════════════════════════════════════════
    # FILE OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def export(self, path: str, format: str = "PNG") -> bool:
        """Export flattened image to file."""
        image = self.render()
        return image.save(path, format)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize document metadata."""
        return {
            'id': self._id,
            'name': self._name,
            'width': self._width,
            'height': self._height,
            'dpi': self._dpi,
            'created': self._created,
            'modified': self._modified,
            'layers': [l.to_dict() for l in self._layers],
            'active_layer': self._active_layer.id if self._active_layer else None
        }
