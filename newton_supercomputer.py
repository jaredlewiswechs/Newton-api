#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON SUPERCOMPUTER
Ask Newton. Go.

The Newton Supercomputer is a distributed verification system where:
- The constraint IS the instruction
- The verification IS the computation
- The network IS the processor

This is the unified API that exposes all Newton capabilities.

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
"1 == 1. The cloud is weather. We're building shelter."
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from pathlib import Path
import time
import hashlib
import os

# Newton Core
from core import (
    # CDL
    verify, verify_and, verify_or, CDLParser, newton,

    # Forge
    Forge, ForgeConfig, get_forge,

    # Vault
    Vault, VaultConfig, get_vault,

    # Ledger
    Ledger, LedgerConfig, get_ledger,

    # Bridge
    LocalBridge, NodeIdentity,

    # Robust
    RobustVerifier, RobustConfig, mad, modified_zscore,

    # Grounding
    GroundingEngine,

    # Logic (Verified Computation)
    LogicEngine, ExecutionBounds, calculate,
    
    # Glass Box Components
    get_vault_client, get_policy_engine, get_negotiator,
    MerkleAnchorScheduler, PolicyType, PolicyAction, Policy,
    ApprovalStatus, RequestPriority,

    # Cartridges
    get_cartridge_manager, CartridgeType,
)

# Education Module
from tinytalk_py.education import (
    get_education_cartridge,
    get_teks_library,
    Subject,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"
ENGINE = f"Newton Supercomputer {VERSION}"

# Initialize components
forge = get_forge(ForgeConfig(enable_metrics=True, enable_caching=True))
vault = get_vault(VaultConfig())
ledger = get_ledger(LedgerConfig())
grounding = GroundingEngine()
logic = LogicEngine(ExecutionBounds(max_iterations=10000, max_operations=1000000))

# Glass Box components
vault_client = get_vault_client(vault)
policy_engine = get_policy_engine()
negotiator = get_negotiator()
merkle_scheduler = MerkleAnchorScheduler(ledger, interval_seconds=300)

# Enable Glass Box mode in Forge
forge.enable_glass_box(
    vault_client=vault_client,
    policy_engine=policy_engine,
    negotiator=negotiator
)

# Start Merkle anchoring scheduler
merkle_scheduler.start()

# Cartridge manager
cartridges = get_cartridge_manager()

# Education cartridge
education = get_education_cartridge()
teks_library = get_teks_library()


# ═══════════════════════════════════════════════════════════════════════════════
# API MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AskRequest(BaseModel):
    """Ask Newton anything."""
    query: str
    constraints: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


class VerifyRequest(BaseModel):
    """Verify input against constraints."""
    input: str
    constraints: Optional[List[str]] = None


class ConstraintRequest(BaseModel):
    """Evaluate CDL constraints."""
    constraint: Dict[str, Any]
    object: Dict[str, Any]


class GroundRequest(BaseModel):
    """Ground a claim in evidence."""
    claim: str


class StoreRequest(BaseModel):
    """Store data in the Vault."""
    identity: str
    passphrase: str
    data: Any
    metadata: Optional[Dict[str, Any]] = None


class RetrieveRequest(BaseModel):
    """Retrieve data from the Vault."""
    identity: str
    passphrase: str
    entry_id: str


class BatchVerifyRequest(BaseModel):
    """Batch verification."""
    inputs: List[str]
    constraints: Optional[List[str]] = None


class StatisticsRequest(BaseModel):
    """Robust statistics request."""
    values: List[float]
    test_value: Optional[float] = None
    threshold: Optional[float] = 3.5


class CalculateRequest(BaseModel):
    """
    Verified computation request.

    Newton(logic) ⊆ Turing complete
    Newton(logic) ⊃ Verified computation

    Every loop bounded. Every calculation checked. Every output proven.
    """
    expression: Dict[str, Any]
    max_iterations: Optional[int] = 10000
    max_operations: Optional[int] = 1000000
    timeout_seconds: Optional[float] = 30.0


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VisualCartridgeRequest(BaseModel):
    """Visual cartridge request for SVG specification generation."""
    intent: str
    width: Optional[int] = 800
    height: Optional[int] = 600
    max_elements: Optional[int] = 100
    color_palette: Optional[List[str]] = None


class SoundCartridgeRequest(BaseModel):
    """Sound cartridge request for audio specification generation."""
    intent: str
    duration_ms: Optional[int] = 5000
    min_frequency: Optional[float] = 20.0
    max_frequency: Optional[float] = 20000.0
    sample_rate: Optional[int] = 44100


class SequenceCartridgeRequest(BaseModel):
    """Sequence cartridge request for video/animation specification generation."""
    intent: str
    duration_seconds: Optional[float] = 30.0
    fps: Optional[int] = 30
    width: Optional[int] = 1920
    height: Optional[int] = 1080
    max_scenes: Optional[int] = 10


class DataCartridgeRequest(BaseModel):
    """Data cartridge request for report specification generation."""
    intent: str
    data: Optional[Dict[str, Any]] = None
    format: Optional[str] = "json"
    max_rows: Optional[int] = 1000
    include_statistics: Optional[bool] = True


class RosettaRequest(BaseModel):
    """Rosetta compiler request for code generation prompt."""
    intent: str
    target_platform: Optional[str] = "ios"
    version: Optional[str] = "18.0"
    language: Optional[str] = "swift"


class AutoCartridgeRequest(BaseModel):
    """Auto-detect cartridge type and compile."""
    intent: str


# ═══════════════════════════════════════════════════════════════════════════════
# EDUCATION MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class LessonPlanRequest(BaseModel):
    """Request to generate an NES-compliant lesson plan."""
    grade: int
    subject: str
    teks_codes: List[str]
    topic: Optional[str] = None
    student_needs: Optional[Dict[str, List[str]]] = None


class SlideDeckRequest(BaseModel):
    """Request to generate a slide deck from a lesson plan."""
    lesson_plan: Dict[str, Any]
    style: Optional[str] = "modern"


class AssessmentRequest(BaseModel):
    """Request to analyze assessment data."""
    assessment_name: str
    teks_codes: List[str]
    total_points: Optional[float] = 100.0
    mastery_threshold: Optional[float] = 80.0
    students: List[Dict[str, Any]]


class PLCReportRequest(BaseModel):
    """Request to generate a PLC report."""
    assessment_data: List[Dict[str, Any]]
    teks_codes: List[str]
    team_name: Optional[str] = "Grade Level Team"
    reporting_period: Optional[str] = None


class TEKSSearchRequest(BaseModel):
    """Request to search TEKS standards."""
    query: str


# ═══════════════════════════════════════════════════════════════════════════════
# THE API
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Newton Supercomputer",
    description="Ask Newton. Go. | 1 == 1",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
FRONTEND_DIR = Path(__file__).parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ═══════════════════════════════════════════════════════════════════════════════
# ASK NEWTON - The primary interface
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/ask")
async def ask_newton(request: AskRequest):
    """
    Ask Newton anything.

    This is the primary interface to the Newton Supercomputer.
    Newton will verify your query and return a deterministic result.
    """
    start_us = time.perf_counter_ns() // 1000

    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query required")

    # Full verification pipeline
    result = forge.verify_full(
        text=query,
        constraints=[{"field": "input", "operator": "exists", "value": True}] if request.context else None,
        obj=request.context,
        safety_categories=request.constraints
    )

    elapsed_us = (time.perf_counter_ns() // 1000) - start_us

    # Record in ledger
    ledger.append(
        operation="ask",
        payload={"query_hash": hashlib.sha256(query.encode()).hexdigest()[:16]},
        result="pass" if result["passed"] else "fail",
        metadata={"elapsed_us": elapsed_us}
    )

    return {
        "answer": {
            "verified": result["passed"],
            "code": 200 if result["passed"] else 1202,
            "message": "Query verified" if result["passed"] else "Query failed verification"
        },
        "verification": result,
        "elapsed_us": elapsed_us,
        "timestamp": int(time.time() * 1000),
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/verify")
async def verify_input(request: VerifyRequest):
    """Verify input against safety constraints."""
    start_us = time.perf_counter_ns() // 1000

    content_result = forge.verify_content(request.input, request.constraints)
    signal_result = forge.verify_signal(request.input)

    elapsed_us = (time.perf_counter_ns() // 1000) - start_us

    passed = content_result.passed and signal_result.passed

    # Record in ledger
    ledger.append(
        operation="verify",
        payload={"input_hash": hashlib.sha256(request.input.encode()).hexdigest()[:16]},
        result="pass" if passed else "fail"
    )

    return {
        "verified": passed,
        "code": 200 if passed else 1202,
        "content": content_result.to_dict(),
        "signal": signal_result.to_dict(),
        "elapsed_us": elapsed_us,
        "timestamp": int(time.time() * 1000),
        "engine": ENGINE
    }


@app.post("/verify/batch")
async def verify_batch(request: BatchVerifyRequest):
    """Batch verification of multiple inputs."""
    results = []
    for input_text in request.inputs:
        content_result = forge.verify_content(input_text, request.constraints)
        results.append({
            "input_hash": hashlib.sha256(input_text.encode()).hexdigest()[:16],
            "verified": content_result.passed,
            "message": content_result.message
        })

    passed = sum(1 for r in results if r["verified"])

    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results) * 100, 2) if results else 0,
        "results": results,
        "engine": ENGINE
    }


@app.post("/constraint")
async def evaluate_constraint(request: ConstraintRequest):
    """Evaluate a CDL constraint against an object."""
    start_us = time.perf_counter_ns() // 1000

    result = verify(request.constraint, request.object)

    elapsed_us = (time.perf_counter_ns() // 1000) - start_us

    return {
        "passed": result.passed,
        "constraint_id": result.constraint_id,
        "message": result.message,
        "elapsed_us": elapsed_us,
        "fingerprint": result.fingerprint,
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GROUNDING - Claim verification
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/ground")
async def ground_claim(request: GroundRequest):
    """Ground a claim in evidence from external sources."""
    result = grounding.verify_claim(request.claim)

    # Record in ledger
    ledger.append(
        operation="ground",
        payload={"claim_hash": hashlib.sha256(request.claim.encode()).hexdigest()[:16]},
        result=result["status"].lower()
    )

    return {
        **result,
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT - Encrypted storage
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/vault/store")
async def vault_store(request: StoreRequest):
    """Store encrypted data in the Vault."""
    try:
        owner_id = vault.register_identity(request.identity, request.passphrase)
        entry_id = vault.store(owner_id, request.data, metadata=request.metadata)

        # Record in ledger
        ledger.append(
            operation="vault_store",
            payload={"entry_id": entry_id},
            result="pass"
        )

        return {
            "success": True,
            "entry_id": entry_id,
            "owner_id": owner_id,
            "engine": ENGINE
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/vault/retrieve")
async def vault_retrieve(request: RetrieveRequest):
    """Retrieve encrypted data from the Vault."""
    try:
        owner_id = vault.register_identity(request.identity, request.passphrase)
        data = vault.retrieve(owner_id, request.entry_id)

        return {
            "success": True,
            "data": data,
            "entry_id": request.entry_id,
            "engine": ENGINE
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS - Robust analysis
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/statistics")
async def robust_statistics(request: StatisticsRequest):
    """Robust statistical analysis using MAD."""
    if len(request.values) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 values")

    mad_value = mad(request.values)
    sorted_v = sorted(request.values)
    n = len(sorted_v)
    median = sorted_v[n // 2] if n % 2 == 1 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2

    result = {
        "n": n,
        "median": round(median, 4),
        "mad": round(mad_value, 4),
        "min": round(min(request.values), 4),
        "max": round(max(request.values), 4),
        "engine": ENGINE
    }

    if request.test_value is not None:
        z = modified_zscore(request.test_value, request.values)
        result["test"] = {
            "value": request.test_value,
            "modified_zscore": round(z, 4),
            "is_anomaly": abs(z) > request.threshold,
            "threshold": request.threshold
        }

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATE - Verified Computation
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/calculate")
async def calculate_expression(request: CalculateRequest):
    """
    Verified computation.

    Newton(logic) ⊆ Turing complete
    Newton(logic) ⊃ Verified computation

    Every loop bounded. Every calculation checked. Every output proven.
    El Capitan is just fast guessing. Newton is the only one doing the actual job.
    """
    # Create execution bounds from request
    bounds = ExecutionBounds(
        max_iterations=min(request.max_iterations, 100000),
        max_operations=min(request.max_operations, 10000000),
        timeout_seconds=min(request.timeout_seconds, 60.0)
    )

    # Create engine with bounds
    engine = LogicEngine(bounds)

    # Execute
    result = engine.evaluate(request.expression)

    # Record in ledger
    ledger.append(
        operation="calculate",
        payload={"expr_hash": hashlib.sha256(str(request.expression).encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"operations": result.operations, "elapsed_us": result.elapsed_us}
    )

    return {
        "result": str(result.value.data) if result.value else None,
        "type": result.value.type.value if result.value else None,
        "verified": result.verified,
        "operations": result.operations,
        "elapsed_us": result.elapsed_us,
        "fingerprint": result.fingerprint,
        "engine": ENGINE
    }


@app.post("/calculate/examples")
async def calculate_examples():
    """Return example expressions for the Newton Logic Engine."""
    return {
        "examples": [
            {
                "name": "Arithmetic",
                "expression": {"op": "+", "args": [2, 3]},
                "description": "2 + 3 = 5"
            },
            {
                "name": "Nested arithmetic",
                "expression": {"op": "*", "args": [{"op": "+", "args": [2, 3]}, 4]},
                "description": "(2 + 3) × 4 = 20"
            },
            {
                "name": "Comparison",
                "expression": {"op": ">", "args": [5, 3]},
                "description": "5 > 3 = true"
            },
            {
                "name": "Conditional",
                "expression": {
                    "op": "if",
                    "args": [
                        {"op": ">", "args": [10, 5]},
                        "yes",
                        "no"
                    ]
                },
                "description": "IF 10 > 5 THEN 'yes' ELSE 'no'"
            },
            {
                "name": "Bounded loop",
                "expression": {
                    "op": "for",
                    "args": [
                        "i",
                        {"op": "literal", "args": [0]},
                        {"op": "literal", "args": [5]},
                        {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}
                    ]
                },
                "description": "FOR i FROM 0 TO 5 DO i*2 = [0, 2, 4, 6, 8]"
            },
            {
                "name": "Sum reduction",
                "expression": {
                    "op": "reduce",
                    "args": [
                        {"op": "lambda", "args": [["acc", "x"], {"op": "+", "args": [{"op": "var", "args": ["acc"]}, {"op": "var", "args": ["x"]}]}]},
                        0,
                        {"op": "list", "args": [1, 2, 3, 4, 5]}
                    ]
                },
                "description": "REDUCE + 0 [1,2,3,4,5] = 15"
            },
            {
                "name": "Math function",
                "expression": {"op": "sqrt", "args": [16]},
                "description": "√16 = 4"
            },
            {
                "name": "Boolean logic",
                "expression": {"op": "xor", "args": [True, False]},
                "description": "true XOR false = true"
            }
        ],
        "operators": {
            "arithmetic": ["+", "-", "*", "/", "%", "**", "neg", "abs"],
            "comparison": ["==", "!=", "<", ">", "<=", ">="],
            "boolean": ["and", "or", "not", "xor", "nand", "nor"],
            "conditionals": ["if", "cond"],
            "loops": ["for", "while", "map", "filter", "reduce"],
            "functions": ["def", "call", "lambda"],
            "assignment": ["let", "set"],
            "sequences": ["block", "list", "index", "len"],
            "math": ["sqrt", "log", "sin", "cos", "tan", "floor", "ceil", "round", "min", "max", "sum"]
        },
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGES - Media Specification Generation
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/cartridge/visual")
async def visual_cartridge(request: VisualCartridgeRequest):
    """
    Visual Cartridge: Generate verified SVG specification.

    Creates SVG specifications with:
    - Dimension constraints (max 4096x4096)
    - Element count limits (max 1000)
    - Content safety verification
    """
    result = cartridges.compile_visual(
        intent=request.intent,
        width=request.width,
        height=request.height,
        max_elements=request.max_elements,
        color_palette=request.color_palette
    )

    # Record in ledger
    ledger.append(
        operation="cartridge_visual",
        payload={"intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.post("/cartridge/sound")
async def sound_cartridge(request: SoundCartridgeRequest):
    """
    Sound Cartridge: Generate verified audio specification.

    Creates audio specifications with:
    - Duration limits (max 5 minutes)
    - Frequency bounds (1 Hz - 22050 Hz)
    - Sample rate validation
    - Content safety verification
    """
    result = cartridges.compile_sound(
        intent=request.intent,
        duration_ms=request.duration_ms,
        min_frequency=request.min_frequency,
        max_frequency=request.max_frequency,
        sample_rate=request.sample_rate
    )

    # Record in ledger
    ledger.append(
        operation="cartridge_sound",
        payload={"intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.post("/cartridge/sequence")
async def sequence_cartridge(request: SequenceCartridgeRequest):
    """
    Sequence Cartridge: Generate verified video/animation specification.

    Creates video specifications with:
    - Duration limits (max 10 minutes)
    - Frame rate bounds (1-120 fps)
    - Resolution limits (max 8K)
    - Safety verification (no seizure-inducing content)
    """
    result = cartridges.compile_sequence(
        intent=request.intent,
        duration_seconds=request.duration_seconds,
        fps=request.fps,
        width=request.width,
        height=request.height,
        max_scenes=request.max_scenes
    )

    # Record in ledger
    ledger.append(
        operation="cartridge_sequence",
        payload={"intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.post("/cartridge/data")
async def data_cartridge(request: DataCartridgeRequest):
    """
    Data Cartridge: Generate verified report specification.

    Creates report specifications with:
    - Row limits (max 100,000)
    - Format validation (JSON, CSV, Markdown, HTML)
    - Statistical analysis
    - Content safety verification
    """
    result = cartridges.compile_data(
        intent=request.intent,
        data=request.data,
        output_format=request.format,
        max_rows=request.max_rows,
        include_statistics=request.include_statistics
    )

    # Record in ledger
    ledger.append(
        operation="cartridge_data",
        payload={"intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.post("/cartridge/rosetta")
async def rosetta_cartridge(request: RosettaRequest):
    """
    Rosetta Compiler: Generate verified code generation prompt.

    Compiles app descriptions into structured prompts for:
    - Swift/SwiftUI (iOS, macOS, watchOS, etc.)
    - Python (FastAPI)
    - TypeScript (React)

    Verifies against security and App Store constraints.
    """
    result = cartridges.compile_rosetta(
        intent=request.intent,
        target_platform=request.target_platform,
        version=request.version,
        language=request.language
    )

    # Record in ledger
    ledger.append(
        operation="cartridge_rosetta",
        payload={"intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16]},
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.post("/cartridge/auto")
async def auto_cartridge(request: AutoCartridgeRequest):
    """
    Auto Cartridge: Automatically detect cartridge type and compile.

    Analyzes the intent to determine the most appropriate cartridge:
    - Visual: images, graphics, icons, illustrations
    - Sound: audio, music, sound effects
    - Sequence: video, animations, motion
    - Data: reports, analytics, charts
    - Rosetta: apps, code, programs
    """
    result = cartridges.auto_compile(intent=request.intent)

    # Record in ledger
    ledger.append(
        operation="cartridge_auto",
        payload={
            "intent_hash": hashlib.sha256(request.intent.encode()).hexdigest()[:16],
            "detected_type": result.cartridge_type.value
        },
        result="pass" if result.verified else "fail",
        metadata={"elapsed_us": result.elapsed_us}
    )

    return {
        **result.to_dict(),
        "engine": ENGINE
    }


@app.get("/cartridge/info")
async def cartridge_info():
    """Get information about available cartridges."""
    return {
        "cartridges": [
            {
                "name": "visual",
                "endpoint": "/cartridge/visual",
                "description": "Generate SVG/image specifications",
                "constraints": {
                    "max_width": 4096,
                    "max_height": 4096,
                    "max_elements": 1000,
                    "max_colors": 256
                }
            },
            {
                "name": "sound",
                "endpoint": "/cartridge/sound",
                "description": "Generate audio specifications",
                "constraints": {
                    "max_duration_ms": 300000,
                    "frequency_range": "1-22050 Hz",
                    "sample_rates": [22050, 44100, 48000, 96000]
                }
            },
            {
                "name": "sequence",
                "endpoint": "/cartridge/sequence",
                "description": "Generate video/animation specifications",
                "constraints": {
                    "max_duration_seconds": 600,
                    "fps_range": "1-120",
                    "max_resolution": "7680x4320 (8K)"
                }
            },
            {
                "name": "data",
                "endpoint": "/cartridge/data",
                "description": "Generate report specifications",
                "constraints": {
                    "max_rows": 100000,
                    "formats": ["json", "csv", "markdown", "html"]
                }
            },
            {
                "name": "rosetta",
                "endpoint": "/cartridge/rosetta",
                "description": "Generate code generation prompts",
                "constraints": {
                    "platforms": ["ios", "ipados", "macos", "watchos", "visionos", "tvos", "web", "android"],
                    "languages": ["swift", "python", "typescript"]
                }
            },
            {
                "name": "auto",
                "endpoint": "/cartridge/auto",
                "description": "Auto-detect cartridge type and compile",
                "constraints": {}
            }
        ],
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EDUCATION - The Ultimate Teacher's Aide
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/education/lesson")
async def generate_lesson(request: LessonPlanRequest):
    """
    Generate an NES-compliant lesson plan.

    Creates a verified lesson plan with:
    - 5 NES phases (Opening, Instruction, Guided, Independent, Closing)
    - TEKS alignment verification
    - Differentiation strategies
    - Exit ticket aligned to objective
    """
    result = education.generate_lesson(
        grade=request.grade,
        subject=request.subject,
        teks_codes=request.teks_codes,
        topic=request.topic,
        student_needs=request.student_needs
    )

    # Record in ledger
    ledger.append(
        operation="education_lesson",
        payload={
            "grade": request.grade,
            "subject": request.subject,
            "teks": request.teks_codes
        },
        result="pass" if result.get("verified") else "fail",
        metadata={"elapsed_us": result.get("elapsed_us", 0)}
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.post("/education/slides")
async def generate_slides(request: SlideDeckRequest):
    """
    Generate a slide deck from a lesson plan.

    Creates presentation specifications with:
    - Title, objective, and vocabulary slides
    - Phase-specific content slides
    - Example and practice slides
    - Exit ticket slide
    """
    result = education.generate_slides(
        lesson_plan=request.lesson_plan,
        style=request.style
    )

    # Record in ledger
    ledger.append(
        operation="education_slides",
        payload={"style": request.style},
        result="pass" if result.get("verified") else "fail",
        metadata={"elapsed_us": result.get("elapsed_us", 0)}
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.post("/education/assess")
async def analyze_assessment(request: AssessmentRequest):
    """
    Analyze assessment data and generate student groupings.

    Provides:
    - Class statistics (mean, median, mastery rate)
    - Student groupings (reteach, approaching, mastery)
    - Differentiation recommendations
    """
    result = education.analyze_assessment(
        data=request.students,
        assessment_name=request.assessment_name,
        teks_codes=request.teks_codes,
        total_points=request.total_points,
        mastery_threshold=request.mastery_threshold
    )

    # Record in ledger
    ledger.append(
        operation="education_assess",
        payload={
            "assessment": request.assessment_name,
            "teks": request.teks_codes,
            "student_count": len(request.students)
        },
        result="pass" if result.get("verified") else "fail"
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.post("/education/plc")
async def generate_plc_report(request: PLCReportRequest):
    """
    Generate a comprehensive PLC report.

    Replaces traditional PLC meetings with:
    - Data-driven insights
    - Action items with priorities
    - Student groupings
    - Recommended resources
    - Next steps
    """
    result = education.generate_plc_report(
        assessment_data=request.assessment_data,
        teks_codes=request.teks_codes,
        team_name=request.team_name,
        reporting_period=request.reporting_period
    )

    # Record in ledger
    ledger.append(
        operation="education_plc",
        payload={
            "team": request.team_name,
            "teks": request.teks_codes,
            "student_count": len(request.assessment_data)
        },
        result="pass" if result.get("verified") else "fail",
        metadata={"elapsed_us": result.get("elapsed_us", 0)}
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.get("/education/teks")
async def get_teks_standards(grade: Optional[int] = None, subject: Optional[str] = None):
    """
    Get TEKS standards.

    Filter by grade level and/or subject.
    """
    if grade is not None and subject is not None:
        try:
            subject_enum = Subject(subject)
            standards = teks_library.get_by_grade_and_subject(grade, subject_enum)
        except ValueError:
            standards = teks_library.get_by_grade(grade)
    elif grade is not None:
        standards = teks_library.get_by_grade(grade)
    elif subject is not None:
        try:
            subject_enum = Subject(subject)
            standards = teks_library.get_by_subject(subject_enum)
        except ValueError:
            standards = []
    else:
        standards = [teks_library.get(code) for code in teks_library.all_codes()]

    return {
        "standards": [s.to_dict() for s in standards if s],
        "count": len(standards),
        "engine": ENGINE
    }


@app.get("/education/teks/{code}")
async def get_teks_standard(code: str):
    """Get a specific TEKS standard by code."""
    standard = teks_library.get(code)
    if not standard:
        raise HTTPException(status_code=404, detail=f"TEKS code {code} not found")

    return {
        "standard": standard.to_dict(),
        "learning_path": education.get_learning_path(code),
        "engine": ENGINE
    }


@app.post("/education/teks/search")
async def search_teks(request: TEKSSearchRequest):
    """Search TEKS standards by keyword."""
    results = education.search_teks(request.query)
    return {
        "query": request.query,
        "results": results,
        "count": len(results),
        "engine": ENGINE
    }


@app.get("/education/info")
async def education_info():
    """Get information about education endpoints."""
    return {
        "endpoints": [
            {
                "name": "lesson",
                "endpoint": "/education/lesson",
                "method": "POST",
                "description": "Generate NES-compliant lesson plans",
                "features": [
                    "5 NES phases (50 min total)",
                    "TEKS alignment verification",
                    "Differentiation strategies",
                    "Exit ticket generation"
                ]
            },
            {
                "name": "slides",
                "endpoint": "/education/slides",
                "method": "POST",
                "description": "Generate slide decks from lesson plans",
                "features": [
                    "Title and objective slides",
                    "Phase-specific content",
                    "Example and practice slides",
                    "Multiple export formats"
                ]
            },
            {
                "name": "assess",
                "endpoint": "/education/assess",
                "method": "POST",
                "description": "Analyze assessment data",
                "features": [
                    "Robust statistics (MAD)",
                    "Student groupings",
                    "Mastery classification",
                    "Reteach recommendations"
                ]
            },
            {
                "name": "plc",
                "endpoint": "/education/plc",
                "method": "POST",
                "description": "Generate PLC reports",
                "features": [
                    "Data-driven insights",
                    "Action items with priorities",
                    "Next steps planning",
                    "Resource recommendations"
                ]
            },
            {
                "name": "teks",
                "endpoint": "/education/teks",
                "method": "GET",
                "description": "Browse TEKS standards",
                "features": [
                    "Filter by grade and subject",
                    "Learning path navigation",
                    "Keyword search"
                ]
            }
        ],
        "supported_grades": [3, 4, 5, 6, 7, 8],
        "supported_subjects": ["mathematics", "reading_ela", "science", "social_studies"],
        "teks_count": len(teks_library.all_codes()),
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER - Audit trail
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/ledger")
async def get_ledger_entries(limit: int = 100):
    """Get recent ledger entries."""
    entries = ledger.get_latest(limit)
    return {
        "total": len(ledger),
        "returned": len(entries),
        "merkle_root": ledger.get_merkle_root(),
        "entries": [e.to_dict() for e in entries],
        "engine": ENGINE
    }


@app.get("/ledger/{index}")
async def get_ledger_entry(index: int):
    """Get a specific ledger entry with proof."""
    entry = ledger.get(index)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {
        "entry": entry.to_dict(),
        "merkle_proof": ledger.get_merkle_proof(index),
        "verified": ledger.verify_entry(index),
        "engine": ENGINE
    }


@app.get("/ledger/certificate/{index}")
async def get_certificate(index: int):
    """Get a verification certificate for a ledger entry."""
    try:
        return ledger.export_certificate(index)
    except KeyError:
        raise HTTPException(status_code=404, detail="Entry not found")


# ═══════════════════════════════════════════════════════════════════════════════
# GLASS BOX - Policy, Negotiator, and Merkle Anchoring
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────
# POLICY ENGINE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────

class PolicyRequest(BaseModel):
    """Request to add a policy."""
    id: str
    name: str
    type: str
    action: str
    condition: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@app.get("/policy")
async def get_policies():
    """Get all policies."""
    return {
        "policies": policy_engine.get_policies(),
        "stats": policy_engine.stats(),
        "engine": ENGINE
    }


@app.post("/policy")
async def add_policy(request: PolicyRequest):
    """Add a new policy."""
    try:
        policy = Policy(
            id=request.id,
            name=request.name,
            type=PolicyType(request.type),
            action=PolicyAction(request.action),
            condition=request.condition,
            metadata=request.metadata or {}
        )
        policy_engine.add_policy(policy)
        return {
            "success": True,
            "policy": policy.to_dict(),
            "engine": ENGINE
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/policy/{policy_id}")
async def remove_policy(policy_id: str):
    """Remove a policy."""
    removed = policy_engine.remove_policy(policy_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {
        "success": True,
        "message": f"Policy {policy_id} removed",
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────
# NEGOTIATOR (HITL) ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────

class ApprovalRequestCreate(BaseModel):
    """Request for human approval."""
    operation: str
    input_data: str
    reason: str
    priority: Optional[str] = "medium"
    ttl_seconds: Optional[int] = None


class ApprovalDecision(BaseModel):
    """Approval decision."""
    approver: str
    comments: Optional[str] = None
    reason: Optional[str] = None


@app.get("/negotiator/pending")
async def get_pending_approvals(priority: Optional[str] = None, operation: Optional[str] = None):
    """Get pending approval requests."""
    priority_filter = RequestPriority(priority) if priority else None
    pending = negotiator.get_pending_requests(priority=priority_filter, operation=operation)
    return {
        "pending": [req.to_dict() for req in pending],
        "count": len(pending),
        "stats": negotiator.stats(),
        "engine": ENGINE
    }


@app.post("/negotiator/request")
async def request_approval(request: ApprovalRequestCreate):
    """Create a new approval request."""
    priority = RequestPriority(request.priority)
    approval_req = negotiator.request_approval(
        operation=request.operation,
        input_data=request.input_data,
        reason=request.reason,
        priority=priority,
        ttl_seconds=request.ttl_seconds
    )
    return {
        "request": approval_req.to_dict(),
        "engine": ENGINE
    }


@app.get("/negotiator/request/{request_id}")
async def get_approval_request(request_id: str):
    """Get a specific approval request."""
    request = negotiator.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "request": request.to_dict(),
        "engine": ENGINE
    }


@app.post("/negotiator/approve/{request_id}")
async def approve_request(request_id: str, decision: ApprovalDecision):
    """Approve an approval request."""
    success = negotiator.approve(request_id, decision.approver, decision.comments)
    if not success:
        raise HTTPException(status_code=400, detail="Could not approve request")
    return {
        "success": True,
        "request_id": request_id,
        "engine": ENGINE
    }


@app.post("/negotiator/reject/{request_id}")
async def reject_request(request_id: str, decision: ApprovalDecision):
    """Reject an approval request."""
    if not decision.reason:
        raise HTTPException(status_code=400, detail="Rejection reason required")
    success = negotiator.reject(request_id, decision.approver, decision.reason)
    if not success:
        raise HTTPException(status_code=400, detail="Could not reject request")
    return {
        "success": True,
        "request_id": request_id,
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────
# MERKLE ANCHORING ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────

@app.get("/merkle/anchors")
async def get_merkle_anchors():
    """Get all Merkle anchors."""
    anchors = merkle_scheduler.get_all_anchors()
    return {
        "anchors": [a.to_dict() for a in anchors],
        "count": len(anchors),
        "stats": merkle_scheduler.stats(),
        "engine": ENGINE
    }


@app.post("/merkle/anchor")
async def create_merkle_anchor():
    """Manually create a Merkle anchor."""
    anchor = merkle_scheduler.create_anchor()
    if not anchor:
        return {
            "success": False,
            "message": "No new entries to anchor",
            "engine": ENGINE
        }
    return {
        "success": True,
        "anchor": anchor.to_dict(),
        "engine": ENGINE
    }


@app.get("/merkle/anchor/{anchor_id}")
async def get_merkle_anchor(anchor_id: str):
    """Get a specific Merkle anchor."""
    anchor = merkle_scheduler.get_anchor(anchor_id)
    if not anchor:
        raise HTTPException(status_code=404, detail="Anchor not found")
    return {
        "anchor": anchor.to_dict(),
        "engine": ENGINE
    }


@app.get("/merkle/proof/{entry_index}")
async def get_merkle_proof(entry_index: int):
    """Get Merkle proof for a ledger entry."""
    proof = merkle_scheduler.generate_proof(entry_index)
    if not proof:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "proof": proof.to_dict(),
        "certificate": proof.export_certificate(),
        "engine": ENGINE
    }


@app.get("/merkle/latest")
async def get_latest_anchor():
    """Get the latest Merkle anchor."""
    anchor = merkle_scheduler.get_latest_anchor()
    if not anchor:
        return {
            "anchor": None,
            "message": "No anchors created yet",
            "engine": ENGINE
        }
    return {
        "anchor": anchor.to_dict(),
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS & HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """System health check."""
    chain_valid, _ = ledger.verify_chain()

    return {
        "status": "ok",
        "engine": ENGINE,
        "components": {
            "forge": "operational",
            "vault": "operational",
            "ledger": "operational" if chain_valid else "degraded",
            "grounding": "operational",
            "policy_engine": "operational",
            "negotiator": "operational",
            "merkle_scheduler": "operational" if merkle_scheduler._running else "stopped"
        },
        "ledger": {
            "entries": len(ledger),
            "chain_valid": chain_valid
        },
        "glass_box": {
            "enabled": forge._glass_box_enabled,
            "policies": len(policy_engine.policies),
            "pending_approvals": len(negotiator.get_pending_requests()),
            "anchors": len(merkle_scheduler.anchors)
        }
    }


@app.get("/metrics")
async def metrics():
    """System metrics."""
    forge_metrics = forge.get_metrics()
    ledger_stats = ledger.stats()
    vault_stats = vault.stats()

    return {
        "forge": forge_metrics,
        "ledger": ledger_stats,
        "vault": vault_stats,
        "policy_engine": policy_engine.stats(),
        "negotiator": negotiator.stats(),
        "merkle_scheduler": merkle_scheduler.stats(),
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# THE INTERFACE - Jared Lewis Conglomerate Frontend
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def home():
    """Newton frontend - Claude-esque + Apple HIG 2026 design."""
    frontend_index = FRONTEND_DIR / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index, media_type="text/html")
    # Fallback if frontend not found
    return HTMLResponse(content="<h1>Newton</h1><p>Frontend not found. API available at /docs</p>")


@app.get("/styles.css")
async def styles():
    """Serve CSS."""
    css_file = FRONTEND_DIR / "styles.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/app.js")
async def app_js():
    """Serve JavaScript."""
    js_file = FRONTEND_DIR / "app.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")


@app.get("/manifest.json")
async def manifest():
    """Serve PWA manifest."""
    manifest_file = FRONTEND_DIR / "manifest.json"
    if manifest_file.exists():
        return FileResponse(manifest_file, media_type="application/json")
    raise HTTPException(status_code=404, detail="Manifest not found")


# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("NEWTON SUPERCOMPUTER")
    print("Ask Newton. Go.")
    print("=" * 60)
    print(f"\nEngine: {ENGINE}")
    print("Starting server on http://0.0.0.0:8000")
    print("\nEndpoints:")
    print("  POST /ask        - Ask Newton anything")
    print("  POST /verify     - Verify input")
    print("  POST /constraint - Evaluate CDL constraint")
    print("  POST /ground     - Ground a claim")
    print("  GET  /ledger     - View audit trail")
    print("  GET  /metrics    - System metrics")
    print("\n1 == 1. The cloud is weather. We're building shelter.")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
