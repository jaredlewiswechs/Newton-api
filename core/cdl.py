#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CDL 3.0 - CONSTRAINT DEFINITION LANGUAGE
The instruction set of the Newton Supercomputer.

Every constraint is an instruction.
Every verification is a computation.
The constraint check IS the work.

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import re
import time
import hashlib
from functools import reduce


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAINS - The seven kingdoms of constraint
# ═══════════════════════════════════════════════════════════════════════════════

class Domain(Enum):
    FINANCIAL = "financial"
    COMMUNICATION = "communication"
    HEALTH = "health"
    EPISTEMIC = "epistemic"
    TEMPORAL = "temporal"
    IDENTITY = "identity"
    CUSTOM = "custom"


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATORS - The verbs of constraint
# ═══════════════════════════════════════════════════════════════════════════════

class Operator(Enum):
    # Comparison (CDL 2.0)
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"
    CONTAINS = "contains"
    MATCHES = "matches"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    EMPTY = "empty"

    # Temporal (CDL 3.0)
    WITHIN = "within"      # field within duration of reference
    AFTER = "after"        # field after reference
    BEFORE = "before"      # field before reference

    # Aggregation (CDL 3.0)
    SUM_LT = "sum_lt"      # sum of field < value over window
    SUM_LE = "sum_le"
    SUM_GT = "sum_gt"
    SUM_GE = "sum_ge"
    COUNT_LT = "count_lt"  # count of occurrences < value over window
    COUNT_LE = "count_le"
    COUNT_GT = "count_gt"
    COUNT_GE = "count_ge"
    AVG_LT = "avg_lt"      # average of field < value over window
    AVG_LE = "avg_le"
    AVG_GT = "avg_gt"
    AVG_GE = "avg_ge"


# ═══════════════════════════════════════════════════════════════════════════════
# DURATION PARSER - For temporal constraints
# ═══════════════════════════════════════════════════════════════════════════════

DURATION_PATTERN = re.compile(r'^(\d+)(s|m|h|d|w)$')
DURATION_MULTIPLIERS = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,
}

def parse_duration(duration: str) -> int:
    """Parse duration string to seconds. E.g., '24h' -> 86400"""
    match = DURATION_PATTERN.match(duration.strip().lower())
    if not match:
        raise ValueError(f"Invalid duration format: {duration}. Use format: 24h, 30m, 7d, etc.")
    value, unit = match.groups()
    return int(value) * DURATION_MULTIPLIERS[unit]


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AtomicConstraint:
    """A single, indivisible constraint."""
    domain: Domain
    field: str
    operator: Operator
    value: Any
    message: Optional[str] = None
    action: str = "reject"  # reject, warn, log
    id: Optional[str] = None

    # CDL 3.0 extensions
    window: Optional[str] = None      # For aggregations: "24h", "7d", etc.
    group_by: Optional[str] = None    # For aggregations: field to group by
    reference: Optional[str] = None   # For temporal: reference field

    def __post_init__(self):
        if self.id is None:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        data = f"{self.domain.value}:{self.field}:{self.operator.value}:{self.value}"
        return f"C_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"


@dataclass
class ConditionalConstraint:
    """CDL 3.0: If-then-else branching."""
    condition: 'Constraint'
    then_constraint: 'Constraint'
    else_constraint: Optional['Constraint'] = None
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"COND_{hashlib.sha256(str(id(self)).encode()).hexdigest()[:8].upper()}"


@dataclass
class CompositeConstraint:
    """Logical composition of constraints."""
    logic: str  # "and", "or", "not"
    constraints: List['Constraint']
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"COMP_{hashlib.sha256(str(id(self)).encode()).hexdigest()[:8].upper()}"


# Union type for all constraints
Constraint = Union[AtomicConstraint, ConditionalConstraint, CompositeConstraint]


# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EvaluationResult:
    """Result of constraint evaluation. Binary: pass or fail."""
    passed: bool
    constraint_id: str
    message: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    fingerprint: Optional[str] = None

    def __post_init__(self):
        if self.fingerprint is None:
            data = f"{self.passed}:{self.constraint_id}:{self.timestamp}"
            self.fingerprint = hashlib.sha256(data.encode()).hexdigest()[:16].upper()


# ═══════════════════════════════════════════════════════════════════════════════
# AGGREGATION STATE - For stateful constraints
# ═══════════════════════════════════════════════════════════════════════════════

class AggregationState:
    """
    Maintains state for aggregation constraints.
    Windowed, grouped, append-only.
    """

    def __init__(self):
        # Structure: {group_key: [(timestamp, value), ...]}
        self._data: Dict[str, List[tuple]] = {}

    def append(self, group_key: str, value: float, timestamp: Optional[int] = None):
        """Append a value to the aggregation state."""
        ts = timestamp or int(time.time())
        if group_key not in self._data:
            self._data[group_key] = []
        self._data[group_key].append((ts, value))

    def get_window(self, group_key: str, window_seconds: int) -> List[float]:
        """Get values within the time window."""
        if group_key not in self._data:
            return []

        now = int(time.time())
        cutoff = now - window_seconds
        return [v for ts, v in self._data[group_key] if ts >= cutoff]

    def sum(self, group_key: str, window_seconds: int) -> float:
        """Sum of values in window."""
        return sum(self.get_window(group_key, window_seconds))

    def count(self, group_key: str, window_seconds: int) -> int:
        """Count of values in window."""
        return len(self.get_window(group_key, window_seconds))

    def avg(self, group_key: str, window_seconds: int) -> float:
        """Average of values in window."""
        values = self.get_window(group_key, window_seconds)
        return sum(values) / len(values) if values else 0.0

    def prune(self, max_age_seconds: int = 604800):
        """Remove entries older than max_age (default: 1 week)."""
        cutoff = int(time.time()) - max_age_seconds
        for key in self._data:
            self._data[key] = [(ts, v) for ts, v in self._data[key] if ts >= cutoff]


# ═══════════════════════════════════════════════════════════════════════════════
# CDL EVALUATOR - The CPU of Newton
# ═══════════════════════════════════════════════════════════════════════════════

class CDLEvaluator:
    """
    Evaluates CDL 3.0 constraints against objects.

    This is the Forge - the CPU of the Newton Supercomputer.
    Every evaluation is a computation. The constraint IS the instruction.
    """

    def __init__(self):
        self.aggregation_state = AggregationState()
        self._evaluation_count = 0
        self._operator_map = self._build_operator_map()

    def _build_operator_map(self) -> Dict[Operator, Callable]:
        """Map operators to evaluation functions."""
        return {
            # Comparison operators
            Operator.EQ: lambda a, b: a == b,
            Operator.NE: lambda a, b: a != b,
            Operator.LT: lambda a, b: a < b,
            Operator.GT: lambda a, b: a > b,
            Operator.LE: lambda a, b: a <= b,
            Operator.GE: lambda a, b: a >= b,
            Operator.CONTAINS: lambda a, b: b in str(a),
            Operator.MATCHES: lambda a, b: bool(re.search(b, str(a))),
            Operator.IN: lambda a, b: a in b,
            Operator.NOT_IN: lambda a, b: a not in b,
            Operator.EXISTS: lambda a, b: a is not None,
            Operator.EMPTY: lambda a, b: a is None or a == "" or a == [] or a == {},
        }

    def evaluate(self, constraint: Constraint, obj: Dict[str, Any]) -> EvaluationResult:
        """
        Evaluate a constraint against an object.

        Returns EvaluationResult with binary pass/fail.
        No probabilities. No maybes. 1 == 1 or it doesn't.
        """
        self._evaluation_count += 1

        if isinstance(constraint, AtomicConstraint):
            return self._evaluate_atomic(constraint, obj)
        elif isinstance(constraint, ConditionalConstraint):
            return self._evaluate_conditional(constraint, obj)
        elif isinstance(constraint, CompositeConstraint):
            return self._evaluate_composite(constraint, obj)
        else:
            return EvaluationResult(
                passed=False,
                constraint_id="UNKNOWN",
                message=f"Unknown constraint type: {type(constraint)}"
            )

    def _get_field_value(self, obj: Dict[str, Any], field_path: str) -> Any:
        """Extract field value using dot notation."""
        parts = field_path.split('.')
        value = obj
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    def _evaluate_atomic(self, c: AtomicConstraint, obj: Dict[str, Any]) -> EvaluationResult:
        """Evaluate an atomic constraint."""
        field_value = self._get_field_value(obj, c.field)

        # Handle temporal operators
        if c.operator in (Operator.WITHIN, Operator.AFTER, Operator.BEFORE):
            return self._evaluate_temporal(c, obj, field_value)

        # Handle aggregation operators
        if c.operator in (Operator.SUM_LT, Operator.SUM_LE, Operator.SUM_GT, Operator.SUM_GE,
                          Operator.COUNT_LT, Operator.COUNT_LE, Operator.COUNT_GT, Operator.COUNT_GE,
                          Operator.AVG_LT, Operator.AVG_LE, Operator.AVG_GT, Operator.AVG_GE):
            return self._evaluate_aggregation(c, obj, field_value)

        # Standard comparison
        if c.operator in self._operator_map:
            try:
                passed = self._operator_map[c.operator](field_value, c.value)
                return EvaluationResult(
                    passed=passed,
                    constraint_id=c.id,
                    message=c.message if not passed else None
                )
            except Exception as e:
                return EvaluationResult(
                    passed=False,
                    constraint_id=c.id,
                    message=f"Evaluation error: {str(e)}"
                )

        return EvaluationResult(
            passed=False,
            constraint_id=c.id,
            message=f"Unknown operator: {c.operator}"
        )

    def _evaluate_temporal(self, c: AtomicConstraint, obj: Dict[str, Any], field_value: Any) -> EvaluationResult:
        """Evaluate temporal constraints (within, after, before)."""
        if field_value is None:
            return EvaluationResult(passed=False, constraint_id=c.id, message="Field not found")

        # Get reference timestamp
        ref_value = self._get_field_value(obj, c.reference) if c.reference else time.time()
        if ref_value is None:
            return EvaluationResult(passed=False, constraint_id=c.id, message="Reference field not found")

        # Parse duration for WITHIN
        if c.operator == Operator.WITHIN:
            try:
                window = parse_duration(c.value)
                diff = abs(float(field_value) - float(ref_value))
                passed = diff <= window
            except Exception as e:
                return EvaluationResult(passed=False, constraint_id=c.id, message=str(e))
        elif c.operator == Operator.AFTER:
            passed = float(field_value) > float(ref_value)
        elif c.operator == Operator.BEFORE:
            passed = float(field_value) < float(ref_value)
        else:
            passed = False

        return EvaluationResult(
            passed=passed,
            constraint_id=c.id,
            message=c.message if not passed else None
        )

    def _evaluate_aggregation(self, c: AtomicConstraint, obj: Dict[str, Any], field_value: Any) -> EvaluationResult:
        """Evaluate aggregation constraints (sum, count, avg over window)."""
        if c.window is None:
            return EvaluationResult(passed=False, constraint_id=c.id, message="Window required for aggregation")

        try:
            window_seconds = parse_duration(c.window)
        except ValueError as e:
            return EvaluationResult(passed=False, constraint_id=c.id, message=str(e))

        # Get group key
        group_key = "default"
        if c.group_by:
            group_value = self._get_field_value(obj, c.group_by)
            group_key = str(group_value) if group_value else "default"

        # Record current value if present
        if field_value is not None:
            try:
                self.aggregation_state.append(group_key, float(field_value))
            except (TypeError, ValueError):
                pass

        # Calculate aggregate
        op_name = c.operator.value
        if op_name.startswith('sum_'):
            agg_value = self.aggregation_state.sum(group_key, window_seconds)
        elif op_name.startswith('count_'):
            agg_value = self.aggregation_state.count(group_key, window_seconds)
        elif op_name.startswith('avg_'):
            agg_value = self.aggregation_state.avg(group_key, window_seconds)
        else:
            agg_value = 0

        # Compare
        comparison = op_name.split('_')[1]  # lt, le, gt, ge
        if comparison == 'lt':
            passed = agg_value < c.value
        elif comparison == 'le':
            passed = agg_value <= c.value
        elif comparison == 'gt':
            passed = agg_value > c.value
        elif comparison == 'ge':
            passed = agg_value >= c.value
        else:
            passed = False

        return EvaluationResult(
            passed=passed,
            constraint_id=c.id,
            message=f"{op_name}({c.field}) = {agg_value}, limit = {c.value}" if not passed else None
        )

    def _evaluate_conditional(self, c: ConditionalConstraint, obj: Dict[str, Any]) -> EvaluationResult:
        """Evaluate conditional (if/then/else) constraint."""
        condition_result = self.evaluate(c.condition, obj)

        if condition_result.passed:
            return self.evaluate(c.then_constraint, obj)
        elif c.else_constraint:
            return self.evaluate(c.else_constraint, obj)
        else:
            # No else clause, condition failed = pass
            return EvaluationResult(passed=True, constraint_id=c.id)

    def _evaluate_composite(self, c: CompositeConstraint, obj: Dict[str, Any]) -> EvaluationResult:
        """Evaluate composite (AND, OR, NOT) constraint."""
        results = [self.evaluate(sub, obj) for sub in c.constraints]

        if c.logic.lower() == "and":
            passed = all(r.passed for r in results)
            failed = [r for r in results if not r.passed]
            message = "; ".join(r.message for r in failed if r.message) if not passed else None
        elif c.logic.lower() == "or":
            passed = any(r.passed for r in results)
            message = "All constraints failed" if not passed else None
        elif c.logic.lower() == "not":
            passed = not any(r.passed for r in results)
            message = "NOT condition not satisfied" if not passed else None
        else:
            passed = False
            message = f"Unknown logic: {c.logic}"

        return EvaluationResult(passed=passed, constraint_id=c.id, message=message)

    @property
    def evaluation_count(self) -> int:
        return self._evaluation_count


# ═══════════════════════════════════════════════════════════════════════════════
# HALT CHECKER - Proves constraints terminate
# ═══════════════════════════════════════════════════════════════════════════════

class HaltChecker:
    """
    Verifies that a CDL constraint will terminate.

    Newton's answer to the Halting Problem:
    We don't solve it. We forbid non-halting constraints at parse time.
    """

    MAX_DEPTH = 100
    MAX_CONSTRAINTS = 1000

    def check(self, constraint: Constraint, depth: int = 0) -> tuple[bool, Optional[str]]:
        """
        Check if constraint is guaranteed to halt.
        Returns (halts, reason) tuple.
        """
        if depth > self.MAX_DEPTH:
            return False, f"Constraint depth exceeds maximum ({self.MAX_DEPTH})"

        if isinstance(constraint, AtomicConstraint):
            return self._check_atomic(constraint)
        elif isinstance(constraint, ConditionalConstraint):
            return self._check_conditional(constraint, depth)
        elif isinstance(constraint, CompositeConstraint):
            return self._check_composite(constraint, depth)

        return False, f"Unknown constraint type: {type(constraint)}"

    def _check_atomic(self, c: AtomicConstraint) -> tuple[bool, Optional[str]]:
        """Atomic constraints always halt (O(1) or O(n) bounded)."""
        # Check aggregation window is bounded
        if c.operator.value.startswith(('sum_', 'count_', 'avg_')):
            if c.window is None:
                return False, "Aggregation requires bounded window"
            try:
                window = parse_duration(c.window)
                if window > 31536000:  # 1 year max
                    return False, "Aggregation window exceeds 1 year"
            except ValueError as e:
                return False, str(e)

        return True, None

    def _check_conditional(self, c: ConditionalConstraint, depth: int) -> tuple[bool, Optional[str]]:
        """Check all branches of conditional."""
        for sub in [c.condition, c.then_constraint, c.else_constraint]:
            if sub is not None:
                halts, reason = self.check(sub, depth + 1)
                if not halts:
                    return False, reason
        return True, None

    def _check_composite(self, c: CompositeConstraint, depth: int) -> tuple[bool, Optional[str]]:
        """Check all children of composite."""
        if len(c.constraints) > self.MAX_CONSTRAINTS:
            return False, f"Composite exceeds maximum constraints ({self.MAX_CONSTRAINTS})"

        for sub in c.constraints:
            halts, reason = self.check(sub, depth + 1)
            if not halts:
                return False, reason
        return True, None


# ═══════════════════════════════════════════════════════════════════════════════
# CDL PARSER - Parse dict/JSON to Constraint objects
# ═══════════════════════════════════════════════════════════════════════════════

class CDLParser:
    """Parse CDL 3.0 constraint definitions from dict/JSON."""

    def __init__(self):
        self.halt_checker = HaltChecker()

    def parse(self, definition: Dict[str, Any], check_halts: bool = True) -> Constraint:
        """Parse a constraint definition and optionally verify it halts."""
        constraint = self._parse_internal(definition)

        if check_halts:
            halts, reason = self.halt_checker.check(constraint)
            if not halts:
                raise ValueError(f"Constraint may not terminate: {reason}")

        return constraint

    def _parse_internal(self, d: Dict[str, Any]) -> Constraint:
        """Internal parsing logic."""
        # Check for conditional
        if 'if' in d:
            return ConditionalConstraint(
                condition=self._parse_internal(d['if']),
                then_constraint=self._parse_internal(d['then']),
                else_constraint=self._parse_internal(d['else']) if 'else' in d else None
            )

        # Check for composite
        if 'logic' in d:
            return CompositeConstraint(
                logic=d['logic'],
                constraints=[self._parse_internal(c) for c in d['constraints']]
            )

        # Atomic constraint
        return AtomicConstraint(
            domain=Domain(d.get('domain', 'custom')),
            field=d['field'],
            operator=Operator(d['operator']),
            value=d.get('value'),
            message=d.get('message'),
            action=d.get('action', 'reject'),
            window=d.get('window'),
            group_by=d.get('group_by'),
            reference=d.get('reference')
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def verify(constraint: Union[Constraint, Dict], obj: Dict[str, Any]) -> EvaluationResult:
    """
    One-liner verification.

    >>> verify({"field": "amount", "operator": "lt", "value": 100}, {"amount": 50})
    EvaluationResult(passed=True, ...)
    """
    evaluator = CDLEvaluator()

    if isinstance(constraint, dict):
        parser = CDLParser()
        constraint = parser.parse(constraint)

    return evaluator.evaluate(constraint, obj)


def verify_all(constraints: List[Union[Constraint, Dict]], obj: Dict[str, Any]) -> List[EvaluationResult]:
    """Verify multiple constraints, return all results."""
    return [verify(c, obj) for c in constraints]


def verify_and(constraints: List[Union[Constraint, Dict]], obj: Dict[str, Any]) -> EvaluationResult:
    """All constraints must pass."""
    results = verify_all(constraints, obj)
    passed = all(r.passed for r in results)
    return EvaluationResult(
        passed=passed,
        constraint_id="AND_" + "_".join(r.constraint_id[:4] for r in results),
        message="; ".join(r.message for r in results if r.message) if not passed else None
    )


def verify_or(constraints: List[Union[Constraint, Dict]], obj: Dict[str, Any]) -> EvaluationResult:
    """At least one constraint must pass."""
    results = verify_all(constraints, obj)
    passed = any(r.passed for r in results)
    return EvaluationResult(
        passed=passed,
        constraint_id="OR_" + "_".join(r.constraint_id[:4] for r in results),
        message="All constraints failed" if not passed else None
    )


# ═══════════════════════════════════════════════════════════════════════════════
# THE CLOSURE CONDITION
# ═══════════════════════════════════════════════════════════════════════════════

def newton(current: Any, goal: Any) -> bool:
    """
    The fundamental law.
    1 == 1.
    Everything else follows.
    """
    return current == goal


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton CDL 3.0 - Constraint Definition Language")
    print("=" * 60)

    # Test basic constraint
    c1 = {"domain": "financial", "field": "amount", "operator": "lt", "value": 1000}
    obj = {"amount": 500, "user_id": "u123"}
    result = verify(c1, obj)
    print(f"\nBasic: amount < 1000 where amount=500")
    print(f"  Result: {'PASS' if result.passed else 'FAIL'}")

    # Test conditional
    c2 = {
        "if": {"field": "amount", "operator": "gt", "value": 10000},
        "then": {"field": "manager_approved", "operator": "eq", "value": True},
        "else": {"field": "auto_approved", "operator": "eq", "value": True}
    }
    obj2 = {"amount": 15000, "manager_approved": True, "auto_approved": False}
    result2 = verify(c2, obj2)
    print(f"\nConditional: if amount > 10000 then manager_approved else auto_approved")
    print(f"  Object: amount=15000, manager_approved=True")
    print(f"  Result: {'PASS' if result2.passed else 'FAIL'}")

    # Test composite
    c3 = {
        "logic": "and",
        "constraints": [
            {"field": "amount", "operator": "lt", "value": 5000},
            {"field": "category", "operator": "ne", "value": "blocked"}
        ]
    }
    obj3 = {"amount": 2000, "category": "allowed"}
    result3 = verify(c3, obj3)
    print(f"\nComposite AND: amount < 5000 AND category != 'blocked'")
    print(f"  Object: amount=2000, category='allowed'")
    print(f"  Result: {'PASS' if result3.passed else 'FAIL'}")

    print("\n" + "=" * 60)
    print("1 == 1. The constraint IS the computation.")
