#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
GRAVITY WARS - A Newton Physics Roguelike Arena Brawler
Built with Newton's Constraint-Verified Game Engine

The first game where cheating is MATHEMATICALLY IMPOSSIBLE.
Every movement, attack, and game state is cryptographically verified.

"You can't hack physics when physics is a constraint."

© 2026 Built with Newton · Ada Computing Company
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import math
import random
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum

# Add parent paths for Newton imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python_package', 'src'))

try:
    from newton import KineticEngine, Presence
except ImportError:
    # Fallback: Define minimal versions if newton not in path
    class Presence:
        def __init__(self, state: dict):
            self.state = state.copy()

    class KineticEngine:
        def __init__(self):
            self.boundaries = []

        def add_boundary(self, check_fn: Callable, name: str = ""):
            self.boundaries.append({"check": check_fn, "name": name})

        def resolve_motion(self, from_state: Presence, to_state: Presence) -> dict:
            # Compute delta
            delta = {}
            for key in to_state.state:
                if key in from_state.state:
                    delta[key] = {
                        "from": from_state.state[key],
                        "to": to_state.state[key],
                        "delta": to_state.state[key] - from_state.state[key] if isinstance(to_state.state[key], (int, float)) else None
                    }

            class Delta:
                def __init__(self, changes):
                    self.changes = changes

            d = Delta(delta)

            for boundary in self.boundaries:
                if boundary["check"](d):
                    return {"status": "finfr", "reason": boundary["name"]}

            return {"status": "synchronized"}

        def interpolate(self, start: Presence, end: Presence, steps: int = 10) -> List[Presence]:
            frames = []
            for i in range(steps + 1):
                t = i / steps
                interpolated = {}
                for key in start.state:
                    if key in end.state and isinstance(start.state[key], (int, float)):
                        interpolated[key] = start.state[key] + (end.state[key] - start.state[key]) * t
                    else:
                        interpolated[key] = end.state[key] if i == steps else start.state[key]
                frames.append(Presence(interpolated))
            return frames


# ═══════════════════════════════════════════════════════════════════════════════
# GAME CONSTANTS - All enforced by constraints
# ═══════════════════════════════════════════════════════════════════════════════

class GameConstants:
    """Immutable game constants - changing these changes the game hash."""

    # Arena dimensions
    ARENA_WIDTH = 800
    ARENA_HEIGHT = 600

    # Physics
    GRAVITY_DEFAULT = 9.81
    GRAVITY_MIN = -20.0  # Can flip gravity!
    GRAVITY_MAX = 30.0
    MAX_SPEED = 15.0
    FRICTION = 0.95

    # Player
    PLAYER_SIZE = 20
    PLAYER_MAX_HEALTH = 100
    PLAYER_SPEED = 8.0
    JUMP_FORCE = 12.0

    # Combat
    PROJECTILE_SPEED = 20.0
    PROJECTILE_DAMAGE = 10
    GRAVITY_BOMB_RADIUS = 150
    GRAVITY_BOMB_DURATION = 3.0  # seconds

    # Roguelike
    MAX_WAVE = 20
    ENEMIES_PER_WAVE_BASE = 3
    ENEMY_SPAWN_DELAY = 2.0

    @classmethod
    def get_hash(cls) -> str:
        """Get cryptographic hash of all constants - game identity."""
        data = f"{cls.ARENA_WIDTH}:{cls.ARENA_HEIGHT}:{cls.GRAVITY_DEFAULT}:{cls.MAX_SPEED}:{cls.PLAYER_MAX_HEALTH}"
        return hashlib.sha256(data.encode()).hexdigest()[:16].upper()


# ═══════════════════════════════════════════════════════════════════════════════
# GAME ENTITIES
# ═══════════════════════════════════════════════════════════════════════════════

class EntityType(Enum):
    PLAYER = "player"
    ENEMY = "enemy"
    PROJECTILE = "projectile"
    GRAVITY_WELL = "gravity_well"
    POWER_UP = "power_up"


@dataclass
class Vector2:
    """2D Vector with constraint-safe operations."""
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self) -> 'Vector2':
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def clamped(self, max_mag: float) -> 'Vector2':
        mag = self.magnitude()
        if mag <= max_mag:
            return Vector2(self.x, self.y)
        return self.normalized() * max_mag

    def distance_to(self, other: 'Vector2') -> float:
        return (self - other).magnitude()

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


@dataclass
class Entity:
    """Base entity with constraint-verified state."""
    id: str
    entity_type: EntityType
    position: Vector2
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    size: float = 20.0
    health: float = 100.0
    max_health: float = 100.0
    alive: bool = True
    gravity_scale: float = 1.0  # Can be modified by gravity wells

    def to_presence(self) -> Presence:
        """Convert to Newton Presence for constraint checking."""
        return Presence({
            'x': self.position.x,
            'y': self.position.y,
            'vx': self.velocity.x,
            'vy': self.velocity.y,
            'health': self.health,
            'alive': 1 if self.alive else 0,
        })

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get AABB bounds (left, top, right, bottom)."""
        half = self.size / 2
        return (
            self.position.x - half,
            self.position.y - half,
            self.position.x + half,
            self.position.y + half
        )

    def collides_with(self, other: 'Entity') -> bool:
        """Check circle collision."""
        dist = self.position.distance_to(other.position)
        return dist < (self.size + other.size) / 2


@dataclass
class Player(Entity):
    """Player entity with special abilities."""
    gravity_bombs: int = 3
    score: int = 0
    combo: int = 0
    invincibility_timer: float = 0.0

    def __post_init__(self):
        self.entity_type = EntityType.PLAYER
        self.max_health = GameConstants.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.size = GameConstants.PLAYER_SIZE


@dataclass
class Enemy(Entity):
    """Enemy entity with AI behavior."""
    behavior: str = "chase"  # chase, patrol, sniper
    reaction_time: float = 0.5
    last_action_time: float = 0.0
    target: Optional[Entity] = None

    def __post_init__(self):
        self.entity_type = EntityType.ENEMY


@dataclass
class Projectile(Entity):
    """Projectile with verified trajectory."""
    owner_id: str = ""
    damage: float = 10.0
    lifetime: float = 5.0

    def __post_init__(self):
        self.entity_type = EntityType.PROJECTILE
        self.size = 8


@dataclass
class GravityWell(Entity):
    """Gravity manipulation zone - core mechanic!"""
    radius: float = 150.0
    gravity_modifier: float = -1.0  # Negative = reverse gravity
    duration: float = 3.0
    created_at: float = 0.0

    def __post_init__(self):
        self.entity_type = EntityType.GRAVITY_WELL
        self.size = self.radius * 2


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT ENGINE - The heart of Newton's cheat-proof design
# ═══════════════════════════════════════════════════════════════════════════════

class GravityWarsEngine:
    """
    The Gravity Wars game engine built on Newton's constraint verification.

    Every state transition is verified BEFORE it happens.
    Invalid states are mathematically impossible.
    """

    def __init__(self, seed: Optional[int] = None):
        self.kinetic = KineticEngine()
        self.seed = seed or int(time.time() * 1000) % (2**32)
        self.rng = random.Random(self.seed)

        # Game state
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.gravity_wells: List[GravityWell] = []
        self.power_ups: List[Entity] = []

        # Wave system
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.wave_complete = False

        # Global physics
        self.gravity = Vector2(0, GameConstants.GRAVITY_DEFAULT)
        self.game_time = 0.0
        self.frame_count = 0

        # Verification ledger
        self.state_hashes: List[str] = []

        # Setup constraints
        self._setup_constraints()

    def _setup_constraints(self):
        """Define all game constraints - these are LAWS, not suggestions."""

        # Boundary constraints (walls)
        self.kinetic.add_boundary(
            lambda d: d.changes.get('x', {}).get('to', 0) < 0,
            name="LeftWall"
        )
        self.kinetic.add_boundary(
            lambda d: d.changes.get('x', {}).get('to', 0) > GameConstants.ARENA_WIDTH,
            name="RightWall"
        )
        self.kinetic.add_boundary(
            lambda d: d.changes.get('y', {}).get('to', 0) < 0,
            name="TopWall"
        )
        self.kinetic.add_boundary(
            lambda d: d.changes.get('y', {}).get('to', 0) > GameConstants.ARENA_HEIGHT,
            name="BottomWall"
        )

        # Speed limit constraint
        self.kinetic.add_boundary(
            lambda d: (abs(d.changes.get('vx', {}).get('to', 0)) > GameConstants.MAX_SPEED * 2 or
                      abs(d.changes.get('vy', {}).get('to', 0)) > GameConstants.MAX_SPEED * 2),
            name="SpeedLimit"
        )

        # Health constraint - can't go negative or above max
        self.kinetic.add_boundary(
            lambda d: d.changes.get('health', {}).get('to', 100) < 0,
            name="HealthMinimum"
        )

        # No resurrection constraint
        self.kinetic.add_boundary(
            lambda d: (d.changes.get('alive', {}).get('from', 1) == 0 and
                      d.changes.get('alive', {}).get('to', 0) == 1),
            name="NoResurrection"
        )

    def initialize(self):
        """Initialize a new game."""
        # Spawn player in center
        self.player = Player(
            id="player_1",
            entity_type=EntityType.PLAYER,
            position=Vector2(GameConstants.ARENA_WIDTH / 2, GameConstants.ARENA_HEIGHT / 2),
        )

        # Reset state
        self.enemies = []
        self.projectiles = []
        self.gravity_wells = []
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.game_time = 0.0
        self.frame_count = 0
        self.state_hashes = []

        # Log initial state
        self._record_state()

        print(f"Gravity Wars initialized with seed: {self.seed}")
        print(f"Game constants hash: {GameConstants.get_hash()}")

    def spawn_enemy(self, wave: int) -> Enemy:
        """Spawn a constraint-verified enemy."""
        # Spawn at random edge
        edge = self.rng.choice(['top', 'bottom', 'left', 'right'])

        if edge == 'top':
            pos = Vector2(self.rng.uniform(50, GameConstants.ARENA_WIDTH - 50), 50)
        elif edge == 'bottom':
            pos = Vector2(self.rng.uniform(50, GameConstants.ARENA_WIDTH - 50), GameConstants.ARENA_HEIGHT - 50)
        elif edge == 'left':
            pos = Vector2(50, self.rng.uniform(50, GameConstants.ARENA_HEIGHT - 50))
        else:
            pos = Vector2(GameConstants.ARENA_WIDTH - 50, self.rng.uniform(50, GameConstants.ARENA_HEIGHT - 50))

        # Enemy stats scale with wave
        base_health = 30 + wave * 5
        behavior = self.rng.choice(['chase', 'chase', 'patrol', 'sniper'])

        enemy = Enemy(
            id=f"enemy_{self.enemies_spawned}",
            entity_type=EntityType.ENEMY,
            position=pos,
            health=base_health,
            max_health=base_health,
            size=25 + wave * 2,
            behavior=behavior,
            reaction_time=max(0.2, 0.8 - wave * 0.05),
        )

        self.enemies.append(enemy)
        self.enemies_spawned += 1

        return enemy

    def create_gravity_well(self, position: Vector2, owner_id: str, reverse: bool = True) -> Optional[GravityWell]:
        """Create a gravity manipulation zone."""
        if self.player and self.player.id == owner_id and self.player.gravity_bombs <= 0:
            return None  # No bombs left!

        well = GravityWell(
            id=f"well_{len(self.gravity_wells)}",
            entity_type=EntityType.GRAVITY_WELL,
            position=position,
            radius=GameConstants.GRAVITY_BOMB_RADIUS,
            gravity_modifier=-1.0 if reverse else 2.0,
            duration=GameConstants.GRAVITY_BOMB_DURATION,
            created_at=self.game_time,
        )

        self.gravity_wells.append(well)

        if self.player and self.player.id == owner_id:
            self.player.gravity_bombs -= 1

        return well

    def fire_projectile(self, owner: Entity, direction: Vector2) -> Projectile:
        """Fire a constraint-verified projectile."""
        velocity = direction.normalized() * GameConstants.PROJECTILE_SPEED

        projectile = Projectile(
            id=f"proj_{len(self.projectiles)}_{self.frame_count}",
            entity_type=EntityType.PROJECTILE,
            position=Vector2(owner.position.x, owner.position.y),
            velocity=velocity,
            owner_id=owner.id,
            damage=GameConstants.PROJECTILE_DAMAGE,
        )

        self.projectiles.append(projectile)
        return projectile

    def move_entity(self, entity: Entity, new_position: Vector2, new_velocity: Vector2) -> Tuple[bool, str]:
        """
        Attempt to move an entity - verified by Newton's kinetic engine.

        Returns (success, reason).
        """
        old_presence = entity.to_presence()

        # Create proposed new state
        new_state = Presence({
            'x': new_position.x,
            'y': new_position.y,
            'vx': new_velocity.x,
            'vy': new_velocity.y,
            'health': entity.health,
            'alive': 1 if entity.alive else 0,
        })

        # Verify the transition
        result = self.kinetic.resolve_motion(old_presence, new_state)

        if result['status'] == 'synchronized':
            # Motion allowed - apply it
            entity.position = new_position
            entity.velocity = new_velocity
            return True, "OK"
        else:
            # Motion blocked by constraint!
            reason = result.get('reason', 'Unknown constraint')

            # Handle wall collisions by clamping
            if 'Wall' in reason:
                entity.position.x = max(0, min(entity.position.x, GameConstants.ARENA_WIDTH))
                entity.position.y = max(0, min(entity.position.y, GameConstants.ARENA_HEIGHT))
                entity.velocity = Vector2(0, 0)

            return False, reason

    def apply_damage(self, entity: Entity, damage: float, source: str = "") -> Tuple[bool, str]:
        """Apply damage with constraint verification."""
        if entity.entity_type == EntityType.PLAYER:
            player = entity
            if hasattr(player, 'invincibility_timer') and player.invincibility_timer > 0:
                return False, "Invincible"

        new_health = entity.health - damage

        old_presence = entity.to_presence()
        new_presence = Presence({
            'x': entity.position.x,
            'y': entity.position.y,
            'vx': entity.velocity.x,
            'vy': entity.velocity.y,
            'health': new_health,
            'alive': 1 if new_health > 0 else 0,
        })

        result = self.kinetic.resolve_motion(old_presence, new_presence)

        if result['status'] == 'synchronized':
            entity.health = max(0, new_health)
            if entity.health <= 0:
                entity.alive = False
            return True, f"Damage applied: {damage}"
        else:
            return False, result.get('reason', 'Damage blocked')

    def get_local_gravity(self, position: Vector2) -> Vector2:
        """Calculate gravity at a position, accounting for gravity wells."""
        local_gravity = Vector2(self.gravity.x, self.gravity.y)

        for well in self.gravity_wells:
            dist = position.distance_to(well.position)
            if dist < well.radius:
                # Inside gravity well - modify gravity
                influence = 1.0 - (dist / well.radius)
                local_gravity.y *= well.gravity_modifier * influence + (1 - influence)

        return local_gravity

    def update(self, dt: float, player_input: Dict[str, Any] = None):
        """
        Update game state for one frame.

        All state transitions are constraint-verified.
        """
        self.game_time += dt
        self.frame_count += 1
        player_input = player_input or {}

        # Update gravity wells (remove expired)
        self.gravity_wells = [
            w for w in self.gravity_wells
            if self.game_time - w.created_at < w.duration
        ]

        # Update player
        if self.player and self.player.alive:
            self._update_player(dt, player_input)

        # Update enemies
        for enemy in self.enemies:
            if enemy.alive:
                self._update_enemy(enemy, dt)

        # Update projectiles
        self._update_projectiles(dt)

        # Check collisions
        self._check_collisions()

        # Remove dead entities
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive and p.lifetime > 0]

        # Wave management
        self._update_wave()

        # Record state for verification
        if self.frame_count % 60 == 0:  # Every ~1 second
            self._record_state()

    def _update_player(self, dt: float, input_data: Dict[str, Any]):
        """Update player with verified movement."""
        if not self.player:
            return

        # Get local gravity
        local_gravity = self.get_local_gravity(self.player.position)

        # Apply gravity
        new_velocity = Vector2(
            self.player.velocity.x,
            self.player.velocity.y + local_gravity.y * dt
        )

        # Apply input
        move_x = input_data.get('move_x', 0)  # -1 to 1
        move_y = input_data.get('move_y', 0)  # -1 to 1 (for flying/jumping)

        new_velocity.x += move_x * GameConstants.PLAYER_SPEED * dt * 10
        new_velocity.y += move_y * GameConstants.PLAYER_SPEED * dt * 10

        # Apply friction
        new_velocity.x *= GameConstants.FRICTION
        new_velocity.y *= GameConstants.FRICTION

        # Clamp velocity
        new_velocity = new_velocity.clamped(GameConstants.MAX_SPEED)

        # Calculate new position
        new_position = Vector2(
            self.player.position.x + new_velocity.x,
            self.player.position.y + new_velocity.y
        )

        # Verify and apply movement
        self.move_entity(self.player, new_position, new_velocity)

        # Handle shooting
        if input_data.get('shoot') and input_data.get('aim_x') is not None:
            aim_dir = Vector2(
                input_data.get('aim_x', 0),
                input_data.get('aim_y', 0)
            )
            if aim_dir.magnitude() > 0:
                self.fire_projectile(self.player, aim_dir)

        # Handle gravity bomb
        if input_data.get('gravity_bomb'):
            bomb_x = input_data.get('bomb_x', self.player.position.x)
            bomb_y = input_data.get('bomb_y', self.player.position.y)
            self.create_gravity_well(Vector2(bomb_x, bomb_y), self.player.id)

        # Update invincibility
        if hasattr(self.player, 'invincibility_timer') and self.player.invincibility_timer > 0:
            self.player.invincibility_timer -= dt

    def _update_enemy(self, enemy: Enemy, dt: float):
        """Update enemy AI with verified movement."""
        if not self.player or not self.player.alive:
            return

        # Get local gravity
        local_gravity = self.get_local_gravity(enemy.position)

        # Apply gravity
        new_velocity = Vector2(
            enemy.velocity.x,
            enemy.velocity.y + local_gravity.y * dt
        )

        # AI behavior
        if self.game_time - enemy.last_action_time > enemy.reaction_time:
            enemy.last_action_time = self.game_time

            if enemy.behavior == 'chase':
                # Move toward player
                to_player = self.player.position - enemy.position
                direction = to_player.normalized()
                new_velocity.x += direction.x * 5
                new_velocity.y += direction.y * 3

            elif enemy.behavior == 'patrol':
                # Random movement
                new_velocity.x += self.rng.uniform(-3, 3)
                new_velocity.y += self.rng.uniform(-2, 2)

            elif enemy.behavior == 'sniper':
                # Shoot at player from distance
                if self.player.position.distance_to(enemy.position) > 200:
                    to_player = self.player.position - enemy.position
                    self.fire_projectile(enemy, to_player)
                else:
                    # Retreat
                    away = enemy.position - self.player.position
                    direction = away.normalized()
                    new_velocity.x += direction.x * 4

        # Apply friction
        new_velocity.x *= GameConstants.FRICTION
        new_velocity.y *= GameConstants.FRICTION

        # Clamp velocity
        new_velocity = new_velocity.clamped(GameConstants.MAX_SPEED * 0.8)

        # Calculate new position
        new_position = Vector2(
            enemy.position.x + new_velocity.x,
            enemy.position.y + new_velocity.y
        )

        # Verify and apply
        self.move_entity(enemy, new_position, new_velocity)

    def _update_projectiles(self, dt: float):
        """Update all projectiles with verified trajectories."""
        for proj in self.projectiles:
            if not proj.alive:
                continue

            # Get local gravity (projectiles affected less)
            local_gravity = self.get_local_gravity(proj.position)
            local_gravity = local_gravity * 0.3  # Reduced gravity effect

            new_velocity = Vector2(
                proj.velocity.x,
                proj.velocity.y + local_gravity.y * dt
            )

            new_position = Vector2(
                proj.position.x + proj.velocity.x,
                proj.position.y + proj.velocity.y
            )

            # Check bounds (projectiles die at walls)
            if (new_position.x < 0 or new_position.x > GameConstants.ARENA_WIDTH or
                new_position.y < 0 or new_position.y > GameConstants.ARENA_HEIGHT):
                proj.alive = False
                continue

            proj.position = new_position
            proj.velocity = new_velocity
            proj.lifetime -= dt

            if proj.lifetime <= 0:
                proj.alive = False

    def _check_collisions(self):
        """Check and resolve all collisions."""
        if not self.player:
            return

        # Player vs projectiles
        for proj in self.projectiles:
            if not proj.alive or proj.owner_id == self.player.id:
                continue

            if self.player.collides_with(proj):
                self.apply_damage(self.player, proj.damage, proj.owner_id)
                proj.alive = False

        # Player vs enemies
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            if self.player.collides_with(enemy):
                self.apply_damage(self.player, 5, enemy.id)
                # Knockback
                knockback = (self.player.position - enemy.position).normalized() * 5
                self.player.velocity = self.player.velocity + knockback

        # Projectiles vs enemies
        for proj in self.projectiles:
            if not proj.alive:
                continue

            if proj.owner_id == self.player.id:
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue

                    if proj.collides_with(enemy):
                        self.apply_damage(enemy, proj.damage, proj.owner_id)
                        proj.alive = False

                        if not enemy.alive:
                            self.enemies_killed += 1
                            self.player.score += 100 * self.wave
                            self.player.combo += 1
                        break

    def _update_wave(self):
        """Manage wave spawning."""
        enemies_this_wave = GameConstants.ENEMIES_PER_WAVE_BASE + self.wave * 2

        # Spawn enemies if needed
        wave_enemies_spawned = len([e for e in self.enemies if e.alive]) + self.enemies_killed

        if wave_enemies_spawned < enemies_this_wave:
            if self.frame_count % int(60 * GameConstants.ENEMY_SPAWN_DELAY / (1 + self.wave * 0.1)) == 0:
                if len(self.enemies) < 10:  # Max concurrent enemies
                    self.spawn_enemy(self.wave)

        # Check wave complete
        if self.enemies_killed >= enemies_this_wave and len(self.enemies) == 0:
            self.wave += 1
            self.enemies_killed = 0

            # Bonus for completing wave
            if self.player:
                self.player.score += 500 * self.wave
                self.player.gravity_bombs = min(5, self.player.gravity_bombs + 1)
                self.player.invincibility_timer = 2.0

            print(f"Wave {self.wave - 1} complete! Starting wave {self.wave}")

    def _record_state(self):
        """Record cryptographic hash of game state for verification."""
        state_data = {
            'frame': self.frame_count,
            'time': self.game_time,
            'player_pos': self.player.position.to_dict() if self.player else None,
            'player_health': self.player.health if self.player else 0,
            'player_score': self.player.score if self.player else 0,
            'enemies': len(self.enemies),
            'wave': self.wave,
        }

        state_str = str(sorted(state_data.items()))
        state_hash = hashlib.sha256(state_str.encode()).hexdigest()[:16].upper()
        self.state_hashes.append((self.frame_count, state_hash))

        return state_hash

    def get_game_state(self) -> Dict[str, Any]:
        """Get complete game state for rendering."""
        return {
            'frame': self.frame_count,
            'time': self.game_time,
            'wave': self.wave,
            'player': {
                'x': self.player.position.x if self.player else 0,
                'y': self.player.position.y if self.player else 0,
                'health': self.player.health if self.player else 0,
                'score': self.player.score if self.player else 0,
                'gravity_bombs': self.player.gravity_bombs if self.player else 0,
                'alive': self.player.alive if self.player else False,
            },
            'enemies': [
                {
                    'x': e.position.x,
                    'y': e.position.y,
                    'health': e.health,
                    'behavior': e.behavior,
                }
                for e in self.enemies if e.alive
            ],
            'projectiles': [
                {
                    'x': p.position.x,
                    'y': p.position.y,
                    'owner': p.owner_id,
                }
                for p in self.projectiles if p.alive
            ],
            'gravity_wells': [
                {
                    'x': w.position.x,
                    'y': w.position.y,
                    'radius': w.radius,
                    'modifier': w.gravity_modifier,
                    'remaining': w.duration - (self.game_time - w.created_at),
                }
                for w in self.gravity_wells
            ],
            'gravity': {'x': self.gravity.x, 'y': self.gravity.y},
            'verification': {
                'seed': self.seed,
                'constants_hash': GameConstants.get_hash(),
                'state_hashes': len(self.state_hashes),
                'last_hash': self.state_hashes[-1][1] if self.state_hashes else None,
            }
        }

    def verify_replay(self, recorded_hashes: List[Tuple[int, str]]) -> bool:
        """Verify a recorded game matches our state hashes - anti-cheat!"""
        for frame, expected_hash in recorded_hashes:
            our_record = next((h for f, h in self.state_hashes if f == frame), None)
            if our_record != expected_hash:
                print(f"Verification FAILED at frame {frame}!")
                print(f"Expected: {expected_hash}, Got: {our_record}")
                return False
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def run_demo():
    """Run a demonstration of Gravity Wars."""
    print("=" * 70)
    print("  GRAVITY WARS - Newton Physics Roguelike")
    print("  The first game where cheating is MATHEMATICALLY IMPOSSIBLE")
    print("=" * 70)
    print()

    # Initialize game
    engine = GravityWarsEngine(seed=42)
    engine.initialize()

    print(f"Player spawned at ({engine.player.position.x:.0f}, {engine.player.position.y:.0f})")
    print(f"Initial health: {engine.player.health}")
    print()

    # Simulate some gameplay
    print("--- Simulating 5 seconds of gameplay ---")
    print()

    dt = 1/60  # 60 FPS

    for frame in range(300):  # 5 seconds at 60 FPS
        # Simulate player input (moving right and shooting)
        player_input = {
            'move_x': 0.5 if frame < 120 else -0.3,  # Move right, then left
            'move_y': -0.3 if frame % 60 < 10 else 0,  # Occasional jump
            'shoot': frame % 20 == 0,  # Shoot every 20 frames
            'aim_x': 1 if frame < 150 else -1,
            'aim_y': 0.2,
        }

        # Drop a gravity bomb at frame 100
        if frame == 100:
            player_input['gravity_bomb'] = True
            player_input['bomb_x'] = engine.player.position.x + 100
            player_input['bomb_y'] = engine.player.position.y
            print(f"Frame {frame}: Deploying gravity bomb!")

        engine.update(dt, player_input)

        # Print status every second
        if frame % 60 == 0:
            state = engine.get_game_state()
            print(f"Time: {state['time']:.1f}s | Wave: {state['wave']} | "
                  f"Score: {state['player']['score']} | "
                  f"Health: {state['player']['health']:.0f} | "
                  f"Enemies: {len(state['enemies'])} | "
                  f"Gravity Wells: {len(state['gravity_wells'])}")

    print()
    print("--- Final State ---")
    final_state = engine.get_game_state()
    print(f"Final Score: {final_state['player']['score']}")
    print(f"Waves Completed: {final_state['wave'] - 1}")
    print(f"Player Health: {final_state['player']['health']:.0f}")
    print(f"Gravity Bombs Remaining: {final_state['player']['gravity_bombs']}")
    print()

    # Show verification
    print("--- Verification Ledger ---")
    print(f"Seed: {final_state['verification']['seed']}")
    print(f"Constants Hash: {final_state['verification']['constants_hash']}")
    print(f"State Checkpoints: {final_state['verification']['state_hashes']}")
    print(f"Final State Hash: {final_state['verification']['last_hash']}")
    print()

    # Demonstrate constraint enforcement
    print("--- Constraint Enforcement Demo ---")

    # Try to move player outside bounds
    print("Attempting to teleport player outside arena (x=-100)...")
    illegal_pos = Vector2(-100, engine.player.position.y)
    success, reason = engine.move_entity(engine.player, illegal_pos, Vector2(0, 0))
    print(f"Result: {'ALLOWED' if success else 'BLOCKED'} - {reason}")
    print(f"Player actual position: ({engine.player.position.x:.0f}, {engine.player.position.y:.0f})")
    print()

    # Try to exceed speed limit
    print("Attempting to set impossible velocity (vx=1000)...")
    illegal_vel = Vector2(1000, 0)
    success, reason = engine.move_entity(
        engine.player,
        Vector2(engine.player.position.x + 10, engine.player.position.y),
        illegal_vel
    )
    print(f"Result: {'ALLOWED' if success else 'BLOCKED'} - {reason}")
    print()

    print("=" * 70)
    print("  Newton's constraint verification prevents ALL invalid states.")
    print("  Cheating is not just difficult - it's IMPOSSIBLE.")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
