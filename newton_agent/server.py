#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON AGENT SERVER
Self-Verifying Autonomous Agent API

Every action is constrained. Every claim is grounded. Every step is logged.
═══════════════════════════════════════════════════════════════════════════════

Endpoints:
    POST /chat          - Send message to agent
    POST /chat/stream   - Stream response from agent
    POST /ground        - Verify a specific claim
    GET  /history       - Get conversation history
    GET  /audit         - Export full audit trail
    GET  /stats         - Get agent statistics
    POST /clear         - Clear conversation
    GET  /models        - List available Ollama models
    POST /model         - Switch Ollama model
    GET  /health        - Health check

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import time
import os
import sys
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from newton_agent import (
    NewtonAgent, AgentConfig, AgentResponse,
    OllamaBackend, OllamaConfig, create_ollama_generator,
    get_kinematic_analyzer, get_trajectory_verifier, get_trajectory_composer,
)

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Newton Agent",
    description="Self-Verifying Autonomous Agent - The constraint IS the instruction",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama backend
ollama_config = OllamaConfig(
    model=os.environ.get("OLLAMA_MODEL", "qwen2.5:3b"),
    base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
)
ollama_backend = OllamaBackend(ollama_config)

# Initialize agent with Ollama
agent = NewtonAgent(
    config=AgentConfig(
        enable_grounding=True,
        require_official_sources=False,
        grounding_threshold=6.0,
        max_conversation_turns=100,
    ),
    response_generator=create_ollama_generator(ollama_config) if ollama_backend.is_available() else None
)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    ground_claims: bool = True


class GroundRequest(BaseModel):
    claim: str
    require_official: bool = False


class ModelRequest(BaseModel):
    model: str


class TrajectoryRequest(BaseModel):
    text: str


class KeystrokeRequest(BaseModel):
    char: str


class ChatResponse(BaseModel):
    content: str
    verified: bool
    action: str
    constraints: Dict[str, List[str]]
    grounding: Dict[str, Any]
    meta: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat UI."""
    ui_path = Path(__file__).parent / "ui" / "index.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(encoding='utf-8'), status_code=200)
    return HTMLResponse(content="<h1>Newton Agent</h1><p>UI not found. Use /docs for API.</p>")


@app.post("/chat")
async def chat(request: ChatRequest) -> Dict:
    """
    Send a message to the Newton Agent.
    
    The message goes through the full verification pipeline:
    1. Constraint checking (safety filters)
    2. Response generation
    3. Claim grounding (if enabled)
    4. Audit logging
    """
    start = time.time()
    
    # Temporarily disable grounding if requested
    original_grounding = agent.config.enable_grounding
    if not request.ground_claims:
        agent.config.enable_grounding = False
    
    try:
        response = agent.process(request.message)
    finally:
        agent.config.enable_grounding = original_grounding
    
    return {
        **response.to_dict(),
        "elapsed_ms": int((time.time() - start) * 1000),
        "model": ollama_config.model,
        "ollama_available": ollama_backend.is_available(),
    }


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream a response from the Newton Agent.
    Returns Server-Sent Events.
    """
    # Check constraints first
    passed, failed = agent._check_constraints(request.message)
    
    if failed:
        refusal = agent._generate_refusal(failed)
        async def error_stream():
            yield f"data: {json.dumps({'content': refusal, 'done': True, 'blocked': True})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    # Log user message
    agent.memory.add_turn(
        role=agent.memory.turns[0].role.__class__.USER if agent.memory.turns else None,
        content=request.message,
    )
    
    async def generate():
        full_response = ""
        context = agent.memory.get_context(max_turns=10)
        
        for chunk in ollama_backend.generate_stream(request.message, context):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
        
        yield f"data: {json.dumps({'content': '', 'done': True, 'full_response': full_response})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/ground")
async def ground_claim(request: GroundRequest) -> Dict:
    """
    Verify a specific claim against external sources.
    
    Returns:
    - confidence_score: 0-10 (lower = more confident)
    - status: VERIFIED, LIKELY, UNCERTAIN, UNVERIFIED
    - evidence: List of supporting sources
    """
    start = time.time()
    
    result = agent.grounding.verify_claim(
        request.claim,
        require_official=request.require_official,
    )
    
    return {
        **result.to_dict(),
        "elapsed_ms": int((time.time() - start) * 1000),
    }


@app.get("/history")
async def get_history() -> Dict:
    """Get conversation history."""
    return {
        "turns": agent.get_conversation_history(),
        "count": len(agent.memory.turns),
    }


@app.get("/audit")
async def export_audit() -> Dict:
    """
    Export full audit trail.
    
    Includes:
    - Complete hash-chained conversation history
    - Constraint check results
    - Grounding verification results
    - Agent statistics
    """
    return agent.export_audit_trail()


@app.get("/stats")
async def get_stats() -> Dict:
    """Get agent statistics."""
    return {
        **agent.get_stats(),
        "grounding_stats": agent.grounding.get_stats(),
    }


@app.post("/clear")
async def clear_conversation() -> Dict:
    """Clear conversation history and start fresh."""
    agent.clear_conversation()
    return {
        "status": "cleared",
        "message": "Conversation history cleared. Memory chain reset.",
    }


@app.get("/health")
async def health() -> Dict:
    """Health check."""
    return {
        "status": "healthy",
        "agent": "Newton Agent",
        "version": "1.0.0",
        "memory_chain_valid": agent.memory.verify_chain(),
        "ollama_available": ollama_backend.is_available(),
        "model": ollama_config.model,
        "invariant": "1 == 1",
    }


@app.get("/models")
async def list_models() -> Dict:
    """List available Ollama models."""
    models = ollama_backend.list_models()
    return {
        "models": models,
        "current": ollama_config.model,
        "available": ollama_backend.is_available(),
    }


@app.post("/model")
async def set_model(request: ModelRequest) -> Dict:
    """Switch to a different Ollama model."""
    global agent, ollama_config
    
    models = ollama_backend.list_models()
    if request.model not in models:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' not found. Available: {models}"
        )
    
    ollama_config.model = request.model
    
    # Recreate agent with new model
    agent = NewtonAgent(
        config=agent.config,
        response_generator=create_ollama_generator(ollama_config)
    )
    
    return {
        "status": "switched",
        "model": request.model,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# KINEMATIC LINGUISTICS ROUTES
# Language IS a Bézier trajectory through meaning space.
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/trajectory/verify")
async def verify_trajectory(request: TrajectoryRequest) -> Dict:
    """
    Verify text as a kinematic trajectory through meaning space.
    
    Checks two constraint surfaces:
    1. Grammar Ω - syntactic admissibility
    2. Meaning Ω - semantic coherence
    
    "Colorless green ideas sleep furiously"
    → Inside grammar Ω ✓
    → Outside meaning Ω ✗
    """
    start = time.time()
    verifier = get_trajectory_verifier()
    result = verifier.verify(request.text)
    
    return {
        **result.to_dict(),
        "elapsed_ms": int((time.time() - start) * 1000),
    }


@app.post("/trajectory/analyze")
async def analyze_trajectory(request: TrajectoryRequest) -> Dict:
    """
    Full kinematic analysis of text.
    
    Returns:
    - Trajectory metrics (weight, curvature, commit)
    - Grammar check (envelope balance, termination)
    - Word-by-word breakdown
    """
    start = time.time()
    analyzer = get_kinematic_analyzer()
    result = analyzer.analyze_sentence(request.text)
    
    return {
        **result,
        "elapsed_ms": int((time.time() - start) * 1000),
    }


@app.post("/trajectory/compose")
async def compose_trajectory(request: TrajectoryRequest) -> Dict:
    """
    Get composition state for text (useful for real-time typing feedback).
    
    Shows:
    - Current kinematic state
    - Envelope depth (open brackets)
    - Suggested completions
    """
    start = time.time()
    composer = get_trajectory_composer()
    state = composer.compose(request.text)
    
    return {
        "text": state.text,
        "cursor": state.cursor_position,
        "weight": round(state.current_weight, 2),
        "curvature": round(state.current_curvature, 2),
        "commit": round(state.current_commit, 2),
        "envelope_depth": state.envelope_depth,
        "suggestions": state.suggested_completions,
        "needs_closure": state.needs_closure,
        "approaching_commit": state.approaching_commit,
        "elapsed_ms": int((time.time() - start) * 1000),
    }


@app.post("/trajectory/keystroke")
async def analyze_keystroke(request: KeystrokeRequest) -> Dict:
    """
    Analyze a single keystroke's kinematic contribution.
    
    Every symbol encodes:
    - A gesture (how you draw it)
    - A sound (how you speak it)
    - A meaning (what it does semantically)
    - An operation (what it does computationally)
    """
    composer = get_trajectory_composer()
    return composer.keystroke_analysis(request.char)


@app.get("/trajectory/alphabet")
async def get_kinematic_alphabet() -> Dict:
    """
    Get the full kinematic alphabet.
    
    The alphabet as frozen kinematics:
    Each character is a trajectory that got committed.
    The shape IS the motion signature.
    """
    analyzer = get_kinematic_analyzer()
    
    vowels = {}
    consonants = {}
    digits = {}
    operators = {}
    
    for char, sig in analyzer.signatures.items():
        entry = {
            "weight": sig.weight,
            "curvature": sig.curvature,
            "commit": sig.commit_strength,
            "description": sig.phonetic_desc,
            "anchor": sig.is_anchor,
            "terminus": sig.is_terminus,
            "handle": sig.is_handle,
        }
        
        if sig.symbol_type.value == "vowel":
            vowels[char] = entry
        elif sig.symbol_type.value == "consonant":
            consonants[char] = entry
        elif sig.symbol_type.value == "digit":
            digits[char] = entry
        else:
            operators[char] = entry
    
    return {
        "vowels": vowels,
        "consonants": consonants,
        "digits": digits,
        "operators": operators,
        "sacred_symbols": {
            ":": "THE f/g RATIO - dimensional analysis",
            ".": "P₃ COMMIT - terminus",
            "?": "VERIFICATION QUERY - is trajectory admissible?",
            "!": "Certainty - deep inside Ω",
            "=": "Constraint satisfaction",
        },
        "philosophy": {
            "subject": "P₀ (anchor, root)",
            "verb": "The curve itself (motion, action)",
            "object": "P₃ (terminus, commitment)",
            "adjectives": "Handle adjustments (H₁, H₂)",
            "syntax": "Ω (admissible region)",
            "grammar": "Constraint geometry, not boolean rules",
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Default port, try alternatives if busy
    default_port = int(os.environ.get("PORT", 8090))
    port = default_port
    
    # Try to find an available port
    for try_port in [default_port, 8091, 8092, 8093, 8080, 3000]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', try_port))
            sock.close()
            port = try_port
            break
        except OSError:
            continue
    
    print(f"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON AGENT SERVER
Self-Verifying Autonomous Agent

The constraint IS the instruction.
The verification IS the computation.
The ledger IS the memory.

Starting on http://localhost:{port}
API docs at http://localhost:{port}/docs
═══════════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
