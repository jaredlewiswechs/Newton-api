"""
═══════════════════════════════════════════════════════════════════════════════
NINA API — FastAPI Endpoints for Nina Desktop
═══════════════════════════════════════════════════════════════════════════════

HTTP interface to Nina kernel.

Routes:
    /nina/cards          GET/POST    Card management
    /nina/cards/{id}     GET/PUT/DEL Single card operations
    /nina/query          POST        Search/query
    /nina/services       GET         List services
    /nina/services/run   POST        Execute service
    /nina/inspect/{id}   GET         Object inspector
    /nina/tinytalk       POST        Run TinyTalk code
    /nina/workspace      GET         Workspace stats
    /nina/undo           POST        Undo last action
    /nina/redo           POST        Redo undone action

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import time
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query as QueryParam
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT NINA KERNEL
# ═══════════════════════════════════════════════════════════════════════════════

from nina.kernel import (
    Card, Query, ResultSet, LinkCurve, ObjectType,
    get_object_store, add_object, delete_object,
    get_service_registry, execute_service,
    get_command_bus, undo, redo,
    inspect,
)


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CardCreate(BaseModel):
    """Request to create a card."""
    title: str = Field(..., description="Card title")
    content: str = Field(..., description="Card content")
    tags: List[str] = Field(default=[], description="Card tags")
    source: Optional[str] = Field(None, description="Source attribution")
    source_url: Optional[str] = Field(None, description="Source URL")


class CardUpdate(BaseModel):
    """Request to update a card."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class QueryRequest(BaseModel):
    """Request to execute a query."""
    text: str = Field(..., description="Query text")
    filters: Dict[str, Any] = Field(default={}, description="Query filters")


class ServiceRunRequest(BaseModel):
    """Request to run a service."""
    service_name: str = Field(..., description="Name of service to run")
    object_hash: str = Field(..., description="Hash of object to process")


class TinyTalkRequest(BaseModel):
    """Request to run TinyTalk code."""
    code: str = Field(..., description="TinyTalk source code")


class LinkRequest(BaseModel):
    """Request to create a link."""
    source_hash: str = Field(..., description="Source object hash")
    target_hash: str = Field(..., description="Target object hash")
    relationship: str = Field(default="links_to", description="Relationship type")


class APIResponse(BaseModel):
    """Standard API response."""
    success: bool
    elapsed_us: int
    data: Optional[Any] = None
    error: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/nina", tags=["Nina Desktop"])


# ═══════════════════════════════════════════════════════════════════════════════
# CARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/cards", response_model=APIResponse)
def list_cards(
    tag: Optional[str] = QueryParam(None, description="Filter by tag"),
    limit: int = QueryParam(100, ge=1, le=1000)
):
    """List all cards."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    cards = store.get_by_type(ObjectType.CARD)
    
    # Apply tag filter
    if tag:
        cards = [c for c in cards if hasattr(c, 'tags') and tag in c.tags]
    
    # Apply limit
    cards = cards[:limit]
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=[c.to_dict() for c in cards]
    )


@router.post("/cards", response_model=APIResponse)
def create_card(request: CardCreate):
    """Create a new card."""
    start = time.perf_counter_ns()
    
    card = Card(
        title=request.title,
        content=request.content,
        tags=request.tags,
        source=request.source,
        source_url=request.source_url,
    )
    add_object(card)
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=card.to_dict()
    )


@router.get("/cards/{card_id}", response_model=APIResponse)
def get_card(card_id: str):
    """Get a card by ID or hash."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    card = store.get(card_id) or store.get_by_id(card_id)
    
    if not card or card.object_type != ObjectType.CARD:
        raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=card.to_dict()
    )


@router.put("/cards/{card_id}", response_model=APIResponse)
def update_card(card_id: str, request: CardUpdate):
    """Update a card."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    card = store.get(card_id) or store.get_by_id(card_id)
    
    if not card or card.object_type != ObjectType.CARD:
        raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")
    
    # Update fields
    if request.title is not None:
        card.title = request.title
    if request.content is not None:
        card.content = request.content
    if request.tags is not None:
        card.tags = request.tags
    if request.source is not None:
        card.source = request.source
    if request.source_url is not None:
        card.source_url = request.source_url
    
    # Rehash after update
    card.rehash()
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=card.to_dict()
    )


@router.delete("/cards/{card_id}", response_model=APIResponse)
def delete_card_endpoint(card_id: str):
    """Delete a card."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    card = store.get(card_id) or store.get_by_id(card_id)
    
    if not card or card.object_type != ObjectType.CARD:
        raise HTTPException(status_code=404, detail=f"Card not found: {card_id}")
    
    hash_to_delete = card.hash
    success = delete_object(hash_to_delete)
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=success,
        elapsed_us=elapsed_us,
        data={"deleted": hash_to_delete}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/query", response_model=APIResponse)
def execute_query(request: QueryRequest):
    """Execute a search query."""
    start = time.perf_counter_ns()
    
    query = Query(text=request.text, filters=request.filters)
    add_object(query)
    
    # Run compute service on query
    try:
        result = execute_service("Compute", query)
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=result.success,
            elapsed_us=elapsed_us,
            data={
                "query": query.to_dict(),
                "results": [r.to_dict() if hasattr(r, 'to_dict') else r for r in result.results],
                "service_duration_ms": result.duration_ms,
            }
        )
    except Exception as e:
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=False,
            elapsed_us=elapsed_us,
            data={
                "query": query.to_dict(),
                "results": [],
            },
            error=str(e)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/services", response_model=APIResponse)
def list_services():
    """List all available services."""
    start = time.perf_counter_ns()
    
    registry = get_service_registry()
    services = registry.list_all()
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=[
            {
                "name": s.name,
                "description": s.description,
                "category": s.category.value,
                "accepts": [t.value for t in s.accepts],
                "produces": [t.value for t in s.produces],
            }
            for s in services
        ]
    )


@router.post("/services/run", response_model=APIResponse)
def run_service(request: ServiceRunRequest):
    """Run a service on an object."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    obj = store.get(request.object_hash)
    
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object not found: {request.object_hash}")
    
    try:
        result = execute_service(request.service_name, obj)
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=result.success,
            elapsed_us=elapsed_us,
            data={
                "results": [r.to_dict() if hasattr(r, 'to_dict') else r for r in result.results],
                "service_duration_ms": result.duration_ms,
                "error": result.error,
            }
        )
    except Exception as e:
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=False,
            elapsed_us=elapsed_us,
            error=str(e)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/inspect/{object_id}", response_model=APIResponse)
def inspect_object(object_id: str):
    """Get inspector data for an object."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    obj = store.get(object_id) or store.get_by_id(object_id)
    
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object not found: {object_id}")
    
    data = inspect(obj)
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=data.to_dict()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TINYTALK ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tinytalk", response_model=APIResponse)
def run_tinytalk(request: TinyTalkRequest):
    """Execute TinyTalk code."""
    start = time.perf_counter_ns()
    
    try:
        from realTinyTalk.runtime import Runtime
        from realTinyTalk.parser import Parser
        from realTinyTalk.lexer import Lexer
        from nina.stdlib.foghorn_bindings import register_nina_stdlib
        
        # Create runtime with Nina stdlib
        runtime = Runtime()
        register_nina_stdlib(runtime)
        
        # Parse and execute
        lexer = Lexer(request.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        result = runtime.execute(ast)
        
        # Convert result to JSON-serializable
        def value_to_json(v):
            from realTinyTalk.types import ValueType
            if v.type == ValueType.NULL:
                return None
            if v.type == ValueType.LIST:
                return [value_to_json(x) for x in v.data]
            if v.type == ValueType.MAP:
                return {k: value_to_json(vv) for k, vv in v.data.items()}
            return v.data
        
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=True,
            elapsed_us=elapsed_us,
            data={
                "result": value_to_json(result),
                "type": result.type.value,
                "traces": [str(t) for t in runtime.traces[-10:]],  # Last 10 traces
            }
        )
    except Exception as e:
        elapsed_us = (time.perf_counter_ns() - start) // 1000
        return APIResponse(
            success=False,
            elapsed_us=elapsed_us,
            error=str(e)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/workspace", response_model=APIResponse)
def workspace_stats():
    """Get workspace statistics."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    bus = get_command_bus()
    
    # Count by type
    counts = {}
    for obj_type in ObjectType:
        counts[obj_type.value] = len(store.get_by_type(obj_type))
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data={
            "total_objects": store.count(),
            "by_type": counts,
            "undo_available": bus.can_undo(),
            "redo_available": bus.can_redo(),
        }
    )


@router.post("/undo", response_model=APIResponse)
def undo_action():
    """Undo the last action."""
    start = time.perf_counter_ns()
    
    success = undo()
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=success,
        elapsed_us=elapsed_us,
        data={"undone": success}
    )


@router.post("/redo", response_model=APIResponse)
def redo_action():
    """Redo the last undone action."""
    start = time.perf_counter_ns()
    
    success = redo()
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=success,
        elapsed_us=elapsed_us,
        data={"redone": success}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LINK ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/links", response_model=APIResponse)
def create_link(request: LinkRequest):
    """Create a link between objects."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    source = store.get(request.source_hash)
    target = store.get(request.target_hash)
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {request.source_hash}")
    if not target:
        raise HTTPException(status_code=404, detail=f"Target not found: {request.target_hash}")
    
    link = LinkCurve(
        source_hash=request.source_hash,
        target_hash=request.target_hash,
        source_type=source.object_type,
        target_type=target.object_type,
        relationship=request.relationship,
        prev_hash=request.source_hash,
    )
    add_object(link)
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=link.to_dict()
    )


@router.get("/links", response_model=APIResponse)
def list_links(
    source: Optional[str] = QueryParam(None),
    target: Optional[str] = QueryParam(None),
):
    """List links, optionally filtered by source/target."""
    start = time.perf_counter_ns()
    
    store = get_object_store()
    links = store.get_by_type(ObjectType.LINK_CURVE)
    
    if source:
        links = [l for l in links if l.source_hash == source]
    if target:
        links = [l for l in links if l.target_hash == target]
    
    elapsed_us = (time.perf_counter_ns() - start) // 1000
    return APIResponse(
        success=True,
        elapsed_us=elapsed_us,
        data=[l.to_dict() for l in links]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MOUNT TO MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def mount_nina_api(app):
    """Mount Nina API to a FastAPI application."""
    app.include_router(router)
    return app
