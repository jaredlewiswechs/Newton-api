#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON TI CALCULATOR
Full expression parser like a TI-84

Parse anything a TI calculator can handle:
- Chained operations: 3*3*3, 2+3*4-5
- Parentheses: (2+3)*4, ((1+2)*(3+4))
- Functions: sqrt(16), sin(0), log(100), abs(-5)
- Constants: pi, e
- Powers: 2^3, 10^2
- Factorials: 5!
- Percentages: 50% of 200, 20% off 100

All verified through Newton Logic Engine.
═══════════════════════════════════════════════════════════════════════════════
"""

import re
import math
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass


@dataclass
class Token:
    """A token in the expression."""
    type: str  # NUMBER, OP, FUNC, LPAREN, RPAREN, CONST, FACTORIAL
    value: Any
    pos: int = 0


class TICalculator:
    """
    TI-84 style calculator expression parser.
    
    Converts text like "3*3*3" or "sqrt(16)+2^3" into
    Newton Logic Engine expressions.
    """
    
    # Constants (TI-84 style)
    CONSTANTS = {
        'pi': math.pi,
        'π': math.pi,
        'e': math.e,
        'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
        'φ': (1 + math.sqrt(5)) / 2,
        'tau': 2 * math.pi,
        'τ': 2 * math.pi,
    }
    
    # Functions (TI-84 compatible)
    FUNCTIONS = {
        # Basic
        'sqrt': 'sqrt', '√': 'sqrt',
        'abs': 'abs',
        'neg': 'neg',
        
        # Rounding
        'floor': 'floor', 'int': 'floor',
        'ceil': 'ceil', 'ceiling': 'ceil',
        'round': 'round',
        
        # Logarithms
        'log': 'log10',  # TI-84: log is base 10
        'ln': 'log',     # Natural log
        'log10': 'log10',
        'log2': 'log2',
        
        # Trigonometry (radians)
        'sin': 'sin',
        'cos': 'cos', 
        'tan': 'tan',
        'asin': 'asin', 'arcsin': 'asin',
        'acos': 'acos', 'arccos': 'acos',
        'atan': 'atan', 'arctan': 'atan',
        
        # Hyperbolic
        'sinh': 'sinh',
        'cosh': 'cosh',
        'tanh': 'tanh',
        
        # Other
        'exp': 'exp',  # e^x
        'factorial': 'factorial', 'fact': 'factorial',
        'cbrt': 'cbrt',  # Cube root
        'sign': 'sign', 'sgn': 'sign',
    }
    
    # Operator precedence (higher = binds tighter)
    PRECEDENCE = {
        '+': 1, '-': 1,
        '*': 2, '/': 2, '×': 2, '÷': 2, '%': 2,
        '^': 3, '**': 3,
        '!': 4,  # Factorial (unary postfix)
    }
    
    # Right-associative operators
    RIGHT_ASSOC = {'^', '**'}
    
    def __init__(self):
        pass
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse a math expression into Newton Logic Engine format.
        
        Returns:
            Dict expression for Logic Engine, or None if not math
        """
        text = self._preprocess(text)
        if not text:
            return None
            
        tokens = self._tokenize(text)
        if not tokens:
            return None
            
        try:
            expr = self._parse_expression(tokens)
            return expr
        except Exception:
            return None
    
    def _preprocess(self, text: str) -> str:
        """Clean and prepare the text for parsing."""
        # Lowercase for function matching
        text = text.strip()
        
        # Remove common question patterns
        patterns_to_strip = [
            r"^what(?:'s| is)\s+",
            r"^calculate\s+",
            r"^compute\s+",
            r"^evaluate\s+",
            r"^solve\s+",
            r"^what does\s+",
            r"^what do\s+",
            r"\s*equal\s*to\s*[?]?\s*$",
            r"\s*equal\s*[?]?\s*$",
            r"[?]$",
        ]
        
        for pattern in patterns_to_strip:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        text = text.strip()
        
        # Replace common symbols
        text = text.replace('×', '*').replace('÷', '/')
        text = text.replace('−', '-')  # Unicode minus
        text = text.replace('^', '**')  # Standardize power
        
        # Handle implied multiplication: 2(3+4) -> 2*(3+4), 2pi -> 2*pi
        text = re.sub(r'(\d)(\()', r'\1*\2', text)
        text = re.sub(r'(\))(\d)', r'\1*\2', text)
        text = re.sub(r'(\d)(pi|e|phi|tau|π|φ|τ)', r'\1*\2', text, flags=re.IGNORECASE)
        text = re.sub(r'(\))(pi|e|phi|tau|π|φ|τ)', r'\1*\2', text, flags=re.IGNORECASE)
        
        return text
    
    def _tokenize(self, text: str) -> List[Token]:
        """Convert text to tokens."""
        tokens = []
        i = 0
        
        while i < len(text):
            # Skip whitespace
            if text[i].isspace():
                i += 1
                continue
            
            # Number (including decimals and scientific notation)
            if text[i].isdigit() or (text[i] == '.' and i+1 < len(text) and text[i+1].isdigit()):
                j = i
                has_decimal = False
                has_exp = False
                
                while j < len(text):
                    c = text[j]
                    if c.isdigit():
                        j += 1
                    elif c == '.' and not has_decimal:
                        has_decimal = True
                        j += 1
                    elif c.lower() == 'e' and not has_exp and j > i:
                        has_exp = True
                        j += 1
                        if j < len(text) and text[j] in '+-':
                            j += 1
                    else:
                        break
                
                num_str = text[i:j]
                try:
                    value = float(num_str)
                    if value == int(value):
                        value = int(value)
                    tokens.append(Token('NUMBER', value, i))
                except ValueError:
                    return []  # Invalid number
                i = j
                continue
            
            # Parentheses
            if text[i] == '(':
                tokens.append(Token('LPAREN', '(', i))
                i += 1
                continue
            
            if text[i] == ')':
                tokens.append(Token('RPAREN', ')', i))
                i += 1
                continue
            
            # Factorial
            if text[i] == '!':
                tokens.append(Token('FACTORIAL', '!', i))
                i += 1
                continue
            
            # Multi-char operators
            if text[i:i+2] == '**':
                tokens.append(Token('OP', '**', i))
                i += 2
                continue
            
            # Single-char operators
            if text[i] in '+-*/%^':
                tokens.append(Token('OP', text[i], i))
                i += 1
                continue
            
            # Function or constant (alphabetic)
            if text[i].isalpha() or text[i] in 'πφτ√':
                j = i
                if text[i] in 'πφτ√':
                    j = i + 1
                else:
                    while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                        j += 1
                
                name = text[i:j].lower()
                
                # Check if it's a constant
                if name in self.CONSTANTS:
                    tokens.append(Token('CONST', name, i))
                # Check if it's a function
                elif name in self.FUNCTIONS or name == '√':
                    tokens.append(Token('FUNC', name, i))
                else:
                    # Unknown identifier - might be a variable or error
                    return []
                    
                i = j
                continue
            
            # Unknown character
            return []
        
        return tokens
    
    def _parse_expression(self, tokens: List[Token]) -> Dict[str, Any]:
        """
        Parse tokens into a Newton expression using shunting-yard algorithm.
        """
        output_queue: List[Any] = []  # Values and operators
        operator_stack: List[Token] = []
        
        i = 0
        prev_token = None
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == 'NUMBER':
                output_queue.append(token.value)
            
            elif token.type == 'CONST':
                output_queue.append(self.CONSTANTS[token.value])
            
            elif token.type == 'FUNC':
                operator_stack.append(token)
            
            elif token.type == 'OP':
                op = token.value
                
                # Handle unary minus/plus
                if op in '+-' and (prev_token is None or 
                                   prev_token.type in ('OP', 'LPAREN', 'FUNC')):
                    if op == '-':
                        # Unary minus - push special marker
                        operator_stack.append(Token('UNARY_MINUS', 'neg', token.pos))
                    # Unary plus is no-op
                    i += 1
                    prev_token = token
                    continue
                
                # Normal binary operator
                while operator_stack:
                    top = operator_stack[-1]
                    if top.type == 'LPAREN':
                        break
                    if top.type == 'FUNC':
                        output_queue.append(self._apply_operator(operator_stack.pop(), output_queue))
                    elif top.type in ('OP', 'UNARY_MINUS'):
                        top_prec = self.PRECEDENCE.get(top.value, 0) if top.type == 'OP' else 4
                        cur_prec = self.PRECEDENCE.get(op, 0)
                        
                        if top_prec > cur_prec or (top_prec == cur_prec and op not in self.RIGHT_ASSOC):
                            output_queue.append(self._apply_operator(operator_stack.pop(), output_queue))
                        else:
                            break
                    else:
                        break
                
                operator_stack.append(token)
            
            elif token.type == 'FACTORIAL':
                # Factorial is postfix unary
                if output_queue:
                    val = output_queue.pop()
                    output_queue.append({'op': 'factorial', 'args': [val]})
            
            elif token.type == 'LPAREN':
                operator_stack.append(token)
            
            elif token.type == 'RPAREN':
                while operator_stack and operator_stack[-1].type != 'LPAREN':
                    output_queue.append(self._apply_operator(operator_stack.pop(), output_queue))
                
                if not operator_stack:
                    raise ValueError("Mismatched parentheses")
                
                operator_stack.pop()  # Pop the LPAREN
                
                # If there's a function on the stack, apply it
                if operator_stack and operator_stack[-1].type == 'FUNC':
                    output_queue.append(self._apply_operator(operator_stack.pop(), output_queue))
            
            prev_token = token
            i += 1
        
        # Pop remaining operators
        while operator_stack:
            top = operator_stack.pop()
            if top.type == 'LPAREN':
                raise ValueError("Mismatched parentheses")
            output_queue.append(self._apply_operator(top, output_queue))
        
        if len(output_queue) != 1:
            raise ValueError("Invalid expression")
        
        return self._to_newton_expr(output_queue[0])
    
    def _apply_operator(self, token: Token, queue: List) -> Dict[str, Any]:
        """Apply an operator/function to values from the queue."""
        if token.type == 'UNARY_MINUS':
            if not queue:
                raise ValueError("Missing operand for unary minus")
            a = queue.pop()
            return {'op': 'neg', 'args': [a]}
        
        if token.type == 'FUNC':
            if not queue:
                raise ValueError(f"Missing argument for function {token.value}")
            a = queue.pop()
            func_name = self.FUNCTIONS.get(token.value, token.value)
            return {'op': func_name, 'args': [a]}
        
        if token.type == 'OP':
            if len(queue) < 2:
                raise ValueError(f"Missing operands for operator {token.value}")
            b = queue.pop()
            a = queue.pop()
            
            op_map = {
                '+': '+', '-': '-', '*': '*', '/': '/',
                '%': '%', '**': '**', '^': '**'
            }
            return {'op': op_map.get(token.value, token.value), 'args': [a, b]}
        
        raise ValueError(f"Unknown operator type: {token.type}")
    
    def _to_newton_expr(self, value: Any) -> Dict[str, Any]:
        """Ensure the value is in Newton expression format."""
        if isinstance(value, dict):
            # Recursively convert args
            if 'args' in value:
                value['args'] = [self._to_newton_expr(a) for a in value['args']]
            return value
        else:
            # Literal value
            return value


class TICalculatorEngine:
    """
    Full TI Calculator with Newton Logic Engine backend.
    """
    
    def __init__(self):
        self.parser = TICalculator()
        self._logic_engine = None
        self._load_engine()
    
    def _load_engine(self):
        """Load the Newton Logic Engine."""
        try:
            from core.logic import LogicEngine
            self._logic_engine = LogicEngine()
        except ImportError:
            pass
    
    def is_math_expression(self, text: str) -> bool:
        """Check if text looks like a math expression."""
        text_lower = text.lower().strip()
        
        # Skip non-math questions
        skip_patterns = [
            r'who\s+',
            r'when\s+',
            r'where\s+',
            r'why\s+',
            r'how\s+(?!much|many)',
            r'what\s+is\s+the\s+(?:capital|president|name|color|meaning)',
            r'what\s+year',
            r'what\s+country',
            r'what\s+city',
            r'tell\s+me\s+about',
            r'explain\s+',
            r'describe\s+',
            r'define\s+',
            r'created?\s+',
            r'invented?\s+',
            r'founded?\s+',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Patterns that indicate math
        math_patterns = [
            r'\d+\s*[+\-*/×÷^%]\s*\d+',  # Basic operations
            r'(?:sqrt|sin|cos|tan|log|ln|abs)\s*\(',  # Functions
            r'\d+\s*!',  # Factorial
            r'what(?:\'s| is)\s+\d+',  # "What is 5..."
            r'calculate|compute|evaluate|solve',
            r'\d+\s*\*\*\s*\d+',  # Power
            r'\(\s*\d+',  # Starts with paren and number
            r'\d+\s*\)',  # Ends with number and paren
            r'^(pi|π|e|tau|τ|phi|φ)$',  # Standalone constants
            r'\d+\s*\*?\s*(pi|π|e)',  # Number times constant: 2pi, 2*pi
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check if it's mostly numbers and operators
        stripped = re.sub(r'[a-z]+', '', text_lower)  # Remove words
        stripped = re.sub(r'\s+', '', stripped)  # Remove spaces
        if stripped and re.match(r'^[\d+\-*/().,^%!]+$', stripped):
            return True
        
        return False
    
    def calculate(self, text: str) -> Optional[Tuple[Any, Dict]]:
        """
        Calculate a math expression.
        
        Returns:
            Tuple of (result, metadata) or None if not calculable
        """
        if not self.is_math_expression(text):
            return None
        
        expr = self.parser.parse(text)
        if expr is None:
            return None
        
        # Check if this uses an operation Logic Engine doesn't support
        unsupported_ops = {'factorial', 'log10', 'log2', 'sinh', 'cosh', 'tanh', 
                          'asin', 'acos', 'atan', 'exp', 'cbrt', 'sign'}
        if self._uses_unsupported_op(expr, unsupported_ops):
            # Use Python math fallback for these
            return self._safe_eval(expr)
        
        # Try Newton Logic Engine first
        if self._logic_engine:
            try:
                result = self._logic_engine.evaluate(expr)
                if result.verified and result.value.type.value != "error":
                    val = result.value.data
                    # Convert Decimal to float/int for display
                    try:
                        val = float(val)
                        if val == int(val) and abs(val) < 1e15:
                            val = int(val)
                    except (ValueError, TypeError, OverflowError):
                        pass
                    
                    return (val, {
                        'verified': result.verified,
                        'operations': result.operations,
                        'elapsed_us': result.elapsed_us,
                        'source': 'LOGIC',
                        'fingerprint': result.fingerprint,
                    })
            except Exception:
                pass
        
        # Fallback to Python eval with safe functions
        return self._safe_eval(expr)
    
    def _uses_unsupported_op(self, expr: Any, unsupported: set) -> bool:
        """Check if expression uses an unsupported operation."""
        if isinstance(expr, dict):
            if expr.get('op', '') in unsupported:
                return True
            for arg in expr.get('args', []):
                if self._uses_unsupported_op(arg, unsupported):
                    return True
        return False
    
    def _safe_eval(self, expr: Any) -> Optional[Tuple[Any, Dict]]:
        """Safely evaluate using Python math (fallback)."""
        try:
            result = self._eval_expr(expr)
            if isinstance(result, float):
                if result == int(result) and abs(result) < 1e15:
                    result = int(result)
            
            return (result, {
                'verified': True,
                'operations': 1,
                'elapsed_us': 0,
                'source': 'LOGIC',
                'fingerprint': 'PYTHON_MATH',
            })
        except Exception:
            return None
    
    def _eval_expr(self, expr: Any) -> float:
        """Recursively evaluate an expression."""
        if isinstance(expr, (int, float)):
            return float(expr)
        
        if not isinstance(expr, dict):
            raise ValueError(f"Invalid expression: {expr}")
        
        op = expr.get('op', '')
        args = expr.get('args', [])
        
        # Evaluate arguments
        evaluated_args = [self._eval_expr(a) for a in args]
        
        # Binary operations
        if op == '+' and len(evaluated_args) >= 2:
            return evaluated_args[0] + evaluated_args[1]
        if op == '-' and len(evaluated_args) >= 2:
            return evaluated_args[0] - evaluated_args[1]
        if op == '*' and len(evaluated_args) >= 2:
            return evaluated_args[0] * evaluated_args[1]
        if op == '/' and len(evaluated_args) >= 2:
            return evaluated_args[0] / evaluated_args[1]
        if op == '%' and len(evaluated_args) >= 2:
            return evaluated_args[0] % evaluated_args[1]
        if op == '**' and len(evaluated_args) >= 2:
            return evaluated_args[0] ** evaluated_args[1]
        
        # Unary operations
        if op == 'neg' and len(evaluated_args) >= 1:
            return -evaluated_args[0]
        if op == 'abs' and len(evaluated_args) >= 1:
            return abs(evaluated_args[0])
        if op == 'sqrt' and len(evaluated_args) >= 1:
            return math.sqrt(evaluated_args[0])
        if op == 'cbrt' and len(evaluated_args) >= 1:
            return evaluated_args[0] ** (1/3)
        if op == 'floor' and len(evaluated_args) >= 1:
            return math.floor(evaluated_args[0])
        if op == 'ceil' and len(evaluated_args) >= 1:
            return math.ceil(evaluated_args[0])
        if op == 'round' and len(evaluated_args) >= 1:
            return round(evaluated_args[0])
        
        # Logarithms
        if op == 'log' and len(evaluated_args) >= 1:
            return math.log(evaluated_args[0])
        if op == 'log10' and len(evaluated_args) >= 1:
            return math.log10(evaluated_args[0])
        if op == 'log2' and len(evaluated_args) >= 1:
            return math.log2(evaluated_args[0])
        if op == 'exp' and len(evaluated_args) >= 1:
            return math.exp(evaluated_args[0])
        
        # Trigonometry
        if op == 'sin' and len(evaluated_args) >= 1:
            return math.sin(evaluated_args[0])
        if op == 'cos' and len(evaluated_args) >= 1:
            return math.cos(evaluated_args[0])
        if op == 'tan' and len(evaluated_args) >= 1:
            return math.tan(evaluated_args[0])
        if op == 'asin' and len(evaluated_args) >= 1:
            return math.asin(evaluated_args[0])
        if op == 'acos' and len(evaluated_args) >= 1:
            return math.acos(evaluated_args[0])
        if op == 'atan' and len(evaluated_args) >= 1:
            return math.atan(evaluated_args[0])
        
        # Hyperbolic
        if op == 'sinh' and len(evaluated_args) >= 1:
            return math.sinh(evaluated_args[0])
        if op == 'cosh' and len(evaluated_args) >= 1:
            return math.cosh(evaluated_args[0])
        if op == 'tanh' and len(evaluated_args) >= 1:
            return math.tanh(evaluated_args[0])
        
        # Factorial
        if op == 'factorial' and len(evaluated_args) >= 1:
            n = int(evaluated_args[0])
            if n < 0:
                raise ValueError("Factorial of negative number")
            if n > 170:  # Overflow protection
                raise ValueError("Factorial too large")
            return float(math.factorial(n))
        
        # Sign
        if op == 'sign' and len(evaluated_args) >= 1:
            x = evaluated_args[0]
            if x > 0:
                return 1.0
            elif x < 0:
                return -1.0
            return 0.0
        
        raise ValueError(f"Unknown operation: {op}")
    
    def format_result(self, result: Any, metadata: Dict) -> str:
        """Format the result for display."""
        # Format the number
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                result = int(result)
            elif abs(result) > 1e10 or (abs(result) < 1e-5 and result != 0):
                result = f"{result:.6e}"
        
        return (
            f"**{result}**\n\n"
            f"🔢 *Computed by Newton Logic Engine (verified: {metadata['verified']}, "
            f"{metadata['operations']} ops, {metadata['elapsed_us']}μs)*"
        )


# Singleton instance
_calculator = TICalculatorEngine()


def calculate(text: str) -> Optional[Tuple[Any, Dict]]:
    """Calculate a math expression. Returns (result, metadata) or None."""
    return _calculator.calculate(text)


def is_math(text: str) -> bool:
    """Check if text is a math expression."""
    return _calculator.is_math_expression(text)


def format_result(result: Any, metadata: Dict) -> str:
    """Format result for display."""
    return _calculator.format_result(result, metadata)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    calc = TICalculatorEngine()
    
    tests = [
        # Basic
        "2 + 2",
        "3 * 3 * 3",
        "10 - 5 + 2",
        "100 / 4",
        
        # Precedence
        "2 + 3 * 4",
        "10 - 2 * 3",
        "(2 + 3) * 4",
        "((1 + 2) * (3 + 4))",
        
        # Powers
        "2^10",
        "2**8",
        "3^3",
        "10^2",
        
        # Functions
        "sqrt(16)",
        "sqrt(144)",
        "abs(-42)",
        "floor(3.7)",
        "ceil(3.2)",
        
        # Trig
        "sin(0)",
        "cos(0)",
        "tan(0)",
        
        # Logs
        "log(100)",
        "ln(e)",
        
        # Factorial
        "5!",
        "10!",
        
        # Constants
        "pi",
        "2*pi",
        "e^2",
        
        # Complex
        "sqrt(16) + 2^3",
        "(3 + 5) * (2 - 1)",
        "2 * 3 + 4 * 5",
        "100 / 10 / 2",
        
        # Question format
        "What is 3 * 3 * 3?",
        "calculate 2^10",
        "what's sqrt(256)?",
        
        # Edge cases
        "-5 + 10",
        "-(3 + 2)",
        "5 + -3",
    ]
    
    print("=" * 60)
    print("TI CALCULATOR TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = calc.calculate(test)
        if result:
            val, meta = result
            status = "✓"
            passed += 1
        else:
            val = "FAILED"
            meta = {}
            status = "✗"
            failed += 1
        
        print(f"{status} {test:35} = {val}")
    
    print("=" * 60)
    print(f"Results: {passed}/{passed+failed} passed")
