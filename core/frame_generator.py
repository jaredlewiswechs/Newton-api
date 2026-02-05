from __future__ import annotations

"""Frame generator (Ada handles) for Stefan.

Provides non-contentful handle set generation (multiple trajectories)
based on an `Omega` or raw prompt. This is intentionally non-creative
— it returns outline handles, not prose.
"""
from typing import Dict, List

from core.schemas import Omega


def generate_handles_from_omega(omega: Omega) -> Dict[str, List[str]]:
    prompt = omega.prompt or ""
    return generate_handles_from_prompt(prompt)


def generate_handles_from_prompt(prompt: str) -> Dict[str, List[str]]:
    """Return three handle sets: chronological, thematic, historiographical.

    Each handle set is a short list of non-contentful section handles students
    can select and expand upon. This is deterministic and safe for MVP.
    """
    # canonical short summaries to use as handles
    chronological = [
        "Introduction: context and thesis",
        "Early developments / background",
        "Middle period / turning point",
        "Later developments / consequences",
        "Conclusion: synthesis and significance",
    ]

    thematic = [
        "Theme 1: definition & scope",
        "Theme 2: evidence & examples",
        "Theme 3: counterexamples / limits",
        "Integrative analysis",
        "Conclusion: implications",
    ]

    historiographical = [
        "Traditional interpretation",
        "Revisionist perspective",
        "Methodological debates",
        "Current consensus / open questions",
        "Conclusion: where research could go next",
    ]

    # lightweight deterministic variation based on prompt length
    if prompt:
        n = len(prompt) % 3
        if n == 1:
            chronological[1] = "Background & origins"
        elif n == 2:
            thematic[1] = "Key studies & findings"

    return {
        "chronological": chronological,
        "thematic": thematic,
        "historiographical": historiographical,
    }


__all__ = ["generate_handles_from_prompt", "generate_handles_from_omega"]
