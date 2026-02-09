# Gravity Wars

**Newton's First Constraint-Verified Physics Game**

```
    ╭──────────────────────────────────────────────────────────────╮
    │                                                              │
    │   🎮 GRAVITY WARS                                           │
    │                                                              │
    │   The first game where cheating is                          │
    │   MATHEMATICALLY IMPOSSIBLE.                                │
    │                                                              │
    │   "You can't hack physics when physics is a constraint."    │
    │                                                              │
    ╰──────────────────────────────────────────────────────────────╯
```

## What is Gravity Wars?

Gravity Wars is a roguelike arena brawler built on Newton's constraint verification system. Every movement, attack, and game state is cryptographically verified before execution.

**This isn't anti-cheat. This is cheat-proof architecture.**

## Play Now

- **Web**: Open `index.html` in any browser
- **Python**: `python gravity_wars.py`

## How It Works

### Newton Constraint Verification

Every frame, the game engine verifies:

| Constraint | What It Prevents |
|------------|-----------------|
| **Speed Limit** | velocity ≤ MAX_SPEED (15.0) |
| **Arena Bounds** | 0 ≤ x ≤ 800, 0 ≤ y ≤ 600 |
| **Health Bounds** | 0 ≤ health ≤ max_health |
| **Gravity Bounds** | -20.0 ≤ gravity ≤ 30.0 |

If any constraint would be violated → **finfr** (operation blocked).

### Gravity Manipulation

The core mechanic: deploy **Gravity Bombs** to create localized gravity wells that:
- Reverse gravity for enemies
- Pull/push projectiles
- Create tactical zones

```
GRAVITY WELL (radius=150, duration=3s)
       ╭─────────╮
      ╱    ↑↑↑    ╲
     │   ↑ ● ↑    │   ← Reverse gravity zone
      ╲   ↑↑↑    ╱
       ╰─────────╯
```

## Game Constants (Immutable)

```python
GameConstants:
    ARENA_WIDTH = 800
    ARENA_HEIGHT = 600
    GRAVITY_DEFAULT = 9.81
    MAX_SPEED = 15.0
    PLAYER_MAX_HEALTH = 100
    GRAVITY_BOMB_RADIUS = 150
    MAX_WAVE = 20
```

These constants are hashed. Changing them changes the game's identity.

## Controls

| Key | Action |
|-----|--------|
| **WASD** / **Arrows** | Move |
| **Space** | Jump |
| **Click** | Shoot |
| **Q** | Deploy Gravity Bomb |
| **R** | Restart (when dead) |

## Architecture

```
┌─────────────────────────────────────────┐
│           GRAVITY WARS ENGINE           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Player    │    │   Enemies   │    │
│  │  (Entity)   │    │  (Entity[]) │    │
│  └──────┬──────┘    └──────┬──────┘    │
│         │                   │           │
│         └─────────┬─────────┘           │
│                   ↓                     │
│         ┌─────────────────┐             │
│         │  KineticEngine  │             │
│         │  (constraints)  │             │
│         └────────┬────────┘             │
│                  ↓                      │
│         ┌─────────────────┐             │
│         │  Verify Before  │             │
│         │    Execute      │             │
│         └────────┬────────┘             │
│                  ↓                      │
│         ✓ synchronized OR ✗ finfr       │
│                                         │
└─────────────────────────────────────────┘
```

## Entity Types

| Entity | Purpose |
|--------|---------|
| **Player** | You. Has gravity bombs, health, score. |
| **Enemy** | Chases, patrols, or snipes. AI-controlled. |
| **Projectile** | Bullets. Affected by gravity wells. |
| **GravityWell** | Temporary zone with modified gravity. |
| **PowerUp** | Health, bombs, score multipliers. |

## Why This Matters

Traditional games: Trust the client, detect cheating after the fact.

**Newton games**: Invalid states cannot exist. The constraint IS the game rule.

```python
# Traditional game
if player.speed > MAX_SPEED:
    player.speed = MAX_SPEED  # Fix after violation

# Newton game
result = kinetic.resolve_motion(old_state, new_state)
if result["status"] == "finfr":
    pass  # Violation never happened
```

## Files

| File | Description |
|------|-------------|
| `index.html` | Web version (self-contained) |
| `gravity_wars.py` | Python implementation with Newton SDK |

## Built With Newton

This game demonstrates Newton's `KineticEngine`:
- **Presence**: Immutable state snapshots
- **Boundaries**: Constraint definitions
- **resolve_motion()**: Verify transitions before execution
- **interpolate()**: Smooth animation within constraints

---

© 2026 Built with Newton · Ada Computing Company

*"You can't hack physics when physics is a constraint."*
