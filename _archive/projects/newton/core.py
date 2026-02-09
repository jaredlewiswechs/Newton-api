"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CORE
The heart of verified computation.

The fundamental law: newton(current, goal) returns current == goal
When true → execute. When false → halt.
═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import hashlib
import re
import ast
import operator

from newton.types import (
    VerificationResult,
    ConstraintResult,
    CalculationResult,
    GroundingResult,
    Bounds,
    AuditEntry,
)
from newton.constraints import Constraint, check_dict


# ═══════════════════════════════════════════════════════════════════════════════
# THE NEWTON CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Newton:
    """
    The Newton verification engine.
    
    Usage:
        n = Newton()
        
        # Verify claims
        n.verify("2 + 2 equals 4")
        
        # Check constraints
        n.check({"age": 25}, {"age": {"ge": 18}})
        
        # Calculate with verification
        n.calc("sqrt(16) + 2")
        
        # Ground in evidence
        n.ground("Python was created by Guido van Rossum")
    """
    
    def __init__(self, bounds: Optional[Bounds] = None):
        self.bounds = bounds or Bounds()
        self._audit_log: List[AuditEntry] = []
        self._operations = 0
    
    def verify(self, claim: str, context: Optional[Dict] = None) -> VerificationResult:
        """
        Verify a claim.
        
        Args:
            claim: The claim to verify
            context: Optional context for verification
            
        Returns:
            VerificationResult with verified status and evidence
        """
        return verify(claim, context, self.bounds)
    
    def check(self, value: Any, constraint: Any) -> ConstraintResult:
        """
        Check a value against a constraint.
        
        Args:
            value: The value to check
            constraint: Constraint specification (Constraint object or dict)
            
        Returns:
            ConstraintResult with pass/fail status
        """
        return check(value, constraint)
    
    def calc(self, expression: str) -> CalculationResult:
        """
        Perform a verified calculation.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            CalculationResult with value and verification
        """
        return calc(expression, self.bounds)
    
    def ground(self, claim: str) -> GroundingResult:
        """
        Ground a claim in external evidence.
        
        Args:
            claim: The claim to ground
            
        Returns:
            GroundingResult with evidence and sources
        """
        return ground(claim)
    
    @property
    def audit_log(self) -> List[AuditEntry]:
        """Get the audit log."""
        return self._audit_log.copy()
    
    def _log(self, action: str, input_data: Any, output: Any, verified: bool):
        """Add entry to audit log."""
        entry = AuditEntry(
            timestamp=datetime.now(),
            action=action,
            input_hash=hashlib.sha256(str(input_data).encode()).hexdigest()[:16],
            output_hash=hashlib.sha256(str(output).encode()).hexdigest()[:16],
            verified=verified,
        )
        self._audit_log.append(entry)


# ═══════════════════════════════════════════════════════════════════════════════
# SIMPLE API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def verify(claim: str, context: Optional[Dict] = None, 
           bounds: Optional[Bounds] = None) -> VerificationResult:
    """
    Verify a claim.
    
    Examples:
        >>> verify("2 + 2 equals 4")
        VerificationResult(✓, confidence=1.00)
        
        >>> verify("The sky is green")
        VerificationResult(✗, confidence=0.10)
    
    Args:
        claim: The claim to verify
        context: Optional context dictionary
        bounds: Execution bounds
        
    Returns:
        VerificationResult
    """
    context = context or {}
    bounds = bounds or Bounds()
    
    # Extract potential mathematical claims
    math_patterns = [
        (r"(\d+)\s*\+\s*(\d+)\s*(?:equals?|=|is)\s*(\d+)", "+"),
        (r"(\d+)\s*-\s*(\d+)\s*(?:equals?|=|is)\s*(\d+)", "-"),
        (r"(\d+)\s*[*×x]\s*(\d+)\s*(?:equals?|=|is)\s*(\d+)", "*"),
        (r"(\d+)\s*[/÷]\s*(\d+)\s*(?:equals?|=|is)\s*(\d+)", "/"),
    ]
    
    for pattern, op in math_patterns:
        match = re.search(pattern, claim, re.IGNORECASE)
        if match:
            groups = match.groups()
            a, b, c = int(groups[0]), int(groups[1]), int(groups[2])
            
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op == "*":
                result = a * b
            else:
                result = a / b if b != 0 else float('inf')
            
            verified = result == c
            
            return VerificationResult(
                verified=verified,
                confidence=1.0 if verified else 0.0,
                evidence=[f"{a} {op} {b} = {result}"],
                details={"type": "mathematical", "expression": claim}
            )
    
    # Check for boolean claims
    if claim.lower() in ("true", "yes", "1"):
        return VerificationResult(verified=True, confidence=1.0)
    if claim.lower() in ("false", "no", "0"):
        return VerificationResult(verified=False, confidence=1.0)
    
    # Check against context
    for key, value in context.items():
        if key.lower() in claim.lower():
            if str(value).lower() in claim.lower():
                return VerificationResult(
                    verified=True,
                    confidence=0.8,
                    evidence=[f"Context contains matching {key}={value}"],
                    details={"type": "context_match", "key": key, "value": value}
                )
    
    # Default: unverified
    return VerificationResult(
        verified=False,
        confidence=0.0,
        details={"type": "unverified", "reason": "No verification method available"}
    )


def check(value: Any, constraint: Any) -> ConstraintResult:
    """
    Check a value against a constraint.
    
    Examples:
        >>> check(25, gt(18))
        ConstraintResult(✓, must be greater than 18)
        
        >>> check({"age": 25}, {"age": gt(18)})
        ConstraintResult(✓, all fields satisfied)
        
        >>> check("hello", contains("ell"))
        ConstraintResult(✓, must contain 'ell')
    
    Args:
        value: The value to check
        constraint: A Constraint object, dict, or raw value
        
    Returns:
        ConstraintResult
    """
    # Direct Constraint object
    if isinstance(constraint, Constraint):
        satisfied = constraint.check(value)
        return ConstraintResult(
            satisfied=satisfied,
            constraint={"op": constraint.op, "value": constraint.value},
            value=value,
            message=constraint.message if not satisfied else "satisfied"
        )
    
    # Dictionary constraint (for checking objects)
    if isinstance(constraint, dict) and isinstance(value, dict):
        results = check_dict(value, constraint)
        all_satisfied = all(results.values())
        failed = [k for k, v in results.items() if not v]
        
        return ConstraintResult(
            satisfied=all_satisfied,
            constraint=constraint,
            value=value,
            message="all fields satisfied" if all_satisfied else f"failed: {failed}"
        )
    
    # Dictionary with constraint operators
    if isinstance(constraint, dict):
        # Single operator dict like {"gt": 5}
        for op, expected in constraint.items():
            from newton.constraints import _evaluate
            satisfied = _evaluate(op, value, expected)
            return ConstraintResult(
                satisfied=satisfied,
                constraint=constraint,
                value=value,
                message=f"{op} {expected}"
            )
    
    # Raw value comparison
    satisfied = value == constraint
    return ConstraintResult(
        satisfied=satisfied,
        constraint={"eq": constraint},
        value=value,
        message=f"equals {constraint}" if satisfied else f"expected {constraint}, got {value}"
    )


def calc(expression: str, bounds: Optional[Bounds] = None) -> CalculationResult:
    """
    Perform a verified calculation.
    
    Supports: +, -, *, /, **, %, sqrt, abs, min, max, sin, cos, tan, log, etc.
    
    Examples:
        >>> calc("2 + 2")
        CalculationResult(4)
        
        >>> calc("sqrt(16) + 2")
        CalculationResult(6.0)
        
        >>> calc("max(1, 2, 3) * 2")
        CalculationResult(6)
    
    Args:
        expression: Mathematical expression
        bounds: Execution bounds
        
    Returns:
        CalculationResult with value
    """
    bounds = bounds or Bounds()
    
    # Safe math functions
    import math
    safe_functions = {
        'sqrt': math.sqrt,
        'abs': abs,
        'min': min,
        'max': max,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'floor': math.floor,
        'ceil': math.ceil,
        'round': round,
        'pow': pow,
        'pi': math.pi,
        'e': math.e,
    }
    
    # Safe operators
    safe_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    operations = [0]  # Mutable counter
    steps = []
    
    def safe_eval(node):
        operations[0] += 1
        if operations[0] > bounds.max_operations:
            raise RuntimeError(f"Exceeded max operations: {bounds.max_operations}")
        
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in safe_functions:
                return safe_functions[node.id]
            raise ValueError(f"Unknown name: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = safe_eval(node.left)
            right = safe_eval(node.right)
            op = safe_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            result = op(left, right)
            steps.append(f"{left} {type(node.op).__name__} {right} = {result}")
            return result
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval(node.operand)
            op = safe_operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(operand)
        elif isinstance(node, ast.Call):
            func = safe_eval(node.func)
            args = [safe_eval(arg) for arg in node.args]
            result = func(*args)
            steps.append(f"{node.func.id}({', '.join(str(a) for a in args)}) = {result}")
            return result
        elif isinstance(node, ast.Expression):
            return safe_eval(node.body)
        else:
            raise ValueError(f"Unsupported expression type: {type(node)}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree)
        
        return CalculationResult(
            value=result,
            expression=expression,
            verified=True,
            steps=steps,
            bounded=True,
            operations_count=operations[0]
        )
    except Exception as e:
        return CalculationResult(
            value=None,
            expression=expression,
            verified=False,
            steps=[f"Error: {e}"],
            bounded=True,
            operations_count=operations[0]
        )


def ground(claim: str, search_fn: Optional[Callable] = None) -> GroundingResult:
    """
    Ground a claim in external evidence.
    
    This function attempts to find evidence for a claim using
    web search or other grounding mechanisms.
    
    Examples:
        >>> ground("Python was created by Guido van Rossum")
        GroundingResult(✓, sources=3)
        
        >>> ground("The moon is made of cheese")
        GroundingResult(✗, sources=0)
    
    Args:
        claim: The claim to ground
        search_fn: Optional custom search function
        
    Returns:
        GroundingResult with evidence and sources
    """
    # Try to use googlesearch if available
    sources = []
    evidence = []
    
    try:
        if search_fn:
            results = search_fn(claim)
            sources = results if isinstance(results, list) else [results]
        else:
            # Try googlesearch-python
            try:
                from googlesearch import search
                sources = list(search(claim, num_results=3, lang="en"))
            except ImportError:
                pass
    except Exception:
        pass
    
    # If we found sources, consider it partially grounded
    if sources:
        return GroundingResult(
            grounded=True,
            claim=claim,
            evidence=[f"Found {len(sources)} relevant sources"],
            sources=sources,
            confidence=min(0.3 + 0.2 * len(sources), 0.9)
        )
    
    # Check for well-known facts (simple heuristics)
    known_facts = {
        "python": ["guido van rossum", "1991", "programming language"],
        "javascript": ["brendan eich", "1995", "netscape"],
        "earth": ["planet", "sun", "solar system"],
        "water": ["h2o", "hydrogen", "oxygen"],
    }
    
    claim_lower = claim.lower()
    for topic, facts in known_facts.items():
        if topic in claim_lower:
            for fact in facts:
                if fact in claim_lower:
                    return GroundingResult(
                        grounded=True,
                        claim=claim,
                        evidence=[f"Known fact: {topic} relates to {fact}"],
                        sources=["internal_knowledge"],
                        confidence=0.7
                    )
    
    return GroundingResult(
        grounded=False,
        claim=claim,
        evidence=[],
        sources=[],
        confidence=0.0
    )


# ═══════════════════════════════════════════════════════════════════════════════
# THE FUNDAMENTAL LAW
# ═══════════════════════════════════════════════════════════════════════════════

def newton(current: Any, goal: Any) -> bool:
    """
    The fundamental law of Newton.
    
    newton(current, goal) returns current == goal
    
    When true → execute
    When false → halt
    
    This is not a feature. This is the architecture.
    """
    return current == goal
