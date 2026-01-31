/*
═══════════════════════════════════════════════════════════════
RUNTIME - EXECUTION ENGINE WITH ACID SEMANTICS
Verified computation with rollback capability
═══════════════════════════════════════════════════════════════
*/

#ifndef RUNTIME_H
#define RUNTIME_H

#include "parser.h"
#include "tinytalk.h"
#include <stdbool.h>

#define MAX_CALL_STACK 256
#define MAX_VARIABLES 256

// Execution bounds (determinism guarantee)
typedef struct {
    size_t max_iterations;
    size_t max_recursion_depth;
    size_t max_operations;
    double timeout_seconds;
} ExecutionBounds;

// Blueprint definition
struct Blueprint {
    char* name;
    ASTNode** fields;
    size_t field_count;
    ASTNode** states;
    size_t state_count;
    ASTNode** whens;
    size_t when_count;
};

// Instance of a blueprint
struct Instance {
    Blueprint* blueprint;
    Value* field_values;
    char* current_state;
    bool in_transaction;
    Value* field_snapshot;  // For ACID rollback
};

// Runtime environment
typedef struct {
    Instance** instances;
    size_t instance_count;
    Blueprint** blueprints;
    size_t blueprint_count;
    Value* variables;
    char** variable_names;
    size_t variable_count;
    ExecutionBounds bounds;
    size_t operation_count;
    size_t recursion_depth;
} Runtime;

// Runtime functions
void runtime_init(Runtime* rt);
void runtime_free(Runtime* rt);

// Blueprint operations
Blueprint* runtime_define_blueprint(Runtime* rt, ASTNode* node);
Instance* runtime_create_instance(Runtime* rt, const char* blueprint_name);

// Execution
Result runtime_execute(Runtime* rt, ASTNode* node);
Result runtime_execute_when(Runtime* rt, Instance* inst, const char* when_name, Value* args, size_t arg_count);

// ACID operations
void runtime_begin_transaction(Instance* inst);
void runtime_commit_transaction(Instance* inst);
void runtime_rollback_transaction(Instance* inst);

// Variable operations
void runtime_set_variable(Runtime* rt, const char* name, Value value);
Value* runtime_get_variable(Runtime* rt, const char* name);

// Evaluation
Value runtime_evaluate_expression(Runtime* rt, ASTNode* expr);
bool runtime_evaluate_condition(Runtime* rt, ASTNode* condition);

#endif // RUNTIME_H
