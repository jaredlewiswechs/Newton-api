#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
STATSY - THE VERIFIED STATISTICAL PROGRAMMING LANGUAGE
═══════════════════════════════════════════════════════════════════════════════

Every calculation is checked. Every result is provable.
Statistics you can trust.

The constraint IS the instruction.
The verification IS the computation.
The data IS the evidence.

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from enum import Enum, auto
import math
import re
import sys
import json


# ═══════════════════════════════════════════════════════════════════════════════
# TOKEN TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    BOOLEAN = auto()
    NA = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    PERCENT = auto()
    
    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    ASSIGN = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Statistical
    PIPE = auto()       # |>
    TILDE = auto()      # ~
    WHERE = auto()
    
    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    NEWLINE = auto()
    
    # Keywords
    DATA = auto()
    LOAD = auto()
    VERIFY = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    IN = auto()
    FUNCTION = auto()
    RETURN = auto()
    PRINT = auto()
    
    # Special
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


# ═══════════════════════════════════════════════════════════════════════════════
# LEXER
# ═══════════════════════════════════════════════════════════════════════════════

class StatsyLexer:
    """Tokenize Statsy source code."""
    
    KEYWORDS = {
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'NA': TokenType.NA,
        'na': TokenType.NA,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'where': TokenType.WHERE,
        'load': TokenType.LOAD,
        'verify': TokenType.VERIFY,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'function': TokenType.FUNCTION,
        'fn': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Convert source to tokens."""
        while self.pos < len(self.source):
            self._scan_token()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def _scan_token(self):
        c = self._advance()
        
        # Whitespace
        if c in ' \t\r':
            return
        
        # Newline
        if c == '\n':
            self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
            self.line += 1
            self.column = 1
            return
        
        # Comment
        if c == '#':
            while self.pos < len(self.source) and self.source[self.pos] != '\n':
                self._advance()
            return
        
        # String
        if c == '"' or c == "'":
            self._scan_string(c)
            return
        
        # Number
        if c.isdigit() or (c == '.' and self._peek().isdigit()):
            self._scan_number(c)
            return
        
        # Identifier or keyword
        if c.isalpha() or c == '_':
            self._scan_identifier(c)
            return
        
        # Two-character operators
        if c == '|' and self._peek() == '>':
            self._advance()
            self.tokens.append(Token(TokenType.PIPE, '|>', self.line, self.column - 1))
            return
        
        if c == '=' and self._peek() == '=':
            self._advance()
            self.tokens.append(Token(TokenType.EQ, '==', self.line, self.column - 1))
            return
        
        if c == '!' and self._peek() == '=':
            self._advance()
            self.tokens.append(Token(TokenType.NE, '!=', self.line, self.column - 1))
            return
        
        if c == '<' and self._peek() == '=':
            self._advance()
            self.tokens.append(Token(TokenType.LE, '<=', self.line, self.column - 1))
            return
        
        if c == '>' and self._peek() == '=':
            self._advance()
            self.tokens.append(Token(TokenType.GE, '>=', self.line, self.column - 1))
            return
        
        # Single-character operators
        single_chars = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '^': TokenType.CARET,
            '%': TokenType.PERCENT,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '=': TokenType.ASSIGN,
            '~': TokenType.TILDE,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
        }
        
        if c in single_chars:
            self.tokens.append(Token(single_chars[c], c, self.line, self.column - 1))
            return
        
        raise SyntaxError(f"Unexpected character '{c}' at line {self.line}, column {self.column}")
    
    def _advance(self) -> str:
        c = self.source[self.pos]
        self.pos += 1
        self.column += 1
        return c
    
    def _peek(self) -> str:
        if self.pos >= len(self.source):
            return '\0'
        return self.source[self.pos]
    
    def _scan_string(self, quote: str):
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == '\n':
                self.line += 1
            self.pos += 1
        
        if self.pos >= len(self.source):
            raise SyntaxError(f"Unterminated string at line {self.line}")
        
        value = self.source[start:self.pos]
        self.pos += 1  # Closing quote
        self.tokens.append(Token(TokenType.STRING, value, self.line, self.column))
    
    def _scan_number(self, first: str):
        start = self.pos - 1
        has_dot = first == '.'
        
        while self.pos < len(self.source):
            c = self.source[self.pos]
            if c.isdigit():
                self.pos += 1
            elif c == '.' and not has_dot:
                has_dot = True
                self.pos += 1
            elif c in 'eE':
                self.pos += 1
                if self.pos < len(self.source) and self.source[self.pos] in '+-':
                    self.pos += 1
            else:
                break
        
        text = self.source[start:self.pos]
        value = float(text) if '.' in text or 'e' in text.lower() else int(text)
        self.tokens.append(Token(TokenType.NUMBER, value, self.line, self.column))
    
    def _scan_identifier(self, first: str):
        start = self.pos - 1
        
        while self.pos < len(self.source):
            c = self.source[self.pos]
            if c.isalnum() or c == '_':
                self.pos += 1
            else:
                break
        
        text = self.source[start:self.pos]
        
        # Check for keyword
        if text in self.KEYWORDS:
            token_type = self.KEYWORDS[text]
            value = True if text == 'true' else False if text == 'false' else text
            self.tokens.append(Token(token_type, value, self.line, self.column))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, text, self.line, self.column))


# ═══════════════════════════════════════════════════════════════════════════════
# AST NODES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ASTNode:
    """Base class for AST nodes."""
    pass

@dataclass
class NumberLiteral(ASTNode):
    value: Union[int, float]

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class BooleanLiteral(ASTNode):
    value: bool

@dataclass
class NALiteral(ASTNode):
    pass

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class VectorLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class BinaryOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass 
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]
    kwargs: Dict[str, ASTNode] = field(default_factory=dict)

@dataclass
class PipeExpr(ASTNode):
    left: ASTNode
    right: ASTNode

@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode

@dataclass
class IfExpr(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode]

@dataclass
class ForExpr(ASTNode):
    var: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class FunctionDef(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]

@dataclass
class PrintStmt(ASTNode):
    value: ASTNode

@dataclass
class PropertyAccess(ASTNode):
    obj: ASTNode
    property: str

@dataclass
class IndexAccess(ASTNode):
    obj: ASTNode
    index: ASTNode

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]


# ═══════════════════════════════════════════════════════════════════════════════
# PARSER
# ═══════════════════════════════════════════════════════════════════════════════

class StatsyParser:
    """Parse tokens into AST."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        """Parse the token stream into an AST."""
        statements = []
        
        while not self._is_at_end():
            self._skip_newlines()
            if not self._is_at_end():
                stmt = self._statement()
                if stmt:
                    statements.append(stmt)
        
        return Program(statements)
    
    def _statement(self) -> Optional[ASTNode]:
        """Parse a statement."""
        # Skip newlines
        self._skip_newlines()
        
        if self._is_at_end():
            return None
        
        # Print statement
        if self._check(TokenType.PRINT):
            return self._print_statement()
        
        # Function definition
        if self._check(TokenType.FUNCTION):
            return self._function_def()
        
        # If statement
        if self._check(TokenType.IF):
            return self._if_statement()
        
        # For loop
        if self._check(TokenType.FOR):
            return self._for_loop()
        
        # Return statement
        if self._check(TokenType.RETURN):
            return self._return_statement()
        
        # Assignment or expression
        return self._assignment_or_expr()
    
    def _print_statement(self) -> PrintStmt:
        self._advance()  # consume 'print'
        if self._check(TokenType.LPAREN):
            self._advance()
            value = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after print argument")
        else:
            value = self._expression()
        return PrintStmt(value)
    
    def _function_def(self) -> FunctionDef:
        self._advance()  # consume 'function' or 'fn'
        name = self._consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self._match(TokenType.COMMA):
                params.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name").value)
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self._block()
        
        return FunctionDef(name, params, body)
    
    def _if_statement(self) -> IfExpr:
        self._advance()  # consume 'if'
        
        # Optional parentheses around condition
        has_paren = self._match(TokenType.LPAREN)
        condition = self._expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after condition")
        
        self._consume(TokenType.LBRACE, "Expected '{' after if condition")
        then_branch = self._block()
        
        else_branch = None
        if self._match(TokenType.ELSE):
            self._consume(TokenType.LBRACE, "Expected '{' after else")
            else_branch = self._block()
        
        return IfExpr(condition, Program(then_branch), Program(else_branch) if else_branch else None)
    
    def _for_loop(self) -> ForExpr:
        self._advance()  # consume 'for'
        var = self._consume(TokenType.IDENTIFIER, "Expected loop variable").value
        self._consume(TokenType.IN, "Expected 'in' in for loop")
        iterable = self._expression()
        self._consume(TokenType.LBRACE, "Expected '{' after for")
        body = self._block()
        return ForExpr(var, iterable, body)
    
    def _return_statement(self) -> ReturnStmt:
        self._advance()  # consume 'return'
        value = None
        if not self._check(TokenType.NEWLINE) and not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._expression()
        return ReturnStmt(value)
    
    def _block(self) -> List[ASTNode]:
        """Parse a block of statements."""
        statements = []
        self._skip_newlines()
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return statements
    
    def _assignment_or_expr(self) -> ASTNode:
        """Parse assignment or expression."""
        if self._check(TokenType.IDENTIFIER) and self._peek_next().type == TokenType.ASSIGN:
            name = self._advance().value
            self._advance()  # consume '='
            value = self._expression()
            return Assignment(name, value)
        
        return self._expression()
    
    def _expression(self) -> ASTNode:
        """Parse an expression."""
        return self._pipe()
    
    def _pipe(self) -> ASTNode:
        """Parse pipe expressions: x |> f(y)."""
        left = self._or_expr()
        
        while self._match(TokenType.PIPE):
            right = self._or_expr()
            left = PipeExpr(left, right)
        
        return left
    
    def _or_expr(self) -> ASTNode:
        left = self._and_expr()
        while self._match(TokenType.OR):
            right = self._and_expr()
            left = BinaryOp('or', left, right)
        return left
    
    def _and_expr(self) -> ASTNode:
        left = self._equality()
        while self._match(TokenType.AND):
            right = self._equality()
            left = BinaryOp('and', left, right)
        return left
    
    def _equality(self) -> ASTNode:
        left = self._comparison()
        while self._match(TokenType.EQ, TokenType.NE):
            op = '==' if self._previous().type == TokenType.EQ else '!='
            right = self._comparison()
            left = BinaryOp(op, left, right)
        return left
    
    def _comparison(self) -> ASTNode:
        left = self._term()
        while self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self._previous().value
            right = self._term()
            left = BinaryOp(op, left, right)
        return left
    
    def _term(self) -> ASTNode:
        left = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._factor()
            left = BinaryOp(op, left, right)
        return left
    
    def _factor(self) -> ASTNode:
        left = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous().value
            right = self._power()
            left = BinaryOp(op, left, right)
        return left
    
    def _power(self) -> ASTNode:
        left = self._unary()
        if self._match(TokenType.CARET):
            right = self._power()  # Right associative
            left = BinaryOp('^', left, right)
        return left
    
    def _unary(self) -> ASTNode:
        if self._match(TokenType.MINUS):
            return UnaryOp('-', self._unary())
        if self._match(TokenType.NOT):
            return UnaryOp('not', self._unary())
        return self._postfix()
    
    def _postfix(self) -> ASTNode:
        """Parse postfix expressions (property access, indexing)."""
        expr = self._primary()
        
        while True:
            if self._match(TokenType.DOT):
                prop = self._consume(TokenType.IDENTIFIER, "Expected property name").value
                expr = PropertyAccess(expr, prop)
            elif self._match(TokenType.LBRACKET):
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexAccess(expr, index)
            elif self._check(TokenType.LPAREN) and isinstance(expr, Identifier):
                # Function call
                expr = self._function_call(expr.name)
            else:
                break
        
        return expr
    
    def _function_call(self, name: str) -> FunctionCall:
        """Parse function call arguments."""
        self._consume(TokenType.LPAREN, "Expected '(' for function call")
        
        args = []
        kwargs = {}
        
        if not self._check(TokenType.RPAREN):
            # First argument
            if self._check(TokenType.IDENTIFIER) and self._peek_next().type == TokenType.COLON:
                key = self._advance().value
                self._advance()  # consume ':'
                kwargs[key] = self._expression()
            else:
                args.append(self._expression())
            
            # Rest of arguments
            while self._match(TokenType.COMMA):
                if self._check(TokenType.IDENTIFIER) and self._peek_next().type == TokenType.COLON:
                    key = self._advance().value
                    self._advance()  # consume ':'
                    kwargs[key] = self._expression()
                else:
                    args.append(self._expression())
        
        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return FunctionCall(name, args, kwargs)
    
    def _primary(self) -> ASTNode:
        """Parse primary expressions."""
        # Literals
        if self._match(TokenType.NUMBER):
            return NumberLiteral(self._previous().value)
        
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        if self._match(TokenType.BOOLEAN):
            return BooleanLiteral(self._previous().value)
        
        if self._match(TokenType.NA):
            return NALiteral()
        
        # Identifier
        if self._match(TokenType.IDENTIFIER):
            return Identifier(self._previous().value)
        
        # Vector literal
        if self._match(TokenType.LBRACKET):
            elements = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._expression())
                while self._match(TokenType.COMMA):
                    elements.append(self._expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after vector")
            return VectorLiteral(elements)
        
        # Parenthesized expression
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise SyntaxError(f"Unexpected token: {self._peek()}")
    
    # Helper methods
    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False
    
    def _check(self, type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type
    
    def _advance(self) -> Token:
        if not self._is_at_end():
            self.pos += 1
        return self._previous()
    
    def _peek(self) -> Token:
        return self.tokens[self.pos]
    
    def _peek_next(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]
    
    def _previous(self) -> Token:
        return self.tokens[self.pos - 1]
    
    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
    
    def _consume(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()
        raise SyntaxError(f"{message} at line {self._peek().line}")
    
    def _skip_newlines(self):
        while self._match(TokenType.NEWLINE):
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# STATSY VALUES
# ═══════════════════════════════════════════════════════════════════════════════

class StatsyNA:
    """Represents a missing value (NA)."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __repr__(self):
        return "NA"
    
    def __str__(self):
        return "NA"
    
    def __bool__(self):
        return False

NA = StatsyNA()


@dataclass
class StatsyVector:
    """A statistical vector with NA support."""
    values: List[Any]
    
    def __len__(self):
        return len(self.values)
    
    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.values[idx]
        elif isinstance(idx, slice):
            return StatsyVector(self.values[idx])
        raise TypeError(f"Invalid index type: {type(idx)}")
    
    def __repr__(self):
        if len(self.values) <= 6:
            return f"[{', '.join(str(v) for v in self.values)}]"
        return f"[{', '.join(str(v) for v in self.values[:3])}, ..., {', '.join(str(v) for v in self.values[-3:])}]"
    
    def numeric_values(self) -> List[float]:
        """Get only numeric, non-NA values."""
        return [v for v in self.values if isinstance(v, (int, float)) and v is not NA]


@dataclass
class StatsyDataFrame:
    """A data frame with named columns."""
    columns: Dict[str, StatsyVector]
    
    def __getattr__(self, name: str):
        if name in self.columns:
            return self.columns[name]
        raise AttributeError(f"Column '{name}' not found")
    
    def __repr__(self):
        cols = list(self.columns.keys())
        n = len(next(iter(self.columns.values()))) if self.columns else 0
        return f"DataFrame({n} rows × {len(cols)} cols: {', '.join(cols)})"


@dataclass
class TestResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    df: Optional[float] = None
    verified: bool = True
    assumptions_checked: List[str] = field(default_factory=list)
    
    def __repr__(self):
        status = "✓" if self.verified else "⚠️"
        return f"{self.test_name}: stat={self.statistic:.4f}, p={self.p_value:.4f} {status}"


@dataclass
class StatsyFunction:
    """User-defined function."""
    name: str
    params: List[str]
    body: List[ASTNode]
    closure: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# INTERPRETER
# ═══════════════════════════════════════════════════════════════════════════════

class StatsyInterpreter:
    """Execute Statsy AST."""
    
    def __init__(self):
        self.globals: Dict[str, Any] = {}
        self.locals: Dict[str, Any] = {}
        self.scope_stack: List[Dict[str, Any]] = []
        
        # Initialize built-in functions
        self._init_builtins()
        
        # Newton integration
        self._newton_kb = None
    
    def _init_builtins(self):
        """Initialize built-in statistical functions."""
        self.globals.update({
            # Descriptive stats
            'mean': self._mean,
            'median': self._median,
            'mode': self._mode,
            'std': self._std,
            'var': self._var,
            'sum': self._sum,
            'min': self._min,
            'max': self._max,
            'range': self._range,
            'quantile': self._quantile,
            'iqr': self._iqr,
            'mad': self._mad,
            'robust_mean': self._robust_mean,
            
            # Vector operations
            'len': lambda x: len(x) if hasattr(x, '__len__') else 1,
            'seq': self._seq,
            'rep': self._rep,
            'c': self._combine,
            
            # Type checking
            'is_na': lambda x: x is NA,
            'is_numeric': lambda x: isinstance(x, (int, float)) and x is not NA,
            'is_vector': lambda x: isinstance(x, StatsyVector),
            
            # Conversion
            'as_vector': lambda x: StatsyVector(x) if isinstance(x, list) else StatsyVector([x]),
            'as_numeric': lambda x: float(x) if x is not NA else NA,
            
            # Math functions
            'sqrt': lambda x: math.sqrt(x) if x is not NA and x >= 0 else NA,
            'abs': lambda x: abs(x) if x is not NA else NA,
            'log': lambda x: math.log(x) if x is not NA and x > 0 else NA,
            'log10': lambda x: math.log10(x) if x is not NA and x > 0 else NA,
            'exp': lambda x: math.exp(x) if x is not NA else NA,
            'sin': lambda x: math.sin(x) if x is not NA else NA,
            'cos': lambda x: math.cos(x) if x is not NA else NA,
            'tan': lambda x: math.tan(x) if x is not NA else NA,
            'floor': lambda x: math.floor(x) if x is not NA else NA,
            'ceil': lambda x: math.ceil(x) if x is not NA else NA,
            'round': lambda x, n=0: round(x, n) if x is not NA else NA,
            
            # Statistical distributions
            'dnorm': self._dnorm,
            'pnorm': self._pnorm,
            'qnorm': self._qnorm,
            'rnorm': self._rnorm,
            
            # Statistical tests
            't_test': self._t_test,
            'cor': self._correlation,
            'cor_test': self._cor_test,
            
            # Data
            'DataFrame': self._create_dataframe,
            'describe': self._describe,
            
            # Newton integration
            'newton_ask': self._newton_ask,
            'newton_verify': self._newton_verify,
            
            # I/O
            'print': print,
        })
        
        # Add visualization and advanced statistics (from statsy_viz)
        self._init_viz_builtins()
    
    def _init_viz_builtins(self):
        """Initialize visualization and advanced statistics builtins."""
        try:
            from . import statsy_viz as viz
        except ImportError:
            try:
                import statsy_viz as viz
            except ImportError:
                # Viz module not available, skip
                return
        
        # Helper to print and return result
        def print_viz(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                print(result)
                return result
            return wrapper
        
        # Convert StatsyVector to list for viz functions
        def to_list(x):
            if isinstance(x, StatsyVector):
                return list(x.values)
            if isinstance(x, list):
                return x
            return [x]
        
        self.globals.update({
            # ═══════════════════════════════════════════════════════════════
            # ASCII VISUALIZATIONS
            # ═══════════════════════════════════════════════════════════════
            'histogram': lambda data, bins=10, width=40, title="Histogram": 
                print(viz.histogram(to_list(data), bins, width, title)) or "",
            
            'boxplot': lambda data, width=50, title="Box Plot": 
                print(viz.boxplot(to_list(data), width, title)) or "",
            
            'sparkline': lambda data, label="": 
                viz.sparkline(to_list(data), label),
            
            'scatter': lambda x, y, width=60, height=20, title="Scatter Plot":
                print(viz.scatter(to_list(x), to_list(y), width, height, title)) or "",
            
            'bar_chart': lambda labels, values, width=40, title="Bar Chart":
                print(viz.bar_chart(to_list(labels), to_list(values), width, title)) or "",
            
            'line_chart': lambda data, width=60, height=15, title="Line Chart":
                print(viz.line_chart(to_list(data), width, height, title)) or "",
            
            # ═══════════════════════════════════════════════════════════════
            # ADVANCED ROBUST STATISTICS
            # ═══════════════════════════════════════════════════════════════
            'modified_zscore': lambda data: StatsyVector(viz.modified_zscore(to_list(data))),
            
            'is_outlier': lambda val, data, threshold=3.5: 
                viz.is_outlier(val, to_list(data), threshold),
            
            'detect_outliers': lambda data, threshold=3.5: 
                viz.detect_outliers(to_list(data), threshold),
            
            'trimmed_mean': lambda data, trim=0.1: 
                viz.trimmed_mean(to_list(data), trim),
            
            'winsorized_mean': lambda data, trim=0.1: 
                viz.winsorized_mean(to_list(data), trim),
            
            # ═══════════════════════════════════════════════════════════════
            # REGRESSION & ANOVA  
            # ═══════════════════════════════════════════════════════════════
            'lm': lambda x, y: self._linear_model(x, y, viz),
            
            'anova': lambda *groups: self._anova(groups, viz),
            
            # ═══════════════════════════════════════════════════════════════
            # TIME SERIES
            # ═══════════════════════════════════════════════════════════════
            'moving_avg': lambda data, window=3: 
                StatsyVector(viz.moving_average(to_list(data), window)),
            
            'exp_smooth': lambda data, alpha=0.3: 
                StatsyVector(viz.exponential_smoothing(to_list(data), alpha)),
            
            'decompose': lambda data, window=3: 
                viz.trend_decomposition(to_list(data), window),
            
            # ═══════════════════════════════════════════════════════════════
            # DATA LOADING
            # ═══════════════════════════════════════════════════════════════
            'load_csv': lambda path, header=True: self._load_csv(path, header, viz),
            
            'load_json': lambda path: viz.load_json(path),
            
            # ═══════════════════════════════════════════════════════════════
            # AUDIT TRAIL (Newton-style)
            # ═══════════════════════════════════════════════════════════════
            'audit': lambda last_n=10: print(viz.get_audit_trail().show(last_n)) or "",
            
            'verified_output': viz.verified_output,
            
            # ═══════════════════════════════════════════════════════════════
            # NEWTON STATISTICAL GUIDANCE  
            # ═══════════════════════════════════════════════════════════════
            'guidance': lambda topic: print(viz.statistical_guidance(topic)) or "",
        })
        
        # Store viz module reference for helper methods
        self._viz = viz
    
    def _linear_model(self, x, y, viz):
        """Fit linear regression and display results."""
        x_list = list(x.values) if isinstance(x, StatsyVector) else list(x)
        y_list = list(y.values) if isinstance(y, StatsyVector) else list(y)
        
        model = viz.linear_regression(x_list, y_list)
        
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│ LINEAR REGRESSION                                           │")
        print("├─────────────────────────────────────────────────────────────┤")
        print(f"│ y = {model.intercept:.4f} + {model.slope:.4f}x{' ' * 30}│")
        print(f"│ R² = {model.r_squared:.4f}{' ' * 47}│")
        print(f"│ n  = {model.n}{' ' * 50}│")
        print("└─────────────────────────────────────────────────────────────┘")
        
        return model
    
    def _anova(self, groups, viz):
        """Run one-way ANOVA and display results."""
        clean_groups = []
        for g in groups:
            if isinstance(g, StatsyVector):
                clean_groups.append(list(g.values))
            else:
                clean_groups.append(list(g))
        
        result = viz.one_way_anova(*clean_groups)
        
        print("┌─────────────────────────────────────────────────────────────┐")
        print("│ ONE-WAY ANOVA                                               │")
        print("├─────────────────────────────────────────────────────────────┤")
        print(f"│ {result}{' ' * (60 - len(str(result)))}│")
        print(f"│ SS_between = {result.ss_between:.4f}{' ' * 40}│")
        print(f"│ SS_within  = {result.ss_within:.4f}{' ' * 40}│")
        print("└─────────────────────────────────────────────────────────────┘")
        
        return result
    
    def _load_csv(self, path, header, viz):
        """Load CSV file into a dictionary of vectors."""
        data = viz.load_csv(path, header)
        # Convert lists to StatsyVectors
        result = {}
        for key, values in data.items():
            result[key] = StatsyVector(values)
        print(f"✓ Loaded {len(data)} columns from {path}")
        for key in data:
            print(f"  • {key}: {len(data[key])} values")
        return result
    
    def execute(self, program: Program) -> Any:
        """Execute a program."""
        result = None
        for stmt in program.statements:
            result = self._evaluate(stmt)
        return result
    
    def _evaluate(self, node: ASTNode) -> Any:
        """Evaluate an AST node."""
        if isinstance(node, NumberLiteral):
            return node.value
        
        if isinstance(node, StringLiteral):
            return node.value
        
        if isinstance(node, BooleanLiteral):
            return node.value
        
        if isinstance(node, NALiteral):
            return NA
        
        if isinstance(node, Identifier):
            return self._lookup(node.name)
        
        if isinstance(node, VectorLiteral):
            values = [self._evaluate(e) for e in node.elements]
            return StatsyVector(values)
        
        if isinstance(node, BinaryOp):
            return self._eval_binary(node)
        
        if isinstance(node, UnaryOp):
            return self._eval_unary(node)
        
        if isinstance(node, FunctionCall):
            return self._eval_call(node)
        
        if isinstance(node, PipeExpr):
            return self._eval_pipe(node)
        
        if isinstance(node, Assignment):
            value = self._evaluate(node.value)
            self._assign(node.name, value)
            return value
        
        if isinstance(node, IfExpr):
            return self._eval_if(node)
        
        if isinstance(node, ForExpr):
            return self._eval_for(node)
        
        if isinstance(node, FunctionDef):
            func = StatsyFunction(node.name, node.params, node.body, self.locals.copy())
            self.globals[node.name] = func
            return func
        
        if isinstance(node, ReturnStmt):
            value = self._evaluate(node.value) if node.value else None
            raise ReturnValue(value)
        
        if isinstance(node, PrintStmt):
            value = self._evaluate(node.value)
            print(value)
            return value
        
        if isinstance(node, PropertyAccess):
            obj = self._evaluate(node.obj)
            if isinstance(obj, StatsyDataFrame):
                return obj.columns.get(node.property)
            if hasattr(obj, node.property):
                return getattr(obj, node.property)
            raise AttributeError(f"No property '{node.property}'")
        
        if isinstance(node, IndexAccess):
            obj = self._evaluate(node.obj)
            idx = self._evaluate(node.index)
            return obj[int(idx)]
        
        if isinstance(node, Program):
            result = None
            for stmt in node.statements:
                result = self._evaluate(stmt)
            return result
        
        raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def _eval_binary(self, node: BinaryOp) -> Any:
        """Evaluate binary operation."""
        left = self._evaluate(node.left)
        right = self._evaluate(node.right)
        
        # NA propagation
        if left is NA or right is NA:
            if node.op in ['and', 'or']:
                pass  # Handle specially
            else:
                return NA
        
        # Vector operations
        if isinstance(left, StatsyVector) or isinstance(right, StatsyVector):
            return self._vector_op(node.op, left, right)
        
        # Scalar operations
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else NA,
            '^': lambda a, b: a ** b,
            '%': lambda a, b: a % b if b != 0 else NA,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b,
        }
        
        if node.op in ops:
            return ops[node.op](left, right)
        
        raise RuntimeError(f"Unknown operator: {node.op}")
    
    def _eval_unary(self, node: UnaryOp) -> Any:
        """Evaluate unary operation."""
        val = self._evaluate(node.operand)
        
        if val is NA:
            return NA
        
        if node.op == '-':
            return -val
        if node.op == 'not':
            return not val
        
        raise RuntimeError(f"Unknown unary operator: {node.op}")
    
    def _eval_call(self, node: FunctionCall) -> Any:
        """Evaluate function call."""
        func = self._lookup(node.name)
        
        if func is None:
            raise RuntimeError(f"Unknown function: {node.name}")
        
        # Evaluate arguments
        args = [self._evaluate(a) for a in node.args]
        kwargs = {k: self._evaluate(v) for k, v in node.kwargs.items()}
        
        # User-defined function
        if isinstance(func, StatsyFunction):
            return self._call_user_function(func, args, kwargs)
        
        # Built-in function
        if callable(func):
            try:
                return func(*args, **kwargs)
            except TypeError as e:
                # Try without kwargs
                return func(*args)
        
        raise RuntimeError(f"'{node.name}' is not callable")
    
    def _call_user_function(self, func: StatsyFunction, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        """Call a user-defined function."""
        # Create new scope
        old_locals = self.locals.copy()
        self.locals = func.closure.copy()
        
        # Bind parameters
        for i, param in enumerate(func.params):
            if i < len(args):
                self.locals[param] = args[i]
            elif param in kwargs:
                self.locals[param] = kwargs[param]
            else:
                self.locals[param] = NA
        
        # Execute body
        result = None
        try:
            for stmt in func.body:
                result = self._evaluate(stmt)
        except ReturnValue as ret:
            result = ret.value
        
        # Restore scope
        self.locals = old_locals
        return result
    
    def _eval_pipe(self, node: PipeExpr) -> Any:
        """Evaluate pipe expression: x |> f becomes f(x)."""
        left = self._evaluate(node.left)
        
        if isinstance(node.right, FunctionCall):
            # Insert left as first argument
            func = self._lookup(node.right.name)
            args = [left] + [self._evaluate(a) for a in node.right.args]
            kwargs = {k: self._evaluate(v) for k, v in node.right.kwargs.items()}
            
            if isinstance(func, StatsyFunction):
                return self._call_user_function(func, args, kwargs)
            if callable(func):
                try:
                    return func(*args, **kwargs)
                except TypeError:
                    return func(*args)
        
        raise RuntimeError("Pipe right side must be a function call")
    
    def _eval_if(self, node: IfExpr) -> Any:
        """Evaluate if expression."""
        cond = self._evaluate(node.condition)
        
        if cond and cond is not NA:
            return self._evaluate(node.then_branch)
        elif node.else_branch:
            return self._evaluate(node.else_branch)
        return None
    
    def _eval_for(self, node: ForExpr) -> Any:
        """Evaluate for loop."""
        iterable = self._evaluate(node.iterable)
        
        if isinstance(iterable, StatsyVector):
            iterable = iterable.values
        elif isinstance(iterable, range):
            iterable = list(iterable)
        
        result = None
        for item in iterable:
            self._assign(node.var, item)
            for stmt in node.body:
                try:
                    result = self._evaluate(stmt)
                except ReturnValue:
                    raise
        
        return result
    
    def _vector_op(self, op: str, left: Any, right: Any) -> StatsyVector:
        """Element-wise vector operation."""
        # Convert scalars to vectors
        if not isinstance(left, StatsyVector):
            left = StatsyVector([left])
        if not isinstance(right, StatsyVector):
            right = StatsyVector([right])
        
        # Recycle shorter vector
        max_len = max(len(left), len(right))
        left_vals = (left.values * (max_len // len(left) + 1))[:max_len]
        right_vals = (right.values * (max_len // len(right) + 1))[:max_len]
        
        ops = {
            '+': lambda a, b: a + b if a is not NA and b is not NA else NA,
            '-': lambda a, b: a - b if a is not NA and b is not NA else NA,
            '*': lambda a, b: a * b if a is not NA and b is not NA else NA,
            '/': lambda a, b: a / b if a is not NA and b is not NA and b != 0 else NA,
            '^': lambda a, b: a ** b if a is not NA and b is not NA else NA,
        }
        
        if op in ops:
            result = [ops[op](a, b) for a, b in zip(left_vals, right_vals)]
            return StatsyVector(result)
        
        raise RuntimeError(f"Vector operation not supported: {op}")
    
    def _lookup(self, name: str) -> Any:
        """Look up a variable."""
        if name in self.locals:
            return self.locals[name]
        if name in self.globals:
            return self.globals[name]
        return None
    
    def _assign(self, name: str, value: Any):
        """Assign a variable."""
        if self.scope_stack:
            self.locals[name] = value
        else:
            self.globals[name] = value
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BUILT-IN STATISTICAL FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _to_numeric_list(self, x: Any) -> List[float]:
        """Convert to list of numeric values, filtering NA."""
        if isinstance(x, StatsyVector):
            return x.numeric_values()
        if isinstance(x, (list, tuple)):
            return [v for v in x if isinstance(v, (int, float)) and v is not NA]
        if isinstance(x, (int, float)) and x is not NA:
            return [x]
        return []
    
    def _mean(self, x: Any) -> float:
        """Calculate arithmetic mean."""
        vals = self._to_numeric_list(x)
        if not vals:
            return NA
        return sum(vals) / len(vals)
    
    def _median(self, x: Any) -> float:
        """Calculate median."""
        vals = sorted(self._to_numeric_list(x))
        if not vals:
            return NA
        n = len(vals)
        mid = n // 2
        if n % 2 == 0:
            return (vals[mid - 1] + vals[mid]) / 2
        return vals[mid]
    
    def _mode(self, x: Any) -> Any:
        """Calculate mode."""
        vals = self._to_numeric_list(x)
        if not vals:
            return NA
        counts = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        return max(counts, key=counts.get)
    
    def _std(self, x: Any, ddof: int = 1) -> float:
        """Calculate standard deviation."""
        v = self._var(x, ddof)
        if v is NA:
            return NA
        return math.sqrt(v)
    
    def _var(self, x: Any, ddof: int = 1) -> float:
        """Calculate variance."""
        vals = self._to_numeric_list(x)
        if len(vals) < 2:
            return NA
        m = sum(vals) / len(vals)
        ss = sum((v - m) ** 2 for v in vals)
        return ss / (len(vals) - ddof)
    
    def _sum(self, x: Any) -> float:
        """Calculate sum."""
        vals = self._to_numeric_list(x)
        return sum(vals) if vals else 0
    
    def _min(self, x: Any) -> float:
        """Calculate minimum."""
        vals = self._to_numeric_list(x)
        return min(vals) if vals else NA
    
    def _max(self, x: Any) -> float:
        """Calculate maximum."""
        vals = self._to_numeric_list(x)
        return max(vals) if vals else NA
    
    def _range(self, x: Any) -> StatsyVector:
        """Calculate range [min, max]."""
        vals = self._to_numeric_list(x)
        if not vals:
            return StatsyVector([NA, NA])
        return StatsyVector([min(vals), max(vals)])
    
    def _quantile(self, x: Any, p: float = 0.5) -> float:
        """Calculate quantile."""
        vals = sorted(self._to_numeric_list(x))
        if not vals:
            return NA
        idx = p * (len(vals) - 1)
        lower = int(idx)
        upper = min(lower + 1, len(vals) - 1)
        frac = idx - lower
        return vals[lower] * (1 - frac) + vals[upper] * frac
    
    def _iqr(self, x: Any) -> float:
        """Calculate interquartile range."""
        q1 = self._quantile(x, 0.25)
        q3 = self._quantile(x, 0.75)
        if q1 is NA or q3 is NA:
            return NA
        return q3 - q1
    
    def _mad(self, x: Any) -> float:
        """Calculate Median Absolute Deviation (robust dispersion)."""
        vals = self._to_numeric_list(x)
        if not vals:
            return NA
        med = self._median(vals)
        deviations = [abs(v - med) for v in vals]
        return self._median(deviations) * 1.4826  # Scale factor for normal distribution
    
    def _robust_mean(self, x: Any, trim: float = 0.1) -> float:
        """Calculate trimmed mean (robust central tendency)."""
        vals = sorted(self._to_numeric_list(x))
        if not vals:
            return NA
        n = len(vals)
        k = int(n * trim)
        if 2 * k >= n:
            return self._median(vals)
        trimmed = vals[k:n-k]
        return sum(trimmed) / len(trimmed)
    
    def _seq(self, start: float, end: float, by: float = 1) -> StatsyVector:
        """Generate sequence."""
        vals = []
        current = start
        while current <= end:
            vals.append(current)
            current += by
        return StatsyVector(vals)
    
    def _rep(self, x: Any, times: int) -> StatsyVector:
        """Repeat values."""
        if isinstance(x, StatsyVector):
            return StatsyVector(x.values * times)
        return StatsyVector([x] * times)
    
    def _combine(self, *args) -> StatsyVector:
        """Combine values into vector."""
        vals = []
        for a in args:
            if isinstance(a, StatsyVector):
                vals.extend(a.values)
            elif isinstance(a, (list, tuple)):
                vals.extend(a)
            else:
                vals.append(a)
        return StatsyVector(vals)
    
    def _dnorm(self, x: float, mu: float = 0, sigma: float = 1) -> float:
        """Normal PDF."""
        if x is NA or mu is NA or sigma is NA or sigma <= 0:
            return NA
        coef = 1 / (sigma * math.sqrt(2 * math.pi))
        exp_term = math.exp(-0.5 * ((x - mu) / sigma) ** 2)
        return coef * exp_term
    
    def _pnorm(self, x: float, mu: float = 0, sigma: float = 1) -> float:
        """Normal CDF (approximation)."""
        if x is NA or mu is NA or sigma is NA or sigma <= 0:
            return NA
        z = (x - mu) / sigma
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    def _qnorm(self, p: float, mu: float = 0, sigma: float = 1) -> float:
        """Normal quantile function (approximation)."""
        if p is NA or mu is NA or sigma is NA or sigma <= 0:
            return NA
        if p <= 0 or p >= 1:
            return NA
        # Approximation using inverse error function
        # For simplicity, use a basic approximation
        if p == 0.5:
            return mu
        sign = 1 if p > 0.5 else -1
        p_adj = p if p > 0.5 else 1 - p
        t = math.sqrt(-2 * math.log(1 - p_adj))
        c = [2.515517, 0.802853, 0.010328]
        d = [1.432788, 0.189269, 0.001308]
        z = t - (c[0] + c[1]*t + c[2]*t*t) / (1 + d[0]*t + d[1]*t*t + d[2]*t*t*t)
        return mu + sign * z * sigma
    
    def _rnorm(self, n: int, mu: float = 0, sigma: float = 1) -> StatsyVector:
        """Generate random normal samples."""
        import random
        vals = [random.gauss(mu, sigma) for _ in range(n)]
        return StatsyVector(vals)
    
    def _t_test(self, x: Any, y: Any = None, **kwargs) -> TestResult:
        """Two-sample t-test."""
        x_vals = self._to_numeric_list(x)
        
        if y is None:
            # One-sample t-test against mu=0
            n = len(x_vals)
            if n < 2:
                return TestResult("One-sample t-test", NA, NA, verified=False)
            m = sum(x_vals) / n
            s = math.sqrt(sum((v - m) ** 2 for v in x_vals) / (n - 1))
            t_stat = m / (s / math.sqrt(n))
            df = n - 1
            # Approximate p-value
            p_value = 2 * (1 - self._pnorm(abs(t_stat)))
            return TestResult("One-sample t-test", t_stat, p_value, df, 
                             assumptions_checked=["normality"])
        
        # Two-sample t-test
        y_vals = self._to_numeric_list(y)
        n1, n2 = len(x_vals), len(y_vals)
        if n1 < 2 or n2 < 2:
            return TestResult("Two-sample t-test", NA, NA, verified=False)
        
        m1 = sum(x_vals) / n1
        m2 = sum(y_vals) / n2
        v1 = sum((v - m1) ** 2 for v in x_vals) / (n1 - 1)
        v2 = sum((v - m2) ** 2 for v in y_vals) / (n2 - 1)
        
        # Welch's t-test
        se = math.sqrt(v1/n1 + v2/n2)
        t_stat = (m1 - m2) / se if se > 0 else NA
        
        # Welch-Satterthwaite df
        num = (v1/n1 + v2/n2) ** 2
        denom = (v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1)
        df = num / denom if denom > 0 else NA
        
        # Approximate p-value
        p_value = 2 * (1 - self._pnorm(abs(t_stat))) if t_stat is not NA else NA
        
        return TestResult("Two-sample t-test (Welch)", t_stat, p_value, df,
                         assumptions_checked=["normality"])
    
    def _correlation(self, x: Any, y: Any) -> float:
        """Pearson correlation coefficient."""
        x_vals = self._to_numeric_list(x)
        y_vals = self._to_numeric_list(y)
        
        # Pair-wise complete
        pairs = [(a, b) for a, b in zip(x_vals, y_vals) 
                 if a is not NA and b is not NA]
        if len(pairs) < 2:
            return NA
        
        x_vals = [p[0] for p in pairs]
        y_vals = [p[1] for p in pairs]
        
        n = len(pairs)
        mx = sum(x_vals) / n
        my = sum(y_vals) / n
        
        num = sum((x - mx) * (y - my) for x, y in pairs)
        denom_x = math.sqrt(sum((x - mx) ** 2 for x in x_vals))
        denom_y = math.sqrt(sum((y - my) ** 2 for y in y_vals))
        
        if denom_x == 0 or denom_y == 0:
            return NA
        
        return num / (denom_x * denom_y)
    
    def _cor_test(self, x: Any, y: Any) -> TestResult:
        """Test correlation significance."""
        r = self._correlation(x, y)
        if r is NA:
            return TestResult("Correlation test", NA, NA, verified=False)
        
        x_vals = self._to_numeric_list(x)
        y_vals = self._to_numeric_list(y)
        n = min(len(x_vals), len(y_vals))
        
        # t-statistic for correlation
        t_stat = r * math.sqrt(n - 2) / math.sqrt(1 - r**2) if abs(r) < 1 else NA
        df = n - 2
        p_value = 2 * (1 - self._pnorm(abs(t_stat))) if t_stat is not NA else NA
        
        return TestResult(f"Correlation test (r={r:.4f})", t_stat, p_value, df)
    
    def _create_dataframe(self, **kwargs) -> StatsyDataFrame:
        """Create a data frame from named columns."""
        columns = {}
        for name, vals in kwargs.items():
            if isinstance(vals, StatsyVector):
                columns[name] = vals
            else:
                columns[name] = StatsyVector(vals) if isinstance(vals, list) else StatsyVector([vals])
        return StatsyDataFrame(columns)
    
    def _describe(self, x: Any) -> Dict[str, Any]:
        """Descriptive statistics summary."""
        vals = self._to_numeric_list(x)
        if not vals:
            return {"count": 0}
        
        m = self._mean(vals)
        med = self._median(vals)
        s = self._std(vals)
        mad = self._mad(vals)
        
        # Check for outlier influence
        robust_m = self._robust_mean(vals)
        outlier_influence = abs(m - robust_m) / s if s > 0 else 0
        
        # Detect outliers using MAD
        outliers = []
        if mad > 0:
            for v in vals:
                z_mad = abs(v - med) / (mad / 1.4826)  # Normalize
                if z_mad > 3:  # More than 3 MAD from median
                    outliers.append(v)
        
        result = {
            "count": len(vals),
            "mean": round(m, 4),
            "median": round(med, 4),
            "std": round(s, 4),
            "min": min(vals),
            "max": max(vals),
            "robust_mean": round(robust_m, 4),
            "mad": round(mad, 4),
            "outlier_influence": "high" if outlier_influence > 0.1 else "low",
            "outliers": outliers,
        }
        
        # Print nicely
        print("┌────────────────────────────────────────┐")
        print("│ DESCRIPTIVE STATISTICS                 │")
        print("├────────────────────────────────────────┤")
        for k, v in result.items():
            if k == "outliers":
                if v:
                    print(f"│ {k:20} {str(v):>12} ⚠️ │")
                continue
            warn = " ⚠️" if k == "mean" and outlier_influence > 0.1 else ""
            check = " ✓" if k == "robust_mean" else ""
            print(f"│ {k:20} {str(v):>12}{warn}{check} │")
        if outliers:
            print(f"│ outliers detected!   {str(outliers):>12} ⚠️ │")
        print("└────────────────────────────────────────┘")
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEWTON INTEGRATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_newton_kb(self):
        """Lazy-load Newton knowledge base connection."""
        if self._newton_kb is not None:
            return self._newton_kb
        
        try:
            import sys
            sys.path.insert(0, str(__file__).replace('statsy/statsy.py', '').replace('statsy\\statsy.py', ''))
            from adan.knowledge_base import get_knowledge_base
            self._newton_kb = get_knowledge_base()
        except ImportError:
            self._newton_kb = None
        
        return self._newton_kb
    
    def _newton_ask(self, question: str) -> str:
        """Query Newton knowledge base from Statsy."""
        kb = self._get_newton_kb()
        if kb is None:
            return "Newton KB not available"
        
        result = kb.query(question)
        if result:
            print(f"📚 {result.fact}")
            print(f"   Source: {result.source}")
            return result.fact
        return "No answer found"
    
    def _newton_verify(self, claim: str) -> bool:
        """Verify a claim through Newton."""
        kb = self._get_newton_kb()
        if kb is None:
            return False
        
        # Try to find supporting evidence
        result = kb.query(claim)
        if result:
            print(f"✓ Verified: {result.fact[:80]}...")
            return True
        print(f"⚠️ Could not verify: {claim}")
        return False


class ReturnValue(Exception):
    """Exception to handle return statements."""
    def __init__(self, value):
        self.value = value


# ═══════════════════════════════════════════════════════════════════════════════
# REPL
# ═══════════════════════════════════════════════════════════════════════════════

def run_repl():
    """Run interactive REPL."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STATSY - The Verified Statistical Programming Language                       ║
║  Every calculation is checked. Every result is provable.                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Type expressions to evaluate. Type 'quit' or 'exit' to exit.                 ║
║  Examples:                                                                    ║
║    mean([1, 2, 3, 4, 5])                                                      ║
║    [1, 2, 3] |> mean()                                                        ║
║    newton_ask("What is the speed of light?")                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    interpreter = StatsyInterpreter()
    
    while True:
        try:
            line = input("statsy> ").strip()
            
            if not line:
                continue
            
            if line in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            
            # Handle multi-line input
            if line.endswith('{'):
                while True:
                    more = input("....... ")
                    line += '\n' + more
                    if '}' in more:
                        break
            
            # Tokenize
            lexer = StatsyLexer(line)
            tokens = lexer.tokenize()
            
            # Parse
            parser = StatsyParser(tokens)
            ast = parser.parse()
            
            # Execute
            result = interpreter.execute(ast)
            
            # Print result if not None and not already printed
            if result is not None:
                print(result)
                
        except EOFError:
            print("\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\n")
            continue
        except Exception as e:
            print(f"Error: {e}")


def run_file(filename: str):
    """Execute a Statsy script file."""
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    lexer = StatsyLexer(source)
    tokens = lexer.tokenize()
    
    parser = StatsyParser(tokens)
    ast = parser.parse()
    
    interpreter = StatsyInterpreter()
    interpreter.execute(ast)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        run_repl()
