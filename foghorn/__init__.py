"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN — Nina Desktop Kernel
═══════════════════════════════════════════════════════════════════════════════

A contemporary NeXTSTEP-like environment where:
- Every object is hash-chained and inspectable
- Every service is constraint-checked
- Every relationship is a Bézier curve

The constraint IS the instruction.
The verification IS the computation.
The ledger IS the memory.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

from .objects import (
    FoghornObject,
    ObjectType,
    Card,
    Query,
    ResultSet,
    FileAsset,
    Task,
    Receipt,
    LinkCurve,
    Rule,
    # Phase A additions
    MapPlace,
    Route,
    Automation,
    ObjectStore,
    get_object_store,
)

from .services import (
    ServiceRegistry,
    ServiceCategory,
    ServiceDefinition,
    ServiceResult,
    service,
    get_service_registry,
    execute_service,
)

from .commands import (
    Command,
    CommandState,
    CommandBus,
    AddObjectCommand,
    UpdateObjectCommand,
    DeleteObjectCommand,
    BatchCommand,
    get_command_bus,
    execute,
    undo,
    redo,
    add_object,
    update_object,
    delete_object,
)

from .inspector import (
    InspectorData,
    InspectorSection,
    Inspector,
    get_inspector,
    inspect,
    inspect_by_hash,
)

from .bezier import (
    Point,
    BezierCurve,
    CurveType,
    RelationshipStyle,
    CurveFactory,
    CurveStore,
    get_curve_store,
    render_curves_svg,
    # Phase A additions - Bézier primitives
    Superellipse,
    MotionCurve,
    EasingType,
    EnvelopeCurve,
)

__version__ = "0.1.0"
__all__ = [
    # Objects
    "FoghornObject",
    "ObjectType",
    "Card",
    "Query", 
    "ResultSet",
    "FileAsset",
    "Task",
    "Receipt",
    "LinkCurve",
    "Rule",
    "ObjectStore",
    "get_object_store",
    # Services
    "ServiceRegistry",
    "ServiceCategory",
    "ServiceDefinition",
    "ServiceResult",
    "service",
    "get_service_registry",
    "execute_service",
    # Commands
    "Command",
    "CommandState",
    "CommandBus",
    "AddObjectCommand",
    "UpdateObjectCommand",
    "DeleteObjectCommand",
    "BatchCommand",
    "get_command_bus",
    "execute",
    "undo",
    "redo",
    "add_object",
    "update_object",
    "delete_object",
    # Inspector
    "InspectorData",
    "InspectorSection",
    "Inspector",
    "get_inspector",
    "inspect",
    "inspect_by_hash",
    # Bézier
    "Point",
    "BezierCurve",
    "CurveType",
    "RelationshipStyle",
    "CurveFactory",
    "CurveStore",
    "get_curve_store",
    "render_curves_svg",
    # API
    "mount_foghorn_api",
    "router",
]

# Import API router for mounting
try:
    from .api import router, mount_foghorn_api
except ImportError:
    # FastAPI not available
    router = None
    mount_foghorn_api = None
