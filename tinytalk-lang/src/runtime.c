/*
═══════════════════════════════════════════════════════════════
RUNTIME IMPLEMENTATION
Execution engine with ACID semantics
═══════════════════════════════════════════════════════════════
*/

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "runtime.h"

// Portable strdup implementation for strict C11
#ifndef _WIN32
#ifndef strdup
static char* my_strdup(const char* s) {
    size_t len = strlen(s) + 1;
    char* new_str = (char*)malloc(len);
    if (new_str) {
        memcpy(new_str, s, len);
    }
    return new_str;
}
#define strdup my_strdup
#endif
#endif

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
        
        case NODE_FIELD_ACCESS: {
            // Evaluate field access (e.g., Screen.text)
            const char* object_name = expr->as.field_access.object->as.identifier.name;
            const char* field_name = expr->as.field_access.field;
            
            // Find the instance
            for (size_t i = 0; i < rt->instance_count; i++) {
                if (strcmp(rt->instances[i]->blueprint->name, object_name) == 0) {
                    // Find the field
                    for (size_t j = 0; j < rt->instances[i]->blueprint->field_count; j++) {
                        if (strcmp(rt->instances[i]->blueprint->fields[j]->as.field.name, field_name) == 0) {
                            return value_copy(&rt->instances[i]->field_values[j]);
                        }
                    }
                }
            }
            return value_null();
        }
        
        case NODE_BINARY_OP: {
            Value left = runtime_evaluate_expression(rt, expr->as.binary_op.left);
            Value right = runtime_evaluate_expression(rt, expr->as.binary_op.right);
            
            // Comparison operators
            if (expr->as.binary_op.op == TOKEN_IS) {
                bool equal = false;
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    equal = left.as.number == right.as.number;
                } else if (left.type == TYPE_STRING && right.type == TYPE_STRING) {
                    equal = strcmp(left.as.string, right.as.string) == 0;
                } else if (left.type == TYPE_BOOLEAN && right.type == TYPE_BOOLEAN) {
                    equal = left.as.boolean == right.as.boolean;
                }
                value_free(&left);
                value_free(&right);
                return value_boolean(equal);
            } else if (expr->as.binary_op.op == TOKEN_ABOVE) {
                bool result = false;
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    result = left.as.number > right.as.number;
                }
                value_free(&left);
                value_free(&right);
                return value_boolean(result);
            } else if (expr->as.binary_op.op == TOKEN_BELOW) {
                bool result = false;
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    result = left.as.number < right.as.number;
                }
                value_free(&left);
                value_free(&right);
                return value_boolean(result);
            } else if (expr->as.binary_op.op == TOKEN_WITHIN) {
                // For now, implement as a range check (requires special handling)
                // This is a simplified implementation
                bool result = false;
                if (left.type == TYPE_NUMBER && right.type == TYPE_NUMBER) {
                    result = left.as.number <= right.as.number;
                }
                value_free(&left);
                value_free(&right);
                return value_boolean(result);
            } else if (expr->as.binary_op.op == TOKEN_IN) {
                // Check if left is in right (array membership)
                bool result = false;
                if (right.type == TYPE_ARRAY) {
                    for (size_t i = 0; i < right.as.array.count; i++) {
                        if (left.type == right.as.array.items[i].type) {
                            if (left.type == TYPE_STRING && 
                                strcmp(left.as.string, right.as.array.items[i].as.string) == 0) {
                                result = true;
                                break;
                            } else if (left.type == TYPE_NUMBER && 
                                      left.as.number == right.as.array.items[i].as.number) {
                                result = true;
                                break;
                            }
                        }
                    }
                }
                value_free(&left);
                value_free(&right);
                return value_boolean(result);
            }
            
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
                    const char* left_str = "";
                    const char* right_str = "";
                    
                    if (left.type == TYPE_STRING) {
                        left_str = left.as.string;
                    }
                    if (right.type == TYPE_STRING) {
                        right_str = right.as.string;
                    }
                    
                    snprintf(buffer, sizeof(buffer), "%s %s", left_str, right_str);
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
                } else if (left.type == TYPE_STRING || right.type == TYPE_STRING) {
                    // Handle string with non-string
                    char buffer[1024];
                    const char* left_str = "";
                    const char* right_str = "";
                    
                    if (left.type == TYPE_STRING) {
                        left_str = left.as.string;
                    }
                    if (right.type == TYPE_STRING) {
                        right_str = right.as.string;
                    }
                    
                    snprintf(buffer, sizeof(buffer), "%s%s", left_str, right_str);
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
            
            bool should_rollback = false;
            char* rollback_message = NULL;
            
            // Set the current instance context for field lookups
            Runtime* runtime_ctx = rt;
            Instance* current_inst = inst;
            
            // Temporarily set variables for fields from current instance
            for (size_t k = 0; k < current_inst->blueprint->field_count; k++) {
                runtime_set_variable(runtime_ctx, 
                                   current_inst->blueprint->fields[k]->as.field.name,
                                   value_copy(&current_inst->field_values[k]));
            }
            
            // Check conditions (block and must statements)
            for (size_t j = 0; j < when->as.when.condition_count; j++) {
                ASTNode* condition = when->as.when.conditions[j];
                
                if (condition->type == NODE_BLOCK) {
                    // block if condition - halt if condition is true
                    bool cond_result = runtime_evaluate_condition(runtime_ctx, condition->as.block.condition);
                    if (cond_result) {
                        should_rollback = true;
                        rollback_message = strdup("Blocked by condition");
                        break;
                    }
                } else if (condition->type == NODE_MUST) {
                    // must condition - rollback if condition is false
                    bool cond_result = runtime_evaluate_condition(runtime_ctx, condition->as.must.condition);
                    if (!cond_result) {
                        should_rollback = true;
                        if (condition->as.must.error_message) {
                            rollback_message = strdup(condition->as.must.error_message);
                        } else {
                            rollback_message = strdup("Must condition failed");
                        }
                        break;
                    }
                }
            }
            
            // Execute actions only if conditions passed
            if (!should_rollback) {
                for (size_t j = 0; j < when->as.when.action_count; j++) {
                    ASTNode* action = when->as.when.actions[j];
                    
                    if (action->type == NODE_ACTION_SET) {
                        Value new_value = runtime_evaluate_expression(runtime_ctx, action->as.action_set.value);
                        
                        // Check if it's a field access (target.field) or just a field
                        if (action->as.action_set.target) {
                            // It's target.field - find the target instance
                            Instance* target_inst = NULL;
                            for (size_t k = 0; k < runtime_ctx->instance_count; k++) {
                                if (strcmp(runtime_ctx->instances[k]->blueprint->name, action->as.action_set.target) == 0) {
                                    target_inst = runtime_ctx->instances[k];
                                    break;
                                }
                            }
                            
                            if (target_inst) {
                                // Find the field and set it
                                for (size_t k = 0; k < target_inst->blueprint->field_count; k++) {
                                    if (strcmp(target_inst->blueprint->fields[k]->as.field.name, action->as.action_set.field) == 0) {
                                        value_free(&target_inst->field_values[k]);
                                        target_inst->field_values[k] = new_value;
                                        break;
                                    }
                                }
                            } else {
                                value_free(&new_value);
                            }
                        } else {
                            // Find the field and set it on current instance
                            for (size_t k = 0; k < current_inst->blueprint->field_count; k++) {
                                if (strcmp(current_inst->blueprint->fields[k]->as.field.name, action->as.action_set.field) == 0) {
                                    value_free(&current_inst->field_values[k]);
                                    current_inst->field_values[k] = new_value;
                                    break;
                                }
                            }
                        }
                    } else if (action->type == NODE_ACTION_CHANGE) {
                        // change field by +/- value
                        Value change_value = runtime_evaluate_expression(runtime_ctx, action->as.action_change.value);
                        
                        // Find target instance
                        Instance* target_inst = current_inst;
                        if (action->as.action_change.target) {
                            for (size_t k = 0; k < runtime_ctx->instance_count; k++) {
                                if (strcmp(runtime_ctx->instances[k]->blueprint->name, action->as.action_change.target) == 0) {
                                    target_inst = runtime_ctx->instances[k];
                                    break;
                                }
                            }
                        }
                        
                        if (target_inst) {
                            // Find the field
                            for (size_t k = 0; k < target_inst->blueprint->field_count; k++) {
                                if (strcmp(target_inst->blueprint->fields[k]->as.field.name, action->as.action_change.field) == 0) {
                                    Value* field_val = &target_inst->field_values[k];
                                    
                                    // Handle array operations
                                    if (field_val->type == TYPE_NULL || field_val->type == TYPE_ARRAY) {
                                        // Initialize array if null
                                        if (field_val->type == TYPE_NULL) {
                                            field_val->type = TYPE_ARRAY;
                                            field_val->as.array.items = NULL;
                                            field_val->as.array.count = 0;
                                            field_val->as.array.capacity = 0;
                                        }
                                        
                                        if (action->as.action_change.op == TOKEN_PLUS) {
                                            // Add to array
                                            if (field_val->as.array.count >= field_val->as.array.capacity) {
                                                size_t new_capacity = field_val->as.array.capacity == 0 ? 8 : field_val->as.array.capacity * 2;
                                                Value* new_items = (Value*)realloc(field_val->as.array.items, new_capacity * sizeof(Value));
                                                if (new_items) {
                                                    field_val->as.array.items = new_items;
                                                    field_val->as.array.capacity = new_capacity;
                                                }
                                            }
                                            
                                            if (field_val->as.array.count < field_val->as.array.capacity) {
                                                field_val->as.array.items[field_val->as.array.count++] = value_copy(&change_value);
                                            }
                                        } else if (action->as.action_change.op == TOKEN_MINUS) {
                                            // Remove from array
                                            for (size_t m = 0; m < field_val->as.array.count; m++) {
                                                bool match = false;
                                                if (field_val->as.array.items[m].type == change_value.type) {
                                                    if (change_value.type == TYPE_STRING && 
                                                        strcmp(field_val->as.array.items[m].as.string, change_value.as.string) == 0) {
                                                        match = true;
                                                    } else if (change_value.type == TYPE_NUMBER && 
                                                              field_val->as.array.items[m].as.number == change_value.as.number) {
                                                        match = true;
                                                    }
                                                }
                                                
                                                if (match) {
                                                    value_free(&field_val->as.array.items[m]);
                                                    // Shift remaining items
                                                    for (size_t n = m; n < field_val->as.array.count - 1; n++) {
                                                        field_val->as.array.items[n] = field_val->as.array.items[n + 1];
                                                    }
                                                    field_val->as.array.count--;
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    
                                    break;
                                }
                            }
                        }
                        
                        value_free(&change_value);
                    } else if (action->type == NODE_ACTION_MAKE) {
                        // make target state - set state on instance
                        Instance* target_inst = NULL;
                        for (size_t k = 0; k < runtime_ctx->instance_count; k++) {
                            if (strcmp(runtime_ctx->instances[k]->blueprint->name, action->as.action_make.target) == 0) {
                                target_inst = runtime_ctx->instances[k];
                                break;
                            }
                        }
                        
                        if (target_inst) {
                            if (target_inst->current_state) {
                                free(target_inst->current_state);
                            }
                            target_inst->current_state = strdup(action->as.action_make.new_state);
                        }
                    }
                }
            }
            
            // Commit or rollback transaction
            if (should_rollback) {
                runtime_rollback_transaction(current_inst);
                result.success = false;
                result.message = rollback_message ? rollback_message : strdup("Transaction rolled back");
            } else {
                runtime_commit_transaction(current_inst);
                result.success = true;
                if (when->as.when.result_message) {
                    result.message = strdup(when->as.when.result_message);
                } else {
                    result.message = strdup("When clause executed successfully");
                }
            }
            break;
        }
    }
    
    return result;
}
