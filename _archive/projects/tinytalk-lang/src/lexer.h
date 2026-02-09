/*
═══════════════════════════════════════════════════════════════
LEXER - TOKENIZER FOR TINYTALK
Handles all keywords, operators, and literals
═══════════════════════════════════════════════════════════════
*/

#ifndef LEXER_H
#define LEXER_H

#include <stddef.h>
#include <stdbool.h>

// Token types
typedef enum {
    // Keywords
    TOKEN_BLUEPRINT,
    TOKEN_STARTS,
    TOKEN_CAN_BE,
    TOKEN_WHEN,
    TOKEN_AND,
    TOKEN_IS,
    TOKEN_ABOVE,
    TOKEN_BELOW,
    TOKEN_WITHIN,
    TOKEN_MAKE,
    TOKEN_SET,
    TOKEN_CHANGE,
    TOKEN_CREATE,
    TOKEN_ERASE,
    TOKEN_EACH,
    TOKEN_FIN,
    TOKEN_FINFR,
    TOKEN_BLOCK,
    TOKEN_MUST,
    TOKEN_CALC,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_TIMES,
    TOKEN_DIV,
    TOKEN_REM,
    TOKEN_MEMO,
    TOKEN_IF,
    TOKEN_OTHERWISE,
    TOKEN_AS,
    TOKEN_AT,
    TOKEN_TO,
    TOKEN_BY,
    TOKEN_IN,
    TOKEN_NOT,
    TOKEN_EMPTY,
    TOKEN_WORLD,
    TOKEN_REPLY,
    TOKEN_REQUEST,
    TOKEN_END,
    
    // Operators
    TOKEN_PLUS_OP,       // + (natural add)
    TOKEN_MINUS_OP,      // - (subtract/remove)
    TOKEN_AMPERSAND,     // & (fuse)
    TOKEN_HASH,          // # (tag/interpolation)
    TOKEN_DOT,           // . (field access)
    TOKEN_COMMA,         // ,
    TOKEN_LPAREN,        // (
    TOKEN_RPAREN,        // )
    
    // Literals
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_IDENTIFIER,
    
    // Special
    TOKEN_COMMENT,
    TOKEN_NEWLINE,
    TOKEN_EOF,
    TOKEN_ERROR
} TokenType;

// Token structure
typedef struct {
    TokenType type;
    const char* start;
    size_t length;
    int line;
    union {
        double number;
        char* string;
    } value;
} Token;

// Lexer structure
typedef struct {
    const char* start;
    const char* current;
    int line;
} Lexer;

// Lexer functions
void lexer_init(Lexer* lexer, const char* source);
Token lexer_next_token(Lexer* lexer);
const char* token_type_name(TokenType type);

#endif // LEXER_H
