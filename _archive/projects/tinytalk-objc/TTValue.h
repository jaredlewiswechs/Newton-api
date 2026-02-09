/*
═══════════════════════════════════════════════════════════════
TTVALUE - VALUE TYPES FOR TINYTALK RUNTIME
Represents runtime values with type information
═══════════════════════════════════════════════════════════════
*/

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSInteger, TTValueType) {
    TTValueTypeNull,
    TTValueTypeNumber,
    TTValueTypeString,
    TTValueTypeBoolean,
    TTValueTypeArray,
    TTValueTypeSymbol
};

@interface TTValue : NSObject <NSCopying>

@property (nonatomic, assign, readonly) TTValueType type;
@property (nonatomic, strong, readonly, nullable) id rawValue;

// Constructors
+ (instancetype)nullValue;
+ (instancetype)numberValue:(double)number;
+ (instancetype)stringValue:(NSString *)string;
+ (instancetype)booleanValue:(BOOL)boolean;
+ (instancetype)arrayValue:(NSArray<TTValue *> *)array;
+ (instancetype)symbolValue:(NSString *)symbol;

// Type checking
- (BOOL)isNull;
- (BOOL)isNumber;
- (BOOL)isString;
- (BOOL)isBoolean;
- (BOOL)isArray;
- (BOOL)isSymbol;
- (BOOL)isTruthy;

// Value extraction
- (double)asNumber;
- (NSString *)asString;
- (BOOL)asBoolean;
- (NSArray<TTValue *> *)asArray;

// Operations
- (TTValue *)add:(TTValue *)other;
- (TTValue *)subtract:(TTValue *)other;
- (TTValue *)multiply:(TTValue *)other;
- (TTValue *)divide:(TTValue *)other;
- (TTValue *)modulo:(TTValue *)other;
- (TTValue *)concatenate:(TTValue *)other;  // Fuse (&)
- (TTValue *)naturalAdd:(TTValue *)other;   // + with space

// Comparison
- (BOOL)isEqualToValue:(TTValue *)other;
- (BOOL)isGreaterThan:(TTValue *)other;
- (BOOL)isLessThan:(TTValue *)other;

@end

NS_ASSUME_NONNULL_END
