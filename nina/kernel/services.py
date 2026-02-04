"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN SERVICES — NeXTSTEP-Style Service Registry
═══════════════════════════════════════════════════════════════════════════════

Services in Nina are:
- Declarative: Specify accepts/produces object types
- Discoverable: Registered in global registry
- Constraint-checked: Validated before execution
- Composable: Chain services via object graph

Service Pattern:
    @service(
        name="Verify Claim",
        accepts=[Card, Query],
        produces=[Receipt, Card],
        constraints=["content.length > 0"]
    )
    def verify_claim(obj: FoghornObject) -> List[FoghornObject]:
        ...

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import time
import functools
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from enum import Enum

from .objects import (
    FoghornObject, ObjectType, Receipt, Task,
    Card, Query, ResultSet, FileAsset, LinkCurve, Rule,
    get_object_store
)


class ServiceCategory(Enum):
    """Service categories for menu organization."""
    COMPUTE = "compute"
    VERIFY = "verify"
    TRANSFORM = "transform"
    SEARCH = "search"
    GROUND = "ground"
    ANALYZE = "analyze"
    CREATE = "create"
    EXPORT = "export"


@dataclass
class ServiceDefinition:
    """
    Service metadata definition.
    """
    name: str
    description: str
    
    # Type signature
    accepts: List[ObjectType]
    produces: List[ObjectType]
    
    # Constraints (CDL-style)
    constraints: List[str] = field(default_factory=list)
    
    # Metadata
    category: ServiceCategory = ServiceCategory.COMPUTE
    enabled: bool = True
    
    # Execution bounds
    max_ops: int = 1_000_000
    max_time_ms: int = 30_000
    
    # The actual function
    handler: Optional[Callable] = None
    
    def can_accept(self, obj: FoghornObject) -> bool:
        """Check if service can accept this object type."""
        return obj.object_type in self.accepts
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API/UI."""
        return {
            "name": self.name,
            "description": self.description,
            "accepts": [t.value for t in self.accepts],
            "produces": [t.value for t in self.produces],
            "constraints": self.constraints,
            "category": self.category.value,
            "enabled": self.enabled,
        }


class ServiceRegistry:
    """
    Global service registry.
    
    Provides NeXTSTEP-style service discovery.
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._by_category: Dict[ServiceCategory, List[str]] = {
            cat: [] for cat in ServiceCategory
        }
        self._by_accepts: Dict[ObjectType, List[str]] = {
            t: [] for t in ObjectType
        }
    
    def register(self, service: ServiceDefinition):
        """Register a service."""
        self._services[service.name] = service
        self._by_category[service.category].append(service.name)
        for obj_type in service.accepts:
            self._by_accepts[obj_type].append(service.name)
    
    def get(self, name: str) -> Optional[ServiceDefinition]:
        """Get service by name."""
        return self._services.get(name)
    
    def list_all(self) -> List[ServiceDefinition]:
        """List all registered services."""
        return list(self._services.values())
    
    def list_by_category(self, category: ServiceCategory) -> List[ServiceDefinition]:
        """List services in a category."""
        names = self._by_category.get(category, [])
        return [self._services[n] for n in names]
    
    def find_for_object(self, obj: FoghornObject) -> List[ServiceDefinition]:
        """Find services that can accept this object."""
        names = self._by_accepts.get(obj.object_type, [])
        return [self._services[n] for n in names if self._services[n].enabled]
    
    def get_context_menu(self, obj: FoghornObject) -> Dict[str, List[Dict]]:
        """
        Get context menu structure for an object.
        
        Returns services grouped by category.
        """
        services = self.find_for_object(obj)
        menu = {}
        
        for svc in services:
            cat_name = svc.category.value.title()
            if cat_name not in menu:
                menu[cat_name] = []
            menu[cat_name].append({
                "name": svc.name,
                "description": svc.description,
                "produces": [t.value for t in svc.produces],
            })
        
        return menu


# Global registry instance
_registry: Optional[ServiceRegistry] = None

def get_service_registry() -> ServiceRegistry:
    """Get the global service registry."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

def service(
    name: str,
    accepts: List[Type[FoghornObject]],
    produces: List[Type[FoghornObject]],
    description: str = "",
    constraints: List[str] = None,
    category: ServiceCategory = ServiceCategory.COMPUTE,
    max_ops: int = 1_000_000,
    max_time_ms: int = 30_000,
):
    """
    Decorator to register a function as a service.
    
    Usage:
        @service(
            name="Verify Claim",
            accepts=[Card],
            produces=[Receipt, Card],
            description="Verify a claim against sources",
            category=ServiceCategory.VERIFY
        )
        def verify_claim(obj: Card) -> List[FoghornObject]:
            ...
    """
    
    # Map types to ObjectTypes
    type_map = {
        Card: ObjectType.CARD,
        Query: ObjectType.QUERY,
        ResultSet: ObjectType.RESULT_SET,
        FileAsset: ObjectType.FILE_ASSET,
        Task: ObjectType.TASK,
        Receipt: ObjectType.RECEIPT,
        LinkCurve: ObjectType.LINK_CURVE,
        Rule: ObjectType.RULE,
    }
    
    accepts_types = [type_map.get(t, ObjectType.CARD) for t in accepts]
    produces_types = [type_map.get(t, ObjectType.CARD) for t in produces]
    
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(obj: FoghornObject, *args, **kwargs) -> 'ServiceResult':
            # Create task
            task = Task(
                name=name,
                status="running",
                max_ops=max_ops,
                max_time_ms=max_time_ms,
                prev_hash=obj.hash,
            )
            
            start_time = time.time()
            
            try:
                # Execute handler
                results = func(obj, *args, **kwargs)
                
                # Ensure results is a list
                if not isinstance(results, list):
                    results = [results] if results else []
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Create receipt
                receipt = Receipt(
                    action=name,
                    actor="service",
                    input_hashes=[obj.hash],
                    output_hashes=[r.hash for r in results if hasattr(r, 'hash')],
                    duration_ms=duration_ms,
                    prev_hash=task.hash,
                )
                
                # Update task
                task.status = "completed"
                task.progress = 1.0
                task.result_hash = receipt.hash
                task.rehash()
                
                # Add to object store
                store = get_object_store()
                store.add(task)
                store.add(receipt)
                for result in results:
                    if isinstance(result, FoghornObject):
                        store.add(result)
                
                return ServiceResult(
                    success=True,
                    task=task,
                    receipt=receipt,
                    results=results,
                    duration_ms=duration_ms,
                )
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                task.status = "failed"
                task.error = str(e)
                task.rehash()
                
                receipt = Receipt(
                    action=f"{name} (FAILED)",
                    actor="service",
                    input_hashes=[obj.hash],
                    output_hashes=[],
                    duration_ms=duration_ms,
                    prev_hash=task.hash,
                    metadata={"error": str(e)},
                )
                
                store = get_object_store()
                store.add(task)
                store.add(receipt)
                
                return ServiceResult(
                    success=False,
                    task=task,
                    receipt=receipt,
                    results=[],
                    duration_ms=duration_ms,
                    error=str(e),
                )
        
        # Register service
        svc_def = ServiceDefinition(
            name=name,
            description=description or func.__doc__ or "",
            accepts=accepts_types,
            produces=produces_types,
            constraints=constraints or [],
            category=category,
            max_ops=max_ops,
            max_time_ms=max_time_ms,
            handler=wrapper,
        )
        
        get_service_registry().register(svc_def)
        
        # Attach definition to wrapper
        wrapper._service_definition = svc_def
        
        return wrapper
    
    return decorator


@dataclass
class ServiceResult:
    """Result from a service execution."""
    success: bool
    task: Task
    receipt: Receipt
    results: List[FoghornObject]
    duration_ms: int
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API."""
        return {
            "success": self.success,
            "task": self.task.to_dict(),
            "receipt": self.receipt.to_dict(),
            "results": [r.to_dict() for r in self.results],
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# BUILT-IN SERVICES (Newton Stack)
# ═══════════════════════════════════════════════════════════════════════════════

@service(
    name="Echo",
    accepts=[Card, Query],
    produces=[Card],
    description="Echo input back (test service)",
    category=ServiceCategory.COMPUTE,
)
def echo_service(obj: FoghornObject) -> List[FoghornObject]:
    """Simple echo service for testing."""
    return [Card(
        title=f"Echo: {obj.id}",
        content=str(obj.to_dict()),
        prev_hash=obj.hash,
    )]


@service(
    name="Create Card",
    accepts=[Query],
    produces=[Card],
    description="Create a new card from a query",
    category=ServiceCategory.CREATE,
)
def create_card_service(obj: Query) -> List[FoghornObject]:
    """Create a card from query text."""
    return [Card(
        title=obj.text[:50] + "..." if len(obj.text) > 50 else obj.text,
        content=obj.text,
        prev_hash=obj.hash,
        tags=list(obj.filters.keys()) if obj.filters else [],
    )]


@service(
    name="Link Objects",
    accepts=[Card, Query, ResultSet],
    produces=[LinkCurve],
    description="Create a link between selected objects",
    category=ServiceCategory.CREATE,
)
def link_objects_service(obj: FoghornObject, target_hash: str = "") -> List[FoghornObject]:
    """Create a LinkCurve between objects."""
    if not target_hash:
        return []
    
    store = get_object_store()
    target = store.get(target_hash)
    
    if not target:
        return []
    
    link = obj.link_to(target)
    return [link]


def execute_service(service_name: str, obj: FoghornObject, **kwargs) -> ServiceResult:
    """
    Execute a registered service by name.
    """
    registry = get_service_registry()
    svc = registry.get(service_name)
    
    if not svc:
        raise ValueError(f"Service not found: {service_name}")
    
    if not svc.can_accept(obj):
        raise ValueError(f"Service '{service_name}' does not accept {obj.object_type.value}")
    
    if not svc.handler:
        raise ValueError(f"Service '{service_name}' has no handler")
    
    return svc.handler(obj, **kwargs)
