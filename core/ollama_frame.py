from __future__ import annotations

"""Ollama-backed handle suggester for frame generation.

This module provides a thin adapter that asks the local Ollama model to
propose non-contentful handles (titles/section names) for a prompt. The
response must be JSON with keys matching the deterministic handles shape.
"""
from typing import Optional, Dict, Any
import json

try:
    from newton_agent.llm_ollama import OllamaClient
    _HAS_OLLAMA = True
except Exception:
    OllamaClient = None  # type: ignore
    _HAS_OLLAMA = False


def llm_suggest_handles(prompt: str, model: str = "qwen2.5:3b") -> Dict[str, Any]:
    if not _HAS_OLLAMA or OllamaClient is None:
        raise ImportError("Ollama client not available")

    client = OllamaClient(model=model)
    system = (
        "You are an assistant that only proposes non-contentful section handles"
        " for student writing. Return JSON with keys: chronological, thematic, historiographical"
        " where each value is a list of short handles (no paragraph content)."
        " Respond ONLY with JSON."
    )
    user = f"Prompt:\n{prompt}\n\nReturn JSON only."

    resp = client.generate(system_prompt=system, user_prompt=user)
    text = resp.strip()
    try:
        jstart = text.find('{')
        jtext = text[jstart:]
        data = json.loads(jtext)
    except Exception:
        raise ValueError("LLM did not return valid JSON for handle suggestions")

    return data


__all__ = ["llm_suggest_handles", "_HAS_OLLAMA"]
