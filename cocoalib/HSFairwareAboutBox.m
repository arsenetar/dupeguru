/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSFairwareAboutBox.h"
#import "HSFairwareAboutBox_UI.h"
#import "HSFairwareReminder.h"

@implementation HSFairwareAboutBox

@synthesize titleTextField;
@synthesize versionTextField;
@synthesize copyrightTextField;
@synthesize registeredTextField;
@synthesize registerButton;

- (id)initWithApp:(PyFairware *)aApp
{
    self = [super initWithWindow:nil];
    [self setWindow:createHSFairwareAboutBox_UI(self)];
    app = [aApp retain];
    [self updateFields];
    return self;
}

- (void)dealloc
{
    [app release];
    [super dealloc];
}

- (void)updateFields
{
    [titleTextField setStringValue:[app appLongName]];
    NSString *version = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleVersion"];
    [versionTextField setStringValue:[NSString stringWithFormat:@"Version: %@",version]];
    NSString *copyright = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"NSHumanReadableCopyright"];
    [copyrightTextField setStringValue:copyright];
    if ([app isRegistered]) {
        [registeredTextField setHidden:NO];
        [registerButton setHidden:YES];
    }
    else {
        [registeredTextField setHidden:YES];
        [registerButton setHidden:NO];
    }    
}

- (void)showRegisterDialog
{
    HSFairwareReminder *fr = [[HSFairwareReminder alloc] initWithApp:app];
    [fr enterCode];
    [fr release];
    [self updateFields];
}
@end
