/*
═══════════════════════════════════════════════════════════════
MAIN - CLI ENTRY POINT
Commands: run, repl, check
═══════════════════════════════════════════════════════════════
*/

#define _POSIX_C_SOURCE 200809L
#include "tinytalk.h"
#include "lexer.h"
#include "parser.h"
#include "runtime.h"
#include "tinytalk_stdlib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

static char* read_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "Error: Could not open file '%s'\n", filename);
        return NULL;
    }
    
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char* buffer = (char*)malloc(size + 1);
    if (!buffer) {
        fclose(file);
        return NULL;
    }
    
    size_t read_size = fread(buffer, 1, size, file);
    buffer[read_size] = '\0';
    
    fclose(file);
    return buffer;
}

Result tinytalk_run_file(const char* filename) {
    Result result;
    result.success = false;
    result.message = NULL;
    result.value = value_null();
    
    char* source = read_file(filename);
    if (!source) {
        result.message = strdup("Failed to read file");
        return result;
    }
    
    result = tinytalk_run_string(source);
    free(source);
    
    return result;
}

Result tinytalk_run_string(const char* source) {
    Result result;
    result.success = false;
    result.message = NULL;
    result.value = value_null();
    
    // Initialize lexer
    Lexer lexer;
    lexer_init(&lexer, source);
    
    // Initialize parser
    Parser parser;
    parser_init(&parser, &lexer);
    
    // Parse the source
    ASTNode* ast = parser_parse(&parser);
    
    if (parser.had_error || !ast) {
        result.message = strdup("Parse error");
        return result;
    }
    
    // Initialize runtime
    Runtime runtime;
    runtime_init(&runtime);
    
    // Initialize standard library
    stdlib_init(&runtime);
    
    // Execute the AST (define the blueprint)
    result = runtime_execute(&runtime, ast);
    
    if (result.success && ast->type == NODE_BLUEPRINT) {
        // Create an instance of the blueprint
        Instance* inst = runtime_create_instance(&runtime, ast->as.blueprint.name);
        
        if (inst && inst->blueprint->when_count > 0) {
            // Execute the first when clause if it exists
            Result when_result = runtime_execute_when(&runtime, inst, 
                                                     inst->blueprint->whens[0]->as.when.name, 
                                                     NULL, 0);
            if (when_result.message) {
                free(result.message);
                result.message = when_result.message;
            }
            result.success = when_result.success;
        }
    }
    
    // Print any output from Screen
    ScreenInstance* screen = stdlib_get_screen(&runtime);
    if (screen && screen->base.field_values) {
        // Find text field (first field)
        if (screen->base.blueprint->field_count > 0) {
            Value* text_val = &screen->base.field_values[0];
            if (text_val->type == TYPE_STRING && text_val->as.string && strlen(text_val->as.string) > 0) {
                printf("%s\n", text_val->as.string);
            }
        }
    }
    
    // Cleanup
    ast_node_free(ast);
    runtime_free(&runtime);
    
    return result;
}

bool tinytalk_check_syntax(const char* source) {
    Lexer lexer;
    lexer_init(&lexer, source);
    
    Parser parser;
    parser_init(&parser, &lexer);
    
    ASTNode* ast = parser_parse(&parser);
    
    bool success = !parser.had_error && ast != NULL;
    
    if (ast) {
        ast_node_free(ast);
    }
    
    return success;
}

void tinytalk_repl(void) {
    printf("tinyTalk %s REPL\n", TINYTALK_VERSION);
    printf("Type 'exit' to quit\n");
    printf("Note: Enter simple expressions like: 2 plus 3, \"Hello\" & \"World\"\n\n");
    
    Runtime runtime;
    runtime_init(&runtime);
    stdlib_init(&runtime);
    
    char line[1024];
    
    while (1) {
        printf(">> ");
        fflush(stdout);
        
        if (!fgets(line, sizeof(line), stdin)) {
            break;
        }
        
        // Remove newline
        line[strcspn(line, "\n")] = 0;
        
        if (strcmp(line, "exit") == 0 || strcmp(line, "quit") == 0) {
            break;
        }
        
        if (strlen(line) == 0) {
            continue;
        }
        
        // Wrap simple expressions as a blueprint with a when clause for evaluation
        char wrapped[2048];
        snprintf(wrapped, sizeof(wrapped), 
                "blueprint REPL\nwhen eval\n  set Screen.text to %s\nfinfr \"ok\"\n", line);
        
        Result result = tinytalk_run_string(wrapped);
        
        if (result.success) {
            // Get Screen.text to show the result
            ScreenInstance* screen = stdlib_get_screen(&runtime);
            if (screen && screen->base.field_values) {
                Value* text_val = &screen->base.field_values[0];
                if (text_val->type == TYPE_STRING && text_val->as.string && strlen(text_val->as.string) > 0) {
                    printf("=> %s\n", text_val->as.string);
                } else if (text_val->type == TYPE_NUMBER) {
                    printf("=> %g\n", text_val->as.number);
                }
            }
        } else {
            if (result.message) {
                printf("Error: %s\n", result.message);
            }
        }
        
        if (result.message) {
            free(result.message);
        }
    }
    
    runtime_free(&runtime);
    printf("\nGoodbye!\n");
}

static void print_usage(const char* program) {
    printf("Usage: %s <command> [arguments]\n\n", program);
    printf("Commands:\n");
    printf("  run <file>     Run a tinyTalk script\n");
    printf("  repl           Start interactive REPL\n");
    printf("  check <file>   Check syntax without running\n");
    printf("\n");
    printf("Example:\n");
    printf("  %s run examples/hello_world.tt\n", program);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }
    
    const char* command = argv[1];
    
    if (strcmp(command, "run") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Error: run command requires a filename\n");
            return 1;
        }
        
        Result result = tinytalk_run_file(argv[2]);
        
        if (!result.success) {
            fprintf(stderr, "Error: %s\n", result.message ? result.message : "Unknown error");
            if (result.message) free(result.message);
            return 1;
        }
        
        if (result.message) {
            printf("%s\n", result.message);
            free(result.message);
        }
        
        return 0;
        
    } else if (strcmp(command, "repl") == 0) {
        tinytalk_repl();
        return 0;
        
    } else if (strcmp(command, "check") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Error: check command requires a filename\n");
            return 1;
        }
        
        char* source = read_file(argv[2]);
        if (!source) {
            return 1;
        }
        
        bool valid = tinytalk_check_syntax(source);
        free(source);
        
        if (valid) {
            printf("Syntax OK\n");
            return 0;
        } else {
            fprintf(stderr, "Syntax errors found\n");
            return 1;
        }
        
    } else {
        fprintf(stderr, "Error: Unknown command '%s'\n", command);
        print_usage(argv[0]);
        return 1;
    }
}
