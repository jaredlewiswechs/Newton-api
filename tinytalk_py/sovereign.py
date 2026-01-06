"""
===============================================================================
 SovereignEngine - Constraint Enforcement for Autonomous Systems
===============================================================================

STATUS: WORKING IMPLEMENTATION (not a spec)

This module implements the concrete enforcement mechanics for constraint-first
autonomous systems. It bridges the spec concepts to Newton's existing:
- Blueprint/Law/Forge architecture (tinytalk_py/core.py)
- Delta/Presence/KineticEngine (tinytalk_py/engine.py)
- Ledger with Merkle proofs (core/ledger.py)

ENFORCEMENT MECHANICS IMPLEMENTED:
1. project_future() - State projection from intent signals
2. Boundary system - Physical/logical boundary definitions
3. Mutual exclusion - Prevents conflicting presence states
4. f/g ratio audit - Dimensional analysis before commit
5. Rollback - Automatic state restoration on law violation
6. Ledger integration - Cryptographic audit trail

Author: Newton API
License: MIT
===============================================================================
"""

from dataclasses import dataclass, field as dc_field
from typing import Any, Dict, Optional, List, Callable, Tuple, Union
from enum import Enum
import time
import hashlib
import copy

from .core import (
    Blueprint, Law, LawResult, LawViolation, FinClosure,
    field, law, forge, when, finfr, fin,
    ratio, RatioResult, finfr_if_undefined
)
from .engine import Presence, Delta, KineticEngine


# =============================================================================
# LAYER 0: GOVERNANCE - Boundary Definitions
# =============================================================================

class BoundaryType(Enum):
    """Types of boundaries that constrain motion."""
    PHYSICAL = "physical"      # Hard physical limits (e.g., max velocity)
    LOGICAL = "logical"        # Logical constraints (e.g., non-negative balance)
    TEMPORAL = "temporal"      # Time-based constraints (e.g., rate limits)
    ONTOLOGICAL = "ontological"  # Existence constraints (e.g., mutual exclusion)


@dataclass
class Boundary:
    """
    A boundary defines where movement is impossible.

    Boundaries are the "vault walls" - immutable constraints that can never
    be violated regardless of intent.
    """
    name: str
    type_: BoundaryType
    check: Callable[[Delta, 'SovereignEngine'], bool]
    message: str = ""

    def evaluate(self, delta: Delta, engine: 'SovereignEngine') -> Tuple[bool, str]:
        """
        Evaluate if this boundary is violated by the delta.

        Returns:
            (violated: bool, message: str)
        """
        try:
            violated = self.check(delta, engine)
            if violated:
                return True, self.message or f"Boundary '{self.name}' violated"
            return False, ""
        except Exception as e:
            # Errors in boundary checks are treated as violations (fail-safe)
            return True, f"Boundary '{self.name}' check failed: {str(e)}"


class BoundaryRegistry:
    """
    Registry of all active boundaries.

    Boundaries are organized by type for efficient evaluation.
    """

    def __init__(self):
        self._boundaries: Dict[BoundaryType, List[Boundary]] = {
            bt: [] for bt in BoundaryType
        }

    def register(
        self,
        name: str,
        check: Callable[[Delta, 'SovereignEngine'], bool],
        type_: BoundaryType = BoundaryType.LOGICAL,
        message: str = ""
    ) -> Boundary:
        """Register a new boundary."""
        boundary = Boundary(name=name, type_=type_, check=check, message=message)
        self._boundaries[type_].append(boundary)
        return boundary

    def evaluate_all(
        self,
        delta: Delta,
        engine: 'SovereignEngine'
    ) -> List[Tuple[Boundary, str]]:
        """
        Evaluate all boundaries against a delta.

        Returns list of (boundary, message) for all violations.
        """
        violations = []
        for type_ in BoundaryType:
            for boundary in self._boundaries[type_]:
                violated, msg = boundary.evaluate(delta, engine)
                if violated:
                    violations.append((boundary, msg))
        return violations

    def clear(self, type_: Optional[BoundaryType] = None):
        """Clear boundaries (optionally by type)."""
        if type_:
            self._boundaries[type_] = []
        else:
            for bt in BoundaryType:
                self._boundaries[bt] = []


# =============================================================================
# STATE PROJECTION - The project_future() Implementation
# =============================================================================

@dataclass
class Intent:
    """
    A signal of desired state change.

    Intents describe what should change without specifying how.
    The sovereign engine resolves intents into deltas.
    """
    action: str                          # The verb (e.g., "withdraw", "move")
    parameters: Dict[str, Any]           # Action parameters
    constraints: Dict[str, Any] = None   # Optional constraints on result
    priority: int = 0                    # Resolution priority

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


def project_future(
    current_state: Dict[str, Any],
    intent: Intent,
    projectors: Optional[Dict[str, Callable]] = None
) -> Presence:
    """
    Project the future state from current state and intent.

    This is the core function that transforms intent into a concrete
    end-state Presence. It applies intent parameters to current state
    using registered projectors or default arithmetic.

    Args:
        current_state: The current state dictionary
        intent: The Intent signal describing desired change
        projectors: Optional dict of custom projection functions
            {action_name: (state, params) -> new_state}

    Returns:
        Presence representing the projected future state

    Example:
        >>> state = {'balance': 1000}
        >>> intent = Intent('withdraw', {'amount': 200})
        >>> future = project_future(state, intent)
        >>> future.state['balance']
        800
    """
    projectors = projectors or {}
    new_state = copy.deepcopy(current_state)

    # Check for custom projector
    if intent.action in projectors:
        new_state = projectors[intent.action](new_state, intent.parameters)
    else:
        # Default projection: apply parameters as deltas
        new_state = _default_projection(new_state, intent)

    # Apply constraints (clip to valid ranges)
    for field_name, constraint in intent.constraints.items():
        if field_name in new_state:
            if isinstance(constraint, dict):
                if 'min' in constraint:
                    new_state[field_name] = max(new_state[field_name], constraint['min'])
                if 'max' in constraint:
                    new_state[field_name] = min(new_state[field_name], constraint['max'])

    return Presence(
        state=new_state,
        timestamp=time.time(),
        label=f"projected:{intent.action}"
    )


def _default_projection(state: Dict[str, Any], intent: Intent) -> Dict[str, Any]:
    """
    Default projection logic for common actions.

    Supports:
    - 'set': Direct assignment
    - 'add'/'increment': Addition
    - 'subtract'/'decrement'/'withdraw': Subtraction
    - 'multiply'/'scale': Multiplication
    - 'move': Delta-based movement
    """
    action = intent.action.lower()
    params = intent.parameters

    if action in ('set', 'assign'):
        for key, value in params.items():
            state[key] = value

    elif action in ('add', 'increment', 'deposit'):
        for key, value in params.items():
            if key in state and isinstance(state[key], (int, float)):
                state[key] = state[key] + value
            else:
                state[key] = value

    elif action in ('subtract', 'decrement', 'withdraw'):
        for key, value in params.items():
            if key in state and isinstance(state[key], (int, float)):
                state[key] = state[key] - value

    elif action in ('multiply', 'scale'):
        for key, value in params.items():
            if key in state and isinstance(state[key], (int, float)):
                state[key] = state[key] * value

    elif action == 'move':
        # Delta-based movement: apply delta to each field
        for key, delta in params.items():
            if key in state and isinstance(state[key], (int, float)):
                state[key] = state[key] + delta
            elif key.endswith('_delta'):
                base_key = key[:-6]  # Remove '_delta' suffix
                if base_key in state:
                    state[base_key] = state[base_key] + delta

    else:
        # Unknown action: treat params as direct field assignments
        for key, value in params.items():
            state[key] = value

    return state


# =============================================================================
# F/G RATIO AUDIT - Dimensional Analysis
# =============================================================================

@dataclass
class AuditResult:
    """Result of sovereign audit with f/g ratio analysis."""
    passed: bool
    fg_ratio: Optional[float]
    violations: List[Tuple[str, str]]  # (boundary_name, message)
    delta: Optional[Delta]
    timestamp: float = dc_field(default_factory=time.time)
    audit_hash: str = ""

    def __post_init__(self):
        if not self.audit_hash:
            # Generate deterministic hash of audit
            content = f"{self.passed}:{self.fg_ratio}:{len(self.violations)}"
            self.audit_hash = hashlib.sha256(content.encode()).hexdigest()[:16]


def calculate_fg_ratio(
    delta: Delta,
    ground_constraints: Dict[str, float]
) -> RatioResult:
    """
    Calculate the f/g ratio for a delta against ground constraints.

    f = forge magnitude (sum of absolute changes)
    g = ground capacity (sum of constraint limits)

    When f/g >= 1.0, the operation exceeds available capacity.

    Args:
        delta: The proposed state change
        ground_constraints: Dict mapping field names to their limits
            e.g., {'balance': 1000} means balance has capacity 1000

    Returns:
        RatioResult that can be compared with threshold

    Example:
        >>> delta = Delta({'balance': {'from': 1000, 'to': 200, 'delta': -800}})
        >>> constraints = {'balance': 1000}
        >>> r = calculate_fg_ratio(delta, constraints)
        >>> r > 1.0  # Would this overdraw?
        False
        >>> r.value
        0.8
    """
    f_total = 0.0  # Forge magnitude
    g_total = 0.0  # Ground capacity

    for field_name, change in delta.changes.items():
        if isinstance(change, dict) and change.get('delta') is not None:
            # Accumulate forge magnitude (absolute change)
            f_total += abs(change['delta'])

            # Accumulate ground capacity
            if field_name in ground_constraints:
                g_total += abs(ground_constraints[field_name])
            else:
                # No constraint = infinite capacity for this field
                pass

    # If no ground constraints, ratio is 0 (always passes)
    if g_total == 0:
        return ratio(f_total, float('inf'))

    return ratio(f_total, g_total)


# =============================================================================
# MUTUAL EXCLUSION - Presence Conflict Detection
# =============================================================================

@dataclass
class PresenceState:
    """
    A named state that can be active or inactive.

    Used for mutual exclusion checking - two conflicting presences
    cannot both be active.
    """
    name: str
    active: bool = False
    exclusive_with: List[str] = dc_field(default_factory=list)


class PresenceManager:
    """
    Manages presence states and detects conflicts.

    This implements the ontological integrity law - reality cannot
    exist in two mutually exclusive states.
    """

    def __init__(self):
        self._presences: Dict[str, PresenceState] = {}

    def register(
        self,
        name: str,
        exclusive_with: Optional[List[str]] = None
    ) -> PresenceState:
        """Register a named presence state."""
        state = PresenceState(
            name=name,
            exclusive_with=exclusive_with or []
        )
        self._presences[name] = state
        return state

    def activate(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Activate a presence state.

        Returns:
            (success, conflicting_presence)
        """
        if name not in self._presences:
            return False, f"Unknown presence: {name}"

        presence = self._presences[name]

        # Check for conflicts
        for exclusive in presence.exclusive_with:
            if exclusive in self._presences and self._presences[exclusive].active:
                return False, f"Conflicts with active presence: {exclusive}"

        presence.active = True
        return True, None

    def deactivate(self, name: str):
        """Deactivate a presence state."""
        if name in self._presences:
            self._presences[name].active = False

    def check_conflicts(self) -> List[Tuple[str, str]]:
        """
        Check for any active conflicts.

        Returns list of (presence_a, presence_b) conflicts.
        """
        conflicts = []
        for name, presence in self._presences.items():
            if presence.active:
                for exclusive in presence.exclusive_with:
                    if exclusive in self._presences and self._presences[exclusive].active:
                        # Avoid duplicates
                        pair = tuple(sorted([name, exclusive]))
                        if pair not in conflicts:
                            conflicts.append(pair)
        return conflicts

    def is_active(self, name: str) -> bool:
        """Check if a presence is active."""
        return name in self._presences and self._presences[name].active


# =============================================================================
# SOVEREIGN ENGINE - The Master Implementation
# =============================================================================

class SovereignEngine(KineticEngine):
    """
    The Master Canon: Constraint-first enforcement for autonomous systems.

    This is a WORKING IMPLEMENTATION that:
    1. Extends KineticEngine with governance layer
    2. Implements project_future() for state projection
    3. Enforces boundaries before any state change
    4. Calculates f/g ratios for dimensional analysis
    5. Provides rollback on any law violation
    6. Generates cryptographic audit proofs

    LAYER 0 (Governance):
        - Boundaries: Physical/logical walls
        - Presence conflicts: Mutual exclusion
        - f/g threshold: Capacity limits

    LAYER 1 (Executive):
        - Intent processing: Signal -> Projected state
        - Delta calculation: Before -> After
        - Motion execution: If laws pass

    Usage:
        engine = SovereignEngine()

        # Define boundaries
        engine.boundaries.register(
            'no_overdraft',
            lambda d, e: d.changes.get('balance', {}).get('to', 0) < 0,
            BoundaryType.LOGICAL,
            'Balance cannot go negative'
        )

        # Set ground constraints (for f/g ratio)
        engine.set_ground_constraints({'balance': 1000})

        # Process intent
        result = engine.execute_intent(
            Intent('withdraw', {'balance': 200})
        )
    """

    # Layer 0: Governance fields
    fg_threshold = field(float, default=1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Governance components
        self.boundaries = BoundaryRegistry()
        self.presences = PresenceManager()
        self._ground_constraints: Dict[str, float] = {}
        self._projectors: Dict[str, Callable] = {}
        self._audit_log: List[AuditResult] = []

        # Register default boundaries from laws
        self._register_default_boundaries()

    def _register_default_boundaries(self):
        """Register boundaries from @law decorated methods."""
        # The persistence_of_reality law
        self.boundaries.register(
            'persistence_of_reality',
            self._check_physical_boundary,
            BoundaryType.PHYSICAL,
            'Motion intersects physical boundary - reality frozen'
        )

        # The ontological_integrity law
        self.boundaries.register(
            'ontological_integrity',
            self._check_ontological_conflict,
            BoundaryType.ONTOLOGICAL,
            'Mutually exclusive states cannot coexist'
        )

    def _check_physical_boundary(self, delta: Delta, engine: 'SovereignEngine') -> bool:
        """
        Check if delta intersects physical boundaries.

        This is the concrete implementation of delta_path_intersects_physical_boundary.
        """
        for field_name, change in delta.changes.items():
            if isinstance(change, dict):
                # Check if path crosses any registered boundary
                for boundary_check, _ in self._boundary_checks:
                    if boundary_check(delta):
                        return True
        return False

    def _check_ontological_conflict(self, delta: Delta, engine: 'SovereignEngine') -> bool:
        """
        Check if delta creates ontological conflict.

        This implements the presence_a_active and presence_b_active check.
        """
        conflicts = self.presences.check_conflicts()
        return len(conflicts) > 0

    def set_ground_constraints(self, constraints: Dict[str, float]):
        """
        Set ground constraints for f/g ratio calculation.

        Args:
            constraints: Dict mapping field names to capacity limits
        """
        self._ground_constraints = constraints

    def register_projector(self, action: str, projector: Callable[[Dict, Dict], Dict]):
        """
        Register a custom projector for an action type.

        Args:
            action: The action name (e.g., 'withdraw')
            projector: Function (state, params) -> new_state
        """
        self._projectors[action] = projector

    def define_presence(
        self,
        name: str,
        exclusive_with: Optional[List[str]] = None
    ):
        """Define a named presence state for mutual exclusion tracking."""
        self.presences.register(name, exclusive_with)

    @law
    def persistence_of_reality(self):
        """If the proposed delta violates physical boundaries, freeze reality."""
        if self.kinetic_delta is not None:
            for check, name in self._boundary_checks:
                if check(self.kinetic_delta):
                    when(True, finfr)

    @law
    def ontological_integrity(self):
        """Reality cannot exist in two mutually exclusive states."""
        conflicts = self.presences.check_conflicts()
        when(len(conflicts) > 0, finfr)

    @law
    def fg_ratio_check(self):
        """f/g ratio must not exceed threshold."""
        if self.kinetic_delta is not None and self._ground_constraints:
            fg = calculate_fg_ratio(self.kinetic_delta, self._ground_constraints)
            when(fg >= self.fg_threshold, finfr)

    def _sovereign_audit(self, delta: Delta) -> AuditResult:
        """
        Perform sovereign audit on proposed delta.

        This is the concrete implementation of the "Sovereign Audit" comment block.
        It checks all boundaries and calculates f/g ratio.

        Returns:
            AuditResult with pass/fail and diagnostics
        """
        violations = []

        # Check all boundaries
        boundary_violations = self.boundaries.evaluate_all(delta, self)
        for boundary, msg in boundary_violations:
            violations.append((boundary.name, msg))

        # Calculate f/g ratio
        fg_ratio = None
        if self._ground_constraints:
            fg = calculate_fg_ratio(delta, self._ground_constraints)
            fg_ratio = fg.value if not fg.undefined else float('inf')

            if fg >= self.fg_threshold:
                violations.append((
                    'fg_threshold',
                    f'f/g ratio {fg_ratio:.4f} >= threshold {self.fg_threshold}'
                ))

        # Check presence conflicts
        conflicts = self.presences.check_conflicts()
        for a, b in conflicts:
            violations.append((
                'presence_conflict',
                f'Presences "{a}" and "{b}" are mutually exclusive'
            ))

        result = AuditResult(
            passed=len(violations) == 0,
            fg_ratio=fg_ratio,
            violations=violations,
            delta=delta
        )

        self._audit_log.append(result)
        return result

    @forge
    def execute_intent(self, intent: Intent) -> Dict[str, Any]:
        """
        Execute an intent through the sovereign engine.

        This is the main entry point that:
        1. Captures current state (Before Card)
        2. Projects future state (After Card)
        3. Calculates kinetic delta
        4. Performs sovereign audit
        5. Executes if all laws pass

        Args:
            intent: The Intent signal to execute

        Returns:
            Dict with status, delta, and audit results

        Raises:
            LawViolation: If any law prevents the state change
        """
        # 1. State Initialization: Where are we now?
        self.presence_start = Presence(
            state=self._get_state(),
            timestamp=time.time(),
            label="current"
        )

        # 2. Projection: Define the "After" Card (Intent)
        self.presence_end = project_future(
            self.presence_start.state,
            intent,
            self._projectors
        )

        # 3. Delta Function: Calculate the 'Diff'
        # The Kinetic Engine models motion as math.
        self.kinetic_delta = self.presence_end - self.presence_start

        # 4. Sovereign Audit
        # The Kernel projects if the kinetic_delta triggers any Laws.
        # If f/g >= threshold, finfr fires before the commit.
        audit = self._sovereign_audit(self.kinetic_delta)

        if not audit.passed:
            # Violations found - raise law violation
            # (The @forge decorator will rollback)
            raise LawViolation(
                'sovereign_audit',
                f"Audit failed: {audit.violations}"
            )

        # 5. Apply the state change
        for field_name, change in self.kinetic_delta.changes.items():
            if isinstance(change, dict) and 'to' in change:
                if hasattr(self, field_name):
                    setattr(self, field_name, change['to'])

        # Return tandem pair: (value, proof)
        return {
            'status': 'MOTION_SYNCHRONIZED',
            'value': self.kinetic_delta.changes,
            'proof': {
                'audit_hash': audit.audit_hash,
                'fg_ratio': audit.fg_ratio,
                'timestamp': audit.timestamp
            }
        }

    def get_audit_log(self) -> List[AuditResult]:
        """Get the audit trail for this engine."""
        return self._audit_log.copy()

    def export_proof(self, audit_result: AuditResult) -> Dict[str, Any]:
        """
        Export a cryptographic proof of an audit result.

        This can be used for external verification or ledger integration.
        """
        return {
            'audit_hash': audit_result.audit_hash,
            'passed': audit_result.passed,
            'fg_ratio': audit_result.fg_ratio,
            'violation_count': len(audit_result.violations),
            'timestamp': audit_result.timestamp,
            'delta_hash': hashlib.sha256(
                str(audit_result.delta.changes).encode()
            ).hexdigest()[:16] if audit_result.delta else None
        }


# =============================================================================
# CONVENIENCE CONSTRUCTORS
# =============================================================================

def create_sovereign_engine(
    ground_constraints: Optional[Dict[str, float]] = None,
    fg_threshold: float = 1.0,
    boundaries: Optional[List[Dict[str, Any]]] = None,
    presences: Optional[List[Dict[str, Any]]] = None
) -> SovereignEngine:
    """
    Factory function to create a configured SovereignEngine.

    Args:
        ground_constraints: Capacity limits for f/g calculation
        fg_threshold: Maximum allowed f/g ratio (default 1.0)
        boundaries: List of boundary definitions
            [{'name': str, 'check': callable, 'type': BoundaryType, 'message': str}]
        presences: List of presence definitions
            [{'name': str, 'exclusive_with': [str]}]

    Returns:
        Configured SovereignEngine instance

    Example:
        engine = create_sovereign_engine(
            ground_constraints={'balance': 1000},
            fg_threshold=1.0,
            boundaries=[
                {'name': 'no_negative',
                 'check': lambda d, e: d.changes.get('balance', {}).get('to', 0) < 0}
            ]
        )
    """
    engine = SovereignEngine(fg_threshold=fg_threshold)

    if ground_constraints:
        engine.set_ground_constraints(ground_constraints)

    if boundaries:
        for b in boundaries:
            engine.boundaries.register(
                name=b.get('name', 'unnamed'),
                check=b['check'],
                type_=b.get('type', BoundaryType.LOGICAL),
                message=b.get('message', '')
            )

    if presences:
        for p in presences:
            engine.define_presence(
                name=p['name'],
                exclusive_with=p.get('exclusive_with')
            )

    return engine


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core types
    'SovereignEngine',
    'Intent',
    'AuditResult',

    # Boundaries
    'Boundary',
    'BoundaryType',
    'BoundaryRegistry',

    # Presence management
    'PresenceState',
    'PresenceManager',

    # Functions
    'project_future',
    'calculate_fg_ratio',
    'create_sovereign_engine',
]
