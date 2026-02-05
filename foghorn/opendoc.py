"""
═══════════════════════════════════════════════════════════════════════════════
OPENDOC — Newton-Verified Compound Document Framework
═══════════════════════════════════════════════════════════════════════════════

OpenDoc reimagined for the 2020s.

Original OpenDoc (1994-1997):
- Small, reusable components
- Document-centered (not app-centered)
- Cross-platform compound documents
- Killed by Steve Jobs in 1997

Newton OpenDoc (2026):
- Same philosophy: small, composable parts
- Verified computation via Newton Logic Engine
- Hash-chained immutable documents via Foghorn
- Constraint-validated via CDL

The difference? Every part is VERIFIED.
- Links between parts? Verified.
- Data transformations? Verified.
- Embedded computations? Verified.

"OpenDoc wasn't wrong. It was just 30 years early."

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foghorn.objects import (
    FoghornObject, ObjectType, Card, Query, ResultSet,
    FileAsset, Task, Receipt, LinkCurve, Rule,
    get_object_store,
)
from foghorn.commands import add_object
from foghorn.services import get_service_registry, ServiceCategory
from core.cdl import CDLEvaluator


# ═══════════════════════════════════════════════════════════════════════════════
# PART TYPES — OpenDoc Component Categories
# ═══════════════════════════════════════════════════════════════════════════════

class PartType(Enum):
    """
    OpenDoc part types.
    
    Original OpenDoc had: text, graphics, spreadsheet, etc.
    Newton OpenDoc adds: verified computation, constraint-checked data
    """
    # Content parts (display data)
    TEXT = "text"                    # Rich text content
    GRAPHIC = "graphic"              # Vector/raster images
    TABLE = "table"                  # Tabular data / spreadsheet
    CHART = "chart"                  # Data visualization
    MEDIA = "media"                  # Audio/video
    
    # Interactive parts
    BROWSER = "browser"              # Web content
    MAIL = "mail"                    # Email content
    FTP = "ftp"                      # File transfer
    TERMINAL = "terminal"            # Command execution
    
    # Computation parts (Newton extensions)
    LOGIC = "logic"                  # Newton Logic Engine expressions
    CONSTRAINT = "constraint"        # CDL constraint definitions
    QUERY = "query"                  # Foghorn queries
    FORM = "form"                    # Data entry with validation
    
    # Structural parts
    CONTAINER = "container"          # Part that contains other parts
    LINK = "link"                    # Reference to another document/part


class PartState(Enum):
    """Part lifecycle states."""
    DRAFT = "draft"                  # Being edited
    VERIFIED = "verified"            # Passed verification
    FROZEN = "frozen"                # Immutable (archived)
    INVALID = "invalid"              # Failed verification


# ═══════════════════════════════════════════════════════════════════════════════
# PART — Base OpenDoc Component
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Part(FoghornObject):
    """
    An OpenDoc Part — the fundamental building block.
    
    Parts are:
    - Self-contained: Have their own data and behavior
    - Embeddable: Can be placed inside containers
    - Verifiable: Constraints checked by Newton
    - Hashable: Content-addressable for deduplication
    
    Original OpenDoc called the part handler an "editor".
    Newton OpenDoc uses Services for editing/manipulation.
    """
    
    # Part identity
    name: str = ""
    part_type: PartType = PartType.TEXT
    
    # Content (type-specific)
    content: Any = None
    
    # Geometry for embedding
    x: int = 0
    y: int = 0
    width: int = 200
    height: int = 100
    z_index: int = 0
    
    # Verification
    state: PartState = PartState.DRAFT
    constraints: List[str] = field(default_factory=list)
    
    # Links to other parts
    linked_parts: List[str] = field(default_factory=list)  # Part hashes
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.CARD  # Parts are stored as Cards
    
    def get_content_for_hash(self) -> str:
        """Hash content for verification."""
        return json.dumps({
            "name": self.name,
            "type": self.part_type.value,
            "content": str(self.content),
            "x": self.x, "y": self.y,
            "width": self.width, "height": self.height,
        }, sort_keys=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/API."""
        return {
            "id": self.id,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "name": self.name,
            "part_type": self.part_type.value,
            "content": self.content,
            "geometry": {
                "x": self.x, "y": self.y,
                "width": self.width, "height": self.height,
                "z_index": self.z_index,
            },
            "state": self.state.value,
            "constraints": self.constraints,
            "linked_parts": self.linked_parts,
            "verified": self.verified,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        """Return type-specific fields for serialization."""
        return {
            "name": self.name,
            "part_type": self.part_type.value,
            "content": self.content,
            "geometry": {
                "x": self.x, "y": self.y,
                "width": self.width, "height": self.height,
                "z_index": self.z_index,
            },
            "state": self.state.value,
            "constraints": self.constraints,
            "linked_parts": self.linked_parts,
        }
    
    def verify(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verify this part against its constraints.
        
        Uses Newton CDL for constraint evaluation.
        Returns True if all constraints pass.
        """
        if not self.constraints:
            self.state = PartState.VERIFIED
            self.verified = True
            return True
        
        context = context or {}
        context["part"] = self.to_dict()
        context["content"] = self.content
        
        evaluator = CDLEvaluator()
        
        for constraint in self.constraints:
            try:
                constraint_obj = json.loads(constraint) if isinstance(constraint, str) else constraint
                result = evaluator.evaluate(constraint_obj, context)
                if not result.passed:
                    self.state = PartState.INVALID
                    self.verified = False
                    return False
            except Exception as e:
                self.state = PartState.INVALID
                self.verified = False
                return False
        
        self.state = PartState.VERIFIED
        self.verified = True
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOUND DOCUMENT — Container of Parts
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CompoundDocument(FoghornObject):
    """
    An OpenDoc Compound Document — container for parts.
    
    This is the "document" in document-centric computing.
    There is no "application" — the document IS the experience.
    
    Structure:
    - Root part (the main container)
    - Embedded parts (nested components)
    - Link graph (relationships between parts)
    """
    
    # Document identity
    title: str = "Untitled Document"
    
    # Root content part
    root_part_hash: Optional[str] = None
    
    # All parts in this document (hash → Part)
    parts: Dict[str, Part] = field(default_factory=dict)
    
    # Document-level constraints
    constraints: List[str] = field(default_factory=list)
    
    # Verification
    state: PartState = PartState.DRAFT
    
    @property
    def object_type(self) -> ObjectType:
        return ObjectType.CARD
    
    def get_content_for_hash(self) -> str:
        """Hash based on all part hashes."""
        part_hashes = sorted(self.parts.keys())
        return json.dumps({
            "title": self.title,
            "root": self.root_part_hash,
            "parts": part_hashes,
        }, sort_keys=True)
    
    def add_part(self, part: Part) -> str:
        """
        Add a part to the document.
        Returns the part's hash.
        """
        self.parts[part.hash] = part
        
        # First part becomes root if no root set
        if self.root_part_hash is None:
            self.root_part_hash = part.hash
        
        # Recompute document hash
        self._compute_hash()
        
        return part.hash
    
    def get_part(self, hash_or_id: str) -> Optional[Part]:
        """Get a part by hash or short ID."""
        if hash_or_id in self.parts:
            return self.parts[hash_or_id]
        
        # Try short ID
        for h, part in self.parts.items():
            if part.id == hash_or_id:
                return part
        
        return None
    
    def link_parts(self, from_hash: str, to_hash: str, link_type: str = "contains") -> bool:
        """
        Create a link between two parts.
        """
        from_part = self.get_part(from_hash)
        to_part = self.get_part(to_hash)
        
        if not from_part or not to_part:
            return False
        
        if to_hash not in from_part.linked_parts:
            from_part.linked_parts.append(to_hash)
            from_part._compute_hash()
        
        return True
    
    def verify_all(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Verify all parts in the document.
        Returns dict of {part_hash: verified_bool}.
        """
        context = context or {}
        context["document"] = self.to_dict()
        
        results = {}
        all_verified = True
        
        for hash_val, part in self.parts.items():
            verified = part.verify(context)
            results[hash_val] = verified
            if not verified:
                all_verified = False
        
        self.state = PartState.VERIFIED if all_verified else PartState.INVALID
        self.verified = all_verified
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize full document."""
        return {
            "id": self.id,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "title": self.title,
            "root_part_hash": self.root_part_hash,
            "parts": {h: p.to_dict() for h, p in self.parts.items()},
            "constraints": self.constraints,
            "state": self.state.value,
            "verified": self.verified,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
    
    def _get_type_specific_fields(self) -> Dict[str, Any]:
        """Return type-specific fields for serialization."""
        return {
            "title": self.title,
            "root_part_hash": self.root_part_hash,
            "parts": {h: p.to_dict() for h, p in self.parts.items()},
            "constraints": self.constraints,
            "state": self.state.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompoundDocument':
        """Deserialize from dict."""
        doc = cls(title=data.get("title", "Untitled"))
        doc.root_part_hash = data.get("root_part_hash")
        doc.constraints = data.get("constraints", [])
        doc.state = PartState(data.get("state", "draft"))
        doc.verified = data.get("verified", False)
        doc.metadata = data.get("metadata", {})
        
        # Reconstruct parts
        for hash_val, part_data in data.get("parts", {}).items():
            part = Part(
                name=part_data.get("name", ""),
                part_type=PartType(part_data.get("part_type", "text")),
                content=part_data.get("content"),
                x=part_data.get("geometry", {}).get("x", 0),
                y=part_data.get("geometry", {}).get("y", 0),
                width=part_data.get("geometry", {}).get("width", 200),
                height=part_data.get("geometry", {}).get("height", 100),
                z_index=part_data.get("geometry", {}).get("z_index", 0),
                constraints=part_data.get("constraints", []),
                linked_parts=part_data.get("linked_parts", []),
            )
            part.state = PartState(part_data.get("state", "draft"))
            part.verified = part_data.get("verified", False)
            doc.parts[part.hash] = part
        
        return doc


# ═══════════════════════════════════════════════════════════════════════════════
# PART REGISTRY — Service Discovery for Parts
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PartHandler:
    """
    Handler for a specific part type.
    
    Original OpenDoc called these "editors".
    Each part type has a handler that knows how to:
    - Render the part
    - Edit the part
    - Verify the part
    """
    part_type: PartType
    name: str
    description: str
    
    # Functions
    render_fn: Optional[Callable[[Part], str]] = None
    edit_fn: Optional[Callable[[Part, Any], Part]] = None
    verify_fn: Optional[Callable[[Part], bool]] = None
    
    # Constraints that apply to all parts of this type
    default_constraints: List[str] = field(default_factory=list)


class PartRegistry:
    """
    Registry of part handlers.
    
    This is the OpenDoc "Component Integration Lab" reimagined.
    """
    
    _instance: Optional['PartRegistry'] = None
    
    def __init__(self):
        self._handlers: Dict[PartType, PartHandler] = {}
        self._initialize_defaults()
    
    @classmethod
    def get_instance(cls) -> 'PartRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _initialize_defaults(self):
        """Register default part handlers."""
        
        # Text handler
        self.register(PartHandler(
            part_type=PartType.TEXT,
            name="Text Editor",
            description="Rich text editing",
            default_constraints=[],
        ))
        
        # Table handler
        self.register(PartHandler(
            part_type=PartType.TABLE,
            name="Table Editor", 
            description="Spreadsheet-style tables",
            default_constraints=[],
        ))
        
        # Logic handler (Newton extension)
        self.register(PartHandler(
            part_type=PartType.LOGIC,
            name="Logic Expression",
            description="Newton Logic Engine expressions",
            default_constraints=[
                '{"op": "exists", "path": "content"}',
            ],
        ))
        
        # Constraint handler (Newton extension)
        self.register(PartHandler(
            part_type=PartType.CONSTRAINT,
            name="Constraint Definition",
            description="CDL constraint rules",
            default_constraints=[],
        ))
        
        # Browser handler (CyberDog)
        self.register(PartHandler(
            part_type=PartType.BROWSER,
            name="Web Browser",
            description="CyberDog web browser component",
            default_constraints=[],
        ))
        
        # Mail handler (CyberDog)
        self.register(PartHandler(
            part_type=PartType.MAIL,
            name="Email Client",
            description="CyberDog email component",
            default_constraints=[],
        ))
    
    def register(self, handler: PartHandler):
        """Register a part handler."""
        self._handlers[handler.part_type] = handler
    
    def get_handler(self, part_type: PartType) -> Optional[PartHandler]:
        """Get handler for a part type."""
        return self._handlers.get(part_type)
    
    def list_handlers(self) -> List[PartHandler]:
        """List all registered handlers."""
        return list(self._handlers.values())
    
    def get_handlers_for_content(self, content_type: str) -> List[PartHandler]:
        """Get handlers that can handle a content type."""
        # TODO: Implement content type negotiation
        return list(self._handlers.values())


def get_part_registry() -> PartRegistry:
    """Get the global part registry."""
    return PartRegistry.get_instance()


# ═══════════════════════════════════════════════════════════════════════════════
# BENTO FORMAT — Document Storage (Original OpenDoc used Bento)
# ═══════════════════════════════════════════════════════════════════════════════

class BentoSerializer:
    """
    Serialize/deserialize OpenDoc documents.
    
    Original OpenDoc used the Bento format.
    Newton OpenDoc uses JSON + hash chains.
    """
    
    @staticmethod
    def serialize(doc: CompoundDocument) -> str:
        """Serialize document to JSON string."""
        return json.dumps(doc.to_dict(), indent=2, default=str)
    
    @staticmethod
    def deserialize(data: str) -> CompoundDocument:
        """Deserialize document from JSON string."""
        dict_data = json.loads(data)
        return CompoundDocument.from_dict(dict_data)
    
    @staticmethod
    def compute_signature(doc: CompoundDocument) -> str:
        """Compute cryptographic signature of document."""
        content = BentoSerializer.serialize(doc)
        return hashlib.sha256(content.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT STORE — Persistence Layer
# ═══════════════════════════════════════════════════════════════════════════════

class DocumentStore:
    """
    Store and retrieve compound documents.
    """
    
    _instance: Optional['DocumentStore'] = None
    
    def __init__(self):
        self._documents: Dict[str, CompoundDocument] = {}
    
    @classmethod
    def get_instance(cls) -> 'DocumentStore':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def save(self, doc: CompoundDocument) -> str:
        """Save document, return hash."""
        self._documents[doc.hash] = doc
        return doc.hash
    
    def get(self, hash_val: str) -> Optional[CompoundDocument]:
        """Get document by hash."""
        return self._documents.get(hash_val)
    
    def get_by_title(self, title: str) -> List[CompoundDocument]:
        """Search documents by title."""
        return [d for d in self._documents.values() if title.lower() in d.title.lower()]
    
    def list_all(self) -> List[CompoundDocument]:
        """List all documents."""
        return list(self._documents.values())
    
    def delete(self, hash_val: str) -> bool:
        """Delete document."""
        if hash_val in self._documents:
            del self._documents[hash_val]
            return True
        return False


def get_document_store() -> DocumentStore:
    """Get the global document store."""
    return DocumentStore.get_instance()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_document(title: str) -> CompoundDocument:
    """Create a new compound document."""
    doc = CompoundDocument(title=title)
    get_document_store().save(doc)
    return doc


def create_part(
    name: str,
    part_type: PartType,
    content: Any,
    **geometry
) -> Part:
    """Create a new part."""
    part = Part(
        name=name,
        part_type=part_type,
        content=content,
        x=geometry.get("x", 0),
        y=geometry.get("y", 0),
        width=geometry.get("width", 200),
        height=geometry.get("height", 100),
    )
    return part


def embed_part(doc: CompoundDocument, part: Part, container_hash: Optional[str] = None) -> str:
    """
    Embed a part in a document.
    
    If container_hash is provided, embeds inside that part.
    Otherwise embeds at document root.
    """
    part_hash = doc.add_part(part)
    
    if container_hash:
        doc.link_parts(container_hash, part_hash, "contains")
    
    get_document_store().save(doc)
    
    return part_hash
