"""
Construct Studio Engine
=======================

The simulation and execution engine that ties everything together.

The engine provides:
- Simulation mode: Test without committing
- Batch operations: Multiple forces in sequence
- Rollback snapshots: Save/restore state
- Analysis: Understand constraint utilization
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List, Callable, Union, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import copy

try:
    from .core import Matter, Floor, Force, Ratio, attempt, ConstructError, OntologicalDeath
    from .ledger import Ledger, LedgerEntry, global_ledger
except ImportError:
    from core import Matter, Floor, Force, Ratio, attempt, ConstructError, OntologicalDeath
    from ledger import Ledger, LedgerEntry, global_ledger


class SimulationMode(Enum):
    """How the engine handles operations."""
    STRICT = "strict"          # Death raises immediately
    SOFT = "soft"              # Death returns False
    ANALYZE = "analyze"        # Just check, don't apply


@dataclass
class SimulationResult:
    """Result of a simulation run."""

    success: bool
    operations: List[Dict[str, Any]]
    deaths: List[Dict[str, Any]]
    final_state: Dict[str, Any]
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def death_count(self) -> int:
        return len(self.deaths)

    @property
    def success_count(self) -> int:
        return len([op for op in self.operations if op.get("success")])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "operations": self.operations,
            "deaths": self.deaths,
            "final_state": self.final_state,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_operations": len(self.operations),
                "successes": self.success_count,
                "deaths": self.death_count,
            }
        }

    def __repr__(self) -> str:
        status = "OK" if self.success else "FAILED"
        return f"SimulationResult({status}, {self.success_count}/{len(self.operations)} ops, {self.death_count} deaths)"


@dataclass
class Snapshot:
    """A snapshot of floor state that can be restored."""

    name: str
    floor_states: Dict[str, Dict[str, float]]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "floor_states": self.floor_states,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        return cls(
            name=data["name"],
            floor_states=data["floor_states"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class ConstructEngine:
    """
    The main simulation and execution engine.

    Usage:
        engine = ConstructEngine()

        # Add floors
        engine.register_floor(CorporateCard)
        engine.register_floor(DeploymentQuota)

        # Run simulation
        result = engine.simulate([
            ("spend", {"amount": 1000}),
            ("spend", {"amount": 2000}),
            ("spend", {"amount": 3000}),  # This would die
        ])

        # Analyze
        engine.analyze()
    """

    def __init__(
        self,
        name: str = "default",
        mode: SimulationMode = SimulationMode.SOFT,
        ledger: Optional[Ledger] = None,
    ):
        self.name = name
        self.mode = mode
        self.ledger = ledger or Ledger(f"engine_{name}")
        self._floors: Dict[str, Floor] = {}
        self._snapshots: List[Snapshot] = []
        self._operations: List[Callable] = []

    def register_floor(self, floor_class: Type[Floor], name: Optional[str] = None) -> Floor:
        """Register a floor with the engine."""
        instance = floor_class()
        key = name or floor_class.__name__
        self._floors[key] = instance
        return instance

    def get_floor(self, name: str) -> Optional[Floor]:
        """Get a registered floor by name."""
        return self._floors.get(name)

    def reset_all(self) -> None:
        """Reset all floors to initial state."""
        for floor in self._floors.values():
            floor._initialize_capacities()

    # ========================================================================
    # SNAPSHOTS
    # ========================================================================

    def snapshot(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Snapshot:
        """Take a snapshot of all floor states."""
        states = {}
        for floor_name, floor in self._floors.items():
            states[floor_name] = {}
            for cap_name, capacity in floor._capacities.items():
                states[floor_name][cap_name] = {
                    "current": capacity.current.value,
                    "maximum": capacity.maximum.value,
                }

        snap = Snapshot(
            name=name,
            floor_states=states,
            metadata=metadata or {},
        )
        self._snapshots.append(snap)
        return snap

    def restore(self, snapshot: Union[Snapshot, str]) -> None:
        """Restore state from a snapshot."""
        if isinstance(snapshot, str):
            # Find by name
            matches = [s for s in self._snapshots if s.name == snapshot]
            if not matches:
                raise ValueError(f"Snapshot not found: {snapshot}")
            snapshot = matches[-1]

        for floor_name, caps in snapshot.floor_states.items():
            floor = self._floors.get(floor_name)
            if floor:
                for cap_name, values in caps.items():
                    if cap_name in floor._capacities:
                        floor._capacities[cap_name].current = Matter(
                            values["current"],
                            floor._capacities[cap_name].current.unit
                        )

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots."""
        return [s.to_dict() for s in self._snapshots]

    # ========================================================================
    # SIMULATION
    # ========================================================================

    def simulate(
        self,
        operations: List[tuple],
        mode: Optional[SimulationMode] = None
    ) -> SimulationResult:
        """
        Simulate a series of operations.

        Args:
            operations: List of (operation_name, kwargs) tuples
            mode: Override the engine mode for this simulation

        Returns:
            SimulationResult with all outcomes
        """
        mode = mode or self.mode
        start = datetime.utcnow()

        # Take snapshot before simulation
        before_snap = self.snapshot(f"before_sim_{start.timestamp()}")

        results = []
        deaths = []
        all_success = True

        for op_name, kwargs in operations:
            op_result = self._execute_operation(op_name, kwargs, mode)
            results.append(op_result)

            if not op_result.get("success", False):
                all_success = False
                if op_result.get("death"):
                    deaths.append(op_result)

        end = datetime.utcnow()
        duration_ms = (end - start).total_seconds() * 1000

        # Capture final state
        final_state = self._capture_state()

        # If in analyze mode, restore original state
        if mode == SimulationMode.ANALYZE:
            self.restore(before_snap)

        return SimulationResult(
            success=all_success,
            operations=results,
            deaths=deaths,
            final_state=final_state,
            duration_ms=duration_ms,
        )

    def _execute_operation(
        self,
        op_name: str,
        kwargs: Dict[str, Any],
        mode: SimulationMode
    ) -> Dict[str, Any]:
        """Execute a single operation."""
        result = {
            "operation": op_name,
            "kwargs": kwargs,
            "success": False,
            "death": False,
        }

        try:
            if op_name == "force":
                # Direct force application
                matter = Matter(kwargs["value"], kwargs["unit"], kwargs.get("label"))
                floor_name = kwargs.get("floor")
                floor = self._floors.get(floor_name) if floor_name else list(self._floors.values())[0]
                cap_name = kwargs.get("capacity")
                capacity = floor._capacities.get(cap_name) if cap_name else list(floor._capacities.values())[0]

                if mode == SimulationMode.ANALYZE:
                    # Just check, don't apply
                    fits = matter.value <= capacity.remaining.value
                    result["would_fit"] = fits
                    result["success"] = fits
                else:
                    with attempt():
                        force_result = matter >> capacity
                        result["success"] = force_result.success
                        result["ratio"] = {
                            "value": force_result.ratio.value,
                            "fits": force_result.ratio.fits,
                        }
                        if not force_result.success:
                            result["death"] = True
                            result["overflow"] = force_result.ratio.overflow

            elif op_name == "reset":
                floor_name = kwargs.get("floor")
                if floor_name and floor_name in self._floors:
                    self._floors[floor_name]._initialize_capacities()
                else:
                    self.reset_all()
                result["success"] = True

            else:
                result["error"] = f"Unknown operation: {op_name}"

        except OntologicalDeath as e:
            result["death"] = True
            result["error"] = str(e)
            if mode == SimulationMode.STRICT:
                raise

        except Exception as e:
            result["error"] = str(e)

        return result

    def _capture_state(self) -> Dict[str, Any]:
        """Capture current state of all floors."""
        state = {}
        for name, floor in self._floors.items():
            state[name] = {}
            for cap_name, capacity in floor._capacities.items():
                state[name][cap_name] = {
                    "current": capacity.current.value,
                    "maximum": capacity.maximum.value,
                    "remaining": capacity.remaining.value,
                    "utilization": capacity.utilization,
                }
        return state

    # ========================================================================
    # ANALYSIS
    # ========================================================================

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze current state of all floors.

        Returns comprehensive utilization and headroom analysis.
        """
        analysis = {
            "floors": {},
            "summary": {
                "total_capacities": 0,
                "fully_utilized": 0,
                "partially_utilized": 0,
                "empty": 0,
            },
            "warnings": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        for name, floor in self._floors.items():
            floor_analysis = {
                "capacities": {},
                "total_utilization": 0,
            }

            cap_count = len(floor._capacities)
            util_sum = 0

            for cap_name, capacity in floor._capacities.items():
                util = capacity.utilization
                util_sum += util

                floor_analysis["capacities"][cap_name] = {
                    "current": capacity.current.value,
                    "maximum": capacity.maximum.value,
                    "remaining": capacity.remaining.value,
                    "utilization": util,
                    "unit": capacity.current.unit,
                    "status": "full" if util >= 1.0 else "partial" if util > 0 else "empty",
                }

                analysis["summary"]["total_capacities"] += 1
                if util >= 1.0:
                    analysis["summary"]["fully_utilized"] += 1
                    analysis["warnings"].append(f"{name}.{cap_name} is at capacity")
                elif util > 0:
                    analysis["summary"]["partially_utilized"] += 1
                else:
                    analysis["summary"]["empty"] += 1

                # Warn if near capacity
                if 0.8 <= util < 1.0:
                    analysis["warnings"].append(
                        f"{name}.{cap_name} is at {util:.0%} utilization"
                    )

            floor_analysis["total_utilization"] = util_sum / cap_count if cap_count else 0
            analysis["floors"][name] = floor_analysis

        return analysis

    def find_headroom(self) -> Dict[str, Any]:
        """
        Find available headroom across all floors.

        Returns what can still fit in each capacity.
        """
        headroom = {}

        for name, floor in self._floors.items():
            headroom[name] = {}
            for cap_name, capacity in floor._capacities.items():
                remaining = capacity.remaining.value
                headroom[name][cap_name] = {
                    "remaining": remaining,
                    "unit": capacity.current.unit,
                    "percent_available": (1 - capacity.utilization) * 100,
                }

        return headroom

    def what_if(
        self,
        matter_value: float,
        matter_unit: str,
        floor_name: Optional[str] = None,
        capacity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        What-if analysis: would this matter fit?

        Does not modify state - pure analysis.
        """
        results = {}

        floors_to_check = [self._floors[floor_name]] if floor_name else self._floors.values()

        for floor in floors_to_check:
            floor_key = floor.name

            for cap_name, capacity in floor._capacities.items():
                if capacity_name and cap_name != capacity_name:
                    continue

                if capacity.current.unit != matter_unit:
                    continue

                remaining = capacity.remaining.value
                fits = matter_value <= remaining

                results[f"{floor_key}.{cap_name}"] = {
                    "would_fit": fits,
                    "matter": matter_value,
                    "remaining": remaining,
                    "unit": matter_unit,
                    "overflow": max(0, matter_value - remaining),
                    "utilization_after": (capacity.current.value + matter_value) / capacity.maximum.value if fits else None,
                }

        return results

    # ========================================================================
    # DISPLAY
    # ========================================================================

    def print_status(self) -> None:
        """Print current status of all floors."""
        print(f"\n{'='*60}")
        print(f"  CONSTRUCT ENGINE: {self.name}")
        print(f"  Mode: {self.mode.value}")
        print(f"{'='*60}\n")

        for name, floor in self._floors.items():
            print(f"  Floor: {name}")
            print(f"  {'-'*40}")

            for cap_name, capacity in floor._capacities.items():
                util = capacity.utilization
                bar_width = 30
                filled = int(bar_width * util)
                bar = "█" * filled + "░" * (bar_width - filled)

                print(f"    {cap_name}:")
                print(f"      [{bar}] {util:.1%}")
                print(f"      {capacity.current.value:.1f}/{capacity.maximum.value:.1f} {capacity.current.unit}")
                print()

        print(f"{'='*60}\n")

    def __repr__(self) -> str:
        return f"ConstructEngine({self.name}, {len(self._floors)} floors, mode={self.mode.value})"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_engine(
    name: str = "default",
    floors: Optional[List[Type[Floor]]] = None,
    mode: SimulationMode = SimulationMode.SOFT
) -> ConstructEngine:
    """Create an engine with floors pre-registered."""
    engine = ConstructEngine(name, mode)

    if floors:
        for floor_class in floors:
            engine.register_floor(floor_class)

    return engine


def quick_simulate(
    floor_class: Type[Floor],
    forces: List[tuple]  # List of (value, unit) or (value, unit, capacity_name)
) -> SimulationResult:
    """
    Quick simulation helper.

    Usage:
        result = quick_simulate(CorporateCard, [
            (1000, "USD"),
            (2000, "USD"),
            (3000, "USD"),  # This would die
        ])
    """
    engine = ConstructEngine("quick_sim", SimulationMode.SOFT)
    engine.register_floor(floor_class)

    operations = []
    for force in forces:
        if len(force) == 2:
            value, unit = force
            operations.append(("force", {"value": value, "unit": unit}))
        else:
            value, unit, cap_name = force
            operations.append(("force", {"value": value, "unit": unit, "capacity": cap_name}))

    return engine.simulate(operations)
