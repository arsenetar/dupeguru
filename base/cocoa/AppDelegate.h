#import <Cocoa/Cocoa.h>
#import "RecentDirectories.h"
#import "PyDupeGuru.h"

@interface AppDelegateBase : NSObject
{
    IBOutlet PyDupeGuruBase *py;
    IBOutlet RecentDirectories *recentDirectories;
    IBOutlet NSMenuItem *unlockMenuItem;
    
    NSString *_appName;
}
- (IBAction)unlockApp:(id)sender;

- (PyDupeGuruBase *)py;
- (RecentDirectories *)recentDirectories;
@end
