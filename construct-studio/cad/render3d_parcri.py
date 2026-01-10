#!/usr/bin/env python3
"""
parcRI HQ 3D Renderer
====================

Generates 3D architectural renderings of parcRI HQ from multiple angles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple
import math

from cad.geometry3d import Vec3, hex_to_rgb, shade_color
from cad.renderer3d import (
    Renderer3D, Render3DConfig, ProjectionType, ViewAngle,
    create_building_mesh, create_ground_plane
)

# Import building definition
from cad.parcri_hq import create_parcri_hq


def building_to_3d_data(building) -> List[Dict]:
    """Convert Building object to 3D render data."""
    levels_data = []

    for level in building.levels:
        level_data = {
            'name': level.name,
            'elevation': level.elevation,
            'height': level.height,
            'spaces': []
        }

        for space in level.spaces:
            space_data = {
                'name': space.name,
                'x': space.bounds.x,
                'y': space.bounds.y,
                'width': space.bounds.width,
                'height': space.bounds.height,
                'color': space.color,
                'type': space.space_type.value
            }
            level_data['spaces'].append(space_data)

        levels_data.append(level_data)

    return levels_data


def create_detailed_building_mesh(levels_data: List[Dict], z_offset: float = 0) -> List:
    """Create detailed 3D mesh from level data."""
    return create_detailed_building_mesh_with_offset(levels_data, z_offset)


def create_detailed_building_mesh_with_offset(levels_data: List[Dict], z_offset: float = 0) -> List:
    """Create detailed 3D mesh from level data with optional z offset.

    Args:
        levels_data: Level definitions with spaces
        z_offset: Vertical offset to apply (e.g., to lift basement to grade)
    """
    from cad.geometry3d import Triangle, Box

    all_triangles = []

    for level in levels_data:
        elevation = level.get('elevation', 0) + z_offset  # Apply offset
        height = level.get('height', 4)

        for space in level.get('spaces', []):
            x, y = space['x'], space['y']
            w, h = space['width'], space['height']
            color_hex = space.get('color', '#CCCCCC')
            color = hex_to_rgb(color_hex)

            # Main volume
            tris = create_building_mesh(
                x, y, elevation,
                w, h, height,
                color,
                shade_color(color, 1.15)  # Lighter roof
            )
            all_triangles.extend(tris)

    return all_triangles


def render_parcri_3d(
    view: ViewAngle = ViewAngle.ISOMETRIC_SW,
    show_single_level: int = None,
    title: str = None
):
    """
    Render parcRI HQ in 3D.

    Args:
        view: Camera view angle
        show_single_level: If set, only show this level index
        title: Custom title
    """
    # Get building data
    building = create_parcri_hq()
    all_levels_data = building_to_3d_data(building)

    # Determine if we're showing a basement level
    is_basement_view = False
    if show_single_level is not None:
        level_to_show = all_levels_data[show_single_level]
        is_basement_view = level_to_show.get('elevation', 0) < 0
        levels_data = [level_to_show]
    else:
        levels_data = all_levels_data

    # Create config
    config = Render3DConfig(
        width=1920,
        height=1080,
        projection=ProjectionType.ISOMETRIC,
        scale=10.0,
        ambient=0.4,
        diffuse=0.6,
        show_edges=True,
        edge_width=1,
        show_ground=True,
        ground_color=(185, 200, 170),
        show_sky=True,
        sky_top=(140, 180, 220),
        sky_bottom=(230, 240, 250),
        show_shadows=True,
        shadow_opacity=0.2,
        show_title=True,
    )

    # Create renderer
    renderer = Renderer3D(config)

    # Calculate bounds first (need for ground plane positioning)
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    min_z = float('inf')
    max_z = float('-inf')

    for level in levels_data:
        elevation = level.get('elevation', 0)
        height = level.get('height', 4)
        for space in level.get('spaces', []):
            min_x = min(min_x, space['x'])
            min_y = min(min_y, space['y'])
            max_x = max(max_x, space['x'] + space['width'])
            max_y = max(max_y, space['y'] + space['height'])
            min_z = min(min_z, elevation)
            max_z = max(max_z, elevation + height)

    # For basement views, shift geometry up so it sits ON the ground
    # (architectural section cut showing basement at grade)
    z_offset = 0
    if is_basement_view and min_z < 0:
        z_offset = -min_z  # Shift up so bottom is at z=0

    # Create mesh with z_offset applied
    triangles = create_detailed_building_mesh_with_offset(levels_data, z_offset)

    # Add ground plane at z=0 (after offset, geometry sits on it)
    ground_size = max(max_x - min_x, max_y - min_y) * 2
    ground_tris = create_ground_plane(
        ground_size,
        config.ground_color,
        Vec3((max_x + min_x) / 2, (max_y + min_y) / 2, 0)
    )
    triangles.extend(ground_tris)

    # Adjust bounds for camera after offset
    min_z += z_offset
    max_z += z_offset

    # Set camera - center on the geometry
    center = Vec3(
        (max_x + min_x) / 2,
        (max_y + min_y) / 2,
        (max_z + min_z) / 2  # Proper center accounting for actual z range
    )
    distance = max(max_x - min_x, max_y - min_y) * 2

    renderer.set_camera_from_view(view, center, distance)

    # Generate title
    if title is None:
        if show_single_level is not None:
            title = f"parcRI HQ - {levels_data[0]['name']} - 3D View"
        else:
            title = f"parcRI HQ - Full Building - 3D View ({view.value})"

    return renderer.render_triangles(triangles, title)


def generate_all_3d_renders():
    """Generate all 3D renderings."""

    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(export_dir, exist_ok=True)

    renders = []

    print("Generating 3D renders of parcRI HQ...")
    print()

    # Full building - multiple angles
    views = [
        (ViewAngle.ISOMETRIC_SW, "isometric_sw"),
        (ViewAngle.ISOMETRIC_SE, "isometric_se"),
        (ViewAngle.ISOMETRIC_NE, "isometric_ne"),
        (ViewAngle.ISOMETRIC_NW, "isometric_nw"),
        (ViewAngle.BIRD_EYE, "bird_eye"),
    ]

    for view, name in views:
        print(f"  Rendering: Full building - {name}...")
        img = render_parcri_3d(view=view)
        path = os.path.join(export_dir, f"parcri_hq_3d_{name}.png")
        img.save(path, "PNG")
        renders.append(path)
        print(f"    Saved: {path}")

    # Individual levels
    level_names = ["l0_basement", "l1_ground", "l2_upper"]
    for i, level_name in enumerate(level_names):
        print(f"  Rendering: {level_name} - 3D...")
        img = render_parcri_3d(
            view=ViewAngle.ISOMETRIC_SW,
            show_single_level=i
        )
        path = os.path.join(export_dir, f"parcri_hq_3d_{level_name}.png")
        img.save(path, "PNG")
        renders.append(path)
        print(f"    Saved: {path}")

    print()
    print(f"Generated {len(renders)} 3D renders.")
    print()

    return renders


if __name__ == "__main__":
    generate_all_3d_renders()
