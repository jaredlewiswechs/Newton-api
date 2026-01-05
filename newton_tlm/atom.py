#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TLM - ATOM
Immutable symbolic atoms in the language machine.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from typing import Any, Dict
import time


@dataclass(frozen=True)
class Atom:
    """
    An immutable atom in the topological language machine.
    
    Atoms are the fundamental units of symbolic computation.
    Once created, they cannot be modified (frozen=True).
    
    Attributes:
        id: Unique identifier for this atom
        kind: Type/category of the atom
        value: The actual data payload
        layer: Which layer in the hierarchy this atom belongs to
        ts: Timestamp when atom was created
    """
    id: str
    kind: str
    value: Any
    layer: int
    ts: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize atom to dictionary.
        
        Returns:
            Dictionary representation of the atom
        """
        return {
            "id": self.id,
            "kind": self.kind,
            "value": self.value,
            "layer": self.layer,
            "ts": self.ts
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Atom':
        """
        Deserialize atom from dictionary.
        
        Args:
            data: Dictionary with atom fields
            
        Returns:
            Reconstructed Atom instance
        """
        return Atom(
            id=data["id"],
            kind=data["kind"],
            value=data["value"],
            layer=data["layer"],
            ts=data["ts"]
        )
    
    @staticmethod
    def create(id: str, kind: str, value: Any, layer: int = 0) -> 'Atom':
        """
        Factory method to create a new atom with automatic timestamp.
        
        Args:
            id: Unique identifier
            kind: Type/category
            value: Data payload
            layer: Layer in hierarchy (default: 0)
            
        Returns:
            New immutable Atom instance
        """
        return Atom(
            id=id,
            kind=kind,
            value=value,
            layer=layer,
            ts=time.time()
        )
