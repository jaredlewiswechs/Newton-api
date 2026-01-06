#!/usr/bin/env python3
"""
===============================================================================
NEWTON TLM - PARADOX DETECTION
Guardrail phase for detecting logical contradictions before commit.
===============================================================================

In this kernel, a "Paradox" is defined as a Relationship Contradiction:
- Internal: Same transaction asserts conflicting relations between nodes
- External: Transaction contradicts existing relations in the immutable graph

This prevents "Hallucination Creep" in larger AI systems by maintaining
logical consistency in the knowledge ledger.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import networkx as nx

if TYPE_CHECKING:
    from .transaction import Transaction


class ParadoxError(Exception):
    """
    Exception raised when a paradox is detected.

    This exception halts the transaction before it can corrupt the ledger.

    Attributes:
        paradox_type: Type of paradox ("internal" or "external")
        source: Source node ID
        target: Target node ID
        existing_relation: The relation already established
        conflicting_relation: The conflicting relation attempted
        message: Human-readable description of the contradiction
    """

    def __init__(
        self,
        paradox_type: str,
        source: str,
        target: str,
        existing_relation: str,
        conflicting_relation: str,
        message: Optional[str] = None
    ):
        self.paradox_type = paradox_type
        self.source = source
        self.target = target
        self.existing_relation = existing_relation
        self.conflicting_relation = conflicting_relation

        if message is None:
            message = (
                f"PARADOX ({paradox_type}): {source} cannot be both "
                f"'{existing_relation}' AND '{conflicting_relation}' to {target}"
            )
        self.message = message
        super().__init__(self.message)


@dataclass
class ParadoxResult:
    """
    Result of paradox detection scan.

    Attributes:
        has_paradox: Whether any paradox was detected
        paradox_type: Type of paradox if found ("internal", "external", or None)
        details: List of contradiction details
        source: Source node ID of first contradiction
        target: Target node ID of first contradiction
        existing_relation: The relation already established
        conflicting_relation: The conflicting relation attempted
    """
    has_paradox: bool = False
    paradox_type: Optional[str] = None
    details: List[str] = field(default_factory=list)
    source: Optional[str] = None
    target: Optional[str] = None
    existing_relation: Optional[str] = None
    conflicting_relation: Optional[str] = None

    def to_error(self) -> Optional[ParadoxError]:
        """
        Convert result to a ParadoxError if paradox was detected.

        Returns:
            ParadoxError if has_paradox is True, None otherwise
        """
        if not self.has_paradox:
            return None
        return ParadoxError(
            paradox_type=self.paradox_type or "unknown",
            source=self.source or "unknown",
            target=self.target or "unknown",
            existing_relation=self.existing_relation or "unknown",
            conflicting_relation=self.conflicting_relation or "unknown",
            message="; ".join(self.details) if self.details else None
        )


class ParadoxDetector:
    """
    Detects logical contradictions in transactions before commit.

    This class implements the PARADOX phase of the Newton TLM cycle,
    serving as a guardrail against contradictory knowledge entering
    the immutable ledger.

    The detector checks for two types of contradictions:
    1. Internal: Conflicts within the transaction itself
    2. External: Conflicts between transaction and existing graph state

    Example:
        >>> detector = ParadoxDetector(graph)
        >>> result = detector.detect(transaction)
        >>> if result.has_paradox:
        ...     raise result.to_error()
    """

    def __init__(self, graph: nx.DiGraph):
        """
        Initialize the paradox detector.

        Args:
            graph: The immutable graph to check against
        """
        self.graph = graph

    def detect_internal(self, tx: "Transaction") -> ParadoxResult:
        """
        Detect contradictions within a single transaction.

        Scans for edges in the transaction that assert different relations
        between the same source-target pair.

        Args:
            tx: Transaction to scan

        Returns:
            ParadoxResult with detection outcome

        Example:
            If tx contains:
              - (A, B, "is_safe")
              - (A, B, "is_unsafe")
            This is an internal paradox.
        """
        result = ParadoxResult()
        seen_pairs: Dict[Tuple[str, str], str] = {}

        for source, target, relation in tx.edges:
            pair = (source, target)
            if pair in seen_pairs:
                existing = seen_pairs[pair]
                if existing != relation:
                    result.has_paradox = True
                    result.paradox_type = "internal"
                    result.source = source
                    result.target = target
                    result.existing_relation = existing
                    result.conflicting_relation = relation
                    result.details.append(
                        f"PARADOX (internal): {source} cannot be both "
                        f"'{existing}' AND '{relation}' to {target}"
                    )
                    return result
            seen_pairs[pair] = relation

        return result

    def detect_external(self, tx: "Transaction") -> ParadoxResult:
        """
        Detect contradictions between transaction and existing graph.

        Scans for edges in the transaction that contradict relations
        already committed to the immutable graph ledger.

        Args:
            tx: Transaction to scan

        Returns:
            ParadoxResult with detection outcome

        Example:
            If graph contains: A --[is_verified]--> B
            And tx contains:   A --[is_banned]--> B
            This is an external paradox.
        """
        result = ParadoxResult()

        for source, target, new_relation in tx.edges:
            if self.graph.has_edge(source, target):
                edge_data = self.graph.edges[source, target]
                existing_relation = edge_data.get("type")

                if existing_relation is not None and existing_relation != new_relation:
                    result.has_paradox = True
                    result.paradox_type = "external"
                    result.source = source
                    result.target = target
                    result.existing_relation = existing_relation
                    result.conflicting_relation = new_relation
                    result.details.append(
                        f"PARADOX (ledger): {source} is known as "
                        f"'{existing_relation}' to {target}, but Tx claims '{new_relation}'"
                    )
                    return result

        return result

    def detect(self, tx: "Transaction") -> ParadoxResult:
        """
        Run full paradox detection on a transaction.

        Checks for both internal and external contradictions.
        Internal contradictions are checked first.

        Args:
            tx: Transaction to validate

        Returns:
            ParadoxResult with detection outcome

        Raises:
            ParadoxError: If raise_on_paradox=True and paradox detected
        """
        # Check internal contradictions first
        internal_result = self.detect_internal(tx)
        if internal_result.has_paradox:
            return internal_result

        # Check external contradictions
        external_result = self.detect_external(tx)
        if external_result.has_paradox:
            return external_result

        # No paradox found
        return ParadoxResult()

    def validate(self, tx: "Transaction") -> None:
        """
        Validate a transaction, raising ParadoxError if contradictions found.

        This is a convenience method that combines detection and error raising.

        Args:
            tx: Transaction to validate

        Raises:
            ParadoxError: If any paradox is detected
        """
        result = self.detect(tx)
        if result.has_paradox:
            error = result.to_error()
            if error:
                raise error
