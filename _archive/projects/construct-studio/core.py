"""
Construct Studio Core Kernel
============================

The physics engine for governance. Where constraints become geometry.

In CAD, intersecting geometry shows a collision.
In Construct, violating a constraint shows Ontological Death.

This is not exception handling. This is reality pruning.
"""

from __future__ import annotations
from typing import Any, Optional, Callable, TypeVar, Generic, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from contextlib import contextmanager
from functools import wraps
import threading
import uuid

# Thread-local storage for the current construct context
_context = threading.local()


class OntologicalDeath(Exception):
    """
    The illegal state never existed.

    This is not an error to be caught and handled.
    This is ontological pruning - the branch of reality
    where this constraint was violated simply does not exist.

    In CAD terms: the geometry intersected. The design is invalid.
    There is no "fix" - there is only "redesign".
    """

    def __init__(
        self,
        message: str,
        matter: Optional['Matter'] = None,
        floor: Optional['Floor'] = None,
        ratio: Optional['Ratio'] = None,
    ):
        self.message = message
        self.matter = matter
        self.floor = floor
        self.ratio = ratio
        self.timestamp = datetime.utcnow()
        self.death_id = str(uuid.uuid4())[:8]
        super().__init__(self._format_death())

    def _format_death(self) -> str:
        lines = [
            f"",
            f"  ONTOLOGICAL DEATH [{self.death_id}]",
            f"  ═══════════════════════════════════════",
            f"  {self.message}",
            f"  ",
        ]
        if self.matter:
            lines.append(f"  Matter: {self.matter}")
        if self.floor:
            lines.append(f"  Floor:  {self.floor}")
        if self.ratio:
            lines.append(f"  Ratio:  {self.ratio}")
        lines.extend([
            f"  ",
            f"  This state cannot exist.",
            f"  ═══════════════════════════════════════",
            f"",
        ])
        return "\n".join(lines)


# Alias for API consistency
ConstructError = OntologicalDeath


class MatterState(Enum):
    """The existential state of Matter."""
    POTENTIAL = "potential"    # Not yet applied
    APPLIED = "applied"        # Successfully applied to Floor
    DEAD = "dead"              # Ontologically pruned


@dataclass
class Matter:
    """
    A typed value with units. The "solid" in your design space.

    Matter has magnitude, unit, and existential state.
    It can be applied to Floors via the >> (force) operator.

    Examples:
        cost = Matter(1500, "USD")
        cpu = Matter(32, "vCPU")
        risk = Matter(0.15, "probability")
    """

    value: float
    unit: str
    label: Optional[str] = None
    state: MatterState = field(default=MatterState.POTENTIAL)
    _id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        if isinstance(self.value, str):
            self.value = float(self.value)

    def __repr__(self) -> str:
        label_str = f" ({self.label})" if self.label else ""
        return f"Matter({self.value} {self.unit}{label_str})"

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    def __rshift__(self, target: Union['Floor', 'Matter', 'Capacity']) -> 'ForceResult':
        """
        The Force operator (>>).

        Apply this Matter to a target (Floor or Capacity).
        This is not assignment. This is physics.

        The force either:
        - Succeeds: Matter is absorbed, capacity reduced
        - Fails: Ontological death - this timeline doesn't exist
        """
        return Force.apply(self, target)

    def __add__(self, other: 'Matter') -> 'Matter':
        if not isinstance(other, Matter):
            return NotImplemented
        if self.unit != other.unit:
            raise ConstructError(
                f"Cannot add incompatible units: {self.unit} + {other.unit}",
                matter=self
            )
        return Matter(self.value + other.value, self.unit)

    def __sub__(self, other: 'Matter') -> 'Matter':
        if not isinstance(other, Matter):
            return NotImplemented
        if self.unit != other.unit:
            raise ConstructError(
                f"Cannot subtract incompatible units: {self.unit} - {other.unit}",
                matter=self
            )
        return Matter(self.value - other.value, self.unit)

    def __mul__(self, scalar: float) -> 'Matter':
        return Matter(self.value * scalar, self.unit, self.label)

    def __rmul__(self, scalar: float) -> 'Matter':
        return self.__mul__(scalar)

    def __truediv__(self, other: Union[float, 'Matter']) -> Union['Matter', float]:
        if isinstance(other, Matter):
            if self.unit != other.unit:
                # Return dimensionless ratio
                return self.value / other.value
            return self.value / other.value
        return Matter(self.value / other, self.unit, self.label)

    def __lt__(self, other: 'Matter') -> bool:
        self._check_compatible(other)
        return self.value < other.value

    def __le__(self, other: 'Matter') -> bool:
        self._check_compatible(other)
        return self.value <= other.value

    def __gt__(self, other: 'Matter') -> bool:
        self._check_compatible(other)
        return self.value > other.value

    def __ge__(self, other: 'Matter') -> bool:
        self._check_compatible(other)
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matter):
            return NotImplemented
        return self.value == other.value and self.unit == other.unit

    def _check_compatible(self, other: 'Matter') -> None:
        if not isinstance(other, Matter):
            raise ConstructError(f"Cannot compare Matter with {type(other)}", matter=self)
        if self.unit != other.unit:
            raise ConstructError(
                f"Cannot compare incompatible units: {self.unit} vs {other.unit}",
                matter=self
            )

    def copy(self) -> 'Matter':
        return Matter(self.value, self.unit, self.label)


@dataclass
class Capacity:
    """
    A container's remaining capacity. What a Floor can still accept.

    Capacity is Matter that can receive Force.
    When Force is applied, capacity is consumed.
    """

    current: Matter
    maximum: Matter
    name: str = "capacity"

    def __post_init__(self):
        if self.current.unit != self.maximum.unit:
            raise ConstructError(
                f"Capacity units must match: {self.current.unit} vs {self.maximum.unit}"
            )

    @property
    def remaining(self) -> Matter:
        return Matter(
            self.maximum.value - self.current.value,
            self.current.unit,
            f"{self.name}_remaining"
        )

    @property
    def utilization(self) -> float:
        if self.maximum.value == 0:
            return 1.0 if self.current.value > 0 else 0.0
        return self.current.value / self.maximum.value

    def can_accept(self, matter: Matter) -> bool:
        """Check if this capacity can accept the given matter."""
        if matter.unit != self.current.unit:
            return False
        return self.current.value + matter.value <= self.maximum.value

    def accept(self, matter: Matter) -> None:
        """Accept matter into this capacity. Mutates state."""
        if not self.can_accept(matter):
            raise ConstructError(
                f"Capacity overflow: {self.current} + {matter} > {self.maximum}",
                matter=matter
            )
        self.current = Matter(
            self.current.value + matter.value,
            self.current.unit
        )

    def __repr__(self) -> str:
        return f"Capacity({self.current}/{self.maximum}, {self.utilization:.1%})"


class FloorMeta(type):
    """Metaclass for Floor that tracks capacity definitions."""

    def __new__(mcs, name, bases, namespace):
        # Collect capacity definitions
        capacities = {}
        for key, value in namespace.items():
            if isinstance(value, Matter):
                capacities[key] = Capacity(
                    current=Matter(0, value.unit),
                    maximum=value,
                    name=key
                )

        namespace['_capacity_definitions'] = capacities
        return super().__new__(mcs, name, bases, namespace)


class Floor(metaclass=FloorMeta):
    """
    A constraint container. The boundary of valid design space.

    Floors define what can exist. Matter applied to a Floor
    must fit within its capacities, or it triggers Ontological Death.

    In CAD terms: Floor is the bounding box.
    In physics terms: Floor is the container.
    In governance terms: Floor is the budget.

    Example:
        class CorporateCard(Floor):
            budget = Matter(5000, "USD")

        # Now you can apply force to CorporateCard.budget
        expense = Matter(1500, "USD")
        expense >> CorporateCard.budget  # OK, fits

        big_expense = Matter(6000, "USD")
        big_expense >> CorporateCard.budget  # Ontological Death
    """

    _instances: dict[str, 'Floor'] = {}
    _capacity_definitions: dict[str, Capacity] = {}

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self._capacities: dict[str, Capacity] = {}
        self._initialize_capacities()
        Floor._instances[self.name] = self

    def _initialize_capacities(self) -> None:
        """Initialize instance capacities from class definitions."""
        for name, cap_def in self._capacity_definitions.items():
            self._capacities[name] = Capacity(
                current=Matter(0, cap_def.maximum.unit),
                maximum=cap_def.maximum.copy(),
                name=name
            )

    def __class_getitem__(cls, key: str) -> Capacity:
        """Allow Floor[capacity_name] syntax."""
        instance = cls._instances.get(cls.__name__)
        if instance is None:
            instance = cls()
        return instance._capacities.get(key)

    @classmethod
    def get_capacity(cls, name: str) -> Optional[Capacity]:
        """Get a capacity by name."""
        instance = cls._instances.get(cls.__name__)
        if instance is None:
            instance = cls()
        return instance._capacities.get(name)

    @classmethod
    def reset(cls) -> None:
        """Reset all capacities to zero. Fresh start."""
        instance = cls._instances.get(cls.__name__)
        if instance:
            instance._initialize_capacities()

    def __repr__(self) -> str:
        caps = ", ".join(f"{k}={v}" for k, v in self._capacities.items())
        return f"{self.__class__.__name__}({caps})"


@dataclass
class Ratio:
    """
    The collision test result.

    Ratio tells you whether the Force succeeded or failed,
    and by how much. It's the geometric intersection test.

    ratio.fits = True  → Force succeeded, state updated
    ratio.fits = False → Ontological Death occurred
    """

    numerator: float      # What was attempted
    denominator: float    # What was available
    unit: str
    fits: bool
    overflow: float = 0.0  # How much didn't fit

    @property
    def value(self) -> float:
        if self.denominator == 0:
            return float('inf') if self.numerator > 0 else 0
        return self.numerator / self.denominator

    @property
    def percentage(self) -> float:
        return self.value * 100

    @property
    def remaining_after(self) -> float:
        """What would remain after this force."""
        return self.denominator - self.numerator

    def __repr__(self) -> str:
        status = "FITS" if self.fits else "COLLISION"
        return f"Ratio({self.numerator}/{self.denominator} {self.unit} = {self.percentage:.1f}% [{status}])"

    def __bool__(self) -> bool:
        return self.fits


@dataclass
class ForceResult:
    """The result of applying Force. Contains the Ratio and outcome."""

    matter: Matter
    target: Union[Floor, Capacity]
    ratio: Ratio
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __bool__(self) -> bool:
        return self.success

    def __repr__(self) -> str:
        status = "OK" if self.success else "DEAD"
        return f"ForceResult({self.matter} >> {self.target} = {status})"


class Force:
    """
    The physics of constraint application.

    Force is not assignment. Force is physics.
    When Matter is pushed (>>) toward a Floor/Capacity,
    Force determines if it fits or causes Ontological Death.
    """

    @staticmethod
    def apply(matter: Matter, target: Union[Floor, Capacity, type]) -> ForceResult:
        """
        Apply force: push Matter toward a target.

        This is O(1) - just a comparison and potential mutation.
        """
        try:
            from .ledger import global_ledger
        except ImportError:
            from ledger import global_ledger

        # Resolve target to Capacity
        capacity = Force._resolve_target(target)

        if capacity is None:
            raise ConstructError(
                f"Cannot apply force to {target}: not a valid Floor or Capacity",
                matter=matter
            )

        # Check unit compatibility
        if matter.unit != capacity.current.unit:
            raise ConstructError(
                f"Unit mismatch: {matter.unit} cannot apply to {capacity.current.unit}",
                matter=matter
            )

        # Calculate Ratio
        available = capacity.maximum.value - capacity.current.value
        ratio = Ratio(
            numerator=matter.value,
            denominator=available,
            unit=matter.unit,
            fits=matter.value <= available,
            overflow=max(0, matter.value - available)
        )

        # Get current context for soft failure mode
        context = getattr(_context, 'current', None)

        if ratio.fits:
            # Success: absorb the matter
            capacity.accept(matter)
            matter.state = MatterState.APPLIED
            result = ForceResult(matter, target, ratio, success=True)
            global_ledger.record_success(matter, target, ratio)
            return result
        else:
            # Failure: Ontological Death
            matter.state = MatterState.DEAD
            global_ledger.record_death(matter, target, ratio)

            if context and context.soft_mode:
                # In 'attempt' context - return failure instead of raising
                return ForceResult(matter, target, ratio, success=False)

            raise OntologicalDeath(
                f"Force exceeds capacity: {matter} cannot fit in {available} {matter.unit} remaining",
                matter=matter,
                floor=target if isinstance(target, Floor) else None,
                ratio=ratio
            )

    @staticmethod
    def _resolve_target(target) -> Optional[Capacity]:
        """Resolve a target to a Capacity object."""
        if isinstance(target, Capacity):
            return target

        if isinstance(target, Floor):
            # Return first capacity
            caps = list(target._capacities.values())
            return caps[0] if caps else None

        if isinstance(target, type) and issubclass(target, Floor):
            # Class reference - get or create instance
            instance = Floor._instances.get(target.__name__)
            if instance is None:
                instance = target()
            caps = list(instance._capacities.values())
            return caps[0] if caps else None

        # Check if it's a class attribute that's a Matter (capacity definition)
        if isinstance(target, Matter):
            # This is a raw Matter used as capacity - wrap it
            return Capacity(
                current=Matter(0, target.unit),
                maximum=target,
                name="inline_capacity"
            )

        return None


class ConstructContext:
    """Context for a Construct execution. Tracks state and mode."""

    def __init__(self, floor: Optional[type] = None, soft_mode: bool = False):
        self.floor = floor
        self.soft_mode = soft_mode
        self.results: list[ForceResult] = []
        self.start_time = datetime.utcnow()

    def __enter__(self):
        self._previous = getattr(_context, 'current', None)
        _context.current = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _context.current = self._previous
        return False


@contextmanager
def attempt():
    """
    Soft failure mode for exploratory force application.

    Within an 'attempt' block, Ontological Death returns False
    instead of raising an exception. Use this for simulation.

    Example:
        with attempt():
            result = big_expense >> budget
            if not result:
                print("Would cause death - trying smaller amount")
    """
    ctx = ConstructContext(soft_mode=True)
    with ctx:
        yield ctx


def Construct(floor: Optional[type] = None, strict: bool = True):
    """
    Decorator that creates a Construct-governed function.

    Functions decorated with @Construct operate within
    the physics of the specified Floor.

    Example:
        @Construct(floor=CorporateCard)
        def purchase(item, price):
            cost = Matter(price, "USD")
            cost >> CorporateCard.budget
            return f"Purchased {item}"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = ConstructContext(floor=floor, soft_mode=not strict)
            with ctx:
                try:
                    result = func(*args, **kwargs)
                    return result
                except OntologicalDeath:
                    if strict:
                        raise
                    return None

        wrapper._construct_floor = floor
        wrapper._construct_strict = strict
        return wrapper

    return decorator


# Convenience functions

def matter(value: float, unit: str, label: Optional[str] = None) -> Matter:
    """Create Matter with a fluent API."""
    return Matter(value, unit, label)


def floor(name: str, **capacities: Matter) -> Floor:
    """Create a Floor dynamically with named capacities."""
    # Create a new Floor subclass dynamically
    namespace = {k: v for k, v in capacities.items()}
    FloorClass = FloorMeta(name, (Floor,), namespace)
    return FloorClass()
