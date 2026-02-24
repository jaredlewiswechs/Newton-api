"""
TinyTalk Lexer
Tokenizer for the TinyTalk language.

Two styles, one language:
  - Modern style:  let/fn/return with { } blocks
  - Classic style:  when/law/forge/reply with end-delimited blocks

Both are first-class. Use whichever reads better for your code.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Any


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    INTERP_STRING_START = auto()   # start of "hello {
    INTERP_STRING_MID = auto()     # } middle {
    INTERP_STRING_END = auto()     # } end"

    # Identifiers
    IDENTIFIER = auto()

    # --- Classic keywords (Smalltalk-inspired) ---
    WHEN = auto()        # constant / function definition
    FIN = auto()         # return (closure can reopen)
    BLUEPRINT = auto()   # class/type definition
    LAW = auto()         # function (conceptually pure)
    FIELD = auto()       # instance field declaration
    FORGE = auto()       # method (mutating action)
    REPLY = auto()       # return from forge/law
    DO = auto()          # return in when-functions
    END = auto()         # block terminator

    # --- Modern keywords ---
    LET = auto()
    CONST = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    FOR = auto()
    WHILE = auto()
    IN = auto()
    BREAK = auto()
    CONTINUE = auto()
    MATCH = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPORT = auto()
    FROM = auto()
    USE = auto()
    AS = auto()
    TRY = auto()
    CATCH = auto()
    THROW = auto()

    # --- Step chains (dplyr-style, underscore-prefixed) ---
    STEP_FILTER = auto()
    STEP_SORT = auto()
    STEP_MAP = auto()
    STEP_TAKE = auto()
    STEP_DROP = auto()
    STEP_FIRST = auto()
    STEP_LAST = auto()
    STEP_REVERSE = auto()
    STEP_UNIQUE = auto()
    STEP_COUNT = auto()
    STEP_SUM = auto()
    STEP_AVG = auto()
    STEP_MIN = auto()
    STEP_MAX = auto()
    STEP_GROUP = auto()
    STEP_FLATTEN = auto()
    STEP_ZIP = auto()
    STEP_CHUNK = auto()
    STEP_REDUCE = auto()
    STEP_SORT_BY = auto()
    STEP_JOIN = auto()
    STEP_MAP_VALUES = auto()
    STEP_EACH = auto()

    # --- dplyr-style verbs ---
    STEP_SELECT = auto()
    STEP_MUTATE = auto()
    STEP_SUMMARIZE = auto()
    STEP_RENAME = auto()
    STEP_ARRANGE = auto()
    STEP_DISTINCT = auto()
    STEP_SLICE = auto()
    STEP_PULL = auto()
    STEP_GROUP_BY = auto()
    STEP_LEFT_JOIN = auto()
    STEP_PIVOT = auto()
    STEP_UNPIVOT = auto()
    STEP_WINDOW = auto()

    # --- Natural language comparisons ---
    IS = auto()
    ISNT = auto()
    HAS = auto()
    HASNT = auto()
    ISIN = auto()
    ISLIKE = auto()

    # --- Type keywords (also usable as identifiers) ---
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    LIST = auto()
    MAP = auto()
    ANY = auto()
    VOID = auto()

    # Logical operators
    AND = auto()
    OR = auto()
    NOT = auto()

    # Arithmetic
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    POWER = auto()
    FLOOR_DIV = auto()

    # Bitwise
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    SHL = auto()
    SHR = auto()

    # Assignment
    ASSIGN = auto()
    WALRUS = auto()
    PLUS_EQ = auto()
    MINUS_EQ = auto()
    STAR_EQ = auto()
    SLASH_EQ = auto()
    PERCENT_EQ = auto()

    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    PIPE = auto()
    DOUBLE_COLON = auto()
    QUESTION = auto()
    AT = auto()
    HASH = auto()
    RANGE = auto()
    RANGE_INCL = auto()

    # Special
    NEWLINE = auto()
    EOF = auto()
    ERROR = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        if self.type in (TokenType.NEWLINE, TokenType.EOF):
            return f"Token({self.type.name})"
        return f"Token({self.type.name}, {self.value!r})"


class Lexer:
    """Tokenizes TinyTalk source code."""

    KEYWORDS = {
        # Classic (Smalltalk-inspired)
        "when": TokenType.WHEN,
        "fin": TokenType.FIN,
        "blueprint": TokenType.BLUEPRINT,
        "law": TokenType.LAW,
        "field": TokenType.FIELD,
        "forge": TokenType.FORGE,
        "reply": TokenType.REPLY,
        "do": TokenType.DO,
        "end": TokenType.END,
        # Modern
        "let": TokenType.LET,
        "const": TokenType.CONST,
        "fn": TokenType.FN,
        "return": TokenType.RETURN,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "elif": TokenType.ELIF,
        "for": TokenType.FOR,
        "while": TokenType.WHILE,
        "in": TokenType.IN,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        "match": TokenType.MATCH,
        "struct": TokenType.STRUCT,
        "enum": TokenType.ENUM,
        "import": TokenType.IMPORT,
        "from": TokenType.FROM,
        "use": TokenType.USE,
        "as": TokenType.AS,
        "try": TokenType.TRY,
        "catch": TokenType.CATCH,
        "throw": TokenType.THROW,
        # Literals
        "true": TokenType.BOOLEAN,
        "false": TokenType.BOOLEAN,
        "null": TokenType.NULL,
        "nil": TokenType.NULL,
        # Logical
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        # Natural comparisons
        "is": TokenType.IS,
        "isnt": TokenType.ISNT,
        "has": TokenType.HAS,
        "hasnt": TokenType.HASNT,
        "isin": TokenType.ISIN,
        "islike": TokenType.ISLIKE,
        # Type keywords
        "int": TokenType.INT,
        "float": TokenType.FLOAT,
        "str": TokenType.STR,
        "bool": TokenType.BOOL,
        "list": TokenType.LIST,
        "map": TokenType.MAP,
        "any": TokenType.ANY,
        "void": TokenType.VOID,
    }

    MULTI_OPS = [
        ("**", TokenType.POWER),
        ("//", TokenType.FLOOR_DIV),
        (":=", TokenType.WALRUS),
        ("~~", TokenType.NE),
        ("==", TokenType.EQ),
        ("!=", TokenType.NE),
        ("<=", TokenType.LE),
        (">=", TokenType.GE),
        ("&&", TokenType.AND),
        ("||", TokenType.OR),
        ("<<", TokenType.SHL),
        (">>", TokenType.SHR),
        ("+=", TokenType.PLUS_EQ),
        ("-=", TokenType.MINUS_EQ),
        ("*=", TokenType.STAR_EQ),
        ("/=", TokenType.SLASH_EQ),
        ("%>%", TokenType.PIPE),
        ("%=", TokenType.PERCENT_EQ),
        ("->", TokenType.ARROW),
        ("=>", TokenType.FAT_ARROW),
        ("|>", TokenType.PIPE),
        ("::", TokenType.DOUBLE_COLON),
        ("..=", TokenType.RANGE_INCL),
        ("..", TokenType.RANGE),
    ]

    SINGLE_OPS = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "%": TokenType.PERCENT,
        "<": TokenType.LT,
        ">": TokenType.GT,
        "=": TokenType.ASSIGN,
        "&": TokenType.BIT_AND,
        "|": TokenType.BIT_OR,
        "^": TokenType.BIT_XOR,
        "~": TokenType.BIT_NOT,
        "!": TokenType.NOT,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        ",": TokenType.COMMA,
        ".": TokenType.DOT,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
        "?": TokenType.QUESTION,
        "@": TokenType.AT,
    }

    STEP_KEYWORDS = {
        "_filter": TokenType.STEP_FILTER,
        "_sort": TokenType.STEP_SORT,
        "_map": TokenType.STEP_MAP,
        "_take": TokenType.STEP_TAKE,
        "_drop": TokenType.STEP_DROP,
        "_first": TokenType.STEP_FIRST,
        "_last": TokenType.STEP_LAST,
        "_reverse": TokenType.STEP_REVERSE,
        "_unique": TokenType.STEP_UNIQUE,
        "_count": TokenType.STEP_COUNT,
        "_sum": TokenType.STEP_SUM,
        "_avg": TokenType.STEP_AVG,
        "_min": TokenType.STEP_MIN,
        "_max": TokenType.STEP_MAX,
        "_group": TokenType.STEP_GROUP,
        "_flatten": TokenType.STEP_FLATTEN,
        "_zip": TokenType.STEP_ZIP,
        "_chunk": TokenType.STEP_CHUNK,
        "_reduce": TokenType.STEP_REDUCE,
        "_sortBy": TokenType.STEP_SORT_BY,
        "_join": TokenType.STEP_JOIN,
        "_mapValues": TokenType.STEP_MAP_VALUES,
        "_each": TokenType.STEP_EACH,
        # dplyr-style verbs
        "_select": TokenType.STEP_SELECT,
        "_mutate": TokenType.STEP_MUTATE,
        "_summarize": TokenType.STEP_SUMMARIZE,
        "_summarise": TokenType.STEP_SUMMARIZE,
        "_rename": TokenType.STEP_RENAME,
        "_arrange": TokenType.STEP_ARRANGE,
        "_distinct": TokenType.STEP_DISTINCT,
        "_slice": TokenType.STEP_SLICE,
        "_pull": TokenType.STEP_PULL,
        "_groupBy": TokenType.STEP_GROUP_BY,
        "_group_by": TokenType.STEP_GROUP_BY,
        "_leftJoin": TokenType.STEP_LEFT_JOIN,
        "_left_join": TokenType.STEP_LEFT_JOIN,
        "_pivot": TokenType.STEP_PIVOT,
        "_unpivot": TokenType.STEP_UNPIVOT,
        "_window": TokenType.STEP_WINDOW,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self._nesting = 0  # paren/bracket nesting depth

    def _is_floor_div(self) -> bool:
        """Disambiguate // as floor-div vs comment.

        Rule: // is floor-division only when INSIDE parentheses or brackets.
        At the top level (statement boundary), // is always a comment.
        """
        return self._nesting > 0

    def tokenize(self) -> List[Token]:
        while not self._at_end():
            self._skip_whitespace()
            if self._at_end():
                break
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    # -- helpers ------------------------------------------------------------

    def _at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self, offset: int = 0) -> str:
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else "\0"

    def _advance(self) -> str:
        c = self.source[self.pos]
        self.pos += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def _skip_whitespace(self):
        while not self._at_end():
            c = self._peek()
            if c in " \t\r":
                self._advance()
            elif c == "\n":
                self._advance()
                self.tokens.append(
                    Token(TokenType.NEWLINE, "\n", self.line - 1, self.column)
                )
            elif c == "/" and self._peek(1) == "/":
                # // is floor-division only inside parens/brackets.
                # At top level it's always a line comment.
                if self._is_floor_div():
                    break
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            elif c == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while not self._at_end():
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
            elif c == "#":
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            else:
                break

    # -- scanning -----------------------------------------------------------

    def _scan_token(self):
        start_line = self.line
        start_col = self.column

        # Multi-char operators
        for op, tt in self.MULTI_OPS:
            if self.source[self.pos : self.pos + len(op)] == op:
                for _ in range(len(op)):
                    self._advance()
                self.tokens.append(Token(tt, op, start_line, start_col))
                return

        c = self._peek()

        # Strings (with interpolation support)
        if c in "\"'":
            self._scan_string(c)
            return

        # Raw strings
        if c == "r" and self._peek(1) in "\"'":
            self._advance()
            self._scan_string(self._peek(), raw=True)
            return

        # Numbers
        if c.isdigit() or (c == "." and self._peek(1).isdigit()):
            self._scan_number()
            return

        # Identifiers / keywords / steps
        if c.isalpha() or c == "_":
            self._scan_identifier()
            return

        # Single-char operators
        if c in self.SINGLE_OPS:
            self._advance()
            tt = self.SINGLE_OPS[c]
            # Track nesting depth for // disambiguation
            if tt in (TokenType.LPAREN, TokenType.LBRACKET):
                self._nesting += 1
            elif tt in (TokenType.RPAREN, TokenType.RBRACKET):
                self._nesting = max(0, self._nesting - 1)
            self.tokens.append(Token(tt, c, start_line, start_col))
            return

        # Unknown
        self._advance()
        self.tokens.append(Token(TokenType.ERROR, c, start_line, start_col))

    def _scan_string(self, quote: str, raw: bool = False):
        """Scan a string literal, with {expr} interpolation for non-raw strings."""
        start_line = self.line
        start_col = self.column
        self._advance()  # opening quote

        # Triple-quoted?
        triple = False
        if self._peek() == quote and self._peek(1) == quote:
            triple = True
            self._advance()
            self._advance()

        # For interpolation we collect parts.
        # If no interpolation is found we emit a normal STRING token.
        parts: list = []  # list of (str_chunk, expr_tokens) pairs
        buf: list = []
        has_interp = False

        while not self._at_end():
            c = self._peek()

            # End of string?
            if triple:
                if c == quote and self._peek(1) == quote and self._peek(2) == quote:
                    self._advance()
                    self._advance()
                    self._advance()
                    break
            else:
                if c == quote:
                    self._advance()
                    break
                if c == "\n":
                    self.tokens.append(
                        Token(TokenType.ERROR, "Unterminated string", start_line, start_col)
                    )
                    return

            # Interpolation: {expr}
            if not raw and c == "{":
                has_interp = True
                text_chunk = "".join(buf)
                buf = []
                self._advance()  # skip {
                # Collect tokens for the expression inside { }
                expr_tokens = self._scan_interp_expr()
                parts.append((text_chunk, expr_tokens))
                continue

            # Escape sequences
            if not raw and c == "\\":
                self._advance()
                if self._at_end():
                    break
                escaped = self._advance()
                escapes = {
                    "n": "\n", "t": "\t", "r": "\r",
                    "\\": "\\", '"': '"', "'": "'",
                    "{": "{", "}": "}",
                }
                buf.append(escapes.get(escaped, escaped))
            else:
                buf.append(self._advance())

        trailing = "".join(buf)

        if not has_interp:
            # Plain string
            self.tokens.append(Token(TokenType.STRING, trailing, start_line, start_col))
        else:
            # Emit interpolation tokens: START, (MID)*, END
            # Each part is (text_before_expr, expr_tokens)
            for i, (text, expr_toks) in enumerate(parts):
                if i == 0:
                    self.tokens.append(
                        Token(TokenType.INTERP_STRING_START, text, start_line, start_col)
                    )
                else:
                    self.tokens.append(
                        Token(TokenType.INTERP_STRING_MID, text, start_line, start_col)
                    )
                self.tokens.extend(expr_toks)
            self.tokens.append(
                Token(TokenType.INTERP_STRING_END, trailing, start_line, start_col)
            )

    def _scan_interp_expr(self) -> List[Token]:
        """Tokenize the expression inside { } of an interpolated string."""
        depth = 1
        expr_tokens = []
        while not self._at_end() and depth > 0:
            # skip whitespace inside interp (but not newlines as tokens)
            while not self._at_end() and self._peek() in " \t":
                self._advance()
            if self._at_end():
                break
            c = self._peek()
            if c == "}":
                depth -= 1
                if depth == 0:
                    self._advance()
                    break
            if c == "{":
                depth += 1

            # Save state and scan one token
            old_tokens = self.tokens
            self.tokens = []
            self._scan_token()
            expr_tokens.extend(self.tokens)
            self.tokens = old_tokens
        return expr_tokens

    def _scan_number(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        if self._peek() == "0":
            self._advance()
            if self._peek() in "xX":
                self._advance()
                while self._peek() in "0123456789abcdefABCDEF_":
                    self._advance()
                val = int(self.source[start_pos : self.pos].replace("_", ""), 16)
                self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))
                return
            if self._peek() in "oO":
                self._advance()
                while self._peek() in "01234567_":
                    self._advance()
                val = int(self.source[start_pos : self.pos].replace("_", ""), 8)
                self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))
                return
            if self._peek() in "bB":
                self._advance()
                while self._peek() in "01_":
                    self._advance()
                val = int(self.source[start_pos : self.pos].replace("_", ""), 2)
                self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))
                return

        while self._peek().isdigit() or self._peek() == "_":
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit() or self._peek() == "_":
                self._advance()

        if self._peek() in "eE":
            is_float = True
            self._advance()
            if self._peek() in "+-":
                self._advance()
            while self._peek().isdigit():
                self._advance()

        num_str = self.source[start_pos : self.pos].replace("_", "")
        val = float(num_str) if is_float else int(num_str)
        self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))

    def _scan_identifier(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[start_pos : self.pos]

        # Step keywords
        if text in self.STEP_KEYWORDS:
            self.tokens.append(
                Token(self.STEP_KEYWORDS[text], text, start_line, start_col)
            )
            return

        # Language keywords
        if text in self.KEYWORDS:
            tt = self.KEYWORDS[text]
            if tt == TokenType.BOOLEAN:
                value = text == "true"
            elif tt == TokenType.NULL:
                value = None
            else:
                value = text
            self.tokens.append(Token(tt, value, start_line, start_col))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, text, start_line, start_col))
