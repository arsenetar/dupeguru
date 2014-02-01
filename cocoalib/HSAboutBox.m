/* 
Copyright 2014 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "HSAboutBox.h"
#import "HSAboutBox_UI.h"

@implementation HSAboutBox

@synthesize titleTextField;
@synthesize versionTextField;
@synthesize copyrightTextField;

- (id)initWithApp:(PyBaseApp *)aApp
{
    self = [super initWithWindow:nil];
    [self setWindow:createHSAboutBox_UI(self)];
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
}

@end
