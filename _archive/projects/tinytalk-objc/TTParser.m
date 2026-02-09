/*
═══════════════════════════════════════════════════════════════
TTPARSER IMPLEMENTATION
Builds AST from token stream
═══════════════════════════════════════════════════════════════
*/

#import "TTParser.h"

@interface TTParser ()
@property (nonatomic, strong) TTLexer *lexer;
@property (nonatomic, strong) TTToken *current;
@property (nonatomic, strong) TTToken *previous;
@property (nonatomic, assign) BOOL hadError;
@property (nonatomic, assign) BOOL panicMode;
@property (nonatomic, copy) NSString *errorMessage;
@end

@implementation TTParser

- (instancetype)initWithLexer:(TTLexer *)lexer {
    self = [super init];
    if (self) {
        _lexer = lexer;
        _hadError = NO;
        _panicMode = NO;
        [self advance];
    }
    return self;
}

#pragma mark - Token Operations

- (void)advance {
    _previous = _current;
    
    while (YES) {
        _current = [_lexer nextToken];
        if (_current.type != TTTokenError) break;
        
        [self errorAtCurrent:_current.lexeme];
    }
}

- (BOOL)check:(TTTokenType)type {
    return _current.type == type;
}

- (BOOL)match:(TTTokenType)type {
    if (![self check:type]) return NO;
    [self advance];
    return YES;
}

- (void)consume:(TTTokenType)type message:(NSString *)message {
    if (_current.type == type) {
        [self advance];
        return;
    }
    
    [self errorAtCurrent:message];
}

- (void)skipNewlines {
    while ([self match:TTTokenNewline] || [self match:TTTokenComment]) {
        // Skip
    }
}

#pragma mark - Error Handling

- (void)errorAtCurrent:(NSString *)message {
    [self errorAt:_current message:message];
}

- (void)error:(NSString *)message {
    [self errorAt:_previous message:message];
}

- (void)errorAt:(TTToken *)token message:(NSString *)message {
    if (_panicMode) return;
    _panicMode = YES;
    _hadError = YES;
    
    NSMutableString *msg = [NSMutableString stringWithFormat:@"[line %ld] Error", (long)token.line];
    
    if (token.type == TTTokenEOF) {
        [msg appendString:@" at end"];
    } else if (token.type == TTTokenError) {
        // Nothing
    } else {
        [msg appendFormat:@" at '%@'", token.lexeme];
    }
    
    [msg appendFormat:@": %@", message];
    _errorMessage = msg;
    
    NSLog(@"%@", msg);
}

- (void)synchronize {
    _panicMode = NO;
    
    while (_current.type != TTTokenEOF) {
        if (_previous.type == TTTokenNewline) return;
        
        switch (_current.type) {
            case TTTokenBlueprint:
            case TTTokenWhen:
            case TTTokenFin:
            case TTTokenFinfr:
            case TTTokenEnd:
            case TTTokenLaw:
            case TTTokenForge:
                return;
            default:
                break;
        }
        
        [self advance];
    }
}

#pragma mark - Expression Parsing

- (TTASTNode *)parsePrimary {
    if ([self match:TTTokenNumber]) {
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeLiteral line:_previous.line];
        [node setNumber:_previous.value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenString]) {
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeLiteral line:_previous.line];
        [node setString:_previous.value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenSymbol]) {
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeLiteral line:_previous.line];
        [node setString:[NSString stringWithFormat:@":%@", _previous.value] forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenIdentifier]) {
        NSString *name = _previous.lexeme;
        
        // Check for field access (e.g., player.cash)
        if ([self match:TTTokenDot]) {
            [self consume:TTTokenIdentifier message:@"Expected field name after '.'"];
            TTASTNode *node = [TTASTNode nodeWithType:TTNodeFieldAccess line:_previous.line];
            [node setString:name forKey:@"object"];
            [node setString:_previous.lexeme forKey:@"field"];
            return node;
        }
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeIdentifier line:_previous.line];
        [node setString:name forKey:@"name"];
        return node;
    }
    
    if ([self match:TTTokenLParen]) {
        TTASTNode *expr = [self parseExpression];
        [self consume:TTTokenRParen message:@"Expected ')' after expression"];
        return expr;
    }
    
    [self error:@"Expected expression"];
    return nil;
}

- (TTASTNode *)parseExpression {
    TTASTNode *left = [self parsePrimary];
    if (!left) return nil;
    
    // Handle "is" keyword before comparison operators
    if ([self match:TTTokenIs]) {
        TTTokenType op = TTTokenIs;
        
        if ([self match:TTTokenAbove]) {
            op = TTTokenAbove;
        } else if ([self match:TTTokenBelow]) {
            op = TTTokenBelow;
        } else if ([self match:TTTokenWithin]) {
            op = TTTokenWithin;
        }
        
        TTASTNode *right = [self parsePrimary];
        if (!right) return nil;
        
        TTASTNode *binary = [TTASTNode nodeWithType:TTNodeBinaryOp line:_previous.line];
        [binary setNode:left forKey:@"left"];
        [binary setNode:right forKey:@"right"];
        [binary setTokenType:op forKey:@"op"];
        left = binary;
    }
    
    // Handle binary operators
    while ([self match:TTTokenPlusOp] || [self match:TTTokenMinusOp] ||
           [self match:TTTokenAmpersand] || [self match:TTTokenHash] ||
           [self match:TTTokenPlus] || [self match:TTTokenMinus] ||
           [self match:TTTokenTimes] || [self match:TTTokenDiv] ||
           [self match:TTTokenIn] || [self match:TTTokenAnd] ||
           [self match:TTTokenGreater] || [self match:TTTokenLess]) {
        TTTokenType op = _previous.type;
        TTASTNode *right = [self parsePrimary];
        if (!right) return nil;
        
        TTASTNode *binary = [TTASTNode nodeWithType:TTNodeBinaryOp line:_previous.line];
        [binary setNode:left forKey:@"left"];
        [binary setNode:right forKey:@"right"];
        [binary setTokenType:op forKey:@"op"];
        left = binary;
    }
    
    return left;
}

#pragma mark - Statement Parsing

- (TTASTNode *)parseField {
    // starts @field_name at value
    // OR: field @field_name: Type
    [self skipNewlines];
    
    [self consume:TTTokenIdentifier message:@"Expected field name"];
    NSString *name = _previous.lexeme;
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeField line:_previous.line];
    [node setString:name forKey:@"name"];
    
    if ([self match:TTTokenAt]) {
        TTASTNode *value = [self parseExpression];
        [node setNode:value forKey:@"initial_value"];
    } else if ([self match:TTTokenAs]) {
        if ([self match:TTTokenEmpty]) {
            // Empty collection
            TTASTNode *emptyNode = [TTASTNode nodeWithType:TTNodeLiteral line:_previous.line];
            [emptyNode setString:@"[]" forKey:@"value"];
            [node setNode:emptyNode forKey:@"initial_value"];
        }
    } else if ([self match:TTTokenColon]) {
        // Type annotation (field @assets: Money)
        [self consume:TTTokenIdentifier message:@"Expected type name"];
        [node setString:_previous.lexeme forKey:@"type"];
    }
    
    return node;
}

- (TTASTNode *)parseState {
    // can be state_name
    [self consume:TTTokenIdentifier message:@"Expected state name"];
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeState line:_previous.line];
    [node setString:_previous.lexeme forKey:@"name"];
    return node;
}

- (TTASTNode *)parseCondition {
    // Parse various condition types
    
    if ([self match:TTTokenBlock]) {
        // block if condition
        [self consume:TTTokenIf message:@"Expected 'if' after 'block'"];
        TTASTNode *condition = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeBlock line:_previous.line];
        [node setNode:condition forKey:@"condition"];
        return node;
    }
    
    if ([self match:TTTokenMust]) {
        // must condition otherwise "message"
        TTASTNode *condition = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeMust line:_previous.line];
        [node setNode:condition forKey:@"condition"];
        
        if ([self match:TTTokenOtherwise]) {
            [self consume:TTTokenString message:@"Expected error message string"];
            [node setString:_previous.value forKey:@"error_message"];
        }
        
        return node;
    }
    
    return nil;
}

- (TTASTNode *)parseAction {
    if ([self match:TTTokenSet]) {
        // set target.field to value
        TTASTNode *target = [self parseExpression];
        [self consume:TTTokenTo message:@"Expected 'to' after set target"];
        TTASTNode *value = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionSet line:_previous.line];
        [node setNode:target forKey:@"target"];
        [node setNode:value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenMake]) {
        // make target state_name
        [self consume:TTTokenIdentifier message:@"Expected target name"];
        NSString *target = _previous.lexeme;
        [self consume:TTTokenIdentifier message:@"Expected state name"];
        NSString *state = _previous.lexeme;
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionMake line:_previous.line];
        [node setString:target forKey:@"target"];
        [node setString:state forKey:@"state"];
        return node;
    }
    
    if ([self match:TTTokenChange]) {
        // change target by +/- value
        TTASTNode *target = [self parseExpression];
        [self consume:TTTokenBy message:@"Expected 'by' after change target"];
        
        TTTokenType op = TTTokenPlusOp;
        if ([self match:TTTokenPlusOp]) {
            op = TTTokenPlusOp;
        } else if ([self match:TTTokenMinusOp]) {
            op = TTTokenMinusOp;
        }
        
        TTASTNode *value = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionChange line:_previous.line];
        [node setNode:target forKey:@"target"];
        [node setTokenType:op forKey:@"op"];
        [node setNode:value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenCalc]) {
        // calc expr op right as result_var
        TTASTNode *left = [self parseExpression];
        
        TTTokenType op = TTTokenPlus;
        if ([self match:TTTokenPlus]) op = TTTokenPlus;
        else if ([self match:TTTokenMinus]) op = TTTokenMinus;
        else if ([self match:TTTokenTimes]) op = TTTokenTimes;
        else if ([self match:TTTokenDiv]) op = TTTokenDiv;
        else if ([self match:TTTokenRem]) op = TTTokenRem;
        
        TTASTNode *right = [self parseExpression];
        [self consume:TTTokenAs message:@"Expected 'as' after calc expression"];
        [self consume:TTTokenIdentifier message:@"Expected result variable name"];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeCalc line:_previous.line];
        [node setNode:left forKey:@"left"];
        [node setTokenType:op forKey:@"op"];
        [node setNode:right forKey:@"right"];
        [node setString:_previous.lexeme forKey:@"result_var"];
        return node;
    }
    
    if ([self match:TTTokenMemo]) {
        // memo name starts value
        [self consume:TTTokenIdentifier message:@"Expected variable name"];
        NSString *name = _previous.lexeme;
        [self consume:TTTokenStarts message:@"Expected 'starts' after memo name"];
        TTASTNode *value = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeMemo line:_previous.line];
        [node setString:name forKey:@"name"];
        [node setNode:value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenReply]) {
        // reply :symbol OR reply value
        TTASTNode *value = [self parseExpression];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionReply line:_previous.line];
        [node setNode:value forKey:@"value"];
        return node;
    }
    
    if ([self match:TTTokenCreate]) {
        // create Blueprint as name
        [self consume:TTTokenIdentifier message:@"Expected blueprint name"];
        NSString *blueprint = _previous.lexeme;
        [self consume:TTTokenAs message:@"Expected 'as' after blueprint name"];
        [self consume:TTTokenIdentifier message:@"Expected instance name"];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionCreate line:_previous.line];
        [node setString:blueprint forKey:@"blueprint"];
        [node setString:_previous.lexeme forKey:@"name"];
        return node;
    }
    
    if ([self match:TTTokenErase]) {
        // erase target
        [self consume:TTTokenIdentifier message:@"Expected target name"];
        
        TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionErase line:_previous.line];
        [node setString:_previous.lexeme forKey:@"target"];
        return node;
    }
    
    // Assignment: identifier = expression
    if ([self check:TTTokenIdentifier]) {
        TTASTNode *left = [self parseExpression];
        if ([self match:TTTokenEquals]) {
            TTASTNode *right = [self parseExpression];
            
            TTASTNode *node = [TTASTNode nodeWithType:TTNodeActionSet line:_previous.line];
            [node setNode:left forKey:@"target"];
            [node setNode:right forKey:@"value"];
            return node;
        }
        // Not an assignment, could be an expression statement
        return left;
    }
    
    return nil;
}

- (TTASTNode *)parseWhen {
    // when event_name(params) conditions actions fin/finfr
    [self consume:TTTokenIdentifier message:@"Expected event name"];
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeWhen line:_previous.line];
    [node setString:_previous.lexeme forKey:@"name"];
    
    // Optional parameters
    NSMutableArray<NSString *> *params = [NSMutableArray array];
    if ([self match:TTTokenLParen]) {
        if (![self check:TTTokenRParen]) {
            do {
                [self consume:TTTokenIdentifier message:@"Expected parameter name"];
                NSString *paramName = _previous.lexeme;
                
                // Optional type annotation
                if ([self match:TTTokenColon]) {
                    [self consume:TTTokenIdentifier message:@"Expected type name"];
                }
                
                [params addObject:paramName];
            } while ([self match:TTTokenComma]);
        }
        [self consume:TTTokenRParen message:@"Expected ')' after parameters"];
    }
    node.data[@"params"] = params;
    
    [self skipNewlines];
    
    // Parse body until fin/finfr/end
    NSMutableArray<TTASTNode *> *conditions = [NSMutableArray array];
    NSMutableArray<TTASTNode *> *actions = [NSMutableArray array];
    
    while (![self check:TTTokenFin] && ![self check:TTTokenFinfr] && 
           ![self check:TTTokenEnd] && ![self check:TTTokenEOF] &&
           ![self check:TTTokenWhen] && ![self check:TTTokenLaw] &&
           ![self check:TTTokenForge]) {
        [self skipNewlines];
        
        if ([self check:TTTokenBlock] || [self check:TTTokenMust]) {
            TTASTNode *cond = [self parseCondition];
            if (cond) [conditions addObject:cond];
        } else if (![self check:TTTokenFin] && ![self check:TTTokenFinfr] &&
                   ![self check:TTTokenEnd] && ![self check:TTTokenEOF]) {
            TTASTNode *action = [self parseAction];
            if (action) [actions addObject:action];
        }
        
        [self skipNewlines];
    }
    
    node.data[@"conditions"] = conditions;
    node.data[@"actions"] = actions;
    
    // Terminator
    if ([self match:TTTokenFinfr]) {
        [node setBool:YES forKey:@"is_finfr"];
        // Optional message
        if ([self check:TTTokenString]) {
            [self advance];
            [node setString:_previous.value forKey:@"result_message"];
        }
    } else if ([self match:TTTokenFin]) {
        [node setBool:NO forKey:@"is_finfr"];
    }
    
    return node;
}

- (TTASTNode *)parseLaw {
    // law LawName
    //   when condition
    //   finfr
    [self consume:TTTokenIdentifier message:@"Expected law name"];
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeLaw line:_previous.line];
    [node setString:_previous.lexeme forKey:@"name"];
    
    [self skipNewlines];
    
    // Parse condition
    if ([self match:TTTokenWhen]) {
        TTASTNode *condition = [self parseExpression];
        [node setNode:condition forKey:@"condition"];
    }
    
    [self skipNewlines];
    
    // Terminator
    if ([self match:TTTokenFinfr]) {
        [node setBool:YES forKey:@"is_finfr"];
    } else if ([self match:TTTokenFin]) {
        [node setBool:NO forKey:@"is_finfr"];
    }
    
    return node;
}

- (TTASTNode *)parseForge {
    // forge method_name(params)
    //   actions
    // end
    [self consume:TTTokenIdentifier message:@"Expected forge name"];
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeForge line:_previous.line];
    [node setString:_previous.lexeme forKey:@"name"];
    
    // Parameters
    NSMutableArray<NSString *> *params = [NSMutableArray array];
    if ([self match:TTTokenLParen]) {
        if (![self check:TTTokenRParen]) {
            do {
                [self consume:TTTokenIdentifier message:@"Expected parameter name"];
                NSString *paramName = _previous.lexeme;
                
                if ([self match:TTTokenColon]) {
                    [self consume:TTTokenIdentifier message:@"Expected type name"];
                }
                
                [params addObject:paramName];
            } while ([self match:TTTokenComma]);
        }
        [self consume:TTTokenRParen message:@"Expected ')' after parameters"];
    }
    node.data[@"params"] = params;
    
    [self skipNewlines];
    
    // Parse body
    NSMutableArray<TTASTNode *> *actions = [NSMutableArray array];
    
    while (![self check:TTTokenEnd] && ![self check:TTTokenEOF] &&
           ![self check:TTTokenWhen] && ![self check:TTTokenLaw] &&
           ![self check:TTTokenForge]) {
        [self skipNewlines];
        
        if (![self check:TTTokenEnd] && ![self check:TTTokenEOF]) {
            TTASTNode *action = [self parseAction];
            if (action) [actions addObject:action];
        }
        
        [self skipNewlines];
    }
    
    node.data[@"actions"] = actions;
    
    [self match:TTTokenEnd];
    
    return node;
}

- (TTASTNode *)parseBlueprint {
    // blueprint TypeName
    //   fields, states, laws, whens, forges
    // end
    [self consume:TTTokenIdentifier message:@"Expected blueprint name"];
    
    TTASTNode *node = [TTASTNode nodeWithType:TTNodeBlueprint line:_previous.line];
    [node setString:_previous.lexeme forKey:@"name"];
    
    [self skipNewlines];
    
    NSMutableArray<TTASTNode *> *fields = [NSMutableArray array];
    NSMutableArray<TTASTNode *> *states = [NSMutableArray array];
    NSMutableArray<TTASTNode *> *laws = [NSMutableArray array];
    NSMutableArray<TTASTNode *> *whens = [NSMutableArray array];
    NSMutableArray<TTASTNode *> *forges = [NSMutableArray array];
    
    while (![self check:TTTokenEnd] && ![self check:TTTokenEOF] &&
           ![self check:TTTokenBlueprint]) {
        [self skipNewlines];
        
        if ([self match:TTTokenStarts] || [self match:TTTokenField]) {
            [fields addObject:[self parseField]];
        } else if ([self match:TTTokenCanBe]) {
            [states addObject:[self parseState]];
        } else if ([self match:TTTokenLaw]) {
            [laws addObject:[self parseLaw]];
        } else if ([self match:TTTokenWhen]) {
            [whens addObject:[self parseWhen]];
        } else if ([self match:TTTokenForge]) {
            [forges addObject:[self parseForge]];
        } else {
            [self skipNewlines];
            if ([self check:TTTokenEnd] || [self check:TTTokenEOF]) break;
            // Skip unknown tokens
            if (![self check:TTTokenEOF]) [self advance];
        }
        
        [self skipNewlines];
    }
    
    node.data[@"fields"] = fields;
    node.data[@"states"] = states;
    node.data[@"laws"] = laws;
    node.data[@"whens"] = whens;
    node.data[@"forges"] = forges;
    
    [self match:TTTokenEnd];
    
    return node;
}

#pragma mark - Top Level

- (TTASTNode *)parse {
    TTASTNode *program = [TTASTNode nodeWithType:TTNodeProgram line:1];
    
    [self skipNewlines];
    
    while (![self check:TTTokenEOF]) {
        if ([self match:TTTokenBlueprint]) {
            TTASTNode *blueprint = [self parseBlueprint];
            if (blueprint) [program addChild:blueprint];
        } else {
            [self skipNewlines];
            if ([self check:TTTokenEOF]) break;
            [self advance];
        }
        
        if (_panicMode) [self synchronize];
        [self skipNewlines];
    }
    
    return _hadError ? nil : program;
}

@end
