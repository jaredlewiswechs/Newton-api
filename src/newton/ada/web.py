"""
Ada Web Interface
==================

FastAPI-based web server for Ada.
Provides REST API and WebSocket support.
"""

from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import json
import uuid

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from .schema import (
    AdaConfig,
    AdaMode,
    AdaResponse,
    CanvasType,
    CodeLanguage,
    ResponseFormat,
    TaskFrequency,
)


# =============================================================================
# Pydantic Models for API
# =============================================================================

if HAS_FASTAPI:

    class ChatRequest(BaseModel):
        """Request model for chat endpoint."""

        message: str = Field(..., description="User message")
        mode: Optional[str] = Field(None, description="Intelligence mode")
        conversation_id: Optional[str] = Field(None, description="Conversation ID")
        stream: bool = Field(False, description="Whether to stream response")

    class ChatResponse(BaseModel):
        """Response model for chat endpoint."""

        content: str
        mode: str
        verified: bool
        verification_status: str
        claims: List[Dict[str, Any]] = []
        conversation_id: str
        message_id: str
        processing_time_ms: int

    class ResearchRequest(BaseModel):
        """Request model for research endpoint."""

        query: str = Field(..., description="Research query")
        max_sources: Optional[int] = Field(None, description="Maximum sources")
        depth: Optional[int] = Field(None, description="Research depth")

    class AgentRequest(BaseModel):
        """Request model for agent endpoint."""

        task: str = Field(..., description="Task description")
        require_approval: bool = Field(False, description="Require human approval")
        max_steps: Optional[int] = Field(None, description="Maximum steps")

    class CanvasRequest(BaseModel):
        """Request model for canvas endpoint."""

        instruction: str = Field(..., description="Canvas instruction")
        canvas_id: Optional[str] = Field(None, description="Existing canvas ID")
        canvas_type: Optional[str] = Field(None, description="Canvas type")
        language: Optional[str] = Field(None, description="Programming language")

    class CodeRequest(BaseModel):
        """Request model for code execution endpoint."""

        code: str = Field(..., description="Code to execute")
        language: str = Field("python", description="Programming language")

    class TaskRequest(BaseModel):
        """Request model for task scheduling endpoint."""

        prompt: str = Field(..., description="Task prompt")
        name: str = Field(..., description="Task name")
        frequency: str = Field("daily", description="Frequency")
        description: Optional[str] = Field(None, description="Description")

    class MemoryRequest(BaseModel):
        """Request model for memory endpoint."""

        key: str = Field(..., description="Memory key")
        value: Any = Field(..., description="Value to store")
        verified: bool = Field(False, description="Is verified")


@dataclass
class AdaWebConfig:
    """Configuration for Ada web server."""

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = dataclass_field(
        default_factory=lambda: ["*"]
    )
    enable_docs: bool = True
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, Any] = {}  # Using Any to avoid WebSocket import issues

    async def connect(self, websocket, client_id: str):
        """Connect a client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Disconnect a client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast to all connected clients."""
        for connection in self.active_connections.values():
            await connection.send_json(message)


def create_ada_app(
    ada_config: Optional[AdaConfig] = None,
    web_config: Optional[AdaWebConfig] = None,
) -> "FastAPI":
    """
    Create the Ada FastAPI application.

    Args:
        ada_config: Ada configuration
        web_config: Web server configuration

    Returns:
        FastAPI application instance
    """
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI is required for web interface. "
            "Install with: pip install fastapi uvicorn"
        )

    from .engine import Ada

    # Initialize configurations
    ada_config = ada_config or AdaConfig()
    web_config = web_config or AdaWebConfig()

    # Create Ada instance
    ada = Ada(ada_config)

    # Create FastAPI app
    app = FastAPI(
        title="Ada - The Better ChatGPT",
        description="""
        Ada is a comprehensive AI assistant built on Newton's constraint verification system.

        ## Features
        - **Chat**: Verified conversational AI
        - **Research**: Deep web research with fact-checking
        - **Agent**: Autonomous task execution
        - **Canvas**: Document and code building
        - **Code**: Safe code execution
        - **Tasks**: Scheduled task execution
        - **Memory**: Persistent verified storage

        ## Why Ada is BETTER than ChatGPT
        1. All outputs are verified before returning
        2. Math is checked with SymPy
        3. Logic is checked for contradictions
        4. Full audit trail of decisions
        """,
        version="1.0.0",
        docs_url="/docs" if web_config.enable_docs else None,
        redoc_url="/redoc" if web_config.enable_docs else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=web_config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # WebSocket manager
    ws_manager = ConnectionManager()

    # Store conversations
    conversations: Dict[str, Any] = {}

    # =========================================================================
    # HEALTH & INFO ENDPOINTS
    # =========================================================================

    @app.get("/")
    async def root():
        """Root endpoint with API info."""
        return {
            "name": "Ada",
            "version": "1.0.0",
            "description": "The Better ChatGPT - Built on Newton's constraint verification",
            "endpoints": {
                "chat": "/api/chat",
                "research": "/api/research",
                "agent": "/api/agent",
                "canvas": "/api/canvas",
                "execute": "/api/execute",
                "tasks": "/api/tasks",
                "memory": "/api/memory",
                "docs": "/docs",
            },
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ada_version": "1.0.0",
        }

    @app.get("/api/stats")
    async def stats():
        """Get Ada usage statistics."""
        return ada.get_stats()

    # =========================================================================
    # CHAT ENDPOINTS
    # =========================================================================

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """
        Send a chat message and get a verified response.

        Ada will:
        1. Generate a response
        2. Extract and validate all claims
        3. If violations found, repair and retry
        4. Return only verified content
        """
        # Get or create conversation
        conv_id = request.conversation_id or str(uuid.uuid4())
        if conv_id not in conversations:
            conversations[conv_id] = ada.new_conversation()

        # Set conversation
        ada._conversation = conversations[conv_id]

        # Get response
        mode = AdaMode(request.mode) if request.mode else None
        response = ada.chat(request.message, mode=mode)

        return ChatResponse(
            content=response.content,
            mode=response.mode.value,
            verified=response.verified,
            verification_status=response.verification_status,
            claims=response.claims,
            conversation_id=conv_id,
            message_id=response.id,
            processing_time_ms=response.processing_time_ms,
        )

    @app.websocket("/ws/chat/{client_id}")
    async def websocket_chat(websocket: WebSocket, client_id: str):
        """WebSocket endpoint for streaming chat."""
        await ws_manager.connect(websocket, client_id)

        try:
            while True:
                data = await websocket.receive_json()
                message = data.get("message", "")
                mode = data.get("mode")

                # Process message
                mode_enum = AdaMode(mode) if mode else None
                response = ada.chat(message, mode=mode_enum)

                # Send response
                await ws_manager.send_message(client_id, {
                    "type": "response",
                    "content": response.content,
                    "verified": response.verified,
                    "claims": response.claims,
                })

        except WebSocketDisconnect:
            ws_manager.disconnect(client_id)

    # =========================================================================
    # RESEARCH ENDPOINTS
    # =========================================================================

    @app.post("/api/research")
    async def research(request: ResearchRequest):
        """
        Perform deep research on a topic.

        Ada will:
        1. Search the web for sources
        2. Extract and verify claims
        3. Cross-reference information
        4. Generate a comprehensive report
        """
        try:
            report = ada.research(
                request.query,
                max_sources=request.max_sources,
                depth=request.depth,
            )
            return report.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # AGENT ENDPOINTS
    # =========================================================================

    @app.post("/api/agent")
    async def agent(request: AgentRequest):
        """
        Execute a task autonomously.

        Ada will:
        1. Create an execution plan
        2. Execute each step with verification
        3. Handle errors and retry
        4. Return comprehensive results
        """
        try:
            result = ada.agent(
                request.task,
                require_approval=request.require_approval,
                max_steps=request.max_steps,
            )
            return result.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # CANVAS ENDPOINTS
    # =========================================================================

    @app.post("/api/canvas")
    async def canvas(request: CanvasRequest):
        """
        Create or modify a canvas document.

        Supports:
        - Code generation
        - Document writing
        - Diagram creation
        """
        try:
            canvas_type = CanvasType(request.canvas_type) if request.canvas_type else None
            language = CodeLanguage(request.language) if request.language else None

            # Get existing canvas if ID provided
            existing = None
            if request.canvas_id:
                existing = ada.engine.canvas.get_canvas(request.canvas_id)

            result = ada.canvas(
                request.instruction,
                document=existing,
            )
            return result.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/canvas/{canvas_id}")
    async def get_canvas(canvas_id: str):
        """Get a canvas by ID."""
        canvas = ada.engine.canvas.get_canvas(canvas_id)
        if not canvas:
            raise HTTPException(status_code=404, detail="Canvas not found")
        return canvas.to_dict()

    @app.get("/api/canvas")
    async def list_canvases():
        """List all canvases."""
        canvases = ada.engine.canvas.list_canvases()
        return [c.to_dict() for c in canvases]

    # =========================================================================
    # CODE EXECUTION ENDPOINTS
    # =========================================================================

    @app.post("/api/execute")
    async def execute_code(request: CodeRequest):
        """
        Execute code in a secure sandbox.

        Supported languages: python, javascript, bash
        """
        try:
            language = CodeLanguage(request.language.lower())
            result = ada.execute(request.code, language)
            return result.to_dict()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/execute/languages")
    async def supported_languages():
        """Get list of supported programming languages."""
        return {
            "languages": [lang.value for lang in ada.engine.sandbox.get_supported_languages()]
        }

    # =========================================================================
    # TASK SCHEDULING ENDPOINTS
    # =========================================================================

    @app.post("/api/tasks")
    async def create_task(request: TaskRequest):
        """Schedule a new task."""
        try:
            task = ada.schedule(
                prompt=request.prompt,
                name=request.name,
                frequency=request.frequency,
                description=request.description or "",
            )
            return task.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/tasks")
    async def list_tasks(enabled_only: bool = Query(False)):
        """List scheduled tasks."""
        tasks = ada.engine.scheduler.list_tasks(enabled_only=enabled_only)
        return [t.to_dict() for t in tasks]

    @app.get("/api/tasks/{task_id}")
    async def get_task(task_id: str):
        """Get a task by ID."""
        task = ada.engine.scheduler.store.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()

    @app.delete("/api/tasks/{task_id}")
    async def delete_task(task_id: str):
        """Delete a scheduled task."""
        if ada.engine.scheduler.unschedule(task_id):
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Task not found")

    @app.post("/api/tasks/{task_id}/run")
    async def run_task_now(task_id: str):
        """Run a task immediately."""
        result = ada.engine.scheduler.run_now(task_id)
        return result.to_dict()

    @app.get("/api/tasks/{task_id}/history")
    async def task_history(task_id: str, limit: int = Query(10)):
        """Get task execution history."""
        history = ada.engine.scheduler.get_history(task_id, limit)
        return [h.to_dict() for h in history]

    # =========================================================================
    # MEMORY ENDPOINTS
    # =========================================================================

    @app.post("/api/memory")
    async def add_memory(request: MemoryRequest):
        """Add an entry to memory."""
        try:
            entry = ada.remember(request.key, request.value, request.verified)
            return entry.to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/memory")
    async def search_memory(query: str = Query(...), limit: int = Query(10)):
        """Search memory."""
        results = ada.recall(query)[:limit]
        return [r.to_dict() for r in results]

    @app.delete("/api/memory/{key}")
    async def delete_memory(key: str):
        """Delete a memory entry."""
        if ada.forget(key):
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Memory entry not found")

    @app.get("/api/memory/stats")
    async def memory_stats():
        """Get memory statistics."""
        return ada.engine.memory.stats()

    # =========================================================================
    # CONVERSATION MANAGEMENT
    # =========================================================================

    @app.post("/api/conversations")
    async def new_conversation(title: Optional[str] = Body(None)):
        """Create a new conversation."""
        conv = ada.new_conversation(title)
        conversations[conv.id] = conv
        return {"conversation_id": conv.id, "title": conv.title}

    @app.get("/api/conversations/{conv_id}")
    async def get_conversation(conv_id: str):
        """Get a conversation by ID."""
        conv = conversations.get(conv_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv.to_dict()

    @app.delete("/api/conversations/{conv_id}")
    async def delete_conversation(conv_id: str):
        """Delete a conversation."""
        if conv_id in conversations:
            del conversations[conv_id]
            return {"status": "deleted"}
        raise HTTPException(status_code=404, detail="Conversation not found")

    return app


def run_server(
    ada_config: Optional[AdaConfig] = None,
    web_config: Optional[AdaWebConfig] = None,
):
    """
    Run the Ada web server.

    Args:
        ada_config: Ada configuration
        web_config: Web server configuration
    """
    if not HAS_FASTAPI:
        raise ImportError(
            "FastAPI and uvicorn are required. "
            "Install with: pip install fastapi uvicorn"
        )

    import uvicorn

    web_config = web_config or AdaWebConfig()
    app = create_ada_app(ada_config, web_config)

    uvicorn.run(
        app,
        host=web_config.host,
        port=web_config.port,
    )
