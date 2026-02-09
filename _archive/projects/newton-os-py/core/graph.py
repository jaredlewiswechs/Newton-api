"""
═══════════════════════════════════════════════════════════════
NOBJECT GRAPH - THE UNIVERSE
All NObjects exist in TheGraph.
Query by constraint, not by path.
═══════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from PyQt6.QtCore import QObject, pyqtSignal
import re

if TYPE_CHECKING:
    from .nobject import NObject, NRelationship


class NObjectGraph(QObject):
    """
    The universal registry of all NObjects.
    
    This is NOT a filesystem. It's a queryable graph:
    - Find by type: graph.query(type='NWindow')
    - Find by property: graph.query(property={'title': 'Console'})
    - Find by constraint: graph.query(constraint={'ge': {'width': 100}})
    - Find by tag: graph.query(tags=['app', 'system'])
    - Find by relationship: graph.query(related_to='some-id')
    """
    
    # Signals
    object_registered = pyqtSignal(str, str)  # id, type
    object_unregistered = pyqtSignal(str)  # id
    relationship_created = pyqtSignal(object)  # NRelationship
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Main storage: id -> NObject
        self._objects: Dict[str, 'NObject'] = {}
        
        # Indexes for fast querying
        self._by_type: Dict[str, List[str]] = {}  # type -> [ids]
        self._by_tag: Dict[str, List[str]] = {}   # tag -> [ids]
        
        # Relationships stored separately
        self._relationships: Dict[str, 'NRelationship'] = {}
    
    # ═══════════════════════════════════════════════════════════
    # REGISTRATION
    # ═══════════════════════════════════════════════════════════
    
    def register(self, obj: 'NObject') -> None:
        """Register an NObject in the graph."""
        obj_id = obj.id
        obj_type = obj.object_type
        
        # Store object
        self._objects[obj_id] = obj
        
        # Index by type
        if obj_type not in self._by_type:
            self._by_type[obj_type] = []
        if obj_id not in self._by_type[obj_type]:
            self._by_type[obj_type].append(obj_id)
        
        # Index by tags
        for tag in obj.tags:
            self._index_tag(obj_id, tag)
        
        # Listen for tag changes (manual for now)
        self.object_registered.emit(obj_id, obj_type)
    
    def unregister(self, obj_id: str) -> None:
        """Remove an NObject from the graph."""
        if obj_id not in self._objects:
            return
        
        obj = self._objects[obj_id]
        obj_type = obj.object_type
        
        # Remove from type index
        if obj_type in self._by_type:
            if obj_id in self._by_type[obj_type]:
                self._by_type[obj_type].remove(obj_id)
        
        # Remove from tag indexes
        for tag in obj.tags:
            self._unindex_tag(obj_id, tag)
        
        # Remove relationships involving this object
        to_remove = [
            rid for rid, rel in self._relationships.items()
            if rel.source_id == obj_id or rel.target_id == obj_id
        ]
        for rid in to_remove:
            del self._relationships[rid]
        
        # Remove object
        del self._objects[obj_id]
        self.object_unregistered.emit(obj_id)
    
    def _index_tag(self, obj_id: str, tag: str) -> None:
        if tag not in self._by_tag:
            self._by_tag[tag] = []
        if obj_id not in self._by_tag[tag]:
            self._by_tag[tag].append(obj_id)
    
    def _unindex_tag(self, obj_id: str, tag: str) -> None:
        if tag in self._by_tag and obj_id in self._by_tag[tag]:
            self._by_tag[tag].remove(obj_id)
    
    # ═══════════════════════════════════════════════════════════
    # RETRIEVAL
    # ═══════════════════════════════════════════════════════════
    
    def get(self, obj_id: str) -> Optional['NObject']:
        """Get object by ID."""
        return self._objects.get(obj_id)
    
    def get_all(self) -> List['NObject']:
        """Get all objects."""
        return list(self._objects.values())
    
    def count(self) -> int:
        """Total object count."""
        return len(self._objects)
    
    # ═══════════════════════════════════════════════════════════
    # QUERYING - The Power of Newton OS
    # ═══════════════════════════════════════════════════════════
    
    def query(self,
              type: Optional[str] = None,
              types: Optional[List[str]] = None,
              tags: Optional[List[str]] = None,
              any_tag: Optional[List[str]] = None,
              properties: Optional[Dict[str, Any]] = None,
              constraint: Optional[Dict] = None,
              related_to: Optional[str] = None,
              filter_fn: Optional[Callable[['NObject'], bool]] = None,
              limit: Optional[int] = None) -> List['NObject']:
        """
        Query objects by various criteria.
        
        Examples:
            # Find all windows
            graph.query(type='NWindow')
            
            # Find objects with specific property
            graph.query(properties={'title': 'Console'})
            
            # Find with constraint (CDL-style)
            graph.query(constraint={'ge': {'width': 100}})
            
            # Find by tags (all must match)
            graph.query(tags=['app', 'system'])
            
            # Find by tags (any must match)
            graph.query(any_tag=['app', 'utility'])
            
            # Complex query
            graph.query(
                type='NWindow',
                tags=['visible'],
                constraint={'lt': {'z': 100}}
            )
        """
        # Start with all objects or filtered by type
        if type:
            candidates = [
                self._objects[oid] 
                for oid in self._by_type.get(type, [])
                if oid in self._objects
            ]
        elif types:
            candidates = []
            for t in types:
                candidates.extend([
                    self._objects[oid]
                    for oid in self._by_type.get(t, [])
                    if oid in self._objects
                ])
        else:
            candidates = list(self._objects.values())
        
        results = []
        
        for obj in candidates:
            # Filter by tags (all must match)
            if tags:
                if not all(obj.has_tag(t) for t in tags):
                    continue
            
            # Filter by tags (any must match)
            if any_tag:
                if not any(obj.has_tag(t) for t in any_tag):
                    continue
            
            # Filter by exact property values
            if properties:
                match = True
                for key, val in properties.items():
                    if obj.get_property(key) != val:
                        match = False
                        break
                if not match:
                    continue
            
            # Filter by constraint (simplified CDL evaluation)
            if constraint:
                if not self._evaluate_constraint(obj, constraint):
                    continue
            
            # Filter by relationship
            if related_to:
                obj_rels = obj.get_relationships()
                has_relation = False
                for rid in obj_rels:
                    rel = self._relationships.get(rid)
                    if rel and (rel.source_id == related_to or rel.target_id == related_to):
                        has_relation = True
                        break
                if not has_relation:
                    continue
            
            # Custom filter function
            if filter_fn and not filter_fn(obj):
                continue
            
            results.append(obj)
            
            # Limit results
            if limit and len(results) >= limit:
                break
        
        return results
    
    def _evaluate_constraint(self, obj: 'NObject', constraint: Dict) -> bool:
        """Evaluate a CDL-style constraint against an object."""
        for op, spec in constraint.items():
            if op == 'eq':
                for key, val in spec.items():
                    if obj.get_property(key) != val:
                        return False
            elif op == 'ne':
                for key, val in spec.items():
                    if obj.get_property(key) == val:
                        return False
            elif op == 'gt':
                for key, val in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or prop_val <= val:
                        return False
            elif op == 'ge':
                for key, val in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or prop_val < val:
                        return False
            elif op == 'lt':
                for key, val in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or prop_val >= val:
                        return False
            elif op == 'le':
                for key, val in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or prop_val > val:
                        return False
            elif op == 'contains':
                for key, val in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or val not in str(prop_val):
                        return False
            elif op == 'matches':
                for key, pattern in spec.items():
                    prop_val = obj.get_property(key)
                    if prop_val is None or not re.match(pattern, str(prop_val)):
                        return False
            elif op == 'exists':
                for key in (spec if isinstance(spec, list) else [spec]):
                    if not obj.has_property(key):
                        return False
            elif op == 'has_tag':
                for tag in (spec if isinstance(spec, list) else [spec]):
                    if not obj.has_tag(tag):
                        return False
        
        return True
    
    # ═══════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════
    
    def create_relationship(self,
                           source_id: str,
                           target_id: str,
                           rel_type: str,
                           properties: Optional[Dict] = None,
                           bidirectional: bool = False) -> Optional['NRelationship']:
        """Create a relationship between two objects."""
        from .nobject import NRelationship
        import uuid
        
        if source_id not in self._objects or target_id not in self._objects:
            return None
        
        rel = NRelationship(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            type=rel_type,
            properties=properties or {},
            bidirectional=bidirectional
        )
        
        # Store relationship
        self._relationships[rel.id] = rel
        
        # Update both objects
        self._objects[source_id].add_relationship(rel.id)
        self._objects[target_id].add_relationship(rel.id)
        
        self.relationship_created.emit(rel)
        return rel
    
    def get_relationship(self, rel_id: str) -> Optional['NRelationship']:
        return self._relationships.get(rel_id)
    
    def get_relationships_for(self, obj_id: str) -> List['NRelationship']:
        """Get all relationships involving an object."""
        return [
            rel for rel in self._relationships.values()
            if rel.source_id == obj_id or rel.target_id == obj_id
        ]
    
    # ═══════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════
    
    def stats(self) -> Dict:
        """Get graph statistics."""
        return {
            'total_objects': len(self._objects),
            'total_relationships': len(self._relationships),
            'types': {t: len(ids) for t, ids in self._by_type.items()},
            'tags': {t: len(ids) for t, ids in self._by_tag.items()}
        }


# ═══════════════════════════════════════════════════════════════
# THE GRAPH - Global Singleton
# ═══════════════════════════════════════════════════════════════

class _TheGraphSingleton:
    """Singleton accessor for the global graph."""
    _instance: Optional[NObjectGraph] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = NObjectGraph()
        return cls._instance
    
    @classmethod
    def get(cls) -> NObjectGraph:
        if cls._instance is None:
            cls._instance = NObjectGraph()
        return cls._instance
    
    # Forward common methods
    def __getattr__(self, name):
        return getattr(self.get(), name)


# Global instance
TheGraph = _TheGraphSingleton.get()
