/*
═══════════════════════════════════════════════════════════════
PARSER IMPLEMENTATION
Builds AST from token stream
═══════════════════════════════════════════════════════════════
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.h"

static void error_at(Parser* parser, Token* token, const char* message) {
    if (parser->panic_mode) return;
    parser->panic_mode = true;
    parser->had_error = true;
    
    fprintf(stderr, "[line %d] Error", token->line);
    
    if (token->type == TOKEN_EOF) {
        fprintf(stderr, " at end");
    } else if (token->type == TOKEN_ERROR) {
        // Nothing
    } else {
        fprintf(stderr, " at '%.*s'", (int)token->length, token->start);
    }
    
    fprintf(stderr, ": %s\n", message);
}

static void error(Parser* parser, const char* message) {
    error_at(parser, &parser->previous, message);
}

static void advance(Parser* parser) {
    parser->previous = parser->current;
    
    for (;;) {
        parser->current = lexer_next_token(parser->lexer);
        if (parser->current.type != TOKEN_ERROR) break;
        
        error_at(parser, &parser->current, parser->current.start);
    }
}

static void consume(Parser* parser, TokenType type, const char* message) {
    if (parser->current.type == type) {
        advance(parser);
        return;
    }
    
    error_at(parser, &parser->current, message);
}

static bool check(Parser* parser, TokenType type) {
    return parser->current.type == type;
}

static bool match(Parser* parser, TokenType type) {
    if (!check(parser, type)) return false;
    advance(parser);
    return true;
}

static void skip_newlines(Parser* parser) {
    while (match(parser, TOKEN_NEWLINE) || match(parser, TOKEN_COMMENT)) {
        // Skip
    }
}

static ASTNode* alloc_node(NodeType type, int line) {
    ASTNode* node = (ASTNode*)calloc(1, sizeof(ASTNode));
    node->type = type;
    node->line = line;
    return node;
}

static char* copy_token_string(Token* token) {
    char* str = (char*)malloc(token->length + 1);
    memcpy(str, token->start, token->length);
    str[token->length] = '\0';
    return str;
}

// Forward declarations
static ASTNode* parse_expression(Parser* parser);
static ASTNode* parse_primary(Parser* parser);

static ASTNode* parse_primary(Parser* parser) {
    if (match(parser, TOKEN_NUMBER)) {
        ASTNode* node = alloc_node(NODE_LITERAL, parser->previous.line);
        node->as.literal.value = value_number(parser->previous.value.number);
        return node;
    }
    
    if (match(parser, TOKEN_STRING)) {
        ASTNode* node = alloc_node(NODE_LITERAL, parser->previous.line);
        node->as.literal.value = value_string(parser->previous.value.string);
        return node;
    }
    
    if (match(parser, TOKEN_IDENTIFIER)) {
        char* name = copy_token_string(&parser->previous);
        
        // Check for field access (e.g., player.cash)
        if (match(parser, TOKEN_DOT)) {
            consume(parser, TOKEN_IDENTIFIER, "Expected field name after '.'");
            ASTNode* node = alloc_node(NODE_FIELD_ACCESS, parser->previous.line);
            node->as.field_access.object = alloc_node(NODE_IDENTIFIER, parser->previous.line);
            node->as.field_access.object->as.identifier.name = name;
            node->as.field_access.field = copy_token_string(&parser->previous);
            return node;
        }
        
        ASTNode* node = alloc_node(NODE_IDENTIFIER, parser->previous.line);
        node->as.identifier.name = name;
        return node;
    }
    
    if (match(parser, TOKEN_LPAREN)) {
        ASTNode* expr = parse_expression(parser);
        consume(parser, TOKEN_RPAREN, "Expected ')' after expression");
        return expr;
    }
    
    error(parser, "Expected expression");
    return NULL;
}

static ASTNode* parse_expression(Parser* parser) {
    ASTNode* left = parse_primary(parser);
    
    // Handle binary operators
    while (match(parser, TOKEN_PLUS_OP) || match(parser, TOKEN_AMPERSAND) ||
           match(parser, TOKEN_HASH) || match(parser, TOKEN_PLUS) ||
           match(parser, TOKEN_MINUS) || match(parser, TOKEN_TIMES) ||
           match(parser, TOKEN_DIV)) {
        TokenType op = parser->previous.type;
        ASTNode* right = parse_primary(parser);
        
        ASTNode* binary = alloc_node(NODE_BINARY_OP, parser->previous.line);
        binary->as.binary_op.left = left;
        binary->as.binary_op.right = right;
        binary->as.binary_op.op = op;
        left = binary;
    }
    
    return left;
}

static ASTNode* parse_field_declaration(Parser* parser) {
    consume(parser, TOKEN_IDENTIFIER, "Expected field name");
    char* field_name = copy_token_string(&parser->previous);
    
    // Support both "at" and "as" for field initialization
    if (!match(parser, TOKEN_AT) && !match(parser, TOKEN_AS)) {
        error(parser, "Expected 'at' or 'as' after field name");
        // Create a default node to avoid NULL
        ASTNode* node = alloc_node(NODE_FIELD, parser->previous.line);
        node->as.field.name = field_name;
        node->as.field.initial_value = alloc_node(NODE_LITERAL, parser->previous.line);
        node->as.field.initial_value->as.literal.value = value_null();
        return node;
    }
    
    // Handle "as empty" special case
    ASTNode* initial_value;
    if (match(parser, TOKEN_EMPTY)) {
        initial_value = alloc_node(NODE_LITERAL, parser->previous.line);
        initial_value->as.literal.value = value_null();
    } else {
        initial_value = parse_expression(parser);
    }
    
    ASTNode* node = alloc_node(NODE_FIELD, parser->previous.line);
    node->as.field.name = field_name;
    node->as.field.initial_value = initial_value;
    
    return node;
}

static ASTNode* parse_state_declaration(Parser* parser) {
    consume(parser, TOKEN_IDENTIFIER, "Expected state name");
    char* state_name = copy_token_string(&parser->previous);
    
    ASTNode* node = alloc_node(NODE_STATE, parser->previous.line);
    node->as.state.name = state_name;
    
    return node;
}

static ASTNode* parse_when_clause(Parser* parser) {
    int line = parser->previous.line;
    
    consume(parser, TOKEN_IDENTIFIER, "Expected when clause name");
    char* when_name = copy_token_string(&parser->previous);
    
    ASTNode* node = alloc_node(NODE_WHEN, line);
    node->as.when.name = when_name;
    node->as.when.param_count = 0;
    node->as.when.condition_count = 0;
    node->as.when.action_count = 0;
    
    // Parse parameters if present
    if (match(parser, TOKEN_LPAREN)) {
        // Simplified: skip parameters for now
        while (!check(parser, TOKEN_RPAREN) && !check(parser, TOKEN_EOF)) {
            advance(parser);
        }
        consume(parser, TOKEN_RPAREN, "Expected ')' after parameters");
    }
    
    skip_newlines(parser);
    
    // Parse actions until fin or finfr
    ASTNode** actions = (ASTNode**)malloc(sizeof(ASTNode*) * 64);
    size_t action_count = 0;
    
    while (!check(parser, TOKEN_FIN) && !check(parser, TOKEN_FINFR) && !check(parser, TOKEN_EOF)) {
        skip_newlines(parser);
        
        if (match(parser, TOKEN_SET)) {
            ASTNode* action = alloc_node(NODE_ACTION_SET, parser->previous.line);
            
            consume(parser, TOKEN_IDENTIFIER, "Expected target");
            char* target = copy_token_string(&parser->previous);
            
            if (match(parser, TOKEN_DOT)) {
                consume(parser, TOKEN_IDENTIFIER, "Expected field name");
                action->as.action_set.target = target;
                action->as.action_set.field = copy_token_string(&parser->previous);
            } else {
                action->as.action_set.target = NULL;
                action->as.action_set.field = target;
            }
            
            consume(parser, TOKEN_TO, "Expected 'to' after field");
            action->as.action_set.value = parse_expression(parser);
            
            actions[action_count++] = action;
        } else if (match(parser, TOKEN_MAKE)) {
            ASTNode* action = alloc_node(NODE_ACTION_MAKE, parser->previous.line);
            
            consume(parser, TOKEN_IDENTIFIER, "Expected target");
            action->as.action_make.target = copy_token_string(&parser->previous);
            
            consume(parser, TOKEN_IDENTIFIER, "Expected state name");
            action->as.action_make.new_state = copy_token_string(&parser->previous);
            
            actions[action_count++] = action;
        } else if (match(parser, TOKEN_CALC)) {
            // Simplified calc parsing
            parse_expression(parser);
            while (!check(parser, TOKEN_NEWLINE) && !check(parser, TOKEN_EOF)) {
                advance(parser);
            }
        } else if (match(parser, TOKEN_BLOCK) || match(parser, TOKEN_MUST) ||
                   match(parser, TOKEN_IF) || match(parser, TOKEN_MEMO)) {
            // Skip these for simplified parser
            while (!check(parser, TOKEN_NEWLINE) && !check(parser, TOKEN_EOF)) {
                advance(parser);
            }
        } else {
            advance(parser);
        }
        
        skip_newlines(parser);
    }
    
    node->as.when.actions = actions;
    node->as.when.action_count = action_count;
    
    // Check for fin or finfr
    if (match(parser, TOKEN_FINFR)) {
        node->as.when.is_finfr = true;
        if (match(parser, TOKEN_STRING)) {
            node->as.when.result_message = parser->previous.value.string;
        }
    } else if (match(parser, TOKEN_FIN)) {
        node->as.when.is_finfr = false;
    }
    
    return node;
}

static ASTNode* parse_blueprint(Parser* parser) {
    int line = parser->previous.line;
    
    consume(parser, TOKEN_IDENTIFIER, "Expected blueprint name");
    char* name = copy_token_string(&parser->previous);
    
    ASTNode* node = alloc_node(NODE_BLUEPRINT, line);
    node->as.blueprint.name = name;
    
    // Parse fields, states, and when clauses
    ASTNode** fields = (ASTNode**)malloc(sizeof(ASTNode*) * MAX_FIELDS);
    ASTNode** states = (ASTNode**)malloc(sizeof(ASTNode*) * MAX_STATES);
    ASTNode** whens = (ASTNode**)malloc(sizeof(ASTNode*) * MAX_WHENS);
    
    size_t field_count = 0;
    size_t state_count = 0;
    size_t when_count = 0;
    
    skip_newlines(parser);
    
    while (!check(parser, TOKEN_EOF) && !check(parser, TOKEN_BLUEPRINT)) {
        skip_newlines(parser);
        
        if (match(parser, TOKEN_STARTS)) {
            fields[field_count++] = parse_field_declaration(parser);
        } else if (match(parser, TOKEN_CAN_BE)) {
            states[state_count++] = parse_state_declaration(parser);
        } else if (match(parser, TOKEN_WHEN)) {
            whens[when_count++] = parse_when_clause(parser);
        } else if (match(parser, TOKEN_END)) {
            break;
        } else {
            advance(parser);
        }
        
        skip_newlines(parser);
    }
    
    node->as.blueprint.fields = fields;
    node->as.blueprint.field_count = field_count;
    node->as.blueprint.states = states;
    node->as.blueprint.state_count = state_count;
    node->as.blueprint.whens = whens;
    node->as.blueprint.when_count = when_count;
    
    return node;
}

void parser_init(Parser* parser, Lexer* lexer) {
    parser->lexer = lexer;
    parser->had_error = false;
    parser->panic_mode = false;
    advance(parser);
}

ASTNode* parser_parse(Parser* parser) {
    skip_newlines(parser);
    
    if (match(parser, TOKEN_BLUEPRINT)) {
        return parse_blueprint(parser);
    }
    
    error(parser, "Expected blueprint declaration");
    return NULL;
}

void ast_node_free(ASTNode* node) {
    if (!node) return;
    
    switch (node->type) {
        case NODE_BLUEPRINT:
            free(node->as.blueprint.name);
            for (size_t i = 0; i < node->as.blueprint.field_count; i++) {
                ast_node_free(node->as.blueprint.fields[i]);
            }
            free(node->as.blueprint.fields);
            for (size_t i = 0; i < node->as.blueprint.state_count; i++) {
                ast_node_free(node->as.blueprint.states[i]);
            }
            free(node->as.blueprint.states);
            for (size_t i = 0; i < node->as.blueprint.when_count; i++) {
                ast_node_free(node->as.blueprint.whens[i]);
            }
            free(node->as.blueprint.whens);
            break;
            
        case NODE_FIELD:
            free(node->as.field.name);
            ast_node_free(node->as.field.initial_value);
            break;
            
        case NODE_STATE:
            free(node->as.state.name);
            break;
            
        case NODE_WHEN:
            free(node->as.when.name);
            for (size_t i = 0; i < node->as.when.action_count; i++) {
                ast_node_free(node->as.when.actions[i]);
            }
            free(node->as.when.actions);
            break;
            
        case NODE_BINARY_OP:
            ast_node_free(node->as.binary_op.left);
            ast_node_free(node->as.binary_op.right);
            break;
            
        case NODE_IDENTIFIER:
            free(node->as.identifier.name);
            break;
            
        case NODE_FIELD_ACCESS:
            ast_node_free(node->as.field_access.object);
            free(node->as.field_access.field);
            break;
            
        case NODE_ACTION_SET:
            free(node->as.action_set.target);
            free(node->as.action_set.field);
            ast_node_free(node->as.action_set.value);
            break;
            
        case NODE_ACTION_MAKE:
            free(node->as.action_make.target);
            free(node->as.action_make.new_state);
            break;
            
        case NODE_LITERAL:
            value_free(&node->as.literal.value);
            break;
            
        default:
            break;
    }
    
    free(node);
}
