"""
NEWTON PUBLIC API
The Free Verification Layer

    def newton(current, goal):
        return current == goal

© 2025 Jared Lewis | Ada Computing Company | Houston, Texas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import hashlib
import time
import re

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DW_AXIS = 2048
THRESHOLD = 1024
VERSION = "1.0.0"

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

CONSTRAINTS = {
    "harm": {
        "name": "No Harm",
        "patterns": [
            r"how to (make|build|create).*(bomb|weapon|explosive|poison)",
            r"how to (kill|murder|harm|hurt|injure)",
            r"how to (suicide|self.harm)",
        ]
    },
    "medical": {
        "name": "Medical Bounds",
        "patterns": [
            r"what (medication|drug|dosage|prescription) should (i|you) take",
            r"diagnose (my|this|the)",
            r"prescribe (me|a)",
        ]
    },
    "legal": {
        "name": "Legal Bounds",
        "patterns": [
            r"how to (evade|avoid|cheat).*(tax|irs)",
            r"how to (launder|hide|offshore) money",
            r"how to (forge|fake|counterfeit)",
        ]
    },
    "security": {
        "name": "Security",
        "patterns": [
            r"how to (hack|crack|break into|exploit|bypass)",
            r"(steal password|phishing|malware|ransomware)",
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VerifyRequest(BaseModel):
    input: str
    constraints: Optional[List[str]] = ["harm", "medical", "legal", "security"]

class VerifyResponse(BaseModel):
    verified: bool
    code: int
    signal: int
    distance: int
    confidence: float
    constraints_passed: List[str]
    constraints_failed: List[str]
    reason: Optional[str]
    fingerprint: str
    timestamp: int
    engine: str

# ═══════════════════════════════════════════════════════════════════════════════
# NEWTON ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def newton(current, goal):
    return current == goal

def melt(text: str) -> int:
    tokens = re.sub(r'[^a-z0-9\s]', '', text.lower()).split()
    if not tokens:
        return 0
    signal = DW_AXIS
    for i, token in enumerate(tokens):
        h = sum(ord(c) << (i % 8) for c in token) & 0xFFF
        signal += (h % 400) - 200
    return max(0, min(4095, signal))

def snap(signal: int) -> dict:
    distance = abs(signal - DW_AXIS)
    crystalline = distance <= THRESHOLD
    confidence = round((1 - distance / THRESHOLD) * 100, 1) if crystalline else 0
    return {
        "signal": signal,
        "distance": distance,
        "crystalline": crystalline,
        "code": 200 if crystalline else 1202,
        "confidence": confidence
    }

def check_constraints(text: str, constraint_list: List[str]) -> dict:
    passed = []
    failed = []
    for key in constraint_list:
        if key not in CONSTRAINTS:
            continue
        constraint = CONSTRAINTS[key]
        violation = False
        for pattern in constraint["patterns"]:
            if re.search(pattern, text.lower()):
                violation = True
                break
        if violation:
            failed.append(key)
        else:
            passed.append(key)
    return {"passed": passed, "failed": failed}

def fingerprint(signal: int, code: int, ts: int) -> str:
    data = f"{signal}{code}{ts}"
    return hashlib.sha256(data.encode()).hexdigest()[:12].upper()

# ═══════════════════════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Newton API",
    description="The free verification layer. 1 == 1.",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Newton API</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #000; color: #e8e8e8; min-height: 100vh; padding: 48px 24px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 32px; font-weight: 500; margin-bottom: 8px; }
        .tagline { color: #666; margin-bottom: 48px; }
        .badge { color: #00875a; }
        .endpoint { background: #111; border: 1px solid #222; padding: 20px; margin-bottom: 16px; }
        .method { background: #00875a; color: #000; padding: 4px 8px; font-size: 12px; font-weight: 600; margin-right: 12px; }
        .path { font-family: monospace; }
        pre { background: #0a0a0a; padding: 16px; margin-top: 16px; overflow-x: auto; font-size: 13px; }
        .try-it { margin-top: 48px; }
        input, button { font-family: inherit; font-size: 15px; padding: 12px 16px; border: none; }
        input { background: #111; color: #e8e8e8; width: 100%; margin-bottom: 12px; border: 1px solid #222; }
        button { background: #00875a; color: #000; font-weight: 600; cursor: pointer; width: 100%; }
        #result { margin-top: 16px; padding: 16px; background: #0a0a0a; display: none; font-family: monospace; font-size: 13px; white-space: pre-wrap; }
        footer { margin-top: 48px; color: #444; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Newton API</h1>
        <p class="tagline">The free verification layer. <span class="badge">1 == 1</span></p>
        <div class="endpoint">
            <span class="method">POST</span><span class="path">/verify</span>
            <pre>{ "input": "text to verify", "constraints": ["harm", "medical", "legal", "security"] }</pre>
        </div>
        <div class="endpoint">
            <span class="method">GET</span><span class="path">/health</span>
            <pre>{ "status": "ok", "engine": "Newton 1.0.0" }</pre>
        </div>
        <div class="try-it">
            <h2 style="font-size: 18px; margin-bottom: 16px;">Try it</h2>
            <input type="text" id="input" placeholder="Enter text to verify...">
            <button onclick="verify()">Verify</button>
            <div id="result"></div>
        </div>
        <footer><p>© 2025 Ada Computing Company · Houston</p></footer>
    </div>
    <script>
    async function verify() {
        const input = document.getElementById('input').value;
        const result = document.getElementById('result');
        if (!input) return;
        result.style.display = 'block';
        result.textContent = 'Verifying...';
        try {
            const res = await fetch('/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input })
            });
            const data = await res.json();
            result.textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            result.textContent = 'Error: ' + e.message;
        }
    }
    document.getElementById('input').addEventListener('keypress', (e) => { if (e.key === 'Enter') verify(); });
    </script>
</body>
</html>"""

@app.get("/health")
async def health():
    return {"status": "ok", "engine": f"Newton {VERSION}"}

@app.post("/verify", response_model=VerifyResponse)
async def verify(request: VerifyRequest):
    text = request.input.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input required")
    
    signal = melt(text)
    result = snap(signal)
    constraints = check_constraints(text, request.constraints)
    verified = result["crystalline"] and len(constraints["failed"]) == 0
    ts = int(time.time())
    fp = fingerprint(signal, result["code"], ts)
    
    reason = None
    if not verified:
        if constraints["failed"]:
            reason = f"Constraint violation: {', '.join(constraints['failed'])}"
        else:
            reason = "Signal outside threshold"
    
    return VerifyResponse(
        verified=verified,
        code=200 if verified else 1202,
        signal=signal,
        distance=result["distance"],
        confidence=result["confidence"],
        constraints_passed=constraints["passed"],
        constraints_failed=constraints["failed"],
        reason=reason,
        fingerprint=fp,
        timestamp=ts,
        engine=f"Newton {VERSION}"
    )

@app.get("/constraints")
async def list_constraints():
    return {key: {"name": val["name"]} for key, val in CONSTRAINTS.items()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
