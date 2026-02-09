/*
═══════════════════════════════════════════════════════════════
TTTOKEN - TOKEN TYPES FOR TINYTALK
Defines all token types used by the lexer
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, TTTokenType) {
    // Keywords
    TTTokenBlueprint,
    TTTokenStarts,
    TTTokenCanBe,
    TTTokenWhen,
    TTTokenAnd,
    TTTokenIs,
    TTTokenAbove,
    TTTokenBelow,
    TTTokenWithin,
    TTTokenMake,
    TTTokenSet,
    TTTokenChange,
    TTTokenCreate,
    TTTokenErase,
    TTTokenEach,
    TTTokenFin,
    TTTokenFinfr,
    TTTokenBlock,
    TTTokenMust,
    TTTokenCalc,
    TTTokenPlus,
    TTTokenMinus,
    TTTokenTimes,
    TTTokenDiv,
    TTTokenRem,
    TTTokenMemo,
    TTTokenIf,
    TTTokenOtherwise,
    TTTokenAs,
    TTTokenAt,
    TTTokenTo,
    TTTokenBy,
    TTTokenIn,
    TTTokenNot,
    TTTokenEmpty,
    TTTokenWorld,
    TTTokenReply,
    TTTokenRequest,
    TTTokenEnd,
    TTTokenLaw,
    TTTokenForge,
    TTTokenField,
    
    // Operators
    TTTokenPlusOp,       // + (natural add)
    TTTokenMinusOp,      // - (subtract/remove)
    TTTokenAmpersand,    // & (fuse)
    TTTokenHash,         // # (tag/interpolation)
    TTTokenDot,          // . (field access)
    TTTokenComma,        // ,
    TTTokenLParen,       // (
    TTTokenRParen,       // )
    TTTokenColon,        // :
    TTTokenEquals,       // =
    TTTokenGreater,      // >
    TTTokenLess,         // <
    
    // Literals
    TTTokenNumber,
    TTTokenString,
    TTTokenIdentifier,
    TTTokenSymbol,       // :symbol
    
    // Special
    TTTokenComment,
    TTTokenNewline,
    TTTokenEOF,
    TTTokenError
};

@interface TTToken : NSObject

@property (nonatomic, assign) TTTokenType type;
@property (nonatomic, copy, nullable) NSString *lexeme;
@property (nonatomic, assign) NSInteger line;
@property (nonatomic, strong, nullable) id value;

+ (instancetype)tokenWithType:(TTTokenType)type lexeme:(nullable NSString *)lexeme line:(NSInteger)line;
+ (instancetype)tokenWithType:(TTTokenType)type lexeme:(nullable NSString *)lexeme line:(NSInteger)line value:(nullable id)value;

- (NSString *)typeName;

@end

NS_ASSUME_NONNULL_END
