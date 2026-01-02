"""
═══════════════════════════════════════════════════════════════════════════════
 tinyTalk Core - The Lexicon and Scaffolds
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
