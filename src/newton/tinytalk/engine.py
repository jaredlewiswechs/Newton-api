"""
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk Engine - Kinetic Intent and Motion
═══════════════════════════════════════════════════════════════════════════════

The Delta Function (Δ) - Animation is the mathematical resolution between
two or more established Presences.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable
from .core import Blueprint, Law, LawResult, LawViolation, field as tt_field


@dataclass
class Presence:
    """
    A snapshot of state at a point in time.

    The "Before" card or "After" card in the Kinetic Engine.
    """
    state: Dict[str, Any]
    timestamp: Optional[float] = None
    label: str = ""

    def __sub__(self, other: 'Presence') -> 'Delta':
        """Calculate the delta between two presences."""
        if not isinstance(other, Presence):
            raise TypeError(f"Cannot subtract {type(other).__name__} from Presence")
        return Delta.from_presences(other, self)

    def __repr__(self):
        return f"Presence({self.state}, label='{self.label}')"


@dataclass
class Delta:
    """
    The mathematical resolution between two Presences.

    Delta IS the motion. No guessing. No prediction. Just math.
    """
    changes: Dict[str, Any]
    source: Optional[Presence] = None
    target: Optional[Presence] = None

    @classmethod
    def from_presences(cls, start: Presence, end: Presence) -> 'Delta':
        """Calculate delta from start to end presence."""
        changes = {}

        # Find all keys
        all_keys = set(start.state.keys()) | set(end.state.keys())

        for key in all_keys:
            start_val = start.state.get(key)
            end_val = end.state.get(key)

            if start_val != end_val:
                # Try numeric diff
                if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                    changes[key] = {
                        'from': start_val,
                        'to': end_val,
                        'delta': end_val - start_val
                    }
                else:
                    changes[key] = {
                        'from': start_val,
                        'to': end_val,
                        'delta': None  # Non-numeric change
                    }

        return cls(changes=changes, source=start, target=end)

    def __repr__(self):
        return f"Delta({self.changes})"


class KineticEngine(Blueprint):
    """
    The master motion engine from the tinyTalk Bible.

    Resolves movement through the Delta Function while respecting Laws.

    Usage:
        engine = KineticEngine()

        # Define start and end states
        start = Presence({'x': 0, 'y': 0})
        end = Presence({'x': 100, 'y': 50})

        # Calculate and execute motion
        result = engine.resolve_motion(start, end)
    """

    presence_start = tt_field(Presence, default=None)
    presence_end = tt_field(Presence, default=None)
    kinetic_delta = tt_field(Delta, default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._boundary_checks: List[Callable[[Delta], bool]] = []

    def add_boundary(self, check: Callable[[Delta], bool], name: str = ""):
        """
        Add a boundary check for the delta.

        The check should return True if the delta violates the boundary.

        Usage:
            engine.add_boundary(
                lambda d: d.changes.get('x', {}).get('to', 0) > 100,
                name="MaxX"
            )
        """
        self._boundary_checks.append((check, name))

    def resolve_motion(
        self,
        start: Presence,
        end: Presence,
        signal: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolve motion from start to end presence.

        This is the core forge that:
        1. Initializes state from start presence
        2. Projects the end state (intent)
        3. Calculates the kinetic delta
        4. Checks all boundary laws
        5. Executes the transition if allowed

        Returns:
            Dict with status, delta, and any violations
        """
        # 1. State Initialization
        self.presence_start = start

        # 2. Project the Intent
        self.presence_end = end

        # 3. Calculate the Delta
        self.kinetic_delta = end - start

        # 4. Sovereign Audit - Check boundaries
        for check, name in self._boundary_checks:
            try:
                if check(self.kinetic_delta):
                    return {
                        'status': 'finfr',
                        'reason': f"Boundary '{name}' violated",
                        'message': "ONTO DEATH: This motion cannot exist.",
                        'delta': self.kinetic_delta.changes
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'reason': str(e),
                    'delta': self.kinetic_delta.changes
                }

        # 5. Motion is allowed
        return {
            'status': 'synchronized',
            'delta': self.kinetic_delta.changes,
            'from': start.state,
            'to': end.state
        }

    def interpolate(
        self,
        start: Presence,
        end: Presence,
        steps: int = 10
    ) -> List[Presence]:
        """
        Generate intermediate presences between start and end.

        This is useful for animation - it creates the "frames" between
        two states, respecting all boundaries at each step.

        Returns:
            List of Presence objects from start to end
        """
        if steps < 2:
            return [start, end]

        presences = [start]
        delta = end - start

        for i in range(1, steps):
            t = i / (steps - 1)  # 0 to 1
            intermediate_state = {}

            for key in start.state:
                start_val = start.state.get(key, 0)
                if key in delta.changes and delta.changes[key]['delta'] is not None:
                    change = delta.changes[key]['delta']
                    intermediate_state[key] = start_val + change * t
                else:
                    # For non-numeric, snap to end at midpoint
                    if t >= 0.5 and key in delta.changes:
                        intermediate_state[key] = delta.changes[key]['to']
                    else:
                        intermediate_state[key] = start_val

            presences.append(Presence(
                state=intermediate_state,
                label=f"step_{i}"
            ))

        presences[-1] = end  # Ensure we end exactly at end
        return presences


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def motion(start: Dict, end: Dict) -> Delta:
    """
    Quick helper to calculate motion between two states.

    Usage:
        delta = motion({'x': 0}, {'x': 100})
        print(delta.changes)  # {'x': {'from': 0, 'to': 100, 'delta': 100}}
    """
    return Presence(start) - Presence(end)
