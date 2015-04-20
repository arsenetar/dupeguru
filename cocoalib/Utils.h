/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>

//Useful shortcuts
#define i2n(i) [NSNumber numberWithInteger:i]
#define n2i(n) [n integerValue]
#define b2n(b) [NSNumber numberWithBool:b]
#define n2b(n) [n boolValue]
#if __LP64__
    #define f2n(d) [NSNumber numberWithDouble:d]
    #define n2f(n) [n doubleValue]
#else
    #define f2n(f) [NSNumber numberWithFloat:f]
    #define n2f(n) [n floatValue]
#endif
#define p2a(p) [Utils indexPath2Array:p]
#define a2p(a) [Utils array2IndexPath:a]
#define fmt(x,...) [NSString stringWithFormat:x,__VA_ARGS__]

@interface Utils : NSObject
+ (NSArray *)indexSet2Array:(NSIndexSet *)aIndexSet;
+ (NSIndexSet *)array2IndexSet:(NSArray *)numberArray;
+ (NSArray *)indexPath2Array:(NSIndexPath *)aIndexPath;
+ (NSIndexPath *)array2IndexPath:(NSArray *)indexArray;
+ (NSString *)indexPath2String:(NSIndexPath *)aIndexPath;
+ (NSIndexPath *)string2IndexPath:(NSString *)aString;
@end

void replacePlaceholderInView(NSView *placeholder, NSView *replaceWith);