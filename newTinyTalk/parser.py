"""
TinyTalk Parser
Recursive-descent parser producing AST.

Supports both modern (brace-delimited) and classic (end-delimited) syntax.
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import (
    ASTNode, Program, Literal, Identifier, BinaryOp, UnaryOp, Call, Index,
    Member, Array, MapLiteral, Lambda, Conditional, Range, Pipe, StepChain,
    StringInterp, LetStmt, ConstStmt, AssignStmt, Block, IfStmt, ForStmt,
    WhileStmt, ReturnStmt, BreakStmt, ContinueStmt, FnDecl, StructDecl,
    EnumDecl, ImportStmt, MatchStmt, TryStmt, ThrowStmt,
)


STEP_TOKEN_TYPES = frozenset({
    TokenType.STEP_FILTER, TokenType.STEP_SORT, TokenType.STEP_MAP,
    TokenType.STEP_TAKE, TokenType.STEP_DROP, TokenType.STEP_FIRST,
    TokenType.STEP_LAST, TokenType.STEP_REVERSE, TokenType.STEP_UNIQUE,
    TokenType.STEP_COUNT, TokenType.STEP_SUM, TokenType.STEP_AVG,
    TokenType.STEP_MIN, TokenType.STEP_MAX, TokenType.STEP_GROUP,
    TokenType.STEP_FLATTEN, TokenType.STEP_ZIP, TokenType.STEP_CHUNK,
    TokenType.STEP_REDUCE,
    TokenType.STEP_SORT_BY, TokenType.STEP_JOIN,
    TokenType.STEP_MAP_VALUES, TokenType.STEP_EACH,
    # dplyr-style verbs
    TokenType.STEP_SELECT, TokenType.STEP_MUTATE, TokenType.STEP_SUMMARIZE,
    TokenType.STEP_RENAME, TokenType.STEP_ARRANGE, TokenType.STEP_DISTINCT,
    TokenType.STEP_SLICE, TokenType.STEP_PULL, TokenType.STEP_GROUP_BY,
    TokenType.STEP_LEFT_JOIN,
    TokenType.STEP_PIVOT, TokenType.STEP_UNPIVOT, TokenType.STEP_WINDOW,
})

EXPR_START_TOKENS = frozenset({
    TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL,
    TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LBRACKET, TokenType.LBRACE,
    TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT,
    TokenType.INTERP_STRING_START,
})


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Program:
        stmts = []
        self._skip_newlines()
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            self._skip_newlines()
        return Program(statements=stmts)

    # -- helpers ------------------------------------------------------------

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self, offset: int = 0) -> Token:
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else self.tokens[-1]

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

    def _consume(self, tt: TokenType, msg: str) -> Token:
        if self._check(tt):
            return self._advance()
        raise SyntaxError(f"Line {self._peek().line}: {msg}")

    def _skip_newlines(self):
        while self._match(TokenType.NEWLINE):
            pass

    # -- statements ---------------------------------------------------------

    def _parse_statement(self) -> Optional[ASTNode]:
        tok = self._peek()

        # Modern keywords
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
        if self._match(TokenType.FROM):
            return self._parse_from_import()
        if self._match(TokenType.IMPORT):
            return self._parse_import()
        if self._match(TokenType.MATCH):
            return self._parse_match()
        if self._match(TokenType.TRY):
            return self._parse_try()
        if self._match(TokenType.THROW):
            return self._parse_throw()
        if self._match(TokenType.STRUCT):
            return self._parse_struct()
        if self._match(TokenType.ENUM):
            return self._parse_enum()

        # Classic (Smalltalk-inspired) keywords
        if self._match(TokenType.BLUEPRINT):
            return self._parse_blueprint()
        if self._match(TokenType.LAW):
            return self._parse_end_delimited_fn()
        if self._match(TokenType.FORGE):
            return self._parse_end_delimited_fn()
        if self._match(TokenType.WHEN):
            return self._parse_when()
        if self._match(TokenType.FIN):
            return self._parse_keyword_return()
        if self._match(TokenType.REPLY):
            return self._parse_keyword_return()
        if self._match(TokenType.DO):
            return self._parse_keyword_return()

        # Bare block
        if self._match(TokenType.LBRACE):
            return self._parse_block()

        # Expression or assignment
        return self._parse_expression_statement()

    # -- modern statement parsers -------------------------------------------

    def _parse_let(self) -> LetStmt:
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        type_hint = None
        if self._match(TokenType.COLON):
            type_hint = self._parse_type_hint()
        value = None
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
        return LetStmt(
            name=name_tok.value, type_hint=type_hint, value=value,
            line=tok.line, column=tok.column,
        )

    def _parse_const(self) -> ConstStmt:
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected constant name")
        self._consume(TokenType.ASSIGN, "Expected '=' after constant name")
        value = self._parse_expression()
        return ConstStmt(name=name_tok.value, value=value, line=tok.line, column=tok.column)

    def _parse_fn(self) -> FnDecl:
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name")
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = [] if self._check(TokenType.RPAREN) else self._parse_params()
        self._consume(TokenType.RPAREN, "Expected ')'")
        ret_type = None
        if self._match(TokenType.ARROW):
            ret_type = self._parse_type_hint()
        elif self._match(TokenType.COLON):
            # fn name(params): ReturnType { body }
            ret_type = self._parse_type_hint()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self._parse_block()
        return FnDecl(
            name=name_tok.value, params=params, return_type=ret_type,
            body=body, line=tok.line, column=tok.column,
        )

    def _parse_params(self) -> list:
        params = []
        while True:
            name_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            th = None
            if self._match(TokenType.COLON):
                th = self._parse_type_hint()
            default = None
            if self._match(TokenType.ASSIGN):
                default = self._parse_expression()
            params.append((name_tok.value, th, default))
            if not self._match(TokenType.COMMA):
                break
        return params

    def _parse_type_hint(self) -> str:
        # Handle leading ? for optional types: ?str, ?int, etc.
        optional_prefix = self._match(TokenType.QUESTION)
        tok = self._advance()
        if tok.type == TokenType.IDENTIFIER:
            ts = tok.value
        elif tok.type in (
            TokenType.INT, TokenType.FLOAT, TokenType.STR,
            TokenType.BOOL, TokenType.LIST, TokenType.MAP,
            TokenType.ANY, TokenType.VOID,
        ):
            ts = tok.value
        else:
            raise SyntaxError(f"Line {tok.line}: Expected type")
        if self._match(TokenType.LBRACKET):
            inner = [self._parse_type_hint()]
            while self._match(TokenType.COMMA):
                inner.append(self._parse_type_hint())
            self._consume(TokenType.RBRACKET, "Expected ']'")
            ts = f"{ts}[{', '.join(inner)}]"
        if optional_prefix or self._match(TokenType.QUESTION):
            ts = f"?{ts}"
        return ts

    def _parse_if(self) -> IfStmt:
        tok = self.tokens[self.pos - 1]
        cond = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{' after if condition")
        then_br = self._parse_block()
        elif_brs = []
        else_br = None
        self._skip_newlines()
        while self._match(TokenType.ELIF):
            ec = self._parse_expression()
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{' after elif condition")
            eb = self._parse_block()
            elif_brs.append((ec, eb))
            self._skip_newlines()
        if self._match(TokenType.ELSE):
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{' after else")
            else_br = self._parse_block()
        return IfStmt(
            condition=cond, then_branch=then_br,
            elif_branches=elif_brs, else_branch=else_br,
            line=tok.line, column=tok.column,
        )

    def _parse_for(self) -> ForStmt:
        tok = self.tokens[self.pos - 1]
        var_tok = self._consume(TokenType.IDENTIFIER, "Expected loop variable")
        self._consume(TokenType.IN, "Expected 'in'")
        iterable = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        body = self._parse_block()
        return ForStmt(var=var_tok.value, iterable=iterable, body=body,
                       line=tok.line, column=tok.column)

    def _parse_while(self) -> WhileStmt:
        tok = self.tokens[self.pos - 1]
        cond = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        body = self._parse_block()
        return WhileStmt(condition=cond, body=body, line=tok.line, column=tok.column)

    def _parse_return(self) -> ReturnStmt:
        tok = self.tokens[self.pos - 1]
        value = None
        if not self._check(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self._parse_expression()
        return ReturnStmt(value=value, line=tok.line, column=tok.column)

    def _parse_block(self) -> Block:
        tok = self.tokens[self.pos - 1]
        stmts = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            self._skip_newlines()
        self._consume(TokenType.RBRACE, "Expected '}'")
        return Block(statements=stmts, line=tok.line, column=tok.column)

    def _parse_struct(self) -> StructDecl:
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected struct name")
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        fields = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            fn = self._consume(TokenType.IDENTIFIER, "Expected field name")
            self._consume(TokenType.COLON, "Expected ':'")
            ft = self._parse_type_hint()
            default = None
            if self._match(TokenType.ASSIGN):
                default = self._parse_expression()
            fields.append((fn.value, ft, default))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        self._consume(TokenType.RBRACE, "Expected '}'")
        return StructDecl(name=name_tok.value, fields=fields, line=tok.line, column=tok.column)

    def _parse_enum(self) -> EnumDecl:
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected enum name")
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        variants = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            vn = self._consume(TokenType.IDENTIFIER, "Expected variant name")
            val = None
            if self._match(TokenType.ASSIGN):
                val = self._parse_expression()
            variants.append((vn.value, val))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        self._consume(TokenType.RBRACE, "Expected '}'")
        return EnumDecl(name=name_tok.value, variants=variants, line=tok.line, column=tok.column)

    def _parse_import(self) -> ImportStmt:
        tok = self.tokens[self.pos - 1]
        mod_tok = self._consume(TokenType.STRING, "Expected module path")
        alias = None
        items = []
        if self._match(TokenType.AS):
            alias = self._consume(TokenType.IDENTIFIER, "Expected alias").value
        # from "module" use { name1, name2 } style is handled by _parse_from
        return ImportStmt(module=mod_tok.value, items=items, alias=alias, line=tok.line, column=tok.column)

    def _parse_from_import(self) -> ImportStmt:
        """from "module" use { name1, name2 }"""
        tok = self.tokens[self.pos - 1]
        mod_tok = self._consume(TokenType.STRING, "Expected module path after 'from'")
        self._consume(TokenType.USE, "Expected 'use' after module path")
        items = []
        if self._match(TokenType.LBRACE):
            self._skip_newlines()
            if not self._check(TokenType.RBRACE):
                items.append(self._consume(TokenType.IDENTIFIER, "Expected name").value)
                while self._match(TokenType.COMMA):
                    self._skip_newlines()
                    if self._check(TokenType.RBRACE):
                        break
                    items.append(self._consume(TokenType.IDENTIFIER, "Expected name").value)
            self._skip_newlines()
            self._consume(TokenType.RBRACE, "Expected '}'")
        else:
            items.append(self._consume(TokenType.IDENTIFIER, "Expected name after 'use'").value)
            while self._match(TokenType.COMMA):
                items.append(self._consume(TokenType.IDENTIFIER, "Expected name").value)
        return ImportStmt(module=mod_tok.value, items=items, alias=None, line=tok.line, column=tok.column)

    def _parse_match(self) -> MatchStmt:
        return self._parse_match_expr()

    def _parse_match_expr(self) -> MatchStmt:
        """Parse match expression: match value { pattern => expr, ... }"""
        tok = self.tokens[self.pos - 1]
        value = self._parse_expression()
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        cases = []
        self._skip_newlines()
        while not self._check(TokenType.RBRACE):
            pattern = self._parse_expression()
            self._consume(TokenType.FAT_ARROW, "Expected '=>'")
            body = self._parse_expression()
            cases.append((pattern, body))
            self._skip_newlines()
            self._match(TokenType.COMMA)
            self._skip_newlines()
        self._consume(TokenType.RBRACE, "Expected '}'")
        return MatchStmt(value=value, cases=cases, line=tok.line, column=tok.column)

    def _parse_try(self) -> TryStmt:
        tok = self.tokens[self.pos - 1]
        self._skip_newlines()
        self._consume(TokenType.LBRACE, "Expected '{'")
        body = self._parse_block()
        catch_var = None
        catch_body = None
        self._skip_newlines()
        if self._match(TokenType.CATCH):
            if self._match(TokenType.LPAREN):
                catch_var = self._consume(TokenType.IDENTIFIER, "Expected catch variable").value
                self._consume(TokenType.RPAREN, "Expected ')'")
            self._skip_newlines()
            self._consume(TokenType.LBRACE, "Expected '{'")
            catch_body = self._parse_block()
        return TryStmt(body=body, catch_var=catch_var, catch_body=catch_body,
                       line=tok.line, column=tok.column)

    def _parse_throw(self) -> ThrowStmt:
        tok = self.tokens[self.pos - 1]
        value = self._parse_expression()
        return ThrowStmt(value=value, line=tok.line, column=tok.column)

    # -- classic (Smalltalk-inspired) parsers --------------------------------

    def _parse_blueprint(self) -> StructDecl:
        """blueprint Name ... end"""
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected blueprint name")
        self._skip_newlines()
        fields = []
        methods = []
        while not self._check(TokenType.END) and not self._at_end():
            self._skip_newlines()
            if self._check(TokenType.END):
                break
            if self._match(TokenType.FIELD):
                fn = self._consume(TokenType.IDENTIFIER, "Expected field name")
                default = None
                if self._match(TokenType.ASSIGN):
                    default = self._parse_expression()
                fields.append((fn.value, None, default))
            elif self._match(TokenType.FORGE):
                method = self._parse_end_delimited_fn()
                methods.append(("forge", method))
            elif self._match(TokenType.LAW):
                method = self._parse_end_delimited_fn()
                methods.append(("law", method))
            self._skip_newlines()
        self._consume(TokenType.END, "Expected 'end' after blueprint")
        return StructDecl(
            name=name_tok.value, fields=fields, methods=methods,
            line=tok.line, column=tok.column,
        )

    def _parse_end_delimited_fn(self) -> FnDecl:
        """law name(params) ... end  or  forge name(params) ... end"""
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name")
        params = []
        if self._match(TokenType.LPAREN):
            if not self._check(TokenType.RPAREN):
                params = self._parse_params()
            self._consume(TokenType.RPAREN, "Expected ')'")
        self._skip_newlines()
        stmts = []
        while not self._check(TokenType.END) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                stmts.append(stmt)
            self._skip_newlines()
        self._consume(TokenType.END, "Expected 'end'")
        body = Block(statements=stmts, line=tok.line, column=tok.column)
        return FnDecl(name=name_tok.value, params=params, body=body,
                      line=tok.line, column=tok.column)

    def _parse_when(self):
        """
        when x = 42          -> ConstStmt
        when square(x) ... end/finfr  -> FnDecl
        """
        tok = self.tokens[self.pos - 1]
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected name after 'when'")

        if self._match(TokenType.LPAREN):
            # Function
            params = [] if self._check(TokenType.RPAREN) else self._parse_params()
            self._consume(TokenType.RPAREN, "Expected ')'")
            self._skip_newlines()
            stmts = []
            while (
                not self._check(TokenType.FIN, TokenType.END)
                and not self._at_end()
            ):
                stmt = self._parse_statement()
                if stmt:
                    stmts.append(stmt)
                self._skip_newlines()
            if not self._match(TokenType.FIN):
                self._consume(TokenType.END, "Expected 'fin' or 'end'")
            body = Block(statements=stmts, line=tok.line, column=tok.column)
            return FnDecl(name=name_tok.value, params=params, body=body,
                          line=tok.line, column=tok.column)
        else:
            # Constant
            self._consume(TokenType.ASSIGN, "Expected '='")
            value = self._parse_expression()
            return ConstStmt(name=name_tok.value, value=value,
                             line=tok.line, column=tok.column)

    def _parse_keyword_return(self) -> ReturnStmt:
        """fin, reply, do -> all produce ReturnStmt."""
        tok = self.tokens[self.pos - 1]
        value = None
        stop = (TokenType.NEWLINE, TokenType.END, TokenType.EOF, TokenType.FIN)
        if not self._check(*stop):
            value = self._parse_expression()
        return ReturnStmt(value=value, line=tok.line, column=tok.column)

    # -- expression statement -----------------------------------------------

    def _parse_expression_statement(self) -> ASTNode:
        expr = self._parse_expression()
        if self._match(
            TokenType.ASSIGN, TokenType.PLUS_EQ, TokenType.MINUS_EQ,
            TokenType.STAR_EQ, TokenType.SLASH_EQ, TokenType.PERCENT_EQ,
        ):
            op = self.tokens[self.pos - 1].value
            value = self._parse_expression()
            return AssignStmt(target=expr, value=value, op=op,
                              line=expr.line, column=expr.column)
        return expr

    # -- expressions (precedence climbing) ----------------------------------

    def _parse_expression(self) -> ASTNode:
        return self._parse_pipe()

    def _parse_pipe(self) -> ASTNode:
        left = self._parse_ternary()
        while self._match(TokenType.PIPE):
            tok = self.tokens[self.pos - 1]
            right = self._parse_ternary()
            left = Pipe(left=left, right=right, line=tok.line, column=tok.column)
        return left

    def _parse_ternary(self) -> ASTNode:
        cond = self._parse_or()
        if self._match(TokenType.QUESTION):
            tok = self.tokens[self.pos - 1]
            then_e = self._parse_expression()
            self._consume(TokenType.COLON, "Expected ':' in ternary")
            else_e = self._parse_expression()
            return Conditional(condition=cond, then_expr=then_e, else_expr=else_e,
                               line=tok.line, column=tok.column)
        return cond

    def _parse_or(self) -> ASTNode:
        left = self._parse_and()
        while self._match(TokenType.OR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_and()
            left = BinaryOp(op="or", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_and(self) -> ASTNode:
        left = self._parse_equality()
        while self._match(TokenType.AND):
            tok = self.tokens[self.pos - 1]
            right = self._parse_equality()
            left = BinaryOp(op="and", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_equality(self) -> ASTNode:
        left = self._parse_comparison()
        while self._match(
            TokenType.EQ, TokenType.NE,
            TokenType.IS, TokenType.ISNT,
            TokenType.HAS, TokenType.HASNT,
            TokenType.ISIN, TokenType.ISLIKE,
        ):
            tok = self.tokens[self.pos - 1]
            op_map = {
                TokenType.EQ: "==", TokenType.NE: "!=",
                TokenType.IS: "is", TokenType.ISNT: "isnt",
                TokenType.HAS: "has", TokenType.HASNT: "hasnt",
                TokenType.ISIN: "isin", TokenType.ISLIKE: "islike",
            }
            right = self._parse_comparison()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_range()
        while self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.LT: "<", TokenType.GT: ">",
                      TokenType.LE: "<=", TokenType.GE: ">="}
            right = self._parse_range()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_range(self) -> ASTNode:
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
        left = self._parse_bitwise_xor()
        while self._match(TokenType.BIT_OR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_xor()
            left = BinaryOp(op="|", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_bitwise_xor(self) -> ASTNode:
        left = self._parse_bitwise_and()
        while self._match(TokenType.BIT_XOR):
            tok = self.tokens[self.pos - 1]
            right = self._parse_bitwise_and()
            left = BinaryOp(op="^", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_bitwise_and(self) -> ASTNode:
        left = self._parse_shift()
        while self._match(TokenType.BIT_AND):
            tok = self.tokens[self.pos - 1]
            right = self._parse_shift()
            left = BinaryOp(op="&", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_shift(self) -> ASTNode:
        left = self._parse_additive()
        while self._match(TokenType.SHL, TokenType.SHR):
            tok = self.tokens[self.pos - 1]
            op = "<<" if tok.type == TokenType.SHL else ">>"
            right = self._parse_additive()
            left = BinaryOp(op=op, left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_additive(self) -> ASTNode:
        left = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            tok = self.tokens[self.pos - 1]
            op = "+" if tok.type == TokenType.PLUS else "-"
            right = self._parse_multiplicative()
            left = BinaryOp(op=op, left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_multiplicative(self) -> ASTNode:
        left = self._parse_power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.FLOOR_DIV):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.STAR: "*", TokenType.SLASH: "/",
                      TokenType.PERCENT: "%", TokenType.FLOOR_DIV: "//"}
            right = self._parse_power()
            left = BinaryOp(op=op_map[tok.type], left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_power(self) -> ASTNode:
        left = self._parse_unary()
        if self._match(TokenType.POWER):
            tok = self.tokens[self.pos - 1]
            right = self._parse_power()  # right-associative
            return BinaryOp(op="**", left=left, right=right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._match(TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT):
            tok = self.tokens[self.pos - 1]
            op_map = {TokenType.MINUS: "-", TokenType.NOT: "not", TokenType.BIT_NOT: "~"}
            operand = self._parse_unary()
            return UnaryOp(op=op_map[tok.type], operand=operand, prefix=True,
                           line=tok.line, column=tok.column)
        return self._parse_postfix()

    def _parse_postfix(self) -> ASTNode:
        expr = self._parse_primary()

        while True:
            # Function call
            if self._check(TokenType.LPAREN) and not isinstance(expr, Literal):
                self._advance()
                tok = self.tokens[self.pos - 1]
                args = [] if self._check(TokenType.RPAREN) else self._parse_args()
                self._consume(TokenType.RPAREN, "Expected ')'")
                expr = Call(callee=expr, args=args, line=tok.line, column=tok.column)

            # Index
            elif self._match(TokenType.LBRACKET):
                tok = self.tokens[self.pos - 1]
                idx = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Expected ']'")
                expr = Index(obj=expr, index=idx, line=tok.line, column=tok.column)

            # Member access
            elif self._match(TokenType.DOT):
                tok = self.tokens[self.pos - 1]
                if self._check(TokenType.IDENTIFIER):
                    ft = self._advance()
                    expr = Member(obj=expr, field_name=ft.value,
                                  line=tok.line, column=tok.column)
                elif self._check(
                    TokenType.STR, TokenType.INT, TokenType.FLOAT,
                    TokenType.BOOL, TokenType.LIST, TokenType.MAP,
                    TokenType.ANY, TokenType.VOID,
                ):
                    ft = self._advance()
                    expr = Member(obj=expr, field_name=ft.value,
                                  line=tok.line, column=tok.column)
                elif self._peek().type in STEP_TOKEN_TYPES:
                    steps = self._collect_steps()
                    expr = StepChain(source=expr, steps=steps,
                                     line=tok.line, column=tok.column)
                else:
                    raise SyntaxError(f"Line {tok.line}: Expected field name after '.'")

            # Step chain
            elif self._peek().type in STEP_TOKEN_TYPES:
                tok = self._peek()
                steps = self._collect_steps()
                expr = StepChain(source=expr, steps=steps,
                                 line=tok.line, column=tok.column)
            else:
                # Before giving up, look past newlines for step chain
                # continuation.  Step tokens (_filter, _select, etc.) can
                # ONLY appear as step chains, never as standalone statements,
                # so this is safe.
                saved = self.pos
                self._skip_newlines()
                if self._peek().type in STEP_TOKEN_TYPES:
                    tok = self._peek()
                    steps = self._collect_steps()
                    expr = StepChain(source=expr, steps=steps,
                                     line=tok.line, column=tok.column)
                else:
                    self.pos = saved
                    break

        return expr

    def _collect_steps(self) -> list:
        steps = []
        while self._peek().type in STEP_TOKEN_TYPES:
            st = self._advance()
            args = []
            if self._match(TokenType.LPAREN):
                if not self._check(TokenType.RPAREN):
                    args = self._parse_args()
                self._consume(TokenType.RPAREN, f"Expected ')' after {st.value}")
            steps.append((st.value, args))
        return steps

    def _parse_args(self) -> List[ASTNode]:
        """Parse call arguments. Supports comma-separated AND space-separated.

        Trailing punctuation like ! or ? after an identifier is absorbed into
        the identifier name so that ``print(Hello, world!)`` parses without
        requiring quotes around bare words.
        """
        args = [self._parse_expression()]
        args[-1] = self._absorb_trailing_punct(args[-1])
        while True:
            if self._match(TokenType.COMMA):
                args.append(self._parse_expression())
                args[-1] = self._absorb_trailing_punct(args[-1])
            elif self._peek().type in EXPR_START_TOKENS and not self._check(TokenType.RPAREN):
                args.append(self._parse_expression())
                args[-1] = self._absorb_trailing_punct(args[-1])
            else:
                break
        return args

    def _absorb_trailing_punct(self, arg: ASTNode) -> ASTNode:
        """If *arg* is an Identifier followed by ``!`` or ``?`` before a
        separator (``,``, ``)``, newline, EOF), consume the punctuation token
        and fold it into the identifier name.  This lets bare words like
        ``world!`` survive the parse."""
        if not isinstance(arg, Identifier):
            return arg
        while self._check(TokenType.NOT, TokenType.QUESTION):
            nxt = self._peek(1).type
            if nxt in (TokenType.COMMA, TokenType.RPAREN, TokenType.NEWLINE, TokenType.EOF):
                punct_tok = self._advance()
                punct = "!" if punct_tok.type == TokenType.NOT else "?"
                arg = Identifier(name=arg.name + punct, line=arg.line, column=arg.column)
            else:
                break
        return arg

    # -- primary expressions ------------------------------------------------

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()

        # Literals
        if self._match(TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL):
            return Literal(value=tok.value, line=tok.line, column=tok.column)

        # String interpolation
        if self._match(TokenType.INTERP_STRING_START):
            return self._parse_interp_string(tok)

        # Identifier
        if self._match(TokenType.IDENTIFIER):
            return Identifier(name=tok.value, line=tok.line, column=tok.column)

        # Type keywords as identifiers
        if self._match(
            TokenType.INT, TokenType.FLOAT, TokenType.STR,
            TokenType.BOOL, TokenType.LIST, TokenType.MAP, TokenType.ANY,
        ):
            return Identifier(name=tok.value, line=tok.line, column=tok.column)

        # Parenthesized expression or lambda
        if self._match(TokenType.LPAREN):
            if self._check(TokenType.RPAREN) or self._check(TokenType.IDENTIFIER):
                saved = self.pos
                try:
                    params = []
                    if not self._check(TokenType.RPAREN):
                        params = self._parse_lambda_params()
                    self._consume(TokenType.RPAREN, "")
                    if self._match(TokenType.FAT_ARROW):
                        body = self._parse_lambda_body()
                        return Lambda(params=params, body=body,
                                      line=tok.line, column=tok.column)
                except Exception:
                    pass
                self.pos = saved
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')'")
            return expr

        # Array literal
        if self._match(TokenType.LBRACKET):
            elems = []
            self._skip_newlines()
            if not self._check(TokenType.RBRACKET):
                elems.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    self._skip_newlines()
                    if self._check(TokenType.RBRACKET):
                        break
                    elems.append(self._parse_expression())
            self._skip_newlines()
            self._consume(TokenType.RBRACKET, "Expected ']'")
            return Array(elements=elems, line=tok.line, column=tok.column)

        # Map literal
        if self._match(TokenType.LBRACE):
            pairs = []
            self._skip_newlines()
            if not self._check(TokenType.RBRACE):
                k = self._parse_expression()
                self._consume(TokenType.COLON, "Expected ':'")
                v = self._parse_expression()
                pairs.append((k, v))
                while self._match(TokenType.COMMA):
                    self._skip_newlines()
                    if self._check(TokenType.RBRACE):
                        break
                    k = self._parse_expression()
                    self._consume(TokenType.COLON, "Expected ':'")
                    v = self._parse_expression()
                    pairs.append((k, v))
            self._skip_newlines()
            self._consume(TokenType.RBRACE, "Expected '}'")
            return MapLiteral(pairs=pairs, line=tok.line, column=tok.column)

        # Match expression (usable as value)
        if self._match(TokenType.MATCH):
            return self._parse_match_expr()

        # Lambda: |x, y| expr or |x, y| { block }
        if self._match(TokenType.BIT_OR):
            params = self._parse_lambda_params()
            self._consume(TokenType.BIT_OR, "Expected '|' after lambda params")
            body = self._parse_lambda_body()
            return Lambda(params=params, body=body, line=tok.line, column=tok.column)

        raise SyntaxError(f"Line {tok.line}: Unexpected token '{tok.value}' ({tok.type.name})")

    def _parse_interp_string(self, start_tok: Token) -> StringInterp:
        """Parse interpolated string after INTERP_STRING_START was consumed."""
        parts = []
        text = start_tok.value
        if text:
            parts.append(text)

        # Now we expect expression tokens followed by MID or END
        expr_tokens = []
        while not self._at_end():
            if self._check(TokenType.INTERP_STRING_MID):
                # Close current expression, start next segment
                if expr_tokens:
                    parts.append(self._tokens_to_expr(expr_tokens))
                    expr_tokens = []
                mid_tok = self._advance()
                if mid_tok.value:
                    parts.append(mid_tok.value)
            elif self._check(TokenType.INTERP_STRING_END):
                if expr_tokens:
                    parts.append(self._tokens_to_expr(expr_tokens))
                    expr_tokens = []
                end_tok = self._advance()
                if end_tok.value:
                    parts.append(end_tok.value)
                break
            else:
                expr_tokens.append(self._advance())

        return StringInterp(parts=parts, line=start_tok.line, column=start_tok.column)

    def _tokens_to_expr(self, tokens: List[Token]) -> ASTNode:
        """Parse a sub-expression from a list of tokens."""
        tokens_with_eof = tokens + [Token(TokenType.EOF, None, 0, 0)]
        sub = Parser(tokens_with_eof)
        return sub._parse_expression()

    def _parse_lambda_body(self) -> ASTNode:
        """Parse lambda body: either a single expression or a { block }.

        Disambiguates { block } from { map literal } by peeking: if the
        first token after { is a STRING followed by :, it is a map and
        we fall through to the expression parser instead.
        """
        self._skip_newlines()
        if self._check(TokenType.LBRACE):
            # Peek ahead to determine if it's a map literal or a block.
            # Map literal: { "key": expr, ... } or { identifier: expr }
            nxt = self._peek(1)
            nxt2 = self._peek(2)
            is_map = (
                (nxt.type == TokenType.STRING and nxt2.type == TokenType.COLON)
                or (nxt.type == TokenType.IDENTIFIER and nxt2.type == TokenType.COLON)
                or (nxt.type == TokenType.NUMBER and nxt2.type == TokenType.COLON)
                or nxt.type == TokenType.RBRACE  # empty map {}
            )
            if not is_map:
                self._advance()  # consume {
                return self._parse_block()
        return self._parse_expression()

    def _parse_lambda_params(self) -> List[str]:
        params = []
        if self._check(TokenType.IDENTIFIER):
            params.append(self._advance().value)
            while self._match(TokenType.COMMA):
                params.append(self._consume(TokenType.IDENTIFIER, "Expected param name").value)
        return params
