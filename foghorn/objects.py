"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN OBJECTS — Hash-Chained Object Graph
═══════════════════════════════════════════════════════════════════════════════

Every object in Nina is:
- Hash-identified (content-addressable)
- Chain-linked (prev_hash for provenance)
- Inspectable (metadata accessible)
- Serializable (JSON round-trip)

Object Types (v1):
- Card: Rich note / block document
- Query: A structured ask
- ResultSet: Search output
- FileAsset: Image/PDF/audio/link
- Task: Bounded computation
- Receipt: History trail entry
- LinkCurve: Bézier connection between objects
- Rule: Constraint pattern

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class ObjectType(Enum):
    """Foghorn object types."""
    CARD = "card"
    QUERY = "query"
    RESULT_SET = "result_set"
    FILE_ASSET = "file_asset"
    TASK = "task"
    RECEIPT = "receipt"
    LINK_CURVE = "link_curve"
    RULE = "rule"
    MAP_PLACE = "map_place"
    ROUTE = "route"
    AUTOMATION = "automation"


@dataclass
class FoghornObject(ABC):
    """
    Base class for all Foghorn objects.
    
    Every object has:
    - id: Unique identifier (computed from hash)
    - hash: SHA-256 of content
    - prev_hash: Link to previous object (provenance chain)
    - created_at: Timestamp
    - verified: Whether object has been verified
    - metadata: Extensible key-value store
    """
    
    # Core identity (computed)
    id: str = field(default="", init=False)
    hash: str = field(default="", init=False)
    
    # Chain linking
    prev_hash: Optional[str] = None
    
    # Timestamps
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))
    
    # Verification
    verified: bool = False
    
    # Extensible metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Compute hash after initialization."""
        self._compute_hash()
    
    @property
    @abstractmethod
    def object_type(self) -> ObjectType:
        """Return the object type."""
        pass
    
    @abstractmethod
    def get_content_for_hash(self) -> str:
        """Return the content string used for hashing."""
        pass
    
    def _compute_hash(self):
        """Compute SHA-256 hash of object content."""
        content = self.get_content_for_hash()
        full_content = f"{self.object_type.value}:{content}:{self.prev_hash or 'genesis'}"
        self.hash = hashlib.sha256(full_content.encode()).hexdigest()
        self.id = self.hash[:16]  # Short ID for display
    
    def rehash(self):
        """Recompute hash (call after modifications)."""
        self._compute_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": self.object_type.value,
            "id": self.id,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "created_at": self.created_at,
            "verified": self.verified,
            "metadata": self.metadata,
            **self._get_type_specific_fields()
        }
    
    @abstractmethod
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        """Return type-specific fields for serialization."""
        pass
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def link_to(self, other: 'FoghornObject') -> 'LinkCurve':
        """Create a LinkCurve connecting this object to another."""
        return LinkCurve(
            source_hash=self.hash,
            target_hash=other.hash,
            source_type=self.object_type,
            target_type=other.object_type,
            prev_hash=self.hash,
        )
    
    def get_inspector_data(self) -> Dict[str, Any]:
        """Return data for the Inspector panel."""
        return {
            "general": {
                "Type": self.object_type.value,
                "ID": self.id,
                "Hash": self.hash,
                "Created": datetime.fromtimestamp(self.created_at / 1000).isoformat(),
                "Verified": "✓ Yes" if self.verified else "✗ No",
                "Prev Hash": self.prev_hash[:16] + "..." if self.prev_hash else "genesis",
            },
            "metadata": self.metadata,
            **self._get_inspector_sections()
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        """Override to add type-specific inspector sections."""
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# CONCRETE OBJECT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Card(FoghornObject):
    """
    A rich note / block document.
    
    Cards are the primary content object in Nina.
    They can contain text, code, or structured data.
    """
    content: str = ""
    title: str = ""
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None
    source_url: Optional[str] = None
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.CARD
    
    def get_content_for_hash(self) -> str:
        return f"{self.title}:{self.content}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "title": self.title,
            "tags": self.tags,
            "source": self.source,
            "source_url": self.source_url,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "content": {
                "Title": self.title or "(untitled)",
                "Length": f"{len(self.content)} chars",
                "Tags": ", ".join(self.tags) if self.tags else "(none)",
            },
            "sources": {
                "Source": self.source or "(unknown)",
                "URL": self.source_url or "(none)",
            }
        }


@dataclass
class Query(FoghornObject):
    """
    A structured ask / search request.
    
    Queries use kinematic shape matching for semantic search.
    """
    text: str = ""
    shape_type: Optional[str] = None  # kinematic query shape
    filters: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.QUERY
    
    def get_content_for_hash(self) -> str:
        return f"{self.text}:{json.dumps(self.filters, sort_keys=True)}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "shape_type": self.shape_type,
            "filters": self.filters,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "query": {
                "Text": self.text,
                "Shape": self.shape_type or "(auto-detect)",
                "Filters": len(self.filters),
            }
        }


@dataclass
class ResultSet(FoghornObject):
    """
    Search output / collection of results.
    
    ResultSets can be converted to Cards or used as input to services.
    """
    query_hash: str = ""
    results: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    sources_checked: int = 0
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.RESULT_SET
    
    def get_content_for_hash(self) -> str:
        return f"{self.query_hash}:{len(self.results)}:{self.total_count}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "query_hash": self.query_hash,
            "results": self.results,
            "total_count": self.total_count,
            "sources_checked": self.sources_checked,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "results": {
                "Count": len(self.results),
                "Total": self.total_count,
                "Sources Checked": self.sources_checked,
                "Query": self.query_hash[:16] + "...",
            }
        }
    
    def to_cards(self) -> List[Card]:
        """Convert results to Card objects."""
        cards = []
        for i, result in enumerate(self.results):
            card = Card(
                content=result.get("content", str(result)),
                title=result.get("title", f"Result {i+1}"),
                source=result.get("source"),
                source_url=result.get("url"),
                prev_hash=self.hash,
                verified=result.get("verified", False),
            )
            cards.append(card)
        return cards


@dataclass
class FileAsset(FoghornObject):
    """
    File reference (image, PDF, audio, link).
    """
    path: str = ""
    filename: str = ""
    mime_type: str = ""
    size_bytes: int = 0
    url: Optional[str] = None
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.FILE_ASSET
    
    def get_content_for_hash(self) -> str:
        return f"{self.path}:{self.filename}:{self.size_bytes}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "url": self.url,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "file": {
                "Filename": self.filename,
                "Path": self.path,
                "Type": self.mime_type,
                "Size": f"{self.size_bytes:,} bytes",
            }
        }


@dataclass
class Task(FoghornObject):
    """
    A bounded computation task.
    
    Tasks have execution bounds and produce Receipts.
    """
    name: str = ""
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    
    # Execution bounds
    max_ops: int = 1_000_000
    max_time_ms: int = 30_000
    
    # Results
    result_hash: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.TASK
    
    def get_content_for_hash(self) -> str:
        return f"{self.name}:{self.status}:{self.result_hash or 'none'}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "max_ops": self.max_ops,
            "max_time_ms": self.max_time_ms,
            "result_hash": self.result_hash,
            "error": self.error,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "task": {
                "Name": self.name,
                "Status": self.status,
                "Progress": f"{self.progress * 100:.1f}%",
            },
            "bounds": {
                "Max Ops": f"{self.max_ops:,}",
                "Max Time": f"{self.max_time_ms:,}ms",
            }
        }


@dataclass
class Receipt(FoghornObject):
    """
    History trail entry.
    
    Receipts are immutable records of actions taken.
    """
    action: str = ""
    actor: str = "system"
    input_hashes: List[str] = field(default_factory=list)
    output_hashes: List[str] = field(default_factory=list)
    duration_ms: int = 0
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.RECEIPT
    
    def get_content_for_hash(self) -> str:
        inputs = ",".join(self.input_hashes)
        outputs = ",".join(self.output_hashes)
        return f"{self.action}:{self.actor}:{inputs}:{outputs}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "actor": self.actor,
            "input_hashes": self.input_hashes,
            "output_hashes": self.output_hashes,
            "duration_ms": self.duration_ms,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "action": {
                "Action": self.action,
                "Actor": self.actor,
                "Duration": f"{self.duration_ms}ms",
            },
            "chain": {
                "Inputs": len(self.input_hashes),
                "Outputs": len(self.output_hashes),
            }
        }


@dataclass
class LinkCurve(FoghornObject):
    """
    Bézier connection between objects.
    
    LinkCurves represent relationships and can be visualized.
    """
    source_hash: str = ""
    target_hash: str = ""
    source_type: ObjectType = ObjectType.CARD
    target_type: ObjectType = ObjectType.CARD
    
    # Bézier control points (normalized 0-1)
    p0: tuple = (0.0, 0.0)  # Source anchor
    h1: tuple = (0.3, 0.0)  # Handle 1
    h2: tuple = (0.7, 1.0)  # Handle 2
    p3: tuple = (1.0, 1.0)  # Target anchor
    
    # Relationship metadata
    relationship: str = "links_to"
    weight: float = 1.0
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.LINK_CURVE
    
    def get_content_for_hash(self) -> str:
        return f"{self.source_hash}:{self.target_hash}:{self.relationship}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "source_hash": self.source_hash,
            "target_hash": self.target_hash,
            "source_type": self.source_type.value,
            "target_type": self.target_type.value,
            "p0": self.p0,
            "h1": self.h1,
            "h2": self.h2,
            "p3": self.p3,
            "relationship": self.relationship,
            "weight": self.weight,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "connection": {
                "Source": self.source_hash[:16] + "...",
                "Target": self.target_hash[:16] + "...",
                "Relationship": self.relationship,
                "Weight": f"{self.weight:.2f}",
            },
            "bezier": {
                "P₀ (anchor)": f"({self.p0[0]:.2f}, {self.p0[1]:.2f})",
                "H₁ (handle)": f"({self.h1[0]:.2f}, {self.h1[1]:.2f})",
                "H₂ (handle)": f"({self.h2[0]:.2f}, {self.h2[1]:.2f})",
                "P₃ (anchor)": f"({self.p3[0]:.2f}, {self.p3[1]:.2f})",
            }
        }
    
    def get_curvature(self) -> float:
        """Calculate curve curvature (how much it bends)."""
        # Simplified curvature: distance of handles from straight line
        dx = self.p3[0] - self.p0[0]
        dy = self.p3[1] - self.p0[1]
        
        # Linear interpolation points
        l1 = (self.p0[0] + dx * 0.33, self.p0[1] + dy * 0.33)
        l2 = (self.p0[0] + dx * 0.67, self.p0[1] + dy * 0.67)
        
        # Distance from handles to linear points
        d1 = ((self.h1[0] - l1[0])**2 + (self.h1[1] - l1[1])**2)**0.5
        d2 = ((self.h2[0] - l2[0])**2 + (self.h2[1] - l2[1])**2)**0.5
        
        return (d1 + d2) / 2


@dataclass 
class Rule(FoghornObject):
    """
    Constraint pattern / safety rule.
    """
    name: str = ""
    description: str = ""
    patterns: List[str] = field(default_factory=list)
    enabled: bool = True
    category: str = "general"
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.RULE
    
    def get_content_for_hash(self) -> str:
        return f"{self.name}:{','.join(self.patterns)}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "patterns": self.patterns,
            "enabled": self.enabled,
            "category": self.category,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "rule": {
                "Name": self.name,
                "Category": self.category,
                "Enabled": "✓ Yes" if self.enabled else "✗ No",
                "Patterns": len(self.patterns),
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MAP & ROUTE OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MapPlace(FoghornObject):
    """
    A geographic location.
    
    MapPlaces can be linked, searched, and turned into Routes.
    """
    name: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    place_type: str = "point"  # point, area, region
    tags: List[str] = field(default_factory=list)
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.MAP_PLACE
    
    def get_content_for_hash(self) -> str:
        return f"{self.name}:{self.latitude:.6f},{self.longitude:.6f}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "place_type": self.place_type,
            "tags": self.tags,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "location": {
                "Name": self.name,
                "Address": self.address or "(none)",
                "Coordinates": f"{self.latitude:.4f}, {self.longitude:.4f}",
                "Type": self.place_type,
            },
            "metadata": {
                "Tags": ", ".join(self.tags) if self.tags else "(none)",
            }
        }
    
    def distance_to(self, other: 'MapPlace') -> float:
        """Haversine distance in kilometers."""
        import math
        R = 6371  # Earth radius in km
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 2 * R * math.asin(math.sqrt(a))


@dataclass
class Route(FoghornObject):
    """
    A path between MapPlaces.
    
    Routes are ordered sequences of places with travel metadata.
    """
    name: str = ""
    waypoints: List[str] = field(default_factory=list)  # MapPlace hashes
    mode: str = "driving"  # driving, walking, transit, cycling
    distance_km: float = 0.0
    duration_minutes: float = 0.0
    polyline: str = ""  # Encoded polyline for rendering
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.ROUTE
    
    def get_content_for_hash(self) -> str:
        return f"{self.name}:{self.mode}:{','.join(self.waypoints)}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "waypoints": self.waypoints,
            "mode": self.mode,
            "distance_km": self.distance_km,
            "duration_minutes": self.duration_minutes,
            "polyline": self.polyline,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "route": {
                "Name": self.name,
                "Mode": self.mode.capitalize(),
                "Waypoints": len(self.waypoints),
            },
            "metrics": {
                "Distance": f"{self.distance_km:.1f} km",
                "Duration": f"{self.duration_minutes:.0f} min",
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATION OBJECT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Automation(FoghornObject):
    """
    A repeatable workflow / automation.
    
    Automations chain services together:
    trigger → condition → action(s) → output
    """
    name: str = ""
    description: str = ""
    
    # Trigger
    trigger_type: str = "manual"  # manual, schedule, event, change
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    
    # Conditions (optional)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Actions (service calls in order)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # State
    enabled: bool = True
    last_run: Optional[int] = None
    run_count: int = 0
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.AUTOMATION
    
    def get_content_for_hash(self) -> str:
        return f"{self.name}:{self.trigger_type}:{len(self.actions)}"
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type,
            "trigger_config": self.trigger_config,
            "conditions": self.conditions,
            "actions": self.actions,
            "enabled": self.enabled,
            "last_run": self.last_run,
            "run_count": self.run_count,
        }
    
    def _get_inspector_sections(self) -> Dict[str, Dict]:
        return {
            "automation": {
                "Name": self.name,
                "Trigger": self.trigger_type.capitalize(),
                "Enabled": "✓ Yes" if self.enabled else "✗ No",
            },
            "workflow": {
                "Conditions": len(self.conditions),
                "Actions": len(self.actions),
            },
            "stats": {
                "Run Count": self.run_count,
                "Last Run": datetime.fromtimestamp(self.last_run / 1000).isoformat() if self.last_run else "Never",
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# OBJECT STORE
# ═══════════════════════════════════════════════════════════════════════════════

class ObjectStore:
    """
    In-memory object store with hash-based lookup.
    """
    
    def __init__(self):
        self._objects: Dict[str, FoghornObject] = {}
        self._by_type: Dict[ObjectType, List[str]] = {t: [] for t in ObjectType}
    
    def add(self, obj: FoghornObject) -> str:
        """Add object to store, return hash."""
        self._objects[obj.hash] = obj
        self._by_type[obj.object_type].append(obj.hash)
        return obj.hash
    
    def get(self, hash: str) -> Optional[FoghornObject]:
        """Get object by hash."""
        return self._objects.get(hash)
    
    def get_by_id(self, id: str) -> Optional[FoghornObject]:
        """Get object by short ID."""
        for obj in self._objects.values():
            if obj.id == id:
                return obj
        return None
    
    def get_by_type(self, obj_type: ObjectType) -> List[FoghornObject]:
        """Get all objects of a type."""
        return [self._objects[h] for h in self._by_type[obj_type] if h in self._objects]
    
    def get_chain(self, hash: str) -> List[FoghornObject]:
        """Get the provenance chain for an object."""
        chain = []
        current = self.get(hash)
        while current:
            chain.append(current)
            if current.prev_hash:
                current = self.get(current.prev_hash)
            else:
                break
        return chain
    
    def verify_chain(self, hash: str) -> bool:
        """Verify the hash chain is intact."""
        chain = self.get_chain(hash)
        for i, obj in enumerate(chain[:-1]):
            if obj.prev_hash != chain[i + 1].hash:
                return False
        return True
    
    def count(self) -> int:
        """Total objects in store."""
        return len(self._objects)
    
    def export(self) -> List[Dict]:
        """Export all objects as JSON-serializable list."""
        return [obj.to_dict() for obj in self._objects.values()]


# Global object store
_object_store: Optional[ObjectStore] = None

def get_object_store() -> ObjectStore:
    """Get the global object store."""
    global _object_store
    if _object_store is None:
        _object_store = ObjectStore()
    return _object_store
