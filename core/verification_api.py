from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from core.schemas import Omega
from core.live_checker import compute_envelope_distance
from core.adanpedia import fetch_witness_examples

router = APIRouter()


class LiveVerifyRequest(BaseModel):
    omega: Omega
    draft_text: str


@router.post("/verify/live")
async def verify_live(req: LiveVerifyRequest):
    try:
        result = compute_envelope_distance(req.omega, req.draft_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


class WitnessRequest(BaseModel):
    handles: Optional[List[str]] = None
    max_examples: Optional[int] = 3


@router.post("/witnesses")
async def witnesses(req: WitnessRequest):
    try:
        examples = fetch_witness_examples(req.handles, req.max_examples)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"examples": examples}


__all__ = ["router", "LiveVerifyRequest", "WitnessRequest"]
