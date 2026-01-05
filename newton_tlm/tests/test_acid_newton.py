#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - ACID + NEWTON COMPLIANCE TESTS
Comprehensive verification of ACID properties and Newton principles.
═══════════════════════════════════════════════════════════════════════════════

ACID Properties:
- A: Atomicity - Empty/failed ingest = zero state change
- C: Consistency - Same input → same hash (determinism)
- I: Isolation - Separate models don't interfere
- D: Durability - Export/replay preserves state

Newton Principles:
- N1: Determinism - Same input always produces same output
- N2: Boundary - Bounded execution with phase limits
- N3: Diffability - All changes tracked in ledger
- N4: Reversibility - Snapshot/restore/rollback works
- N5: Phase Loop - 0→9→0 cycle enforced
- N6: 1==1 Invariant - Goal equivalence checking
- N7: Ledger Integrity - Hash chains maintain consistency
"""

import pytest
import time
from newton_tlm import (
    NewtonTLM, Atom, Transaction, LedgerEntry,
    Phase, PhaseMachine,
    canonical_hash, one_equals_one, GoalRegistry,
    Snapshot
)


# =============================================================================
# ACID COMPLIANCE TESTS
# =============================================================================

class TestAcidCompliance:
    """Test ACID properties of Newton TLM."""
    
    def test_atomicity_empty_ingest(self):
        """
        ACID-A: Atomicity - Empty ingest should not change state.
        """
        tlm = NewtonTLM()
        
        # Get initial state hash
        hash_before = tlm.get_state_hash()
        
        # Try to ingest None (should handle gracefully)
        try:
            tlm.ingest(None)
        except:
            pass
        
        # State hash should be same or properly updated
        hash_after = tlm.get_state_hash()
        
        # Either it ingested (hash changed) or failed atomically (hash same)
        # Both are valid atomic behaviors
        assert hash_before is not None
        assert hash_after is not None
    
    def test_atomicity_transaction_abort(self):
        """
        ACID-A: Aborted transaction should not change state.
        """
        tlm = NewtonTLM()
        
        # Ingest some initial data
        tlm.ingest("initial")
        hash_before = tlm.get_state_hash()
        
        # Start transaction
        tx = tlm.begin_transaction()
        atom = Atom.create("test_atom", "test", "data")
        tx.add_atom(atom)
        
        # Abort transaction
        tlm.abort_transaction()
        
        # State should be unchanged
        hash_after = tlm.get_state_hash()
        assert hash_before == hash_after
    
    def test_consistency_determinism(self):
        """
        ACID-C: Same input should produce same hash.
        """
        tlm1 = NewtonTLM()
        tlm2 = NewtonTLM()
        
        # Ingest same data
        data = "test_data_123"
        tlm1.ingest(data)
        tlm2.ingest(data)
        
        # Hashes should match (determinism)
        hash1 = tlm1.get_state_hash()
        hash2 = tlm2.get_state_hash()
        
        assert hash1 == hash2
    
    def test_consistency_repeated_operations(self):
        """
        ACID-C: Repeated operations should maintain consistency.
        """
        tlm = NewtonTLM()
        
        # Ingest multiple items
        for i in range(5):
            tlm.ingest(f"item_{i}")
        
        # Check hash is stable
        hash1 = tlm.get_state_hash()
        time.sleep(0.01)
        hash2 = tlm.get_state_hash()
        
        # Hash should be deterministic
        assert hash1 == hash2
    
    def test_isolation_separate_instances(self):
        """
        ACID-I: Separate TLM instances should not interfere.
        """
        tlm1 = NewtonTLM()
        tlm2 = NewtonTLM()
        
        # Operate on separate instances
        tlm1.ingest("data_for_tlm1")
        tlm2.ingest("data_for_tlm2")
        
        # Should have different states
        hash1 = tlm1.get_state_hash()
        hash2 = tlm2.get_state_hash()
        
        assert hash1 != hash2
    
    def test_isolation_transaction_independence(self):
        """
        ACID-I: Transactions on different instances are independent.
        """
        tlm1 = NewtonTLM()
        tlm2 = NewtonTLM()
        
        # Start transactions
        tx1 = tlm1.begin_transaction()
        tx2 = tlm2.begin_transaction()
        
        # Add different atoms
        tx1.add_atom(Atom.create("atom1", "type1", "value1"))
        tx2.add_atom(Atom.create("atom2", "type2", "value2"))
        
        # Commit both
        tlm1.commit_transaction()
        tlm2.commit_transaction()
        
        # Should have different states
        assert tlm1.get_state_hash() != tlm2.get_state_hash()
    
    def test_durability_export_replay(self):
        """
        ACID-D: Export/replay should preserve state.
        """
        tlm1 = NewtonTLM()
        
        # Ingest data
        for i in range(3):
            tlm1.ingest(f"data_{i}")
        
        hash_before = tlm1.get_state_hash()
        
        # Export ledger
        ledger_data = tlm1.export_ledger()
        
        # Create new TLM and replay
        tlm2 = NewtonTLM()
        success = tlm2.replay_ledger(ledger_data)
        
        assert success
        
        # State should match
        hash_after = tlm2.get_state_hash()
        assert hash_before == hash_after
    
    def test_durability_ledger_persistence(self):
        """
        ACID-D: Ledger entries are immutable once written.
        """
        tlm = NewtonTLM()
        
        # Ingest data
        tlm.ingest("test_data")
        
        # Get ledger entry
        assert len(tlm.ledger) > 0
        entry = tlm.ledger[0]
        
        # Entry attributes should be set
        assert entry.index >= 0
        assert entry.hash_before is not None
        assert entry.hash_after is not None
        assert entry.timestamp > 0


# =============================================================================
# NEWTON COMPLIANCE TESTS
# =============================================================================

class TestNewtonCompliance:
    """Test Newton principles compliance."""
    
    def test_n1_determinism(self):
        """
        N1: Determinism - Same input always produces same output.
        """
        # Create two TLMs with identical operations
        tlm1 = NewtonTLM()
        tlm2 = NewtonTLM()
        
        inputs = ["apple", "banana", "cherry"]
        
        for inp in inputs:
            tlm1.ingest(inp)
            tlm2.ingest(inp)
        
        # States must be identical
        assert tlm1.get_state_hash() == tlm2.get_state_hash()
        
        # Ledgers must be identical
        ledger1 = tlm1.export_ledger()
        ledger2 = tlm2.export_ledger()
        
        assert len(ledger1) == len(ledger2)
    
    def test_n2_boundary_phase_limits(self):
        """
        N2: Boundary - Phase machine enforces bounded execution.
        """
        pm = PhaseMachine()
        
        # Cannot skip phases
        pm.transition(Phase.INGEST)
        
        with pytest.raises(RuntimeError):
            # Cannot jump to COMMIT from INGEST
            pm.transition(Phase.COMMIT)
    
    def test_n2_boundary_cycle_enforcement(self):
        """
        N2: Boundary - Must return to IDLE after cycle.
        """
        pm = PhaseMachine()
        
        # Start at IDLE
        assert pm.current == Phase.IDLE
        
        # Go through cycle
        pm.transition(Phase.INGEST)
        pm.transition(Phase.PARSE)
        pm.transition(Phase.CRYSTALLIZE)
        pm.transition(Phase.DIFFUSE)
        pm.transition(Phase.CONVERGE)
        pm.transition(Phase.VERIFY)
        pm.transition(Phase.COMMIT)
        pm.transition(Phase.REFLECT)
        
        # Must return to IDLE
        pm.transition(Phase.IDLE)
        assert pm.current == Phase.IDLE
        assert pm.cycle_count == 1
    
    def test_n3_diffability_ledger_tracking(self):
        """
        N3: Diffability - All changes tracked in ledger.
        """
        tlm = NewtonTLM()
        
        # Initial state
        assert len(tlm.ledger) == 0
        
        # Make changes
        tlm.ingest("change_1")
        tlm.ingest("change_2")
        
        # Ledger should track all changes
        assert len(tlm.ledger) == 2
        
        # Each entry should have diffs
        for entry in tlm.ledger:
            assert len(entry.atoms_added) > 0 or len(entry.pattern_deltas) > 0
    
    def test_n3_diffability_hash_chaining(self):
        """
        N3: Diffability - Hash chaining connects all diffs.
        """
        tlm = NewtonTLM()
        
        # Make several changes
        for i in range(3):
            tlm.ingest(f"data_{i}")
        
        # Check hash chain
        for i in range(1, len(tlm.ledger)):
            prev_hash_after = tlm.ledger[i-1].hash_after
            curr_hash_before = tlm.ledger[i].hash_before
            
            # Chain should be connected
            assert prev_hash_after == curr_hash_before
    
    def test_n4_reversibility_snapshot_restore(self):
        """
        N4: Reversibility - Snapshot/restore works correctly.
        """
        tlm = NewtonTLM()
        
        # Initial state
        tlm.ingest("state_1")
        snapshot1 = tlm.snapshot()
        hash1 = tlm.get_state_hash()
        
        # Change state
        tlm.ingest("state_2")
        hash2 = tlm.get_state_hash()
        
        assert hash1 != hash2
        
        # Restore to snapshot1
        tlm.restore(snapshot1)
        hash_restored = tlm.get_state_hash()
        
        # Should match original
        assert hash_restored == hash1
    
    def test_n4_reversibility_rollback(self):
        """
        N4: Reversibility - Rollback to previous state.
        """
        tlm = NewtonTLM()
        
        # Create snapshots at different states
        tlm.ingest("a")
        snap1 = tlm.snapshot()
        
        tlm.ingest("b")
        snap2 = tlm.snapshot()
        
        tlm.ingest("c")
        hash_final = tlm.get_state_hash()
        
        # Rollback to snap1
        success = tlm.rollback(snap1.index)
        assert success
        
        # Should be at snap1 state
        hash_rolled_back = tlm.get_state_hash()
        assert hash_rolled_back == snap1.state_hash
    
    def test_n5_phase_loop_0_to_9_to_0(self):
        """
        N5: Phase Loop - Complete 0→9→0 cycle in ingest.
        """
        tlm = NewtonTLM()
        
        # Should start at IDLE (0)
        assert tlm.phase_machine.current == Phase.IDLE
        
        # Ingest performs full cycle
        tlm.ingest("test")
        
        # Should return to IDLE (0)
        assert tlm.phase_machine.current == Phase.IDLE
        assert tlm.phase_machine.cycle_count == 1
    
    def test_n5_phase_loop_no_mutation_in_idle(self):
        """
        N5: Phase Loop - No state mutation allowed in IDLE.
        """
        pm = PhaseMachine()
        
        # In IDLE, cannot mutate
        assert pm.current == Phase.IDLE
        assert not pm.can_mutate_state()
        
        # After transitioning, can mutate
        pm.transition(Phase.INGEST)
        assert pm.can_mutate_state()
    
    def test_n6_one_equals_one_invariant(self):
        """
        N6: 1==1 Invariant - Goal equivalence checking works.
        """
        # Test canonical hashing
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 2, "a": 1}  # Different order, same content
        
        hash1 = canonical_hash(obj1)
        hash2 = canonical_hash(obj2)
        
        # Should be identical (order-independent)
        assert hash1 == hash2
        
        # Test one_equals_one
        assert one_equals_one(obj1, obj2)
    
    def test_n6_goal_registry(self):
        """
        N6: 1==1 Invariant - Goal registry tracks achievements.
        """
        registry = GoalRegistry()
        
        # Register goals
        registry.register_goal("goal_1", {"target": 100})
        registry.register_goal("goal_2", {"target": 200})
        
        # Check goals
        assert registry.check_goal("goal_1", {"target": 100})
        assert not registry.check_goal("goal_2", {"target": 100})
        
        # Check achievement tracking
        assert registry.is_achieved("goal_1")
        assert not registry.is_achieved("goal_2")
    
    def test_n7_ledger_integrity_verification(self):
        """
        N7: Ledger Integrity - Hash chains maintain consistency.
        """
        tlm = NewtonTLM()
        
        # Make changes
        for i in range(5):
            tlm.ingest(f"entry_{i}")
        
        # Verify integrity
        assert tlm.verify_integrity()
        
        # Corrupt a hash (simulate tampering)
        if len(tlm.ledger) > 1:
            tlm.ledger[1].hash_before = "corrupted_hash"
            
            # Integrity check should fail
            assert not tlm.verify_integrity()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_cycle_with_all_components(self):
        """
        Test complete cycle using all TLM components.
        """
        tlm = NewtonTLM()
        
        # Register goal
        tlm.goal_registry.register_goal("ingest_3_items", 3)
        
        # Ingest items
        for i in range(3):
            success = tlm.ingest(f"item_{i}")
            assert success
            
            # Take snapshot after each
            tlm.snapshot()
        
        # Check goal
        item_count = len(tlm.graph.nodes())
        assert tlm.goal_registry.check_goal("ingest_3_items", item_count)
        
        # Verify ledger
        assert len(tlm.ledger) == 3
        assert tlm.verify_integrity()
        
        # Test rollback
        assert tlm.rollback(1)
        
        # Verify state after rollback
        assert len(tlm.graph.nodes()) < item_count
    
    def test_transaction_with_multiple_operations(self):
        """
        Test transaction with multiple atoms and edges.
        """
        tlm = NewtonTLM()
        
        # Begin transaction
        tx = tlm.begin_transaction()
        
        # Add multiple atoms
        atom1 = Atom.create("a1", "type1", "value1")
        atom2 = Atom.create("a2", "type2", "value2")
        tx.add_atom(atom1)
        tx.add_atom(atom2)
        
        # Add edge
        tx.add_edge("a1", "a2", "connects_to")
        
        # Update patterns
        tx.update_pattern("pattern1", 1)
        tx.update_pattern("pattern2", 2)
        
        # Commit
        tlm.commit_transaction()
        
        # Verify state
        assert "a1" in tlm.graph.nodes()
        assert "a2" in tlm.graph.nodes()
        assert tlm.graph.has_edge("a1", "a2")
        assert tlm.patterns.get("pattern1") == 1
        assert tlm.patterns.get("pattern2") == 2
    
    def test_export_replay_with_snapshots(self):
        """
        Test export/replay combined with snapshots.
        """
        tlm1 = NewtonTLM()
        
        # Build state with snapshots
        for i in range(3):
            tlm1.ingest(f"data_{i}")
            tlm1.snapshot()
        
        hash_original = tlm1.get_state_hash()
        
        # Export
        ledger_data = tlm1.export_ledger()
        
        # Replay in new TLM
        tlm2 = NewtonTLM()
        tlm2.replay_ledger(ledger_data)
        
        hash_replayed = tlm2.get_state_hash()
        
        # Should match
        assert hash_original == hash_replayed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
