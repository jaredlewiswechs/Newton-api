/*
═══════════════════════════════════════════════════════════════
TINYTALK 1.0 - PUBLIC API
Human-First Programming Language
═══════════════════════════════════════════════════════════════
*/

#ifndef TINYTALK_H
#define TINYTALK_H

#include <stddef.h>
#include <stdbool.h>

#define TINYTALK_VERSION "1.0"
#define MAX_IDENTIFIER_LEN 256
#define MAX_STRING_LEN 1024
#define MAX_FIELDS 64
#define MAX_STATES 32
#define MAX_WHENS 128

// Forward declarations
typedef struct Value Value;
typedef struct Blueprint Blueprint;
typedef struct Instance Instance;

// Value types
typedef enum {
    TYPE_NUMBER,
    TYPE_STRING,
    TYPE_SYMBOL,
    TYPE_BOOLEAN,
    TYPE_ARRAY,
    TYPE_BLUEPRINT,
    TYPE_NULL
} ValueType;

// Value structure
struct Value {
    ValueType type;
    union {
        double number;
        char* string;
        bool boolean;
        struct {
            Value* items;
            size_t count;
            size_t capacity;
        } array;
        Instance* instance;
    } as;
};

// Result structure for operations
typedef struct {
    bool success;
    char* message;
    Value value;
} Result;

// Public API functions
Result tinytalk_run_file(const char* filename);
Result tinytalk_run_string(const char* source);
void tinytalk_repl(void);
bool tinytalk_check_syntax(const char* source);

// Value operations
Value value_number(double n);
Value value_string(const char* s);
Value value_boolean(bool b);
Value value_null(void);
void value_free(Value* v);
Value value_copy(const Value* v);

#endif // TINYTALK_H
