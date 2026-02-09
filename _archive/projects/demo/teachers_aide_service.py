"""Teacher's Aide service: exposes TEKS, semantic search, logic evaluation, and TI-Calc endpoints.

This is a compact FastAPI app intended for local demo and integration with the
existing `adanpedia`/`adan_portable` and `newton` core components.
"""
from typing import Optional, List, Dict, Any

# Monkey patch to fix Pydantic v1.10.x compatibility with FastAPI
import pydantic
if hasattr(pydantic, 'VERSION') and pydantic.VERSION.startswith('1.'):
    # Fix for Contact model in FastAPI openapi
    try:
        from pydantic import BaseModel, Field
        class Contact(BaseModel):
            name: Optional[str] = None
            url: Optional[str] = None
            email: Optional[str] = None

            class Config:
                extra = "allow"
        # Monkey patch into fastapi.openapi.models
        import fastapi.openapi.models
        fastapi.openapi.models.Contact = Contact
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Query, Depends, Header, Request
from pydantic import BaseModel

from tinytalk_py.education import get_teks_library
from core.logic import LogicEngine, ExecutionContext
from core.ti_calc import bounded_normalized_distance, citation_score, combine_scores
from demo.adanpedia_adapter import fetch_examples

app = FastAPI(title="Teacher's Aide Service", version="0.2")

# --- Simple API key auth + in-memory rate limiter (per-key)
_API_KEYS = {
    "demo-key": {"name": "demo", "scopes": ["read", "write"]}
}

# rate limiter state: {key: {count, window_start}}
_RATE_STATE: Dict[str, Dict[str, Any]] = {}
_RATE_LIMIT = 60  # requests
_RATE_WINDOW = 60  # seconds


def _check_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key not in _API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    # rate limiting
    import time
    now = int(time.time())
    state = _RATE_STATE.get(x_api_key)
    if not state:
        _RATE_STATE[x_api_key] = {"count": 1, "window_start": now}
        return _API_KEYS[x_api_key]

    window_start = state["window_start"]
    if now - window_start >= _RATE_WINDOW:
        # reset window
        _RATE_STATE[x_api_key] = {"count": 1, "window_start": now}
        return _API_KEYS[x_api_key]

    if state["count"] >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    state["count"] += 1
    return _API_KEYS[x_api_key]


class EvalRequest(BaseModel):
    expr: Dict[str, Any]
    bounds: Optional[Dict[str, int]] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/teks")
def list_teks(q: Optional[str] = Query(None, description="Optional keyword to filter TEKS"),
              _auth=Depends(_check_api_key)):
    teks = get_teks_library()
    if not q:
        return {"count": len(teks), "keys": list(teks.keys())}
    # simple filter by keyword in skill or knowledge
    keys = [k for k, v in teks.items() if q.lower() in (v.skill_statement + v.knowledge_statement).lower()]
    return {"count": len(keys), "keys": keys}


@app.get("/teks/{code}")
def get_teks(code: str):
    teks = get_teks_library()
    std = teks.get(code)
    if not std:
        raise HTTPException(status_code=404, detail="TEKS not found")
    # Return serializable subset
    return {
        "code": std.code,
        "grade": std.grade,
        "subject": str(std.subject.value),
        "knowledge": std.knowledge_statement,
        "skill": std.skill_statement,
        "cognitive_level": getattr(std.cognitive_level, "name", str(std.cognitive_level)),
        "prerequisites": std.prerequisite_codes or [],
        "keywords": std.keywords,
    }


@app.get("/search")
def semantic_search(q: str = Query(..., description="Query keywords"), limit: int = 5,
                    _auth=Depends(_check_api_key)):
    teks = get_teks_library()
    # Use TEKS semantic search first (if implemented)
    try:
        teks_results = teks.search(q)
        teks_hits = [{"code": r.code, "skill": r.skill_statement} for r in teks_results[:limit]]
    except Exception:
        teks_hits = []

    # Get witness examples from adanpedia adapter
    examples = fetch_examples(handles=[q], max_examples=limit)

    # If adan_portable knowledge store is available, also run store.search
    portable_hits = []
    try:
        # attempt to use adan_portable store directly (fast path)
        from adan.knowledge_store import get_knowledge_store
        ks = get_knowledge_store()
        facts = ks.search(q, limit=limit)
        portable_hits = [{"id": f.id, "key": f.key, "snippet": f.fact} for f in facts]
    except Exception:
        portable_hits = []

    return {"query": q, "teks": teks_hits, "examples": examples, "portable": portable_hits}


@app.post("/logic/evaluate")
def logic_evaluate(req: EvalRequest, _auth=Depends(_check_api_key)):
    engine = LogicEngine()
    ctx = ExecutionContext()
    if req.bounds:
        # allow caller to override subset of bounds
        for k, v in req.bounds.items():
            if hasattr(ctx.bounds, k):
                setattr(ctx.bounds, k, int(v))

    result = engine.evaluate(req.expr, context=ctx)
    return {**result.to_dict(), "trace": result.trace}


class TICalcReq(BaseModel):
    value: Optional[int] = None
    lo: Optional[int] = None
    hi: Optional[int] = None


@app.post("/ti/bounded_distance")
def ti_bounded(req: TICalcReq):
    score = bounded_normalized_distance(req.value, req.lo, req.hi)
    return {"score": score}


class CitationReq(BaseModel):
    required: bool = True
    found: int = 0
    min_required: Optional[int] = None


@app.post("/ti/citation_score")
def ti_citation(req: CitationReq):
    score = citation_score(req.required, req.found, req.min_required)
    return {"score": score}


@app.post("/ti/combine")
def ti_combine(scores: Dict[str, float]):
    return {"combined": combine_scores(scores)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8088)
