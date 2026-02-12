#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VOICE INTERFACE - Standalone API
AskAda: Mother Of All Demos

"Easy now with Newton. He has so much power. Think speaking to your computer."

Standalone deployment of Newton's voice interface for Vercel.
All dependencies are inlined - no external Newton imports required.

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time

from core.voice_interface import (
    NewtonVoiceInterface,
    StreamingVoiceInterface,
    IntentParser,
    PatternLibrary,
)

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

ENGINE = "Newton Voice Interface (Standalone) 1.0.0"

app = FastAPI(
    title="Newton Voice Interface - AskAda",
    description=(
        "Mother Of All Demos: Natural language → verified computation.\n\n"
        "Speak to your computer. Newton understands intent, generates constraints, "
        "executes verified computation, and returns results with cryptographic proofs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton instances
voice_interface = NewtonVoiceInterface()
streaming_voice = StreamingVoiceInterface()


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceAskRequest(BaseModel):
    """Ask Newton via voice/natural language interface."""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class VoiceStreamRequest(BaseModel):
    """Streaming voice request."""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class IntentParseRequest(BaseModel):
    """Parse natural language to intent."""
    text: str


class PatternSearchRequest(BaseModel):
    """Search available app patterns."""
    query: str
    domain: Optional[str] = None
    limit: Optional[int] = 5


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH & ROOT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Newton Voice Interface - AskAda."""
    return {
        "name": "Newton Voice Interface - AskAda",
        "tagline": "Easy now with Newton. He has so much power. Think speaking to your computer.",
        "version": "1.0.0",
        "engine": ENGINE,
        "endpoints": {
            "ask": "POST /voice/ask",
            "stream": "POST /voice/stream",
            "intent": "POST /voice/intent",
            "patterns": "GET /voice/patterns",
            "search_patterns": "POST /voice/patterns/search",
            "pattern_detail": "GET /voice/patterns/{pattern_id}",
            "session": "GET /voice/session/{session_id}",
            "demo": "GET /voice/demo",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "engine": ENGINE, "timestamp": int(time.time() * 1000)}


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE ENDPOINTS - Mother Of All Demos
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/voice/ask")
async def voice_ask(request: VoiceAskRequest):
    """
    Ask Newton via natural language - The MOAD Interface.

    This is the Mother Of All Demos entry point:
    - User describes what they want in natural language
    - Newton understands intent → generates CDL → builds/deploys app
    - Returns verified results with cryptographic proofs

    Examples:
        "Build me a calculator"
        "Create a financial calculator that proves its math"
        "I need a lesson planner for 5th grade math"
        "Deploy an expense tracker with audit trails"
    """
    try:
        response = voice_interface.ask(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
        )

        return {
            "session_id": response.session_id,
            "turn_id": response.turn_id,
            "intent": response.intent,
            "cdl": response.cdl,
            "result": response.result,
            "verified": response.verified,
            "proof": response.proof,
            "message": response.message,
            "suggestions": response.suggestions,
            "elapsed_us": response.elapsed_us,
            "engine": ENGINE,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/stream")
async def voice_stream(request: VoiceStreamRequest):
    """
    Streaming voice interface - Progressive results.

    Returns a list of status updates showing the progressive
    processing of your request through Newton's pipeline:
    1. Session ready
    2. Intent parsed
    3. CDL generated
    4. Executed
    5. Verified
    6. Complete with proof
    """
    try:
        results = []
        for update in streaming_voice.ask_streaming(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
        ):
            results.append(update)

        return {
            "updates": results,
            "final": results[-1] if results else None,
            "engine": ENGINE,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/intent")
async def parse_intent_endpoint(request: IntentParseRequest):
    """
    Parse natural language to structured intent.

    Returns:
        - intent_type: what/do/go/remember
        - domain: finance/education/health/make/etc.
        - action: the primary verb
        - entities: extracted values
        - confidence: how sure we are
    """
    parser = IntentParser()
    intent = parser.parse(request.text)

    return {
        "intent": intent.to_dict(),
        "raw_input": intent.raw_input,
        "engine": ENGINE,
    }


@app.get("/voice/patterns")
async def list_patterns(domain: Optional[str] = None):
    """
    List available app patterns.

    These are pre-built templates that Newton can deploy instantly:
    - calculator_basic: Simple verified arithmetic
    - calculator_financial: Compound interest with proofs
    - lesson_planner: NES-compliant lesson plans
    - quiz_builder: Fair grading verification
    - expense_tracker: Audit trail tracking
    - And more...
    """
    patterns = voice_interface.patterns_list(domain)
    return {
        "patterns": patterns,
        "count": len(patterns),
        "engine": ENGINE,
    }


@app.post("/voice/patterns/search")
async def search_patterns(request: PatternSearchRequest):
    """Search for app patterns matching your needs."""
    library = PatternLibrary()
    patterns = library.search_patterns(request.query, request.limit or 5)

    return {
        "patterns": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "domain": p.domain.value,
                "keywords": p.keywords,
                "example_prompts": p.example_prompts,
            }
            for p in patterns
        ],
        "query": request.query,
        "engine": ENGINE,
    }


@app.get("/voice/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get details about a specific app pattern."""
    library = PatternLibrary()
    pattern = library.get_pattern(pattern_id)

    if not pattern:
        raise HTTPException(
            status_code=404, detail=f"Pattern '{pattern_id}' not found"
        )

    return {
        "pattern": {
            "id": pattern.id,
            "name": pattern.name,
            "description": pattern.description,
            "domain": pattern.domain.value,
            "keywords": pattern.keywords,
            "cdl_template": pattern.cdl_template,
            "interface_template": pattern.interface_template,
            "example_prompts": pattern.example_prompts,
        },
        "engine": ENGINE,
    }


@app.get("/voice/session/{session_id}")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    history = voice_interface.get_session_history(session_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found or expired",
        )

    return {
        "session_id": session_id,
        "turns": history,
        "count": len(history),
        "engine": ENGINE,
    }


@app.get("/voice/demo")
async def voice_demo():
    """
    MOAD Demo Scenarios - Mother Of All Demos

    Returns example scenarios that demonstrate Newton's voice interface.
    """
    return {
        "title": "Mother Of All Demos - Newton Voice Interface",
        "tagline": "Easy now with Newton. He has so much power. Think speaking to your computer.",
        "scenarios": [
            {
                "name": "Financial Calculator",
                "description": "Build a verified financial calculator in 30 seconds",
                "example_query": "Build a financial calculator that proves its math is correct",
                "expected_result": "Deployed calculator with cryptographic verification",
                "time_estimate": "30 seconds",
            },
            {
                "name": "Education Platform",
                "description": "Create a TEKS-aligned lesson planner",
                "example_query": "Create a lesson planner for 5th grade math on fractions",
                "expected_result": "50-minute NES lesson plan with TEKS alignment",
                "time_estimate": "30 seconds",
            },
            {
                "name": "Content Safety",
                "description": "Add Forge content verification",
                "example_query": "Add content safety verification so it can't show inappropriate material",
                "expected_result": "Content safety constraints applied",
                "time_estimate": "instant",
            },
            {
                "name": "Audit Trail",
                "description": "Show immutable audit trail",
                "example_query": "Show me the audit trail of everything I just built",
                "expected_result": "Merkle-anchored ledger of all operations",
                "time_estimate": "instant",
            },
            {
                "name": "Inventory Tracker",
                "description": "Build verified inventory management",
                "example_query": "Build a restaurant inventory tracker with verification that nobody can fake the numbers",
                "expected_result": "Inventory app with tamper-proof audit trail",
                "time_estimate": "30 seconds",
            },
        ],
        "key_points": [
            "Every computation is verified before execution",
            "Immutable audit trail of all operations",
            "Cryptographic proofs for external verification",
            "Sub-millisecond constraint checking",
            "No hallucinations - constraints prevent invalid states",
        ],
        "try_it": {
            "endpoint": "/voice/ask",
            "method": "POST",
            "example_body": {"query": "Build me a calculator", "session_id": None},
        },
        "engine": ENGINE,
    }
