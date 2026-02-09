/*
═══════════════════════════════════════════════════════════════
TTTOKEN IMPLEMENTATION
═══════════════════════════════════════════════════════════════
*/

#import "TTToken.h"

@implementation TTToken

+ (instancetype)tokenWithType:(TTTokenType)type lexeme:(NSString *)lexeme line:(NSInteger)line {
    return [self tokenWithType:type lexeme:lexeme line:line value:nil];
}

+ (instancetype)tokenWithType:(TTTokenType)type lexeme:(NSString *)lexeme line:(NSInteger)line value:(id)value {
    TTToken *token = [[TTToken alloc] init];
    token.type = type;
    token.lexeme = lexeme;
    token.line = line;
    token.value = value;
    return token;
}

- (NSString *)typeName {
    switch (self.type) {
        case TTTokenBlueprint: return @"BLUEPRINT";
        case TTTokenStarts: return @"STARTS";
        case TTTokenCanBe: return @"CAN_BE";
        case TTTokenWhen: return @"WHEN";
        case TTTokenAnd: return @"AND";
        case TTTokenIs: return @"IS";
        case TTTokenAbove: return @"ABOVE";
        case TTTokenBelow: return @"BELOW";
        case TTTokenWithin: return @"WITHIN";
        case TTTokenMake: return @"MAKE";
        case TTTokenSet: return @"SET";
        case TTTokenChange: return @"CHANGE";
        case TTTokenCreate: return @"CREATE";
        case TTTokenErase: return @"ERASE";
        case TTTokenEach: return @"EACH";
        case TTTokenFin: return @"FIN";
        case TTTokenFinfr: return @"FINFR";
        case TTTokenBlock: return @"BLOCK";
        case TTTokenMust: return @"MUST";
        case TTTokenCalc: return @"CALC";
        case TTTokenPlus: return @"PLUS";
        case TTTokenMinus: return @"MINUS";
        case TTTokenTimes: return @"TIMES";
        case TTTokenDiv: return @"DIV";
        case TTTokenRem: return @"REM";
        case TTTokenMemo: return @"MEMO";
        case TTTokenIf: return @"IF";
        case TTTokenOtherwise: return @"OTHERWISE";
        case TTTokenAs: return @"AS";
        case TTTokenAt: return @"AT";
        case TTTokenTo: return @"TO";
        case TTTokenBy: return @"BY";
        case TTTokenIn: return @"IN";
        case TTTokenNot: return @"NOT";
        case TTTokenEmpty: return @"EMPTY";
        case TTTokenWorld: return @"WORLD";
        case TTTokenReply: return @"REPLY";
        case TTTokenRequest: return @"REQUEST";
        case TTTokenEnd: return @"END";
        case TTTokenLaw: return @"LAW";
        case TTTokenForge: return @"FORGE";
        case TTTokenField: return @"FIELD";
        case TTTokenPlusOp: return @"+";
        case TTTokenMinusOp: return @"-";
        case TTTokenAmpersand: return @"&";
        case TTTokenHash: return @"#";
        case TTTokenDot: return @".";
        case TTTokenComma: return @",";
        case TTTokenLParen: return @"(";
        case TTTokenRParen: return @")";
        case TTTokenColon: return @":";
        case TTTokenEquals: return @"=";
        case TTTokenGreater: return @">";
        case TTTokenLess: return @"<";
        case TTTokenNumber: return @"NUMBER";
        case TTTokenString: return @"STRING";
        case TTTokenIdentifier: return @"IDENTIFIER";
        case TTTokenSymbol: return @"SYMBOL";
        case TTTokenComment: return @"COMMENT";
        case TTTokenNewline: return @"NEWLINE";
        case TTTokenEOF: return @"EOF";
        case TTTokenError: return @"ERROR";
    }
    return @"UNKNOWN";
}

- (NSString *)description {
    if (self.value) {
        return [NSString stringWithFormat:@"Token(%@, '%@', value=%@, line=%ld)", 
                [self typeName], self.lexeme, self.value, (long)self.line];
    }
    return [NSString stringWithFormat:@"Token(%@, '%@', line=%ld)", 
            [self typeName], self.lexeme, (long)self.line];
}

@end
