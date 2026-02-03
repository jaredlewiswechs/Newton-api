"""
═══════════════════════════════════════════════════════════════
NOBJECT - THE ATOMIC UNIT
Everything in Newton OS is an NObject.
QObject provides signals/slots for true reactivity.
═══════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import uuid
import time


@dataclass
class NProperty:
    """A verified property with change tracking."""
    name: str
    value: Any
    type_hint: str = "any"
    verified: bool = False
    constraints: List[Dict] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)
    
    def set(self, new_value: Any) -> bool:
        """Set value, tracking history."""
        old_value = self.value
        self.history.append({
            'from': old_value,
            'to': new_value,
            'timestamp': time.time()
        })
        self.value = new_value
        return True
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type_hint,
            'verified': self.verified,
            'constraints': self.constraints
        }


@dataclass  
class NRelationship:
    """A relationship between NObjects - also an NObject."""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    bidirectional: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'source': self.source_id,
            'target': self.target_id,
            'type': self.type,
            'properties': self.properties,
            'bidirectional': self.bidirectional
        }


class NObject(QObject):
    """
    The fundamental unit of Newton OS.
    
    Every object in the system inherits from NObject:
    - Windows are NObjects
    - Files are NObjects  
    - Relationships are NObjects
    - The dock is an NObject
    - Even properties can be NObjects
    
    QObject base provides:
    - Signals/slots for reactivity
    - Parent/child hierarchy
    - Memory management
    """
    
    # Signals for reactivity
    property_changed = pyqtSignal(str, object, object)  # name, old, new
    relationship_added = pyqtSignal(object)  # NRelationship
    relationship_removed = pyqtSignal(str)  # relationship_id
    verified = pyqtSignal(bool, dict)  # success, result
    destroyed_signal = pyqtSignal(str)  # object_id
    
    def __init__(self, 
                 object_type: str = "NObject",
                 parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Core identity
        self._id = str(uuid.uuid4())
        self._type = object_type
        self._created = time.time()
        
        # Property storage
        self._properties: Dict[str, NProperty] = {}
        
        # Relationships (by ID)
        self._relationships: List[str] = []
        
        # Verification state
        self._verified = False
        self._verification_result: Optional[Dict] = None
        
        # Tags for querying
        self._tags: List[str] = []
        
        # Register with global graph
        from .graph import TheGraph
        TheGraph.register(self)
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def object_type(self) -> str:
        return self._type
    
    @property
    def created(self) -> float:
        return self._created
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    # ═══════════════════════════════════════════════════════════
    # PROPERTY MANAGEMENT
    # ═══════════════════════════════════════════════════════════
    
    def set_property(self, name: str, value: Any, 
                     type_hint: str = "any",
                     constraints: Optional[List[Dict]] = None) -> bool:
        """Set a property with optional constraints."""
        old_value = None
        
        if name in self._properties:
            old_value = self._properties[name].value
            self._properties[name].set(value)
        else:
            self._properties[name] = NProperty(
                name=name,
                value=value,
                type_hint=type_hint,
                constraints=constraints or []
            )
        
        # Emit change signal
        self.property_changed.emit(name, old_value, value)
        return True
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property value."""
        if name in self._properties:
            return self._properties[name].value
        return default
    
    def get_property_object(self, name: str) -> Optional[NProperty]:
        """Get the full property object with history."""
        return self._properties.get(name)
    
    def has_property(self, name: str) -> bool:
        return name in self._properties
    
    def list_properties(self) -> List[str]:
        return list(self._properties.keys())
    
    # ═══════════════════════════════════════════════════════════
    # TAGS
    # ═══════════════════════════════════════════════════════════
    
    def add_tag(self, tag: str) -> None:
        if tag not in self._tags:
            self._tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        if tag in self._tags:
            self._tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        return tag in self._tags
    
    # ═══════════════════════════════════════════════════════════
    # RELATIONSHIPS  
    # ═══════════════════════════════════════════════════════════
    
    def add_relationship(self, relationship_id: str) -> None:
        """Track a relationship ID."""
        if relationship_id not in self._relationships:
            self._relationships.append(relationship_id)
    
    def remove_relationship(self, relationship_id: str) -> None:
        """Remove relationship tracking."""
        if relationship_id in self._relationships:
            self._relationships.remove(relationship_id)
            self.relationship_removed.emit(relationship_id)
    
    def get_relationships(self) -> List[str]:
        """Get all relationship IDs."""
        return self._relationships.copy()
    
    # ═══════════════════════════════════════════════════════════
    # VERIFICATION (Newton Agent integration)
    # ═══════════════════════════════════════════════════════════
    
    def verify(self, constraint: Optional[Dict] = None) -> bool:
        """
        Verify this object against constraints.
        Uses Newton Agent for verification.
        """
        try:
            # Import here to avoid circular dependency
            from newton_agent import NewtonAgent
            
            agent = NewtonAgent()
            
            # Build verification request
            data = self.to_dict()
            if constraint:
                data['_constraint'] = constraint
            
            # Use CDL verification
            result = agent.verify_constraint(constraint or {}, data)
            
            self._verified = result.get('verified', False)
            self._verification_result = result
            self.verified.emit(self._verified, result)
            
            return self._verified
            
        except ImportError:
            # Newton Agent not available, mark as unverified
            self._verified = False
            return False
    
    @property
    def is_verified(self) -> bool:
        return self._verified
    
    # ═══════════════════════════════════════════════════════════
    # SERIALIZATION
    # ═══════════════════════════════════════════════════════════
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'id': self._id,
            'type': self._type,
            'created': self._created,
            'properties': {
                name: prop.to_dict() 
                for name, prop in self._properties.items()
            },
            'relationships': self._relationships,
            'tags': self._tags,
            'verified': self._verified
        }
    
    @classmethod
    def from_dict(cls, data: Dict, parent: Optional[QObject] = None) -> 'NObject':
        """Deserialize from dictionary."""
        obj = cls(object_type=data.get('type', 'NObject'), parent=parent)
        obj._id = data.get('id', obj._id)
        obj._created = data.get('created', obj._created)
        obj._tags = data.get('tags', [])
        obj._verified = data.get('verified', False)
        
        # Restore properties
        for name, prop_data in data.get('properties', {}).items():
            obj.set_property(
                name=name,
                value=prop_data.get('value'),
                type_hint=prop_data.get('type', 'any'),
                constraints=prop_data.get('constraints', [])
            )
        
        return obj
    
    # ═══════════════════════════════════════════════════════════
    # CLEANUP
    # ═══════════════════════════════════════════════════════════
    
    def destroy(self) -> None:
        """Clean removal from graph."""
        self.destroyed_signal.emit(self._id)
        from .graph import TheGraph
        TheGraph.unregister(self._id)
        self.deleteLater()
    
    def __repr__(self) -> str:
        return f"<NObject:{self._type} id={self._id[:8]}>"
