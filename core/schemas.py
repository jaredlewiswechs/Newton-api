from __future__ import annotations

"""
Ω (Omega) schema definitions for assignment constraints.

This module defines Pydantic models used to represent the structured
assignment envelope (Ω) produced by the intake + extractor step.
"""
from typing import Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class CitationRequirement(BaseModel):
    required: bool = False
    min_count: Optional[int] = None
    style: Optional[str] = None


class StructureConstraint(BaseModel):
    name: str
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    required: bool = False
    notes: Optional[str] = None


class Omega(BaseModel):
    """Pydantic model representing the assignment envelope (Ω).

    Fields capture explicit and implicit constraints, structural
    requirements, citation rules, and lightweight metadata.
    """

    assignment_id: Optional[str] = None
    title: Optional[str] = None
    prompt: str = Field(..., description="Original assignment prompt text")
    due_date: Optional[datetime] = None
    format: Optional[str] = None

    # quantitative constraints
    word_count_min: Optional[int] = None
    word_count_max: Optional[int] = None

    # citation and structure
    citations: CitationRequirement = Field(default_factory=CitationRequirement)
    structure: List[StructureConstraint] = Field(default_factory=list)

    # freeform constraint lists (explicitly extracted and inferred)
    explicit_constraints: List[str] = Field(default_factory=list)
    implicit_constraints: List[str] = Field(default_factory=list)

    # handles proposed by a frame generator (Ada)
    handles: List[str] = Field(default_factory=list)

    # arbitrary metadata for integration (course, section, tags, etc.)
    metadata: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_counts(self):
        lo = self.word_count_min
        hi = self.word_count_max
        if lo is not None and hi is not None:
            if lo < 0 or hi < 0:
                raise ValueError("word counts must be non-negative")
            if lo > hi:
                raise ValueError("word_count_min cannot be greater than word_count_max")
        return self


__all__ = ["Omega", "StructureConstraint", "CitationRequirement"]
