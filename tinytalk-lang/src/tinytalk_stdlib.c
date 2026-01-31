/*
═══════════════════════════════════════════════════════════════
STDLIB IMPLEMENTATION
Standard Kit: Clock, Random, Input, Screen, Storage
═══════════════════════════════════════════════════════════════
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "tinytalk_stdlib.h"

static ScreenInstance* global_screen = NULL;

void stdlib_init(Runtime* rt) {
    stdlib_register_clock(rt);
    stdlib_register_random(rt);
    stdlib_register_input(rt);
    stdlib_register_screen(rt);
    stdlib_register_storage(rt);
}

void stdlib_register_clock(Runtime* rt) {
    // Create Clock blueprint
    ASTNode* bp_node = (ASTNode*)calloc(1, sizeof(ASTNode));
    bp_node->type = NODE_BLUEPRINT;
    bp_node->as.blueprint.name = strdup("Clock");
    bp_node->as.blueprint.field_count = 3;
    bp_node->as.blueprint.fields = (ASTNode**)calloc(3, sizeof(ASTNode*));
    
    // time_of_day field
    ASTNode* field1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field1->type = NODE_FIELD;
    field1->as.field.name = strdup("time_of_day");
    ASTNode* init1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init1->type = NODE_LITERAL;
    init1->as.literal.value = value_number(0);
    field1->as.field.initial_value = init1;
    bp_node->as.blueprint.fields[0] = field1;
    
    // day_count field
    ASTNode* field2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field2->type = NODE_FIELD;
    field2->as.field.name = strdup("day_count");
    ASTNode* init2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init2->type = NODE_LITERAL;
    init2->as.literal.value = value_number(0);
    field2->as.field.initial_value = init2;
    bp_node->as.blueprint.fields[1] = field2;
    
    // paused field
    ASTNode* field3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field3->type = NODE_FIELD;
    field3->as.field.name = strdup("paused");
    ASTNode* init3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init3->type = NODE_LITERAL;
    init3->as.literal.value = value_boolean(false);
    field3->as.field.initial_value = init3;
    bp_node->as.blueprint.fields[2] = field3;
    
    bp_node->as.blueprint.state_count = 0;
    bp_node->as.blueprint.states = NULL;
    bp_node->as.blueprint.when_count = 0;
    bp_node->as.blueprint.whens = NULL;
    
    runtime_define_blueprint(rt, bp_node);
}

void stdlib_register_random(Runtime* rt) {
    // Create Random blueprint
    ASTNode* bp_node = (ASTNode*)calloc(1, sizeof(ASTNode));
    bp_node->type = NODE_BLUEPRINT;
    bp_node->as.blueprint.name = strdup("Random");
    bp_node->as.blueprint.field_count = 3;
    bp_node->as.blueprint.fields = (ASTNode**)calloc(3, sizeof(ASTNode*));
    
    // number field (0.0 - 1.0)
    ASTNode* field1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field1->type = NODE_FIELD;
    field1->as.field.name = strdup("number");
    ASTNode* init1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init1->type = NODE_LITERAL;
    init1->as.literal.value = value_number((double)rand() / RAND_MAX);
    field1->as.field.initial_value = init1;
    bp_node->as.blueprint.fields[0] = field1;
    
    // percent field (0 - 100)
    ASTNode* field2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field2->type = NODE_FIELD;
    field2->as.field.name = strdup("percent");
    ASTNode* init2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init2->type = NODE_LITERAL;
    init2->as.literal.value = value_number(rand() % 101);
    field2->as.field.initial_value = init2;
    bp_node->as.blueprint.fields[1] = field2;
    
    // dice field (1 - 6)
    ASTNode* field3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field3->type = NODE_FIELD;
    field3->as.field.name = strdup("dice");
    ASTNode* init3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init3->type = NODE_LITERAL;
    init3->as.literal.value = value_number((rand() % 6) + 1);
    field3->as.field.initial_value = init3;
    bp_node->as.blueprint.fields[2] = field3;
    
    bp_node->as.blueprint.state_count = 0;
    bp_node->as.blueprint.states = NULL;
    bp_node->as.blueprint.when_count = 0;
    bp_node->as.blueprint.whens = NULL;
    
    runtime_define_blueprint(rt, bp_node);
}

void stdlib_register_input(Runtime* rt) {
    // Create Input blueprint
    ASTNode* bp_node = (ASTNode*)calloc(1, sizeof(ASTNode));
    bp_node->type = NODE_BLUEPRINT;
    bp_node->as.blueprint.name = strdup("Input");
    bp_node->as.blueprint.field_count = 2;
    bp_node->as.blueprint.fields = (ASTNode**)calloc(2, sizeof(ASTNode*));
    
    // mouse_x field
    ASTNode* field1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field1->type = NODE_FIELD;
    field1->as.field.name = strdup("mouse_x");
    ASTNode* init1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init1->type = NODE_LITERAL;
    init1->as.literal.value = value_number(0);
    field1->as.field.initial_value = init1;
    bp_node->as.blueprint.fields[0] = field1;
    
    // mouse_y field
    ASTNode* field2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field2->type = NODE_FIELD;
    field2->as.field.name = strdup("mouse_y");
    ASTNode* init2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init2->type = NODE_LITERAL;
    init2->as.literal.value = value_number(0);
    field2->as.field.initial_value = init2;
    bp_node->as.blueprint.fields[1] = field2;
    
    bp_node->as.blueprint.state_count = 0;
    bp_node->as.blueprint.states = NULL;
    bp_node->as.blueprint.when_count = 0;
    bp_node->as.blueprint.whens = NULL;
    
    runtime_define_blueprint(rt, bp_node);
}

void stdlib_register_screen(Runtime* rt) {
    // Create Screen blueprint
    ASTNode* bp_node = (ASTNode*)calloc(1, sizeof(ASTNode));
    bp_node->type = NODE_BLUEPRINT;
    bp_node->as.blueprint.name = strdup("Screen");
    bp_node->as.blueprint.field_count = 3;
    bp_node->as.blueprint.fields = (ASTNode**)calloc(3, sizeof(ASTNode*));
    
    // text field
    ASTNode* field1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field1->type = NODE_FIELD;
    field1->as.field.name = strdup("text");
    ASTNode* init1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init1->type = NODE_LITERAL;
    init1->as.literal.value = value_string("");
    field1->as.field.initial_value = init1;
    bp_node->as.blueprint.fields[0] = field1;
    
    // color field
    ASTNode* field2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field2->type = NODE_FIELD;
    field2->as.field.name = strdup("color");
    ASTNode* init2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init2->type = NODE_LITERAL;
    init2->as.literal.value = value_string("white");
    field2->as.field.initial_value = init2;
    bp_node->as.blueprint.fields[1] = field2;
    
    // cleared field
    ASTNode* field3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field3->type = NODE_FIELD;
    field3->as.field.name = strdup("cleared");
    ASTNode* init3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init3->type = NODE_LITERAL;
    init3->as.literal.value = value_boolean(false);
    field3->as.field.initial_value = init3;
    bp_node->as.blueprint.fields[2] = field3;
    
    bp_node->as.blueprint.state_count = 0;
    bp_node->as.blueprint.states = NULL;
    bp_node->as.blueprint.when_count = 0;
    bp_node->as.blueprint.whens = NULL;
    
    runtime_define_blueprint(rt, bp_node);
}

void stdlib_register_storage(Runtime* rt) {
    // Create Storage blueprint
    ASTNode* bp_node = (ASTNode*)calloc(1, sizeof(ASTNode));
    bp_node->type = NODE_BLUEPRINT;
    bp_node->as.blueprint.name = strdup("Storage");
    bp_node->as.blueprint.field_count = 3;
    bp_node->as.blueprint.fields = (ASTNode**)calloc(3, sizeof(ASTNode*));
    
    // save_file field
    ASTNode* field1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field1->type = NODE_FIELD;
    field1->as.field.name = strdup("save_file");
    ASTNode* init1 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init1->type = NODE_LITERAL;
    init1->as.literal.value = value_string("");
    field1->as.field.initial_value = init1;
    bp_node->as.blueprint.fields[0] = field1;
    
    // saved field
    ASTNode* field2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field2->type = NODE_FIELD;
    field2->as.field.name = strdup("saved");
    ASTNode* init2 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init2->type = NODE_LITERAL;
    init2->as.literal.value = value_boolean(false);
    field2->as.field.initial_value = init2;
    bp_node->as.blueprint.fields[1] = field2;
    
    // loaded field
    ASTNode* field3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    field3->type = NODE_FIELD;
    field3->as.field.name = strdup("loaded");
    ASTNode* init3 = (ASTNode*)calloc(1, sizeof(ASTNode));
    init3->type = NODE_LITERAL;
    init3->as.literal.value = value_boolean(false);
    field3->as.field.initial_value = init3;
    bp_node->as.blueprint.fields[2] = field3;
    
    bp_node->as.blueprint.state_count = 0;
    bp_node->as.blueprint.states = NULL;
    bp_node->as.blueprint.when_count = 0;
    bp_node->as.blueprint.whens = NULL;
    
    runtime_define_blueprint(rt, bp_node);
}

ScreenInstance* stdlib_get_screen(Runtime* rt) {
    if (!global_screen) {
        Instance* inst = runtime_create_instance(rt, "Screen");
        global_screen = (ScreenInstance*)inst;
    }
    return global_screen;
}
