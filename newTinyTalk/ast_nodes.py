"""
TinyTalk AST Node Definitions
All AST node types used by the parser and runtime.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Any


class NodeType(Enum):
    PROGRAM = auto()
    # TinyTalk constructs
    BLUEPRINT = auto()
    FIELD_DECL = auto()
    # Statements
    LET_STMT = auto()
    CONST_STMT = auto()
    EXPR_STMT = auto()
    BLOCK_STMT = auto()
    IF_STMT = auto()
    FOR_STMT = auto()
    WHILE_STMT = auto()
    RETURN_STMT = auto()
    BREAK_STMT = auto()
    CONTINUE_STMT = auto()
    FN_DECL = auto()
    STRUCT_DECL = auto()
    ENUM_DECL = auto()
    IMPORT_STMT = auto()
    MATCH_STMT = auto()
    TRY_STMT = auto()
    THROW_STMT = auto()
    ASSIGN = auto()
    # Expressions
    LITERAL = auto()
    IDENTIFIER = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    CALL = auto()
    INDEX = auto()
    MEMBER = auto()
    ARRAY = auto()
    MAP_LITERAL = auto()
    LAMBDA = auto()
    CONDITIONAL = auto()
    PIPE = auto()
    RANGE = auto()
    STEP_CHAIN = auto()
    STRING_INTERP = auto()


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    type: NodeType = None
    line: int = 0
    column: int = 0


# ---------------------------------------------------------------------------
# Program
# ---------------------------------------------------------------------------

@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.PROGRAM


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class Literal(ASTNode):
    value: Any = None

    def __post_init__(self):
        self.type = NodeType.LITERAL


@dataclass
class Identifier(ASTNode):
    name: str = ""

    def __post_init__(self):
        self.type = NodeType.IDENTIFIER


@dataclass
class BinaryOp(ASTNode):
    op: str = ""
    left: ASTNode = None
    right: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.BINARY_OP


@dataclass
class UnaryOp(ASTNode):
    op: str = ""
    operand: ASTNode = None
    prefix: bool = True

    def __post_init__(self):
        self.type = NodeType.UNARY_OP


@dataclass
class Call(ASTNode):
    callee: ASTNode = None
    args: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.CALL


@dataclass
class Index(ASTNode):
    obj: ASTNode = None
    index: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.INDEX


@dataclass
class Member(ASTNode):
    obj: ASTNode = None
    field_name: str = ""

    def __post_init__(self):
        self.type = NodeType.MEMBER


@dataclass
class Array(ASTNode):
    elements: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.ARRAY


@dataclass
class MapLiteral(ASTNode):
    pairs: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.MAP_LITERAL


@dataclass
class Lambda(ASTNode):
    params: List[str] = field(default_factory=list)
    body: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.LAMBDA


@dataclass
class Conditional(ASTNode):
    condition: ASTNode = None
    then_expr: ASTNode = None
    else_expr: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.CONDITIONAL


@dataclass
class Range(ASTNode):
    start: ASTNode = None
    end: ASTNode = None
    inclusive: bool = False

    def __post_init__(self):
        self.type = NodeType.RANGE


@dataclass
class Pipe(ASTNode):
    left: ASTNode = None
    right: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.PIPE


@dataclass
class StepChain(ASTNode):
    """data _filter(pred) _sort _take(3)"""
    source: ASTNode = None
    steps: List[tuple] = field(default_factory=list)  # [(step_name, args)]

    def __post_init__(self):
        self.type = NodeType.STEP_CHAIN


@dataclass
class StringInterp(ASTNode):
    """String interpolation: "Hello {name}, you are {age} years old" """
    parts: List[Any] = field(default_factory=list)  # [str | ASTNode, ...]

    def __post_init__(self):
        self.type = NodeType.STRING_INTERP


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class LetStmt(ASTNode):
    name: str = ""
    type_hint: Optional[str] = None
    value: Optional[ASTNode] = None
    mutable: bool = True

    def __post_init__(self):
        self.type = NodeType.LET_STMT


@dataclass
class ConstStmt(ASTNode):
    name: str = ""
    value: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.CONST_STMT


@dataclass
class AssignStmt(ASTNode):
    target: ASTNode = None
    value: ASTNode = None
    op: str = "="

    def __post_init__(self):
        self.type = NodeType.ASSIGN


@dataclass
class Block(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.BLOCK_STMT


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode = None
    then_branch: ASTNode = None
    elif_branches: List[tuple] = field(default_factory=list)
    else_branch: Optional[ASTNode] = None

    def __post_init__(self):
        self.type = NodeType.IF_STMT


@dataclass
class ForStmt(ASTNode):
    var: str = ""
    iterable: ASTNode = None
    body: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.FOR_STMT


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode = None
    body: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.WHILE_STMT


@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode] = None

    def __post_init__(self):
        self.type = NodeType.RETURN_STMT


@dataclass
class BreakStmt(ASTNode):
    def __post_init__(self):
        self.type = NodeType.BREAK_STMT


@dataclass
class ContinueStmt(ASTNode):
    def __post_init__(self):
        self.type = NodeType.CONTINUE_STMT


@dataclass
class FnDecl(ASTNode):
    name: str = ""
    params: List[tuple] = field(default_factory=list)  # [(name, type_hint)]
    return_type: Optional[str] = None
    body: ASTNode = None
    is_pub: bool = False

    def __post_init__(self):
        self.type = NodeType.FN_DECL


@dataclass
class StructDecl(ASTNode):
    """Used for both struct {} and blueprint ... end"""
    name: str = ""
    fields: List[tuple] = field(default_factory=list)  # [(name, type, default)]
    methods: List[tuple] = field(default_factory=list)  # [(kind, FnDecl)]

    def __post_init__(self):
        self.type = NodeType.STRUCT_DECL


@dataclass
class EnumDecl(ASTNode):
    name: str = ""
    variants: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.ENUM_DECL


@dataclass
class ImportStmt(ASTNode):
    module: str = ""
    items: List[str] = field(default_factory=list)
    alias: Optional[str] = None

    def __post_init__(self):
        self.type = NodeType.IMPORT_STMT


@dataclass
class MatchStmt(ASTNode):
    value: ASTNode = None
    cases: List[tuple] = field(default_factory=list)  # [(pattern, body)]

    def __post_init__(self):
        self.type = NodeType.MATCH_STMT


@dataclass
class TryStmt(ASTNode):
    body: ASTNode = None
    catch_var: Optional[str] = None
    catch_body: Optional[ASTNode] = None

    def __post_init__(self):
        self.type = NodeType.TRY_STMT


@dataclass
class ThrowStmt(ASTNode):
    value: ASTNode = None

    def __post_init__(self):
        self.type = NodeType.THROW_STMT
