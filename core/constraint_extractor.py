#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CONSTRAINT EXTRACTOR - From Fuzzy to Formal
The bridge between natural language and verified computation.

"You're parsing it like a CONSTRAINT EXTRACTOR, not a language model."

This module transforms natural language into:
- Structured constraint trees (CDL 3.0)
- TinyTalk specifications (when/finfr/fin)
- Verified execution plans with cryptographic proofs

The key insight: LLMs are actually good at constraint extraction -
they just don't know they're doing it. This makes it explicit.

Pipeline: Natural Language → Constraint Extraction → Formal Spec → Verified Output
              (fuzzy)            (parsing)           (Newton^2)      (deterministic)

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import re
import time
import uuid

from .cdl import (
    Domain, Operator, AtomicConstraint, CompositeConstraint,
    ConditionalConstraint, RatioConstraint, parse_duration
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT CATEGORIES - What types of constraints exist in natural language?
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintCategory(Enum):
    """
    The fundamental categories of constraints extractable from natural language.

    Based on Jared's insight: Every natural language statement about requirements
    contains implicit or explicit constraints that can be formalized.
    """
    NUMERIC = "numeric"           # Quantities, counts, amounts
    TEMPORAL = "temporal"         # Time, duration, scheduling
    RELATIONAL = "relational"     # Group dynamics, consensus
    QUALITATIVE = "qualitative"   # Subjective → objective mapping
    SPATIAL = "spatial"           # Location, distance, geography
    SAFETY = "safety"             # Risk, verification, compliance
    BUDGETARY = "budgetary"       # Cost, value, affordability
    PREFERENCE = "preference"     # Wants vs requirements (soft vs hard)


class ConstraintStrength(Enum):
    """
    How binding is this constraint?

    HARD constraints trigger finfr if violated.
    SOFT constraints are preferences that can be traded off.
    IMPLICIT constraints are inferred from context.
    """
    HARD = "hard"       # Must be satisfied (finfr if violated)
    SOFT = "soft"       # Preference, can be traded off
    IMPLICIT = "implicit"  # Inferred, not explicitly stated


class ConstraintPolarity(Enum):
    """
    Is this a positive or negative constraint?

    REQUIRE: Must include/have (positive)
    FORBID: Must not include/have (negative)
    PREFER: Should include (soft positive)
    AVOID: Should not include (soft negative)
    """
    REQUIRE = "require"   # and X
    FORBID = "forbid"     # not X (finfr if X)
    PREFER = "prefer"     # should X
    AVOID = "avoid"       # should not X


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTED CONSTRAINT - The output of constraint extraction
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractedConstraint:
    """
    A constraint extracted from natural language.

    This is the intermediate representation between fuzzy natural language
    and formal CDL/TinyTalk specifications.
    """
    id: str
    category: ConstraintCategory
    strength: ConstraintStrength
    polarity: ConstraintPolarity

    # The constraint specification
    field: str                    # What is being constrained
    operator: Operator            # How it's being constrained
    value: Any                    # The constraint value

    # Context and provenance
    source_text: str              # Original natural language
    confidence: float             # Extraction confidence (0-1)
    reasoning: str                # Why this constraint was extracted

    # For complex constraints
    sub_constraints: List['ExtractedConstraint'] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    # Metadata
    domain: Domain = Domain.CUSTOM
    action: str = "reject"        # What to do if violated
    message: Optional[str] = None

    def to_cdl(self) -> Union[AtomicConstraint, CompositeConstraint]:
        """Convert to CDL constraint object."""
        if not self.sub_constraints:
            return AtomicConstraint(
                domain=self.domain,
                field=self.field,
                operator=self.operator,
                value=self.value,
                message=self.message or f"Constraint from: {self.source_text}",
                action=self.action,
                id=self.id
            )
        else:
            logic = "and" if self.polarity == ConstraintPolarity.REQUIRE else "or"
            return CompositeConstraint(
                logic=logic,
                constraints=[sub.to_cdl() for sub in self.sub_constraints],
                id=self.id
            )

    def to_tinytalk(self) -> str:
        """Convert to TinyTalk law specification."""
        op_map = {
            Operator.EQ: "==",
            Operator.NE: "!=",
            Operator.LT: "<",
            Operator.GT: ">",
            Operator.LE: "<=",
            Operator.GE: ">=",
        }

        op_str = op_map.get(self.operator, self.operator.value)
        trigger = "finfr" if self.strength == ConstraintStrength.HARD else "fin"

        if self.polarity == ConstraintPolarity.FORBID:
            return f"when(self.{self.field} {op_str} {self.value}, {trigger})"
        else:
            # Invert for require
            inverse_ops = {"<": ">=", ">": "<=", "<=": ">", ">=": "<", "==": "!="}
            inv_op = inverse_ops.get(op_str, op_str)
            return f"when(not (self.{self.field} {inv_op} {self.value}), {trigger})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "category": self.category.value,
            "strength": self.strength.value,
            "polarity": self.polarity.value,
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
            "source_text": self.source_text,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "domain": self.domain.value,
            "sub_constraints": [sub.to_dict() for sub in self.sub_constraints],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION RESULT - Full extraction output with verification certificates
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractionResult:
    """
    Complete result of constraint extraction from natural language.

    Includes the extracted constraints, verification certificates,
    and cryptographic proofs for audit trails.
    """
    id: str
    source_text: str
    timestamp: float

    # Extracted structure
    action: str                   # Primary action detected
    subject: Dict[str, Any]       # Who/what is the subject
    objects: List[Dict[str, Any]] # What is being acted upon
    constraints: List[ExtractedConstraint]

    # Verification
    all_extractable: bool         # Were all constraints extracted?
    ambiguities: List[str]        # What couldn't be resolved?
    assumptions: List[str]        # What was assumed?

    # Cryptographic proof
    merkle_root: str
    signature: str

    def generate_proof(self) -> str:
        """Generate merkle proof of extraction."""
        data = json.dumps({
            "source": self.source_text,
            "constraints": [c.to_dict() for c in self.constraints],
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def to_cdl_spec(self) -> Dict[str, Any]:
        """Generate CDL specification from extraction."""
        return {
            "when": self.action,
            "constraints": [c.to_cdl() for c in self.constraints],
            "verification": {
                "merkle_root": self.merkle_root,
                "timestamp": self.timestamp
            }
        }

    def to_tinytalk_blueprint(self, name: str = "ExtractedPlan") -> str:
        """Generate TinyTalk Blueprint class from extraction."""
        lines = [
            f"class {name}(Blueprint):",
            f'    """Auto-generated from: {self.source_text[:50]}..."""',
            "",
        ]

        # Add fields for each constraint
        fields_added = set()
        for c in self.constraints:
            if c.field not in fields_added:
                lines.append(f"    {c.field} = field(Any, default=None)")
                fields_added.add(c.field)

        lines.append("")

        # Add laws for each constraint
        for i, c in enumerate(self.constraints):
            if c.strength == ConstraintStrength.HARD:
                lines.append(f"    @law")
                lines.append(f"    def constraint_{i}(self):")
                lines.append(f'        """{c.source_text}"""')
                lines.append(f"        {c.to_tinytalk()}")
                lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "source_text": self.source_text,
            "timestamp": self.timestamp,
            "action": self.action,
            "subject": self.subject,
            "objects": self.objects,
            "constraints": [c.to_dict() for c in self.constraints],
            "all_extractable": self.all_extractable,
            "ambiguities": self.ambiguities,
            "assumptions": self.assumptions,
            "verification": {
                "merkle_root": self.merkle_root,
                "signature": self.signature
            }
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION PATTERNS - Natural Language → Constraint Mapping
# ═══════════════════════════════════════════════════════════════════════════════

class ExtractionPatterns:
    """
    Pattern matching for constraint extraction.

    These patterns recognize natural language expressions and map them
    to formal constraints. Each pattern includes:
    - Regex for matching
    - Extraction logic
    - Constraint type mapping
    """

    # ─────────────────────────────────────────────────────────────────────────
    # NUMERIC PATTERNS
    # ─────────────────────────────────────────────────────────────────────────

    NUMERIC_PATTERNS = {
        # "at least X"
        "at_least": (
            r'\bat\s+least\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.GE,
            ConstraintPolarity.REQUIRE
        ),
        # "at most X"
        "at_most": (
            r'\bat\s+most\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.LE,
            ConstraintPolarity.REQUIRE
        ),
        # "no more than X"
        "no_more_than": (
            r'\bno\s+more\s+than\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.LE,
            ConstraintPolarity.FORBID
        ),
        # "no less than X"
        "no_less_than": (
            r'\bno\s+less\s+than\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.GE,
            ConstraintPolarity.FORBID
        ),
        # "exactly X"
        "exactly": (
            r'\bexactly\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.EQ,
            ConstraintPolarity.REQUIRE
        ),
        # "X or more"
        "or_more": (
            r'\b(\d+(?:\.\d+)?)\s+or\s+more\s*(\w+)?',
            Operator.GE,
            ConstraintPolarity.REQUIRE
        ),
        # "X or fewer"
        "or_fewer": (
            r'\b(\d+(?:\.\d+)?)\s+or\s+(?:fewer|less)\s*(\w+)?',
            Operator.LE,
            ConstraintPolarity.REQUIRE
        ),
        # "between X and Y"
        "between": (
            r'\bbetween\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            None,  # Special handling for range
            ConstraintPolarity.REQUIRE
        ),
        # "under X" / "below X"
        "under": (
            r'\b(?:under|below)\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.LT,
            ConstraintPolarity.REQUIRE
        ),
        # "over X" / "above X"
        "over": (
            r'\b(?:over|above)\s+(\d+(?:\.\d+)?)\s*(\w+)?',
            Operator.GT,
            ConstraintPolarity.REQUIRE
        ),
    }

    # ─────────────────────────────────────────────────────────────────────────
    # TEMPORAL PATTERNS
    # ─────────────────────────────────────────────────────────────────────────

    TEMPORAL_PATTERNS = {
        # "before X"
        "before": (
            r'\bbefore\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}(?::\d{2})?)',
            Operator.BEFORE,
            ConstraintPolarity.REQUIRE
        ),
        # "after X"
        "after": (
            r'\bafter\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}(?::\d{2})?)',
            Operator.AFTER,
            ConstraintPolarity.REQUIRE
        ),
        # "within X hours/days"
        "within_duration": (
            r'\bwithin\s+(\d+)\s*(hour|day|week|month)s?',
            Operator.WITHIN,
            ConstraintPolarity.REQUIRE
        ),
        # "for X weeks/days"
        "for_duration": (
            r'\bfor\s+(\d+)\s*(week|day|month|year)s?',
            None,  # Duration extraction
            ConstraintPolarity.REQUIRE
        ),
        # "no later than"
        "no_later_than": (
            r'\bno\s+later\s+than\s+(.+?)(?:\.|,|$)',
            Operator.LE,
            ConstraintPolarity.FORBID
        ),
        # "in X" (months, like "in December")
        "in_month": (
            r'\bin\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
            Operator.EQ,
            ConstraintPolarity.REQUIRE
        ),
    }

    # ─────────────────────────────────────────────────────────────────────────
    # QUALITATIVE → QUANTITATIVE PATTERNS
    # "nothing too expensive" → cost < threshold
    # ─────────────────────────────────────────────────────────────────────────

    # Maps qualitative terms to what they MEAN (not what we want)
    # When negated, the operator is inverted to create the constraint
    QUALITATIVE_INVERSIONS = {
        # Budget qualifiers - describe what the word MEANS
        # "expensive" means high cost, negated → we want cost < high
        "expensive": ("cost", Operator.GE, "high"),      # expensive = high cost
        "cheap": ("cost", Operator.LE, "low"),           # cheap = low cost
        "affordable": ("cost", Operator.LE, "moderate"), # affordable = moderate cost
        "budget": ("cost", Operator.LE, "low"),          # budget = low cost
        "luxury": ("quality", Operator.GE, "high"),      # luxury = high quality

        # Safety qualifiers
        "safe": ("safety_rating", Operator.GE, "high"),  # safe = high safety
        "dangerous": ("safety_rating", Operator.LE, "low"),  # dangerous = low safety
        "risky": ("risk_level", Operator.GE, "moderate"),    # risky = high risk
        "secure": ("security_level", Operator.GE, "high"),   # secure = high security

        # Time qualifiers
        "early": ("time", Operator.LE, "morning"),   # early = morning time
        "late": ("time", Operator.GE, "evening"),    # late = evening time
        "night": ("time", Operator.GE, "night"),     # night = night time

        # Quality qualifiers
        "good": ("quality", Operator.GE, "good"),        # good = high quality
        "bad": ("quality", Operator.LE, "acceptable"),   # bad = low quality
        "excellent": ("quality", Operator.GE, "excellent"),

        # Size qualifiers
        "small": ("size", Operator.LE, "medium"),
        "large": ("size", Operator.GE, "medium"),
        "big": ("size", Operator.GE, "large"),
    }

    # Negation patterns that invert constraints
    NEGATION_PATTERNS = [
        r"\bnot?\b",
        r"\bno\b",
        r"\bnever\b",
        r"\bdon't\b",
        r"\bdoesn't\b",
        r"\bwon't\b",
        r"\bwouldn't\b",
        r"\bcan't\b",
        r"\bnot\s+(?:a|an)\b",
        r"\bnone\b",
        r"\bnothing\b",
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # RELATIONAL/GROUP PATTERNS
    # ─────────────────────────────────────────────────────────────────────────

    GROUP_PATTERNS = {
        # "X friends" / "X people"
        "group_size": (
            r'\b(\d+)\s*(?:friends?|people|persons?|members?|guests?)',
            "group_size",
            Operator.EQ
        ),
        # "all of us" / "everyone"
        "all": (
            r'\b(?:all\s+of\s+us|everyone|everybody|the\s+whole\s+group)',
            "consensus",
            Operator.EQ
        ),
        # "at least X people agree"
        "consensus": (
            r'\b(?:at\s+least\s+)?(\d+)\s*(?:people|of\s+us)?\s*(?:agree|approve|confirm)',
            "min_agreement",
            Operator.GE
        ),
    }

    # ─────────────────────────────────────────────────────────────────────────
    # PREFERENCE vs REQUIREMENT PATTERNS
    # ─────────────────────────────────────────────────────────────────────────

    HARD_CONSTRAINT_MARKERS = [
        r"\bmust\b",
        r"\brequire[ds]?\b",
        r"\bneed[s]?\b",
        r"\bhas\s+to\b",
        r"\bhave\s+to\b",
        r"\bessential\b",
        r"\bmandatory\b",
        r"\bcritical\b",
        r"\bnon-?negotiable\b",
    ]

    SOFT_CONSTRAINT_MARKERS = [
        r"\bwant[s]?\b",
        r"\bwould\s+like\b",
        r"\bprefer[s]?\b",
        r"\bhope[s]?\b",
        r"\bideally\b",
        r"\bif\s+possible\b",
        r"\bnice\s+to\s+have\b",
        r"\boptional\b",
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT EXTRACTOR - The main extraction engine
# ═══════════════════════════════════════════════════════════════════════════════

class ConstraintExtractor:
    """
    Extract formal constraints from natural language input.

    This is the bridge between fuzzy human language and deterministic
    Newton verification. It parses natural language like a compiler,
    not like an LLM.

    Pipeline:
    1. Tokenize and normalize input
    2. Extract explicit constraints (numbers, times, requirements)
    3. Infer implicit constraints (inversions, negations)
    4. Detect constraint strength (must vs want)
    5. Resolve ambiguities or flag for clarification
    6. Generate formal CDL/TinyTalk specification
    7. Compute verification certificates
    """

    def __init__(self):
        # Compile all patterns
        self._numeric_re = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, (pattern, _, _) in ExtractionPatterns.NUMERIC_PATTERNS.items()
        }

        self._temporal_re = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, (pattern, _, _) in ExtractionPatterns.TEMPORAL_PATTERNS.items()
        }

        self._group_re = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, (pattern, _, _) in ExtractionPatterns.GROUP_PATTERNS.items()
        }

        self._hard_markers = [
            re.compile(p, re.IGNORECASE)
            for p in ExtractionPatterns.HARD_CONSTRAINT_MARKERS
        ]

        self._soft_markers = [
            re.compile(p, re.IGNORECASE)
            for p in ExtractionPatterns.SOFT_CONSTRAINT_MARKERS
        ]

        self._negation_re = [
            re.compile(p, re.IGNORECASE)
            for p in ExtractionPatterns.NEGATION_PATTERNS
        ]

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract all constraints from natural language text.

        Returns a complete ExtractionResult with:
        - All extracted constraints
        - Verification certificates
        - Ambiguities and assumptions
        """
        text = text.strip()
        extraction_id = f"EX_{hashlib.sha256(f'{text}{time.time()}'.encode()).hexdigest()[:12]}"
        timestamp = time.time()

        constraints: List[ExtractedConstraint] = []
        ambiguities: List[str] = []
        assumptions: List[str] = []

        # Split into sentences for analysis
        sentences = self._split_sentences(text)

        # Extract action and subject
        action, subject = self._extract_action_subject(text)
        objects = self._extract_objects(text)

        # Process each sentence
        for sentence in sentences:
            # Extract numeric constraints
            numeric_constraints = self._extract_numeric_constraints(sentence)
            constraints.extend(numeric_constraints)

            # Extract temporal constraints
            temporal_constraints = self._extract_temporal_constraints(sentence)
            constraints.extend(temporal_constraints)

            # Extract qualitative constraints (inversions)
            qualitative_constraints = self._extract_qualitative_constraints(sentence)
            constraints.extend(qualitative_constraints)

            # Extract group/relational constraints
            group_constraints = self._extract_group_constraints(sentence)
            constraints.extend(group_constraints)

        # Detect any unresolved ambiguities
        ambiguities.extend(self._detect_ambiguities(text, constraints))

        # Document assumptions made
        assumptions.extend(self._document_assumptions(constraints))

        # Generate cryptographic proofs
        result = ExtractionResult(
            id=extraction_id,
            source_text=text,
            timestamp=timestamp,
            action=action,
            subject=subject,
            objects=objects,
            constraints=constraints,
            all_extractable=len(ambiguities) == 0,
            ambiguities=ambiguities,
            assumptions=assumptions,
            merkle_root="",  # Will be computed
            signature=""     # Will be computed
        )

        result.merkle_root = result.generate_proof()
        result.signature = f"newton_{result.merkle_root[:16]}"

        return result

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences for processing."""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        # Also split on semicolons and significant conjunctions
        expanded = []
        for s in sentences:
            parts = re.split(r'[;]|(?:,\s*(?:and|but|or)\s+)', s)
            expanded.extend(p.strip() for p in parts if p.strip())
        return expanded

    def _extract_action_subject(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extract the primary action and subject."""
        text_lower = text.lower()

        # Common action verbs
        actions = {
            "take": r'\b(?:take|bring|transport)\b',
            "plan": r'\b(?:plan|organize|arrange)\b',
            "book": r'\b(?:book|reserve|schedule)\b',
            "buy": r'\b(?:buy|purchase|get)\b',
            "find": r'\b(?:find|search|look for)\b',
            "calculate": r'\b(?:calculate|compute|determine)\b',
            "verify": r'\b(?:verify|check|validate)\b',
        }

        detected_action = "unknown"
        for action, pattern in actions.items():
            if re.search(pattern, text_lower):
                detected_action = action
                break

        # Extract subject (usually "I", "we", or a named entity)
        subject = {"type": "individual", "count": 1}

        if re.search(r'\bwe\b|\bour\b|\bus\b', text_lower):
            subject["type"] = "group"
            # Try to find group size
            match = re.search(r'\b(\d+)\s*(?:friends?|people|of us)', text_lower)
            if match:
                # Add 1 for the speaker
                subject["count"] = int(match.group(1)) + 1

        if re.search(r'\bmy\s+(\d+)\s*friends?', text_lower):
            match = re.search(r'\bmy\s+(\d+)\s*friends?', text_lower)
            if match:
                subject["count"] = int(match.group(1)) + 1
                subject["type"] = "group"

        return detected_action, subject

    def _extract_objects(self, text: str) -> List[Dict[str, Any]]:
        """Extract objects being acted upon."""
        objects = []

        # Location patterns
        location_match = re.search(
            r'\bto\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            text
        )
        if location_match:
            objects.append({
                "type": "location",
                "value": location_match.group(1)
            })

        # Duration patterns
        duration_match = re.search(
            r'\bfor\s+(\d+)\s*(day|week|month|year)s?',
            text.lower()
        )
        if duration_match:
            objects.append({
                "type": "duration",
                "value": int(duration_match.group(1)),
                "unit": duration_match.group(2)
            })

        return objects

    def _extract_numeric_constraints(self, text: str) -> List[ExtractedConstraint]:
        """Extract numeric constraints from text."""
        constraints = []
        text_lower = text.lower()

        for name, (pattern_str, op, polarity) in ExtractionPatterns.NUMERIC_PATTERNS.items():
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.findall(text_lower)

            for match in matches:
                if isinstance(match, tuple):
                    value = float(match[0])
                    unit = match[1] if len(match) > 1 else None
                else:
                    value = float(match)
                    unit = None

                # Handle "between X and Y" specially
                if name == "between" and isinstance(match, tuple) and len(match) >= 2:
                    # Create two constraints: >= X and <= Y
                    field_name = match[2] if len(match) > 2 and match[2] else "value"

                    constraints.append(ExtractedConstraint(
                        id=self._generate_id(text, "lower"),
                        category=ConstraintCategory.NUMERIC,
                        strength=self._detect_strength(text),
                        polarity=ConstraintPolarity.REQUIRE,
                        field=field_name,
                        operator=Operator.GE,
                        value=float(match[0]),
                        source_text=text,
                        confidence=0.9,
                        reasoning=f"Extracted lower bound from 'between {match[0]} and {match[1]}'"
                    ))

                    constraints.append(ExtractedConstraint(
                        id=self._generate_id(text, "upper"),
                        category=ConstraintCategory.NUMERIC,
                        strength=self._detect_strength(text),
                        polarity=ConstraintPolarity.REQUIRE,
                        field=field_name,
                        operator=Operator.LE,
                        value=float(match[1]),
                        source_text=text,
                        confidence=0.9,
                        reasoning=f"Extracted upper bound from 'between {match[0]} and {match[1]}'"
                    ))
                else:
                    field_name = unit if unit else "count"

                    constraints.append(ExtractedConstraint(
                        id=self._generate_id(text, name),
                        category=ConstraintCategory.NUMERIC,
                        strength=self._detect_strength(text),
                        polarity=polarity,
                        field=field_name,
                        operator=op,
                        value=value,
                        source_text=text,
                        confidence=0.85,
                        reasoning=f"Extracted from '{name}' pattern: {pattern_str}"
                    ))

        return constraints

    def _extract_temporal_constraints(self, text: str) -> List[ExtractedConstraint]:
        """Extract temporal constraints from text."""
        constraints = []
        text_lower = text.lower()

        for name, (pattern_str, op, polarity) in ExtractionPatterns.TEMPORAL_PATTERNS.items():
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.findall(text_lower)

            for match in matches:
                if isinstance(match, tuple):
                    value = match[0]
                    unit = match[1] if len(match) > 1 else None
                else:
                    value = match
                    unit = None

                field_name = "time" if not unit else f"duration_{unit}"

                constraints.append(ExtractedConstraint(
                    id=self._generate_id(text, name),
                    category=ConstraintCategory.TEMPORAL,
                    strength=self._detect_strength(text),
                    polarity=polarity,
                    field=field_name,
                    operator=op if op else Operator.EQ,
                    value=value,
                    source_text=text,
                    confidence=0.8,
                    reasoning=f"Extracted from temporal pattern: {name}"
                ))

        return constraints

    def _extract_qualitative_constraints(self, text: str) -> List[ExtractedConstraint]:
        """
        Extract qualitative constraints and invert them to quantitative.

        "nothing too expensive" → cost < high_threshold
        "should be safe" → safety_rating >= high
        "not night people" → activities.end_time < evening
        """
        constraints = []
        text_lower = text.lower()

        # Check for each qualitative term
        for qualifier, (field, operator, level) in ExtractionPatterns.QUALITATIVE_INVERSIONS.items():
            if re.search(rf'\b{qualifier}\b', text_lower):
                # Check for negation
                is_negated = self._is_negated(text_lower, qualifier)

                # Invert operator if negated
                if is_negated:
                    operator = self._invert_operator(operator)
                    polarity = ConstraintPolarity.FORBID
                else:
                    polarity = ConstraintPolarity.REQUIRE

                # Map qualitative levels to numeric thresholds
                level_thresholds = {
                    "high": 0.8,
                    "moderate": 0.5,
                    "low": 0.3,
                    "morning": 9,      # 9 AM
                    "evening": 18,     # 6 PM
                    "night": 21,       # 9 PM
                    "good": 0.7,
                    "excellent": 0.9,
                    "acceptable": 0.5,
                    "medium": 0.5,
                    "large": 0.7,
                }

                value = level_thresholds.get(level, 0.5)

                constraints.append(ExtractedConstraint(
                    id=self._generate_id(text, qualifier),
                    category=ConstraintCategory.QUALITATIVE,
                    strength=self._detect_strength(text),
                    polarity=polarity,
                    field=field,
                    operator=operator,
                    value=value,
                    source_text=text,
                    confidence=0.75,
                    reasoning=f"Inverted qualitative '{qualifier}' to quantitative constraint on {field}"
                ))

        return constraints

    def _extract_group_constraints(self, text: str) -> List[ExtractedConstraint]:
        """Extract group and relational constraints."""
        constraints = []
        text_lower = text.lower()

        for name, (pattern_str, field, op) in ExtractionPatterns.GROUP_PATTERNS.items():
            pattern = re.compile(pattern_str, re.IGNORECASE)
            matches = pattern.findall(text_lower)

            for match in matches:
                if isinstance(match, tuple):
                    value = match[0]
                else:
                    value = match

                # Convert numeric strings
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    if value in ["all", "everyone", "everybody"]:
                        value = "unanimous"

                constraints.append(ExtractedConstraint(
                    id=self._generate_id(text, name),
                    category=ConstraintCategory.RELATIONAL,
                    strength=ConstraintStrength.HARD,
                    polarity=ConstraintPolarity.REQUIRE,
                    field=field,
                    operator=op,
                    value=value,
                    source_text=text,
                    confidence=0.85,
                    reasoning=f"Extracted group constraint from '{name}' pattern"
                ))

        return constraints

    def _is_negated(self, text: str, term: str) -> bool:
        """Check if a term is negated in the text."""
        # Look for negation words before the term
        for negation_pattern in self._negation_re:
            # Check if negation appears within 5 words before the term
            pattern = rf'{negation_pattern.pattern}\s+(?:\w+\s+){{0,5}}{term}'
            if re.search(pattern, text):
                return True
        return False

    def _invert_operator(self, op: Operator) -> Operator:
        """Invert an operator (for negation)."""
        inversions = {
            Operator.LT: Operator.GE,
            Operator.LE: Operator.GT,
            Operator.GT: Operator.LE,
            Operator.GE: Operator.LT,
            Operator.EQ: Operator.NE,
            Operator.NE: Operator.EQ,
        }
        return inversions.get(op, op)

    def _detect_strength(self, text: str) -> ConstraintStrength:
        """Detect if constraint is hard or soft."""
        text_lower = text.lower()

        # Check for hard constraint markers
        for pattern in self._hard_markers:
            if pattern.search(text_lower):
                return ConstraintStrength.HARD

        # Check for soft constraint markers
        for pattern in self._soft_markers:
            if pattern.search(text_lower):
                return ConstraintStrength.SOFT

        # Default to implicit (inferred)
        return ConstraintStrength.IMPLICIT

    def _detect_ambiguities(
        self,
        text: str,
        constraints: List[ExtractedConstraint]
    ) -> List[str]:
        """Detect unresolved ambiguities in the extraction."""
        ambiguities = []

        # Check for undefined thresholds
        if re.search(r'\btoo\s+\w+\b', text.lower()):
            # "too expensive", "too far", etc. - need to define threshold
            match = re.search(r'\btoo\s+(\w+)', text.lower())
            if match:
                qualifier = match.group(1)
                ambiguities.append(
                    f"Threshold for 'too {qualifier}' not defined - using default"
                )

        # Check for vague quantities
        vague_quantities = [
            (r'\bseveral\b', "several"),
            (r'\bfew\b', "few"),
            (r'\bmany\b', "many"),
            (r'\bsome\b', "some"),
        ]

        for pattern, word in vague_quantities:
            if re.search(pattern, text.lower()):
                ambiguities.append(
                    f"Vague quantity '{word}' detected - specific number recommended"
                )

        return ambiguities

    def _document_assumptions(
        self,
        constraints: List[ExtractedConstraint]
    ) -> List[str]:
        """Document assumptions made during extraction."""
        assumptions = []

        for c in constraints:
            if c.category == ConstraintCategory.QUALITATIVE:
                assumptions.append(
                    f"Assumed {c.field} threshold of {c.value} for qualitative term"
                )

            if c.strength == ConstraintStrength.IMPLICIT:
                assumptions.append(
                    f"Constraint '{c.field} {c.operator.value} {c.value}' inferred from context"
                )

        return assumptions

    def _generate_id(self, text: str, suffix: str) -> str:
        """Generate unique constraint ID."""
        data = f"{text}:{suffix}:{time.time()}"
        return f"C_{hashlib.sha256(data.encode()).hexdigest()[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFIED PLAN GENERATOR - From constraints to executable plan
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VerificationCertificate:
    """A certificate proving a constraint was satisfied."""
    constraint_id: str
    constraint_description: str
    verified: bool
    actual_value: Any
    expected_value: Any
    timestamp: float
    proof_hash: str


@dataclass
class VerifiedPlan:
    """
    A plan that has been verified against all extracted constraints.

    This is Newton^2's output: not "I think this is good" but
    "This IS verified to satisfy all constraints."
    """
    id: str
    name: str
    source_extraction: ExtractionResult

    # The plan content
    items: List[Dict[str, Any]]
    summary: Dict[str, Any]

    # Verification
    certificates: List[VerificationCertificate]
    all_verified: bool

    # Cryptographic proof
    merkle_root: str
    signature: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "verified": self.all_verified,
            "items": self.items,
            "summary": self.summary,
            "certificates": [
                {
                    "constraint": c.constraint_description,
                    "verified": c.verified,
                    "actual": c.actual_value,
                    "expected": c.expected_value
                }
                for c in self.certificates
            ],
            "proof": {
                "merkle_root": self.merkle_root,
                "signature": self.signature,
                "timestamp": self.timestamp
            }
        }


class PlanVerifier:
    """
    Verify a plan against extracted constraints.

    This takes a proposed plan and the constraints extracted from
    user input, then verifies each constraint is satisfied.
    """

    def verify(
        self,
        plan: Dict[str, Any],
        extraction: ExtractionResult
    ) -> VerifiedPlan:
        """
        Verify a plan against extracted constraints.

        Returns a VerifiedPlan with certificates for each constraint.
        """
        plan_id = f"VP_{hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:12]}"
        timestamp = time.time()

        certificates = []

        for constraint in extraction.constraints:
            cert = self._verify_constraint(constraint, plan)
            certificates.append(cert)

        all_verified = all(c.verified for c in certificates)

        # Generate merkle proof
        proof_data = json.dumps({
            "plan": plan,
            "certificates": [
                {"id": c.constraint_id, "verified": c.verified}
                for c in certificates
            ],
            "timestamp": timestamp
        }, sort_keys=True)

        merkle_root = hashlib.sha256(proof_data.encode()).hexdigest()

        return VerifiedPlan(
            id=plan_id,
            name=plan.get("name", "Verified Plan"),
            source_extraction=extraction,
            items=plan.get("items", []),
            summary=plan.get("summary", {}),
            certificates=certificates,
            all_verified=all_verified,
            merkle_root=merkle_root,
            signature=f"newton_verified_{merkle_root[:16]}",
            timestamp=timestamp
        )

    def _verify_constraint(
        self,
        constraint: ExtractedConstraint,
        plan: Dict[str, Any]
    ) -> VerificationCertificate:
        """Verify a single constraint against the plan."""
        # Extract the value from the plan
        actual_value = self._extract_value(plan, constraint.field)
        expected_value = constraint.value

        # Evaluate the constraint
        verified = self._evaluate(actual_value, constraint.operator, expected_value)

        return VerificationCertificate(
            constraint_id=constraint.id,
            constraint_description=f"{constraint.field} {constraint.operator.value} {expected_value}",
            verified=verified,
            actual_value=actual_value,
            expected_value=expected_value,
            timestamp=time.time(),
            proof_hash=hashlib.sha256(
                f"{constraint.id}:{verified}:{time.time()}".encode()
            ).hexdigest()[:16]
        )

    def _extract_value(self, plan: Dict[str, Any], field: str) -> Any:
        """Extract a value from the plan by field path."""
        parts = field.split(".")
        value = plan

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                idx = int(part)
                value = value[idx] if idx < len(value) else None
            else:
                return None

        return value

    def _evaluate(self, actual: Any, operator: Operator, expected: Any) -> bool:
        """Evaluate if actual value satisfies constraint."""
        if actual is None:
            return False

        try:
            if operator == Operator.EQ:
                return actual == expected
            elif operator == Operator.NE:
                return actual != expected
            elif operator == Operator.LT:
                return float(actual) < float(expected)
            elif operator == Operator.GT:
                return float(actual) > float(expected)
            elif operator == Operator.LE:
                return float(actual) <= float(expected)
            elif operator == Operator.GE:
                return float(actual) >= float(expected)
            elif operator == Operator.CONTAINS:
                return expected in actual
            elif operator == Operator.IN:
                return actual in expected
            else:
                return False
        except (ValueError, TypeError):
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Global extractor instance
_extractor: Optional[ConstraintExtractor] = None

def get_extractor() -> ConstraintExtractor:
    """Get or create the global constraint extractor."""
    global _extractor
    if _extractor is None:
        _extractor = ConstraintExtractor()
    return _extractor


def extract_constraints(text: str) -> ExtractionResult:
    """
    Extract constraints from natural language text.

    This is the main entry point for constraint extraction.

    Example:
        result = extract_constraints(
            "I want to take my 4 friends to Costa Rica for 2 weeks in December. "
            "Nothing too expensive, but it should be safe and fun."
        )

        print(result.constraints)  # List of ExtractedConstraint objects
        print(result.to_tinytalk_blueprint())  # TinyTalk code
    """
    return get_extractor().extract(text)


def verify_plan(plan: Dict[str, Any], extraction: ExtractionResult) -> VerifiedPlan:
    """
    Verify a plan against extracted constraints.

    Returns a VerifiedPlan with certificates proving each constraint
    was (or wasn't) satisfied.
    """
    verifier = PlanVerifier()
    return verifier.verify(plan, extraction)
