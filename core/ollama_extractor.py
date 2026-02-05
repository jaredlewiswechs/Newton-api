from __future__ import annotations

"""Optional Ollama-based Omega extractor.

This module provides `llm_extract_omega` which, when an Ollama client is
available in the workspace (`newton_agent.llm_ollama`), will call the local
LLM to parse an assignment prompt and return a validated `Omega`.

If the Ollama integration is not present, calling code should handle the
ImportError and fallback to regex extractor in `core.intake_api`.
"""
from typing import Optional, Dict
import json

from core.schemas import Omega

try:
    from newton_agent.llm_ollama import OllamaClient
    _HAS_OLLAMA = True
except Exception:
    OllamaClient = None  # type: ignore
    _HAS_OLLAMA = False


def llm_extract_omega(prompt: str, metadata: Optional[Dict] = None, model: str = "qwen2.5:3b") -> Omega:
    """Use Ollama LLM to extract an Omega JSON from `prompt`.

    This function expects the LLM to return a JSON blob matching `Omega`.
    For safety, it validates the returned JSON against the `Omega` model.
    """
    if not _HAS_OLLAMA or OllamaClient is None:
        raise ImportError("Ollama client not available in this environment")

    client = OllamaClient(model=model)
    # prompt template instructing the model to emit JSON
    system = (
        "You are a structured extractor. Parse the assignment prompt and return a JSON object"
        " matching the Omega schema with keys: prompt, word_count_min, word_count_max, citations(required bool),"
        " due_date (ISO 8601) if present, and metadata. Respond ONLY with JSON."
    )
    user = f"Assignment prompt:\n{prompt}\n\nReturn JSON only."

    resp = client.generate(system_prompt=system, user_prompt=user)
    # resp may be text; attempt to parse JSON block
    text = resp.strip()
    # try to locate first JSON object in text
    try:
        jstart = text.find('{')
        jtext = text[jstart:]
        data = json.loads(jtext)
    except Exception:
        # if parsing fails, raise
        raise ValueError("LLM did not return valid JSON for Omega extraction")

    # Validate and coerce to Omega
    return Omega(**data)


__all__ = ["llm_extract_omega", "_HAS_OLLAMA"]
