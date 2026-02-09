/*
═══════════════════════════════════════════════════════════════
TTLEXER - TOKENIZER FOR TINYTALK
Handles all keywords, operators, and literals
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTToken.h"

NS_ASSUME_NONNULL_BEGIN

@interface TTLexer : NSObject

@property (nonatomic, copy, readonly) NSString *source;
@property (nonatomic, assign, readonly) NSInteger line;

- (instancetype)initWithSource:(NSString *)source;

/// Returns the next token from the source
- (TTToken *)nextToken;

/// Returns all tokens (for debugging)
- (NSArray<TTToken *> *)allTokens;

@end

NS_ASSUME_NONNULL_END
