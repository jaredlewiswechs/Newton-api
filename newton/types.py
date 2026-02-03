"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TYPES
Core data types for verified computation.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
import hashlib
import json


class VerificationStatus(Enum):
    """Status of a verification."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class VerificationResult:
    """
    Result of a verification operation.
    
    Attributes:
        verified: Whether the claim was verified
        confidence: Confidence score (0-1)
        evidence: Supporting evidence
        sources: List of sources used
        timestamp: When verification occurred
        hash: Cryptographic hash of the verification
    """
    verified: bool
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def hash(self) -> str:
        """Generate verification hash."""
        data = f"{self.verified}:{self.confidence}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def __bool__(self) -> bool:
        return self.verified
    
    def __repr__(self) -> str:
        status = "✓" if self.verified else "✗"
        return f"VerificationResult({status}, confidence={self.confidence:.2f})"


@dataclass
class ConstraintResult:
    """
    Result of a constraint check.
    
    Attributes:
        satisfied: Whether constraint was satisfied
        constraint: The constraint that was checked
        value: The value that was checked
        message: Human-readable result message
    """
    satisfied: bool
    constraint: Dict[str, Any]
    value: Any
    message: str = ""
    
    def __bool__(self) -> bool:
        return self.satisfied
    
    def __repr__(self) -> str:
        status = "✓" if self.satisfied else "✗"
        return f"ConstraintResult({status}, {self.message})"


@dataclass
class CalculationResult:
    """
    Result of a verified calculation.
    
    Attributes:
        value: The calculated value
        expression: The original expression
        verified: Whether the calculation was verified
        steps: Computation steps (for audit)
        bounded: Whether computation was bounded
    """
    value: Any
    expression: str
    verified: bool = True
    steps: List[str] = field(default_factory=list)
    bounded: bool = True
    operations_count: int = 0
    
    def __repr__(self) -> str:
        return f"CalculationResult({self.value})"
    
    # Allow using result directly as the value
    def __int__(self) -> int:
        return int(self.value)
    
    def __float__(self) -> float:
        return float(self.value)
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass
class GroundingResult:
    """
    Result of grounding a claim in evidence.
    
    Attributes:
        grounded: Whether claim was grounded
        claim: The original claim
        evidence: Evidence found
        sources: Source URLs/references
        confidence: Grounding confidence
    """
    grounded: bool
    claim: str
    evidence: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def __bool__(self) -> bool:
        return self.grounded
    
    def __repr__(self) -> str:
        status = "✓" if self.grounded else "✗"
        return f"GroundingResult({status}, sources={len(self.sources)})"


@dataclass
class Bounds:
    """
    Execution bounds for verified computation.
    
    All Newton computations are bounded to guarantee termination.
    """
    max_iterations: int = 10_000
    max_recursion: int = 100
    max_operations: int = 1_000_000
    timeout_seconds: float = 30.0
    max_memory_mb: int = 512
    
    def __post_init__(self):
        # Hard caps - cannot be exceeded
        self.max_iterations = min(self.max_iterations, 100_000)
        self.max_recursion = min(self.max_recursion, 1000)
        self.max_operations = min(self.max_operations, 100_000_000)
        self.timeout_seconds = min(self.timeout_seconds, 300.0)


@dataclass
class AuditEntry:
    """
    Entry in the verification audit log.
    """
    timestamp: datetime
    action: str
    input_hash: str
    output_hash: str
    verified: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "verified": self.verified,
            "details": self.details,
        }
