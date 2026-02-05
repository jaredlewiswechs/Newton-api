"""TI-Calc math layer (minimal implementation).

Provides formalized distance metrics and repair-gradient helpers used by
the live constraint checker. This is a compact, deterministic implementation
suitable for integration and unit testing; it can be replaced by a fuller
TI-Calc backend later.
"""
from typing import Optional


def bounded_normalized_distance(value: Optional[int], lo: Optional[int], hi: Optional[int]) -> float:
    """Return a normalized score in [0,1] representing how well `value` fits
    within [lo, hi]. 1.0 means fully inside; 0.0 means maximally outside.

    If bounds are missing, treat missing bounds as satisfied (score 1.0).
    """
    if value is None:
        return 1.0
    if lo is None and hi is None:
        return 1.0
    if lo is None:
        # only upper bound
        if value <= hi:
            return 1.0
        # linearly decay to 0 at 2*hi
        return max(0.0, 1.0 - (value - hi) / max(1, hi))
    if hi is None:
        if value >= lo:
            return 1.0
        return max(0.0, 1.0 - (lo - value) / max(1, lo))

    # both bounds present
    if lo <= value <= hi:
        return 1.0
    if value < lo:
        return max(0.0, 1.0 - (lo - value) / max(1, lo))
    # value > hi
    return max(0.0, 1.0 - (value - hi) / max(1, hi))


def citation_score(required: bool, found: int, min_required: Optional[int]) -> float:
    if not required:
        return 1.0
    target = min_required or 1
    if found >= target:
        return 1.0
    # linear ratio
    return max(0.0, found / target)


def combine_scores(scores: dict) -> float:
    """Combine component scores (0..1) into overall percentage [0..100].
    Use weighted average; equal weights by default.
    """
    if not scores:
        return 100.0
    vals = list(scores.values())
    avg = sum(vals) / len(vals)
    return round(avg * 100.0, 2)


__all__ = ["bounded_normalized_distance", "citation_score", "combine_scores"]
