#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
GOVERNANCE LATTICE - Monotonic Safety
════════════════════════════════════════════════════════════════════════════════

            ┌─────────────────────────────────────┐
            │              REFUSE                  │
            │         (maximum safety)             │
            └──────────────┬──────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        ┌───────────┐            ┌───────────┐
        │   DEFER   │            │    ASK    │
        │(redirect) │            │ (clarify) │
        └─────┬─────┘            └─────┬─────┘
              │                        │
              └───────────┬────────────┘
                          │
                          ▼
                   ┌───────────┐
                   │  ANSWER   │
                   │(generate) │
                   └───────────┘
                          │
              ════════════╧════════════
                    (minimum safety)


    RULE: You can only move UP this lattice, never down.

    If governance says DEFER and constraints say ANSWER:
        Final decision = DEFER ⊔ ANSWER = DEFER

    Safety is MONOTONIC.

The lattice structure ensures:
    1. Any join (⊔) of decisions goes to the SAFER option
    2. Any meet (⊓) of decisions goes to the LESS SAFE option (for analysis only)
    3. REFUSE is the top element (⊤)
    4. ANSWER is the bottom element (⊥)

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Dict, Any, Optional, Set, FrozenSet, Tuple
from .simplex import Decision


class SafetyLevel(IntEnum):
    """
    Safety levels in the governance lattice.

    Higher value = higher safety = closer to REFUSE.
    This is an IntEnum so we can compare and order levels.
    """

    MINIMUM = 0   # ANSWER (bottom of lattice)
    LOW = 1       # Slightly above ANSWER
    MEDIUM = 2    # Between ANSWER and DEFER/ASK
    HIGH = 3      # DEFER/ASK level
    MAXIMUM = 4   # REFUSE (top of lattice)

    @classmethod
    def from_decision(cls, decision: Decision) -> SafetyLevel:
        """Map a decision to its safety level."""
        mapping = {
            Decision.ANSWER: cls.MINIMUM,
            Decision.DEFER: cls.HIGH,
            Decision.ASK: cls.HIGH,
            Decision.REFUSE: cls.MAXIMUM,
        }
        return mapping[decision]


@dataclass(frozen=True)
class LatticeNode:
    """
    A node in the governance lattice.

    Each node represents a possible decision with its safety level
    and relationships to other nodes.
    """

    decision: Decision
    safety_level: SafetyLevel
    description: str = ""

    def __lt__(self, other: LatticeNode) -> bool:
        """A node is 'less than' another if it's less safe."""
        if not isinstance(other, LatticeNode):
            return NotImplemented
        return self.safety_level < other.safety_level

    def __le__(self, other: LatticeNode) -> bool:
        """A node is 'less than or equal' if equally or less safe."""
        if not isinstance(other, LatticeNode):
            return NotImplemented
        return self.safety_level <= other.safety_level

    def covers(self, other: LatticeNode) -> bool:
        """
        True if this node covers the other in the lattice.

        A covers B if A > B and there's no C where A > C > B.
        """
        if self.safety_level <= other.safety_level:
            return False

        # Check for immediate coverage
        level_diff = self.safety_level - other.safety_level
        return level_diff == 1 or (
            # REFUSE covers both DEFER and ASK
            self.decision == Decision.REFUSE and
            other.decision in (Decision.DEFER, Decision.ASK)
        )


@dataclass
class GovernanceLattice:
    """
    The complete governance lattice for decision safety.

    This implements a bounded lattice with:
        - Top element (⊤): REFUSE
        - Bottom element (⊥): ANSWER
        - Join (⊔): Safer decision (supremum)
        - Meet (⊓): Less safe decision (infimum)

    The key property: MONOTONICITY
        Once a decision is escalated, it cannot be de-escalated.
        Safety only goes UP in this system.
    """

    # The lattice nodes (fixed structure)
    _nodes: Dict[Decision, LatticeNode] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the lattice structure."""
        self._nodes = {
            Decision.ANSWER: LatticeNode(
                decision=Decision.ANSWER,
                safety_level=SafetyLevel.MINIMUM,
                description="Generate a response (minimum safety)",
            ),
            Decision.DEFER: LatticeNode(
                decision=Decision.DEFER,
                safety_level=SafetyLevel.HIGH,
                description="Redirect to authoritative source (high safety)",
            ),
            Decision.ASK: LatticeNode(
                decision=Decision.ASK,
                safety_level=SafetyLevel.HIGH,
                description="Request clarification (high safety)",
            ),
            Decision.REFUSE: LatticeNode(
                decision=Decision.REFUSE,
                safety_level=SafetyLevel.MAXIMUM,
                description="Decline to engage (maximum safety)",
            ),
        }

    @property
    def top(self) -> LatticeNode:
        """The top element (⊤) of the lattice: REFUSE."""
        return self._nodes[Decision.REFUSE]

    @property
    def bottom(self) -> LatticeNode:
        """The bottom element (⊥) of the lattice: ANSWER."""
        return self._nodes[Decision.ANSWER]

    def node(self, decision: Decision) -> LatticeNode:
        """Get the lattice node for a decision."""
        return self._nodes[decision]

    def join(self, a: Decision, b: Decision) -> Decision:
        """
        Compute the join (supremum, ⊔) of two decisions.

        The join is the SAFER of the two options.
        This is the operation used when combining constraints.

        Rules:
            - REFUSE ⊔ X = REFUSE (for any X)
            - DEFER ⊔ ASK = either (both are HIGH)
            - X ⊔ ANSWER = X (for any X)
        """
        node_a = self._nodes[a]
        node_b = self._nodes[b]

        if node_a.safety_level >= node_b.safety_level:
            return a
        else:
            return b

    def meet(self, a: Decision, b: Decision) -> Decision:
        """
        Compute the meet (infimum, ⊓) of two decisions.

        The meet is the LESS SAFE of the two options.
        This is used for analysis, NOT for actual governance.

        Rules:
            - ANSWER ⊓ X = ANSWER (for any X)
            - DEFER ⊓ ASK = either (both are HIGH)
            - X ⊓ REFUSE = X (for any X)
        """
        node_a = self._nodes[a]
        node_b = self._nodes[b]

        if node_a.safety_level <= node_b.safety_level:
            return a
        else:
            return b

    def can_escalate(self, from_decision: Decision, to_decision: Decision) -> bool:
        """
        Check if escalation from one decision to another is valid.

        Escalation is only valid if moving UP the lattice.
        """
        from_node = self._nodes[from_decision]
        to_node = self._nodes[to_decision]
        return to_node.safety_level > from_node.safety_level

    def escalate(self, current: Decision, reason: str = "") -> Tuple[Decision, str]:
        """
        Escalate a decision one level up the lattice.

        Returns the new decision and the escalation path.
        """
        current_node = self._nodes[current]

        if current == Decision.REFUSE:
            return Decision.REFUSE, "Already at maximum safety"

        if current == Decision.ANSWER:
            # ANSWER can escalate to either DEFER or ASK
            # Default to DEFER for safety
            return Decision.DEFER, f"ANSWER → DEFER: {reason}"

        if current in (Decision.DEFER, Decision.ASK):
            return Decision.REFUSE, f"{current.name} → REFUSE: {reason}"

        return current, "Unknown escalation path"

    def governance_join(self, decisions: List[Decision]) -> Decision:
        """
        Combine multiple governance decisions using join.

        The result is the SAFEST of all decisions.
        This is the core governance operation.

        Example:
            governance_join([ANSWER, DEFER, ANSWER]) = DEFER
            governance_join([ANSWER, REFUSE]) = REFUSE
        """
        if not decisions:
            return Decision.ANSWER  # Empty defaults to bottom

        result = decisions[0]
        for d in decisions[1:]:
            result = self.join(result, d)
        return result

    def compare(self, a: Decision, b: Decision) -> int:
        """
        Compare two decisions for safety ordering.

        Returns:
            -1 if a is less safe than b
             0 if a and b are equally safe
            +1 if a is safer than b
        """
        node_a = self._nodes[a]
        node_b = self._nodes[b]

        if node_a.safety_level < node_b.safety_level:
            return -1
        elif node_a.safety_level > node_b.safety_level:
            return 1
        else:
            return 0

    def is_safe_transition(self, from_decision: Decision, to_decision: Decision) -> bool:
        """
        Check if a transition is safe (monotonically increasing safety).

        Returns True if the transition maintains or increases safety.
        """
        return self.compare(from_decision, to_decision) <= 0

    def all_above(self, decision: Decision) -> Set[Decision]:
        """Get all decisions strictly above the given decision in the lattice."""
        node = self._nodes[decision]
        return {
            d for d, n in self._nodes.items()
            if n.safety_level > node.safety_level
        }

    def all_below(self, decision: Decision) -> Set[Decision]:
        """Get all decisions strictly below the given decision in the lattice."""
        node = self._nodes[decision]
        return {
            d for d, n in self._nodes.items()
            if n.safety_level < node.safety_level
        }

    def covering_relation(self) -> List[Tuple[Decision, Decision]]:
        """
        Get the covering relation of the lattice.

        Returns pairs (a, b) where a covers b (a is immediately above b).
        """
        relations = []
        for d1, n1 in self._nodes.items():
            for d2, n2 in self._nodes.items():
                if n1.covers(n2):
                    relations.append((d1, d2))
        return relations

    def hasse_diagram(self) -> str:
        """
        Generate an ASCII Hasse diagram of the lattice.
        """
        return """
            ┌──────────┐
            │  REFUSE  │
            │   (⊤)    │
            └────┬─────┘
          ┌──────┴──────┐
          │             │
     ┌────┴────┐   ┌────┴────┐
     │  DEFER  │   │   ASK   │
     └────┬────┘   └────┬────┘
          │             │
          └──────┬──────┘
            ┌────┴────┐
            │ ANSWER  │
            │   (⊥)   │
            └─────────┘
        """


# ═══════════════════════════════════════════════════════════════════════════════
# The Monotonicity Theorem
# ═══════════════════════════════════════════════════════════════════════════════
#
# For any sequence of governance decisions d₁, d₂, ..., dₙ:
#
#     final = d₁ ⊔ d₂ ⊔ ... ⊔ dₙ
#
# The final decision is AT LEAST as safe as any individual decision.
#
# This is not a policy we enforce.
# This is a mathematical property of the lattice structure.
#
# Safety cannot decrease. By construction. By geometry.
#
# ═══════════════════════════════════════════════════════════════════════════════
