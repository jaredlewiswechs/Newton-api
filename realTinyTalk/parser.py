"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK PARSER
Recursive descent parser producing AST

The Sovereign Stack Language Parser
Grammar → Tokens → AST
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Any, Dict, Union
from .lexer import Token, TokenType


# ═══════════════════════════════════════════════════════════════════════════════
# AST NODE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class NodeType(Enum):
    """AST node types."""
    # Program
    PROGRAM = auto()
    
    # ═══════════════════════════════════════════════════════════════
    # TINYTALK SOVEREIGN CONSTRUCTS
    # ═══════════════════════════════════════════════════════════════
    BLUEPRINT = auto()      # Type/class definition
    LAW = auto()            # Constraint (Layer 0: Governance)
    FORGE = auto()          # Action method (Layer 1: Executive)
    FIELD_DECL = auto()     # State declaration
    WHEN_EXPR = auto()      # Fact declaration
    FIN_STMT = auto()       # Closure
    FINFR_STMT = auto()     # Finality (ontological death)
    REPLY_STMT = auto()     # Return from forge
    RATIO_EXPR = auto()     # Dimensional analysis
    
    # Standard Statements
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
    IMPL_DECL = auto()
    IMPORT_STMT = auto()
    EXPORT_STMT = auto()
    MATCH_STMT = auto()
    TRY_STMT = auto()
    THROW_STMT = auto()
    
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
    ASSIGN = auto()
    COMPOUND_ASSIGN = auto()
    STEP_CHAIN = auto()     # dplyr-style step chain: data _filter _sort _take


@dataclass
class ASTNode:
    """Base AST node."""
    type: NodeType = None  # Will be set by subclass __post_init__
    line: int = 0
    column: int = 0
    
    # Node-specific data stored as attributes
    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if k not in ('type', 'line', 'column')}
        if attrs:
            return f"{self.type.name}({attrs})"
        return f"{self.type.name}"


@dataclass
class Program(ASTNode):
    """Root program node."""
    statements: List[ASTNode] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.PROGRAM


@dataclass
class Literal(ASTNode):
    """Literal value (number, string, bool, null)."""
    value: Any = None
    
    def __post_init__(self):
        self.type = NodeType.LITERAL


@dataclass
class Identifier(ASTNode):
    """Variable or function name."""
    name: str = ""
    
    def __post_init__(self):
        self.type = NodeType.IDENTIFIER


@dataclass
class BinaryOp(ASTNode):
    """Binary operation."""
    op: str = ""
    left: ASTNode = None
    right: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.BINARY_OP


@dataclass
class UnaryOp(ASTNode):
    """Unary operation."""
    op: str = ""
    operand: ASTNode = None
    prefix: bool = True
    
    def __post_init__(self):
        self.type = NodeType.UNARY_OP


@dataclass
class Call(ASTNode):
    """Function call."""
    callee: ASTNode = None
    args: List[ASTNode] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.CALL


@dataclass
class Index(ASTNode):
    """Array/map index access."""
    obj: ASTNode = None
    index: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.INDEX


@dataclass 
class Member(ASTNode):
    """Member access (obj.field)."""
    obj: ASTNode = None
    field: str = ""
    
    def __post_init__(self):
        self.type = NodeType.MEMBER


@dataclass
class Array(ASTNode):
    """Array literal."""
    elements: List[ASTNode] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.ARRAY


@dataclass
class MapLiteral(ASTNode):
    """Map/dict literal."""
    pairs: List[tuple] = field(default_factory=list)  # [(key, value), ...]
    
    def __post_init__(self):
        self.type = NodeType.MAP_LITERAL


@dataclass
class Lambda(ASTNode):
    """Lambda/anonymous function."""
    params: List[str] = field(default_factory=list)
    body: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.LAMBDA


@dataclass
class Conditional(ASTNode):
    """Ternary conditional (cond ? then : else)."""
    condition: ASTNode = None
    then_expr: ASTNode = None
    else_expr: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.CONDITIONAL


@dataclass
class Range(ASTNode):
    """Range expression (start..end or start..=end)."""
    start: ASTNode = None
    end: ASTNode = None
    inclusive: bool = False
    
    def __post_init__(self):
        self.type = NodeType.RANGE


@dataclass
class Pipe(ASTNode):
    """Pipe expression (x |> f)."""
    left: ASTNode = None
    right: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.PIPE


@dataclass
class StepChain(ASTNode):
    """
    Step chain expression (dplyr-style data manipulation).
    
    data _filter(x > 5) _sort _take(3)
    """
    source: ASTNode = None  # The data source
    steps: List[tuple] = field(default_factory=list)  # [(step_name, args), ...]
    dotted: bool = False
    
    def __post_init__(self):
        self.type = NodeType.STEP_CHAIN


@dataclass
class LetStmt(ASTNode):
    """Variable declaration."""
    name: str = ""
    type_hint: Optional[str] = None
    value: Optional[ASTNode] = None
    mutable: bool = True
    
    def __post_init__(self):
        self.type = NodeType.LET_STMT


@dataclass
class ConstStmt(ASTNode):
    """Constant declaration."""
    name: str = ""
    value: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.CONST_STMT


@dataclass
class AssignStmt(ASTNode):
    """Assignment."""
    target: ASTNode = None
    value: ASTNode = None
    op: str = "="  # =, +=, -=, etc.
    
    def __post_init__(self):
        self.type = NodeType.ASSIGN


@dataclass
class Block(ASTNode):
    """Block of statements."""
    statements: List[ASTNode] = field(default_factory=list)
    
    def __post_init__(self):
        self.type = NodeType.BLOCK_STMT


@dataclass
class IfStmt(ASTNode):
    """If statement."""
    condition: ASTNode = None
    then_branch: ASTNode = None
    elif_branches: List[tuple] = field(default_factory=list)  # [(cond, body), ...]
    else_branch: Optional[ASTNode] = None
    
    def __post_init__(self):
        self.type = NodeType.IF_STMT


@dataclass
class ForStmt(ASTNode):
    """For loop (bounded iteration)."""
    var: str = ""
    iterable: ASTNode = None
    body: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.FOR_STMT


@dataclass
class WhileStmt(ASTNode):
    """While loop (with implicit bound)."""
    condition: ASTNode = None
    body: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.WHILE_STMT


@dataclass
class ReturnStmt(ASTNode):
    """Return statement."""
    value: Optional[ASTNode] = None
    
    def __post_init__(self):
        self.type = NodeType.RETURN_STMT


@dataclass
class BreakStmt(ASTNode):
    """Break statement."""
    def __post_init__(self):
        self.type = NodeType.BREAK_STMT


@dataclass
class ContinueStmt(ASTNode):
    """Continue statement."""
    def __post_init__(self):
        self.type = NodeType.CONTINUE_STMT


@dataclass
class FnDecl(ASTNode):
    """Function declaration."""
    name: str = ""
    params: List[tuple] = field(default_factory=list)  # [(name, type_hint), ...]
    return_type: Optional[str] = None
    body: ASTNode = None
    is_async: bool = False
    is_pub: bool = False
    
    def __post_init__(self):
        self.type = NodeType.FN_DECL


@dataclass
class StructDecl(ASTNode):
    """Struct/Blueprint declaration."""
    name: str = ""
    fields: List[tuple] = field(default_factory=list)  # [(name, type, default), ...]
    methods: List[tuple] = field(default_factory=list)  # [('forge'/'law', FnDecl), ...]
    is_pub: bool = False
    
    def __post_init__(self):
        self.type = NodeType.STRUCT_DECL


@dataclass
class EnumDecl(ASTNode):
    """Enum declaration."""
    name: str = ""
    variants: List[tuple] = field(default_factory=list)  # [(name, value), ...]
    
    def __post_init__(self):
        self.type = NodeType.ENUM_DECL


@dataclass
class ImportStmt(ASTNode):
    """Import statement."""
    module: str = ""
    items: List[str] = field(default_factory=list)  # Empty = import all
    alias: Optional[str] = None
    
    def __post_init__(self):
        self.type = NodeType.IMPORT_STMT


@dataclass
class MatchStmt(ASTNode):
    """Match/pattern matching statement."""
    value: ASTNode = None
    cases: List[tuple] = field(default_factory=list)  # [(pattern, body), ...]
    
    def __post_init__(self):
        self.type = NodeType.MATCH_STMT


@dataclass
class TryStmt(ASTNode):
    """Try-catch statement."""
    body: ASTNode = None
    catch_var: Optional[str] = None
    catch_body: Optional[ASTNode] = None
    
    def __post_init__(self):
        self.type = NodeType.TRY_STMT


@dataclass
class ThrowStmt(ASTNode):
    """Throw statement."""
    value: ASTNode = None
    
    def __post_init__(self):
        self.type = NodeType.THROW_STMT


# ═══════════════════════════════════════════════════════════════════════════════
# PARSER
# ═══════════════════════════════════════════════════════════════════════════════

class Parser:
    """
    TinyTalk Parser - Recursive descent.
    
    Converts token stream to AST.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> Program:
        """Parse the entire program."""
        statements = []
        
        self._skip_newlines()
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()
        
        return Program(statements=statements)
    
    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    
    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
    
    def _peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[pos]
    
    def _advance(self) -> Token:
        if not self._at_end():
            self.pos += 1
        return self.tokens[self.pos - 1]
    
    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types
    
    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False
    
    def _consume(self, type: TokenType, message: str) -> Token:
        if self._check(type):
            return self._advance()
        raise SyntaxError(f"Line {self._peek().line}: {message}")
    
    def _skip_newlines(self):
        while self._match(TokenType.NEWLINE):
            pass
    
    def _expect_end(self):
        """Expect end of statement."""
        if not self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE, TokenType.SEMICOLON):
            raise SyntaxError(f"Line {self._peek().line}: Expected end of statement")
        self._match(TokenType.SEMICOLON)
        self._skip_newlines()
    
    # ─────────────────────────────────────────────────────────────────────────
    # STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        tok = self._peek()

        if self._match(TokenType.LET):
            return self._parse_let()
        if self._match(TokenType.CONST):
            return self._parse_const()
        if self._match(TokenType.FN):
            return self._parse_fn()
        if self._match(TokenType.IF):
            return self._parse_if()
        if self._match(TokenType.FOR):
            return self._parse_for()
        if self._match(TokenType.WHILE):
            return self._parse_while()
        if self._match(TokenType.RETURN):
            return self._parse_return()
        if self._match(TokenType.BREAK):
            return BreakStmt(line=tok.line, column=tok.column)
        if self._match(TokenType.CONTINUE):
            return ContinueStmt(line=tok.line, column=tok.column)
        if self._match(TokenType.IMPORT):
            return self._parse_import()
        if self._match(TokenType.MATCH):
            return self._parse_match()
        if self._match(TokenType.TRY):
            return self._parse_try()
        if self._match(TokenType.THROW):
            return self._parse_throw()

        # ═══════════════════════════════════════════════════════════════
        # TINYTALK SACRED KEYWORDS (from the Bible)
        # ═══════════════════════════════════════════════════════════════
        
        if self._match(TokenType.BLUEPRINT):
            return self._parse_blueprint()
        
        if self._match(TokenType.LAW):
            return self._parse_law()
        
        if self._match(TokenType.FORGE):
            return self._parse_forge()
        
        if self._match(TokenType.WHEN):
            return self._parse_when()
        
        if self._match(TokenType.FIN):
            return self._parse_fin()
        
        if self._match(TokenType.FINFR):
            return self._parse_finfr()
        
        if self._match(TokenType.REPLY):
            return self._parse_reply()
        
        if self._match(TokenType.DO):
            return self._parse_do()
        
        if self._match(TokenType.LBRACE):
            return self._parse_block()
        
        # Expression statement (including assignment)
        return self._parse_expression_statement()
    
    def _parse_let(self) -> LetStmt:
        """Parse let statement: let name [: type] = value"""
        tok = self.tokens[self.pos - 1]
        mutable = self._match(TokenType.MUT)
        
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_tok.value
        
        type_hint = None
        if self._match(TokenType.COLON):
            type_hint = self._parse_type_hint()
        
        value = None
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
        
        return LetStmt(name=name, type_hint=type_hint, value=value, mutable=mutable,
                       line=tok.line, column=tok.column)
    
    def _parse_const(self) -> ConstStmt:
        """Parse const statement: const name = value"""
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected constant name")
        self._consume(TokenType.ASSIGN, "Expected '=' after constant name")
        value = self._parse_expression()
        
        return ConstStmt(name=name_tok.value, value=value,
                         line=tok.line, column=tok.column)
    
    def _parse_fn(self) -> FnDecl:
        """Parse function: fn name(params) [-> type] { body }"""
        tok = self.tokens[self.pos - 1]
        
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name")
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        if not self._check(TokenType.RPAREN):
            params = self._parse_params()
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type_hint()
        
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self._parse_block()
        
        return FnDecl(name=name_tok.value, params=params, return_type=return_type,
                      body=body, line=tok.line, column=tok.column)
    
    def _parse_params(self) -> List[tuple]:
        """Parse function parameters."""
        params = []
        
        while True:
            name_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            type_hint = None
            if self._match(TokenType.COLON):
                type_hint = self._parse_type_hint()
            params.append((name_tok.value, type_hint))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params
    
    def _parse_type_hint(self) -> str:
        """Parse a type hint."""
        tok = self._advance()
        if tok.type == TokenType.IDENTIFIER:
            type_str = tok.value
        elif tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.STR, 
                          TokenType.BOOL, TokenType.LIST, TokenType.MAP,
                          TokenType.ANY, TokenType.VOID):
            type_str = tok.value
        else:
            raise SyntaxError(f"Line {tok.line}: Expected type")
        
        # Handle generics: list[int], map[str, int]
        if self._match(TokenType.LBRACKET):
            inner_types = [self._parse_type_hint()]
            while self._match(TokenType.COMMA):
                inner_types.append(self._parse_type_hint())
            self._consume(TokenType.RBRACKET, "Expected ']' after type parameters")
            type_str = f"{type_str}[{', '.join(inner_types)}]"
        
        # Handle optional: ?int
        if self._match(TokenType.QUESTION):
            type_str = f"?{type_str}"
        
        return type_str
    
    def _parse_if(self) -> IfStmt:
        """Parse if statement."""
        tok = self.tokens[self.pos - 1]
        
        condition = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after if condition")
        then_branch = self._parse_block()
        
        elif_branches = []
        else_branch = None
        
        self._skip_newlines()
        while self._match(TokenType.ELIF):
            elif_cond = self._parse_expression()
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{' after elif condition")
            elif_body = self._parse_block()
            elif_branches.append((elif_cond, elif_body))
            self._skip_newlines()
        
        if self._match(TokenType.ELSE):
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{' after else")
            else_branch = self._parse_block()
        
        return IfStmt(condition=condition, then_branch=then_branch,
                      elif_branches=elif_branches, else_branch=else_branch,
                      line=tok.line, column=tok.column)
    
    def _parse_for(self) -> ForStmt:
        """Parse for loop: for x in iterable { body }"""
        tok = self.tokens[self.pos - 1]
        
        var_tok = self._consume(TokenType.IDENTIFIER, "Expected loop variable")
        self._consume(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self._parse_expression()
        
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after for expression")
        body = self._parse_block()
        
        return ForStmt(var=var_tok.value, iterable=iterable, body=body,
                       line=tok.line, column=tok.column)
    
    def _parse_while(self) -> WhileStmt:
        """Parse while loop."""
        tok = self.tokens[self.pos - 1]
        
        condition = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after while condition")
        body = self._parse_block()
        
        return WhileStmt(condition=condition, body=body,
                         line=tok.line, column=tok.column)
    
    def _parse_return(self) -> ReturnStmt:
        """Parse return statement."""
        tok = self.tokens[self.pos - 1]
        
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self._parse_expression()
        
        return ReturnStmt(value=value, line=tok.line, column=tok.column)
    
    def _parse_block(self) -> Block:
        """Parse a block of statements."""
        tok = self.tokens[self.pos - 1]
        statements = []
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        
        return Block(statements=statements, line=tok.line, column=tok.column)
    
    def _parse_struct(self) -> StructDecl:
        """Parse struct declaration."""
        tok = self.tokens[self.pos - 1]
        
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected struct name")
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after struct name")
        
        fields = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            field_name = self._consume(TokenType.IDENTIFIER, "Expected field name")
            self._consume(TokenType.COLON, "Expected ':' after field name")
            field_type = self._parse_type_hint()
            
            default = None
            if self._match(TokenType.ASSIGN):
                default = self._parse_expression()
            
            fields.append((field_name.value, field_type, default))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}' after struct fields")
        
        return StructDecl(name=name_tok.value, fields=fields,
                          line=tok.line, column=tok.column)
    
    def _parse_enum(self) -> EnumDecl:
        """Parse enum declaration."""
        tok = self.tokens[self.pos - 1]
        
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected enum name")
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after enum name")
        
        variants = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            variant_name = self._consume(TokenType.IDENTIFIER, "Expected variant name")
            value = None
            if self._match(TokenType.ASSIGN):
                value = self._parse_expression()
            variants.append((variant_name.value, value))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}' after enum variants")
        
        return EnumDecl(name=name_tok.value, variants=variants,
                        line=tok.line, column=tok.column)
    
    def _parse_import(self) -> ImportStmt:
        """Parse import statement: import "module" or from "module" import x, y"""
        tok = self.tokens[self.pos - 1]
        
        module_tok = self._consume(TokenType.STRING, "Expected module path")
        
        items = []
        alias = None
        
        if self._match(TokenType.AS):
            alias_tok = self._consume(TokenType.IDENTIFIER, "Expected alias name")
            alias = alias_tok.value
        
        return ImportStmt(module=module_tok.value, items=items, alias=alias,
                          line=tok.line, column=tok.column)
    
    def _parse_match(self) -> MatchStmt:
        """Parse match statement."""
        tok = self.tokens[self.pos - 1]
        
        value = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after match value")
        
        cases = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            pattern = self._parse_expression()
            self._consume(TokenType.FAT_ARROW, "Expected '=>' after pattern")
            body = self._parse_expression()
            cases.append((pattern, body))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}' after match cases")
        
        return MatchStmt(value=value, cases=cases, line=tok.line, column=tok.column)
    
    def _parse_try(self) -> TryStmt:
        """Parse try-catch."""
        tok = self.tokens[self.pos - 1]
        
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after try")
        body = self._parse_block()
        
        catch_var = None
        catch_body = None
        
        self._skip_newlines()
        if self._match(TokenType.CATCH):
            if self._match(TokenType.LPAREN):
                catch_var_tok = self._consume(TokenType.IDENTIFIER, "Expected catch variable")
                catch_var = catch_var_tok.value
                self._consume(TokenType.RPAREN, "Expected ')' after catch variable")
            
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{' after catch")
            catch_body = self._parse_block()
        
        return TryStmt(body=body, catch_var=catch_var, catch_body=catch_body,
                       line=tok.line, column=tok.column)
    
    def _parse_throw(self) -> ThrowStmt:
        """Parse throw statement."""
        tok = self.tokens[self.pos - 1]
        value = self._parse_expression()
        return ThrowStmt(value=value, line=tok.line, column=tok.column)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TINYTALK SACRED PARSERS (from the Bible)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _parse_blueprint(self) -> StructDecl:
        """
        Parse blueprint (class) declaration.
        
        blueprint Counter
            field count = 0
            
            forge increment
                count = count + 1
                reply self
            end
            
            law getValue
                reply count
            end
        end
        """
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected blueprint name")
        self._skip_newlines()
        
        fields = []
        methods = []
        
        # Parse body until 'end'
        while not self._check(TokenType.END) and not self._at_end():
            self._skip_newlines()
            
            if self._match(TokenType.FIELD):
                # field name = value
                field_name = self._consume(TokenType.IDENTIFIER, "Expected field name")
                value = None
                if self._match(TokenType.ASSIGN):
                    value = self._parse_expression()
                fields.append((field_name.value, None, value))
            
            elif self._match(TokenType.FORGE):
                # forge methodName ... end
                method = self._parse_forge_body()
                methods.append(('forge', method))
            
            elif self._match(TokenType.LAW):
                # law methodName ... end
                method = self._parse_law_body()
                methods.append(('law', method))
            
            self._skip_newlines()
        
        self._consume(TokenType.END, "Expected 'end' after blueprint")
        
        # Convert to StructDecl with methods attached
        return StructDecl(name=name_tok.value, fields=fields, methods=methods,
                          line=tok.line, column=tok.column)
    
    def _parse_forge(self) -> FnDecl:
        """Parse standalone forge (mutable action)."""
        return self._parse_forge_body()
    
    def _parse_forge_body(self) -> FnDecl:
        """Parse forge method body."""
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected forge name")
        
        # Optional parameters
        params = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                params = self._parse_params()
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        self._skip_newlines()
        
        # Parse body until 'end'
        statements = []
        while not self._check(TokenType.END) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()
        
        self._consume(TokenType.END, "Expected 'end' after forge")
        
        body = Block(statements=statements, line=tok.line, column=tok.column)
        return FnDecl(name=name_tok.value, params=params, body=body,
                      line=tok.line, column=tok.column)
    
    def _parse_law(self) -> FnDecl:
        """Parse standalone law (constraint/pure function)."""
        return self._parse_law_body()
    
    def _parse_law_body(self) -> FnDecl:
        """Parse law method body (no mutation allowed conceptually)."""
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected law name")
        
        # Optional parameters
        params = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                params = self._parse_params()
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        self._skip_newlines()
        
        # Parse body until 'end'
        statements = []
        while not self._check(TokenType.END) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()
        
        self._consume(TokenType.END, "Expected 'end' after law")
        
        body = Block(statements=statements, line=tok.line, column=tok.column)
        return FnDecl(name=name_tok.value, params=params, body=body,
                      line=tok.line, column=tok.column)
    
    def _parse_when(self):
        """
        Parse when - either a fact (constant) or a function definition.
        
        when x = 42           -> constant (immutable fact)
        when name = "Newton"  -> constant
        
        when square(x)        -> function definition
          do x * x
        finfr
        """
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected name after 'when'")
        
        # Check if this is a function definition (has parentheses)
        if self._match(TokenType.LPAREN):
            # Function definition: when square(x) ... finfr
            params = []
            if not self._check(TokenType.RPAREN):
                params = self._parse_params()
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
            
            self._skip_newlines()
            
            # Parse body until 'finfr' or 'end'
            statements = []
            while not self._check(TokenType.FINFR, TokenType.END) and not self._at_end():
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
                self._skip_newlines()
            
            # Accept either 'finfr' or 'end' as terminator
            if not self._match(TokenType.FINFR):
                self._consume(TokenType.END, "Expected 'finfr' or 'end' after when function")
            
            body = Block(statements=statements, line=tok.line, column=tok.column)
            return FnDecl(name=name_tok.value, params=params, body=body,
                          line=tok.line, column=tok.column)
        else:
            # Constant declaration: when x = 42
            self._consume(TokenType.ASSIGN, "Expected '=' after fact name")
            value = self._parse_expression()
            
            return ConstStmt(name=name_tok.value, value=value,
                             line=tok.line, column=tok.column)
    
    def _parse_fin(self) -> ReturnStmt:
        """
        Parse fin (closure - can reopen).
        
        fin result  -> marks end of scope, returns result
        """
        tok = self.tokens[self.pos - 1]
        
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.END, TokenType.EOF):
            value = self._parse_expression()
        
        return ReturnStmt(value=value, line=tok.line, column=tok.column)
    
    def _parse_finfr(self) -> ReturnStmt:
        """
        Parse finfr (finality - ontological death, cannot reopen).
        
        finfr result  -> final return, scope destroyed
        """
        tok = self.tokens[self.pos - 1]
        
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.END, TokenType.EOF):
            value = self._parse_expression()
        
        # For now, finfr is the same as fin/return
        # In a full implementation, it would mark the scope as terminated
        return ReturnStmt(value=value, line=tok.line, column=tok.column)
    
    def _parse_do(self) -> ReturnStmt:
        """
        Parse do (action/return in when functions).
        
        do x * x     -> returns x * x
        do result    -> returns result
        """
        tok = self.tokens[self.pos - 1]
        
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.END, TokenType.EOF, TokenType.FINFR, TokenType.FIN_THEN):
            value = self._parse_expression()
        
        return ReturnStmt(value=value, line=tok.line, column=tok.column)
    
    def _parse_reply(self) -> ReturnStmt:
        """
        Parse reply (return from forge/law).
        
        reply self    -> return self
        reply value   -> return value
        """
        tok = self.tokens[self.pos - 1]
        
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.END, TokenType.EOF):
            value = self._parse_expression()
        
        return ReturnStmt(value=value, line=tok.line, column=tok.column)

    def _parse_expression_statement(self) -> ASTNode:
        """Parse expression or assignment statement."""
        expr = self._parse_expression()
        
        # Check for assignment
        if self._match(TokenType.ASSIGN, TokenType.PLUS_EQ, TokenType.MINUS_EQ,
                       TokenType.STAR_EQ, TokenType.SLASH_EQ, TokenType.PERCENT_EQ):
            op = self.tokens[self.pos - 1].value
            value = self._parse_expression()
            return AssignStmt(target=expr, value=value, op=op,
                              line=expr.line, column=expr.column)
        
        return expr
    
    # ─────────────────────────────────────────────────────────────────────────
    # EXPRESSIONS (Precedence climbing)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _parse_expression(self) -> ASTNode:
        """Parse an expression."""
        return self._parse_pipe()
    
    def _parse_pipe(self) -> ASTNode:
        """Parse pipe expression: x |> f"""
        left = self._parse_ternary()
        
        while self._match(TokenType.PIPE):
            tok = self.tokens[self.pos - 1]
            right = self._parse_ternary()
            left = Pipe(left=left, right=right, line=tok.line, column=tok.column)
        
        return left
    
    def _parse_ternary(self) -> ASTNode:
        """Parse ternary: cond ? then : else"""
        cond = self._parse_or()
        
        if self._match(TokenType.QUESTION):
            tok = self.tokens[self.pos - 1]
            then_expr = self._parse_expression()
            self._consume(TokenType.COLON, "Expected ':' in ternary expression")
            else_expr = self._parse_expression()
            return Conditional(condition=cond, then_expr=then_expr, else_expr=else_expr,
                               line=tok.line, column=tok.column)
        
        return cond
    
    def _parse_or(self) -> ASTNode:
        """Parse or expression."""
        left = self._parse_and()
        
        while self._match(TokenType.OR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_and()
            left = BinaryOp(op='or', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_and(self) -> ASTNode:
        """Parse and expression."""
        left = self._parse_equality()
        
        while self._match(TokenType.AND):
            tok = self.tokens[self.pos - 1]
            right = self._parse_equality()
            left = BinaryOp(op='and', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_equality(self) -> ASTNode:
        """Parse equality: ==, !=, is, isnt, has, hasnt, isin, islike"""
        left = self._parse_comparison()
        
        while self._match(TokenType.EQ, TokenType.NE, 
                          TokenType.IS, TokenType.ISNT,
                          TokenType.HAS, TokenType.HASNT,
                          TokenType.ISIN, TokenType.ISLIKE):
            tok = self.tokens[self.pos - 1]
            op_map = {
                TokenType.EQ: '==', TokenType.NE: '!=',
                TokenType.IS: 'is', TokenType.ISNT: 'isnt',
                TokenType.HAS: 'has', TokenType.HASNT: 'hasnt',
                TokenType.ISIN: 'isin', TokenType.ISLIKE: 'islike',
            }
            right = self._parse_comparison()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison: <, >, <=, >="""
        left = self._parse_range()
        
        while self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.LT: '<', TokenType.GT: '>', 
                      TokenType.LE: '<=', TokenType.GE: '>='}
            right = self._parse_range()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_range(self) -> ASTNode:
        """Parse range: start..end or start..=end"""
        left = self._parse_bitwise_or()
        
        if self._match(TokenType.RANGE_INCL):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_or()
            return Range(start=left, end=right, inclusive=True,
                         line=tok.line, column=tok.column)
        
        if self._match(TokenType.RANGE):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_or()
            return Range(start=left, end=right, inclusive=False,
                         line=tok.line, column=tok.column)
        
        return left
    
    def _parse_bitwise_or(self) -> ASTNode:
        """Parse bitwise or: |"""
        left = self._parse_bitwise_xor()
        
        while self._match(TokenType.BIT_OR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_xor()
            left = BinaryOp(op='|', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_bitwise_xor(self) -> ASTNode:
        """Parse bitwise xor: ^"""
        left = self._parse_bitwise_and()
        
        while self._match(TokenType.BIT_XOR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_and()
            left = BinaryOp(op='^', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_bitwise_and(self) -> ASTNode:
        """Parse bitwise and: &"""
        left = self._parse_shift()
        
        while self._match(TokenType.BIT_AND):
            tok = self.tokens[self.pos - 1]
            right = self._parse_shift()
            left = BinaryOp(op='&', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_shift(self) -> ASTNode:
        """Parse shift: <<, >>"""
        left = self._parse_additive()
        
        while self._match(TokenType.SHL, TokenType.SHR):
            tok = self.tokens[self.pos - 1]
            op = '<<' if tok.type == TokenType.SHL else '>>'
            right = self._parse_additive()
            left = BinaryOp(op=op, left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_additive(self) -> ASTNode:
        """Parse addition/subtraction."""
        left = self._parse_multiplicative()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            tok = self.tokens[self.pos - 1]
            op = '+' if tok.type == TokenType.PLUS else '-'
            right = self._parse_multiplicative()
            left = BinaryOp(op=op, left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division/modulo."""
        left = self._parse_power()
        
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.FLOOR_DIV):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.STAR: '*', TokenType.SLASH: '/',
                      TokenType.PERCENT: '%', TokenType.FLOOR_DIV: '//'}
            right = self._parse_power()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_power(self) -> ASTNode:
        """Parse power: ** (right associative)"""
        left = self._parse_unary()
        
        if self._match(TokenType.POWER):
            tok = self.tokens[self.pos - 1]
            right = self._parse_power()  # Right associative
            return BinaryOp(op='**', left=left, right=right,
                            line=tok.line, column=tok.column)
        
        return left
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary: -, !, not, ~"""
        if self._match(TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.MINUS: '-', TokenType.NOT: 'not', TokenType.BIT_NOT: '~'}
            operand = self._parse_unary()
            return UnaryOp(op=op_map[tok.type], operand=operand, prefix=True,
                           line=tok.line, column=tok.column)
        
        return self._parse_postfix()
    
    def _parse_postfix(self) -> ASTNode:
        """Parse postfix: calls, indexing, member access, step chains."""
        expr = self._parse_primary()
        
        while True:
            # Only allow function calls on identifiers, member access, or other calls
            # NOT on literals (prevents "string"(args) being parsed as call)
            if self._check(TokenType.LPAREN) and not isinstance(expr, Literal):
                self._advance()  # consume LPAREN
                # Function call
                tok = self.tokens[self.pos - 1]
                args = []
                if not self._check(TokenType.RPAREN):
                    args = self._parse_args()
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                expr = Call(callee=expr, args=args, line=tok.line, column=tok.column)
            
            elif self._match(TokenType.LBRACKET):
                # Index access
                tok = self.tokens[self.pos - 1]
                index = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = Index(obj=expr, index=index, line=tok.line, column=tok.column)
            
            elif self._match(TokenType.DOT):
                # Member access - allow type keywords as field names too
                # e.g., x.str, x.int, x.float, x.bool, x.type
                tok = self.tokens[self.pos - 1]
                
                # Accept identifier OR type keywords as field names
                if self._check(TokenType.IDENTIFIER):
                    field_tok = self._advance()
                    field_name = field_tok.value
                    expr = Member(obj=expr, field=field_name,
                                  line=tok.line, column=tok.column)
                elif self._check(TokenType.STR, TokenType.INT, TokenType.FLOAT,
                                  TokenType.BOOL, TokenType.TYPE, TokenType.LIST,
                                  TokenType.MAP, TokenType.ANY):
                    field_tok = self._advance()
                    field_name = field_tok.value
                    expr = Member(obj=expr, field=field_name,
                                  line=tok.line, column=tok.column)
                else:
                    # Allow step tokens directly after a dot, e.g. obj._sort._take
                    if self._is_step_token():
                        steps = []
                        while self._is_step_token():
                            step_tok = self._advance()
                            step_name = step_tok.value
                            step_args = []
                            if self._match(TokenType.LPAREN):
                                if not self._check(TokenType.RPAREN):
                                    step_args = self._parse_args()
                                self._consume(TokenType.RPAREN, f"Expected ')' after {step_name} arguments")
                            steps.append((step_name, step_args))
                        expr = StepChain(source=expr, steps=steps, dotted=True,
                                         line=tok.line, column=tok.column)
                    else:
                        raise SyntaxError(f"Line {tok.line}: Expected field name after '.'")
            
            elif self._is_step_token():
                # Step chain: data _filter _sort _take
                # Collect all steps until no more step tokens
                tok = self._peek()
                steps = []
                
                while self._is_step_token():
                    step_tok = self._advance()
                    step_name = step_tok.value  # _filter, _sort, etc.
                    step_args = []
                    
                    # Check for optional arguments: _filter(x > 5) or _take(3)
                    if self._match(TokenType.LPAREN):
                        if not self._check(TokenType.RPAREN):
                            step_args = self._parse_args()
                        self._consume(TokenType.RPAREN, f"Expected ')' after {step_name} arguments")
                    
                    steps.append((step_name, step_args))
                
                expr = StepChain(source=expr, steps=steps,
                                 line=tok.line, column=tok.column)
            
            else:
                break
        
        return expr
    
    def _is_step_token(self) -> bool:
        """Check if current token is a step token (_filter, _sort, etc.)."""
        return self._check(
            TokenType.STEP_FILTER, TokenType.STEP_SORT, TokenType.STEP_MAP,
            TokenType.STEP_TAKE, TokenType.STEP_DROP, TokenType.STEP_FIRST,
            TokenType.STEP_LAST, TokenType.STEP_REVERSE, TokenType.STEP_UNIQUE,
            TokenType.STEP_COUNT, TokenType.STEP_SUM, TokenType.STEP_AVG,
            TokenType.STEP_MIN, TokenType.STEP_MAX, TokenType.STEP_GROUP,
            TokenType.STEP_FLATTEN, TokenType.STEP_ZIP, TokenType.STEP_CHUNK,
        )
    
    def _parse_args(self) -> List[ASTNode]:
        """Parse function call arguments.
        
        Supports both comma-separated and space-separated arguments:
            show("hello", name)   -- comma separated (traditional)
            show("hello" name)    -- space separated (friendly)
            show "hello" name     -- also works
        """
        args = [self._parse_expression()]
        
        while True:
            # Traditional comma separator
            if self._match(TokenType.COMMA):
                args.append(self._parse_expression())
            # Space-separated: if next token is a valid expression start, treat as another arg
            elif self._can_start_expression() and not self._check(TokenType.RPAREN):
                args.append(self._parse_expression())
            else:
                break
        
        return args
    
    def _can_start_expression(self) -> bool:
        """Check if current token can start an expression (for space-separated args)."""
        return self._check(
            TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL,
            TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LBRACKET, TokenType.LBRACE,
            TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT
        )
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        tok = self._peek()
        
        # Literals
        if self._match(TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL):
            return Literal(value=tok.value, line=tok.line, column=tok.column)
        
        # Identifier
        if self._match(TokenType.IDENTIFIER):
            return Identifier(name=tok.value, line=tok.line, column=tok.column)
        
        # Type keywords as identifiers (for builtin functions like str(), int(), etc.)
        if self._match(TokenType.INT, TokenType.FLOAT, TokenType.STR, TokenType.BOOL,
                       TokenType.LIST, TokenType.MAP, TokenType.ANY):
            return Identifier(name=tok.value, line=tok.line, column=tok.column)
        
        # Parenthesized expression or lambda
        if self._match(TokenType.LPAREN):
            # Check for lambda: (x, y) => ...
            if self._check(TokenType.RPAREN) or self._check(TokenType.IDENTIFIER):
                # Might be lambda
                start_pos = self.pos
                params = []
                
                try:
                    if not self._check(TokenType.RPAREN):
                        params = self._parse_lambda_params()
                    self._consume(TokenType.RPAREN, "")
                    
                    if self._match(TokenType.FAT_ARROW):
                        body = self._parse_expression()
                        return Lambda(params=params, body=body,
                                       line=tok.line, column=tok.column)
                except:
                    pass
                
                # Not a lambda, backtrack
                self.pos = start_pos
            
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # Array literal
        if self._match(TokenType.LBRACKET):
            elements = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    if self._check(TokenType.RBRACKET):
                        break
                    elements.append(self._parse_expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after array elements")
            return Array(elements=elements, line=tok.line, column=tok.column)
        
        # Map literal: { key: value, ... }
        if self._match(TokenType.LBRACE):
            pairs = []
            self._skip_newlines()
            if not self._check(TokenType.RBRACE):
                key = self._parse_expression()
                self._consume(TokenType.COLON, "Expected ':' after map key")
                value = self._parse_expression()
                pairs.append((key, value))
                
                while self._match(TokenType.COMMA):
                    self._skip_newlines()
                    if self._check(TokenType.RBRACE):
                        break
                    key = self._parse_expression()
                    self._consume(TokenType.COLON, "Expected ':' after map key")
                    value = self._parse_expression()
                    pairs.append((key, value))
            
            self._skip_newlines()
            self._consume(TokenType.RBRACE, "Expected '}' after map literal")
            return MapLiteral(pairs=pairs, line=tok.line, column=tok.column)
        
        # Lambda: |x, y| expr
        if self._match(TokenType.BIT_OR):
            params = self._parse_lambda_params()
            self._consume(TokenType.BIT_OR, "Expected '|' after lambda parameters")
            body = self._parse_expression()
            return Lambda(params=params, body=body, line=tok.line, column=tok.column)
        
        raise SyntaxError(f"Line {tok.line}: Unexpected token '{tok.value}'")
    
    def _parse_lambda_params(self) -> List[str]:
        """Parse lambda parameters."""
        params = []
        
        if self._check(TokenType.IDENTIFIER):
            tok = self._advance()
            params.append(tok.value)
            
            while self._match(TokenType.COMMA):
                tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
                params.append(tok.value)
        
        return params
