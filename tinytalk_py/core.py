"""
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk Core - The Lexicon and Scaffolds
═══════════════════════════════════════════════════════════════════════════════

HISTORICAL LINEAGE:

TinyTalk is a constraint-first language inspired by Smalltalk (Kay, 1972) and
ThingLab (Borning, Xerox PARC, 1979). Like ThingLab, TinyTalk implements
multi-way dataflow constraints where relationships are bidirectional.

The Blueprint/Law/Forge architecture follows the CLP(X) paradigm (Jaffar &
Lassez, 1987), where:
- Blueprint = Class with constraint-governed state
- Law = Declarative constraint (what must be true)
- Forge = Guarded mutation (what can change)

The @forge decorator implements atomic state transitions with rollback—the same
save/execute/verify/commit cycle that Sussman's Propagator Networks (1980) use.

Key Insight from Alan Kay:
  "Smalltalk is not about objects, it's about messaging."
  TinyTalk is not about objects, it's about constraints.

See: docs/NEWTON_CLP_SYSTEM_DEFINITION.md for full historical context.
═══════════════════════════════════════════════════════════════════════════════
"""

from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Generic, List, Dict
from dataclasses import dataclass, field as dataclass_field
from functools import wraps
import copy


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK I: THE LEXICON
# ═══════════════════════════════════════════════════════════════════════════════

class LawResult(Enum):
    """The possible outcomes of evaluating a law."""
    ALLOWED = "allowed"    # State is permitted
    FIN = "fin"           # Closed, but can be reopened
    FINFR = "finfr"       # Finality - ontological death


# Sentinel values for the lexicon
class _Finfr:
    """Finality. Ontological death. The state cannot exist."""
    def __repr__(self):
        return "finfr"

    def __bool__(self):
        return True


class _Fin:
    """Closure. A stopping point that can be reopened."""
    def __repr__(self):
        return "fin"

    def __bool__(self):
        return True


FINFR = _Finfr()
FIN = _Fin()
finfr = FINFR
fin = FIN


class LawViolation(Exception):
    """Raised when a law's finfr condition is triggered."""

    def __init__(self, law_name: str, message: str = ""):
        self.law_name = law_name
        self.message = message or f"Law '{law_name}' prevents this state (finfr)"
        super().__init__(self.message)


class FinClosure(Exception):
    """Raised when a fin condition is triggered (can be caught and handled)."""

    def __init__(self, law_name: str, message: str = ""):
        self.law_name = law_name
        self.message = message or f"Law '{law_name}' closed this path (fin)"
        super().__init__(self.message)


def when(condition: bool, result: Any = None) -> bool:
    """
    Declares a fact. The present state.

    Usage:
        when(liabilities > assets, finfr)  # Triggers finfr if condition is true
        when(balance > 0)                  # Returns boolean
    """
    if result is FINFR and condition:
        raise LawViolation("inline", "finfr triggered by when() condition")
    if result is FIN and condition:
        raise FinClosure("inline", "fin triggered by when() condition")
    return condition


class RatioResult:
    """
    Result of a ratio calculation for f/g dimensional analysis.

    This encapsulates the ratio between what you're trying to do (f)
    and what reality allows (g). When the ratio is undefined (g=0)
    or exceeds bounds, finfr is triggered.
    """

    def __init__(self, f: float, g: float, epsilon: float = 1e-9):
        self.f = f
        self.g = g
        self.epsilon = epsilon
        self._undefined = abs(g) < epsilon

    @property
    def undefined(self) -> bool:
        """True if the ratio is undefined (g ≈ 0)."""
        return self._undefined

    @property
    def value(self) -> float:
        """The ratio value (f/g). Returns infinity if undefined."""
        if self._undefined:
            return float('inf') if self.f >= 0 else float('-inf')
        return self.f / self.g

    def __lt__(self, other: float) -> bool:
        if self._undefined:
            return False  # Undefined ratio never satisfies < comparison
        return self.value < other

    def __le__(self, other: float) -> bool:
        if self._undefined:
            return False  # Undefined ratio never satisfies <= comparison
        return self.value <= other

    def __gt__(self, other: float) -> bool:
        if self._undefined:
            return True  # Undefined ratio always exceeds any finite threshold
        return self.value > other

    def __ge__(self, other: float) -> bool:
        if self._undefined:
            return True  # Undefined ratio always exceeds any finite threshold
        return self.value >= other

    def __eq__(self, other: float) -> bool:
        if self._undefined:
            return False  # Undefined ratio is never equal to a finite value
        return abs(self.value - other) < self.epsilon

    def __repr__(self) -> str:
        if self._undefined:
            return f"RatioResult(f={self.f}, g={self.g}, undefined=True)"
        return f"RatioResult(f={self.f}, g={self.g}, value={self.value:.4f})"


def ratio(f: float, g: float, epsilon: float = 1e-9) -> RatioResult:
    """
    Calculate the f/g ratio for dimensional analysis.

    This is Newton's core insight: finfr = f/g where:
    - f = forge/fact/function (what you're trying to do)
    - g = ground/goal/governance (what reality allows)

    When the ratio is undefined (g=0) or exceeds bounds,
    the operation cannot phase into existence.

    Usage in laws:
        @law
        def no_overdraft(self):
            # withdrawal/balance must be <= 1.0
            when(ratio(self.withdrawal, self.balance) > 1.0, finfr)

        @law
        def leverage_limit(self):
            # debt/equity must be <= 3.0
            when(ratio(self.debt, self.equity) > 3.0, finfr)

        @law
        def seizure_safety(self):
            # flicker_rate/safe_threshold must be < 1.0
            when(ratio(self.flicker_rate, self.safe_threshold) >= 1.0, finfr)

    Args:
        f: The numerator (forge/fact/function)
        g: The denominator (ground/goal/governance)
        epsilon: Tolerance for zero comparison (default: 1e-9)

    Returns:
        RatioResult that can be compared with <, <=, >, >=, ==
    """
    return RatioResult(float(f), float(g), epsilon)


def finfr_if_undefined(f: float, g: float, epsilon: float = 1e-9) -> None:
    """
    Trigger finfr if the ratio f/g is undefined (g ≈ 0).

    This is the ontological death check - if the denominator is zero,
    the ratio cannot exist and the operation must be forbidden.

    Usage:
        @law
        def valid_balance(self):
            finfr_if_undefined(self.withdrawal, self.balance)

    Args:
        f: The numerator
        g: The denominator
        epsilon: Tolerance for zero comparison
    """
    if abs(float(g)) < epsilon:
        raise LawViolation("ratio_undefined", f"finfr: ratio is undefined (denominator ≈ 0)")


# ═══════════════════════════════════════════════════════════════════════════════
# BOOK II: THE SCAFFOLDS - Fields and Forges
# ═══════════════════════════════════════════════════════════════════════════════

T = TypeVar('T')


@dataclass
class Field(Generic[T]):
    """
    A field declaration for a Blueprint.

    Fields hold Matter - typed values with units.
    """
    type_: type
    default: Optional[T] = None
    name: str = ""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None) -> T:
        if obj is None:
            return self
        return getattr(obj, f"_field_{self.name}", self.default)

    def __set__(self, obj, value: T):
        # Type checking
        if value is not None and self.type_ is not None:
            if hasattr(self.type_, '__origin__'):  # Generic type
                pass  # Skip complex type checking for now
            elif not isinstance(value, self.type_):
                # Try to convert
                try:
                    value = self.type_(value)
                except (TypeError, ValueError):
                    raise TypeError(
                        f"Field '{self.name}' expects {self.type_.__name__}, "
                        f"got {type(value).__name__}"
                    )
        setattr(obj, f"_field_{self.name}", value)


def field(type_: type = Any, default: Any = None) -> Field:
    """
    Declare a field in a Blueprint.

    Usage:
        class MyBlueprint(Blueprint):
            balance = field(Money, default=Money(0))
            name = field(str, default="")
    """
    return Field(type_=type_, default=default)


@dataclass
class Law:
    """
    A governance rule that defines forbidden states.

    Laws are evaluated before any forge executes.
    If a law's condition is True and result is finfr, the operation is blocked.
    """
    name: str
    condition: Callable[['Blueprint'], bool]
    result: LawResult = LawResult.FINFR
    message: str = ""

    def evaluate(self, blueprint: 'Blueprint') -> tuple[bool, LawResult]:
        """Evaluate the law against current blueprint state."""
        try:
            triggered = self.condition(blueprint)
            if triggered:
                return True, self.result
            return False, LawResult.ALLOWED
        except Exception as e:
            # Law evaluation errors are treated as not triggered
            return False, LawResult.ALLOWED


def law(func: Callable) -> Callable:
    """
    Decorator to mark a method as a Law.

    Usage:
        @law
        def insolvency(self):
            when(self.liabilities > self.assets, finfr)
    """
    func._is_law = True
    return func


def forge(func: Callable) -> Callable:
    """
    Decorator to mark a method as a Forge.

    Forges are the executive layer - they mutate state.
    Before a forge runs, all laws are checked against the projected state.

    Usage:
        @forge
        def execute_trade(self, amount: Money):
            self.liabilities += amount
            return "cleared"
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Save current state for rollback
        saved_state = self._save_state()

        try:
            # Execute the forge
            result = func(self, *args, **kwargs)

            # Check all laws against new state
            for law_obj in self._laws:
                triggered, law_result = law_obj.evaluate(self)
                if triggered and law_result == LawResult.FINFR:
                    # Rollback and raise
                    self._restore_state(saved_state)
                    raise LawViolation(
                        law_obj.name,
                        law_obj.message or f"Law '{law_obj.name}' prevents this state"
                    )
                elif triggered and law_result == LawResult.FIN:
                    # Rollback but allow handling
                    self._restore_state(saved_state)
                    raise FinClosure(law_obj.name, law_obj.message)

            return result

        except (LawViolation, FinClosure):
            # Re-raise law violations
            raise
        except Exception as e:
            # Rollback on any error
            self._restore_state(saved_state)
            raise

    wrapper._is_forge = True
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════════
# THE BLUEPRINT - Base class for all tinyTalk objects
# ═══════════════════════════════════════════════════════════════════════════════

class BlueprintMeta(type):
    """Metaclass that collects laws and forges from class definition."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Collect laws
        cls._law_methods = []
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and getattr(attr_value, '_is_law', False):
                cls._law_methods.append(attr_name)

        return cls


class Blueprint(metaclass=BlueprintMeta):
    """
    Base class for all tinyTalk blueprints.

    A Blueprint defines:
    - Fields (Layer 1: Executive state)
    - Laws (Layer 0: Governance constraints)
    - Forges (Layer 1: Executive mutations)

    Usage:
        class RiskGovernor(Blueprint):
            assets = field(float, default=1000.0)
            liabilities = field(float, default=0.0)

            @law
            def insolvency(self):
                when(self.liabilities > self.assets, finfr)

            @forge
            def execute_trade(self, amount: float):
                self.liabilities += amount
                return "cleared"
    """

    def __init__(self, **kwargs):
        # Initialize fields with defaults
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, Field):
                default = kwargs.get(attr_name, attr.default)
                setattr(self, attr_name, default)

        # Build law objects from law methods
        self._laws: List[Law] = []
        for law_name in self.__class__._law_methods:
            law_method = getattr(self, law_name)

            def make_condition(method):
                def condition(bp):
                    try:
                        method()
                        return False  # No exception = law not triggered
                    except LawViolation:
                        return True
                    except FinClosure:
                        return True
                return condition

            self._laws.append(Law(
                name=law_name,
                condition=make_condition(law_method),
                result=LawResult.FINFR
            ))

    def _save_state(self) -> Dict[str, Any]:
        """Save current field values for potential rollback."""
        state = {}
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, Field):
                value = getattr(self, attr_name)
                # Deep copy to handle mutable objects
                state[attr_name] = copy.deepcopy(value)
        return state

    def _restore_state(self, state: Dict[str, Any]):
        """Restore field values from saved state."""
        for attr_name, value in state.items():
            setattr(self, attr_name, value)

    def _get_state(self) -> Dict[str, Any]:
        """Get current state as dictionary."""
        state = {}
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if isinstance(attr, Field):
                state[attr_name] = getattr(self, attr_name)
        return state

    def _check_laws(self) -> tuple[bool, Optional[Law]]:
        """Check all laws. Returns (blocked, triggered_law)."""
        for law_obj in self._laws:
            triggered, result = law_obj.evaluate(self)
            if triggered and result == LawResult.FINFR:
                return True, law_obj
        return False, None

    def __repr__(self):
        state = self._get_state()
        fields_str = ", ".join(f"{k}={v}" for k, v in state.items())
        return f"{self.__class__.__name__}({fields_str})"
