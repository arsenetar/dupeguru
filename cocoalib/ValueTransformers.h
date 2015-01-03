/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
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
