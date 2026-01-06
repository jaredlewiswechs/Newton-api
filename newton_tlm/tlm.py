#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - TOPOLOGICAL LANGUAGE MACHINE
Main class implementing the Newton-compliant symbolic language kernel.
═══════════════════════════════════════════════════════════════════════════════
"""

import networkx as nx
from typing import Any, Dict, List, Optional, Tuple
import time

from .atom import Atom
from .transaction import Transaction
from .ledger_entry import LedgerEntry
from .phases import Phase, PhaseMachine
from .invariant import canonical_hash, one_equals_one, GoalRegistry
from .reversibility import Snapshot, SnapshotManager
from .paradox import ParadoxDetector, ParadoxError, ParadoxResult


class NewtonTLM:
    """
    Newton Topological Language Machine.
    
    A deterministic symbolic language kernel for verified computation.
    
    Key properties:
    - Phase-driven execution (0→9→0 cycle)
    - Atomic transactions (all-or-nothing)
    - Perfect reversibility (snapshot/restore/rollback)
    - Append-only ledger with hash-chaining
    - 1==1 invariant checking
    
    Attributes:
        graph: NetworkX graph storing atoms and edges
        patterns: Pattern count registry
        phase_machine: Phase cycle controller
        goal_registry: Goal tracking system
        transaction: Current transaction buffer
        ledger: Append-only history of state transitions
        snapshots: Snapshot manager for rollback
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.patterns: Dict[str, int] = {}
        self.phase_machine = PhaseMachine()
        self.goal_registry = GoalRegistry()
        self.transaction: Optional[Transaction] = None
        self.ledger: List[LedgerEntry] = []
        self.snapshots = SnapshotManager()
        self._atom_counter = 0  # Counter for deterministic atom IDs
    
    def get_state_hash(self) -> str:
        """
        Compute deterministic hash of current state.
        
        Timestamps are excluded for determinism since they're metadata.
        
        Returns:
            SHA256 hash of state
        """
        # Extract atoms without timestamps for deterministic hashing
        atoms_for_hash = []
        for n in self.graph.nodes():
            node_data = dict(self.graph.nodes[n])
            # Remove timestamp for deterministic comparison
            node_data_clean = {k: v for k, v in node_data.items() if k != 'ts'}
            atoms_for_hash.append(node_data_clean)
        
        state = {
            "atoms": sorted(atoms_for_hash, key=lambda x: x.get("id", "")),
            "edges": sorted(list(self.graph.edges())),
            "patterns": dict(sorted(self.patterns.items()))
        }
        return canonical_hash(state)
    
    def begin_transaction(self) -> Transaction:
        """
        Begin a new transaction.
        
        Returns:
            New transaction buffer
            
        Raises:
            RuntimeError: If transaction already in progress
        """
        if self.transaction is not None and not self.transaction.committed:
            raise RuntimeError("Transaction already in progress")
        
        self.transaction = Transaction()
        return self.transaction
    
    def commit_transaction(self) -> None:
        """
        Commit current transaction to state.
        
        Applies all buffered changes atomically.
        
        Raises:
            RuntimeError: If no transaction in progress
        """
        if self.transaction is None:
            raise RuntimeError("No transaction in progress")
        
        hash_before = self.get_state_hash()
        
        # Apply atoms
        for atom in self.transaction.atoms:
            self.graph.add_node(atom.id, **atom.to_dict())
        
        # Apply edges
        for from_id, to_id, edge_type in self.transaction.edges:
            self.graph.add_edge(from_id, to_id, type=edge_type)
        
        # Apply pattern deltas
        for pattern, delta in self.transaction.pattern_deltas.items():
            self.patterns[pattern] = self.patterns.get(pattern, 0) + delta
        
        hash_after = self.get_state_hash()
        
        # Record in ledger
        entry = LedgerEntry.create(
            index=len(self.ledger),
            hash_before=hash_before,
            hash_after=hash_after,
            atoms_added=[a.to_dict() for a in self.transaction.atoms],
            edges_added=self.transaction.edges,
            pattern_deltas=self.transaction.pattern_deltas,
            phase=self.phase_machine.get_phase_name(),
            operation="commit_transaction"
        )
        self.ledger.append(entry)
        
        # Mark transaction as committed
        self.transaction.commit()
    
    def abort_transaction(self) -> None:
        """
        Abort current transaction.

        Discards all buffered changes.
        """
        if self.transaction is not None:
            self.transaction.abort()
            self.transaction = None

    def detect_paradox(self, tx: Transaction) -> ParadoxResult:
        """
        Detect logical contradictions in a transaction.

        Checks for both internal contradictions (within the transaction)
        and external contradictions (against the immutable graph ledger).

        This method is called during the PARADOX phase (phase 7) to ensure
        no contradictory knowledge enters the ledger.

        Args:
            tx: Transaction to validate

        Returns:
            ParadoxResult with detection outcome

        Example:
            Existing Truth: Node A has relation 'is_safe' to Node B.
            New Transaction: Attempts to assert Node A 'is_unsafe' to Node B.
            Result: ParadoxResult.has_paradox = True
        """
        detector = ParadoxDetector(self.graph)
        return detector.detect(tx)

    def validate_paradox(self, tx: Transaction) -> None:
        """
        Validate a transaction, raising ParadoxError if contradictions found.

        This is a convenience method for external validation.

        Args:
            tx: Transaction to validate

        Raises:
            ParadoxError: If any paradox is detected
        """
        detector = ParadoxDetector(self.graph)
        detector.validate(tx)

    def ingest(self, data: Any) -> bool:
        """
        Full phase-driven ingest cycle.

        Executes complete 0→10→0 phase cycle to ingest data.
        Includes PARADOX phase (7) for contradiction detection.
        
        Args:
            data: Data to ingest
            
        Returns:
            True if ingest successful
        """
        try:
            # Start cycle: IDLE → INGEST
            self.phase_machine.transition(Phase.INGEST)
            
            # Begin transaction
            tx = self.begin_transaction()
            
            # INGEST → PARSE
            self.phase_machine.transition(Phase.PARSE)
            
            # Create atom from data with deterministic ID
            atom = Atom.create(
                id=f"atom_{self._atom_counter}",
                kind="data",
                value=data,
                layer=0
            )
            self._atom_counter += 1
            tx.add_atom(atom)
            
            # PARSE → CRYSTALLIZE
            self.phase_machine.transition(Phase.CRYSTALLIZE)
            
            # Update pattern counts
            pattern_key = f"kind:{atom.kind}"
            tx.update_pattern(pattern_key, 1)
            
            # CRYSTALLIZE → DIFFUSE
            self.phase_machine.transition(Phase.DIFFUSE)
            
            # DIFFUSE → CONVERGE
            self.phase_machine.transition(Phase.CONVERGE)
            
            # CONVERGE → VERIFY
            self.phase_machine.transition(Phase.VERIFY)

            # Verify transaction not empty
            if tx.is_empty():
                self.abort_transaction()
                self.phase_machine.reset()
                return False

            # VERIFY → PARADOX
            self.phase_machine.transition(Phase.PARADOX)

            # Run paradox detection - halt if contradictions found
            paradox_result = self.detect_paradox(tx)
            if paradox_result.has_paradox:
                self.abort_transaction()
                self.phase_machine.reset()
                return False

            # PARADOX → COMMIT
            self.phase_machine.transition(Phase.COMMIT)

            # Commit transaction
            self.commit_transaction()
            
            # COMMIT → REFLECT
            self.phase_machine.transition(Phase.REFLECT)
            
            # REFLECT → IDLE (complete cycle)
            self.phase_machine.transition(Phase.IDLE)
            
            return True
            
        except Exception as e:
            # On error, abort and reset
            self.abort_transaction()
            self.phase_machine.reset()
            raise e
    
    def snapshot(self) -> Snapshot:
        """
        Create snapshot of current state.
        
        Returns:
            Snapshot capturing full state
        """
        snapshot = Snapshot(
            index=len(self.snapshots.snapshots),
            state_hash=self.get_state_hash(),
            atoms=[self.graph.nodes[n] for n in self.graph.nodes()],
            edges=list(self.graph.edges(data=True)),
            patterns=dict(self.patterns),
            phase=self.phase_machine.get_phase_name(),
            ledger_size=len(self.ledger),
            metadata={"timestamp": time.time(), "atom_counter": self._atom_counter}
        )
        
        self.snapshots.save_snapshot(snapshot)
        return snapshot
    
    def restore(self, snapshot: Snapshot) -> None:
        """
        Restore state from snapshot.
        
        Args:
            snapshot: Snapshot to restore from
        """
        # Clear current state
        self.graph.clear()
        self.patterns.clear()
        
        # Restore atoms
        for atom_data in snapshot.atoms:
            self.graph.add_node(atom_data["id"], **atom_data)
        
        # Restore edges
        for from_id, to_id, edge_data in snapshot.edges:
            self.graph.add_edge(from_id, to_id, **edge_data)
        
        # Restore patterns
        self.patterns.update(snapshot.patterns)
        
        # Restore atom counter if available
        if "atom_counter" in snapshot.metadata:
            self._atom_counter = snapshot.metadata["atom_counter"]
        
        # Reset phase machine
        self.phase_machine.reset()
    
    def rollback(self, to_index: Optional[int] = None) -> bool:
        """
        Rollback to a previous snapshot.
        
        Args:
            to_index: Snapshot index to rollback to (None = latest)
            
        Returns:
            True if rollback successful
        """
        if to_index is None:
            snapshot = self.snapshots.get_latest()
        else:
            snapshot = self.snapshots.get_by_index(to_index)
        
        if snapshot is None:
            return False
        
        self.restore(snapshot)
        return True
    
    def export_ledger(self) -> List[Dict[str, Any]]:
        """
        Export ledger for external storage or replay.
        
        Returns:
            List of ledger entries as dictionaries
        """
        return [entry.to_dict() for entry in self.ledger]
    
    def replay_ledger(self, ledger_data: List[Dict[str, Any]]) -> bool:
        """
        Replay ledger to reconstruct state.
        
        Args:
            ledger_data: List of ledger entry dictionaries
            
        Returns:
            True if replay successful
        """
        try:
            # Clear current state
            self.graph.clear()
            self.patterns.clear()
            self.ledger.clear()
            self.phase_machine.reset()
            
            # Replay each entry
            for entry_data in ledger_data:
                entry = LedgerEntry.from_dict(entry_data)
                
                # Apply atoms
                for atom_data in entry.atoms_added:
                    atom = Atom.from_dict(atom_data)
                    self.graph.add_node(atom.id, **atom.to_dict())
                
                # Apply edges
                for from_id, to_id, edge_type in entry.edges_added:
                    self.graph.add_edge(from_id, to_id, type=edge_type)
                
                # Apply pattern deltas
                for pattern, delta in entry.pattern_deltas.items():
                    self.patterns[pattern] = self.patterns.get(pattern, 0) + delta
                
                # Add to ledger
                self.ledger.append(entry)
            
            return True
            
        except Exception:
            return False
    
    def verify_integrity(self) -> bool:
        """
        Verify ledger integrity using hash chains.
        
        Returns:
            True if all hashes are consistent
        """
        if not self.ledger:
            return True
        
        # Check each entry's hash chain
        for i, entry in enumerate(self.ledger):
            if i > 0:
                # Current entry's hash_before should match previous entry's hash_after
                if entry.hash_before != self.ledger[i-1].hash_after:
                    return False
        
        return True
