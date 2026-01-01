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
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
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
            "grounding": "operational"
        },
        "ledger": {
            "entries": len(ledger),
            "chain_valid": chain_valid
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
        "engine": ENGINE
    }


# ═══════════════════════════════════════════════════════════════════════════════
# THE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home():
    """Ask Newton interface."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton Supercomputer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
            background: #000;
            color: #e8e8e8;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .container { max-width: 600px; width: 100%; text-align: center; }
        h1 {
            font-size: 48px;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -1px;
        }
        .tagline {
            color: #666;
            font-size: 18px;
            margin-bottom: 48px;
        }
        .badge {
            color: #00875a;
            font-family: 'SF Mono', monospace;
        }
        .ask-box {
            background: #111;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        .ask-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        input {
            width: 100%;
            padding: 16px;
            font-size: 18px;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #e8e8e8;
            outline: none;
            font-family: inherit;
        }
        input:focus { border-color: #00875a; }
        button {
            width: 100%;
            padding: 16px;
            font-size: 18px;
            font-weight: 600;
            background: #00875a;
            color: #000;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 16px;
            font-family: inherit;
        }
        button:hover { background: #00a36c; }
        .result {
            background: #0a0a0a;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 24px;
            text-align: left;
            display: none;
            margin-bottom: 24px;
        }
        .result.show { display: block; }
        .result-header {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }
        .result-badge {
            font-size: 14px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            margin-right: 12px;
        }
        .result-badge.pass { background: #00875a; color: #000; }
        .result-badge.fail { background: #dc3545; color: #fff; }
        .result-time { color: #666; font-size: 14px; }
        .result-details {
            font-family: 'SF Mono', monospace;
            font-size: 13px;
            color: #888;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }
        .metric {
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 16px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            color: #00875a;
        }
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
        footer {
            margin-top: 48px;
            color: #444;
            font-size: 13px;
        }
        .endpoints {
            text-align: left;
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 16px;
            margin-top: 24px;
        }
        .endpoint {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #222;
        }
        .endpoint:last-child { border-bottom: none; }
        .method {
            background: #00875a;
            color: #000;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 4px;
            margin-right: 12px;
            font-family: 'SF Mono', monospace;
        }
        .path {
            font-family: 'SF Mono', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Newton</h1>
        <p class="tagline">The Supercomputer. <span class="badge">1 == 1</span></p>

        <div class="metrics" id="metrics">
            <div class="metric">
                <div class="metric-value" id="m-total">-</div>
                <div class="metric-label">Verifications</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="m-rate">-</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="m-time">-</div>
                <div class="metric-label">Avg Time</div>
            </div>
        </div>

        <div class="ask-box">
            <div class="ask-label">Ask Newton</div>
            <input type="text" id="query" placeholder="Enter your query...">
            <button onclick="askNewton()">Verify</button>
        </div>

        <div class="result" id="result">
            <div class="result-header">
                <span class="result-badge" id="badge">PASS</span>
                <span class="result-time" id="time">42μs</span>
            </div>
            <pre class="result-details" id="details"></pre>
        </div>

        <div class="endpoints">
            <div class="endpoint"><span class="method">POST</span><span class="path">/ask</span></div>
            <div class="endpoint"><span class="method">POST</span><span class="path">/verify</span></div>
            <div class="endpoint"><span class="method">POST</span><span class="path">/constraint</span></div>
            <div class="endpoint"><span class="method">POST</span><span class="path">/ground</span></div>
            <div class="endpoint"><span class="method">GET</span><span class="path">/ledger</span></div>
            <div class="endpoint"><span class="method">GET</span><span class="path">/metrics</span></div>
        </div>

        <footer>
            <p>© 2025-2026 Jared Lewis · Ada Computing Company · Houston</p>
            <p style="margin-top: 8px; color: #333;">The cloud is weather. We're building shelter.</p>
        </footer>
    </div>

    <script>
        async function askNewton() {
            const query = document.getElementById('query').value;
            if (!query) return;

            const resultEl = document.getElementById('result');
            const badgeEl = document.getElementById('badge');
            const timeEl = document.getElementById('time');
            const detailsEl = document.getElementById('details');

            resultEl.className = 'result show';
            detailsEl.textContent = 'Verifying...';

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await res.json();

                badgeEl.textContent = data.answer.verified ? 'VERIFIED' : 'FAILED';
                badgeEl.className = 'result-badge ' + (data.answer.verified ? 'pass' : 'fail');
                timeEl.textContent = data.elapsed_us + 'μs';
                detailsEl.textContent = JSON.stringify(data, null, 2);

                loadMetrics();
            } catch (e) {
                detailsEl.textContent = 'Error: ' + e.message;
            }
        }

        async function loadMetrics() {
            try {
                const res = await fetch('/metrics');
                const data = await res.json();
                document.getElementById('m-total').textContent = data.forge.total_evaluations;
                document.getElementById('m-rate').textContent = data.forge.pass_rate + '%';
                document.getElementById('m-time').textContent = Math.round(data.forge.avg_time_us) + 'μs';
            } catch (e) {}
        }

        document.getElementById('query').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') askNewton();
        });

        loadMetrics();
    </script>
</body>
</html>"""


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
