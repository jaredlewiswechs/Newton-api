#!/usr/bin/env python3
"""
parcRI HQ Design
================

A constraint-first headquarters design.
Campus-style layout with central commons.

Levels:
- L0 (Basement): Work areas, support, parking
- L1 (Ground): Grand Entry, Reception, Commons, Forge
- L2 (Upper): Visible Work, Labs, Studios, Strategy

Design Philosophy:
- The Floor: Where quiet work happens
- Civic Life: Where community gathers
- Visible Work: Where creation is seen
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cad.core import (
    Building, Level, Space, Zone, SpaceType, Rect, space, level, building
)
from cad.renderer import (
    CADRenderer, RenderConfig, RenderStyle, export_png, export_all_levels
)


def create_parcri_hq() -> Building:
    """
    Create the parcRI HQ building design.

    Based on:
    - Campus-style layout with central green
    - Modern office with maker spaces
    - Community-focused amenities
    """

    # Create the building
    hq = Building(
        name="parcRI HQ",
        address="Innovation District",
        architect="Construct Studio",
        client="parcRI"
    )

    # =========================================================================
    # LEVEL 0 - BASEMENT
    # The foundation. Support systems and focused work.
    # =========================================================================

    l0 = Level(
        name="L0 - Basement",
        elevation=-4.0,
        height=4.0,
        bounds=Rect(0, 0, 80, 60),
        is_basement=True
    )

    # Work Areas (The Floor - Quiet Work)
    l0.add_space(Space(
        name="Deep Work East",
        space_type=SpaceType.OFFICE,
        bounds=Rect(0, 0, 25, 25),
        label="Deep Work\nEast"
    ))

    l0.add_space(Space(
        name="Deep Work West",
        space_type=SpaceType.OFFICE,
        bounds=Rect(0, 25, 25, 25),
        label="Deep Work\nWest"
    ))

    l0.add_space(Space(
        name="Server Room",
        space_type=SpaceType.SERVER,
        bounds=Rect(0, 50, 15, 10),
        label="Server\nRoom"
    ))

    # Central Utilities
    l0.add_space(Space(
        name="Mechanical",
        space_type=SpaceType.MECHANICAL,
        bounds=Rect(25, 0, 15, 20),
        label="Mechanical"
    ))

    l0.add_space(Space(
        name="Storage",
        space_type=SpaceType.STORAGE,
        bounds=Rect(25, 20, 15, 20),
        label="Storage"
    ))

    l0.add_space(Space(
        name="Basement Corridor",
        space_type=SpaceType.CORRIDOR,
        bounds=Rect(25, 40, 30, 8),
        label=""
    ))

    # Workshop / Maker Space
    l0.add_space(Space(
        name="Workshop",
        space_type=SpaceType.WORKSHOP,
        bounds=Rect(40, 0, 25, 30),
        label="Workshop"
    ))

    l0.add_space(Space(
        name="Material Storage",
        space_type=SpaceType.STORAGE,
        bounds=Rect(40, 30, 15, 10),
        label="Materials"
    ))

    # Circulation
    l0.add_space(Space(
        name="Stair B0",
        space_type=SpaceType.STAIR,
        bounds=Rect(55, 40, 8, 8),
        label="Stair"
    ))

    l0.add_space(Space(
        name="Elevator B0",
        space_type=SpaceType.ELEVATOR,
        bounds=Rect(63, 40, 5, 8),
        label="Elev"
    ))

    # East Wing Support
    l0.add_space(Space(
        name="Utility",
        space_type=SpaceType.UTILITY,
        bounds=Rect(65, 0, 15, 20),
        label="Utility"
    ))

    l0.add_space(Space(
        name="Archive",
        space_type=SpaceType.STORAGE,
        bounds=Rect(65, 20, 15, 20),
        label="Archive"
    ))

    l0.add_space(Space(
        name="Restrooms B0",
        space_type=SpaceType.RESTROOM,
        bounds=Rect(68, 40, 12, 10),
        label="WC"
    ))

    l0.add_space(Space(
        name="Break Room",
        space_type=SpaceType.LOUNGE,
        bounds=Rect(15, 50, 25, 10),
        label="Break Room"
    ))

    hq.add_level(l0)

    # =========================================================================
    # LEVEL 1 - GROUND FLOOR
    # Civic Life. Entry, commons, forge.
    # =========================================================================

    l1 = Level(
        name="L1 - Ground",
        elevation=0.0,
        height=5.0,  # Taller ground floor
        bounds=Rect(0, 0, 80, 60)
    )

    # GRAND ENTRY (South)
    l1.add_space(Space(
        name="Grand Entry",
        space_type=SpaceType.GRAND_ENTRY,
        bounds=Rect(25, 48, 30, 12),
        label="GRAND ENTRY"
    ))

    l1.add_space(Space(
        name="Vestibule",
        space_type=SpaceType.VESTIBULE,
        bounds=Rect(32, 42, 16, 6),
        label="Vestibule"
    ))

    # RECEPTION & LOUNGE (Central South)
    l1.add_space(Space(
        name="Reception",
        space_type=SpaceType.RECEPTION,
        bounds=Rect(25, 30, 15, 12),
        label="Reception"
    ))

    l1.add_space(Space(
        name="Main Lounge",
        space_type=SpaceType.LOUNGE,
        bounds=Rect(40, 30, 15, 12),
        label="Lounge"
    ))

    # COMMONS (Central)
    l1.add_space(Space(
        name="Commons",
        space_type=SpaceType.COMMONS,
        bounds=Rect(20, 10, 40, 20),
        label="COMMONS",
        color_override="#7CB342"
    ))

    # THE FORGE (West Wing)
    l1.add_space(Space(
        name="Forge",
        space_type=SpaceType.FORGE,
        bounds=Rect(0, 0, 20, 30),
        label="THE FORGE\n(Maker Space)"
    ))

    l1.add_space(Space(
        name="Forge Storage",
        space_type=SpaceType.STORAGE,
        bounds=Rect(0, 30, 10, 12),
        label="Storage"
    ))

    l1.add_space(Space(
        name="Tool Room",
        space_type=SpaceType.UTILITY,
        bounds=Rect(10, 30, 10, 12),
        label="Tools"
    ))

    # CAFE & DINING (East Wing)
    l1.add_space(Space(
        name="Cafe",
        space_type=SpaceType.CAFE,
        bounds=Rect(60, 20, 20, 15),
        label="CAFE"
    ))

    l1.add_space(Space(
        name="Kitchen",
        space_type=SpaceType.KITCHEN,
        bounds=Rect(60, 35, 12, 10),
        label="Kitchen"
    ))

    l1.add_space(Space(
        name="Dining",
        space_type=SpaceType.DINING,
        bounds=Rect(60, 0, 20, 20),
        label="Dining"
    ))

    # GYM (Northeast)
    l1.add_space(Space(
        name="Gym",
        space_type=SpaceType.GYM,
        bounds=Rect(72, 35, 8, 15),
        label="Gym"
    ))

    # Circulation
    l1.add_space(Space(
        name="Main Corridor",
        space_type=SpaceType.CORRIDOR,
        bounds=Rect(20, 42, 5, 6),
        label=""
    ))

    l1.add_space(Space(
        name="East Corridor",
        space_type=SpaceType.CORRIDOR,
        bounds=Rect(55, 30, 5, 12),
        label=""
    ))

    l1.add_space(Space(
        name="Stair 1",
        space_type=SpaceType.STAIR,
        bounds=Rect(0, 42, 8, 8),
        label="Stair"
    ))

    l1.add_space(Space(
        name="Stair 2",
        space_type=SpaceType.STAIR,
        bounds=Rect(72, 50, 8, 8),
        label="Stair"
    ))

    l1.add_space(Space(
        name="Elevator 1",
        space_type=SpaceType.ELEVATOR,
        bounds=Rect(8, 42, 5, 8),
        label="Elev"
    ))

    l1.add_space(Space(
        name="Restrooms L1",
        space_type=SpaceType.RESTROOM,
        bounds=Rect(0, 50, 12, 10),
        label="WC"
    ))

    # Pocket Park entry indicator
    l1.add_space(Space(
        name="To Pocket Park",
        space_type=SpaceType.GARDEN,
        bounds=Rect(13, 42, 7, 8),
        label="To Park"
    ))

    hq.add_level(l1)

    # =========================================================================
    # LEVEL 2 - UPPER FLOOR
    # Visible Work. Labs, studios, strategy.
    # =========================================================================

    l2 = Level(
        name="L2 - Upper",
        elevation=5.0,
        height=4.0,
        bounds=Rect(0, 0, 80, 60)
    )

    # VISIBLE WORK - WEST WING (Labs & Media)
    l2.add_space(Space(
        name="Lab A",
        space_type=SpaceType.LAB,
        bounds=Rect(0, 0, 18, 20),
        label="LAB A\n(Research)"
    ))

    l2.add_space(Space(
        name="Lab B",
        space_type=SpaceType.LAB,
        bounds=Rect(0, 20, 18, 15),
        label="LAB B\n(Prototype)"
    ))

    l2.add_space(Space(
        name="Media Studio",
        space_type=SpaceType.STUDIO,
        bounds=Rect(0, 35, 18, 15),
        label="Media\nStudio"
    ))

    # CENTRAL - Open Office & Collaboration
    l2.add_space(Space(
        name="Open Office",
        space_type=SpaceType.OPEN_OFFICE,
        bounds=Rect(18, 0, 27, 25),
        label="OPEN OFFICE",
        color_override="#5BA3EC"
    ))

    l2.add_space(Space(
        name="Collaboration Hub",
        space_type=SpaceType.COMMONS,
        bounds=Rect(18, 25, 27, 15),
        label="Collaboration\nHub"
    ))

    # MEETING ROOMS
    l2.add_space(Space(
        name="Conference A",
        space_type=SpaceType.CONFERENCE,
        bounds=Rect(18, 40, 12, 10),
        label="Conf A"
    ))

    l2.add_space(Space(
        name="Conference B",
        space_type=SpaceType.CONFERENCE,
        bounds=Rect(30, 40, 12, 10),
        label="Conf B"
    ))

    l2.add_space(Space(
        name="Meeting 1",
        space_type=SpaceType.MEETING,
        bounds=Rect(18, 50, 8, 8),
        label="Mtg 1"
    ))

    l2.add_space(Space(
        name="Meeting 2",
        space_type=SpaceType.MEETING,
        bounds=Rect(26, 50, 8, 8),
        label="Mtg 2"
    ))

    l2.add_space(Space(
        name="Meeting 3",
        space_type=SpaceType.MEETING,
        bounds=Rect(34, 50, 8, 8),
        label="Mtg 3"
    ))

    # THE FLOOR - EAST WING (Strategy & Law)
    l2.add_space(Space(
        name="Strategy Room",
        space_type=SpaceType.BOARDROOM,
        bounds=Rect(45, 0, 20, 18),
        label="STRATEGY\nROOM"
    ))

    l2.add_space(Space(
        name="Executive Office",
        space_type=SpaceType.OFFICE,
        bounds=Rect(45, 18, 15, 12),
        label="Executive\nOffice"
    ))

    l2.add_space(Space(
        name="Legal",
        space_type=SpaceType.OFFICE,
        bounds=Rect(60, 18, 10, 12),
        label="Legal"
    ))

    l2.add_space(Space(
        name="Finance",
        space_type=SpaceType.OFFICE,
        bounds=Rect(70, 18, 10, 12),
        label="Finance"
    ))

    # QUIET WORK - Far East
    l2.add_space(Space(
        name="Focus Room A",
        space_type=SpaceType.OFFICE,
        bounds=Rect(65, 0, 15, 9),
        label="Focus A"
    ))

    l2.add_space(Space(
        name="Focus Room B",
        space_type=SpaceType.OFFICE,
        bounds=Rect(65, 9, 15, 9),
        label="Focus B"
    ))

    # Library
    l2.add_space(Space(
        name="Library",
        space_type=SpaceType.LIBRARY,
        bounds=Rect(45, 30, 20, 12),
        label="LIBRARY"
    ))

    # Amenities
    l2.add_space(Space(
        name="Wellness Room",
        space_type=SpaceType.WELLNESS,
        bounds=Rect(65, 30, 15, 12),
        label="Wellness"
    ))

    l2.add_space(Space(
        name="Restrooms L2",
        space_type=SpaceType.RESTROOM,
        bounds=Rect(65, 42, 15, 8),
        label="WC"
    ))

    # Circulation
    l2.add_space(Space(
        name="Upper Corridor",
        space_type=SpaceType.CORRIDOR,
        bounds=Rect(42, 40, 23, 10),
        label=""
    ))

    l2.add_space(Space(
        name="Stair L2",
        space_type=SpaceType.STAIR,
        bounds=Rect(0, 50, 8, 8),
        label="Stair"
    ))

    l2.add_space(Space(
        name="Elevator L2",
        space_type=SpaceType.ELEVATOR,
        bounds=Rect(8, 50, 5, 8),
        label="Elev"
    ))

    # Terrace
    l2.add_space(Space(
        name="Terrace",
        space_type=SpaceType.TERRACE,
        bounds=Rect(65, 50, 15, 10),
        label="TERRACE",
        color_override="#A5D6A7"
    ))

    hq.add_level(l2)

    # =========================================================================
    # SITE - POCKET PARK & GROUNDS
    # =========================================================================

    # Add site spaces (these appear on a site plan)
    hq.site_spaces.append(Space(
        name="Pocket Park",
        space_type=SpaceType.POCKET_PARK,
        bounds=Rect(-20, 20, 20, 30),
        label="POCKET\nPARK"
    ))

    hq.site_spaces.append(Space(
        name="Entry Plaza",
        space_type=SpaceType.COURTYARD,
        bounds=Rect(20, 60, 40, 15),
        label="Entry Plaza"
    ))

    hq.site_spaces.append(Space(
        name="Service Court",
        space_type=SpaceType.COURTYARD,
        bounds=Rect(80, 20, 15, 30),
        label="Service"
    ))

    return hq


def generate_exports():
    """Generate all PNG exports for parcRI HQ."""

    # Create the design
    print("Creating parcRI HQ design...")
    hq = create_parcri_hq()

    # Print summary
    print(hq.summary())

    # Configure renderer
    config = RenderConfig(
        scale=18.0,  # pixels per meter
        style=RenderStyle.SCHEMATIC,
        show_grid=True,
        show_labels=True,
        show_areas=True,
        show_compass=True,
        show_scale_bar=True,
        show_title=True,
        padding=100,
        title_size=28,
        label_size=13,
        area_size=10,
    )

    # Export directory
    export_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "exports"
    )
    os.makedirs(export_dir, exist_ok=True)

    # Export all levels
    print(f"\nExporting to: {export_dir}")
    paths = export_all_levels(hq, export_dir, config)

    for path in paths:
        print(f"  Saved: {path}")

    # Also save building data as JSON
    json_path = os.path.join(export_dir, "parcri_hq.json")
    with open(json_path, "w") as f:
        f.write(hq.to_json())
    print(f"  Saved: {json_path}")

    print("\nDone!")
    return paths


if __name__ == "__main__":
    generate_exports()
