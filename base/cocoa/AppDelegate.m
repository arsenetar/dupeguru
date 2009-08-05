/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
