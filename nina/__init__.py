"""
═══════════════════════════════════════════════════════════════════════════════
NINA DESKTOP — A Contemporary NeXTSTEP-like Environment
═══════════════════════════════════════════════════════════════════════════════

"The constraint IS the instruction."
"The verification IS the computation."
"The ledger IS the memory."

Nina Desktop brings the elegance of NeXTSTEP into the verified computing era:

    ┌─────────────────────────────────────────────────────────────────┐
    │                        NINA ARCHITECTURE                        │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
    │   │   TINYTALK  │────▶│   KERNEL    │────▶│     API     │      │
    │   │  (Language) │     │  (Objects)  │     │  (FastAPI)  │      │
    │   └─────────────┘     └─────────────┘     └─────────────┘      │
    │          │                   │                   │              │
    │          ▼                   ▼                   ▼              │
    │   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
    │   │   STDLIB    │     │   BÉZIER    │     │   NEWTON    │      │
    │   │ (Builtins)  │     │  (Curves)   │     │ (Services)  │      │
    │   └─────────────┘     └─────────────┘     └─────────────┘      │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

Components:
    - kernel/     Hash-chained objects, services, commands, inspector
    - stdlib/     TinyTalk Foghorn bindings
    - api/        FastAPI HTTP interface
    - apps/       Example TinyTalk applications

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

__version__ = "0.1.0"
__author__ = "Jared Lewis"
__company__ = "Ada Computing Company"

# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

from .kernel.objects import (
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
    ObjectStore,
    get_object_store,
)

from .kernel.services import (
    ServiceRegistry,
    ServiceCategory,
    ServiceDefinition,
    ServiceResult,
    service,
    get_service_registry,
    execute_service,
)

from .kernel.commands import (
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

from .kernel.inspector import (
    InspectorData,
    InspectorSection,
    Inspector,
    get_inspector,
    inspect,
    inspect_by_hash,
)

from .kernel.bezier import (
    Point,
    BezierCurve,
    CurveType,
    RelationshipStyle,
    CurveFactory,
    CurveStore,
    get_curve_store,
    render_curves_svg,
)

# ═══════════════════════════════════════════════════════════════════════════════
# API EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from .api.routes import router, mount_nina_api
except ImportError:
    # FastAPI not available
    router = None
    mount_nina_api = None

# ═══════════════════════════════════════════════════════════════════════════════
# ALL EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__company__",
    
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
    "router",
    "mount_nina_api",
]
