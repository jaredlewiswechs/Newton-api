"""
═══════════════════════════════════════════════════════════════
NFILTERS - VERIFIED IMAGE FILTERS
Newton-bounded computations for image processing.
Every filter terminates. Every result is deterministic.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, Any, Tuple, List
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QColor
import math


class FilterType(Enum):
    """Available filter types."""
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    HUE = "hue"
    INVERT = "invert"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    BLUR = "blur"
    SHARPEN = "sharpen"
    NOISE = "noise"
    POSTERIZE = "posterize"
    THRESHOLD = "threshold"


class NFilter(QObject):
    """
    Base class for Newton Image filters.
    
    Filters are bounded computations:
    - Max iterations = width * height (O(n) pixels)
    - Deterministic output
    - Reversible via history
    """
    
    # Newton bounds
    MAX_OPERATIONS = 100_000_000  # 10k x 10k max
    
    progress = pyqtSignal(float)  # 0-1
    completed = pyqtSignal(object)  # QImage result
    
    def __init__(self, 
                 filter_type: FilterType,
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self._type = filter_type
        self._parameters: Dict[str, Any] = {}
    
    @property
    def filter_type(self) -> FilterType:
        return self._type
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters.copy()
    
    def apply(self, image: QImage) -> QImage:
        """Apply filter to image. Override in subclasses."""
        raise NotImplementedError
    
    def _verify_bounds(self, width: int, height: int) -> bool:
        """Verify operation count is within bounds."""
        ops = width * height
        return ops <= self.MAX_OPERATIONS


class BrightnessFilter(NFilter):
    """Adjust image brightness."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.BRIGHTNESS, parent)
        self._parameters['value'] = 0  # -100 to 100
    
    @property
    def value(self) -> int:
        return self._parameters['value']
    
    @value.setter
    def value(self, v: int) -> None:
        self._parameters['value'] = max(-100, min(100, v))
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        adjustment = int(self.value * 2.55)  # Scale to 0-255
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                r = max(0, min(255, color.red() + adjustment))
                g = max(0, min(255, color.green() + adjustment))
                b = max(0, min(255, color.blue() + adjustment))
                result.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
            
            # Report progress
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class ContrastFilter(NFilter):
    """Adjust image contrast."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.CONTRAST, parent)
        self._parameters['value'] = 0  # -100 to 100
    
    @property
    def value(self) -> int:
        return self._parameters['value']
    
    @value.setter
    def value(self, v: int) -> None:
        self._parameters['value'] = max(-100, min(100, v))
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        
        # Contrast factor
        factor = (259 * (self.value + 255)) / (255 * (259 - self.value))
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                
                r = max(0, min(255, int(factor * (color.red() - 128) + 128)))
                g = max(0, min(255, int(factor * (color.green() - 128) + 128)))
                b = max(0, min(255, int(factor * (color.blue() - 128) + 128)))
                
                result.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class SaturationFilter(NFilter):
    """Adjust color saturation."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.SATURATION, parent)
        self._parameters['value'] = 0  # -100 to 100
    
    @property
    def value(self) -> int:
        return self._parameters['value']
    
    @value.setter
    def value(self, v: int) -> None:
        self._parameters['value'] = max(-100, min(100, v))
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        factor = 1 + (self.value / 100)
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                
                # Convert to HSL
                h, s, l, a = color.getHslF()
                
                # Adjust saturation
                s = max(0, min(1, s * factor))
                
                # Convert back
                new_color = QColor.fromHslF(h, s, l, a)
                result.setPixelColor(x, y, new_color)
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class GrayscaleFilter(NFilter):
    """Convert to grayscale."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.GRAYSCALE, parent)
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                
                # Luminance-preserving grayscale
                gray = int(0.299 * color.red() + 
                          0.587 * color.green() + 
                          0.114 * color.blue())
                
                result.setPixelColor(x, y, QColor(gray, gray, gray, color.alpha()))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class InvertFilter(NFilter):
    """Invert colors."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.INVERT, parent)
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                result.setPixelColor(x, y, QColor(
                    255 - color.red(),
                    255 - color.green(),
                    255 - color.blue(),
                    color.alpha()
                ))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class SepiaFilter(NFilter):
    """Apply sepia tone."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.SEPIA, parent)
        self._parameters['intensity'] = 100  # 0-100
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        intensity = self._parameters['intensity'] / 100
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                
                # Sepia transformation
                r = color.red()
                g = color.green()
                b = color.blue()
                
                new_r = int(r * 0.393 + g * 0.769 + b * 0.189)
                new_g = int(r * 0.349 + g * 0.686 + b * 0.168)
                new_b = int(r * 0.272 + g * 0.534 + b * 0.131)
                
                # Blend with original based on intensity
                final_r = int(r * (1 - intensity) + min(255, new_r) * intensity)
                final_g = int(g * (1 - intensity) + min(255, new_g) * intensity)
                final_b = int(b * (1 - intensity) + min(255, new_b) * intensity)
                
                result.setPixelColor(x, y, QColor(final_r, final_g, final_b, color.alpha()))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class BlurFilter(NFilter):
    """Gaussian blur."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.BLUR, parent)
        self._parameters['radius'] = 5  # pixels
    
    @property
    def radius(self) -> int:
        return self._parameters['radius']
    
    @radius.setter
    def radius(self, v: int) -> None:
        self._parameters['radius'] = max(1, min(50, v))  # Bounded
    
    def _create_gaussian_kernel(self, radius: int) -> List[List[float]]:
        """Create normalized Gaussian kernel."""
        size = radius * 2 + 1
        kernel = []
        sigma = radius / 3
        total = 0
        
        for y in range(-radius, radius + 1):
            row = []
            for x in range(-radius, radius + 1):
                value = math.exp(-(x*x + y*y) / (2 * sigma * sigma))
                row.append(value)
                total += value
            kernel.append(row)
        
        # Normalize
        for y in range(size):
            for x in range(size):
                kernel[y][x] /= total
        
        return kernel
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        kernel = self._create_gaussian_kernel(self.radius)
        
        for y in range(result.height()):
            for x in range(result.width()):
                r_sum, g_sum, b_sum, a_sum = 0.0, 0.0, 0.0, 0.0
                
                for ky, row in enumerate(kernel):
                    for kx, weight in enumerate(row):
                        px = x + kx - self.radius
                        py = y + ky - self.radius
                        
                        # Clamp to edges
                        px = max(0, min(image.width() - 1, px))
                        py = max(0, min(image.height() - 1, py))
                        
                        color = image.pixelColor(px, py)
                        r_sum += color.red() * weight
                        g_sum += color.green() * weight
                        b_sum += color.blue() * weight
                        a_sum += color.alpha() * weight
                
                result.setPixelColor(x, y, QColor(
                    int(r_sum), int(g_sum), int(b_sum), int(a_sum)
                ))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


class PosterizeFilter(NFilter):
    """Reduce color levels."""
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(FilterType.POSTERIZE, parent)
        self._parameters['levels'] = 4  # 2-16
    
    @property
    def levels(self) -> int:
        return self._parameters['levels']
    
    @levels.setter
    def levels(self, v: int) -> None:
        self._parameters['levels'] = max(2, min(16, v))
    
    def apply(self, image: QImage) -> QImage:
        if not self._verify_bounds(image.width(), image.height()):
            raise ValueError("Image too large for bounded computation")
        
        result = image.copy()
        step = 256 // self.levels
        
        for y in range(result.height()):
            for x in range(result.width()):
                color = result.pixelColor(x, y)
                
                r = (color.red() // step) * step
                g = (color.green() // step) * step
                b = (color.blue() // step) * step
                
                result.setPixelColor(x, y, QColor(r, g, b, color.alpha()))
            
            self.progress.emit(y / result.height())
        
        self.completed.emit(result)
        return result


# Filter factory
def create_filter(filter_type: FilterType) -> NFilter:
    """Create a filter instance by type."""
    filters = {
        FilterType.BRIGHTNESS: BrightnessFilter,
        FilterType.CONTRAST: ContrastFilter,
        FilterType.SATURATION: SaturationFilter,
        FilterType.GRAYSCALE: GrayscaleFilter,
        FilterType.INVERT: InvertFilter,
        FilterType.SEPIA: SepiaFilter,
        FilterType.BLUR: BlurFilter,
        FilterType.POSTERIZE: PosterizeFilter,
    }
    
    filter_class = filters.get(filter_type)
    if filter_class:
        return filter_class()
    
    raise ValueError(f"Unknown filter type: {filter_type}")
