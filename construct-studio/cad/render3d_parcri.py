#!/usr/bin/env python3
"""
parcRI HQ 3D Renderer - Newton CAD
==================================

Generates 3D architectural renderings of parcRI HQ with Newton f/g visualization.

The Floor of Newton:
- Ground plane (z=0) = Floor (g) - reality's constraint boundary
- Building volumes = Matter (f) - spatial intentions
- f/g ratio = constraint utilization, shown as color

Colors follow Newton's f/g Visual Language:
- GREEN (#00C853) - VERIFIED: f/g < 0.9θ, safe margin
- AMBER (#FFD600) - WARNING: 0.9θ ≤ f/g < θ, approaching boundary
- RED (#FF1744) - FORBIDDEN: f/g ≥ θ, constraint violated
- DEEP RED (#B71C1C) - UNDEFINED: g ≈ 0, ontological death (finfr)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple
import math

from cad.geometry3d import Vec3, hex_to_rgb, shade_color
from cad.renderer3d import (
    Renderer3D, Render3DConfig, ProjectionType, ViewAngle,
    create_building_mesh, create_ground_plane,
    FGState, FG_COLORS, get_fg_state, get_fg_color
)

# Import building definition
from cad.parcri_hq import create_parcri_hq


# =============================================================================
# Newton f/g Constraint Definitions for parcRI HQ
# =============================================================================

# Floor capacity constraints (g values) - what reality allows per level
LEVEL_CONSTRAINTS = {
    "L0 - Basement": {
        "floor_area": 4800.0,  # m² total buildable
        "capacity": 0.85,      # 85% max utilization allowed
    },
    "L1 - Ground": {
        "floor_area": 4800.0,
        "capacity": 0.80,      # Ground floor needs more circulation
    },
    "L2 - Upper": {
        "floor_area": 4800.0,
        "capacity": 0.90,      # Upper floor can be denser
    },
}

# Space type constraints - f/g thresholds per type
SPACE_CONSTRAINTS = {
    "office": 0.75,       # Offices should have margin
    "commons": 0.60,      # Commons need lots of flex space
    "forge": 0.70,        # Maker spaces need room
    "lab": 0.65,          # Labs need safety margins
    "corridor": 1.0,      # Corridors can be fully used
    "storage": 0.95,      # Storage can be dense
    "mechanical": 0.80,
    "server": 0.70,       # Servers need cooling space
}


def calculate_level_fg(level_name: str, used_area: float) -> Tuple[float, float, FGState]:
    """
    Calculate f/g ratio for a building level.

    Returns: (f, g, state)
    - f = used floor area (what we're attempting)
    - g = allowed floor area (what reality permits)
    - state = FGState based on ratio
    """
    constraints = LEVEL_CONSTRAINTS.get(level_name, {"floor_area": 4800.0, "capacity": 0.85})
    g = constraints["floor_area"] * constraints["capacity"]  # Available capacity
    f = used_area  # What we're using

    state = get_fg_state(f, g)
    return f, g, state


def building_to_3d_data(building, use_fg_colors: bool = False) -> List[Dict]:
    """
    Convert Building object to 3D render data.

    Args:
        building: The Building object
        use_fg_colors: If True, color spaces by f/g constraint state
                       If False, use original space type colors
    """
    levels_data = []

    for level in building.levels:
        # Calculate level's total used area for f/g ratio
        total_used = sum(s.bounds.width * s.bounds.height for s in level.spaces)
        f, g, level_state = calculate_level_fg(level.name, total_used)

        level_data = {
            'name': level.name,
            'elevation': level.elevation,
            'height': level.height,
            'spaces': [],
            # Newton f/g data
            'fg_f': f,
            'fg_g': g,
            'fg_ratio': f / g if g > 0 else float('inf'),
            'fg_state': level_state.value,
        }

        for space in level.spaces:
            space_area = space.bounds.width * space.bounds.height

            # Calculate space-level f/g (space area vs level capacity)
            space_type = space.space_type.value.lower()
            type_threshold = SPACE_CONSTRAINTS.get(space_type, 0.85)

            # f = space area, g = proportional share of level capacity
            space_g = (g * space_area / total_used) if total_used > 0 else space_area
            space_f = space_area * type_threshold  # Effective demand

            space_fg_state = get_fg_state(space_f, space_g)

            # Determine color
            if use_fg_colors:
                # Use Newton f/g colors
                color = FG_COLORS.get(space_fg_state, (176, 190, 197))
                color_hex = '#{:02x}{:02x}{:02x}'.format(*color)
            else:
                # Use original space type color
                color_hex = space.color

            space_data = {
                'name': space.name,
                'x': space.bounds.x,
                'y': space.bounds.y,
                'width': space.bounds.width,
                'height': space.bounds.height,
                'color': color_hex,
                'type': space.space_type.value,
                # Newton f/g data
                'fg_f': space_f,
                'fg_g': space_g,
                'fg_ratio': space_f / space_g if space_g > 0 else float('inf'),
                'fg_state': space_fg_state.value,
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
    title: str = None,
    use_fg_colors: bool = False
):
    """
    Render parcRI HQ in 3D with optional Newton f/g visualization.

    Args:
        view: Camera view angle
        show_single_level: If set, only show this level index
        title: Custom title
        use_fg_colors: If True, color by f/g constraint state (green/amber/red)
                       If False, use original architectural colors
    """
    # Get building data
    building = create_parcri_hq()
    all_levels_data = building_to_3d_data(building, use_fg_colors=use_fg_colors)

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
    """Generate all 3D renderings including Newton f/g constraint visualization."""

    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(export_dir, exist_ok=True)

    renders = []

    print("Generating 3D renders of parcRI HQ...")
    print()

    # ==========================================================================
    # Standard architectural renders (original colors)
    # ==========================================================================
    print("=== Standard Architectural Views ===")

    views = [
        (ViewAngle.ISOMETRIC_SW, "isometric_sw"),
        (ViewAngle.ISOMETRIC_SE, "isometric_se"),
        (ViewAngle.ISOMETRIC_NE, "isometric_ne"),
        (ViewAngle.ISOMETRIC_NW, "isometric_nw"),
        (ViewAngle.BIRD_EYE, "bird_eye"),
    ]

    for view, name in views:
        print(f"  Rendering: Full building - {name}...")
        img = render_parcri_3d(view=view, use_fg_colors=False)
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
            show_single_level=i,
            use_fg_colors=False
        )
        path = os.path.join(export_dir, f"parcri_hq_3d_{level_name}.png")
        img.save(path, "PNG")
        renders.append(path)
        print(f"    Saved: {path}")

    # ==========================================================================
    # Newton f/g constraint visualization (green/amber/red)
    # ==========================================================================
    print()
    print("=== Newton f/g Constraint Visualization ===")
    print("  Colors: GREEN=verified, AMBER=warning, RED=forbidden")

    # Full building with f/g colors
    print(f"  Rendering: Full building - Newton f/g view...")
    img = render_parcri_3d(
        view=ViewAngle.ISOMETRIC_SW,
        use_fg_colors=True,
        title="parcRI HQ - Newton f/g Constraint View"
    )
    path = os.path.join(export_dir, f"parcri_hq_3d_newton_fg.png")
    img.save(path, "PNG")
    renders.append(path)
    print(f"    Saved: {path}")

    # Bird's eye f/g view (shows all constraint states)
    print(f"  Rendering: Bird's eye - Newton f/g view...")
    img = render_parcri_3d(
        view=ViewAngle.BIRD_EYE,
        use_fg_colors=True,
        title="parcRI HQ - Floor of Newton (f/g Constraint Map)"
    )
    path = os.path.join(export_dir, f"parcri_hq_3d_newton_fg_bird.png")
    img.save(path, "PNG")
    renders.append(path)
    print(f"    Saved: {path}")

    # Individual levels with f/g colors
    for i, level_name in enumerate(level_names):
        print(f"  Rendering: {level_name} - Newton f/g view...")
        level_display = level_name.replace("_", " ").title()
        img = render_parcri_3d(
            view=ViewAngle.ISOMETRIC_SW,
            show_single_level=i,
            use_fg_colors=True,
            title=f"parcRI HQ - {level_display} - f/g Constraint State"
        )
        path = os.path.join(export_dir, f"parcri_hq_3d_{level_name}_newton_fg.png")
        img.save(path, "PNG")
        renders.append(path)
        print(f"    Saved: {path}")

    print()
    print(f"Generated {len(renders)} 3D renders.")
    print()
    print("Newton f/g Visual Language:")
    print("  GREEN  (#00C853) = VERIFIED  - f/g < 0.9θ (safe margin)")
    print("  AMBER  (#FFD600) = WARNING   - 0.9θ ≤ f/g < θ (approaching boundary)")
    print("  RED    (#FF1744) = FORBIDDEN - f/g ≥ θ (constraint violated)")
    print()

    return renders


if __name__ == "__main__":
    generate_all_3d_renders()
