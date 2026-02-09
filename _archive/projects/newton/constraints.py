"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CONSTRAINTS
The Constraint Definition Language (CDL).

Simple, composable constraints for verified computation.

Usage:
    from newton import check, eq, gt, contains, all_of
    
    # Simple checks
    check(5, gt(0))           # True
    check("hello", contains("ell"))  # True
    
    # Compound constraints
    check(25, all_of(gt(18), lt(65)))  # True
    
    # Dictionary constraints
    check({"age": 25}, {"age": gt(18)})  # True
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class Constraint:
    """
    A constraint that can be checked against a value.
    
    Constraints are composable and can be combined with
    all_of, any_of, and none_of.
    """
    op: str
    value: Any = None
    message: str = ""
    
    def check(self, actual: Any) -> bool:
        """Check if actual value satisfies this constraint."""
        return _evaluate(self.op, actual, self.value)
    
    def __call__(self, actual: Any) -> bool:
        """Allow constraint to be called directly."""
        return self.check(actual)
    
    def __repr__(self) -> str:
        if self.value is not None:
            return f"Constraint({self.op}, {self.value})"
        return f"Constraint({self.op})"
    
    def __and__(self, other: "Constraint") -> "Constraint":
        """Combine with AND: c1 & c2"""
        return all_of(self, other)
    
    def __or__(self, other: "Constraint") -> "Constraint":
        """Combine with OR: c1 | c2"""
        return any_of(self, other)
    
    def __invert__(self) -> "Constraint":
        """Negate: ~c"""
        return Constraint("not", self)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def eq(value: Any) -> Constraint:
    """Equal to value."""
    return Constraint("eq", value, f"must equal {value}")

def ne(value: Any) -> Constraint:
    """Not equal to value."""
    return Constraint("ne", value, f"must not equal {value}")

def lt(value: Any) -> Constraint:
    """Less than value."""
    return Constraint("lt", value, f"must be less than {value}")

def gt(value: Any) -> Constraint:
    """Greater than value."""
    return Constraint("gt", value, f"must be greater than {value}")

def le(value: Any) -> Constraint:
    """Less than or equal to value."""
    return Constraint("le", value, f"must be at most {value}")

def ge(value: Any) -> Constraint:
    """Greater than or equal to value."""
    return Constraint("ge", value, f"must be at least {value}")

def between(low: Any, high: Any) -> Constraint:
    """Value must be between low and high (inclusive)."""
    return Constraint("between", (low, high), f"must be between {low} and {high}")


# ═══════════════════════════════════════════════════════════════════════════════
# STRING CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def contains(substring: str) -> Constraint:
    """String must contain substring."""
    return Constraint("contains", substring, f"must contain '{substring}'")

def starts_with(prefix: str) -> Constraint:
    """String must start with prefix."""
    return Constraint("starts_with", prefix, f"must start with '{prefix}'")

def ends_with(suffix: str) -> Constraint:
    """String must end with suffix."""
    return Constraint("ends_with", suffix, f"must end with '{suffix}'")

def matches(pattern: str) -> Constraint:
    """String must match regex pattern."""
    return Constraint("matches", pattern, f"must match pattern '{pattern}'")

def length(constraint: Constraint) -> Constraint:
    """Check length of string/list."""
    return Constraint("length", constraint, f"length {constraint.message}")


# ═══════════════════════════════════════════════════════════════════════════════
# COLLECTION CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def is_in(collection: List[Any]) -> Constraint:
    """Value must be in collection."""
    return Constraint("in", collection, f"must be one of {collection}")

def not_in(collection: List[Any]) -> Constraint:
    """Value must not be in collection."""
    return Constraint("not_in", collection, f"must not be one of {collection}")

def is_empty() -> Constraint:
    """Collection must be empty."""
    return Constraint("empty", None, "must be empty")

def is_not_empty() -> Constraint:
    """Collection must not be empty."""
    return Constraint("not_empty", None, "must not be empty")


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def is_type(expected_type: type) -> Constraint:
    """Value must be of type."""
    return Constraint("type", expected_type, f"must be of type {expected_type.__name__}")

def is_none() -> Constraint:
    """Value must be None."""
    return Constraint("is_none", None, "must be None")

def is_not_none() -> Constraint:
    """Value must not be None."""
    return Constraint("is_not_none", None, "must not be None")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPORAL CONSTRAINTS  
# ═══════════════════════════════════════════════════════════════════════════════

def within(seconds: float) -> Constraint:
    """Timestamp must be within N seconds of now."""
    return Constraint("within", seconds, f"must be within {seconds} seconds")

def after(timestamp: datetime) -> Constraint:
    """Timestamp must be after given time."""
    return Constraint("after", timestamp, f"must be after {timestamp}")

def before(timestamp: datetime) -> Constraint:
    """Timestamp must be before given time."""
    return Constraint("before", timestamp, f"must be before {timestamp}")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def all_of(*constraints: Constraint) -> Constraint:
    """All constraints must be satisfied (AND)."""
    return Constraint("all", list(constraints), "all conditions must be met")

def any_of(*constraints: Constraint) -> Constraint:
    """At least one constraint must be satisfied (OR)."""
    return Constraint("any", list(constraints), "at least one condition must be met")

def none_of(*constraints: Constraint) -> Constraint:
    """No constraints should be satisfied (NOR)."""
    return Constraint("none", list(constraints), "no conditions should be met")


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

def custom(fn: Callable[[Any], bool], message: str = "custom check") -> Constraint:
    """Create constraint from custom function."""
    return Constraint("custom", fn, message)


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def _evaluate(op: str, actual: Any, expected: Any) -> bool:
    """Evaluate a constraint operation."""
    
    # Comparison
    if op == "eq":
        return actual == expected
    elif op == "ne":
        return actual != expected
    elif op == "lt":
        return actual < expected
    elif op == "gt":
        return actual > expected
    elif op == "le":
        return actual <= expected
    elif op == "ge":
        return actual >= expected
    elif op == "between":
        low, high = expected
        return low <= actual <= high
    
    # String
    elif op == "contains":
        return expected in str(actual)
    elif op == "starts_with":
        return str(actual).startswith(expected)
    elif op == "ends_with":
        return str(actual).endswith(expected)
    elif op == "matches":
        return bool(re.match(expected, str(actual)))
    elif op == "length":
        return expected.check(len(actual))
    
    # Collection
    elif op == "in":
        return actual in expected
    elif op == "not_in":
        return actual not in expected
    elif op == "empty":
        return len(actual) == 0
    elif op == "not_empty":
        return len(actual) > 0
    
    # Type
    elif op == "type":
        return isinstance(actual, expected)
    elif op == "is_none":
        return actual is None
    elif op == "is_not_none":
        return actual is not None
    
    # Temporal
    elif op == "within":
        if isinstance(actual, datetime):
            delta = abs((datetime.now() - actual).total_seconds())
            return delta <= expected
        return False
    elif op == "after":
        return actual > expected
    elif op == "before":
        return actual < expected
    
    # Composite
    elif op == "all":
        return all(c.check(actual) for c in expected)
    elif op == "any":
        return any(c.check(actual) for c in expected)
    elif op == "none":
        return not any(c.check(actual) for c in expected)
    elif op == "not":
        return not expected.check(actual)
    
    # Custom
    elif op == "custom":
        return expected(actual)
    
    else:
        raise ValueError(f"Unknown constraint operator: {op}")


def check_dict(data: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check a dictionary against a dictionary of constraints.
    
    Returns a dict mapping field names to pass/fail status.
    """
    results = {}
    
    for field, constraint in constraints.items():
        if field not in data:
            results[field] = False
            continue
        
        value = data[field]
        
        if isinstance(constraint, Constraint):
            results[field] = constraint.check(value)
        elif isinstance(constraint, dict):
            # Nested object
            results[field] = all(check_dict(value, constraint).values())
        else:
            # Direct value comparison
            results[field] = value == constraint
    
    return results
