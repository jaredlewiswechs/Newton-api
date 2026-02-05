from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.schemas import Omega
from core.frame_generator import generate_handles_from_omega, generate_handles_from_prompt
from core.ollama_extractor import _HAS_OLLAMA as _HAS_OLLAMA_EXTRACTOR
from core.ollama_frame import llm_suggest_handles, _HAS_OLLAMA as _HAS_OLLAMA_FRAME

router = APIRouter()


class FrameRequest(BaseModel):
    prompt: Optional[str] = None
    omega: Optional[Omega] = None


@router.post("/frames")
async def frames(req: FrameRequest, use_llm: bool = False) -> Dict[str, Any]:
    if use_llm:
        if not (_HAS_OLLAMA_FRAME or _HAS_OLLAMA_EXTRACTOR):
            raise HTTPException(status_code=503, detail="LLM unavailable for frame generation")
        # Prefer the dedicated frame suggester when available
        if _HAS_OLLAMA_FRAME:
            try:
                handles = llm_suggest_handles(req.prompt or (req.omega.prompt if req.omega else ""))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"LLM frame suggestion failed: {e}")
        else:
            # Fallback: use extractor + simple template mapping (not implemented deeply here)
            handles = generate_handles_from_prompt(req.prompt or (req.omega.prompt if req.omega else ""))
    else:
        if req.omega is not None:
            handles = generate_handles_from_omega(req.omega)
        elif req.prompt:
            handles = generate_handles_from_prompt(req.prompt)
        else:
            raise HTTPException(status_code=400, detail="Provide `prompt` or `omega` in request body")

    return {"handles": handles}


__all__ = ["router", "FrameRequest"]
