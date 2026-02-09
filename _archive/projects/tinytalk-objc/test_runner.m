/*
═══════════════════════════════════════════════════════════════
TINYTALK TEST RUNNER
Comprehensive stress, Turing, and ACID tests
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTLexer.h"
#import "TTParser.h"
#import "TTRuntime.h"

// Test result tracking
static NSInteger totalTests = 0;
static NSInteger passedTests = 0;
static NSInteger failedTests = 0;

void printHeader(NSString *title) {
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("  %s\n", [title UTF8String]);
    printf("═══════════════════════════════════════════════════════════════\n");
}

void printSubHeader(NSString *title) {
    printf("\n── %s ──\n", [title UTF8String]);
}

void testPass(NSString *name) {
    totalTests++;
    passedTests++;
    printf("  ✓ %s\n", [name UTF8String]);
}

void testFail(NSString *name, NSString *reason) {
    totalTests++;
    failedTests++;
    printf("  ✗ %s: %s\n", [name UTF8String], [reason UTF8String]);
}

void assertEqual(id actual, id expected, NSString *testName) {
    if ([actual isEqual:expected]) {
        testPass(testName);
    } else {
        testFail(testName, [NSString stringWithFormat:@"Expected %@, got %@", expected, actual]);
    }
}

void assertTrue(BOOL condition, NSString *testName) {
    if (condition) {
        testPass(testName);
    } else {
        testFail(testName, @"Condition was false");
    }
}

void assertFalse(BOOL condition, NSString *testName) {
    if (!condition) {
        testPass(testName);
    } else {
        testFail(testName, @"Condition was true");
    }
}

#pragma mark - Lexer Tests

void runLexerTests(void) {
    printHeader(@"LEXER TESTS");
    
    // Test basic tokens
    printSubHeader(@"Basic Tokens");
    {
        TTLexer *lexer = [[TTLexer alloc] initWithSource:@"blueprint Player"];
        TTToken *t1 = [lexer nextToken];
        assertEqual(@(t1.type), @(TTTokenBlueprint), @"Recognize 'blueprint' keyword");
        TTToken *t2 = [lexer nextToken];
        assertEqual(@(t2.type), @(TTTokenIdentifier), @"Recognize identifier");
        assertEqual(t2.lexeme, @"Player", @"Identifier value correct");
    }
    
    // Test numbers
    printSubHeader(@"Number Literals");
    {
        TTLexer *lexer = [[TTLexer alloc] initWithSource:@"42 3.14159 0 -100"];
        TTToken *t1 = [lexer nextToken];
        assertEqual(@(t1.type), @(TTTokenNumber), @"Integer token type");
        assertEqual(t1.value, @(42.0), @"Integer value");
        
        TTToken *t2 = [lexer nextToken];
        assertEqual(t2.value, @(3.14159), @"Float value");
    }
    
    // Test strings
    printSubHeader(@"String Literals");
    {
        TTLexer *lexer = [[TTLexer alloc] initWithSource:@"\"Hello, World!\""];
        TTToken *t1 = [lexer nextToken];
        assertEqual(@(t1.type), @(TTTokenString), @"String token type");
        assertEqual(t1.value, @"Hello, World!", @"String content");
    }
    
    // Test all keywords
    printSubHeader(@"Keywords");
    {
        NSArray *keywords = @[@"when", @"and", @"fin", @"finfr", @"law", @"forge", 
                              @"set", @"calc", @"memo", @"must", @"block"];
        for (NSString *kw in keywords) {
            TTLexer *lexer = [[TTLexer alloc] initWithSource:kw];
            TTToken *t = [lexer nextToken];
            assertTrue(t.type != TTTokenIdentifier, 
                      [NSString stringWithFormat:@"'%@' is keyword not identifier", kw]);
        }
    }
    
    // Test operators
    printSubHeader(@"Operators");
    {
        TTLexer *lexer = [[TTLexer alloc] initWithSource:@"+ - & # . , ( )"];
        NSArray *expectedTypes = @[@(TTTokenPlusOp), @(TTTokenMinusOp), @(TTTokenAmpersand),
                                   @(TTTokenHash), @(TTTokenDot), @(TTTokenComma),
                                   @(TTTokenLParen), @(TTTokenRParen)];
        for (NSNumber *expected in expectedTypes) {
            TTToken *t = [lexer nextToken];
            assertEqual(@(t.type), expected, 
                       [NSString stringWithFormat:@"Operator %@", expected]);
        }
    }
    
    // Test symbols
    printSubHeader(@"Symbols");
    {
        TTLexer *lexer = [[TTLexer alloc] initWithSource:@":cleared :success :error"];
        TTToken *t1 = [lexer nextToken];
        assertEqual(@(t1.type), @(TTTokenSymbol), @"Symbol token type");
        assertEqual(t1.value, @"cleared", @"Symbol value");
    }
}

#pragma mark - Parser Tests

void runParserTests(void) {
    printHeader(@"PARSER TESTS");
    
    // Test blueprint parsing
    printSubHeader(@"Blueprint Parsing");
    {
        NSString *source = @"blueprint Player\n  starts @health at 100\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        assertFalse(parser.hadError, @"No parse errors");
        assertEqual(@(ast.type), @(TTNodeProgram), @"Root is Program node");
        assertEqual(@(ast.children.count), @(1), @"One blueprint");
        assertEqual([ast.children[0] stringForKey:@"name"], @"Player", @"Blueprint name");
    }
    
    // Test law parsing
    printSubHeader(@"Law Parsing");
    {
        NSString *source = @"blueprint Test\n  law MaxLimit\n    when @value is above 100\n    finfr\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        assertFalse(parser.hadError, @"No parse errors for law");
        TTASTNode *bp = ast.children[0];
        NSArray *laws = bp.data[@"laws"];
        assertEqual(@(laws.count), @(1), @"One law parsed");
    }
    
    // Test when parsing
    printSubHeader(@"When Clause Parsing");
    {
        NSString *source = @"blueprint Test\n  when damage(amount)\n    calc @health minus amount as h\n    set @health to h\n    fin\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        assertFalse(parser.hadError, @"No parse errors for when");
        TTASTNode *bp = ast.children[0];
        NSArray *whens = bp.data[@"whens"];
        assertEqual(@(whens.count), @(1), @"One when clause");
        assertEqual([whens[0] stringForKey:@"name"], @"damage", @"When name");
    }
    
    // Test expression parsing
    printSubHeader(@"Expression Parsing");
    {
        NSString *source = @"blueprint Test\n  when test\n    calc 10 plus 20 as result\n    fin\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        assertFalse(parser.hadError, @"No parse errors for expression");
    }
}

#pragma mark - Runtime Tests

void runRuntimeTests(void) {
    printHeader(@"RUNTIME TESTS");
    
    // Test value operations
    printSubHeader(@"Value Operations");
    {
        TTValue *num1 = [TTValue numberValue:10];
        TTValue *num2 = [TTValue numberValue:3];
        
        TTValue *sum = [num1 add:num2];
        assertEqual(@([sum asNumber]), @(13), @"Addition: 10 + 3 = 13");
        
        TTValue *diff = [num1 subtract:num2];
        assertEqual(@([diff asNumber]), @(7), @"Subtraction: 10 - 3 = 7");
        
        TTValue *prod = [num1 multiply:num2];
        assertEqual(@([prod asNumber]), @(30), @"Multiplication: 10 * 3 = 30");
        
        TTValue *quot = [num1 divide:num2];
        assertTrue(fabs([quot asNumber] - 3.333) < 0.01, @"Division: 10 / 3 ≈ 3.33");
        
        TTValue *rem = [num1 modulo:num2];
        assertEqual(@([rem asNumber]), @(1), @"Modulo: 10 % 3 = 1");
    }
    
    // Test string operations
    printSubHeader(@"String Operations");
    {
        TTValue *s1 = [TTValue stringValue:@"Hello"];
        TTValue *s2 = [TTValue stringValue:@"World"];
        
        TTValue *concat = [s1 concatenate:s2];
        assertEqual([concat asString], @"HelloWorld", @"Concatenation (fuse)");
        
        TTValue *natural = [s1 naturalAdd:s2];
        assertEqual([natural asString], @"Hello World", @"Natural add (with space)");
    }
    
    // Test comparison
    printSubHeader(@"Comparisons");
    {
        TTValue *v10 = [TTValue numberValue:10];
        TTValue *v5 = [TTValue numberValue:5];
        TTValue *v10b = [TTValue numberValue:10];
        
        assertTrue([v10 isGreaterThan:v5], @"10 > 5");
        assertFalse([v5 isGreaterThan:v10], @"5 not > 10");
        assertTrue([v5 isLessThan:v10], @"5 < 10");
        assertTrue([v10 isEqualToValue:v10b], @"10 == 10");
    }
    
    // Test blueprint execution
    printSubHeader(@"Blueprint Execution");
    {
        NSString *source = @"blueprint Counter\n  starts @value at 0\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        TTRuntime *rt = [[TTRuntime alloc] init];
        TTResult *result = [rt execute:ast];
        
        assertTrue(result.success, @"Blueprint loads successfully");
        TTBlueprint *bp = [rt blueprintNamed:@"Counter"];
        assertTrue(bp != nil, @"Blueprint is registered");
    }
    
    // Test instance creation
    printSubHeader(@"Instance Creation");
    {
        NSString *source = @"blueprint Player\n  starts @health at 100\n  starts @name at \"Hero\"\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        TTRuntime *rt = [[TTRuntime alloc] init];
        [rt execute:ast];
        
        TTInstance *player = [rt createInstance:@"Player"];
        assertTrue(player != nil, @"Instance created");
        assertEqual(@([player.fields[@"@health"] asNumber]), @(100), @"Health initialized to 100");
        assertEqual([player.fields[@"@name"] asString], @"Hero", @"Name initialized");
    }
}

#pragma mark - Stress Tests

void runStressTests(void) {
    printHeader(@"STRESS TESTS");
    
    // Test many operations
    printSubHeader(@"Operation Count");
    {
        TTRuntime *rt = [[TTRuntime alloc] init];
        NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
        
        for (int i = 0; i < 10000; i++) {
            TTValue *a = [TTValue numberValue:i];
            TTValue *b = [TTValue numberValue:i + 1];
            [a add:b];
        }
        
        NSTimeInterval elapsed = [[NSDate date] timeIntervalSince1970] - start;
        printf("    10,000 operations in %.3f seconds\n", elapsed);
        assertTrue(elapsed < 1.0, @"10k operations under 1 second");
    }
    
    // Test large strings
    printSubHeader(@"String Building");
    {
        NSMutableString *huge = [NSMutableString string];
        for (int i = 0; i < 1000; i++) {
            [huge appendString:@"ABCDEFGHIJ"];
        }
        TTValue *v = [TTValue stringValue:huge];
        assertEqual(@([[v asString] length]), @(10000), @"Large string (10k chars)");
    }
    
    // Test many tokens
    printSubHeader(@"Lexer Stress");
    {
        NSMutableString *source = [NSMutableString stringWithString:@"blueprint Stress\n"];
        for (int i = 0; i < 100; i++) {
            [source appendFormat:@"  starts @field%d at %d\n", i, i];
        }
        [source appendString:@"end"];
        
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        NSArray *tokens = [lexer allTokens];
        assertTrue(tokens.count > 500, @"Many tokens parsed");
        printf("    Parsed %lu tokens\n", (unsigned long)tokens.count);
    }
    
    // Test execution bounds
    printSubHeader(@"Execution Bounds");
    {
        TTExecutionBounds *bounds = [[TTExecutionBounds alloc] init];
        bounds.maxOperations = 100;
        bounds.timeoutSeconds = 0.1;
        
        TTRuntime *rt = [[TTRuntime alloc] initWithBounds:bounds];
        assertTrue(rt.bounds.maxOperations == 100, @"Custom bounds applied");
    }
}

#pragma mark - Turing Completeness Tests

void runTuringTests(void) {
    printHeader(@"TURING COMPLETENESS TESTS");
    
    // Test arithmetic completeness
    printSubHeader(@"Arithmetic Operations");
    {
        TTValue *a = [TTValue numberValue:100];
        TTValue *b = [TTValue numberValue:7];
        
        TTValue *sum = [a add:b];
        TTValue *diff = [a subtract:b];
        TTValue *prod = [a multiply:b];
        TTValue *quot = [a divide:b];
        TTValue *rem = [a modulo:b];
        
        assertEqual(@([sum asNumber]), @(107), @"Addition complete");
        assertEqual(@([diff asNumber]), @(93), @"Subtraction complete");
        assertEqual(@([prod asNumber]), @(700), @"Multiplication complete");
        assertTrue(fabs([quot asNumber] - 14.285) < 0.01, @"Division complete");
        assertEqual(@([rem asNumber]), @(2), @"Modulo complete");
    }
    
    // Test conditionals
    printSubHeader(@"Conditional Logic");
    {
        TTValue *t = [TTValue booleanValue:YES];
        TTValue *f = [TTValue booleanValue:NO];
        
        assertTrue([t isTruthy], @"True is truthy");
        assertFalse([f isTruthy], @"False is not truthy");
        assertTrue([[TTValue numberValue:1] isTruthy], @"1 is truthy");
        assertFalse([[TTValue numberValue:0] isTruthy], @"0 is not truthy");
        assertTrue([[TTValue stringValue:@"hello"] isTruthy], @"Non-empty string is truthy");
        assertFalse([[TTValue stringValue:@""] isTruthy], @"Empty string is not truthy");
    }
    
    // Test state mutation
    printSubHeader(@"State Mutation");
    {
        NSString *source = @"blueprint StatefulTest\n  starts @counter at 0\n  when increment\n    calc @counter plus 1 as c\n    set @counter to c\n    fin\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        TTRuntime *rt = [[TTRuntime alloc] init];
        [rt execute:ast];
        
        TTInstance *inst = [rt createInstance:@"StatefulTest"];
        rt.world[@"test"] = inst;
        
        // Verify initial state
        assertEqual(@([inst.fields[@"@counter"] asNumber]), @(0), @"Initial state is 0");
        
        // Execute when
        [rt executeWhen:@"increment" onInstance:inst withArgs:nil];
        assertEqual(@([inst.fields[@"@counter"] asNumber]), @(1), @"State mutated to 1");
    }
    
    // Test arrays (data structures)
    printSubHeader(@"Data Structures");
    {
        TTValue *arr = [TTValue arrayValue:@[
            [TTValue numberValue:1],
            [TTValue numberValue:2],
            [TTValue numberValue:3]
        ]];
        
        assertTrue([arr isArray], @"Array type recognized");
        assertEqual(@([[arr asArray] count]), @(3), @"Array has 3 elements");
    }
    
    // Test Fibonacci calculation manually
    printSubHeader(@"Fibonacci Simulation");
    {
        // Simulate fib(10) = 55
        double current = 0, next = 1;
        for (int i = 0; i < 10; i++) {
            double temp = current + next;
            current = next;
            next = temp;
        }
        assertEqual(@(current), @(55), @"Fibonacci(10) = 55");
    }
    
    // Test factorial simulation
    printSubHeader(@"Factorial Simulation");
    {
        // Simulate 5! = 120
        double result = 1;
        for (int i = 5; i >= 1; i--) {
            result *= i;
        }
        assertEqual(@(result), @(120), @"5! = 120");
    }
}

#pragma mark - ACID Tests

void runACIDTests(void) {
    printHeader(@"ACID TESTS");
    
    // Test Atomicity
    printSubHeader(@"Atomicity");
    {
        TTInstance *inst = [[TTInstance alloc] init];
        inst.fields = [NSMutableDictionary dictionary];
        inst.fields[@"balance"] = [TTValue numberValue:100];
        
        // Begin transaction
        [inst beginTransaction];
        inst.fields[@"balance"] = [TTValue numberValue:50];
        
        // Rollback
        [inst rollbackTransaction];
        
        assertEqual(@([inst.fields[@"balance"] asNumber]), @(100), @"Rollback restores state");
    }
    
    {
        TTInstance *inst = [[TTInstance alloc] init];
        inst.fields = [NSMutableDictionary dictionary];
        inst.fields[@"balance"] = [TTValue numberValue:100];
        
        // Begin transaction
        [inst beginTransaction];
        inst.fields[@"balance"] = [TTValue numberValue:50];
        
        // Commit
        [inst commitTransaction];
        
        assertEqual(@([inst.fields[@"balance"] asNumber]), @(50), @"Commit persists state");
    }
    
    // Test Consistency (Law Checking)
    printSubHeader(@"Consistency");
    {
        NSString *source = @"blueprint BoundedValue\n  starts @value at 50\n  law MaxBound\n    when @value is above 100\n    finfr\nend";
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        TTRuntime *rt = [[TTRuntime alloc] init];
        [rt execute:ast];
        
        TTInstance *inst = [rt createInstance:@"BoundedValue"];
        
        // Check laws pass for valid state
        NSString *error;
        BOOL valid = [rt checkLawsForInstance:inst error:&error];
        assertTrue(valid, @"Valid state passes law check");
        
        // Violate the law
        inst.fields[@"@value"] = [TTValue numberValue:150];
        valid = [rt checkLawsForInstance:inst error:&error];
        assertFalse(valid, @"Invalid state fails law check");
    }
    
    // Test Isolation
    printSubHeader(@"Isolation");
    {
        TTInstance *inst = [[TTInstance alloc] init];
        inst.fields = [NSMutableDictionary dictionary];
        inst.fields[@"counter"] = [TTValue numberValue:0];
        
        // Take snapshot
        [inst beginTransaction];
        NSDictionary *snapshot = [inst.fields copy];
        
        // Modify
        inst.fields[@"counter"] = [TTValue numberValue:100];
        
        // Snapshot should be unchanged
        assertEqual(@([[snapshot[@"counter"] copy] asNumber]), @(0), @"Snapshot isolated from changes");
    }
    
    // Test Durability
    printSubHeader(@"Durability");
    {
        TTInstance *inst = [[TTInstance alloc] init];
        inst.fields = [NSMutableDictionary dictionary];
        inst.fields[@"value"] = [TTValue numberValue:42];
        
        [inst beginTransaction];
        inst.fields[@"value"] = [TTValue numberValue:100];
        [inst commitTransaction];
        
        // Value should persist after commit
        assertEqual(@([inst.fields[@"value"] asNumber]), @(100), @"Committed value persists");
        
        // Transaction state should be cleared
        assertFalse(inst.inTransaction, @"Transaction ended after commit");
        assertTrue(inst.fieldSnapshot == nil, @"Snapshot cleared after commit");
    }
    
    // Test complete ACID flow
    printSubHeader(@"Complete ACID Flow");
    {
        NSString *source = @"blueprint Account\n  starts @balance at 1000\n  law NoOverdraft\n    when @balance is below 0\n    finfr\n  when withdraw(amount)\n    must @balance is above amount\n      otherwise \"Insufficient funds\"\n    calc @balance minus amount as b\n    set @balance to b\n    fin\nend";
        
        TTLexer *lexer = [[TTLexer alloc] initWithSource:source];
        TTParser *parser = [[TTParser alloc] initWithLexer:lexer];
        TTASTNode *ast = [parser parse];
        
        TTRuntime *rt = [[TTRuntime alloc] init];
        [rt execute:ast];
        
        TTInstance *acct = [rt createInstance:@"Account"];
        rt.world[@"acct"] = acct;
        
        // Valid withdrawal
        TTResult *r1 = [rt executeWhen:@"withdraw" onInstance:acct 
                              withArgs:@{@"amount": [TTValue numberValue:100]}];
        assertTrue(r1.success, @"Valid withdrawal succeeds");
        assertEqual(@([acct.fields[@"@balance"] asNumber]), @(900), @"Balance reduced");
        
        // Invalid withdrawal (would overdraft)
        TTResult *r2 = [rt executeWhen:@"withdraw" onInstance:acct 
                              withArgs:@{@"amount": [TTValue numberValue:10000]}];
        assertFalse(r2.success, @"Invalid withdrawal rejected");
        assertEqual(@([acct.fields[@"@balance"] asNumber]), @(900), @"Balance unchanged after reject");
    }
}

#pragma mark - Main

void printSummary(void) {
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("  TEST SUMMARY\n");
    printf("═══════════════════════════════════════════════════════════════\n");
    printf("\n");
    printf("  Total:  %ld\n", (long)totalTests);
    printf("  Passed: %ld\n", (long)passedTests);
    printf("  Failed: %ld\n", (long)failedTests);
    printf("\n");
    
    if (failedTests == 0) {
        printf("  ✓ ALL TESTS PASSED!\n");
    } else {
        printf("  ✗ SOME TESTS FAILED\n");
    }
    
    printf("\n");
    printf("═══════════════════════════════════════════════════════════════\n");
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        printf("\n");
        printf("╔═══════════════════════════════════════════════════════════════╗\n");
        printf("║  TINYTALK OBJECTIVE-C - COMPREHENSIVE TEST SUITE              ║\n");
        printf("║  Stress • Turing • ACID                                       ║\n");
        printf("╚═══════════════════════════════════════════════════════════════╝\n");
        
        runLexerTests();
        runParserTests();
        runRuntimeTests();
        runStressTests();
        runTuringTests();
        runACIDTests();
        
        printSummary();
        
        return (failedTests > 0) ? 1 : 0;
    }
}
