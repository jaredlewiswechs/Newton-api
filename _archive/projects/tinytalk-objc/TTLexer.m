/*
═══════════════════════════════════════════════════════════════
TTLEXER IMPLEMENTATION
Tokenizer for tinyTalk keywords, operators, and literals
═══════════════════════════════════════════════════════════════
*/

#import "TTLexer.h"

@interface TTLexer ()
@property (nonatomic, assign) NSUInteger start;
@property (nonatomic, assign) NSUInteger current;
@property (nonatomic, assign) NSInteger line;
@property (nonatomic, strong) NSDictionary<NSString *, NSNumber *> *keywords;
@end

@implementation TTLexer

- (instancetype)initWithSource:(NSString *)source {
    self = [super init];
    if (self) {
        _source = [source copy];
        _start = 0;
        _current = 0;
        _line = 1;
        [self setupKeywords];
    }
    return self;
}

- (void)setupKeywords {
    _keywords = @{
        @"blueprint": @(TTTokenBlueprint),
        @"starts": @(TTTokenStarts),
        @"can": @(TTTokenCanBe),  // Will check for "be" next
        @"when": @(TTTokenWhen),
        @"and": @(TTTokenAnd),
        @"is": @(TTTokenIs),
        @"above": @(TTTokenAbove),
        @"below": @(TTTokenBelow),
        @"within": @(TTTokenWithin),
        @"make": @(TTTokenMake),
        @"set": @(TTTokenSet),
        @"change": @(TTTokenChange),
        @"create": @(TTTokenCreate),
        @"erase": @(TTTokenErase),
        @"each": @(TTTokenEach),
        @"fin": @(TTTokenFin),
        @"finfr": @(TTTokenFinfr),
        @"block": @(TTTokenBlock),
        @"must": @(TTTokenMust),
        @"calc": @(TTTokenCalc),
        @"plus": @(TTTokenPlus),
        @"minus": @(TTTokenMinus),
        @"times": @(TTTokenTimes),
        @"div": @(TTTokenDiv),
        @"rem": @(TTTokenRem),
        @"memo": @(TTTokenMemo),
        @"if": @(TTTokenIf),
        @"otherwise": @(TTTokenOtherwise),
        @"as": @(TTTokenAs),
        @"at": @(TTTokenAt),
        @"to": @(TTTokenTo),
        @"by": @(TTTokenBy),
        @"in": @(TTTokenIn),
        @"not": @(TTTokenNot),
        @"empty": @(TTTokenEmpty),
        @"world": @(TTTokenWorld),
        @"reply": @(TTTokenReply),
        @"request": @(TTTokenRequest),
        @"end": @(TTTokenEnd),
        @"law": @(TTTokenLaw),
        @"forge": @(TTTokenForge),
        @"field": @(TTTokenField),
    };
}

- (BOOL)isAtEnd {
    return _current >= _source.length;
}

- (unichar)advance {
    unichar c = [_source characterAtIndex:_current];
    _current++;
    return c;
}

- (unichar)peek {
    if ([self isAtEnd]) return '\0';
    return [_source characterAtIndex:_current];
}

- (unichar)peekNext {
    if (_current + 1 >= _source.length) return '\0';
    return [_source characterAtIndex:_current + 1];
}

- (BOOL)match:(unichar)expected {
    if ([self isAtEnd]) return NO;
    if ([_source characterAtIndex:_current] != expected) return NO;
    _current++;
    return YES;
}

- (void)skipWhitespace {
    while (![self isAtEnd]) {
        unichar c = [self peek];
        if (c == ' ' || c == '\r' || c == '\t') {
            [self advance];
        } else {
            break;
        }
    }
}

- (NSString *)currentLexeme {
    return [_source substringWithRange:NSMakeRange(_start, _current - _start)];
}

- (TTToken *)makeToken:(TTTokenType)type {
    return [TTToken tokenWithType:type lexeme:[self currentLexeme] line:_line];
}

- (TTToken *)makeTokenWithValue:(TTTokenType)type value:(id)value {
    return [TTToken tokenWithType:type lexeme:[self currentLexeme] line:_line value:value];
}

- (TTToken *)errorToken:(NSString *)message {
    return [TTToken tokenWithType:TTTokenError lexeme:message line:_line];
}

- (TTToken *)stringToken {
    while ([self peek] != '"' && ![self isAtEnd]) {
        if ([self peek] == '\n') _line++;
        [self advance];
    }
    
    if ([self isAtEnd]) {
        return [self errorToken:@"Unterminated string"];
    }
    
    // Closing quote
    [self advance];
    
    // Extract string content without quotes
    NSString *value = [_source substringWithRange:NSMakeRange(_start + 1, _current - _start - 2)];
    return [self makeTokenWithValue:TTTokenString value:value];
}

- (TTToken *)numberToken {
    while ([[NSCharacterSet decimalDigitCharacterSet] characterIsMember:[self peek]]) {
        [self advance];
    }
    
    // Look for decimal part
    if ([self peek] == '.' && [[NSCharacterSet decimalDigitCharacterSet] characterIsMember:[self peekNext]]) {
        [self advance]; // Consume '.'
        while ([[NSCharacterSet decimalDigitCharacterSet] characterIsMember:[self peek]]) {
            [self advance];
        }
    }
    
    NSString *lexeme = [self currentLexeme];
    NSNumber *value = @([lexeme doubleValue]);
    return [self makeTokenWithValue:TTTokenNumber value:value];
}

- (TTToken *)identifierToken {
    NSCharacterSet *alphanumericSet = [NSCharacterSet alphanumericCharacterSet];
    
    while ([[NSCharacterSet letterCharacterSet] characterIsMember:[self peek]] ||
           [alphanumericSet characterIsMember:[self peek]] ||
           [self peek] == '_' ||
           [self peek] == '@') {
        [self advance];
    }
    
    NSString *lexeme = [self currentLexeme];
    NSNumber *type = _keywords[lexeme];
    
    if (type) {
        // Special case: "can be" is two words
        if ([lexeme isEqualToString:@"can"]) {
            [self skipWhitespace];
            if ([self peek] == 'b') {
                NSUInteger savedStart = _start;
                _start = _current;
                [self advance]; // 'b'
                if ([self peek] == 'e' && ![self isAtEnd]) {
                    [self advance]; // 'e'
                    unichar next = [self peek];
                    if (next == ' ' || next == '\n' || next == '\r' || next == '\t' || [self isAtEnd]) {
                        return [TTToken tokenWithType:TTTokenCanBe lexeme:@"can be" line:_line];
                    }
                }
                // Rollback if not "be"
                _current = savedStart;
                _start = savedStart;
            }
        }
        return [self makeToken:(TTTokenType)[type integerValue]];
    }
    
    return [self makeToken:TTTokenIdentifier];
}

- (TTToken *)symbolToken {
    // :symbol_name
    while ([[NSCharacterSet letterCharacterSet] characterIsMember:[self peek]] ||
           [[NSCharacterSet decimalDigitCharacterSet] characterIsMember:[self peek]] ||
           [self peek] == '_') {
        [self advance];
    }
    
    NSString *value = [_source substringWithRange:NSMakeRange(_start + 1, _current - _start - 1)];
    return [self makeTokenWithValue:TTTokenSymbol value:value];
}

- (TTToken *)nextToken {
    [self skipWhitespace];
    
    _start = _current;
    
    if ([self isAtEnd]) {
        return [self makeToken:TTTokenEOF];
    }
    
    unichar c = [self advance];
    
    // Check for newline
    if (c == '\n') {
        _line++;
        return [self makeToken:TTTokenNewline];
    }
    
    // Check for comment
    if (c == '/' && [self peek] == '/') {
        [self advance]; // Second '/'
        while ([self peek] != '\n' && ![self isAtEnd]) {
            [self advance];
        }
        return [self makeToken:TTTokenComment];
    }
    
    // Check for # comment (alternative comment style)
    if (c == '#' && [self peek] == ' ') {
        while ([self peek] != '\n' && ![self isAtEnd]) {
            [self advance];
        }
        return [self makeToken:TTTokenComment];
    }
    
    // Single character tokens
    switch (c) {
        case '+': return [self makeToken:TTTokenPlusOp];
        case '-': return [self makeToken:TTTokenMinusOp];
        case '&': return [self makeToken:TTTokenAmpersand];
        case '#': return [self makeToken:TTTokenHash];
        case '.': return [self makeToken:TTTokenDot];
        case ',': return [self makeToken:TTTokenComma];
        case '(': return [self makeToken:TTTokenLParen];
        case ')': return [self makeToken:TTTokenRParen];
        case '=': return [self makeToken:TTTokenEquals];
        case '>': return [self makeToken:TTTokenGreater];
        case '<': return [self makeToken:TTTokenLess];
        case ':': {
            // Check if it's a symbol or just colon
            if ([[NSCharacterSet letterCharacterSet] characterIsMember:[self peek]]) {
                return [self symbolToken];
            }
            return [self makeToken:TTTokenColon];
        }
    }
    
    // String literal
    if (c == '"') {
        return [self stringToken];
    }
    
    // Number literal
    if ([[NSCharacterSet decimalDigitCharacterSet] characterIsMember:c]) {
        return [self numberToken];
    }
    
    // Identifier or keyword (including @field names)
    if ([[NSCharacterSet letterCharacterSet] characterIsMember:c] || c == '@') {
        return [self identifierToken];
    }
    
    return [self errorToken:[NSString stringWithFormat:@"Unexpected character '%c'", c]];
}

- (NSArray<TTToken *> *)allTokens {
    NSMutableArray<TTToken *> *tokens = [NSMutableArray array];
    
    TTToken *token;
    do {
        token = [self nextToken];
        [tokens addObject:token];
    } while (token.type != TTTokenEOF);
    
    return [tokens copy];
}

@end
