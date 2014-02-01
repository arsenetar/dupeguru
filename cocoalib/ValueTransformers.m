/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "ValueTransformers.h"
#import "Utils.h"

@implementation VTIsIntIn
- (id)initWithValues:(NSIndexSet *)values
{
    return [self initWithValues:values reverse:NO];
}

- (id)initWithValues:(NSIndexSet *)values reverse:(BOOL)doReverse
{
    self = [super init];
    ints = values;
    [ints retain];
    reverse = doReverse;
    return self;
}

- (void)dealloc
{
    [ints release];
    [super dealloc];
}

+ (Class)transformedValueClass
{
    return [NSNumber class]; //Boolean
}

+ (BOOL)allowsReverseTransformation
{
    return NO;   
}

- (id)transformedValue:(id)value
{
    if (value == nil)
        return nil;
    NSNumber *i = value;
    BOOL r = [ints containsIndex:[i intValue]];
    if (reverse)
        r = !r;
    return [NSNumber numberWithBool:r];
}
@end

@implementation HSVTAdd
- (id)initWithValue:(int)value
{
    self = [super init];
    toAdd = value;
    return self;
}

+ (Class)transformedValueClass
{
    return [NSNumber class];
}

+ (BOOL)allowsReverseTransformation
{
    return NO;   
}

- (id)transformedValue:(id)value
{
    if (value == nil)
        return nil;
    return i2n(n2i(value) + toAdd);
}
@end
