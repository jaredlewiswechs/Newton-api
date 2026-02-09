"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON SDK - TI CALCULATOR
TI-84 Style Expression Parser

Re-exports the TI Calculator for natural math input.

Usage:
    from newton import ti_calc
    
    # Parse and evaluate like a TI-84
    result = ti_calc("3*3*3")        # 27
    result = ti_calc("sqrt(16)+2^3") # 12.0
    result = ti_calc("5!")           # 120
    result = ti_calc("2pi")          # 6.28...
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os

# Add parent path to import from newton_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from newton_agent.ti_calculator import TICalculator, TICalculatorEngine, Token

# Create default engine instance
_default_engine = None


def _get_engine():
    """Get or create the default TI calculator engine."""
    global _default_engine
    if _default_engine is None:
        _default_engine = TICalculatorEngine()
    return _default_engine


def ti_calc(expression: str):
    """
    Evaluate a math expression like a TI-84 calculator.
    
    Supports:
        - Basic ops: +, -, *, /, ^, **
        - Functions: sqrt, sin, cos, tan, log, ln, abs, floor, ceil
        - Constants: pi, e, phi, tau
        - Factorials: 5!
        - Parentheses: (2+3)*4
        - Implied multiplication: 2pi, 3(4+5)
    
    Args:
        expression: Math expression string
        
    Returns:
        Computed result, or None if not a valid expression
        
    Examples:
        >>> ti_calc("2+2")
        4
        >>> ti_calc("sqrt(16)")
        4.0
        >>> ti_calc("5!")
        120
        >>> ti_calc("2*pi")
        6.283185307179586
    """
    engine = _get_engine()
    result = engine.calculate(expression)
    
    # Handle tuple return (value, metadata)
    if result is None:
        return None
    if isinstance(result, tuple):
        value, metadata = result
        return value
    # Handle dict return
    if isinstance(result, dict):
        if result.get('verified'):
            return result.get('value')
    return result


def parse_math(expression: str):
    """
    Parse a math expression into Newton Logic Engine format.
    
    Args:
        expression: Math expression string
        
    Returns:
        Dict expression for LogicEngine, or None if invalid
        
    Example:
        >>> parse_math("2+3*4")
        {'op': '+', 'args': [2, {'op': '*', 'args': [3, 4]}]}
    """
    parser = TICalculator()
    return parser.parse(expression)


__all__ = [
    "ti_calc",
    "parse_math",
    "TICalculator",
    "TICalculatorEngine",
    "Token",
]
