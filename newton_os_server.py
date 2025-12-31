#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
NEWTON OS - UNIFIED SERVER
Ada speaks. Tahoe remembers. THIA sees.
═══════════════════════════════════════════════════════════════════════════

Author: Jared Lewis | Ada Computing Company | Houston, Texas
"1 == 1. The cloud is weather. We're building shelter."

Architecture:
    /verify   → Newton Core (intent verification)
    /analyze  → THIA (anomaly detection)
    /health   → Infrastructure status

One API. Multiple capabilities. Single identity.
═══════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import hashlib
import time
import re
import statistics

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

DW_AXIS = 2048
THRESHOLD = 1024
VERSION = "2.0.0"
ENGINE = f"Newton OS {VERSION}"

# ═══════════════════════════════════════════════════════════════════════════
# CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════

CONSTRAINTS = {
    "harm": {
        "name": "No Harm",
        "patterns": [
            r"(how to )?(make|build|create|construct).*\b(bomb|weapon|explosive|poison|grenade)\b",
            r"(how to )?(kill|murder|harm|hurt|injure|assassinate)",
            r"(how to )?(suicide|self.harm)",
            r"\b(i want to|i need to|help me) (kill|murder|harm|hurt)",
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
            r"(how to )?(evade|avoid|cheat).*(tax|irs)",
            r"(how to )?(launder|hide|offshore) money",
            r"(how to )?(forge|fake|counterfeit)",
        ]
    },
    "security": {
        "name": "Security",
        "patterns": [
            r"(how to )?(hack|crack|break into|exploit|bypass)",
            r"\b(steal password|phishing|malware|ransomware)\b",
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class VerifyRequest(BaseModel):
    input: str
    constraints: Optional[List[str]] = None

class AnalyzeRequest(BaseModel):
    data: List[float]
    method: Optional[str] = "zscore"
    threshold: Optional[float] = 3.0
    labels: Optional[List[str]] = None

class BatchAnalyzeRequest(BaseModel):
    datasets: Dict[str, List[float]]
    method: Optional[str] = "zscore"
    threshold: Optional[float] = 3.0

# ═══════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def fingerprint(data: Any) -> str:
    """Generate SHA-256 fingerprint."""
    h = hashlib.sha256(str(data).encode()).hexdigest()
    return h[:12].upper()

def melt(text: str) -> int:
    """Convert text to signal value."""
    cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower())
    tokens = cleaned.split()

    if not tokens:
        return DW_AXIS

    signal = DW_AXIS
    for i, token in enumerate(tokens):
        h = 0
        for char in token:
            h = ((h << 5) ^ h ^ ord(char)) & 0xFFF
        weight = (h % 400) - 200
        signal += weight

    return max(0, min(4095, signal))

def snap(signal: int) -> dict:
    """Determine verification status from signal."""
    distance = abs(signal - DW_AXIS)
    crystalline = distance <= THRESHOLD
    confidence = round((1 - distance / THRESHOLD) * 100, 1) if crystalline else 0

    return {
        "signal": signal,
        "distance": distance,
        "verified": crystalline,
        "code": 200 if crystalline else 1202,
        "confidence": confidence
    }

def check_constraints(text: str, constraint_list: List[str]) -> dict:
    """Check text against constraint patterns."""
    text_lower = text.lower()
    passed = []
    failed = []

    for key in constraint_list:
        if key not in CONSTRAINTS:
            continue

        constraint = CONSTRAINTS[key]
        violation = False

        for pattern in constraint["patterns"]:
            if re.search(pattern, text_lower):
                violation = True
                break

        if violation:
            failed.append(key)
        else:
            passed.append(key)

    return {"passed": passed, "failed": failed}

# ═══════════════════════════════════════════════════════════════════════════
# THIA - ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def thia_zscore(values: List[float], threshold: float = 3.0) -> dict:
    """Z-score anomaly detection."""
    n = len(values)
    if n < 2:
        return {"error": "Insufficient data points", "anomalies": []}

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    sd = variance ** 0.5 if variance > 0 else 0.0001

    scores = [(x - mean) / sd for x in values]
    anomalies = [i for i, z in enumerate(scores) if abs(z) > threshold]

    return {
        "method": "zscore",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "mean": round(mean, 4),
            "std_dev": round(sd, 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4)
        },
        "scores": [round(z, 4) for z in scores],
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_iqr(values: List[float], threshold: float = 1.5) -> dict:
    """IQR anomaly detection."""
    n = len(values)
    if n < 4:
        return {"error": "Insufficient data points for IQR", "anomalies": []}

    sorted_vals = sorted(values)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1

    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr

    anomalies = [i for i, v in enumerate(values) if v < lower or v > upper]

    return {
        "method": "iqr",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "q1": round(q1, 4),
            "q3": round(q3, 4),
            "iqr": round(iqr, 4),
            "lower_bound": round(lower, 4),
            "upper_bound": round(upper, 4)
        },
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_mad(values: List[float], threshold: float = 3.0) -> dict:
    """Median Absolute Deviation anomaly detection."""
    n = len(values)
    if n < 2:
        return {"error": "Insufficient data points", "anomalies": []}

    sorted_vals = sorted(values)
    median = sorted_vals[n // 2]

    abs_devs = [abs(x - median) for x in values]
    sorted_devs = sorted(abs_devs)
    mad = sorted_devs[n // 2]

    if mad == 0:
        mad = 0.0001

    scores = [abs(x - median) / mad for x in values]
    anomalies = [i for i, s in enumerate(scores) if s > threshold]

    return {
        "method": "mad",
        "threshold": threshold,
        "statistics": {
            "n": n,
            "median": round(median, 4),
            "mad": round(mad, 4)
        },
        "scores": [round(s, 4) for s in scores],
        "anomalies": anomalies,
        "anomaly_values": [round(values[i], 4) for i in anomalies],
        "n_anomalies": len(anomalies),
        "pct_anomalies": round(len(anomalies) / n * 100, 2)
    }

def thia_analyze(values: List[float], method: str = "zscore", threshold: float = 3.0) -> dict:
    """Unified THIA analysis dispatcher."""
    if method == "zscore":
        return thia_zscore(values, threshold)
    elif method == "iqr":
        return thia_iqr(values, threshold)
    elif method == "mad":
        return thia_mad(values, threshold)
    elif method == "all":
        return {
            "zscore": thia_zscore(values, threshold),
            "iqr": thia_iqr(values, 1.5),
            "mad": thia_mad(values, threshold)
        }
    else:
        return {"error": f"Unknown method: {method}. Use 'zscore', 'iqr', 'mad', or 'all'."}

# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Newton OS",
    description="Ada speaks. Tahoe remembers. THIA sees.",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 48px 24px;
        }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { font-size: 32px; font-weight: 600; margin-bottom: 8px; }
        .tagline { color: #00875a; font-size: 18px; margin-bottom: 8px; }
        .subtitle { color: #666; font-size: 14px; margin-bottom: 48px; }
        .section { margin-bottom: 40px; }
        .section-title {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #222;
        }
        .endpoint {
            background: #111;
            border: 1px solid #222;
            padding: 20px;
            margin-bottom: 12px;
        }
        .method {
            display: inline-block;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 3px;
            margin-right: 12px;
        }
        .post { background: #00875a; color: #000; }
        .get { background: #2d5a9e; color: #fff; }
        .path { font-family: 'SF Mono', monospace; font-size: 14px; }
        .desc { color: #888; font-size: 13px; margin-top: 8px; }
        pre {
            background: #161616;
            border: 1px solid #222;
            padding: 16px;
            font-family: 'SF Mono', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 12px;
        }
        .try-section { margin-top: 48px; }
        input, select {
            width: 100%;
            padding: 12px 16px;
            font-size: 14px;
            background: #111;
            border: 1px solid #333;
            color: #e0e0e0;
            font-family: inherit;
            margin-bottom: 12px;
        }
        textarea {
            width: 100%;
            padding: 12px 16px;
            font-size: 13px;
            font-family: 'SF Mono', monospace;
            background: #111;
            border: 1px solid #333;
            color: #e0e0e0;
            min-height: 100px;
            margin-bottom: 12px;
        }
        button {
            background: #00875a;
            color: #000;
            border: none;
            padding: 12px 32px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        button:hover { background: #00a06a; }
        #result {
            margin-top: 20px;
            padding: 20px;
            background: #111;
            border: 1px solid #222;
            font-family: 'SF Mono', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            display: none;
        }
        footer {
            margin-top: 64px;
            padding-top: 24px;
            border-top: 1px solid #222;
            font-size: 12px;
            color: #444;
        }
        .tabs { display: flex; gap: 0; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            background: #111;
            border: 1px solid #222;
            color: #666;
            cursor: pointer;
            font-size: 13px;
        }
        .tab.active { background: #00875a; color: #000; border-color: #00875a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Newton OS</h1>
        <p class="tagline">The free verification layer. 1 == 1</p>
        <p class="subtitle">Ada speaks. Tahoe remembers. THIA sees.</p>

        <div class="section">
            <div class="section-title">Capabilities</div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/verify</span>
                <p class="desc">Intent verification with constraint checking</p>
                <pre>{ "input": "text to verify", "constraints": ["harm", "medical", "legal", "security"] }</pre>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/analyze</span>
                <p class="desc">THIA anomaly detection for numerical data</p>
                <pre>{ "data": [45.2, 46.1, 102.4, 45.8], "method": "zscore", "threshold": 3.0 }</pre>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/health</span>
                <p class="desc">System status and engine version</p>
            </div>
        </div>

        <div class="section try-section">
            <div class="section-title">Try It</div>

            <div class="tabs">
                <div class="tab active" onclick="switchTab('verify')">Verify</div>
                <div class="tab" onclick="switchTab('analyze')">Analyze</div>
            </div>

            <div id="verify-form">
                <input type="text" id="verify-input" placeholder="Enter text to verify...">
                <button onclick="runVerify()">Verify</button>
            </div>

            <div id="analyze-form" style="display: none;">
                <textarea id="analyze-input" placeholder="Enter comma-separated numbers...&#10;Example: 45.2, 46.1, 44.8, 102.4, 45.8, 0.0, 65.2">45.2, 46.1, 44.8, 45.5, 45.9, 46.2, 45.1, 44.9, 45.3, 102.4, 45.7, 46.0, 0.0, 45.8, 65.2, 66.1</textarea>
                <select id="analyze-method">
                    <option value="zscore">Z-Score (default)</option>
                    <option value="iqr">IQR</option>
                    <option value="mad">MAD</option>
                    <option value="all">All Methods</option>
                </select>
                <button onclick="runAnalyze()">Analyze</button>
            </div>

            <div id="result"></div>
        </div>

        <footer>
            © 2025 Ada Computing Company · Houston
        </footer>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('verify-form').style.display = tab === 'verify' ? 'block' : 'none';
            document.getElementById('analyze-form').style.display = tab === 'analyze' ? 'block' : 'none';
            document.getElementById('result').style.display = 'none';
        }

        async function runVerify() {
            const input = document.getElementById('verify-input').value;
            if (!input) return;

            const res = await fetch('/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input })
            });
            const data = await res.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            document.getElementById('result').style.display = 'block';
        }

        async function runAnalyze() {
            const input = document.getElementById('analyze-input').value;
            const method = document.getElementById('analyze-method').value;
            if (!input) return;

            const data = input.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));

            const res = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data, method })
            });
            const result = await res.json();
            document.getElementById('result').textContent = JSON.stringify(result, null, 2);
            document.getElementById('result').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "engine": ENGINE,
        "capabilities": ["verify", "analyze"],
        "timestamp": int(time.time())
    }

@app.get("/constraints")
async def get_constraints():
    """List available constraints."""
    return {
        "constraints": list(CONSTRAINTS.keys()),
        "details": {k: v["name"] for k, v in CONSTRAINTS.items()}
    }

@app.get("/methods")
async def get_methods():
    """List available analysis methods."""
    return {
        "methods": ["zscore", "iqr", "mad", "all"],
        "details": {
            "zscore": "Standard deviation based detection (default threshold: 3σ)",
            "iqr": "Interquartile range based detection (default threshold: 1.5×IQR)",
            "mad": "Median absolute deviation based detection (default threshold: 3)",
            "all": "Run all methods and return combined results"
        }
    }

@app.post("/verify")
async def verify(request: VerifyRequest):
    """Verify text against constraints."""
    text = request.input.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input required")

    constraint_list = request.constraints or list(CONSTRAINTS.keys())

    # Process
    signal = melt(text)
    result = snap(signal)
    constraints = check_constraints(text, constraint_list)

    # Determine final status
    verified = result["verified"] and len(constraints["failed"]) == 0
    reason = None
    if not result["verified"]:
        reason = "Signal outside verification threshold"
    elif constraints["failed"]:
        reason = f"Constraint violation: {', '.join(constraints['failed'])}"

    # Generate fingerprint
    timestamp = int(time.time())
    fp = fingerprint(f"{signal}{result['code']}{timestamp}")

    return {
        "verified": verified,
        "code": 200 if verified else 1202,
        "signal": signal,
        "distance": result["distance"],
        "confidence": result["confidence"],
        "constraints_passed": constraints["passed"],
        "constraints_failed": constraints["failed"],
        "reason": reason,
        "fingerprint": fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Analyze data for anomalies using THIA."""
    if not request.data or len(request.data) < 2:
        raise HTTPException(status_code=400, detail="At least 2 data points required")

    # Generate input fingerprint
    input_fp = fingerprint(request.data)

    # Run analysis
    result = thia_analyze(
        values=request.data,
        method=request.method,
        threshold=request.threshold
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Generate output fingerprint
    timestamp = int(time.time())
    output_fp = fingerprint(f"{result}{timestamp}")

    # Add labels if provided
    if request.labels and len(request.labels) == len(request.data):
        if request.method != "all":
            result["anomaly_labels"] = [request.labels[i] for i in result["anomalies"]]

    return {
        "analysis": result,
        "input_fingerprint": input_fp,
        "output_fingerprint": output_fp,
        "timestamp": timestamp,
        "engine": ENGINE
    }

@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """Analyze multiple datasets in a single request."""
    results = {}
    timestamp = int(time.time())

    for name, data in request.datasets.items():
        if len(data) < 2:
            results[name] = {"error": "Insufficient data points"}
            continue

        input_fp = fingerprint(data)
        analysis = thia_analyze(data, request.method, request.threshold)
        output_fp = fingerprint(f"{analysis}{timestamp}")

        results[name] = {
            "analysis": analysis,
            "input_fingerprint": input_fp,
            "output_fingerprint": output_fp
        }

    return {
        "results": results,
        "datasets_processed": len(request.datasets),
        "timestamp": timestamp,
        "engine": ENGINE
    }

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
