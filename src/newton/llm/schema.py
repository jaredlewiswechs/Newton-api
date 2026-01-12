"""
NEWTON LLM CONSTRAINT SCHEMA - Universal Claim and Validation Types
═══════════════════════════════════════════════════════════════════════════════

"LLM proposes → Validator decides → LLM repairs → repeat"

This module defines the universal schema that all LLM claims must conform to,
and the validation results that all domain validators must return.

The key insight: meaning lives in validators, not tokens.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
from enum import Enum
import hashlib
import time
import json


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN TYPES - What constraint systems exist
# ═══════════════════════════════════════════════════════════════════════════════

class Domain(str, Enum):
    """
    The domains of constraint validation.

    Each domain has its own validator that encodes ground truth.
    The LLM knows nothing; validators know everything.
    """
    PHYSICS = "physics"     # Kinematic/kinetic constraints
    MATH = "math"           # Symbolic equality, arithmetic
    LOGIC = "logic"         # Propositional consistency
    POLICY = "policy"       # Rule tables, forbidden content
    TEMPORAL = "temporal"   # Time ordering, duration bounds
    FINANCIAL = "financial" # Budget, cost constraints
    UNKNOWN = "unknown"     # Unvalidatable domain


DomainLiteral = Literal["physics", "math", "logic", "policy", "temporal", "financial", "unknown"]


# ═══════════════════════════════════════════════════════════════════════════════
# CLAIM - What the LLM outputs
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Claim:
    """
    A single atomic claim from the LLM.

    The LLM must emit only this structure. No prose. No hedging.
    Each claim is validated independently by the appropriate domain validator.

    Rules:
    - text: The atomic claim (one fact, one equation, one statement)
    - domain: Which validator handles this claim
    - metadata: Optional context for the validator
    """
    text: str
    domain: Domain
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Normalize domain if string
        if isinstance(self.domain, str):
            self.domain = Domain(self.domain)

    @property
    def fingerprint(self) -> str:
        """Unique identifier for this claim."""
        data = f"{self.text}|{self.domain.value}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "text": self.text,
            "domain": self.domain.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        """Create from dictionary (e.g., parsed JSON)."""
        return cls(
            text=data["text"],
            domain=Domain(data["domain"]),
            metadata=data.get("metadata", {}),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION RESULT - What validators return
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """
    The result of validating a claim against domain constraints.

    This is the only thing that matters. The LLM's confidence is irrelevant.
    Only the validator's verdict counts.

    Fields:
    - valid: Boolean ground truth
    - domain: Which validator checked this
    - rule: Which specific rule was applied
    - message: Human-readable explanation (for repair prompts)
    - details: Optional structured data about the validation
    """
    valid: bool
    domain: Domain
    rule: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if isinstance(self.domain, str):
            self.domain = Domain(self.domain)

    @property
    def proof_hash(self) -> str:
        """Cryptographic proof of this validation."""
        data = json.dumps({
            "valid": self.valid,
            "domain": self.domain.value,
            "rule": self.rule,
            "timestamp": self.timestamp,
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "valid": self.valid,
            "domain": self.domain.value,
            "rule": self.rule,
            "message": self.message,
            "details": self.details,
            "proof_hash": self.proof_hash,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLAIM BATCH - Multiple claims from single LLM response
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ClaimBatch:
    """
    A batch of claims from a single LLM response.

    The LLM outputs this structure:
    {
        "claims": [
            {"text": "...", "domain": "physics|math|logic|policy"},
            ...
        ]
    }
    """
    claims: List[Claim]
    source_prompt: str = ""
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_json(cls, data: Dict[str, Any], source_prompt: str = "") -> "ClaimBatch":
        """Parse LLM JSON response into ClaimBatch."""
        claims = [Claim.from_dict(c) for c in data.get("claims", [])]
        return cls(claims=claims, source_prompt=source_prompt)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claims": [c.to_dict() for c in self.claims],
            "source_prompt": self.source_prompt,
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION BATCH RESULT - Full validation of a claim batch
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BatchValidationResult:
    """
    Result of validating an entire ClaimBatch.

    Contains approved claims and violations for repair prompting.
    """
    approved: List[Claim]
    violations: List[Dict[str, Any]]  # {"claim": Claim, "result": ValidationResult}
    all_valid: bool
    timestamp: float = field(default_factory=time.time)

    @property
    def status(self) -> str:
        """Overall status: verified, partial, or refused."""
        if self.all_valid and self.approved:
            return "verified"
        elif self.approved:
            return "partial"
        else:
            return "refused"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "approved": [c.to_dict() for c in self.approved],
            "violations": [
                {
                    "claim": v["claim"].to_dict(),
                    "domain": v["result"].domain.value,
                    "rule": v["result"].rule,
                    "message": v["result"].message,
                }
                for v in self.violations
            ],
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LLM CONTRACT - The system prompt specification
# ═══════════════════════════════════════════════════════════════════════════════

LLM_SYSTEM_PROMPT = """You are a proposal generator.

Output JSON only.
Schema:
{
  "claims": [
    { "text": string, "domain": "physics|math|logic|policy|temporal|financial" }
  ]
}

Rules:
- Each claim must be atomic (one fact, one equation, one statement)
- No explanations or hedging
- No metaphors or figurative language
- Prefer physical realism over speculation
- Mathematical claims must be equations (e.g., "2 + 2 = 4")
- Physics claims must reference measurable quantities
- Logic claims must be propositional statements
- Policy claims must be factual assertions about rules
"""


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "Domain",
    "DomainLiteral",
    "Claim",
    "ClaimBatch",
    "ValidationResult",
    "BatchValidationResult",
    "LLM_SYSTEM_PROMPT",
]
