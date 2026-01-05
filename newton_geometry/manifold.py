#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
EXPAND/REDUCE MANIFOLD - The Fiber Bundle of Meaning
════════════════════════════════════════════════════════════════════════════════

Bijection as FOLDING and UNFOLDING:

    CONSTRAINT SPACE (C)              TEXT SPACE (T)

         ┌─────┐                      ┌─────────────┐
         │  •  │                      │   "balance  │
         │  c  │      expand()        │   must be   │
         │     │ ──────────────────▶  │   ≥ 0"      │
         └─────┘                      └──────┬──────┘
            ▲                                │
            │                                │
            │         reduce()               │
            └────────────────────────────────┘

         IDENTITY: c = reduce(expand(c))


    The two spaces are FOLDED onto each other.

    Every point in T maps back to exactly one point in C.

    If it doesn't → the point in T doesn't exist.


Visualized as fiber bundle:

         T (text space)
         │
         │  π (projection = reduce)
         │
         ▼
         C (constraint space)

    Each constraint c has a "fiber" of valid texts above it:

              t₁  t₂  t₃        (valid phrasings)
               ╲  │  ╱
                ╲ │ ╱
                 ╲│╱
                  c              (single constraint)

    Hallucination = text with no fiber connection
                  = floating point in T with no ground in C
                  = REJECTED

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set, FrozenSet, Callable, Tuple
import hashlib
import json


class ProjectionStatus(Enum):
    """Status of a text-to-constraint projection."""

    GROUNDED = auto()     # Text maps to a valid constraint
    HALLUCINATED = auto() # Text has no constraint grounding
    AMBIGUOUS = auto()    # Text maps to multiple constraints
    PARTIAL = auto()      # Text partially maps to constraint


@dataclass(frozen=True)
class ConstraintPoint:
    """
    A point in constraint space (C).

    Constraint points are the "ground truth" - the semantic content
    that text must faithfully represent.
    """

    id: str
    constraint_type: str
    content: Dict[str, Any]
    _hash: str = field(default="", repr=False)

    def __post_init__(self):
        if not self._hash:
            # Compute content hash for identity
            content_str = json.dumps(self.content, sort_keys=True)
            hash_val = hashlib.sha256(content_str.encode()).hexdigest()[:16]
            object.__setattr__(self, '_hash', hash_val)

    def __hash__(self):
        return hash(self._hash)

    def __eq__(self, other):
        if not isinstance(other, ConstraintPoint):
            return False
        return self._hash == other._hash

    @property
    def canonical_form(self) -> str:
        """The canonical string representation of this constraint."""
        return json.dumps({
            "type": self.constraint_type,
            "content": self.content,
        }, sort_keys=True)


@dataclass(frozen=True)
class TextPoint:
    """
    A point in text space (T).

    Text points are natural language expressions that may or may not
    have grounding in constraint space.
    """

    text: str
    style: str = "formal"
    _hash: str = field(default="", repr=False)

    def __post_init__(self):
        if not self._hash:
            hash_val = hashlib.sha256(self.text.encode()).hexdigest()[:16]
            object.__setattr__(self, '_hash', hash_val)

    def __hash__(self):
        return hash((self.text, self.style))

    @property
    def length(self) -> int:
        return len(self.text)


@dataclass
class Fiber:
    """
    A fiber over a constraint point.

    The fiber contains all valid text representations of a single constraint.
    These are the "equivalent phrasings" that reduce to the same meaning.
    """

    base_point: ConstraintPoint
    text_points: Set[TextPoint] = field(default_factory=set)

    def add_text(self, text: TextPoint) -> None:
        """Add a valid text representation to the fiber."""
        self.text_points.add(text)

    def contains(self, text: TextPoint) -> bool:
        """Check if a text point is in this fiber."""
        return text in self.text_points

    @property
    def cardinality(self) -> int:
        """Number of text points in the fiber."""
        return len(self.text_points)

    def is_empty(self) -> bool:
        """True if the fiber has no text representations."""
        return len(self.text_points) == 0


@dataclass
class FiberBundle:
    """
    The complete fiber bundle structure.

    This represents the total space of the manifold:
        E (total space) = T
        B (base space) = C
        π (projection) = reduce
        F (fiber) = set of equivalent texts

    The bundle structure ensures:
        1. Every constraint has at least one text representation
        2. Every valid text has exactly one constraint grounding
        3. reduce(expand(c)) = c for all c in C
    """

    fibers: Dict[str, Fiber] = field(default_factory=dict)
    _expand_fn: Optional[Callable[[ConstraintPoint], TextPoint]] = None
    _reduce_fn: Optional[Callable[[TextPoint], Optional[ConstraintPoint]]] = None

    def add_fiber(self, constraint: ConstraintPoint) -> Fiber:
        """Create a new fiber over a constraint point."""
        fiber = Fiber(base_point=constraint)
        self.fibers[constraint._hash] = fiber
        return fiber

    def get_fiber(self, constraint: ConstraintPoint) -> Optional[Fiber]:
        """Get the fiber over a constraint point."""
        return self.fibers.get(constraint._hash)

    def set_expand(self, fn: Callable[[ConstraintPoint], TextPoint]) -> None:
        """Set the expand function (section of the bundle)."""
        self._expand_fn = fn

    def set_reduce(self, fn: Callable[[TextPoint], Optional[ConstraintPoint]]) -> None:
        """Set the reduce function (projection of the bundle)."""
        self._reduce_fn = fn

    def expand(self, constraint: ConstraintPoint) -> TextPoint:
        """
        Expand a constraint to text (section σ: C → T).

        This is a section of the fiber bundle - it selects one
        canonical text representation for each constraint.
        """
        if self._expand_fn is None:
            # Default expansion: use canonical form
            return TextPoint(text=constraint.canonical_form, style="formal")
        return self._expand_fn(constraint)

    def reduce(self, text: TextPoint) -> Optional[ConstraintPoint]:
        """
        Reduce text to a constraint (projection π: T → C).

        Returns None if the text has no grounding (hallucination).
        """
        if self._reduce_fn is None:
            return None
        return self._reduce_fn(text)

    def project(self, text: TextPoint) -> Tuple[ProjectionStatus, Optional[ConstraintPoint]]:
        """
        Full projection with status information.

        Returns:
            Tuple of (status, constraint or None)
        """
        constraint = self.reduce(text)

        if constraint is None:
            return ProjectionStatus.HALLUCINATED, None

        # Verify the constraint exists in our fibers
        fiber = self.get_fiber(constraint)
        if fiber is None:
            return ProjectionStatus.HALLUCINATED, None

        return ProjectionStatus.GROUNDED, constraint

    def verify_identity(self, constraint: ConstraintPoint) -> bool:
        """
        Verify the fundamental identity: c = reduce(expand(c))

        This is the core correctness property of the manifold.
        """
        text = self.expand(constraint)
        recovered = self.reduce(text)

        if recovered is None:
            return False

        return recovered == constraint


@dataclass
class ExpandReduceManifold:
    """
    The complete Expand/Reduce Manifold.

    This is the topological structure that ensures text and constraints
    are in bijective correspondence. It's the geometric formalization
    of "constraint-preserving text generation."

    Key properties:
        1. BIJECTION: Every constraint has equivalent text representations
        2. IDENTITY: reduce(expand(c)) = c
        3. GROUNDING: Text without constraint grounding doesn't exist
        4. FIBER STRUCTURE: Equivalent texts form fibers over constraints
    """

    bundle: FiberBundle = field(default_factory=FiberBundle)
    _registered_constraints: Set[str] = field(default_factory=set)

    def register_constraint(self, constraint: ConstraintPoint) -> Fiber:
        """
        Register a constraint in the manifold.

        This creates a fiber over the constraint, making it available
        for text generation.
        """
        self._registered_constraints.add(constraint._hash)
        return self.bundle.add_fiber(constraint)

    def register_text(
        self,
        text: TextPoint,
        constraint: ConstraintPoint
    ) -> bool:
        """
        Register a text as a valid representation of a constraint.

        Adds the text to the fiber over the constraint.
        Returns False if the constraint isn't registered.
        """
        fiber = self.bundle.get_fiber(constraint)
        if fiber is None:
            return False
        fiber.add_text(text)
        return True

    def expand(self, constraint: ConstraintPoint) -> TextPoint:
        """Generate text from constraint."""
        return self.bundle.expand(constraint)

    def reduce(self, text: TextPoint) -> Optional[ConstraintPoint]:
        """Extract constraint from text."""
        return self.bundle.reduce(text)

    def is_grounded(self, text: TextPoint) -> bool:
        """Check if text has constraint grounding."""
        status, _ = self.bundle.project(text)
        return status == ProjectionStatus.GROUNDED

    def is_hallucination(self, text: TextPoint) -> bool:
        """Check if text is a hallucination (no grounding)."""
        status, _ = self.bundle.project(text)
        return status == ProjectionStatus.HALLUCINATED

    def verify_roundtrip(self, constraint: ConstraintPoint) -> bool:
        """Verify c = reduce(expand(c))."""
        return self.bundle.verify_identity(constraint)

    def get_equivalent_texts(self, constraint: ConstraintPoint) -> Set[TextPoint]:
        """Get all valid text representations of a constraint."""
        fiber = self.bundle.get_fiber(constraint)
        if fiber is None:
            return set()
        return fiber.text_points.copy()

    def fiber_statistics(self) -> Dict[str, Any]:
        """Get statistics about the fiber bundle structure."""
        total_fibers = len(self.bundle.fibers)
        total_texts = sum(f.cardinality for f in self.bundle.fibers.values())
        empty_fibers = sum(1 for f in self.bundle.fibers.values() if f.is_empty())

        return {
            "total_constraints": total_fibers,
            "total_texts": total_texts,
            "empty_fibers": empty_fibers,
            "average_fiber_size": total_texts / total_fibers if total_fibers > 0 else 0,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# The Fiber Bundle Theorem
# ═══════════════════════════════════════════════════════════════════════════════
#
# The text space T is a fiber bundle over constraint space C:
#
#     T ──π──▶ C
#
# Where:
#     - π (reduce) is the projection
#     - Each fiber π⁻¹(c) is the set of valid texts for constraint c
#     - A section σ: C → T (expand) picks one text per constraint
#
# The IDENTITY PROPERTY:
#
#     π ∘ σ = id_C
#
# In other words:
#
#     reduce(expand(c)) = c
#
# This is not a property we hope text has.
# This is a property we CONSTRUCT the manifold to have.
#
# Hallucination = point in T with empty fiber
#              = floating text with no constraint grounding
#              = REJECTED by the manifold structure
#
# ═══════════════════════════════════════════════════════════════════════════════
