/*
═══════════════════════════════════════════════════════════════
TTRUNTIME IMPLEMENTATION
Execution engine with ACID semantics
═══════════════════════════════════════════════════════════════
*/

#import "TTRuntime.h"

#pragma mark - TTExecutionBounds

@implementation TTExecutionBounds

+ (instancetype)defaultBounds {
    TTExecutionBounds *bounds = [[TTExecutionBounds alloc] init];
    bounds.maxIterations = 10000;
    bounds.maxRecursionDepth = 100;
    bounds.maxOperations = 1000000;
    bounds.timeoutSeconds = 30.0;
    return bounds;
}

@end

#pragma mark - TTResult

@implementation TTResult

+ (instancetype)successWithValue:(TTValue *)value {
    TTResult *result = [[TTResult alloc] init];
    result.success = YES;
    result.value = value;
    result.isFinfr = NO;
    return result;
}

+ (instancetype)failureWithMessage:(NSString *)message {
    TTResult *result = [[TTResult alloc] init];
    result.success = NO;
    result.errorMessage = message;
    result.isFinfr = NO;
    return result;
}

+ (instancetype)finfrWithMessage:(NSString *)message {
    TTResult *result = [[TTResult alloc] init];
    result.success = NO;
    result.errorMessage = message;
    result.isFinfr = YES;
    return result;
}

- (NSString *)description {
    if (self.success) {
        return [NSString stringWithFormat:@"Success: %@", self.value];
    }
    if (self.isFinfr) {
        return [NSString stringWithFormat:@"FINFR (Ontological Death): %@", self.errorMessage];
    }
    return [NSString stringWithFormat:@"Failure: %@", self.errorMessage];
}

@end

#pragma mark - TTBlueprint

@implementation TTBlueprint

- (instancetype)init {
    self = [super init];
    if (self) {
        _fields = @[];
        _states = @[];
        _laws = @[];
        _whens = @[];
        _forges = @[];
    }
    return self;
}

@end

#pragma mark - TTInstance

@implementation TTInstance

- (instancetype)init {
    self = [super init];
    if (self) {
        _fields = [NSMutableDictionary dictionary];
        _inTransaction = NO;
    }
    return self;
}

- (void)beginTransaction {
    self.inTransaction = YES;
    self.fieldSnapshot = [self.fields copy];
}

- (void)commitTransaction {
    self.inTransaction = NO;
    self.fieldSnapshot = nil;
}

- (void)rollbackTransaction {
    if (self.fieldSnapshot) {
        [self.fields removeAllObjects];
        [self.fields addEntriesFromDictionary:self.fieldSnapshot];
    }
    self.inTransaction = NO;
    self.fieldSnapshot = nil;
}

@end

#pragma mark - TTRuntime

@interface TTRuntime ()
@property (nonatomic, strong) TTExecutionBounds *bounds;
@property (nonatomic, assign) NSUInteger operationCount;
@property (nonatomic, assign) NSUInteger recursionDepth;
@property (nonatomic, strong) NSMutableDictionary<NSString *, TTBlueprint *> *blueprints;
@property (nonatomic, strong) NSMutableDictionary<NSString *, TTInstance *> *world;
@property (nonatomic, strong) NSMutableDictionary<NSString *, TTValue *> *variables;
@property (nonatomic, strong) NSDate *startTime;
@end

@implementation TTRuntime

- (instancetype)init {
    return [self initWithBounds:[TTExecutionBounds defaultBounds]];
}

- (instancetype)initWithBounds:(TTExecutionBounds *)bounds {
    self = [super init];
    if (self) {
        _bounds = bounds;
        _operationCount = 0;
        _recursionDepth = 0;
        _blueprints = [NSMutableDictionary dictionary];
        _world = [NSMutableDictionary dictionary];
        _variables = [NSMutableDictionary dictionary];
        _startTime = [NSDate date];
    }
    return self;
}

#pragma mark - Bounds Checking

- (BOOL)checkBoundsWithError:(NSString * _Nullable *)error {
    _operationCount++;
    
    if (_operationCount > _bounds.maxOperations) {
        if (error) *error = @"Maximum operations exceeded";
        return NO;
    }
    
    if (_recursionDepth > _bounds.maxRecursionDepth) {
        if (error) *error = @"Maximum recursion depth exceeded";
        return NO;
    }
    
    if ([[NSDate date] timeIntervalSinceDate:_startTime] > _bounds.timeoutSeconds) {
        if (error) *error = @"Execution timeout exceeded";
        return NO;
    }
    
    return YES;
}

#pragma mark - Blueprint Operations

- (TTBlueprint *)defineBlueprint:(TTASTNode *)node {
    if (node.type != TTNodeBlueprint) return nil;
    
    TTBlueprint *bp = [[TTBlueprint alloc] init];
    bp.name = [node stringForKey:@"name"];
    bp.fields = node.data[@"fields"] ?: @[];
    bp.states = node.data[@"states"] ?: @[];
    bp.laws = node.data[@"laws"] ?: @[];
    bp.whens = node.data[@"whens"] ?: @[];
    bp.forges = node.data[@"forges"] ?: @[];
    
    _blueprints[bp.name] = bp;
    
    return bp;
}

- (TTBlueprint *)blueprintNamed:(NSString *)name {
    return _blueprints[name];
}

- (TTInstance *)createInstance:(NSString *)blueprintName {
    TTBlueprint *bp = _blueprints[blueprintName];
    if (!bp) return nil;
    
    TTInstance *instance = [[TTInstance alloc] init];
    instance.blueprint = bp;
    
    // Initialize fields with default values
    for (TTASTNode *field in bp.fields) {
        NSString *name = [field stringForKey:@"name"];
        TTASTNode *initialValue = [field nodeForKey:@"initial_value"];
        
        if (initialValue) {
            instance.fields[name] = [self evaluateExpression:initialValue];
        } else {
            instance.fields[name] = [TTValue nullValue];
        }
    }
    
    return instance;
}

- (TTInstance *)instanceNamed:(NSString *)name {
    return _world[name];
}

#pragma mark - Expression Evaluation

- (TTValue *)evaluateExpression:(TTASTNode *)expr {
    if (!expr) return [TTValue nullValue];
    
    NSString *error;
    if (![self checkBoundsWithError:&error]) {
        NSLog(@"Bounds exceeded: %@", error);
        return [TTValue nullValue];
    }
    
    switch (expr.type) {
        case TTNodeLiteral: {
            id value = expr.data[@"value"];
            if ([value isKindOfClass:[NSNumber class]]) {
                // Check if it's a boolean
                if (strcmp([value objCType], @encode(BOOL)) == 0) {
                    return [TTValue booleanValue:[value boolValue]];
                }
                return [TTValue numberValue:[value doubleValue]];
            }
            if ([value isKindOfClass:[NSString class]]) {
                NSString *str = value;
                if ([str hasPrefix:@":"]) {
                    return [TTValue symbolValue:str];
                }
                if ([str isEqualToString:@"[]"]) {
                    return [TTValue arrayValue:@[]];
                }
                return [TTValue stringValue:str];
            }
            return [TTValue nullValue];
        }
            
        case TTNodeIdentifier: {
            NSString *name = [expr stringForKey:@"name"];
            
            // Check variables first
            TTValue *varValue = _variables[name];
            if (varValue) return varValue;
            
            // Check world instances
            TTInstance *instance = _world[name];
            if (instance) {
                // Return the instance as a special value (could be enhanced)
                return [TTValue stringValue:[NSString stringWithFormat:@"<Instance:%@>", name]];
            }
            
            return [TTValue nullValue];
        }
            
        case TTNodeFieldAccess: {
            NSString *objectName = [expr stringForKey:@"object"];
            NSString *fieldName = [expr stringForKey:@"field"];
            
            TTInstance *instance = _world[objectName];
            if (instance) {
                TTValue *fieldValue = instance.fields[fieldName];
                return fieldValue ?: [TTValue nullValue];
            }
            
            return [TTValue nullValue];
        }
            
        case TTNodeBinaryOp: {
            TTASTNode *leftNode = [expr nodeForKey:@"left"];
            TTASTNode *rightNode = [expr nodeForKey:@"right"];
            TTTokenType op = [expr tokenTypeForKey:@"op"];
            
            TTValue *left = [self evaluateExpression:leftNode];
            TTValue *right = [self evaluateExpression:rightNode];
            
            switch (op) {
                case TTTokenPlus:
                case TTTokenPlusOp:
                    return [left naturalAdd:right];
                    
                case TTTokenMinus:
                case TTTokenMinusOp:
                    return [left subtract:right];
                    
                case TTTokenTimes:
                    return [left multiply:right];
                    
                case TTTokenDiv:
                    return [left divide:right];
                    
                case TTTokenRem:
                    return [left modulo:right];
                    
                case TTTokenAmpersand:
                    return [left concatenate:right];
                    
                case TTTokenIs:
                    return [TTValue booleanValue:[left isEqualToValue:right]];
                    
                case TTTokenAbove:
                case TTTokenGreater:
                    return [TTValue booleanValue:[left isGreaterThan:right]];
                    
                case TTTokenBelow:
                case TTTokenLess:
                    return [TTValue booleanValue:[left isLessThan:right]];
                    
                case TTTokenAnd:
                    return [TTValue booleanValue:[left isTruthy] && [right isTruthy]];
                    
                case TTTokenIn: {
                    // Check if left is in right (array)
                    if ([right isArray]) {
                        for (TTValue *item in [right asArray]) {
                            if ([left isEqualToValue:item]) {
                                return [TTValue booleanValue:YES];
                            }
                        }
                    }
                    return [TTValue booleanValue:NO];
                }
                    
                default:
                    return [TTValue nullValue];
            }
        }
            
        default:
            return [TTValue nullValue];
    }
}

- (BOOL)evaluateCondition:(TTASTNode *)condition {
    TTValue *result = [self evaluateExpression:condition];
    return [result isTruthy];
}

#pragma mark - Law Checking

- (BOOL)checkLawsForInstance:(TTInstance *)instance error:(NSString **)error {
    for (TTASTNode *law in instance.blueprint.laws) {
        TTASTNode *condition = [law nodeForKey:@"condition"];
        BOOL isFinfr = [law boolForKey:@"is_finfr"];
        
        if (condition) {
            // Push instance fields to variables for evaluation
            NSMutableDictionary *savedVars = [_variables mutableCopy];
            [_variables addEntriesFromDictionary:instance.fields];
            
            BOOL conditionMet = [self evaluateCondition:condition];
            
            _variables = savedVars;
            
            // If condition is met and law is finfr, this is ontological death
            if (conditionMet && isFinfr) {
                if (error) {
                    *error = [NSString stringWithFormat:@"Law '%@' violated: ontological death",
                              [law stringForKey:@"name"]];
                }
                return NO;
            }
        }
    }
    return YES;
}

#pragma mark - Action Execution

- (TTResult *)executeAction:(TTASTNode *)action onInstance:(TTInstance *)instance {
    switch (action.type) {
        case TTNodeActionSet: {
            TTASTNode *target = [action nodeForKey:@"target"];
            TTASTNode *valueNode = [action nodeForKey:@"value"];
            TTValue *value = [self evaluateExpression:valueNode];
            
            if (target.type == TTNodeFieldAccess) {
                NSString *objectName = [target stringForKey:@"object"];
                NSString *fieldName = [target stringForKey:@"field"];
                
                TTInstance *targetInstance = _world[objectName];
                if (targetInstance) {
                    targetInstance.fields[fieldName] = value;
                }
            } else if (target.type == TTNodeIdentifier) {
                NSString *name = [target stringForKey:@"name"];
                
                // Check if it's an instance field
                if (instance && instance.fields[name]) {
                    instance.fields[name] = value;
                } else {
                    _variables[name] = value;
                }
            }
            
            return [TTResult successWithValue:value];
        }
            
        case TTNodeActionMake: {
            NSString *targetName = [action stringForKey:@"target"];
            NSString *stateName = [action stringForKey:@"state"];
            
            TTInstance *targetInstance = _world[targetName];
            if (targetInstance) {
                targetInstance.currentState = stateName;
            }
            
            return [TTResult successWithValue:[TTValue symbolValue:stateName]];
        }
            
        case TTNodeActionChange: {
            TTASTNode *target = [action nodeForKey:@"target"];
            TTTokenType op = [action tokenTypeForKey:@"op"];
            TTASTNode *valueNode = [action nodeForKey:@"value"];
            TTValue *changeValue = [self evaluateExpression:valueNode];
            
            NSString *fieldName = nil;
            TTInstance *targetInstance = nil;
            
            if (target.type == TTNodeFieldAccess) {
                NSString *objectName = [target stringForKey:@"object"];
                fieldName = [target stringForKey:@"field"];
                targetInstance = _world[objectName];
            } else if (target.type == TTNodeIdentifier) {
                fieldName = [target stringForKey:@"name"];
                targetInstance = instance;
            }
            
            if (targetInstance && fieldName) {
                TTValue *currentValue = targetInstance.fields[fieldName];
                if (!currentValue) currentValue = [TTValue nullValue];
                
                TTValue *newValue;
                if ([currentValue isArray]) {
                    // Array operation
                    NSMutableArray *arr = [[currentValue asArray] mutableCopy];
                    if (op == TTTokenPlusOp) {
                        [arr addObject:changeValue];
                    } else if (op == TTTokenMinusOp) {
                        [arr removeObject:changeValue];
                    }
                    newValue = [TTValue arrayValue:arr];
                } else {
                    // Numeric operation
                    if (op == TTTokenPlusOp) {
                        newValue = [currentValue add:changeValue];
                    } else {
                        newValue = [currentValue subtract:changeValue];
                    }
                }
                
                targetInstance.fields[fieldName] = newValue;
                return [TTResult successWithValue:newValue];
            }
            
            return [TTResult failureWithMessage:@"Change target not found"];
        }
            
        case TTNodeCalc: {
            TTASTNode *leftNode = [action nodeForKey:@"left"];
            TTTokenType op = [action tokenTypeForKey:@"op"];
            TTASTNode *rightNode = [action nodeForKey:@"right"];
            NSString *resultVar = [action stringForKey:@"result_var"];
            
            TTValue *left = [self evaluateExpression:leftNode];
            TTValue *right = [self evaluateExpression:rightNode];
            TTValue *result;
            
            switch (op) {
                case TTTokenPlus:
                    result = [left add:right];
                    break;
                case TTTokenMinus:
                    result = [left subtract:right];
                    break;
                case TTTokenTimes:
                    result = [left multiply:right];
                    break;
                case TTTokenDiv:
                    result = [left divide:right];
                    break;
                case TTTokenRem:
                    result = [left modulo:right];
                    break;
                default:
                    result = [TTValue nullValue];
            }
            
            _variables[resultVar] = result;
            return [TTResult successWithValue:result];
        }
            
        case TTNodeMemo: {
            NSString *name = [action stringForKey:@"name"];
            TTASTNode *valueNode = [action nodeForKey:@"value"];
            TTValue *value = [self evaluateExpression:valueNode];
            
            _variables[name] = value;
            return [TTResult successWithValue:value];
        }
            
        case TTNodeActionReply: {
            TTASTNode *valueNode = [action nodeForKey:@"value"];
            TTValue *value = [self evaluateExpression:valueNode];
            return [TTResult successWithValue:value];
        }
            
        case TTNodeActionCreate: {
            NSString *blueprintName = [action stringForKey:@"blueprint"];
            NSString *instanceName = [action stringForKey:@"name"];
            
            TTInstance *newInstance = [self createInstance:blueprintName];
            if (newInstance) {
                _world[instanceName] = newInstance;
                return [TTResult successWithValue:[TTValue stringValue:instanceName]];
            }
            return [TTResult failureWithMessage:@"Could not create instance"];
        }
            
        case TTNodeActionErase: {
            NSString *targetName = [action stringForKey:@"target"];
            [_world removeObjectForKey:targetName];
            return [TTResult successWithValue:[TTValue nullValue]];
        }
            
        default:
            return [TTResult failureWithMessage:@"Unknown action type"];
    }
}

#pragma mark - When/Forge Execution

- (TTResult *)executeWhen:(NSString *)whenName 
               onInstance:(TTInstance *)instance 
                 withArgs:(NSDictionary<NSString *, TTValue *> *)args {
    
    // Find the when handler
    TTASTNode *whenNode = nil;
    for (TTASTNode *w in instance.blueprint.whens) {
        if ([[w stringForKey:@"name"] isEqualToString:whenName]) {
            whenNode = w;
            break;
        }
    }
    
    if (!whenNode) {
        return [TTResult failureWithMessage:[NSString stringWithFormat:@"When '%@' not found", whenName]];
    }
    
    // Begin transaction for ACID semantics
    [instance beginTransaction];
    
    // Set up arguments as variables
    if (args) {
        [_variables addEntriesFromDictionary:args];
    }
    
    // Push instance fields to variables
    [_variables addEntriesFromDictionary:instance.fields];
    
    // Check conditions (block/must)
    NSArray<TTASTNode *> *conditions = whenNode.data[@"conditions"];
    for (TTASTNode *cond in conditions) {
        if (cond.type == TTNodeBlock) {
            TTASTNode *condExpr = [cond nodeForKey:@"condition"];
            if ([self evaluateCondition:condExpr]) {
                [instance rollbackTransaction];
                return [TTResult failureWithMessage:@"Block condition triggered"];
            }
        } else if (cond.type == TTNodeMust) {
            TTASTNode *condExpr = [cond nodeForKey:@"condition"];
            if (![self evaluateCondition:condExpr]) {
                NSString *msg = [cond stringForKey:@"error_message"] ?: @"Must condition failed";
                [instance rollbackTransaction];
                return [TTResult failureWithMessage:msg];
            }
        }
    }
    
    // Check laws before execution
    NSString *lawError;
    if (![self checkLawsForInstance:instance error:&lawError]) {
        [instance rollbackTransaction];
        return [TTResult finfrWithMessage:lawError];
    }
    
    // Execute actions
    TTResult *lastResult = [TTResult successWithValue:[TTValue nullValue]];
    NSArray<TTASTNode *> *actions = whenNode.data[@"actions"];
    
    for (TTASTNode *action in actions) {
        lastResult = [self executeAction:action onInstance:instance];
        
        if (!lastResult.success) {
            [instance rollbackTransaction];
            return lastResult;
        }
        
        // Sync variables back to instance fields
        for (NSString *fieldName in instance.fields) {
            if (_variables[fieldName]) {
                instance.fields[fieldName] = _variables[fieldName];
            }
        }
        
        // Check laws after each action
        if (![self checkLawsForInstance:instance error:&lawError]) {
            [instance rollbackTransaction];
            return [TTResult finfrWithMessage:lawError];
        }
    }
    
    // Check if this is a finfr terminator
    BOOL isFinfr = [whenNode boolForKey:@"is_finfr"];
    if (isFinfr) {
        [instance commitTransaction];
        NSString *msg = [whenNode stringForKey:@"result_message"] ?: @"Finality reached";
        return [TTResult finfrWithMessage:msg];
    }
    
    // Commit transaction
    [instance commitTransaction];
    
    return lastResult;
}

- (TTResult *)executeForge:(NSString *)forgeName
                onInstance:(TTInstance *)instance
                  withArgs:(NSDictionary<NSString *, TTValue *> *)args {
    
    // Find the forge
    TTASTNode *forgeNode = nil;
    for (TTASTNode *f in instance.blueprint.forges) {
        if ([[f stringForKey:@"name"] isEqualToString:forgeName]) {
            forgeNode = f;
            break;
        }
    }
    
    if (!forgeNode) {
        return [TTResult failureWithMessage:[NSString stringWithFormat:@"Forge '%@' not found", forgeName]];
    }
    
    // Begin transaction
    [instance beginTransaction];
    
    // Set up arguments
    if (args) {
        [_variables addEntriesFromDictionary:args];
    }
    [_variables addEntriesFromDictionary:instance.fields];
    
    // Check laws BEFORE execution (pre-verification)
    NSString *lawError;
    if (![self checkLawsForInstance:instance error:&lawError]) {
        [instance rollbackTransaction];
        return [TTResult finfrWithMessage:lawError];
    }
    
    // Execute actions
    TTResult *lastResult = [TTResult successWithValue:[TTValue nullValue]];
    NSArray<TTASTNode *> *actions = forgeNode.data[@"actions"];
    
    for (TTASTNode *action in actions) {
        lastResult = [self executeAction:action onInstance:instance];
        
        if (!lastResult.success) {
            [instance rollbackTransaction];
            return lastResult;
        }
        
        // Sync variables back to instance fields
        for (NSString *fieldName in instance.fields) {
            if (_variables[fieldName]) {
                instance.fields[fieldName] = _variables[fieldName];
            }
        }
    }
    
    // Check laws AFTER execution (post-verification)
    if (![self checkLawsForInstance:instance error:&lawError]) {
        [instance rollbackTransaction];
        return [TTResult finfrWithMessage:lawError];
    }
    
    [instance commitTransaction];
    return lastResult;
}

#pragma mark - Variable Operations

- (void)setVariable:(NSString *)name value:(TTValue *)value {
    _variables[name] = value;
}

- (TTValue *)variableNamed:(NSString *)name {
    return _variables[name];
}

#pragma mark - Top-Level Execution

- (TTResult *)execute:(TTASTNode *)node {
    if (!node) return [TTResult failureWithMessage:@"Null AST node"];
    
    _startTime = [NSDate date];
    _operationCount = 0;
    
    switch (node.type) {
        case TTNodeProgram: {
            // Execute all blueprints (define them)
            for (TTASTNode *child in node.children) {
                if (child.type == TTNodeBlueprint) {
                    [self defineBlueprint:child];
                }
            }
            return [TTResult successWithValue:[TTValue numberValue:node.children.count]];
        }
            
        case TTNodeBlueprint:
            [self defineBlueprint:node];
            return [TTResult successWithValue:[TTValue stringValue:[node stringForKey:@"name"]]];
            
        default:
            return [TTResult failureWithMessage:@"Unknown node type"];
    }
}

@end
