"""
CAD Renderer
============

Renders building plans to PNG images.
Uses PIL/Pillow for image generation.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import math

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not installed. PNG export disabled.")

from .core import (
    Building, Level, Space, Wall, Door, Window,
    Zone, SpaceType, Furniture, Point, Rect,
    SPACE_COLORS
)


class RenderStyle(Enum):
    """Rendering styles for floor plans."""
    SCHEMATIC = "schematic"      # Simple colored boxes
    ARCHITECTURAL = "architectural"  # More detailed
    PRESENTATION = "presentation"    # High quality
    DIAGRAM = "diagram"          # Minimal, diagram style


@dataclass
class RenderConfig:
    """Configuration for rendering."""

    # Image settings
    width: int = 1920
    height: int = 1080
    dpi: int = 150
    background: str = "#FFFFFF"

    # Scale
    scale: float = 20.0  # pixels per meter
    padding: int = 80    # pixels

    # Style
    style: RenderStyle = RenderStyle.SCHEMATIC

    # Colors
    wall_color: str = "#333333"
    door_color: str = "#8B4513"
    window_color: str = "#87CEEB"
    grid_color: str = "#E8E8E8"
    text_color: str = "#333333"
    label_color: str = "#FFFFFF"

    # Line widths
    wall_width: int = 3
    outline_width: int = 2

    # Text
    title_size: int = 32
    label_size: int = 14
    area_size: int = 11

    # Features
    show_grid: bool = True
    show_labels: bool = True
    show_areas: bool = True
    show_dimensions: bool = False
    show_compass: bool = True
    show_scale_bar: bool = True
    show_title: bool = True


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def darken(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color."""
    rgb = hex_to_rgb(hex_color)
    darkened = tuple(int(c * factor) for c in rgb)
    return rgb_to_hex(darkened)


def lighten(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color."""
    rgb = hex_to_rgb(hex_color)
    lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
    return rgb_to_hex(lightened)


class CADRenderer:
    """
    Renders building floor plans to images.
    """

    def __init__(self, config: Optional[RenderConfig] = None):
        if not HAS_PIL:
            raise ImportError("PIL/Pillow is required for rendering. Install with: pip install Pillow")

        self.config = config or RenderConfig()
        self._font_cache: Dict[int, Any] = {}

    def _get_font(self, size: int) -> Any:
        """Get or create a font at the specified size."""
        if size not in self._font_cache:
            try:
                # Try to load a nice font
                for font_name in [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/TTF/DejaVuSans.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "arial.ttf",
                    "Arial.ttf",
                ]:
                    try:
                        self._font_cache[size] = ImageFont.truetype(font_name, size)
                        break
                    except (OSError, IOError):
                        continue
                else:
                    # Fall back to default
                    self._font_cache[size] = ImageFont.load_default()
            except Exception:
                self._font_cache[size] = ImageFont.load_default()

        return self._font_cache[size]

    def _world_to_screen(self, point: Point, offset: Point) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        x = int(self.config.padding + (point.x + offset.x) * self.config.scale)
        y = int(self.config.padding + (point.y + offset.y) * self.config.scale)
        return (x, y)

    def _rect_to_screen(self, rect: Rect, offset: Point) -> Tuple[int, int, int, int]:
        """Convert world rect to screen coordinates."""
        x1 = int(self.config.padding + (rect.x + offset.x) * self.config.scale)
        y1 = int(self.config.padding + (rect.y + offset.y) * self.config.scale)
        x2 = int(self.config.padding + (rect.x + rect.width + offset.x) * self.config.scale)
        y2 = int(self.config.padding + (rect.y + rect.height + offset.y) * self.config.scale)
        return (x1, y1, x2, y2)

    def render_level(self, level: Level, title: Optional[str] = None) -> Image.Image:
        """Render a single level to an image."""

        # Calculate image size based on level bounds
        img_width = int(level.bounds.width * self.config.scale + self.config.padding * 2)
        img_height = int(level.bounds.height * self.config.scale + self.config.padding * 2)

        # Add space for title
        title_height = 60 if self.config.show_title else 0
        img_height += title_height

        # Ensure minimum size
        img_width = max(img_width, 800)
        img_height = max(img_height, 600)

        # Create image
        img = Image.new('RGB', (img_width, img_height), self.config.background)
        draw = ImageDraw.Draw(img)

        # Offset for centering
        offset = Point(0, 0)

        # Draw grid
        if self.config.show_grid:
            self._draw_grid(draw, level.bounds, offset, title_height)

        # Draw spaces
        for space in level.spaces:
            self._draw_space(draw, space, offset, title_height)

        # Draw walls
        for wall in level.walls:
            self._draw_wall(draw, wall, offset, title_height)

        # Draw title
        if self.config.show_title:
            display_title = title or f"{level.name}"
            self._draw_title(draw, display_title, img_width, level)

        # Draw scale bar
        if self.config.show_scale_bar:
            self._draw_scale_bar(draw, img_width, img_height)

        # Draw compass
        if self.config.show_compass:
            self._draw_compass(draw, img_width, title_height)

        return img

    def _draw_grid(
        self,
        draw: ImageDraw.Draw,
        bounds: Rect,
        offset: Point,
        title_offset: int
    ) -> None:
        """Draw background grid."""
        grid_spacing = 5.0  # 5 meter grid

        color = self.config.grid_color

        # Vertical lines
        x = 0
        while x <= bounds.width:
            x1, y1 = self._world_to_screen(Point(x, 0), offset)
            x2, y2 = self._world_to_screen(Point(x, bounds.height), offset)
            y1 += title_offset
            y2 += title_offset
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
            x += grid_spacing

        # Horizontal lines
        y = 0
        while y <= bounds.height:
            x1, y1 = self._world_to_screen(Point(0, y), offset)
            x2, y2 = self._world_to_screen(Point(bounds.width, y), offset)
            y1 += title_offset
            y2 += title_offset
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
            y += grid_spacing

    def _draw_space(
        self,
        draw: ImageDraw.Draw,
        space: Space,
        offset: Point,
        title_offset: int
    ) -> None:
        """Draw a space (room)."""
        rect = self._rect_to_screen(space.bounds, offset)
        rect = (rect[0], rect[1] + title_offset, rect[2], rect[3] + title_offset)

        # Fill
        fill_color = space.color
        draw.rectangle(rect, fill=fill_color)

        # Outline
        outline_color = darken(fill_color, 0.6)
        draw.rectangle(rect, outline=outline_color, width=self.config.outline_width)

        # Label
        if self.config.show_labels:
            # Calculate center
            cx = (rect[0] + rect[2]) // 2
            cy = (rect[1] + rect[3]) // 2

            # Get text
            label = space.display_name

            # Choose text color based on background brightness
            rgb = hex_to_rgb(fill_color)
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            text_color = "#FFFFFF" if brightness < 128 else "#333333"

            # Draw label
            font = self._get_font(self.config.label_size)
            bbox = draw.textbbox((cx, cy), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Only draw if space is big enough
            space_width = rect[2] - rect[0]
            space_height = rect[3] - rect[1]

            if text_width < space_width - 10 and text_height < space_height - 10:
                draw.text(
                    (cx - text_width // 2, cy - text_height // 2 - 5),
                    label,
                    fill=text_color,
                    font=font
                )

                # Draw area
                if self.config.show_areas:
                    area_text = f"{space.area:.0f} m²"
                    area_font = self._get_font(self.config.area_size)
                    draw.text(
                        (cx - text_width // 2, cy + text_height // 2),
                        area_text,
                        fill=text_color,
                        font=area_font
                    )

    def _draw_wall(
        self,
        draw: ImageDraw.Draw,
        wall: Wall,
        offset: Point,
        title_offset: int
    ) -> None:
        """Draw a wall segment."""
        start = self._world_to_screen(wall.start, offset)
        end = self._world_to_screen(wall.end, offset)

        start = (start[0], start[1] + title_offset)
        end = (end[0], end[1] + title_offset)

        width = int(wall.thickness * self.config.scale)
        width = max(width, self.config.wall_width)

        color = self.config.wall_color
        if wall.exterior:
            color = darken(color, 0.5)

        draw.line([start, end], fill=color, width=width)

    def _draw_title(
        self,
        draw: ImageDraw.Draw,
        title: str,
        img_width: int,
        level: Level
    ) -> None:
        """Draw the title bar."""
        # Background
        draw.rectangle(
            [(0, 0), (img_width, 55)],
            fill="#2C3E50"
        )

        # Title text
        font = self._get_font(self.config.title_size)
        draw.text(
            (self.config.padding, 10),
            title,
            fill="#FFFFFF",
            font=font
        )

        # Level info
        info_font = self._get_font(14)
        info_text = f"Area: {level.total_area:,.0f} m²  |  Efficiency: {level.efficiency:.0%}"
        bbox = draw.textbbox((0, 0), info_text, font=info_font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (img_width - text_width - self.config.padding, 20),
            info_text,
            fill="#BDC3C7",
            font=info_font
        )

    def _draw_scale_bar(
        self,
        draw: ImageDraw.Draw,
        img_width: int,
        img_height: int
    ) -> None:
        """Draw a scale bar."""
        bar_length = 10  # meters
        bar_pixels = int(bar_length * self.config.scale)

        x1 = self.config.padding
        x2 = x1 + bar_pixels
        y = img_height - 30

        # Bar
        draw.line([(x1, y), (x2, y)], fill="#333333", width=3)
        draw.line([(x1, y - 5), (x1, y + 5)], fill="#333333", width=2)
        draw.line([(x2, y - 5), (x2, y + 5)], fill="#333333", width=2)

        # Label
        font = self._get_font(12)
        draw.text((x1 + bar_pixels // 2 - 15, y + 8), f"{bar_length}m", fill="#333333", font=font)

    def _draw_compass(
        self,
        draw: ImageDraw.Draw,
        img_width: int,
        title_offset: int
    ) -> None:
        """Draw a north compass."""
        cx = img_width - 50
        cy = title_offset + 50
        size = 20

        # Arrow
        points = [
            (cx, cy - size),      # North point
            (cx - 8, cy + 8),     # Bottom left
            (cx, cy),             # Center
            (cx + 8, cy + 8),     # Bottom right
        ]
        draw.polygon(points, fill="#333333")

        # N label
        font = self._get_font(14)
        draw.text((cx - 4, cy - size - 18), "N", fill="#333333", font=font)

    def render_building(self, building: Building) -> List[Image.Image]:
        """Render all levels of a building."""
        images = []
        for level in building.levels:
            title = f"{building.name} - {level.name}"
            img = self.render_level(level, title)
            images.append(img)
        return images


def export_png(
    level: Level,
    path: str,
    config: Optional[RenderConfig] = None,
    title: Optional[str] = None
) -> str:
    """Export a level to PNG."""
    renderer = CADRenderer(config)
    img = renderer.render_level(level, title)
    img.save(path, "PNG")
    return path


def export_all_levels(
    building: Building,
    output_dir: str,
    config: Optional[RenderConfig] = None
) -> List[str]:
    """Export all levels of a building to PNG files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    renderer = CADRenderer(config)
    paths = []

    for level in building.levels:
        # Create filename
        safe_name = level.name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{building.name.lower().replace(' ', '_')}_{safe_name}.png"
        filepath = output_path / filename

        # Render and save
        title = f"{building.name} - {level.name}"
        img = renderer.render_level(level, title)
        img.save(str(filepath), "PNG")
        paths.append(str(filepath))

    return paths
