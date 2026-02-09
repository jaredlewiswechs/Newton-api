#!/usr/bin/env python3
"""
07_kinetic_game.py - Game Physics with Kinetic Engine

Use the Kinetic Engine for game physics with boundaries.
Demonstrates state transitions with movement constraints.
"""

from newton import KineticEngine, Presence


def main():
    print("=" * 60)
    print("  KINETIC GAME - Physics with Boundaries")
    print("=" * 60)
    print()

    # Create game engine with boundaries
    engine = KineticEngine()

    # Define game world boundaries (400x300 pixels)
    WORLD_WIDTH = 400
    WORLD_HEIGHT = 300

    # Add boundary: can't go past left edge
    engine.add_boundary(
        lambda d: d.changes.get('x', {}).get('to', 0) < 0,
        name="LeftWall"
    )

    # Add boundary: can't go past right edge
    engine.add_boundary(
        lambda d: d.changes.get('x', {}).get('to', 0) > WORLD_WIDTH,
        name="RightWall"
    )

    # Add boundary: can't go past top
    engine.add_boundary(
        lambda d: d.changes.get('y', {}).get('to', 0) < 0,
        name="TopWall"
    )

    # Add boundary: can't go past bottom
    engine.add_boundary(
        lambda d: d.changes.get('y', {}).get('to', 0) > WORLD_HEIGHT,
        name="BottomWall"
    )

    # Add boundary: max speed of 50 units per frame
    engine.add_boundary(
        lambda d: abs(d.changes.get('x', {}).get('delta', 0)) > 50 or
                  abs(d.changes.get('y', {}).get('delta', 0)) > 50,
        name="MaxSpeed"
    )

    print(f"Game world: {WORLD_WIDTH}x{WORLD_HEIGHT}")
    print(f"Boundaries: LeftWall, RightWall, TopWall, BottomWall, MaxSpeed")
    print()

    # Initial player position
    player = Presence({'x': 200, 'y': 150, 'health': 100})
    print(f"Player starts at: ({player.state['x']}, {player.state['y']})")
    print()

    # Test valid movements
    print("--- Valid Movements ---")

    # Move right
    new_pos = Presence({'x': 230, 'y': 150, 'health': 100})
    result = engine.resolve_motion(player, new_pos)
    print(f"Move to (230, 150): {result['status']}")
    if result['status'] == 'synchronized':
        player = new_pos

    # Move down
    new_pos = Presence({'x': 230, 'y': 200, 'health': 100})
    result = engine.resolve_motion(player, new_pos)
    print(f"Move to (230, 200): {result['status']}")
    if result['status'] == 'synchronized':
        player = new_pos

    print(f"Player now at: ({player.state['x']}, {player.state['y']})")
    print()

    # Test boundary collisions
    print("--- Boundary Collisions ---")

    # Try to go past right edge
    new_pos = Presence({'x': 450, 'y': 200, 'health': 100})  # Past 400
    result = engine.resolve_motion(player, new_pos)
    print(f"Try (450, 200): {result['status']} - {result.get('reason', 'OK')}")

    # Try to go past bottom
    new_pos = Presence({'x': 230, 'y': 350, 'health': 100})  # Past 300
    result = engine.resolve_motion(player, new_pos)
    print(f"Try (230, 350): {result['status']} - {result.get('reason', 'OK')}")

    # Try to move too fast
    new_pos = Presence({'x': 330, 'y': 200, 'health': 100})  # 100 units jump
    result = engine.resolve_motion(player, new_pos)
    print(f"Try jump 100 units: {result['status']} - {result.get('reason', 'OK')}")
    print()

    print(f"Player still at: ({player.state['x']}, {player.state['y']})")
    print()

    # Demonstrate interpolation for smooth movement
    print("--- Smooth Movement (Interpolation) ---")
    start = Presence({'x': 100, 'y': 100})
    end = Presence({'x': 200, 'y': 200})

    frames = engine.interpolate(start, end, steps=5)
    print(f"Moving from (100,100) to (200,200) in 5 steps:")
    for i, frame in enumerate(frames):
        print(f"  Frame {i}: ({frame.state['x']:.1f}, {frame.state['y']:.1f})")

    print()
    print("=" * 60)
    print("The Kinetic Engine enforces game physics boundaries.")
    print("Invalid movements are blocked before they happen.")
    print("=" * 60)


if __name__ == "__main__":
    main()
