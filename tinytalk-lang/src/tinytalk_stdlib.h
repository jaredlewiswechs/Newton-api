/*
═══════════════════════════════════════════════════════════════
STDLIB - STANDARD KIT IMPLEMENTATION
Clock, Random, Input, Screen, Storage blueprints
═══════════════════════════════════════════════════════════════
*/

#ifndef TINYTALK_STDLIB_H
#define TINYTALK_STDLIB_H

#include "runtime.h"
#include <stdbool.h>
#include <time.h>

// Clock blueprint
typedef struct {
    Instance base;
    int time_of_day;
    int day_count;
    bool paused;
} ClockInstance;

// Random blueprint
typedef struct {
    Instance base;
    double number;      // 0.0 - 1.0
    int percent;        // 0 - 100
    int dice;           // 1 - 6
} RandomInstance;

// Input blueprint
typedef struct {
    Instance base;
    int mouse_x;
    int mouse_y;
    char** keys;
    size_t key_count;
} InputInstance;

// Screen blueprint
typedef struct {
    Instance base;
    char* text;
    char* color;
    bool cleared;
} ScreenInstance;

// Storage blueprint
typedef struct {
    Instance base;
    char* save_file;
    bool saved;
    bool loaded;
} StorageInstance;

// Standard library initialization
void stdlib_init(Runtime* rt);

// Standard blueprint registration
void stdlib_register_clock(Runtime* rt);
void stdlib_register_random(Runtime* rt);
void stdlib_register_input(Runtime* rt);
void stdlib_register_screen(Runtime* rt);
void stdlib_register_storage(Runtime* rt);

// Helper functions
ClockInstance* stdlib_get_clock(Runtime* rt);
RandomInstance* stdlib_get_random(Runtime* rt);
InputInstance* stdlib_get_input(Runtime* rt);
ScreenInstance* stdlib_get_screen(Runtime* rt);
StorageInstance* stdlib_get_storage(Runtime* rt);

#endif // TINYTALK_STDLIB_H
