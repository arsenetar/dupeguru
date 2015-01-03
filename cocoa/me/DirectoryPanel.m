/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "DirectoryPanel.h"

@implementation DirectoryPanelME
- (id)initWithParentApp:(id)aParentApp
{
    self = [super initWithParentApp:aParentApp];
    _alwaysShowPopUp = YES;
    return self;
}

- (void)fillPopUpMenu
{
    [super fillPopUpMenu];
    NSMenu *m = [addButtonPopUp menu];
    NSMenuItem *mi = [m insertItemWithTitle:NSLocalizedString(@"Add iTunes Library", @"") action:@selector(addiTunes:)
        keyEquivalent:@"" atIndex:1];
    [mi setTarget:self];
}

- (IBAction)addiTunes:(id)sender
{
    [self addDirectory:@"iTunes Library"];
}
@end
