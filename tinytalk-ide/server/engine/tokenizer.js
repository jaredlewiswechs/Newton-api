/**
 * TinyTalk Tokenizer
 *
 * Converts source text into a stream of tokens for the parser.
 * Frozen lexicon: blueprint, field, law, when, and, fin, finfr, forge, reply, end, ground
 */

const TokenType = {
  // Keywords (frozen lexicon)
  BLUEPRINT: 'BLUEPRINT',
  FIELD: 'FIELD',
  LAW: 'LAW',
  WHEN: 'WHEN',
  AND: 'AND',
  FIN: 'FIN',
  FINFR: 'FINFR',
  FORGE: 'FORGE',
  REPLY: 'REPLY',
  END: 'END',
  GROUND: 'GROUND',

  // Contextual keywords
  IS: 'IS',
  REQUEST: 'REQUEST',

  // Literals
  IDENTIFIER: 'IDENTIFIER',
  FIELD_REF: 'FIELD_REF',       // @name
  NUMBER: 'NUMBER',
  STRING: 'STRING',
  SYMBOL: 'SYMBOL',             // :name

  // Type constructors
  TYPE_NAME: 'TYPE_NAME',       // Count, Real, Money, etc.

  // Operators
  PLUS: 'PLUS',
  MINUS: 'MINUS',
  STAR: 'STAR',
  SLASH: 'SLASH',
  EQ: 'EQ',
  EQ_EQ: 'EQ_EQ',
  BANG_EQ: 'BANG_EQ',
  LT: 'LT',
  LT_EQ: 'LT_EQ',
  GT: 'GT',
  GT_EQ: 'GT_EQ',
  ARROW: 'ARROW',               // ->

  // Delimiters
  LPAREN: 'LPAREN',
  RPAREN: 'RPAREN',
  COMMA: 'COMMA',
  COLON: 'COLON',
  DOT: 'DOT',
  HASH: 'HASH',

  // Special
  NEWLINE: 'NEWLINE',
  EOF: 'EOF',
};

const KEYWORDS = {
  'blueprint': TokenType.BLUEPRINT,
  'field': TokenType.FIELD,
  'law': TokenType.LAW,
  'when': TokenType.WHEN,
  'and': TokenType.AND,
  'fin': TokenType.FIN,
  'finfr': TokenType.FINFR,
  'forge': TokenType.FORGE,
  'reply': TokenType.REPLY,
  'end': TokenType.END,
  'ground': TokenType.GROUND,
  'is': TokenType.IS,
  'request': TokenType.REQUEST,
};

// Known type names (extensible)
const TYPE_NAMES = new Set([
  'Count', 'Real', 'Money', 'Celsius', 'PSI',
  'Meters', 'Seconds', 'Boolean', 'String', 'Percent',
  'Rate', 'Ratio', 'Vector', 'Point',
]);

class Token {
  constructor(type, value, line, column) {
    this.type = type;
    this.value = value;
    this.line = line;
    this.column = column;
  }
}

class TokenizerError {
  constructor(message, line, column) {
    this.message = message;
    this.line = line;
    this.column = column;
  }
}

class Tokenizer {
  constructor(source) {
    this.source = source;
    this.pos = 0;
    this.line = 1;
    this.column = 1;
    this.tokens = [];
    this.errors = [];
  }

  peek() {
    if (this.pos >= this.source.length) return '\0';
    return this.source[this.pos];
  }

  peekNext() {
    if (this.pos + 1 >= this.source.length) return '\0';
    return this.source[this.pos + 1];
  }

  advance() {
    const ch = this.source[this.pos];
    this.pos++;
    if (ch === '\n') {
      this.line++;
      this.column = 1;
    } else {
      this.column++;
    }
    return ch;
  }

  skipWhitespace() {
    while (this.pos < this.source.length) {
      const ch = this.peek();
      if (ch === ' ' || ch === '\t' || ch === '\r') {
        this.advance();
      } else {
        break;
      }
    }
  }

  skipComment() {
    // Skip from # to end of line
    while (this.pos < this.source.length && this.peek() !== '\n') {
      this.advance();
    }
  }

  readString() {
    const startLine = this.line;
    const startCol = this.column;
    const quote = this.advance(); // consume opening quote
    let value = '';

    while (this.pos < this.source.length && this.peek() !== quote) {
      if (this.peek() === '\\') {
        this.advance();
        const escaped = this.advance();
        switch (escaped) {
          case 'n': value += '\n'; break;
          case 't': value += '\t'; break;
          case '\\': value += '\\'; break;
          case '"': value += '"'; break;
          case "'": value += "'"; break;
          default: value += escaped;
        }
      } else {
        value += this.advance();
      }
    }

    if (this.pos >= this.source.length) {
      this.errors.push(new TokenizerError('Unterminated string', startLine, startCol));
    } else {
      this.advance(); // consume closing quote
    }

    return new Token(TokenType.STRING, value, startLine, startCol);
  }

  readNumber() {
    const startLine = this.line;
    const startCol = this.column;
    let value = '';
    let hasDecimal = false;

    while (this.pos < this.source.length) {
      const ch = this.peek();
      if (ch >= '0' && ch <= '9') {
        value += this.advance();
      } else if (ch === '.' && !hasDecimal) {
        // Check it's not a method call
        if (this.peekNext() >= '0' && this.peekNext() <= '9') {
          hasDecimal = true;
          value += this.advance();
        } else {
          break;
        }
      } else if (ch === '_') {
        // Allow numeric separators like 1_000_000
        this.advance();
      } else {
        break;
      }
    }

    return new Token(TokenType.NUMBER, parseFloat(value), startLine, startCol);
  }

  readIdentifier() {
    const startLine = this.line;
    const startCol = this.column;
    let value = '';

    while (this.pos < this.source.length) {
      const ch = this.peek();
      if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
          (ch >= '0' && ch <= '9') || ch === '_') {
        value += this.advance();
      } else {
        break;
      }
    }

    // Check if it's a keyword
    const lower = value.toLowerCase();
    if (KEYWORDS[lower]) {
      return new Token(KEYWORDS[lower], lower, startLine, startCol);
    }

    // Check if it's a type name (starts with uppercase)
    if (value[0] >= 'A' && value[0] <= 'Z') {
      return new Token(TokenType.TYPE_NAME, value, startLine, startCol);
    }

    return new Token(TokenType.IDENTIFIER, value, startLine, startCol);
  }

  readFieldRef() {
    const startLine = this.line;
    const startCol = this.column;
    this.advance(); // consume @
    let name = '';

    while (this.pos < this.source.length) {
      const ch = this.peek();
      if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
          (ch >= '0' && ch <= '9') || ch === '_') {
        name += this.advance();
      } else {
        break;
      }
    }

    if (name.length === 0) {
      this.errors.push(new TokenizerError('Expected field name after @', startLine, startCol));
      return null;
    }

    return new Token(TokenType.FIELD_REF, name, startLine, startCol);
  }

  readSymbol() {
    const startLine = this.line;
    const startCol = this.column;
    this.advance(); // consume :
    let name = '';

    while (this.pos < this.source.length) {
      const ch = this.peek();
      if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
          (ch >= '0' && ch <= '9') || ch === '_') {
        name += this.advance();
      } else {
        break;
      }
    }

    if (name.length === 0) {
      // It's just a colon, not a symbol
      return new Token(TokenType.COLON, ':', startLine, startCol);
    }

    return new Token(TokenType.SYMBOL, name, startLine, startCol);
  }

  tokenize() {
    while (this.pos < this.source.length) {
      this.skipWhitespace();
      if (this.pos >= this.source.length) break;

      const ch = this.peek();
      const startLine = this.line;
      const startCol = this.column;

      // Newlines are significant (statement separators)
      if (ch === '\n') {
        this.advance();
        // Only add newline if last token wasn't already a newline
        const lastToken = this.tokens[this.tokens.length - 1];
        if (!lastToken || lastToken.type !== TokenType.NEWLINE) {
          this.tokens.push(new Token(TokenType.NEWLINE, '\n', startLine, startCol));
        }
        continue;
      }

      // Comments
      if (ch === '#') {
        this.skipComment();
        continue;
      }

      // Strings
      if (ch === '"' || ch === "'") {
        this.tokens.push(this.readString());
        continue;
      }

      // Numbers
      if (ch >= '0' && ch <= '9') {
        this.tokens.push(this.readNumber());
        continue;
      }

      // Field references (@name)
      if (ch === '@') {
        const token = this.readFieldRef();
        if (token) this.tokens.push(token);
        continue;
      }

      // Symbols (:name) or just colon
      if (ch === ':') {
        this.tokens.push(this.readSymbol());
        continue;
      }

      // Identifiers / keywords
      if ((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || ch === '_') {
        this.tokens.push(this.readIdentifier());
        continue;
      }

      // Operators and delimiters
      switch (ch) {
        case '+': this.advance(); this.tokens.push(new Token(TokenType.PLUS, '+', startLine, startCol)); break;
        case '*': this.advance(); this.tokens.push(new Token(TokenType.STAR, '*', startLine, startCol)); break;
        case '/': this.advance(); this.tokens.push(new Token(TokenType.SLASH, '/', startLine, startCol)); break;
        case '(': this.advance(); this.tokens.push(new Token(TokenType.LPAREN, '(', startLine, startCol)); break;
        case ')': this.advance(); this.tokens.push(new Token(TokenType.RPAREN, ')', startLine, startCol)); break;
        case ',': this.advance(); this.tokens.push(new Token(TokenType.COMMA, ',', startLine, startCol)); break;
        case '.': this.advance(); this.tokens.push(new Token(TokenType.DOT, '.', startLine, startCol)); break;

        case '-':
          this.advance();
          if (this.peek() === '>') {
            this.advance();
            this.tokens.push(new Token(TokenType.ARROW, '->', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.MINUS, '-', startLine, startCol));
          }
          break;

        case '=':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.EQ_EQ, '==', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.EQ, '=', startLine, startCol));
          }
          break;

        case '!':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.BANG_EQ, '!=', startLine, startCol));
          } else {
            this.errors.push(new TokenizerError(`Unexpected character: !`, startLine, startCol));
          }
          break;

        case '<':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.LT_EQ, '<=', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.LT, '<', startLine, startCol));
          }
          break;

        case '>':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.GT_EQ, '>=', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.GT, '>', startLine, startCol));
          }
          break;

        default:
          this.errors.push(new TokenizerError(`Unexpected character: ${ch}`, startLine, startCol));
          this.advance();
      }
    }

    this.tokens.push(new Token(TokenType.EOF, null, this.line, this.column));
    return { tokens: this.tokens, errors: this.errors };
  }
}

function tokenize(source) {
  const t = new Tokenizer(source);
  return t.tokenize();
}

module.exports = { tokenize, TokenType, Token, TokenizerError, TYPE_NAMES };
