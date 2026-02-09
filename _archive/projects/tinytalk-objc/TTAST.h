/*
═══════════════════════════════════════════════════════════════
TTAST - ABSTRACT SYNTAX TREE NODES FOR TINYTALK
Defines all AST node types
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTToken.h"

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, TTNodeType) {
    TTNodeProgram,
    TTNodeBlueprint,
    TTNodeField,
    TTNodeState,
    TTNodeLaw,
    TTNodeWhen,
    TTNodeForge,
    TTNodeCondition,
    TTNodeActionMake,
    TTNodeActionSet,
    TTNodeActionChange,
    TTNodeActionCreate,
    TTNodeActionErase,
    TTNodeActionReply,
    TTNodeBlock,
    TTNodeMust,
    TTNodeCalc,
    TTNodeMemo,
    TTNodeExpression,
    TTNodeLiteral,
    TTNodeIdentifier,
    TTNodeFieldAccess,
    TTNodeBinaryOp,
    TTNodeIf,
    TTNodeEach
};

@interface TTASTNode : NSObject

@property (nonatomic, assign) TTNodeType type;
@property (nonatomic, assign) NSInteger line;
@property (nonatomic, strong, nullable) NSMutableDictionary *data;
@property (nonatomic, strong, nullable) NSMutableArray<TTASTNode *> *children;

+ (instancetype)nodeWithType:(TTNodeType)type line:(NSInteger)line;

// Convenience accessors
- (void)setString:(NSString *)value forKey:(NSString *)key;
- (NSString *)stringForKey:(NSString *)key;
- (void)setNumber:(NSNumber *)value forKey:(NSString *)key;
- (NSNumber *)numberForKey:(NSString *)key;
- (void)setBool:(BOOL)value forKey:(NSString *)key;
- (BOOL)boolForKey:(NSString *)key;
- (void)setNode:(TTASTNode *)value forKey:(NSString *)key;
- (nullable TTASTNode *)nodeForKey:(NSString *)key;
- (void)setTokenType:(TTTokenType)value forKey:(NSString *)key;
- (TTTokenType)tokenTypeForKey:(NSString *)key;

- (void)addChild:(TTASTNode *)child;
- (NSString *)nodeTypeName;
- (NSString *)prettyPrint:(NSInteger)indent;

@end

NS_ASSUME_NONNULL_END
