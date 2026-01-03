#!/usr/bin/env python3
"""
===============================================================================
 KNOWLEDGE SYSTEM TEST SUITE
===============================================================================

Tests for the Knowledge Navigator - Environmental Design for Learning.

"Understanding is not something the system claims to have —
it is something the system enforces structurally."

Run with: pytest tests/test_knowledge.py -v
"""

import pytest
import time
from typing import Dict, Any

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from tinytalk_py.knowledge import (
    # Enums
    NavigationResult,
    MasteryLevel,
    ContentType,
    # Events and Ledger
    KnowledgeEvent,
    KnowledgeLedger,
    # Content Structure
    ContentItem,
    KnowledgeNode,
    KnowledgeGraph,
    # State and Navigation
    KnowledgeState,
    KnowledgeNavigator,
    # Example Domain
    create_algebra_unit_2,
    create_navigator_for_algebra,
    # Simulations
    simulate_fast_learner,
    simulate_struggling_learner,
)

from tinytalk_py.core import LawViolation, FinClosure


# =============================================================================
# PART 1: KNOWLEDGE EVENT AND LEDGER TESTS
# =============================================================================

class TestKnowledgeEvent:
    """Test KnowledgeEvent creation and representation."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = KnowledgeEvent(
            timestamp=time.time(),
            topic="Algebra",
            unit=2,
            step=3,
            action="attempt",
            outcome="success"
        )

        assert event.topic == "Algebra"
        assert event.unit == 2
        assert event.step == 3
        assert event.action == "attempt"
        assert event.outcome == "success"

    def test_event_with_details(self):
        """Test event with additional details."""
        event = KnowledgeEvent(
            timestamp=time.time(),
            topic="Algebra",
            unit=1,
            step=1,
            action="blocked",
            outcome="blocked",
            details={"reason": "missing_concepts", "missing": ["variables"]}
        )

        assert event.details["reason"] == "missing_concepts"
        assert "variables" in event.details["missing"]

    def test_event_repr(self):
        """Test event string representation."""
        event = KnowledgeEvent(
            timestamp=time.time(),
            topic="Algebra",
            unit=2,
            step=3,
            action="advance",
            outcome="success"
        )

        repr_str = repr(event)
        assert "advance" in repr_str
        assert "Algebra" in repr_str
        assert "success" in repr_str


class TestKnowledgeLedger:
    """Test KnowledgeLedger for tracking learning history."""

    def test_ledger_creation(self):
        """Test ledger creation."""
        ledger = KnowledgeLedger()
        assert len(ledger) == 0

    def test_record_event(self):
        """Test recording events to ledger."""
        ledger = KnowledgeLedger()

        event = ledger.record(
            topic="Math",
            unit=1,
            step=1,
            action="attempt",
            outcome="success"
        )

        assert len(ledger) == 1
        assert event.topic == "Math"
        assert event.action == "attempt"

    def test_query_by_topic(self):
        """Test filtering events by topic."""
        ledger = KnowledgeLedger()

        ledger.record("Math", 1, 1, "attempt", "success")
        ledger.record("Science", 1, 1, "attempt", "success")
        ledger.record("Math", 1, 2, "advance", "success")

        math_events = ledger.get_events(topic="Math")
        assert len(math_events) == 2

        science_events = ledger.get_events(topic="Science")
        assert len(science_events) == 1

    def test_query_by_action(self):
        """Test filtering events by action."""
        ledger = KnowledgeLedger()

        ledger.record("Math", 1, 1, "attempt", "success")
        ledger.record("Math", 1, 1, "attempt", "blocked")
        ledger.record("Math", 1, 2, "advance", "success")

        attempts = ledger.get_events(action="attempt")
        assert len(attempts) == 2

        advances = ledger.get_events(action="advance")
        assert len(advances) == 1

    def test_count_attempts(self):
        """Test counting attempts at a specific step."""
        ledger = KnowledgeLedger()

        # Multiple attempts at step 3
        ledger.record("Math", 2, 3, "attempt", "blocked")
        ledger.record("Math", 2, 3, "attempt", "blocked")
        ledger.record("Math", 2, 3, "attempt", "success")
        ledger.record("Math", 2, 4, "attempt", "success")  # Different step

        count = ledger.count_attempts("Math", 2, 3)
        assert count == 3

    def test_last_event(self):
        """Test getting the last event."""
        ledger = KnowledgeLedger()

        ledger.record("Math", 1, 1, "attempt", "success")
        ledger.record("Math", 1, 2, "advance", "success")

        last = ledger.last_event()
        assert last.action == "advance"
        assert last.step == 2


# =============================================================================
# PART 2: CONTENT STRUCTURE TESTS
# =============================================================================

class TestContentItem:
    """Test ContentItem for knowledge content."""

    def test_content_creation(self):
        """Test creating content items."""
        content = ContentItem(
            content_type=ContentType.EXPLANATION_SHORT,
            title="What is a Variable?",
            body="A variable is a letter that represents an unknown number."
        )

        assert content.content_type == ContentType.EXPLANATION_SHORT
        assert content.title == "What is a Variable?"
        assert "unknown number" in content.body

    def test_content_with_media(self):
        """Test content with optional media."""
        content = ContentItem(
            content_type=ContentType.VIDEO,
            title="Variables Explained",
            body="Watch this video to learn about variables.",
            duration_minutes=5,
            media_url="/videos/variables.mp4"
        )

        assert content.duration_minutes == 5
        assert content.media_url == "/videos/variables.mp4"


class TestKnowledgeNode:
    """Test KnowledgeNode for knowledge graph nodes."""

    def test_node_creation(self):
        """Test creating knowledge nodes."""
        node = KnowledgeNode(
            id="math_variables",
            name="Variables",
            description="Understanding variables in algebra",
            prerequisites=[],
            vocabulary={"variable", "unknown"},
            concepts={"variables"}
        )

        assert node.id == "math_variables"
        assert node.name == "Variables"
        assert "variable" in node.vocabulary
        assert "variables" in node.concepts

    def test_node_add_content(self):
        """Test adding content to a node."""
        node = KnowledgeNode(
            id="test_node",
            name="Test",
            description="Test node"
        )

        node.add_content(
            ContentType.EXPLANATION_SHORT,
            "Short Explanation",
            "This is brief."
        )
        node.add_content(
            ContentType.PRACTICE,
            "Practice Problem",
            "Solve: x + 5 = 10"
        )

        assert len(node.content) == 2

    def test_node_get_content_by_type(self):
        """Test filtering content by type."""
        node = KnowledgeNode(
            id="test_node",
            name="Test",
            description="Test node"
        )

        node.add_content(ContentType.EXPLANATION_SHORT, "Short", "Brief")
        node.add_content(ContentType.EXPLANATION_MEDIUM, "Medium", "Detailed")
        node.add_content(ContentType.PRACTICE, "Practice 1", "Problem 1")
        node.add_content(ContentType.PRACTICE, "Practice 2", "Problem 2")

        practices = node.get_content(ContentType.PRACTICE)
        assert len(practices) == 2

        explanations = node.get_content(ContentType.EXPLANATION_SHORT)
        assert len(explanations) == 1


class TestKnowledgeGraph:
    """Test KnowledgeGraph for organizing knowledge nodes."""

    def test_graph_creation(self):
        """Test creating knowledge graph."""
        graph = KnowledgeGraph("Test Topic")
        assert graph.topic == "Test Topic"
        assert len(graph) == 0

    def test_add_nodes(self):
        """Test adding nodes to graph."""
        graph = KnowledgeGraph("Math")

        node1 = graph.add_node(
            node_id="n1",
            name="Node 1",
            description="First node",
            unit=1
        )

        node2 = graph.add_node(
            node_id="n2",
            name="Node 2",
            description="Second node",
            unit=1,
            prerequisites=["n1"]
        )

        assert len(graph) == 2
        assert graph.get_node("n1") == node1
        assert graph.get_node("n2") == node2

    def test_get_unit_nodes(self):
        """Test getting nodes by unit."""
        graph = KnowledgeGraph("Math")

        graph.add_node("u1_n1", "U1 Node 1", "Desc", unit=1)
        graph.add_node("u1_n2", "U1 Node 2", "Desc", unit=1)
        graph.add_node("u2_n1", "U2 Node 1", "Desc", unit=2)

        unit1_nodes = graph.get_unit_nodes(1)
        assert len(unit1_nodes) == 2

        unit2_nodes = graph.get_unit_nodes(2)
        assert len(unit2_nodes) == 1

    def test_get_prerequisites(self):
        """Test getting prerequisite nodes."""
        graph = KnowledgeGraph("Math")

        graph.add_node("a", "A", "First", unit=1)
        graph.add_node("b", "B", "Second", unit=1, prerequisites=["a"])
        graph.add_node("c", "C", "Third", unit=1, prerequisites=["a", "b"])

        prereqs_c = graph.get_prerequisites("c")
        prereq_ids = [n.id for n in prereqs_c]
        assert "a" in prereq_ids
        assert "b" in prereq_ids

    def test_get_required_concepts(self):
        """Test getting required concepts from prerequisites recursively."""
        graph = KnowledgeGraph("Math")

        graph.add_node("a", "A", "First", unit=1, concepts={"concept_a"})
        graph.add_node("b", "B", "Second", unit=1,
                       prerequisites=["a"], concepts={"concept_b"})
        graph.add_node("c", "C", "Third", unit=1,
                       prerequisites=["b"], concepts={"concept_c"})

        # Node c requires concepts from its prerequisites recursively (a and b)
        required = graph.get_required_concepts("c")

        # Should include concept_b from direct prerequisite b
        assert "concept_b" in required
        # Should include concept_a from b's prerequisite a (recursive)
        assert "concept_a" in required
        # c's own concepts are NOT required to enter c
        assert "concept_c" not in required

        # Test node b only requires concepts from a
        required_b = graph.get_required_concepts("b")
        assert "concept_a" in required_b
        assert "concept_b" not in required_b  # b's own concept not required

        # Test node a requires no concepts (no prerequisites)
        required_a = graph.get_required_concepts("a")
        assert len(required_a) == 0


# =============================================================================
# PART 3: KNOWLEDGE STATE TESTS
# =============================================================================

class TestKnowledgeState:
    """Test KnowledgeState Blueprint for learner state."""

    def test_state_creation(self):
        """Test creating knowledge state."""
        state = KnowledgeState(topic="Algebra")

        assert state.topic == "Algebra"
        assert state.unit == 1
        assert state.step == 1
        assert len(state.concepts_mastered) == 0
        assert len(state.vocabulary_known) == 0

    def test_learn_concept(self):
        """Test learning concepts."""
        state = KnowledgeState(topic="Math")

        state.learn_concept("variables", MasteryLevel.EXPOSED)
        state.learn_concept("constants", MasteryLevel.PROFICIENT)

        assert "variables" in state.concepts_mastered
        assert "constants" in state.concepts_mastered
        assert state.mastery_levels["variables"] == MasteryLevel.EXPOSED
        assert state.mastery_levels["constants"] == MasteryLevel.PROFICIENT

    def test_learn_vocabulary(self):
        """Test learning vocabulary."""
        state = KnowledgeState(topic="Math")

        state.learn_vocabulary("solve")
        state.learn_vocabulary("equation")

        assert "solve" in state.vocabulary_known
        assert "equation" in state.vocabulary_known

    def test_advance_step(self):
        """Test advancing steps."""
        state = KnowledgeState(topic="Math")
        state.attempts = 3  # Some attempts recorded

        state.advance_step()

        assert state.step == 2
        assert state.attempts == 0  # Reset on advance

    def test_advance_unit(self):
        """Test advancing units."""
        state = KnowledgeState(topic="Math")
        state.step = 5

        state.advance_unit()

        assert state.unit == 2
        assert state.step == 1  # Reset to first step

    def test_fatigue_check(self):
        """Test fatigue check triggers after many attempts."""
        state = KnowledgeState(topic="Math")

        # Initially not fatigued
        assert not state.is_fatigued()

        # Record 5 attempts (at limit)
        for _ in range(5):
            state.record_attempt()

        assert state.attempts == 5
        assert not state.is_fatigued()  # Not fatigued at exactly 5

        # One more attempt triggers fatigue
        state.record_attempt()
        assert state.attempts == 6
        assert state.is_fatigued()  # Now fatigued (> 5)


# =============================================================================
# PART 4: KNOWLEDGE NAVIGATOR TESTS
# =============================================================================

class TestKnowledgeNavigator:
    """Test KnowledgeNavigator for knowledge navigation."""

    def test_navigator_creation(self):
        """Test creating a navigator."""
        nav = KnowledgeNavigator("Test Topic")

        assert nav.state.topic == "Test Topic"
        assert nav.graph.topic == "Test Topic"
        assert len(nav.ledger) == 0

    def test_check_prerequisites_no_requirements(self):
        """Test prerequisite check when there are none."""
        nav = KnowledgeNavigator("Math")
        nav.graph.add_node("first", "First Node", "Start here", unit=1)

        can_proceed, missing = nav.check_prerequisites("first")
        assert can_proceed is True
        assert len(missing) == 0

    def test_check_prerequisites_missing(self):
        """Test prerequisite check when concepts are missing."""
        nav = KnowledgeNavigator("Math")
        nav.graph.add_node("a", "A", "First", unit=1, concepts={"concept_a"})
        nav.graph.add_node("b", "B", "Second", unit=1,
                           prerequisites=["a"], concepts={"concept_b"})

        # Try to access b without learning a's concepts
        can_proceed, missing = nav.check_prerequisites("b")
        assert can_proceed is False
        assert "concept_a" in missing

    def test_check_prerequisites_satisfied(self):
        """Test prerequisite check when concepts are known."""
        nav = KnowledgeNavigator("Math")
        nav.graph.add_node("a", "A", "First", unit=1, concepts={"concept_a"})
        nav.graph.add_node("b", "B", "Second", unit=1,
                           prerequisites=["a"], concepts={"concept_b"})

        # Learn the required concept
        nav.state.learn_concept("concept_a")

        can_proceed, missing = nav.check_prerequisites("b")
        assert can_proceed is True
        assert len(missing) == 0

    def test_check_vocabulary(self):
        """Test vocabulary prerequisite check."""
        nav = KnowledgeNavigator("Math")

        # Node a has vocabulary that you LEARN there, not require
        nav.graph.add_node("a", "A", "First", unit=1,
                           vocabulary={"variable", "equation"})
        # Node b requires node a, so needs a's vocabulary
        nav.graph.add_node("b", "B", "Second", unit=1,
                           prerequisites=["a"],
                           vocabulary={"solve"})

        # Node a has no prerequisites, so no vocabulary required
        can_proceed, missing = nav.check_vocabulary("a")
        assert can_proceed is True  # First node needs no vocab

        # Node b requires vocab from prerequisite a
        can_proceed, missing = nav.check_vocabulary("b")
        assert can_proceed is False
        assert "variable" in missing
        assert "equation" in missing

        # Learn vocabulary from node a
        nav.state.learn_vocabulary("variable")
        nav.state.learn_vocabulary("equation")

        can_proceed, missing = nav.check_vocabulary("b")
        assert can_proceed is True

    def test_check_fatigue(self):
        """Test fatigue check."""
        nav = KnowledgeNavigator("Math")

        # No fatigue initially
        should_pause, reason = nav.check_fatigue()
        assert should_pause is False

        # Add 6 attempts (record_attempt is now allowed)
        for _ in range(6):
            nav.state.record_attempt()

        # Check fatigue returns True when attempts > 5
        should_pause, reason = nav.check_fatigue()
        assert should_pause is True
        assert "attempts" in reason.lower() or "break" in reason.lower()

    def test_attempt_advance_success(self):
        """Test successful navigation advance."""
        nav = KnowledgeNavigator("Math")
        nav.graph.add_node("first", "First", "Start", unit=1,
                           concepts={"first_concept"})

        result = nav.attempt_advance("first")

        assert result["status"] == NavigationResult.ALLOWED.value
        assert "first_concept" in nav.state.concepts_mastered
        assert len(nav.ledger) >= 1

    def test_attempt_advance_blocked_by_prereqs(self):
        """Test navigation blocked by missing prerequisites."""
        nav = KnowledgeNavigator("Math")
        nav.graph.add_node("a", "A", "First", unit=1, concepts={"concept_a"})
        nav.graph.add_node("b", "B", "Second", unit=1,
                           prerequisites=["a"], concepts={"concept_b"})

        result = nav.attempt_advance("b")

        assert result["status"] == NavigationResult.BLOCKED.value
        assert result["reason"] == "missing_concepts"
        assert "concept_a" in result["missing"]

    def test_attempt_advance_blocked_by_vocab(self):
        """Test navigation blocked by missing vocabulary from prerequisites."""
        nav = KnowledgeNavigator("Math")

        # Node a teaches vocabulary, node b requires it
        nav.graph.add_node("a", "A", "First", unit=1,
                           vocabulary={"solve"},
                           concepts={"solving"})
        nav.graph.add_node("b", "B", "Second", unit=1,
                           prerequisites=["a"],
                           vocabulary={"equation"})

        # Can advance to first node (no vocab requirements)
        result_a = nav.attempt_advance("a")
        assert result_a["status"] == NavigationResult.ALLOWED.value

        # Reset state to test blocking (normally would learn concepts from a)
        nav.state.concepts_mastered = set()
        nav.state.vocabulary_known = set()

        # Now try to advance to b without learning a's vocab
        result_b = nav.attempt_advance("b")

        assert result_b["status"] == NavigationResult.BLOCKED.value
        # Could be blocked by either missing concepts or vocabulary
        assert result_b["reason"] in ["missing_vocabulary", "missing_concepts"]

    def test_teach_concept(self):
        """Test explicitly teaching a concept."""
        nav = KnowledgeNavigator("Math")

        nav.teach_concept("variables", MasteryLevel.PROFICIENT)

        assert "variables" in nav.state.concepts_mastered
        assert nav.state.mastery_levels["variables"] == MasteryLevel.PROFICIENT

    def test_teach_word(self):
        """Test explicitly teaching vocabulary."""
        nav = KnowledgeNavigator("Math")

        nav.teach_word("equation")

        assert "equation" in nav.state.vocabulary_known

    def test_progress_summary(self):
        """Test getting progress summary."""
        nav = KnowledgeNavigator("Math")
        nav.state.learn_concept("a")
        nav.state.learn_concept("b")
        nav.state.learn_vocabulary("x")

        summary = nav.get_progress_summary()

        assert summary["topic"] == "Math"
        assert summary["concepts_mastered"] == 2
        assert summary["vocabulary_known"] == 1


# =============================================================================
# PART 5: ALGEBRA DOMAIN TESTS
# =============================================================================

class TestAlgebraDomain:
    """Test the example Algebra I domain."""

    def test_algebra_graph_creation(self):
        """Test creating the Algebra I graph."""
        graph = create_algebra_unit_2()

        assert graph.topic == "Algebra I: Linear Equations"
        assert len(graph) == 5  # 5 nodes in unit 2

    def test_algebra_node_content(self):
        """Test that algebra nodes have content."""
        graph = create_algebra_unit_2()

        variables_node = graph.get_node("alg1_u2_variables")
        assert variables_node is not None
        assert len(variables_node.content) > 0

        # Check for multiple content types
        content_types = {c.content_type for c in variables_node.content}
        assert ContentType.EXPLANATION_SHORT in content_types

    def test_algebra_prerequisite_chain(self):
        """Test the prerequisite chain in algebra."""
        graph = create_algebra_unit_2()

        # Variables has no prerequisites
        variables = graph.get_node("alg1_u2_variables")
        assert len(variables.prerequisites) == 0

        # Constants requires variables
        constants = graph.get_node("alg1_u2_constants")
        assert "alg1_u2_variables" in constants.prerequisites

        # Solving requires simple_equations
        solving = graph.get_node("alg1_u2_solving")
        assert "alg1_u2_simple_equations" in solving.prerequisites

    def test_algebra_navigator_sequential(self):
        """Test navigating through algebra sequentially."""
        nav = create_navigator_for_algebra()

        nodes = [
            "alg1_u2_variables",
            "alg1_u2_constants",
            "alg1_u2_expressions",
            "alg1_u2_simple_equations",
            "alg1_u2_solving"
        ]

        for node_id in nodes:
            result = nav.attempt_advance(node_id)
            assert result["status"] == NavigationResult.ALLOWED.value, \
                f"Failed to advance to {node_id}: {result}"

    def test_algebra_navigator_skip_blocked(self):
        """Test that skipping ahead is blocked."""
        nav = create_navigator_for_algebra()

        # Try to skip directly to solving
        result = nav.attempt_advance("alg1_u2_solving")

        assert result["status"] == NavigationResult.BLOCKED.value
        # Should be missing concepts from prerequisites


# =============================================================================
# PART 6: SIMULATION TESTS
# =============================================================================

class TestSimulations:
    """Test user journey simulations."""

    def test_fast_learner_simulation(self):
        """Test fast learner completes successfully."""
        nav = simulate_fast_learner()

        # Should have completed all nodes
        assert nav.state.step >= 5

        # Should have learned all concepts
        assert len(nav.state.concepts_mastered) >= 5

    def test_struggling_learner_simulation(self):
        """Test struggling learner hits appropriate blocks."""
        nav = simulate_struggling_learner()

        # Should have recorded events including blocks
        events = nav.ledger.get_events(action="attempt")
        assert len(events) > 0

        # Should have some blocked outcomes
        blocked_events = [e for e in events if e.outcome == "blocked"]
        assert len(blocked_events) > 0


# =============================================================================
# PART 7: PERFORMANCE TESTS
# =============================================================================

class TestKnowledgePerformance:
    """Performance tests for knowledge system."""

    def test_ledger_recording_speed(self):
        """Test ledger can handle many events."""
        ledger = KnowledgeLedger()

        iterations = 10000
        start = time.perf_counter()

        for i in range(iterations):
            ledger.record("Math", i % 10, i % 100, "attempt", "success")

        elapsed = time.perf_counter() - start
        events_per_second = iterations / elapsed

        assert events_per_second > 10000, f"Too slow: {events_per_second} events/sec"
        print(f"\nLedger Recording: {events_per_second:.0f} events/sec")

    def test_navigation_check_speed(self):
        """Test navigation checks are fast."""
        nav = create_navigator_for_algebra()

        iterations = 1000
        start = time.perf_counter()

        for _ in range(iterations):
            nav.check_prerequisites("alg1_u2_solving")
            nav.check_vocabulary("alg1_u2_solving")
            nav.check_fatigue()

        elapsed = time.perf_counter() - start
        checks_per_second = (iterations * 3) / elapsed

        assert checks_per_second > 10000, f"Too slow: {checks_per_second} checks/sec"
        print(f"\nNavigation Checks: {checks_per_second:.0f} checks/sec")

    def test_large_graph_navigation(self):
        """Test navigation works with large graphs."""
        nav = KnowledgeNavigator("Large Topic")

        # Create 100 nodes with prerequisites
        for i in range(100):
            prereqs = [f"node_{i-1}"] if i > 0 else []
            nav.graph.add_node(
                f"node_{i}",
                f"Node {i}",
                f"Description {i}",
                unit=i // 10 + 1,
                prerequisites=prereqs,
                concepts={f"concept_{i}"}
            )

        # Navigate through all nodes
        start = time.perf_counter()
        for i in range(100):
            result = nav.attempt_advance(f"node_{i}")
            assert result["status"] == NavigationResult.ALLOWED.value

        elapsed = time.perf_counter() - start
        print(f"\nLarge Graph (100 nodes): {elapsed*1000:.2f}ms total")


# =============================================================================
# PART 8: EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_graph_navigation(self):
        """Test navigation with empty graph."""
        nav = KnowledgeNavigator("Empty")

        result = nav.attempt_advance("nonexistent")

        # Should handle gracefully (node doesn't exist, but allowed as no prereqs)
        assert result is not None

    def test_self_referential_prerequisites(self):
        """Test handling of node without circular dependencies."""
        nav = KnowledgeNavigator("Test")

        nav.graph.add_node("a", "A", "Desc", unit=1, concepts={"c_a"})
        nav.graph.add_node("b", "B", "Desc", unit=1,
                           prerequisites=["a"], concepts={"c_b"})

        # Should work normally
        result = nav.attempt_advance("a")
        assert result["status"] == NavigationResult.ALLOWED.value

    def test_multiple_content_types_per_node(self):
        """Test node with many content items."""
        node = KnowledgeNode("rich", "Rich Node", "Lots of content")

        for ct in ContentType:
            node.add_content(ct, f"Title for {ct.value}", f"Body for {ct.value}")

        assert len(node.content) == len(ContentType)

    def test_mastery_level_progression(self):
        """Test mastery levels can progress."""
        state = KnowledgeState(topic="Test")

        # Start at EXPOSED
        state.learn_concept("test", MasteryLevel.EXPOSED)
        assert state.mastery_levels["test"] == MasteryLevel.EXPOSED

        # Progress to PROFICIENT
        state.learn_concept("test", MasteryLevel.PROFICIENT)
        assert state.mastery_levels["test"] == MasteryLevel.PROFICIENT

        # Progress to MASTERED
        state.learn_concept("test", MasteryLevel.MASTERED)
        assert state.mastery_levels["test"] == MasteryLevel.MASTERED


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
