"""
═══════════════════════════════════════════════════════════════
NTOOLS - VERIFIED DRAWING TOOLS
Each stroke is an NObject. Each pixel is accountable.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QImage, QColor, QPainter, QPen, QBrush, 
    QPainterPath, QLinearGradient
)
import math
import uuid
import time


class ToolType(Enum):
    """Available tool types."""
    BRUSH = "brush"
    ERASER = "eraser"
    SELECT_RECT = "select_rect"
    SELECT_LASSO = "select_lasso"
    SELECT_MAGIC = "select_magic"
    MOVE = "move"
    TEXT = "text"
    EYEDROPPER = "eyedropper"
    FILL = "fill"
    GRADIENT = "gradient"
    CROP = "crop"
    HAND = "hand"
    ZOOM = "zoom"
    SHAPE = "shape"
    PEN = "pen"
    CLONE = "clone"
    BLUR = "blur"
    SHARPEN = "sharpen"
    DODGE = "dodge"
    BURN = "burn"


class ToolState(Enum):
    """Tool interaction states."""
    IDLE = "idle"
    HOVER = "hover"
    ACTIVE = "active"
    DRAGGING = "dragging"


@dataclass
class BrushSettings:
    """Settings for brush-based tools."""
    size: int = 10
    hardness: float = 1.0  # 0-1, soft to hard edge
    opacity: float = 1.0
    flow: float = 1.0
    spacing: float = 0.25  # As fraction of brush size
    smoothing: float = 0.5
    pressure_size: bool = True
    pressure_opacity: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'size': self.size,
            'hardness': self.hardness,
            'opacity': self.opacity,
            'flow': self.flow,
            'spacing': self.spacing,
            'smoothing': self.smoothing,
            'pressure_size': self.pressure_size,
            'pressure_opacity': self.pressure_opacity
        }


class NTool(QObject):
    """
    Base class for all Newton Image tools.
    
    Tools are NObjects that:
    - Have state (idle, active, dragging)
    - Emit signals for UI updates
    - Record their actions for undo
    """
    
    # Signals
    state_changed = pyqtSignal(object)  # ToolState
    settings_changed = pyqtSignal()
    stroke_started = pyqtSignal()
    stroke_ended = pyqtSignal()
    cursor_changed = pyqtSignal(object)  # QCursor
    
    def __init__(self, 
                 tool_type: ToolType,
                 name: str,
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self._id = str(uuid.uuid4())
        self._type = tool_type
        self._name = name
        self._state = ToolState.IDLE
        
        # Tool-specific settings
        self._settings: Dict[str, Any] = {}
        
        # Stroke tracking
        self._stroke_id: Optional[str] = None
        self._stroke_points: List[QPointF] = []
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def tool_type(self) -> ToolType:
        return self._type
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def state(self) -> ToolState:
        return self._state
    
    @state.setter
    def state(self, value: ToolState) -> None:
        if self._state != value:
            self._state = value
            self.state_changed.emit(value)
    
    def begin_stroke(self, point: QPointF, pressure: float = 1.0) -> None:
        """Start a new stroke."""
        self._stroke_id = str(uuid.uuid4())
        self._stroke_points = [point]
        self._state = ToolState.ACTIVE
        self.stroke_started.emit()
    
    def continue_stroke(self, point: QPointF, pressure: float = 1.0) -> None:
        """Continue current stroke."""
        if self._stroke_id:
            self._stroke_points.append(point)
    
    def end_stroke(self) -> List[QPointF]:
        """End current stroke, return points."""
        points = self._stroke_points.copy()
        self._stroke_id = None
        self._stroke_points = []
        self._state = ToolState.IDLE
        self.stroke_ended.emit()
        return points
    
    def cancel_stroke(self) -> None:
        """Cancel current stroke without applying."""
        self._stroke_id = None
        self._stroke_points = []
        self._state = ToolState.IDLE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self._id,
            'type': self._type.value,
            'name': self._name,
            'state': self._state.value,
            'settings': self._settings
        }


class NBrushTool(NTool):
    """
    Brush tool for painting.
    
    Features:
    - Variable size and hardness
    - Pressure sensitivity
    - Smooth stroke interpolation
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.BRUSH, "Brush", parent)
        
        self.settings = BrushSettings()
        self._color = QColor(0, 0, 0)
        
    @property
    def color(self) -> QColor:
        return self._color
    
    @color.setter
    def color(self, value: QColor) -> None:
        self._color = value
        self.settings_changed.emit()
    
    def create_brush_tip(self, size: int, hardness: float) -> QImage:
        """Create brush tip image with falloff."""
        tip = QImage(size, size, QImage.Format.Format_ARGB32)
        tip.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(tip)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = size / 2
        radius = size / 2
        
        # Create radial gradient for soft edge
        if hardness < 1.0:
            gradient = QLinearGradient()
            # Draw with alpha falloff
            for r in range(int(radius), 0, -1):
                # Calculate alpha based on distance and hardness
                dist = r / radius
                if dist > hardness:
                    alpha = int(255 * (1 - (dist - hardness) / (1 - hardness)))
                else:
                    alpha = 255
                
                color = QColor(self._color)
                color.setAlpha(alpha)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(
                    int(center - r), int(center - r),
                    int(r * 2), int(r * 2)
                )
        else:
            # Hard brush
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self._color))
            painter.drawEllipse(0, 0, size, size)
        
        painter.end()
        return tip
    
    def paint_stroke(self, 
                     target: QImage,
                     points: List[QPointF],
                     pressure: float = 1.0) -> None:
        """Paint a stroke onto target image."""
        if len(points) < 2:
            return
        
        size = int(self.settings.size * (pressure if self.settings.pressure_size else 1.0))
        opacity = self.settings.opacity * (pressure if self.settings.pressure_opacity else 1.0)
        
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(opacity * self.settings.flow)
        
        # Create brush tip
        tip = self.create_brush_tip(size, self.settings.hardness)
        
        # Interpolate points for smooth stroke
        spacing = max(1, int(size * self.settings.spacing))
        
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            dist = math.sqrt(dx * dx + dy * dy)
            
            steps = max(1, int(dist / spacing))
            for step in range(steps):
                t = step / steps
                x = p1.x() + dx * t - size / 2
                y = p1.y() + dy * t - size / 2
                painter.drawImage(int(x), int(y), tip)
        
        painter.end()


class NEraserTool(NTool):
    """
    Eraser tool - paints with transparency.
    
    Uses same brush engine but erases instead of paints.
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.ERASER, "Eraser", parent)
        self.settings = BrushSettings()
    
    def erase_stroke(self,
                     target: QImage,
                     points: List[QPointF],
                     pressure: float = 1.0) -> None:
        """Erase along stroke path."""
        if len(points) < 2:
            return
        
        size = int(self.settings.size * (pressure if self.settings.pressure_size else 1.0))
        
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        
        pen = QPen(QColor(0, 0, 0, 0), size, Qt.PenStyle.SolidLine, 
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # Draw path
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        
        painter.drawPath(path)
        painter.end()


class NSelectTool(NTool):
    """Base class for selection tools."""
    
    selection_changed = pyqtSignal(object)  # QImage mask or None
    
    def __init__(self, 
                 tool_type: ToolType,
                 name: str,
                 parent: Optional[QObject] = None):
        super().__init__(tool_type, name, parent)
        
        self._selection: Optional[QImage] = None
        self._feather = 0
        self._anti_alias = True
    
    @property
    def selection(self) -> Optional[QImage]:
        return self._selection
    
    @property
    def feather(self) -> int:
        return self._feather
    
    @feather.setter
    def feather(self, value: int) -> None:
        self._feather = max(0, value)
        self.settings_changed.emit()
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        self._selection = None
        self.selection_changed.emit(None)


class NRectSelectTool(NSelectTool):
    """Rectangular marquee selection tool."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.SELECT_RECT, "Rectangular Marquee", parent)
        
        self._start_point: Optional[QPointF] = None
        self._current_rect: Optional[QRectF] = None
    
    def begin_stroke(self, point: QPointF, pressure: float = 1.0) -> None:
        """Start selection from point."""
        super().begin_stroke(point, pressure)
        self._start_point = point
        self._current_rect = QRectF(point, point)
    
    def continue_stroke(self, point: QPointF, pressure: float = 1.0) -> None:
        """Update selection rectangle."""
        super().continue_stroke(point, pressure)
        if self._start_point:
            self._current_rect = QRectF(self._start_point, point).normalized()
    
    def end_stroke(self) -> List[QPointF]:
        """Finalize selection."""
        points = super().end_stroke()
        # Keep the rect for later use
        return points
    
    @property
    def selection_rect(self) -> Optional[QRectF]:
        """Get the current selection rectangle."""
        return self._current_rect
    
    def create_selection(self, 
                         width: int, 
                         height: int,
                         rect: Tuple[int, int, int, int]) -> QImage:
        """Create a selection mask from rectangle."""
        mask = QImage(width, height, QImage.Format.Format_ARGB32)
        mask.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(mask)
        if self._anti_alias:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
        
        x, y, w, h = rect
        painter.drawRect(x, y, w, h)
        painter.end()
        
        self._selection = mask
        self.selection_changed.emit(mask)
        return mask


class NMoveTool(NTool):
    """Move tool for repositioning layers."""
    
    position_changed = pyqtSignal(int, int)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.MOVE, "Move", parent)
        
        self._start_pos: Optional[QPointF] = None
        self._layer_start_pos: Optional[Tuple[int, int]] = None
    
    def begin_move(self, point: QPointF, layer_pos: Tuple[int, int]) -> None:
        """Start moving a layer."""
        self._start_pos = point
        self._layer_start_pos = layer_pos
        self.state = ToolState.DRAGGING
    
    def update_move(self, point: QPointF) -> Tuple[int, int]:
        """Update layer position during move."""
        if self._start_pos and self._layer_start_pos:
            dx = int(point.x() - self._start_pos.x())
            dy = int(point.y() - self._start_pos.y())
            new_x = self._layer_start_pos[0] + dx
            new_y = self._layer_start_pos[1] + dy
            self.position_changed.emit(new_x, new_y)
            return (new_x, new_y)
        return (0, 0)
    
    def end_move(self) -> Optional[Tuple[int, int]]:
        """End move operation."""
        self._start_pos = None
        self._layer_start_pos = None
        self.state = ToolState.IDLE


class NTextTool(NTool):
    """Text tool for adding text layers."""
    
    text_created = pyqtSignal(str, object, object)  # text, position, settings
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.TEXT, "Text", parent)
        
        self.font_family = "SF Pro Display"
        self.font_size = 24
        self.font_weight = 400
        self.text_color = QColor(0, 0, 0)
        self.alignment = Qt.AlignmentFlag.AlignLeft
    
    def create_text_layer(self, 
                          text: str,
                          position: QPointF,
                          width: int,
                          height: int) -> QImage:
        """Create an image with rendered text."""
        from PyQt6.QtGui import QFont
        
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        font = QFont()
        font.setFamily(self.font_family)
        if self.font_size > 0:
            font.setPointSize(self.font_size)
        else:
            font.setPointSize(12)
        font.setWeight(self.font_weight)
        painter.setFont(font)
        painter.setPen(self.text_color)
        
        # Draw text
        rect = image.rect()
        rect.moveTopLeft(position.toPoint())
        painter.drawText(rect, int(self.alignment), text)
        
        painter.end()
        
        self.text_created.emit(text, position, {
            'font': self.font_family,
            'size': self.font_size,
            'weight': self.font_weight,
            'color': self.text_color.name()
        })
        
        return image


class NEyedropperTool(NTool):
    """Eyedropper tool for color sampling."""
    
    color_sampled = pyqtSignal(object)  # QColor
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(ToolType.EYEDROPPER, "Eyedropper", parent)
        
        self._sampled_color: Optional[QColor] = None
        self._sample_size = 1  # 1 = point sample, 3 = 3x3 average, etc.
    
    @property
    def sampled_color(self) -> Optional[QColor]:
        return self._sampled_color
    
    @property
    def sample_size(self) -> int:
        return self._sample_size
    
    @sample_size.setter
    def sample_size(self, value: int) -> None:
        self._sample_size = max(1, value)
        self.settings_changed.emit()
    
    def sample(self, image: QImage, point: QPointF) -> QColor:
        """Sample color from image at point."""
        x, y = int(point.x()), int(point.y())
        
        if self._sample_size == 1:
            # Point sample
            color = image.pixelColor(x, y)
        else:
            # Average over sample area
            half = self._sample_size // 2
            r_sum, g_sum, b_sum, count = 0, 0, 0, 0
            
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    px, py = x + dx, y + dy
                    if 0 <= px < image.width() and 0 <= py < image.height():
                        c = image.pixelColor(px, py)
                        r_sum += c.red()
                        g_sum += c.green()
                        b_sum += c.blue()
                        count += 1
            
            if count > 0:
                color = QColor(
                    r_sum // count,
                    g_sum // count,
                    b_sum // count
                )
            else:
                color = QColor(0, 0, 0)
        
        self._sampled_color = color
        self.color_sampled.emit(color)
        return color
    
    # Alias for convenience
    def pick_color(self, image: QImage, point: QPointF) -> QColor:
        """Alias for sample()."""
        return self.sample(image, point)
