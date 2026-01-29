/**
 * TinyTalk Parser
 *
 * Converts token stream into an AST (Abstract Syntax Tree).
 *
 * Grammar (EBNF):
 *
 *   program       := blueprint*
 *   blueprint     := 'blueprint' IDENTIFIER NEWLINE body 'end'
 *   body          := (field_decl | law_decl | forge_decl | NEWLINE)*
 *   field_decl    := 'field' FIELD_REF ':' TYPE_NAME
 *   law_decl      := 'law' IDENTIFIER NEWLINE law_body 'end'
 *   law_body      := (when_clause | and_clause | 'fin' | 'finfr')*
 *   when_clause   := 'when' condition
 *   and_clause    := 'and' condition
 *   condition     := expr comparison_op expr | 'request' 'is' SYMBOL
 *   forge_decl    := 'forge' IDENTIFIER '(' params? ')' return_type? NEWLINE forge_body 'end'
 *   return_type   := '->' TYPE_NAME
 *   params        := param (',' param)*
 *   param         := IDENTIFIER ':' TYPE_NAME
 *   forge_body    := (assignment | reply_stmt | local_def | request_set | NEWLINE)*
 *   assignment    := FIELD_REF '=' expr
 *   local_def     := IDENTIFIER '=' expr
 *   request_set   := 'request' '=' SYMBOL
 *   reply_stmt    := 'reply' expr
 *   expr          := term (('+' | '-') term)*
 *   term          := factor (('*' | '/') factor)*
 *   factor        := unary | primary
 *   unary         := '-' factor
 *   primary       := NUMBER | STRING | SYMBOL | FIELD_REF | IDENTIFIER
 *                  | TYPE_NAME '(' expr ')' | '(' expr ')' | func_call
 *   func_call     := IDENTIFIER '(' args? ')'
 *   args          := expr (',' expr)*
 */

const { TokenType, TYPE_NAMES } = require('./tokenizer');

// AST Node Types
const NodeType = {
  PROGRAM: 'Program',
  BLUEPRINT: 'Blueprint',
  FIELD_DECL: 'FieldDecl',
  LAW_DECL: 'LawDecl',
  WHEN_CLAUSE: 'WhenClause',
  AND_CLAUSE: 'AndClause',
  FIN: 'Fin',
  FINFR: 'Finfr',
  FORGE_DECL: 'ForgeDecl',
  PARAM: 'Param',
  ASSIGNMENT: 'Assignment',
  LOCAL_DEF: 'LocalDef',
  REQUEST_SET: 'RequestSet',
  REPLY: 'Reply',
  BINARY_EXPR: 'BinaryExpr',
  UNARY_EXPR: 'UnaryExpr',
  FIELD_REF: 'FieldRef',
  IDENTIFIER: 'Identifier',
  NUMBER_LIT: 'NumberLiteral',
  STRING_LIT: 'StringLiteral',
  SYMBOL_LIT: 'SymbolLiteral',
  TYPE_CONSTRUCT: 'TypeConstruct',
  FUNC_CALL: 'FuncCall',
  GROUP_EXPR: 'GroupExpr',
  COMPARISON: 'Comparison',
  REQUEST_IS: 'RequestIs',
};

class ParseError {
  constructor(message, line, column) {
    this.message = message;
    this.line = line;
    this.column = column;
  }
}

class Parser {
  constructor(tokens) {
    this.tokens = tokens.filter(t => t.type !== TokenType.NEWLINE || true);
    this.pos = 0;
    this.errors = [];
  }

  peek() {
    return this.tokens[this.pos] || { type: TokenType.EOF };
  }

  peekType() {
    return this.peek().type;
  }

  advance() {
    const token = this.tokens[this.pos];
    this.pos++;
    return token;
  }

  expect(type, message) {
    const token = this.peek();
    if (token.type === type) {
      return this.advance();
    }
    this.errors.push(new ParseError(
      message || `Expected ${type} but got ${token.type} ('${token.value}')`,
      token.line, token.column
    ));
    return null;
  }

  /**
   * Expect a name token — either IDENTIFIER or TYPE_NAME.
   * Law names and blueprint names are PascalCase (tokenized as TYPE_NAME).
   */
  expectName(message) {
    const token = this.peek();
    if (token.type === TokenType.IDENTIFIER || token.type === TokenType.TYPE_NAME) {
      return this.advance();
    }
    this.errors.push(new ParseError(
      message || `Expected name but got ${token.type} ('${token.value}')`,
      token.line, token.column
    ));
    return null;
  }

  match(type) {
    if (this.peekType() === type) {
      return this.advance();
    }
    return null;
  }

  skipNewlines() {
    while (this.peekType() === TokenType.NEWLINE) {
      this.advance();
    }
  }

  // ── Program ──────────────────────────────────────────
  parseProgram() {
    const blueprints = [];
    this.skipNewlines();

    while (this.peekType() !== TokenType.EOF) {
      if (this.peekType() === TokenType.BLUEPRINT) {
        blueprints.push(this.parseBlueprint());
      } else {
        // Skip unexpected tokens
        const tok = this.peek();
        this.errors.push(new ParseError(
          `Expected 'blueprint' but got '${tok.value}'`,
          tok.line, tok.column
        ));
        this.advance();
      }
      this.skipNewlines();
    }

    return {
      type: NodeType.PROGRAM,
      blueprints,
      line: 1,
      column: 1,
    };
  }

  // ── Blueprint ────────────────────────────────────────
  parseBlueprint() {
    const kw = this.expect(TokenType.BLUEPRINT, "Expected 'blueprint'");
    const line = kw ? kw.line : 0;
    const column = kw ? kw.column : 0;

    const nameToken = this.expectName("Expected blueprint name");
    const name = nameToken ? nameToken.value : '<missing>';

    this.skipNewlines();

    const fields = [];
    const laws = [];
    const forges = [];

    while (this.peekType() !== TokenType.END && this.peekType() !== TokenType.EOF) {
      this.skipNewlines();
      if (this.peekType() === TokenType.END || this.peekType() === TokenType.EOF) break;

      switch (this.peekType()) {
        case TokenType.FIELD:
          fields.push(this.parseFieldDecl());
          break;
        case TokenType.LAW:
          laws.push(this.parseLawDecl());
          break;
        case TokenType.FORGE:
          forges.push(this.parseForgeDecl());
          break;
        default: {
          const tok = this.peek();
          this.errors.push(new ParseError(
            `Unexpected '${tok.value}' in blueprint body`,
            tok.line, tok.column
          ));
          this.advance();
        }
      }
      this.skipNewlines();
    }

    this.expect(TokenType.END, "Expected 'end' to close blueprint");

    return {
      type: NodeType.BLUEPRINT,
      name,
      fields,
      laws,
      forges,
      line, column,
    };
  }

  // ── Field Declaration ────────────────────────────────
  parseFieldDecl() {
    const kw = this.advance(); // consume 'field'
    const nameToken = this.expect(TokenType.FIELD_REF, "Expected @field_name after 'field'");
    const name = nameToken ? nameToken.value : '<missing>';

    this.expect(TokenType.COLON, "Expected ':' after field name");

    const typeToken = this.expect(TokenType.TYPE_NAME, "Expected type name");
    const fieldType = typeToken ? typeToken.value : '<missing>';

    return {
      type: NodeType.FIELD_DECL,
      name,
      fieldType,
      line: kw.line,
      column: kw.column,
    };
  }

  // ── Law Declaration ──────────────────────────────────
  parseLawDecl() {
    const kw = this.advance(); // consume 'law'
    const nameToken = this.expectName("Expected law name");
    const name = nameToken ? nameToken.value : '<missing>';

    this.skipNewlines();

    const clauses = [];
    let outcome = null;

    while (this.peekType() !== TokenType.END && this.peekType() !== TokenType.EOF) {
      this.skipNewlines();
      if (this.peekType() === TokenType.END || this.peekType() === TokenType.EOF) break;

      if (this.peekType() === TokenType.WHEN) {
        clauses.push(this.parseWhenClause());
      } else if (this.peekType() === TokenType.AND) {
        clauses.push(this.parseAndClause());
      } else if (this.peekType() === TokenType.FIN) {
        outcome = { type: NodeType.FIN, line: this.peek().line, column: this.peek().column };
        this.advance();
      } else if (this.peekType() === TokenType.FINFR) {
        outcome = { type: NodeType.FINFR, line: this.peek().line, column: this.peek().column };
        this.advance();
      } else {
        const tok = this.peek();
        this.errors.push(new ParseError(
          `Unexpected '${tok.value}' in law body`,
          tok.line, tok.column
        ));
        this.advance();
      }
      this.skipNewlines();
    }

    this.expect(TokenType.END, "Expected 'end' to close law");

    return {
      type: NodeType.LAW_DECL,
      name,
      clauses,
      outcome,
      line: kw.line,
      column: kw.column,
    };
  }

  // ── When / And Clauses ───────────────────────────────
  parseWhenClause() {
    const kw = this.advance(); // consume 'when'
    const condition = this.parseCondition();
    return {
      type: NodeType.WHEN_CLAUSE,
      condition,
      line: kw.line,
      column: kw.column,
    };
  }

  parseAndClause() {
    const kw = this.advance(); // consume 'and'
    const condition = this.parseCondition();
    return {
      type: NodeType.AND_CLAUSE,
      condition,
      line: kw.line,
      column: kw.column,
    };
  }

  parseCondition() {
    // Check for "request is :symbol"
    if (this.peekType() === TokenType.REQUEST) {
      const reqToken = this.advance();
      if (this.peekType() === TokenType.IS) {
        this.advance(); // consume 'is'
        const symbol = this.expect(TokenType.SYMBOL, "Expected :symbol after 'request is'");
        return {
          type: NodeType.REQUEST_IS,
          symbol: symbol ? symbol.value : '<missing>',
          line: reqToken.line,
          column: reqToken.column,
        };
      }
      // Put request back conceptually - treat as identifier
      this.pos--;
    }

    // Normal comparison: expr op expr
    const left = this.parseExpr();
    const opToken = this.peek();

    if ([TokenType.LT, TokenType.LT_EQ, TokenType.GT, TokenType.GT_EQ,
         TokenType.EQ_EQ, TokenType.BANG_EQ].includes(opToken.type)) {
      this.advance();
      const right = this.parseExpr();
      return {
        type: NodeType.COMPARISON,
        left,
        operator: opToken.value,
        right,
        line: left.line,
        column: left.column,
      };
    }

    return left;
  }

  // ── Forge Declaration ────────────────────────────────
  parseForgeDecl() {
    const kw = this.advance(); // consume 'forge'
    const nameToken = this.expect(TokenType.IDENTIFIER, "Expected forge name");
    const name = nameToken ? nameToken.value : '<missing>';

    this.expect(TokenType.LPAREN, "Expected '(' after forge name");

    const params = [];
    if (this.peekType() !== TokenType.RPAREN) {
      params.push(this.parseParam());
      while (this.match(TokenType.COMMA)) {
        params.push(this.parseParam());
      }
    }

    this.expect(TokenType.RPAREN, "Expected ')' after parameters");

    // Optional return type: -> TypeName
    let returnType = null;
    if (this.peekType() === TokenType.ARROW) {
      this.advance();
      const typeToken = this.expect(TokenType.TYPE_NAME, "Expected return type after '->'");
      returnType = typeToken ? typeToken.value : null;
    }

    this.skipNewlines();

    const body = [];

    while (this.peekType() !== TokenType.END && this.peekType() !== TokenType.EOF) {
      this.skipNewlines();
      if (this.peekType() === TokenType.END || this.peekType() === TokenType.EOF) break;

      const stmt = this.parseForgeStatement();
      if (stmt) body.push(stmt);
      this.skipNewlines();
    }

    this.expect(TokenType.END, "Expected 'end' to close forge");

    return {
      type: NodeType.FORGE_DECL,
      name,
      params,
      returnType,
      body,
      line: kw.line,
      column: kw.column,
    };
  }

  parseParam() {
    const nameToken = this.expect(TokenType.IDENTIFIER, "Expected parameter name");
    const name = nameToken ? nameToken.value : '<missing>';

    this.expect(TokenType.COLON, "Expected ':' after parameter name");

    const typeToken = this.expect(TokenType.TYPE_NAME, "Expected parameter type");
    const paramType = typeToken ? typeToken.value : '<missing>';

    return {
      type: NodeType.PARAM,
      name,
      paramType,
      line: nameToken ? nameToken.line : 0,
      column: nameToken ? nameToken.column : 0,
    };
  }

  parseForgeStatement() {
    // request = :symbol
    if (this.peekType() === TokenType.REQUEST) {
      const tok = this.advance();
      if (this.peekType() === TokenType.EQ) {
        this.advance();
        const sym = this.expect(TokenType.SYMBOL, "Expected :symbol after 'request ='");
        return {
          type: NodeType.REQUEST_SET,
          symbol: sym ? sym.value : '<missing>',
          line: tok.line,
          column: tok.column,
        };
      }
      this.pos--;
    }

    // reply expr
    if (this.peekType() === TokenType.REPLY) {
      const tok = this.advance();
      const expr = this.parseExpr();
      return {
        type: NodeType.REPLY,
        value: expr,
        line: tok.line,
        column: tok.column,
      };
    }

    // @field = expr (assignment)
    if (this.peekType() === TokenType.FIELD_REF) {
      const fieldToken = this.advance();
      if (this.peekType() === TokenType.EQ) {
        this.advance();
        const expr = this.parseExpr();
        return {
          type: NodeType.ASSIGNMENT,
          field: fieldToken.value,
          value: expr,
          line: fieldToken.line,
          column: fieldToken.column,
        };
      }
      // Not an assignment, put back and parse as expr
      this.pos--;
    }

    // identifier = expr (local def)
    if (this.peekType() === TokenType.IDENTIFIER) {
      const idToken = this.advance();
      if (this.peekType() === TokenType.EQ) {
        this.advance();
        const expr = this.parseExpr();
        return {
          type: NodeType.LOCAL_DEF,
          name: idToken.value,
          value: expr,
          line: idToken.line,
          column: idToken.column,
        };
      }
      // Not a local def, put back
      this.pos--;
    }

    // Fallback: expression statement
    return this.parseExpr();
  }

  // ── Expression Parsing (Pratt-style precedence) ──────
  parseExpr() {
    return this.parseAddSub();
  }

  parseAddSub() {
    let left = this.parseMulDiv();

    while (this.peekType() === TokenType.PLUS || this.peekType() === TokenType.MINUS) {
      const op = this.advance();
      const right = this.parseMulDiv();
      left = {
        type: NodeType.BINARY_EXPR,
        left,
        operator: op.value,
        right,
        line: left.line,
        column: left.column,
      };
    }

    return left;
  }

  parseMulDiv() {
    let left = this.parseUnary();

    while (this.peekType() === TokenType.STAR || this.peekType() === TokenType.SLASH) {
      const op = this.advance();
      const right = this.parseUnary();
      left = {
        type: NodeType.BINARY_EXPR,
        left,
        operator: op.value,
        right,
        line: left.line,
        column: left.column,
      };
    }

    return left;
  }

  parseUnary() {
    if (this.peekType() === TokenType.MINUS) {
      const op = this.advance();
      const operand = this.parseUnary();
      return {
        type: NodeType.UNARY_EXPR,
        operator: '-',
        operand,
        line: op.line,
        column: op.column,
      };
    }
    return this.parsePrimary();
  }

  parsePrimary() {
    const tok = this.peek();

    // Number literal
    if (tok.type === TokenType.NUMBER) {
      this.advance();
      return {
        type: NodeType.NUMBER_LIT,
        value: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // String literal
    if (tok.type === TokenType.STRING) {
      this.advance();
      return {
        type: NodeType.STRING_LIT,
        value: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // Symbol literal
    if (tok.type === TokenType.SYMBOL) {
      this.advance();
      return {
        type: NodeType.SYMBOL_LIT,
        value: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // Field reference
    if (tok.type === TokenType.FIELD_REF) {
      this.advance();
      return {
        type: NodeType.FIELD_REF,
        name: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // Type constructor: TypeName(expr)
    if (tok.type === TokenType.TYPE_NAME) {
      this.advance();
      if (this.peekType() === TokenType.LPAREN) {
        this.advance();
        const arg = this.parseExpr();
        this.expect(TokenType.RPAREN, "Expected ')' after type constructor argument");
        return {
          type: NodeType.TYPE_CONSTRUCT,
          typeName: tok.value,
          argument: arg,
          line: tok.line,
          column: tok.column,
        };
      }
      // Just a type name reference
      return {
        type: NodeType.IDENTIFIER,
        name: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // Identifier or function call
    if (tok.type === TokenType.IDENTIFIER) {
      this.advance();
      if (this.peekType() === TokenType.LPAREN) {
        this.advance();
        const args = [];
        if (this.peekType() !== TokenType.RPAREN) {
          args.push(this.parseExpr());
          while (this.match(TokenType.COMMA)) {
            args.push(this.parseExpr());
          }
        }
        this.expect(TokenType.RPAREN, "Expected ')' after function arguments");
        return {
          type: NodeType.FUNC_CALL,
          name: tok.value,
          args,
          line: tok.line,
          column: tok.column,
        };
      }
      return {
        type: NodeType.IDENTIFIER,
        name: tok.value,
        line: tok.line,
        column: tok.column,
      };
    }

    // Grouped expression
    if (tok.type === TokenType.LPAREN) {
      this.advance();
      const expr = this.parseExpr();
      this.expect(TokenType.RPAREN, "Expected ')'");
      return {
        type: NodeType.GROUP_EXPR,
        expression: expr,
        line: tok.line,
        column: tok.column,
      };
    }

    // Fin / Finfr as expressions
    if (tok.type === TokenType.FIN) {
      this.advance();
      return { type: NodeType.FIN, line: tok.line, column: tok.column };
    }
    if (tok.type === TokenType.FINFR) {
      this.advance();
      return { type: NodeType.FINFR, line: tok.line, column: tok.column };
    }

    // Error recovery
    this.errors.push(new ParseError(
      `Unexpected token '${tok.value}' (${tok.type})`,
      tok.line, tok.column
    ));
    this.advance();
    return {
      type: NodeType.IDENTIFIER,
      name: '<error>',
      line: tok.line,
      column: tok.column,
    };
  }
}

function parse(tokens) {
  const parser = new Parser(tokens);
  const ast = parser.parseProgram();
  return { ast, errors: parser.errors };
}

module.exports = { parse, NodeType, ParseError };
