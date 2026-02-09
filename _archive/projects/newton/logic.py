"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON SDK - LOGIC ENGINE
Turing-Complete Verified Computation

Re-exports the full LogicEngine from core/logic.py for SDK users.
This provides:
- Bounded loops (for, while, map, filter, reduce)
- Recursion with depth limits
- Conditionals (if, cond)
- Lambda functions
- Full arithmetic, comparison, boolean logic
- All verified with execution bounds

Usage:
    from newton import LogicEngine, Expr, ExprType
    
    engine = LogicEngine()
    
    # Factorial via recursion
    result = engine.evaluate({
        "op": "def",
        "args": ["factorial", ["n"],
            {"op": "if", "args": [
                {"op": "le", "args": [{"op": "var", "args": ["n"]}, 1]},
                1,
                {"op": "*", "args": [
                    {"op": "var", "args": ["n"]},
                    {"op": "call", "args": ["factorial",
                        {"op": "-", "args": [{"op": "var", "args": ["n"]}, 1]}
                    ]}
                ]}
            ]}
        ]
    })
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os

# Add parent path to import from core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logic import (
    LogicEngine,
    ExecutionBounds,
    ExecutionContext,
    ExecutionResult,
    Expr,
    ExprType,
    Value,
    ValueType,
)

__all__ = [
    "LogicEngine",
    "ExecutionBounds",
    "ExecutionContext", 
    "ExecutionResult",
    "Expr",
    "ExprType",
    "Value",
    "ValueType",
]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def execute(expr: dict, bounds: ExecutionBounds = None) -> ExecutionResult:
    """
    Execute a Newton Logic expression with verification.
    
    Args:
        expr: Expression in dict form (JSON-compatible)
        bounds: Optional execution bounds
        
    Returns:
        ExecutionResult with value, operations count, and verification status
        
    Example:
        >>> execute({"op": "+", "args": [2, 3]})
        ExecutionResult(value=5, verified=True)
        
        >>> execute({"op": "for", "args": ["i", 0, 10, {"op": "*", "args": [{"op": "var", "args": ["i"]}, 2]}]})
        ExecutionResult(value=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18], verified=True)
    """
    engine = LogicEngine(bounds)
    return engine.evaluate(expr)


def run_program(statements: list, bounds: ExecutionBounds = None) -> ExecutionResult:
    """
    Run a sequence of statements as a program.
    
    Args:
        statements: List of expressions to execute in order
        bounds: Optional execution bounds
        
    Returns:
        ExecutionResult of the last statement
        
    Example:
        >>> run_program([
        ...     {"op": "let", "args": ["x", 10]},
        ...     {"op": "let", "args": ["y", 20]},
        ...     {"op": "+", "args": [{"op": "var", "args": ["x"]}, {"op": "var", "args": ["y"]}]}
        ... ])
        ExecutionResult(value=30, verified=True)
    """
    engine = LogicEngine(bounds)
    return engine.evaluate({"op": "block", "args": statements})
