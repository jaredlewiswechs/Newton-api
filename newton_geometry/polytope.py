#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
CONSTRAINT POLYTOPE - The Shape of Possibility
════════════════════════════════════════════════════════════════════════════════

Every set of constraints defines a SHAPE in possibility space.

                        g (what reality allows)
                        ▲
                        │
                        │      ╱
                        │    ╱
                        │  ╱  f/g = 1
                        │╱    (boundary)
            ┌───────────┼───────────────────▶ f (what you attempt)
            │╲          │
            │  ╲        │
            │    ╲      │
            │ fin  ╲    │         finfr
            │        ╲  │      (impossible)
            │(allowed) ╲│
            │           ╲
            │            ╲

    Inside the polytope: computation executes
    Outside the polytope: state doesn't exist

The Fundamental Law:
    f/g ≤ 1  →  FIN (finite, allowed, executable)
    f/g > 1  →  FINFR (finite forbidden, impossible, rejected)

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Tuple, Set, FrozenSet
import math


class FeasibilityRegion(Enum):
    """The three regions of possibility space."""

    FIN = auto()      # f/g < 1: Inside the polytope, fully allowed
    BOUNDARY = auto() # f/g = 1: On the edge, marginal execution
    FINFR = auto()    # f/g > 1: Outside the polytope, impossible


@dataclass(frozen=True)
class Boundary:
    """
    A single boundary constraint in the polytope.

    Each boundary is defined by f (attempt) and g (reality):
        - f: What you're trying to do (numerator)
        - g: What reality allows (denominator)
        - The ratio f/g determines feasibility
    """

    name: str
    f: float  # Attempt dimension
    g: float  # Reality dimension
    description: str = ""

    def __post_init__(self):
        if self.g <= 0:
            raise ValueError(f"Reality dimension g must be positive, got {self.g}")
        if self.f < 0:
            raise ValueError(f"Attempt dimension f must be non-negative, got {self.f}")

    @property
    def ratio(self) -> float:
        """The f/g ratio determining feasibility."""
        return self.f / self.g

    @property
    def region(self) -> FeasibilityRegion:
        """Which region this boundary places us in."""
        r = self.ratio
        if r < 1.0 - 1e-10:  # Allow for floating point tolerance
            return FeasibilityRegion.FIN
        elif r > 1.0 + 1e-10:
            return FeasibilityRegion.FINFR
        else:
            return FeasibilityRegion.BOUNDARY

    @property
    def margin(self) -> float:
        """How much margin we have (negative if over boundary)."""
        return 1.0 - self.ratio

    def is_satisfied(self) -> bool:
        """True if we're inside or on the boundary."""
        return self.region != FeasibilityRegion.FINFR


@dataclass
class ConstraintPolytope:
    """
    The complete constraint polytope in N-dimensional space.

    A polytope is the intersection of multiple half-spaces, where each
    constraint boundary defines one half-space. A point is inside the
    polytope if and only if ALL constraints are satisfied.

    The geometry:
        - Each Boundary defines a hyperplane f/g = 1
        - The feasible region is the intersection of all half-spaces f/g ≤ 1
        - A point outside ANY boundary is outside the polytope

    Newton's Law applied to geometry:
        1 == 1 → inside the polytope → execute
        1 != 1 → outside the polytope → reject
    """

    name: str
    boundaries: List[Boundary] = field(default_factory=list)
    _frozen: bool = field(default=False, repr=False)

    def add_boundary(self, boundary: Boundary) -> None:
        """Add a constraint boundary to the polytope."""
        if self._frozen:
            raise RuntimeError("Cannot modify frozen polytope")
        self.boundaries.append(boundary)

    def freeze(self) -> ConstraintPolytope:
        """Freeze the polytope, preventing further modifications."""
        self._frozen = True
        return self

    @property
    def dimension(self) -> int:
        """Number of constraint dimensions."""
        return len(self.boundaries)

    @property
    def region(self) -> FeasibilityRegion:
        """
        The overall feasibility region.

        Rules:
            - If ANY boundary is FINFR, entire polytope is FINFR
            - If ANY boundary is BOUNDARY and none are FINFR, result is BOUNDARY
            - Only if ALL boundaries are FIN, result is FIN
        """
        if not self.boundaries:
            return FeasibilityRegion.FIN  # No constraints = always allowed

        regions = [b.region for b in self.boundaries]

        if FeasibilityRegion.FINFR in regions:
            return FeasibilityRegion.FINFR
        elif FeasibilityRegion.BOUNDARY in regions:
            return FeasibilityRegion.BOUNDARY
        else:
            return FeasibilityRegion.FIN

    @property
    def max_ratio(self) -> float:
        """The maximum f/g ratio across all boundaries."""
        if not self.boundaries:
            return 0.0
        return max(b.ratio for b in self.boundaries)

    @property
    def min_margin(self) -> float:
        """The minimum margin across all boundaries (most constrained)."""
        if not self.boundaries:
            return float('inf')
        return min(b.margin for b in self.boundaries)

    @property
    def binding_constraints(self) -> List[Boundary]:
        """Constraints that are at or near the boundary (margin < 0.1)."""
        return [b for b in self.boundaries if b.margin < 0.1]

    @property
    def violated_constraints(self) -> List[Boundary]:
        """Constraints that are violated (f/g > 1)."""
        return [b for b in self.boundaries if b.region == FeasibilityRegion.FINFR]

    def is_feasible(self) -> bool:
        """True if the current state is inside the polytope."""
        return self.region != FeasibilityRegion.FINFR

    def evaluate(self) -> Tuple[bool, FeasibilityRegion, Dict[str, Any]]:
        """
        Full evaluation of the polytope state.

        Returns:
            Tuple of:
                - feasible: bool (can we execute?)
                - region: FeasibilityRegion (where are we?)
                - details: Dict with margin info and violations
        """
        feasible = self.is_feasible()
        region = self.region

        details = {
            "dimension": self.dimension,
            "max_ratio": self.max_ratio,
            "min_margin": self.min_margin,
            "binding_count": len(self.binding_constraints),
            "violated_count": len(self.violated_constraints),
            "boundaries": [
                {
                    "name": b.name,
                    "f": b.f,
                    "g": b.g,
                    "ratio": b.ratio,
                    "margin": b.margin,
                    "region": b.region.name,
                    "satisfied": b.is_satisfied(),
                }
                for b in self.boundaries
            ],
        }

        return feasible, region, details

    def project_to_boundary(self, boundary_name: str) -> Optional[float]:
        """
        Calculate how much f needs to decrease to reach f/g = 1 for a boundary.

        Returns None if boundary not found, 0 if already feasible,
        or the required reduction in f to make the constraint feasible.
        """
        for b in self.boundaries:
            if b.name == boundary_name:
                if b.is_satisfied():
                    return 0.0
                # f/g > 1, need to reduce f to f' where f'/g = 1
                # f' = g, so reduction = f - g
                return b.f - b.g
        return None

    def __contains__(self, point: Dict[str, float]) -> bool:
        """
        Check if a point (f, g values for each dimension) is in the polytope.

        Point should be a dict mapping boundary names to (f, g) tuples.
        """
        for b in self.boundaries:
            if b.name in point:
                f, g = point[b.name]
                if f / g > 1.0 + 1e-10:
                    return False
        return True


def create_polytope_from_constraints(
    name: str,
    constraints: List[Dict[str, Any]]
) -> ConstraintPolytope:
    """
    Factory function to create a polytope from constraint specifications.

    Each constraint dict should have:
        - name: str
        - f: float (attempt dimension)
        - g: float (reality dimension)
        - description: str (optional)
    """
    polytope = ConstraintPolytope(name=name)

    for c in constraints:
        boundary = Boundary(
            name=c["name"],
            f=c["f"],
            g=c["g"],
            description=c.get("description", ""),
        )
        polytope.add_boundary(boundary)

    return polytope.freeze()


# ═══════════════════════════════════════════════════════════════════════════════
# The Fundamental Theorem of the Constraint Polytope
# ═══════════════════════════════════════════════════════════════════════════════
#
# For any computation C with constraints {c₁, c₂, ..., cₙ}:
#
#     C is executable ⟺ ∀i: fᵢ/gᵢ ≤ 1
#
# This is not a check we perform AFTER computation.
# This IS the definition of what computation means.
#
# The polytope doesn't constrain the computer.
# The polytope IS the computer.
#
# ═══════════════════════════════════════════════════════════════════════════════
