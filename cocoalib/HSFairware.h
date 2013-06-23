/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSFairwareProtocol.h"

@interface HSFairware : NSObject <HSFairwareProtocol>
{
    NSInteger appId;
    NSString *name;
    BOOL registered;
}
- (id)initWithAppId:(NSInteger)aAppId name:(NSString *)aName;
@end