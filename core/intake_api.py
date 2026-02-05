from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import re
from datetime import datetime

from core.schemas import Omega, CitationRequirement
from core.audit import log_event
from core.ollama_extractor import llm_extract_omega, _HAS_OLLAMA

router = APIRouter()


class IntakeRequest(BaseModel):
    prompt: str
    metadata: Dict[str, Any] = {}


def extract_omega_from_prompt(prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Omega:
    metadata = metadata or {}
    # simple regex-based extraction for MVP
    word_min = None
    word_max = None

    m = re.search(r"(\d+)[\s-]*(?:to|–|-)[\s-]*(\d+)\s+words", prompt, flags=re.I)
    if m:
        word_min = int(m.group(1))
        word_max = int(m.group(2))
    else:
        m2 = re.search(r"at least (\d+)\s+words", prompt, flags=re.I)
        if m2:
            word_min = int(m2.group(1))
        m3 = re.search(r"no more than (\d+)\s+words", prompt, flags=re.I)
        if m3:
            word_max = int(m3.group(1))

    # due date extraction (yyyy-mm-dd or mm/dd/YYYY)
    due = None
    md = re.search(r"due\s+(?:on\s+)?(\d{4}-\d{2}-\d{2})", prompt, flags=re.I)
    if md:
        try:
            due = datetime.fromisoformat(md.group(1))
        except Exception:
            due = None
    else:
        md2 = re.search(r"due\s+(?:on\s+)?(\d{1,2}/\d{1,2}/\d{4})", prompt, flags=re.I)
        if md2:
            try:
                due = datetime.strptime(md2.group(1), "%m/%d/%Y")
            except Exception:
                due = None

    cit_required = bool(re.search(r"\b(cite|citation|references|reference)\b", prompt, flags=re.I))
    citations = CitationRequirement(required=cit_required)

    omega = Omega(
        prompt=prompt,
        due_date=due,
        word_count_min=word_min,
        word_count_max=word_max,
        citations=citations,
        metadata={**(metadata or {})},
    )

    return omega


@router.post("/intake", response_model=Omega)
async def intake(req: IntakeRequest, use_llm: bool = False):
    """Intake endpoint. Set `use_llm=true` to request Ollama extraction.

    If Ollama is not available and `use_llm` is requested, returns 503.
    """
    try:
        if use_llm:
            if not _HAS_OLLAMA:
                raise HTTPException(status_code=503, detail="LLM extractor unavailable")
            o = llm_extract_omega(req.prompt, req.metadata)
        else:
            o = extract_omega_from_prompt(req.prompt, req.metadata)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Audit the intake
    try:
        log_event("intake", payload={"prompt": req.prompt}, result="ok", metadata={"word_count_min": o.word_count_min, "word_count_max": o.word_count_max})
    except Exception:
        pass

    return o


__all__ = ["router", "extract_omega_from_prompt", "IntakeRequest"]
