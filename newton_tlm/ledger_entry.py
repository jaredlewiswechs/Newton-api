#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - LEDGER ENTRY
Canonical diff format for append-only ledger.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import time


@dataclass
class LedgerEntry:
    """
    Canonical diff format for append-only ledger.
    
    Each entry represents a verified state transition with hash-chaining
    for integrity verification and perfect replay capability.
    
    Attributes:
        index: Sequential index in the ledger
        timestamp: When this entry was created
        hash_before: Hash of state before transition
        hash_after: Hash of state after transition
        atoms_added: List of atoms added in this transition
        edges_added: List of edges added (from_id, to_id, edge_type)
        pattern_deltas: Changes to pattern counts
        phase: Which phase this transition occurred in
        operation: Description of the operation
    """
    index: int
    timestamp: float
    hash_before: str
    hash_after: str
    atoms_added: List[Dict[str, Any]]
    edges_added: List[Tuple[str, str, str]]
    pattern_deltas: Dict[str, int]
    phase: str
    operation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize ledger entry to dictionary.
        
        Returns:
            Dictionary representation of the entry
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "hash_before": self.hash_before,
            "hash_after": self.hash_after,
            "atoms_added": self.atoms_added,
            "edges_added": self.edges_added,
            "pattern_deltas": self.pattern_deltas,
            "phase": self.phase,
            "operation": self.operation
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LedgerEntry':
        """
        Deserialize ledger entry from dictionary.
        
        Args:
            data: Dictionary with entry fields
            
        Returns:
            Reconstructed LedgerEntry instance
        """
        return LedgerEntry(
            index=data["index"],
            timestamp=data["timestamp"],
            hash_before=data["hash_before"],
            hash_after=data["hash_after"],
            atoms_added=data["atoms_added"],
            edges_added=data["edges_added"],
            pattern_deltas=data["pattern_deltas"],
            phase=data["phase"],
            operation=data["operation"]
        )
    
    @staticmethod
    def create(
        index: int,
        hash_before: str,
        hash_after: str,
        atoms_added: List[Dict[str, Any]],
        edges_added: List[Tuple[str, str, str]],
        pattern_deltas: Dict[str, int],
        phase: str,
        operation: str
    ) -> 'LedgerEntry':
        """
        Factory method to create a new ledger entry with automatic timestamp.
        
        Args:
            index: Sequential index in ledger
            hash_before: Hash before transition
            hash_after: Hash after transition
            atoms_added: Atoms added
            edges_added: Edges added
            pattern_deltas: Pattern count changes
            phase: Current phase
            operation: Operation description
            
        Returns:
            New LedgerEntry instance
        """
        return LedgerEntry(
            index=index,
            timestamp=time.time(),
            hash_before=hash_before,
            hash_after=hash_after,
            atoms_added=atoms_added,
            edges_added=edges_added,
            pattern_deltas=pattern_deltas,
            phase=phase,
            operation=operation
        )
