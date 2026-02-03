"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON SDK
Verified computation for everyone.

Usage:
    import newton
    
    # Verify a claim
    result = newton.verify("The sky is blue")
    
    # Check a constraint
    newton.check({"age": 25}, {"ge": 18})  # True
    
    # Calculate with verification
    newton.calc("2 + 2")  # 4
    
    # Ground a claim in evidence
    newton.ground("Python was created in 1991")

The fundamental law: newton(current, goal) returns current == goal
When true → execute. When false → halt.

"1 == 1. The cloud is weather. We're building shelter."
═══════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "Newton"

# Core imports - the simple API
from newton.core import (
    verify,
    check,
    calc,
    ground,
    Newton,
)

# Constraint language
from newton.constraints import (
    Constraint,
    eq, ne, lt, gt, le, ge,
    contains, matches,
    within, after, before,
    all_of, any_of, none_of,
)

# Verification results
from newton.types import (
    VerificationResult,
    ConstraintResult,
    CalculationResult,
    GroundingResult,
)

# Decorators for verified functions
from newton.decorators import (
    verified,
    bounded,
    logged,
    constrained,
)

__all__ = [
    # Version
    "__version__",
    
    # Core functions
    "verify",
    "check", 
    "calc",
    "ground",
    "Newton",
    
    # Constraints
    "Constraint",
    "eq", "ne", "lt", "gt", "le", "ge",
    "contains", "matches",
    "within", "after", "before",
    "all_of", "any_of", "none_of",
    
    # Types
    "VerificationResult",
    "ConstraintResult", 
    "CalculationResult",
    "GroundingResult",
    
    # Decorators
    "verified",
    "bounded",
    "logged",
    "constrained",
]
