/*
═══════════════════════════════════════════════════════════════
LEXER IMPLEMENTATION
Tokenizer for tinyTalk keywords, operators, and literals
═══════════════════════════════════════════════════════════════
*/

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include "lexer.h"

void lexer_init(Lexer* lexer, const char* source) {
    lexer->start = source;
    lexer->current = source;
    lexer->line = 1;
}

static bool is_at_end(Lexer* lexer) {
    return *lexer->current == '\0';
}

static char advance(Lexer* lexer) {
    lexer->current++;
    return lexer->current[-1];
}

static char peek(Lexer* lexer) {
    return *lexer->current;
}

static char peek_next(Lexer* lexer) {
    if (is_at_end(lexer)) return '\0';
    return lexer->current[1];
}

static bool match(Lexer* lexer, char expected) {
    if (is_at_end(lexer)) return false;
    if (*lexer->current != expected) return false;
    lexer->current++;
    return true;
}

static void skip_whitespace(Lexer* lexer) {
    for (;;) {
        char c = peek(lexer);
        switch (c) {
            case ' ':
            case '\r':
            case '\t':
                advance(lexer);
                break;
            default:
                return;
        }
    }
}

static Token make_token(Lexer* lexer, TokenType type) {
    Token token;
    token.type = type;
    token.start = lexer->start;
    token.length = (size_t)(lexer->current - lexer->start);
    token.line = lexer->line;
    return token;
}

static Token error_token(Lexer* lexer, const char* message) {
    Token token;
    token.type = TOKEN_ERROR;
    token.start = message;
    token.length = strlen(message);
    token.line = lexer->line;
    return token;
}

static Token string_token(Lexer* lexer) {
    while (peek(lexer) != '"' && !is_at_end(lexer)) {
        if (peek(lexer) == '\n') lexer->line++;
        advance(lexer);
    }
    
    if (is_at_end(lexer)) {
        return error_token(lexer, "Unterminated string");
    }
    
    // Closing quote
    advance(lexer);
    
    Token token = make_token(lexer, TOKEN_STRING);
    // Copy string content without quotes
    size_t len = token.length - 2;
    token.value.string = (char*)malloc(len + 1);
    memcpy(token.value.string, token.start + 1, len);
    token.value.string[len] = '\0';
    return token;
}

static Token number_token(Lexer* lexer) {
    while (isdigit(peek(lexer))) advance(lexer);
    
    // Look for decimal part
    if (peek(lexer) == '.' && isdigit(peek_next(lexer))) {
        advance(lexer);
        while (isdigit(peek(lexer))) advance(lexer);
    }
    
    Token token = make_token(lexer, TOKEN_NUMBER);
    char* end;
    token.value.number = strtod(token.start, &end);
    return token;
}

static TokenType check_keyword(const char* start, size_t length, 
                               const char* rest, TokenType type) {
    if ((size_t)strlen(rest) == length && memcmp(start, rest, length) == 0) {
        return type;
    }
    return TOKEN_IDENTIFIER;
}

static TokenType identifier_type(const char* start, size_t length) {
    // Check for keywords
    switch (start[0]) {
        case 'a':
            if (length > 1) {
                switch (start[1]) {
                    case 'b': return check_keyword(start, length, "above", TOKEN_ABOVE);
                    case 'n': return check_keyword(start, length, "and", TOKEN_AND);
                    case 's': return check_keyword(start, length, "as", TOKEN_AS);
                    case 't': return check_keyword(start, length, "at", TOKEN_AT);
                }
            }
            break;
        case 'b':
            if (length > 1) {
                switch (start[1]) {
                    case 'e': return check_keyword(start, length, "below", TOKEN_BELOW);
                    case 'l':
                        if (length > 2) {
                            switch (start[2]) {
                                case 'o': return check_keyword(start, length, "block", TOKEN_BLOCK);
                                case 'u': return check_keyword(start, length, "blueprint", TOKEN_BLUEPRINT);
                            }
                        }
                        break;
                    case 'y': return check_keyword(start, length, "by", TOKEN_BY);
                }
            }
            break;
        case 'c':
            if (length > 1) {
                switch (start[1]) {
                    case 'a':
                        if (length > 2 && start[2] == 'l') return check_keyword(start, length, "calc", TOKEN_CALC);
                        if (length > 2 && start[2] == 'n') return check_keyword(start, length, "can", TOKEN_CAN_BE);
                        break;
                    case 'h': return check_keyword(start, length, "change", TOKEN_CHANGE);
                    case 'r': return check_keyword(start, length, "create", TOKEN_CREATE);
                }
            }
            break;
        case 'd':
            return check_keyword(start, length, "div", TOKEN_DIV);
        case 'e':
            if (length > 1) {
                switch (start[1]) {
                    case 'a': return check_keyword(start, length, "each", TOKEN_EACH);
                    case 'm': return check_keyword(start, length, "empty", TOKEN_EMPTY);
                    case 'n': return check_keyword(start, length, "end", TOKEN_END);
                    case 'r': return check_keyword(start, length, "erase", TOKEN_ERASE);
                }
            }
            break;
        case 'f':
            if (length > 2) {
                if (start[1] == 'i' && start[2] == 'n') {
                    if (length == 3) return TOKEN_FIN;
                    if (length == 5 && start[3] == 'f' && start[4] == 'r') return TOKEN_FINFR;
                }
            }
            break;
        case 'i':
            if (length > 1) {
                switch (start[1]) {
                    case 'f': return check_keyword(start, length, "if", TOKEN_IF);
                    case 'n': return check_keyword(start, length, "in", TOKEN_IN);
                    case 's': return check_keyword(start, length, "is", TOKEN_IS);
                }
            }
            break;
        case 'm':
            if (length > 1) {
                switch (start[1]) {
                    case 'a': return check_keyword(start, length, "make", TOKEN_MAKE);
                    case 'e': return check_keyword(start, length, "memo", TOKEN_MEMO);
                    case 'i': return check_keyword(start, length, "minus", TOKEN_MINUS);
                    case 'u': return check_keyword(start, length, "must", TOKEN_MUST);
                }
            }
            break;
        case 'n':
            return check_keyword(start, length, "not", TOKEN_NOT);
        case 'o':
            return check_keyword(start, length, "otherwise", TOKEN_OTHERWISE);
        case 'p':
            return check_keyword(start, length, "plus", TOKEN_PLUS);
        case 'r':
            if (length > 2) {
                switch (start[2]) {
                    case 'm': return check_keyword(start, length, "rem", TOKEN_REM);
                    case 'p': return check_keyword(start, length, "reply", TOKEN_REPLY);
                    case 'q': return check_keyword(start, length, "request", TOKEN_REQUEST);
                }
            }
            break;
        case 's':
            if (length > 1) {
                switch (start[1]) {
                    case 'e': return check_keyword(start, length, "set", TOKEN_SET);
                    case 't': return check_keyword(start, length, "starts", TOKEN_STARTS);
                }
            }
            break;
        case 't':
            if (length > 1) {
                switch (start[1]) {
                    case 'i': return check_keyword(start, length, "times", TOKEN_TIMES);
                    case 'o': return check_keyword(start, length, "to", TOKEN_TO);
                }
            }
            break;
        case 'w':
            if (length > 1) {
                switch (start[1]) {
                    case 'h': return check_keyword(start, length, "when", TOKEN_WHEN);
                    case 'i': return check_keyword(start, length, "within", TOKEN_WITHIN);
                    case 'o': return check_keyword(start, length, "world", TOKEN_WORLD);
                }
            }
            break;
    }
    
    return TOKEN_IDENTIFIER;
}

static Token identifier_token(Lexer* lexer) {
    while (isalnum(peek(lexer)) || peek(lexer) == '_') {
        advance(lexer);
    }
    
    TokenType type = identifier_type(lexer->start, (size_t)(lexer->current - lexer->start));
    return make_token(lexer, type);
}

Token lexer_next_token(Lexer* lexer) {
    skip_whitespace(lexer);
    
    lexer->start = lexer->current;
    
    if (is_at_end(lexer)) {
        return make_token(lexer, TOKEN_EOF);
    }
    
    char c = advance(lexer);
    
    if (isalpha(c) || c == '_') {
        return identifier_token(lexer);
    }
    
    if (isdigit(c)) {
        return number_token(lexer);
    }
    
    switch (c) {
        case '\n':
            lexer->line++;
            return make_token(lexer, TOKEN_NEWLINE);
        case '+': return make_token(lexer, TOKEN_PLUS_OP);
        case '&': return make_token(lexer, TOKEN_AMPERSAND);
        case '#': return make_token(lexer, TOKEN_HASH);
        case '.': return make_token(lexer, TOKEN_DOT);
        case ',': return make_token(lexer, TOKEN_COMMA);
        case '(': return make_token(lexer, TOKEN_LPAREN);
        case ')': return make_token(lexer, TOKEN_RPAREN);
        case '"': return string_token(lexer);
        case '/':
            if (match(lexer, '/')) {
                // Comment
                while (peek(lexer) != '\n' && !is_at_end(lexer)) {
                    advance(lexer);
                }
                return make_token(lexer, TOKEN_COMMENT);
            }
            break;
    }
    
    return error_token(lexer, "Unexpected character");
}

const char* token_type_name(TokenType type) {
    switch (type) {
        case TOKEN_BLUEPRINT: return "blueprint";
        case TOKEN_STARTS: return "starts";
        case TOKEN_CAN_BE: return "can be";
        case TOKEN_WHEN: return "when";
        case TOKEN_AND: return "and";
        case TOKEN_IS: return "is";
        case TOKEN_ABOVE: return "above";
        case TOKEN_BELOW: return "below";
        case TOKEN_WITHIN: return "within";
        case TOKEN_MAKE: return "make";
        case TOKEN_SET: return "set";
        case TOKEN_CHANGE: return "change";
        case TOKEN_CREATE: return "create";
        case TOKEN_ERASE: return "erase";
        case TOKEN_EACH: return "each";
        case TOKEN_FIN: return "fin";
        case TOKEN_FINFR: return "finfr";
        case TOKEN_BLOCK: return "block";
        case TOKEN_MUST: return "must";
        case TOKEN_CALC: return "calc";
        case TOKEN_PLUS: return "plus";
        case TOKEN_MINUS: return "minus";
        case TOKEN_TIMES: return "times";
        case TOKEN_DIV: return "div";
        case TOKEN_REM: return "rem";
        case TOKEN_MEMO: return "memo";
        case TOKEN_NUMBER: return "number";
        case TOKEN_STRING: return "string";
        case TOKEN_IDENTIFIER: return "identifier";
        case TOKEN_PLUS_OP: return "+";
        case TOKEN_AMPERSAND: return "&";
        case TOKEN_HASH: return "#";
        case TOKEN_DOT: return ".";
        case TOKEN_COMMA: return ",";
        case TOKEN_LPAREN: return "(";
        case TOKEN_RPAREN: return ")";
        case TOKEN_COMMENT: return "comment";
        case TOKEN_NEWLINE: return "newline";
        case TOKEN_EOF: return "EOF";
        case TOKEN_ERROR: return "error";
        default: return "unknown";
    }
}
