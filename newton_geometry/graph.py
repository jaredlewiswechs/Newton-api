#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
COMPUTATION GRAPH - The Deterministic Path
════════════════════════════════════════════════════════════════════════════════

Request Types as Graph Nodes:

                            ┌─────────┐
                            │ HARMFUL │
                            └────┬────┘
                                 │
                                 │ (always)
                                 ▼
        ┌──────────────────── REFUSE ◀────────────────────┐
        │                        ▲                         │
        │                        │                         │
        │               ┌────────┴────────┐                │
        │               │                 │                │
   ┌────┴────┐    ┌─────┴─────┐    ┌──────┴─────┐    ┌────┴────┐
   │PERSONAL │    │  MEDICAL  │    │   LEGAL    │    │FINANCIAL│
   │  DATA   │    │  ADVICE   │    │  ADVICE    │    │ ADVICE  │
   └─────────┘    └─────┬─────┘    └──────┬─────┘    └────┬────┘
                        │                 │               │
                        └────────┬────────┘               │
                                 │                        │
                                 ▼                        ▼
                              DEFER ◀─────────────────────┘


   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │QUESTION │    │ OPINION │    │INSTRUCT │    │  CODE   │
   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                                 │
                                 ▼
                              ANSWER


                         ┌─────────┐
                         │ UNKNOWN │
                         └────┬────┘
                              │
                              ▼
                             ASK


Computation as Path Through the Graph:

    PATH CONSTRAINT:

    ∀ input: ∃! path through graph
    (For all inputs, exists exactly one path)

    No branching. No backtracking. No ambiguity.
    Deterministic finite automaton.

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Set, Tuple, Callable
from .simplex import Decision


class RequestType(Enum):
    """Categories of incoming requests."""

    # Harmful - always REFUSE
    HARMFUL = auto()

    # Professional domains - DEFER
    PERSONAL_DATA = auto()
    MEDICAL_ADVICE = auto()
    LEGAL_ADVICE = auto()
    FINANCIAL_ADVICE = auto()

    # Standard requests - ANSWER
    QUESTION = auto()
    OPINION = auto()
    INSTRUCTION = auto()
    CODE = auto()

    # Unknown - ASK
    UNKNOWN = auto()
    AMBIGUOUS = auto()

    @classmethod
    def default_decision(cls, request_type: RequestType) -> Decision:
        """Get the default decision for a request type."""
        mapping = {
            cls.HARMFUL: Decision.REFUSE,
            cls.PERSONAL_DATA: Decision.REFUSE,
            cls.MEDICAL_ADVICE: Decision.DEFER,
            cls.LEGAL_ADVICE: Decision.DEFER,
            cls.FINANCIAL_ADVICE: Decision.DEFER,
            cls.QUESTION: Decision.ANSWER,
            cls.OPINION: Decision.ANSWER,
            cls.INSTRUCTION: Decision.ANSWER,
            cls.CODE: Decision.ANSWER,
            cls.UNKNOWN: Decision.ASK,
            cls.AMBIGUOUS: Decision.ASK,
        }
        return mapping[request_type]


class ProcessingStage(Enum):
    """Stages in the computation pipeline."""

    CLASSIFY = auto()   # Determine request type
    TYPE = auto()       # Type-check the request
    RISK = auto()       # Assess risk level
    VERIFY = auto()     # Verify constraints
    DECIDE = auto()     # Make final decision
    OUTPUT = auto()     # Produce output


@dataclass(frozen=True)
class GraphNode:
    """
    A node in the computation graph.

    Each node represents either a request type or a processing stage.
    """

    id: str
    node_type: str  # "request", "stage", or "decision"
    data: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, GraphNode):
            return False
        return self.id == other.id


@dataclass(frozen=True)
class GraphEdge:
    """
    An edge in the computation graph.

    Each edge represents a valid transition between nodes.
    """

    source: str
    target: str
    condition: str = "always"  # Condition for taking this edge
    weight: float = 1.0

    def __hash__(self):
        return hash((self.source, self.target))


@dataclass
class PathResult:
    """
    The result of traversing the computation graph.

    Contains the path taken and the final decision.
    """

    path: List[str]
    decision: Decision
    stages_completed: List[ProcessingStage]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def length(self) -> int:
        return len(self.path)

    def add_step(self, node_id: str) -> None:
        self.path.append(node_id)

    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value


@dataclass
class ComputationGraph:
    """
    The deterministic computation graph.

    This implements the DFA (Deterministic Finite Automaton) structure
    where every input maps to exactly one path through the graph.

    Key properties:
        1. DETERMINISM: Same input → same path → same output
        2. COMPLETENESS: Every input has a valid path
        3. TERMINATION: Every path ends at a decision node
        4. NO BACKTRACKING: Once a node is visited, we don't return
    """

    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)
    _adjacency: Dict[str, List[GraphEdge]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the default graph structure."""
        self._build_default_graph()

    def _build_default_graph(self) -> None:
        """Build the default computation graph structure."""
        # Decision nodes
        for decision in Decision:
            self.add_node(GraphNode(
                id=f"decision_{decision.name}",
                node_type="decision",
                data={"decision": decision},
            ))

        # Request type nodes
        for req_type in RequestType:
            self.add_node(GraphNode(
                id=f"request_{req_type.name}",
                node_type="request",
                data={"request_type": req_type},
            ))

        # Processing stage nodes
        for stage in ProcessingStage:
            self.add_node(GraphNode(
                id=f"stage_{stage.name}",
                node_type="stage",
                data={"stage": stage},
            ))

        # Build edges based on the request type flow
        # HARMFUL → REFUSE
        self.add_edge(GraphEdge("request_HARMFUL", "decision_REFUSE", "always"))

        # PERSONAL_DATA → REFUSE
        self.add_edge(GraphEdge("request_PERSONAL_DATA", "decision_REFUSE", "always"))

        # Professional domains → DEFER
        for req_type in [RequestType.MEDICAL_ADVICE, RequestType.LEGAL_ADVICE,
                         RequestType.FINANCIAL_ADVICE]:
            self.add_edge(GraphEdge(
                f"request_{req_type.name}",
                "decision_DEFER",
                "always"
            ))

        # Standard requests → ANSWER
        for req_type in [RequestType.QUESTION, RequestType.OPINION,
                         RequestType.INSTRUCTION, RequestType.CODE]:
            self.add_edge(GraphEdge(
                f"request_{req_type.name}",
                "decision_ANSWER",
                "always"
            ))

        # Unknown/Ambiguous → ASK
        self.add_edge(GraphEdge("request_UNKNOWN", "decision_ASK", "always"))
        self.add_edge(GraphEdge("request_AMBIGUOUS", "decision_ASK", "always"))

        # Processing pipeline edges
        stages = [ProcessingStage.CLASSIFY, ProcessingStage.TYPE,
                  ProcessingStage.RISK, ProcessingStage.VERIFY,
                  ProcessingStage.DECIDE, ProcessingStage.OUTPUT]
        for i in range(len(stages) - 1):
            self.add_edge(GraphEdge(
                f"stage_{stages[i].name}",
                f"stage_{stages[i+1].name}",
                "always"
            ))

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = []
        self._adjacency[edge.source].append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_outgoing_edges(self, node_id: str) -> List[GraphEdge]:
        """Get all outgoing edges from a node."""
        return self._adjacency.get(node_id, [])

    def get_decision_node(self, decision: Decision) -> GraphNode:
        """Get the node for a specific decision."""
        return self.nodes[f"decision_{decision.name}"]

    def get_request_node(self, request_type: RequestType) -> GraphNode:
        """Get the node for a specific request type."""
        return self.nodes[f"request_{request_type.name}"]

    def classify_and_route(self, request_type: RequestType) -> PathResult:
        """
        Route a classified request through the graph.

        This is the main entry point for the computation.
        Returns the path taken and the final decision.
        """
        path = PathResult(
            path=[],
            decision=Decision.ANSWER,  # Default, will be overwritten
            stages_completed=[],
        )

        # Start at the request type node
        start_node_id = f"request_{request_type.name}"
        current = start_node_id
        path.add_step(current)

        # Follow edges until we reach a decision node
        visited = {current}
        max_steps = 100  # Safety limit

        for _ in range(max_steps):
            node = self.get_node(current)
            if node is None:
                break

            # Check if we've reached a decision
            if node.node_type == "decision":
                path.decision = node.data["decision"]
                break

            # Get outgoing edges
            edges = self.get_outgoing_edges(current)
            if not edges:
                # No outgoing edges - use default decision
                path.decision = RequestType.default_decision(request_type)
                break

            # Take the first valid edge (deterministic)
            next_edge = edges[0]  # In a DFA, there's exactly one valid edge
            current = next_edge.target

            if current in visited:
                # Cycle detected - shouldn't happen in valid graph
                raise RuntimeError(f"Cycle detected at node {current}")

            visited.add(current)
            path.add_step(current)

        return path

    def process_through_pipeline(
        self,
        input_data: Dict[str, Any]
    ) -> PathResult:
        """
        Process input through the full computation pipeline.

        This runs through all processing stages.
        """
        path = PathResult(
            path=[],
            decision=Decision.ANSWER,
            stages_completed=[],
        )

        stages = [
            ProcessingStage.CLASSIFY,
            ProcessingStage.TYPE,
            ProcessingStage.RISK,
            ProcessingStage.VERIFY,
            ProcessingStage.DECIDE,
            ProcessingStage.OUTPUT,
        ]

        for stage in stages:
            node_id = f"stage_{stage.name}"
            path.add_step(node_id)
            path.stages_completed.append(stage)

            # Stage-specific processing would go here
            path.add_metadata(f"{stage.name}_completed", True)

        return path

    def is_deterministic(self) -> bool:
        """
        Verify that the graph is deterministic.

        A graph is deterministic if every node has at most one
        outgoing edge per condition.
        """
        for node_id, edges in self._adjacency.items():
            # Group edges by condition
            conditions = {}
            for edge in edges:
                if edge.condition in conditions:
                    # Multiple edges with same condition = non-deterministic
                    return False
                conditions[edge.condition] = edge
        return True

    def is_complete(self) -> bool:
        """
        Verify that every request type has a path to a decision.
        """
        for req_type in RequestType:
            try:
                result = self.classify_and_route(req_type)
                if result.decision is None:
                    return False
            except Exception:
                return False
        return True

    def visualize_as_ascii(self) -> str:
        """Generate ASCII visualization of the graph."""
        return """
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   INPUT                                                 │
    │     │                                                   │
    │     ▼                                                   │
    │   ┌───┐    ┌───┐    ┌───┐    ┌───┐                     │
    │   │ C │───▶│ T │───▶│ R │───▶│ V │                     │
    │   │ L │    │ Y │    │ I │    │ E │                     │
    │   │ A │    │ P │    │ S │    │ R │                     │
    │   │ S │    │ E │    │ K │    │ I │                     │
    │   │ S │    │   │    │   │    │ F │                     │
    │   │ I │    │   │    │   │    │ Y │                     │
    │   │ F │    │   │    │   │    │   │                     │
    │   │ Y │    │   │    │   │    │   │                     │
    │   └─┬─┘    └─┬─┘    └─┬─┘    └─┬─┘                     │
    │     │        │        │        │                       │
    │     ▼        ▼        ▼        ▼                       │
    │   ┌───────────────────────────────┐                    │
    │   │         DECISION NODE         │                    │
    │   │    ┌───┬───┬───┬───┐         │                    │
    │   │    │ A │ D │ R │ ? │         │                    │
    │   │    │ N │ E │ E │ A │         │                    │
    │   │    │ S │ F │ F │ S │         │                    │
    │   │    │ W │ E │ U │ K │         │                    │
    │   │    │ E │ R │ S │   │         │                    │
    │   │    │ R │   │ E │   │         │                    │
    │   │    └─┬─┴─┬─┴─┬─┴─┬─┘         │                    │
    │   └──────┼───┼───┼───┼───────────┘                    │
    │          │   │   │   │                                 │
    │          ▼   ▼   ▼   ▼                                 │
    │       OUTPUT (exactly one edge taken)                  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
        """


# ═══════════════════════════════════════════════════════════════════════════════
# The Determinism Theorem
# ═══════════════════════════════════════════════════════════════════════════════
#
# For any input I:
#
#     ∃! path P : start ──P──▶ decision
#
# (There exists exactly one path from start to decision)
#
# This makes the computation:
#     - Deterministic: Same input → same output
#     - Traceable: Every decision has an audit path
#     - Verifiable: The path can be replayed and checked
#
# The graph IS the computer.
# The path IS the computation.
# The decision IS the output.
#
# ═══════════════════════════════════════════════════════════════════════════════
