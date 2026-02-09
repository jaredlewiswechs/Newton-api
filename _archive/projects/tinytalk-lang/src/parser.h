/*
═══════════════════════════════════════════════════════════════
PARSER - AST BUILDER FOR TINYTALK
Builds abstract syntax tree from tokens
═══════════════════════════════════════════════════════════════
*/

#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"
#include "tinytalk.h"
#include <stdbool.h>

// AST Node types
typedef enum {
    NODE_BLUEPRINT,
    NODE_FIELD,
    NODE_STATE,
    NODE_WHEN,
    NODE_CONDITION,
    NODE_ACTION_MAKE,
    NODE_ACTION_SET,
    NODE_ACTION_CHANGE,
    NODE_ACTION_CREATE,
    NODE_ACTION_ERASE,
    NODE_BLOCK,
    NODE_MUST,
    NODE_CALC,
    NODE_EXPRESSION,
    NODE_LITERAL,
    NODE_IDENTIFIER,
    NODE_FIELD_ACCESS,
    NODE_BINARY_OP,
    NODE_IF,
    NODE_EACH
} NodeType;

// AST Node structure
typedef struct ASTNode {
    NodeType type;
    int line;
    union {
        struct {
            char* name;
            struct ASTNode** fields;
            size_t field_count;
            struct ASTNode** states;
            size_t state_count;
            struct ASTNode** whens;
            size_t when_count;
        } blueprint;
        
        struct {
            char* name;
            struct ASTNode* initial_value;
        } field;
        
        struct {
            char* name;
        } state;
        
        struct {
            char* name;
            struct ASTNode** params;
            size_t param_count;
            struct ASTNode** conditions;
            size_t condition_count;
            struct ASTNode** actions;
            size_t action_count;
            bool is_finfr;
            char* result_message;
        } when;
        
        struct {
            struct ASTNode* left;
            struct ASTNode* right;
            TokenType op;
        } binary_op;
        
        struct {
            Value value;
        } literal;
        
        struct {
            char* name;
        } identifier;
        
        struct {
            struct ASTNode* object;
            char* field;
        } field_access;
        
        struct {
            struct ASTNode* condition;
            struct ASTNode** actions;
            size_t action_count;
        } block;
        
        struct {
            struct ASTNode* condition;
            char* error_message;
        } must;
        
        struct {
            struct ASTNode* expr;
            TokenType op;
            struct ASTNode* right;
            char* result_var;
        } calc;
        
        struct {
            char* target;
            char* field;
            struct ASTNode* value;
        } action_set;
        
        struct {
            char* target;
            char* new_state;
        } action_make;
        
        struct {
            char* target;
            char* field;
            TokenType op;
            struct ASTNode* value;
        } action_change;
    } as;
} ASTNode;

// Parser structure
typedef struct {
    Lexer* lexer;
    Token current;
    Token previous;
    bool had_error;
    bool panic_mode;
} Parser;

// Parser functions
void parser_init(Parser* parser, Lexer* lexer);
ASTNode* parser_parse(Parser* parser);
void ast_node_free(ASTNode* node);

#endif // PARSER_H
