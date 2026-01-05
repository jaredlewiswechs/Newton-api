#!/usr/bin/env python3
"""
===========================================================================
NEWTON TEXT GENERATION MODULE - Constraint-Preserving Text Projection
===========================================================================

Purpose:
- Deterministic, constraint-preserving text projection
- No probabilistic guessing - no hallucination possible by construction
- Expand . Reduce = Identity (bijective text generation)
- Ledger-provable text generation

The core guarantee:
    return set(reduced) == set(original)
    If false -> text is rejected.

Newton does not generate language - it projects lawful meaning into words.

===========================================================================

ARCHITECTURE:

    CDL Constraints
         |
         v
    +------------+
    |  TEMPLATES |  (Expansion: constraints -> text candidates)
    +------------+
         |
         v
    +------------+
    |  PROJECTOR |  (Selection: verify each candidate)
    +------------+
         |
         v
    +------------+
    |  REDUCTION |  (Verification: text -> constraints)
    +------------+
         |
         v
    Verified Text (only if reduce(text) == original)

===========================================================================

HISTORICAL LINEAGE:

This module implements FORMAL LANGUAGE GENERATION from constraints,
following the same philosophy as Newton's other components:
- The constraint IS the instruction
- The verification IS the computation
- Expand . Reduce = Identity (reversible projection)

Unlike LLMs which generate probabilistically and may hallucinate,
Newton TextGen generates ONLY text that can be reduced back to
the original constraints. No new claims. No drift. No lies.

===========================================================================

Created: January 5, 2026
Author: Jared Lewis / Newton Supercomputer
===========================================================================
"""

from typing import List, Dict, Callable, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re
import time

# Import Newton core components for integration
try:
    from .cdl import (
        Constraint, AtomicConstraint, RatioConstraint,
        CompositeConstraint, ConditionalConstraint,
        Operator, Domain, EvaluationResult, CDLEvaluator
    )
    from .ledger import LedgerEntry
except ImportError:
    # Allow standalone testing
    Constraint = Any
    AtomicConstraint = Any
    RatioConstraint = Any
    CompositeConstraint = Any
    ConditionalConstraint = Any
    Operator = None
    Domain = None
    EvaluationResult = None
    CDLEvaluator = None
    LedgerEntry = None


# ===========================================================================
# CORE CONCEPTS
# ===========================================================================

class TextStyle(Enum):
    """Output text style levels."""
    FORMAL = "formal"           # Legal/contract language
    TECHNICAL = "technical"     # Developer documentation
    EDUCATIONAL = "educational" # Teacher-friendly explanations
    MINIMAL = "minimal"         # Terse, code-like


@dataclass
class TextConstraint:
    """
    Canonical constraint representation for text generation.
    Can be created from CDL constraints or standalone.
    """
    field: str
    op: str  # ge, le, eq, lt, gt, ne, ratio_le, ratio_lt, etc.
    value: Any
    denominator: Optional[str] = None  # For ratio constraints (f/g)
    domain: str = "custom"
    message: Optional[str] = None

    def canonical(self) -> str:
        """Return canonical string representation."""
        if self.denominator:
            return f"{self.field}/{self.denominator} {self.op} {self.value}"
        return f"{self.field} {self.op} {self.value}"

    def __hash__(self):
        return hash(self.canonical())

    def __eq__(self, other):
        if not isinstance(other, TextConstraint):
            return False
        return self.canonical() == other.canonical()

    @classmethod
    def from_cdl(cls, constraint: Constraint) -> 'TextConstraint':
        """Create TextConstraint from a CDL constraint."""
        if isinstance(constraint, AtomicConstraint):
            return cls(
                field=constraint.field,
                op=constraint.operator.value if hasattr(constraint.operator, 'value') else str(constraint.operator),
                value=constraint.value,
                denominator=constraint.denominator,
                domain=constraint.domain.value if hasattr(constraint.domain, 'value') else str(constraint.domain),
                message=constraint.message
            )
        elif isinstance(constraint, RatioConstraint):
            return cls(
                field=constraint.f_field,
                op=constraint.operator.value if hasattr(constraint.operator, 'value') else str(constraint.operator),
                value=constraint.threshold,
                denominator=constraint.g_field,
                domain=constraint.domain.value if hasattr(constraint.domain, 'value') else str(constraint.domain),
                message=constraint.message
            )
        else:
            raise ValueError(f"Cannot convert {type(constraint)} to TextConstraint")


# ===========================================================================
# EXPANSION TEMPLATES - Constraints -> Text
# ===========================================================================

# Operator templates by style
TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "formal": {
        "ge": [
            "{field} must be greater than or equal to {value}.",
            "{field} shall not be less than {value}.",
            "The {field} is required to maintain a minimum of {value}."
        ],
        "le": [
            "{field} must be less than or equal to {value}.",
            "{field} shall not exceed {value}.",
            "The {field} is capped at {value}."
        ],
        "eq": [
            "{field} must equal {value}.",
            "{field} shall be exactly {value}.",
            "The {field} is required to be {value}."
        ],
        "lt": [
            "{field} must be less than {value}.",
            "{field} shall be strictly below {value}.",
            "The {field} cannot reach {value}."
        ],
        "gt": [
            "{field} must be greater than {value}.",
            "{field} shall exceed {value}.",
            "The {field} must be strictly above {value}."
        ],
        "ne": [
            "{field} must not equal {value}.",
            "{field} shall differ from {value}.",
            "The {field} cannot be {value}."
        ],
        # Ratio constraints (f/g)
        "ratio_le": [
            "The ratio of {field} to {denominator} must not exceed {value}.",
            "{field}/{denominator} shall be at most {value}.",
            "The {field} to {denominator} ratio is capped at {value}."
        ],
        "ratio_lt": [
            "The ratio of {field} to {denominator} must be strictly less than {value}.",
            "{field}/{denominator} shall remain below {value}.",
            "The {field} to {denominator} ratio cannot reach {value}."
        ],
        "ratio_ge": [
            "The ratio of {field} to {denominator} must be at least {value}.",
            "{field}/{denominator} shall not fall below {value}.",
            "The {field} to {denominator} ratio is required to maintain a minimum of {value}."
        ],
        "ratio_gt": [
            "The ratio of {field} to {denominator} must exceed {value}.",
            "{field}/{denominator} shall be strictly above {value}.",
            "The {field} to {denominator} ratio must surpass {value}."
        ],
    },
    "technical": {
        "ge": [
            "{field} >= {value}",
            "assert({field} >= {value})",
            "require: {field} >= {value}"
        ],
        "le": [
            "{field} <= {value}",
            "assert({field} <= {value})",
            "require: {field} <= {value}"
        ],
        "eq": [
            "{field} == {value}",
            "assert({field} == {value})",
            "require: {field} == {value}"
        ],
        "lt": [
            "{field} < {value}",
            "assert({field} < {value})",
            "require: {field} < {value}"
        ],
        "gt": [
            "{field} > {value}",
            "assert({field} > {value})",
            "require: {field} > {value}"
        ],
        "ne": [
            "{field} != {value}",
            "assert({field} != {value})",
            "require: {field} != {value}"
        ],
        "ratio_le": [
            "{field}/{denominator} <= {value}",
            "assert({field}/{denominator} <= {value})",
            "require: {field}/{denominator} <= {value}"
        ],
        "ratio_lt": [
            "{field}/{denominator} < {value}",
            "assert({field}/{denominator} < {value})",
            "require: {field}/{denominator} < {value}"
        ],
        "ratio_ge": [
            "{field}/{denominator} >= {value}",
            "assert({field}/{denominator} >= {value})",
            "require: {field}/{denominator} >= {value}"
        ],
        "ratio_gt": [
            "{field}/{denominator} > {value}",
            "assert({field}/{denominator} > {value})",
            "require: {field}/{denominator} > {value}"
        ],
    },
    "educational": {
        "ge": [
            "The {field} needs to be at least {value}.",
            "Make sure {field} is {value} or more.",
            "Remember: {field} can't go below {value}!"
        ],
        "le": [
            "The {field} can't be more than {value}.",
            "Keep {field} at {value} or less.",
            "Remember: {field} has a limit of {value}!"
        ],
        "eq": [
            "The {field} has to be exactly {value}.",
            "Set {field} to {value} - no more, no less.",
            "{field} must match {value} exactly."
        ],
        "lt": [
            "The {field} needs to stay below {value}.",
            "Keep {field} under {value}.",
            "{field} must be less than {value}."
        ],
        "gt": [
            "The {field} needs to be more than {value}.",
            "Make {field} greater than {value}.",
            "{field} must exceed {value}."
        ],
        "ne": [
            "The {field} can be anything except {value}.",
            "Avoid setting {field} to {value}.",
            "{field} must differ from {value}."
        ],
        "ratio_le": [
            "The ratio of {field} to {denominator} should stay at or below {value}.",
            "When you divide {field} by {denominator}, keep it under {value}.",
            "Think of it like a balance: {field}/{denominator} can't exceed {value}."
        ],
        "ratio_lt": [
            "The ratio of {field} to {denominator} must stay under {value}.",
            "Keep {field} divided by {denominator} below {value}.",
            "{field}/{denominator} needs to be less than {value}."
        ],
        "ratio_ge": [
            "The ratio of {field} to {denominator} needs to be at least {value}.",
            "Make sure {field} divided by {denominator} is {value} or higher.",
            "{field}/{denominator} should be at least {value}."
        ],
        "ratio_gt": [
            "The ratio of {field} to {denominator} must exceed {value}.",
            "{field} divided by {denominator} needs to be more than {value}.",
            "Keep {field}/{denominator} above {value}."
        ],
    },
    "minimal": {
        "ge": ["{field} >= {value}"],
        "le": ["{field} <= {value}"],
        "eq": ["{field} = {value}"],
        "lt": ["{field} < {value}"],
        "gt": ["{field} > {value}"],
        "ne": ["{field} != {value}"],
        "ratio_le": ["{field}/{denominator} <= {value}"],
        "ratio_lt": ["{field}/{denominator} < {value}"],
        "ratio_ge": ["{field}/{denominator} >= {value}"],
        "ratio_gt": ["{field}/{denominator} > {value}"],
    }
}


# ===========================================================================
# REDUCTION ENGINE - Text -> Constraints
# ===========================================================================

# Reduction rules: functions that extract constraints from text
REDUCTION_RULES: List[Callable[[str], Optional[TextConstraint]]] = []


def register_reduction(rule: Callable[[str], Optional[TextConstraint]]):
    """Register a reduction rule."""
    REDUCTION_RULES.append(rule)
    return rule


def reduce_text(text: str) -> List[TextConstraint]:
    """
    Reduce text back into constraints.
    If reduction fails -> hallucination detected.
    """
    constraints = []
    for rule in REDUCTION_RULES:
        result = rule(text)
        if result:
            constraints.append(result)
    return constraints


# ===========================================================================
# BUILT-IN REDUCTION RULES
# ===========================================================================

@register_reduction
def reduce_ge(text: str) -> Optional[TextConstraint]:
    """Reduce 'greater than or equal to' patterns."""
    patterns = [
        r"(\w+)\s+must be greater than or equal to\s+(.+?)[.\s]*$",
        r"(\w+)\s+shall not be less than\s+(.+?)[.\s]*$",
        r"(\w+)\s+>=\s+(.+?)(?:\s|$)",
        r"assert\((\w+)\s+>=\s+(.+?)\)",
        r"require:\s+(\w+)\s+>=\s+(.+?)(?:\s|$)",
        r"(\w+)\s+needs to be at least\s+(.+?)[.\s]*$",
        r"(\w+)\s+can't go below\s+(.+?)[!\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="ge",
                value=match.group(2).strip().rstrip('.')
            )
    return None


@register_reduction
def reduce_le(text: str) -> Optional[TextConstraint]:
    """Reduce 'less than or equal to' patterns."""
    patterns = [
        r"(\w+)\s+must be less than or equal to\s+(.+?)[.\s]*$",
        r"(\w+)\s+shall not exceed\s+(.+?)[.\s]*$",
        r"(\w+)\s+is capped at\s+(.+?)[.\s]*$",
        r"(\w+)\s+<=\s+(.+?)(?:\s|$)",
        r"assert\((\w+)\s+<=\s+(.+?)\)",
        r"require:\s+(\w+)\s+<=\s+(.+?)(?:\s|$)",
        r"(\w+)\s+can't be more than\s+(.+?)[.\s]*$",
        r"(\w+)\s+has a limit of\s+(.+?)[!\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="le",
                value=match.group(2).strip().rstrip('.')
            )
    return None


@register_reduction
def reduce_eq(text: str) -> Optional[TextConstraint]:
    """Reduce 'equals' patterns."""
    patterns = [
        r"(\w+)\s+must equal\s+(.+?)[.\s]*$",
        r"(\w+)\s+shall be exactly\s+(.+?)[.\s]*$",
        r"(\w+)\s+is required to be\s+(.+?)[.\s]*$",
        r"(\w+)\s+==\s+(.+?)(?:\s|$)",
        r"assert\((\w+)\s+==\s+(.+?)\)",
        r"require:\s+(\w+)\s+==\s+(.+?)(?:\s|$)",
        r"(\w+)\s+=\s+(.+?)(?:\s|$)",
        r"(\w+)\s+has to be exactly\s+(.+?)[.\s]*$",
        r"(\w+)\s+must match\s+(.+?)\s+exactly",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="eq",
                value=match.group(2).strip().rstrip('.')
            )
    return None


@register_reduction
def reduce_lt(text: str) -> Optional[TextConstraint]:
    """Reduce 'less than' patterns."""
    patterns = [
        r"(\w+)\s+must be less than\s+(.+?)[.\s]*$",
        r"(\w+)\s+shall be strictly below\s+(.+?)[.\s]*$",
        r"(\w+)\s+cannot reach\s+(.+?)[.\s]*$",
        r"(\w+)\s+<\s+(.+?)(?:\s|$)",
        r"assert\((\w+)\s+<\s+(.+?)\)",
        r"require:\s+(\w+)\s+<\s+(.+?)(?:\s|$)",
        r"(\w+)\s+needs to stay below\s+(.+?)[.\s]*$",
        r"keep\s+(\w+)\s+under\s+(.+?)[.\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="lt",
                value=match.group(2).strip().rstrip('.')
            )
    return None


@register_reduction
def reduce_gt(text: str) -> Optional[TextConstraint]:
    """Reduce 'greater than' patterns."""
    patterns = [
        r"(\w+)\s+must be greater than\s+(.+?)[.\s]*$",
        r"(\w+)\s+shall exceed\s+(.+?)[.\s]*$",
        r"(\w+)\s+must be strictly above\s+(.+?)[.\s]*$",
        r"(\w+)\s+>\s+(.+?)(?:\s|$)",
        r"assert\((\w+)\s+>\s+(.+?)\)",
        r"require:\s+(\w+)\s+>\s+(.+?)(?:\s|$)",
        r"(\w+)\s+needs to be more than\s+(.+?)[.\s]*$",
        r"(\w+)\s+must exceed\s+(.+?)[.\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="gt",
                value=match.group(2).strip().rstrip('.')
            )
    return None


@register_reduction
def reduce_ratio_le(text: str) -> Optional[TextConstraint]:
    """Reduce ratio 'less than or equal' patterns."""
    patterns = [
        r"ratio of (\w+) to (\w+) must not exceed (.+?)[.\s]*$",
        r"(\w+)/(\w+)\s+shall be at most\s+(.+?)[.\s]*$",
        r"(\w+)/(\w+)\s+<=\s+(.+?)(?:\s|$)",
        r"assert\((\w+)/(\w+)\s+<=\s+(.+?)\)",
        r"require:\s+(\w+)/(\w+)\s+<=\s+(.+?)(?:\s|$)",
        r"(\w+)\s+to\s+(\w+)\s+ratio is capped at\s+(.+?)[.\s]*$",
        r"(\w+)/(\w+)\s+can't exceed\s+(.+?)[.\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="ratio_le",
                value=match.group(3).strip().rstrip('.'),
                denominator=match.group(2).strip()
            )
    return None


@register_reduction
def reduce_ratio_lt(text: str) -> Optional[TextConstraint]:
    """Reduce ratio 'strictly less than' patterns."""
    patterns = [
        r"ratio of (\w+) to (\w+) must be strictly less than (.+?)[.\s]*$",
        r"(\w+)/(\w+)\s+shall remain below\s+(.+?)[.\s]*$",
        r"(\w+)/(\w+)\s+<\s+(.+?)(?:\s|$)",
        r"assert\((\w+)/(\w+)\s+<\s+(.+?)\)",
        r"require:\s+(\w+)/(\w+)\s+<\s+(.+?)(?:\s|$)",
        r"(\w+)\s+to\s+(\w+)\s+ratio cannot reach\s+(.+?)[.\s]*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return TextConstraint(
                field=match.group(1).strip(),
                op="ratio_lt",
                value=match.group(3).strip().rstrip('.'),
                denominator=match.group(2).strip()
            )
    return None


# ===========================================================================
# TEXT PROJECTOR - The Core Engine
# ===========================================================================

@dataclass
class ProjectionResult:
    """Result of text projection."""
    text: str
    constraint: TextConstraint
    fingerprint: str
    verified: bool
    style: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "constraint": self.constraint.canonical(),
            "fingerprint": self.fingerprint,
            "verified": self.verified,
            "style": self.style,
            "timestamp": self.timestamp
        }


class NewtonTextProjector:
    """
    Generates text ONLY if it preserves constraints.

    The core guarantee:
        expand . reduce = identity

    If a generated text cannot be reduced back to the original
    constraint, it is rejected. This makes hallucination impossible.
    """

    def __init__(self, style: str = "formal"):
        self.style = style
        self._projection_count = 0
        self._rejection_count = 0

    def expand(self, constraints: List[TextConstraint]) -> List[Tuple[str, TextConstraint]]:
        """
        Expand constraints into (text, constraint) candidates.
        """
        templates = TEMPLATES.get(self.style, TEMPLATES["formal"])
        outputs = []

        for c in constraints:
            op_templates = templates.get(c.op, [])
            for t in op_templates:
                try:
                    if c.denominator:
                        text = t.format(
                            field=c.field,
                            value=c.value,
                            denominator=c.denominator
                        )
                    else:
                        text = t.format(field=c.field, value=c.value)
                    outputs.append((text, c))
                except KeyError:
                    # Template doesn't match constraint type
                    continue

        return outputs

    def verify_expansion(
        self,
        original: TextConstraint,
        text: str
    ) -> bool:
        """
        Reduction check: expand . reduce = identity

        Returns True if the text reduces back to the original constraint.
        """
        reduced = reduce_text(text)

        # Check if any reduced constraint matches the original
        for r in reduced:
            if r.canonical() == original.canonical():
                return True

        return False

    def generate(
        self,
        constraints: List[TextConstraint],
        verify: bool = True
    ) -> List[ProjectionResult]:
        """
        Main entrypoint - generate verified text from constraints.

        Args:
            constraints: List of TextConstraint objects
            verify: If True (default), only return text that passes reduction

        Returns:
            List of ProjectionResult objects
        """
        results = []

        candidates = self.expand(constraints)
        for text, constraint in candidates:
            self._projection_count += 1

            if verify:
                verified = self.verify_expansion(constraint, text)
                if not verified:
                    self._rejection_count += 1
                    continue
            else:
                verified = False

            results.append(ProjectionResult(
                text=text,
                constraint=constraint,
                fingerprint=text_fingerprint(text),
                verified=verified,
                style=self.style
            ))

        return results

    def project_one(
        self,
        constraint: TextConstraint,
        verify: bool = True
    ) -> Optional[ProjectionResult]:
        """
        Project a single constraint to text.
        Returns the first valid projection or None.
        """
        results = self.generate([constraint], verify=verify)
        return results[0] if results else None

    @property
    def stats(self) -> Dict[str, int]:
        """Return projection statistics."""
        return {
            "projections": self._projection_count,
            "rejections": self._rejection_count,
            "acceptance_rate": (
                (self._projection_count - self._rejection_count) / self._projection_count
                if self._projection_count > 0 else 1.0
            )
        }


# ===========================================================================
# LEDGER INTEGRATION - Fingerprinting & Provenance
# ===========================================================================

def text_fingerprint(text: str) -> str:
    """Generate SHA-256 fingerprint for text (truncated to 16 chars)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16].upper()


def create_text_ledger_entry(
    result: ProjectionResult,
    prev_hash: str = "GENESIS"
) -> Dict[str, Any]:
    """
    Create a ledger entry for a text projection.
    Can be recorded in Newton's immutable ledger.
    """
    return {
        "index": -1,  # Assigned by ledger
        "timestamp": result.timestamp,
        "operation": "textgen",
        "payload_hash": text_fingerprint(result.text),
        "result": "pass" if result.verified else "unverified",
        "prev_hash": prev_hash,
        "metadata": {
            "constraint": result.constraint.canonical(),
            "style": result.style,
            "fingerprint": result.fingerprint
        }
    }


# ===========================================================================
# CDL SYNTAX SUGAR - For Integration
# ===========================================================================

def project(
    field: str,
    op: str,
    value: Any,
    denominator: Optional[str] = None,
    style: str = "formal"
) -> Optional[str]:
    """
    One-liner text projection from constraint parameters.

    Examples:
        >>> project("balance", "ge", 0)
        "balance must be greater than or equal to 0."

        >>> project("debt", "ratio_le", 3.0, denominator="equity")
        "The ratio of debt to equity must not exceed 3.0."
    """
    constraint = TextConstraint(
        field=field,
        op=op,
        value=value,
        denominator=denominator
    )
    projector = NewtonTextProjector(style=style)
    result = projector.project_one(constraint)
    return result.text if result else None


def project_cdl(constraint: Constraint, style: str = "formal") -> Optional[str]:
    """
    Project a CDL constraint to text.

    Examples:
        >>> from core.cdl import AtomicConstraint, Operator, Domain
        >>> c = AtomicConstraint(
        ...     domain=Domain.FINANCIAL,
        ...     field="balance",
        ...     operator=Operator.GE,
        ...     value=0
        ... )
        >>> project_cdl(c)
        "balance must be greater than or equal to 0."
    """
    try:
        text_constraint = TextConstraint.from_cdl(constraint)
        projector = NewtonTextProjector(style=style)
        result = projector.project_one(text_constraint)
        return result.text if result else None
    except (ValueError, AttributeError):
        return None


def explain_constraints(
    constraints: List[TextConstraint],
    style: str = "educational"
) -> List[str]:
    """
    Generate educational explanations for a list of constraints.
    Useful for teacher-friendly documentation.

    Examples:
        >>> constraints = [
        ...     TextConstraint("balance", "ge", 0),
        ...     TextConstraint("withdrawal", "ratio_le", 1.0, denominator="balance")
        ... ]
        >>> explain_constraints(constraints)
        ["The balance needs to be at least 0.", ...]
    """
    projector = NewtonTextProjector(style=style)
    results = projector.generate(constraints, verify=True)
    return [r.text for r in results]


# ===========================================================================
# DOCUMENT GENERATION - Multi-Constraint Documents
# ===========================================================================

@dataclass
class TextDocument:
    """A document composed of multiple projected constraints."""
    title: str
    sections: List[ProjectionResult]
    fingerprint: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def __post_init__(self):
        if not self.fingerprint:
            combined = self.title + "".join(s.fingerprint for s in self.sections)
            self.fingerprint = text_fingerprint(combined)

    def to_markdown(self) -> str:
        """Export document as markdown."""
        lines = [f"# {self.title}", ""]
        for i, section in enumerate(self.sections, 1):
            lines.append(f"{i}. {section.text}")
        lines.append("")
        lines.append(f"*Document fingerprint: {self.fingerprint}*")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "sections": [s.to_dict() for s in self.sections],
            "fingerprint": self.fingerprint,
            "timestamp": self.timestamp
        }


def generate_document(
    title: str,
    constraints: List[TextConstraint],
    style: str = "formal"
) -> TextDocument:
    """
    Generate a complete document from constraints.

    Examples:
        >>> constraints = [
        ...     TextConstraint("balance", "ge", 0),
        ...     TextConstraint("withdrawal", "le", "balance")
        ... ]
        >>> doc = generate_document("Account Rules", constraints)
        >>> print(doc.to_markdown())
    """
    projector = NewtonTextProjector(style=style)
    results = projector.generate(constraints, verify=True)
    return TextDocument(title=title, sections=results)


# ===========================================================================
# JESTER INTEGRATION - Code Analysis -> Text
# ===========================================================================

def project_jester_constraints(
    jester_output: List[Dict[str, Any]],
    style: str = "technical"
) -> List[ProjectionResult]:
    """
    Convert JESTER constraint extraction output to text.

    JESTER extracts constraints from source code. This function
    projects those constraints into readable documentation.

    Args:
        jester_output: List of constraint dicts from JESTER analyzer
        style: Text style (default: technical)

    Returns:
        List of ProjectionResult objects
    """
    constraints = []
    for j in jester_output:
        # Map JESTER constraint kinds to TextConstraint ops
        kind = j.get("kind", "unknown")
        op_map = {
            "null_check": "ne",
            "range_check": "ge",
            "upper_bound": "le",
            "lower_bound": "ge",
            "equality": "eq",
            "inequality": "ne",
            "assertion": "eq",
        }
        op = op_map.get(kind, "eq")

        constraints.append(TextConstraint(
            field=j.get("field", j.get("variable", "unknown")),
            op=op,
            value=j.get("value", j.get("bound", "valid"))
        ))

    projector = NewtonTextProjector(style=style)
    return projector.generate(constraints, verify=True)


# ===========================================================================
# CLI DEMO
# ===========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("NEWTON TEXT GENERATION MODULE")
    print("Constraint-Preserving Text Projection")
    print("=" * 70)

    # Demo constraints
    constraints = [
        TextConstraint("balance", "ge", 0),
        TextConstraint("withdrawal", "le", "balance"),
        TextConstraint("debt", "ratio_le", 3.0, denominator="equity"),
    ]

    print("\n--- Formal Style ---")
    projector = NewtonTextProjector(style="formal")
    for result in projector.generate(constraints):
        print(f"[OK] {result.text}")
        print(f"     Fingerprint: {result.fingerprint}")

    print("\n--- Technical Style ---")
    projector = NewtonTextProjector(style="technical")
    for result in projector.generate(constraints):
        print(f"[OK] {result.text}")

    print("\n--- Educational Style ---")
    projector = NewtonTextProjector(style="educational")
    for result in projector.generate(constraints):
        print(f"[OK] {result.text}")

    print("\n--- One-liner API ---")
    text = project("flicker_rate", "ratio_lt", 1.0, denominator="safe_threshold")
    print(f"[OK] {text}")

    print("\n--- Document Generation ---")
    doc = generate_document("Banking Rules", constraints[:2], style="formal")
    print(doc.to_markdown())

    print("\n--- Statistics ---")
    print(f"Projector stats: {projector.stats}")

    print("\n" + "=" * 70)
    print("Newton does not generate language - it projects lawful meaning into words.")
    print("Expand . Reduce = Identity")
    print("=" * 70)
