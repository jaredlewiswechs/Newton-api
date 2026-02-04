"""
═══════════════════════════════════════════════════════════════════════════════
FOGHORN STDLIB — TinyTalk Bindings for Nina Desktop
═══════════════════════════════════════════════════════════════════════════════

This module exposes Foghorn kernel to TinyTalk programs.

Users can write Nina apps in TinyTalk:

    # Create a card
    let card = Card.new("My Note", "This is content")
    
    # Add to workspace
    Workspace.add(card)
    
    # Run a service
    let result = Services.run("Verify Claim", card)
    
    # Inspect anything
    Inspector.show(card)

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from realTinyTalk.types import Value, ValueType

# Import Foghorn kernel
from foghorn import (
    Card, Query, ResultSet, FileAsset, Task, Receipt, LinkCurve, Rule,
    ObjectType, get_object_store, add_object, delete_object,
    get_service_registry, execute_service,
    get_command_bus, undo, redo,
    inspect, get_inspector,
)


# ═══════════════════════════════════════════════════════════════════════════════
# VALUE CONVERSION
# ═══════════════════════════════════════════════════════════════════════════════

def foghorn_to_tinytalk(obj: Any) -> Value:
    """Convert Foghorn object to TinyTalk value."""
    if obj is None:
        return Value.null_val()
    
    if hasattr(obj, 'to_dict'):
        # Foghorn object - convert to map
        d = obj.to_dict()
        return Value.map_val({k: foghorn_to_tinytalk(v) for k, v in d.items()})
    
    if isinstance(obj, dict):
        return Value.map_val({k: foghorn_to_tinytalk(v) for k, v in obj.items()})
    
    if isinstance(obj, list):
        return Value.list_val([foghorn_to_tinytalk(x) for x in obj])
    
    if isinstance(obj, bool):
        return Value.bool_val(obj)
    
    if isinstance(obj, int):
        return Value.int_val(obj)
    
    if isinstance(obj, float):
        return Value.float_val(obj)
    
    if isinstance(obj, str):
        return Value.string_val(obj)
    
    return Value.string_val(str(obj))


def tinytalk_to_foghorn(val: Value) -> Any:
    """Convert TinyTalk value to Python for Foghorn."""
    if val.type == ValueType.NULL:
        return None
    if val.type == ValueType.LIST:
        return [tinytalk_to_foghorn(v) for v in val.data]
    if val.type == ValueType.MAP:
        return {k: tinytalk_to_foghorn(v) for k, v in val.data.items()}
    return val.data


# ═══════════════════════════════════════════════════════════════════════════════
# CARD FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_card_new(args: List[Value]) -> Value:
    """
    Create a new Card.
    
    Usage:
        let card = Card.new("Title", "Content")
        let card = Card.new("Title", "Content", ["tag1", "tag2"])
    """
    if len(args) < 2:
        return Value.null_val()
    
    title = args[0].data if args[0].type == ValueType.STRING else str(args[0].data)
    content = args[1].data if args[1].type == ValueType.STRING else str(args[1].data)
    
    tags = []
    if len(args) > 2 and args[2].type == ValueType.LIST:
        tags = [v.data for v in args[2].data if v.type == ValueType.STRING]
    
    card = Card(title=title, content=content, tags=tags)
    add_object(card)
    
    return foghorn_to_tinytalk(card)


def builtin_card_get(args: List[Value]) -> Value:
    """
    Get a Card by hash or ID.
    
    Usage:
        let card = Card.get("abc123")
    """
    if not args or args[0].type != ValueType.STRING:
        return Value.null_val()
    
    hash_or_id = args[0].data
    store = get_object_store()
    
    obj = store.get(hash_or_id) or store.get_by_id(hash_or_id)
    
    if obj and obj.object_type == ObjectType.CARD:
        return foghorn_to_tinytalk(obj)
    
    return Value.null_val()


def builtin_card_all(args: List[Value]) -> Value:
    """
    Get all Cards.
    
    Usage:
        let cards = Card.all()
    """
    store = get_object_store()
    cards = store.get_by_type(ObjectType.CARD)
    return Value.list_val([foghorn_to_tinytalk(c) for c in cards])


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_query_new(args: List[Value]) -> Value:
    """
    Create a new Query.
    
    Usage:
        let q = Query.new("What is Newton?")
        let q = Query.new("search term", {type: "card"})
    """
    if not args:
        return Value.null_val()
    
    text = args[0].data if args[0].type == ValueType.STRING else str(args[0].data)
    
    filters = {}
    if len(args) > 1 and args[1].type == ValueType.MAP:
        filters = tinytalk_to_foghorn(args[1])
    
    query = Query(text=text, filters=filters)
    add_object(query)
    
    return foghorn_to_tinytalk(query)


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_services_list(args: List[Value]) -> Value:
    """
    List all available services.
    
    Usage:
        let services = Services.list()
    """
    registry = get_service_registry()
    services = registry.list_all()
    
    return Value.list_val([
        Value.map_val({
            "name": Value.string_val(s.name),
            "description": Value.string_val(s.description),
            "category": Value.string_val(s.category.value),
            "accepts": Value.list_val([Value.string_val(t.value) for t in s.accepts]),
            "produces": Value.list_val([Value.string_val(t.value) for t in s.produces]),
        })
        for s in services
    ])


def builtin_services_run(args: List[Value]) -> Value:
    """
    Run a service on an object.
    
    Usage:
        let result = Services.run("Compute", query)
        let result = Services.run("Verify Claim", card)
    """
    if len(args) < 2:
        return Value.null_val()
    
    service_name = args[0].data if args[0].type == ValueType.STRING else str(args[0].data)
    
    # Get the object from the store by hash
    if args[1].type == ValueType.MAP and "hash" in args[1].data:
        hash_val = args[1].data["hash"]
        obj_hash = hash_val.data if hasattr(hash_val, 'data') else str(hash_val)
        store = get_object_store()
        obj = store.get(obj_hash)
        
        if not obj:
            return Value.map_val({
                "success": Value.bool_val(False),
                "error": Value.string_val(f"Object not found: {obj_hash}"),
            })
    else:
        return Value.map_val({
            "success": Value.bool_val(False),
            "error": Value.string_val("Invalid object - must have 'hash' field"),
        })
    
    try:
        result = execute_service(service_name, obj)
        return Value.map_val({
            "success": Value.bool_val(result.success),
            "duration_ms": Value.int_val(result.duration_ms),
            "results": Value.list_val([foghorn_to_tinytalk(r) for r in result.results]),
            "error": Value.string_val(result.error) if result.error else Value.null_val(),
        })
    except Exception as e:
        return Value.map_val({
            "success": Value.bool_val(False),
            "error": Value.string_val(str(e)),
        })


def builtin_services_for(args: List[Value]) -> Value:
    """
    Find services that work with an object type.
    
    Usage:
        let services = Services.for("card")
    """
    if not args or args[0].type != ValueType.STRING:
        return Value.list_val([])
    
    type_name = args[0].data.lower()
    
    # Create a dummy object of that type
    type_map = {
        "card": Card(title="", content=""),
        "query": Query(text=""),
    }
    
    obj = type_map.get(type_name)
    if not obj:
        return Value.list_val([])
    
    registry = get_service_registry()
    services = registry.find_for_object(obj)
    
    return Value.list_val([Value.string_val(s.name) for s in services])


# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_inspect(args: List[Value]) -> Value:
    """
    Inspect an object.
    
    Usage:
        let info = inspect(card)
    """
    if not args or args[0].type != ValueType.MAP:
        return Value.null_val()
    
    # Get object by hash
    if "hash" in args[0].data:
        hash_val = args[0].data["hash"]
        obj_hash = hash_val.data if hasattr(hash_val, 'data') else str(hash_val)
        store = get_object_store()
        obj = store.get(obj_hash)
        
        if obj:
            data = inspect(obj)
            return foghorn_to_tinytalk(data.to_dict())
    
    return Value.null_val()


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND BUS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_undo(args: List[Value]) -> Value:
    """
    Undo the last action.
    
    Usage:
        undo()
    """
    success = undo()
    return Value.bool_val(success)


def builtin_redo(args: List[Value]) -> Value:
    """
    Redo the last undone action.
    
    Usage:
        redo()
    """
    success = redo()
    return Value.bool_val(success)


def builtin_history(args: List[Value]) -> Value:
    """
    Get command history.
    
    Usage:
        let history = history()
        let history = history(10)  # Last 10
    """
    limit = 10
    if args and args[0].type == ValueType.INT:
        limit = args[0].data
    
    bus = get_command_bus()
    history = bus.get_history(limit)
    
    return Value.list_val([foghorn_to_tinytalk(h) for h in history])


# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_workspace_count(args: List[Value]) -> Value:
    """
    Get count of objects in workspace.
    
    Usage:
        let count = Workspace.count()
    """
    store = get_object_store()
    return Value.int_val(store.count())


def builtin_workspace_all(args: List[Value]) -> Value:
    """
    Get all objects in workspace.
    
    Usage:
        let objects = Workspace.all()
    """
    store = get_object_store()
    objects = store.export()
    return Value.list_val([foghorn_to_tinytalk(o) for o in objects])


def builtin_workspace_delete(args: List[Value]) -> Value:
    """
    Delete an object from workspace.
    
    Usage:
        Workspace.delete(card.hash)
    """
    if not args or args[0].type != ValueType.STRING:
        return Value.bool_val(False)
    
    hash_str = args[0].data
    success = delete_object(hash_str)
    return Value.bool_val(success)


# ═══════════════════════════════════════════════════════════════════════════════
# LINK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_link_new(args: List[Value]) -> Value:
    """
    Create a link between two objects.
    
    Usage:
        let link = Link.new(card1.hash, card2.hash)
        let link = Link.new(card1.hash, card2.hash, "references")
    """
    if len(args) < 2:
        return Value.null_val()
    
    source_hash = args[0].data if args[0].type == ValueType.STRING else str(args[0].data)
    target_hash = args[1].data if args[1].type == ValueType.STRING else str(args[1].data)
    
    relationship = "links_to"
    if len(args) > 2 and args[2].type == ValueType.STRING:
        relationship = args[2].data
    
    store = get_object_store()
    source = store.get(source_hash)
    target = store.get(target_hash)
    
    if not source or not target:
        return Value.null_val()
    
    link = LinkCurve(
        source_hash=source_hash,
        target_hash=target_hash,
        source_type=source.object_type,
        target_type=target.object_type,
        relationship=relationship,
        prev_hash=source_hash,
    )
    
    add_object(link)
    return foghorn_to_tinytalk(link)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ALL BUILTINS
# ═══════════════════════════════════════════════════════════════════════════════

FOGHORN_BUILTINS = {
    # Card
    'Card.new': builtin_card_new,
    'Card.get': builtin_card_get,
    'Card.all': builtin_card_all,
    
    # Query
    'Query.new': builtin_query_new,
    
    # Services
    'Services.list': builtin_services_list,
    'Services.run': builtin_services_run,
    'Services.find_for': builtin_services_for,  # Renamed from 'for' (reserved word)
    
    # Inspector
    'inspect': builtin_inspect,
    
    # Commands
    'undo': builtin_undo,
    'redo': builtin_redo,
    'history': builtin_history,
    
    # Workspace
    'Workspace.count': builtin_workspace_count,
    'Workspace.all': builtin_workspace_all,
    'Workspace.delete': builtin_workspace_delete,
    
    # Links
    'Link.new': builtin_link_new,
}


def register_foghorn_stdlib(runtime):
    """Register Foghorn builtins with a TinyTalk runtime."""
    from realTinyTalk.runtime import TinyFunction
    
    for name, fn in FOGHORN_BUILTINS.items():
        # Create a native function wrapper
        func = TinyFunction(
            name=name,
            params=[],
            body=None,
            closure=runtime.global_scope,
            is_native=True,
            native_fn=fn,
        )
        
        # Handle dotted names (Card.new -> Card object with new method)
        if '.' in name:
            parts = name.split('.')
            obj_name, method_name = parts[0], parts[1]
            
            # Get or create the namespace object
            ns = runtime.global_scope.get(obj_name)
            if ns is None or ns.type != ValueType.MAP:
                ns = Value.map_val({})
                runtime.global_scope.define(obj_name, ns)
            
            # Add method
            ns.data[method_name] = Value(ValueType.FUNCTION, func)
        else:
            # Simple function
            runtime.global_scope.define(name, Value(ValueType.FUNCTION, func))
