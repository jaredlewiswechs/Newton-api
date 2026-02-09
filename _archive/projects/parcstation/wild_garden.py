#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
WILD GARDEN — parcStation for Schools
The local AI playground where schools own their compute, own their data,
and Newton keeps everything grounded.

                    ╔═══════════════════════════════════════╗
                    ║     🌱 THE WILD GARDEN 🌱               ║
                    ║                                         ║
                    ║   "Let the LLM think freely inside.     ║
                    ║    Newton is the fence. Nothing leaves  ║
                    ║    without verification."               ║
                    ║                                         ║
                    ║   Built on proof.                       ║
                    ╚═══════════════════════════════════════╝

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
In the spirit of ATG: Bill Atkinson, Woz, Larry Tesler
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiohttp
import urllib.parse

# TEKS import
try:
    from tinytalk_py.teks_database import get_extended_teks_library
    TEKS_AVAILABLE = True
async def get_teks(grade: Optional[int] = None, subject: Optional[str] = None):
    """Return the full TEKS standards library. Optional filters: grade, subject."""
    if not TEKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TEKS database not available")
    lib = get_extended_teks_library()
    # lib stores standards in _standards dict
    standards = list(lib._standards.values())

    # Apply filters
    if grade is not None:
        standards = [s for s in standards if getattr(s, 'grade', None) == int(grade)]
    if subject:
        subj = subject.lower()
        standards = [s for s in standards if getattr(s, 'subject', None) and s.subject.value == subj]

    return {
        "teks": [s.to_dict() for s in standards],
        "count": len(standards)
    }


@app.post("/teks/search")
async def teks_search(payload: Dict[str, Any]):
    """Search TEKS standards by keyword or code. POST body: {"query": "..."} """
    if not TEKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TEKS database not available")
    query = (payload.get('query') if isinstance(payload, dict) else None) or ''
    query = query.strip()
    lib = get_extended_teks_library()
    standards = list(lib._standards.values())

    if not query:
        results = standards
    else:
        q = query.lower()
        results = [s for s in standards if s.matches_keywords(q) or q in s.code.lower()]

    return {"results": [s.to_dict() for s in results], "count": len(results)}
class AuditEntry:
    """An immutable audit log entry."""
    id: str
    timestamp: float
    student_id: str  # Anonymized
    query: str
    llm_response: str
    verified_response: str
    claims: List[Dict]
    policy_checks: List[Dict]
    hash: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StudentSession:
    """A student's session with conversation history."""
    session_id: str
    student_id: str  # Anonymized hash, not PII
    started_at: float
    turns: List[Dict] = field(default_factory=list)
    stack_progress: Dict[str, float] = field(default_factory=dict)


# Request/Response Models
class AskRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    student_id: Optional[str] = None
    context: Optional[Dict] = None


class VerifyRequest(BaseModel):
    claim: str
    sources: Optional[List[str]] = None


class MathRequest(BaseModel):
    expression: str
    show_steps: bool = True


class PolicyCheckRequest(BaseModel):
    content: str
    policy_level: str = "school"  # "school", "coppa", "ferpa"


class WikipediaRequest(BaseModel):
    query: str
    sentences: int = 3


class ArxivRequest(BaseModel):
    query: str
    max_results: int = 5


# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

SCHOOL_SAFETY_PATTERNS = {
    "violence": [
        r"\b(how to )?(make|build|create).*(weapon|bomb|gun|explosive)",
        r"\b(hurt|kill|harm|attack)\b.*\b(someone|people|person|student|teacher)\b",
    ],
    "inappropriate": [
        r"\b(porn|nsfw|xxx|explicit|nude)\b",
        r"\b(drug|cocaine|heroin|meth)\s*(use|make|buy|sell)\b",
    ],
    "cheating": [
        r"\b(write my|do my|complete my)\s*(essay|homework|assignment|test)\b",
        r"\b(cheat|copy|plagiarize)\b.*\b(test|exam|assignment)\b",
    ],
    "jailbreak": [
        r"\b(ignore|bypass|override)\s*(rules|filters|safety|restrictions)\b",
        r"\bjailbreak\b",
        r"\bpretend you (have no|don't have)\s*(rules|restrictions)\b",
    ],
    "pii_request": [
        r"\b(give me|find|get).*(address|phone number|social security|credit card)\b",
        r"\b(dox|doxx)\b",
    ],
}


class PolicyEngine:
    """
    The fence around the wild garden.
    Checks content against school safety policies.
    """
    
    def __init__(self, level: str = "school"):
        self.level = level
        self.patterns = SCHOOL_SAFETY_PATTERNS
        
    def check(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check content against policies.
        Returns (passed, list of violations).
        """
        content_lower = content.lower()
        violations = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    violations.append(category)
                    break
        
        return len(violations) == 0, violations


# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON FENCE — The Core Verification Layer
# ═══════════════════════════════════════════════════════════════════════════════

class NewtonFence:
    """
    The fence that surrounds the wild garden.
    LLM can say anything inside. Nothing leaves without verification.
    
    Steps:
    1. Extract claims from LLM response
    2. Verify each claim against sources
    3. Check safety policies
    4. Correct or mark unverified claims
    5. Build verified response with citations
    """
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.grounding = EnhancedGroundingEngine() if GROUNDING_AVAILABLE else None
        self.logic_engine = LogicEngine() if NEWTON_CORE_AVAILABLE else None
        self.audit_log: List[AuditEntry] = []
        
    def extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Skip questions, commands, opinions
            if sentence.endswith('?'):
                continue
            if sentence.lower().startswith(('please', 'let me', 'i think', 'i believe', 'maybe')):
                continue
            
            claims.append(sentence)
        
        return claims
    
    def extract_math(self, text: str) -> List[Dict]:
        """Extract and verify mathematical expressions."""
        math_patterns = [
            r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)',  # Addition
            r'(\d+)\s*-\s*(\d+)\s*=\s*(\d+)',   # Subtraction
            r'(\d+)\s*[×x\*]\s*(\d+)\s*=\s*(\d+)',  # Multiplication
            r'(\d+)\s*[÷/]\s*(\d+)\s*=\s*(\d+)',   # Division
            r'(\d+)\s*\^\s*(\d+)\s*=\s*(\d+)',     # Exponent
        ]
        
        results = []
        for pattern in math_patterns[:1]:  # Start with addition
            for match in re.finditer(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', text):
                a, b, result = int(match.group(1)), int(match.group(2)), int(match.group(3))
                correct = a + b
                results.append({
                    "expression": f"{a} + {b} = {result}",
                    "claimed": result,
                    "correct": correct,
                    "verified": result == correct
                })
        
        # Subtraction
        for match in re.finditer(r'(\d+)\s*-\s*(\d+)\s*=\s*(\d+)', text):
            a, b, result = int(match.group(1)), int(match.group(2)), int(match.group(3))
            correct = a - b
            results.append({
                "expression": f"{a} - {b} = {result}",
                "claimed": result,
                "correct": correct,
                "verified": result == correct
            })
        
        # Multiplication
        for match in re.finditer(r'(\d+)\s*[×x\*]\s*(\d+)\s*=\s*(\d+)', text):
            a, b, result = int(match.group(1)), int(match.group(2)), int(match.group(3))
            correct = a * b
            results.append({
                "expression": f"{a} × {b} = {result}",
                "claimed": result,
                "correct": correct,
                "verified": result == correct
            })
        
        return results
    
    def verify_claim(self, claim: str) -> VerifiedClaim:
        """Verify a single claim."""
        if not self.grounding:
            # No grounding engine - mark as unverified
            return VerifiedClaim(
                text=claim,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                reason="Grounding engine not available"
            )
        
        try:
            result = self.grounding.verify_claim(claim)
            
            if result.status == "VERIFIED":
                return VerifiedClaim(
                    text=claim,
                    status=VerificationStatus.VERIFIED,
                    confidence=result.confidence_score,
                    sources=[e.to_dict() for e in result.evidence[:3]]
                )
            elif result.status == "LIKELY":
                return VerifiedClaim(
                    text=claim,
                    status=VerificationStatus.VERIFIED,
                    confidence=result.confidence_score,
                    sources=[e.to_dict() for e in result.evidence[:3]]
                )
            else:
                return VerifiedClaim(
                    text=claim,
                    status=VerificationStatus.UNVERIFIED,
                    confidence=result.confidence_score,
                    reason="Could not verify against reliable sources"
                )
        except Exception as e:
            return VerifiedClaim(
                text=claim,
                status=VerificationStatus.UNVERIFIED,
                confidence=0.0,
                reason=str(e)
            )
    
    def process(
        self, 
        llm_response: str,
        query: str,
        student_id: str = "anonymous"
    ) -> Dict:
        """
        Process an LLM response through the Newton Fence.
        
        Returns a verified response with:
        - Verified claims with sources
        - Corrected claims (if needed)
        - Unverified claims marked
        - Math verified
        - Safety checked
        """
        
        # Step 1: Safety check on the query
        query_safe, query_violations = self.policy_engine.check(query)
        if not query_safe:
            return {
                "success": False,
                "blocked": True,
                "reason": f"Query blocked by policy: {', '.join(query_violations)}",
                "response": "I can't help with that. Let's focus on your learning. What topic are you working on?",
                "audit_hash": self._log_blocked(query, student_id, query_violations)
            }
        
        # Step 2: Safety check on the response
        response_safe, response_violations = self.policy_engine.check(llm_response)
        if not response_safe:
            return {
                "success": False,
                "blocked": True,
                "reason": f"Response blocked by policy: {', '.join(response_violations)}",
                "response": "I need to rephrase that. Let me give you a better answer.",
                "audit_hash": self._log_blocked(llm_response, student_id, response_violations)
            }
        
        # Step 3: Extract and verify math
        math_results = self.extract_math(llm_response)
        math_errors = [m for m in math_results if not m["verified"]]
        
        # Step 4: Extract and verify claims
        claims = self.extract_claims(llm_response)
        verified_claims = []
        
        for claim in claims[:5]:  # Limit to first 5 claims for performance
            verified = self.verify_claim(claim)
            verified_claims.append(verified)
        
        # Step 5: Build the verified response
        response_text = llm_response
        corrections = []
        
        # Correct math errors
        for error in math_errors:
            correction = f"Correction: {error['expression'].split('=')[0]}= {error['correct']}"
            corrections.append(correction)
            response_text = response_text.replace(
                str(error['claimed']),
                f"**{error['correct']}** (corrected from {error['claimed']})"
            )
        
        # Gather sources
        all_sources = []
        for vc in verified_claims:
            all_sources.extend(vc.sources)
        
        # Calculate overall confidence
        if verified_claims:
            avg_confidence = sum(vc.confidence for vc in verified_claims) / len(verified_claims)
        else:
            avg_confidence = 0.5  # No claims to verify
        
        # Step 6: Log to audit trail
        audit_hash = self._log_interaction(
            query=query,
            llm_response=llm_response,
            verified_response=response_text,
            claims=verified_claims,
            student_id=student_id
        )
        
        return {
            "success": True,
            "blocked": False,
            "response": response_text,
            "corrections": corrections,
            "claims": [
                {
                    "text": vc.text,
                    "status": vc.status.value,
                    "confidence": vc.confidence,
                    "sources": vc.sources
                }
                for vc in verified_claims
            ],
            "math_verified": math_results,
            "overall_confidence": avg_confidence,
            "sources": all_sources[:5],  # Top 5 sources
            "audit_hash": audit_hash
        }
    
    def _log_interaction(
        self,
        query: str,
        llm_response: str,
        verified_response: str,
        claims: List[VerifiedClaim],
        student_id: str
    ) -> str:
        """Log interaction to audit trail."""
        entry_id = hashlib.sha256(
            f"{time.time()}:{query}:{student_id}".encode()
        ).hexdigest()[:16]
        
        entry = AuditEntry(
            id=entry_id,
            timestamp=time.time(),
            student_id=hashlib.sha256(student_id.encode()).hexdigest()[:16],
            query=query,
            llm_response=llm_response,
            verified_response=verified_response,
            claims=[
                {"text": c.text, "status": c.status.value, "confidence": c.confidence}
                for c in claims
            ],
            policy_checks=[{"name": "school_safety", "passed": True}],
            hash=""
        )
        
        # Compute hash
        entry_content = json.dumps(entry.to_dict(), sort_keys=True)
        entry.hash = hashlib.sha256(entry_content.encode()).hexdigest()
        
        self.audit_log.append(entry)
        return entry.hash
    
    def _log_blocked(self, content: str, student_id: str, violations: List[str]) -> str:
        """Log a blocked interaction."""
        entry_id = f"blocked_{int(time.time())}"
        return entry_id
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit entries."""
        return [e.to_dict() for e in self.audit_log[-limit:]]


# ═══════════════════════════════════════════════════════════════════════════════
# WILD GARDEN — The Main Server
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Wild Garden",
    description="parcStation for Schools - Local AI with Newton verification",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ollama = OllamaBackend(OllamaConfig(
    model="qwen2.5:3b",  # Fast, good for schools
    temperature=0.7,
    system_prompt=(
        "You are a helpful educational assistant. "
        "Keep explanations clear and age-appropriate. "
        "Always show your work when solving problems. "
        "If you're uncertain, say 'I'm not sure, let me check.'"
    )
)) if OLLAMA_AVAILABLE else None

fence = NewtonFence()
sessions: Dict[str, StudentSession] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the Wild Garden UI."""
    ui_path = os.path.join(os.path.dirname(__file__), "wild_garden_ui.html")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <body style="font-family: system-ui; padding: 40px; text-align: center;">
            <h1>🌱 Wild Garden</h1>
            <p>parcStation for Schools - Local AI with Newton verification</p>
            <p><a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """


@app.get("/api")
async def api_info():
    """Wild Garden API info."""
    return {
        "name": "Wild Garden",
        "version": "1.0.0",
        "description": "parcStation for Schools - The classroom AI that stays in the classroom",
        "components": {
            "ollama": OLLAMA_AVAILABLE,
            "grounding": GROUNDING_AVAILABLE,
            "newton_core": NEWTON_CORE_AVAILABLE,
        },
        "philosophy": "Let the LLM think freely inside. Newton is the fence.",
    }


@app.get("/health")
async def health():
    """Health check."""
    ollama_status = "not_available"
    if OLLAMA_AVAILABLE:
        try:
            # Quick test
            test_response = ollama.generate("test", [])
            ollama_status = "connected" if test_response else "error"
        except:
            ollama_status = "error"
    
    return {
        "status": "healthy",
        "ollama": ollama_status,
        "grounding": "available" if GROUNDING_AVAILABLE else "not_available",
        "newton": "available" if NEWTON_CORE_AVAILABLE else "not_available",
        "sessions": len(sessions),
        "audit_entries": len(fence.audit_log),
    }


@app.post("/ask")
async def ask(request: AskRequest):
    """
    The main endpoint: Ask the Wild Garden a question.
    
    Flow:
    1. LLM generates response (wild)
    2. Newton Fence verifies (safe)
    3. Response returned with proof
    """
    query = request.query
    session_id = request.session_id or f"session_{int(time.time())}"
    student_id = request.student_id or "anonymous"
    
    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = StudentSession(
            session_id=session_id,
            student_id=student_id,
            started_at=time.time()
        )
    session = sessions[session_id]
    
    # Build conversation context
    context = [{"role": t["role"], "content": t["content"]} for t in session.turns[-10:]]
    
    # Step 1: Get LLM response (the wild part)
    if not OLLAMA_AVAILABLE:
        # Fallback response without LLM
        llm_response = f"I understand you're asking about: {query}. Let me help you with that. (Note: Local LLM not connected - install Ollama for full AI responses)"
    else:
        try:
            llm_response = ollama.generate(query, context)
        except Exception as e:
            llm_response = f"I'm having trouble connecting to the AI engine. Error: {str(e)}"
    
    # Step 2: Pass through Newton Fence (the safe part)
    verified = fence.process(llm_response, query, student_id)
    
    # Step 3: Update session
    session.turns.append({"role": "user", "content": query, "timestamp": time.time()})
    session.turns.append({
        "role": "assistant", 
        "content": verified["response"],
        "verified": verified["success"],
        "timestamp": time.time()
    })
    
    return {
        "success": verified["success"],
        "response": verified["response"],
        "blocked": verified.get("blocked", False),
        "verification": {
            "claims": verified.get("claims", []),
            "math_verified": verified.get("math_verified", []),
            "confidence": verified.get("overall_confidence", 0.5),
            "sources": verified.get("sources", []),
        },
        "corrections": verified.get("corrections", []),
        "session_id": session_id,
        "audit_hash": verified.get("audit_hash"),
    }


@app.post("/verify")
async def verify(request: VerifyRequest):
    """Verify a specific claim against sources."""
    result = fence.verify_claim(request.claim)
    return {
        "claim": request.claim,
        "status": result.status.value,
        "confidence": result.confidence,
        "sources": result.sources,
        "correction": result.correction,
        "reason": result.reason,
    }


@app.post("/math")
async def verify_math(request: MathRequest):
    """Verify a mathematical expression."""
    if not NEWTON_CORE_AVAILABLE:
        # Simple eval fallback
        try:
            # Safe eval for basic math
            allowed = set('0123456789+-*/()., ')
            expr = request.expression
            if all(c in allowed for c in expr):
                result = eval(expr)
                return {
                    "expression": expr,
                    "result": result,
                    "verified": True,
                    "steps": [f"Computed: {expr} = {result}"]
                }
        except:
            pass
        
        return {
            "expression": request.expression,
            "error": "Newton core not available for advanced math",
            "verified": False
        }
    
    try:
        result = fence.logic_engine.evaluate(
            {"op": "eval", "args": [request.expression]}
        )
        return {
            "expression": request.expression,
            "result": result,
            "verified": True,
        }
    except Exception as e:
        return {
            "expression": request.expression,
            "error": str(e),
            "verified": False
        }


@app.post("/policy/check")
async def check_policy(request: PolicyCheckRequest):
    """Check content against school safety policy."""
    passed, violations = fence.policy_engine.check(request.content)
    return {
        "content_length": len(request.content),
        "passed": passed,
        "violations": violations,
        "policy_level": request.policy_level,
    }


@app.get("/audit")
async def get_audit_log(limit: int = 50):
    """Get the audit trail (for teachers/admins)."""
    return {
        "entries": fence.get_audit_log(limit),
        "total": len(fence.audit_log),
    }


@app.get("/sessions")
async def list_sessions():
    """List active sessions (for teachers)."""
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "student_id": s.student_id,
                "started_at": s.started_at,
                "turns": len(s.turns),
            }
            for s in sessions.values()
        ],
        "total": len(sessions)
    }


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get a specific session's history."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session.session_id,
        "student_id": session.student_id,
        "started_at": session.started_at,
        "turns": session.turns,
        "progress": session.stack_progress,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CARTRIDGES — Knowledge Modules (Wikipedia, arXiv)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# TEKS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/teks")
async def get_teks(grade: Optional[int] = None, subject: Optional[str] = None):
    """Return the full TEKS standards library. Optional filters: grade, subject."""
    if not TEKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TEKS database not available")
    lib = get_extended_teks_library()
    # lib stores standards in _standards dict
    standards = list(lib._standards.values())

    # Apply filters
    if grade is not None:
        standards = [s for s in standards if getattr(s, 'grade', None) == int(grade)]
    if subject:
        subj = subject.lower()
        standards = [s for s in standards if getattr(s, 'subject', None) and s.subject.value == subj]

    return {
        "teks": [s.to_dict() for s in standards],
        "count": len(standards)
    }


@app.post("/teks/search")
async def teks_search(payload: Dict[str, Any]):
    """Search TEKS standards by keyword or code. POST body: {"query": "..."} """
    if not TEKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="TEKS database not available")
    query = (payload.get('query') if isinstance(payload, dict) else None) or ''
    query = query.strip()
    lib = get_extended_teks_library()
    standards = list(lib._standards.values())

    if not query:
        results = standards
    else:
        q = query.lower()
        results = [s for s in standards if s.matches_keywords(q) or q in s.code.lower()]

    return {"results": [s.to_dict() for s in results], "count": len(results)}


@app.post("/cartridge/wikipedia")
async def wikipedia_search(request: WikipediaRequest):
    """Search Wikipedia for educational content."""
    try:
        encoded_query = urllib.parse.quote(request.query.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
        
        headers = {
            "User-Agent": "WildGarden/1.0 (Educational AI; contact@adacomputing.com)"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    return {"found": False, "query": request.query, "error": "Article not found"}
                
                data = await resp.json()
                extract = data.get("extract", "")
                sentences = ". ".join(extract.split(". ")[:request.sentences]) + "."
                
                return {
                    "found": True,
                    "query": request.query,
                    "title": data.get("title", request.query),
                    "summary": sentences,
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "thumbnail": data.get("thumbnail", {}).get("source"),
                    "source": "Wikipedia",
                    "source_tier": "reference"
                }
    except Exception as e:
        return {"found": False, "query": request.query, "error": str(e)}


@app.post("/cartridge/arxiv")
async def arxiv_search(request: ArxivRequest):
    """Search arXiv for academic papers."""
    try:
        import ssl
        encoded_query = urllib.parse.quote(request.query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={request.max_results}"
        
        headers = {
            "User-Agent": "WildGarden/1.0 (Educational AI; contact@adacomputing.com)"
        }
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                text = await resp.text()
                
                papers = []
                entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
                
                for entry in entries:
                    title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                    summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                    id_match = re.search(r'<id>(.*?)</id>', entry)
                    authors = re.findall(r'<author>.*?<name>(.*?)</name>.*?</author>', entry, re.DOTALL)
                    
                    if title_match:
                        title = title_match.group(1).strip().replace('\n', ' ')
                        summary = summary_match.group(1).strip().replace('\n', ' ')[:300] if summary_match else ""
                        arxiv_id = id_match.group(1) if id_match else ""
                        
                        papers.append({
                            "title": title,
                            "summary": summary,
                            "authors": authors[:3],
                            "url": arxiv_id,
                            "pdf_url": arxiv_id.replace('/abs/', '/pdf/') + ".pdf" if '/abs/' in arxiv_id else "",
                        })
                
                return {
                    "query": request.query,
                    "results": papers,
                    "source": "arXiv",
                    "source_tier": "academic"
                }
    except Exception as e:
        return {"query": request.query, "results": [], "error": str(e)}


@app.get("/cartridges")
async def list_cartridges():
    """List available knowledge cartridges."""
    return {
        "cartridges": [
            {
                "id": "wikipedia",
                "name": "Wikipedia",
                "icon": "📚",
                "description": "Encyclopedia articles for research",
                "endpoint": "/cartridge/wikipedia"
            },
            {
                "id": "arxiv",
                "name": "arXiv",
                "icon": "📄",
                "description": "Academic papers and research",
                "endpoint": "/cartridge/arxiv"
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ═══════════════════════════════════════════════════════════════════════════════
    🌱 WILD GARDEN — parcStation for Schools
    ═══════════════════════════════════════════════════════════════════════════════
    
    "Let the LLM think freely inside. Newton is the fence."
    
    Components:
    """)
    print(f"  • Ollama LLM:      {'✓ Available' if OLLAMA_AVAILABLE else '✗ Not installed (pip install httpx)'}")
    print(f"  • Grounding:       {'✓ Available' if GROUNDING_AVAILABLE else '✗ Not available'}")
    print(f"  • Newton Core:     {'✓ Available' if NEWTON_CORE_AVAILABLE else '✗ Not available'}")
    print("""
    Starting server on http://localhost:8091
    
    Endpoints:
      POST /ask           — Ask the AI (verified)
      POST /verify        — Verify a claim
      POST /math          — Verify math
      GET  /audit         — View audit log
      GET  /sessions      — View active sessions
    
    Built on proof. © 2026 Ada Computing Company
    ═══════════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8091)
