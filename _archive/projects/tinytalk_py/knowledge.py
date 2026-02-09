"""
===============================================================================
 tinyTalk Knowledge System - Environmental Design for Learning
===============================================================================

"A computer can be less intimidating than a human teacher."
                                        - Apple Knowledge Navigator (1987)

The real insight: The computer removes social judgment from the learning loop.

    No embarrassment.
    No authority pressure.
    No fear of asking "dumb" questions.

That's not AI intelligence — that's environmental design.

Understanding is not something the system claims to have — it is something
the system enforces structurally.

    Not inside a brain.
    Not inside a model.
    Inside the environment.

This module implements Knowledge Navigation through Laws, not judgment.
The system is calm, bounded, patient, and procedural.

===============================================================================
"""

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, List, Set, Optional, Callable
from enum import Enum
import time
import copy

from .core import (
    Blueprint, Law, LawResult, LawViolation, FinClosure,
    field, forge, law, when, finfr, fin, ratio
)


# =============================================================================
# BOOK I: THE KNOWLEDGE LEXICON
# =============================================================================

class NavigationResult(Enum):
    """Outcomes of attempting to navigate knowledge space."""
    ALLOWED = "allowed"           # Learner can proceed
    BLOCKED = "blocked"           # Missing prerequisite (can be resolved)
    HOLD = "hold"                 # Pause suggested (fatigue, etc.)
    FORBIDDEN = "forbidden"       # Cannot exist in this state


class MasteryLevel(Enum):
    """Levels of concept mastery."""
    UNKNOWN = 0      # Never encountered
    EXPOSED = 1      # Seen but not practiced
    FAMILIAR = 2     # Some practice, not consistent
    PROFICIENT = 3   # Consistent success
    MASTERED = 4     # Automatic, can teach others


class ContentType(Enum):
    """Types of content that can exist at a knowledge node."""
    EXPLANATION_SHORT = "explanation_short"
    EXPLANATION_MEDIUM = "explanation_medium"
    EXPLANATION_LONG = "explanation_long"
    PRACTICE = "practice"
    EXAMPLE = "example"
    REAL_WORLD = "real_world"
    ANALOGY = "analogy"
    VIDEO = "video"
    STORY = "story"
    ASSESSMENT = "assessment"


# =============================================================================
# BOOK II: KNOWLEDGE EVENTS - The Ledger
# =============================================================================

@dataclass
class KnowledgeEvent:
    """
    A single event in the knowledge ledger.

    This is how progress becomes meaningful:
    - remember
    - rewind
    - branch
    - show growth

    No AI. Just history.
    """
    timestamp: float
    topic: str
    unit: int
    step: int
    action: str      # "attempt", "advance", "review", "blocked", "pause"
    outcome: str     # "success", "blocked", "paused", "failed"
    details: Dict[str, Any] = dataclass_field(default_factory=dict)

    def __repr__(self):
        ts = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"[{ts}] {self.action} {self.topic} U{self.unit}S{self.step} → {self.outcome}"


class KnowledgeLedger:
    """
    Immutable history of knowledge navigation.

    Example ledger:
        [10:01] Attempt step 2 → blocked (missing vocab)
        [10:05] Learned word "solve"
        [10:07] Advance step 2 → success
        [10:15] Attempt step 3 → success

    This lets the system remember without guessing.
    """

    def __init__(self):
        self._events: List[KnowledgeEvent] = []

    def record(
        self,
        topic: str,
        unit: int,
        step: int,
        action: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None
    ) -> KnowledgeEvent:
        """Record an event to the ledger."""
        event = KnowledgeEvent(
            timestamp=time.time(),
            topic=topic,
            unit=unit,
            step=step,
            action=action,
            outcome=outcome,
            details=details or {}
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        topic: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[float] = None
    ) -> List[KnowledgeEvent]:
        """Query events with optional filters."""
        events = self._events
        if topic:
            events = [e for e in events if e.topic == topic]
        if action:
            events = [e for e in events if e.action == action]
        if since:
            events = [e for e in events if e.timestamp >= since]
        return events

    def count_attempts(self, topic: str, unit: int, step: int) -> int:
        """Count attempts at a specific step."""
        return len([
            e for e in self._events
            if e.topic == topic and e.unit == unit and e.step == step
            and e.action == "attempt"
        ])

    def last_event(self) -> Optional[KnowledgeEvent]:
        """Get the most recent event."""
        return self._events[-1] if self._events else None

    def __len__(self):
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __repr__(self):
        return f"KnowledgeLedger({len(self._events)} events)"


# =============================================================================
# BOOK III: KNOWLEDGE STRUCTURE - The Content Graph
# =============================================================================

@dataclass
class ContentItem:
    """A single piece of content at a knowledge node."""
    content_type: ContentType
    title: str
    body: str
    duration_minutes: Optional[int] = None
    media_url: Optional[str] = None

    def __repr__(self):
        return f"ContentItem({self.content_type.value}: {self.title})"


@dataclass
class KnowledgeNode:
    """
    A node in the knowledge graph.

    The node IS strict about order.
    The node IS flexible about experience.

    Newton doesn't limit content.
    It only says: "You can't be here unless X and Y are true."
    """
    id: str
    name: str
    description: str
    prerequisites: List[str] = dataclass_field(default_factory=list)  # Node IDs
    vocabulary: Set[str] = dataclass_field(default_factory=set)        # Required words
    concepts: Set[str] = dataclass_field(default_factory=set)          # Concepts taught
    content: List[ContentItem] = dataclass_field(default_factory=list)

    def add_content(self, content_type: ContentType, title: str, body: str, **kwargs):
        """Add content to this node."""
        self.content.append(ContentItem(
            content_type=content_type,
            title=title,
            body=body,
            **kwargs
        ))

    def get_content(self, content_type: Optional[ContentType] = None) -> List[ContentItem]:
        """Get content, optionally filtered by type."""
        if content_type:
            return [c for c in self.content if c.content_type == content_type]
        return self.content

    def __repr__(self):
        return f"KnowledgeNode({self.id}: {self.name}, {len(self.content)} items)"


class KnowledgeGraph:
    """
    A directed graph of knowledge nodes.

    The graph is strict.
    The content is rich.

    You can explore, retry, detour, pause, go deeper by choice.
    The system is strict about order, but flexible about experience.
    """

    def __init__(self, topic: str):
        self.topic = topic
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._units: Dict[int, List[str]] = {}  # unit -> [node_ids]

    def add_node(
        self,
        node_id: str,
        name: str,
        description: str,
        unit: int,
        prerequisites: Optional[List[str]] = None,
        vocabulary: Optional[Set[str]] = None,
        concepts: Optional[Set[str]] = None
    ) -> KnowledgeNode:
        """Add a node to the graph."""
        node = KnowledgeNode(
            id=node_id,
            name=name,
            description=description,
            prerequisites=prerequisites or [],
            vocabulary=vocabulary or set(),
            concepts=concepts or set()
        )
        self._nodes[node_id] = node

        if unit not in self._units:
            self._units[unit] = []
        self._units[unit].append(node_id)

        return node

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_unit_nodes(self, unit: int) -> List[KnowledgeNode]:
        """Get all nodes in a unit, in order."""
        node_ids = self._units.get(unit, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def get_prerequisites(self, node_id: str) -> List[KnowledgeNode]:
        """Get prerequisite nodes for a node."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[pid] for pid in node.prerequisites if pid in self._nodes]

    def get_required_vocabulary(self, node_id: str) -> Set[str]:
        """
        Get all vocabulary required for a node.

        This gathers vocabulary from all prerequisite nodes recursively,
        but NOT from the current node itself (that's what you learn there).
        """
        node = self._nodes.get(node_id)
        if not node:
            return set()

        vocab = set()
        visited = set()

        def gather_prereq_vocab(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            prereq_node = self._nodes.get(nid)
            if prereq_node:
                vocab.update(prereq_node.vocabulary)
                for pid in prereq_node.prerequisites:
                    gather_prereq_vocab(pid)

        # Gather vocabulary from prerequisites only
        for prereq_id in node.prerequisites:
            gather_prereq_vocab(prereq_id)

        return vocab

    def get_required_concepts(self, node_id: str) -> Set[str]:
        """
        Get all concepts required for a node.

        This gathers concepts from all prerequisite nodes recursively,
        but NOT from the current node itself (that's what you learn there).
        """
        node = self._nodes.get(node_id)
        if not node:
            return set()

        concepts = set()
        visited = set()

        def gather_prereq_concepts(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            prereq_node = self._nodes.get(nid)
            if prereq_node:
                concepts.update(prereq_node.concepts)
                for pid in prereq_node.prerequisites:
                    gather_prereq_concepts(pid)

        # Gather concepts from prerequisites only
        for prereq_id in node.prerequisites:
            gather_prereq_concepts(prereq_id)

        return concepts

    def units(self) -> List[int]:
        """Get list of unit numbers."""
        return sorted(self._units.keys())

    def __len__(self):
        return len(self._nodes)

    def __repr__(self):
        return f"KnowledgeGraph({self.topic}: {len(self._nodes)} nodes, {len(self._units)} units)"


# =============================================================================
# BOOK IV: KNOWLEDGE STATE - The Navigator Blueprint
# =============================================================================

class KnowledgeState(Blueprint):
    """
    The learner's current state in knowledge space.

    This is not AI. This is structure.

    The state tracks:
        - Where you are (topic, unit, step)
        - What you know (concepts, vocabulary)
        - How many times you've tried (attempts)

    Laws control when you can move.
    Forges execute the movement.
    """

    # Current position
    topic = field(str, default="")
    unit = field(int, default=1)
    step = field(int, default=1)
    node_id = field(str, default="")

    # Knowledge accumulation
    concepts_mastered = field(set, default=None)
    vocabulary_known = field(set, default=None)
    mastery_levels = field(dict, default=None)  # concept -> MasteryLevel

    # Session tracking
    attempts = field(int, default=0)
    session_start = field(float, default=0.0)
    last_activity = field(float, default=0.0)

    def __init__(self, **kwargs):
        # Initialize sets/dicts before calling super().__init__
        if 'concepts_mastered' not in kwargs or kwargs['concepts_mastered'] is None:
            kwargs['concepts_mastered'] = set()
        if 'vocabulary_known' not in kwargs or kwargs['vocabulary_known'] is None:
            kwargs['vocabulary_known'] = set()
        if 'mastery_levels' not in kwargs or kwargs['mastery_levels'] is None:
            kwargs['mastery_levels'] = {}
        if 'session_start' not in kwargs:
            kwargs['session_start'] = time.time()
        if 'last_activity' not in kwargs:
            kwargs['last_activity'] = time.time()

        super().__init__(**kwargs)

    # =========================================================================
    # LAWS - Navigation Rules (not judgments)
    # =========================================================================

    # Note: Laws in this system are primarily checked via the Navigator's
    # check_prerequisites(), check_vocabulary(), and check_fatigue() methods.
    # This allows for soft enforcement (blocking navigation but not forges)
    # rather than hard finfr violations.

    def is_fatigued(self) -> bool:
        """
        Check if learner shows signs of fatigue.

        This is a navigation rule, not a judgment.
        Not punishment. Protection.
        The system is patient, so you can be too.

        Returns True if attempts > 5 (suggesting a pause).
        """
        return self.attempts > 5

    # =========================================================================
    # FORGES - State Mutations
    # =========================================================================

    @forge
    def learn_concept(self, concept: str, level: MasteryLevel = MasteryLevel.EXPOSED):
        """Add a concept to the learner's knowledge."""
        self.concepts_mastered.add(concept)
        self.mastery_levels[concept] = level
        self.last_activity = time.time()
        return f"Learned concept: {concept}"

    @forge
    def learn_vocabulary(self, word: str):
        """Add a word to the learner's vocabulary."""
        self.vocabulary_known.add(word)
        self.last_activity = time.time()
        return f"Learned word: {word}"

    @forge
    def advance_step(self):
        """Move to the next step."""
        self.step += 1
        self.attempts = 0  # Reset attempts for new step
        self.last_activity = time.time()
        return f"Advanced to step {self.step}"

    @forge
    def advance_unit(self):
        """Move to the next unit."""
        self.unit += 1
        self.step = 1
        self.attempts = 0
        self.last_activity = time.time()
        return f"Advanced to unit {self.unit}"

    @forge
    def record_attempt(self):
        """Record an attempt at the current step."""
        self.attempts += 1
        self.last_activity = time.time()
        return f"Attempt {self.attempts}"

    @forge
    def reset_attempts(self):
        """Reset attempt counter (e.g., after a break)."""
        self.attempts = 0
        return "Attempts reset"

    @forge
    def set_node(self, node_id: str):
        """Set the current node."""
        self.node_id = node_id
        self.last_activity = time.time()
        return f"Moved to node: {node_id}"


# =============================================================================
# BOOK V: THE KNOWLEDGE NAVIGATOR - Environmental Design
# =============================================================================

class KnowledgeNavigator(Blueprint):
    """
    The Knowledge Navigator - Environmental Design for Learning.

    Both Newton and Knowledge Navigator operate on this principle:

        Understanding is not something the system claims to have —
        it is something the system enforces structurally.

    The computer was calm, bounded, patient, and procedural.
    That's critical.

    The Navigator:
        - Doesn't guess what you need
        - Doesn't judge your pace
        - Doesn't make you feel stupid
        - Does enforce structure
        - Does remember everything
        - Does let you explore within bounds
    """

    # The knowledge graph (the structure)
    graph = field(KnowledgeGraph, default=None)

    # The learner's state (the position)
    state = field(KnowledgeState, default=None)

    # The ledger (the history)
    ledger = field(KnowledgeLedger, default=None)

    def __init__(self, topic: str, **kwargs):
        if 'graph' not in kwargs or kwargs['graph'] is None:
            kwargs['graph'] = KnowledgeGraph(topic)
        if 'state' not in kwargs or kwargs['state'] is None:
            kwargs['state'] = KnowledgeState(topic=topic)
        if 'ledger' not in kwargs or kwargs['ledger'] is None:
            kwargs['ledger'] = KnowledgeLedger()

        super().__init__(**kwargs)

    # =========================================================================
    # NAVIGATION CHECKS - These are the physics of knowledge
    # =========================================================================

    def check_prerequisites(self, node_id: str) -> tuple[bool, Set[str]]:
        """
        Check if prerequisite concepts are satisfied.

        Returns (can_proceed, missing_concepts)
        """
        required = self.graph.get_required_concepts(node_id)
        known = self.state.concepts_mastered
        missing = required - known
        return len(missing) == 0, missing

    def check_vocabulary(self, node_id: str) -> tuple[bool, Set[str]]:
        """
        Check if prerequisite vocabulary is satisfied.

        Returns (can_proceed, missing_words)
        """
        required = self.graph.get_required_vocabulary(node_id)
        known = self.state.vocabulary_known
        missing = required - known
        return len(missing) == 0, missing

    def check_fatigue(self) -> tuple[bool, str]:
        """
        Check if a pause is suggested.

        Returns (should_pause, reason)
        """
        if self.state.is_fatigued():
            return True, "Many attempts at this step. Consider taking a break."

        # Check session duration
        session_minutes = (time.time() - self.state.session_start) / 60
        if session_minutes > 45:
            return True, "Long session. Consider taking a break."

        return False, ""

    # =========================================================================
    # NAVIGATION ACTIONS - Moving through knowledge space
    # =========================================================================

    @forge
    def attempt_advance(self, node_id: str) -> Dict[str, Any]:
        """
        Attempt to advance to a knowledge node.

        This is the core navigation action. It:
        1. Checks prerequisites (concepts)
        2. Checks vocabulary
        3. Checks fatigue
        4. Either advances or explains why not

        Returns a result dict with status and details.
        """
        # Record the attempt
        self.state.record_attempt()

        # Check prerequisites
        prereqs_ok, missing_concepts = self.check_prerequisites(node_id)
        if not prereqs_ok:
            self.ledger.record(
                topic=self.state.topic,
                unit=self.state.unit,
                step=self.state.step,
                action="attempt",
                outcome="blocked",
                details={"reason": "missing_concepts", "missing": list(missing_concepts)}
            )
            return {
                "status": NavigationResult.BLOCKED.value,
                "reason": "missing_concepts",
                "missing": list(missing_concepts),
                "message": f"Missing concepts: {', '.join(missing_concepts)}"
            }

        # Check vocabulary
        vocab_ok, missing_words = self.check_vocabulary(node_id)
        if not vocab_ok:
            self.ledger.record(
                topic=self.state.topic,
                unit=self.state.unit,
                step=self.state.step,
                action="attempt",
                outcome="blocked",
                details={"reason": "missing_vocabulary", "missing": list(missing_words)}
            )
            return {
                "status": NavigationResult.BLOCKED.value,
                "reason": "missing_vocabulary",
                "missing": list(missing_words),
                "message": f"Missing vocabulary: {', '.join(missing_words)}"
            }

        # Check fatigue
        should_pause, pause_reason = self.check_fatigue()
        if should_pause:
            self.ledger.record(
                topic=self.state.topic,
                unit=self.state.unit,
                step=self.state.step,
                action="attempt",
                outcome="paused",
                details={"reason": "fatigue", "message": pause_reason}
            )
            return {
                "status": NavigationResult.HOLD.value,
                "reason": "fatigue",
                "message": pause_reason
            }

        # All checks passed - advance
        node = self.graph.get_node(node_id)
        if node:
            # Learn the concepts from this node
            for concept in node.concepts:
                self.state.learn_concept(concept, MasteryLevel.EXPOSED)

            # Learn the vocabulary from this node
            for word in node.vocabulary:
                self.state.learn_vocabulary(word)

            # Update position
            self.state.set_node(node_id)
            self.state.advance_step()

        self.ledger.record(
            topic=self.state.topic,
            unit=self.state.unit,
            step=self.state.step,
            action="advance",
            outcome="success",
            details={"node_id": node_id}
        )

        return {
            "status": NavigationResult.ALLOWED.value,
            "node_id": node_id,
            "message": f"Advanced to: {node.name if node else node_id}"
        }

    @forge
    def teach_concept(self, concept: str, level: MasteryLevel = MasteryLevel.EXPOSED):
        """Explicitly teach a concept to the learner."""
        self.state.learn_concept(concept, level)
        self.ledger.record(
            topic=self.state.topic,
            unit=self.state.unit,
            step=self.state.step,
            action="learn",
            outcome="success",
            details={"concept": concept, "level": level.value}
        )
        return f"Taught concept: {concept}"

    @forge
    def teach_word(self, word: str):
        """Explicitly teach a vocabulary word to the learner."""
        self.state.learn_vocabulary(word)
        self.ledger.record(
            topic=self.state.topic,
            unit=self.state.unit,
            step=self.state.step,
            action="learn",
            outcome="success",
            details={"word": word}
        )
        return f"Taught word: {word}"

    def get_available_content(self, node_id: str) -> List[ContentItem]:
        """Get content available at a node."""
        node = self.graph.get_node(node_id)
        return node.content if node else []

    def get_current_node(self) -> Optional[KnowledgeNode]:
        """Get the current node."""
        return self.graph.get_node(self.state.node_id)

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of the learner's progress."""
        return {
            "topic": self.state.topic,
            "unit": self.state.unit,
            "step": self.state.step,
            "current_node": self.state.node_id,
            "concepts_mastered": len(self.state.concepts_mastered),
            "vocabulary_known": len(self.state.vocabulary_known),
            "total_events": len(self.ledger),
            "attempts_this_step": self.state.attempts
        }


# =============================================================================
# BOOK VI: EXAMPLE DOMAIN - Algebra I
# =============================================================================

def create_algebra_unit_2() -> KnowledgeGraph:
    """
    Create a knowledge graph for Algebra I, Unit 2: Linear Equations.

    Content graph (simplified):
        Variables → Constants → Expressions → Simple equations → Solving equations

    Each node:
        - has content
        - has laws
        - has multiple presentations

    The graph is strict.
    The content is rich.
    """
    graph = KnowledgeGraph("Algebra I: Linear Equations")

    # Node 1: Variables
    node1 = graph.add_node(
        node_id="alg1_u2_variables",
        name="Variables",
        description="Understanding what variables represent in algebra",
        unit=2,
        prerequisites=[],
        vocabulary={"variable", "unknown", "represent"},
        concepts={"variables"}
    )
    node1.add_content(
        ContentType.EXPLANATION_SHORT,
        "What is a Variable?",
        "A variable is a letter that represents an unknown number."
    )
    node1.add_content(
        ContentType.EXPLANATION_MEDIUM,
        "Variables in Depth",
        "In algebra, we use letters like x, y, or n to represent numbers we don't know yet. "
        "These letters are called variables because their value can vary. "
        "For example, if x represents your age, x could be 10 today and 11 next year."
    )
    node1.add_content(
        ContentType.EXAMPLE,
        "Variable Example",
        "If you have x apples and your friend gives you 3 more, you now have x + 3 apples."
    )
    node1.add_content(
        ContentType.PRACTICE,
        "Practice: Identifying Variables",
        "Which letters are variables in this expression: 2x + 5y - 3?"
    )

    # Node 2: Constants
    node2 = graph.add_node(
        node_id="alg1_u2_constants",
        name="Constants",
        description="Understanding constants and fixed values",
        unit=2,
        prerequisites=["alg1_u2_variables"],
        vocabulary={"constant", "fixed", "coefficient"},
        concepts={"constants", "coefficients"}
    )
    node2.add_content(
        ContentType.EXPLANATION_SHORT,
        "What is a Constant?",
        "A constant is a number that doesn't change."
    )
    node2.add_content(
        ContentType.EXPLANATION_MEDIUM,
        "Constants vs Variables",
        "While variables can change, constants stay the same. In 2x + 5, the 5 is a constant. "
        "The 2 is called a coefficient - it multiplies the variable."
    )
    node2.add_content(
        ContentType.REAL_WORLD,
        "Constants in Real Life",
        "Pi (π ≈ 3.14159) is a famous constant - it's always the same, no matter what circle you measure."
    )

    # Node 3: Expressions
    node3 = graph.add_node(
        node_id="alg1_u2_expressions",
        name="Expressions",
        description="Building and understanding algebraic expressions",
        unit=2,
        prerequisites=["alg1_u2_constants"],
        vocabulary={"expression", "term", "simplify"},
        concepts={"expressions", "terms"}
    )
    node3.add_content(
        ContentType.EXPLANATION_SHORT,
        "What is an Expression?",
        "An expression is a combination of numbers, variables, and operations."
    )
    node3.add_content(
        ContentType.EXAMPLE,
        "Expression Examples",
        "2x + 3 is an expression with two terms: 2x and 3"
    )
    node3.add_content(
        ContentType.PRACTICE,
        "Build an Expression",
        "Write an expression for: 'Five more than twice a number'"
    )

    # Node 4: Simple Equations
    node4 = graph.add_node(
        node_id="alg1_u2_simple_equations",
        name="Simple Equations",
        description="Understanding what equations are and what it means to solve them",
        unit=2,
        prerequisites=["alg1_u2_expressions"],
        vocabulary={"equation", "equals", "solution", "solve"},
        concepts={"equations", "equality"}
    )
    node4.add_content(
        ContentType.EXPLANATION_SHORT,
        "What is an Equation?",
        "An equation says two things are equal, using the = sign."
    )
    node4.add_content(
        ContentType.EXPLANATION_MEDIUM,
        "Equations in Depth",
        "An equation like x + 3 = 7 is a statement: 'some number plus 3 equals 7'. "
        "Solving the equation means finding what number x must be to make it true."
    )
    node4.add_content(
        ContentType.ANALOGY,
        "The Balance Scale",
        "Think of an equation like a balance scale. Both sides must weigh the same. "
        "Whatever you do to one side, you must do to the other to keep it balanced."
    )

    # Node 5: Solving Equations
    node5 = graph.add_node(
        node_id="alg1_u2_solving",
        name="Solving Equations",
        description="Techniques for solving linear equations",
        unit=2,
        prerequisites=["alg1_u2_simple_equations"],
        vocabulary={"isolate", "inverse", "operation"},
        concepts={"solving_equations", "inverse_operations"}
    )
    node5.add_content(
        ContentType.EXPLANATION_SHORT,
        "How to Solve",
        "To solve an equation, isolate the variable by doing inverse operations."
    )
    node5.add_content(
        ContentType.EXPLANATION_MEDIUM,
        "Step-by-Step Solving",
        "To solve x + 3 = 7:\n"
        "1. We want x alone on one side\n"
        "2. Subtract 3 from both sides: x + 3 - 3 = 7 - 3\n"
        "3. Simplify: x = 4\n"
        "4. Check: 4 + 3 = 7 ✓"
    )
    node5.add_content(
        ContentType.EXPLANATION_LONG,
        "Complete Guide to Solving Linear Equations",
        "Linear equations follow a pattern. Here's the complete process:\n\n"
        "1. SIMPLIFY both sides (combine like terms, distribute)\n"
        "2. COLLECT variables on one side (usually left)\n"
        "3. COLLECT constants on the other side\n"
        "4. ISOLATE the variable (divide by its coefficient)\n"
        "5. CHECK your answer in the original equation\n\n"
        "Example: 2x + 3 = x + 7\n"
        "Step 2: 2x - x + 3 = 7 → x + 3 = 7\n"
        "Step 3: x = 7 - 3 → x = 4\n"
        "Step 5: 2(4) + 3 = 4 + 7 → 11 = 11 ✓"
    )
    node5.add_content(
        ContentType.PRACTICE,
        "Practice Problem 1",
        "Solve: x - 5 = 12"
    )
    node5.add_content(
        ContentType.PRACTICE,
        "Practice Problem 2",
        "Solve: 3x = 15"
    )
    node5.add_content(
        ContentType.PRACTICE,
        "Practice Problem 3",
        "Solve: 2x + 4 = 10"
    )
    node5.add_content(
        ContentType.REAL_WORLD,
        "Equations in Real Life",
        "You have $20 and want to buy notebooks that cost $3 each, plus a $2 pen. "
        "How many notebooks can you buy? Equation: 3x + 2 = 20"
    )
    node5.add_content(
        ContentType.STORY,
        "The Mystery Number",
        "Detective Maya has a case: Someone left a coded message: 'My number plus seven equals fifteen.' "
        "Can you help her crack the code and find the mystery number?"
    )

    return graph


def create_navigator_for_algebra() -> KnowledgeNavigator:
    """
    Create a ready-to-use Knowledge Navigator for Algebra I, Unit 2.

    Usage:
        nav = create_navigator_for_algebra()

        # Learner starts with no knowledge
        result = nav.attempt_advance("alg1_u2_variables")  # Should succeed
        result = nav.attempt_advance("alg1_u2_constants")  # Should succeed

        # Skip ahead (will be blocked)
        result = nav.attempt_advance("alg1_u2_solving")    # Blocked: missing concepts
    """
    nav = KnowledgeNavigator("Algebra I: Linear Equations")
    nav.graph = create_algebra_unit_2()
    return nav


# =============================================================================
# BOOK VII: SIMULATION - User Journeys
# =============================================================================

def simulate_fast_learner():
    """
    Simulate a fast learner going through the algebra unit.

    This demonstrates how the system handles someone who:
    - Grasps concepts quickly
    - Moves through the material efficiently
    - Doesn't trigger fatigue limits
    """
    nav = create_navigator_for_algebra()

    print("=== Fast Learner Simulation ===\n")

    nodes = [
        "alg1_u2_variables",
        "alg1_u2_constants",
        "alg1_u2_expressions",
        "alg1_u2_simple_equations",
        "alg1_u2_solving"
    ]

    for node_id in nodes:
        result = nav.attempt_advance(node_id)
        print(f"→ {node_id}: {result['status']} - {result.get('message', '')}")

    print(f"\nProgress: {nav.get_progress_summary()}")
    print(f"Events recorded: {len(nav.ledger)}")

    return nav


def simulate_struggling_learner():
    """
    Simulate a learner who struggles and needs support.

    This demonstrates how the system handles someone who:
    - Tries to skip ahead (blocked by prerequisites)
    - Makes multiple attempts (triggers fatigue)
    - Needs explicit teaching before advancing
    """
    nav = create_navigator_for_algebra()

    print("=== Struggling Learner Simulation ===\n")

    # Try to skip directly to solving equations
    print("Attempting to skip ahead...")
    result = nav.attempt_advance("alg1_u2_solving")
    print(f"→ alg1_u2_solving: {result['status']}")
    print(f"  Missing: {result.get('missing', [])}\n")

    # Start from beginning
    print("Starting from the beginning...")
    nav.attempt_advance("alg1_u2_variables")

    # Multiple attempts at constants (simulate struggle)
    print("\nStruggling with constants...")
    for i in range(6):
        nav.state.record_attempt()

    result = nav.attempt_advance("alg1_u2_constants")
    print(f"→ alg1_u2_constants: {result['status']}")
    print(f"  Message: {result.get('message', '')}")

    # Take a break (reset attempts)
    print("\nTaking a break...")
    nav.state.reset_attempts()

    # Try again
    result = nav.attempt_advance("alg1_u2_constants")
    print(f"→ alg1_u2_constants: {result['status']}")

    print(f"\nEvents recorded: {len(nav.ledger)}")
    for event in nav.ledger:
        print(f"  {event}")

    return nav


# =============================================================================
# SCALE ANALYSIS
# =============================================================================

"""
How much content can this handle?

Suppose:
    - 1 subject = Algebra I
    - 10 units
    - 10 steps per unit
    - 5 content items per step (videos, text, problems)

That's:
    10 × 10 × 5 = 500 content items

Now multiply by:
    - short / medium / long versions
    - examples vs practice vs explanation

You're easily at 2,000–5,000 pieces of content
without changing the engine at all.

Newton doesn't care how much content exists.
It only controls when you see it.

================================================================================

Why this will NOT be boring:

❌ Boring systems
    - Linear slides
    - Same explanation every time
    - No memory
    - No consequence
    - No navigation

✅ Newton-style systems
    - You can explore
    - You can retry
    - You can detour
    - You can pause
    - You can go deeper by choice

The system is strict about order,
but flexible about experience.

That's how Apple's Knowledge Navigator demo felt alive — not because it was
"smart", but because it respected the learner's agency without letting them
fall through the floor.
"""
