/*
═══════════════════════════════════════════════════════════════
TTAST IMPLEMENTATION
═══════════════════════════════════════════════════════════════
*/

#import "TTAST.h"

@implementation TTASTNode

+ (instancetype)nodeWithType:(TTNodeType)type line:(NSInteger)line {
    TTASTNode *node = [[TTASTNode alloc] init];
    node.type = type;
    node.line = line;
    node.data = [NSMutableDictionary dictionary];
    node.children = [NSMutableArray array];
    return node;
}

- (void)setString:(NSString *)value forKey:(NSString *)key {
    self.data[key] = value;
}

- (NSString *)stringForKey:(NSString *)key {
    return self.data[key];
}

- (void)setNumber:(NSNumber *)value forKey:(NSString *)key {
    self.data[key] = value;
}

- (NSNumber *)numberForKey:(NSString *)key {
    return self.data[key];
}

- (void)setBool:(BOOL)value forKey:(NSString *)key {
    self.data[key] = @(value);
}

- (BOOL)boolForKey:(NSString *)key {
    return [self.data[key] boolValue];
}

- (void)setNode:(TTASTNode *)value forKey:(NSString *)key {
    self.data[key] = value;
}

- (TTASTNode *)nodeForKey:(NSString *)key {
    return self.data[key];
}

- (void)setTokenType:(TTTokenType)value forKey:(NSString *)key {
    self.data[key] = @(value);
}

- (TTTokenType)tokenTypeForKey:(NSString *)key {
    return (TTTokenType)[self.data[key] integerValue];
}

- (void)addChild:(TTASTNode *)child {
    [self.children addObject:child];
}

- (NSString *)nodeTypeName {
    switch (self.type) {
        case TTNodeProgram: return @"Program";
        case TTNodeBlueprint: return @"Blueprint";
        case TTNodeField: return @"Field";
        case TTNodeState: return @"State";
        case TTNodeLaw: return @"Law";
        case TTNodeWhen: return @"When";
        case TTNodeForge: return @"Forge";
        case TTNodeCondition: return @"Condition";
        case TTNodeActionMake: return @"Make";
        case TTNodeActionSet: return @"Set";
        case TTNodeActionChange: return @"Change";
        case TTNodeActionCreate: return @"Create";
        case TTNodeActionErase: return @"Erase";
        case TTNodeActionReply: return @"Reply";
        case TTNodeBlock: return @"Block";
        case TTNodeMust: return @"Must";
        case TTNodeCalc: return @"Calc";
        case TTNodeMemo: return @"Memo";
        case TTNodeExpression: return @"Expression";
        case TTNodeLiteral: return @"Literal";
        case TTNodeIdentifier: return @"Identifier";
        case TTNodeFieldAccess: return @"FieldAccess";
        case TTNodeBinaryOp: return @"BinaryOp";
        case TTNodeIf: return @"If";
        case TTNodeEach: return @"Each";
    }
    return @"Unknown";
}

- (NSString *)prettyPrint:(NSInteger)indent {
    NSMutableString *result = [NSMutableString string];
    NSString *padding = [@"" stringByPaddingToLength:indent * 2 withString:@" " startingAtIndex:0];
    
    [result appendFormat:@"%@%@", padding, [self nodeTypeName]];
    
    // Add relevant data
    NSString *name = [self stringForKey:@"name"];
    if (name) {
        [result appendFormat:@" '%@'", name];
    }
    
    id value = self.data[@"value"];
    if (value && ![value isKindOfClass:[TTASTNode class]]) {
        [result appendFormat:@" = %@", value];
    }
    
    [result appendString:@"\n"];
    
    // Print children
    for (TTASTNode *child in self.children) {
        [result appendString:[child prettyPrint:indent + 1]];
    }
    
    // Print nested nodes in data
    for (NSString *key in self.data) {
        id obj = self.data[key];
        if ([obj isKindOfClass:[TTASTNode class]]) {
            [result appendFormat:@"%@  [%@]:\n", padding, key];
            [result appendString:[(TTASTNode *)obj prettyPrint:indent + 2]];
        }
    }
    
    return result;
}

- (NSString *)description {
    return [self prettyPrint:0];
}

@end
