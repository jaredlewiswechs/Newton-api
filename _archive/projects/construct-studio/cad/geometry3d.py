"""
3D Geometry Engine
==================

Vector math, matrices, and 3D transformations.
The mathematical foundation for 3D CAD rendering.
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class Vec3:
    """3D vector."""
    x: float
    y: float
    z: float

    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> 'Vec3':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> 'Vec3':
        return Vec3(-self.x, -self.y, -self.z)

    def dot(self, other: 'Vec3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vec3') -> 'Vec3':
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self) -> 'Vec3':
        l = self.length()
        if l == 0:
            return Vec3(0, 0, 0)
        return self / l

    def tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @staticmethod
    def zero() -> 'Vec3':
        return Vec3(0, 0, 0)

    @staticmethod
    def up() -> 'Vec3':
        return Vec3(0, 0, 1)

    @staticmethod
    def forward() -> 'Vec3':
        return Vec3(0, 1, 0)

    @staticmethod
    def right() -> 'Vec3':
        return Vec3(1, 0, 0)


@dataclass
class Vec4:
    """4D vector (homogeneous coordinates)."""
    x: float
    y: float
    z: float
    w: float

    def to_vec3(self) -> Vec3:
        if self.w != 0:
            return Vec3(self.x / self.w, self.y / self.w, self.z / self.w)
        return Vec3(self.x, self.y, self.z)

    @staticmethod
    def from_vec3(v: Vec3, w: float = 1.0) -> 'Vec4':
        return Vec4(v.x, v.y, v.z, w)


class Mat4:
    """4x4 transformation matrix."""

    def __init__(self, data: Optional[List[List[float]]] = None):
        if data is None:
            self.data = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        else:
            self.data = data

    def __mul__(self, other: 'Mat4') -> 'Mat4':
        result = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        return Mat4(result)

    def transform(self, v: Vec3) -> Vec3:
        """Transform a Vec3 point."""
        x = self.data[0][0] * v.x + self.data[0][1] * v.y + self.data[0][2] * v.z + self.data[0][3]
        y = self.data[1][0] * v.x + self.data[1][1] * v.y + self.data[1][2] * v.z + self.data[1][3]
        z = self.data[2][0] * v.x + self.data[2][1] * v.y + self.data[2][2] * v.z + self.data[2][3]
        w = self.data[3][0] * v.x + self.data[3][1] * v.y + self.data[3][2] * v.z + self.data[3][3]
        if w != 0 and w != 1:
            return Vec3(x / w, y / w, z / w)
        return Vec3(x, y, z)

    def transform_direction(self, v: Vec3) -> Vec3:
        """Transform a direction vector (ignores translation)."""
        x = self.data[0][0] * v.x + self.data[0][1] * v.y + self.data[0][2] * v.z
        y = self.data[1][0] * v.x + self.data[1][1] * v.y + self.data[1][2] * v.z
        z = self.data[2][0] * v.x + self.data[2][1] * v.y + self.data[2][2] * v.z
        return Vec3(x, y, z)

    @staticmethod
    def identity() -> 'Mat4':
        return Mat4()

    @staticmethod
    def translation(x: float, y: float, z: float) -> 'Mat4':
        return Mat4([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def scale(x: float, y: float, z: float) -> 'Mat4':
        return Mat4([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotation_x(angle: float) -> 'Mat4':
        """Rotation around X axis (angle in radians)."""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotation_y(angle: float) -> 'Mat4':
        """Rotation around Y axis (angle in radians)."""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotation_z(angle: float) -> 'Mat4':
        """Rotation around Z axis (angle in radians)."""
        c, s = math.cos(angle), math.sin(angle)
        return Mat4([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def look_at(eye: Vec3, target: Vec3, up: Vec3 = None) -> 'Mat4':
        """Create a view matrix looking from eye to target."""
        if up is None:
            up = Vec3.up()

        forward = (target - eye).normalized()
        right = forward.cross(up).normalized()
        up = right.cross(forward).normalized()

        return Mat4([
            [right.x, right.y, right.z, -right.dot(eye)],
            [up.x, up.y, up.z, -up.dot(eye)],
            [-forward.x, -forward.y, -forward.z, forward.dot(eye)],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def perspective(fov: float, aspect: float, near: float, far: float) -> 'Mat4':
        """Create a perspective projection matrix."""
        f = 1.0 / math.tan(fov / 2)
        return Mat4([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])

    @staticmethod
    def orthographic(left: float, right: float, bottom: float, top: float,
                     near: float, far: float) -> 'Mat4':
        """Create an orthographic projection matrix."""
        return Mat4([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def isometric() -> 'Mat4':
        """Create an isometric projection matrix."""
        # Standard isometric: rotate 45° around Y, then ~35.264° around X
        angle_y = math.radians(45)
        angle_x = math.radians(35.264)
        return Mat4.rotation_x(angle_x) * Mat4.rotation_z(angle_y)


@dataclass
class Triangle:
    """A 3D triangle with vertices and normal."""
    v0: Vec3
    v1: Vec3
    v2: Vec3
    color: Tuple[int, int, int] = (200, 200, 200)
    normal: Optional[Vec3] = None

    def __post_init__(self):
        if self.normal is None:
            self.normal = self.compute_normal()

    def compute_normal(self) -> Vec3:
        """Compute face normal."""
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        return edge1.cross(edge2).normalized()

    def center(self) -> Vec3:
        """Get triangle centroid."""
        return (self.v0 + self.v1 + self.v2) / 3

    def transform(self, mat: Mat4) -> 'Triangle':
        """Transform triangle by matrix."""
        return Triangle(
            mat.transform(self.v0),
            mat.transform(self.v1),
            mat.transform(self.v2),
            self.color,
            mat.transform_direction(self.normal).normalized() if self.normal else None
        )


@dataclass
class Quad:
    """A 3D quad (two triangles)."""
    v0: Vec3  # Bottom-left
    v1: Vec3  # Bottom-right
    v2: Vec3  # Top-right
    v3: Vec3  # Top-left
    color: Tuple[int, int, int] = (200, 200, 200)

    def to_triangles(self) -> List[Triangle]:
        """Convert quad to two triangles."""
        return [
            Triangle(self.v0, self.v1, self.v2, self.color),
            Triangle(self.v0, self.v2, self.v3, self.color)
        ]

    def normal(self) -> Vec3:
        """Compute face normal."""
        edge1 = self.v1 - self.v0
        edge2 = self.v3 - self.v0
        return edge1.cross(edge2).normalized()


@dataclass
class Box:
    """A 3D axis-aligned box."""
    min_point: Vec3
    max_point: Vec3
    color: Tuple[int, int, int] = (200, 200, 200)
    top_color: Optional[Tuple[int, int, int]] = None

    @property
    def center(self) -> Vec3:
        return (self.min_point + self.max_point) / 2

    @property
    def size(self) -> Vec3:
        return self.max_point - self.min_point

    def to_quads(self) -> List[Quad]:
        """Convert box to 6 quads (faces)."""
        mn = self.min_point
        mx = self.max_point
        top = self.top_color or self.color

        # Define 8 vertices
        v = [
            Vec3(mn.x, mn.y, mn.z),  # 0: front-bottom-left
            Vec3(mx.x, mn.y, mn.z),  # 1: front-bottom-right
            Vec3(mx.x, mx.y, mn.z),  # 2: back-bottom-right
            Vec3(mn.x, mx.y, mn.z),  # 3: back-bottom-left
            Vec3(mn.x, mn.y, mx.z),  # 4: front-top-left
            Vec3(mx.x, mn.y, mx.z),  # 5: front-top-right
            Vec3(mx.x, mx.y, mx.z),  # 6: back-top-right
            Vec3(mn.x, mx.y, mx.z),  # 7: back-top-left
        ]

        # 6 faces (outward-facing normals)
        return [
            Quad(v[0], v[1], v[5], v[4], self.color),  # Front
            Quad(v[2], v[3], v[7], v[6], self.color),  # Back
            Quad(v[3], v[0], v[4], v[7], self.color),  # Left
            Quad(v[1], v[2], v[6], v[5], self.color),  # Right
            Quad(v[4], v[5], v[6], v[7], top),         # Top
            Quad(v[3], v[2], v[1], v[0], self.color),  # Bottom
        ]

    def to_triangles(self) -> List[Triangle]:
        """Convert box to triangles."""
        triangles = []
        for quad in self.to_quads():
            triangles.extend(quad.to_triangles())
        return triangles


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def shade_color(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Shade a color by a factor (0=black, 1=original, >1=lighter)."""
    return tuple(int(clamp(c * factor, 0, 255)) for c in color)


def blend_colors(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Blend two colors."""
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
