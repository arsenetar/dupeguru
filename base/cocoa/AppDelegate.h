/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "PyDupeGuru.h"
#import "ResultWindow.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet PyDupeGuruBase *py;
    IBOutlet RecentDirectories *recentDirectories;
    IBOutlet NSMenuItem *unlockMenuItem;
    IBOutlet ResultWindowBase *result;
    
    NSString *_appName;
}
- (IBAction)unlockApp:(id)sender;

- (PyDupeGuruBase *)py;
- (RecentDirectories *)recentDirectories;
@end
