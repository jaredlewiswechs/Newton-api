"""Live constraint checker using `Omega` and a student draft.

Computes component scores (word count, citations, structure) and an overall
envelope coverage percentage plus lightweight repair suggestions.
"""
from typing import Dict, Any, List
import re

from core.schemas import Omega
from core.ti_calc import bounded_normalized_distance, citation_score, combine_scores


def count_words(text: str) -> int:
    return len(re.findall(r"\w+", text or ""))


def count_citations(text: str) -> int:
    # crude citation count: occurrences of parentheses with year or 'et al.' or 'doi'
    matches = re.findall(r"\(.*?\d{4}.*?\)|et al\.|doi:|https?://", text or "", flags=re.I)
    return len(matches)


def structure_satisfaction(omega: Omega, text: str) -> float:
    # For MVP, check presence of section headings by name (case-insensitive)
    if not omega.structure:
        return 1.0
    score = 0.0
    for s in omega.structure:
        name = s.name.lower()
        if name and name in (text or "").lower():
            score += 1.0
    return score / max(1, len(omega.structure))


def compute_envelope_distance(omega: Omega, draft_text: str) -> Dict[str, Any]:
    wc = count_words(draft_text)
    cits = count_citations(draft_text)

    wc_score = bounded_normalized_distance(wc, omega.word_count_min, omega.word_count_max)
    cit_score = citation_score(omega.citations.required, cits, omega.citations.min_count)
    struct_score = structure_satisfaction(omega, draft_text)

    scores = {
        "word_count": wc_score,
        "citations": cit_score,
        "structure": struct_score,
    }

    overall = combine_scores(scores)

    # repair suggestions (simple): indicate which components are below threshold
    suggestions: List[str] = []
    if wc_score < 1.0:
        if omega.word_count_min and wc < omega.word_count_min:
            suggestions.append(f"Increase word count to at least {omega.word_count_min} words")
        elif omega.word_count_max and wc > omega.word_count_max:
            suggestions.append(f"Reduce word count to at most {omega.word_count_max} words")
    if cit_score < 1.0:
        suggestions.append("Add more citations to meet the assignment's citation requirement")
    if struct_score < 1.0:
        suggestions.append("Include required section headings or labels listed in the assignment structure")

    return {
        "scores": scores,
        "overall_percentage": overall,
        "word_count": wc,
        "citations": cits,
        "suggestions": suggestions,
    }


__all__ = ["compute_envelope_distance"]
