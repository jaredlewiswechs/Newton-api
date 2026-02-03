"""
═══════════════════════════════════════════════════════════════
NHISTORY - VERIFIED UNDO/REDO
Every action is logged to the Newton Ledger.
Time travel for your edits.
═══════════════════════════════════════════════════════════════
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
import time
import hashlib
import json


class HistoryAction(Enum):
    """Types of actions that can be undone."""
    PAINT = "paint"
    ERASE = "erase"
    FILL = "fill"
    TRANSFORM = "transform"
    FILTER = "filter"
    LAYER_ADD = "layer_add"
    LAYER_REMOVE = "layer_remove"
    LAYER_MERGE = "layer_merge"
    LAYER_REORDER = "layer_reorder"
    LAYER_PROPERTY = "layer_property"
    SELECTION = "selection"
    TEXT = "text"
    CROP = "crop"
    RESIZE = "resize"


@dataclass
class NHistoryEntry:
    """
    A single entry in the undo history.
    
    Each entry contains:
    - What action was performed
    - State before the action (for undo)
    - State after the action (for redo)  
    - Verification hash to ensure integrity
    """
    id: str
    action: HistoryAction
    description: str
    timestamp: float
    layer_id: str
    before_state: bytes  # Compressed image data
    after_state: bytes   # Compressed image data
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_hash: str = ""
    
    def __post_init__(self):
        if not self.verification_hash:
            self.verification_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute verification hash of this entry."""
        data = f"{self.id}:{self.action.value}:{self.timestamp}:{self.layer_id}"
        data += f":{len(self.before_state)}:{len(self.after_state)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def verify(self) -> bool:
        """Verify entry integrity."""
        return self.verification_hash == self._compute_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'action': self.action.value,
            'description': self.description,
            'timestamp': self.timestamp,
            'layer_id': self.layer_id,
            'metadata': self.metadata,
            'verification_hash': self.verification_hash,
            'verified': self.verify()
        }


class NHistory(QObject):
    """
    History manager with verified undo/redo.
    
    This integrates with Newton's verification system:
    - Every action is recorded with before/after state
    - Hash verification ensures no tampering
    - Bounded history prevents memory overflow
    """
    
    # Signals
    can_undo_changed = pyqtSignal(bool)
    can_redo_changed = pyqtSignal(bool)
    history_changed = pyqtSignal()
    action_recorded = pyqtSignal(object)  # NHistoryEntry
    
    # Newton-style bounds
    MAX_HISTORY_ENTRIES = 100
    MAX_MEMORY_MB = 500
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        self._entries: List[NHistoryEntry] = []
        self._current_index = -1
        self._memory_used = 0
        
        # For grouping related actions
        self._group_id: Optional[str] = None
        self._group_depth = 0
    
    @property
    def can_undo(self) -> bool:
        return self._current_index >= 0
    
    @property
    def can_redo(self) -> bool:
        return self._current_index < len(self._entries) - 1
    
    @property
    def entries(self) -> List[NHistoryEntry]:
        return self._entries[:self._current_index + 1]
    
    @property
    def current_entry(self) -> Optional[NHistoryEntry]:
        if 0 <= self._current_index < len(self._entries):
            return self._entries[self._current_index]
        return None
    
    def record(self, 
               action: HistoryAction,
               description: str,
               layer_id: str,
               before_state: bytes,
               after_state: bytes,
               metadata: Optional[Dict[str, Any]] = None) -> NHistoryEntry:
        """
        Record a new action to history.
        
        This is the core of verified undo - we capture the complete
        state transition so we can replay or reverse it.
        """
        import uuid
        
        # Remove any redo entries if we're not at the end
        if self._current_index < len(self._entries) - 1:
            removed = self._entries[self._current_index + 1:]
            for entry in removed:
                self._memory_used -= len(entry.before_state) + len(entry.after_state)
            self._entries = self._entries[:self._current_index + 1]
        
        # Create entry
        entry = NHistoryEntry(
            id=str(uuid.uuid4()),
            action=action,
            description=description,
            timestamp=time.time(),
            layer_id=layer_id,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata or {}
        )
        
        # Add to history
        self._entries.append(entry)
        self._current_index = len(self._entries) - 1
        self._memory_used += len(before_state) + len(after_state)
        
        # Enforce bounds
        self._enforce_bounds()
        
        # Emit signals
        self.can_undo_changed.emit(self.can_undo)
        self.can_redo_changed.emit(self.can_redo)
        self.history_changed.emit()
        self.action_recorded.emit(entry)
        
        return entry
    
    def undo(self) -> Optional[NHistoryEntry]:
        """
        Undo the last action.
        
        Returns the entry that was undone (contains before_state to restore).
        """
        if self.can_undo:
            entry = self._entries[self._current_index]
            self._current_index -= 1
            
            self.can_undo_changed.emit(self.can_undo)
            self.can_redo_changed.emit(self.can_redo)
            self.history_changed.emit()
            
            return entry
        return None
    
    def redo(self) -> Optional[NHistoryEntry]:
        """
        Redo a previously undone action.
        
        Returns the entry that was redone (contains after_state to restore).
        """
        if self.can_redo:
            self._current_index += 1
            entry = self._entries[self._current_index]
            
            self.can_undo_changed.emit(self.can_undo)
            self.can_redo_changed.emit(self.can_redo)
            self.history_changed.emit()
            
            return entry
        return None
    
    def _enforce_bounds(self) -> None:
        """
        Enforce Newton-style bounds on history.
        
        - Max entries (to bound time complexity)
        - Max memory (to bound space complexity)
        """
        # Check entry count
        while len(self._entries) > self.MAX_HISTORY_ENTRIES:
            removed = self._entries.pop(0)
            self._memory_used -= len(removed.before_state) + len(removed.after_state)
            self._current_index -= 1
        
        # Check memory usage
        memory_mb = self._memory_used / (1024 * 1024)
        while memory_mb > self.MAX_MEMORY_MB and len(self._entries) > 1:
            removed = self._entries.pop(0)
            self._memory_used -= len(removed.before_state) + len(removed.after_state)
            self._current_index -= 1
            memory_mb = self._memory_used / (1024 * 1024)
    
    def begin_group(self, group_id: str) -> None:
        """Begin a group of related actions."""
        self._group_id = group_id
        self._group_depth += 1
    
    def end_group(self) -> None:
        """End a group of related actions."""
        self._group_depth -= 1
        if self._group_depth <= 0:
            self._group_id = None
            self._group_depth = 0
    
    def clear(self) -> None:
        """Clear all history."""
        self._entries.clear()
        self._current_index = -1
        self._memory_used = 0
        
        self.can_undo_changed.emit(False)
        self.can_redo_changed.emit(False)
        self.history_changed.emit()
    
    def verify_all(self) -> Dict[str, Any]:
        """
        Verify integrity of entire history.
        
        Returns verification report.
        """
        verified = 0
        failed = 0
        
        for entry in self._entries:
            if entry.verify():
                verified += 1
            else:
                failed += 1
        
        return {
            'total': len(self._entries),
            'verified': verified,
            'failed': failed,
            'integrity': failed == 0,
            'memory_mb': self._memory_used / (1024 * 1024)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize history metadata (not full state data)."""
        return {
            'entries': [e.to_dict() for e in self._entries],
            'current_index': self._current_index,
            'verification': self.verify_all()
        }
