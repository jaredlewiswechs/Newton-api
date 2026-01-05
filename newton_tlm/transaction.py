#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - TRANSACTION
Atomic mutation buffer for verified state transitions.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from .atom import Atom


@dataclass
class Transaction:
    """
    Atomic transaction buffer for collecting mutations before commit.
    
    Nothing touches the model state until commit() is called.
    This ensures atomicity: either all changes apply or none do.
    
    Attributes:
        atoms: New atoms to be added
        edges: New edges to be added (from_id, to_id, edge_type)
        pattern_deltas: Changes to pattern counts
        committed: Whether this transaction has been committed
    """
    atoms: List[Atom] = field(default_factory=list)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)
    pattern_deltas: Dict[str, int] = field(default_factory=dict)
    committed: bool = False
    
    def add_atom(self, atom: Atom) -> None:
        """
        Add an atom to the transaction buffer.
        
        Args:
            atom: Atom to add
            
        Raises:
            RuntimeError: If transaction already committed
        """
        if self.committed:
            raise RuntimeError("Cannot add to committed transaction")
        self.atoms.append(atom)
    
    def add_edge(self, from_id: str, to_id: str, edge_type: str) -> None:
        """
        Add an edge to the transaction buffer.
        
        Args:
            from_id: Source atom ID
            to_id: Target atom ID
            edge_type: Type of edge/relationship
            
        Raises:
            RuntimeError: If transaction already committed
        """
        if self.committed:
            raise RuntimeError("Cannot add to committed transaction")
        self.edges.append((from_id, to_id, edge_type))
    
    def update_pattern(self, pattern: str, delta: int) -> None:
        """
        Update pattern count in the transaction buffer.
        
        Args:
            pattern: Pattern identifier
            delta: Amount to change the count by
            
        Raises:
            RuntimeError: If transaction already committed
        """
        if self.committed:
            raise RuntimeError("Cannot modify committed transaction")
        self.pattern_deltas[pattern] = self.pattern_deltas.get(pattern, 0) + delta
    
    def commit(self) -> None:
        """
        Mark transaction as committed.
        
        This signals that all changes have been applied to the model state.
        """
        self.committed = True
    
    def abort(self) -> None:
        """
        Abort transaction and clear all pending changes.
        
        All buffered changes are discarded.
        """
        self.atoms.clear()
        self.edges.clear()
        self.pattern_deltas.clear()
        self.committed = False
    
    def is_empty(self) -> bool:
        """
        Check if transaction has any pending changes.
        
        Returns:
            True if transaction buffer is empty
        """
        return (
            len(self.atoms) == 0 and
            len(self.edges) == 0 and
            len(self.pattern_deltas) == 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize transaction to dictionary.
        
        Returns:
            Dictionary representation of transaction
        """
        return {
            "atoms": [a.to_dict() for a in self.atoms],
            "edges": self.edges,
            "pattern_deltas": self.pattern_deltas,
            "committed": self.committed
        }
