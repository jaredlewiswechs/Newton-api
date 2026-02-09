/*
═══════════════════════════════════════════════════════════════
TTVALUE IMPLEMENTATION
═══════════════════════════════════════════════════════════════
*/

#import "TTValue.h"

@interface TTValue ()
@property (nonatomic, assign) TTValueType type;
@property (nonatomic, strong) id rawValue;
@end

@implementation TTValue

+ (instancetype)nullValue {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeNull;
    value.rawValue = nil;
    return value;
}

+ (instancetype)numberValue:(double)number {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeNumber;
    value.rawValue = @(number);
    return value;
}

+ (instancetype)stringValue:(NSString *)string {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeString;
    value.rawValue = [string copy];
    return value;
}

+ (instancetype)booleanValue:(BOOL)boolean {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeBoolean;
    value.rawValue = @(boolean);
    return value;
}

+ (instancetype)arrayValue:(NSArray<TTValue *> *)array {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeArray;
    value.rawValue = [array copy];
    return value;
}

+ (instancetype)symbolValue:(NSString *)symbol {
    TTValue *value = [[TTValue alloc] init];
    value.type = TTValueTypeSymbol;
    value.rawValue = [symbol copy];
    return value;
}

#pragma mark - Type Checking

- (BOOL)isNull {
    return self.type == TTValueTypeNull;
}

- (BOOL)isNumber {
    return self.type == TTValueTypeNumber;
}

- (BOOL)isString {
    return self.type == TTValueTypeString;
}

- (BOOL)isBoolean {
    return self.type == TTValueTypeBoolean;
}

- (BOOL)isArray {
    return self.type == TTValueTypeArray;
}

- (BOOL)isSymbol {
    return self.type == TTValueTypeSymbol;
}

- (BOOL)isTruthy {
    switch (self.type) {
        case TTValueTypeNull:
            return NO;
        case TTValueTypeBoolean:
            return [self.rawValue boolValue];
        case TTValueTypeNumber:
            return [self.rawValue doubleValue] != 0.0;
        case TTValueTypeString:
            return [(NSString *)self.rawValue length] > 0;
        case TTValueTypeArray:
            return [(NSArray *)self.rawValue count] > 0;
        case TTValueTypeSymbol:
            return YES;
    }
    return NO;
}

#pragma mark - Value Extraction

- (double)asNumber {
    if (self.type == TTValueTypeNumber) {
        return [self.rawValue doubleValue];
    }
    if (self.type == TTValueTypeString) {
        return [(NSString *)self.rawValue doubleValue];
    }
    if (self.type == TTValueTypeBoolean) {
        return [self.rawValue boolValue] ? 1.0 : 0.0;
    }
    return 0.0;
}

- (NSString *)asString {
    if (self.type == TTValueTypeString || self.type == TTValueTypeSymbol) {
        return self.rawValue;
    }
    if (self.type == TTValueTypeNumber) {
        double num = [self.rawValue doubleValue];
        if (num == (long)num) {
            return [NSString stringWithFormat:@"%ld", (long)num];
        }
        return [NSString stringWithFormat:@"%g", num];
    }
    if (self.type == TTValueTypeBoolean) {
        return [self.rawValue boolValue] ? @"true" : @"false";
    }
    if (self.type == TTValueTypeNull) {
        return @"null";
    }
    if (self.type == TTValueTypeArray) {
        NSMutableArray *strings = [NSMutableArray array];
        for (TTValue *v in (NSArray *)self.rawValue) {
            [strings addObject:[v asString]];
        }
        return [NSString stringWithFormat:@"[%@]", [strings componentsJoinedByString:@", "]];
    }
    return @"";
}

- (BOOL)asBoolean {
    return [self isTruthy];
}

- (NSArray<TTValue *> *)asArray {
    if (self.type == TTValueTypeArray) {
        return self.rawValue;
    }
    return @[self];
}

#pragma mark - Operations

- (TTValue *)add:(TTValue *)other {
    return [TTValue numberValue:[self asNumber] + [other asNumber]];
}

- (TTValue *)subtract:(TTValue *)other {
    return [TTValue numberValue:[self asNumber] - [other asNumber]];
}

- (TTValue *)multiply:(TTValue *)other {
    return [TTValue numberValue:[self asNumber] * [other asNumber]];
}

- (TTValue *)divide:(TTValue *)other {
    double divisor = [other asNumber];
    if (divisor == 0) {
        return [TTValue nullValue];  // Division by zero
    }
    return [TTValue numberValue:[self asNumber] / divisor];
}

- (TTValue *)modulo:(TTValue *)other {
    double divisor = [other asNumber];
    if (divisor == 0) {
        return [TTValue nullValue];
    }
    return [TTValue numberValue:fmod([self asNumber], divisor)];
}

- (TTValue *)concatenate:(TTValue *)other {
    // Fuse: no space
    return [TTValue stringValue:[NSString stringWithFormat:@"%@%@", [self asString], [other asString]]];
}

- (TTValue *)naturalAdd:(TTValue *)other {
    // Natural add: with space for strings, numeric for numbers
    if (self.type == TTValueTypeString || other.type == TTValueTypeString) {
        return [TTValue stringValue:[NSString stringWithFormat:@"%@ %@", [self asString], [other asString]]];
    }
    return [self add:other];
}

#pragma mark - Comparison

- (BOOL)isEqualToValue:(TTValue *)other {
    if (self.type != other.type) {
        // Allow number/string comparison
        if ((self.type == TTValueTypeNumber && other.type == TTValueTypeString) ||
            (self.type == TTValueTypeString && other.type == TTValueTypeNumber)) {
            return [self asNumber] == [other asNumber];
        }
        return NO;
    }
    
    switch (self.type) {
        case TTValueTypeNull:
            return YES;
        case TTValueTypeNumber:
            return [self asNumber] == [other asNumber];
        case TTValueTypeString:
        case TTValueTypeSymbol:
            return [[self asString] isEqualToString:[other asString]];
        case TTValueTypeBoolean:
            return [self asBoolean] == [other asBoolean];
        case TTValueTypeArray: {
            NSArray *selfArr = [self asArray];
            NSArray *otherArr = [other asArray];
            if (selfArr.count != otherArr.count) return NO;
            for (NSUInteger i = 0; i < selfArr.count; i++) {
                if (![selfArr[i] isEqualToValue:otherArr[i]]) return NO;
            }
            return YES;
        }
    }
    return NO;
}

- (BOOL)isGreaterThan:(TTValue *)other {
    return [self asNumber] > [other asNumber];
}

- (BOOL)isLessThan:(TTValue *)other {
    return [self asNumber] < [other asNumber];
}

#pragma mark - NSCopying

- (id)copyWithZone:(NSZone *)zone {
    TTValue *copy = [[TTValue alloc] init];
    copy.type = self.type;
    if ([self.rawValue conformsToProtocol:@protocol(NSCopying)]) {
        copy.rawValue = [self.rawValue copyWithZone:zone];
    } else {
        copy.rawValue = self.rawValue;
    }
    return copy;
}

#pragma mark - Description

- (NSString *)description {
    return [self asString];
}

- (BOOL)isEqual:(id)object {
    if (![object isKindOfClass:[TTValue class]]) return NO;
    return [self isEqualToValue:(TTValue *)object];
}

- (NSUInteger)hash {
    return [[self asString] hash];
}

@end
