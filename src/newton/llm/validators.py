"""
NEWTON LLM DOMAIN VALIDATORS - Where Meaning Lives
═══════════════════════════════════════════════════════════════════════════════

"Meaning lives in validators, not tokens."

Each domain validator encodes ground truth for its domain.
The LLM proposes; validators decide.

Validators:
- PhysicsValidator: Wraps existing KineticForge/kinematic engine
- MathValidator: Symbolic equality via SymPy
- LogicValidator: Propositional consistency tracking
- PolicyValidator: Rule table enforcement
- TemporalValidator: Time ordering and duration constraints
- FinancialValidator: Budget and cost constraints

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Union
import re
import time

from .schema import Claim, Domain, ValidationResult


# ═══════════════════════════════════════════════════════════════════════════════
# BASE VALIDATOR INTERFACE - All validators implement this
# ═══════════════════════════════════════════════════════════════════════════════

class DomainValidator(ABC):
    """
    Abstract base class for all domain validators.

    Every domain has exactly one validator that encodes ground truth.
    No domain logic lives in the LLM.
    """

    domain: Domain = Domain.UNKNOWN

    @abstractmethod
    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a claim against domain constraints.

        Args:
            claim: The claim to validate

        Returns:
            ValidationResult with boolean verdict and explanation
        """
        pass

    def validate_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Convenience method to validate raw text.

        Args:
            text: The claim text
            metadata: Optional metadata

        Returns:
            ValidationResult
        """
        claim = Claim(text=text, domain=self.domain, metadata=metadata or {})
        return self.validate(claim)


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS VALIDATOR - Wraps Existing Kinematic Engine
# ═══════════════════════════════════════════════════════════════════════════════

class PhysicsValidator(DomainValidator):
    """
    Validates physics claims against kinematic constraints.

    This validator wraps Newton's existing kinematic/kinetic engines
    (KineticForge, constraint_extractor, CDL) to validate physical claims.

    For standalone use, it provides basic physical plausibility checks.
    For full integration, inject your kinematic_validator instance.
    """

    domain = Domain.PHYSICS

    # Basic physical constants and bounds for sanity checks
    SPEED_OF_LIGHT = 299_792_458  # m/s
    ABSOLUTE_ZERO = -273.15  # Celsius
    MAX_ACCELERATION_G = 1000  # reasonable upper bound in g's

    def __init__(self, kinematic_validator: Optional[Any] = None):
        """
        Initialize physics validator.

        Args:
            kinematic_validator: Optional external kinematic validator
                                 (e.g., KineticForge instance)
        """
        self.kv = kinematic_validator
        self._patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Pattern]:
        """Compile regex patterns for physics claim parsing."""
        return {
            "velocity": re.compile(
                r"velocity\s*[=:]\s*([-+]?\d*\.?\d+)\s*(m/s|km/h|mph)?",
                re.IGNORECASE
            ),
            "acceleration": re.compile(
                r"acceleration\s*[=:]\s*([-+]?\d*\.?\d+)\s*(m/s²|g)?",
                re.IGNORECASE
            ),
            "temperature": re.compile(
                r"temperature\s*[=:]\s*([-+]?\d*\.?\d+)\s*(°?[CFK]|celsius|fahrenheit|kelvin)?",
                re.IGNORECASE
            ),
            "mass": re.compile(
                r"mass\s*[=:]\s*([-+]?\d*\.?\d+)\s*(kg|g|lb)?",
                re.IGNORECASE
            ),
            "distance": re.compile(
                r"distance\s*[=:]\s*([-+]?\d*\.?\d+)\s*(m|km|mi|ft)?",
                re.IGNORECASE
            ),
            "time": re.compile(
                r"time\s*[=:]\s*([-+]?\d*\.?\d+)\s*(s|ms|min|h)?",
                re.IGNORECASE
            ),
            "energy": re.compile(
                r"energy\s*[=:]\s*([-+]?\d*\.?\d+)\s*(J|kJ|eV)?",
                re.IGNORECASE
            ),
            "force": re.compile(
                r"force\s*[=:]\s*([-+]?\d*\.?\d+)\s*(N|kN)?",
                re.IGNORECASE
            ),
        }

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a physics claim.

        If a kinematic_validator is injected, delegates to it.
        Otherwise, performs basic physical plausibility checks.
        """
        # If external validator is available, use it
        if self.kv is not None:
            return self._validate_with_kinematic_engine(claim)

        # Otherwise, do basic validation
        return self._validate_basic(claim)

    def _validate_with_kinematic_engine(self, claim: Claim) -> ValidationResult:
        """Validate using injected kinematic engine."""
        try:
            # Try the validate_text method if available
            if hasattr(self.kv, 'validate_text'):
                result = self.kv.validate_text(claim.text)

                if isinstance(result, dict):
                    status = result.get("overall_status", result.get("status", "unknown"))
                    if status == "verified":
                        return ValidationResult(
                            valid=True,
                            domain=Domain.PHYSICS,
                            rule="kinematic_constraints",
                            message="Physically valid",
                            details=result,
                        )
                    else:
                        violations = result.get("violations", [])
                        message = violations[0].get("message", "Physics violation") if violations else "Invalid physics"
                        return ValidationResult(
                            valid=False,
                            domain=Domain.PHYSICS,
                            rule="kinematic_constraints",
                            message=message,
                            details=result,
                        )

            # Try verify method (for KineticForge)
            if hasattr(self.kv, 'verify'):
                # KineticForge.verify needs (intent, priority, scene_type, user_state)
                # For physics claims, we extract and check
                return self._validate_basic(claim)

            # Unknown validator interface
            return ValidationResult(
                valid=False,
                domain=Domain.PHYSICS,
                rule="validator_error",
                message="Kinematic validator interface not recognized",
            )

        except Exception as e:
            return ValidationResult(
                valid=False,
                domain=Domain.PHYSICS,
                rule="validation_error",
                message=f"Validation error: {str(e)}",
            )

    def _validate_basic(self, claim: Claim) -> ValidationResult:
        """Basic physical plausibility validation."""
        text = claim.text.lower()

        # Check for impossible speeds
        vel_match = self._patterns["velocity"].search(text)
        if vel_match:
            value = float(vel_match.group(1))
            unit = vel_match.group(2) or "m/s"

            # Convert to m/s
            if "km/h" in unit.lower():
                value = value / 3.6
            elif "mph" in unit.lower():
                value = value * 0.44704

            if value > self.SPEED_OF_LIGHT:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="speed_of_light_limit",
                    message=f"Velocity {value:.2e} m/s exceeds speed of light",
                    details={"value": value, "limit": self.SPEED_OF_LIGHT},
                )

            if value < 0:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="negative_velocity",
                    message="Velocity magnitude cannot be negative",
                    details={"value": value},
                )

        # Check for impossible temperatures
        temp_match = self._patterns["temperature"].search(text)
        if temp_match:
            value = float(temp_match.group(1))
            unit = temp_match.group(2) or "C"

            # Convert to Celsius
            if "k" in unit.lower():
                value = value - 273.15
            elif "f" in unit.lower():
                value = (value - 32) * 5/9

            if value < self.ABSOLUTE_ZERO:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="absolute_zero_limit",
                    message=f"Temperature {value:.2f}°C below absolute zero",
                    details={"value_celsius": value, "limit": self.ABSOLUTE_ZERO},
                )

        # Check for negative mass
        mass_match = self._patterns["mass"].search(text)
        if mass_match:
            value = float(mass_match.group(1))
            if value < 0:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="negative_mass",
                    message="Mass cannot be negative",
                    details={"value": value},
                )

        # Check for negative time duration
        time_match = self._patterns["time"].search(text)
        if time_match:
            value = float(time_match.group(1))
            if value < 0:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="negative_time",
                    message="Time duration cannot be negative",
                    details={"value": value},
                )

        # Check for negative distance
        dist_match = self._patterns["distance"].search(text)
        if dist_match:
            value = float(dist_match.group(1))
            if value < 0:
                return ValidationResult(
                    valid=False,
                    domain=Domain.PHYSICS,
                    rule="negative_distance",
                    message="Distance cannot be negative",
                    details={"value": value},
                )

        # If we got here, claim is physically plausible
        return ValidationResult(
            valid=True,
            domain=Domain.PHYSICS,
            rule="physical_plausibility",
            message="Physically plausible",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MATH VALIDATOR - Symbolic Equality (Deterministic)
# ═══════════════════════════════════════════════════════════════════════════════

class MathValidator(DomainValidator):
    """
    Validates mathematical claims using symbolic computation.

    This validator kills all arithmetic hallucinations by:
    1. Parsing equations with SymPy
    2. Symbolically verifying equality
    3. Checking for algebraic correctness

    Supports:
    - Basic arithmetic: 2 + 2 = 4
    - Algebraic: x^2 - 1 = (x+1)(x-1)
    - Trigonometric: sin(0) = 0
    - Calculus: derivative of x^2 = 2x
    """

    domain = Domain.MATH

    def __init__(self, allow_numeric_approximation: bool = False, tolerance: float = 1e-9):
        """
        Initialize math validator.

        Args:
            allow_numeric_approximation: Whether to allow approximate numeric equality
            tolerance: Tolerance for numeric comparisons if approximation allowed
        """
        self.allow_numeric_approximation = allow_numeric_approximation
        self.tolerance = tolerance
        self._sympy_available = self._check_sympy()

    def _check_sympy(self) -> bool:
        """Check if SymPy is available."""
        try:
            import sympy
            return True
        except ImportError:
            return False

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a mathematical claim.

        Expects claims in the form "LHS = RHS" or "expression".
        """
        text = claim.text.strip()

        # Must contain an equals sign
        if "=" not in text:
            return ValidationResult(
                valid=False,
                domain=Domain.MATH,
                rule="equation_format",
                message="Mathematical claims must be equations (e.g., 'a = b')",
            )

        # Handle multiple equals (e.g., "a = b = c")
        parts = text.split("=")
        if len(parts) < 2:
            return ValidationResult(
                valid=False,
                domain=Domain.MATH,
                rule="parse_error",
                message="Invalid equation format",
            )

        # Strip whitespace from all parts
        parts = [p.strip() for p in parts]

        if self._sympy_available:
            return self._validate_with_sympy(parts, claim)
        else:
            return self._validate_basic(parts, claim)

    def _validate_with_sympy(self, parts: List[str], claim: Claim) -> ValidationResult:
        """Validate using SymPy symbolic computation."""
        try:
            import sympy as sp
            from sympy.parsing.sympy_parser import (
                parse_expr,
                standard_transformations,
                implicit_multiplication_application,
                convert_xor,
            )

            transformations = standard_transformations + (
                implicit_multiplication_application,
                convert_xor,
            )

            # Parse all parts
            expressions = []
            for part in parts:
                # Normalize mathematical notation
                normalized = self._normalize_math(part)
                try:
                    expr = parse_expr(normalized, transformations=transformations)
                    expressions.append(expr)
                except Exception as e:
                    return ValidationResult(
                        valid=False,
                        domain=Domain.MATH,
                        rule="parse_error",
                        message=f"Cannot parse '{part}': {str(e)}",
                        details={"part": part, "error": str(e)},
                    )

            # Check that all expressions are equal
            base_expr = expressions[0]
            for i, expr in enumerate(expressions[1:], 1):
                diff = sp.simplify(base_expr - expr)

                # Check symbolic equality
                if diff == 0:
                    continue

                # Try numeric evaluation if allowed
                if self.allow_numeric_approximation:
                    try:
                        numeric_diff = abs(complex(diff.evalf()))
                        if numeric_diff < self.tolerance:
                            continue
                    except (TypeError, ValueError):
                        pass

                return ValidationResult(
                    valid=False,
                    domain=Domain.MATH,
                    rule="symbolic_equality",
                    message=f"Equation does not hold: {parts[0]} ≠ {parts[i]}",
                    details={
                        "lhs": str(base_expr),
                        "rhs": str(expr),
                        "difference": str(diff),
                    },
                )

            return ValidationResult(
                valid=True,
                domain=Domain.MATH,
                rule="symbolic_equality",
                message="Mathematically valid",
                details={"simplified": str(sp.simplify(base_expr))},
            )

        except Exception as e:
            return ValidationResult(
                valid=False,
                domain=Domain.MATH,
                rule="validation_error",
                message=f"Math validation error: {str(e)}",
            )

    def _validate_basic(self, parts: List[str], claim: Claim) -> ValidationResult:
        """Basic numeric validation without SymPy."""
        try:
            # Try to evaluate both sides as Python expressions
            lhs = eval(self._normalize_math(parts[0]), {"__builtins__": {}}, {})
            rhs = eval(self._normalize_math(parts[1]), {"__builtins__": {}}, {})

            if abs(lhs - rhs) < self.tolerance:
                return ValidationResult(
                    valid=True,
                    domain=Domain.MATH,
                    rule="numeric_equality",
                    message="Numerically valid",
                    details={"lhs": lhs, "rhs": rhs},
                )
            else:
                return ValidationResult(
                    valid=False,
                    domain=Domain.MATH,
                    rule="numeric_equality",
                    message=f"Equation does not hold: {lhs} ≠ {rhs}",
                    details={"lhs": lhs, "rhs": rhs},
                )

        except Exception as e:
            return ValidationResult(
                valid=False,
                domain=Domain.MATH,
                rule="parse_error",
                message=f"Cannot evaluate expression: {str(e)}",
            )

    def _normalize_math(self, expr: str) -> str:
        """Normalize mathematical notation for parsing."""
        result = expr.strip()

        # Replace common notation
        result = result.replace("^", "**")  # Exponentiation
        result = result.replace("×", "*")   # Multiplication
        result = result.replace("÷", "/")   # Division
        result = result.replace("−", "-")   # Minus sign
        result = result.replace("·", "*")   # Middle dot multiplication

        # Handle factorial notation: n! -> factorial(n)
        result = re.sub(r'(\d+)!', r'factorial(\1)', result)

        # Handle sqrt
        result = re.sub(r'√(\d+)', r'sqrt(\1)', result)
        result = re.sub(r'sqrt\s*(\d+)', r'sqrt(\1)', result)

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIC VALIDATOR - Propositional Consistency
# ═══════════════════════════════════════════════════════════════════════════════

class LogicValidator(DomainValidator):
    """
    Validates logical claims for propositional consistency.

    Tracks facts and enforces the law of non-contradiction.
    A proposition cannot be both true and false.

    This validator maintains state - facts accumulate across validations.
    Call reset() to clear the fact base.
    """

    domain = Domain.LOGIC

    def __init__(self):
        """Initialize the logic validator with empty fact base."""
        self.facts: Dict[str, bool] = {}
        self._validation_count = 0

    def reset(self):
        """Clear all stored facts."""
        self.facts.clear()
        self._validation_count = 0

    def validate(self, claim: Claim) -> ValidationResult:
        """
        Validate a logical claim for consistency.

        Handles:
        - Simple propositions: "X" (asserts X is true)
        - Negations: "not X", "¬X" (asserts X is false)
        - Explicit truth values: "X is true", "X is false"
        """
        self._validation_count += 1
        text = claim.text.strip()

        # Detect negation
        is_negated = False
        proposition = text

        # Check for explicit negation patterns
        negation_patterns = [
            (r"^not\s+(.+)$", True),
            (r"^¬\s*(.+)$", True),
            (r"^(.+)\s+is\s+false$", True),
            (r"^it\s+is\s+not\s+the\s+case\s+that\s+(.+)$", True),
            (r"^(.+)\s+is\s+true$", False),
        ]

        for pattern, negated in negation_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                proposition = match.group(1).strip()
                is_negated = negated
                break

        # Normalize proposition (lowercase, strip)
        proposition = proposition.lower().strip()

        # Check for contradiction
        if proposition in self.facts:
            existing_value = self.facts[proposition]
            new_value = not is_negated

            if existing_value != new_value:
                return ValidationResult(
                    valid=False,
                    domain=Domain.LOGIC,
                    rule="non_contradiction",
                    message=f"Contradiction: '{proposition}' was previously {'true' if existing_value else 'false'}",
                    details={
                        "proposition": proposition,
                        "existing_value": existing_value,
                        "new_value": new_value,
                    },
                )

        # Store the fact
        self.facts[proposition] = not is_negated

        return ValidationResult(
            valid=True,
            domain=Domain.LOGIC,
            rule="non_contradiction",
            message="Logically consistent",
            details={
                "proposition": proposition,
                "value": not is_negated,
                "total_facts": len(self.facts),
            },
        )

    def get_facts(self) -> Dict[str, bool]:
        """Return current fact base."""
        return dict(self.facts)


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY VALIDATOR - Rule Table Enforcement
# ═══════════════════════════════════════════════════════════════════════════════

class PolicyValidator(DomainValidator):
    """
    Validates claims against policy rules.

    Policy is just another constraint system. Rules can be:
    - Forbidden phrases (blocklist)
    - Required phrases (allowlist with requirement)
    - Pattern matches (regex rules)
    - Custom rule functions

    Policy is NOT morality. Policy is organizational constraint.
    """

    domain = Domain.POLICY

    def __init__(
        self,
        forbidden_phrases: Optional[List[str]] = None,
        required_phrases: Optional[List[str]] = None,
        forbidden_patterns: Optional[List[str]] = None,
        custom_rules: Optional[List[Callable[[str], Tuple[bool, str]]]] = None,
    ):
        """
        Initialize policy validator.

        Args:
            forbidden_phrases: List of phrases that trigger violation
            required_phrases: List of phrases, at least one must be present
            forbidden_patterns: List of regex patterns that trigger violation
            custom_rules: List of functions (text) -> (valid, message)
        """
        self.forbidden_phrases = [p.lower() for p in (forbidden_phrases or [])]
        self.required_phrases = [p.lower() for p in (required_phrases or [])]
        self.forbidden_patterns = [
            re.compile(p, re.IGNORECASE) for p in (forbidden_patterns or [])
        ]
        self.custom_rules = custom_rules or []

    def validate(self, claim: Claim) -> ValidationResult:
        """Validate a claim against policy rules."""
        text = claim.text
        text_lower = text.lower()

        # Check forbidden phrases
        for phrase in self.forbidden_phrases:
            if phrase in text_lower:
                return ValidationResult(
                    valid=False,
                    domain=Domain.POLICY,
                    rule="forbidden_phrase",
                    message=f"Policy violation: forbidden content '{phrase}'",
                    details={"matched_phrase": phrase},
                )

        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            match = pattern.search(text)
            if match:
                return ValidationResult(
                    valid=False,
                    domain=Domain.POLICY,
                    rule="forbidden_pattern",
                    message=f"Policy violation: forbidden pattern matched",
                    details={"matched": match.group(), "pattern": pattern.pattern},
                )

        # Check required phrases (at least one must be present)
        if self.required_phrases:
            found = any(phrase in text_lower for phrase in self.required_phrases)
            if not found:
                return ValidationResult(
                    valid=False,
                    domain=Domain.POLICY,
                    rule="missing_required",
                    message=f"Policy violation: must include one of {self.required_phrases}",
                    details={"required": self.required_phrases},
                )

        # Check custom rules
        for rule_fn in self.custom_rules:
            try:
                valid, message = rule_fn(text)
                if not valid:
                    return ValidationResult(
                        valid=False,
                        domain=Domain.POLICY,
                        rule="custom_rule",
                        message=message,
                    )
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    domain=Domain.POLICY,
                    rule="rule_error",
                    message=f"Policy rule error: {str(e)}",
                )

        return ValidationResult(
            valid=True,
            domain=Domain.POLICY,
            rule="policy_check",
            message="Allowed by policy",
        )

    def add_forbidden(self, phrase: str):
        """Add a forbidden phrase."""
        self.forbidden_phrases.append(phrase.lower())

    def add_required(self, phrase: str):
        """Add a required phrase."""
        self.required_phrases.append(phrase.lower())

    def add_pattern(self, pattern: str):
        """Add a forbidden pattern."""
        self.forbidden_patterns.append(re.compile(pattern, re.IGNORECASE))

    def add_rule(self, rule_fn: Callable[[str], Tuple[bool, str]]):
        """Add a custom rule function."""
        self.custom_rules.append(rule_fn)


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPORAL VALIDATOR - Time Ordering and Duration
# ═══════════════════════════════════════════════════════════════════════════════

class TemporalValidator(DomainValidator):
    """
    Validates temporal claims for logical ordering and constraints.

    Checks:
    - Events cannot occur before they are caused
    - Durations must be positive
    - Time references must be valid
    - Sequence consistency
    """

    domain = Domain.TEMPORAL

    def __init__(self):
        """Initialize temporal validator."""
        self.events: Dict[str, float] = {}  # event -> timestamp
        self._patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Pattern]:
        """Compile temporal parsing patterns."""
        return {
            "before": re.compile(r"(.+)\s+(?:before|prior to|precedes)\s+(.+)", re.IGNORECASE),
            "after": re.compile(r"(.+)\s+(?:after|following|succeeds)\s+(.+)", re.IGNORECASE),
            "duration": re.compile(r"duration\s*[=:]\s*([-+]?\d*\.?\d+)\s*(s|ms|min|h|d)?", re.IGNORECASE),
            "at_time": re.compile(r"(.+)\s+(?:at|occurs? at)\s+(\d+(?:\.\d+)?)", re.IGNORECASE),
        }

    def reset(self):
        """Clear event timeline."""
        self.events.clear()

    def validate(self, claim: Claim) -> ValidationResult:
        """Validate a temporal claim."""
        text = claim.text.strip()

        # Check for duration claims
        duration_match = self._patterns["duration"].search(text)
        if duration_match:
            value = float(duration_match.group(1))
            if value < 0:
                return ValidationResult(
                    valid=False,
                    domain=Domain.TEMPORAL,
                    rule="positive_duration",
                    message="Duration cannot be negative",
                    details={"value": value},
                )
            return ValidationResult(
                valid=True,
                domain=Domain.TEMPORAL,
                rule="positive_duration",
                message="Valid duration",
            )

        # Check for "before" relationships
        before_match = self._patterns["before"].search(text)
        if before_match:
            event_a = before_match.group(1).strip().lower()
            event_b = before_match.group(2).strip().lower()

            # Check for contradiction with known ordering
            if event_a in self.events and event_b in self.events:
                if self.events[event_a] >= self.events[event_b]:
                    return ValidationResult(
                        valid=False,
                        domain=Domain.TEMPORAL,
                        rule="temporal_ordering",
                        message=f"Temporal contradiction: '{event_a}' cannot be before '{event_b}'",
                        details={
                            "event_a": event_a,
                            "event_b": event_b,
                            "time_a": self.events[event_a],
                            "time_b": self.events[event_b],
                        },
                    )

            # Record ordering if not contradicted
            if event_b not in self.events:
                self.events[event_b] = time.time()
            if event_a not in self.events:
                self.events[event_a] = self.events[event_b] - 1

            return ValidationResult(
                valid=True,
                domain=Domain.TEMPORAL,
                rule="temporal_ordering",
                message="Temporal ordering valid",
            )

        # Check for "after" relationships
        after_match = self._patterns["after"].search(text)
        if after_match:
            event_a = after_match.group(1).strip().lower()
            event_b = after_match.group(2).strip().lower()

            if event_a in self.events and event_b in self.events:
                if self.events[event_a] <= self.events[event_b]:
                    return ValidationResult(
                        valid=False,
                        domain=Domain.TEMPORAL,
                        rule="temporal_ordering",
                        message=f"Temporal contradiction: '{event_a}' cannot be after '{event_b}'",
                        details={
                            "event_a": event_a,
                            "event_b": event_b,
                        },
                    )

            if event_b not in self.events:
                self.events[event_b] = time.time()
            if event_a not in self.events:
                self.events[event_a] = self.events[event_b] + 1

            return ValidationResult(
                valid=True,
                domain=Domain.TEMPORAL,
                rule="temporal_ordering",
                message="Temporal ordering valid",
            )

        # Generic temporal claim - check for at_time pattern
        at_time_match = self._patterns["at_time"].search(text)
        if at_time_match:
            event = at_time_match.group(1).strip().lower()
            timestamp = float(at_time_match.group(2))
            self.events[event] = timestamp

            return ValidationResult(
                valid=True,
                domain=Domain.TEMPORAL,
                rule="event_recorded",
                message="Temporal event recorded",
                details={"event": event, "timestamp": timestamp},
            )

        # Default: accept unrecognized temporal claims
        return ValidationResult(
            valid=True,
            domain=Domain.TEMPORAL,
            rule="temporal_default",
            message="Temporal claim accepted",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FINANCIAL VALIDATOR - Budget and Cost Constraints
# ═══════════════════════════════════════════════════════════════════════════════

class FinancialValidator(DomainValidator):
    """
    Validates financial claims against budget constraints.

    Supports:
    - Budget limits
    - Cost calculations
    - Balance checks (no overdraft)
    - Rate limits
    """

    domain = Domain.FINANCIAL

    def __init__(
        self,
        budget: Optional[float] = None,
        min_balance: float = 0.0,
        max_transaction: Optional[float] = None,
    ):
        """
        Initialize financial validator.

        Args:
            budget: Maximum total budget
            min_balance: Minimum allowed balance (default 0 = no overdraft)
            max_transaction: Maximum single transaction amount
        """
        self.budget = budget
        self.min_balance = min_balance
        self.max_transaction = max_transaction
        self.balance = budget or float('inf')
        self._transactions: List[Dict[str, Any]] = []

    def reset(self, budget: Optional[float] = None):
        """Reset financial state."""
        if budget is not None:
            self.budget = budget
            self.balance = budget
        else:
            self.balance = self.budget or float('inf')
        self._transactions.clear()

    def validate(self, claim: Claim) -> ValidationResult:
        """Validate a financial claim."""
        text = claim.text.lower()

        # Extract cost/price from claim
        cost_pattern = re.compile(
            r"(?:cost|price|amount|charge|fee|total)\s*[=:]\s*\$?([\d,]+\.?\d*)",
            re.IGNORECASE
        )

        cost_match = cost_pattern.search(text)
        if cost_match:
            cost = float(cost_match.group(1).replace(",", ""))

            # Check max transaction
            if self.max_transaction and cost > self.max_transaction:
                return ValidationResult(
                    valid=False,
                    domain=Domain.FINANCIAL,
                    rule="max_transaction",
                    message=f"Transaction ${cost:.2f} exceeds maximum ${self.max_transaction:.2f}",
                    details={"amount": cost, "limit": self.max_transaction},
                )

            # Check if would cause overdraft
            new_balance = self.balance - cost
            if new_balance < self.min_balance:
                return ValidationResult(
                    valid=False,
                    domain=Domain.FINANCIAL,
                    rule="overdraft_prevention",
                    message=f"Transaction would reduce balance below ${self.min_balance:.2f}",
                    details={
                        "amount": cost,
                        "current_balance": self.balance,
                        "would_be_balance": new_balance,
                        "minimum_balance": self.min_balance,
                    },
                )

            # Record the transaction
            self._transactions.append({"amount": cost, "timestamp": time.time()})
            self.balance = new_balance

            return ValidationResult(
                valid=True,
                domain=Domain.FINANCIAL,
                rule="budget_check",
                message=f"Transaction approved. Remaining: ${self.balance:.2f}",
                details={
                    "amount": cost,
                    "new_balance": self.balance,
                },
            )

        # No financial amount detected - pass through
        return ValidationResult(
            valid=True,
            domain=Domain.FINANCIAL,
            rule="non_financial",
            message="No financial constraint to validate",
        )

    @property
    def remaining_budget(self) -> float:
        """Get remaining budget."""
        return self.balance


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE VALIDATOR - Validates against multiple domains
# ═══════════════════════════════════════════════════════════════════════════════

class CompositeValidator(DomainValidator):
    """
    A validator that chains multiple validators together.

    Claims pass only if ALL validators approve.
    First failing validator determines the result.
    """

    domain = Domain.UNKNOWN

    def __init__(self, validators: List[DomainValidator]):
        """
        Initialize composite validator.

        Args:
            validators: List of validators to chain
        """
        self.validators = validators

    def validate(self, claim: Claim) -> ValidationResult:
        """Validate against all validators in sequence."""
        for validator in self.validators:
            result = validator.validate(claim)
            if not result.valid:
                return result

        return ValidationResult(
            valid=True,
            domain=Domain.UNKNOWN,
            rule="composite_pass",
            message="Passed all validators",
            details={"validator_count": len(self.validators)},
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "DomainValidator",
    "PhysicsValidator",
    "MathValidator",
    "LogicValidator",
    "PolicyValidator",
    "TemporalValidator",
    "FinancialValidator",
    "CompositeValidator",
]
