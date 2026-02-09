/*
═══════════════════════════════════════════════════════════════
TTRUNTIME - EXECUTION ENGINE WITH ACID SEMANTICS
Verified computation with rollback capability
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>
#import "TTAST.h"
#import "TTValue.h"
#import "TTToken.h"

NS_ASSUME_NONNULL_BEGIN

// Execution bounds (determinism guarantee)
@interface TTExecutionBounds : NSObject
@property (nonatomic, assign) NSUInteger maxIterations;
@property (nonatomic, assign) NSUInteger maxRecursionDepth;
@property (nonatomic, assign) NSUInteger maxOperations;
@property (nonatomic, assign) NSTimeInterval timeoutSeconds;

+ (instancetype)defaultBounds;
@end

// Result of execution
@interface TTResult : NSObject
@property (nonatomic, assign) BOOL success;
@property (nonatomic, strong, nullable) TTValue *value;
@property (nonatomic, copy, nullable) NSString *errorMessage;
@property (nonatomic, assign) BOOL isFinfr;  // Ontological death

+ (instancetype)successWithValue:(nullable TTValue *)value;
+ (instancetype)failureWithMessage:(NSString *)message;
+ (instancetype)finfrWithMessage:(NSString *)message;
@end

// Blueprint definition
@interface TTBlueprint : NSObject
@property (nonatomic, copy) NSString *name;
@property (nonatomic, strong) NSArray<TTASTNode *> *fields;
@property (nonatomic, strong) NSArray<TTASTNode *> *states;
@property (nonatomic, strong) NSArray<TTASTNode *> *laws;
@property (nonatomic, strong) NSArray<TTASTNode *> *whens;
@property (nonatomic, strong) NSArray<TTASTNode *> *forges;
@end

// Instance of a blueprint
@interface TTInstance : NSObject
@property (nonatomic, strong) TTBlueprint *blueprint;
@property (nonatomic, strong) NSMutableDictionary<NSString *, TTValue *> *fields;
@property (nonatomic, copy, nullable) NSString *currentState;
@property (nonatomic, assign) BOOL inTransaction;
@property (nonatomic, strong, nullable) NSDictionary<NSString *, TTValue *> *fieldSnapshot;

- (void)beginTransaction;
- (void)commitTransaction;
- (void)rollbackTransaction;
@end

// Runtime environment
@interface TTRuntime : NSObject

@property (nonatomic, strong, readonly) TTExecutionBounds *bounds;
@property (nonatomic, assign, readonly) NSUInteger operationCount;

- (instancetype)init;
- (instancetype)initWithBounds:(TTExecutionBounds *)bounds;

// Blueprint operations
- (TTBlueprint *)defineBlueprint:(TTASTNode *)node;
- (nullable TTBlueprint *)blueprintNamed:(NSString *)name;
- (TTInstance *)createInstance:(NSString *)blueprintName;
- (nullable TTInstance *)instanceNamed:(NSString *)name;

// Execution
- (TTResult *)execute:(TTASTNode *)node;
- (TTResult *)executeWhen:(NSString *)whenName 
               onInstance:(TTInstance *)instance 
                 withArgs:(nullable NSDictionary<NSString *, TTValue *> *)args;
- (TTResult *)executeForge:(NSString *)forgeName
                onInstance:(TTInstance *)instance
                  withArgs:(nullable NSDictionary<NSString *, TTValue *> *)args;

// Law checking (constraint verification)
- (BOOL)checkLawsForInstance:(TTInstance *)instance error:(NSString * _Nullable * _Nullable)error;

// Variable operations
- (void)setVariable:(NSString *)name value:(TTValue *)value;
- (nullable TTValue *)variableNamed:(NSString *)name;

// Evaluation
- (TTValue *)evaluateExpression:(TTASTNode *)expr;
- (BOOL)evaluateCondition:(TTASTNode *)condition;

// World (global namespace)
@property (nonatomic, strong, readonly) NSMutableDictionary<NSString *, TTInstance *> *world;

@end

NS_ASSUME_NONNULL_END
