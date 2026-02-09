/*
═══════════════════════════════════════════════════════════════
TINYTALK - MAIN ENTRY POINT
CLI interface for the tinyTalk interpreter
═══════════════════════════════════════════════════════════════

The tinyTalk Philosophy:
- The constraint IS the instruction
- The verification IS the computation
- The network IS the processor

tinyTalk is "No-First": it defines the boundary space where reality
is allowed to exist. You are not writing a script; you are defining
the Physics of your World.

Core Principle: newton(current, goal) → current == goal
  When true → execute
  When false → halt (finfr - ontological death)

═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTLexer.h"
#import "TTParser.h"
#import "TTRuntime.h"

void printUsage(const char *programName) {
    printf("tinyTalk Interpreter (Objective-C Edition)\n");
    printf("══════════════════════════════════════════\n");
    printf("\n");
    printf("Usage: %s <command> [options]\n", programName);
    printf("\n");
    printf("Commands:\n");
    printf("  run <file>       Run a tinyTalk program\n");
    printf("  check <file>     Check syntax without executing\n");
    printf("  tokens <file>    Show tokens (for debugging)\n");
    printf("  ast <file>       Show AST (for debugging)\n");
    printf("  repl             Start interactive REPL\n");
    printf("  help             Show this help message\n");
    printf("  version          Show version information\n");
    printf("\n");
    printf("Examples:\n");
    printf("  %s run game.tt\n", programName);
    printf("  %s check player.tt\n", programName);
    printf("  %s repl\n", programName);
    printf("\n");
}

void printVersion(void) {
    printf("tinyTalk 1.0.0 (Objective-C Edition)\n");
    printf("Newton Supercomputer - Constraint-First Computing\n");
    printf("Copyright 2026 Jared Lewis Conglomerate\n");
    printf("\n");
    printf("\"The constraint IS the instruction.\"\n");
}

NSString *readFile(NSString *path) {
    NSError *error;
    NSString *content = [NSString stringWithContentsOfFile:path 
                                                  encoding:NSUTF8StringEncoding 
                                                     error:&error];
    if (error) {
        fprintf(stderr, "Error reading file: %s\n", [[error localizedDescription] UTF8String]);
        return nil;
    }
    return content;
}

void showTokens(NSString *source) {
    TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
    NSArray<TTToken *> *tokens = [lexer allTokens];
    
    printf("Tokens:\n");
    printf("══════════════════════════════════════════\n");
    for (TTToken *token in tokens) {
        printf("  [%3ld] %-15s '%s'", 
               (long)token.line, 
               [[token typeName] UTF8String], 
               [token.lexeme UTF8String] ?: "");
        if (token.value) {
            printf(" → %s", [[token.value description] UTF8String]);
        }
        printf("\n");
    }
    printf("══════════════════════════════════════════\n");
    printf("Total: %lu tokens\n", (unsigned long)tokens.count);
}

void showAST(NSString *source) {
    TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
    TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
    TTASTNode *ast = [parser parse];
    
    if (parser.hadError) {
        fprintf(stderr, "Parse error: %s\n", [parser.errorMessage UTF8String]);
        return;
    }
    
    printf("AST:\n");
    printf("══════════════════════════════════════════\n");
    printf("%s", [[ast prettyPrint:0] UTF8String]);
    printf("══════════════════════════════════════════\n");
}

int checkSyntax(NSString *source, NSString *filename) {
    TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
    TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
    TTASTNode *ast = [parser parse];
    
    if (parser.hadError) {
        fprintf(stderr, "✗ Syntax error in %s:\n", [filename UTF8String]);
        fprintf(stderr, "  %s\n", [parser.errorMessage UTF8String]);
        return 1;
    }
    
    printf("✓ %s: Syntax OK\n", [filename UTF8String]);
    
    // Count constructs
    NSUInteger blueprintCount = ast.children.count;
    NSUInteger fieldCount = 0;
    NSUInteger whenCount = 0;
    NSUInteger lawCount = 0;
    NSUInteger forgeCount = 0;
    
    for (TTASTNode *bp in ast.children) {
        fieldCount += [bp.data[@"fields"] count];
        whenCount += [bp.data[@"whens"] count];
        lawCount += [bp.data[@"laws"] count];
        forgeCount += [bp.data[@"forges"] count];
    }
    
    printf("  Blueprints: %lu\n", (unsigned long)blueprintCount);
    printf("  Fields: %lu\n", (unsigned long)fieldCount);
    printf("  Laws: %lu\n", (unsigned long)lawCount);
    printf("  Whens: %lu\n", (unsigned long)whenCount);
    printf("  Forges: %lu\n", (unsigned long)forgeCount);
    
    return 0;
}

int runProgram(NSString *source, NSString *filename) {
    TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
    TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
    TTASTNode *ast = [parser parse];
    
    if (parser.hadError) {
        fprintf(stderr, "Parse error: %s\n", [parser.errorMessage UTF8String]);
        return 1;
    }
    
    TTRuntime *runtime = [[TTRuntime alloc] init];
    TTResult *result = [runtime execute:ast];
    
    if (!result.success) {
        if (result.isFinfr) {
            printf("FINFR (Ontological Death): %s\n", [result.errorMessage UTF8String]);
        } else {
            fprintf(stderr, "Runtime error: %s\n", [result.errorMessage UTF8String]);
        }
        return 1;
    }
    
    printf("Program loaded: %s\n", [[result.value asString] UTF8String]);
    printf("\nBlueprints defined:\n");
    for (NSString *name in runtime.world.allKeys) {
        printf("  - %s\n", [name UTF8String]);
    }
    
    return 0;
}

void runREPL(void) {
    printf("tinyTalk REPL (Objective-C Edition)\n");
    printf("══════════════════════════════════════════\n");
    printf("Type 'help' for commands, 'quit' to exit\n\n");
    
    TTRuntime *runtime = [[TTRuntime alloc] init];
    char buffer[4096];
    
    while (1) {
        printf("tt> ");
        fflush(stdout);
        
        if (!fgets(buffer, sizeof(buffer), stdin)) {
            break;
        }
        
        NSString *input = [[NSString stringWithUTF8String:buffer] 
                           stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        
        if ([input length] == 0) continue;
        
        if ([input isEqualToString:@"quit"] || [input isEqualToString:@"exit"]) {
            printf("Goodbye!\n");
            break;
        }
        
        if ([input isEqualToString:@"help"]) {
            printf("REPL Commands:\n");
            printf("  help              Show this help\n");
            printf("  quit/exit         Exit REPL\n");
            printf("  :blueprints       List defined blueprints\n");
            printf("  :world            Show world state\n");
            printf("  :vars             Show variables\n");
            printf("  :clear            Clear runtime state\n");
            printf("\nOr enter tinyTalk code to execute.\n");
            continue;
        }
        
        if ([input isEqualToString:@":blueprints"]) {
            printf("Defined blueprints: (use world inspection)\n");
            continue;
        }
        
        if ([input isEqualToString:@":world"]) {
            printf("World instances:\n");
            for (NSString *name in runtime.world) {
                TTInstance *inst = runtime.world[name];
                printf("  %s (%s)\n", [name UTF8String], [inst.blueprint.name UTF8String]);
                for (NSString *field in inst.fields) {
                    printf("    .%s = %s\n", [field UTF8String], 
                           [[inst.fields[field] asString] UTF8String]);
                }
            }
            continue;
        }
        
        if ([input isEqualToString:@":vars"]) {
            printf("Variables: (internal state)\n");
            continue;
        }
        
        if ([input isEqualToString:@":clear"]) {
            runtime = [[TTRuntime alloc] init];
            printf("Runtime state cleared.\n");
            continue;
        }
        
        // Try to parse and execute
        TTLexer *lexer = [[TTLexer alloc] initWithSource:input];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        if (parser.hadError) {
            fprintf(stderr, "Error: %s\n", [parser.errorMessage UTF8String]);
            continue;
        }
        
        if (ast) {
            TTResult *result = [runtime execute:ast];
            if (result.success) {
                printf("=> %s\n", [[result.value asString] UTF8String]);
            } else if (result.isFinfr) {
                printf("FINFR: %s\n", [result.errorMessage UTF8String]);
            } else {
                fprintf(stderr, "Error: %s\n", [result.errorMessage UTF8String]);
            }
        }
    }
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 2) {
            printUsage(argv[0]);
            return 1;
        }
        
        NSString *command = [NSString stringWithUTF8String:argv[1]];
        
        if ([command isEqualToString:@"help"] || [command isEqualToString:@"-h"] || 
            [command isEqualToString:@"--help"]) {
            printUsage(argv[0]);
            return 0;
        }
        
        if ([command isEqualToString:@"version"] || [command isEqualToString:@"-v"] ||
            [command isEqualToString:@"--version"]) {
            printVersion();
            return 0;
        }
        
        if ([command isEqualToString:@"repl"]) {
            runREPL();
            return 0;
        }
        
        // Commands that need a file
        if (argc < 3) {
            fprintf(stderr, "Error: Command '%s' requires a file argument\n", argv[1]);
            return 1;
        }
        
        NSString *filename = [NSString stringWithUTF8String:argv[2]];
        NSString *source = readFile(filename);
        
        if (!source) {
            return 1;
        }
        
        if ([command isEqualToString:@"run"]) {
            return runProgram(source, filename);
        }
        
        if ([command isEqualToString:@"check"]) {
            return checkSyntax(source, filename);
        }
        
        if ([command isEqualToString:@"tokens"]) {
            showTokens(source);
            return 0;
        }
        
        if ([command isEqualToString:@"ast"]) {
            showAST(source);
            return 0;
        }
        
        fprintf(stderr, "Unknown command: %s\n", [command UTF8String]);
        printUsage(argv[0]);
        return 1;
    }
}
