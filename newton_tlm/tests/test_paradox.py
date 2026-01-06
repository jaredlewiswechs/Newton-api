#!/usr/bin/env python3
"""
===============================================================================
NEWTON TLM - PARADOX DETECTION TESTS
Comprehensive verification of paradox detection and contradiction prevention.
===============================================================================

Tests cover:
- Internal contradictions (within a single transaction)
- External contradictions (against existing graph state)
- Idempotency (re-asserting same relation passes)
- State hash preservation on rejection
- ParadoxError exception handling
- Integration with the full ingest cycle
"""

import pytest
from newton_tlm import (
    NewtonTLM, Atom, Transaction,
    Phase, PhaseMachine,
    ParadoxDetector, ParadoxError, ParadoxResult,
)


# =============================================================================
# PARADOX DETECTOR UNIT TESTS
# =============================================================================

class TestParadoxDetectorInternal:
    """Test internal contradiction detection within transactions."""

    def test_no_internal_paradox_single_edge(self):
        """Single edge should not trigger paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_safe")

        result = detector.detect_internal(tx)
        assert not result.has_paradox

    def test_no_internal_paradox_different_pairs(self):
        """Different source-target pairs should not conflict."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_safe")
        tx.add_edge("C", "D", "is_unsafe")

        result = detector.detect_internal(tx)
        assert not result.has_paradox

    def test_internal_paradox_same_pair_different_relation(self):
        """Same pair with different relations should trigger paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_safe")
        tx.add_edge("A", "B", "is_unsafe")

        result = detector.detect_internal(tx)
        assert result.has_paradox
        assert result.paradox_type == "internal"
        assert result.source == "A"
        assert result.target == "B"
        assert result.existing_relation == "is_safe"
        assert result.conflicting_relation == "is_unsafe"

    def test_internal_paradox_idempotent_same_relation(self):
        """Same pair with same relation should NOT trigger paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_verified")
        tx.add_edge("A", "B", "is_verified")

        result = detector.detect_internal(tx)
        assert not result.has_paradox


class TestParadoxDetectorExternal:
    """Test external contradiction detection against graph ledger."""

    def test_no_external_paradox_empty_graph(self):
        """Empty graph should never trigger external paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_safe")

        result = detector.detect_external(tx)
        assert not result.has_paradox

    def test_no_external_paradox_same_relation(self):
        """Same relation in graph and tx should not conflict (idempotent)."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("A", "B", type="is_verified")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_verified")

        result = detector.detect_external(tx)
        assert not result.has_paradox

    def test_external_paradox_different_relation(self):
        """Different relation for same edge should trigger paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("concept_transfer", "attribute_safety", type="is_verified")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("concept_transfer", "attribute_safety", "is_banned")

        result = detector.detect_external(tx)
        assert result.has_paradox
        assert result.paradox_type == "external"
        assert result.source == "concept_transfer"
        assert result.target == "attribute_safety"
        assert result.existing_relation == "is_verified"
        assert result.conflicting_relation == "is_banned"

    def test_external_paradox_no_conflict_different_target(self):
        """Different target should not conflict."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("A", "B", type="is_safe")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "C", "is_unsafe")

        result = detector.detect_external(tx)
        assert not result.has_paradox


class TestParadoxDetectorFull:
    """Test full paradox detection combining internal and external."""

    def test_detect_returns_internal_first(self):
        """Internal paradoxes should be detected before external."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("X", "Y", type="relation_1")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        # Both internal and external paradoxes
        tx.add_edge("A", "B", "is_safe")
        tx.add_edge("A", "B", "is_unsafe")  # Internal paradox
        tx.add_edge("X", "Y", "relation_2")  # External paradox

        result = detector.detect(tx)
        assert result.has_paradox
        assert result.paradox_type == "internal"

    def test_detect_no_paradox_clean_tx(self):
        """Clean transaction should pass detection."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("existing", "node", type="established")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("new", "relation", "created")

        result = detector.detect(tx)
        assert not result.has_paradox

    def test_validate_raises_on_paradox(self):
        """validate() should raise ParadoxError on contradiction."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("A", "B", type="is_verified")
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "is_banned")

        with pytest.raises(ParadoxError) as exc_info:
            detector.validate(tx)

        assert exc_info.value.paradox_type == "external"
        assert "is_verified" in str(exc_info.value)
        assert "is_banned" in str(exc_info.value)


# =============================================================================
# PARADOX RESULT TESTS
# =============================================================================

class TestParadoxResult:
    """Test ParadoxResult dataclass."""

    def test_default_no_paradox(self):
        """Default ParadoxResult should indicate no paradox."""
        result = ParadoxResult()
        assert not result.has_paradox
        assert result.paradox_type is None
        assert result.details == []
        assert result.to_error() is None

    def test_to_error_with_paradox(self):
        """to_error() should return ParadoxError when has_paradox is True."""
        result = ParadoxResult(
            has_paradox=True,
            paradox_type="internal",
            source="A",
            target="B",
            existing_relation="is_safe",
            conflicting_relation="is_unsafe",
            details=["Test detail"]
        )

        error = result.to_error()
        assert error is not None
        assert isinstance(error, ParadoxError)
        assert error.paradox_type == "internal"


# =============================================================================
# NEWTON TLM INTEGRATION TESTS
# =============================================================================

class TestNewtonTLMParadoxIntegration:
    """Test paradox detection integrated with NewtonTLM."""

    def test_phase_cycle_includes_paradox(self):
        """Phase cycle should include PARADOX phase."""
        pm = PhaseMachine()

        # Go through cycle including PARADOX
        pm.transition(Phase.INGEST)
        pm.transition(Phase.PARSE)
        pm.transition(Phase.CRYSTALLIZE)
        pm.transition(Phase.DIFFUSE)
        pm.transition(Phase.CONVERGE)
        pm.transition(Phase.VERIFY)
        pm.transition(Phase.PARADOX)  # New phase
        pm.transition(Phase.COMMIT)
        pm.transition(Phase.REFLECT)
        pm.transition(Phase.IDLE)

        assert pm.current == Phase.IDLE
        assert pm.cycle_count == 1

    def test_cannot_skip_paradox_phase(self):
        """Cannot skip PARADOX phase in cycle."""
        pm = PhaseMachine()

        pm.transition(Phase.INGEST)
        pm.transition(Phase.PARSE)
        pm.transition(Phase.CRYSTALLIZE)
        pm.transition(Phase.DIFFUSE)
        pm.transition(Phase.CONVERGE)
        pm.transition(Phase.VERIFY)

        # Should not be able to skip to COMMIT
        with pytest.raises(RuntimeError):
            pm.transition(Phase.COMMIT)

    def test_ingest_completes_with_paradox_phase(self):
        """Ingest should complete full cycle including PARADOX."""
        tlm = NewtonTLM()

        assert tlm.phase_machine.current == Phase.IDLE

        success = tlm.ingest("test_data")

        assert success
        assert tlm.phase_machine.current == Phase.IDLE
        assert tlm.phase_machine.cycle_count == 1

    def test_detect_paradox_method(self):
        """detect_paradox method should work on TLM."""
        tlm = NewtonTLM()

        # Add existing edge to graph
        tlm.graph.add_edge("concept", "attribute", type="is_verified")

        # Create transaction with conflicting edge
        tx = Transaction()
        tx.add_edge("concept", "attribute", "is_banned")

        result = tlm.detect_paradox(tx)
        assert result.has_paradox
        assert result.paradox_type == "external"

    def test_validate_paradox_raises(self):
        """validate_paradox should raise on contradiction."""
        tlm = NewtonTLM()
        tlm.graph.add_edge("A", "B", type="safe")

        tx = Transaction()
        tx.add_edge("A", "B", "unsafe")

        with pytest.raises(ParadoxError):
            tlm.validate_paradox(tx)


class TestNewtonTLMParadoxSimulation:
    """
    Full simulation of paradox detection as described in the spec.

    This tests the exact scenario from the user's example:
    1. Establish a truth (Transfer is_verified Safety)
    2. Reinforce (idempotency check)
    3. Attempt contradiction (Transfer is_banned Safety)
    """

    def test_paradox_protocol_simulation(self):
        """
        Simulate the Paradox Protocol:
        1. Teach: 'Transfer is Verified'
        2. Reinforce: 'Transfer is Verified' (Again - should pass)
        3. Attack: 'Transfer is Banned' (Should be rejected)
        """
        tlm = NewtonTLM()

        # Step 1: Establish a Truth
        # Manually add an edge to simulate learning a rule
        tx1 = tlm.begin_transaction()
        atom1 = Atom.create("concept_transfer", "concept", "Transfer")
        atom2 = Atom.create("attribute_safety", "attribute", "Safety")
        tx1.add_atom(atom1)
        tx1.add_atom(atom2)
        tx1.add_edge("concept_transfer", "attribute_safety", "is_verified")
        tlm.commit_transaction()

        hash_after_truth = tlm.get_state_hash()

        # Step 2: Reinforce (Idempotency) - same relation should pass paradox check
        tx2 = Transaction()
        tx2.add_edge("concept_transfer", "attribute_safety", "is_verified")

        result2 = tlm.detect_paradox(tx2)
        assert not result2.has_paradox, "Idempotent re-assertion should not trigger paradox"

        # Step 3: Introduce Contradiction - different relation should trigger paradox
        tx3 = Transaction()
        tx3.add_edge("concept_transfer", "attribute_safety", "is_banned")

        result3 = tlm.detect_paradox(tx3)
        assert result3.has_paradox, "Contradictory assertion should trigger paradox"
        assert result3.paradox_type == "external"
        assert result3.existing_relation == "is_verified"
        assert result3.conflicting_relation == "is_banned"

        # Verify state unchanged after rejected attack
        # (In real ingest, the transaction would be aborted)
        hash_final = tlm.get_state_hash()
        assert hash_after_truth == hash_final, "Ledger should remain untouched after paradox detection"

    def test_ingest_rejects_contradicting_data(self):
        """
        Test that full ingest cycle rejects contradictory edges.
        """
        tlm = NewtonTLM()

        # First, manually establish a truth via direct transaction
        tx1 = tlm.begin_transaction()
        tx1.add_atom(Atom.create("nodeA", "type", "value"))
        tx1.add_atom(Atom.create("nodeB", "type", "value"))
        tx1.add_edge("nodeA", "nodeB", "is_friend")
        tlm.commit_transaction()

        hash_before = tlm.get_state_hash()
        ledger_len_before = len(tlm.ledger)

        # Now try to add conflicting edge via custom transaction
        tx2 = tlm.begin_transaction()
        tx2.add_edge("nodeA", "nodeB", "is_enemy")  # Contradiction!

        # Simulate what ingest does in PARADOX phase
        result = tlm.detect_paradox(tx2)
        assert result.has_paradox

        # Abort as ingest would
        tlm.abort_transaction()

        # Verify state unchanged
        hash_after = tlm.get_state_hash()
        assert hash_before == hash_after

        # Ledger should not have new entry
        assert len(tlm.ledger) == ledger_len_before


class TestParadoxEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_transaction_no_paradox(self):
        """Empty transaction should not trigger paradox."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        result = detector.detect(tx)
        assert not result.has_paradox

    def test_self_loop_edge(self):
        """Self-loop edges should be handled correctly."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("A", "A", type="self_reference")
        detector = ParadoxDetector(graph)

        # Same self-reference should not conflict
        tx1 = Transaction()
        tx1.add_edge("A", "A", "self_reference")
        assert not detector.detect(tx1).has_paradox

        # Different self-reference should conflict
        tx2 = Transaction()
        tx2.add_edge("A", "A", "different_reference")
        assert detector.detect(tx2).has_paradox

    def test_multiple_internal_paradoxes(self):
        """Only first internal paradox should be reported."""
        import networkx as nx
        graph = nx.DiGraph()
        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "rel1")
        tx.add_edge("A", "B", "rel2")  # First paradox
        tx.add_edge("C", "D", "rel3")
        tx.add_edge("C", "D", "rel4")  # Second paradox (not reported)

        result = detector.detect(tx)
        assert result.has_paradox
        assert result.source == "A"
        assert result.target == "B"

    def test_edge_without_type_in_graph(self):
        """Edge in graph without type attribute should not crash."""
        import networkx as nx
        graph = nx.DiGraph()
        graph.add_edge("A", "B")  # No type attribute

        detector = ParadoxDetector(graph)

        tx = Transaction()
        tx.add_edge("A", "B", "some_relation")

        # Should not crash, and no paradox since existing has no type
        result = detector.detect(tx)
        assert not result.has_paradox


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
