/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>


@interface VTIsIntIn :  NSValueTransformer
{
    NSIndexSet *ints;
    BOOL reverse;
}
- (id)initWithValues:(NSIndexSet *)values;
- (id)initWithValues:(NSIndexSet *)values reverse:(BOOL)doReverse;
@end

@interface HSVTAdd : NSValueTransformer
{
    int toAdd;
}
- (id)initWithValue:(int)value;
@end
