#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - REVERSIBILITY
Snapshot, restore, and rollback operations for verified reversibility.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import copy


@dataclass
class InverseOperation:
    """
    Represents the inverse of an operation for rollback.
    
    Attributes:
        operation_type: Type of operation (add_atom, add_edge, etc.)
        data: Data needed to reverse the operation
    """
    operation_type: str
    data: Any


def compute_inverse(operation: str, data: Any) -> InverseOperation:
    """
    Compute the inverse operation for a given operation.
    
    Args:
        operation: Operation type (e.g., "add_atom", "add_edge")
        data: Operation data
        
    Returns:
        InverseOperation that reverses the effect
    """
    # Map operations to their inverses
    inverse_map = {
        "add_atom": "remove_atom",
        "add_edge": "remove_edge",
        "increment_pattern": "decrement_pattern",
        "decrement_pattern": "increment_pattern",
        "remove_atom": "add_atom",
        "remove_edge": "add_edge"
    }
    
    inverse_type = inverse_map.get(operation, f"undo_{operation}")
    return InverseOperation(operation_type=inverse_type, data=data)


@dataclass
class Snapshot:
    """
    Complete state snapshot for restore/rollback.
    
    Captures the entire state of the TLM at a point in time,
    enabling perfect rollback and verification of reversibility.
    
    Attributes:
        index: Snapshot index/version
        state_hash: Hash of the state at snapshot time
        atoms: All atoms in the system
        edges: All edges in the system
        patterns: All pattern counts
        phase: Current phase at snapshot time
        ledger_size: Size of ledger at snapshot time
        metadata: Additional snapshot metadata
    """
    index: int
    state_hash: str
    atoms: List[Dict[str, Any]]
    edges: List[tuple]
    patterns: Dict[str, int]
    phase: str
    ledger_size: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize snapshot to dictionary.
        
        Returns:
            Dictionary representation of snapshot
        """
        return {
            "index": self.index,
            "state_hash": self.state_hash,
            "atoms": self.atoms,
            "edges": self.edges,
            "patterns": self.patterns,
            "phase": self.phase,
            "ledger_size": self.ledger_size,
            "metadata": self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Snapshot':
        """
        Deserialize snapshot from dictionary.
        
        Args:
            data: Dictionary with snapshot fields
            
        Returns:
            Reconstructed Snapshot instance
        """
        return Snapshot(
            index=data["index"],
            state_hash=data["state_hash"],
            atoms=data["atoms"],
            edges=data["edges"],
            patterns=data["patterns"],
            phase=data["phase"],
            ledger_size=data["ledger_size"],
            metadata=data["metadata"]
        )
    
    def deep_copy(self) -> 'Snapshot':
        """
        Create a deep copy of this snapshot.
        
        Returns:
            Independent copy of the snapshot
        """
        return Snapshot(
            index=self.index,
            state_hash=self.state_hash,
            atoms=copy.deepcopy(self.atoms),
            edges=copy.deepcopy(self.edges),
            patterns=copy.deepcopy(self.patterns),
            phase=self.phase,
            ledger_size=self.ledger_size,
            metadata=copy.deepcopy(self.metadata)
        )


class SnapshotManager:
    """
    Manages snapshots for rollback capability.
    
    Attributes:
        snapshots: List of stored snapshots
        max_snapshots: Maximum number of snapshots to keep
    """
    
    def __init__(self, max_snapshots: int = 100):
        self.snapshots: List[Snapshot] = []
        self.max_snapshots = max_snapshots
    
    def save_snapshot(self, snapshot: Snapshot) -> None:
        """
        Save a snapshot.
        
        Args:
            snapshot: Snapshot to save
        """
        self.snapshots.append(snapshot)
        
        # Trim old snapshots if needed
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
    
    def get_latest(self) -> Optional[Snapshot]:
        """
        Get the most recent snapshot.
        
        Returns:
            Latest snapshot or None if no snapshots
        """
        return self.snapshots[-1] if self.snapshots else None
    
    def get_by_index(self, index: int) -> Optional[Snapshot]:
        """
        Get snapshot by index.
        
        Args:
            index: Snapshot index to retrieve
            
        Returns:
            Snapshot with matching index or None
        """
        for snapshot in self.snapshots:
            if snapshot.index == index:
                return snapshot
        return None
    
    def clear(self) -> None:
        """
        Clear all snapshots.
        """
        self.snapshots.clear()
    
    def count(self) -> int:
        """
        Get number of stored snapshots.
        
        Returns:
            Number of snapshots
        """
        return len(self.snapshots)
