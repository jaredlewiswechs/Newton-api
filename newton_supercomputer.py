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

    # Gumroad (Payments)
    get_gumroad_service, GumroadConfig,
)

# Education Module
from tinytalk_py.education import (
    get_education_cartridge,
    get_teks_library,
    Subject,
)

# Teacher's Aide Database
from tinytalk_py.teachers_aide_db import (
    get_teachers_aide_db,
    Student,
    Classroom,
    Assessment,
    InterventionPlan,
    MasteryLevel,
    AccommodationType,
)

# Extended TEKS Database
from tinytalk_py.teks_database import get_extended_teks_library

# Interface Builder
from tinytalk_py.interface_builder import (
    get_interface_builder,
    InterfaceType,
    LayoutPattern,
    ComponentType,
)

# Voice Interface (MOAD - Mother Of All Demos)
from core.voice_interface import (
    get_voice_interface,
    get_streaming_interface,
    IntentType,
    DomainCategory,
)

# Constraint Extractor - From Fuzzy to Formal
from core.constraint_extractor import (
    extract_constraints,
    verify_plan,
    get_extractor,
    ConstraintCategory,
    ConstraintStrength,
)

# Chatbot Compiler - The Better ChatGPT
from core.chatbot_compiler import (
    ChatbotCompiler,
    get_chatbot_compiler,
    get_chatbot_governor,
    compile_request,
    classify_only,
    RequestType,
    RiskLevel,
    CompilerDecision,
)

# parcCloud Authentication Gateway
from parccloud.auth import (
    signup as parccloud_signup,
    signin as parccloud_signin,
    admin_auth as parccloud_admin,
    verify_token as parccloud_verify_token,
    logout as parccloud_logout,
    get_user_count as parccloud_user_count,
    SignUpRequest,
    SignInRequest,
    AdminAuthRequest,
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

# Teacher's Aide Database - Easy data management for teachers
teachers_db = get_teachers_aide_db()
extended_teks = get_extended_teks_library()

# Interface Builder - Verified UI Generation
interface_builder = get_interface_builder()

# Gumroad - Payment & License Management
gumroad = get_gumroad_service()

# Voice Interface (MOAD - Mother Of All Demos)
voice_interface = get_voice_interface()
streaming_voice = get_streaming_interface()

# Chatbot Compiler - The Better ChatGPT
# "LLMs are great generators. They are terrible governors."
chatbot_compiler = get_chatbot_compiler()
chatbot_governor = get_chatbot_governor()


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
# CONSTRAINT EXTRACTION MODELS - From Fuzzy to Formal
# ═══════════════════════════════════════════════════════════════════════════════

class ExtractConstraintsRequest(BaseModel):
    """
    Extract formal constraints from natural language.

    "You're parsing it like a CONSTRAINT EXTRACTOR, not a language model."

    Example input:
        "I want to take my 4 friends to Costa Rica for 2 weeks in December.
         Nothing too expensive, but it should be safe and fun.
         We all want at least 3 activities. Oh, and we're not night people."

    Output: Formal CDL constraints + TinyTalk specification
    """
    text: str
    include_tinytalk: Optional[bool] = True
    include_cdl: Optional[bool] = True


class VerifyPlanRequest(BaseModel):
    """
    Verify a plan against extracted constraints.

    Not "I think this is good" but "This IS verified."
    """
    plan: Dict[str, Any]
    extraction_id: Optional[str] = None
    text: Optional[str] = None  # Alternative: extract constraints from text


# ═══════════════════════════════════════════════════════════════════════════════
# CHATBOT COMPILER MODELS - The Better ChatGPT
# ═══════════════════════════════════════════════════════════════════════════════

class ChatbotCompileRequest(BaseModel):
    """
    Compile user input through the constrained chatbot pipeline.

    The best chatbot is not the one that answers the most -
    it's the one that knows when not to.

    Pipeline:
        User Input → Intent Parsing → Constraint Checking →
        Response Generation (if allowed) → Response Validation → Final Output
    """
    input: str
    context: Optional[Dict[str, Any]] = None


class ChatbotClassifyRequest(BaseModel):
    """
    Classify user input without generating a response.

    Useful for understanding intent before processing.
    """
    input: str


class ChatbotBatchRequest(BaseModel):
    """
    Process multiple inputs through the chatbot compiler.
    """
    inputs: List[str]
    context: Optional[Dict[str, Any]] = None


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
# TEACHER'S AIDE DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AddStudentRequest(BaseModel):
    """Add a new student."""
    first_name: str
    last_name: str
    grade: int
    accommodations: Optional[List[str]] = None
    student_id: Optional[str] = None


class AddStudentsRequest(BaseModel):
    """Add multiple students at once."""
    students: List[AddStudentRequest]


class CreateClassroomRequest(BaseModel):
    """Create a new classroom."""
    name: str
    grade: int
    subject: str
    teacher_name: Optional[str] = ""


class AddStudentToClassRequest(BaseModel):
    """Add student(s) to a classroom."""
    student_ids: List[str]


class CreateAssessmentRequest(BaseModel):
    """Create a new assessment."""
    name: str
    classroom_id: str
    teks_codes: List[str]
    total_points: float
    assessment_type: Optional[str] = "formative"


class EnterScoresRequest(BaseModel):
    """Enter scores for an assessment."""
    scores: Dict[str, float]  # student_id -> points


class QuickScoresRequest(BaseModel):
    """Quick score entry by student name."""
    scores: List[List[Any]]  # [[name, points], ...]


class CreateInterventionRequest(BaseModel):
    """Create an intervention plan."""
    classroom_id: str
    teks_codes: List[str]
    target_group: str
    strategy: str
    student_ids: Optional[List[str]] = None


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE INTERFACE MODELS (MOAD - Mother Of All Demos)
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

# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING - Protect against abuse while allowing 1000s of iPhone users
# ═══════════════════════════════════════════════════════════════════════════════
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """Simple in-memory rate limiter. 100 requests/minute per IP."""
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60

        with self.lock:
            # Clean old requests
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if t > window_start
            ]

            if len(self.requests[client_ip]) >= self.requests_per_minute:
                return False

            self.requests[client_ip].append(now)
            return True

    def get_remaining(self, client_ip: str) -> int:
        now = time.time()
        window_start = now - 60
        with self.lock:
            recent = [t for t in self.requests.get(client_ip, []) if t > window_start]
            return max(0, self.requests_per_minute - len(recent))

rate_limiter = RateLimiter(requests_per_minute=100)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks
    if request.url.path == "/health":
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please wait a minute.",
                "limit": "100 requests per minute"
            },
            headers={"Retry-After": "60"}
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_ip))
    response.headers["X-RateLimit-Limit"] = "100"
    return response

# ═══════════════════════════════════════════════════════════════════════════════
# PARCCLOUD GATEWAY - Optional authentication gate for all routes
# Enable with: PARCCLOUD_GATEWAY_ENABLED=true
# ═══════════════════════════════════════════════════════════════════════════════

PARCCLOUD_GATEWAY_ENABLED = os.environ.get("PARCCLOUD_GATEWAY_ENABLED", "false").lower() == "true"

# Paths that don't require authentication (even when gateway is enabled)
PARCCLOUD_PUBLIC_PATHS = {
    "/login",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}

# Path prefixes that don't require authentication
PARCCLOUD_PUBLIC_PREFIXES = (
    "/parccloud/",
    "/static/",
)

@app.middleware("http")
async def parccloud_gateway_middleware(request: Request, call_next):
    """
    Optional gateway middleware - when enabled, requires parcCloud authentication
    for all protected routes. Unauthenticated requests are redirected to /login.
    """
    # Skip if gateway is disabled
    if not PARCCLOUD_GATEWAY_ENABLED:
        return await call_next(request)

    path = request.url.path

    # Allow public paths
    if path in PARCCLOUD_PUBLIC_PATHS:
        return await call_next(request)

    # Allow public prefixes
    if path.startswith(PARCCLOUD_PUBLIC_PREFIXES):
        return await call_next(request)

    # Check for valid token
    auth_header = request.headers.get("Authorization", "")
    token = None

    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        # Also check cookies for browser sessions
        token = request.cookies.get("parccloud_token")

    if token:
        user = parccloud_verify_token(token)
        if user:
            # Valid token - allow request
            return await call_next(request)

    # No valid token - redirect to login for HTML requests, 401 for API
    accept = request.headers.get("Accept", "")
    if "text/html" in accept:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    else:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Authentication required",
                "message": "Please sign in at /login to access this resource",
                "login_url": "/login"
            }
        )

# Mount static files for all frontends
ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / "frontend"
TEACHERS_DIR = ROOT_DIR / "teachers-aide"
BUILDER_DIR = ROOT_DIR / "interface-builder"
PARCCLOUD_DIR = ROOT_DIR / "parccloud"

# Helper: Find file across multiple possible paths (handles Render's environment)
def find_app_file(app_dir: Path, filename: str = "index.html") -> Optional[Path]:
    """Find a file, trying multiple path resolutions for Render compatibility."""
    import os
    possible_paths = [
        app_dir / filename,
        Path(os.getcwd()) / app_dir.name / filename,
        Path("/opt/render/project/src") / app_dir.name / filename,
    ]
    for path in possible_paths:
        if path.exists():
            return path
    return None

# Helper: Find file across multiple possible paths (handles Render's environment)
def find_app_file(app_dir: Path, filename: str = "index.html") -> Optional[Path]:
    """Find a file, trying multiple path resolutions for Render compatibility."""
    import os
    possible_paths = [
        app_dir / filename,
        Path(os.getcwd()) / app_dir.name / filename,
        Path("/opt/render/project/src") / app_dir.name / filename,
    ]
    for path in possible_paths:
        if path.exists():
            return path
    return None

# Mount static directories
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
if TEACHERS_DIR.exists():
    app.mount("/teachers-aide", StaticFiles(directory=str(TEACHERS_DIR), html=True), name="teachers-aide")
if BUILDER_DIR.exists():
    app.mount("/interface-builder", StaticFiles(directory=str(BUILDER_DIR), html=True), name="interface-builder")

# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON PHONE - Static Frontend Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the Newton Phone home screen"""
    import os

    # Try multiple paths to find index.html
    possible_paths = [
        ROOT_DIR / "index.html",
        Path(os.getcwd()) / "index.html",
        Path("/opt/render/project/src/index.html"),
    ]

    for index_file in possible_paths:
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(), status_code=200)

    # Log debug info if not found
    print(f"[Newton] index.html not found. ROOT_DIR={ROOT_DIR}, CWD={os.getcwd()}")
    if ROOT_DIR.exists():
        print(f"[Newton] Files in ROOT_DIR: {[f.name for f in list(ROOT_DIR.iterdir())[:20]]}")

    # Fallback: Minimal home screen that still works
    fallback_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000;
            color: #fff;
            font-family: -apple-system, system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        h1 { color: #4ecdc4; font-size: 48px; margin-bottom: 20px; }
        .tagline { color: #86868b; margin-bottom: 40px; }
        .apps {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 400px;
        }
        a {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            background: #1a1a1a;
            border-radius: 16px;
            text-decoration: none;
            color: #fff;
            transition: transform 0.2s;
        }
        a:hover { transform: scale(1.05); }
        .icon {
            width: 60px;
            height: 60px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .newton { background: #4ecdc4; color: #000; }
        .teachers { background: #ff3b30; }
        .builder { background: #af52de; }
        .docs { background: #007aff; }
    </style>
</head>
<body>
    <h1>Newton</h1>
    <p class="tagline">The verification layer for AI</p>
    <div class="apps">
        <a href="/app">
            <div class="icon newton">N</div>
            <span>Newton</span>
        </a>
        <a href="/teachers">
            <div class="icon teachers">T</div>
            <span>Teacher's Aide</span>
        </a>
        <a href="/builder">
            <div class="icon builder">B</div>
            <span>Builder</span>
        </a>
        <a href="/docs">
            <div class="icon docs">API</div>
            <span>Docs</span>
        </a>
    </div>
</body>
</html>"""
    return HTMLResponse(content=fallback_html, status_code=200)

@app.get("/app", response_class=HTMLResponse)
async def serve_newton_app():
    """Serve the Newton Supercomputer app"""
    index_file = find_app_file(FRONTEND_DIR)
    if index_file:
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Newton App</h1><p>Not found</p>", status_code=404)

@app.get("/teachers", response_class=HTMLResponse)
async def serve_teachers_aide():
    """Serve Teacher's Aide app"""
    index_file = find_app_file(TEACHERS_DIR)
    if index_file:
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Teacher's Aide</h1><p>Not found</p>", status_code=404)

@app.get("/builder", response_class=HTMLResponse)
async def serve_builder():
    """Serve Interface Builder app"""
    index_file = find_app_file(BUILDER_DIR)
    if index_file:
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Interface Builder</h1><p>Not found</p>", status_code=404)


# ═══════════════════════════════════════════════════════════════════════════════
# PARCCLOUD - Authentication Gateway
# "Like iCloud, but for Newton. The beach before the API."
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
async def serve_parccloud_login():
    """Serve parcCloud login page"""
    index_file = find_app_file(PARCCLOUD_DIR)
    if index_file:
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    return HTMLResponse(content="<h1>parcCloud</h1><p>Login page not found</p>", status_code=404)


@app.post("/parccloud/signup")
async def parccloud_signup_route(request: SignUpRequest):
    """Create a free parcCloud account"""
    result = parccloud_signup(request.name, request.email, request.password)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result.model_dump()


@app.post("/parccloud/signin")
async def parccloud_signin_route(request: SignInRequest):
    """Sign in to parcCloud"""
    result = parccloud_signin(request.email, request.password)
    if not result.success:
        raise HTTPException(status_code=401, detail=result.message)
    return result.model_dump()


@app.post("/parccloud/admin")
async def parccloud_admin_route(request: AdminAuthRequest):
    """Admin access to parcCloud"""
    result = parccloud_admin(request.adminKey, request.adminSecret)
    if not result.success:
        raise HTTPException(status_code=403, detail=result.message)
    return result.model_dump()


@app.get("/parccloud/verify")
async def parccloud_verify_route(request: Request):
    """Verify a parcCloud session token"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    user = parccloud_verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"valid": True, "user": user}


@app.post("/parccloud/logout")
async def parccloud_logout_route(request: Request):
    """Logout from parcCloud (invalidate token)"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    if token and parccloud_logout(token):
        return {"success": True, "message": "Logged out successfully"}
    return {"success": False, "message": "No active session"}


@app.get("/parccloud/stats")
async def parccloud_stats_route():
    """Get parcCloud statistics (public)"""
    return {
        "total_users": parccloud_user_count(),
        "tier": "free",
        "status": "operational"
    }


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
# CONSTRAINT EXTRACTION - From Fuzzy to Formal
# "You're parsing it like a CONSTRAINT EXTRACTOR, not a language model."
# ═══════════════════════════════════════════════════════════════════════════════

# Cache for extractions (so verify_plan can reference by ID)
_extraction_cache: Dict[str, Any] = {}

@app.post("/extract")
async def extract_constraints_endpoint(request: ExtractConstraintsRequest):
    """
    Extract formal constraints from natural language.

    Pipeline: Natural Language → Constraint Extraction → Formal Spec → Verified Output
                  (fuzzy)            (parsing)           (Newton^2)      (deterministic)

    Example:
        Input: "I want to take my 4 friends to Costa Rica for 2 weeks in December.
                Nothing too expensive, but it should be safe and fun."

        Output:
        {
            "constraints": [
                {"field": "group_size", "operator": "eq", "value": 5},
                {"field": "duration_week", "operator": "eq", "value": 2},
                {"field": "cost", "operator": "lt", "value": 0.8},
                {"field": "safety_rating", "operator": "ge", "value": 0.8}
            ],
            "tinytalk": "when(self.group_size == 5, finfr)...",
            "cdl": {...}
        }
    """
    start_us = time.perf_counter_ns() // 1000

    # Extract constraints
    extraction = extract_constraints(request.text)

    # Cache for later verification
    _extraction_cache[extraction.id] = extraction

    elapsed_us = (time.perf_counter_ns() // 1000) - start_us

    # Build response
    response = {
        "id": extraction.id,
        "source_text": extraction.source_text,
        "action": extraction.action,
        "subject": extraction.subject,
        "objects": extraction.objects,
        "constraints": [c.to_dict() for c in extraction.constraints],
        "constraint_count": len(extraction.constraints),
        "all_extractable": extraction.all_extractable,
        "ambiguities": extraction.ambiguities,
        "assumptions": extraction.assumptions,
        "verification": {
            "merkle_root": extraction.merkle_root,
            "signature": extraction.signature,
            "timestamp": extraction.timestamp
        },
        "elapsed_us": elapsed_us,
        "engine": ENGINE
    }

    # Include TinyTalk specification if requested
    if request.include_tinytalk:
        response["tinytalk"] = extraction.to_tinytalk_blueprint("ExtractedPlan")

    # Include CDL specification if requested
    if request.include_cdl:
        response["cdl"] = extraction.to_cdl_spec()

    # Record in ledger
    ledger.append(
        operation="extract_constraints",
        payload={
            "text_hash": hashlib.sha256(request.text.encode()).hexdigest()[:16],
            "constraint_count": len(extraction.constraints)
        },
        result="success"
    )

    return response


@app.post("/extract/verify")
async def verify_plan_endpoint(request: VerifyPlanRequest):
    """
    Verify a plan against extracted constraints.

    Not "I think this is good" but "This IS verified."

    Returns verification certificates for each constraint, proving
    whether the plan satisfies all requirements.
    """
    start_us = time.perf_counter_ns() // 1000

    # Get or create extraction
    extraction = None

    if request.extraction_id and request.extraction_id in _extraction_cache:
        extraction = _extraction_cache[request.extraction_id]
    elif request.text:
        extraction = extract_constraints(request.text)
        _extraction_cache[extraction.id] = extraction
    else:
        raise HTTPException(
            status_code=400,
            detail="Either extraction_id or text must be provided"
        )

    # Verify the plan
    verified_plan = verify_plan(request.plan, extraction)

    elapsed_us = (time.perf_counter_ns() // 1000) - start_us

    # Record in ledger
    ledger.append(
        operation="verify_plan",
        payload={
            "plan_id": verified_plan.id,
            "all_verified": verified_plan.all_verified,
            "certificate_count": len(verified_plan.certificates)
        },
        result="verified" if verified_plan.all_verified else "failed"
    )

    return {
        **verified_plan.to_dict(),
        "elapsed_us": elapsed_us,
        "engine": ENGINE
    }


@app.get("/extract/example")
async def extract_example():
    """
    Show an example of constraint extraction.

    This demonstrates Newton^2's constraint extraction pipeline:
    Natural Language → Constraints → Verified Plan
    """
    example_input = (
        "I want to take my 4 friends to Costa Rica for 2 weeks in December. "
        "Nothing too expensive, but it should be safe and fun. "
        "We all want at least 3 activities. Oh, and we're not night people."
    )

    extraction = extract_constraints(example_input)

    # Example plan that satisfies the constraints
    example_plan = {
        "name": "Costa Rica Adventure",
        "group_size": 5,
        "duration_week": 2,
        "cost": 4500,
        "safety_rating": 0.9,
        "activities": [
            {"name": "Hiking La Fortuna", "end_time": 16},
            {"name": "Zip-lining", "end_time": 15},
            {"name": "Snorkeling", "end_time": 14}
        ],
        "count": 3
    }

    verified = verify_plan(example_plan, extraction)

    return {
        "example_input": example_input,
        "extraction": {
            "id": extraction.id,
            "constraints": [c.to_dict() for c in extraction.constraints],
            "ambiguities": extraction.ambiguities,
            "assumptions": extraction.assumptions
        },
        "example_plan": example_plan,
        "verification": {
            "all_verified": verified.all_verified,
            "certificates": [
                {
                    "constraint": c.constraint_description,
                    "verified": c.verified,
                    "actual": c.actual_value,
                    "expected": c.expected_value
                }
                for c in verified.certificates
            ]
        },
        "message": "This is Newton^2: Not 'I think this is good' but 'This IS verified'",
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHATBOT COMPILER - The Better ChatGPT
# "The best chatbot is not the one that answers the most -
#  it's the one that knows when not to."
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/chatbot/compile")
async def chatbot_compile(request: ChatbotCompileRequest):
    """
    Compile user input through the constrained chatbot pipeline.

    This is NOT a chatbot. This is a compiler for human intent.

    Pipeline:
    1. Parse user input into intent types
    2. Determine what is allowed to be answered
    3. Ask clarifying questions when intent is underspecified
    4. Refuse when constraints are violated
    5. Only generate content that satisfies constraints

    The model does not free-generate text and then "hope it's okay".
    Generation is constrained by law. That's the compiler pass.
    """
    start_time = time.time()

    # Compile through the constrained pipeline
    response = compile_request(
        user_input=request.input,
        context=request.context
    )

    elapsed_us = int((time.time() - start_time) * 1_000_000)

    # Record in ledger
    ledger.append(
        operation="chatbot_compile",
        payload={
            "input_hash": hashlib.sha256(request.input.encode()).hexdigest()[:16],
            "decision": response.decision.value,
            "request_type": response.classification.request_type.value,
            "risk_level": response.classification.risk_level.value
        },
        result="compiled"
    )

    return {
        **response.to_dict(),
        "elapsed_us": elapsed_us,
        "engine": ENGINE,
        "philosophy": "LLMs are great generators. They are terrible governors. This is the governor."
    }


@app.post("/chatbot/classify")
async def chatbot_classify(request: ChatbotClassifyRequest):
    """
    Classify user input without generating a response.

    This is the first compiler pass: type inference for natural language.
    Every user input is classified into exactly one type, with rules
    about what the chatbot is allowed to do.

    Types:
    - question: Factual queries
    - opinion: Subjective matters
    - instruction: Commands, tasks
    - calculation: Math, computation
    - medical_advice: Health guidance (-> DEFER)
    - legal_advice: Law guidance (-> DEFER)
    - financial_advice: Money guidance (-> DEFER)
    - personal_data: PII (-> REFUSE)
    - harmful: Dangerous content (-> REFUSE)
    - unknown: Cannot classify (-> ASK)
    """
    start_time = time.time()

    # Classify only
    classification = classify_only(request.input)

    # Check governance laws
    laws_passed, violated_laws = chatbot_governor.evaluate_all(classification)

    elapsed_us = int((time.time() - start_time) * 1_000_000)

    return {
        "classification": classification.to_dict(),
        "governance": {
            "laws_passed": laws_passed,
            "violated_laws": violated_laws
        },
        "elapsed_us": elapsed_us,
        "engine": ENGINE
    }


@app.post("/chatbot/batch")
async def chatbot_batch(request: ChatbotBatchRequest):
    """
    Process multiple inputs through the chatbot compiler.

    Useful for batch processing or testing multiple scenarios.
    """
    start_time = time.time()

    results = []
    for user_input in request.inputs:
        response = compile_request(
            user_input=user_input,
            context=request.context
        )
        results.append({
            "input": user_input,
            "decision": response.decision.value,
            "request_type": response.classification.request_type.value,
            "risk_level": response.classification.risk_level.value,
            "verified": response.verified,
            "content": response.content,
            "referral": response.referral
        })

    elapsed_us = int((time.time() - start_time) * 1_000_000)

    # Summary statistics
    decisions = {}
    types = {}
    for r in results:
        decisions[r["decision"]] = decisions.get(r["decision"], 0) + 1
        types[r["request_type"]] = types.get(r["request_type"], 0) + 1

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "decisions": decisions,
            "types": types
        },
        "elapsed_us": elapsed_us,
        "engine": ENGINE
    }


@app.get("/chatbot/metrics")
async def chatbot_metrics():
    """
    Get chatbot compiler performance metrics.

    Shows how the compiler has been making decisions.
    """
    return {
        "metrics": chatbot_compiler.get_metrics(),
        "engine": ENGINE
    }


@app.get("/chatbot/types")
async def chatbot_types():
    """
    List all request types and their constraint rules.

    This is the type system documentation.
    """
    from core.chatbot_compiler import RESPONSE_CONSTRAINTS

    types_info = {}
    for request_type, constraint in RESPONSE_CONSTRAINTS.items():
        types_info[request_type.value] = {
            "allowed": constraint.allowed,
            "requires_disclaimer": constraint.requires_disclaimer,
            "requires_deferral": constraint.requires_deferral,
            "requires_citation": constraint.requires_citation,
            "requires_verification": constraint.requires_verification,
            "max_specificity": constraint.max_specificity,
            "recovery_action": constraint.recovery_action.value
        }

    return {
        "types": types_info,
        "philosophy": {
            "insight": "Most chatbots optimize for response quality. That's the mistake.",
            "goal": "Only say something when it is allowed, grounded, and helpful - otherwise ask, defer, or refuse.",
            "differentiation": "The best chatbot optimizes for decision correctness, not response quality."
        },
        "engine": ENGINE
    }


@app.get("/chatbot/example")
async def chatbot_example():
    """
    Show examples of the chatbot compiler in action.

    Demonstrates how different inputs get different treatments.
    """
    examples = [
        {
            "input": "What is the capital of France?",
            "expected_type": "question",
            "expected_decision": "answer"
        },
        {
            "input": "What dose of ibuprofen should I take?",
            "expected_type": "medical_advice",
            "expected_decision": "defer"
        },
        {
            "input": "Can I sue my landlord for not fixing the AC?",
            "expected_type": "legal_advice",
            "expected_decision": "defer"
        },
        {
            "input": "Calculate 15% of 847.50",
            "expected_type": "calculation",
            "expected_decision": "answer"
        },
        {
            "input": "How do I hack into my ex's email?",
            "expected_type": "harmful",
            "expected_decision": "refuse"
        },
        {
            "input": "Should I invest in crypto right now?",
            "expected_type": "financial_advice",
            "expected_decision": "defer"
        }
    ]

    results = []
    for example in examples:
        response = compile_request(example["input"])
        results.append({
            "input": example["input"],
            "expected": {
                "type": example["expected_type"],
                "decision": example["expected_decision"]
            },
            "actual": {
                "type": response.classification.request_type.value,
                "decision": response.decision.value,
                "risk_level": response.classification.risk_level.value
            },
            "response": {
                "content": response.content,
                "disclaimer": response.disclaimer,
                "referral": response.referral,
                "clarification": response.clarification_question
            }
        })

    return {
        "examples": results,
        "insight": "Notice how medical, legal, and financial advice gets DEFER, harmful gets REFUSE, but questions and calculations get ANSWER.",
        "message": "This is the type system in action. Natural language is no longer untyped chaos.",
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
# TEACHER'S AIDE DATABASE - Easy Classroom Management
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/teachers/db")
async def teachers_db_summary():
    """
    Get Teacher's Aide Database summary.

    Shows total counts of students, classrooms, assessments, and interventions.
    """
    return {
        **teachers_db.get_summary(),
        "extended_teks_count": len(extended_teks.all_codes()),
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# STUDENTS - Manage student data
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/teachers/students")
async def add_student(request: AddStudentRequest):
    """
    Add a new student.

    Example:
        POST /teachers/students
        {"first_name": "Maria", "last_name": "Garcia", "grade": 5, "accommodations": ["ell"]}
    """
    student = teachers_db.add_student(
        first_name=request.first_name,
        last_name=request.last_name,
        grade=request.grade,
        accommodations=request.accommodations,
        student_id=request.student_id
    )

    ledger.append(
        operation="teachers_add_student",
        payload={"student_id": student.student_id},
        result="pass"
    )

    return {
        "message": f"Added {student.full_name}",
        "student": student.to_dict(),
        "engine": ENGINE
    }


@app.post("/teachers/students/batch")
async def add_students_batch(request: AddStudentsRequest):
    """
    Add multiple students at once.

    Example:
        POST /teachers/students/batch
        {"students": [
            {"first_name": "Maria", "last_name": "Garcia", "grade": 5},
            {"first_name": "John", "last_name": "Smith", "grade": 5}
        ]}
    """
    added = []
    for s in request.students:
        student = teachers_db.add_student(
            first_name=s.first_name,
            last_name=s.last_name,
            grade=s.grade,
            accommodations=s.accommodations,
            student_id=s.student_id
        )
        added.append(student.to_dict())

    ledger.append(
        operation="teachers_add_students_batch",
        payload={"count": len(added)},
        result="pass"
    )

    return {
        "message": f"Added {len(added)} students",
        "students": added,
        "engine": ENGINE
    }


@app.get("/teachers/students")
async def list_students(grade: Optional[int] = None, name: Optional[str] = None):
    """
    List or search students.

    Query params:
        grade: Filter by grade level
        name: Search by name (partial match)
    """
    if name:
        students = teachers_db.find_students(name)
    else:
        students = teachers_db.list_students(grade=grade)

    return {
        "students": [s.to_dict() for s in students],
        "count": len(students),
        "engine": ENGINE
    }


@app.get("/teachers/students/{student_id}")
async def get_student(student_id: str):
    """Get a specific student by ID."""
    student = teachers_db.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    return {
        "student": student.to_dict(),
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLASSROOMS - Manage classroom data
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/teachers/classrooms")
async def create_classroom(request: CreateClassroomRequest):
    """
    Create a new classroom.

    Example:
        POST /teachers/classrooms
        {"name": "5th Period Math", "grade": 5, "subject": "math", "teacher_name": "Ms. Johnson"}
    """
    classroom = teachers_db.create_classroom(
        name=request.name,
        grade=request.grade,
        subject=request.subject,
        teacher_name=request.teacher_name
    )

    ledger.append(
        operation="teachers_create_classroom",
        payload={"classroom_id": classroom.classroom_id},
        result="pass"
    )

    return {
        "message": f"Created classroom: {classroom.name}",
        "classroom": classroom.to_dict(),
        "engine": ENGINE
    }


@app.get("/teachers/classrooms")
async def list_classrooms():
    """List all classrooms."""
    classrooms = list(teachers_db.classrooms.values())
    return {
        "classrooms": [c.to_dict() for c in classrooms],
        "count": len(classrooms),
        "engine": ENGINE
    }


@app.get("/teachers/classrooms/{classroom_id}")
async def get_classroom(classroom_id: str):
    """Get a specific classroom by ID."""
    classroom = teachers_db.get_classroom(classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail=f"Classroom {classroom_id} not found")

    return {
        "classroom": classroom.to_dict(),
        "roster": classroom.get_roster(),
        "engine": ENGINE
    }


@app.post("/teachers/classrooms/{classroom_id}/students")
async def add_students_to_classroom(classroom_id: str, request: AddStudentToClassRequest):
    """
    Add students to a classroom.

    Example:
        POST /teachers/classrooms/CLASS001/students
        {"student_ids": ["STU0001", "STU0002"]}
    """
    result = teachers_db.add_students_to_classroom(request.student_ids, classroom_id)

    ledger.append(
        operation="teachers_add_to_classroom",
        payload={"classroom_id": classroom_id, "count": len(request.student_ids)},
        result="pass"
    )

    return {
        "message": result,
        "classroom_id": classroom_id,
        "engine": ENGINE
    }


@app.get("/teachers/classrooms/{classroom_id}/roster")
async def get_classroom_roster(classroom_id: str):
    """Get the class roster sorted by last name."""
    classroom = teachers_db.get_classroom(classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail=f"Classroom {classroom_id} not found")

    return {
        "classroom": classroom.name,
        "roster": classroom.get_roster(),
        "count": classroom.student_count,
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# DIFFERENTIATION - The core feature for teachers
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/teachers/classrooms/{classroom_id}/groups")
async def get_differentiated_groups(classroom_id: str):
    """
    Get differentiated student groups for a classroom.

    THIS IS THE KEY FEATURE - automatically groups students by mastery level
    for differentiated instruction.

    Returns:
        - Tier 3 (Needs Reteach): Students below 70%
        - Tier 2 (Approaching): Students 70-79%
        - Tier 1 (Mastery): Students 80-89%
        - Enrichment (Advanced): Students 90%+
    """
    result = teachers_db.get_groups(classroom_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    ledger.append(
        operation="teachers_get_groups",
        payload={"classroom_id": classroom_id},
        result="pass"
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.get("/teachers/classrooms/{classroom_id}/reteach")
async def get_reteach_group(classroom_id: str):
    """
    Get students who need reteaching.

    Quick access to the Tier 3 intervention group.
    """
    students = teachers_db.get_reteach_group(classroom_id)

    return {
        "classroom_id": classroom_id,
        "reteach_group": [s.to_simple_dict() for s in students],
        "count": len(students),
        "recommendation": "Small group instruction on prerequisite skills",
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# ASSESSMENTS - Track and enter scores
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/teachers/assessments")
async def create_assessment(request: CreateAssessmentRequest):
    """
    Create a new assessment.

    Example:
        POST /teachers/assessments
        {
            "name": "Exit Ticket 5.3A",
            "classroom_id": "CLASS001",
            "teks_codes": ["5.3A"],
            "total_points": 3
        }
    """
    assessment = teachers_db.create_assessment(
        name=request.name,
        classroom_id=request.classroom_id,
        teks_codes=request.teks_codes,
        total_points=request.total_points,
        assessment_type=request.assessment_type
    )

    ledger.append(
        operation="teachers_create_assessment",
        payload={"assessment_id": assessment.assessment_id, "teks": request.teks_codes},
        result="pass"
    )

    return {
        "message": f"Created assessment: {assessment.name}",
        "assessment": assessment.to_dict(),
        "engine": ENGINE
    }


@app.get("/teachers/assessments")
async def list_assessments():
    """List all assessments."""
    assessments = list(teachers_db.assessments.values())
    return {
        "assessments": [a.to_dict() for a in assessments],
        "count": len(assessments),
        "engine": ENGINE
    }


@app.get("/teachers/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get a specific assessment by ID."""
    assessment = teachers_db.assessments.get(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")

    return {
        "assessment": assessment.to_dict(),
        "groups": assessment.get_results_grouped(),
        "engine": ENGINE
    }


@app.post("/teachers/assessments/{assessment_id}/scores")
async def enter_scores(assessment_id: str, request: EnterScoresRequest):
    """
    Enter scores for an assessment.

    Automatically updates student mastery levels and groupings!

    Example:
        POST /teachers/assessments/ASSESS0001/scores
        {"scores": {"STU0001": 3, "STU0002": 2, "STU0003": 1}}
    """
    result = teachers_db.enter_scores(assessment_id, request.scores)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    ledger.append(
        operation="teachers_enter_scores",
        payload={"assessment_id": assessment_id, "count": len(request.scores)},
        result="pass"
    )

    return {
        **result,
        "message": "Scores entered! Student groups have been updated.",
        "engine": ENGINE
    }


@app.post("/teachers/assessments/{assessment_id}/quick-scores")
async def quick_enter_scores(assessment_id: str, request: QuickScoresRequest):
    """
    Quick score entry by student name.

    Enter scores using student names instead of IDs.

    Example:
        POST /teachers/assessments/ASSESS0001/quick-scores
        {"scores": [["Maria Garcia", 3], ["John Smith", 2]]}
    """
    scores_list = [(s[0], float(s[1])) for s in request.scores]
    result = teachers_db.quick_enter_scores(assessment_id, scores_list)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    ledger.append(
        operation="teachers_quick_scores",
        payload={"assessment_id": assessment_id, "count": len(request.scores)},
        result="pass"
    )

    return {
        **result,
        "message": "Scores entered! Student groups have been updated.",
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# INTERVENTIONS - Track intervention plans
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/teachers/interventions")
async def create_intervention(request: CreateInterventionRequest):
    """
    Create an intervention plan.

    If student_ids not provided, auto-populates from current grouping.

    Example:
        POST /teachers/interventions
        {
            "classroom_id": "CLASS001",
            "teks_codes": ["5.3A"],
            "target_group": "needs_reteach",
            "strategy": "Small group manipulatives"
        }
    """
    plan = teachers_db.create_intervention(
        classroom_id=request.classroom_id,
        teks_codes=request.teks_codes,
        target_group=request.target_group,
        strategy=request.strategy,
        student_ids=request.student_ids
    )

    ledger.append(
        operation="teachers_create_intervention",
        payload={"plan_id": plan.plan_id, "group": request.target_group},
        result="pass"
    )

    return {
        "message": f"Created intervention plan for {len(plan.student_ids)} students",
        "intervention": plan.to_dict(),
        "engine": ENGINE
    }


@app.get("/teachers/interventions")
async def list_interventions():
    """List all intervention plans."""
    interventions = list(teachers_db.interventions.values())
    return {
        "interventions": [i.to_dict() for i in interventions],
        "count": len(interventions),
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# TEKS - Extended standards database
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/teachers/teks")
async def get_extended_teks(grade: Optional[int] = None, subject: Optional[str] = None):
    """
    Get TEKS standards from the extended database.

    Includes 200+ standards across K-8 Math, Reading, Science, and Social Studies.
    """
    if grade is not None and subject is not None:
        try:
            subject_enum = Subject(subject)
            standards = extended_teks.get_by_grade_and_subject(grade, subject_enum)
        except ValueError:
            standards = extended_teks.get_by_grade(grade)
    elif grade is not None:
        standards = extended_teks.get_by_grade(grade)
    elif subject is not None:
        try:
            subject_enum = Subject(subject)
            standards = extended_teks.get_by_subject(subject_enum)
        except ValueError:
            standards = []
    else:
        standards = [extended_teks.get(code) for code in extended_teks.all_codes()]

    return {
        "standards": [s.to_dict() for s in standards if s],
        "count": len([s for s in standards if s]),
        "engine": ENGINE
    }


@app.get("/teachers/teks/stats")
async def get_teks_statistics():
    """Get statistics about the TEKS database."""
    return {
        **extended_teks.get_statistics(),
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATA PERSISTENCE - Save and load
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/teachers/db/save")
async def save_teachers_db(filename: Optional[str] = None):
    """
    Save the database to a JSON file.

    Example:
        POST /teachers/db/save?filename=my_class_data.json
    """
    filepath = teachers_db.save(filename)

    ledger.append(
        operation="teachers_db_save",
        payload={"filepath": filepath},
        result="pass"
    )

    return {
        "message": "Database saved",
        "filepath": filepath,
        "engine": ENGINE
    }


@app.post("/teachers/db/load")
async def load_teachers_db(filename: str):
    """
    Load the database from a JSON file.

    Example:
        POST /teachers/db/load?filename=my_class_data.json
    """
    result = teachers_db.load(filename)

    ledger.append(
        operation="teachers_db_load",
        payload={"filename": filename},
        result="pass" if "Loaded" in result else "fail"
    )

    return {
        "message": result,
        "summary": teachers_db.get_summary(),
        "engine": ENGINE
    }


@app.get("/teachers/info")
async def teachers_aide_info():
    """Get information about Teacher's Aide Database endpoints."""
    return {
        "description": "Easy-to-use classroom management for teachers",
        "philosophy": "Less paperwork, more teaching.",
        "endpoints": [
            {
                "category": "Students",
                "endpoints": [
                    {"method": "POST", "path": "/teachers/students", "description": "Add a student"},
                    {"method": "POST", "path": "/teachers/students/batch", "description": "Add multiple students"},
                    {"method": "GET", "path": "/teachers/students", "description": "List/search students"},
                    {"method": "GET", "path": "/teachers/students/{id}", "description": "Get student details"}
                ]
            },
            {
                "category": "Classrooms",
                "endpoints": [
                    {"method": "POST", "path": "/teachers/classrooms", "description": "Create a classroom"},
                    {"method": "GET", "path": "/teachers/classrooms", "description": "List classrooms"},
                    {"method": "GET", "path": "/teachers/classrooms/{id}", "description": "Get classroom details"},
                    {"method": "POST", "path": "/teachers/classrooms/{id}/students", "description": "Add students to class"},
                    {"method": "GET", "path": "/teachers/classrooms/{id}/roster", "description": "Get class roster"}
                ]
            },
            {
                "category": "Differentiation",
                "endpoints": [
                    {"method": "GET", "path": "/teachers/classrooms/{id}/groups", "description": "Get student groups by mastery (THE KEY FEATURE!)"},
                    {"method": "GET", "path": "/teachers/classrooms/{id}/reteach", "description": "Get reteach group"}
                ]
            },
            {
                "category": "Assessments",
                "endpoints": [
                    {"method": "POST", "path": "/teachers/assessments", "description": "Create an assessment"},
                    {"method": "GET", "path": "/teachers/assessments", "description": "List assessments"},
                    {"method": "POST", "path": "/teachers/assessments/{id}/scores", "description": "Enter scores"},
                    {"method": "POST", "path": "/teachers/assessments/{id}/quick-scores", "description": "Quick entry by name"}
                ]
            },
            {
                "category": "Interventions",
                "endpoints": [
                    {"method": "POST", "path": "/teachers/interventions", "description": "Create intervention plan"},
                    {"method": "GET", "path": "/teachers/interventions", "description": "List interventions"}
                ]
            },
            {
                "category": "TEKS",
                "endpoints": [
                    {"method": "GET", "path": "/teachers/teks", "description": "Browse 200+ TEKS standards"},
                    {"method": "GET", "path": "/teachers/teks/stats", "description": "TEKS database statistics"}
                ]
            },
            {
                "category": "Data",
                "endpoints": [
                    {"method": "POST", "path": "/teachers/db/save", "description": "Save database to file"},
                    {"method": "POST", "path": "/teachers/db/load", "description": "Load database from file"}
                ]
            }
        ],
        "key_features": [
            "Automatic student grouping by mastery level",
            "Enter scores by name (no IDs needed!)",
            "Auto-update groups after each assessment",
            "200+ TEKS standards included",
            "Save/load data for persistence"
        ],
        "differentiation_tiers": {
            "tier_3": "Needs Reteach - Below 70% - Small group with teacher",
            "tier_2": "Approaching - 70-79% - Guided practice with scaffolds",
            "tier_1": "Mastery - 80-89% - Standard instruction",
            "enrichment": "Advanced - 90%+ - Extension activities"
        },
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
# INTERFACE BUILDER - Verified UI Generation
# ═══════════════════════════════════════════════════════════════════════════════

class InterfaceBuildRequest(BaseModel):
    """Build interface from template or spec."""
    template_id: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    spec: Optional[Dict[str, Any]] = None
    output_format: str = "json"  # json, jsx, html, all


@app.get("/interface/templates")
async def get_interface_templates(
    query: str = "",
    type: Optional[str] = None,
    tags: Optional[str] = None
):
    """
    Get available interface templates.

    Query params:
        query: Search query string
        type: Filter by interface type (form, dashboard, settings, etc.)
        tags: Comma-separated tags to filter by

    Example:
        GET /interface/templates?type=dashboard
        GET /interface/templates?query=form
        GET /interface/templates?tags=settings,preferences
    """
    tag_list = tags.split(",") if tags else None
    result = interface_builder.get_templates(query, type, tag_list)

    return {
        **result,
        "engine": ENGINE
    }


@app.get("/interface/templates/{template_id}")
async def get_interface_template(template_id: str):
    """
    Get a specific template by ID.

    Example:
        GET /interface/templates/dashboard-basic
    """
    template = interface_builder.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")

    return {
        "template": template,
        "engine": ENGINE
    }


@app.post("/interface/build")
async def build_interface(request: InterfaceBuildRequest):
    """
    Build a verified interface.

    Either provide:
    - template_id + variables: Build from a template with variable substitution
    - spec: Build from a complete component specification

    Output formats:
    - json: Component tree as JSON
    - jsx: React JSX component code
    - html: Production HTML
    - all: All formats

    Example (from template):
        POST /interface/build
        {
            "template_id": "dashboard-basic",
            "variables": {
                "title": "My Dashboard",
                "metric1_value": "98.4%",
                "metric1_label": "Pass Rate"
            },
            "output_format": "all"
        }

    Example (from spec):
        POST /interface/build
        {
            "spec": {
                "name": "Custom Form",
                "type": "form",
                "layout": "single_column",
                "components": [
                    {"id": "title", "type": "heading", "props": {"content": "Contact"}}
                ]
            },
            "output_format": "jsx"
        }
    """
    if request.template_id:
        result = interface_builder.build_from_template(
            template_id=request.template_id,
            variables=request.variables,
            output_format=request.output_format
        )
    elif request.spec:
        result = interface_builder.build_from_spec(
            spec=request.spec,
            output_format=request.output_format
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Either template_id or spec must be provided"
        )

    # Log to ledger
    ledger.append(
        operation="interface_build",
        payload={
            "template_id": request.template_id,
            "has_spec": request.spec is not None,
            "output_format": request.output_format
        },
        result="pass" if result.get("verified") else "fail",
        metadata={"elapsed_us": result.get("elapsed_us", 0)}
    )

    return {
        **result,
        "engine": ENGINE
    }


@app.get("/interface/components")
async def get_component_types():
    """
    Get all available component types.

    Returns components grouped by category:
    - layout: Container, Grid, Flex, Sidebar, Header, Footer, Card, Modal
    - input: Button, Input, Textarea, Select, Checkbox, Radio, Toggle, Slider
    - display: Text, Heading, Badge, Metric, Code, Table, List, Image, Icon
    - feedback: Alert, Toast, Progress, Spinner, Skeleton
    """
    return {
        "components": interface_builder.get_component_types(),
        "engine": ENGINE
    }


@app.get("/interface/info")
async def interface_builder_info():
    """Get Interface Builder capabilities and documentation."""
    info = interface_builder.get_info()

    return {
        **info,
        "endpoints": [
            {"method": "GET", "path": "/interface/templates", "description": "List all templates"},
            {"method": "GET", "path": "/interface/templates/{id}", "description": "Get template by ID"},
            {"method": "POST", "path": "/interface/build", "description": "Build interface from template or spec"},
            {"method": "GET", "path": "/interface/components", "description": "List component types"},
            {"method": "GET", "path": "/interface/info", "description": "This info endpoint"}
        ],
        "examples": {
            "build_from_template": {
                "endpoint": "POST /interface/build",
                "body": {
                    "template_id": "dashboard-basic",
                    "variables": {"title": "My App"},
                    "output_format": "all"
                }
            },
            "build_from_spec": {
                "endpoint": "POST /interface/build",
                "body": {
                    "spec": {
                        "name": "Custom UI",
                        "type": "form",
                        "layout": "single_column",
                        "components": [{"id": "btn", "type": "button", "props": {"label": "Click"}}]
                    }
                }
            }
        },
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GUMROAD - Payments, Licensing, and Feedback
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# GUMROAD MODELS
# ─────────────────────────────────────────────────────────────────────────────

class LicenseVerifyRequest(BaseModel):
    """Verify a Gumroad license key."""
    license_key: str


class FeedbackRequest(BaseModel):
    """Submit feedback."""
    message: str
    email: Optional[str] = "anonymous"
    rating: Optional[int] = None  # 1-5 stars
    category: Optional[str] = "general"  # bug, feature, general, praise


class ApiKeyRequest(BaseModel):
    """Get API key using license."""
    license_key: str


# ─────────────────────────────────────────────────────────────────────────────
# LICENSE & API KEY ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/license/verify")
async def verify_license(request: LicenseVerifyRequest):
    """
    Verify a Gumroad license key.

    After purchasing Newton access on Gumroad, use this endpoint to verify
    your license and get your API key.

    Example:
        POST /license/verify
        {"license_key": "YOUR_GUMROAD_LICENSE_KEY"}

    Returns your API key if valid.
    """
    result = gumroad.verify_license(request.license_key)

    if result.valid:
        # Get or create API key for this license
        api_key = gumroad.get_api_key_for_license(request.license_key)

        ledger.append(
            operation="license_verify",
            payload={"email": result.email, "valid": True},
            result="pass"
        )

        return {
            "valid": True,
            "email": result.email,
            "api_key": api_key,
            "uses": result.uses,
            "purchase_date": result.purchase_date,
            "product": result.product_name,
            "message": "License verified! Use your API key in the X-API-Key header.",
            "engine": ENGINE
        }

    ledger.append(
        operation="license_verify",
        payload={"valid": False, "error": result.error},
        result="fail"
    )

    raise HTTPException(status_code=401, detail=result.error or "Invalid license key")


@app.get("/license/info")
async def license_info():
    """
    Get information about purchasing Newton access.

    Returns pricing, what's included, and how to buy.
    """
    return {
        **gumroad.get_pricing_info(),
        "how_to_buy": {
            "step_1": "Visit the Gumroad product page (link in response)",
            "step_2": "Purchase Newton Supercomputer Access for $5",
            "step_3": "You'll receive a license key via email",
            "step_4": "POST /license/verify with your license key",
            "step_5": "Use your API key in the X-API-Key header for all requests"
        },
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# WEBHOOK ENDPOINT (for Gumroad)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/webhooks/gumroad")
async def gumroad_webhook(request: Request):
    """
    Gumroad webhook endpoint.

    Receives events from Gumroad when:
    - New sale occurs
    - Refund is processed
    - Dispute is opened/resolved

    Configure this URL in your Gumroad product settings:
    https://your-domain.com/webhooks/gumroad
    """
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("X-Gumroad-Signature", "")

    # Verify webhook signature
    if not gumroad.verify_webhook_signature(body, signature):
        ledger.append(
            operation="webhook_gumroad",
            payload={"error": "Invalid signature"},
            result="fail"
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse webhook data
    try:
        data = await request.json()
    except Exception:
        # Gumroad sends form data, not JSON
        form = await request.form()
        data = dict(form)

    event_type = data.get("resource_name", "sale")

    # Process the webhook
    result = gumroad.process_webhook(event_type, data)

    ledger.append(
        operation="webhook_gumroad",
        payload={"event": event_type, "processed": result.get("processed", False)},
        result="pass" if result.get("processed") else "fail"
    )

    return {
        **result,
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback about Newton.

    We're in testing mode and would LOVE to hear from you!
    Bug reports, feature requests, general thoughts - all welcome.

    Example:
        POST /feedback
        {
            "message": "The constraint verification is super fast!",
            "rating": 5,
            "category": "praise"
        }

    Categories: bug, feature, general, praise
    Rating: 1-5 stars (optional)
    """
    feedback = gumroad.submit_feedback(
        message=request.message,
        email=request.email or "anonymous",
        rating=request.rating,
        category=request.category or "general"
    )

    ledger.append(
        operation="feedback_submit",
        payload={"category": request.category, "has_rating": request.rating is not None},
        result="pass"
    )

    return {
        "success": True,
        "feedback_id": feedback.id,
        "message": "Thank you for your feedback! We read every submission.",
        "engine": ENGINE
    }


@app.get("/feedback/summary")
async def get_feedback_summary():
    """
    Get a summary of all feedback (admin endpoint).

    Shows feedback statistics and trends.
    """
    return {
        **gumroad.get_feedback_summary(),
        "engine": ENGINE
    }


# ─────────────────────────────────────────────────────────────────────────────
# GUMROAD STATS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/gumroad/stats")
async def gumroad_stats():
    """Get Gumroad integration statistics."""
    return {
        **gumroad.stats(),
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS & HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """System health check."""
    import os
    chain_valid, _ = ledger.verify_chain()
    gumroad_stats = gumroad.stats()

    # Debug: Check file system for static files
    static_files = {
        "root_dir": str(ROOT_DIR),
        "cwd": os.getcwd(),
        "index_html_exists": (ROOT_DIR / "index.html").exists(),
        "frontend_exists": FRONTEND_DIR.exists(),
        "teachers_exists": TEACHERS_DIR.exists(),
        "builder_exists": BUILDER_DIR.exists(),
    }
    if ROOT_DIR.exists():
        static_files["root_files"] = [f.name for f in list(ROOT_DIR.iterdir())[:10]]

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
            "merkle_scheduler": "operational" if merkle_scheduler._running else "stopped",
            "gumroad": "operational"
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
        },
        "gumroad": {
            "active_customers": gumroad_stats.get("active_customers", 0),
            "total_feedback": gumroad_stats.get("feedback_count", 0)
        },
        "static_files": static_files
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
# VOICE INTERFACE - MOAD (Mother Of All Demos)
# "Easy now with Newton. He has so much power. Think speaking to your computer."
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
            user_id=request.user_id
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
            "engine": ENGINE
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
            user_id=request.user_id
        ):
            results.append(update)

        return {
            "updates": results,
            "final": results[-1] if results else None,
            "engine": ENGINE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/intent")
async def parse_intent(request: IntentParseRequest):
    """
    Parse natural language to structured intent.

    Returns:
        - intent_type: what/do/go/remember
        - domain: finance/education/health/make/etc.
        - action: the primary verb
        - entities: extracted values
        - confidence: how sure we are
    """
    from core.voice_interface import IntentParser
    parser = IntentParser()
    intent = parser.parse(request.text)

    return {
        "intent": intent.to_dict(),
        "raw_input": intent.raw_input,
        "engine": ENGINE
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
        "engine": ENGINE
    }


@app.post("/voice/patterns/search")
async def search_patterns(request: PatternSearchRequest):
    """Search for app patterns matching your needs."""
    from core.voice_interface import PatternLibrary
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
                "example_prompts": p.example_prompts
            }
            for p in patterns
        ],
        "query": request.query,
        "engine": ENGINE
    }


@app.get("/voice/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get details about a specific app pattern."""
    from core.voice_interface import PatternLibrary
    library = PatternLibrary()
    pattern = library.get_pattern(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern '{pattern_id}' not found")

    return {
        "pattern": {
            "id": pattern.id,
            "name": pattern.name,
            "description": pattern.description,
            "domain": pattern.domain.value,
            "keywords": pattern.keywords,
            "cdl_template": pattern.cdl_template,
            "interface_template": pattern.interface_template,
            "example_prompts": pattern.example_prompts
        },
        "engine": ENGINE
    }


@app.get("/voice/session/{session_id}")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    history = voice_interface.get_session_history(session_id)

    if history is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found or expired")

    return {
        "session_id": session_id,
        "turns": history,
        "count": len(history),
        "engine": ENGINE
    }


@app.get("/voice/demo")
async def voice_demo():
    """
    MOAD Demo Scenarios - Mother Of All Demos

    Returns example scenarios that demonstrate Newton's voice interface:
    1. Financial Calculator with Proofs (30 seconds)
    2. TEKS-Aligned Education App (30 seconds)
    3. Content Safety Verification (instant)
    4. Audit Trail Demo (instant)
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
                "time_estimate": "30 seconds"
            },
            {
                "name": "Education Platform",
                "description": "Create a TEKS-aligned lesson planner",
                "example_query": "Create a lesson planner for 5th grade math on fractions",
                "expected_result": "50-minute NES lesson plan with TEKS alignment",
                "time_estimate": "30 seconds"
            },
            {
                "name": "Content Safety",
                "description": "Add Forge content verification",
                "example_query": "Add content safety verification so it can't show inappropriate material",
                "expected_result": "Content safety constraints applied",
                "time_estimate": "instant"
            },
            {
                "name": "Audit Trail",
                "description": "Show immutable audit trail",
                "example_query": "Show me the audit trail of everything I just built",
                "expected_result": "Merkle-anchored ledger of all operations",
                "time_estimate": "instant"
            },
            {
                "name": "Inventory Tracker",
                "description": "Build verified inventory management",
                "example_query": "Build a restaurant inventory tracker with verification that nobody can fake the numbers",
                "expected_result": "Inventory app with tamper-proof audit trail",
                "time_estimate": "30 seconds"
            }
        ],
        "key_points": [
            "Every computation is verified before execution",
            "Immutable audit trail of all operations",
            "Cryptographic proofs for external verification",
            "Sub-millisecond constraint checking",
            "No hallucinations - constraints prevent invalid states"
        ],
        "try_it": {
            "endpoint": "/voice/ask",
            "method": "POST",
            "example_body": {
                "query": "Build me a calculator",
                "session_id": None
            }
        },
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
    print("\nCore Endpoints:")
    print("  POST /ask        - Ask Newton anything")
    print("  POST /verify     - Verify input")
    print("  POST /constraint - Evaluate CDL constraint")
    print("  POST /ground     - Ground a claim")
    print("  GET  /ledger     - View audit trail")
    print("  GET  /metrics    - System metrics")
    print("\nVoice Interface (MOAD):")
    print("  POST /voice/ask      - Natural language → verified app")
    print("  POST /voice/stream   - Streaming voice interface")
    print("  GET  /voice/patterns - List app patterns")
    print("  GET  /voice/demo     - MOAD demo scenarios")
    print("\nPayment & Access ($5 during testing):")
    print("  GET  /license/info   - Pricing & how to buy")
    print("  POST /license/verify - Verify license & get API key")
    print("  POST /feedback       - Send us feedback!")
    print("\n1 == 1. The cloud is weather. We're building shelter.")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
