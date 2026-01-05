#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
DECISION SIMPLEX - The Tetrahedron of Choice
════════════════════════════════════════════════════════════════════════════════

Four decisions. Three dimensions. One tetrahedron.

                    REFUSE
                      ╱╲
                     ╱  ╲
                    ╱    ╲
                   ╱      ╲
                  ╱   ◉    ╲        ← Every request maps to
                 ╱  (you    ╲         ONE point in this space
                ╱   are      ╲
               ╱    here)     ╲
              ╱                ╲
           DEFER ────────────── ASK
              ╲                ╱
               ╲              ╱
                ╲            ╱
                 ╲          ╱
                  ╲        ╱
                   ╲      ╱
                    ╲    ╱
                     ╲  ╱
                    ANSWER

Risk Level = Height in the tetrahedron:

    CRITICAL ─────────── REFUSE (apex)
        ▲
        │
    HIGH ──────────────── DEFER/ASK (mid-plane)
        │
        │
    MEDIUM ────────────── ANSWER possible
        │
        │
    LOW ───────────────── ANSWER (base)

Every request maps to exactly ONE point in this simplex.
The closest vertex determines the decision.

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Tuple
import math


class Decision(Enum):
    """The four vertices of the decision tetrahedron."""

    ANSWER = auto()  # Base: Generate a response
    DEFER = auto()   # Mid-left: Redirect to authoritative source
    ASK = auto()     # Mid-right: Request clarification
    REFUSE = auto()  # Apex: Decline to engage


class RiskLevel(Enum):
    """Risk levels corresponding to height in the simplex."""

    LOW = 0       # Base of tetrahedron
    MEDIUM = 1    # Lower-mid region
    HIGH = 2      # Mid-plane (DEFER/ASK level)
    CRITICAL = 3  # Apex (REFUSE level)

    @classmethod
    def from_score(cls, score: float) -> RiskLevel:
        """Convert a 0-1 risk score to a RiskLevel."""
        if score < 0.25:
            return cls.LOW
        elif score < 0.5:
            return cls.MEDIUM
        elif score < 0.75:
            return cls.HIGH
        else:
            return cls.CRITICAL


@dataclass(frozen=True)
class SimplexPoint:
    """
    A point in barycentric coordinates within the decision simplex.

    Barycentric coordinates: (answer, defer, ask, refuse)
    Constraints: all >= 0 and sum to 1.0

    The coordinate value represents "affinity" to each vertex.
    """

    answer: float
    defer: float
    ask: float
    refuse: float

    def __post_init__(self):
        # Validate barycentric constraints
        coords = [self.answer, self.defer, self.ask, self.refuse]
        if any(c < -1e-10 for c in coords):
            raise ValueError(f"Barycentric coordinates must be non-negative: {coords}")
        total = sum(coords)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Barycentric coordinates must sum to 1.0, got {total}")

    @property
    def dominant_decision(self) -> Decision:
        """The vertex with highest affinity."""
        coords = {
            Decision.ANSWER: self.answer,
            Decision.DEFER: self.defer,
            Decision.ASK: self.ask,
            Decision.REFUSE: self.refuse,
        }
        return max(coords, key=coords.get)

    @property
    def risk_level(self) -> RiskLevel:
        """
        Risk level based on height in the tetrahedron.

        Height is determined by REFUSE coordinate (apex)
        plus weighted contributions from DEFER and ASK.
        """
        # Height formula: refuse is at top, answer at bottom
        # DEFER and ASK are at mid-height
        height = self.refuse + 0.5 * (self.defer + self.ask)
        return RiskLevel.from_score(height)

    @property
    def confidence(self) -> float:
        """How confident are we in the dominant decision? (max coordinate)"""
        return max(self.answer, self.defer, self.ask, self.refuse)

    @property
    def ambiguity(self) -> float:
        """
        How ambiguous is the decision? (entropy-like measure)

        0 = completely certain (one vertex)
        1 = completely ambiguous (center of simplex)
        """
        coords = [self.answer, self.defer, self.ask, self.refuse]
        # Normalize and compute entropy
        entropy = 0.0
        for c in coords:
            if c > 1e-10:
                entropy -= c * math.log(c)
        # Normalize by max entropy (uniform = log(4))
        max_entropy = math.log(4)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def as_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            "answer": self.answer,
            "defer": self.defer,
            "ask": self.ask,
            "refuse": self.refuse,
        }

    @classmethod
    def from_decision(cls, decision: Decision) -> SimplexPoint:
        """Create a point at a specific vertex."""
        coords = {"answer": 0.0, "defer": 0.0, "ask": 0.0, "refuse": 0.0}
        coords[decision.name.lower()] = 1.0
        return cls(**coords)

    @classmethod
    def uniform(cls) -> SimplexPoint:
        """Create a point at the center of the simplex (maximum ambiguity)."""
        return cls(answer=0.25, defer=0.25, ask=0.25, refuse=0.25)


@dataclass
class DecisionSimplex:
    """
    The complete decision simplex for request classification.

    This implements the tetrahedron geometry where every request
    maps to exactly one point, and the dominant vertex determines
    the action taken.

    The simplex enforces:
        1. Mutual exclusivity: exactly one decision is taken
        2. Monotonicity: you can only move UP (toward safety)
        3. Determinism: same input → same point → same decision
    """

    # Vertex positions in 3D space (for visualization)
    _VERTICES = {
        Decision.ANSWER: (0.0, 0.0, 0.0),          # Origin (base)
        Decision.DEFER: (-1.0, 0.0, 1.0),          # Left, mid-height
        Decision.ASK: (1.0, 0.0, 1.0),             # Right, mid-height
        Decision.REFUSE: (0.0, 1.0, 2.0),          # Center, top
    }

    # Risk thresholds for automatic escalation
    risk_threshold_defer: float = 0.4
    risk_threshold_ask: float = 0.5
    risk_threshold_refuse: float = 0.75

    def classify(
        self,
        risk_score: float,
        clarity_score: float,
        capability_score: float,
    ) -> SimplexPoint:
        """
        Map input signals to a point in the decision simplex.

        Args:
            risk_score: 0-1 how risky is this request
            clarity_score: 0-1 how clear is the request
            capability_score: 0-1 can we actually help

        Returns:
            SimplexPoint with barycentric coordinates
        """
        # Validate inputs
        for name, score in [("risk", risk_score), ("clarity", clarity_score),
                            ("capability", capability_score)]:
            if not 0 <= score <= 1:
                raise ValueError(f"{name}_score must be in [0, 1], got {score}")

        # Compute affinities based on input signals
        refuse_affinity = risk_score ** 2  # Quadratic for safety
        ask_affinity = (1 - clarity_score) * (1 - refuse_affinity)
        defer_affinity = (1 - capability_score) * (1 - refuse_affinity) * clarity_score
        answer_affinity = capability_score * clarity_score * (1 - risk_score)

        # Normalize to barycentric coordinates
        total = refuse_affinity + ask_affinity + defer_affinity + answer_affinity
        if total < 1e-10:
            # Edge case: all affinities near zero, default to ASK
            return SimplexPoint(answer=0.0, defer=0.0, ask=1.0, refuse=0.0)

        return SimplexPoint(
            answer=answer_affinity / total,
            defer=defer_affinity / total,
            ask=ask_affinity / total,
            refuse=refuse_affinity / total,
        )

    def decide(
        self,
        risk_score: float,
        clarity_score: float,
        capability_score: float,
    ) -> Tuple[Decision, SimplexPoint]:
        """
        Make a decision based on input signals.

        Returns the Decision enum and the SimplexPoint for analysis.
        """
        point = self.classify(risk_score, clarity_score, capability_score)
        return point.dominant_decision, point

    def escalate(self, point: SimplexPoint, target: Decision) -> SimplexPoint:
        """
        Escalate a decision toward a safer vertex.

        In the governance lattice, you can only move UP:
            ANSWER → DEFER/ASK → REFUSE

        This transfers weight from lower vertices to the target.
        """
        if target == Decision.ANSWER:
            raise ValueError("Cannot escalate TO answer (can only escalate UP)")

        # Get current coordinates
        coords = point.as_dict()
        target_key = target.name.lower()

        # Determine what can be transferred (lower vertices)
        transferable = 0.0
        if target == Decision.REFUSE:
            # Can transfer from all lower vertices
            transferable = coords["answer"] + coords["defer"] + coords["ask"]
            coords["answer"] = 0.0
            coords["defer"] = 0.0
            coords["ask"] = 0.0
        elif target == Decision.DEFER:
            # Can only transfer from ANSWER
            transferable = coords["answer"]
            coords["answer"] = 0.0
        elif target == Decision.ASK:
            # Can only transfer from ANSWER
            transferable = coords["answer"]
            coords["answer"] = 0.0

        coords[target_key] += transferable

        return SimplexPoint(**coords)

    def distance_to_vertex(self, point: SimplexPoint, vertex: Decision) -> float:
        """
        Compute distance from point to a vertex in the simplex.

        Uses barycentric distance: d = 1 - coordinate_value
        """
        coords = point.as_dict()
        vertex_key = vertex.name.lower()
        return 1.0 - coords[vertex_key]

    def get_vertex_position(self, vertex: Decision) -> Tuple[float, float, float]:
        """Get 3D position of a vertex for visualization."""
        return self._VERTICES[vertex]

    def interpolate(
        self,
        point1: SimplexPoint,
        point2: SimplexPoint,
        t: float
    ) -> SimplexPoint:
        """
        Linear interpolation between two simplex points.

        Args:
            point1: Starting point
            point2: Ending point
            t: Interpolation parameter in [0, 1]

        Returns:
            Interpolated SimplexPoint
        """
        if not 0 <= t <= 1:
            raise ValueError(f"Interpolation parameter t must be in [0, 1], got {t}")

        c1 = point1.as_dict()
        c2 = point2.as_dict()

        return SimplexPoint(
            answer=(1 - t) * c1["answer"] + t * c2["answer"],
            defer=(1 - t) * c1["defer"] + t * c2["defer"],
            ask=(1 - t) * c1["ask"] + t * c2["ask"],
            refuse=(1 - t) * c1["refuse"] + t * c2["refuse"],
        )


# ═══════════════════════════════════════════════════════════════════════════════
# The Fundamental Theorem of the Decision Simplex
# ═══════════════════════════════════════════════════════════════════════════════
#
# For any request R:
#
#     ∃! p ∈ S³ : classify(R) = p
#
# (There exists exactly one point p in the 3-simplex S³)
#
# The decision is the closest vertex to p.
#
# This is not probabilistic. It's geometric.
# The simplex doesn't "choose" the decision.
# The simplex IS the decision space.
#
# ═══════════════════════════════════════════════════════════════════════════════
