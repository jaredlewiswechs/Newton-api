/*
═══════════════════════════════════════════════════════════════
TTPARSER - AST BUILDER FOR TINYTALK
Builds abstract syntax tree from tokens
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTLexer.h"
#import "TTAST.h"

NS_ASSUME_NONNULL_BEGIN

@interface TTParser : NSObject

@property (nonatomic, assign, readonly) BOOL hadError;
@property (nonatomic, copy, readonly, nullable) NSString *errorMessage;

- (instancetype)initWithLexer:(TTLexer *)lexer;

/// Parse the entire program
- (nullable TTASTNode *)parse;

/// Parse a single expression (for REPL)
- (nullable TTASTNode *)parseExpression;

@end

NS_ASSUME_NONNULL_END
