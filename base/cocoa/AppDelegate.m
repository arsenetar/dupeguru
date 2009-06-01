#import "AppDelegate.h"
#import "ProgressController.h"
#import "RegistrationInterface.h"
#import "Utils.h"
#import "Consts.h"

@implementation AppDelegateBase
- (id)init
{
    self = [super init];
    _appName = @"";
    return self;
}

- (IBAction)unlockApp:(id)sender
{
    if ([[self py] isRegistered])
        return;
    RegistrationInterface *ri = [[RegistrationInterface alloc] initWithApp:[self py] name:_appName limitDescription:LIMIT_DESC];
    if ([ri enterCode] == NSOKButton)
    {
        NSString *menuTitle = [NSString stringWithFormat:@"Thanks for buying %@",_appName];
        [unlockMenuItem setTitle:menuTitle];
    }
    [ri release];
}

- (PyDupeGuruBase *)py { return py; }
- (RecentDirectories *)recentDirectories { return recentDirectories; }
@end
