/*
═══════════════════════════════════════════════════════════════
RUNTIME IMPLEMENTATION
Execution engine with ACID semantics
═══════════════════════════════════════════════════════════════
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "runtime.h"

// Value operations
Value value_number(double n) {
    Value v;
    v.type = TYPE_NUMBER;
    v.as.number = n;
    return v;
}

Value value_string(const char* s) {
    Value v;
    v.type = TYPE_STRING;
    v.as.string = strdup(s);
    return v;
}

Value value_boolean(bool b) {
    Value v;
    v.type = TYPE_BOOLEAN;
    v.as.boolean = b;
    return v;
}

Value value_null(void) {
    Value v;
    v.type = TYPE_NULL;
    return v;
}

void value_free(Value* v) {
    if (v->type == TYPE_STRING && v->as.string) {
        free(v->as.string);
        v->as.string = NULL;
    } else if (v->type == TYPE_ARRAY && v->as.array.items) {
        for (size_t i = 0; i < v->as.array.count; i++) {
            value_free(&v->as.array.items[i]);
        }
        free(v->as.array.items);
        v->as.array.items = NULL;
    }
}

Value value_copy(const Value* v) {
    Value copy;
    copy.type = v->type;
    
    switch (v->type) {
        case TYPE_NUMBER:
            copy.as.number = v->as.number;
            break;
        case TYPE_STRING:
            copy.as.string = strdup(v->as.string);
            break;
        case TYPE_BOOLEAN:
            copy.as.boolean = v->as.boolean;
            break;
        case TYPE_NULL:
            break;
        default:
            copy = value_null();
    }
    
    return copy;
}

void runtime_init(Runtime* rt) {
    rt->instances = NULL;
    rt->instance_count = 0;
    rt->blueprints = (Blueprint**)calloc(64, sizeof(Blueprint*));
    rt->blueprint_count = 0;
    rt->variables = (Value*)calloc(MAX_VARIABLES, sizeof(Value));
    rt->variable_names = (char**)calloc(MAX_VARIABLES, sizeof(char*));
    rt->variable_count = 0;
    
    // Set default execution bounds
    rt->bounds.max_iterations = 10000;
    rt->bounds.max_recursion_depth = 100;
    rt->bounds.max_operations = 1000000;
    rt->bounds.timeout_seconds = 30.0;
    rt->operation_count = 0;
    rt->recursion_depth = 0;
}

void runtime_free(Runtime* rt) {
    // Free blueprints
    for (size_t i = 0; i < rt->blueprint_count; i++) {
        if (rt->blueprints[i]) {
            free(rt->blueprints[i]->name);
            free(rt->blueprints[i]);
        }
    }
    free(rt->blueprints);
    
    // Free variables
    for (size_t i = 0; i < rt->variable_count; i++) {
        value_free(&rt->variables[i]);
        free(rt->variable_names[i]);
    }
    free(rt->variables);
    free(rt->variable_names);
    
    // Free instances
    if (rt->instances) {
        for (size_t i = 0; i < rt->instance_count; i++) {
            if (rt->instances[i]) {
                if (rt->instances[i]->field_values) {
                    for (size_t j = 0; j < rt->instances[i]->blueprint->field_count; j++) {
                        value_free(&rt->instances[i]->field_values[j]);
                    }
                    free(rt->instances[i]->field_values);
                }
                free(rt->instances[i]->current_state);
                free(rt->instances[i]);
            }
        }
        free(rt->instances);
    }
}

Blueprint* runtime_define_blueprint(Runtime* rt, ASTNode* node) {
    if (node->type != NODE_BLUEPRINT) return NULL;
    
    Blueprint* bp = (Blueprint*)calloc(1, sizeof(Blueprint));
    bp->name = strdup(node->as.blueprint.name);
    bp->fields = node->as.blueprint.fields;
    bp->field_count = node->as.blueprint.field_count;
    bp->states = node->as.blueprint.states;
    bp->state_count = node->as.blueprint.state_count;
    bp->whens = node->as.blueprint.whens;
    bp->when_count = node->as.blueprint.when_count;
    
    rt->blueprints[rt->blueprint_count++] = bp;
    
    return bp;
}

Instance* runtime_create_instance(Runtime* rt, const char* blueprint_name) {
    Blueprint* bp = NULL;
    for (size_t i = 0; i < rt->blueprint_count; i++) {
        if (strcmp(rt->blueprints[i]->name, blueprint_name) == 0) {
            bp = rt->blueprints[i];
            break;
        }
    }
    
    if (!bp) return NULL;
    
    Instance* inst = (Instance*)calloc(1, sizeof(Instance));
    inst->blueprint = bp;
    inst->field_values = (Value*)calloc(bp->field_count, sizeof(Value));
    inst->current_state = NULL;
    inst->in_transaction = false;
    inst->field_snapshot = NULL;
    
    // Initialize fields with default values
    for (size_t i = 0; i < bp->field_count; i++) {
        inst->field_values[i] = runtime_evaluate_expression(rt, bp->fields[i]->as.field.initial_value);
    }
    
    // Add to runtime
    if (!rt->instances) {
        rt->instances = (Instance**)calloc(64, sizeof(Instance*));
    }
    rt->instances[rt->instance_count++] = inst;
    
    return inst;
}

void runtime_begin_transaction(Instance* inst) {
    inst->in_transaction = true;
    inst->field_snapshot = (Value*)calloc(inst->blueprint->field_count, sizeof(Value));
    
    for (size_t i = 0; i < inst->blueprint->field_count; i++) {
        inst->field_snapshot[i] = value_copy(&inst->field_values[i]);
    }
}

void runtime_commit_transaction(Instance* inst) {
    inst->in_transaction = false;
    
    if (inst->field_snapshot) {
        for (size_t i = 0; i < inst->blueprint->field_count; i++) {
            value_free(&inst->field_snapshot[i]);
        }
        free(inst->field_snapshot);
        inst->field_snapshot = NULL;
    }
}

void runtime_rollback_transaction(Instance* inst) {
    if (!inst->in_transaction || !inst->field_snapshot) return;
    
    for (size_t i = 0; i < inst->blueprint->field_count; i++) {
        value_free(&inst->field_values[i]);
        inst->field_values[i] = value_copy(&inst->field_snapshot[i]);
        value_free(&inst->field_snapshot[i]);
    }
    
    free(inst->field_snapshot);
    inst->field_snapshot = NULL;
    inst->in_transaction = false;
}

void runtime_set_variable(Runtime* rt, const char* name, Value value) {
    // Check if variable exists
    for (size_t i = 0; i < rt->variable_count; i++) {
        if (strcmp(rt->variable_names[i], name) == 0) {
            value_free(&rt->variables[i]);
            rt->variables[i] = value;
            return;
        }
    }
    
    // Add new variable
    rt->variable_names[rt->variable_count] = strdup(name);
    rt->variables[rt->variable_count] = value;
    rt->variable_count++;
}

Value* runtime_get_variable(Runtime* rt, const char* name) {
    for (size_t i = 0; i < rt->variable_count; i++) {
        if (strcmp(rt->variable_names[i], name) == 0) {
            return &rt->variables[i];
        }
    }
    return NULL;
}

Value runtime_evaluate_expression(Runtime* rt, ASTNode* expr) {
    if (!expr) return value_null();
    
    rt->operation_count++;
    if (rt->operation_count > rt->bounds.max_operations) {
        fprintf(stderr, "Error: Maximum operations exceeded\n");
        return value_null();
    }
    
    switch (expr->type) {
        case NODE_LITERAL:
            return value_copy(&expr->as.literal.value);
            
        case NODE_IDENTIFIER: {
            Value* var = runtime_get_variable(rt, expr->as.identifier.name);
            if (var) return value_copy(var);
            return value_null();
        }
        
        case NODE_BINARY_OP: {
            Value left = runtime_evaluate_expression(rt, expr->as.binary_op.left);
            Value right = runtime_evaluate_expression(rt, expr->as.binary_op.right);
            
            // Smart operators
            if (expr->as.binary_op.op == TOKEN_PLUS_OP || expr->as.binary_op.op == TOKEN_PLUS) {
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    Value result = value_number(left.as.number + right.as.number);
                    value_free(&left);
                    value_free(&right);
                    return result;
                } else if (left.type == TYPE_STRING || right.type == TYPE_STRING) {
                    // Join with space
                    char buffer[1024];
                    snprintf(buffer, sizeof(buffer), "%s %s",
                            left.type == TYPE_STRING ? left.as.string : "",
                            right.type == TYPE_STRING ? right.as.string : "");
                    value_free(&left);
                    value_free(&right);
                    return value_string(buffer);
                }
            } else if (expr->as.binary_op.op == TOKEN_AMPERSAND) {
                // Fuse without space
                if (left.type == TYPE_STRING && right.type == TYPE_STRING) {
                    char buffer[1024];
                    snprintf(buffer, sizeof(buffer), "%s%s", left.as.string, right.as.string);
                    value_free(&left);
                    value_free(&right);
                    return value_string(buffer);
                }
            } else if (expr->as.binary_op.op == TOKEN_MINUS) {
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    Value result = value_number(left.as.number - right.as.number);
                    value_free(&left);
                    value_free(&right);
                    return result;
                }
            } else if (expr->as.binary_op.op == TOKEN_TIMES) {
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    Value result = value_number(left.as.number * right.as.number);
                    value_free(&left);
                    value_free(&right);
                    return result;
                }
            } else if (expr->as.binary_op.op == TOKEN_DIV) {
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    Value result = value_number(left.as.number / right.as.number);
                    value_free(&left);
                    value_free(&right);
                    return result;
                }
            }
            
            value_free(&left);
            value_free(&right);
            return value_null();
        }
        
        default:
            return value_null();
    }
}

bool runtime_evaluate_condition(Runtime* rt, ASTNode* condition) {
    if (!condition) return true;
    
    // Simplified condition evaluation
    Value result = runtime_evaluate_expression(rt, condition);
    bool is_true = (result.type == TYPE_BOOLEAN && result.as.boolean) ||
                   (result.type == TYPE_NUMBER && result.as.number != 0);
    value_free(&result);
    return is_true;
}

Result runtime_execute(Runtime* rt, ASTNode* node) {
    Result result;
    result.success = true;
    result.message = NULL;
    result.value = value_null();
    
    if (!node) {
        result.success = false;
        result.message = strdup("No AST node to execute");
        return result;
    }
    
    if (node->type == NODE_BLUEPRINT) {
        Blueprint* bp = runtime_define_blueprint(rt, node);
        if (bp) {
            result.message = strdup("Blueprint defined successfully");
        } else {
            result.success = false;
            result.message = strdup("Failed to define blueprint");
        }
    }
    
    return result;
}

Result runtime_execute_when(Runtime* rt, Instance* inst, const char* when_name, Value* args, size_t arg_count) {
    (void)args;  // Unused for now
    (void)arg_count;
    
    Result result;
    result.success = false;
    result.message = strdup("When clause not found");
    result.value = value_null();
    
    // Find the when clause
    for (size_t i = 0; i < inst->blueprint->when_count; i++) {
        ASTNode* when = inst->blueprint->whens[i];
        if (strcmp(when->as.when.name, when_name) == 0) {
            // Begin transaction for ACID semantics
            runtime_begin_transaction(inst);
            
            // Execute actions
            for (size_t j = 0; j < when->as.when.action_count; j++) {
                ASTNode* action = when->as.when.actions[j];
                
                if (action->type == NODE_ACTION_SET) {
                    Value new_value = runtime_evaluate_expression(rt, action->as.action_set.value);
                    
                    // Find the field and set it
                    for (size_t k = 0; k < inst->blueprint->field_count; k++) {
                        if (strcmp(inst->blueprint->fields[k]->as.field.name, action->as.action_set.field) == 0) {
                            value_free(&inst->field_values[k]);
                            inst->field_values[k] = new_value;
                            break;
                        }
                    }
                }
            }
            
            // Commit transaction
            runtime_commit_transaction(inst);
            
            result.success = true;
            if (when->as.when.result_message) {
                result.message = strdup(when->as.when.result_message);
            } else {
                result.message = strdup("When clause executed successfully");
            }
            break;
        }
    }
    
    return result;
}
