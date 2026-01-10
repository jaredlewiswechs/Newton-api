"""
3D Renderer - Newton CAD
========================

Software 3D renderer with Newton f/g visualization:
- Isometric and perspective projection
- Painter's algorithm (depth sorting)
- Directional lighting with ambient
- f/g ratio color coding (green/amber/red)
- Constraint state visualization
- PNG export

The Floor of Newton: The ground plane IS the constraint (g).
Building volumes are Matter (f) applied against the Floor.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import math

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .geometry3d import (
    Vec3, Mat4, Triangle, Quad, Box,
    hex_to_rgb, shade_color, blend_colors, clamp
)


# =============================================================================
# f/g Visual Language Colors (from Newton type theory)
# =============================================================================

class FGState(Enum):
    """Newton f/g constraint states."""
    VERIFIED = "verified"      # f/g < 0.9θ  - Safe margin
    WARNING = "warning"        # 0.9θ ≤ f/g < θ - Approaching boundary
    FORBIDDEN = "forbidden"    # f/g ≥ θ - Constraint violated
    UNDEFINED = "undefined"    # g ≈ 0 - Ontological death (finfr)


# f/g Visual Language colors from docs/product-architecture/FG_VISUAL_LANGUAGE.md
FG_COLORS = {
    FGState.VERIFIED: (0, 200, 83),      # #00C853 - Green
    FGState.WARNING: (255, 214, 0),      # #FFD600 - Amber
    FGState.FORBIDDEN: (255, 23, 68),    # #FF1744 - Red
    FGState.UNDEFINED: (183, 28, 28),    # #B71C1C - Deep Red (finfr)
}


def get_fg_state(f: float, g: float, threshold: float = 1.0) -> FGState:
    """Determine f/g state from ratio values."""
    if g <= 0:
        return FGState.UNDEFINED
    ratio = f / g
    if ratio >= threshold:
        return FGState.FORBIDDEN
    if ratio >= threshold * 0.9:
        return FGState.WARNING
    return FGState.VERIFIED


def get_fg_color(f: float, g: float, threshold: float = 1.0) -> Tuple[int, int, int]:
    """Get color based on f/g ratio."""
    state = get_fg_state(f, g, threshold)
    return FG_COLORS.get(state, (176, 190, 197))


class ProjectionType(Enum):
    """Types of 3D projection."""
    ISOMETRIC = "isometric"
    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"
    DIMETRIC = "dimetric"


class ViewAngle(Enum):
    """Preset view angles."""
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    ISOMETRIC_NE = "isometric_ne"  # Northeast
    ISOMETRIC_NW = "isometric_nw"  # Northwest
    ISOMETRIC_SE = "isometric_se"  # Southeast
    ISOMETRIC_SW = "isometric_sw"  # Southwest
    BIRD_EYE = "bird_eye"
    WORM_EYE = "worm_eye"


@dataclass
class Light:
    """A directional light source."""
    direction: Vec3
    color: Tuple[int, int, int] = (255, 255, 255)
    intensity: float = 1.0

    def __post_init__(self):
        self.direction = self.direction.normalized()


@dataclass
class Camera:
    """3D camera."""
    position: Vec3
    target: Vec3
    up: Vec3 = field(default_factory=lambda: Vec3(0, 0, 1))
    fov: float = 60.0  # degrees
    near: float = 0.1
    far: float = 1000.0

    def get_view_matrix(self) -> Mat4:
        return Mat4.look_at(self.position, self.target, self.up)

    def get_direction(self) -> Vec3:
        return (self.target - self.position).normalized()


@dataclass
class Render3DConfig:
    """Configuration for 3D rendering."""

    # Image
    width: int = 1920
    height: int = 1080
    background: Tuple[int, int, int] = (240, 245, 250)

    # Projection
    projection: ProjectionType = ProjectionType.ISOMETRIC
    scale: float = 12.0  # For isometric/ortho

    # Lighting
    ambient: float = 0.35
    diffuse: float = 0.65
    sun_direction: Vec3 = field(default_factory=lambda: Vec3(-0.5, -0.3, -0.8))
    sun_color: Tuple[int, int, int] = (255, 252, 245)

    # Style
    show_edges: bool = True
    edge_color: Tuple[int, int, int] = (60, 60, 70)
    edge_width: int = 1

    # Ground
    show_ground: bool = True
    ground_color: Tuple[int, int, int] = (200, 210, 190)
    ground_size: float = 200.0

    # Sky gradient
    show_sky: bool = True
    sky_top: Tuple[int, int, int] = (135, 180, 220)
    sky_bottom: Tuple[int, int, int] = (220, 235, 250)

    # Shadow
    show_shadows: bool = True
    shadow_opacity: float = 0.25

    # Title
    show_title: bool = True
    title: str = ""


class Renderer3D:
    """
    Software 3D renderer.

    Renders a list of triangles to a 2D image using:
    - Configurable projection (isometric, perspective, ortho)
    - Painter's algorithm for depth sorting
    - Lambert diffuse shading
    - Optional edge rendering
    """

    def __init__(self, config: Optional[Render3DConfig] = None):
        if not HAS_PIL:
            raise ImportError("PIL/Pillow required for 3D rendering")

        self.config = config or Render3DConfig()
        self.triangles: List[Triangle] = []
        self.camera: Optional[Camera] = None
        self._font_cache: Dict[int, Any] = {}

    def _get_font(self, size: int):
        """Get or create font."""
        if size not in self._font_cache:
            try:
                for font_path in [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "arial.ttf",
                ]:
                    try:
                        self._font_cache[size] = ImageFont.truetype(font_path, size)
                        break
                    except:
                        continue
                else:
                    self._font_cache[size] = ImageFont.load_default()
            except:
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def set_camera_from_view(self, view: ViewAngle, target: Vec3, distance: float = 100):
        """Set camera from a preset view angle."""
        angles = {
            ViewAngle.FRONT: (0, 0),
            ViewAngle.BACK: (180, 0),
            ViewAngle.LEFT: (90, 0),
            ViewAngle.RIGHT: (-90, 0),
            ViewAngle.TOP: (0, 90),
            ViewAngle.ISOMETRIC_NE: (-45, 35),
            ViewAngle.ISOMETRIC_NW: (45, 35),
            ViewAngle.ISOMETRIC_SE: (-135, 35),
            ViewAngle.ISOMETRIC_SW: (135, 35),
            ViewAngle.BIRD_EYE: (-45, 60),
            ViewAngle.WORM_EYE: (-45, -20),
        }

        yaw, pitch = angles.get(view, (-45, 35))
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)

        # Calculate camera position
        x = distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        y = distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        z = distance * math.sin(pitch_rad)

        self.camera = Camera(
            position=target + Vec3(x, y, z),
            target=target,
            up=Vec3(0, 0, 1)
        )

    def project(self, point: Vec3) -> Tuple[float, float, float]:
        """Project 3D point to 2D screen coordinates.

        Uses standard 2D isometric projection formula:
        - screen_x = (x - y) * scale
        - screen_y = (x + y) / 2 * scale - z * scale

        This maps the 3D world where:
        - X/Y are horizontal floor plane axes
        - Z is vertical (up)

        To 2D screen where:
        - Higher Z = higher on screen (smaller screen_y)
        - Objects at z=0 sit on the ground plane
        """
        cfg = self.config
        cx = cfg.width / 2
        cy = cfg.height / 2

        if cfg.projection == ProjectionType.ISOMETRIC:
            # Standard 2D isometric projection
            # This is the classic game/CAD isometric formula

            # Screen X: diagonal based on world x and y
            screen_x = (point.x - point.y) * cfg.scale * 0.866  # cos(30°)

            # Screen Y: combination of x+y (depth on floor) minus z (height)
            # The 0.5 factor creates the isometric angle
            # Z directly affects vertical screen position
            screen_y = (point.x + point.y) * cfg.scale * 0.5 - point.z * cfg.scale

            # Depth for painter's algorithm sorting
            # Objects further from camera (higher x+y, lower z) render first
            depth = point.x + point.y - point.z * 2

            return (cx + screen_x, cy + screen_y, depth)

        elif cfg.projection == ProjectionType.PERSPECTIVE:
            if not self.camera:
                self.set_camera_from_view(ViewAngle.ISOMETRIC_NE, Vec3.zero(), 100)

            # View transform
            view = self.camera.get_view_matrix()
            p = view.transform(point)

            # Perspective divide
            fov_rad = math.radians(self.camera.fov)
            f = 1.0 / math.tan(fov_rad / 2)

            if p.z < 0.1:
                p.z = 0.1  # Clamp near plane

            screen_x = (p.x / p.z) * f * cfg.height / 2
            screen_y = (p.y / p.z) * f * cfg.height / 2

            return (cx + screen_x, cy - screen_y, p.z)

        else:  # Orthographic
            return (cx + point.x * cfg.scale, cy - point.y * cfg.scale, -point.z)

    def calculate_lighting(self, normal: Vec3, base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Calculate lit color using Lambert diffuse."""
        cfg = self.config

        # Normalize light direction (pointing toward light)
        light_dir = (-cfg.sun_direction).normalized()

        # Lambert diffuse
        ndotl = max(0, normal.dot(light_dir))

        # Combine ambient and diffuse
        intensity = cfg.ambient + cfg.diffuse * ndotl

        # Apply to color
        r = int(clamp(base_color[0] * intensity, 0, 255))
        g = int(clamp(base_color[1] * intensity, 0, 255))
        b = int(clamp(base_color[2] * intensity, 0, 255))

        return (r, g, b)

    def render_triangles(self, triangles: List[Triangle], title: str = "") -> Image.Image:
        """Render a list of triangles to an image."""
        cfg = self.config
        img = Image.new('RGB', (cfg.width, cfg.height), cfg.background)
        draw = ImageDraw.Draw(img)

        # Draw sky gradient
        if cfg.show_sky:
            for y in range(cfg.height // 2):
                t = y / (cfg.height // 2)
                color = blend_colors(cfg.sky_top, cfg.sky_bottom, t)
                draw.line([(0, y), (cfg.width, y)], fill=color)

        # Draw ground plane
        if cfg.show_ground:
            # Simple ground representation
            ground_y = cfg.height * 0.7
            draw.rectangle(
                [(0, int(ground_y)), (cfg.width, cfg.height)],
                fill=cfg.ground_color
            )

        # Project all triangles and calculate depth
        projected = []
        for tri in triangles:
            p0 = self.project(tri.v0)
            p1 = self.project(tri.v1)
            p2 = self.project(tri.v2)

            # Calculate average depth for sorting
            avg_depth = (p0[2] + p1[2] + p2[2]) / 3

            # Backface culling (for isometric, check normal.z)
            if cfg.projection == ProjectionType.ISOMETRIC:
                # Recalculate screen-space normal
                edge1 = (p1[0] - p0[0], p1[1] - p0[1])
                edge2 = (p2[0] - p0[0], p2[1] - p0[1])
                cross_z = edge1[0] * edge2[1] - edge1[1] * edge2[0]
                if cross_z < 0:
                    continue  # Backface

            projected.append((avg_depth, tri, [p0, p1, p2]))

        # Sort by depth (painter's algorithm - far to near)
        projected.sort(key=lambda x: x[0], reverse=True)

        # Draw shadows first (if enabled)
        if cfg.show_shadows:
            shadow_offset = (20, 15)
            for _, tri, points in projected:
                shadow_points = [
                    (p[0] + shadow_offset[0], p[1] + shadow_offset[1])
                    for p in points
                ]
                shadow_color = tuple(
                    int(c * (1 - cfg.shadow_opacity))
                    for c in cfg.ground_color
                )
                draw.polygon(shadow_points, fill=shadow_color)

        # Draw triangles
        for _, tri, points in projected:
            screen_points = [(p[0], p[1]) for p in points]

            # Calculate lit color
            if tri.normal:
                lit_color = self.calculate_lighting(tri.normal, tri.color)
            else:
                lit_color = tri.color

            # Fill triangle
            draw.polygon(screen_points, fill=lit_color)

            # Draw edges
            if cfg.show_edges:
                draw.line([screen_points[0], screen_points[1]], fill=cfg.edge_color, width=cfg.edge_width)
                draw.line([screen_points[1], screen_points[2]], fill=cfg.edge_color, width=cfg.edge_width)
                draw.line([screen_points[2], screen_points[0]], fill=cfg.edge_color, width=cfg.edge_width)

        # Draw title
        if cfg.show_title and (title or cfg.title):
            display_title = title or cfg.title
            self._draw_title(draw, display_title)

        return img

    def _draw_title(self, draw: ImageDraw.Draw, title: str):
        """Draw title bar."""
        cfg = self.config

        # Title background
        draw.rectangle([(0, 0), (cfg.width, 60)], fill=(35, 45, 60))

        # Title text
        font = self._get_font(28)
        draw.text((30, 15), title, fill=(255, 255, 255), font=font)

        # Subtitle
        sub_font = self._get_font(14)
        draw.text(
            (cfg.width - 200, 22),
            "Construct Studio CAD",
            fill=(150, 160, 170),
            font=sub_font
        )

    def render(self, title: str = "") -> Image.Image:
        """Render stored triangles."""
        return self.render_triangles(self.triangles, title)


def create_building_mesh(
    x: float, y: float, z: float,
    width: float, depth: float, height: float,
    color: Tuple[int, int, int],
    roof_color: Optional[Tuple[int, int, int]] = None
) -> List[Triangle]:
    """Create triangles for a building box."""
    box = Box(
        min_point=Vec3(x, y, z),
        max_point=Vec3(x + width, y + depth, z + height),
        color=color,
        top_color=roof_color or shade_color(color, 1.1)
    )
    return box.to_triangles()


def create_ground_plane(
    size: float,
    color: Tuple[int, int, int] = (180, 195, 170),
    center: Vec3 = None
) -> List[Triangle]:
    """Create a ground plane."""
    if center is None:
        center = Vec3.zero()

    half = size / 2
    v0 = Vec3(center.x - half, center.y - half, 0)
    v1 = Vec3(center.x + half, center.y - half, 0)
    v2 = Vec3(center.x + half, center.y + half, 0)
    v3 = Vec3(center.x - half, center.y + half, 0)

    return [
        Triangle(v0, v1, v2, color),
        Triangle(v0, v2, v3, color)
    ]


def render_building_3d(
    levels: List[Dict],
    config: Optional[Render3DConfig] = None,
    view: ViewAngle = ViewAngle.ISOMETRIC_SW,
    title: str = ""
) -> Image.Image:
    """
    Render a multi-level building in 3D.

    Args:
        levels: List of level dicts with 'spaces', 'elevation', 'height'
        config: Render configuration
        view: Camera view angle
        title: Title to display

    Returns:
        PIL Image
    """
    config = config or Render3DConfig()
    renderer = Renderer3D(config)

    all_triangles = []

    # Calculate building bounds for camera
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    max_z = 0

    for level in levels:
        elevation = level.get('elevation', 0)
        height = level.get('height', 4)

        for space in level.get('spaces', []):
            x, y = space['x'], space['y']
            w, h = space['width'], space['height']
            color = hex_to_rgb(space.get('color', '#CCCCCC'))

            # Track bounds
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
            max_z = max(max_z, elevation + height)

            # Create building mesh
            tris = create_building_mesh(
                x, y, elevation,
                w, h, height,
                color
            )
            all_triangles.extend(tris)

    # Add ground plane
    ground_tris = create_ground_plane(
        max(max_x - min_x, max_y - min_y) * 1.5,
        config.ground_color,
        Vec3((max_x + min_x) / 2, (max_y + min_y) / 2, 0)
    )
    all_triangles.extend(ground_tris)

    # Set camera based on building bounds
    center = Vec3(
        (max_x + min_x) / 2,
        (max_y + min_y) / 2,
        max_z / 2
    )
    distance = max(max_x - min_x, max_y - min_y, max_z) * 1.5

    renderer.set_camera_from_view(view, center, distance)

    return renderer.render_triangles(all_triangles, title)
