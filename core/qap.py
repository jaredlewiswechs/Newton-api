#!/usr/bin/env python3
"""
===============================================================================
NEWTON QAP COMPILER - TINYALK TO QUADRATIC ARITHMETIC PROGRAM
Cryptographic proof layer for Newton's constraint verification system.

This module compiles tinyTalk constraints to:
- Lexer tokens
- Abstract Syntax Tree (AST)
- Symbol tables with enum encodings
- SSA/IR representation
- R1CS (Rank-1 Constraint System)
- QAP polynomials

The QAP compilation enables zero-knowledge proofs of constraint satisfaction,
adding cryptographic verifiability to Newton's existing structural proofs.

Historical Lineage:
- R1CS: Rank-1 Constraint Systems (Ben-Sasson et al., 2013)
- QAP: Quadratic Arithmetic Programs (Gennaro et al., 2012)
- Groth16: zkSNARK construction (Groth, 2016)

finfr in circuit form: g2 * 1 = 0 (the unrepresentable state)
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Set
from enum import Enum, auto
import re
import hashlib
from fractions import Fraction


# ===============================================================================
# FIELD ARITHMETIC - BN254 Scalar Field
# ===============================================================================

# BN254 (alt_bn128) scalar field prime
# This is the order of the scalar field used in Ethereum's precompiles
BN254_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# For testing with smaller field
TEST_PRIME = 2**31 - 1  # Mersenne prime


class FieldElement:
    """
    Element in a prime field F_p.

    Used for circuit arithmetic where all operations are mod p.
    """

    _prime = BN254_PRIME

    def __init__(self, value: int, prime: Optional[int] = None):
        self.prime = prime or FieldElement._prime
        self.value = value % self.prime

    @classmethod
    def set_prime(cls, prime: int):
        """Set the global prime for all field elements."""
        cls._prime = prime

    def __add__(self, other: 'FieldElement') -> 'FieldElement':
        return FieldElement((self.value + other.value) % self.prime, self.prime)

    def __sub__(self, other: 'FieldElement') -> 'FieldElement':
        return FieldElement((self.value - other.value) % self.prime, self.prime)

    def __mul__(self, other: 'FieldElement') -> 'FieldElement':
        return FieldElement((self.value * other.value) % self.prime, self.prime)

    def __neg__(self) -> 'FieldElement':
        return FieldElement((-self.value) % self.prime, self.prime)

    def __eq__(self, other) -> bool:
        if isinstance(other, FieldElement):
            return self.value == other.value and self.prime == other.prime
        return self.value == other

    def __hash__(self) -> int:
        return hash((self.value, self.prime))

    def __repr__(self) -> str:
        return f"F({self.value})"

    def inverse(self) -> 'FieldElement':
        """Multiplicative inverse using extended Euclidean algorithm."""
        if self.value == 0:
            raise ValueError("Cannot invert zero")
        return FieldElement(pow(self.value, self.prime - 2, self.prime), self.prime)

    def __truediv__(self, other: 'FieldElement') -> 'FieldElement':
        return self * other.inverse()

    @classmethod
    def zero(cls, prime: Optional[int] = None) -> 'FieldElement':
        return cls(0, prime)

    @classmethod
    def one(cls, prime: Optional[int] = None) -> 'FieldElement':
        return cls(1, prime)


def F(value: int, prime: Optional[int] = None) -> FieldElement:
    """Shorthand for creating field elements."""
    return FieldElement(value, prime)


# ===============================================================================
# LEXER - Token Types and Tokenization
# ===============================================================================

class TokenType(Enum):
    # Keywords
    WHEN = auto()
    FIN = auto()
    FINFR = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    TRUE = auto()
    FALSE = auto()

    # Operators
    EQEQ = auto()      # ==
    NE = auto()        # !=
    LT = auto()        # <
    GT = auto()        # >
    LE = auto()        # <=
    GE = auto()        # >=

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()

    # Literals
    IDENT = auto()
    STRING = auto()
    NUMBER = auto()
    BOOL = auto()

    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """A lexer token."""
    type: TokenType
    value: Any
    line: int = 0
    column: int = 0

    def __repr__(self) -> str:
        if self.value is not None:
            return f"[{self.type.name}({self.value})]"
        return f"[{self.type.name}]"


class Lexer:
    """
    Tokenizes tinyTalk constraint specifications.

    Converts source text into a stream of tokens for parsing.
    """

    KEYWORDS = {
        'when': TokenType.WHEN,
        'fin': TokenType.FIN,
        'finfr': TokenType.FINFR,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'in': TokenType.IN,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Tokenize the source and return list of tokens."""
        self.tokens = []

        while self.pos < len(self.source):
            self._skip_whitespace()

            if self.pos >= len(self.source):
                break

            char = self.source[self.pos]

            # Skip comments
            if char == '#':
                self._skip_comment()
                continue

            # Newline
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, None, self.line, self.column))
                self._advance()
                self.line += 1
                self.column = 1
                continue

            # String literals
            if char == '"':
                self.tokens.append(self._read_string())
                continue

            # Numbers
            if char.isdigit() or (char == '-' and self._peek(1).isdigit()):
                self.tokens.append(self._read_number())
                continue

            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self._read_identifier())
                continue

            # Two-character operators
            if self.pos + 1 < len(self.source):
                two_char = self.source[self.pos:self.pos + 2]
                if two_char == '==':
                    self.tokens.append(Token(TokenType.EQEQ, '==', self.line, self.column))
                    self._advance(2)
                    continue
                elif two_char == '!=':
                    self.tokens.append(Token(TokenType.NE, '!=', self.line, self.column))
                    self._advance(2)
                    continue
                elif two_char == '<=':
                    self.tokens.append(Token(TokenType.LE, '<=', self.line, self.column))
                    self._advance(2)
                    continue
                elif two_char == '>=':
                    self.tokens.append(Token(TokenType.GE, '>=', self.line, self.column))
                    self._advance(2)
                    continue

            # Single-character operators
            if char == '<':
                self.tokens.append(Token(TokenType.LT, '<', self.line, self.column))
                self._advance()
                continue
            elif char == '>':
                self.tokens.append(Token(TokenType.GT, '>', self.line, self.column))
                self._advance()
                continue
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.column))
                self._advance()
                continue
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.column))
                self._advance()
                continue
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self._advance()
                continue

            # Unknown character - skip
            self._advance()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _advance(self, count: int = 1):
        """Advance position by count characters."""
        for _ in range(count):
            if self.pos < len(self.source):
                self.column += 1
                self.pos += 1

    def _peek(self, offset: int = 0) -> str:
        """Peek at character at current position + offset."""
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''

    def _skip_whitespace(self):
        """Skip whitespace except newlines."""
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self._advance()

    def _skip_comment(self):
        """Skip comment until end of line."""
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self._advance()

    def _read_string(self) -> Token:
        """Read a string literal."""
        start_col = self.column
        self._advance()  # Skip opening quote

        value = ""
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\\' and self.pos + 1 < len(self.source):
                self._advance()
                if self.source[self.pos] == 'n':
                    value += '\n'
                elif self.source[self.pos] == 't':
                    value += '\t'
                else:
                    value += self.source[self.pos]
            else:
                value += self.source[self.pos]
            self._advance()

        self._advance()  # Skip closing quote
        return Token(TokenType.STRING, value, self.line, start_col)

    def _read_number(self) -> Token:
        """Read a numeric literal."""
        start_col = self.column
        start_pos = self.pos

        if self.source[self.pos] == '-':
            self._advance()

        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            self._advance()

        value_str = self.source[start_pos:self.pos]
        if '.' in value_str:
            value = float(value_str)
        else:
            value = int(value_str)

        return Token(TokenType.NUMBER, value, self.line, start_col)

    def _read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_col = self.column
        start_pos = self.pos

        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()

        value = self.source[start_pos:self.pos]

        # Check for keywords
        if value.lower() in self.KEYWORDS:
            token_type = self.KEYWORDS[value.lower()]
            if token_type in (TokenType.TRUE, TokenType.FALSE):
                return Token(TokenType.BOOL, value.lower() == 'true', self.line, start_col)
            return Token(token_type, value, self.line, start_col)

        return Token(TokenType.IDENT, value, self.line, start_col)


# ===============================================================================
# AST - Abstract Syntax Tree Nodes
# ===============================================================================

@dataclass
class ASTNode:
    """Base class for AST nodes."""
    pass


@dataclass
class Program(ASTNode):
    """Root node containing all rules."""
    rules: List['Rule']


@dataclass
class Rule(ASTNode):
    """A when/fin/finfr rule."""
    guard: 'Expression'
    action: str  # 'fin' or 'finfr' or action name


@dataclass
class Expression(ASTNode):
    """Base class for expressions."""
    pass


@dataclass
class BinaryOp(Expression):
    """Binary operation (and, or, ==, etc.)."""
    op: str
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation (not)."""
    op: str
    operand: Expression


@dataclass
class Comparison(Expression):
    """Comparison operation."""
    op: str  # '==', '!=', '<', '>', '<=', '>='
    left: Expression
    right: Expression


@dataclass
class InExpr(Expression):
    """Set membership check."""
    element: Expression
    set_name: str


@dataclass
class Identifier(Expression):
    """Variable reference."""
    name: str


@dataclass
class Literal(Expression):
    """Literal value."""
    value: Any


# ===============================================================================
# PARSER - Build AST from Tokens
# ===============================================================================

class Parser:
    """
    Parses tokens into an AST.

    Grammar (simplified):
        program     -> rule*
        rule        -> 'when' expression action
        action      -> 'fin' IDENT? | 'finfr'
        expression  -> or_expr
        or_expr     -> and_expr ('or' and_expr)*
        and_expr    -> not_expr ('and' not_expr)*
        not_expr    -> 'not' not_expr | comparison
        comparison  -> primary (('==' | '!=' | '<' | '>' | '<=' | '>=') primary)?
                     | primary 'in' IDENT
        primary     -> IDENT | STRING | NUMBER | BOOL | '(' expression ')'
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Program:
        """Parse tokens into a Program AST."""
        rules = []

        while not self._at_end():
            self._skip_newlines()
            if self._at_end():
                break

            if self._check(TokenType.WHEN):
                rules.append(self._parse_rule())
            else:
                self._advance()  # Skip unknown tokens

        return Program(rules=rules)

    def _parse_rule(self) -> Rule:
        """Parse a when/fin/finfr rule."""
        self._consume(TokenType.WHEN, "Expected 'when'")
        self._skip_newlines()

        guard = self._parse_expression()
        self._skip_newlines()

        # Parse action
        if self._check(TokenType.FIN):
            self._advance()
            self._skip_newlines()
            action_name = "fin"
            if self._check(TokenType.IDENT):
                action_name = self._advance().value
            return Rule(guard=guard, action=action_name)
        elif self._check(TokenType.FINFR):
            self._advance()
            return Rule(guard=guard, action="finfr")
        else:
            return Rule(guard=guard, action="fin")

    def _parse_expression(self) -> Expression:
        """Parse an expression."""
        return self._parse_or()

    def _parse_or(self) -> Expression:
        """Parse OR expression."""
        self._skip_newlines()
        expr = self._parse_and()

        self._skip_newlines()
        while self._check(TokenType.OR):
            self._advance()
            self._skip_newlines()
            right = self._parse_and()
            self._skip_newlines()
            expr = BinaryOp(op="or", left=expr, right=right)

        return expr

    def _parse_and(self) -> Expression:
        """Parse AND expression."""
        self._skip_newlines()
        expr = self._parse_not()

        self._skip_newlines()
        while self._check(TokenType.AND):
            self._advance()
            self._skip_newlines()
            right = self._parse_not()
            self._skip_newlines()
            expr = BinaryOp(op="and", left=expr, right=right)

        return expr

    def _parse_not(self) -> Expression:
        """Parse NOT expression."""
        if self._check(TokenType.NOT):
            self._advance()
            return UnaryOp(op="not", operand=self._parse_not())

        return self._parse_comparison()

    def _parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        left = self._parse_primary()

        # Check for 'in' operator
        if self._check(TokenType.IN):
            self._advance()
            set_name = self._consume(TokenType.IDENT, "Expected set name").value
            return InExpr(element=left, set_name=set_name)

        # Check for comparison operators
        if self._check(TokenType.EQEQ):
            self._advance()
            return Comparison(op="==", left=left, right=self._parse_primary())
        elif self._check(TokenType.NE):
            self._advance()
            return Comparison(op="!=", left=left, right=self._parse_primary())
        elif self._check(TokenType.LT):
            self._advance()
            return Comparison(op="<", left=left, right=self._parse_primary())
        elif self._check(TokenType.GT):
            self._advance()
            return Comparison(op=">", left=left, right=self._parse_primary())
        elif self._check(TokenType.LE):
            self._advance()
            return Comparison(op="<=", left=left, right=self._parse_primary())
        elif self._check(TokenType.GE):
            self._advance()
            return Comparison(op=">=", left=left, right=self._parse_primary())

        return left

    def _parse_primary(self) -> Expression:
        """Parse primary expression."""
        if self._check(TokenType.IDENT):
            return Identifier(name=self._advance().value)
        elif self._check(TokenType.STRING):
            return Literal(value=self._advance().value)
        elif self._check(TokenType.NUMBER):
            return Literal(value=self._advance().value)
        elif self._check(TokenType.BOOL):
            return Literal(value=self._advance().value)
        elif self._check(TokenType.TRUE):
            self._advance()
            return Literal(value=True)
        elif self._check(TokenType.FALSE):
            self._advance()
            return Literal(value=False)
        elif self._check(TokenType.LPAREN):
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')'")
            return expr

        raise SyntaxError(f"Unexpected token: {self._current()}")

    def _current(self) -> Token:
        """Get current token."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def _check(self, type: TokenType) -> bool:
        """Check if current token is of given type."""
        return not self._at_end() and self._current().type == type

    def _advance(self) -> Token:
        """Advance to next token and return current."""
        token = self._current()
        if not self._at_end():
            self.pos += 1
        return token

    def _consume(self, type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self._check(type):
            return self._advance()
        raise SyntaxError(f"{message}, got {self._current()}")

    def _at_end(self) -> bool:
        """Check if at end of tokens."""
        return self._current().type == TokenType.EOF

    def _skip_newlines(self):
        """Skip newline tokens."""
        while self._check(TokenType.NEWLINE):
            self._advance()


# ===============================================================================
# SYMBOL TABLE - Enum and Variable Bindings
# ===============================================================================

@dataclass
class EnumTable:
    """Maps string values to field integers."""
    name: str
    values: Dict[str, int] = field(default_factory=dict)
    next_value: int = 1

    def encode(self, value: str) -> int:
        """Get or assign integer encoding for a value."""
        if value not in self.values:
            self.values[value] = self.next_value
            self.next_value += 1
        return self.values[value]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "values": self.values}


@dataclass
class SetTable:
    """Represents a set for membership checks."""
    name: str
    elements: Set[str] = field(default_factory=set)

    def add(self, element: str):
        self.elements.add(element)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "elements": list(self.elements)}


class SymbolTable:
    """
    Symbol table for the QAP compiler.

    Tracks:
    - Enum tables for string->int mapping
    - Set tables for membership constraints
    - Witness variable indices
    """

    def __init__(self):
        self.enums: Dict[str, EnumTable] = {}
        self.sets: Dict[str, SetTable] = {}
        self.witness_vars: Dict[str, int] = {"1": 0}  # w[0] = 1 (constant)
        self.next_witness_idx: int = 1

    def get_or_create_enum(self, name: str) -> EnumTable:
        """Get or create enum table for a variable."""
        if name not in self.enums:
            self.enums[name] = EnumTable(name=name)
        return self.enums[name]

    def get_or_create_set(self, name: str) -> SetTable:
        """Get or create set table."""
        if name not in self.sets:
            self.sets[name] = SetTable(name=name)
        return self.sets[name]

    def allocate_witness(self, name: str) -> int:
        """Allocate a witness variable index."""
        if name not in self.witness_vars:
            self.witness_vars[name] = self.next_witness_idx
            self.next_witness_idx += 1
        return self.witness_vars[name]

    def get_witness_index(self, name: str) -> int:
        """Get witness index for a variable."""
        return self.witness_vars.get(name, -1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enums": {k: v.to_dict() for k, v in self.enums.items()},
            "sets": {k: v.to_dict() for k, v in self.sets.items()},
            "witness_vars": self.witness_vars,
            "next_witness_idx": self.next_witness_idx
        }


# ===============================================================================
# IR - Intermediate Representation (SSA-like)
# ===============================================================================

@dataclass
class IRInstruction:
    """Base class for IR instructions."""
    result: str  # Result variable name


@dataclass
class IRConst(IRInstruction):
    """Load constant value."""
    value: int


@dataclass
class IRSub(IRInstruction):
    """Subtraction: result = left - right."""
    left: str
    right: Union[str, int]


@dataclass
class IRMul(IRInstruction):
    """Multiplication: result = left * right."""
    left: str
    right: str


@dataclass
class IRIsZero(IRInstruction):
    """isZero gadget: produces (eq, inv) pair."""
    input: str
    eq_var: str
    inv_var: str


@dataclass
class IRMembership(IRInstruction):
    """Set membership check."""
    element: str
    set_name: str


@dataclass
class IRNot(IRInstruction):
    """Logical NOT: result = 1 - input."""
    input: str


@dataclass
class IRAssert(IRInstruction):
    """Assert constraint: variable must equal value."""
    variable: str
    value: int


class IRBuilder:
    """
    Builds IR from AST.

    Converts high-level expressions to low-level circuit operations.
    """

    def __init__(self, symbol_table: SymbolTable):
        self.symbols = symbol_table
        self.instructions: List[IRInstruction] = []
        self.temp_counter = 0

    def build(self, ast: Program) -> List[IRInstruction]:
        """Build IR from AST."""
        self.instructions = []

        for rule in ast.rules:
            guard_var = self._compile_expression(rule.guard)

            if rule.action == "finfr":
                # FINFR: guard must be false (guard == 0)
                self.instructions.append(IRAssert(
                    result=f"_assert_{len(self.instructions)}",
                    variable=guard_var,
                    value=0
                ))
            else:
                # FIN: allowed action, no constraint needed
                pass

        return self.instructions

    def _compile_expression(self, expr: Expression) -> str:
        """Compile expression and return result variable name."""
        if isinstance(expr, Literal):
            return self._compile_literal(expr)
        elif isinstance(expr, Identifier):
            return self._compile_identifier(expr)
        elif isinstance(expr, Comparison):
            return self._compile_comparison(expr)
        elif isinstance(expr, BinaryOp):
            return self._compile_binary(expr)
        elif isinstance(expr, UnaryOp):
            return self._compile_unary(expr)
        elif isinstance(expr, InExpr):
            return self._compile_in(expr)
        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")

    def _compile_literal(self, lit: Literal) -> str:
        """Compile literal value."""
        var_name = self._new_temp()

        if isinstance(lit.value, bool):
            value = 1 if lit.value else 0
        elif isinstance(lit.value, (int, float)):
            value = int(lit.value)
        else:
            # String - encode via enum
            enum = self.symbols.get_or_create_enum("_literals")
            value = enum.encode(str(lit.value))

        self.symbols.allocate_witness(var_name)
        self.instructions.append(IRConst(result=var_name, value=value))
        return var_name

    def _compile_identifier(self, ident: Identifier) -> str:
        """Compile identifier reference."""
        self.symbols.allocate_witness(ident.name)
        return ident.name

    def _compile_comparison(self, comp: Comparison) -> str:
        """Compile comparison to isZero gadget."""
        left_var = self._compile_expression(comp.left)
        right_var = self._compile_expression(comp.right)

        if comp.op == "==":
            # x == y becomes isZero(x - y)
            diff_var = self._new_temp()
            eq_var = self._new_temp()
            inv_var = self._new_temp()

            self.symbols.allocate_witness(diff_var)
            self.symbols.allocate_witness(eq_var)
            self.symbols.allocate_witness(inv_var)

            self.instructions.append(IRSub(result=diff_var, left=left_var, right=right_var))
            self.instructions.append(IRIsZero(result=eq_var, input=diff_var, eq_var=eq_var, inv_var=inv_var))

            return eq_var

        elif comp.op == "!=":
            # x != y is NOT isZero(x - y)
            eq_var = self._compile_comparison(Comparison(op="==", left=comp.left, right=comp.right))
            not_var = self._new_temp()
            self.symbols.allocate_witness(not_var)
            self.instructions.append(IRNot(result=not_var, input=eq_var))
            return not_var

        else:
            # <, >, <=, >= - for now, treat as range checks
            # In full implementation, would need comparison gadgets
            raise NotImplementedError(f"Comparison operator {comp.op} not yet implemented in circuit form")

    def _compile_binary(self, binop: BinaryOp) -> str:
        """Compile binary operation."""
        left_var = self._compile_expression(binop.left)
        right_var = self._compile_expression(binop.right)

        if binop.op == "and":
            # AND = multiplication of booleans
            result_var = self._new_temp()
            self.symbols.allocate_witness(result_var)
            self.instructions.append(IRMul(result=result_var, left=left_var, right=right_var))
            return result_var

        elif binop.op == "or":
            # OR = a + b - a*b (for booleans)
            # Simplified: 1 - (1-a)*(1-b)
            not_a = self._new_temp()
            not_b = self._new_temp()
            not_a_and_not_b = self._new_temp()
            result_var = self._new_temp()

            self.symbols.allocate_witness(not_a)
            self.symbols.allocate_witness(not_b)
            self.symbols.allocate_witness(not_a_and_not_b)
            self.symbols.allocate_witness(result_var)

            self.instructions.append(IRNot(result=not_a, input=left_var))
            self.instructions.append(IRNot(result=not_b, input=right_var))
            self.instructions.append(IRMul(result=not_a_and_not_b, left=not_a, right=not_b))
            self.instructions.append(IRNot(result=result_var, input=not_a_and_not_b))

            return result_var

        else:
            raise ValueError(f"Unknown binary operator: {binop.op}")

    def _compile_unary(self, unop: UnaryOp) -> str:
        """Compile unary operation."""
        operand_var = self._compile_expression(unop.operand)

        if unop.op == "not":
            result_var = self._new_temp()
            self.symbols.allocate_witness(result_var)
            self.instructions.append(IRNot(result=result_var, input=operand_var))
            return result_var

        raise ValueError(f"Unknown unary operator: {unop.op}")

    def _compile_in(self, in_expr: InExpr) -> str:
        """Compile set membership check."""
        element_var = self._compile_expression(in_expr.element)
        result_var = self._new_temp()

        self.symbols.allocate_witness(result_var)
        self.symbols.get_or_create_set(in_expr.set_name)

        self.instructions.append(IRMembership(
            result=result_var,
            element=element_var,
            set_name=in_expr.set_name
        ))

        return result_var

    def _new_temp(self) -> str:
        """Generate a new temporary variable name."""
        name = f"_t{self.temp_counter}"
        self.temp_counter += 1
        return name


# ===============================================================================
# R1CS - Rank-1 Constraint System
# ===============================================================================

@dataclass
class R1CSConstraint:
    """
    A single R1CS constraint: <A, w> * <B, w> = <C, w>

    Where A, B, C are coefficient vectors and w is the witness vector.
    """
    A: Dict[int, int]  # {witness_index: coefficient}
    B: Dict[int, int]
    C: Dict[int, int]
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "label": self.label
        }


class R1CSBuilder:
    """
    Builds R1CS constraints from IR.

    Each IR instruction is converted to one or more R1CS constraints.
    """

    def __init__(self, symbol_table: SymbolTable):
        self.symbols = symbol_table
        self.constraints: List[R1CSConstraint] = []

    def build(self, instructions: List[IRInstruction]) -> List[R1CSConstraint]:
        """Build R1CS from IR instructions."""
        self.constraints = []

        for instr in instructions:
            if isinstance(instr, IRConst):
                self._emit_const(instr)
            elif isinstance(instr, IRSub):
                self._emit_sub(instr)
            elif isinstance(instr, IRMul):
                self._emit_mul(instr)
            elif isinstance(instr, IRIsZero):
                self._emit_is_zero(instr)
            elif isinstance(instr, IRNot):
                self._emit_not(instr)
            elif isinstance(instr, IRMembership):
                self._emit_membership(instr)
            elif isinstance(instr, IRAssert):
                self._emit_assert(instr)

        return self.constraints

    def _get_idx(self, name: str) -> int:
        """Get witness index for variable."""
        idx = self.symbols.get_witness_index(name)
        if idx < 0:
            idx = self.symbols.allocate_witness(name)
        return idx

    def _emit_const(self, instr: IRConst):
        """Emit constraint: result = value (const * 1 = result)."""
        result_idx = self._get_idx(instr.result)
        # value * 1 = result -> A={value at w0}, B={1 at w0}, C={1 at result}
        self.constraints.append(R1CSConstraint(
            A={0: instr.value},
            B={0: 1},
            C={result_idx: 1},
            label=f"{instr.result} = {instr.value}"
        ))

    def _emit_sub(self, instr: IRSub):
        """Emit constraint: result = left - right."""
        result_idx = self._get_idx(instr.result)
        left_idx = self._get_idx(instr.left)

        if isinstance(instr.right, int):
            # result = left - const -> (left - const) * 1 = result
            self.constraints.append(R1CSConstraint(
                A={left_idx: 1, 0: -instr.right},
                B={0: 1},
                C={result_idx: 1},
                label=f"{instr.result} = {instr.left} - {instr.right}"
            ))
        else:
            right_idx = self._get_idx(instr.right)
            # result = left - right -> (left - right) * 1 = result
            self.constraints.append(R1CSConstraint(
                A={left_idx: 1, right_idx: -1},
                B={0: 1},
                C={result_idx: 1},
                label=f"{instr.result} = {instr.left} - {instr.right}"
            ))

    def _emit_mul(self, instr: IRMul):
        """Emit constraint: result = left * right."""
        result_idx = self._get_idx(instr.result)
        left_idx = self._get_idx(instr.left)
        right_idx = self._get_idx(instr.right)

        self.constraints.append(R1CSConstraint(
            A={left_idx: 1},
            B={right_idx: 1},
            C={result_idx: 1},
            label=f"{instr.result} = {instr.left} * {instr.right}"
        ))

    def _emit_is_zero(self, instr: IRIsZero):
        """
        Emit isZero gadget constraints.

        isZero(z) produces:
        - eq: 1 if z=0, 0 otherwise
        - inv: z^-1 if z!=0, arbitrary otherwise

        Constraints:
        1. z * inv = 1 - eq
        2. eq * z = 0
        3. eq * (eq - 1) = 0 (boolean)
        """
        z_idx = self._get_idx(instr.input)
        eq_idx = self._get_idx(instr.eq_var)
        inv_idx = self._get_idx(instr.inv_var)

        # Constraint 1: z * inv = 1 - eq
        self.constraints.append(R1CSConstraint(
            A={z_idx: 1},
            B={inv_idx: 1},
            C={0: 1, eq_idx: -1},
            label=f"{instr.input} * {instr.inv_var} = 1 - {instr.eq_var}"
        ))

        # Constraint 2: eq * z = 0
        self.constraints.append(R1CSConstraint(
            A={eq_idx: 1},
            B={z_idx: 1},
            C={},
            label=f"{instr.eq_var} * {instr.input} = 0"
        ))

        # Constraint 3: eq * (eq - 1) = 0 (boolean constraint)
        self.constraints.append(R1CSConstraint(
            A={eq_idx: 1},
            B={eq_idx: 1, 0: -1},
            C={},
            label=f"{instr.eq_var} * ({instr.eq_var} - 1) = 0"
        ))

    def _emit_not(self, instr: IRNot):
        """Emit NOT constraint: result = 1 - input."""
        result_idx = self._get_idx(instr.result)
        input_idx = self._get_idx(instr.input)

        # (1 - input) * 1 = result
        self.constraints.append(R1CSConstraint(
            A={0: 1, input_idx: -1},
            B={0: 1},
            C={result_idx: 1},
            label=f"{instr.result} = 1 - {instr.input}"
        ))

    def _emit_membership(self, instr: IRMembership):
        """
        Emit membership gadget constraints.

        For set membership, we use a disjunction over elements:
        isMember(x, S) = OR_{s in S}(x == s)

        This expands to individual equality checks combined with OR.
        For efficiency in production, would use Merkle tree proofs.
        """
        result_idx = self._get_idx(instr.result)
        element_idx = self._get_idx(instr.element)

        # Placeholder: membership witness variable
        # In full implementation, would expand to set-specific constraints
        self.constraints.append(R1CSConstraint(
            A={result_idx: 1},
            B={result_idx: 1, 0: -1},
            C={},
            label=f"isMember({instr.element}, {instr.set_name}) boolean"
        ))

    def _emit_assert(self, instr: IRAssert):
        """Emit assertion constraint: variable = value."""
        var_idx = self._get_idx(instr.variable)

        if instr.value == 0:
            # variable * 1 = 0
            self.constraints.append(R1CSConstraint(
                A={var_idx: 1},
                B={0: 1},
                C={},
                label=f"FINFR: {instr.variable} = 0"
            ))
        else:
            # variable * 1 = value
            self.constraints.append(R1CSConstraint(
                A={var_idx: 1},
                B={0: 1},
                C={0: instr.value},
                label=f"assert {instr.variable} = {instr.value}"
            ))


# ===============================================================================
# QAP - Quadratic Arithmetic Program
# ===============================================================================

@dataclass
class QAPPolynomial:
    """
    A polynomial in coefficient form.

    Coefficients are indexed from degree 0 (constant term) upward.
    """
    coefficients: List[FieldElement]

    def evaluate(self, x: FieldElement) -> FieldElement:
        """Evaluate polynomial at x using Horner's method."""
        if not self.coefficients:
            return FieldElement.zero(x.prime)

        result = self.coefficients[-1]
        for coeff in reversed(self.coefficients[:-1]):
            result = result * x + coeff

        return result

    def degree(self) -> int:
        """Return degree of polynomial."""
        return len(self.coefficients) - 1

    def to_list(self) -> List[int]:
        """Return coefficients as list of integers."""
        return [c.value for c in self.coefficients]


class QAPBuilder:
    """
    Builds QAP from R1CS.

    Converts R1CS constraints to polynomial form via Lagrange interpolation.

    QAP consists of polynomials A_j(x), B_j(x), C_j(x) for each witness variable j,
    such that the R1CS constraints are satisfied iff:
        A(x) * B(x) - C(x) = H(x) * T(x)

    where T(x) is the target polynomial vanishing on evaluation points.
    """

    def __init__(self, prime: int = BN254_PRIME):
        self.prime = prime
        self.A_polys: Dict[int, QAPPolynomial] = {}
        self.B_polys: Dict[int, QAPPolynomial] = {}
        self.C_polys: Dict[int, QAPPolynomial] = {}
        self.target_poly: Optional[QAPPolynomial] = None
        self.roots: List[int] = []
        self.num_constraints: int = 0
        self.num_witness: int = 0

    def build(self, constraints: List[R1CSConstraint], num_witness: int) -> 'QAPBuilder':
        """Build QAP from R1CS constraints."""
        self.num_constraints = len(constraints)
        self.num_witness = num_witness

        if self.num_constraints == 0:
            return self

        # Choose evaluation points: r_i = i for i in 1..m
        self.roots = list(range(1, self.num_constraints + 1))

        # Build target polynomial T(x) = prod_{i=1..m}(x - r_i)
        self.target_poly = self._build_target_polynomial()

        # For each witness variable, build A_j, B_j, C_j polynomials
        for j in range(num_witness):
            # Extract coefficient of w_j in each constraint's A vector
            a_values = [
                constraints[i].A.get(j, 0) for i in range(self.num_constraints)
            ]
            b_values = [
                constraints[i].B.get(j, 0) for i in range(self.num_constraints)
            ]
            c_values = [
                constraints[i].C.get(j, 0) for i in range(self.num_constraints)
            ]

            # Interpolate polynomials passing through (r_i, value_i)
            self.A_polys[j] = self._lagrange_interpolate(self.roots, a_values)
            self.B_polys[j] = self._lagrange_interpolate(self.roots, b_values)
            self.C_polys[j] = self._lagrange_interpolate(self.roots, c_values)

        return self

    def _build_target_polynomial(self) -> QAPPolynomial:
        """Build target polynomial T(x) = prod(x - r_i)."""
        # Start with T(x) = 1
        coeffs = [F(1, self.prime)]

        for root in self.roots:
            # Multiply by (x - root)
            new_coeffs = [F(0, self.prime)] * (len(coeffs) + 1)

            for i, c in enumerate(coeffs):
                # c * x term
                new_coeffs[i + 1] = new_coeffs[i + 1] + c
                # c * (-root) term
                new_coeffs[i] = new_coeffs[i] - c * F(root, self.prime)

            coeffs = new_coeffs

        return QAPPolynomial(coefficients=coeffs)

    def _lagrange_interpolate(self, points: List[int], values: List[int]) -> QAPPolynomial:
        """
        Lagrange interpolation to find polynomial passing through given points.

        L_i(x) = prod_{j!=i}((x - x_j) / (x_i - x_j))
        P(x) = sum_i(y_i * L_i(x))
        """
        n = len(points)

        if n == 0:
            return QAPPolynomial(coefficients=[F(0, self.prime)])

        # Build each Lagrange basis polynomial
        result_coeffs = [F(0, self.prime)] * n

        for i in range(n):
            if values[i] == 0:
                continue

            # Build L_i(x)
            basis = self._build_lagrange_basis(points, i)

            # Multiply by y_i and add to result
            for j, coeff in enumerate(basis.coefficients):
                if j < len(result_coeffs):
                    result_coeffs[j] = result_coeffs[j] + coeff * F(values[i], self.prime)

        return QAPPolynomial(coefficients=result_coeffs)

    def _build_lagrange_basis(self, points: List[int], i: int) -> QAPPolynomial:
        """Build i-th Lagrange basis polynomial L_i(x)."""
        n = len(points)
        x_i = points[i]

        # L_i(x) = prod_{j!=i}((x - x_j) / (x_i - x_j))
        # Start with 1
        coeffs = [F(1, self.prime)]

        denominator = F(1, self.prime)

        for j in range(n):
            if j == i:
                continue

            x_j = points[j]

            # Multiply by (x - x_j)
            new_coeffs = [F(0, self.prime)] * (len(coeffs) + 1)
            for k, c in enumerate(coeffs):
                new_coeffs[k + 1] = new_coeffs[k + 1] + c  # c * x
                new_coeffs[k] = new_coeffs[k] - c * F(x_j, self.prime)  # c * (-x_j)
            coeffs = new_coeffs

            # Accumulate denominator
            denominator = denominator * (F(x_i, self.prime) - F(x_j, self.prime))

        # Divide by denominator
        inv_denom = denominator.inverse()
        coeffs = [c * inv_denom for c in coeffs]

        return QAPPolynomial(coefficients=coeffs)

    def to_dict(self) -> Dict[str, Any]:
        """Export QAP as dictionary."""
        return {
            "field": f"F_p where p = {self.prime}",
            "num_constraints": self.num_constraints,
            "num_witness": self.num_witness,
            "roots": self.roots,
            "target_poly": self.target_poly.to_list() if self.target_poly else [],
            "A_polys": {k: v.to_list() for k, v in self.A_polys.items()},
            "B_polys": {k: v.to_list() for k, v in self.B_polys.items()},
            "C_polys": {k: v.to_list() for k, v in self.C_polys.items()}
        }


# ===============================================================================
# QAP COMPILER - Main Entry Point
# ===============================================================================

@dataclass
class CompilationResult:
    """Result of compiling tinyTalk to QAP."""
    success: bool
    tokens: List[Token]
    ast: Optional[Program]
    symbols: Optional[SymbolTable]
    ir: List[IRInstruction]
    r1cs: List[R1CSConstraint]
    qap: Optional[QAPBuilder]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "tokens": [{"type": t.type.name, "value": t.value, "line": t.line, "col": t.column} for t in self.tokens],
            "ast": self._ast_to_dict(self.ast) if self.ast else None,
            "symbols": self.symbols.to_dict() if self.symbols else None,
            "ir": [self._ir_to_dict(i) for i in self.ir],
            "r1cs": [c.to_dict() for c in self.r1cs],
            "qap": self.qap.to_dict() if self.qap else None,
            "errors": self.errors
        }

    def _ast_to_dict(self, node: ASTNode) -> Dict[str, Any]:
        """Convert AST node to dictionary."""
        if isinstance(node, Program):
            return {"type": "Program", "rules": [self._ast_to_dict(r) for r in node.rules]}
        elif isinstance(node, Rule):
            return {"type": "Rule", "guard": self._ast_to_dict(node.guard), "action": node.action}
        elif isinstance(node, BinaryOp):
            return {"type": "BinaryOp", "op": node.op, "left": self._ast_to_dict(node.left), "right": self._ast_to_dict(node.right)}
        elif isinstance(node, UnaryOp):
            return {"type": "UnaryOp", "op": node.op, "operand": self._ast_to_dict(node.operand)}
        elif isinstance(node, Comparison):
            return {"type": "Comparison", "op": node.op, "left": self._ast_to_dict(node.left), "right": self._ast_to_dict(node.right)}
        elif isinstance(node, InExpr):
            return {"type": "InExpr", "element": self._ast_to_dict(node.element), "set_name": node.set_name}
        elif isinstance(node, Identifier):
            return {"type": "Identifier", "name": node.name}
        elif isinstance(node, Literal):
            return {"type": "Literal", "value": node.value}
        return {"type": type(node).__name__}

    def _ir_to_dict(self, instr: IRInstruction) -> Dict[str, Any]:
        """Convert IR instruction to dictionary."""
        d = {"type": type(instr).__name__, "result": instr.result}
        if isinstance(instr, IRConst):
            d["value"] = instr.value
        elif isinstance(instr, IRSub):
            d["left"] = instr.left
            d["right"] = instr.right
        elif isinstance(instr, IRMul):
            d["left"] = instr.left
            d["right"] = instr.right
        elif isinstance(instr, IRIsZero):
            d["input"] = instr.input
            d["eq_var"] = instr.eq_var
            d["inv_var"] = instr.inv_var
        elif isinstance(instr, IRNot):
            d["input"] = instr.input
        elif isinstance(instr, IRMembership):
            d["element"] = instr.element
            d["set_name"] = instr.set_name
        elif isinstance(instr, IRAssert):
            d["variable"] = instr.variable
            d["value"] = instr.value
        return d


class QAPCompiler:
    """
    Main compiler that transforms tinyTalk to QAP.

    Pipeline:
        tinyTalk source -> Lexer -> Parser -> IR Builder -> R1CS -> QAP

    Usage:
        compiler = QAPCompiler()
        result = compiler.compile(source)

        # Access compilation artifacts
        result.tokens      # Lexer output
        result.ast         # Abstract Syntax Tree
        result.symbols     # Symbol table (enums, sets, witnesses)
        result.ir          # SSA-like IR
        result.r1cs        # Rank-1 Constraint System
        result.qap         # Quadratic Arithmetic Program
    """

    def __init__(self, prime: int = BN254_PRIME, debug: bool = False):
        self.prime = prime
        self.debug = debug

    def compile(self, source: str) -> CompilationResult:
        """Compile tinyTalk source to QAP."""
        errors = []
        tokens = []
        ast = None
        symbols = None
        ir = []
        r1cs = []
        qap = None

        try:
            # Lexer phase
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            if self.debug:
                self._debug_print("TOKENS", tokens)

            # Parser phase
            parser = Parser(tokens)
            ast = parser.parse()

            if self.debug:
                self._debug_print("AST", ast)

            # Symbol binding phase
            symbols = SymbolTable()

            # IR generation phase
            ir_builder = IRBuilder(symbols)
            ir = ir_builder.build(ast)

            if self.debug:
                self._debug_print("IR", ir)
                self._debug_print("SYMBOLS", symbols.to_dict())

            # R1CS generation phase
            r1cs_builder = R1CSBuilder(symbols)
            r1cs = r1cs_builder.build(ir)

            if self.debug:
                self._debug_print("R1CS", r1cs)

            # QAP conversion phase
            qap = QAPBuilder(self.prime)
            qap.build(r1cs, symbols.next_witness_idx)

            if self.debug:
                self._debug_print("QAP", qap.to_dict())

            return CompilationResult(
                success=True,
                tokens=tokens,
                ast=ast,
                symbols=symbols,
                ir=ir,
                r1cs=r1cs,
                qap=qap,
                errors=errors
            )

        except Exception as e:
            errors.append(str(e))
            return CompilationResult(
                success=False,
                tokens=tokens,
                ast=ast,
                symbols=symbols,
                ir=ir,
                r1cs=r1cs,
                qap=qap,
                errors=errors
            )

    def _debug_print(self, phase: str, data: Any):
        """Print debug output for a compilation phase."""
        print(f"\n[QAP→{phase}]")
        print("-" * 60)
        if hasattr(data, '__iter__') and not isinstance(data, (str, dict)):
            for item in data:
                print(f"  {item}")
        else:
            print(f"  {data}")


def compile_to_qap(source: str, prime: int = BN254_PRIME, debug: bool = False) -> CompilationResult:
    """
    Convenience function to compile tinyTalk to QAP.

    Args:
        source: tinyTalk source code
        prime: Field prime (default: BN254)
        debug: Print debug output

    Returns:
        CompilationResult with all compilation artifacts
    """
    compiler = QAPCompiler(prime=prime, debug=debug)
    return compiler.compile(source)


# ===============================================================================
# PRETTY PRINTER - Human-readable output
# ===============================================================================

def format_compilation_output(result: CompilationResult) -> str:
    """Format compilation result as human-readable string."""
    lines = []

    lines.append("=" * 70)
    lines.append("NEWTON QAP COMPILER OUTPUT")
    lines.append("=" * 70)

    # Token stream
    lines.append("\n[1] LEXER OUTPUT (tokens)")
    lines.append("-" * 40)
    for i, token in enumerate(result.tokens):
        if token.type != TokenType.NEWLINE:
            lines.append(f"  [{i:2d}] {token}")

    # AST
    if result.ast:
        lines.append("\n[2] PARSER OUTPUT (AST)")
        lines.append("-" * 40)
        for i, rule in enumerate(result.ast.rules):
            lines.append(f"  Rule {i+1}:")
            lines.append(f"    Guard: {_format_expr(rule.guard)}")
            lines.append(f"    Action: {rule.action}")

    # Symbol table
    if result.symbols:
        lines.append("\n[3] SYMBOL TABLE")
        lines.append("-" * 40)

        if result.symbols.enums:
            lines.append("  Enums:")
            for name, enum in result.symbols.enums.items():
                lines.append(f"    {name}: {enum.values}")

        if result.symbols.sets:
            lines.append("  Sets:")
            for name, set_table in result.symbols.sets.items():
                lines.append(f"    {name}: {set_table.elements}")

        lines.append("  Witness Layout:")
        for name, idx in sorted(result.symbols.witness_vars.items(), key=lambda x: x[1]):
            lines.append(f"    w[{idx}] = {name}")

    # IR
    if result.ir:
        lines.append("\n[4] IR (SSA-like)")
        lines.append("-" * 40)
        for instr in result.ir:
            lines.append(f"  {_format_ir(instr)}")

    # R1CS
    if result.r1cs:
        lines.append(f"\n[5] R1CS CONSTRAINTS (m={len(result.r1cs)})")
        lines.append("-" * 40)
        for i, c in enumerate(result.r1cs):
            lines.append(f"  c{i+1}: {c.label}")
            lines.append(f"       A={c.A}, B={c.B}, C={c.C}")

    # QAP
    if result.qap:
        lines.append("\n[6] QAP")
        lines.append("-" * 40)
        lines.append(f"  Field: F_p (p = {result.qap.prime})")
        lines.append(f"  Constraints: {result.qap.num_constraints}")
        lines.append(f"  Witness vars: {result.qap.num_witness}")
        lines.append(f"  Roots: {result.qap.roots}")

        if result.qap.target_poly:
            lines.append(f"  T(x) = prod(x - r_i)")

        lines.append("  Polynomials:")
        for j in sorted(result.qap.A_polys.keys()):
            a_deg = result.qap.A_polys[j].degree() if result.qap.A_polys[j].coefficients else 0
            b_deg = result.qap.B_polys[j].degree() if result.qap.B_polys[j].coefficients else 0
            c_deg = result.qap.C_polys[j].degree() if result.qap.C_polys[j].coefficients else 0
            lines.append(f"    w[{j}]: A deg={a_deg}, B deg={b_deg}, C deg={c_deg}")

    # Errors
    if result.errors:
        lines.append("\n[ERRORS]")
        lines.append("-" * 40)
        for err in result.errors:
            lines.append(f"  {err}")

    lines.append("\n" + "=" * 70)
    status = "SUCCESS" if result.success else "FAILED"
    lines.append(f"Compilation {status}")
    lines.append("=" * 70)

    return "\n".join(lines)


def _format_expr(expr: Expression) -> str:
    """Format expression as string."""
    if isinstance(expr, Literal):
        return repr(expr.value)
    elif isinstance(expr, Identifier):
        return expr.name
    elif isinstance(expr, Comparison):
        return f"({_format_expr(expr.left)} {expr.op} {_format_expr(expr.right)})"
    elif isinstance(expr, BinaryOp):
        return f"({_format_expr(expr.left)} {expr.op} {_format_expr(expr.right)})"
    elif isinstance(expr, UnaryOp):
        return f"({expr.op} {_format_expr(expr.operand)})"
    elif isinstance(expr, InExpr):
        return f"({_format_expr(expr.element)} in {expr.set_name})"
    return str(expr)


def _format_ir(instr: IRInstruction) -> str:
    """Format IR instruction as string."""
    if isinstance(instr, IRConst):
        return f"{instr.result} = {instr.value}"
    elif isinstance(instr, IRSub):
        return f"{instr.result} = {instr.left} - {instr.right}"
    elif isinstance(instr, IRMul):
        return f"{instr.result} = {instr.left} * {instr.right}"
    elif isinstance(instr, IRIsZero):
        return f"({instr.eq_var}, {instr.inv_var}) = isZero({instr.input})"
    elif isinstance(instr, IRNot):
        return f"{instr.result} = NOT {instr.input}"
    elif isinstance(instr, IRMembership):
        return f"{instr.result} = isMember({instr.element}, {instr.set_name})"
    elif isinstance(instr, IRAssert):
        return f"ASSERT {instr.variable} == {instr.value}"
    return str(instr)


# ===============================================================================
# CLI / DEMO
# ===============================================================================

if __name__ == "__main__":
    # Demo: Compile the example from the specification
    source = '''
when user_intent == "homework_help" and
     topic in approved_curriculum and
     response_tone == "educational" and
     no_direct_answers == true
fin generate_educational_response

when user_intent == "request_direct_answer" and
     context == "assessment"
finfr
'''

    print("Newton QAP Compiler - tinyTalk to Quadratic Arithmetic Program")
    print("=" * 70)
    print("\nInput Source:")
    print("-" * 40)
    print(source)

    # Compile with test prime for readable output
    result = compile_to_qap(source, prime=TEST_PRIME)

    # Print formatted output
    print(format_compilation_output(result))
