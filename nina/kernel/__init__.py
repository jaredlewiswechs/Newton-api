"""
Nina Desktop Kernel — Core Object System
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
)

__all__ = [
    # Objects
    "FoghornObject", "ObjectType", "Card", "Query", "ResultSet",
    "FileAsset", "Task", "Receipt", "LinkCurve", "Rule",
    "ObjectStore", "get_object_store",
    # Services
    "ServiceRegistry", "ServiceCategory", "ServiceDefinition", "ServiceResult",
    "service", "get_service_registry", "execute_service",
    # Commands
    "Command", "CommandState", "CommandBus", "AddObjectCommand",
    "UpdateObjectCommand", "DeleteObjectCommand", "BatchCommand",
    "get_command_bus", "execute", "undo", "redo",
    "add_object", "update_object", "delete_object",
    # Inspector
    "InspectorData", "InspectorSection", "Inspector",
    "get_inspector", "inspect", "inspect_by_hash",
    # Bézier
    "Point", "BezierCurve", "CurveType", "RelationshipStyle",
    "CurveFactory", "CurveStore", "get_curve_store", "render_curves_svg",
]
