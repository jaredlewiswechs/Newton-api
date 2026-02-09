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
    
    # TI-84 style calculator
    newton.ti_calc("sqrt(16) + 2^3")  # 12.0
    
    # Turing-complete logic engine
    newton.execute({"op": "for", "args": ["i", 0, 5, {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}]})
    
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
    contains, matches, between,
    within, after, before,
    all_of, any_of, none_of,
)

# Verification results
from newton.types import (
    VerificationResult,
    ConstraintResult,
    CalculationResult,
    GroundingResult,
    Bounds,
)

# Decorators for verified functions
from newton.decorators import (
    verified,
    bounded,
    logged,
    constrained,
)

# Turing-complete Logic Engine
from newton.logic import (
    LogicEngine,
    ExecutionBounds,
    ExecutionContext,
    ExecutionResult,
    Expr,
    ExprType,
    Value,
    ValueType,
    execute,
    run_program,
)

# TI Calculator
from newton.calculator import (
    ti_calc,
    parse_math,
    TICalculator,
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
    "contains", "matches", "between",
    "within", "after", "before",
    "all_of", "any_of", "none_of",
    
    # Types
    "VerificationResult",
    "ConstraintResult", 
    "CalculationResult",
    "GroundingResult",
    "Bounds",
    
    # Decorators
    "verified",
    "bounded",
    "logged",
    "constrained",
    
    # Logic Engine (Turing-complete)
    "LogicEngine",
    "ExecutionBounds",
    "ExecutionContext",
    "ExecutionResult",
    "Expr",
    "ExprType",
    "Value",
    "ValueType",
    "execute",
    "run_program",
    
    # TI Calculator
    "ti_calc",
    "parse_math",
    "TICalculator",
]
