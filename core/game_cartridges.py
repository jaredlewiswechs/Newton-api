"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON GAME CARTRIDGES
Complete Game Engine Subsystems through Verified Specification

Every game system as a constraint-verified cartridge.
The specification IS the game engine.

Cartridge Types:
- Physics: Rigid body, collision, vehicle dynamics
- AI: NPC behavior, pathfinding, decision trees
- Input: Controllers, gestures, touch, keyboard
- Network: Multiplayer, state sync, matchmaking
- Economy: Currency, progression, rewards, trading
- Narrative: Dialogue, branching stories, quests
- World: Procedural generation, terrain, levels
- Particle: Effects, explosions, weather, ambient
- Haptic: Vibration, force feedback, tactile
- Save: State persistence, checkpoints, cloud sync
- Locale: Translation, cultural adaptation, accessibility

"The constraint IS the physics. The specification IS the world."

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum
import re
import hashlib
import time
import math

# Import base cartridge infrastructure
from .cartridges import (
    CartridgeType, CartridgeResult, ConstraintResult,
    ConstraintChecker, SAFETY_PATTERNS
)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME CARTRIDGE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class GameCartridgeType(Enum):
    """Types of game-specific cartridges."""
    PHYSICS = "physics"
    AI = "ai"
    INPUT = "input"
    NETWORK = "network"
    ECONOMY = "economy"
    NARRATIVE = "narrative"
    WORLD = "world"
    PARTICLE = "particle"
    HAPTIC = "haptic"
    SAVE = "save"
    LOCALE = "locale"


class GameOutputFormat(Enum):
    """Output formats for game cartridges."""
    # Physics
    PHYSICS_SPEC = "physics_spec"
    COLLISION_SPEC = "collision_spec"
    VEHICLE_SPEC = "vehicle_spec"

    # AI
    BEHAVIOR_TREE = "behavior_tree"
    STATE_MACHINE = "state_machine"
    PATHFINDING_SPEC = "pathfinding_spec"

    # Input
    INPUT_MAP = "input_map"
    GESTURE_SPEC = "gesture_spec"

    # Network
    NETCODE_SPEC = "netcode_spec"
    LOBBY_SPEC = "lobby_spec"

    # Economy
    ECONOMY_SPEC = "economy_spec"
    PROGRESSION_SPEC = "progression_spec"

    # Narrative
    DIALOGUE_TREE = "dialogue_tree"
    QUEST_SPEC = "quest_spec"

    # World
    TERRAIN_SPEC = "terrain_spec"
    LEVEL_SPEC = "level_spec"

    # Particle
    PARTICLE_SPEC = "particle_spec"
    WEATHER_SPEC = "weather_spec"

    # Haptic
    HAPTIC_SPEC = "haptic_spec"

    # Save
    SAVE_SPEC = "save_spec"

    # Locale
    LOCALE_SPEC = "locale_spec"


# ═══════════════════════════════════════════════════════════════════════════════
# GAME CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

PHYSICS_CONSTRAINTS = {
    "gravity": {"min": 0, "max": 100},  # m/s²
    "friction": {"min": 0.0, "max": 1.0},
    "restitution": {"min": 0.0, "max": 1.0},  # bounciness
    "mass": {"min": 0.001, "max": 1000000},  # kg
    "max_velocity": {"cap": 1000},  # m/s
    "time_step": {"min": 0.001, "max": 0.1},  # seconds
    "substeps": {"min": 1, "max": 16},
    "patterns": []
}

AI_CONSTRAINTS = {
    "reaction_time_ms": {"min": 16, "max": 5000},
    "awareness_radius": {"min": 0.1, "max": 1000},
    "memory_duration_s": {"min": 0, "max": 3600},
    "max_behavior_depth": {"max": 20},
    "max_states": {"max": 100},
    "patterns": []
}

INPUT_CONSTRAINTS = {
    "polling_rate_hz": {"min": 30, "max": 1000},
    "deadzone": {"min": 0.0, "max": 0.5},
    "sensitivity": {"min": 0.1, "max": 10.0},
    "max_simultaneous_touches": {"max": 10},
    "gesture_timeout_ms": {"max": 2000},
    "patterns": []
}

NETWORK_CONSTRAINTS = {
    "tick_rate": {"min": 10, "max": 128},
    "max_players": {"min": 1, "max": 1000},
    "max_latency_ms": {"max": 500},
    "packet_size_bytes": {"max": 1400},  # MTU safe
    "interpolation_delay_ms": {"min": 0, "max": 200},
    "patterns": [
        r"\b(ddos|denial of service|flood)\b",
        r"\b(exploit|cheat|hack)\b.*\b(server|game)\b",
    ]
}

ECONOMY_CONSTRAINTS = {
    "max_currency_types": {"max": 20},
    "max_items": {"max": 10000},
    "inflation_rate": {"min": 0, "max": 1.0},
    "exchange_rate_bounds": {"min": 0.001, "max": 1000},
    "patterns": [
        r"\b(real money|cash out|gambling)\b",
        r"\b(exploit|dupe|duplicate)\b.*\b(currency|item|gold)\b",
    ]
}

NARRATIVE_CONSTRAINTS = {
    "max_dialogue_nodes": {"max": 10000},
    "max_choices_per_node": {"max": 10},
    "max_quest_depth": {"max": 50},
    "max_concurrent_quests": {"max": 100},
    "patterns": []
}

WORLD_CONSTRAINTS = {
    "max_world_size": {"max": 1000000},  # units
    "chunk_size": {"min": 8, "max": 256},
    "lod_levels": {"min": 1, "max": 10},
    "max_entities_per_chunk": {"max": 1000},
    "seed_range": {"min": 0, "max": 2**32 - 1},
    "patterns": []
}

PARTICLE_CONSTRAINTS = {
    "max_particles": {"max": 100000},
    "max_emitters": {"max": 1000},
    "lifetime_ms": {"min": 1, "max": 60000},
    "spawn_rate": {"min": 0, "max": 10000},  # per second
    "patterns": [
        r"\b(seizure|epilepsy)\b.*\b(inducing|triggering)\b",
        r"\b(strobing|flashing)\b.*\b(rapid|fast)\b",
    ]
}

HAPTIC_CONSTRAINTS = {
    "intensity": {"min": 0.0, "max": 1.0},
    "duration_ms": {"min": 1, "max": 5000},
    "frequency_hz": {"min": 1, "max": 500},
    "patterns": []
}

SAVE_CONSTRAINTS = {
    "max_save_size_mb": {"max": 100},
    "max_save_slots": {"max": 100},
    "autosave_interval_s": {"min": 10, "max": 3600},
    "compression_level": {"min": 0, "max": 9},
    "patterns": [
        r"\b(corrupt|destroy|delete)\b.*\b(save|data|progress)\b",
    ]
}

LOCALE_CONSTRAINTS = {
    "max_languages": {"max": 50},
    "max_string_length": {"max": 10000},
    "supported_encodings": ["utf-8", "utf-16", "ascii"],
    "patterns": []
}


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class PhysicsCartridge:
    """
    Physics Cartridge: Verified Physics Simulation Specifications

    Generates constraint-verified physics parameters for:
    - Rigid body dynamics (mass, inertia, forces)
    - Collision detection and response
    - Vehicle physics (wheels, suspension, engine)
    - Character controllers (ground detection, slopes)
    - Projectile ballistics (trajectory, penetration)
    - Fluid dynamics (buoyancy, drag)
    - Soft body physics (cloth, rope, deformables)

    "The constraint IS the physics law."
    """

    BODY_PATTERNS = {
        "rigid": r"\b(rigid|solid|hard|box|sphere|capsule|cube)\b",
        "soft": r"\b(soft|deformable|cloth|rope|spring|jelly)\b",
        "vehicle": r"\b(car|truck|motorcycle|vehicle|wheel|tank|boat)\b",
        "character": r"\b(character|player|npc|humanoid|biped|walker)\b",
        "projectile": r"\b(bullet|projectile|missile|arrow|thrown|grenade)\b",
        "fluid": r"\b(water|fluid|liquid|ocean|river|pool)\b",
        "ragdoll": r"\b(ragdoll|death|limp|physics body)\b",
    }

    COLLISION_PATTERNS = {
        "discrete": r"\b(discrete|standard|normal)\b",
        "continuous": r"\b(continuous|ccd|fast|bullet)\b",
        "trigger": r"\b(trigger|sensor|overlap|detect)\b",
    }

    MATERIAL_PRESETS = {
        "metal": {"friction": 0.4, "restitution": 0.3, "density": 7800},
        "wood": {"friction": 0.5, "restitution": 0.2, "density": 600},
        "rubber": {"friction": 0.9, "restitution": 0.8, "density": 1100},
        "ice": {"friction": 0.05, "restitution": 0.1, "density": 920},
        "concrete": {"friction": 0.6, "restitution": 0.1, "density": 2400},
        "flesh": {"friction": 0.7, "restitution": 0.1, "density": 1000},
        "glass": {"friction": 0.4, "restitution": 0.5, "density": 2500},
    }

    def compile(
        self,
        intent: str,
        gravity: float = 9.81,
        time_step: float = 0.016,  # 60 Hz
        substeps: int = 4,
        world_bounds: Optional[Tuple[float, float, float]] = None
    ) -> CartridgeResult:
        """Compile physics intent into simulation specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp parameters
        gravity = max(
            PHYSICS_CONSTRAINTS["gravity"]["min"],
            min(gravity, PHYSICS_CONSTRAINTS["gravity"]["max"])
        )
        time_step = max(
            PHYSICS_CONSTRAINTS["time_step"]["min"],
            min(time_step, PHYSICS_CONSTRAINTS["time_step"]["max"])
        )
        substeps = max(
            PHYSICS_CONSTRAINTS["substeps"]["min"],
            min(substeps, PHYSICS_CONSTRAINTS["substeps"]["max"])
        )

        # Safety check
        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            body_type = self._parse_body_type(intent)
            collision_type = self._parse_collision_type(intent)
            materials = self._infer_materials(intent)

            spec = {
                "type": "physics",
                "format": GameOutputFormat.PHYSICS_SPEC.value,
                "simulation": {
                    "gravity": {"x": 0, "y": -gravity, "z": 0},
                    "time_step": time_step,
                    "substeps": substeps,
                    "solver_iterations": 8,
                    "velocity_iterations": 3,
                },
                "body_type": body_type,
                "collision": {
                    "type": collision_type,
                    "layers": self._infer_layers(body_type),
                    "masks": self._infer_masks(body_type),
                },
                "materials": materials,
                "constraints": self._generate_physics_constraints(intent, body_type),
                "world_bounds": world_bounds or (10000, 10000, 10000),
                "optimizations": {
                    "sleep_threshold": 0.1,
                    "broad_phase": "dynamic_bvh",
                    "narrow_phase": "gjk_epa",
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

            # Add vehicle-specific physics if detected
            if body_type == "vehicle":
                spec["vehicle"] = self._generate_vehicle_spec(intent)

            # Add character-specific physics if detected
            if body_type == "character":
                spec["character"] = self._generate_character_spec(intent)

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,  # Using DATA as base
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "bounds": {
                    "gravity": gravity,
                    "time_step": time_step,
                    "substeps": substeps
                }
            },
            fingerprint=hashlib.sha256(f"{intent}{gravity}{time_step}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_body_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for body_type, pattern in self.BODY_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return body_type
        return "rigid"

    def _parse_collision_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for col_type, pattern in self.COLLISION_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return col_type
        return "discrete"

    def _infer_materials(self, intent: str) -> List[Dict[str, Any]]:
        intent_lower = intent.lower()
        materials = []
        for material, props in self.MATERIAL_PRESETS.items():
            if material in intent_lower:
                materials.append({"name": material, **props})
        return materials if materials else [{"name": "default", "friction": 0.5, "restitution": 0.3, "density": 1000}]

    def _infer_layers(self, body_type: str) -> int:
        layers = {
            "rigid": 1,
            "vehicle": 2,
            "character": 4,
            "projectile": 8,
            "soft": 16,
            "fluid": 32,
            "ragdoll": 64,
        }
        return layers.get(body_type, 1)

    def _infer_masks(self, body_type: str) -> int:
        # What this body type collides with
        masks = {
            "rigid": 0b1111111,      # collides with everything
            "vehicle": 0b1111101,    # not with other vehicles (layer 2)
            "character": 0b1110111,  # not with other characters
            "projectile": 0b1110111, # not with other projectiles
            "soft": 0b0111111,
            "fluid": 0b1011111,
            "ragdoll": 0b1111111,
        }
        return masks.get(body_type, 0b1111111)

    def _generate_physics_constraints(self, intent: str, body_type: str) -> List[Dict[str, Any]]:
        constraints = []
        intent_lower = intent.lower()

        if "joint" in intent_lower or "hinge" in intent_lower:
            constraints.append({
                "type": "hinge",
                "axis": [0, 1, 0],
                "limits": {"min": -180, "max": 180}
            })
        if "spring" in intent_lower:
            constraints.append({
                "type": "spring",
                "stiffness": 1000,
                "damping": 10
            })
        if "distance" in intent_lower or "rope" in intent_lower:
            constraints.append({
                "type": "distance",
                "min_distance": 0,
                "max_distance": 10
            })
        if body_type == "character":
            constraints.append({
                "type": "ground_constraint",
                "max_slope_angle": 45,
                "step_height": 0.5
            })

        return constraints

    def _generate_vehicle_spec(self, intent: str) -> Dict[str, Any]:
        intent_lower = intent.lower()

        # Detect vehicle type
        if "motorcycle" in intent_lower or "bike" in intent_lower:
            wheels = 2
            wheel_base = 1.5
        elif "truck" in intent_lower:
            wheels = 6
            wheel_base = 4.0
        else:  # car default
            wheels = 4
            wheel_base = 2.5

        return {
            "wheels": wheels,
            "wheel_base": wheel_base,
            "suspension": {
                "stiffness": 50000,
                "damping": 4500,
                "travel": 0.3,
            },
            "engine": {
                "max_torque": 400,
                "max_rpm": 7000,
                "gear_ratios": [3.5, 2.2, 1.4, 1.0, 0.8],
            },
            "steering": {
                "max_angle": 35,
                "speed_factor": 0.8,
            },
            "brakes": {
                "max_force": 5000,
                "abs_enabled": True,
            },
            "aerodynamics": {
                "drag_coefficient": 0.3,
                "downforce_coefficient": 0.5,
            }
        }

    def _generate_character_spec(self, intent: str) -> Dict[str, Any]:
        return {
            "capsule": {
                "height": 1.8,
                "radius": 0.3,
            },
            "movement": {
                "walk_speed": 2.0,
                "run_speed": 6.0,
                "jump_force": 8.0,
                "air_control": 0.3,
            },
            "ground_detection": {
                "ray_length": 0.1,
                "max_slope": 45,
                "step_height": 0.3,
            },
            "gravity_scale": 1.0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AI CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class AICartridge:
    """
    AI Cartridge: Verified NPC Behavior Specifications

    Generates constraint-verified AI behavior for:
    - Behavior trees (selector, sequence, parallel)
    - Finite state machines (states, transitions)
    - Goal-oriented action planning (GOAP)
    - Pathfinding (A*, navmesh, flow fields)
    - Perception systems (sight, sound, memory)
    - Group behaviors (flocking, formations)
    - Difficulty scaling

    "The constraint IS the decision."
    """

    BEHAVIOR_PATTERNS = {
        "aggressive": r"\b(aggressive|attack|hostile|combat|fight|chase)\b",
        "defensive": r"\b(defensive|guard|protect|patrol|watch)\b",
        "passive": r"\b(passive|peaceful|neutral|friendly|civilian)\b",
        "fearful": r"\b(fearful|flee|escape|coward|run away)\b",
        "curious": r"\b(curious|investigate|explore|search|wander)\b",
        "supportive": r"\b(support|heal|buff|assist|help|ally)\b",
    }

    STATE_PATTERNS = {
        "idle": r"\b(idle|wait|stand|rest)\b",
        "patrol": r"\b(patrol|walk|wander|roam)\b",
        "alert": r"\b(alert|suspicious|aware|notice)\b",
        "combat": r"\b(combat|fight|attack|engage)\b",
        "flee": r"\b(flee|escape|run|retreat)\b",
        "dead": r"\b(dead|death|die|killed)\b",
        "interact": r"\b(interact|talk|trade|use)\b",
    }

    def compile(
        self,
        intent: str,
        reaction_time_ms: int = 200,
        awareness_radius: float = 50.0,
        memory_duration_s: float = 30.0,
        difficulty: float = 0.5
    ) -> CartridgeResult:
        """Compile AI intent into behavior specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp parameters
        reaction_time_ms = max(
            AI_CONSTRAINTS["reaction_time_ms"]["min"],
            min(reaction_time_ms, AI_CONSTRAINTS["reaction_time_ms"]["max"])
        )
        awareness_radius = max(
            AI_CONSTRAINTS["awareness_radius"]["min"],
            min(awareness_radius, AI_CONSTRAINTS["awareness_radius"]["max"])
        )
        memory_duration_s = max(
            AI_CONSTRAINTS["memory_duration_s"]["min"],
            min(memory_duration_s, AI_CONSTRAINTS["memory_duration_s"]["max"])
        )
        difficulty = max(0.0, min(difficulty, 1.0))

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            behavior_type = self._parse_behavior_type(intent)
            states = self._parse_states(intent)

            spec = {
                "type": "ai",
                "format": GameOutputFormat.BEHAVIOR_TREE.value,
                "behavior_type": behavior_type,
                "perception": {
                    "sight": {
                        "range": awareness_radius,
                        "fov_degrees": 120,
                        "ray_count": 8,
                    },
                    "hearing": {
                        "range": awareness_radius * 0.5,
                        "sensitivity": 0.5 + difficulty * 0.5,
                    },
                    "memory": {
                        "duration_s": memory_duration_s,
                        "max_targets": 10,
                    },
                },
                "reaction": {
                    "time_ms": reaction_time_ms,
                    "variance_ms": reaction_time_ms * 0.2,
                },
                "behavior_tree": self._generate_behavior_tree(behavior_type, difficulty),
                "state_machine": {
                    "initial_state": "idle",
                    "states": states,
                    "transitions": self._generate_transitions(states, behavior_type),
                },
                "pathfinding": {
                    "algorithm": "a_star",
                    "navmesh_agent": {
                        "radius": 0.5,
                        "height": 2.0,
                        "step_height": 0.4,
                        "max_slope": 45,
                    },
                    "avoidance": {
                        "enabled": True,
                        "priority": 50,
                    },
                },
                "difficulty_modifiers": {
                    "accuracy": 0.3 + difficulty * 0.6,
                    "aggression": 0.2 + difficulty * 0.6,
                    "reaction_speed": 1.0 - difficulty * 0.5,
                    "health_multiplier": 0.5 + difficulty * 1.0,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "bounds": {
                    "reaction_time_ms": reaction_time_ms,
                    "awareness_radius": awareness_radius,
                    "memory_duration_s": memory_duration_s,
                }
            },
            fingerprint=hashlib.sha256(f"{intent}{reaction_time_ms}{awareness_radius}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _parse_behavior_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for behavior, pattern in self.BEHAVIOR_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return behavior
        return "passive"

    def _parse_states(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        states = []
        for state, pattern in self.STATE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                states.append(state)
        return states if states else ["idle", "patrol", "alert", "combat"]

    def _generate_behavior_tree(self, behavior_type: str, difficulty: float) -> Dict[str, Any]:
        trees = {
            "aggressive": {
                "root": "selector",
                "children": [
                    {"type": "sequence", "name": "attack", "children": [
                        {"type": "condition", "name": "has_target"},
                        {"type": "condition", "name": "in_range"},
                        {"type": "action", "name": "attack_target"},
                    ]},
                    {"type": "sequence", "name": "chase", "children": [
                        {"type": "condition", "name": "has_target"},
                        {"type": "action", "name": "move_to_target"},
                    ]},
                    {"type": "action", "name": "search_for_target"},
                ]
            },
            "defensive": {
                "root": "selector",
                "children": [
                    {"type": "sequence", "name": "defend", "children": [
                        {"type": "condition", "name": "threat_detected"},
                        {"type": "action", "name": "face_threat"},
                        {"type": "action", "name": "attack_if_close"},
                    ]},
                    {"type": "action", "name": "patrol_area"},
                ]
            },
            "passive": {
                "root": "selector",
                "children": [
                    {"type": "sequence", "name": "flee_if_attacked", "children": [
                        {"type": "condition", "name": "is_damaged"},
                        {"type": "action", "name": "flee"},
                    ]},
                    {"type": "action", "name": "wander"},
                ]
            },
            "fearful": {
                "root": "selector",
                "children": [
                    {"type": "sequence", "name": "flee", "children": [
                        {"type": "condition", "name": "threat_detected"},
                        {"type": "action", "name": "flee_from_threat"},
                    ]},
                    {"type": "action", "name": "hide"},
                ]
            },
        }
        return trees.get(behavior_type, trees["passive"])

    def _generate_transitions(self, states: List[str], behavior_type: str) -> List[Dict[str, Any]]:
        transitions = []

        if "idle" in states and "patrol" in states:
            transitions.append({"from": "idle", "to": "patrol", "condition": "patrol_timer_elapsed"})
        if "patrol" in states and "alert" in states:
            transitions.append({"from": "patrol", "to": "alert", "condition": "suspicious_detected"})
        if "alert" in states and "combat" in states:
            transitions.append({"from": "alert", "to": "combat", "condition": "threat_confirmed"})
        if "combat" in states and "idle" in states:
            transitions.append({"from": "combat", "to": "idle", "condition": "no_threats"})
        if "flee" in states:
            transitions.append({"from": "combat", "to": "flee", "condition": "health_low"})
        if "dead" in states:
            transitions.append({"from": "*", "to": "dead", "condition": "health_zero"})

        return transitions


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class InputCartridge:
    """
    Input Cartridge: Verified Input Handling Specifications

    Generates constraint-verified input configurations for:
    - Keyboard and mouse mapping
    - Gamepad/controller support
    - Touch and gesture recognition
    - Motion controls (gyro, accelerometer)
    - Accessibility options
    - Input buffering and combo detection

    "The constraint IS the control scheme."
    """

    INPUT_DEVICE_PATTERNS = {
        "keyboard": r"\b(keyboard|key|wasd|arrow keys|type)\b",
        "mouse": r"\b(mouse|click|cursor|pointer|aim)\b",
        "gamepad": r"\b(gamepad|controller|joystick|xbox|playstation|dualshock|dualsense)\b",
        "touch": r"\b(touch|tap|swipe|pinch|mobile|phone|tablet)\b",
        "motion": r"\b(motion|gyro|accelerometer|tilt|shake)\b",
        "vr": r"\b(vr|virtual reality|headset|hand tracking)\b",
    }

    GENRE_PRESETS = {
        "fps": {
            "move": ["w", "a", "s", "d"],
            "look": "mouse",
            "shoot": "mouse_left",
            "aim": "mouse_right",
            "jump": "space",
            "crouch": "ctrl",
            "reload": "r",
        },
        "platformer": {
            "move": ["left", "right"],
            "jump": "space",
            "attack": "z",
            "special": "x",
        },
        "rpg": {
            "move": ["w", "a", "s", "d"],
            "interact": "e",
            "inventory": "i",
            "map": "m",
            "attack": "mouse_left",
        },
        "racing": {
            "accelerate": "w",
            "brake": "s",
            "steer": ["a", "d"],
            "nitro": "shift",
            "handbrake": "space",
        },
        "fighting": {
            "move": ["left", "right"],
            "jump": "up",
            "crouch": "down",
            "light_attack": "z",
            "heavy_attack": "x",
            "special": "c",
            "block": "v",
        },
    }

    def compile(
        self,
        intent: str,
        genre: str = "auto",
        allow_rebinding: bool = True,
        haptic_feedback: bool = True
    ) -> CartridgeResult:
        """Compile input intent into control specification."""
        start_us = time.perf_counter_ns() // 1000

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            devices = self._detect_devices(intent)
            detected_genre = self._detect_genre(intent) if genre == "auto" else genre

            spec = {
                "type": "input",
                "format": GameOutputFormat.INPUT_MAP.value,
                "devices": devices,
                "genre": detected_genre,
                "mappings": {
                    "keyboard_mouse": self._generate_keyboard_mapping(detected_genre),
                    "gamepad": self._generate_gamepad_mapping(detected_genre),
                    "touch": self._generate_touch_mapping(detected_genre) if "touch" in devices else None,
                },
                "settings": {
                    "allow_rebinding": allow_rebinding,
                    "haptic_feedback": haptic_feedback,
                    "mouse_sensitivity": 1.0,
                    "stick_deadzone": 0.15,
                    "trigger_deadzone": 0.1,
                    "invert_y": False,
                },
                "combos": self._generate_combos(detected_genre),
                "input_buffer": {
                    "enabled": True,
                    "window_ms": 100,
                },
                "accessibility": {
                    "hold_to_toggle": ["crouch", "aim"],
                    "auto_aim_assist": False,
                    "button_remapping": True,
                    "one_handed_mode": False,
                },
                "gestures": self._generate_gestures(intent) if "touch" in devices else [],
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{genre}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_devices(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        devices = []
        for device, pattern in self.INPUT_DEVICE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                devices.append(device)
        return devices if devices else ["keyboard", "mouse", "gamepad"]

    def _detect_genre(self, intent: str) -> str:
        intent_lower = intent.lower()
        if re.search(r"\b(fps|shooter|gun|shoot)\b", intent_lower):
            return "fps"
        elif re.search(r"\b(platformer|jump|side.?scroll)\b", intent_lower):
            return "platformer"
        elif re.search(r"\b(rpg|role.?play|adventure)\b", intent_lower):
            return "rpg"
        elif re.search(r"\b(racing|drive|car|race)\b", intent_lower):
            return "racing"
        elif re.search(r"\b(fighting|fighter|combat|beat.?em)\b", intent_lower):
            return "fighting"
        return "rpg"

    def _generate_keyboard_mapping(self, genre: str) -> Dict[str, Any]:
        preset = self.GENRE_PRESETS.get(genre, self.GENRE_PRESETS["rpg"])
        return {
            "actions": preset,
            "modifiers": {
                "shift": "sprint",
                "ctrl": "crouch",
                "alt": "walk",
            },
            "ui": {
                "escape": "pause",
                "tab": "scoreboard",
                "enter": "chat",
            }
        }

    def _generate_gamepad_mapping(self, genre: str) -> Dict[str, Any]:
        return {
            "sticks": {
                "left": "move",
                "right": "look" if genre in ["fps", "rpg"] else "aim",
            },
            "buttons": {
                "a": "jump" if genre != "racing" else "nitro",
                "b": "crouch" if genre == "fps" else "cancel",
                "x": "reload" if genre == "fps" else "attack",
                "y": "switch_weapon" if genre == "fps" else "interact",
            },
            "triggers": {
                "lt": "aim" if genre == "fps" else "brake",
                "rt": "shoot" if genre == "fps" else "accelerate",
            },
            "bumpers": {
                "lb": "grenade" if genre == "fps" else "prev_item",
                "rb": "melee" if genre == "fps" else "next_item",
            },
            "dpad": {
                "up": "item_1",
                "right": "item_2",
                "down": "item_3",
                "left": "item_4",
            }
        }

    def _generate_touch_mapping(self, genre: str) -> Dict[str, Any]:
        return {
            "virtual_stick_left": "move",
            "virtual_stick_right": "look",
            "tap_zones": {
                "bottom_right": "jump",
                "right_center": "attack",
                "top_right": "special",
            },
            "gestures": {
                "swipe_up": "jump",
                "swipe_down": "crouch",
                "double_tap": "interact",
                "pinch": "zoom",
            }
        }

    def _generate_combos(self, genre: str) -> List[Dict[str, Any]]:
        if genre == "fighting":
            return [
                {"name": "hadouken", "sequence": ["down", "down_right", "right", "punch"], "window_ms": 500},
                {"name": "shoryuken", "sequence": ["right", "down", "down_right", "punch"], "window_ms": 400},
                {"name": "super", "sequence": ["down", "down_right", "right", "down", "down_right", "right", "punch"], "window_ms": 800},
            ]
        elif genre == "fps":
            return [
                {"name": "quick_reload", "sequence": ["reload", "reload"], "window_ms": 200},
                {"name": "slide", "sequence": ["sprint", "crouch"], "window_ms": 300},
            ]
        return []

    def _generate_gestures(self, intent: str) -> List[Dict[str, Any]]:
        return [
            {"name": "tap", "fingers": 1, "action": "select"},
            {"name": "double_tap", "fingers": 1, "action": "interact"},
            {"name": "swipe", "fingers": 1, "directions": ["up", "down", "left", "right"]},
            {"name": "pinch", "fingers": 2, "action": "zoom"},
            {"name": "rotate", "fingers": 2, "action": "rotate_camera"},
            {"name": "long_press", "fingers": 1, "duration_ms": 500, "action": "context_menu"},
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# NETWORK CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class NetworkCartridge:
    """
    Network Cartridge: Verified Multiplayer Specifications

    Generates constraint-verified networking for:
    - Client-server architecture
    - Peer-to-peer networking
    - State synchronization
    - Lag compensation
    - Matchmaking
    - Anti-cheat considerations

    "The constraint IS the protocol."
    """

    TOPOLOGY_PATTERNS = {
        "client_server": r"\b(server|dedicated|authoritative|mmo)\b",
        "peer_to_peer": r"\b(p2p|peer|host|listen server)\b",
        "hybrid": r"\b(hybrid|relay|mixed)\b",
    }

    GAME_MODE_PATTERNS = {
        "competitive": r"\b(competitive|ranked|esport|pvp)\b",
        "cooperative": r"\b(coop|cooperative|pve|team)\b",
        "casual": r"\b(casual|social|party|fun)\b",
        "mmo": r"\b(mmo|massive|persistent|world)\b",
    }

    def compile(
        self,
        intent: str,
        max_players: int = 16,
        tick_rate: int = 64,
        region: str = "auto"
    ) -> CartridgeResult:
        """Compile network intent into multiplayer specification."""
        start_us = time.perf_counter_ns() // 1000

        # Clamp parameters
        max_players = max(1, min(max_players, NETWORK_CONSTRAINTS["max_players"]["max"]))
        tick_rate = max(
            NETWORK_CONSTRAINTS["tick_rate"]["min"],
            min(tick_rate, NETWORK_CONSTRAINTS["tick_rate"]["max"])
        )

        safety_check = ConstraintChecker.check_safety(intent)
        network_check = ConstraintChecker.check_patterns(
            intent, NETWORK_CONSTRAINTS["patterns"], "network"
        )

        verified = safety_check.passed and network_check.passed

        spec = None
        if verified:
            topology = self._detect_topology(intent)
            game_mode = self._detect_game_mode(intent)

            spec = {
                "type": "network",
                "format": GameOutputFormat.NETCODE_SPEC.value,
                "topology": topology,
                "game_mode": game_mode,
                "connection": {
                    "max_players": max_players,
                    "tick_rate": tick_rate,
                    "protocol": "udp",
                    "reliable_channel": True,
                    "unreliable_channel": True,
                },
                "synchronization": {
                    "method": "state_interpolation",
                    "interpolation_delay_ms": 100,
                    "extrapolation_limit_ms": 250,
                    "snapshot_rate": tick_rate,
                },
                "lag_compensation": {
                    "enabled": True,
                    "rewind_limit_ms": 200,
                    "client_prediction": True,
                    "server_reconciliation": True,
                },
                "matchmaking": self._generate_matchmaking(game_mode, max_players),
                "anti_cheat": {
                    "server_authoritative": topology == "client_server",
                    "input_validation": True,
                    "position_validation": True,
                    "rate_limiting": True,
                },
                "regions": ["us-east", "us-west", "eu-west", "eu-east", "asia", "oceania"] if region == "auto" else [region],
                "voice_chat": {
                    "enabled": game_mode in ["competitive", "cooperative"],
                    "codec": "opus",
                    "channels": "team" if game_mode == "competitive" else "proximity",
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "network": {"passed": network_check.passed, "violations": network_check.violations},
                "bounds": {"max_players": max_players, "tick_rate": tick_rate}
            },
            fingerprint=hashlib.sha256(f"{intent}{max_players}{tick_rate}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_topology(self, intent: str) -> str:
        intent_lower = intent.lower()
        for topology, pattern in self.TOPOLOGY_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return topology
        return "client_server"

    def _detect_game_mode(self, intent: str) -> str:
        intent_lower = intent.lower()
        for mode, pattern in self.GAME_MODE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return mode
        return "casual"

    def _generate_matchmaking(self, game_mode: str, max_players: int) -> Dict[str, Any]:
        return {
            "enabled": True,
            "algorithm": "skill_based" if game_mode == "competitive" else "quick_match",
            "parameters": {
                "skill_range": 200 if game_mode == "competitive" else 1000,
                "max_wait_time_s": 120,
                "expand_search_after_s": 30,
                "team_size": max_players // 2 if max_players > 1 else 1,
            },
            "lobby": {
                "max_size": max_players,
                "ready_check": game_mode == "competitive",
                "auto_start": game_mode == "casual",
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ECONOMY CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class EconomyCartridge:
    """
    Economy Cartridge: Verified Game Economy Specifications

    Generates constraint-verified economy systems for:
    - Currency systems (soft/hard currency)
    - Item systems (inventory, equipment, consumables)
    - Progression systems (XP, levels, skill trees)
    - Trading systems (player-to-player, marketplace)
    - Reward loops (loot tables, drop rates)
    - Monetization (ethical constraints applied)

    "The constraint IS the economy."
    """

    ECONOMY_TYPE_PATTERNS = {
        "free_to_play": r"\b(f2p|free to play|freemium|mobile)\b",
        "premium": r"\b(premium|paid|buy to play|single purchase)\b",
        "subscription": r"\b(subscription|monthly|season pass)\b",
    }

    PROGRESSION_PATTERNS = {
        "linear": r"\b(linear|story|campaign|level based)\b",
        "open": r"\b(open|sandbox|freeform|non.?linear)\b",
        "competitive": r"\b(competitive|ranked|elo|mmr|ladder)\b",
    }

    def compile(
        self,
        intent: str,
        economy_type: str = "auto",
        max_level: int = 100,
        inflation_rate: float = 0.05
    ) -> CartridgeResult:
        """Compile economy intent into game economy specification."""
        start_us = time.perf_counter_ns() // 1000

        inflation_rate = max(0, min(inflation_rate, ECONOMY_CONSTRAINTS["inflation_rate"]["max"]))

        safety_check = ConstraintChecker.check_safety(intent)
        economy_check = ConstraintChecker.check_patterns(
            intent, ECONOMY_CONSTRAINTS["patterns"], "economy"
        )

        verified = safety_check.passed and economy_check.passed

        spec = None
        if verified:
            detected_type = self._detect_economy_type(intent) if economy_type == "auto" else economy_type
            progression_type = self._detect_progression_type(intent)

            spec = {
                "type": "economy",
                "format": GameOutputFormat.ECONOMY_SPEC.value,
                "economy_type": detected_type,
                "currencies": self._generate_currencies(detected_type),
                "progression": {
                    "type": progression_type,
                    "max_level": max_level,
                    "xp_curve": self._generate_xp_curve(max_level),
                    "prestige": max_level >= 50,
                },
                "items": {
                    "rarities": ["common", "uncommon", "rare", "epic", "legendary"],
                    "rarity_weights": [0.60, 0.25, 0.10, 0.04, 0.01],
                    "categories": ["weapon", "armor", "consumable", "material", "cosmetic"],
                    "max_inventory_size": 500,
                },
                "rewards": self._generate_reward_tables(),
                "trading": {
                    "enabled": detected_type != "competitive",
                    "marketplace": detected_type == "free_to_play",
                    "player_to_player": True,
                    "trade_tax_percent": 5,
                },
                "sinks_and_faucets": {
                    "faucets": ["quests", "enemies", "daily_rewards", "achievements"],
                    "sinks": ["items", "upgrades", "repairs", "fast_travel", "cosmetics"],
                    "target_inflation_rate": inflation_rate,
                },
                "monetization": self._generate_monetization(detected_type),
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "economy": {"passed": economy_check.passed, "violations": economy_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{max_level}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_economy_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for etype, pattern in self.ECONOMY_TYPE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return etype
        return "premium"

    def _detect_progression_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for ptype, pattern in self.PROGRESSION_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return ptype
        return "linear"

    def _generate_currencies(self, economy_type: str) -> List[Dict[str, Any]]:
        currencies = [
            {"name": "gold", "type": "soft", "earn_method": "gameplay", "cap": None}
        ]
        if economy_type == "free_to_play":
            currencies.append({
                "name": "gems", "type": "hard", "earn_method": "purchase_or_rare_drop",
                "cap": None, "ethical_note": "No gameplay advantages, cosmetics only"
            })
        return currencies

    def _generate_xp_curve(self, max_level: int) -> Dict[str, Any]:
        return {
            "formula": "base * (level ^ exponent)",
            "base": 100,
            "exponent": 1.5,
            "total_xp_to_max": int(100 * sum(i ** 1.5 for i in range(1, max_level + 1))),
        }

    def _generate_reward_tables(self) -> Dict[str, Any]:
        return {
            "enemy_drops": {
                "currency_range": [10, 100],
                "xp_range": [5, 50],
                "item_chance": 0.15,
            },
            "quest_rewards": {
                "currency_multiplier": 10,
                "xp_multiplier": 5,
                "guaranteed_item": True,
            },
            "daily_login": {
                "day_1": {"currency": 100},
                "day_7": {"currency": 500, "item_rarity": "rare"},
                "day_30": {"currency": 2000, "item_rarity": "epic"},
            },
        }

    def _generate_monetization(self, economy_type: str) -> Dict[str, Any]:
        if economy_type == "premium":
            return {
                "type": "one_time_purchase",
                "dlc_support": True,
                "cosmetic_shop": False,
            }
        elif economy_type == "free_to_play":
            return {
                "type": "free_to_play",
                "cosmetic_shop": True,
                "battle_pass": True,
                "ethical_constraints": [
                    "no_pay_to_win",
                    "no_loot_boxes_with_random_gameplay_items",
                    "all_gameplay_content_earnable",
                    "clear_pricing",
                    "spending_limits_optional",
                ]
            }
        else:
            return {
                "type": "subscription",
                "monthly_cost_usd": 14.99,
                "includes_all_content": True,
            }


# ═══════════════════════════════════════════════════════════════════════════════
# NARRATIVE CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class NarrativeCartridge:
    """
    Narrative Cartridge: Verified Story and Dialogue Specifications

    Generates constraint-verified narrative systems for:
    - Dialogue trees (branching conversations)
    - Quest systems (main, side, procedural)
    - Character relationships (affinity, reputation)
    - Story state tracking
    - Localization hooks

    "The constraint IS the story structure."
    """

    NARRATIVE_STYLE_PATTERNS = {
        "linear": r"\b(linear|cinematic|scripted|story.?driven)\b",
        "branching": r"\b(branching|choice|consequence|multiple endings)\b",
        "emergent": r"\b(emergent|procedural|dynamic|systemic)\b",
        "open": r"\b(open world|sandbox|non.?linear)\b",
    }

    def compile(
        self,
        intent: str,
        max_dialogue_nodes: int = 1000,
        max_quests: int = 100,
        voice_acted: bool = False
    ) -> CartridgeResult:
        """Compile narrative intent into story specification."""
        start_us = time.perf_counter_ns() // 1000

        max_dialogue_nodes = min(max_dialogue_nodes, NARRATIVE_CONSTRAINTS["max_dialogue_nodes"]["max"])

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            narrative_style = self._detect_narrative_style(intent)

            spec = {
                "type": "narrative",
                "format": GameOutputFormat.DIALOGUE_TREE.value,
                "style": narrative_style,
                "dialogue": {
                    "max_nodes": max_dialogue_nodes,
                    "max_choices_per_node": 6,
                    "voice_acted": voice_acted,
                    "emotion_tags": ["neutral", "happy", "sad", "angry", "fearful", "surprised"],
                    "conditions": ["quest_state", "reputation", "inventory", "stats", "time"],
                },
                "quests": {
                    "max_quests": max_quests,
                    "types": ["main", "side", "daily", "event", "hidden"],
                    "structure": {
                        "objectives": ["collect", "kill", "deliver", "escort", "discover", "craft", "talk"],
                        "max_objectives_per_quest": 10,
                        "branching": narrative_style == "branching",
                    },
                },
                "relationships": {
                    "enabled": True,
                    "affinity_range": [-100, 100],
                    "reputation_factions": ["faction_a", "faction_b", "faction_c"],
                    "romance": False,  # Opt-in feature
                },
                "state_tracking": {
                    "flags": True,
                    "variables": True,
                    "quest_journal": True,
                    "codex": True,
                },
                "localization": {
                    "string_ids": True,
                    "placeholder_format": "{variable}",
                    "gender_support": True,
                    "pluralization": True,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{max_dialogue_nodes}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_narrative_style(self, intent: str) -> str:
        intent_lower = intent.lower()
        for style, pattern in self.NARRATIVE_STYLE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return style
        return "branching"


# ═══════════════════════════════════════════════════════════════════════════════
# WORLD CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class WorldCartridge:
    """
    World Cartridge: Verified Procedural World Specifications

    Generates constraint-verified world generation for:
    - Terrain generation (heightmaps, biomes)
    - Level design (rooms, corridors, arenas)
    - Prop placement (decorations, obstacles)
    - Environmental storytelling
    - LOD and streaming

    "The constraint IS the world seed."
    """

    WORLD_TYPE_PATTERNS = {
        "terrain": r"\b(terrain|landscape|outdoor|nature|world map)\b",
        "dungeon": r"\b(dungeon|cave|underground|maze|labyrinth)\b",
        "city": r"\b(city|urban|town|building|street)\b",
        "space": r"\b(space|galaxy|planet|asteroid|station)\b",
        "interior": r"\b(interior|room|building|house|indoor)\b",
    }

    BIOME_PATTERNS = {
        "forest": r"\b(forest|woods|trees|jungle)\b",
        "desert": r"\b(desert|sand|dunes|arid)\b",
        "snow": r"\b(snow|ice|frozen|tundra|arctic)\b",
        "ocean": r"\b(ocean|sea|water|underwater|beach)\b",
        "volcanic": r"\b(volcano|lava|fire|magma)\b",
        "plains": r"\b(plains|grassland|meadow|field)\b",
        "mountain": r"\b(mountain|cliff|peak|highland)\b",
    }

    def compile(
        self,
        intent: str,
        seed: Optional[int] = None,
        world_size: Tuple[int, int, int] = (1000, 100, 1000),
        chunk_size: int = 32
    ) -> CartridgeResult:
        """Compile world intent into generation specification."""
        start_us = time.perf_counter_ns() // 1000

        chunk_size = max(
            WORLD_CONSTRAINTS["chunk_size"]["min"],
            min(chunk_size, WORLD_CONSTRAINTS["chunk_size"]["max"])
        )

        if seed is None:
            seed = int(time.time() * 1000) % (2**32)
        seed = seed % WORLD_CONSTRAINTS["seed_range"]["max"]

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            world_type = self._detect_world_type(intent)
            biomes = self._detect_biomes(intent)

            spec = {
                "type": "world",
                "format": GameOutputFormat.TERRAIN_SPEC.value,
                "world_type": world_type,
                "generation": {
                    "seed": seed,
                    "size": {"x": world_size[0], "y": world_size[1], "z": world_size[2]},
                    "chunk_size": chunk_size,
                    "algorithm": self._get_generation_algorithm(world_type),
                },
                "terrain": {
                    "biomes": biomes,
                    "heightmap": {
                        "noise_type": "simplex",
                        "octaves": 6,
                        "persistence": 0.5,
                        "lacunarity": 2.0,
                        "scale": 100,
                    },
                    "features": self._get_terrain_features(world_type, biomes),
                },
                "props": {
                    "density": 0.3,
                    "categories": ["vegetation", "rocks", "debris", "structures"],
                    "clustering": True,
                },
                "streaming": {
                    "enabled": True,
                    "load_distance": chunk_size * 8,
                    "unload_distance": chunk_size * 12,
                    "lod_levels": 4,
                },
                "environment": {
                    "time_of_day": True,
                    "weather": True,
                    "ambient_sounds": True,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "bounds": {"seed": seed, "chunk_size": chunk_size}
            },
            fingerprint=hashlib.sha256(f"{intent}{seed}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_world_type(self, intent: str) -> str:
        intent_lower = intent.lower()
        for wtype, pattern in self.WORLD_TYPE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                return wtype
        return "terrain"

    def _detect_biomes(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        biomes = []
        for biome, pattern in self.BIOME_PATTERNS.items():
            if re.search(pattern, intent_lower):
                biomes.append(biome)
        return biomes if biomes else ["plains", "forest"]

    def _get_generation_algorithm(self, world_type: str) -> str:
        algorithms = {
            "terrain": "noise_based",
            "dungeon": "bsp_rooms",
            "city": "wave_function_collapse",
            "space": "poisson_disc",
            "interior": "room_templates",
        }
        return algorithms.get(world_type, "noise_based")

    def _get_terrain_features(self, world_type: str, biomes: List[str]) -> List[str]:
        features = []
        if world_type == "terrain":
            features.extend(["hills", "valleys", "rivers", "lakes"])
        if "mountain" in biomes:
            features.extend(["peaks", "cliffs", "caves"])
        if "forest" in biomes:
            features.extend(["clearings", "dense_growth"])
        if "desert" in biomes:
            features.extend(["oasis", "dunes", "canyons"])
        if "ocean" in biomes:
            features.extend(["reefs", "shipwrecks", "trenches"])
        return features


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class ParticleCartridge:
    """
    Particle Cartridge: Verified Visual Effects Specifications

    Generates constraint-verified particle systems for:
    - Explosions and impacts
    - Environmental effects (rain, snow, fog)
    - Magic and abilities
    - UI feedback
    - Ambient atmosphere

    "The constraint IS the effect."
    """

    EFFECT_PATTERNS = {
        "explosion": r"\b(explosion|explode|blast|burst|boom)\b",
        "fire": r"\b(fire|flame|burn|torch|ember)\b",
        "smoke": r"\b(smoke|steam|fog|mist|cloud)\b",
        "water": r"\b(water|splash|rain|spray|drip)\b",
        "electric": r"\b(electric|lightning|spark|zap|shock)\b",
        "magic": r"\b(magic|spell|aura|glow|energy)\b",
        "debris": r"\b(debris|dust|dirt|rubble|shatter)\b",
        "weather": r"\b(weather|rain|snow|wind|storm)\b",
    }

    def compile(
        self,
        intent: str,
        max_particles: int = 10000,
        lifetime_ms: int = 2000,
        gpu_accelerated: bool = True
    ) -> CartridgeResult:
        """Compile particle intent into effect specification."""
        start_us = time.perf_counter_ns() // 1000

        max_particles = min(max_particles, PARTICLE_CONSTRAINTS["max_particles"]["max"])
        lifetime_ms = max(
            PARTICLE_CONSTRAINTS["lifetime_ms"]["min"],
            min(lifetime_ms, PARTICLE_CONSTRAINTS["lifetime_ms"]["max"])
        )

        safety_check = ConstraintChecker.check_safety(intent)
        particle_check = ConstraintChecker.check_patterns(
            intent, PARTICLE_CONSTRAINTS["patterns"], "particle"
        )

        verified = safety_check.passed and particle_check.passed

        spec = None
        if verified:
            effect_types = self._detect_effect_types(intent)

            spec = {
                "type": "particle",
                "format": GameOutputFormat.PARTICLE_SPEC.value,
                "effect_types": effect_types,
                "system": {
                    "max_particles": max_particles,
                    "gpu_accelerated": gpu_accelerated,
                    "sort_mode": "back_to_front",
                    "render_mode": "billboard",
                },
                "emitters": [self._generate_emitter(effect) for effect in effect_types],
                "global_forces": {
                    "gravity": {"x": 0, "y": -9.81, "z": 0},
                    "wind": {"x": 0, "y": 0, "z": 0},
                    "turbulence": 0.1,
                },
                "rendering": {
                    "blend_mode": "additive" if any(e in effect_types for e in ["fire", "electric", "magic"]) else "alpha",
                    "soft_particles": True,
                    "depth_fade": True,
                },
                "optimization": {
                    "lod_enabled": True,
                    "culling": True,
                    "particle_pooling": True,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "particle": {"passed": particle_check.passed, "violations": particle_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{max_particles}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_effect_types(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        effects = []
        for effect, pattern in self.EFFECT_PATTERNS.items():
            if re.search(pattern, intent_lower):
                effects.append(effect)
        return effects if effects else ["debris"]

    def _generate_emitter(self, effect_type: str) -> Dict[str, Any]:
        presets = {
            "explosion": {
                "shape": "sphere",
                "spawn_rate": 1000,
                "burst": True,
                "lifetime_ms": 500,
                "start_speed": 20,
                "start_size": 1.0,
                "end_size": 3.0,
                "start_color": "#FF6600",
                "end_color": "#333333",
            },
            "fire": {
                "shape": "cone",
                "spawn_rate": 100,
                "burst": False,
                "lifetime_ms": 1000,
                "start_speed": 3,
                "start_size": 0.5,
                "end_size": 0.1,
                "start_color": "#FF4400",
                "end_color": "#FF0000",
            },
            "smoke": {
                "shape": "cone",
                "spawn_rate": 50,
                "burst": False,
                "lifetime_ms": 3000,
                "start_speed": 1,
                "start_size": 0.5,
                "end_size": 3.0,
                "start_color": "#666666",
                "end_color": "#00000000",
            },
            "water": {
                "shape": "hemisphere",
                "spawn_rate": 200,
                "burst": False,
                "lifetime_ms": 1500,
                "start_speed": 5,
                "start_size": 0.2,
                "end_size": 0.1,
                "start_color": "#4488FF",
                "end_color": "#4488FF88",
            },
            "electric": {
                "shape": "line",
                "spawn_rate": 500,
                "burst": True,
                "lifetime_ms": 100,
                "start_speed": 50,
                "start_size": 0.1,
                "end_size": 0.05,
                "start_color": "#88FFFF",
                "end_color": "#FFFFFF",
            },
            "magic": {
                "shape": "sphere",
                "spawn_rate": 80,
                "burst": False,
                "lifetime_ms": 2000,
                "start_speed": 2,
                "start_size": 0.3,
                "end_size": 0.0,
                "start_color": "#FF00FF",
                "end_color": "#00FFFF",
            },
        }
        return presets.get(effect_type, presets["debris"] if "debris" not in presets else {
            "shape": "point",
            "spawn_rate": 100,
            "lifetime_ms": 2000,
            "start_speed": 10,
            "start_size": 0.2,
            "end_size": 0.1,
            "start_color": "#888888",
            "end_color": "#444444",
        })


# ═══════════════════════════════════════════════════════════════════════════════
# HAPTIC CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class HapticCartridge:
    """
    Haptic Cartridge: Verified Tactile Feedback Specifications

    Generates constraint-verified haptic patterns for:
    - Controller vibration (gamepad, phone)
    - Force feedback (steering wheels, joysticks)
    - Adaptive triggers (DualSense)
    - Spatial haptics (VR controllers)

    "The constraint IS the feeling."
    """

    HAPTIC_EVENT_PATTERNS = {
        "impact": r"\b(impact|hit|collision|crash|punch|kick)\b",
        "explosion": r"\b(explosion|blast|boom|detonate)\b",
        "engine": r"\b(engine|motor|vehicle|driving|rumble)\b",
        "heartbeat": r"\b(heartbeat|pulse|health|damage)\b",
        "notification": r"\b(notification|alert|pickup|collect)\b",
        "texture": r"\b(texture|surface|terrain|ground)\b",
        "weapon": r"\b(weapon|gun|sword|bow|shoot|fire)\b",
    }

    def compile(
        self,
        intent: str,
        intensity: float = 0.5,
        duration_ms: int = 200
    ) -> CartridgeResult:
        """Compile haptic intent into feedback specification."""
        start_us = time.perf_counter_ns() // 1000

        intensity = max(
            HAPTIC_CONSTRAINTS["intensity"]["min"],
            min(intensity, HAPTIC_CONSTRAINTS["intensity"]["max"])
        )
        duration_ms = max(
            HAPTIC_CONSTRAINTS["duration_ms"]["min"],
            min(duration_ms, HAPTIC_CONSTRAINTS["duration_ms"]["max"])
        )

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            event_types = self._detect_event_types(intent)

            spec = {
                "type": "haptic",
                "format": GameOutputFormat.HAPTIC_SPEC.value,
                "event_types": event_types,
                "patterns": [self._generate_pattern(event, intensity, duration_ms) for event in event_types],
                "platforms": {
                    "ios": {
                        "api": "CoreHaptics",
                        "supported": True,
                    },
                    "android": {
                        "api": "VibrationEffect",
                        "supported": True,
                    },
                    "gamepad": {
                        "left_motor": True,
                        "right_motor": True,
                        "adaptive_triggers": True,
                    },
                },
                "accessibility": {
                    "user_adjustable": True,
                    "disable_option": True,
                    "intensity_scale": 1.0,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "bounds": {"intensity": intensity, "duration_ms": duration_ms}
            },
            fingerprint=hashlib.sha256(f"{intent}{intensity}{duration_ms}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_event_types(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        events = []
        for event, pattern in self.HAPTIC_EVENT_PATTERNS.items():
            if re.search(pattern, intent_lower):
                events.append(event)
        return events if events else ["notification"]

    def _generate_pattern(self, event_type: str, intensity: float, duration_ms: int) -> Dict[str, Any]:
        patterns = {
            "impact": {
                "type": "transient",
                "sharpness": 0.8,
                "intensity": intensity,
                "duration_ms": min(duration_ms, 100),
            },
            "explosion": {
                "type": "continuous",
                "attack_ms": 10,
                "sustain_ms": duration_ms,
                "decay_ms": 200,
                "intensity_curve": "exponential_decay",
                "base_intensity": intensity,
            },
            "engine": {
                "type": "continuous",
                "frequency_hz": 30,
                "intensity": intensity * 0.5,
                "modulation": "rpm_based",
            },
            "heartbeat": {
                "type": "pattern",
                "beats": [
                    {"delay_ms": 0, "intensity": intensity, "duration_ms": 50},
                    {"delay_ms": 100, "intensity": intensity * 0.7, "duration_ms": 50},
                ],
                "repeat": True,
                "interval_ms": 800,
            },
            "notification": {
                "type": "transient",
                "sharpness": 0.5,
                "intensity": intensity * 0.6,
                "duration_ms": 50,
            },
            "weapon": {
                "type": "transient",
                "sharpness": 1.0,
                "intensity": intensity,
                "duration_ms": 80,
                "adaptive_trigger": {"resistance": 0.7, "start_position": 0.3},
            },
        }
        return {"event": event_type, **patterns.get(event_type, patterns["notification"])}


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class SaveCartridge:
    """
    Save Cartridge: Verified State Persistence Specifications

    Generates constraint-verified save systems for:
    - Manual and auto saves
    - Cloud synchronization
    - Save file formats
    - Migration and versioning
    - Checkpoints

    "The constraint IS the memory."
    """

    SAVE_TYPE_PATTERNS = {
        "checkpoint": r"\b(checkpoint|autosave|auto.?save|automatic)\b",
        "manual": r"\b(manual|save slot|quicksave|save game)\b",
        "cloud": r"\b(cloud|sync|icloud|steam cloud|online)\b",
        "profile": r"\b(profile|settings|preferences|config)\b",
    }

    def compile(
        self,
        intent: str,
        max_saves: int = 10,
        autosave_interval_s: int = 300,
        cloud_sync: bool = True
    ) -> CartridgeResult:
        """Compile save intent into persistence specification."""
        start_us = time.perf_counter_ns() // 1000

        max_saves = min(max_saves, SAVE_CONSTRAINTS["max_save_slots"]["max"])
        autosave_interval_s = max(
            SAVE_CONSTRAINTS["autosave_interval_s"]["min"],
            min(autosave_interval_s, SAVE_CONSTRAINTS["autosave_interval_s"]["max"])
        )

        safety_check = ConstraintChecker.check_safety(intent)
        save_check = ConstraintChecker.check_patterns(
            intent, SAVE_CONSTRAINTS["patterns"], "save"
        )

        verified = safety_check.passed and save_check.passed

        spec = None
        if verified:
            save_types = self._detect_save_types(intent)

            spec = {
                "type": "save",
                "format": GameOutputFormat.SAVE_SPEC.value,
                "save_types": save_types,
                "slots": {
                    "max_saves": max_saves,
                    "quicksave_slot": True,
                    "autosave_slots": 3,
                },
                "autosave": {
                    "enabled": "checkpoint" in save_types or "autosave" in intent.lower(),
                    "interval_s": autosave_interval_s,
                    "triggers": ["level_complete", "checkpoint_reached", "significant_progress"],
                },
                "cloud": {
                    "enabled": cloud_sync,
                    "provider": "platform_native",  # iCloud, Steam Cloud, etc.
                    "conflict_resolution": "newest_wins",
                    "offline_support": True,
                },
                "data_format": {
                    "format": "json",
                    "compression": "gzip",
                    "encryption": True,
                    "versioning": True,
                    "current_version": 1,
                },
                "contents": {
                    "player_state": True,
                    "world_state": True,
                    "quest_progress": True,
                    "inventory": True,
                    "settings": False,  # Settings saved separately
                    "statistics": True,
                    "achievements": True,
                },
                "migration": {
                    "auto_migrate": True,
                    "backup_before_migrate": True,
                    "supported_versions": [1],
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=verified,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
                "save": {"passed": save_check.passed, "violations": save_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{max_saves}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )

    def _detect_save_types(self, intent: str) -> List[str]:
        intent_lower = intent.lower()
        types = []
        for stype, pattern in self.SAVE_TYPE_PATTERNS.items():
            if re.search(pattern, intent_lower):
                types.append(stype)
        return types if types else ["manual", "checkpoint"]


# ═══════════════════════════════════════════════════════════════════════════════
# LOCALE CARTRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class LocaleCartridge:
    """
    Locale Cartridge: Verified Localization Specifications

    Generates constraint-verified localization for:
    - Text translation structure
    - Audio localization
    - Cultural adaptation
    - Accessibility features
    - Right-to-left support

    "The constraint IS the language."
    """

    def compile(
        self,
        intent: str,
        base_language: str = "en",
        target_languages: Optional[List[str]] = None,
        voice_localization: bool = False
    ) -> CartridgeResult:
        """Compile locale intent into localization specification."""
        start_us = time.perf_counter_ns() // 1000

        if target_languages is None:
            target_languages = ["en", "es", "fr", "de", "ja", "zh", "ko", "pt", "ru", "it"]

        target_languages = target_languages[:LOCALE_CONSTRAINTS["max_languages"]["max"]]

        safety_check = ConstraintChecker.check_safety(intent)

        spec = None
        if safety_check.passed:
            spec = {
                "type": "locale",
                "format": GameOutputFormat.LOCALE_SPEC.value,
                "base_language": base_language,
                "target_languages": target_languages,
                "text": {
                    "format": "key_value",
                    "file_format": "json",
                    "encoding": "utf-8",
                    "placeholder_syntax": "{variable}",
                    "pluralization": True,
                    "gendered_text": True,
                    "context_hints": True,
                },
                "audio": {
                    "voice_localization": voice_localization,
                    "subtitles": True,
                    "audio_description": True,
                },
                "rtl_support": {
                    "enabled": any(lang in target_languages for lang in ["ar", "he", "fa"]),
                    "mirror_ui": True,
                },
                "cultural_adaptation": {
                    "date_format": "locale_native",
                    "number_format": "locale_native",
                    "currency_format": "locale_native",
                    "color_sensitivity": True,
                    "iconography_review": True,
                },
                "accessibility": {
                    "screen_reader_support": True,
                    "text_to_speech": True,
                    "high_contrast_mode": True,
                    "font_size_options": [0.8, 1.0, 1.2, 1.5, 2.0],
                    "colorblind_modes": ["deuteranopia", "protanopia", "tritanopia"],
                },
                "workflow": {
                    "string_extraction": True,
                    "translation_memory": True,
                    "machine_translation_draft": True,
                    "review_required": True,
                },
                "intent_hash": hashlib.sha256(intent.encode()).hexdigest()[:16].upper()
            }

        elapsed_us = (time.perf_counter_ns() // 1000) - start_us

        return CartridgeResult(
            verified=safety_check.passed,
            cartridge_type=CartridgeType.DATA,
            spec=spec,
            constraints={
                "safety": {"passed": safety_check.passed, "violations": safety_check.violations},
            },
            fingerprint=hashlib.sha256(f"{intent}{base_language}".encode()).hexdigest()[:12].upper(),
            elapsed_us=elapsed_us,
            timestamp=int(time.time() * 1000)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GAME CARTRIDGE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class GameCartridgeManager:
    """
    Central manager for all Newton Game Cartridges.

    Provides unified interface for game system specification
    with automatic type detection and composition.
    """

    def __init__(self):
        self.physics = PhysicsCartridge()
        self.ai = AICartridge()
        self.input = InputCartridge()
        self.network = NetworkCartridge()
        self.economy = EconomyCartridge()
        self.narrative = NarrativeCartridge()
        self.world = WorldCartridge()
        self.particle = ParticleCartridge()
        self.haptic = HapticCartridge()
        self.save = SaveCartridge()
        self.locale = LocaleCartridge()

    def compile_physics(self, intent: str, **kwargs) -> CartridgeResult:
        return self.physics.compile(intent, **kwargs)

    def compile_ai(self, intent: str, **kwargs) -> CartridgeResult:
        return self.ai.compile(intent, **kwargs)

    def compile_input(self, intent: str, **kwargs) -> CartridgeResult:
        return self.input.compile(intent, **kwargs)

    def compile_network(self, intent: str, **kwargs) -> CartridgeResult:
        return self.network.compile(intent, **kwargs)

    def compile_economy(self, intent: str, **kwargs) -> CartridgeResult:
        return self.economy.compile(intent, **kwargs)

    def compile_narrative(self, intent: str, **kwargs) -> CartridgeResult:
        return self.narrative.compile(intent, **kwargs)

    def compile_world(self, intent: str, **kwargs) -> CartridgeResult:
        return self.world.compile(intent, **kwargs)

    def compile_particle(self, intent: str, **kwargs) -> CartridgeResult:
        return self.particle.compile(intent, **kwargs)

    def compile_haptic(self, intent: str, **kwargs) -> CartridgeResult:
        return self.haptic.compile(intent, **kwargs)

    def compile_save(self, intent: str, **kwargs) -> CartridgeResult:
        return self.save.compile(intent, **kwargs)

    def compile_locale(self, intent: str, **kwargs) -> CartridgeResult:
        return self.locale.compile(intent, **kwargs)

    def compile_full_game(self, intent: str, **kwargs) -> Dict[str, CartridgeResult]:
        """
        Compile a complete game specification from a single intent.

        Returns all relevant cartridge specifications for the game.
        """
        results = {}

        # Always compile these core systems
        results["physics"] = self.compile_physics(intent, **kwargs.get("physics", {}))
        results["ai"] = self.compile_ai(intent, **kwargs.get("ai", {}))
        results["input"] = self.compile_input(intent, **kwargs.get("input", {}))
        results["economy"] = self.compile_economy(intent, **kwargs.get("economy", {}))
        results["world"] = self.compile_world(intent, **kwargs.get("world", {}))
        results["save"] = self.compile_save(intent, **kwargs.get("save", {}))

        # Compile optional systems based on intent
        intent_lower = intent.lower()

        if re.search(r"\b(multiplayer|online|coop|pvp|mmo)\b", intent_lower):
            results["network"] = self.compile_network(intent, **kwargs.get("network", {}))

        if re.search(r"\b(story|quest|dialogue|narrative|rpg)\b", intent_lower):
            results["narrative"] = self.compile_narrative(intent, **kwargs.get("narrative", {}))

        if re.search(r"\b(effect|particle|explosion|magic|weather)\b", intent_lower):
            results["particle"] = self.compile_particle(intent, **kwargs.get("particle", {}))

        if re.search(r"\b(haptic|vibrat|feedback|controller)\b", intent_lower):
            results["haptic"] = self.compile_haptic(intent, **kwargs.get("haptic", {}))

        if re.search(r"\b(locali|translat|language|international)\b", intent_lower):
            results["locale"] = self.compile_locale(intent, **kwargs.get("locale", {}))

        return results


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

_game_cartridge_manager: Optional[GameCartridgeManager] = None


def get_game_cartridge_manager() -> GameCartridgeManager:
    """Get or create the global GameCartridgeManager instance."""
    global _game_cartridge_manager
    if _game_cartridge_manager is None:
        _game_cartridge_manager = GameCartridgeManager()
    return _game_cartridge_manager


__all__ = [
    # Types
    'GameCartridgeType',
    'GameOutputFormat',

    # Constraints
    'PHYSICS_CONSTRAINTS',
    'AI_CONSTRAINTS',
    'INPUT_CONSTRAINTS',
    'NETWORK_CONSTRAINTS',
    'ECONOMY_CONSTRAINTS',
    'NARRATIVE_CONSTRAINTS',
    'WORLD_CONSTRAINTS',
    'PARTICLE_CONSTRAINTS',
    'HAPTIC_CONSTRAINTS',
    'SAVE_CONSTRAINTS',
    'LOCALE_CONSTRAINTS',

    # Cartridges
    'PhysicsCartridge',
    'AICartridge',
    'InputCartridge',
    'NetworkCartridge',
    'EconomyCartridge',
    'NarrativeCartridge',
    'WorldCartridge',
    'ParticleCartridge',
    'HapticCartridge',
    'SaveCartridge',
    'LocaleCartridge',

    # Manager
    'GameCartridgeManager',
    'get_game_cartridge_manager',
]
